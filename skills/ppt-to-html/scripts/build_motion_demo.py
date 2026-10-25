"""Build a self-contained gallery of three fictional motion-story presets."""
import argparse
import base64
import html
import json
import math
from pathlib import Path

ASSETS=Path(__file__).resolve().parent.parent/'assets'


def validate(config):
    if not isinstance(config,dict) or not isinstance(config.get('title'),str):
        raise ValueError('A title and a story collection are required')
    if type(config.get('duration')) not in (int,float) or not math.isfinite(config['duration']) or not 12<=config['duration']<=120:
        raise ValueError('Duration must be 12–120 seconds')
    stories=config.get('stories')
    if not isinstance(stories,list) or len(stories)!=3 or not all(isinstance(s,dict) for s in stories) or {s.get('id') for s in stories}!={'delivery','marketing','warehouse'}:
        raise ValueError('Exactly one delivery, marketing and warehouse story is required')
    for story in stories:
        for key in ('label','eyebrow','title','lead','note'):
            if not isinstance(story.get(key),str) or not story[key].strip():
                raise ValueError(f'Story field {key} requires text')
        if not isinstance(story.get('phases'),list) or len(story['phases'])!=4 or not all(isinstance(p,str) and p.strip() for p in story['phases']):
            raise ValueError('Each story requires four phase names')
        if story['id']=='delivery':
            coordinates=[story.get('hub'),*story.get('stops',[])]
            if len(coordinates)!=13 or any(not isinstance(p,list) or len(p)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) or not 0<=x<=1280 for x in p) for p in coordinates):
                raise ValueError('Delivery requires one hub and twelve finite coordinate pairs')
            for key in ('before','after'):
                plan=story.get(key)
                if not isinstance(plan,list) or len(plan)!=3 or any(not isinstance(route,list) or not route for route in plan):
                    raise ValueError('Delivery requires three nonempty routes')
                ids=[item for route in plan for item in route]
                if any(type(i) is not int for i in ids) or sorted(ids)!=list(range(12)):
                    raise ValueError('Every stop must occur exactly once in each route plan')
        elif story['id']=='marketing':
            counts=story.get('counts')
            if not isinstance(counts,list) or len(counts)!=4 or any(type(n) is not int or n<=0 for n in counts) or counts!=sorted(counts,reverse=True):
                raise ValueError('Marketing requires four positive, nonincreasing fictional counts')
    return config


def summaries(config):
    """Always-readable facts, independent of SVG opacity and timeline position."""
    english=config.get('language')=='en'
    result=[]
    for story in config['stories']:
        if story['id']=='delivery':
            def length(plan):
                return sum(sum(math.dist(a,b) for a,b in zip(points,points[1:]))
                           for ids in plan for points in [[story['hub'],*[story['stops'][i] for i in ids],story['hub']]])
            before,after=length(story['before']),length(story['after'])
            gain=math.floor((1-after/before)*100+.5) if before else 0
            facts=[f"{len(story['stops'])} fictional stops · {len(story['after'])} vehicles" if english else f"가상 배송처 {len(story['stops'])}곳 · 차량 {len(story['after'])}대",
                   f"{gain}% shorter total route length on fictional coordinates; not a road-performance result." if english else f"가상 좌표의 총 경로 길이 {gain}% 감소 · 실측 운행 성과가 아닙니다."]
        elif story['id']=='marketing':
            names=['Reach','Engagement','Purchases','Return visits'] if english else ['도달','참여','구매','재방문']
            facts=[f'{name}: {count:,}' for name,count in zip(names,story['counts'])]
            facts.append(('Reach-to-purchase conversion: ' if english else '도달 대비 구매 전환율: ')+f"{story['counts'][2]/story['counts'][0]*100:.1f}%")
        else:
            facts=['4 illustrative process steps; not measured throughput or storage capacity.' if english else '가상 공정 4단계 · 실측 처리량이나 보관 용량이 아닙니다.']
        facts_html=''.join('<li>'+html.escape(value)+'</li>' for value in facts)
        phases=''.join('<li>'+html.escape(value)+'</li>' for value in story['phases'])
        result.append('<section class="story-summary" data-story="'+story['id']+'"'+(' hidden' if result else '')+'><p class="summary-label">'+('KEY FACTS / AVAILABLE WITHOUT MOTION' if english else '핵심 정보 / 모션 없이도 확인')+'</p><h2>'+html.escape(story['title'])+'</h2><p>'+html.escape(story['lead'])+'</p><ul>'+facts_html+'</ul><ol>'+phases+'</ol><p class="summary-note">'+html.escape(story['note'])+'</p></section>')
    return ''.join(result)


