import csv, hashlib, os, sys
rows = list(csv.DictReader(open('registry/artifacts.csv', encoding='utf-8')))
print('columns:', list(rows[0].keys()))
for r in rows:
    if r['container'] != 'worktree': continue
    p = r['path']
    if not os.path.isfile(p): continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if h != r['sha256']:
        print('CHANGED', r['artifact_id'], p, r['sha256'][:12], '->', h[:12], 'tree_check=', r.get('tree_check',''))
