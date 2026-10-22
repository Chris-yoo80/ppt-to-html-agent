"""Create a portable skill ZIP from an explicit public-source allowlist."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/ppt-to-html'
OUTPUT = ROOT / 'docs/downloads/ppt-to-html.zip'


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    license_text = (ROOT / 'LICENSE').read_text(encoding='utf-8')
    (SKILL / 'LICENSE').write_text(license_text, encoding='utf-8', newline='\n')
    (ROOT / 'docs/license.txt').write_text(license_text, encoding='utf-8', newline='\n')
    files = [SKILL / 'SKILL.md', SKILL / 'LICENSE']
    for directory, suffixes in [('references', {'.md'}), ('scripts', {'.py'}), ('assets', {'.css', '.js'})]:
        files.extend(path for path in (SKILL / directory).iterdir() if path.is_file() and path.suffix in suffixes)
    files.extend(path for path in (SKILL/'assets/fonts').iterdir() if path.is_file() and path.suffix in {'.woff2','.txt','.json'})
    # Stored entries avoid zlib-version differences across Windows/Linux hosts.
    with zipfile.ZipFile(OUTPUT, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path in sorted(files):
            if path.is_symlink():
                raise ValueError(f'Symlinks are not packaged: {path.name}')
            info = zipfile.ZipInfo('ppt-to-html/' + path.relative_to(SKILL).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(f'Packaged {len(files)} public skill files into {OUTPUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
