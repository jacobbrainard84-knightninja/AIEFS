#!/usr/bin/env python3
"""Inventory the extracted zips and PDFs from commit 6b49a7b and compare by SHA-256
against every file tracked in the repo at 6b49a7b (excluding the new items themselves),
and against files inside the repo's other tracked workspace-*.zip archives.
Read-only on repo/. Output: inventory.json"""
import hashlib, json, os, subprocess, zipfile, collections, mimetypes
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, "repo")
NEW = subprocess.check_output(["git","-C",REPO,"diff","--name-only","d041c69","6b49a7b"],text=True).split("\n")
NEW = [n for n in NEW if n]
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()
tracked = subprocess.check_output(["git","-C",REPO,"ls-files","-z"],text=True).split("\0")
repo_index = collections.defaultdict(list)
for t in tracked:
    if not t or t in NEW: continue
    p=os.path.join(REPO,t)
    if os.path.isfile(p): repo_index[sha(p)].append(t)
# members of pre-existing tracked zips
zip_index = collections.defaultdict(list)
for t in tracked:
    if t.endswith(".zip") and t not in NEW:
        try:
            with zipfile.ZipFile(os.path.join(REPO,t)) as z:
                for i in z.infolist():
                    if i.is_dir(): continue
                    zip_index[hashlib.sha256(z.read(i)).hexdigest()].append(f"{t}::{i.filename}")
        except Exception as e: print("zip err",t,e)
def ftype(p):
    try: return subprocess.check_output(["file","-b",p],text=True).strip()[:80]
    except Exception:
        import mimetypes
        ext=os.path.splitext(p)[1].lower()
        return {".py":"python source",".md":"markdown",".npz":"numpy archive",".npy":"numpy array",
                ".json":"json",".csv":"csv",".txt":"text",".log":"text log",".png":"png image",
                ".pdf":"pdf",".zip":"zip"}.get(ext, mimetypes.guess_type(p)[0] or "unknown")+" (by extension; `file` not installed)"
out={"commit":"6b49a7b","base":"d041c69","items":[]}
for n in NEW:
    p=os.path.join(REPO,n); item={"path":n,"bytes":os.path.getsize(p),"sha256":sha(p),
        "dup_in_repo":repo_index.get(sha(p),[])}
    if n.endswith(".zip"):
        d=os.path.join(ROOT,"scratch","zips",os.path.basename(n)[:-4])
        members=[]
        for dp,_,fs in os.walk(d):
            for f in fs:
                fp=os.path.join(dp,f); h=sha(fp); rel=os.path.relpath(fp,d)
                members.append({"path":rel,"bytes":os.path.getsize(fp),"sha256":h,"type":ftype(fp),
                    "dup_in_repo_tracked":repo_index.get(h,[]),"dup_in_repo_zips":zip_index.get(h,[])[:5]})
        members.sort(key=lambda m:m["path"])
        item["members"]=members
        item["n_members"]=len(members)
        item["n_members_dup_tracked"]=sum(1 for m in members if m["dup_in_repo_tracked"])
        item["n_members_dup_any"]=sum(1 for m in members if m["dup_in_repo_tracked"] or m["dup_in_repo_zips"])
        item["bytes_unique"]=sum(m["bytes"] for m in members if not(m["dup_in_repo_tracked"] or m["dup_in_repo_zips"]))
    elif n.endswith(".pdf"):
        item["pdfinfo"]=subprocess.check_output(["pdfinfo",p],text=True)
    else:
        item["note"]="mode change only: "+subprocess.check_output(["git","-C",REPO,"diff","--summary","d041c69","6b49a7b","--",n],text=True).strip()
    out["items"].append(item)
json.dump(out,open(os.path.join(ROOT,"inventory.json"),"w"),indent=1)
for it in out["items"]:
    print(it["path"],it["bytes"],"dup:",it["dup_in_repo"][:3], it.get("n_members"),it.get("n_members_dup_tracked"),it.get("n_members_dup_any"),it.get("bytes_unique"))
