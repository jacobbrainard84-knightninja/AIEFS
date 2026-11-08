"""Selected, read-only007 source/feedback refresh. Imports no acquired code.
Keep identifiers only; raw commit author/contact/signature payloads never persist.
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


def get(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    OUT.mkdir(exist_ok=True)
    for branch, label in (('main', 'main'), ('audit-inbox', 'inbox')):
        response = json.loads(get(API + '/branches/' + branch))
        commit = response['commit']['sha']
        if not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise RuntimeError('Unexpected source identifier')
        save(OUT / (label + '_branch.json'), {'branch': branch, 'commit': commit,
             'metadata_policy': 'Only branch/commit; omit all author/committer/contact/signature payloads'})
        raw = json.loads(get(API + '/git/trees/' + commit + '?recursive=1'))
        if raw.get('truncated'):
            raise RuntimeError('Incomplete tree; do not infer absence')
        tree = {'sha': raw['sha'], 'truncated': False,
                'tree': [{k: row[k] for k in ('path', 'mode', 'type', 'sha', 'size') if k in row}
                         for row in raw['tree']]}
        save(OUT / (label + '_tree.json'), tree)
        files = {row['path']: row for row in tree['tree'] if row['type'] == 'blob'}
        if label == 'main':
            fixed = {'CURRENT_STATUS.md', 'README.md', 'registry/artifacts.csv', 'registry/claims.csv',
                     'aief_experiment_engine_v1.py',
                     'AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/validation.py',
                     'AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/oracle.py'}
            selected = fixed.intersection(files)
            selected |= {name for name, item in files.items()
                         if item.get('size', 0) < 250000 and name.endswith(('.md', '.py', '.csv'))
                         and ('errata' in name.lower() or
                              ('test' in name.lower() and any(x in name.lower() for x in
                                  ('validation', 'exact_equal', 'nan', 'oracle', 'engine'))))
                         and not name.startswith('workspace-')}
        else:
            fixed = {'audit_inbox/README.md', 'audit_inbox/TRIAGE.md',
                     'audit_inbox/briefing/STATE.md', 'audit_inbox/briefing/OPEN_QUESTIONS.md'}
            selected = fixed.intersection(files)
            selected |= {name for name, item in files.items()
                         if item.get('size', 0) < 225000 and name.endswith('.md')
                         and '/source_state/' not in name and '040282' in name.lower()
                         and any(x in name.lower() for x in
                                 ('intake', 'triage', 'review', 'feedback', '005', '006', '007', 'addendum'))}
        def acquire(name):
            content = get('https://raw.githubusercontent.com/' + REPO + '/' + commit + '/' + quote(name, safe='/'))
            blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
            if blob != files[name]['sha']:
                raise RuntimeError('Acquisition verification failed: ' + name)
            target = OUT / label / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            return {'path': name, 'blob': blob, 'bytes': len(content)}
        with ThreadPoolExecutor(max_workers=6) as pool:
            acquired = list(pool.map(acquire, sorted(selected)))
        save(OUT / (label + '_selected.json'), {'branch': branch, 'commit': commit,
             'fetched_and_verified': len(acquired), 'files': acquired,
             'scope': 'Selected007 current source/feedback navigation; not exhaustive repository review, old science rerun, or remote submission'})
        print(label, commit, 'selected', len(acquired), flush=True)
        for name in sorted(files):
            if any(x in name.lower() for x in ('040282', 'complex_nan', 'exact_equal', 'errata', 'test_validation')):
                if not any(x in name.lower() for x in ('/source_state/', '/checks/', '/standalone/')):
                    print('NAV', label, name, flush=True)


if __name__ == '__main__':
    main()
