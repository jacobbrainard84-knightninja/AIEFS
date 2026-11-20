# H3 Python mutation report — checker scripts (R001, 2026-11-20, Tirane) — FINAL
Tool: research/hardening/py_mutation_check.py (branch research/h3-py-mutation). Report-only, not a CI gate.
Base: origin/main 0a6a2f6. Seed 20261120, <= 40 mutants/file (sampled when more), per-signal timeout 90 s, unshare -rn,
every mutant written into a scratch `git clone` under /tmp (working tree never touched).
research/lean_gate/spec_results_line.py: not on main -> skipped. engine_guards / engine / pinned: out of scope (refused).

## Method notes (read first)
1. Run A (CI tests only: tools/ci/tests etc.; tools/redteam NOT included, and CI does not run tools/redteam).
2. Run B: Run A's survivors re-run with tools/redteam suites added (test_rt_sha256sums, test_rt_hashes, test_rt_claims_hygiene).
3. SURPRISE / tool fix: in Run A every mutant of an inventory-hashing checker was "killed" by the self-hash: writing the mutant
   changes the checker's own bytes, registry/artifacts_current.csv flags that file, so the good run fails for a reason unrelated to
   the mutant's logic. verify_inventory_current.py showed 35/40 such vacuous kills (37/40 "killed"). Fixed: for
   check_current_inventory.py and verify_inventory_current.py the inventory is regenerated after each mutant (judged as if committed
   with a fresh inventory); Run C re-ran those two targets in full. Run A numbers for those two are INVALID and not used.
4. Classification: "equivalent" = cannot change any verdict (exit status) on any input, or changes only display/annotation text;
   "gap" = a real input exists on which the verdict changes and no test notices. Gaps are ranked by how directly they could let a
   false PASS through (H = silent pass on a real defect, M = weaker detection / scope, L = counts, warn-only or stricter direction).

## Run A per-file (CI-run tests + good run + bad fixture)
| file | sites | run | killed | survived | timeout | kill rate |
|---|---|---|---|---|---|---|
| check_artifact_pins.py | 107 | 40 | 34 | 6 | 0 | 0.85 |
| check_manifest.py | 66 | 40 | 35 | 4 | 1 | 0.90 |
| check_modes.py | 58 | 40 | 28 | 11 | 1 | 0.72 |
| check_pinned_restatement.py | 37 | 37 | 22 | 14 | 1 | 0.61 |
| check_sha256sums.py | 78 | 40 | 22 | 17 | 1 | 0.56 |
| check_study_paths.py | 110 | 40 | 33 | 7 | 0 | 0.83 |
| hygiene_scan.py | 79 | 40 | 22 | 18 | 0 | 0.55 |
| lint_claims.py | 126 | 40 | 27 | 13 | 0 | 0.68 |
| (check_current_inventory.py, verify_inventory_current.py: see Run C) | | | | | | |
Timeouts (4): all are `and -> or` / const flips in the `-I -B` re-exec guard (infinite re-exec) — detected, not survivors.
(Run B / Run C sections and the survivor classification follow.)

## Run C (inventory refreshed per mutant; CI-run tests)
| file | sites | run | killed | survived | kill rate |
|---|---|---|---|---|---|
| check_current_inventory.py | 29 | 29 | 22 | 7 | 0.76 |
| verify_inventory_current.py | 40 | 40 | 17 | 23 | 0.43 (no test file at all; only the [1/5]-failing fixture) |

### verify_inventory_current.py survivors
GAPS (no test exercises gates [2/5]-[4/5]; the one bad fixture fails at [1/5] first):
- H L72 `return 1 -> 0` after [2/5] FAIL: a stale/mismatched current inventory would PASS the gate.
- H L81 `return 1 -> 0` vocabulary violation passes. H L78 `or -> and`: a row needs BOTH bad status and bad scope to fail.
- H L86 `return 1 -> 0`: Unreviewed artifacts pass.
- H L101 `return 1 -> 0`: a Lean lock hash mismatch passes. H L97 `== -> !=`: skips every ledger entry except the self-entry, so no
  Lean digest is checked. M L94/L98 `continue -> break`: ledger read stops at the first blank line / self-entry; later digests unchecked.
