"""Verify audit_manifest.json. Run from the AIEFS repo root:
    python "AI Agent Audits/evidence/verify_manifest.py"            # published files (size + sha256)
    python "AI Agent Audits/evidence/verify_manifest.py" --inputs   # also the hashed repo inputs
Exit status: 0 if everything matches, 1 on any missing file or size/sha256 mismatch, 2 on usage errors."""
import hashlib, json, sys, glob, os
from pathlib import Path
E = Path(__file__).resolve().parent; P = E.parent; R = Path.cwd()
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
try: M = json.load(open(E / 'audit_manifest.json'))
except Exception as ex: print('cannot read audit_manifest.json:', ex); sys.exit(2)
bad = []
for rel, v in M['files_sha256'].items():
    p = P / rel
    if not p.is_file(): bad.append(f'MISSING  {rel}'); continue
    if p.stat().st_size != v['bytes']: bad.append(f'SIZE     {rel}: {p.stat().st_size} != {v["bytes"]}')
    elif sha(p) != v['sha256']: bad.append(f'SHA256   {rel}')
post = set(M.get('post_manifest_logs', []))  # attestation logs written after the manifest (not hashable in it)
listed = set(M['files_sha256']) | {'evidence/audit_manifest.json'} | post
extra = sorted(str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and str(p.relative_to(P)) not in listed
               and '__pycache__' not in p.parts)
for x in extra: bad.append(f'UNLISTED {x}')
n_in = 0
if '--inputs' in sys.argv:
    if not (R / 'AIEF_1_3_falsification_updated.py').exists(): print('--inputs: run from the AIEFS repo root'); sys.exit(2)
    for key, h in M['inputs_sha256'].items():
        n_in += 1
        if key.startswith('runs/') and '(aggregate' in key:
            d = key.split('/*')[0]; fs = sorted(glob.glob(str(R / d / '*'))); a = hashlib.sha256()
            for f in fs: a.update(f"{os.path.relpath(f, R)} {sha(f)}\n".encode())
            if a.hexdigest() != h: bad.append(f'INPUT    {key}')
        elif not (R / key).is_file(): bad.append(f'INPUT MISSING {key}')
        elif sha(R / key) != h: bad.append(f'INPUT    {key}')
print(f"checked {len(M['files_sha256'])} published files" + (f" and {n_in} inputs" if n_in else '') + (f"; {len(post)} post-manifest logs listed but not hashed" if post else ''))
for b in bad: print(b)
print('OK' if not bad else f'FAILED: {len(bad)} problem(s)')
sys.exit(1 if bad else 0)
