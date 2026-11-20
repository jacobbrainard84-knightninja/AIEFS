# H3 Python mutation report — checker scripts (R001, 2026-11-20, Tirane) — FINAL
Tool: research/hardening/py_mutation_check.py (branch research/h3-py-mutation). Report-only, not a CI gate.
Base: origin/main 0a6a2f6. Seed 20261120 (tool default), <= 40 mutants/file (default; sampled when more), per-signal timeout
90 s passed explicitly as `--timeout 90` (the tool default is 300 s), interpreter /workspace/venv_req_cmp/bin/python, unshare -rn.
Every mutant is written into a scratch `git clone` (default: a new mkdtemp dir under /tmp); the source tree is only read.
Clone guard (added after the A002 audit, F1): before anything is deleted or cloned, --repo and <work>/clone are realpath-resolved
and the run is refused with exit 2 if they are equal or either lies inside the other; an existing <work>/clone is removed only if
it carries the marker .git/H3_MUTATION_CLONE that the tool writes into every clone it makes (anything else, or a symlink: exit 2,
nothing removed). Self-tests on throwaway repos under pytest's tmp_path cover each refusal and the marker. Before the fix
`--repo <w>/clone --work <w>` deleted the source (reproduced by A002); the runs below used the default mkdtemp work dir.
Command lines (reconstructed from the JSON reports' seed/max_per_file and the settings recorded when the runs were made; the
tool did not record argv then and now does; A002 re-ran Run A/C for two files with these flags and got identical survivor ids):
  Run A: unshare -rn $PY research/hardening/py_mutation_check.py --ci-tests-only --timeout 90 --out h3_report_ci.json
  Run C: same + --target tools/ci/check_current_inventory.py --target audits/engineering/verify_inventory_current.py
         --out h3_report_inv.json
  Run B: unshare -rn $PY research/hardening/py_mutation_check.py --timeout 90 --rescore h3_report_ci.json --out h3_report_rescore.json
         (first six files; hygiene_scan/lint_claims re-run as `... --rescore h3_report_ci.json --tests-only` -> h3_report_rescore2.json)
research/lean_gate/spec_results_line.py: not on main -> skipped. engine_guards / engine / pinned: out of scope (refused).

## Method notes (read first)
1. Run A (CI tests only). CI runs `unittest discover -s tools/ci/tests` and `pytest research/lean_gate/tests`; the tool's
   CI_TEST_DIRS is now exactly those two (A002 N3: it previously also listed research/hardening/tests and audits/engineering/tests,
   which CI does not run; neither held a test for any target, so every target's test set and all numbers are unchanged — checked
   with find_tests per target). The tool runs the tools/ci/tests TestCase files with pytest; equivalent to unittest for them.
2. Run B: Run A's survivors re-run with tools/redteam suites added (test_rt_sha256sums, test_rt_hashes, test_rt_claims_hygiene).
3. SURPRISE / tool fix: in Run A every mutant of an inventory-hashing checker was "killed" by the self-hash: writing the mutant
   changes the checker's own bytes, registry/artifacts_current.csv flags that file, so the good run fails for a reason unrelated to
   the mutant's logic. verify_inventory_current.py showed 35/40 such vacuous kills (37/40 "killed"). Fixed: for
   check_current_inventory.py and verify_inventory_current.py the inventory is regenerated after each mutant (judged as if committed
   with a fresh inventory); Run C re-ran those two targets in full. Run A numbers for those two are INVALID and not used.
4. Classification: "equivalent" = cannot change any verdict (exit status) on any input, or changes only display/annotation text;
   "gap" = a real input exists on which the verdict changes and no test notices. Gaps are ranked by how directly they could let a
   false PASS through (H = silent pass on a real defect, M = weaker detection / scope, L = counts, warn-only or stricter direction).
   This "unit" rating ignores other CI steps; the final ranking adds a second axis, CI exposure (A002 N1), see "Top gaps".
