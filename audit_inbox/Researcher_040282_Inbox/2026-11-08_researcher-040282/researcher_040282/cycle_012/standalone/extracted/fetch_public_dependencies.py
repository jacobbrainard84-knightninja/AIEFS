"""Fetch one reviewed public engine and three scope/compiler metadata files.
No acquired-source execution, raw author metadata or compiler download here.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=Path('upstream'))
    args=parser.parse_args();manifest=json.loads((Path(__file__).resolve().parent/'source_modules.json').read_text())
    def fetch(record):
        relative=Path(record['path'])
        if relative.is_absolute() or '..' in relative.parts or not (relative.suffix in {'.py','.csv'} or relative.name in {'lean-toolchain','lake-manifest.json'}):
            raise ValueError('Unexpected dependency path')
        target=args.output/relative;was_present=target.exists()
        if was_present:data=target.read_bytes()
        else:
            url='https://raw.githubusercontent.com/'+manifest['repo']+'/'+manifest['commit']+'/'+quote(record['path'],safe='/')
            request=urllib.request.Request(url,headers={'User-Agent':'Researcher-040282-read-only'})
            with urllib.request.urlopen(request,timeout=60) as response:data=response.read()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if blob!=record['blob'] or len(data)!=record['bytes']:raise RuntimeError('Dependency differs: '+record['path'])
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        return {'path':str(relative),'freshly_fetched':not was_present,'verified':True}
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(fetch,manifest['modules']+manifest['metadata']))
    print(json.dumps({'tested_main':manifest['commit'],'public_dependencies_fetched_and_verified':len(files),
                      'python_sources':len(manifest['modules']),'metadata_files':len(manifest['metadata']),
                      'files':files,'source_executed_by_fetcher':False,'raw_commit_author_metadata_requested':False},indent=2))


if __name__=='__main__':main()
