"""Disposable prescribed complete Lean runtime; Mathlib is a separate targeted setup; no global toolchain change.
Public release verified before selective extraction. Caller may supply installed
compiler instead. Own cache is excluded from snapshots and removed at closeout.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

HERE=Path(__file__).resolve().parent
DEFAULT=Path.home()/'.cache/researcher040282-cycle016'


def require(condition,message):
    if not condition:raise RuntimeError(message)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,default=DEFAULT)
    p.add_argument('--receipt',type=Path,required=True);args=p.parse_args();start=time.perf_counter()
    cache=args.cache.resolve();cache.mkdir(parents=True,exist_ok=True)
    record=json.loads((HERE/'source_modules.json').read_text())['lean_toolchain']
    archive=cache/record['asset_name'];install=cache/record['asset_name'].removesuffix('.tar.zst');binary=install/'bin/lean'
    if not archive.is_file() or archive.stat().st_size!=record['bytes']:
        partial=archive.with_name(archive.name+'.partial')
        print('Downloading disposable prescribed compiler asset:',record['bytes'],'bytes',flush=True)
        request=urllib.request.Request(record['url'],headers={'User-Agent':'Researcher-040282-read-only'})
        with urllib.request.urlopen(request,timeout=60) as response,partial.open('wb') as stream:
            shutil.copyfileobj(response,stream,8*1024*1024)
        partial.replace(archive)
    digest=hashlib.sha256()
    with archive.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):digest.update(block)
    require(archive.stat().st_size==record['bytes'] and 'sha256:'+digest.hexdigest()==record['published_digest'],
            'Compiler asset differs from recorded public release')
    decoder=cache/'decoder'
    try:zstandard=importlib.import_module('zstandard');decoder_installed=False
    except ImportError:
        if not (decoder/'zstandard').is_dir():
            subprocess.run([sys.executable,'-m','pip','install','--quiet','--disable-pip-version-check','--no-input',
                            '--no-cache-dir','--no-deps','--target',str(decoder),'zstandard==0.25.0'],check=True,timeout=90)
        sys.path.insert(0,str(decoder));zstandard=importlib.import_module('zstandard');decoder_installed=True
    files=0;bytes_written=0
    print('Extracting complete compiler/runtime for Lake cache helper; Mathlib separate.',flush=True)
    with archive.open('rb') as source,zstandard.ZstdDecompressor().stream_reader(source) as decoded:
        with tarfile.open(fileobj=decoded,mode='r|') as tar:
            for member in tar:
                path=Path(member.name)
                require(not path.is_absolute() and '..' not in path.parts,'Unsafe release member path')
                if path.parts[0]!=install.name:raise RuntimeError('Unexpected compiler release root')
                wanted=True  # complete verified public runtime, own disposable target only
                if wanted:
                    tar.extract(member,cache,filter='data');files+=1;bytes_written+=member.size
    require(binary.is_file(),'Complete compiler extraction incomplete')
    version=subprocess.check_output([str(binary),'--version'],text=True).strip()
    expected=record['toolchain'].rsplit(':v',1)[1]
    require('version '+expected+',' in version,'Wrong prescribed compiler')
    receipt={'toolchain':record['toolchain'],'compiler_version':version,'public_asset_verified':True,
             'download_bytes':record['bytes'],'complete_runtime_extracted_members':files,'complete_runtime_extracted_bytes':bytes_written,
             'compiler_binary':str(binary),'cache':str(cache),'Mathlib_installed':False,'global_toolchain_changed':False,
             'decoder_installed_into_disposable_target':decoder_installed,'decoder_version':zstandard.__version__,
             'cache_ephemeral_until_direct_checks_complete':True,
             'elapsed_seconds':time.perf_counter()-start}
    args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