5. One denominator everywhere (A002 N2): detected = killed + timeout (a hang is noticed); rate = detected / run, where
   run = killed + timeout + survived (non-compiling mutants, 0 here, excluded). The tool's JSON kill_rate now uses this definition.

## Run A per-file (CI-run tests + good run + bad fixture)
| file | sites | run | killed | survived | timeout | detected rate |
|---|---|---|---|---|---|---|
| check_artifact_pins.py | 107 | 40 | 34 | 6 | 0 | 34/40 = 0.850 |
| check_manifest.py | 66 | 40 | 35 | 4 | 1 | 36/40 = 0.900 |
| check_modes.py | 58 | 40 | 28 | 11 | 1 | 29/40 = 0.725 |
| check_pinned_restatement.py | 37 | 37 | 22 | 14 | 1 | 23/37 = 0.622 |
| check_sha256sums.py | 78 | 40 | 22 | 17 | 1 | 23/40 = 0.575 |
| check_study_paths.py | 110 | 40 | 33 | 7 | 0 | 33/40 = 0.825 |
| hygiene_scan.py | 79 | 40 | 22 | 18 | 0 | 22/40 = 0.550 |
| lint_claims.py | 126 | 40 | 27 | 13 | 0 | 27/40 = 0.675 |
| (check_current_inventory.py, verify_inventory_current.py: see Run C) | | | | | | |
Timeouts (4): all are `and -> or` / const flips in the `-I -B` re-exec guard (infinite re-exec) — detected, not survivors.
(Run B / Run C sections and the survivor classification follow.)

## Run C (inventory refreshed per mutant; CI-run tests)
| file | sites | run | killed | survived | timeout | detected rate |
|---|---|---|---|---|---|---|
| check_current_inventory.py | 29 | 29 | 22 | 7 | 0 | 22/29 = 0.759 |
| verify_inventory_current.py | 40 | 40 | 17 | 23 | 0 | 17/40 = 0.425 (no test file at all; only the [1/5]-failing fixture) |

### verify_inventory_current.py survivors
GAPS (no test exercises gates [2/5]-[4/5]; the one bad fixture fails at [1/5] first):
- H L72 `return 1 -> 0` after [2/5] FAIL: a stale/mismatched current inventory would PASS the gate.
- H L81 `return 1 -> 0` vocabulary violation passes. H L78 `or -> and`: a row needs BOTH bad status and bad scope to fail.
- H L86 `return 1 -> 0`: Unreviewed artifacts pass.
- H L101 `return 1 -> 0`: a Lean lock hash mismatch passes. H L97 `== -> !=`: skips every ledger entry except the self-entry, so no
  Lean digest is checked. H L93 drop `not` (`if line.strip(): continue`): skips every NON-blank line, so with the current ledger
  (no blank lines) [4/5] verifies 0 digests and prints "PASS: 0 ... digests verified" (RELABELLED from EQUIVALENT after A002 F2;
  my earlier "blank line -> crash, stricter" reading had the condition backwards). Same class as L97: the follow-up test must
  assert n > 0, ideally the exact digest count of the ledger. M L94/L98 `continue -> break`: ledger read stops at the first blank line / self-entry; later digests unchecked.
- M L49 `return 1 -> 0`: a missing sub-checker script counts as PASS.
EQUIVALENT: L40 chunk size 2^20->2^21 bytes (hash unchanged); L50 text=False (display; crash path only when rc!=0, still non-zero);
L51/L55 tail lengths (display); L54 `!= -> ==` only selects when stderr is echoed; L60 argparse description; L77 enumerate start
(message line number); L91/L102 digest counter (display); L110/L111 sys.path.insert(0 -> 1) (module still found; nothing shadows it in the clone).

