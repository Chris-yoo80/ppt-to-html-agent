"""Screenshot every step of a built presentation, flag overflow and sparse slides, and optionally print a PDF.

Uses a locally installed Chromium browser (Edge or Chrome) over the DevTools protocol with the Python
standard library only. Each step is opened through the player's #scene=<id>&step=<n> link.

  python capture_steps.py output/presentation.html --out output/shots [--reduced] [--pdf output/deck.pdf]
"""
import argparse
import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
]
NAMES = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'msedge', 'chrome']

# Elements that leave the stage, or whose content is clipped by an overflow:hidden box.
OVERFLOW_JS = r"""(() => {
  const stage = document.getElementById('stage'), box = stage.getBoundingClientRect(), found = [];
  const name = el => el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  for (const el of stage.querySelectorAll('*')) {
    if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    if (r.right > box.right + 1 || r.bottom > box.bottom + 1 || r.left < box.left - 1 || r.top < box.top - 1) found.push(['outside the slide', name(el)]);
    const cs = getComputedStyle(el);
    if ([cs.overflow, cs.overflowX, cs.overflowY].includes('hidden') && (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2)) found.push(['content clipped', name(el)]);
  }
  return found.slice(0, 25);
})()"""

# Share of the slide (32 x 18 cells) that holds no text, graphic, image or strong fill. Faint (build-hidden) parts do not count.
EMPTY_JS = r"""(() => {
  const box = document.getElementById('stage').getBoundingClientRect(), cols = 32, rows = 18, filled = new Uint8Array(cols * rows);
  const cw = box.width / cols, ch = box.height / rows;
  const mark = r => {
    if (r.width < 1 || r.height < 1 || r.right < box.left || r.left > box.right || r.bottom < box.top || r.top > box.bottom) return;
    const x0 = Math.max(0, Math.floor((r.left - box.left) / cw)), x1 = Math.min(cols - 1, Math.floor((r.right - box.left - .01) / cw));
    const y0 = Math.max(0, Math.floor((r.top - box.top) / ch)), y1 = Math.min(rows - 1, Math.floor((r.bottom - box.top - .01) / ch));
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) filled[y * cols + x] = 1;
  };
  const shown = el => { for (let e = el; e && e.id !== 'viewport'; e = e.parentElement) { const s = getComputedStyle(e); if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity < .15) return false; } return true; };
  const dark = c => { const m = c.match(/[\d.]+/g); if (!m || (m.length > 3 && +m[3] < .3)) return false; return (.2126 * m[0] + .7152 * m[1] + .0722 * m[2]) / 255 < .8; };
  const stage = document.getElementById('stage'), walker = document.createTreeWalker(stage, NodeFilter.SHOW_TEXT);
  for (let n; (n = walker.nextNode());) { if (!n.textContent.trim() || !shown(n.parentElement)) continue; const range = document.createRange(); range.selectNodeContents(n); for (const r of range.getClientRects()) mark(r); }
  const skip = new Set(['svg', 'g', 'defs', 'clippath', 'mask', 'lineargradient', 'radialgradient', 'stop', 'text', 'tspan', 'title', 'desc', 'marker', 'pattern', 'symbol']);
  for (const el of stage.querySelectorAll('*')) {
    const tag = el.tagName.toLowerCase(), graphic = el.closest('svg') && !skip.has(tag);
    if ((graphic || tag === 'img' || dark(getComputedStyle(el).backgroundColor)) && shown(el)) mark(el.getBoundingClientRect());
  }
  return Math.round(filled.reduce((sum, f) => sum + !f, 0) / filled.length * 100);
})()"""
SPARSE = 45  # percent; dense report slides measure about 25-40


def find_browser(explicit):
    if explicit:
        return explicit
    for path in CANDIDATES:
        if os.path.exists(path):
            return path
    for name in NAMES:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit('No Chromium browser found. Install Edge or Chrome, or pass --browser PATH.')