- M L49 `return 1 -> 0`: a missing sub-checker script counts as PASS.
EQUIVALENT: L40 chunk size 2^20->2^21 bytes (hash unchanged); L50 text=False (display; crash path only when rc!=0, still non-zero);
L51/L55 tail lengths (display); L54 `!= -> ==` only selects when stderr is echoed; L60 argparse description; L77 enumerate start
(message line number); L91/L102 digest counter (display); L93 drop `not` (blank line -> split() ValueError -> crash: stricter);
L110/L111 sys.path.insert(0 -> 1) (module still found; nothing shadows it in the clone).

### check_current_inventory.py survivors (all EQUIVALENT or L)
L39 IN_GHA flip (annotation only); L43 MAX_LISTED 20->21 and L117 `> -> >=` (how many lines are listed); L57 capture_output
(git noise only); L100 description; L108 `return 2 -> 3` (still non-zero). L L48 drop `not` in load_generator: would always use the
checker's own copy of the generator instead of the target repo's; identical file here, differs only for --repo of another tree.

## Run B (Run A survivors + tools/redteam) — and survivor classification per file
### check_sha256sums.py: Run A 22/39 (0.56); with redteam 30/39 (0.77)
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

### check_pinned_restatement.py: 22/36 (0.61), redteam adds nothing
- H L110 delete "cannot read pinned source" (+ continue): an unreadable/missing pinned source is silently skipped -> PASS.
- M L116 delete "not listed with sha256 ... in SUMS": pinned file and SUMS ledger may disagree unnoticed (hard pin still checked).
- M L124 delete "no namespace/import substitution applied": a substitution table that stops matching is not reported.
- L L91 `continue -> break` in read_sums: stops at the first blank/comment line (stricter: later pins look unlisted).
- EQUIVALENT: L111/L121 continue->break after an error; L128 x3 and L129 only change the "at line N" text in a message
  (L129 can crash with None+1, still non-zero); L137 RESTATED_DIR unlistable is also reported by every per-file read;
  L90 `or -> and` only lets blank/comment lines into the sums dict as junk keys never queried; L146 description; L151 `2 -> 3`.

### check_modes.py: 28/39 (0.72), redteam adds nothing
- M L86 `"/" in tok -> not in` and L78 `break -> continue`: the PUSH_NOTES backtick-path branch and the section end are untested;
  a mutant can drop PUSH_NOTES-listed scripts from the exec-bit check (L86) or pull in other sections (L78, stricter).
- L L116 `continue -> break`: shebang scan stops at a missing object (SHEBANG_NOT_EXEC is warn-only). L L174 warning count.
- EQUIVALENT: L33 GHA flag; L110 parse start 0->1 (only header[1], header[2] are used); L115 x2 (`or -> and`, `[1] -> [0]`:
  a "missing" header always has < 3 fields, so the result is the same); L125 description; L167 x2 annotation path index.
Timeout: L114 `pos = nl + 1 -> + 0` (infinite loop) — detected.

### check_artifact_pins.py: 34/40 (0.85), redteam adds nothing
- L L195/L251/L266 summary counters (ok/known_missing/known_changed) wrong by one — display only, but untested counts.
- L L252 `and -> or`: FLAG_DISAGREES notice logic (notice, never an error).
- EQUIVALENT: L163 GHA flag; L179 `or -> and` in the work-tree probe (rc != 0 and stdout != "true" coincide in practice).

### check_manifest.py: 35/39 (0.90), redteam adds nothing
- EQUIVALENT (all 4): L206/L214 `continue -> break` after `failed += 1`/error (run fails anyway; later manifests unchecked but
  verdict already FAIL); L218 display quoting; L224 trailing-newline display. Timeout L60 (re-exec guard) detected.

