# Ad-hoc shell commands used to build and check the package (verbatim from the session record, paths/personal values redacted)
These were typed interactively, not saved as scripts. Each block is one command; the number is its position in the session record.

## [1] Round 1 clone (blob filter 5 MB), commit count, .git and checkout size

```bash
cd <scratch> && git clone --filter=blob:limit=5m https://github.com/jacobbrainard84-knightninja/AIEFS.git 2>&1 | tail -5; cd AIEFS && git log --oneline | wc -l && du -sh .git . && ls -la
```

## [2] Round 1 history, .gitignore, lock file and top-level listing (author e-mail and lock-file contents were read but are not reproduced)

```bash
cd <repo-clone> && git log --stat --format='%H %an <%ae> %ad %s' | grep -v '^ ' | head; git log --format='%h %an %ad %s' --date=iso; echo; git rev-list --objects --all --missing=print | grep '^?' | wc -l; cat .gitignore; echo; cat .~lock*; cat "Sci- stuff.txt"; ls Papers "Project Histories" "Project Origins" lean lean/* Test_Terminal_Output test_output __pycache__ AIEF_Experiments runs runs_aief14_smoke runs_pivot_study "Older files" | head -150
```

## [3] Round 1 tracked-file count, largest files, extensions, __pycache__ count, README/LICENSE/test search

```bash
cd <repo-clone> && git ls-files | wc -l; git ls-files -z | xargs -0 du -b 2>/dev/null | sort -rn | head -30; echo; git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20; echo; git ls-files | grep -c __pycache__; git ls-files | grep -iE 'readme|license|requirements|setup.py|pyproject|\.github|test_' 
```

## [11] Round 1 secret/token scan of the repository clone

```bash
cd <repo-clone> && rg -n --no-messages -e 'ghp_[A-Za-z0-9]{30,}' -e 'github_pat_' -e 'sk-[A-Za-z0-9_-]{20,}' -e 'xai-[A-Za-z0-9]{20,}' -e 'AKIA[0-9A-Z]{16}' -e 'AIza[0-9A-Za-z_-]{35}' -e '-----BEGIN [A-Z ]*PRIVATE KEY' -e 'xox[abp]-' -e '(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*["'"'"'][^"'"'"']{8,}' . <tmp>/txt | head -30; echo ===; rg -o --no-messages -I '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' <tmp>/txt . | sort | uniq -c | sort -rn | head -20; echo ===; rg -c --no-messages '<home>' . | head; rg -o --no-messages -I '/home/[a-z]+' <tmp>/txt | sort | uniq -c
```

## [12] Round 1 personal-data, absolute-path and unsafe-code grep of the repository

```bash
cd <repo-clone> && rg -n --no-messages '<owner-email-redacted>' <tmp>/txt . | cut -c1-200; rg -n '<home>' AIEF_1_3_closure_diagnostics_updated.py *.py | cut -c1-200 | head; rg -ln --no-messages 'pickle|eval\(|exec\(|subprocess|os\.system|shell=True|allow_pickle=True|yaml\.load|torch\.load' --glob '*.py' . | head -30
```

## [13] Round 1 unsafe-code grep and junk-script inspection

```bash
cd <repo-clone> && rg -n --no-messages -g '*.py' -e 'allow_pickle\s*=\s*True' -e 'pickle\.load' -e '\beval\(' -e '\bexec\(' -e 'shell\s*=\s*True' -e 'os\.system' -e 'yaml\.load\(' . | grep -v 'Older files' | cut -c1-180 | head -30; echo; rg -c -g '*.py' 'allow_pickle\s*=\s*False' . | wc -l; for f in check.py check_001.py check_01.py check_02.py probe_01.py probe_02.py test_01.py diagnose_import.py; do echo "=== $f"; cat -n $f | head -40; done
```

## [21] Round 1 pytest of a temporary copy of aief_modular_platform_v1_analysis_v4 (40 passed, 2 skipped)

```bash
cd <tmp>/modv4 && . <scratch>/venv/bin/activate && PYTHONPATH=<repo-clone>:<tmp>/modv4 timeout 1200 python -m pytest -q -rs 2>&1 | tail -40
```

