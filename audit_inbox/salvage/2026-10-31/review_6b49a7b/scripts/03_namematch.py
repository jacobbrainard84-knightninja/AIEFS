#!/usr/bin/env python3
"""For zip members NOT byte-identical to anything in the repo, find tracked repo files with the
same basename and report a text similarity ratio (difflib) for text files. Output: namematch.json"""
import json, os, subprocess, difflib, collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); REPO=os.path.join(ROOT,"repo")
inv=json.load(open(os.path.join(ROOT,"inventory.json")))
tracked=[t for t in subprocess.check_output(["git","-C",REPO,"ls-files"],text=True).splitlines()]
byname=collections.defaultdict(list)
for t in tracked: byname[os.path.basename(t)].append(t)
TXT=(".py",".md",".txt",".csv",".json",".log",".lean")
res=[]
for it in inv["items"]:
    if "members" not in it: continue
    zdir=os.path.join(ROOT,"scratch","zips",os.path.basename(it["path"])[:-4])
    for m in it["members"]:
        if m["dup_in_repo_tracked"] or m["dup_in_repo_zips"]: continue
        b=os.path.basename(m["path"]); cands=byname.get(b,[])
        if not cands: res.append({"zip":it["path"],"member":m["path"],"same_name_in_repo":[]}); continue
        best=[]
        for c in cands[:8]:
            r=None
            if b.endswith(TXT) and m["bytes"]<2_000_000:
                a=open(os.path.join(zdir,m["path"]),errors="replace").read().splitlines()
                bb=open(os.path.join(REPO,c),errors="replace").read().splitlines()
                r=round(difflib.SequenceMatcher(None,a,bb,autojunk=False).ratio(),3)
            best.append({"repo_path":c,"line_similarity":r})
        res.append({"zip":it["path"],"member":m["path"],"same_name_in_repo":best})
json.dump(res,open(os.path.join(ROOT,"namematch.json"),"w"),indent=1)
for r in res:
    if r["same_name_in_repo"]:
        print(os.path.basename(r["zip"])[10:18], r["member"][:70], [(c["repo_path"][:60],c["line_similarity"]) for c in r["same_name_in_repo"][:3]])
print("no-name-match count:",sum(1 for r in res if not r["same_name_in_repo"]))