def build(config):
    validate(config)
    css='\n'.join((ASSETS/name).read_text(encoding='utf-8') for name in ('motion-stories.css','motion-mobile.css'))
    for weight,style in [(400,'regular'),(700,'bold')]:
        encoded=base64.b64encode((ASSETS/'fonts'/f'story-sans-{style}.woff2').read_bytes()).decode('ascii')
        css+=f'\n@font-face{{font-family:"Story Sans";font-style:normal;font-weight:{weight};font-display:swap;src:url(data:font/woff2;base64,{encoded}) format("woff2")}}'
    js='\n'.join((ASSETS/name).read_text(encoding='utf-8') for name in ('motion-math.js','motion-stories.js'))
    license_text=(ASSETS.parent/'LICENSE').read_text(encoding='utf-8')
    font_notice=(ASSETS/'fonts/NOTICE.txt').read_text(encoding='utf-8')+'\n'+(ASSETS/'fonts/OFL.txt').read_text(encoding='utf-8')
    data=json.dumps(config,ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    output = f'''<!doctype html>
<!-- Copyright (c) 2026 Chris-yoo80. Embedded runtime from PPT to HTML Agent.
Presentation Output Exception applies. Keep this notice and the license below.
{license_text.replace('--','- -')}
-->
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(config['title'])}</title><style>{css}</style></head>
<body><template id="font-license"><pre>{html.escape(font_notice)}</pre></template>
<main class="story-shell"><nav class="story-tabs" role="tablist" aria-label="모션 예제 선택"><span>FICTIONAL MOTION STUDIES</span></nav>
<section id="story-panel" role="tabpanel" aria-labelledby="story-title">
<div class="story-screen"><svg id="story-svg" viewBox="0 0 1280 720" role="img" aria-label="가상 업무 흐름 모션 그래픽"></svg>
<header class="story-head"><p class="story-eyebrow" id="story-eyebrow"></p><h1 id="story-title"></h1><p class="story-lead" id="story-lead"></p></header>
<footer class="story-captions"><p class="phase-caption"><small id="phase-number"></small><span id="phase-label"></span></p><div class="story-metric"><div class="metric-value" id="metric-value"></div><p class="metric-label" id="metric-label"></p></div></footer></div>
<nav class="story-controls" aria-label="동영상형 모션 재생 조작"><button type="button" id="toggle-play" aria-pressed="false">▶ 재생</button><button type="button" id="prev-phase" aria-label="이전 설명 단계">←</button><button type="button" id="next-phase" aria-label="다음 설명 단계">→</button><input type="range" id="timeline" aria-label="모션 타임라인 탐색" min="0" value="0" step="0.05"><span class="timecode" id="timecode"></span><button type="button" id="restart">다시 보기 ↺</button><button type="button" id="motion-mode" aria-pressed="false">모션 끄기</button><button type="button" id="print-stories">인쇄 / PDF</button></nav>
<nav class="phase-nav" aria-label="설명 단계 선택"></nav><p id="story-note" class="story-note"></p></section>
<aside id="story-print-toolbar"><p>세 예제의 핵심 정보 · A4 가로 · 인쇄 창에서 PDF 저장을 선택하세요.</p><button type="button" id="story-print-confirm">인쇄 / PDF로 저장</button><button type="button" id="story-print-close">데모로 돌아가기</button></aside>
<div id="story-summaries">{summaries(config)}</div><p id="story-status" class="sr-only" role="status" aria-live="polite"></p></main>
<script id="stories-data" type="application/json">{data}</script><script>{js}</script></body></html>'''
    if config.get('language') == 'en':
        from motion_locale import english
        # Translate only the UI/runtime, leaving data and legal notices untouched.
        before, rest = output.split('<script id="stories-data"', 1)
        data_block, runtime = rest.split('<script>', 1)
        output = english(before).replace('lang="ko"', 'lang="en"') + '<script id="stories-data"' + data_block + '<script>' + english(runtime)
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        output=build(json.loads(args.input.read_text(encoding='utf-8-sig')))
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output,encoding='utf-8',newline='\n')
    except (OSError,ValueError) as error:
        parser.exit(1,f'Build failed: {error}\n')
    print(f'Built motion gallery: {args.output} ({len(output.encode("utf-8")):,} bytes)')


if __name__=='__main__':
    main()
