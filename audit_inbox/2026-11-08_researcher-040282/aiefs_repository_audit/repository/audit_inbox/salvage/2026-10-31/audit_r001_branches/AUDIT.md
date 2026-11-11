# Audit: Researcher 001 local branches (read-only), 2026-10-29

Scope: `research/lean-kn` @ 8d33097 (15 files) and `research/freezing` @ 2672698 (31 files). Both are one commit on
merge-prep 9d46d9b, in `/workspace/branches/r001/research-base`, with report `/workspace/branches/r001/REPORT.md`.
All work was done in an independent clone (`repo/`) plus worktrees `wt_lk`, `wt_fz`, `wt_base`, `wt_pins`, `wt_merge`
under this directory. No pushes, no GitHub writes, no edits to the researcher's clone or worktrees, and no git config
changes (merge identity came from GIT_AUTHOR_*/GIT_COMMITTER_* env vars only). Logs are in `logs/`.

## Verdicts

| Branch | Verdict |
|---|---|
| research/lean-kn @ 8d33097 | **CLEAN WITH NOTES** |
| research/freezing @ 2672698 | **FIXES REQUIRED** (one wording fix in ERRATA E12; everything else passes) |

### Required fixes
1. **freezing, `ERRATA_2026-10-28.md:188` (E12 "Mechanism-aligned"):** "B rises iff R > μ/(η+μ) (ungated)" is only true at
   B = 0. The map is U = B + dt((η+μ)R − μ − γB), so B rises iff R > (μ+γB)/(η+μ). The equilibrium is above B_c iff
   R > (μ+γB_c)/(η+μ) ≈ 0.4543 (η=0.04, μ=0.03, γ=0.015, B_c=0.12). The note itself is correct
   (`research/freezing/REPORT.md:67,113-114`), so only the errata sentence is wrong. Suggested text: "In the discrete map
   B rises iff R > (μ+γB)/(η+μ) (ungated); an edge settles above B_c iff R > (μ+γB_c)/(η+μ) ≈ 0.454".

The validator default (item g) is a real defect, but it is **pre-existing on 9d46d9b and not introduced by either
branch**. It should be fixed on merge-prep, not on these branches.

### Non-blocking notes
- lean-kn: declarations live in namespace `AIEFProofs.*` inside the `AIEFProofsKn` library. This works, but a future
  name clash with the base package is possible. Consider `AIEFProofsKn.*`.
- lean-kn and freezing: the new Lake projects are not built by `.github/workflows/lean.yml` (see i). Both ledger rows
  already say so.
- freezing: `ERRATA_2026-10-28.md:193` citation title should be "**Dynamics of** phase oscillator networks with synaptic
  weight and structural plasticity", *Sci Rep* 12:15003 (2022). The DOI is correct.
- freezing: `/workspace/branches/r001/REPORT.md:249` says backups are "kept in `preguard/`", but they are not in the repo
  (the in-repo note line 4 and REPORT.md:56 say they were not copied). Fix the stale sentence.
- freezing: trailing whitespace at `research/freezing/freeze_check.py:103`. The output JSONs have no final newline
  (json.dump default). This is cosmetic, and the outputs regenerate byte-identically.
- Pre-existing and out of scope: root `test_01.py` is junk (mixed shell and Python, contains a home-directory path).

## (a) Hash pins
Neither branch changes a hash-pinned path: `audit_manifest.json files_sha256`, the registry sha256 column, and the Lean
SHA256SUMS/lock files are all unchanged. `tools/ci/check_artifact_pins.py` (from ci/artifact-pins a64d90e) passes on
base, lk, fz and the trial merge: 2898 rows, 2839 match, 7 known-changed, 52 known-missing, 0 errors. Pins tool caveat: a
for/else bug gave a false positive on README.md in my own helper only; README.md is not actually pinned.

## (b) CI
Ran `scripts/ci_all.sh` (logs/b_ci_{base,lk,fz}.log), using a private-tmp copy of run_ci.sh because the original
shares `/tmp/ci_out.txt`:
- run_ci passed: lint_claims, hygiene, hygiene --pii, check_manifest, check_modes, check_artifact_pins, tools/ci pytest
  and unittest.
- `lint_claims --strict` passed: 76 rows on each branch, 0 violations.
- claims regeneration gave no diff.
- pytest fast and slow passed in the modular v4 package and in workspace-019ff86e. The remaining skips are
  environmental and identical on base: the oracle run is absent, and the authoritative engine is not in the scaffold.
