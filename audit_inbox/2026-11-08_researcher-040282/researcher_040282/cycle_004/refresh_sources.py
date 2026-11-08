"""Read-only selected source/intake refresh; no repository checkout or writes."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import urllib.request
from urllib.parse import quote

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_state'
REPO='jacobbrainard84-knightninja/AIEFS'
API='https://api.github.com/repos/'+REPO
HEADERS={'User-Agent':'Researcher-040282-read-only','Accept':'application/vnd.github+json'}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=60) as r:return r.read()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for branch,label in [('main','main'),('audit-inbox','inbox')]:
        detail=json.loads(get(API+'/branches/'+branch));(OUT/(label+'_branch.json')).write_text(json.dumps(detail,indent=2)+'\n')
        commit=detail['commit']['sha']
        tree=json.loads(get(API+'/git/trees/'+commit+'?recursive=1'));assert not tree.get('truncated')
        (OUT/(label+'_tree.json')).write_text(json.dumps(tree,indent=2)+'\n')
        files={item['path']:item for item in tree['tree'] if item['type']=='blob'}
        prior=json.loads((ROOT.parent/'cycle_003/source_state'/(label+'_selected.json')).read_text())
        selected={p for p in prior['paths'] if p in files}
        if label=='main':
            selected|={p for p in files if p.endswith('.lean')}
            selected|={p for p in files if p.endswith(('.md','.py')) and any(s in p.lower() for s in ['research/ema','research/coherence','complexema']) and files[p].get('size',0)<250_000}
        else:
            selected|={p for p in files if p.endswith('.md') and '040282' in p and files[p].get('size',0)<250_000}
        def acquire(path):
            url='https://raw.githubusercontent.com/'+REPO+'/'+commit+'/'+quote(path,safe='/')
            data=get(url);expected=files[path]['sha']
            observed=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            assert observed==expected
            out=OUT/label/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
            return path
        with ThreadPoolExecutor(max_workers=8) as pool:paths=sorted(pool.map(acquire,sorted(selected)))
        record={'branch':branch,'commit':commit,'fetched_and_verified':len(paths),'paths':paths,
            'scope':'Selected public read-only current-source/intake refresh, not a complete active-branch/assignment audit'}
        (OUT/(label+'_selected.json')).write_text(json.dumps(record,indent=2)+'\n')
        print(label,commit,'selected files',len(paths),flush=True)
    for label in ['main','inbox']:
        for p in sorted((OUT/label).rglob('*')):
            if p.is_file() and p.suffix in ['.lean','.md','.csv']:
                for n,line in enumerate(p.read_text(errors='replace').splitlines(),1):
                    lower=line.lower()
                    if any(word in lower for word in ['040282','unit disk','unit-disk','ema','coherence']):
                        print(str(p.relative_to(ROOT))+':'+str(n)+': '+line[:260])

if __name__=='__main__':main()
