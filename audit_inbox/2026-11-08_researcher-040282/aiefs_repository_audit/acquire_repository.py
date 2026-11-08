"""Read-only acquisition of a fixed public branch snapshot for local auditing.

No credentials, git pushes, or remote modifications. Large generated datasets
are intentionally excluded unless explicitly requested as extra paths.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
REPO = ROOT / 'repository'
BRANCH = json.loads((ROOT / 'branch_snapshot.json').read_text())
SHA = BRANCH['commit']['sha']
BLOBS = {x['path']: x for x in json.loads((ROOT / 'repository_tree.json').read_text())['tree'] if x['type'] == 'blob'}
TEXT_SUFFIXES = {'.py', '.md', '.lean', '.sh', '.yml', '.yaml', '.toml', '.ini', '.cfg'}


def selected(path, entry):
    p = Path(path)
    size = entry.get('size', 0)
    return (
        p.suffix.lower() in TEXT_SUFFIXES
        or p.name in {'lean-toolchain', '.gitignore', 'LICENSE', 'LICENSE-docs', 'LICENSING.md', 'NOTICE'}
        or (p.suffix.lower() == '.json' and size < 1_000_000)
        or (p.suffix.lower() in {'.txt', '.log'} and size < 250_000)
        or (p.suffix.lower() == '.csv' and size < 1_000_000)
    )


def fetch(path):
    entry = BLOBS[path]
    dest = REPO / path
    def valid(data):
        header = f'blob {len(data)}\0'.encode()
        return len(data) == entry.get('size', len(data)) and hashlib.sha1(header + data).hexdigest() == entry['sha']
    if dest.is_file() and valid(dest.read_bytes()):
        dest.chmod(int(entry['mode'], 8) & 0o777)
        return path, 'cached', len(dest.read_bytes())
    url = 'https://raw.githubusercontent.com/jacobbrainard84-knightninja/AIEFS/' + SHA + '/' + urllib.parse.quote(path)
    error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Arena-read-only-source-audit'})
            with urllib.request.urlopen(request, timeout=40) as response:
                data = response.read()
            if not valid(data):
                raise ValueError('Downloaded content does not match fixed Git tree entry')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            dest.chmod(int(entry['mode'], 8) & 0o777)
            return path, 'downloaded', len(data)
        except Exception as exc:
            error = exc
            if attempt < 2:
                time.sleep(attempt + 1)
    raise RuntimeError(f'{path}: {error}')


def main():
    paths = sorted(set(sys.argv[1:]) or {p for p,e in BLOBS.items() if selected(p,e)})
    print(f'Snapshot acquisition: {len(paths)} files, {sum(BLOBS[p].get("size",0) for p in paths):,} bytes', flush=True)
    results, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch,p): p for p in paths}
        for number, future in enumerate(concurrent.futures.as_completed(futures), 1):
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append(str(exc))
            if number % 100 == 0:
                print(f'{number}/{len(paths)} completed; errors={len(errors)}', flush=True)
    state = {'snapshot': SHA, 'requested_count': len(paths), 'results': sorted(results), 'errors': errors}
    (ROOT / ('acquisition_extra.json' if sys.argv[1:] else 'acquisition.json')).write_text(json.dumps(state,indent=2))
    print(f'Finished: {len(results)} files, errors={errors}', flush=True)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