## [32] Round 1 chat-log PDF history and the byte-identical SSRH draft check (cmp)

```bash
cd <repo-clone>; git log --format='%h %ad' --date=short --name-status -- "Project Histories" "Project Origins" | head -40; ls -la "Project Histories" | head -15; cmp "Project Origins/Solar System Resonance Hypothesis Delay‑Coupled Dynamics draft.pdf" "Project Origins/Solar System Resonance Hypothesis Delay‑Coupled Dynamics draft 02.pdf" && echo IDENTICAL; wc -l <round1-scratch>/repro13.log
```

## [42] Round 1 .gitignore / test_01 / probe_02 / hard-coded path / .pyc / lock-file checks

```bash
cd <repo-clone>; grep -n pycache .gitignore; sed -n 1,2p test_01.py; sed -n 10,13p probe_02.py; grep -n "import" probe_02.py; sed -n 36,43p AIEF_1_3_closure_diagnostics_updated.py; sed -n 1,4p lean/AIEFProofs/AIEFProofs/ControllerFiber.lean; git ls-files | grep -c '\.pyc$'; git ls-files | grep 'lock'| head -3; ls Papers; cat <round1-scratch>/freq_predictor.py | head -50
```

## [51] Round 1 run directories, test files, .py count, .git size, tracked-file count

```bash
cd <repo-clone>; ls -d runs/* | head; ls runs | grep -c .; ls -d runs/b57562a8ee77 2>&1 | tail -1; git ls-files | grep -E '(^|/)test_[^/]*\.py$' | grep -v tests_modular; git ls-files | grep -c '\.py$'; du -sh .git; git ls-files | wc -l
```

## [77] Round 1 terminology counts (later packaged as scripts/terminology_grep.sh)

```bash
cd <repo-clone>; for t in cocycle Duhamel Ehresmann "fiber bundle" bundle holonomy gauge connection lineality biorthogonal "winner map" controller "spectral gap" Bregman "entropy geometry" Jordan intertwining "operator family" "slow bundle" "Lyapunov" "attractor" "memory" "resonance" "emergen" "falsif" "closure" "theorem" "Hamiltonian" "renormaliz" "topological" "quantum"; do md=$(git ls-files '*.md' | tr '\n' '\0' | xargs -0 grep -i -o -- "$t" 2>/dev/null | wc -l); py=$(git ls-files '*.py' | tr '\n' '\0' | xargs -0 grep -i -o -- "$t" 2>/dev/null | wc -l); echo "$t | md=$md | py=$py"; done
```

## [93] Extract the committed audit texts from GitHub output and compute git blob hashes

```bash
cd <scratch>/agent-tools; mkdir -p <scratch>/committed_audits; python3 - <<'EOF'
import json
for f,name in [('<tool-output>.txt','AIEFS_salvage.md'),('<tool-output>.txt','AIEFS_audit.md')]:
    for l in open(f).read().splitlines():
        try: j=json.loads(l)
        except Exception: continue
        open('<scratch>/committed_audits/'+name,'w').write(j['resource']['text'])
EOF
cd <scratch>; diff committed_audits/AIEFS_salvage.md AIEFS_salvage.md && echo SAME_S; diff committed_audits/AIEFS_audit.md AIEFS_audit.md && echo SAME_A; git hash-object committed_audits/*
```

## [195] Round 2 PII/secret scan of the staged publication tree

```bash
cd "<v2-staging>/AI Agent Audits"; echo "== emails"; rg -n -o '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' . | head; echo "== @ any (non-csv)"; rg -n '@' -g '!*.csv' . | cut -c1-160 | head -20; echo "== gmail<redacted>/home<scratch>/tmp"; rg -n -i 'gmail|<redacted>/home|<scratch>|/tmp|/root|/Users/' . | cut -c1-200 | head -30; echo "== tokens"; rg -n 'ghp_|gho_|github_pat_|sk-[A-Za-z0-9]{10}|AKIA[0-9A-Z]{12}|xox[bp]-|BEGIN [A-Z ]*PRIVATE|-----BEGIN' . | head; rg -n -i 'token|password|secret|api[_-]?key' . | cut -c1-160 | head; echo "== binaries"; find . -type f \( -name '*.pyc' -o -name '*.zip' -o -name '*.npz' -o -name '*.pdf' \) ; find . -type d -name __pycache__; for f in $(find . -type f); do file -b --mime "$f" | grep -qv '^text/\|application/json' && echo "NONTEXT $f $(file -b --mime $f)"; done; echo "== >1MB"; find . -type f -size +1000k; du -sb .
```

