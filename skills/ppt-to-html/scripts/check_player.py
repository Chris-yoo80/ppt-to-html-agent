"""Operate a built presentation in a real browser and report which playback behaviors work.

  python check_player.py output/presentation.html

Uses a local Edge/Chrome/Chromium (same as capture_steps.py) and real key presses and clicks to check:
next/previous through every step, Home/End, the end behavior, the Contents panel, question marks and return,
every backup jump and its exact return, step links, print preview (all scenes, step kept), autoplay start and
stop, and that no script error occurred. Exit code 1 when a check fails. This does not judge layout or
content; look at the capture_steps.py screenshots for that.
"""
import argparse
import json
import sys
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling modules also load under python -I
from capture_steps import Browser, find_browser

KEYS = {'ArrowRight': 39, 'ArrowLeft': 37, 'Home': 36, 'End': 35, 'Escape': 27, 'Backspace': 8, 'g': 71, 'b': 66, 'r': 82, 'a': 65}


class Player:
    def __init__(self, browser):
        self.browser = browser

    def js(self, expression):
        return self.browser.evaluate(expression)

    def key(self, key, wait=0.15):
        text = key if len(key) == 1 else ''
        for kind in ('keyDown', 'keyUp'):
            params = {'type': kind, 'key': key, 'code': f'Key{key.upper()}' if text else key, 'windowsVirtualKeyCode': KEYS[key]}
            if kind == 'keyDown' and text:
                params['text'] = text
            self.browser.call('Input.dispatchKeyEvent', **params)
        time.sleep(wait)

    def click(self, selector, wait=0.25):
        self.js(f"document.querySelector({json.dumps(selector)}).click()")
        time.sleep(wait)

    def position(self):
        return self.js('__pptPlayer.current().position')

    def scene(self):
        return self.js('__pptPlayer.deck.scenes[__pptPlayer.current().sceneIndex].id')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('html')
    parser.add_argument('--browser', help='path to Edge/Chrome/Chromium')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    from pathlib import Path
    url = Path(args.html).resolve().as_uri()
    browser = Browser(find_browser(args.browser), 1600, 1000)
    results = []

    def check(name, ok, detail=''):
        results.append((name, bool(ok), detail))

    try:
        browser.call('Page.enable')
        browser.call('Runtime.enable')
        browser.call('Page.navigate', url=url)
        for _ in range(50):
            if browser.evaluate('Boolean(globalThis.__pptPlayer)'):
                break
            time.sleep(0.2)
        time.sleep(0.5)  # first paint and fonts on a cold browser
        p = Player(browser)
        if not p.js('Boolean(globalThis.__pptPlayer)'):
            raise SystemExit('This file has no ppt-to-html player (built with an older skill?).')
        steps = p.js('__pptPlayer.steps()')
        main_count = sum(1 for step in steps if not step['backup'])
        settings = p.js('__pptPlayer.deck.settings || {}')

        p.key('Home')
        seen = [p.position()]
        for _ in range(main_count + 1):
            before = p.position()
            p.key('ArrowRight', 0.05)
            for _ in range(20):  # wait for the step to settle instead of trusting a fixed pause
                if p.position() != before:
                    break
                time.sleep(0.05)
            seen.append(p.position())
        expected = list(range(main_count)) + [main_count - 1] * 2 if settings.get('end', 'stop') == 'stop' else None
        if expected:
            check('Next walks every main step once and stops at the end', seen == expected, f'{seen[:4]}…{seen[-3:]}')
            check('Next button is disabled at the end', p.js("document.getElementById('next').disabled"))
        else:
            check('Next walks every main step and loops to the start', seen[:main_count] == list(range(main_count)) and seen[main_count] == 0)
        p.key('End')
        p.key('ArrowLeft')
        check('Previous goes back one step', p.position() == main_count - 2, str(p.position()))
        p.key('Home')
        check('Home opens the first step', p.position() == 0)
        p.key('End')
        check('End opens the last main step', p.position() == main_count - 1)

        p.key('Home')
        p.key('g', 0.3)
        opened = p.js("document.getElementById('outline-dialog').open")
        buttons = p.js("document.querySelectorAll('#outline-list button').length")
        p.js("[...document.querySelectorAll('#outline-list button')].at(-1).click()")
        time.sleep(0.3)
        check('Contents (G) opens, lists steps and jumps', opened and buttons >= main_count and p.position() != 0 and not p.js("document.getElementById('outline-dialog').open"),
              f'{buttons} entries')

        target = min(main_count - 1, max(1, main_count // 2))
        p.js(f'__pptPlayer.go({target})')
        time.sleep(0.2)
        p.key('b')
        p.key('Home')
        p.key('r', 0.3)
        check('Question mark (B) and return (R) come back to the exact step', p.position() == target, f'{p.position()} vs {target}')

        gotos = p.js("""(() => { const out = [];
          __pptPlayer.deck.scenes.forEach(scene => { const walk = nodes => (nodes || []).forEach(n => {
            if (Array.isArray(n)) { const [, attrs, children] = n; if (attrs && attrs['data-goto']) out.push([scene.id, attrs['data-goto']]); walk(children); } });
            walk(scene.body); }); return out; })()""") or []
        for source, goal in gotos:
            start = p.js(f"__pptPlayer.firstStep({json.dumps(source)})")
            last = start + p.js(f"__pptPlayer.labelsOf(__pptPlayer.deck.scenes.find(s => s.id === {json.dumps(source)})).length") - 1
            p.js(f'__pptPlayer.go({last})')
            time.sleep(0.25)
            p.click(f'#stage [data-goto="{goal}"]')
            arrived = p.scene() == goal
            p.click('#return-origin')
            check(f'Jump {source} → {goal} and Back returns to the same step', arrived and p.position() == last, f'arrived={arrived}, back at {p.position()} vs {last}')
        if not gotos:
            check('Backup jumps', True, 'no data-goto buttons in this deck')

        probe = steps[min(len(steps) - 1, 2)]
        p.js(f"location.hash = '#scene={probe['scene']}&step={probe['step']}'")
        time.sleep(0.4)
        check('A step link (#scene=…&step=…) opens that step', p.scene() == probe['scene'] and p.js('__pptPlayer.current().itemIndex') + 1 == probe['step'])

        before = p.position()
        p.click('#print', 0.6)
        pages = p.js("document.querySelectorAll('#print-pages .print-page').length")
        scenes = len(p.js('__pptPlayer.deck.scenes'))
        p.click('#print-close', 0.4)
        check('Print preview has every scene and keeps the current step', pages == scenes and p.position() == before, f'{pages} pages / {scenes} scenes')

        if settings.get('playback', 'manual') != 'manual':
            p.key('Home')
            p.key('a', 0.3)
            playing = p.js("document.getElementById('play').getAttribute('aria-pressed')") == 'true'
            p.key('a', 0.3)
            stopped = p.js("document.getElementById('play').getAttribute('aria-pressed')") == 'false'
            check('Autoplay (A) starts and stops', playing and stopped)
        check('Presenter view button is present', p.js("Boolean(document.getElementById('presenter'))"))
        errors = [event for event in browser.events if event.get('method') == 'Runtime.exceptionThrown']
        check('No script errors', not errors, '; '.join(e['params']['exceptionDetails'].get('text', '') for e in errors[:3]))
    finally:
        browser.close()

    failed = [name for name, ok, _ in results if not ok]
    print('| check | result | detail |\n|---|---|---|')
    for name, ok, detail in results:
        print(f"| {name} | {'pass' if ok else 'FAIL'} | {detail} |")
    print(f'\n{len(results)} checks, {len(failed)} failed. Layout, wording and timing on the real display still need a person.')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
