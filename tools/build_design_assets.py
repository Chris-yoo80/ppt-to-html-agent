"""Regenerate the bundled free design assets (icons and palettes) from pinned, verified npm packages.

  python tools/build_design_assets.py            # download, verify integrity, write skills/ppt-to-html/assets/design/

Sources are pinned by version and checked against the npm registry's sha512 integrity before anything is read.
Package code is never executed: icon data comes from JSON files, and ColorBrewer colors are parsed from the
package's CSS. Each source's license text is copied next to the data.
"""
import base64
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'skills/ppt-to-html/assets/design'
LUCIDE = ('lucide-static', '1.70.0', 'sha512-A9UgY98g94IuHQY7rl7/AFwHX7T1qNpzryim+Kw5CGhdV2STobtBY+ib/Z44ohyqXEJB88gvXFAeJ87uOOHKLw==')
COLORBREWER = ('colorbrewer', '1.7.0', None)  # integrity read from the registry entry of this exact version
# Okabe & Ito (2008) color-universal-design set, and viridis (matplotlib, CC0) sampled at 10 stops.
OKABE_ITO = ['#000000', '#e69f00', '#56b4e9', '#009e73', '#f0e442', '#0072b2', '#d55e00', '#cc79a7']
VIRIDIS = ['#440154', '#482878', '#3e4989', '#31688e', '#26828e', '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725']


def package(name, version, integrity):
    meta = json.load(urllib.request.urlopen(f'https://registry.npmjs.org/{name}/{version}', timeout=60))
    expected = integrity or meta['dist']['integrity']
    data = urllib.request.urlopen(meta['dist']['tarball'], timeout=120).read()
    actual = 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode()
    if actual != expected:
        raise SystemExit(f'{name}@{version}: integrity mismatch')
    archive = tarfile.open(fileobj=io.BytesIO(data))
    return lambda path: archive.extractfile(f'package/{path}').read().decode('utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    read = package(*LUCIDE)
    nodes, tags = json.loads(read('icon-nodes.json')), json.loads(read('tags.json'))
    icons = {name: [tags.get(name, []), [[tag, {k: v for k, v in attrs.items() if k != 'key'}] for tag, attrs in nodes[name]]] for name in sorted(nodes)}
    (OUT / 'lucide-icons.json').write_text(json.dumps({'source': f'{LUCIDE[0]} {LUCIDE[1]}', 'license': 'ISC; icons derived from Feather are MIT (see LICENSE-lucide.txt)',
                                                       'viewBox': '0 0 24 24', 'icons': icons}, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
    (OUT / 'LICENSE-lucide.txt').write_text(read('LICENSE').replace('\r\n', '\n'), encoding='utf-8', newline='\n')

    read = package(*COLORBREWER)
    css = read('colorbrewer.css')
    schemes = {}
    for scheme, index, count, color in re.findall(r'\.([A-Za-z0-9]+) \.q(\d+)-(\d+)\{fill:(rgb\(\d+,\d+,\d+\))\}', css):
        r, g, b = map(int, re.findall(r'\d+', color))
        schemes.setdefault(scheme, {}).setdefault(count, {})[int(index)] = f'#{r:02x}{g:02x}{b:02x}'
    block = re.search(r'schemeGroups:\s*\{(.*?)\}', read('index.js'), re.S).group(1)
    groups = {group: re.findall(r'"([A-Za-z0-9]+)"', names) for group, names in re.findall(r'(\w+):\s*\[([^\]]*)\]', block)}
    palettes = {'colorbrewer': {group: {name: {count: [colors[i] for i in sorted(colors)] for count, colors in sorted(schemes[name].items(), key=lambda kv: int(kv[0]))}
                                        for name in names if name in schemes} for group, names in groups.items()},
                'okabe-ito': OKABE_ITO, 'viridis': VIRIDIS,
                'license': 'ColorBrewer: Apache-2.0 style license with acknowledgement (see LICENSE-colorbrewer.txt). Okabe-Ito and viridis: free to use (viridis CC0).'}
    (OUT / 'palettes.json').write_text(json.dumps(palettes, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
    (OUT / 'LICENSE-colorbrewer.txt').write_text(read('LICENSE.txt').replace('\r\n', '\n'), encoding='utf-8', newline='\n')
    print(f'{len(icons)} icons, {sum(len(v) for v in palettes["colorbrewer"].values())} ColorBrewer schemes written to {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
