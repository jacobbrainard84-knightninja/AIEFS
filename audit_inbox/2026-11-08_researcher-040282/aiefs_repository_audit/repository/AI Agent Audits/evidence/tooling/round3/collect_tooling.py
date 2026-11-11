# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
"""Round 3 (2026-10-24): copy every scratch tooling/analysis script used to build the audit package into
evidence/tooling/, with local paths and personal values redacted. Also extracts the ad-hoc shell commands
(staging, zip, line-ending normalisation, PII scan, GitHub blob check, result diff) verbatim from the session record.
Run locally by the auditor; not needed to reproduce results."""
import json, re, sys, shutil
from pathlib import Path
T = Path(sys.argv[1]); T.mkdir(parents=True, exist_ok=True)
PRIV = [l.strip() for l in open(sys.argv[2]) if l.strip()] if len(sys.argv) > 2 else []   # private literals, never published
RED = [(r'<scratch-root>/AIEFS_publish_v3/AI Agent Audits', '<v3-staging>/AI Agent Audits'),
       (r'<scratch-root>/AIEFS_publish', '<v2-staging>'), (r'<scratch-root>/AIEFS_audit_evidence', '<v1-evidence-scratch>'),
       (r'<scratch-root>/AIEFS', '<repo-clone>'), (r'<scratch-root>/audit', '<round1-scratch>'), (r'<scratch-root>/v2', '<v2-tooling>'),
       (r'<scratch-root>/v3', '<v3-tooling>'), (r'<scratch-root>/venv/bin/python', 'python'), (r'<scratch-root>/agent-tools/[0-9a-f-]+\.txt', '<tool-output>.txt'),
       (r'agent-tools/[0-9a-f-]+\.txt', '<tool-output>.txt'), (r'[0-9a-f]{8}-[0-9a-f-]{27}\.txt', '<tool-output>.txt'),
       (r'<scratch-root>/', '<scratch>/'), (r'<scratch-root>', '<scratch>'), (r'/home/[A-Za-z0-9_.-]+', '<home>'), (r'/tmp/', '<tmp>/'),
       (r'[A-Za-z0-9._%+-]+@gmail\.com', '<owner-email-redacted>')]
def clean(s):
    for a, b in RED: s = re.sub(a, b, s)
    for p in PRIV: s = s.replace(p, '<redacted>')
    return s
HDR = "# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.\n"
files = {'round1/mathcheck.py': '<scratch-root>/audit/mathcheck.py', 'round1/mathcheck.log': '<scratch-root>/audit/mathcheck.log',
         'round1/freq_predictor.py': '<scratch-root>/audit/freq_predictor.py', 'round1/repro13.py': '<scratch-root>/audit/repro13.py', 'round1/repro13.log': '<scratch-root>/audit/repro13.log',
         'round1/deep/omega_random.json': '<scratch-root>/audit/deep/omega_random.json', 'round1/deep/omega_multistab.json': '<scratch-root>/audit/deep/omega_multistab.json',
         'round1/summ.py': '<scratch-root>/audit/summ.py', 'round1/summ.log': '<scratch-root>/audit/summ.log',
         'round1/deep/omega_random.py': '<scratch-root>/audit/deep/omega_random.py', 'round1/deep/omega_random.log': '<scratch-root>/audit/deep/omega_random.log',
         'round1/deep/omega_multistab.py': '<scratch-root>/audit/deep/omega_multistab.py', 'round1/deep/omega_multistab.log': '<scratch-root>/audit/deep/omega_multistab.log',
         'round2/make_v2.py': '<scratch-root>/v2/make_v2.py', 'round2/make_manifest_v2.py': '<scratch-root>/v2/make_manifest.py',
         'round3/corrections.py': '<scratch-root>/v3/corrections.py', 'round3/kck_one.py': '<scratch-root>/v3/kck_one.py',
         'round3/collect_tooling.py': '<scratch-root>/v3/collect_tooling.py'}
for dst, src in files.items():
    d = T / dst; d.parent.mkdir(parents=True, exist_ok=True)
    s = open(src, encoding='utf-8').read()
    # this script's own redaction table would be mangled by clean(); for it, only the scratch root is replaced
    s = s.replace('<scratch-root>', '<scratch-root>') if dst == 'round3/collect_tooling.py' else clean(s)
    d.write_text((HDR if dst.endswith('.py') else '') + s, encoding='utf-8')
# ad-hoc commands from the session record (JSON lines prepared locally: position <TAB> json-input)
if len(sys.argv) > 3:
    want = {int(x.split(':')[0]): x.split(':', 1)[1] for x in sys.argv[4].split('|')}
    out = ["# Ad-hoc shell commands used to build and check the package (verbatim from the session record, paths/personal values redacted)\n",
           "These were typed interactively, not saved as scripts. Each block is one command; the number is its position in the session record.\n"]
    for line in open(sys.argv[3], encoding='utf-8'):
        pos, js = line.split('\t', 1); pos = int(pos)
        if pos in want:
            c = json.loads(js)
            if isinstance(c, str): c = json.loads(c)   # some records are double-encoded
            c = c.get('command', '')
            out.append(f"\n## [{pos}] {want[pos]}\n\n```bash\n{clean(c)}\n```\n")
    (T / 'adhoc_commands.md').write_text(''.join(out), encoding='utf-8')
print('wrote', len(files), 'files to', T)
