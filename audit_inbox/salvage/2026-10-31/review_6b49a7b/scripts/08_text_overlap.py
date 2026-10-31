#!/usr/bin/env python3
"""Text-overlap check: are the 3 new Origin Document PDFs already in the repo as other PDFs?
Uses 12-word shingles from pdftotext of every tracked PDF in 'Project Origins/' and 'Project Histories/'.
Output: results/text_overlap.json (fraction of each new doc's shingles found in each old PDF)."""
import subprocess, os, re, json, glob
R="repo"; NEW=["Project Origins/Origin Document.pdf","Project Origins/Origin Document 01.pdf","Project Origins/Origin Document 02.pdf"]
def sh(path):
    t=subprocess.run(["pdftotext",path,"-"],capture_output=True,text=True).stdout.lower()
    w=re.findall(r"[a-z0-9]+",t); return {" ".join(w[i:i+12]) for i in range(0,max(0,len(w)-12),3)}
old=[p for p in glob.glob(R+"/Project Origins/*.pdf")+glob.glob(R+"/Project Histories/*.pdf") if os.path.relpath(p,R) not in NEW]
newsh={n:sh(os.path.join(R,n)) for n in NEW}
res={}
for o in old:
    s=sh(o)
    for n,ns in newsh.items():
        f=len(ns&s)/max(1,len(ns))
        if f>0.01: res.setdefault(n,{})[os.path.relpath(o,R)]=round(f,3)
res["_between_new"]={f"{a} vs {b}":round(len(newsh[a]&newsh[b])/max(1,len(newsh[a])),3) for a in NEW for b in NEW if a!=b}
json.dump(res,open("results/text_overlap.json","w"),indent=1); print(json.dumps(res,indent=1))