### check_current_inventory.py survivors (all EQUIVALENT or L)
L39 IN_GHA flip (annotation only); L43 MAX_LISTED 20->21 and L117 `> -> >=` (how many lines are listed); L57 capture_output
(git noise only); L100 description; L108 `return 2 -> 3` (still non-zero). L L48 drop `not` in load_generator: would always use the
checker's own copy of the generator instead of the target repo's; identical file here, differs only for --repo of another tree.

## Run B (Run A survivors + tools/redteam) — and survivor classification per file
### check_sha256sums.py: Run A 23/40 (0.575); with redteam 31/40 (0.775)
Killed ONLY by tools/redteam/test_rt_sha256sums.py (which CI does not run) — CI-level gaps (H): L178 delete `MISSING` error
(a listed file deleted -> PASS); L175 `is not -> is` (missing non-allow-listed entry becomes a notice -> PASS); L149 unreadable list
skipped; L162 `or -> and` and L167 path-escape / symlink-escape errors; L108/L109 unclassified hash-list detection; L172 allow-list tracking.
Still surviving with redteam:
- M L189 delete "contains no checksum entries": an emptied SUMS list passes.
- M L154 `continue -> break` on a blank/comment line: the rest of that list is silently unchecked (no current list has one, so latent).
- M L91 delete raise "not the top of its git work tree": a subfolder --repo is accepted (mis-scoped tracked-file set).
- L L112 delete "stale EXTRA_INCLUDE entry" (config hygiene).
- EQUIVALENT: L150/L158/L169 `continue -> break` right after an error was recorded (run already fails); L202 `return 2 -> 3`;
  L205 GHA flag (annotation only).

### check_pinned_restatement.py: 23/37 (0.622), redteam adds nothing
- H L110 delete "cannot read pinned source" (+ continue): an unreadable/missing pinned source is silently skipped -> PASS.
- M L116 delete "not listed with sha256 ... in SUMS": pinned file and SUMS ledger may disagree unnoticed (hard pin still checked).
- M L124 delete "no namespace/import substitution applied": a substitution table that stops matching is not reported.
- L L91 `continue -> break` in read_sums: stops at the first blank/comment line (stricter: later pins look unlisted).
- EQUIVALENT: L111/L121 continue->break after an error; L128 x3 and L129 only change the "at line N" text in a message
  (L129 can crash with None+1, still non-zero); L137 RESTATED_DIR unlistable is also reported by every per-file read;
  L90 `or -> and` only lets blank/comment lines into the sums dict as junk keys never queried; L146 description; L151 `2 -> 3`.

### check_modes.py: 29/40 (0.725), redteam adds nothing
- M L86 `"/" in tok -> not in` and L78 `break -> continue`: the PUSH_NOTES backtick-path branch and the section end are untested;
  a mutant can drop PUSH_NOTES-listed scripts from the exec-bit check (L86) or pull in other sections (L78, stricter).
- L L116 `continue -> break`: shebang scan stops at a missing object (SHEBANG_NOT_EXEC is warn-only). L L174 warning count.
- EQUIVALENT: L33 GHA flag; L110 parse start 0->1 (only header[1], header[2] are used); L115 x2 (`or -> and`, `[1] -> [0]`:
  a "missing" header always has < 3 fields, so the result is the same); L125 description; L167 x2 annotation path index.
Timeout: L114 `pos = nl + 1 -> + 0` (infinite loop) — detected.

### check_artifact_pins.py: 34/40 (0.850), redteam adds nothing
- L L195/L251/L266 summary counters (ok/known_missing/known_changed) wrong by one — display only, but untested counts.
- L L252 `and -> or`: FLAG_DISAGREES notice logic (notice, never an error).
- EQUIVALENT: L163 GHA flag; L179 `or -> and` in the work-tree probe (rc != 0 and stdout != "true" coincide in practice).

### check_manifest.py: 36/40 (0.900), redteam adds nothing
- EQUIVALENT (all 4): L206/L214 `continue -> break` after `failed += 1`/error (run fails anyway; later manifests unchecked but
  verdict already FAIL); L218 display quoting; L224 trailing-newline display. Timeout L60 (re-exec guard) detected.

