#!/usr/bin/env python3
"""Hygiene scan of the new items (PDF text extracts + extracted zip members).
Reports TYPE and LOCATION only (file, line), never the matched value.
Output: results/hygiene_scan.json"""
import os, re, json, collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT={
 "email":re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
 "home_path_generic(/home/user,/home/<user>)":re.compile(r"/home/(user|deck)\b"),
 "home_path_other":re.compile(r"/home/(?!user\b|deck\b)[A-Za-z0-9._-]+|/Users/[A-Za-z0-9._-]+|C:\\\\Users"),
# [line redacted during salvage: contained a private literal]
 "phone_like":re.compile(r"(?<![\d.])(?:\+?1[ -.]?)?\(?\d{3}\)?[ -.]\d{3}[ -.]\d{4}(?![\d.])"),
 "github_token":re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"),
 "openai_like_key":re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
 "aws_key":re.compile(r"AKIA[0-9A-Z]{16}"),
 "private_key":re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
 "bearer_or_password":re.compile(r"(?i)\b(bearer\s+[A-Za-z0-9._-]{20,}|password\s*[:=]\s*\S+|api[_-]?key\s*[:=]\s*\S+)"),
 "ip_address":re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"),
 "street_address":re.compile(r"\b\d{2,5}\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Blvd)\b"),
 "personal_context":re.compile(r"(?i)\b(my (wife|husband|son|daughter|kids?|job|employer|boss|address|phone)|factory|I work (at|in)|off time|formal training|college|builds? desks|my (age|birthday|town|city|state))\b"),
 "owner_name":re.compile(r"(?i)\bjacob\b|brainard|knightninja"),
}
TXT=(".txt",".py",".md",".json",".csv",".log")
def scan_file(path,label):
    hits=collections.defaultdict(list)
    try: lines=open(path,errors="replace").read().split("\n")
    except Exception: return {}
    for i,l in enumerate(lines,1):
        for k,p in PAT.items():
            if p.search(l):
                if k=="ip_address" and not all(0<=int(x)<=255 for x in re.findall(r"\d+",p.search(l).group(0))): continue
                hits[k].append(i)
    return {k:{"count":len(v),"lines_first":v[:12]} for k,v in hits.items()}
res={}
for f in sorted(os.listdir(os.path.join(ROOT,"scratch/pdf"))):
    if f.endswith(".txt") and not f.endswith(".info.txt"):
        res["Project Origins/"+f.replace("_"," ").replace(".txt",".pdf")+" (pdftotext -layout line numbers)"]=scan_file(os.path.join(ROOT,"scratch/pdf",f),f)
zd=os.path.join(ROOT,"scratch/zips")
for z in sorted(os.listdir(zd)):
    p=os.path.join(zd,z)
    if not os.path.isdir(p): continue
    for dp,_,fs in os.walk(p):
        for f in fs:
            if f.endswith(TXT) and os.path.getsize(os.path.join(dp,f))<6_000_000:
                r=scan_file(os.path.join(dp,f),f)
                if r: res[f"Project Histories/{z}.zip::{os.path.relpath(os.path.join(dp,f),p)}"]=r
os.makedirs(os.path.join(ROOT,"results"),exist_ok=True)
json.dump(res,open(os.path.join(ROOT,"results/hygiene_scan.json"),"w"),indent=1)
agg=collections.Counter()
for loc,r in res.items():
    for k,v in r.items(): agg[k]+=v["count"]
print("TOTALS:",dict(agg))
for loc,r in res.items():
    print(loc[:110], {k:(v["count"],v["lines_first"][:5]) for k,v in r.items()})
