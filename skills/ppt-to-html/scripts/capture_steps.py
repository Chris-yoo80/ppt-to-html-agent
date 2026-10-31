"""Screenshot every step of a built presentation, flag overflow, and optionally print a PDF.

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
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
    parser.add_argument('--height', type=int, default=982, help='window height; the default leaves room for the control bar')
    parser.add_argument('--reduced', action='store_true', help='emulate reduced motion (every step fully revealed)')
    parser.add_argument('--wait', type=float, default=0.9, help='seconds to wait after each step for transitions')
    parser.add_argument('--pdf', type=Path, help='also print the deck to this PDF')
    parser.add_argument('--browser', help='path to Edge/Chrome/Chromium')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    args.out.mkdir(parents=True, exist_ok=True)
    url = args.html.resolve().as_uri()
    browser = Browser(find_browser(args.browser), args.width, args.height)
    report = {'file': str(args.html), 'reduced_motion': args.reduced, 'steps': []}
    try:
        browser.call('Page.enable')
        browser.call('Emulation.setDeviceMetricsOverride', width=args.width, height=args.height, deviceScaleFactor=1, mobile=False)
        if args.reduced:
            browser.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-reduced-motion', 'value': 'reduce'}])
        browser.call('Page.navigate', url=url)
        for _ in range(50):
            if browser.evaluate('Boolean(globalThis.__pptPlayer)'):
                break
            time.sleep(0.2)
        steps = browser.evaluate('__pptPlayer.steps()') or []
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
                    shot = browser.call('Page.captureScreenshot', format='png')['data']
                    break
                except (TimeoutError, socket.timeout, RuntimeError) as error:
                    if attempt == 2:
                        raise SystemExit(f'Step {index} ({step["scene"]} {step["step"]}) failed twice: {error}. Partial results are in report.json.')
            (args.out / name).write_bytes(base64.b64decode(shot))
            report['steps'].append({**step, 'file': name, 'issues': issues})
            # Keep a usable report even if a later step fails.
            (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            flag = f"  ⚠ {len(issues)} layout issue(s)" if issues else ''
            print(f"{index:02d} {step['scene']} step {step['step']}{' (backup)' if step['backup'] else ''}{flag}  [{time.time() - started:.0f}s]")
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