### check_study_paths.py: 33/40 (0.825), redteam adds nothing
- L L178 delete "empty <id_col>" error: a registry row with an empty id is not flagged.
- EQUIVALENT: L166/L179/L183 continue->break after an error; L175 enumerate start (message line numbers); L206 `or -> and` on
  the baseline shape check (a malformed baseline then crashes -> non-zero); L300 `2 -> 3`.

### hygiene_scan.py: Run A 22/40 (0.550); with redteam (test_rt_claims_hygiene.py) still 22/40 — redteam adds nothing
CI invokes it twice (repo-checks.yml): `--base "$BASE" --pii` (only after the workflow verified `git cat-file -e $BASE`) and a
plain full scan. Neither uses --strict; no tracked symlinks/submodules on main.
- M L122 delete `raise` in git(): a failing git call returns [] instead of an error, so `--base <bad ref>` scans 0 files -> PASS.
  CI pre-checks the base, but the PR-template command `--base origin/main` run in a clone without origin/main silently passes.
- M L260 `continue -> break` on a non-file/symlink path: the scan stops at the first such path in sorted order and everything
  after it is unchecked -> PASS. Latent (no tracked symlink today; a deleted-in-worktree tracked file in a local run also triggers it).
- M L135 `not in skip -> in` in walk_files: non-git mode descends ONLY into .git/.lake/venv/... so real files below top level are
  never scanned. Non-git mode only (CI is a git checkout), hence M not H.
- M L286c60 `warnings > 0 -> > 1`: under --strict a single warning passes. --strict is untested and unused in CI.
- M L275 drop `not` (`elif not a.base -> elif a.base`): full-scan BINARY_OUTSIDE warning disappears (warn-only in full mode).
- L L168 `return False -> True` on OSError: an unreadable file is treated as binary -> its content scan is skipped (UNREADABLE
  warning lost; NEW_BINARY error instead if it was added in --base mode).
- L L43 MiB 1024->1025, L265/L278 `> -> >=`, L166 NUL-sniff window 8192->8193: exact-boundary behaviour untested.
- L L184 `break -> continue`: several PII_EMAIL warnings per line (warn count only).
- L (stricter direction) L143 `and -> or` (missing allow file crashes instead of "0 patterns"); L226 `and -> or` (blank/comment
  lines enter the private list; "" matches every line -> PRIVATE_LITERAL warnings everywhere); L247 `and -> or` (untracked files
  scanned without --untracked); L286c19 `> -> >=` (--strict always FAILs).
- EQUIVALENT: L128 capture_output on `rev-parse` (stderr noise only; returncode unchanged); L147 `and -> or` in load_allow
  (blank/comment lines become patterns "" / "# ..." that can never match a repo path, so allowed() is unchanged); L216 `2 -> 3`.
Note: tools/ci/tests/test_ci_tools.py covers the pattern table and a secret_file fixture but none of: --base with a failing git
call, symlinks, non-git mode, --strict, or size thresholds.

### lint_claims.py: Run A 27/40 (0.675); with redteam 31/40 (0.775)
Killed ONLY by tools/redteam/test_rt_claims_hygiene.py (CI does not run it) — CI-level gaps:
- H L170 `in row -> not in row`: the evidence_scope vocabulary check never runs when the column exists -> any scope value PASSes.
- H L373 drop `not` (`scopes is None and not unreadable`): a README with no Axis-2 scope table no longer errors and scopes stays
  None -> evidence_scope checking silently disabled -> PASS.
- H L148 `break -> continue` in parse_scope_vocab: the scope table no longer ends at the next heading, so backticked first-column
  values of LATER tables become allowed evidence_scope values (widened vocabulary -> false PASS).
