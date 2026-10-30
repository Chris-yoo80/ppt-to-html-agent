"""Validate the small, portable scene format used by the bundled player."""
import math

from scene_markup import MarkupError, check_css, parse_scene_html

THEMES = ('default', 'consulting', 'executive')
REVEALS = ('spotlight', 'build', 'none')


def validate_deck(deck):
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    def string(value, location):
        require(isinstance(value, str) and value.strip(), f'{location}: nonempty text required')

    require(isinstance(deck, dict), 'deck must be an object')
    string(deck.get('title'), 'title')
    require(deck.get('language','ko') in ('ko','en'), 'language: ko or en required')
    require('version' not in deck or (isinstance(deck['version'], str) and len(deck['version']) <= 24), 'version: text of at most 24 characters required')
    if 'css' in deck:
        require(isinstance(deck['css'], str) and len(deck['css'].encode('utf-8')) <= 200 * 1024, 'css: text of at most 200 KiB required')
        try:
            check_css(deck['css'], 'css')
        except MarkupError as error:
            raise ValueError(str(error)) from None
    supplements=deck.get('supplements',[])
    require(isinstance(supplements,list) and len(supplements)<=8,'supplements: at most eight HTML resources')
    supplement_ids=set()
    for item in supplements:
        require(isinstance(item,dict),'supplement must be an object')
        for key in ('id','label','html'):string(item.get(key),'supplement.'+key)
        require(item['id'] not in supplement_ids,'duplicate supplement id');supplement_ids.add(item['id'])
        require(len(item['html'].encode('utf8'))<=2*1024*1024,'supplement exceeds 2 MiB')
    settings = deck.get('settings', {})
    require(isinstance(settings, dict), 'settings must be an object')
    for name, default in [('width', 1600), ('height', 900)]:
        value = settings.get(name, default)
        require(type(value) is int and 320 <= value <= 7680, f'{name}: integer from 320 to 7680 required')
    require(settings.get('motion', 'key') in ('none', 'key', 'rich'), 'motion: none, key or rich required')
    require(settings.get('playback', 'manual') in ('manual', 'both', 'auto'), 'playback: manual, both or auto required')
    require(settings.get('end', 'stop') in ('stop', 'loop'), 'end: stop or loop required')
    require(settings.get('font', 'system') in ('system', 'serif', 'story'), 'font: system, serif or story required')
    require(settings.get('theme', 'default') in THEMES, 'theme: default, consulting or executive required')
    require(type(settings.get('review', True)) is bool, 'review: true or false required')
    scenes = deck.get('scenes')
    require(isinstance(scenes, list) and 1 <= len(scenes) <= 100, 'scenes: 1–100 scenes required')
    ids = set()
    gotos = []
    for i, scene in enumerate(scenes):
        prefix = f'scenes[{i}]'
        require(isinstance(scene, dict), f'{prefix}: object required')
        string(scene.get('id'), prefix + '.id')
        require(scene['id'] not in ids, f'{prefix}: duplicate id')
        ids.add(scene['id'])
        string(scene.get('title'), prefix + '.title')
        string(scene.get('message'), prefix + '.message')
        if 'html' in scene:
            validate_composed(scene, prefix, require, string, gotos)
        else:
            require(scene.get('layout', 'cards') in ('cards', 'flow', 'compare'), f'{prefix}: unsupported layout')
            items = scene.get('items')
            require(isinstance(items, list) and 1 <= len(items) <= 4, f'{prefix}.items: 1–4 items required (or write a composed scene with html + steps)')
            for j, item in enumerate(items):
                require(isinstance(item, dict), f'{prefix}.items[{j}]: object required')
                string(item.get('label'), f'{prefix}.items[{j}].label')
                for optional in ('body', 'value'):
                    require(optional not in item or isinstance(item[optional], str), f'{prefix}.items[{j}].{optional}: text required')
            require(scene.get('motion', 'none') in ('none', 'points', 'lines', 'planes'), f'{prefix}: unsupported motion')
            if 'chart' in scene:
                validate_chart(scene['chart'], prefix + '.chart', require, string)
        for optional in ('eyebrow', 'lead', 'source', 'motion_caption', 'message_label'):
            require(optional not in scene or isinstance(scene[optional], str), f'{prefix}.{optional}: text required')
        if 'chapter' in scene:
            require(isinstance(scene['chapter'], str) and 0 < len(scene['chapter'].strip()) <= 24, f'{prefix}.chapter: 1–24 characters required')
        require(type(scene.get('backup', False)) is bool, f'{prefix}.backup: true or false required')
        duration = scene.get('duration', 7)
        require(type(duration) in (int, float) and math.isfinite(duration) and 3 <= duration <= 120,
                f'{prefix}.duration: seconds from 3 to 120 required')
    require(any(not scene.get('backup') for scene in scenes), 'scenes: at least one non-backup scene required')
    for location, target in gotos:
        require(target in ids, f'{location}: data-goto="{target}" does not match any scene id')
    return deck


