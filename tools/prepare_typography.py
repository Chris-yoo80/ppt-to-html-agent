"""Prepare offline review fonts from Pretendard 1.3.9 (optional build tooling).

Requires fonttools and brotli, installable into .font-build. Runtime helpers
continue to require only the standard library. Modified subset fonts use the
new family name Story Sans and retain the original OFL license.
"""
import argparse
import json
from pathlib import Path
import shutil
import string
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.font-build'
FONTS = ROOT / 'skills/ppt-to-html/assets/fonts'
WEB_FONTS = ROOT / 'docs/fonts'
FONT_URL = 'https://raw.githubusercontent.com/orioncactus/pretendard/v1.3.9/packages/pretendard/dist/web/variable/woff2/PretendardVariable.woff2'
LICENSE_URL = 'https://raw.githubusercontent.com/orioncactus/pretendard/v1.3.9/LICENSE'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    CACHE.mkdir(exist_ok=True)
    source = CACHE/'PretendardVariable.woff2'
    license_path = CACHE/'PRETENDARD-OFL.txt'
    if args.download:
        for url, destination in [(FONT_URL, source), (LICENSE_URL, license_path)]:
            with urlopen(url, timeout=60) as response:
                destination.write_bytes(response.read())
    if not source.is_file() or not license_path.is_file():
        parser.error('Font source missing. Run again with --download.')
    sys.path.insert(0, str(CACHE))
    from fontTools.ttLib import TTFont
    from fontTools import subset
    from fontTools.varLib.instancer import instantiateVariableFont
    text = string.printable
    for path in [*ROOT.glob('docs/*.html'), ROOT/'docs/site.js', *ROOT.glob('examples/**/*.json'),
                 *ROOT.glob('skills/ppt-to-html/assets/*.js')]:
        text += path.read_text(encoding='utf-8')
    FONTS.mkdir(parents=True, exist_ok=True)
    WEB_FONTS.mkdir(parents=True, exist_ok=True)
    codepoints=set(ord(char) for char in text)
    for weight, name in [(400, 'Regular'), (700, 'Bold')]:
        font=TTFont(source)
        font=instantiateVariableFont(font, {'wght':weight}, inplace=True)
        options=subset.Options()
        options.name_IDs=['*']
        options.name_legacy=True
        options.name_languages=['*']
        subsetter=subset.Subsetter(options=options)
        subsetter.populate(unicodes=codepoints)
        subsetter.subset(font)
        replacements={1:'Story Sans',2:name,3:'StorySans-'+name+'-Review-1',
                      4:'Story Sans '+name,6:'StorySans-'+name,16:'Story Sans',17:name}
        for record in font['name'].names:
            if record.nameID in replacements:
                record.string=replacements[record.nameID].encode(record.getEncoding())
        font.flavor='woff2'
        destination=FONTS/f'story-sans-{name.lower()}.woff2'
        font.save(destination)
        shutil.copyfile(destination,WEB_FONTS/destination.name)
    for directory in (FONTS,WEB_FONTS):
        shutil.copyfile(license_path,directory/'OFL.txt')
    notice=('Story Sans review subsets, derived from Pretendard 1.3.9.\n'
            'Source: '+FONT_URL+'\n'
            'Subset and renamed for the current public demo; original glyph shapes retained.\n'
            'Font files remain under SIL OFL 1.1, not the project Community License.\n'
            'Only current demo characters are bundled. Other characters use the system fallback.\n')
    for directory in (FONTS,WEB_FONTS):
        (directory/'NOTICE.txt').write_text(notice,encoding='utf-8',newline='\n')
    (FONTS/'coverage.json').write_text(json.dumps(sorted(codepoints)),encoding='utf-8')
    print('Prepared Story Sans regular/bold, OFL notices, and website copies.')
    for path in FONTS.glob('*.woff2'):
        print(path.name, path.stat().st_size, 'bytes')


if __name__=='__main__':
    main()
