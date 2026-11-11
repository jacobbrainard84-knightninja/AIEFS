import re,sys,glob,os
proj=sys.argv[1]; names=[]
for f in sorted(glob.glob(f'{proj}/{proj}/**/*.lean',recursive=True)):
    ns=[]; sec=[]
    for line in open(f):
        m=re.match(r'\s*namespace\s+(\S+)',line)
        if m: ns.append(m.group(1)); sec.append('ns'); continue
        m=re.match(r'\s*(noncomputable\s+)?section\b\s*(\S*)',line)
        if m: sec.append('sec'); continue
        m=re.match(r'\s*end\b',line)
        if m and sec:
            if sec.pop()=='ns': ns.pop()
            continue
        m=re.match(r'\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?(theorem|lemma)\s+([^\s:(\[{]+)',line)
        if m: names.append('.'.join(ns+[m.group(2)]))
print(f'import {proj}')
for n in names: print(f'#print axioms {n}')
