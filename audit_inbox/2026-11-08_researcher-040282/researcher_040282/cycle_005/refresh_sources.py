"""Public read-only source/intake acquisition with minimal, contact-free metadata.
Never persist raw commit API responses, author/committer contact fields, or
signature payloads. Blob IDs identify acquired sources; no remote write occurs.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import quote
import urllib.request

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_state'
REPO='jacobbrainard84-knightninja/AIEFS'
API='https://api.github.com/repos/'+REPO
HEADERS={'User-Agent':'Researcher-040282-read-only','Accept':'application/vnd.github+json'}
EMAIL=re.compile(r'[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=60) as r:return r.read()


def write_json(path,value):
    text=json.dumps(value,indent=2)+'\n';assert not EMAIL.search(text)
    path.write_text(text)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for branch,label in [('main','main'),('audit-inbox','inbox')]:
        raw=json.loads(get(API+'/branches/'+branch));commit=raw['commit']['sha']
        # Keep only explicit acquisition identifiers; do not copy commit metadata.
        write_json(OUT/(label+'_branch.json'),{'branch':branch,'commit':commit,'metadata_policy':'author/committer/contact/signature payload omitted'})
        tree=json.loads(get(API+'/git/trees/'+commit+'?recursive=1'));assert not tree.get('truncated')
        tree={'sha':tree['sha'],'truncated':False,'tree':[{k:x[k] for k in ['path','mode','type','sha','size'] if k in x} for x in tree['tree']]}
        write_json(OUT/(label+'_tree.json'),tree)
        files={x['path']:x for x in tree['tree'] if x['type']=='blob'}
        if label=='main':
            fixed={'CURRENT_STATUS.md','registry/claims.csv','registry/artifacts.csv','aief_experiment_engine_v1.py','.github/workflows/repo-checks.yml'}
            selected={p for p in fixed if p in files}
            selected|={p for p in files if p.endswith(('.py','.md','.yml','.sh','.csv')) and files[p].get('size',0)<300_000 and any(w in p.lower() for w in ['proposal_bridge','proposal-bridge','bridge_proposal','oracle','analysis_v4_1','analysis_v41','analysis_v4.1','errata','erratum'])}
        else:
            nav={'audit_inbox/README.md','audit_inbox/TRIAGE.md','audit_inbox/briefing/STATE.md','audit_inbox/briefing/NORTH_STAR.md','audit_inbox/briefing/OPEN_QUESTIONS.md'}
            selected={p for p in nav if p in files}
            selected|={p for p in files if '040282' in p and p.endswith(('.md','.csv')) and '/source_state/' not in p and files[p].get('size',0)<180_000}
        def acquire(path):
            data=get('https://raw.githubusercontent.com/'+REPO+'/'+commit+'/'+quote(path,safe='/'))
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==files[path]['sha']
            dest=OUT/label/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            return {'path':path,'blob':files[path]['sha'],'bytes':len(data)}
        with ThreadPoolExecutor(max_workers=8) as pool:records=list(pool.map(acquire,sorted(selected)))
        write_json(OUT/(label+'_selected.json'),{'branch':branch,'commit':commit,'fetched_and_verified':len(records),'files':records,'scope':'Selected current-source/intake refresh, not exhaustive branch assignment/review audit'})
        print(label,commit,'selected',len(records),flush=True)
        if label=='main':
            print('Relevant paths:',flush=True)
            for p in files:
                if any(w in p.lower() for w in ['proposal_bridge','proposal-bridge','analysis_v4_1','analysis_v41','analysis_v4.1','upload_new','checksum','oracle']):print(p,flush=True)


if __name__=='__main__':main()
