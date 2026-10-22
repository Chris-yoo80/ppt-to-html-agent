"""Build a self-contained HTML presentation from an agent-authored JSON outline."""
import argparse
import base64
import html
import json
from pathlib import Path

from deck_model import validate_deck

ASSETS = Path(__file__).resolve().parent.parent / 'assets'


def build(deck):
    validate_deck(deck)
    data = json.dumps(deck, ensure_ascii=False, allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    css = '\n'.join((ASSETS / name).read_text(encoding='utf-8') for name in ('player.css', 'motion.css'))
    js = (ASSETS / 'player.js').read_text(encoding='utf-8')
    license_text = (ASSETS.parent / 'LICENSE').read_text(encoding='utf-8')
    font_legal = ''
    if deck.get('settings', {}).get('font') == 'story':
        fonts = ASSETS / 'fonts'
        for weight, style in [(400, 'regular'), (700, 'bold')]:
            encoded = base64.b64encode((fonts / f'story-sans-{style}.woff2').read_bytes()).decode('ascii')
            css += f'\n@font-face{{font-family:"Story Sans";font-style:normal;font-weight:{weight};font-display:swap;src:url(data:font/woff2;base64,{encoded}) format("woff2")}}'
        css += '\n:root{font-family:"Story Sans","Malgun Gothic","Apple SD Gothic Neo",sans-serif;font-synthesis:none}'
        font_notice = (fonts / 'NOTICE.txt').read_text(encoding='utf-8') + '\n' + (fonts / 'OFL.txt').read_text(encoding='utf-8')
        font_legal = '<template id="font-license"><pre>' + html.escape(font_notice) + '</pre></template>'
    legal_notice = ('Copyright (c) 2026 Chris-yoo80. Embedded runtime from PPT to HTML Agent.\n'
                    'This completed presentation may be shared under the Presentation Output Exception.\n'
                    'Retain this notice and the license below. Standalone tool redistribution follows the Package terms.\n\n'
                    + license_text).replace('--', '- -')
    return f'''<!doctype html>
<!--
{legal_notice}
-->
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(deck['title'])}</title><style>{css}</style></head>
<body>{font_legal}<main id="viewport" aria-label="발표 화면"><section id="stage" aria-label="현재 발표 장면"></section></main>
<nav class="controls" aria-label="발표 조작"><button id="prev" type="button" aria-label="이전 단계">←</button>
<span id="position" role="status" aria-live="polite"></span><button id="next" type="button" aria-label="다음 단계">→</button>
<button id="play" type="button" aria-pressed="false">자동 재생</button><button id="replay" type="button">처음부터</button>
<button id="fullscreen" type="button">전체 화면</button><span class="keyhint">← → 단계 이동 · Home 처음 · A 재생</span></nav>
<p class="sr-only" id="announcement" role="status" aria-live="polite"></p>
<script type="application/json" id="deck-data">{data}</script><script>{js}</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='scene JSON, authored by the agent')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        output = build(json.loads(args.input.read_text(encoding='utf-8-sig')))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding='utf-8', newline='\n')
    except (ValueError, OSError) as error:
        parser.exit(1, f'Build failed: {error}\n')
    print(f'Built {args.output} ({len(output.encode("utf-8")):,} bytes)')


if __name__ == '__main__':
    main()