- The validator fails only with its default `--edited-since ce8cced` (see g). It passes with `--edited-since 9d46d9b`.
- The tree stayed clean after CI.

## (c) Lean
**lean-kn, `lean/AIEFProofsKn` (check_lean_kn.sh from scratch with `.lake/build` removed): PASS 7/7.**
- Toolchain 4.33.1; Mathlib pin 0df444a3.
- Base project hashes verified.
- 52 declarations, 0 warnings.
- Forbidden markers: none (sorry/admit/axiom/etc.).
- Axioms: propext, Classical.choice, Quot.sound only.

Statements were confirmed independently with `lean_audit/AuditKn.lean` (`#check` and `#print axioms`):
- The general theorem `dim ker = C(n,2) − n` for all n ≥ 3 is stated for the **repo's own** `inc`/`rinv`. The imported
  base definitions are used directly, so no copy is involved; `rinv_eq_rinv` is `rfl`.
- The n = 12 instance gives 54.
- There is also a Mathlib edge-restricted version.

Base project:
- `lean/AIEFProofs` diff vs 9d46d9b is empty, and the per-n file sha (f1382204…) is unchanged.
- Base `check_lean.sh` from scratch: PASS, 115 declarations, 0 warnings.

**freezing, `lean/AIEFFreezeCore` (check_lean_freeze.sh from scratch): PASS 7/7.**
- 5 declarations, 0 warnings, standard axioms only.
- Compared with the previously audited copy, only the header, imports, docstring, options and whitespace differ. The
  theorem statements are identical and match the note's FreezeCore section.
- All previously required note fixes are present.

## (d) Freezing scripts
Re-run in wt_fz (logs/d_*.out):
- Engine cross-check: 0.0.
- All 4 output JSONs are byte-identical (git tree clean after the re-run), and the logs match.
- 1412 certified (run, T) pairs with 0 violations.

## (e) claims.csv and errata
- claims.csv regenerates byte-identically on both branches.
- Every line pointer in E11 and E12 resolves to the stated text.
- E11 is accurate.
- E12 has the formula error listed under Required fixes, plus the citation-title note.

## (f) PII and hygiene
- `hygiene_scan --pii` passes.
- Files are UTF-8 with LF line endings; there are no absolute paths (apart from a benign `/tmp` usage example in a
  README), no pycache and no secrets.
- The copyright header with the owner's name follows the existing convention in all 6 base Lean files.

## (g) Validator default `--edited-since ce8cced`
**This is a real defect (pre-existing).**
- `audits/engineering/validate_registry_against_tree.py:50` defaults to ce8cced, and line 56 runs
  `git diff --name-only -z <rev> HEAD`.
- ce8cced exists only in an unpublished local merge-prep repo (a local merge of arena 7edbab2). No published commit has
  that tree, and 7edbab2 is not an ancestor of 9d46d9b.
- As a result, the default exits with git status 128 on every fresh clone: base, lk, fz and the trial merge all fail.
- The same default is on 9d46d9b, audit/nanfix-v2 and ci/artifact-pins. The validator does not exist on main.
- The PR template (line 56) and `registry/README.md:13` tell reviewers to run it with defaults.

The edited set only affects `--write` notes. Exactly 2 rows are annotated: ART-0744 (`Basic.lean`) and ART-0746
(`Smoke.lean`). Substituting another revision changes those notes (tested, then reverted).

**Proposed fix (on merge-prep):**
- Replace the git-derived default with a frozen set:
  `EDITED_BY_MERGE_PREP = {"lean/AIEFProofs/AIEFProofs/Basic.lean", "lean/AIEFProofs/AIEFProofs/Smoke.lean"}`.
  Alternatively, default to `None` and keep the existing notes untouched.
- Keep `--edited-since REV` as an optional override, validated with `git rev-parse --verify REV^{commit}`, and exit
  with a clear message instead of a traceback.
- Update the PR template and `registry/README.md`.
- Add a test that runs the validator in a shallow or fresh clone.

## (h) Trial merge (wt_merge, from 9d46d9b)
Merge order and results:

