"""Extract PPTX text, tables, notes and media inventory with Python's standard library.

Does not render slides or execute embedded objects. Legacy .ppt and encrypted files
must be exported to an accessible .pptx or PDF by their owner first.
"""
import argparse
import json
import posixpath
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = '{http://schemas.openxmlformats.org/package/2006/relationships}'


def aspect_label(cx, cy):
    """Name the slide ratio from its EMU size: 16:9, 4:3, 16:10 or W:H rounded."""
    from math import gcd
    for label, (w, h) in {'16:9': (16, 9), '4:3': (4, 3), '16:10': (16, 10)}.items():
        if abs(cx / cy - w / h) < 0.01:
            return label
    divisor = gcd(cx, cy) or 1
    return f'{cx // divisor}:{cy // divisor}'


def relationships(archive, part):
    folder, filename = posixpath.split(part)
    name = posixpath.join(folder, '_rels', filename + '.rels')
    if name not in archive.namelist():
        return {}
    result = {}
    for entry in ET.fromstring(archive.read(name)).findall(REL + 'Relationship'):
        external = entry.get('TargetMode') == 'External'
        target = entry.get('Target', '')
        result[entry.get('Id')] = {
            'type': entry.get('Type', '').rsplit('/', 1)[-1],
            'target': target if external else posixpath.normpath(posixpath.join(folder, target)) if not target.startswith('/') else target.lstrip('/'),
            'external': external,
        }
    return result


def paragraphs(root):
    if root is None:
        return []
    output = []
    drawing = '{' + NS['a'] + '}'
    for paragraph in root.findall('.//a:p', NS):
        parts = []
        for child in paragraph:
            if child.tag == drawing + 'br':
                parts.append('\n')
            elif child.tag == drawing + 'tab':
                parts.append('\t')
            elif child.tag == drawing + 't':
                parts.append(child.text or '')
            else:
                parts.extend(node.text or '' for node in child.findall('.//a:t', NS))
        content = ''.join(parts).strip()
        if content:
            output.append(content)
    return output


def extract(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if sum(item.file_size for item in entries) > 256 * 1024 * 1024:
            raise ValueError('Archive exceeds the 256 MiB uncompressed input limit')
        presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
        rels = relationships(archive, 'ppt/presentation.xml')
        size = presentation.find('p:sldSz', NS)
        result = {'format': 'pptx-text-v1', 'source_file': Path(path).name if isinstance(path, (str, Path)) else '<memory>',
                  'limitations': ['No slide rendering, OCR, layout fidelity, chart workbook interpretation or embedded-object execution.',
                                  'SmartArt text is not extracted; diagram relationships are inventoried for further review.',
                                  'Notes may contain private material; do not publish extracted inputs by default.'],
                  'size_emu': dict(size.attrib) if size is not None else {}, 'slides': []}
        if size is not None and size.get('cx', '').isdigit() and size.get('cy', '').isdigit():
            # The declared type is often stale (e.g. screen4x3 on a 16:9 deck); the real ratio comes from cx/cy.
            result['aspect'] = aspect_label(int(size.get('cx')), int(size.get('cy')))
            declared = size.get('type', '')
            if declared in ('screen4x3', 'screen16x9', 'screen16x10') and declared[6:].replace('x', ':') != result['aspect']:
                result['limitations'].append(f"Declared slide type {declared} does not match the actual size {result['aspect']}; use aspect.")
        order = presentation.findall('p:sldIdLst/p:sldId', NS)
        for number, slide_id in enumerate(order, 1):
            relation = rels[slide_id.get('{' + NS['r'] + '}id')]
            if relation['external']:
                raise ValueError('External slide references are not supported')
            part = relation['target']
            root = ET.fromstring(archive.read(part))
            slide = {'number': number, 'part': part, 'hidden': root.get('show', '1') in ('0', 'false'),
                     'text': [], 'tables': [], 'notes': [], 'media': [], 'warnings': []}
            for shape in root.findall('.//p:sp', NS):
                text = paragraphs(shape.find('p:txBody', NS))
                if text:
                    slide['text'].append(text)
            for table in root.findall('.//a:tbl', NS):
                slide['tables'].append([[ '\n'.join(paragraphs(cell)) for cell in row.findall('a:tc', NS)]
                                        for row in table.findall('a:tr', NS)])
            for link in relationships(archive, part).values():
                if link['type'] == 'notesSlide' and not link['external']:
                    notes = ET.fromstring(archive.read(link['target']))
                    for shape in notes.findall('.//p:sp', NS):
                        placeholder = shape.find('p:nvSpPr/p:nvPr/p:ph', NS)
                        if placeholder is not None and placeholder.get('type') in ('sldNum', 'hdr', 'ftr', 'dt', 'sldImg'):
                            continue
                        slide['notes'].extend(paragraphs(shape.find('p:txBody', NS)))
                elif link['type'].startswith('diagram'):
                    slide['media'].append(link)
                    if link['type'] == 'diagramData':
                        slide['warnings'].append('SmartArt text was not extracted; inspect the diagram source or rendered slide.')
                elif link['type'] in ('image', 'video', 'audio', 'media', 'chart', 'oleObject', 'hyperlink'):
                    slide['media'].append(link)
            result['slides'].append(slide)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = extract(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    except (zipfile.BadZipFile, KeyError, OSError, ET.ParseError, ValueError) as error:
        parser.exit(1, f'Extraction failed: {error}\n')
    print(f'Extracted {len(result["slides"])} slides to {args.output}; visual verification still required.')


if __name__ == '__main__':
    main()
