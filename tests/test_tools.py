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
from build_analysis import build as build_analysis
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

    def test_supporting_html_is_inert_in_parent_and_sandboxed(self):
        self.deck['supplements']=[{'id':'extra','label':'Marketing','html':'<!doctype html><script>globalThis.EXTRA=true</script>'}]
        result=build(self.deck)
        self.assertNotIn('<script>globalThis.EXTRA',result)
        self.assertIn('sandbox="allow-scripts allow-downloads allow-forms allow-modals"',result)
        self.assertNotIn('allow-same-origin',result)
        payload=json.loads(result.split('id="deck-data">',1)[1].split('</script>',1)[0])
        self.assertEqual(payload['supplements'],self.deck['supplements'])
        self.deck['supplements'].append(dict(self.deck['supplements'][0]))
        with self.assertRaises(ValueError):build(self.deck)

    def test_analysis_builder_escapes_input_and_rejects_invalid_counts(self):
        config=json.loads((ROOT/'examples/marketing-analysis/data.json').read_text(encoding='utf8'))
        config['title']='</title><script>globalThis.UNSAFE=true</script>'
        result=build_analysis(config)
        self.assertNotIn('<script>globalThis.UNSAFE',result)
        self.assertIn('analysis-license',result)
        self.assertIn('Presentation Output Exception',result)
        config['records'][0]['clicks']=config['records'][0]['impressions']+1
        with self.assertRaises(ValueError):build_analysis(config)

    def test_analysis_metadata_defines_actual_units_denominators_scope_and_rounding(self):
        # Newly authored fictional rows: deliberately different denominators/groups.
        config={'title':'Fictional review case','fictional':True,'source':'Review!A1:H4','records':[
            {'week':'2026-01-05','channel':'One','region':'North','spend':14000,'impressions':110,'clicks':11,'orders':2,'revenue':23000},
            {'week':'2026-01-05','channel':'Two','region':'South','spend':27000,'impressions':220,'clicks':22,'orders':3,'revenue':41000},
            {'week':'2026-01-12','channel':'One','region':'South','spend':8000,'impressions':50,'clicks':5,'orders':1,'revenue':9000}]}
        before=copy.deepcopy(config)
        for language in ['ko','en']:
            config['language']=language
            result=build_analysis(config)
            data=json.loads(result.split('id="analysis-data" type="application/json">',1)[1].split('</script>',1)[0])
            meta=data['metricMetadata']
            self.assertEqual(meta['source'],'Review!A1:H4')
            self.assertEqual(meta['sourceUnits']['spend'],'KRW')
            self.assertEqual(meta['sourceUnits']['revenue'],'KRW')
            for key,numerator,denominator,unit,multiplier in [('roas','revenue','spend','x',1),('cvr','orders','clicks','%',100),('ctr','clicks','impressions','%',100),('aov','revenue','orders','KRW',1)]:
                self.assertEqual(meta['rates'][key],dict(numerator=numerator,denominator=denominator,unit=unit,displayMultiplier=multiplier))
            self.assertEqual(meta['aggregation'],'ratio_of_sums_within_same_filtered_group')
            self.assertEqual(meta['zeroDenominator'],'unavailable')
            self.assertEqual(meta['scope']['values'],{'week':['2026-01-05','2026-01-12'],'channel':['One','Two'],'region':['North','South']})
            self.assertEqual(meta['display']['ko']['moneyDivisor'],10000)
            self.assertEqual(meta['display']['en']['moneyDivisor'],1000000)
            self.assertEqual(meta['display']['en']['trendMaxDecimals'],1)
            self.assertEqual(meta['display']['rateMaxDecimals'],2)
            self.assertIn('round for display only',meta['rounding'])
            self.assertIn('not a passed audit',meta['sourceReview'])
            self.assertIn('id="verification-evidence"',result)
            self.assertEqual(data['records'],before['records'])
        config.pop('language')
        self.assertEqual(config,before) # Builder must not mutate the caller's source.

    def test_analysis_rejects_conflicting_metadata_and_keeps_source_inert(self):
        config=json.loads((ROOT/'examples/marketing-analysis/data.json').read_text(encoding='utf8'))
        config['source']='Review!A1:H25 </script><script>globalThis.UNSAFE=true</script>'
        output=build_analysis(config)
        self.assertNotIn('<script>globalThis.UNSAFE',output)
        payload=json.loads(output.split('id="analysis-data" type="application/json">',1)[1].split('</script>',1)[0])
        self.assertEqual(payload['metricMetadata']['source'],config['source'])
        self.assertEqual(build_analysis(payload),output) # Canonical metadata is accepted on rebuild.
        payload['metricMetadata']['rates']['cvr']['denominator']='impressions'
        with self.assertRaisesRegex(ValueError,'conflicts'):build_analysis(payload)

    def test_campaign_workbook_rows_and_cached_formulas_match_reviewed_json(self):
        config=json.loads((ROOT/'examples/marketing-analysis/data.json').read_text(encoding='utf8'))
        ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        with zipfile.ZipFile(ROOT/'examples/marketing-analysis/campaign-source.xlsx') as archive:
            strings=[]
            if 'xl/sharedStrings.xml' in archive.namelist():
                strings=[''.join(n.itertext()) for n in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('x:si',ns)]
            root=ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
            cells={}
            for cell in root.findall('.//x:c',ns):
                value=cell.findtext('x:v',namespaces=ns)
                if cell.get('t')=='s':value=strings[int(value)]
                elif cell.get('t')=='inlineStr':value=''.join(cell.find('x:is',ns).itertext())
                elif value is not None and cell.get('t') not in ('str','e','d'):value=float(value)
                cells[cell.get('r')]=value
        keys=['week','channel','region','spend','impressions','clicks','orders','revenue']
        self.assertEqual([cells[f'{col}1'] for col in 'ABCDEFGH'],['Week','Channel','Region','Spend (KRW)','Impressions','Clicks','Orders','Revenue (KRW)'])
        for number,record in enumerate(config['records'],2):
            self.assertEqual([cells[f'{col}{number}'] for col in 'ABCDEFGH'],[record[k] for k in keys])
        expected=config['expected']
        for cell,key in [('K2','spend'),('K3','revenue'),('K4','orders'),('K5','clicks')]:self.assertEqual(cells[cell],expected[key])
        self.assertAlmostEqual(cells['K6'],expected['revenue']/expected['spend'])

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
