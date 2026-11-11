import csv, hashlib, subprocess, sys, collections
rev=sys.argv[1]; repo='/workspace/audit_pp1/repo'
rows=list(csv.DictReader(open(f'{repo}/registry/artifacts.csv',encoding='utf-8',newline='')))
c=collections.Counter()
for r in rows:
    t=r['planned_stage4_target'].strip()
    if not r['container'].startswith('zip:') or not t: continue
    b=subprocess.run(['git','-C',repo,'cat-file','blob',f'{rev}:{t}'],capture_output=True)
    if b.returncode: c['target_absent']+=1; continue
    ok=hashlib.sha256(b.stdout).hexdigest()==r['sha256']
    c['match' if ok else 'MISMATCH']+=1
    if not ok: print('MISMATCH',r['artifact_id'],t)
print(dict(c))
