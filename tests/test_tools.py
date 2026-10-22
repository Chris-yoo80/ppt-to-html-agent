"""Behavior checks for input ordering, sensitive notes and inert HTML output."""
import copy
import io
import json
from pathlib import Path
import sys
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/ppt-to-html/scripts'))
from build_deck import build
from deck_model import validate_deck
from extract_pptx import extract, paragraphs, NS
from build_motion_demo import build as build_motion, validate as validate_motion
from xml.etree import ElementTree as ET


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.deck = json.loads((ROOT / 'examples/library/deck.json').read_text(encoding='utf-8'))

    def test_single_file_output_keeps_user_text_inert(self):
        self.deck['title'] = '</title><script>globalThis.UNSAFE=true</script>'
        self.deck['scenes'][0]['items'][0]['body'] = '</script><img src=x onerror=alert(1)> & 한글'
        result = build(self.deck)
        self.assertNotIn('<script>globalThis.UNSAFE', result)
        self.assertNotIn('<img src=x', result)
        data = result.split('id="deck-data">', 1)[1].split('</script>', 1)[0]
        self.assertEqual(json.loads(data)['scenes'][0]['items'][0]['body'], self.deck['scenes'][0]['items'][0]['body'])
        self.assertNotRegex(result, r'<(?:script|link)[^>]+(?:src|href)="https?://')

    def test_rejects_unusable_scene_models(self):
        mutations = [lambda d: d['scenes'].append(copy.deepcopy(d['scenes'][0])),
                     lambda d: d['scenes'][0].update(items=[]),
                     lambda d: d['settings'].update(width=0),
                     lambda d: d['scenes'][0].update(duration=float('nan')),
                     lambda d: d['scenes'][0].update(layout='unknown')]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                deck=copy.deepcopy(self.deck); mutation(deck)
                with self.assertRaises(ValueError):
                    validate_deck(deck)

    def test_paragraph_breaks_and_tabs_survive_extraction(self):
        root=ET.fromstring(f'<text xmlns:a="{NS["a"]}"><a:p><a:r><a:t>첫 줄</a:t></a:r><a:br/><a:r><a:t>둘째 줄</a:t></a:r><a:tab/><a:r><a:t>끝</a:t></a:r></a:p></text>')
        self.assertEqual(paragraphs(root),['첫 줄\n둘째 줄\t끝'])

    def test_motion_route_validation_rejects_missing_or_duplicated_stops(self):
        config=json.loads((ROOT/'examples/motion-stories/stories.json').read_text(encoding='utf-8'))
        config['stories'][0]['after'][0][0]=1
        with self.assertRaises(ValueError):
            validate_motion(config)

    def test_motion_gallery_keeps_labels_inert_and_legal_notices(self):
        config=json.loads((ROOT/'examples/motion-stories/stories.json').read_text(encoding='utf-8'))
        config['stories'][0]['title']='</script><script>globalThis.UNSAFE=true</script>'
        result=build_motion(config)
        self.assertNotIn('<script>globalThis.UNSAFE',result)
        self.assertIn('Presentation Output Exception',result)
        self.assertIn('id="font-license"',result)
        data=result.split('id="stories-data" type="application/json">',1)[1].split('</script>',1)[0]
        self.assertEqual(json.loads(data)['stories'][0]['title'],config['stories'][0]['title'])

    def test_pptx_follows_relationship_order_and_separates_notes(self):
        ns='http://schemas.openxmlformats.org/'
        p=ns+'presentationml/2006/main'; a=ns+'drawingml/2006/main'
        r=ns+'officeDocument/2006/relationships'; package=ns+'package/2006/relationships'
        def relations(body):
            return f'<Relationships xmlns="{package}">{body}</Relationships>'
        def rel(identity, kind, target):
            return f'<Relationship Id="{identity}" Type="{r}/{kind}" Target="{target}"/>'
        def slide(value):
            return f'<p:sld xmlns:p="{p}" xmlns:a="{a}"><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{value}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
        document=io.BytesIO()
        with zipfile.ZipFile(document,'w') as archive:
            archive.writestr('ppt/presentation.xml',f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId id="256" r:id="second"/><p:sldId id="257" r:id="first"/></p:sldIdLst></p:presentation>')
            archive.writestr('ppt/_rels/presentation.xml.rels',relations(rel('first','slide','slides/slide1.xml')+rel('second','slide','slides/slide2.xml')))
            archive.writestr('ppt/slides/slide1.xml',slide('두 번째').replace('<p:sld ', '<p:sld show="0" '))
            table=f'<p:graphicFrame><a:graphic><a:graphicData><a:tbl><a:tr><a:tc><a:txBody><a:p><a:r><a:t>표 데이터</a:t></a:r></a:p></a:txBody></a:tc></a:tr></a:tbl></a:graphicData></a:graphic></p:graphicFrame>'
            archive.writestr('ppt/slides/slide2.xml',slide('첫 번째').replace('</p:spTree>',table+'</p:spTree>'))
            archive.writestr('ppt/slides/_rels/slide2.xml.rels',relations(rel('notes','notesSlide','../notesSlides/notesSlide2.xml')+rel('picture','image','../media/picture.png')+rel('diagram','diagramData','../diagrams/data1.xml')))
            archive.writestr('ppt/notesSlides/notesSlide2.xml',slide('PRIVATE TEST NOTE').replace('p:sld ', 'p:notes ').replace('</p:sld>', '</p:notes>'))
            archive.writestr('ppt/media/picture.png',b'NOT A REAL IMAGE')
        document.seek(0)
        result=extract(document)
        self.assertEqual([s['text'] for s in result['slides']],[[['첫 번째']],[['두 번째']]])
        self.assertEqual(result['slides'][0]['notes'],['PRIVATE TEST NOTE'])
        self.assertEqual(result['slides'][0]['tables'],[[['표 데이터']]])
        self.assertEqual(result['slides'][0]['media'][0]['target'],'ppt/media/picture.png')
        self.assertNotIn('PRIVATE TEST NOTE',str(result['slides'][0]['text']))
        self.assertNotIn('NOT A REAL IMAGE',json.dumps(result))
        self.assertFalse(result['slides'][0]['hidden'])
        self.assertTrue(result['slides'][1]['hidden'])
        self.assertEqual(result['slides'][0]['media'][1]['type'],'diagramData')
        self.assertIn('SmartArt',result['slides'][0]['warnings'][0])


if __name__ == '__main__':
    unittest.main()
