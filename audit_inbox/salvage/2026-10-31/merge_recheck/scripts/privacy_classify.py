"""Classify PII-like hits in files added/modified vs a base ref. Prints file, line, type and pin status ONLY,
never matched values. Private literals are used only to count/flag matches by index.
Usage: python3 privacy_classify.py <repo> <base> [private_literals_file]"""
import re, subprocess, sys, os, csv, json, collections
repo, base = sys.argv[1], sys.argv[2]
priv = [l.strip() for l in open(sys.argv[3]) if l.strip()] if len(sys.argv) > 3 else []
os.chdir(repo)
ns = subprocess.run(['git','diff','--name-status','--no-renames',base,'HEAD'],capture_output=True,text=True).stdout.splitlines()
pinned = {}
for r in csv.DictReader(open('registry/artifacts.csv',encoding='utf-8',newline='')):
    if r['container']=='worktree': pinned[r['path']] = r['artifact_id']
man = json.load(open('AI Agent Audits/evidence/audit_manifest.json'))
inputs = set()
def walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(k,str) and '/' not in k and k.endswith(('.md','.txt','.py','.csv','.json')): inputs.add(k)
            if isinstance(k,str): inputs.add(k)
            walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
walk(man.get('inputs_sha256', {}))
PAT = {'home_path': rb'(?:/home/|/Users/|/root/)[A-Za-z0-9_.-]+|[A-Z]:\\\\?Users\\\\?[A-Za-z]',
       'ipv4': rb'\b(?:\d{1,3}\.){3}\d{1,3}\b',
       'email': rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}',
       'phone': rb'(?<![\d.])\+?\d{1,3}[ .-]\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?![\d.])'}
GENERIC = (b'/home/user', b'/home/box', b'/root/', b'/home/runner', b'/home/username', b'/Users/USER', b'/home/<')
out = []
tot = collections.Counter()
for line in ns:
    st, path = line.split('\t',1)
    if st=='D': continue
    b = open(path,'rb').read()
    binary = b'\x00' in b[:8000]
    for k,r in PAT.items():
        for m in re.finditer(r,b):
            v = m.group(0)
            if k=='email' and v.endswith((b'.invalid',b'example.com',b'.example',b'.test')): continue
            ln = b.count(b'\n',0,m.start())+1
            sub = ''
            if k=='home_path':
                pl = [i for i,p in enumerate(priv,1) if p.encode() in v]
                sub = f'private_literal#{pl}' if pl else ('generic' if v.startswith(GENERIC) else 'other_username')
            if k=='ipv4':
                parts=[int(x) for x in v.split(b'.')]
                ctx = b[max(0,m.start()-40):m.end()+40]
                sub = 'invalid_octet' if max(parts)>255 else ('private_range' if parts[0] in (10,127) or parts[:2]==[192,168] or (parts[0]==172 and 16<=parts[1]<=31) else 'public_range')
                if binary or b'stream' in ctx or b'obj' in ctx: sub += ',in_binary_or_pdf_stream'
                if re.search(rb'\d\.\d+\.\d+\.\d+', ctx) and b'version' in ctx.lower(): sub += ',version-like'
            if k=='email':
                pl = [i for i,p in enumerate(priv,1) if p.encode() in v]
                sub = f'private_literal#{pl}' if pl else 'other'
            out.append((path,ln,k,sub,pinned.get(path,''),'AUDIT_INPUT' if path in inputs else '', st))
            tot[(k,sub.split(',')[0])]+=1
    for i,p in enumerate(priv,1):
        c=b.count(p.encode())
        if c: tot[('private_literal_any',f'#{i}')]+=c
for o in out: print('\t'.join(map(str,o)))
print('TOTALS', dict(tot))
print('FILES', len({o[0] for o in out}))
