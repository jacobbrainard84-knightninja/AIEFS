"""Selected, read-only011 source/feedback refresh. Imports no acquired code.
Outgoing metadata keeps identifiers only; Git objects are confined to an excluded
disposable navigation cache, never copied into the packet.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import os
import subprocess
from urllib.parse import quote
import urllib.request

HERE = Path(__file__).resolve().parent
OUT = HERE / 'source_state'
REPO = 'jacobbrainard84-knightninja/AIEFS'
API = 'https://api.github.com/repos/' + REPO
CACHE = Path.home()/'.cache/researcher040282-cycle011/navigation'
GIT_URL = 'https://github.com/' + REPO + '.git'
ENV = dict(os.environ, GIT_TERMINAL_PROMPT='0')
HEADERS = {'User-Agent': 'Researcher-040282-read-only', 'Accept': 'application/vnd.github+json'}


def get(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    OUT.mkdir(exist_ok=True)
    CACHE.mkdir(parents=True,exist_ok=True)
    subprocess.run(['git','init','--bare','--quiet',str(CACHE)],check=True,env=ENV,timeout=30)
    refs=subprocess.check_output(['git','ls-remote','--heads',GIT_URL,'main','audit-inbox'],text=True,env=ENV,timeout=60)
    heads={line.split()[1].removeprefix('refs/heads/'):line.split()[0] for line in refs.splitlines()}
    for branch, label in (('main', 'main'), ('audit-inbox', 'inbox')):
        commit = heads[branch]
        if not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise RuntimeError('Unexpected source identifier')
        save(OUT / (label + '_branch.json'), {'branch': branch, 'commit': commit,
             'metadata_policy': 'Only branch/commit; omit all author/committer/contact/signature payloads'})
        # Blobless shallow transfer: tree navigation, NOT a generated-data download.
        subprocess.run(['git','-C',str(CACHE),'fetch','--quiet','--depth=1','--no-tags','--filter=blob:none',
                        GIT_URL,commit],check=True,env=ENV,timeout=90)
        listing=subprocess.check_output(['git','-C',str(CACHE),'ls-tree','-r','-z',commit],text=True,env=ENV,timeout=30)
        rows=[]
        for line in listing.split('\0'):
            if not line:continue
            header,path=line.split('\t',1);mode,kind,object_id=header.split()
            rows.append({'path':path,'mode':mode,'type':kind,'sha':object_id})
        tree_id=subprocess.check_output(['git','-C',str(CACHE),'rev-parse',commit+'^{tree}'],text=True,env=ENV,timeout=30).strip()
        tree = {'sha':tree_id,'truncated':False,'tree':rows,
                'transport':'Git shallow blobless tree after GitHub API403; selected blobs fetched as raw only'}
        save(OUT / (label + '_tree.json'), tree)
        files = {row['path']: row for row in tree['tree'] if row['type'] == 'blob'}
        if label == 'main':
            fixed = {'CURRENT_STATUS.md','README.md','registry/artifacts.csv',
                     'aief_experiment_engine_v1.py'}
            selected = fixed.intersection(files)
            selected |= {name for name,item in files.items()
                         if name.startswith('lean/') and item.get('size',0)<100000
                         and (name.endswith(('.lean','README.md','lean-toolchain','lakefile.toml','lake-manifest.json')))}
            selected |= {name for name,item in files.items()
                         if item.get('size',0)<200000 and name.endswith(('.md','.py'))
                         and ('errata' in name.lower() or
                              ('test' in name.lower() and any(t in name.lower() for t in ('history','delay','phase','phasor','wrap','advance_state'))))
                         and not name.startswith('workspace-')}
        else:
            fixed = {'audit_inbox/README.md','audit_inbox/TRIAGE.md',
                     'audit_inbox/briefing/STATE.md','audit_inbox/briefing/OPEN_QUESTIONS.md'}
            selected = fixed.intersection(files)
            selected |= {name for name,item in files.items()
                         if item.get('size',0)<225000 and name.endswith('.md') and '/source_state/' not in name
                         and (('040282' in name.lower() and any(t in name.lower() for t in
                              ('intake','triage','review','feedback','005','006','007','008','009','011','addendum')))
                              or any(t in name.lower() for t in ('history','delay','phase','phasor','wrap','buffer','dynamics')))}
        def acquire(name):
            content = get('https://raw.githubusercontent.com/' + REPO + '/' + commit + '/' + quote(name, safe='/'))
            blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
            if blob != files[name]['sha']:
                raise RuntimeError('Acquisition verification failed: ' + name)
            if name not in ('registry/artifacts.csv',) and len(content)>225000: raise RuntimeError('Unexpected oversized selected text: '+name)
            target = OUT / label / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            return {'path': name, 'blob': blob, 'bytes': len(content)}
        with ThreadPoolExecutor(max_workers=6) as pool:
            acquired = list(pool.map(acquire, sorted(selected)))
        save(OUT / (label + '_selected.json'), {'branch': branch, 'commit': commit,
             'fetched_and_verified': len(acquired), 'files': acquired,
             'scope': 'Selected011 current source/feedback navigation; not exhaustive repository review, old science rerun, or remote submission'})
        print(label, commit, 'selected', len(acquired), flush=True)
        for name in sorted(files):
            if any(x in name.lower() for x in ('history','buffer','phase-step','phase_step','lean','040282')):
                if not any(x in name.lower() for x in ('/source_state/','/checks/','/standalone/')):
                    print('NAV',label,name,flush=True)



if __name__ == '__main__':
    main()
