"""Download only the reviewed public Python dependency set; execute no code.

No commit author/contact/signature API metadata is requested or persisted.
Existing mismatched files cause an error rather than silent replacement.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('upstream'))
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parent / 'source_modules.json').read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    def acquire(record):
        name = record['path']
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or relative.suffix != '.py':
            raise ValueError('Unexpected public module path')
        target = args.output / relative
        if target.exists():
            content = target.read_bytes()
        else:
            url = ('https://raw.githubusercontent.com/' + manifest['repo'] + '/' +
                   manifest['commit'] + '/' + quote(name, safe='/'))
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                content = response.read()
        blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if blob != record['blob'] or len(content) != record['bytes']:
            raise RuntimeError('Dependency differs from reviewed source: ' + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return name
    with ThreadPoolExecutor(max_workers=4) as pool:
        names = list(pool.map(acquire, manifest['modules']))
    print(json.dumps({'tested_main': manifest['commit'], 'public_modules_fetched_and_verified': len(names),
                      'code_executed_by_fetcher': False,
                      'metadata_policy': 'no author/committer/contact/signature payloads'}, indent=2))


if __name__ == '__main__':
    main()
