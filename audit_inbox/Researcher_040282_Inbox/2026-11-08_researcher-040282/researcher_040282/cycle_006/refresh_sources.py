"""Read-only, selected public source/review refresh for bounded cycle006.

Persist minimal identifiers, never raw commit API contact/signature payloads.
No code is imported or executed. Git blob verification is acquisition metadata,
not an audit finding about versions or competing source copies.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote
import urllib.request

HERE = Path(__file__).resolve().parent
OUT = HERE / 'source_state'
REPO = 'jacobbrainard84-knightninja/AIEFS'
API = 'https://api.github.com/repos/' + REPO
HEADERS = {'User-Agent': 'Researcher-040282-read-only', 'Accept': 'application/vnd.github+json'}
EMAIL = re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as response:
        return response.read()


def store_json(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    if EMAIL.search(data):
        raise RuntimeError('Unexpected contact-like content in acquisition identifiers; values not printed')
    path.write_bytes(data)


def main():
    OUT.mkdir(exist_ok=True)
    for branch, label in [('main', 'main'), ('audit-inbox', 'inbox')]:
        raw = json.loads(get(API + '/branches/' + branch))
        commit = raw['commit']['sha']
        if not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise ValueError('Unexpected branch identifier')
        store_json(OUT / (label + '_branch.json'), {
            'branch': branch, 'commit': commit,
            'metadata_policy': 'author/committer/contact/signature payload omitted'})
        raw_tree = json.loads(get(API + '/git/trees/' + commit + '?recursive=1'))
        if raw_tree.get('truncated'):
            raise RuntimeError('Truncated source listing; stop rather than assume absence')
        tree = {'sha': raw_tree['sha'], 'truncated': False,
                'tree': [{k: record[k] for k in ('path', 'mode', 'type', 'sha', 'size') if k in record}
                         for record in raw_tree['tree']]}
        store_json(OUT / (label + '_tree.json'), tree)
        files = {record['path']: record for record in tree['tree'] if record['type'] == 'blob'}
        if label == 'main':
            fixed = {'CURRENT_STATUS.md', 'README.md', 'registry/artifacts.csv',
                     'registry/claims.csv', '.github/workflows/repo-checks.yml'}
            selected = {path for path in fixed if path in files}
            selected |= {path for path, record in files.items()
                         if record.get('size', 0) < 350000 and path.endswith(('.py', '.md', '.csv'))
                         and any(token in path.lower() for token in (
                             'analysis_v4_1', 'analysis_v41', 'analysis_v4.1', 'v4_1',
                             'v4.1', 'errata', 'redteam'))}
        else:
            fixed = {'audit_inbox/README.md', 'audit_inbox/TRIAGE.md',
                     'audit_inbox/briefing/STATE.md', 'audit_inbox/briefing/OPEN_QUESTIONS.md'}
            selected = {path for path in fixed if path in files}
            selected |= {path for path, record in files.items()
                         if record.get('size', 0) < 220000 and path.endswith(('.md', '.csv'))
                         and '/source_state/' not in path
                         and any(token in path.lower() for token in (
                             '040282', 'v4_1', 'v4.1', 'tw_sensitivity', 'triage', 'coordinator'))}
        def acquire(path):
            data = get('https://raw.githubusercontent.com/' + REPO + '/' + commit + '/' + quote(path, safe='/'))
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if blob != files[path]['sha']:
                raise RuntimeError('Fetched dependency differs from pinned acquisition: ' + path)
            target = OUT / label / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            return {'path': path, 'blob': blob, 'bytes': len(data)}
        with ThreadPoolExecutor(max_workers=6) as pool:
            records = list(pool.map(acquire, sorted(selected)))
        store_json(OUT / (label + '_selected.json'), {
            'branch': branch, 'commit': commit, 'fetched_and_verified': len(records),
            'files': records, 'scope': 'Selected current-source/review refresh; not an exhaustive assignment or wrapper audit'})
        print(label, commit, 'selected', len(records), flush=True)
        for path in sorted(files):
            if any(token in path.lower() for token in ('v4_1', 'v4.1', 'v41', 'triage', 'errata')):
                print('NAV', label, path, flush=True)


if __name__ == '__main__':
    main()
