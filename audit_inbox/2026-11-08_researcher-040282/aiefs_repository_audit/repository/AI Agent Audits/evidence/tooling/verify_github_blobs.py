"""Compare local files with what landed on GitHub, by git blob sha1 (round 3, 2026-10-24).
Usage (from the AIEFS repo root):
  python "AI Agent Audits/evidence/tooling/verify_github_blobs.py" TREE.json [LOCAL_DIR]
TREE.json is the JSON of a recursive git tree for the commit to check, e.g. from
  https://api.github.com/repos/<owner>/<repo>/git/trees/<commit>?recursive=1   (public, read-only)
or `git ls-tree -r <commit>` converted to {"tree":[{"path":..,"type":"blob","sha":..}]}. LOCAL_DIR defaults to "AI Agent Audits".
The git blob sha1 of a file is sha1(b"blob <size>\\0" + bytes), the same as `git hash-object FILE`.
Exit 0 if every local file is present remotely with the same blob sha and nothing extra is under the prefix."""
import hashlib, json, sys
from pathlib import Path
tree = json.load(open(sys.argv[1])); items = tree.get('tree', tree) if isinstance(tree, dict) else tree
L = Path(sys.argv[2] if len(sys.argv) > 2 else 'AI Agent Audits'); prefix = 'AI Agent Audits/'
blob = lambda b: hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
remote = {i['path']: i['sha'] for i in items if i.get('type') == 'blob' and i['path'].startswith(prefix)}
local = {prefix + str(p.relative_to(L)): blob(p.read_bytes()) for p in sorted(L.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
miss = sorted(set(local) - set(remote)); extra = sorted(set(remote) - set(local))
diff = sorted(k for k in set(local) & set(remote) if local[k] != remote[k])
print(f'local {len(local)} files, remote {len(remote)} blobs under {prefix!r}')
for k in miss: print('NOT ON REMOTE ', k)
for k in extra: print('ONLY ON REMOTE', k)
for k in diff: print('BLOB DIFFERS  ', k)
ok = not (miss or extra or diff); print('IDENTICAL' if ok else 'DIFFERENT'); sys.exit(0 if ok else 1)