class Socket:
    """Minimal WebSocket client (RFC 6455) for the local DevTools endpoint."""

    def __init__(self, url):
        parts = urllib.parse.urlparse(url)
        self.sock = socket.create_connection((parts.hostname, parts.port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        request = (f'GET {parts.path} HTTP/1.1\r\nHost: {parts.hostname}:{parts.port}\r\nUpgrade: websocket\r\n'
                   f'Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n')
        self.sock.sendall(request.encode())
        header = b''
        while b'\r\n\r\n' not in header:
            chunk = self.sock.recv(1)
            if not chunk:
                raise ConnectionError('DevTools closed the connection during the handshake')
            header += chunk
        if b' 101 ' not in header.split(b'\r\n', 1)[0]:
            raise ConnectionError('DevTools refused the WebSocket upgrade')

    def _read(self, size):
        data = b''
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError('DevTools connection closed')
            data += chunk
        return data

    def send(self, text):
        payload = text.encode('utf-8')
        mask = os.urandom(4)
        length = len(payload)
        if length < 126:
            header = struct.pack('!BB', 0x81, 0x80 | length)
        elif length < 1 << 16:
            header = struct.pack('!BBH', 0x81, 0x80 | 126, length)
        else:
            header = struct.pack('!BBQ', 0x81, 0x80 | 127, length)
        self.sock.sendall(header + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def recv(self):
        message = b''
        while True:
            first, second = self._read(2)
            length = second & 0x7F
            if length == 126:
                length = struct.unpack('!H', self._read(2))[0]
            elif length == 127:
                length = struct.unpack('!Q', self._read(8))[0]
            payload = self._read(length)
            opcode = first & 0x0F
            if opcode == 0x8:
                raise ConnectionError('DevTools closed the connection')
            if opcode in (0x9, 0xA):
                continue  # ping/pong
            message += payload
            if first & 0x80:
                return message.decode('utf-8')


class Browser:
    def __init__(self, executable, width, height):
        self.profile = tempfile.mkdtemp(prefix='ppt-capture-')
        self.process = subprocess.Popen([executable, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--remote-debugging-port=0',
                                         f'--user-data-dir={self.profile}', f'--window-size={width},{height}', 'about:blank'],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=self.profile)  # browser logs stay out of the user's folder
        port_file = Path(self.profile) / 'DevToolsActivePort'
        for _ in range(100):
            if port_file.exists() and port_file.read_text().strip():
                break
            time.sleep(0.1)
        port = port_file.read_text().split()[0]
        targets = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list'))
        page = next(target for target in targets if target.get('type') == 'page')
        self.ws = Socket(page['webSocketDebuggerUrl'])
        self.sequence = 0

    def call(self, method, **params):
        self.sequence += 1
        self.ws.send(json.dumps({'id': self.sequence, 'method': method, 'params': params}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get('id') == self.sequence:
                if 'error' in message:
                    raise RuntimeError(f"{method}: {message['error'].get('message')}")
                return message.get('result', {})

    def evaluate(self, expression):
        result = self.call('Runtime.evaluate', expression=expression, returnByValue=True, awaitPromise=True)
        return result.get('result', {}).get('value')

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
        shutil.rmtree(self.profile, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('html', type=Path)
    parser.add_argument('--out', type=Path, required=True, help='folder for PNG screenshots and report.json')
    parser.add_argument('--width', type=int, default=1600)
    parser.add_argument('--height', type=int, help='window height; by default the window is sized so the slide renders at its deck size')
    parser.add_argument('--reduced', action='store_true', help='emulate reduced motion (every step fully revealed)')
    parser.add_argument('--wait', type=float, default=0.9, help='seconds to wait after each step for transitions')
    parser.add_argument('--pdf', type=Path, help='also print the deck to this PDF')
    parser.add_argument('--stage-only', action='store_true', help='crop screenshots to the slide (no controls or margins)')
    parser.add_argument('--browser', help='path to Edge/Chrome/Chromium')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    args.out.mkdir(parents=True, exist_ok=True)
    url = args.html.resolve().as_uri()
    browser = Browser(find_browser(args.browser), args.width, args.height or 982)
    report = {'file': str(args.html), 'reduced_motion': args.reduced, 'steps': []}
    try:
        browser.call('Page.enable')
        browser.call('Emulation.setDeviceMetricsOverride', width=args.width, height=args.height or 982, deviceScaleFactor=1, mobile=False)
        if args.reduced:
            browser.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-reduced-motion', 'value': 'reduce'}])
        browser.call('Page.navigate', url=url)
        for _ in range(50):
            if browser.evaluate('Boolean(globalThis.__pptPlayer)'):
                break
            time.sleep(0.2)
        if not args.height and browser.evaluate('Boolean(globalThis.__pptPlayer)'):
            # Controls and chapter tabs take window height; grow the window so the slide is not scaled down.
            size = browser.evaluate("(() => { const s = __pptPlayer.deck.settings || {}; return {w: s.width || 1600, h: s.height || 900, chrome: innerHeight - document.getElementById('viewport').clientHeight}; })()")
            height = round(size['h'] * args.width / size['w'] + size['chrome'])
            browser.call('Emulation.setDeviceMetricsOverride', width=args.width, height=height, deviceScaleFactor=1, mobile=False)
            time.sleep(0.3)
        steps = browser.evaluate('__pptPlayer.steps()') or []
        if args.stage_only:  # slide-only images: hide controls, chapter tabs and the review toolbar
            browser.evaluate("document.querySelectorAll('[data-editor-ui], .controls, #chapter-nav').forEach(node => node.style.visibility = 'hidden')")
        if not steps:
            raise SystemExit('This file has no ppt-to-html player (built with an older skill?).')
        started = time.time()
        print(f'{len(steps)} steps; about {max(1, round(len(steps) * (args.wait + 1.5) / 60))} min. Run it with a long command timeout.')
        for index, step in enumerate(steps, 1):
            target = f"#scene={urllib.parse.quote(step['scene'])}&step={step['step']}"
            name = f"{index:02d}-{step['scene']}-{step['step']}.png"
            for attempt in (1, 2):
                try:
                    browser.evaluate(f'location.hash = {json.dumps(target)}')
                    time.sleep(args.wait * attempt)
                    issues = browser.evaluate(OVERFLOW_JS) or []
                    empty = browser.evaluate(EMPTY_JS)
                    clip = {}
                    if args.stage_only:
                        box = browser.evaluate("(() => { const r = document.getElementById('stage').getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; })()")
                        clip = {'clip': {**box, 'scale': 1}}
                    shot = browser.call('Page.captureScreenshot', format='png', **clip)['data']
                    break
                except (TimeoutError, socket.timeout, RuntimeError) as error:
                    if attempt == 2:
                        raise SystemExit(f'Step {index} ({step["scene"]} {step["step"]}) failed twice: {error}. Partial results are in report.json.')
            (args.out / name).write_bytes(base64.b64decode(shot))
            last = index == len(steps) or steps[index]['scene'] != step['scene']  # fully revealed step of its scene
            if last and empty is not None and empty >= SPARSE:
                issues = issues + [['sparse', f'{empty}% of the slide is empty']]
            report['steps'].append({**step, 'file': name, 'empty_pct': empty, 'issues': issues})
            # Keep a usable report even if a later step fails.
            (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            flag = f"  ⚠ {len(issues)} layout issue(s)" if issues else ''
            print(f"{index:02d} {step['scene']} step {step['step']}{' (backup)' if step['backup'] else ''}  empty {empty}%{flag}  [{time.time() - started:.0f}s]")
        if args.pdf:
            pdf = browser.call('Page.printToPDF', printBackground=True, preferCSSPageSize=True)['data']
            args.pdf.parent.mkdir(parents=True, exist_ok=True)
            args.pdf.write_bytes(base64.b64decode(pdf))
            print(f'PDF: {args.pdf} (open it and look at every page; this tool cannot see printed pages)')
    finally:
        browser.close()
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    flagged = [step for step in report['steps'] if step['issues']]
    print(f"{len(report['steps'])} steps captured; {len(flagged)} step(s) with layout issues to review (see report.json).")
    print('Screenshots are evidence for your own visual review; an empty issue list does not prove the layout is right.')


if __name__ == '__main__':
    main()
