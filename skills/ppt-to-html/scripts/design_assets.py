"""Look up the free design assets bundled with the skill: Lucide icons and color palettes.

  python design_assets.py icons coffee cup        # find icons by name or tag (English words)
  python design_assets.py icon coffee --size 28   # print inline SVG to paste into a composed scene
  python design_assets.py palettes                # list palettes
  python design_assets.py palette Set2 5          # print a palette's colors

Icons are drawn with stroke="currentColor", so CSS `color` sets their color. Everything works offline.
Licenses: Lucide ISC (some icons MIT), ColorBrewer Apache-2.0 style with acknowledgement; the builder adds the
required notices to a deck that uses them. Do not read the JSON files directly; they are large.
"""
import argparse
import html
import json
from pathlib import Path
import sys

DESIGN = Path(__file__).resolve().parents[1] / 'assets/design'


def load(name):
    return json.loads((DESIGN / name).read_text(encoding='utf-8'))


def icon_svg(name, size=24, stroke=2, css_class=''):
    data = load('lucide-icons.json')
    if name not in data['icons']:
        raise SystemExit(f'No icon named "{name}". Search with: design_assets.py icons <words>')
    parts = []
    for tag, attrs in data['icons'][name][1]:
        attributes = ' '.join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in attrs.items())
        parts.append(f'<{tag} {attributes}/>')
    classes = ' '.join(filter(None, ['lucide', f'lucide-{name}', css_class]))
    return (f'<svg class="{html.escape(classes, quote=True)}" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + ''.join(parts) + '</svg>')


def search(words):
    icons = load('lucide-icons.json')['icons']
    words = [word.lower() for word in words]
    scored = []
    for name, (tags, _) in icons.items():
        score = 0
        for word in words:
            if word == name or word in name.split('-'):
                score += 3
            elif word in name:
                score += 2
            if word in tags:
                score += 2
            elif any(word in tag for tag in tags):
                score += 1
        if score:
            scored.append((-score, len(name), name, tags))
    return [(score, name, tags) for score, _, name, tags in sorted(scored)[:30]]


def palettes():
    data = load('palettes.json')
    rows = [(group, name, sorted(int(n) for n in sizes)) for group, schemes in data['colorbrewer'].items() for name, sizes in schemes.items()]
    return rows, data


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    find = sub.add_parser('icons', help='search icons by name or tag')
    find.add_argument('words', nargs='+')
    one = sub.add_parser('icon', help='print inline SVG for one icon')
    one.add_argument('name')
    one.add_argument('--size', type=int, default=24)
    one.add_argument('--stroke', type=float, default=2)
    one.add_argument('--class', dest='css_class', default='', help='extra CSS class')
    sub.add_parser('palettes', help='list palettes')
    show = sub.add_parser('palette', help='print one palette')
    show.add_argument('name', help='ColorBrewer scheme (e.g. Set2, Blues, RdBu), okabe-ito or viridis')
    show.add_argument('count', nargs='?', type=int, help='number of colors (ColorBrewer)')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    if args.command == 'icons':
        results = search(args.words)
        for _, name, tags in results:
            print(f"{name}  ({', '.join(tags[:8])})")
        if not results:
            print('No match. Try other English words (e.g. chart, money, user, truck, calendar).')
    elif args.command == 'icon':
        print(icon_svg(args.name, args.size, args.stroke, args.css_class))
    elif args.command == 'palettes':
        rows, data = palettes()
        for group, name, sizes in rows:
            print(f'{group:12} {name:10} {sizes[0]}–{sizes[-1]} colors')
        print(f"{'qualitative':12} {'okabe-ito':10} {len(data['okabe-ito'])} colors (color-blind safe)")
        print(f"{'sequential':12} {'viridis':10} {len(data['viridis'])} colors")
    else:
        rows, data = palettes()
        key = args.name.lower()
        if key in ('okabe-ito', 'viridis'):
            colors = data[key][:args.count] if args.count else data[key]
        else:
            match = [(group, name) for group, name, _ in rows if name.lower() == key]
            if not match:
                raise SystemExit(f'No palette "{args.name}". List them with: design_assets.py palettes')
            group, name = match[0]
            sizes = data['colorbrewer'][group][name]
            count = str(args.count or max(int(n) for n in sizes))
            if count not in sizes:
                raise SystemExit(f'{name} comes in {min(map(int, sizes))}–{max(map(int, sizes))} colors')
            colors = sizes[count]
            print(f'{group} · uses ColorBrewer (acknowledgement added to the deck automatically)')
        print(' '.join(colors))


if __name__ == '__main__':
    main()
