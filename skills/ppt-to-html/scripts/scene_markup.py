"""Convert agent-authored scene HTML into a validated data tree.

The player rebuilds the tree with createElement/setAttribute/textContent, so a
composed scene never reaches the page as raw markup. Anything outside the
allowlist is rejected with a message the agent can act on.
"""
from html.parser import HTMLParser
import json
import re

HTML_TAGS = {
    'div', 'span', 'p', 'h2', 'h3', 'h4', 'h5', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'table', 'thead', 'tbody', 'tfoot',
    'tr', 'th', 'td', 'caption', 'colgroup', 'col', 'strong', 'em', 'b', 'i', 'u', 's', 'small', 'sup', 'sub', 'mark',
    'br', 'hr', 'figure', 'figcaption', 'section', 'article', 'header', 'footer', 'aside', 'blockquote', 'button', 'img',
}
SVG_TAGS = {
    'svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text', 'tspan', 'defs',
    'lineargradient', 'radialgradient', 'stop', 'clippath', 'mask', 'pattern', 'marker', 'title', 'desc', 'use', 'symbol',
}
# html.parser lowercases names; SVG needs its original camelCase back.
SVG_CASE = {'lineargradient': 'linearGradient', 'radialgradient': 'radialGradient', 'clippath': 'clipPath',
            'viewbox': 'viewBox', 'preserveaspectratio': 'preserveAspectRatio', 'gradientunits': 'gradientUnits',
            'gradienttransform': 'gradientTransform', 'patternunits': 'patternUnits', 'markerwidth': 'markerWidth',
            'markerheight': 'markerHeight', 'markerunits': 'markerUnits', 'refx': 'refX', 'refy': 'refY',
            'textlength': 'textLength', 'lengthadjust': 'lengthAdjust', 'clippathunits': 'clipPathUnits',
            'maskunits': 'maskUnits', 'patterntransform': 'patternTransform', 'patterncontentunits': 'patternContentUnits',
            'maskcontentunits': 'maskContentUnits', 'spreadmethod': 'spreadMethod', 'pathlength': 'pathLength'}
VOID = {'br', 'hr', 'img', 'col'}
REMOTE = re.compile(r'(?i)(?:javascript:|vbscript:|https?:|//|url\(\s*["\']?\s*(?!#|data:image/))')
MAX_NODES = 4000
BLOCKED = re.compile(r'(?i)<\s*(script|style|iframe|object|embed|link|meta|base|form|input|textarea|select|video|audio|source)\b')
ATTR_NAME = re.compile(r'[a-z][a-z0-9_.:-]*\Z')
STEP = re.compile(r'(?:[1-9]|1[0-2])\Z')
# Attribute allowlist (lowercase, as html.parser reports them). Anything that can carry a URL is absent
# except src (img, data:image/ only) and href/xlink:href (#ids only).
GLOBAL_ATTRS = {'class', 'id', 'style', 'title', 'role', 'lang', 'dir'}
HTML_ATTRS = {'td': {'colspan', 'rowspan', 'headers'}, 'th': {'colspan', 'rowspan', 'headers', 'scope'},
              'col': {'span'}, 'colgroup': {'span'}, 'img': {'src', 'alt', 'width', 'height'}, 'ol': {'start', 'reversed'},
              'button': {'type'}}
SVG_ATTRS = {
    'viewbox', 'preserveaspectratio', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'r', 'rx', 'ry', 'fx', 'fy', 'width', 'height',
    'd', 'points', 'transform', 'fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-width', 'stroke-opacity', 'stroke-dasharray',
    'stroke-dashoffset', 'stroke-linecap', 'stroke-linejoin', 'stroke-miterlimit', 'opacity', 'font-size', 'font-weight',
    'font-family', 'font-style', 'text-anchor', 'dominant-baseline', 'alignment-baseline', 'letter-spacing', 'dx', 'dy', 'rotate',
    'textlength', 'lengthadjust', 'offset', 'stop-color', 'stop-opacity', 'gradientunits', 'gradienttransform', 'spreadmethod',
    'patternunits', 'patterncontentunits', 'patterntransform', 'clip-path', 'clippathunits', 'clip-rule', 'mask', 'maskunits',
    'maskcontentunits', 'marker-start', 'marker-mid', 'marker-end', 'markerwidth', 'markerheight', 'markerunits', 'refx', 'refy',
    'orient', 'visibility', 'display', 'vector-effect', 'paint-order', 'shape-rendering', 'text-rendering', 'pathlength',
    'href', 'xlink:href', 'xmlns', 'xmlns:xlink', 'aria-hidden', 'focusable', 'overflow'}
# The player's own element ids; scene content may not reuse them.
RESERVED_IDS = {'stage', 'viewport', 'deck-data', 'chapter-nav', 'prev', 'next', 'position', 'play', 'replay', 'open-outline',
                'bookmark-current', 'open-bookmarks', 'return-bookmark', 'return-origin', 'fullscreen', 'print', 'print-confirm',
                'print-close', 'print-toolbar', 'print-pages', 'announcement', 'outline-dialog', 'outline-close', 'outline-list',
                'outline-title', 'bookmarks-dialog', 'bookmarks-close', 'bookmarks-list', 'bookmarks-title', 'supplements-dialog',
                'supplement-tabs', 'supplement-frame', 'open-supplements', 'close-supplements', 'supplements-title', 'font-license'}


class MarkupError(ValueError):
    pass


