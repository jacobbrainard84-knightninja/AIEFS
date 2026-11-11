"""Scan files added/modified on the merge-prep branch vs main. Prints counts and locations only (never values).
Usage: python3 diff_scan.py <repo> <base-ref> [private_literals_file]"""
import re, subprocess, sys, os, collections
repo, base = sys.argv[1], sys.argv[2]
priv = [l.strip() for l in open(sys.argv[3]) if l.strip()] if len(sys.argv) > 3 else []
os.chdir(repo)
ns = subprocess.run(['git', 'diff', '--name-status', '--no-renames', base, 'HEAD'], capture_output=True, text=True).stdout.splitlines()
PAT = {'email': rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}',
       'home_path': rb'(?:/home/|/Users/|/root/)[A-Za-z0-9_.-]+|[A-Z]:\\\\?Users\\\\?[A-Za-z]',
       'workspace_path': rb'/workspace/',
       'github_token': rb'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}',
       'sk_key': rb'\bsk-[A-Za-z0-9]{20,}', 'aws': rb'\bAKIA[0-9A-Z]{16}\b', 'slack': rb'\bxox[abpr]-[A-Za-z0-9-]{10,}',
       'pem': rb'-----BEGIN [A-Z ]*PRIVATE KEY-----', 'bearer': rb'\b[Bb]earer\s+[A-Za-z0-9._-]{20,}',
       'ipv4': rb'\b(?:\d{1,3}\.){3}\d{1,3}\b'}
tot = collections.Counter()
for line in ns:
    st, path = line.split('\t', 1)
    if st == 'D': print('DELETED', path); continue
    b = open(path, 'rb').read()
    flags = []
    if len(b) >= 1_000_000: flags.append(f'LARGE {len(b)}B')
    if b'\r\n' in b: flags.append(f'CRLF x{b.count(chr(13).encode()+chr(10).encode())}')
    binary = b'\x00' in b[:8000]
    if binary: flags.append('BINARY')
    for k, r in PAT.items():
        ms = list(re.finditer(r, b))
        if k == 'email': ms = [m for m in ms if not m.group(0).endswith((b'.invalid', b'example.com'))]
        if ms:
            lines = sorted({b.count(b'\n', 0, m.start()) + 1 for m in ms})
            flags.append(f'{k} x{len(ms)} lines {lines[:8]}{"..." if len(lines) > 8 else ""}'); tot[k] += len(ms)
    for i, lit in enumerate(priv, 1):
        c = b.count(lit.encode())
        if c: flags.append(f'private_literal#{i} x{c}'); tot[f'private#{i}'] += c
    print(st, path, len(b), '|', '; '.join(flags))
print('TOTALS', dict(tot))