| Merge | Result |
|---|---|
| origin/audit/nanfix-v2 (cbf2ae7) | clean |
| origin/ci/artifact-pins (a64d90e) | clean |
| refs/r001/lean-kn | conflict in `ERRATA_2026-10-28.md` (E10 and E11 both appended at the end) |
| refs/r001/freezing | conflicts in `ERRATA_2026-10-28.md`, `README.md`, `registry/claims.csv` and `registry/reconciliation/build_claims_reconciliation.py`; `CURRENT_STATUS.md` auto-merged |

How each conflict was resolved:
- **ERRATA:** kept both sides in order E10, E11, E12.
- **Generator:** union of the LEAN-KN-01 and RES-FREEZE-01 blocks.
- **README Lean section:** kept the lean-kn extended Lean bullet, then the freezing bullet, with the duplicate
  "`check_lean.sh` run (`LEAN-R4`)." line dropped.
- **claims.csv:** took ours, then regenerated.

Result: **77 rows**. nanfix-v2 rewrites the existing AUD-REPRO-B2A95 row rather than adding one, so the count is
75 + LEAN-KN-01 + RES-FREEZE-01.

Checks on the combined tree (logs/h_ci_merge.log):
- The regenerator is idempotent.
- The merged `lean/` and `research/freezing/` subtrees are identical to the branch versions, and `lean/AIEFProofs` is
  unchanged vs 9d46d9b.

CI on the combined tree passed everything except the validator default:
- lint --strict: 77 rows, 0 violations.
- hygiene and PII, manifest, modes: pass.
- check_artifact_pins: 2898/2839/7/52, 0 errors.
- All pytest fast and slow: pass.
- Validator with `--edited-since 9d46d9b`: pass. With the default: fails, same as g.
- The tree stayed clean.

E11's sentence "(E10 is used by the separate branch audit/nanfix-v2 …)" still reads correctly after the merge.

## (i) lean.yml coverage
**Yes, the new projects are missing.** `.github/workflows/lean.yml` (main = 9d46d9b) has one job, hard-wired to
`lean/AIEFProofs`. Its `lean/**` path filter means a change to `lean/AIEFProofsKn` or `lean/AIEFFreezeCore` triggers the
workflow, but it rebuilds only the base project, so the run is green without checking them. That is a false green.

Minimal change: turn the job into a matrix and leave everything else as it is (pinned SHAs, permissions, concurrency).

```yaml
jobs:
  lean:
    name: lean (${{ matrix.project }})
    runs-on: ubuntu-latest
    timeout-minutes: 60
    strategy:
      fail-fast: false
      matrix:
        include:
          - { project: AIEFProofs,     script: check_lean.sh }
          - { project: AIEFProofsKn,   script: check_lean_kn.sh }
          - { project: AIEFFreezeCore, script: check_lean_freeze.sh }
    defaults:
      run:
        working-directory: lean/${{ matrix.project }}
    steps:
      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5
      - uses: leanprover/lean-action@24581d74d674803a25a81b10b059c5c0cdd344c6 # v1.6.2
        with:
          lake-package-directory: lean/${{ matrix.project }}
          use-mathlib-cache: true
          build: true
          test: false
          lint: false
          axiom-audit: true
          axiom-audit-allow: propext,Classical.choice,Quot.sound
          axiom-audit-root: ${{ matrix.project }}
          leanchecker: false
      - name: ${{ matrix.script }}
        run: |
          chmod +x ./${{ matrix.script }}
          SKIP_CACHE=1 STRICT_ORPHANS=1 LOG_DIR="$GITHUB_WORKSPACE/lean-check-logs" ./${{ matrix.script }}
      - name: Upload check logs
        if: always()
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        with:
          name: lean-check-logs-${{ matrix.project }}
          path: lean-check-logs/
          retention-days: 30
```

Notes on this proposal:
- All three scripts honour SKIP_CACHE, STRICT_ORPHANS and LOG_DIR. The Kn and FreezeCore scripts default to strict.
- The base `check_lean.sh` is mode 644 in the tree, so the `chmod +x` is still needed.
- AIEFProofsKn's path dependency `../AIEFProofs` resolves in the checkout. Its script also re-verifies the base hashes.
- The artifact name changes from `lean-check-logs` to `lean-check-logs-<project>`. Update any docs that cite it, such as
  the header comment and README run references.
- Optional: name the new projects in `lean/README` or the workflow header comment.
- This change was not run on GitHub (no writes allowed). Each script was run locally from scratch and passed.
