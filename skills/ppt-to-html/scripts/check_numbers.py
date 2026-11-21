"""Recompute every derived number from source values and confirm the slides show it.

  python check_numbers.py work/deck.json work/numbers.json

numbers.json lists the source values (with where they came from) and one check per derived figure:

  {"values": {"revenue": {"value": 45000, "source": "slide 7"}, "spend": {"value": 12000, "source": "slide 7"}},
   "checks": [{"scene": "summary", "label": "ROAS", "expr": "revenue / spend * 100",
               "decimals": 0, "suffix": "%", "show": "375%"}]}

For each check the expression is evaluated (numbers, value names, + - * / and parentheses, abs/min/max/round),
rounded half-up to `decimals`, formatted with thousands separators plus optional `prefix`, `suffix` and
`sign` ("+" on positive results), and compared with `show`. `show` must also appear on the named scene
(`scene: "*"` searches the whole deck). It then lists numbers on each slide that no check or source value
accounts for; review those by hand. Exit code 1 when a check fails.
"""
import argparse
import ast
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

FUNCTIONS = {'abs': abs, 'min': min, 'max': max, 'round': round}
OPERATORS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b}
NUMBER = re.compile(r'[+−-]?\d[\d,]*(?:\.\d+)?%?')


def evaluate(expr, values):
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in values:
                raise ValueError(f'unknown value "{node.id}"')
            return values[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = walk(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS and not node.keywords:
            return FUNCTIONS[node.func.id](*[walk(arg) for arg in node.args])
        raise ValueError(f'unsupported expression part: {ast.dump(node)[:60]}')
    return walk(ast.parse(expr, mode='eval'))


def formatted(value, check):
    decimals = int(check.get('decimals', 0))
    rounded = Decimal(str(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    text = f'{abs(rounded):,.{decimals}f}' if check.get('commas', True) else f'{abs(rounded):.{decimals}f}'
    sign = '-' if rounded < 0 else ('+' if check.get('sign') and rounded > 0 else '')
    if rounded < 0 and check.get('minus') == 'unicode':
        sign = '−'
    return f"{check.get('prefix', '')}{sign}{text}{check.get('suffix', '')}"


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        self.parts.append(' ')
        for name, value in attrs:
            if name == 'data-chart' and value:  # chart labels are on the slide too
                self.parts.append(' ' + value + ' ')


def scene_text(scene):
    parser = Text()
    parser.feed(scene.get('html', ''))
    fields = [scene.get(key, '') for key in ('eyebrow', 'title', 'lead', 'message', 'source')]
    items = [f"{item.get('value', '')} {item.get('label', '')} {item.get('body', '')}" for item in scene.get('items', [])]
    chart = [json.dumps(scene['chart'], ensure_ascii=False)] if scene.get('chart') else []
    return ' '.join(fields + items + chart + parser.parts).replace('**', '')


def squash(text):
    return re.sub(r'\s+', ' ', text)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('deck', type=Path)
    parser.add_argument('numbers', type=Path)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    deck = json.loads(args.deck.read_text(encoding='utf-8'))
    spec = json.loads(args.numbers.read_text(encoding='utf-8'))
    values = {name: (entry['value'] if isinstance(entry, dict) else entry) for name, entry in spec.get('values', {}).items()}
    texts = {scene['id']: squash(scene_text(scene)) for scene in deck['scenes']}
    everything = ' '.join(texts.values())
    failures, shown = 0, set()
    print('| scene | figure | recomputed | shown | on slide | result |\n|---|---|---|---|---|---|')
    for check in spec.get('checks', []):
        scene, label, show = check.get('scene', '*'), check.get('label', check.get('expr', '')), check.get('show', '')
        try:
            expected = formatted(evaluate(check['expr'], values), check)
            error = ''
        except (KeyError, ValueError, ZeroDivisionError, TypeError, SyntaxError) as problem:
            expected, error = '—', str(problem)
        haystack = everything if scene == '*' else texts.get(scene)
        on_slide = haystack is not None and squash(show) in haystack
        ok = not error and expected == show and on_slide
        failures += not ok
        shown.add(show)
        reason = error or ('' if expected == show else 'recomputed value differs') or ('' if on_slide else 'not found on the slide' if haystack is not None else 'unknown scene')
        print(f"| {scene} | {label} | {expected} | {show} | {'yes' if on_slide else 'no'} | {'pass' if ok else 'FAIL: ' + reason} |")
    known = {formatted(value, {'decimals': decimals}) for value in values.values() for decimals in (0, 1, 2)}
    known |= {str(value) for value in values.values()}
    # Whole-number match: "1,000" is not covered just because "11,000" was checked.
    covered = {token.lstrip('+−-').rstrip('%') for text in list(shown) + list(known) for token in NUMBER.findall(text)}
    print('\nNumbers on slides that no check or source value accounts for (review by hand):')
    unchecked = 0
    for scene_id, text in texts.items():
        tokens = []
        for token in NUMBER.findall(text):
            core = token.lstrip('+−-')
            if (',' in core or '.' in core or core.endswith('%') or len(core) >= 3) and core.rstrip('%') not in covered and token not in tokens:
                tokens.append(token)
        if tokens:
            unchecked += len(tokens)
            print(f"- {scene_id}: {', '.join(tokens[:12])}{' …' if len(tokens) > 12 else ''}")
    if not unchecked:
        print('- none')
    print(f"\n{len(spec.get('checks', []))} checks, {failures} failed, {unchecked} unchecked numbers to review.")
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
