"""Bundle a review page with its fictional demo for an inline chat attachment.

This is an artifact export, not browser verification or a public deployment.
"""
import argparse
import base64
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def data_url(kind, content):
    return 'data:' + kind + ';base64,' + base64.b64encode(content).decode('ascii')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    docs = ROOT / 'docs'
    page = (docs/'index.html').read_text(encoding='utf-8')
    page = page.replace('<link rel="stylesheet" href="site.css">', '<style>' + (docs/'site.css').read_text(encoding='utf-8') + '</style>')
    typography = (docs/'typography.css').read_text(encoding='utf-8')
    for weight in ('regular','bold'):
        name=f'story-sans-{weight}.woff2'
        typography=typography.replace('fonts/'+name, data_url('font/woff2',(docs/'fonts'/name).read_bytes()))
    page = page.replace('<link rel="stylesheet" href="typography.css">', '<style>' + typography + '</style>')
    page = page.replace('<script src="site.js" defer></script>', '')
    demo = (docs/'demo.html').read_text(encoding='utf-8')
    page = page.replace('src="demo.html"', 'srcdoc="' + html.escape(demo, quote=True) + '"')
    page = page.replace('href="demo.html" target="_blank" rel="noopener"', 'href="#demo" data-expand-demo')
    page = page.replace('href="demo.html" download=', 'href="#demo" data-download-demo download=')
    page = page.replace('href="downloads/ppt-to-html.zip"', 'href="' + data_url('application/zip', (docs/'downloads/ppt-to-html.zip').read_bytes()) + '"')
    page = page.replace('href="license.html"', 'href="#review-license"')
    page = page.replace('href="https://github.com/Chris-yoo80/ppt-to-html-agent"', 'href="#review-status"')
    banner = '<aside id="review-status" class="wrap" style="padding-top:16px;padding-bottom:16px;background:#e9eddf;font-size:13px;line-height:1.8">검토용 미리보기입니다. GitHub 업로드·공개 배포는 아직 하지 않았습니다. 아래에서 가상 데모를 조작하고 시작 요청문을 만들어볼 수 있습니다.</aside>'
    page = page.replace('<main id="main">', '<main id="main">' + banner)
    legal = '<section class="wrap" style="padding-bottom:30px"><details id="review-license"><summary>Community License 1.0 · 라이선스 전문 보기</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.7">' + html.escape((ROOT/'LICENSE').read_text(encoding='utf-8')) + '</pre></details></section>'
    font_notice = (docs/'fonts/NOTICE.txt').read_text(encoding='utf-8') + '\n' + (docs/'fonts/OFL.txt').read_text(encoding='utf-8')
    legal += '<section class="wrap" style="padding-bottom:30px"><details><summary>글꼴 출처 및 SIL OFL 1.1</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.7">' + html.escape(font_notice) + '</pre></details></section>'
    preview_js = '''
document.querySelector('[data-download-demo]').addEventListener('click',event=>{
  event.preventDefault();
  const blob=new Blob([document.querySelector('.after-panel iframe').srcdoc],{type:'text/html;charset=utf-8'});
  const url=URL.createObjectURL(blob), link=document.createElement('a');
  link.href=url;link.download='motion-stories.html';document.body.append(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),30000);
});
document.querySelector('[data-expand-demo]').addEventListener('click',event=>{
  event.preventDefault();
  const comparison=document.querySelector('.comparison');
  const expanded=comparison.dataset.expanded!=='true';
  comparison.dataset.expanded=String(expanded);
  comparison.style.gridTemplateColumns=expanded?'1fr':'';
  const before=document.querySelector('.before-panel');if(before)before.style.display=expanded?'none':'';
  const frame=document.querySelector('.after-panel iframe');
  frame.style.height=expanded?'980px':''; frame.style.flex=expanded?'none':'';
  event.currentTarget.textContent=expanded?'기본 크기로 ↙':'크게 열기 ↗';
});
'''
    page = page.replace('</body>', legal + '<script>' + (docs/'site.js').read_text(encoding='utf-8') + preview_js + '</script></body>')
    size = len(page.encode('utf-8'))
    if size >= 512 * 1024:
        raise ValueError('Inline preview exceeds 512 KiB')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding='utf-8', newline='\n')
    print(f'Created self-contained review artifact: {args.output.name} ({size:,} bytes)')


if __name__ == '__main__':
    main()
