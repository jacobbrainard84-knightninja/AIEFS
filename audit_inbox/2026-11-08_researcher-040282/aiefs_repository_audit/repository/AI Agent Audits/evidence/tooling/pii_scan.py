"""PII / secret / packaging scan of the published audit tree (round 3, 2026-10-24).
Run from the AIEFS repo root:  python "AI Agent Audits/evidence/tooling/pii_scan.py" [--private FILE]
Checks every file under "AI Agent Audits/":
  * e-mail addresses (any user@host.tld), except the placeholder forms listed in ALLOW;
  * absolute local paths: /home/<name>, /Users/<name>, /root/<name>, /workspace, C:\\Users, and relative escapes like ../AIEFS_publish
    (a /home/ etc. followed by a regex character such as [ is search-pattern text, not a path, and is not flagged);
  * secret/token shapes: GitHub (ghp_/gho_/ghu_/ghs_/github_pat_), OpenAI-style sk-, AWS AKIA, Slack xox?-, PEM private keys,
    OAuth device codes (XXXX-XXXX in a device/user-code context), Bearer tokens;
  * packaging: non-UTF-8 or binary files, .pyc/__pycache__/.zip/.npz/.pdf, CR line endings, files >= 1 MB, total >= 5 MB.
--private FILE: extra literal strings (one per line) that must not appear, e.g. the owner's personal e-mail or user name.
  That file is kept locally and is NOT published; matches are reported as "<private literal #k>" so values never print.
Exit 0 if clean, 1 if anything is found."""
import re, sys
from pathlib import Path
P = Path(__file__).resolve().parents[2]
PRIV = []
if '--private' in sys.argv: PRIV = [l.strip() for l in open(sys.argv[sys.argv.index('--private') + 1]) if l.strip()]
ALLOW = {'<owner-email-redacted>'}
PAT = {'email': r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}',
       'abs_path': r'(/home/|/Users/|/root/)[A-Za-z0-9_.-]|/workspace|[A-Z]:\\\\Users', 'rel_escape': r'\.\./AIEFS_publish',
       'github_token': r'\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}',
       'sk_key': r'\bsk-[A-Za-z0-9]{20,}', 'aws': r'\bAKIA[0-9A-Z]{16}\b', 'slack': r'\bxox[abpr]-[A-Za-z0-9-]{10,}',
       'pem': r'-----BEGIN [A-Z ]*PRIVATE KEY-----', 'bearer': r'\b[Bb]earer\s+[A-Za-z0-9._-]{20,}',
       'device_code': r'(?i)(device|user)[ _-]?code\W{0,5}[A-Z0-9]{4}-[A-Z0-9]{4}\b'}
BIN = {'.pyc', '.zip', '.npz', '.pdf', '.npy', '.pkl', '.gz'}
bad = []; skipped = []; total = 0; n = 0; SELF = str(Path(__file__).resolve().relative_to(P))
for p in sorted(P.rglob('*')):
    if p.is_dir():
        if p.name == '__pycache__': bad.append(f'PYCACHE  {p.relative_to(P)}')
        continue
    n += 1; rel = str(p.relative_to(P)); b = p.read_bytes(); total += len(b)
    if p.suffix in BIN: bad.append(f'BINARY   {rel}')
    if len(b) >= 1_000_000: bad.append(f'SIZE     {rel}: {len(b)} bytes')
    try: s = b.decode('utf-8')
    except UnicodeDecodeError: bad.append(f'NONUTF8  {rel}'); continue
    if '\x00' in s: bad.append(f'NUL      {rel}')
    if '\r' in s: bad.append(f'CR       {rel}')
    for i, line in enumerate(s.splitlines(), 1):
        for k, r in PAT.items():
            for m in re.finditer(r, line):
                if m.group(0) in ALLOW: continue
                if rel == SELF and k in ('email', 'abs_path', 'rel_escape'): skipped.append(f'{rel}:{i}'); continue   # this file's own pattern text
                if k == 'email' and line[m.end():m.end() + 1] == '(': continue   # matrix product like C@np.array(...), not an address
                bad.append(f'{k.upper():8} {rel}:{i}: {m.group(0)[:60]}')
        for j, lit in enumerate(PRIV, 1):
            if lit.lower() in line.lower(): bad.append(f'PRIVATE  {rel}:{i}: <private literal #{j}>')
if total >= 5_000_000: bad.append(f'TOTAL    {total} bytes >= 5 MB')
print(f'scanned {n} files, {total} bytes' + (f', {len(PRIV)} private literals' if PRIV else ''))
if skipped: print('self-pattern lines not scanned for paths/emails:', ', '.join(sorted(set(skipped))))
for x in bad: print(x)
print('CLEAN' if not bad else f'FOUND {len(bad)} issue(s)'); sys.exit(1 if bad else 0)
