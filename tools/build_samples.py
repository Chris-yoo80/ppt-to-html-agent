"""Build the sample gallery in docs/samples/ (Korean + English) from examples/.

  python tools/build_samples.py           # rebuild sample HTML, downloads and gallery pages
  python tools/build_samples.py --media   # also refresh PDFs and thumbnails (needs Edge/Chrome)

Every sample is fictional. Sample HTML is rebuilt with the current skill so it always shows the
current player; PDFs and thumbnails are refreshed only with --media.
"""
import argparse
import copy
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/ppt-to-html/scripts'
sys.path.insert(0, str(SCRIPTS))
from build_deck import build  # noqa: E402

OUT = ROOT / 'docs/samples'
SAMPLES = [
    {'slug': 'lumi-q3', 'deck': 'examples/samples/lumi-q3/deck.json', 'pptx': 'examples/samples/lumi-q3/source.pptx',
     'supplements': [('채널 성과표', 'examples/samples/lumi-q3/supplement-channel.html')], 'thumb': 'conclusion',
     'ko': ('루미 텀블러 3분기 마케팅 결과', '보온 텀블러라는 제품에서 디자인을 끌어낸 덱. 목표선 위로 넘친 텀블러 게이지, 광고비와 매출을 같은 눈금에 맞댄 막대, 예산 비율 띠.',
            '내용에 맞춘 디자인 · frontend-design 스킬 활용'),
     'en': ('Lumi tumbler Q3 marketing results', 'Design drawn from the product itself: a tumbler gauge overflowing its target line, spend and revenue on one scale, a budget-share band.',
            'Content-led design with the frontend-design skill')},
    {'slug': 'saebom-round1', 'deck': 'examples/samples/saebom-round1/deck.json', 'pptx': 'examples/samples/saebom-round1/source.pptx', 'thumb': 'summary',
     'ko': ('새봄병원 외래 대기시간 단축 (1차)', '맥락 없는 AI가 스킬 지침만 읽고 만든 덱. 모든 대기시간을 같은 분 눈금자로, 민원 412건을 칸 그림으로 보여줍니다.',
            '맥락 없는 AI 제작 · 같은 원본 1차'),
     'en': ('Saebom hospital outpatient waits (run 1)', 'Built by a context-free agent from the skill alone: one minute ruler for every wait, 412 complaints as a square grid.',
            'Context-free agent, same source, run 1')},
    {'slug': 'saebom-round2', 'deck': 'examples/samples/saebom-round2/deck.json', 'pptx': 'examples/samples/saebom-round2/source.pptx', 'thumb': 'summary',
     'ko': ('새봄병원 외래 대기시간 단축 (2차)', '같은 원본을 다른 AI가 개선된 스킬로 다시 만든 덱. 병원 층별 안내선처럼 접수·진료·수납을 색으로 이어 전체를 통일했습니다.',
            '맥락 없는 AI 제작 · 같은 원본 2차'),
     'en': ('Saebom hospital outpatient waits (run 2)', 'The same source rebuilt by another agent with the improved skill, using hospital floor-guide colours for reception, consultation and payment.',
            'Context-free agent, same source, run 2')},
    {'slug': 'parts-center-consulting', 'deck': 'examples/composed-report/deck.json', 'thumb': 'investment', 'theme': 'consulting',
     'ko': ('부품센터 자동화 검토 (consulting 프리셋)', '구성형 장면 기능 예제. 한 화면 여러 패널, 워터폴, 간트, 자료실 바로가기와 정확한 단계로 돌아오기.',
            '기능 예제 · consulting 프리셋'),
     'en': ('Parts-center automation review (consulting preset)', 'Composed-scene feature example: multi-panel screens, waterfall, Gantt, backup jump and exact-step return.',
            'Feature example, consulting preset')},
    {'slug': 'parts-center-executive', 'deck': 'examples/composed-report/deck.json', 'thumb': 'operation', 'theme': 'executive',
     'ko': ('부품센터 자동화 검토 (executive 프리셋)', '같은 내용을 executive 프리셋으로. 스포트라이트 단계, 하단 장 탭, 시사점 막대.',
            '기능 예제 · executive 프리셋'),
     'en': ('Parts-center automation review (executive preset)', 'The same content with the executive preset: spotlight steps, bottom chapter tabs, insight bar.',
            'Feature example, executive preset')},
    {'slug': 'cafe-charts', 'deck': 'examples/chart-scenes/deck.json', 'thumb': 'app-funnel',
     'ko': ('카페 브랜드 분기 리뷰 (차트 장면)', '카드 장면 + 차트 예제. 막대·선·퍼널·도넛을 0부터 실제 비율로 그리고 단계마다 하나씩 강조합니다.',
            '기능 예제 · 차트 장면'),
     'en': ('Café brand quarterly review (chart scenes)', 'Card scenes with charts: bar, line, funnel and donut drawn to scale from zero, highlighted step by step.',
            'Feature example, chart scenes')},
]
EXISTING = [  # pages already on the site
    ('marketing-presentation', '발표 + 추가 자료(마케팅 분석)', 'Presentation with supporting analysis'),
    ('full-presentation', '처음부터 끝까지 7장 전체 발표', 'Complete seven-scene presentation'),
    ('monthly-report-2026-10', '월간 매출 리포트(같은 구조 반복)', 'Repeatable monthly sales report'),
    ('demo', '모션 갤러리(배송·마케팅·창고)', 'Motion gallery (delivery, marketing, warehouse)'),
]