- M L160 `is not -> is`: KNOWN_MISSING_ARTIFACTS bookkeeping inverted (stale/now-existing allow-list entries mis-reported).
Still surviving with redteam:
- M L247 `or -> and` in parse_readme_vocab: if the line after the status heading is NOT a fence, the original returns [] (fallback
  vocabulary); the mutant parses onward to the NEXT fence pair and takes that block as the status vocabulary (possibly wider).
  Only a malformed README triggers it, so M.
- L (stricter) L245 `k < len -> <=`: heading followed only by blank lines to EOF -> IndexError crash instead of [] (non-zero).
- EQUIVALENT: L110/L336/L413 `1 -> 0` (line number in the message/annotation only; still rep.error); L275 `heads[1] -> heads[0]`
  (annotation line); L371 `unreadable = True -> False` (adds a second ERROR on a run that already has load_vocab's 'cannot be
  read' ERROR; verdict unchanged); L426 description `[0] -> [1]`; L436 `2 -> 3`.

## Totals (valid numbers only; Run A for 8 files + Run C for the 2 inventory checkers; Run A inventory numbers discarded)
Denominator as in method note 5 (detected = killed + timeout; rate = detected / run).
386 mutants run. CI tests only: 262 killed + 4 timeouts = 266 detected, 120 survived -> 266/386 = 0.689.
Adding tools/redteam: +8 (check_sha256sums) +4 (lint_claims) = 278 detected, 108 survived -> 278/386 = 0.720.
(The earlier "289 killed / 93 survived" from the raw first run counted the vacuous self-hash kills; superseded.)
Per file, detected/run (CI only -> with redteam): check_manifest 36/40 (0.900); check_artifact_pins 34/40 (0.850);
check_study_paths 33/40 (0.825); check_current_inventory 22/29 (0.759); check_modes 29/40 (0.725); lint_claims 27/40 (0.675 ->
0.775); check_pinned_restatement 23/37 (0.622); check_sha256sums 23/40 (0.575 -> 0.775); hygiene_scan 22/40 (0.550);
verify_inventory_current 17/40 (0.425).
Sampling: <= 40 of each file's sites (seed 20261120), so per-file rates are estimates and unsampled sites may hide more gaps.
Regression check after the audit fixes: check_manifest re-run with the fixed tool (`--ci-tests-only --timeout 90 --target
tools/ci/check_manifest.py`, unshare -rn): 35 killed / 4 survived / 1 timeout, detected 36/40 = 0.900, the same 5 non-killed ids
as Run A (L60 timeout; L206/L214/L218/L224 survivors), so the guard/denominator/CI_TEST_DIRS changes did not move any result.

## Top gaps, ranked on two axes (A002 N1)
"Unit" = no test (CI or redteam) notices the mutant (H/M/L as in method note 4). "CI exposure" = if the checker regressed this way,
would any OTHER step in .github/workflows (repo-checks.yml, lean.yml) still fail on the defect? Backstops checked by reading the
workflow and code (2026-11-20): repo-checks.yml runs lint_claims, hygiene_scan (x2), check_manifest, check_sha256sums,
check_artifact_pins, check_modes --strict, check_current_inventory, check_study_paths and verify_inventory_current as separate
steps; check_sha256sums verifies lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt (EXTRA_INCLUDE) and
AIEF_LEAN_SOURCE_SHA256SUMS.txt (NAME_RE); check_pinned_restatement runs inside the Lean gate. No tools/ci checker other than
verify_inventory_current reads artifact_status/evidence_scope of artifacts.csv, studies.csv or relocation_map.csv, or counts
Unreviewed (rg over tools/ci: no hits). lint_claims parses the README Axis-2 table, which is today EXACTLY verify [3/5]'s
VALID_SCOPE (same 6 strings); its status vocabulary (14 values) is a superset of VALID_STATUS (7).

### Real CI false-PASS exposures (unit gap AND no CI backstop), ranked
1. H/H verify_inventory_current [3/5] vocabulary, L81 `return 1 -> 0` and L78 `or -> and`: an invalid artifact_status/
   evidence_scope in artifacts.csv, studies.csv or relocation_map.csv passes CI (claims.csv is partly backed by lint_claims,
   but not for statuses in the README vocabulary outside VALID_STATUS, e.g. "Quarantined" in artifact_status).
2. H/H verify_inventory_current [3/5] L86 `return 1 -> 0`: Unreviewed artifacts pass CI. Nothing else counts them.
3. H/M check_sha256sums redteam-only kills: L178 (a deleted listed file -> PASS) and L175 (missing entry -> notice). Only the
   Lean source SUMS has a second check (check_pinned_restatement's sums cross-check for its pinned pairs); for the other 7 lists a
   deletion committed with a fresh inventory passes every other step unless the file is also an e47bad1-snapshot row
   (check_artifact_pins); not checked per entry. L162/L167 path/symlink escape and L149 unreadable list:
   no backstop (needs a malicious or broken SUMS entry, hence M).
4. M/M check_sha256sums L189 emptied SUMS list passes; L154 a blank/comment line truncates a list (latent: none today).
5. M/M check_modes L86/L78: PUSH_NOTES-listed scripts can drop out of the exec-bit check; nothing else checks modes.
6. M/M lint_claims L247: a malformed status heading makes the NEXT fenced block the status vocabulary (audited_status has no
   backstop; artifact_status values are still bounded by verify [3/5] VALID_STATUS).
7. M/L hygiene_scan L260 (symlink/missing path stops the scan; latent, no tracked symlinks) and L122 (failing git -> 0 files; CI
   pre-checks the base ref and the full scan still runs, so exposure is local/PR-template use only).

### Unit-test gaps that CI currently backstops (still worth tests; not CI false-PASS today)
- verify_inventory_current L72 (stale inventory) and L49 (missing sub-checker): check_artifact_pins / check_current_inventory
  run as their own CI steps.
- verify_inventory_current [4/5] L101/L97/L93/L94/L98 (Lean lock digests unchecked): check_sha256sums verifies the same ledger.
- check_pinned_restatement L110 (unreadable pinned source skipped): the pinned file is listed in AIEF_LEAN_SOURCE_SHA256SUMS.txt,
  so check_sha256sums reports it MISSING; L116 SUMS disagreement is likewise caught by check_sha256sums.
- lint_claims L170/L373/L148 (evidence_scope checking disabled or widened; redteam-only kills): verify [3/5] checks claims.csv
  evidence_scope against VALID_SCOPE, which equals the README table today. Exposure returns if the two lists ever diverge.
Previous single-axis ranking put verify L72 and pinned_restatement L110 in the top 3; on the CI-exposure axis they drop out and
verify [3/5] moves to the top.

## Recommended follow-ups (separate branches; no gap-filling tests on this branch)
1. tools/ci/tests/test_verify_inventory_current.py: one bad fixture per gate [2/5]-[5/5], especially [3/5] (bad status/scope in
   each of the 4 CSVs; one Unreviewed artifact) and [4/5] with an exact digest-count assert (kills L93/L97, not just n > 0).
2. Owner decision: run tools/redteam in CI, or port the sha256sums (deleted file, missing entry, escapes) and lint_claims
   evidence_scope cases into tools/ci/tests.
3. check_sha256sums: empty-list and blank/comment-line fixtures; subfolder --repo rejection test.
4. check_modes: a PUSH_NOTES fixture; lint_claims: a malformed-vocabulary-heading fixture.
5. Consider a CI-side assert that lint_claims' Axis-2 scope list equals verify_inventory_current.VALID_SCOPE (keeps the backstop).
6. hygiene_scan: failing `--base` ref must exit 2; tracked symlink mid-tree; non-git walk; --strict with 1 warning.
7. check_pinned_restatement L110 and verify L72/L49 unit tests (backstopped, lower priority).
8. Re-run with a higher --max-per-file on the four lowest files after 1-4 land.
