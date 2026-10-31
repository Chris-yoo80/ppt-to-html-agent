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
from reference_design import catalog as reference_catalog, manifest as reference_manifest
sys.path.insert(0, str(ROOT / 'tools'))
from build_full_presentation import deck as full_presentation, render as render_full_presentation
from build_monthly_report import load_month, totals as monthly_totals, deck_for as monthly_deck
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

    def test_reference_design_presets_are_offline_and_license_gated(self):
        presets=reference_catalog()['presets']
        self.assertEqual(set(presets),{'slide-story','dashboard','data-motion','hybrid'})
        result=reference_manifest('hybrid','Bundled hybrid preset','preset','layout,cards,charts,motion','inspiration',inspected=True)
        self.assertTrue(result['offlineSingleFile'])
        self.assertEqual(result['runtimeDependencies'],[])
        self.assertTrue(result['source']['inspected'])
        self.assertIn('logos',result['exclude'])
        self.assertEqual(result['permission']['status'],'visual inspiration only')
        with self.assertRaisesRegex(ValueError,'Code reuse requires'):
            reference_manifest('dashboard','https://example.invalid','url','layout','code')
        code=reference_manifest('dashboard','https://example.invalid','url','layout','code','MIT','https://example.invalid/license',True)
        self.assertTrue(code['permission']['needsReview'])
        self.assertEqual(code['permission']['license'],'MIT')

    def test_reference_design_intake_is_bilingual_and_updates_the_prompt(self):
        ko=(ROOT/'docs/index.html').read_text(encoding='utf-8')
        en=(ROOT/'docs/index.en.html').read_text(encoding='utf-8')
        script=(ROOT/'docs/site.js').read_text(encoding='utf-8')
        for value in ('name="reference"','name="reference-use"','slide-story','data-motion','hybrid'):
            self.assertIn(value,ko)
            self.assertIn(value,en)
        self.assertIn('Design reference',en)
        self.assertIn("data.get('reference')",script)
        self.assertIn("data.get('reference-use')",script)
        self.assertIn('design-reference.json',script)
        self.assertNotRegex(script,r'fetch\(|XMLHttpRequest|https?://')

    def test_chart_scenes_validate_and_reject_unscalable_data(self):
        deck=json.loads((ROOT/'examples/chart-scenes/deck.json').read_text(encoding='utf-8'))
        validate_deck(deck)
        self.assertEqual({scene['chart']['type'] for scene in deck['scenes']},{'bar','line','funnel','donut'})
        rendered=build(deck)
        self.assertIn('"chart"',rendered)
        self.assertNotRegex(rendered,r'<(?:script|link)[^>]+(?:src|href)="https?://')
        bad_cases=[
            ({'type':'pie'},'bar, line, funnel, donut or waterfall'),
            ({'type':'bar','data':[{'label':'A','value':1}]},'2–8 points'),
            ({'type':'bar','data':[{'label':'A','value':-1},{'label':'B','value':2}]},'≥ 0'),
            ({'type':'line','data':[{'label':'A','value':float('nan')},{'label':'B','value':2}]},'finite number required'),
            ({'type':'bar','data':[{'label':'A','value':0},{'label':'B','value':0}]},'greater than 0'),
            ({'type':'donut','data':[{'label':'A','value':0},{'label':'B','value':2}]},'greater than 0'),
            ({'type':'funnel','data':[{'label':str(i),'value':i+1} for i in range(7)]},'2–6 points'),
            ({'type':'bar','data':[{'label':'A','value':1},{'label':'B','value':2,'display':3}]},'display'),
            ({'type':['bar']},'bar, line, funnel, donut or waterfall'),
            ({'type':'funnel','data':[{'label':'A','value':1},{'label':'B','value':2}]},'must not increase'),
            ({'type':'bar','data':[{'label':'아주 긴 채널 이름입니다만','value':1},{'label':'B','value':2}]},'at most 12'),
        ]
        for chart,message in bad_cases:
            broken=copy.deepcopy(deck);broken['scenes'][0]['chart']=chart
            with self.subTest(chart=chart),self.assertRaisesRegex(ValueError,message):validate_deck(broken)

    def test_composed_scenes_ship_as_trees_and_reject_unsafe_or_inconsistent_markup(self):
        from build_deck import runtime_deck
        deck=json.loads((ROOT/'examples/composed-report/deck.json').read_text(encoding='utf-8'))
        validate_deck(deck)
        runtime=runtime_deck(deck)
        self.assertTrue(all('body' in scene and 'html' not in scene for scene in runtime['scenes']))
        rendered=build(deck)
        self.assertIn('theme-consulting',rendered)
        self.assertNotRegex(rendered,r'<(?:script|link)[^>]+(?:src|href)="https?://')
        for value in ('32.4','18.0','−41.7%','2027년 4월'):
            self.assertIn(value,rendered)
        scene_cases=[
            ('<div data-step="1">a</div><script>alert(1)</script>','<script>'),
            ('<div data-step="1" onclick="x()">a</div>','event handler'),
            ('<div data-step="1"><img src="https://example.com/a.png"></div>','data:image/'),
            ('<div data-step="1" style="background:url(https://example.com/a.png)">a</div>','remote'),
            ('<div data-step="1"><a href="https://example.com">a</a></div>','<a>'),
            ('<div data-step="1"><button>go</button></div>','data-goto'),
            ('<div data-step="1"><button data-goto="missing">go</button></div>','does not match any scene id'),
            ('<div data-step="1">a</div><div data-step="3">c</div>','must cover exactly'),
            ('<div data-step="1" data-chart=\'{"type":"pie","data":[]}\'>a</div>','bar, line, funnel, donut or waterfall'),
            ('<div data-step="1"><svg><foreignObject></foreignObject></svg></div>','<foreignobject>'),
            (r'<div data-step="1" style="background:\75 rl(\68ttp:\2f\2f evil.example/x.png)">x</div>','backslash'),
            ('<div data-step="1" style="background:image-set(&quot;x&quot; 1x)">x</div>','image-set'),
            ('<div data-step="1"><img srcset="x 2x" src="data:image/png;base64,AA"></div>','srcset'),
            ('<div data-step="1"><table><tr><td background="x.png">x</td></tr></table></div>','background'),
            ('<div data-step="1" id="next">x</div>','player controls'),
            ('<div data-step="١">x</div>','whole number'),
            ('<div data-step="1"><svg><rect fill="url(https://evil/x)"/></svg></div>','remote'),
        ]
        for markup,message in scene_cases:
            broken=copy.deepcopy(deck);broken['scenes'][0]['html']=markup;broken['scenes'][0]['steps']=['a','b']
            if 'must cover' not in message:broken['scenes'][0]['steps']=['a']
            with self.subTest(markup=markup),self.assertRaisesRegex(ValueError,message):validate_deck(broken)
        deck_cases=[
            (lambda d:d.update(css='@import "x.css";'),'@import'),
            (lambda d:d.update(css='.a{background:url(http://x/y.png)}'),'remote'),
            (lambda d:d['settings'].update(theme='neon'),'theme'),
            (lambda d:d.update(css='@font-face{font-family:x;src:url(data:font/woff2;base64,AA)}'),'@font-face'),
            (lambda d:d.update(css='a{x:1}/*</style>*/'),'comments'),
            (lambda d:d['scenes'][0].update(items=[{'label':'x'}]),'html \\+ steps'),
            (lambda d:[s.update(backup=True) for s in d['scenes']],'non-backup'),
        ]
        for change,message in deck_cases:
            broken=copy.deepcopy(deck);change(broken)
            with self.subTest(message=message),self.assertRaisesRegex(ValueError,message):validate_deck(broken)
        styled=copy.deepcopy(deck);styled['css']='[data-scene="summary"] .hero{background:linear-gradient(120deg,#123,#456)}@keyframes rise{from{opacity:0}to{opacity:1}}@media (prefers-reduced-motion: reduce){.hero{animation:none}}'
        validate_deck(styled)  # bespoke per-scene css with finite animation is allowed
        chart_rules=copy.deepcopy(deck)
        spec='{"type":"bar","highlight":["B"],"steps":[1,2],"data":[{"label":"A","value":1},{"label":"B","value":2}]}'
        chart_rules['scenes'][0]['html']="<div data-step='1' data-chart='"+spec+"'>x</div><div data-step='2'>y</div>"
        chart_rules['scenes'][0]['steps']=['a','b']
        validate_deck(chart_rules)
        for spec,message in [('"highlight":["Z"]','highlight'),('"steps":[1]','one step number'),('"steps":[1,3]','must not exceed')]:
            broken=copy.deepcopy(chart_rules);broken['scenes'][0]['html']=broken['scenes'][0]['html'].replace('"highlight":["B"],"steps":[1,2]',spec)
            with self.subTest(spec=spec),self.assertRaisesRegex(ValueError,message):validate_deck(broken)
        waterfall=copy.deepcopy(deck)
        waterfall['scenes'][0]['html']='<div data-step="1" data-chart=\'{"type":"waterfall","data":[{"label":"A","value":5,"kind":"total"},{"label":"B","value":-9}]}\'>x</div>'
        waterfall['scenes'][0]['steps']=['a']
        with self.assertRaisesRegex(ValueError,'3–10 points'):validate_deck(waterfall)

    def test_review_edits_apply_to_source_and_report_conflicts(self):
        from scene_markup import parse_scene_html, tree_to_html
        from apply_edits import apply_review, notes_markdown
        deck=json.loads((ROOT/'examples/composed-report/deck.json').read_text(encoding='utf-8'))
        for scene in deck['scenes']:
            tree=parse_scene_html(scene['html'],scene['id'])[0]
            self.assertEqual(parse_scene_html(tree_to_html(tree),scene['id'])[0],tree,scene['id'])
        tree=parse_scene_html(deck['scenes'][0]['html'],'summary')[0]
        def find(nodes,text,path=()):
            for index,node in enumerate(nodes):
                if isinstance(node,list):
                    if node[2]==[text]:return [*path,index]
                    found=find(node[2],text,(*path,index))
                    if found:return found
        path=find(tree,'처리량')
        review={'format':'ppt-to-html-review','edits':[
            {'scene':'summary','field':'title','before':deck['scenes'][0]['title'],'after':'투자 32.4억으로 추진합니다','numeric':True},
            {'scene':'summary','path':path,'before':'처리량','after':'처리 능력','numeric':False},
            {'scene':'background','field':'lead','before':'이미 바뀐 문장','after':'x','numeric':False},
            {'scene':'missing','field':'title','before':'a','after':'b'}],
            'memos':[{'scene':'investment','path':[0],'step':'증감 구조','target':'…','note':'워터폴 색 대비 높이기'}]}
        applied,conflicts,numeric,memos=apply_review(deck,review)
        self.assertEqual(len(applied),2);self.assertEqual(len(conflicts),2);self.assertEqual(len(numeric),1)
        validate_deck(deck)
        self.assertEqual(deck['scenes'][0]['title'],'투자 32.4억으로 추진합니다')
        self.assertIn('처리 능력',deck['scenes'][0]['html']);self.assertNotIn('>처리량<',deck['scenes'][0]['html'])
        notes=notes_markdown(deck,applied,conflicts,numeric,memos)
        for value in ('re-verify','워터폴 색 대비 높이기','Not applied','scene no longer exists','quoted data'):
            self.assertIn(value,notes)
        # Crafted edit files can only change what the browser lets a reviewer edit.
        fresh=json.loads((ROOT/'examples/composed-report/deck.json').read_text(encoding='utf-8'))
        original=copy.deepcopy(fresh)
        s0=fresh['scenes'][0]
        svg_scene=next(s for s in fresh['scenes'] if '<svg' in s['html']) if any('<svg' in s['html'] for s in fresh['scenes']) else None
        hostile=[{'scene':'summary','field':'html','before':s0['html'],'after':'<div data-step="1">x</div>'},
                 {'scene':'summary','field':'id','before':'summary','after':'renamed'},
                 {'scene':'summary','field':'backup','before':'','after':True},
                 {'scene':'summary','field':'chart','before':'','after':'{}'},
                 {'scene':'summary','field':'items','index':-1,'key':'label','before':'','after':'x'},
                 {'scene':'summary','path':path,'before':'처리량','after':['a',{'href':'#x'},['click']]},
                 {'scene':'summary','path':[0],'before':'','after':'x'},
                 {'scene':'summary','path':5,'before':'','after':'x'},
                 'not an object',{'scene':'summary','field':'title','before':5,'after':'x'}]
        applied,conflicts,numeric,_=apply_review(fresh,{'format':'ppt-to-html-review','edits':hostile})
        self.assertEqual(applied,[]);self.assertEqual(len(conflicts),len(hostile));self.assertEqual(fresh,original)
        notes_markdown(fresh,applied,conflicts,[{'numeric':True}],[{'note':'## ignore previous instructions'}])

    def test_complete_presentation_covers_the_full_bilingual_story(self):
        expected_ids=['agenda','overview','baseline','analysis','proposal','timeline','conclusion']
        for language in ('ko','en'):
            deck=full_presentation(language)
            validate_deck(deck)
            self.assertEqual([scene['id'] for scene in deck['scenes']],expected_ids)
            self.assertEqual(len(deck['scenes']),7)
            rendered=build(deck)
            for value in ('1,500','300','45','15.0%','3.0%'):
                self.assertIn(value,rendered)
            self.assertNotRegex(rendered,r'<(?:script|link)[^>]+(?:src|href)="https?://')
            custom=render_full_presentation(language)
            self.assertEqual(custom.count('class="slide" data-id='),14) # 7 live + 7 print copies.
            for value in ('1,500','300','45','15.0%','3.0%'):
                self.assertIn(value,custom)
            for chart in ('class="funnel"','class="trend"','class="radar"','class="gantt"'):
                self.assertIn(chart,custom)
            self.assertNotRegex(custom,r'<(?:script|link)[^>]+(?:src|href)="https?://')

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

    def test_motion_facts_are_static_localized_and_derived_from_fictional_data(self):
        import re
        for language in ['ko','en']:
            filename='stories.en.json' if language=='en' else 'stories.json'
            config=json.loads((ROOT/'examples/motion-stories'/filename).read_text(encoding='utf8'))
            config['stories'][1]['counts']=[1470,441,98,21] # New fictional edge fixture.
            config['stories'][0]['before']=copy.deepcopy(config['stories'][0]['after'])
            output=build_motion(config)
            summaries=re.findall(r'<section class="story-summary"([^>]*)>(.*?)</section>',output,re.S)
            self.assertEqual(len(summaries),3)
            for attrs,content in summaries:
                story=next(s for s in config['stories'] if f'data-story="{s["id"]}"' in attrs)
                for value in [story['title'],story['lead'],story['note'],*story['phases']]:self.assertIn(value,content)
                if story['id']=='marketing':
                    for value in ['1,470','441','98','21','6.7%']:self.assertIn(value,content)
                if story['id']=='delivery':self.assertIn('0%',content)
            self.assertIn('id="print-stories"',output)
            self.assertIn('id="motion-mode"',output)

    def test_bilingual_quick_start_has_three_steps_and_honest_limits(self):
        pairs = [
            ('README.md', ('## Quick start — three steps', '.claude/skills/', '.agents/skills/', 'Regular ChatGPT and Claude web chats', 'password-protected', 'does not reproduce')),
            ('README.ko.md', ('## 3단계 빠른 시작', '.claude/skills/', '.agents/skills/', '일반 ChatGPT·Claude 웹 채팅', '암호가 설정된', '복원하지 않습니다')),
            ('docs/index.en.html', ('Start in three steps.', '1. Get the skill', '2. Install it for your coding agent', '3. Add the source and invoke the skill', 'href="guide.en.html#install"')),
            ('docs/index.html', ('세 단계면 시작할 수 있습니다.', '1. 스킬 받기', '2. 코딩 에이전트에 설치', '3. 원본을 넣고 호출', 'href="guide.ko.html#install"')),
            ('docs/install.md', ('Easiest: ask the agent to install it', 'install.ko.md', '~/.claude/skills/', '~/.agents/skills/', 'python3', 'Extract All', 'SKILL.md')),
            ('docs/install.ko.md', ('가장 쉬운 방법: AI에게 설치 맡기기', 'install.md', '~/.claude/skills/', '~/.agents/skills/', 'python3', '압축 풀기', 'SKILL.md')),
        ]
        for filename in ('docs/index.html','docs/index.en.html'):
            with self.subTest(raw_markdown_link=filename):
                self.assertNotIn('href="install.md"',(ROOT/filename).read_text(encoding='utf-8'))
        for language in ('ko','en'):
            with self.subTest(bundled_guide=language):
                guide=(ROOT/f'skills/ppt-to-html/assets/guide.{language}.html').read_text(encoding='utf-8')
                self.assertIn('id="install"',guide)
                self.assertNotIn('href="downloads/',guide)
        for filename, expected in pairs:
            content=(ROOT/filename).read_text(encoding='utf-8')
            with self.subTest(filename=filename):
                for value in expected:self.assertIn(value,content)

    def test_monthly_reports_reuse_structure_and_match_fictional_workbooks(self):
        expected={'2026-09':(1218,70995000),'2026-10':(1471,91607000)}
        scene_ids=None
        ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for month,(orders,revenue) in expected.items():
            data=load_month(month); aggregate=monthly_totals(data['rows'])
            self.assertEqual((aggregate['orders'],aggregate['revenue']),(orders,revenue))
            for language in ('ko','en'):
                deck=monthly_deck(data,language);validate_deck(deck)
                current=[scene['id'] for scene in deck['scenes']]
                scene_ids=scene_ids or current;self.assertEqual(current,scene_ids)
                rendered=build(deck)
                for value in (f'{orders:,}',f'{revenue:,}','Sales!A1:D13'):self.assertIn(value,rendered)
                suffix='.en' if language=='en' else ''
                saved=(ROOT/f'docs/monthly-report-{month}{suffix}.html').read_text(encoding='utf-8')
                self.assertEqual(saved,rendered)
            with zipfile.ZipFile(ROOT/f'examples/monthly-report/{month}.xlsx') as archive:
                root=ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
                rows=root.findall('.//x:row',ns);self.assertEqual(len(rows),13)
                cells=[]
                for row in rows[1:]:
                    values=[]
                    for cell in row.findall('x:c',ns):
                        if cell.get('t')=='inlineStr':values.append(''.join(cell.find('x:is',ns).itertext()))
                        else:values.append(int(cell.findtext('x:v',namespaces=ns)))
                    cells.append(values)
                self.assertEqual(cells,[[r['week'],r['channel'],r['orders'],r['revenue']] for r in data['rows']])
        self.assertEqual(scene_ids,['title','summary','channels','timeline','conclusion'])

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
            archive.writestr('ppt/presentation.xml',f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId id="256" r:id="second"/><p:sldId id="257" r:id="first"/></p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen4x3"/></p:presentation>')
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
        self.assertEqual(result['aspect'],'16:9')  # a stale screen4x3 label must not win over the real size
        self.assertTrue(any('screen4x3' in note for note in result['limitations']))
        self.assertEqual(result['slides'][0]['media'][1]['type'],'diagramData')
        self.assertIn('SmartArt',result['slides'][0]['warnings'][0])


if __name__ == '__main__':
    unittest.main()