def check_css(css, where):
    """Reject CSS that could fetch, import or escape its style element.

    CSS escapes (\\75 rl) and comments can hide a URL from a text match, so backslashes and
    comments are rejected outright, as are other image-fetching functions and @-rules.
    """
    lowered = css.lower()
    for token in ('\\', '/*', '@import', '@font-face', '@namespace', 'image-set(', 'cross-fade(', 'element(', 'image(',
                  'expression(', '</style', '<!--', 'behavior:', '-moz-binding', 'src:'):
        if token in lowered:
            shown = 'backslash escapes' if token == '\\' else 'comments' if token == '/*' else token
            raise MarkupError(f'{where}: {shown} not allowed in offline CSS')
    if REMOTE.search(css):
        raise MarkupError(f'{where}: remote or script URLs are not allowed; embed data:image/ or use #ids')


class _Builder(HTMLParser):
    def __init__(self, where):
        super().__init__(convert_charrefs=True)
        self.where = where
        self.root = ['div', {}, []]
        self.stack = [(self.root, False)]
        self.count = 0
        self.steps = set()
        self.gotos = set()
        self.charts = []

    def fail(self, message):
        raise MarkupError(f'{self.where}: {message}')

    def handle_starttag(self, tag, attrs):
        self._open(tag, attrs, closing=tag in VOID)

    def handle_startendtag(self, tag, attrs):
        self._open(tag, attrs, closing=True)

    def _open(self, tag, attrs, closing):
        parent, in_svg = self.stack[-1]
        svg = in_svg or tag == 'svg'
        if tag not in (SVG_TAGS if svg else HTML_TAGS):
            self.fail(f'<{tag}> is not allowed. Use layout/text/table/SVG drawing tags only (no script, iframe, form, link, style or video).')
        self.count += 1
        if self.count > MAX_NODES:
            self.fail(f'more than {MAX_NODES} elements; split the scene')
        clean = {}
        for name, value in attrs:
            value = '' if value is None else value
            if name.startswith('on'):
                self.fail(f'<{tag} {name}>: event handler attributes are not allowed; the player provides interaction')
            allowed = (name in GLOBAL_ATTRS or name.startswith(('data-', 'aria-'))
                       or (name in SVG_ATTRS if svg else name in HTML_ATTRS.get(tag, ())))
            if not ATTR_NAME.match(name) or not allowed:
                self.fail(f'<{tag} {name}> is not an allowed attribute; use class/style/title/data-*/aria-* (and SVG drawing attributes inside <svg>)')
            if name in ('xmlns', 'xmlns:xlink'):
                continue  # namespaces come from createElementNS; the declaration is not needed
            if svg and name not in ('href', 'xlink:href') and ('\\' in value or 'url(' in value.lower()):
                # SVG paint attributes are parsed as CSS values, so they get the CSS checks.
                check_css(value, f'{self.where} <{tag} {name}>')
            if name == 'id' and value in RESERVED_IDS:
                self.fail(f'<{tag} id="{value}">: this id is used by the player controls; choose another id')
            if name in ('href', 'xlink:href'):
                if not value.startswith('#'):
                    self.fail(f'<{tag} {name}="{value[:40]}">: only in-document #ids are allowed; use data-goto="scene-id" to jump')
            if name == 'src':
                if tag != 'img' or not value.startswith('data:image/'):
                    self.fail(f'<{tag} src>: only embedded data:image/ sources are allowed')
            elif name == 'style':
                check_css(value, f'{self.where} <{tag} style>')
            elif REMOTE.search(value) and name not in ('data-chart',):
                self.fail(f'<{tag} {name}>: remote or script URLs are not allowed')
            if name == 'data-step':
                if not STEP.match(value):
                    self.fail(f'<{tag} data-step="{value}">: use a whole number from 1 to 12')
                self.steps.add(int(value))
            if name == 'data-goto':
                if not value.strip():
                    self.fail(f'<{tag} data-goto>: scene id required')
                self.gotos.add(value)
            if name == 'data-chart':
                try:
                    self.charts.append(json.loads(value))
                except json.JSONDecodeError as error:
                    self.fail(f'<{tag} data-chart>: invalid JSON ({error.msg})')
            clean[SVG_CASE.get(name, name) if svg else name] = value
        if tag == 'button' and 'data-goto' not in clean:
            self.fail('<button> needs data-goto="scene-id"; other buttons have no behavior offline')
        node = [SVG_CASE.get(tag, tag), clean, []]
        parent[2].append(node)
        if not closing:
            self.stack.append((node, svg))

    def handle_endtag(self, tag):
        name = SVG_CASE.get(tag, tag)
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index][0][0] == name:
                del self.stack[index:]
                return
        # Stray end tags are ignored, matching browser behavior.

    def handle_data(self, data):
        if data.strip() or (data and self.stack[-1][0][2]):
            self.stack[-1][0][2].append(data if data.strip() else ' ')

    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        self.fail('declarations are not allowed inside a scene')

    def handle_pi(self, data):
        self.fail('processing instructions are not allowed inside a scene')


def parse_scene_html(markup, where):
    """Return (children, steps used, goto targets, chart specs)."""
    if not isinstance(markup, str) or not markup.strip():
        raise MarkupError(f'{where}: nonempty HTML required')
    if len(markup.encode('utf-8')) > 400 * 1024:
        raise MarkupError(f'{where}: scene HTML exceeds 400 KiB; move detail to a backup scene')
    # Checked before parsing so raw-text elements (script/style) never reach the tree.
    blocked = BLOCKED.search(markup)
    if blocked:
        raise MarkupError(f'{where}: <{blocked.group(1).lower()}> is not allowed in a scene')
    builder = _Builder(where)
    builder.feed(markup)
    builder.close()
    return builder.root[2], builder.steps, builder.gotos, builder.charts
