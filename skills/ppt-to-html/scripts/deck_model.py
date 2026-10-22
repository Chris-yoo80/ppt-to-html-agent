"""Validate the small, portable scene format used by the bundled player."""
import math


def validate_deck(deck):
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    def string(value, location):
        require(isinstance(value, str) and value.strip(), f'{location}: nonempty text required')

    require(isinstance(deck, dict), 'deck must be an object')
    string(deck.get('title'), 'title')
    settings = deck.get('settings', {})
    require(isinstance(settings, dict), 'settings must be an object')
    for name, default in [('width', 1600), ('height', 900)]:
        value = settings.get(name, default)
        require(type(value) is int and 320 <= value <= 7680, f'{name}: integer from 320 to 7680 required')
    require(settings.get('motion', 'key') in ('none', 'key', 'rich'), 'motion: none, key or rich required')
    require(settings.get('playback', 'manual') in ('manual', 'both', 'auto'), 'playback: manual, both or auto required')
    require(settings.get('end', 'stop') in ('stop', 'loop'), 'end: stop or loop required')
    require(settings.get('font', 'system') in ('system', 'serif', 'story'), 'font: system, serif or story required')
    scenes = deck.get('scenes')
    require(isinstance(scenes, list) and 1 <= len(scenes) <= 100, 'scenes: 1–100 scenes required')
    ids = set()
    for i, scene in enumerate(scenes):
        prefix = f'scenes[{i}]'
        require(isinstance(scene, dict), f'{prefix}: object required')
        string(scene.get('id'), prefix + '.id')
        require(scene['id'] not in ids, f'{prefix}: duplicate id')
        ids.add(scene['id'])
        string(scene.get('title'), prefix + '.title')
        string(scene.get('message'), prefix + '.message')
        require(scene.get('layout', 'cards') in ('cards', 'flow', 'compare'), f'{prefix}: unsupported layout')
        items = scene.get('items')
        require(isinstance(items, list) and 1 <= len(items) <= 4, f'{prefix}.items: 1–4 items required')
        for j, item in enumerate(items):
            require(isinstance(item, dict), f'{prefix}.items[{j}]: object required')
            string(item.get('label'), f'{prefix}.items[{j}].label')
            for optional in ('body', 'value'):
                require(optional not in item or isinstance(item[optional], str), f'{prefix}.items[{j}].{optional}: text required')
        for optional in ('eyebrow', 'lead', 'source', 'motion_caption'):
            require(optional not in scene or isinstance(scene[optional], str), f'{prefix}.{optional}: text required')
        require(scene.get('motion', 'none') in ('none', 'points', 'lines', 'planes'), f'{prefix}: unsupported motion')
        duration = scene.get('duration', 7)
        require(type(duration) in (int, float) and math.isfinite(duration) and 3 <= duration <= 120,
                f'{prefix}.duration: seconds from 3 to 120 required')
    return deck
