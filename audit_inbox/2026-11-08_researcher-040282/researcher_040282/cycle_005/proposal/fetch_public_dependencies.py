"""Fetch the ten reviewed public source modules for the bounded self-test.

No Git API commit metadata/contact/signature payloads are requested or stored.
This helper downloads text only; it does not import or execute downloaded code.
Read the files before running the checks. Existing mismatched files are not
silently overwritten. Third-party Python packages must be installed separately.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('upstream'))
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parent / 'source_modules.json').read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    def acquire(record):
        name = record['path']
        if Path(name).name != name or not name.endswith('.py'):
            raise ValueError('Unexpected module path')
        target = args.output / name
        if target.exists():
            data = target.read_bytes()
        else:
            url = ('https://raw.githubusercontent.com/' + manifest['repo'] + '/' +
                   manifest['commit'] + '/' + quote(name, safe=''))
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
        if git_blob(data) != record['blob'] or len(data) != record['bytes']:
            raise RuntimeError('Dependency differs from reviewed source: ' + name)
        target.write_bytes(data)
        return name
    with ThreadPoolExecutor(max_workers=4) as pool:
        names = list(pool.map(acquire, manifest['modules']))
    print(json.dumps({'source_commit': manifest['commit'], 'verified_modules': len(names),
                      'downloaded_code_executed_by_helper': False,
                      'metadata_policy': 'no author/committer/contact/signature payloads'}, indent=2))


if __name__ == '__main__':
    main()