def validate_composed(scene, prefix, require, string, gotos):
    """A composed scene is agent-authored HTML whose [data-step] elements map to step labels."""
    require('items' not in scene and 'chart' not in scene, f'{prefix}: a composed scene uses html + steps; put charts inside it with data-chart')
    labels = scene.get('steps')
    require(isinstance(labels, list) and 1 <= len(labels) <= 12, f'{prefix}.steps: 1–12 step labels required')
    for j, label in enumerate(labels):
        string(label, f'{prefix}.steps[{j}]')
    require(scene.get('reveal', 'spotlight') in REVEALS, f'{prefix}.reveal: spotlight, build or none required')
    try:
        _, used, targets, charts = parse_scene_html(scene['html'], prefix + '.html')
    except MarkupError as error:
        raise ValueError(str(error)) from None
    expected = set(range(1, len(labels) + 1))
    if len(labels) > 1 or used:
        require(used == expected, f'{prefix}: data-step values {sorted(used)} must cover exactly 1–{len(labels)} (one per step label)')
    for k, chart in enumerate(charts):
        validate_chart(chart, f'{prefix}.html data-chart[{k}]', require, string)
    gotos.extend((prefix + '.html', target) for target in targets)


def composed_tree(scene):
    """Return the validated element tree the player renders for a composed scene."""
    return parse_scene_html(scene['html'], scene['id'])[0]


CHART_POINTS = {'bar': 8, 'line': 8, 'funnel': 6, 'donut': 6, 'waterfall': 10}


def validate_chart(chart, prefix, require, string):
    """Charts are drawn to scale from zero, so values must be finite and non-negative."""
    require(isinstance(chart, dict), f'{prefix}: object required')
    kind = chart.get('type')
    require(isinstance(kind, str) and kind in CHART_POINTS, f'{prefix}.type: bar, line, funnel, donut or waterfall required')
    data = chart.get('data')
    limit = CHART_POINTS[kind]
    minimum = 3 if kind == 'waterfall' else 2
    require(isinstance(data, list) and minimum <= len(data) <= limit, f'{prefix}.data: {minimum}–{limit} points required for {kind}')
    running = 0
    for k, point in enumerate(data):
        location = f'{prefix}.data[{k}]'
        require(isinstance(point, dict), f'{location}: object required')
        string(point.get('label'), location + '.label')
        # SVG text does not wrap; longer text overlaps neighbouring labels.
        require(len(point['label']) <= 12, f'{location}.label: at most 12 characters (shorten it; put detail in the item card)')
        value = point.get('value')
        require(type(value) in (int, float) and math.isfinite(value), f'{location}.value: finite number required')
        if kind == 'waterfall':
            # Waterfalls start from a total; deltas may be negative but the running total may not.
            step_kind = point.get('kind', 'total' if k == 0 else 'delta')
            require(step_kind in ('total', 'delta'), f'{location}.kind: total or delta required')
            require(k > 0 or step_kind == 'total', f'{location}.kind: a waterfall starts with a total')
            running = value if step_kind == 'total' else running + value
            require(value >= 0 or step_kind == 'delta', f'{location}.value: totals must be ≥ 0')
            require(running >= 0, f'{location}: the running total may not go below 0')
        else:
            require(value >= 0, f'{location}.value: finite number ≥ 0 required')
        require(kind != 'donut' or value > 0, f'{location}.value: donut slices must be greater than 0')
        require('display' not in point or (isinstance(point['display'], str) and len(point['display']) <= 14), f'{location}.display: text of at most 14 characters required')
    require(kind in ('donut', 'waterfall') or max(point['value'] for point in data) > 0, f'{prefix}.data: at least one value must be greater than 0')
    values = [point['value'] for point in data]
    require(kind != 'funnel' or all(a >= b for a, b in zip(values, values[1:])), f'{prefix}.data: funnel stages must not increase; use a bar chart instead')
    for optional in ('title', 'unit', 'note', 'center'):
        require(optional not in chart or isinstance(chart[optional], str), f'{prefix}.{optional}: text required')