## [199] Round 2 staging: apply make_v2.py, then regenerate the manifest

```bash
cd <v2-tooling>; sed -i "39s#^a=a.replace('a /tmp copy','a temporary copy');#a=a.replace('a /tmp copy','a temporary copy').replace(\"The owner's gmail appears\",\"The owner's personal email address appears\");#" make_v2.py && python make_v2.py && P="<v2-staging>/AI Agent Audits" && cp <repo-clone>_audit_v2.md "$P/AIEFS_audit.md" && cp <repo-clone>_salvage_v2.md "$P/AIEFS_salvage.md" && python make_manifest.py && cd "$P" && rg -c -i 'gmail|<redacted>/home|<scratch>|/tmp|/root|/Users/|ghp_|github_pat|AKIA|xox[bp]-|BEGIN .*PRIVATE' . ; echo "scan exit $?"; rg -n -o '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}' . ; echo "email exit $?"; rg -n -i '\btoken' . | cut -c1-140
```

## [201] Round 2 zip builder (zip -qr -X), first attempt

```bash
cd <v2-staging> && rm -f <v1-evidence-scratch>.zip && zip -qr -X <v1-evidence-scratch>.zip "AI Agent Audits" && ls -l <v1-evidence-scratch>.zip && unzip -l <v1-evidence-scratch>.zip | tail -1; cd "AI Agent Audits"; find . -type f -printf '%s\t%P\n' | sort -k2 ; find . -type f | wc -l; du -sb . ; cd <repo-clone> && git status --short | head -3; echo "clone clean check done"
```

## [202] Round 2 zip builder (shutil.make_archive) and zip-content hash check

```bash
cd <v2-staging> && python -c "
import shutil; shutil.make_archive('<v1-evidence-scratch>','zip','.','AI Agent Audits')" && ls -l <v1-evidence-scratch>.zip && python - <<'EOF'
import json,hashlib,pathlib
P=pathlib.Path("<v2-staging>/AI Agent Audits")
m=json.load(open(P/"evidence/audit_manifest.json"))
bad=[k for k,v in m['files_sha256'].items() if hashlib.sha256((P/k).read_bytes()).hexdigest()!=v['sha256']]
print("manifest mismatches:",bad)
EOF
```

## [216] CR line-ending detection

```bash
cd "<v2-staging>/AI Agent Audits"; rg -l $'\r' . ; grep -n "csv.writer\|lineterminator" evidence/scripts/*.py
```

## [218] LF fix for analyze_kappa_tw.py csv.DictWriter (lineterminator)

```bash
E="<v2-staging>/AI Agent Audits/evidence"; cp "$E/results/kappa_tw_summary.json" <tmp>/sum_before.json; tr -d '\r' < "$E/results/kappa_tw_components.csv" > <tmp>/csv_lf.csv; sed -i "s/w = csv.DictWriter(fh, fieldnames=list(rows\[0\]))/w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\\\\n')/" "$E/scripts/analyze_kappa_tw.py"; grep -n DictWriter "$E/scripts/analyze_kappa_tw.py"; cd <repo-clone> && PYTHONDONTWRITEBYTECODE=1 python "$E/scripts/analyze_kappa_tw.py" > <tmp>/akt.out 2>&1; echo rc $?; cmp <tmp>/sum_before.json "$E/results/kappa_tw_summary.json" && echo summary-same; cmp <tmp>/csv_lf.csv "$E/results/kappa_tw_components.csv" && echo csv-equals-LF; wc -c "$E/results/kappa_tw_components.csv"; find "$E" -name __pycache__; git -C <repo-clone> status --short | head
```

## [219] Re-run check after the LF fix and manifest regeneration

