import csv, hashlib, subprocess, sys, zipfile, io, collections
rev = sys.argv[1]
repo = '/workspace/audit_pp1/repo'
def blob(path):
    r = subprocess.run(['git','-C',repo,'cat-file','blob',f'{rev}:{path}'],capture_output=True)
    return r.stdout if r.returncode==0 else None
rows = list(csv.DictReader(open(f'{repo}/registry/artifacts.csv',encoding='utf-8',newline='')))
zips = {}
res = collections.Counter(); detail = collections.defaultdict(list)
for r in rows:
    c = r['container']; p = r['path']; exp = r['sha256']
    if c == 'worktree':
        b = blob(p)
    elif c.startswith('zip:'):
        zp = c[4:]
        if zp not in zips:
            zb = blob(zp); zips[zp] = zipfile.ZipFile(io.BytesIO(zb)) if zb else None
        z = zips[zp]
        try: b = z.read(p) if z else None
        except KeyError: b = None
    else:
        res['other_container'] += 1; continue
    if b is None: k = 'MISSING'
    else: k = 'SAME' if hashlib.sha256(b).hexdigest()==exp else 'CHANGED'
    key = (c.split(':')[0], k, r['tree_check_2026_10_28'])
    res[key]+=1
    if k=='CHANGED': detail['CHANGED'].append((r['artifact_id'],p,r['tree_check_2026_10_28']))
for k,v in sorted(res.items(), key=str): print(k, v)
for x in detail['CHANGED']: print('CHANGED', *x)