### check_study_paths.py: 33/40 (0.83), redteam adds nothing
- L L178 delete "empty <id_col>" error: a registry row with an empty id is not flagged.
- EQUIVALENT: L166/L179/L183 continue->break after an error; L175 enumerate start (message line numbers); L206 `or -> and` on
  the baseline shape check (a malformed baseline then crashes -> non-zero); L300 `2 -> 3`.

### hygiene_scan.py: Run A 22/40 (0.55); with redteam (test_rt_claims_hygiene.py) still 22/40 — redteam adds nothing
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

### lint_claims.py: Run A 27/40 (0.68); with redteam 31/40 (0.78)
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
386 mutants run. CI tests only: 262 killed + 4 timeouts (detected) = 266 detected, 120 survived -> 0.69.
Adding tools/redteam: +8 (check_sha256sums) +4 (lint_claims) = 278 detected, 108 survived -> 0.72.
(The earlier "289 killed / 93 survived" from the raw first run counted the vacuous self-hash kills; superseded.)
Per file, detected/run (CI only -> with redteam): check_manifest 36/40 (0.90); check_artifact_pins 34/40 (0.85);
check_study_paths 33/40 (0.83); check_current_inventory 22/29 (0.76); check_modes 29/40 (0.72); lint_claims 27/40 (0.68 -> 0.78);
check_pinned_restatement 23/37 (0.62); check_sha256sums 23/40 (0.58 -> 0.78); hygiene_scan 22/40 (0.55); verify_inventory_current 17/40 (0.43).
Sampling: <= 40 of each file's sites (seed 20261120), so per-file rates are estimates and unsampled sites may hide more gaps.

## Top gaps, ranked
1. H verify_inventory_current.py gates [2/5]-[4/5] have NO test: `return 1 -> 0` at L72 (stale current inventory), L81/L78
   (vocabulary), L86 (unreviewed artifacts), L101/L97 (Lean lock hash) all PASS silently. This is the main inventory gate.
2. H CI does not run tools/redteam, so check_sha256sums.py core failures (L178 deleted listed file, L175 missing entry -> notice,
   L162/L167 path/symlink escape, L149 unreadable list) and lint_claims.py evidence_scope checks (L170, L373, L148) are protected
   only by tests CI never executes.
3. H check_pinned_restatement.py L110: an unreadable/missing pinned source is silently skipped -> PASS (no test, redteam included).
4. M check_sha256sums.py L189: an emptied SUMS list passes; L154 a blank/comment line truncates the rest of a list (latent).
5. M hygiene_scan.py L122/L260: a failing git call returns [] (`--base <missing ref>` scans 0 files -> PASS outside CI's
   pre-check), and a symlink/missing path stops the whole scan (latent).
Next tier (M): verify_inventory_current L49 missing sub-checker = PASS and L94/L98 ledger loop truncation; check_pinned_restatement
L116/L124; check_sha256sums L91 subfolder --repo; check_modes L86/L78 PUSH_NOTES branch; lint_claims L247 wrong fenced block as
vocabulary; hygiene_scan L135 non-git walk, L286 --strict with one warning.

## Recommended follow-ups (separate branches; no gap-filling tests on this branch)
1. Add tools/ci/tests/test_verify_inventory_current.py with one bad fixture per gate [2/5]-[5/5] (stale row, bad vocabulary,
   unreviewed artifact, Lean lock digest mismatch, missing sub-checker), each asserting the failing gate's message.
2. Decide (owner) whether CI runs tools/redteam; if not, port the sha256sums and lint_claims evidence_scope cases into tools/ci/tests.
3. check_pinned_restatement: fixture with an unreadable pinned source; plus SUMS-disagreement and dead-substitution fixtures.
4. check_sha256sums: empty-list and blank/comment-line fixtures; subfolder --repo rejection test.
5. hygiene_scan: tests for a failing `--base` ref (must be rc 2), a tracked symlink mid-tree, non-git walk, --strict with 1 warning.
6. Re-run this tool with a higher --max-per-file on the four lowest files after 1-5 land, to sample the unrun sites.