```bash
E="<v2-staging>/AI Agent Audits/evidence"; diff <(sed '1d;$d' "$E/logs/analyze_kappa_tw.log") <tmp>/akt.out && echo log-same; python <v2-tooling>/make_manifest.py; rg -l $'\r' "<v2-staging>" ; cp "$E/scripts/analyze_kappa_tw.py" <v1-evidence-scratch>/scripts/ 2>/dev/null; echo ok
```

## [229] GitHub tree vs local git blob-hash verification after the round-2 push

```bash
cd <scratch>; head -c 600 <tool-output>.txt; echo; python - <<'EOF'
import json,re,subprocess,pathlib
t=open('<tool-output>.txt').read()
s=t[t.index('{'):t.rindex('}')+1]
d=json.loads(s)
items=d.get('tree',d) if isinstance(d,dict) else d
blobs={i['path']:i for i in items if i.get('type')=='blob'}
P=pathlib.Path('<v2-staging>/AI Agent Audits')
local={ 'AI Agent Audits/'+str(p.relative_to(P)):p for p in P.rglob('*') if p.is_file()}
print('remote blobs',len(blobs),'local',len(local))
print('missing remote:',sorted(set(local)-set(blobs)))
print('extra remote:',sorted(set(blobs)-set(local)))
bad=[]
for k,p in local.items():
    h=subprocess.check_output(['git','hash-object',str(p)]).decode().strip()
    if blobs.get(k,{}).get('sha')!=h: bad.append((k,h,blobs.get(k,{}).get('sha')))
print('sha mismatches:',bad)
EOF
```

## [232] Final round-2 zip build

```bash
cd <v2-staging> && python -c "import shutil; shutil.make_archive('<v1-evidence-scratch>','zip','.','AI Agent Audits')" && ls -l <v1-evidence-scratch>.zip
```

## [233] Round 3 staging copy (cp -a v2 tree) and git fetch/diff of origin/main

```bash
mkdir -p <v2-staging>_v3 && cp -a "<v2-staging>/AI Agent Audits" <v2-staging>_v3/ && cd <repo-clone> && git fetch -q origin 2>&1 | tail -2; git log --oneline -1 origin/main; git diff --stat e47bad1 origin/main | tail -3; git diff --name-only e47bad1 origin/main | grep -v '^AI Agent Audits/' | wc -l; ls <round1-scratch> | head -50; free -g | head -2; nproc
```

## [318] Round 3: v2 vs v3 results JSON diff (metadata stripped)

```bash
cd <scratch> && O="AIEFS_publish/AI Agent Audits/evidence/results"; N="AIEFS_publish_v3/AI Agent Audits/evidence/results"; python3 - "$O" "$N" <<'EOF'
import json,sys,os
O,N=sys.argv[1:]
def strip(x):
    if isinstance(x,dict): return {k:strip(v) for k,v in x.items() if k!='_meta'}
    if isinstance(x,list): return [strip(v) for v in x]
    return x
def diff(a,b,p='',out=None):
    if out is None: out=[]
    if type(a)!=type(b): out.append((p,'type')); return out
    if isinstance(a,dict):
        for k in set(a)|set(b):
            if k not in a: out.append((p+'/'+k,'added'))
            elif k not in b: out.append((p+'/'+k,'removed'))
            else: diff(a[k],b[k],p+'/'+k,out)
    elif isinstance(a,list):
        if len(a)!=len(b): out.append((p,'len')); return out
        for i,(x,y) in enumerate(zip(a,b)): diff(x,y,p+f'[{i}]',out)
    elif a!=b:
        if isinstance(a,float) and isinstance(b,float) and abs(a-b)<=1e-12*max(1,abs(a)): out.append((p,'tiny %g'%(a-b)))
        else: out.append((p,f'{str(a)[:40]} -> {str(b)[:40]}'))
    return out
for f in ['ablation14_topology.json','archived13_closedform.json','delay_heldout_analysis.json','delay_paired_runs.json','gate_idempotence.json','kappa_rows.json','kappa_tw_summary.json','omega_random.json','repro13.json','matched_phase_check.json']:
    a=strip(json.load(open(os.path.join(O,f)))); b=strip(json.load(open(os.path.join(N,f))))
    d=diff(a,b); print('==',f,len(d)); 
    for x in d[:8]: print('   ',x)
EOF
```
