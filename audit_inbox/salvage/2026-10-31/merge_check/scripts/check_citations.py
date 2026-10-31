"""Extract file+line citations from registry/claims.csv audit_source and print the cited line (truncated)
so each citation can be checked by hand. Read-only."""
import csv, re, sys, os
root = sys.argv[1]
A = os.path.join(root, 'AI Agent Audits')
files = {'salvage': 'AIEFS_salvage.md', 'resp1': 'AIEFS_audit_response.md', 'resp2': 'AIEFS_audit_response_2.md',
         'resp3': 'AIEFS_audit_response_3.md', 'audit.md': 'AIEFS_audit.md'}
lines = {k: open(os.path.join(A, v), encoding='utf-8').read().split('\n') for k, v in files.items()}
rows = list(csv.DictReader(open(os.path.join(root, 'registry/claims.csv'), encoding='utf-8')))
bad = 0
for r in rows:
    src = r['audit_source']
    # split on ';' segments, each begins with a file key
    for seg in re.split(r';', src):
        seg = seg.strip()
        key = next((k for k in files if seg.startswith(k)), None)
        if not key:
            continue
        for m in re.finditer(r'\(lines? (\d+)(?:-(\d+))?\)', seg):
            a = int(m.group(1)); b = int(m.group(2) or a)
            for ln in range(a, b + 1):
                txt = lines[key][ln - 1] if ln <= len(lines[key]) else '<<OUT OF RANGE>>'
                if txt.strip() == '': bad += 1
                print(f"{r['claim_id']:16s} {key}:{ln:<4d} | {txt[:150]}")
print('blank/out-of-range cited lines:', bad)