def load_deck(sample):
    deck = json.loads((ROOT / sample['deck']).read_text(encoding='utf-8'))
    deck = copy.deepcopy(deck)
    if sample.get('theme'):
        deck.setdefault('settings', {})['theme'] = sample['theme']
    for label, path in sample.get('supplements', []):
        deck.setdefault('supplements', []).append({'id': f'additional-{len(deck["supplements"]) + 1}', 'label': label,
                                                   'html': (ROOT / path).read_text(encoding='utf-8')})
    return deck


def build_samples():
    """Write sample HTML and downloads; return {slug: (deck, steps, has_pdf, has_thumb)}."""
    info = {}
    for sample in SAMPLES:
        folder = OUT / sample['slug']
        folder.mkdir(parents=True, exist_ok=True)
        deck = load_deck(sample)
        (folder / 'presentation.html').write_text(build(deck), encoding='utf-8', newline='\n')
        source = json.loads((ROOT / sample['deck']).read_text(encoding='utf-8'))
        (folder / 'deck.json').write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        if sample.get('pptx'):
            shutil.copyfile(ROOT / sample['pptx'], folder / 'source.pptx')
        main = [scene for scene in deck['scenes'] if not scene.get('backup')]
        steps = sum(len(scene.get('steps') or scene.get('items') or []) for scene in main)
        info[sample['slug']] = (deck, len(main), len(deck['scenes']) - len(main), steps)
    return info


def refresh_media():
    """PDF + thumbnail per sample through the skill's capture tool (needs a local Chromium browser)."""
    for sample in SAMPLES:
        folder = OUT / sample['slug']
        shots = folder / '_shots'
        subprocess.run([sys.executable, str(SCRIPTS / 'capture_steps.py'), str(folder / 'presentation.html'), '--out', str(shots),
                        '--reduced', '--stage-only', '--width', '960', '--height', '622', '--wait', '0.6', '--pdf', str(folder / 'presentation.pdf')], check=True)
        thumb = next(path for path in sorted(shots.glob('*.png')) if f"-{sample['thumb']}-" in path.name)
        shutil.copyfile(thumb, folder / 'thumb.png')
        shutil.rmtree(shots)


STYLE = '''*{box-sizing:border-box}body{margin:0;background:#fff;color:#14181f;font:16px/1.6 "Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:40px 28px 64px}nav{display:flex;gap:18px;font-size:14px;margin-bottom:36px}nav a{color:#14181f}
h1{font-size:40px;line-height:1.2;letter-spacing:-.02em;margin:0 0 12px}.lead{font-size:18px;color:#4b5563;max-width:720px;margin:0 0 10px}
.note{font-size:14px;color:#6b7280;margin:0 0 36px}h2{font-size:22px;margin:48px 0 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:28px}
.card{display:flex;flex-direction:column;border:1px solid #e3e6ea;border-radius:12px;overflow:hidden;background:#fff}
.card>a.thumb{display:block;background:#eef1f4;aspect-ratio:16/9;overflow:hidden;border-bottom:1px solid #e3e6ea}.card img{display:block;width:100%;height:100%;object-fit:cover}
.body{padding:18px 20px 20px;display:flex;flex-direction:column;gap:8px;flex:1}.body h3{font-size:19px;margin:0;line-height:1.35}
.made{font-size:13px;color:#2457c5;font-weight:600;margin:0}.body p{margin:0;font-size:15px;color:#374151}
.facts{font-size:13px;color:#6b7280}.links{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto;padding-top:8px}
.links a{font-size:14px;text-decoration:none;color:#14181f;border:1px solid #cfd5dc;border-radius:7px;padding:6px 11px}
.links a.primary{background:#14181f;color:#fff;border-color:#14181f}.links a:hover{border-color:#14181f}
.links a:focus-visible,nav a:focus-visible{outline:3px solid #2457c5;outline-offset:2px}
ul.existing{padding-left:20px}ul.existing li{margin:6px 0}footer{margin-top:56px;font-size:13px;color:#6b7280;border-top:1px solid #e3e6ea;padding-top:18px}
@media(max-width:640px){h1{font-size:30px}main{padding:28px 18px}}'''


