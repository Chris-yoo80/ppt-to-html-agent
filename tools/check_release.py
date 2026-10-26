"""Check local page references, generated demo and explicit skill package contents.

Static verification only. This does not render a page or certify privacy.
"""
import json
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/ppt-to-html/scripts'))
from build_deck import build
from build_motion_demo import build as build_motion
from build_marketing_examples import outputs as marketing_outputs
from build_full_presentation import outputs as full_presentation_outputs
from build_guides import build as build_guide


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=set()

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for attribute in ('href','src'):
            if attribute in attrs:
                self.links.append((tag,attrs[attribute]))


def main():
    problems=[]
    license_bytes = (ROOT/'LICENSE').read_bytes()
    for copy in (ROOT/'skills/ppt-to-html/LICENSE', ROOT/'docs/license.txt'):
        if copy.read_bytes() != license_bytes:
            problems.append(f'license copy differs: {copy.relative_to(ROOT)}')
    pages=list((ROOT/'docs').glob('*.html'))
    parsed={}
    for page in pages:
        parser=References(); parser.feed(page.read_text(encoding='utf-8')); parsed[page]=parser
    links=0
    for page, parser in parsed.items():
        for tag, raw in parser.links:
            url=urlsplit(raw)
            if url.scheme or url.netloc:
                if tag!='a':
                    problems.append(f'{page.name}: external resource {raw}')
                continue
            links+=1
            target=(page.parent/unquote(url.path)).resolve() if url.path else page
            if not target.is_relative_to(ROOT):
                problems.append(f'{page.name}: reference leaves public root')
            elif not target.is_file():
                problems.append(f'{page.name}: missing local target {raw}')
            elif url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                problems.append(f'{page.name}: missing anchor {raw}')
    expected=build_motion(json.loads((ROOT/'examples/motion-stories/stories.json').read_text(encoding='utf-8')))
    if (ROOT/'docs/demo.html').read_text(encoding='utf-8')!=expected:
        problems.append('demo.html does not match current source')
    english=build_motion(json.loads((ROOT/'examples/motion-stories/stories.en.json').read_text(encoding='utf-8')))
    if (ROOT/'docs/demo.en.html').read_text(encoding='utf-8')!=english:
        problems.append('demo.en.html does not match current source')
    if __import__('re').search('[가-힣]',__import__('re').sub(r'data:font/woff2;base64,[A-Za-z0-9+/=]+','',english)):
        problems.append('English motion gallery contains untranslated Korean')
    if 'Presentation Output Exception' not in expected or license_bytes.decode('utf-8') not in expected:
        problems.append('generated presentation is missing its output license or notice')
    if (ROOT/'docs/library-demo.html').read_text(encoding='utf-8') != build(json.loads((ROOT/'examples/library/deck.json').read_text(encoding='utf-8'))):
        problems.append('library-demo.html does not match current source')
    for filename,expected_content in marketing_outputs().items():
        if (ROOT/filename).read_text(encoding='utf8')!=expected_content:problems.append(f'stale marketing artifact: {filename}')
    for filename,expected_content in full_presentation_outputs().items():
        if (ROOT/filename).read_text(encoding='utf8')!=expected_content:problems.append(f'stale complete presentation artifact: {filename}')
    for language in ['ko','en']:
        for filename in [f'docs/guide.{language}.html',f'skills/ppt-to-html/assets/guide.{language}.html']:
            if (ROOT/filename).read_text(encoding='utf8')!=build_guide(language):problems.append(f'stale HTML guide: {filename}')
    skill=ROOT/'skills/ppt-to-html'
    source_files={p.relative_to(skill).as_posix():p for p in skill.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    package=ROOT/'docs/downloads/ppt-to-html.zip'
    with zipfile.ZipFile(package) as archive:
        members=archive.namelist()
        expected_names={'ppt-to-html/'+name for name in source_files}
        if set(members)!=expected_names or len(members)!=len(expected_names):
            problems.append('skill ZIP does not match the explicit public skill tree')
        for name,path in source_files.items():
            entry='ppt-to-html/'+name
            content = path.read_bytes() if path.suffix == '.woff2' else path.read_text(encoding='utf-8').encode('utf-8')
            if entry in members and archive.read(entry)!=content:
                problems.append(f'stale ZIP entry: {name}')
    if problems:
        for problem in problems:
            print('FAIL:',problem)
        return 1
    print(f'PASS: {len(pages)} HTML pages, {links} local references, deterministic demo and {len(source_files)} ZIP entries.')
    print('Browser rendering, actual host execution and public deployment are not covered.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
