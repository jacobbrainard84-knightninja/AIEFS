"""Install the recorded Lean toolchain into an excluded disposable cache.

Downloads are public/read-only. No repository files or global toolchain settings
are changed. The release asset is checked against its published SHA-256 digest.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parent
CACHE=ROOT.parent.parent/'.cache/researcher040282'
CACHE.mkdir(parents=True,exist_ok=True)
release=json.loads((ROOT/'lean_release.json').read_text())
asset=next(a for a in release['assets'] if a['name']=='lean-4.33.1-linux.tar.zst')
archive=CACHE/asset['name']
install=CACHE/'lean-4.33.1-linux'
if (install/'bin/lean').is_file():
    print(subprocess.check_output([str(install/'bin/lean'),'--version'],text=True),flush=True)
    raise SystemExit(0)
if not archive.exists() or archive.stat().st_size!=asset['size']:
    temporary=archive.with_suffix(archive.suffix+'.partial')
    print('Downloading public Lean asset:',asset['name'],asset['size'],'bytes',flush=True)
    request=urllib.request.Request(asset['browser_download_url'],headers={'User-Agent':'Researcher-040282-read-only'})
    with urllib.request.urlopen(request,timeout=60) as response,temporary.open('wb') as handle:
        shutil.copyfileobj(response,handle,8*1024*1024)
    temporary.replace(archive)
h=hashlib.sha256()
with archive.open('rb') as handle:
    for block in iter(lambda:handle.read(8*1024*1024),b''):h.update(block)
assert archive.stat().st_size==asset['size']
assert 'sha256:'+h.hexdigest()==asset['digest']
print('Asset checksum matches published release digest.',flush=True)
try:import zstandard
except ImportError:
    subprocess.run([sys.executable,'-m','pip','install','--quiet','zstandard'],check=True)
    import zstandard
print('Extracting toolchain into disposable cache.',flush=True)
with archive.open('rb') as source,zstandard.ZstdDecompressor().stream_reader(source) as decoded:
    with tarfile.open(fileobj=decoded,mode='r|') as tar:
        tar.extractall(CACHE,filter='data')
print(subprocess.check_output([str(install/'bin/lean'),'--version'],text=True),flush=True)
(ROOT/'lean_installation.json').write_text(json.dumps({'toolchain':'leanprover/lean4:v4.33.1',
    'asset':asset['browser_download_url'],'published_digest':asset['digest'],
    'checksum_verified':True,'compiler_version':subprocess.check_output([str(install/'bin/lean'),'--version'],text=True).strip(),
    'installation_scope':'disposable excluded cache; no global or repository change'},indent=2)+'\n')
