"""Report whether a newer version of this skill has been published.

  python check_update.py

Makes one plain GET request for a small public JSON file and sends no deck content, file names or
identifiers (the host sees an ordinary web request). Never downloads or changes anything, never fails the
caller: any problem ends with "not checked" and exit code 0. Only a validated version number is taken from
the response; the links printed are fixed here. Set PPT_TO_HTML_NO_UPDATE_CHECK=1 to turn the check off.
"""
import http.client
import json
import os
from pathlib import Path
import re
import urllib.request

LATEST_URL = 'https://chris-yoo80.github.io/ppt-to-html-agent/latest.json'
RELEASES_URL = 'https://github.com/Chris-yoo80/ppt-to-html-agent/releases/latest'
DOWNLOAD_URL = 'https://chris-yoo80.github.io/ppt-to-html-agent/downloads/ppt-to-html.zip'
VERSION_FILE = Path(__file__).resolve().parents[1] / 'assets/version.json'
SEMVER = re.compile(r'\d{1,4}\.\d{1,4}\.\d{1,4}')


def parse(text):
    """Return a version tuple from JSON text, or raise ValueError."""
    version = json.loads(text)['version']
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise ValueError('invalid version')
    return tuple(int(part) for part in version.split('.'))


def text_of(version):
    return '.'.join(str(part) for part in version)


def latest():
    with urllib.request.urlopen(LATEST_URL, timeout=3) as response:
        return parse(response.read(1024).decode('utf-8'))


def main():
    if os.environ.get('PPT_TO_HTML_NO_UPDATE_CHECK'):
        print('Update check turned off.')
        return 0
    try:
        installed = parse(VERSION_FILE.read_text(encoding='utf-8'))
        newest = latest()
    except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException):
        print('Update not checked.')
        return 0
    if newest > installed:
        print(f'Update available: installed {text_of(installed)}, latest {text_of(newest)}.')
        print(f'Changes: {RELEASES_URL}')
        print(f'Download: {DOWNLOAD_URL}')
    else:
        print(f'Up to date: {text_of(installed)}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
