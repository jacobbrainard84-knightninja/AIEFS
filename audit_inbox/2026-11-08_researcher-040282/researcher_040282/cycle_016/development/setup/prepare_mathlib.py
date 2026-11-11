"""Targeted prescribed Mathlib cache into OWN disposable016 target only.
Public setup dependencies are executed by Lake, not counted as science/controls.
No global toolchain setting, credentials, remote write or outgoing Git metadata.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

HERE=Path(__file__).resolve().parent
DEFAULT=Path.home()/'.cache/researcher040282-cycle016'


def require(condition,message):
    if not condition:raise RuntimeError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cache',type=Path,default=DEFAULT)
    parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();started=time.perf_counter()
    cache=args.cache.resolve();manifest=json.loads((HERE/'source_modules.json').read_text());record=manifest['mathlib']
    install=cache/manifest['lean_toolchain']['asset_name'].removesuffix('.tar.zst');lake=install/'bin/lake';lean=install/'bin/lean'
    require(lean.is_file() and lake.is_file(),'Complete prescribed runtime required before Mathlib: setup blocker')
    env=dict(os.environ,PATH=str(install/'bin')+os.pathsep+os.environ.get('PATH',''),GIT_TERMINAL_PROMPT='0',
             XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),
             ELAN_HOME=str(cache/'elan-home'),PYTHONDONTWRITEBYTECODE='1')
    mathlib=cache/'mathlib4'
    if not (mathlib/'.git').is_dir():
        subprocess.run(['git','clone','--quiet','--depth','1','--branch',record['inputRev'],record['url']+'.git',str(mathlib)],
                       env=env,check=True,timeout=180)
    revision=subprocess.check_output(['git','-C',str(mathlib),'rev-parse','HEAD'],env=env,text=True,timeout=30).strip()
    require(revision==record['revision'],'Wrong prescribed Mathlib source: setup blocker')
    source_prescription=(mathlib/'lean-toolchain').read_text().strip()
    require(source_prescription==manifest['lean_toolchain']['toolchain'],'Incompatible dependency compiler prescription')
    require(all((mathlib/path).is_file() for path in record['targets']),'Missing targeted dependency source')
    print('Acquiring targeted public cache closure only:',len(record['targets']),'roots',flush=True)
    subprocess.run([str(lake),'exe','cache','get']+record['targets'],cwd=mathlib,env=env,check=True,timeout=660)
    size=sum(path.stat().st_size for path in cache.rglob('*') if path.is_file() and not path.is_symlink())
    require(size<=12*1024**3,'Owned setup exceeded preregistered12GiB resource bound')
    version=subprocess.check_output([str(lean),'--version'],env=env,text=True,timeout=20).strip()
    receipt={'mathlib_revision':revision,'compiler_version':version,'compiler_prescription':source_prescription,
             'mathlib_directory':str(mathlib),'compiler_binary':str(lean),'cache':str(cache),'targeted_roots':record['targets'],
             'targeted_not_omnibus_Mathlib':True,'cache_helper_returncode':0,'owned_regular_file_logical_bytes':size,
             'all_setup_cache_download_targets_inside_own_prefix':True,'global_toolchain_changed':False,
             'raw_git_objects_not_copied_to_packet':True,'remove_only_own_cache_after_direct_checks':True,
             'elapsed_seconds':time.perf_counter()-started}
    args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