def gallery(language, info):
    en = language == 'en'
    t = lambda ko, english: english if en else ko
    other = 'index.html' if en else 'index.en.html'
    cards = []
    for sample in SAMPLES:
        slug = sample['slug']; folder = OUT / slug
        title, description, made = sample[language]
        deck, scenes, backups, steps = info[slug]
        facts = t(f'장면 {scenes}개 + 자료실 {backups}개, {steps}단계', f'{scenes} scenes + {backups} backup, {steps} steps') if backups else t(f'장면 {scenes}개, {steps}단계', f'{scenes} scenes, {steps} steps')
        links = [f'<a class="primary" href="{slug}/presentation.html">{t("발표 열기", "Open presentation")}</a>']
        if (folder / 'presentation.pdf').exists():
            links.append(f'<a href="{slug}/presentation.pdf">PDF</a>')
        if sample.get('pptx'):
            links.append(f'<a href="{slug}/source.pptx" download>{t("원본 PPT", "Source PPT")}</a>')
        links.append(f'<a href="{slug}/deck.json" download>{t("편집용 JSON", "Editable JSON")}</a>')
        thumb = (f'<a class="thumb" href="{slug}/presentation.html"><img src="{slug}/thumb.png" alt="{html.escape(title)}" loading="lazy"></a>'
                 if (folder / 'thumb.png').exists() else '')
        cards.append(f'<article class="card">{thumb}<div class="body"><p class="made">{html.escape(made)}</p><h3>{html.escape(title)}</h3>'
                     f'<p>{html.escape(description)}</p><p class="facts">{facts}</p><div class="links">{"".join(links)}</div></div></article>')
    suffix = '.en' if en else ''
    existing = ''.join(f'<li><a href="../{page}{suffix if page != "monthly-report-2026-10" or en else ""}.html">{html.escape(en_text if en else ko_text)}</a></li>'
                       for page, ko_text, en_text in EXISTING)
    return f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t("샘플 갤러리", "Sample gallery")} · PPT to HTML Agent</title><style>{STYLE}</style></head><body><main>
<nav><a href="../{'index.en.html' if en else 'index.html'}">{t("← 소개 페이지", "← Home")}</a><a href="{other}">{t("English", "한국어")}</a><a href="../{'guide.en.html' if en else 'guide.ko.html'}">{t("사용설명서", "User guide")}</a></nav>
<h1>{t("샘플 갤러리", "Sample gallery")}</h1>
<p class="lead">{t("ppt-to-html 스킬로 만든 발표입니다. 발표를 열어 화살표로 넘겨 보고, 원본 PPT와 비교해 보세요. 오른쪽 위 편집·메모 도구도 그대로 써볼 수 있습니다.", "Presentations made with the ppt-to-html skill. Open one, step through it with the arrow keys and compare it with the source PPT. The edit and memo tools in the top-right corner work here too.")}</p>
<p class="note">{t("모든 샘플은 새로 만든 가상 자료입니다. 실제 회사, 병원, 성과가 아닙니다.", "Every sample uses newly written fictional data. No real company, hospital or result.")}</p>
<div class="grid">{"".join(cards)}</div>
<h2>{t("사이트의 다른 예제", "More examples on the site")}</h2><ul class="existing">{existing}</ul>
<footer>{t("발표 결과물은 Community License 1.0의 발표물 예외에 따라 공유할 수 있습니다.", "Presentation outputs may be shared under the presentation output exception of Community License 1.0.")}</footer>
</main></body></html>'''


def outputs(info):
    return {OUT / 'index.html': gallery('ko', info), OUT / 'index.en.html': gallery('en', info)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--media', action='store_true', help='refresh PDFs and thumbnails with a local Edge/Chrome')
    args = parser.parse_args()
    info = build_samples()
    if args.media:
        refresh_media()
    for path, content in outputs(info).items():
        path.write_text(content, encoding='utf-8', newline='\n')
    print(f'Built {len(SAMPLES)} samples and the gallery in {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
