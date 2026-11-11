# Lean recovery record — `ControllerFiberProjector.lean`

## Provenance (read first)
* The module imported by `lean/AIEFProofs/AIEFProofs.lean` was never committed (see `LEAN_STATUS.md`). The owner found two local
  copies on their own machine: `ControllerFiberProjector.lean` (191 lines, older) and `ControllerFiberProjector 01.lean` (303 lines, newer).
* `originals/` holds those two files **as reconstructed from the owner's chat paste**: the 191-line file verbatim; the 303-line file
  rebuilt from the 191-line file plus the owner's pasted `diff` output (`originals/v191_vs_v303.diff`). Trailing whitespace was stripped.
  They are therefore faithful in content but not guaranteed byte-identical to the files on the owner's disk.
* `fixed/` holds the tactic-only fixes; `patches/` the original→fixed unified diffs; `scripts/mkfix.py` (generates the fixed files from the
  originals, each replacement asserted to match exactly once) and `scripts/check_statements.py` (asserts all theorem/lemma/def statements are unchanged).
* `fixed/ControllerFiberProjector.v303.fixed.lean` (sha256 52a2f273…) is byte-identical to the file committed in
  `0b5b1082561b7717a0ea465d76bb9ebefa26b770` as `lean/AIEFProofs/AIEFProofs/ControllerFiberProjector.lean`.
* `logs/<run>.log` bundle each `check_lean.sh` run (console output, then every per-step log file). Local paths are redacted to
  `<repo-clone>` (the checked-out repo), `<logs>`, `<work>`, `<home>`. Runs: `v191_original`, `v303_original` (both FAIL, step 5),
  `v191_fixed`, `v303_fixed` (PASS) on 60e6029 + the file; `verify_main` (PASS) on main @ 0b5b108; `verify_0b5b108_plus_0003` (PASS) on
  0b5b108 + check_lean.sh / `.check_logs` ignore / root workflow (patch 0003), before those were committed.
* `SHA256SUMS` covers every file in this folder. Original file names used below map as: `tested_files/` → `originals/`, `fix/*.lean` → `fixed/`,
  `fix/*.patch` → `patches/`, `fix/*.py` → `scripts/`, `clone_v191/`, `clone_v303/`, `verify_main/` = fresh clones (not committed).

---

## Original test report (written before the push of 0b5b108)

Repo `jacobbrainard84-knightninja/AIEFS` main @ `60e60297e6dd34887348e6f858c32b3829d72f69`, project `lean/AIEFProofs`,
Lean `v4.33.1`, Mathlib `0df444a360eaa60ab8c11dca51a86af692955474` (manifest pin, verified by check_lean.sh step 2).
Fresh clones `clone_v191/`, `clone_v303/`. The only change to the repo is adding `lean/AIEFProofs/AIEFProofs/ControllerFiberProjector.lean`.
(`git status` also shows the committed `.lake/build` artefacts as modified/deleted, because check_lean.sh deletes `.lake/build` to force a rebuild — a known repo issue, see LEAN_STATUS.md.)
Nothing committed or pushed at that point.

## Files tested (SHA-256 in SHA256SUMS)
| file | lines | what it is |
|---|---|---|
| tested_files/ControllerFiberProjector.v191.original.lean | 191 | owner's older file, unmodified |
| tested_files/ControllerFiberProjector.v303.original.lean | 303 | owner's newer file ("… 01.lean"), unmodified |
| fix/ControllerFiberProjector.v191.fixed.lean | 189 | MY FIX of v191 (proof scripts only) |
| fix/ControllerFiberProjector.v303.fixed.lean | 299 | MY FIX of v303 (proof scripts only) |

`tested_files/v191_vs_v303.diff` reproduces the owner's `diff` output exactly (whitespace aside).

## Results (check_lean.sh: cache get, rebuild from source, marker scan, collectAxioms audit + #print axioms)
| version | build | jobs | Lean errors | warnings | markers | axioms |
|---|---|---|---|---|---|---|
| v191 original | **FAIL** (step 5) | stopped at [1235/1237] | 7 | 5 (`linter.unusedSimpArgs`) | not reached | not reached |
| v303 original | **FAIL** (step 5) | stopped at [1234/1236] | 10 | 8 (unusedSimpArgs ×6, unusedTactic, unreachableTactic) | not reached | not reached |
| v191 fixed | **PASS** | 1237 | 0 | 0 | 0 hits | 43 project decls, all ⊆ {propext, Classical.choice, Quot.sound} |
| v303 fixed | **PASS** | 1236 | 0 | 0 | 0 hits | 58 project decls, all ⊆ {propext, Classical.choice, Quot.sound} |

(v191 has 1 extra job because of `import Mathlib.Tactic.Abel`.)
Theorems/lemmas in the projector module: v191 = 13 (+2 defs PPar, PPerp); v303 = 23 (+3 defs incl. SPerp).
Every one: `#print axioms` = [propext, Classical.choice, Quot.sound]. ControllerFiber decls unchanged: same allowed set
(the `@[simp]` literal lemmas use only [propext, Quot.sound]). Logs: `logs/<v>_{original,fixed}/7_axioms*.txt`.

## Diagnosis of the original failures — proof-script (tactic) breakage, NOT missing names and NOT a math gap
Every name the file uses from ControllerFiber exists with the expected statement: `CCtrl`, `vCtrl`, `vCtrl_zero/one/two`,
`sum_fin3`, `CCtrl_mulVec_apply_zero/one`, `CCtrl_mulVec_vCtrl`, `CCtrl_mulVec_eq_zero_iff_exists_smul`. No "unknown identifier" errors.
All statements are true; each failure is `simp` normalising differently from what the script expects under this Mathlib
(`1/3` → `3⁻¹`, `(c • v) j` → `c * v j`, `mul_eq_mul_right_iff` producing `… ∨ vCtrl i = 0`,
`Matrix.mulVec_mulVec` folding `P *ᵥ (P *ᵥ x)` into `(P*P) *ᵥ x`), or simp closing a goal before a trailing `ring`.
The errors are consistent with the files having never been compiled against this pin (or written against a different Mathlib).

v303 original errors (verbatim locations; full text in logs/v303_original/5_build.log):
1. 60:61 `PPar_apply_comm` — unsolved `3⁻¹ * vCtrl i * vCtrl j = vCtrl i * (3⁻¹ * vCtrl j)` (`simp [mul_comm]`).
2. 85:2 `PPar_mulVec_vCtrl` — `No goals to be solved` (trailing `ring`).
3. 120:65 `PPerp_symmetric` — unsolved `3⁻¹ * vCtrl i * vCtrl j = 3⁻¹ * vCtrl j * vCtrl i` (simp unfolds PPar via `@[simp] PPar_apply` before using the comm lemma).
4. 131:39 `PPar_sq_mulVec` — unsolved `∑ (vCtrl x_1 ^ 2 * ∑ …) * (1/3) = ∑ … ∨ vCtrl i = 0`; `hS` unused.
5. 148:50 `PPar_mulVec_PPerp` (inner `hdiff`) — unsolved `x 0 - ∑ x_1, vCtrl x_1 * x x_1 - x 1 - x 2 = 0`.
6. 145:32 `PPar_mulVec_PPerp` — unsolved `… = 0 ∨ vCtrl i = 0`; `hdiff` unused because `rw [… PPar_mulVec x]` had already rewritten the `PPar *ᵥ x` that `hdiff` mentions.
7. 194:12 `PPar_dot_PPerp` — `simp` max recursion depth (`simpa [hx]` with `hx : PPar *ᵥ x = PPar *ᵥ (PPar *ᵥ x)` loops).
8. 195:38 `PPar_dot_PPerp` — unsolved `∑ ((PPar * PPar) *ᵥ x) x_1 * y x_1 = …` (`simp [PPar_sq_mulVec]` loses to `mulVec_mulVec`).
9. 243:25 `range_PPar_iff_ker_CCtrl` — `rewrite` failed, pattern `∑ i, vCtrl i * (?a * vCtrl i)` not found (goal has `(a • vCtrl) j`).
10. 253:2 `id_eq_PPar_add_PPerp` — `No goals to be solved` (trailing `ring`).
Warnings: 121:15, 140:23, 155:23, 196:18, 213:8, 213:33 unused simp args; 214:6 unusedTactic + unreachableTactic (`ring`).

v191 original: the same failures for the shared lemmas (83:2, 115:39, 138:50, 135:32, 178:25, 188:2), plus
129:42 `PPerp_sq_mulVec` — unsolved `(PPar *ᵥ fun i ↦ x i - (PPar *ᵥ x) i) i = 0`: it is proved *before*
`PPar_mulVec_PPerp`, which it needs (v303 already fixes this by moving it after and reproving it). Warnings: 124:23, 131:22, 145:23, 163:6, 163:31 unused simp args.

## Fixes (separate files; owner originals untouched)
`fix/v303-original-to-fixed.patch`, `fix/v191-original-to-fixed.patch` (unified diffs original→fixed).
Statements verified identical by `fix/check_statements.py` (all 23 / 13 theorem+lemma+def headers byte-identical after whitespace
normalisation; v303 declaration order unchanged; v191 only moves `PPerp_sq_mulVec` after `PPar_mulVec_PPerp`, as v303 does).
No sorry/admit/axiom/native_decide. Changes are tactic-only: `simp` → `simp only [..., smul_eq_mul, ...]` where the normal form
mattered, delete redundant trailing `ring`, replace looping `simpa [hx]` by the exact term `(PPar_selfAdjoint (PPar *ᵥ x) y).symm`,
`simp [PPar_sq_mulVec]` → `rw [PPar_sq_mulVec]`, and drop unused simp args (warning cleanup).

## Lakefile / root import
`lakefile.toml` has `[[lean_lib]] name = "AIEFProofs"` with no `globs`/`roots`, so the default root `AIEFProofs` and everything it
imports are built. The existing `import AIEFProofs.ControllerFiberProjector` in `AIEFProofs.lean` is sufficient; no lakefile or other
import change is needed (check_lean.sh step 3: all imports resolve; `Built AIEFProofs.ControllerFiberProjector` appears in the build log).
Only remaining orphan: `AIEFProofs/Smoke.lean` (pre-existing, unrelated).

## Recommendation
Commit **fix/ControllerFiberProjector.v303.fixed.lean** as `lean/AIEFProofs/AIEFProofs/ControllerFiberProjector.lean`
(done: committed in 0b5b108).
It is a strict superset of v191's theorems, does not need `Mathlib.Tactic.Abel`, builds with 0 warnings, and is axiom-clean.
Do NOT commit either original as-is: both fail `lake build`.

## Post-push verification of main @ 0b5b1082561b7717a0ea465d76bb9ebefa26b770
Fresh clone `verify_main/` with HEAD = 0b5b108 and 0 local changes before the run. The committed blob 6c64fb29 has sha256 52a2f273…, the same as fix/ControllerFiberProjector.v303.fixed.lean.
I ran `check_lean.sh` unmodified (sha256 0fe26306…, same as the copy in the investigation workspace and as committed later). **PASS, exit 0**: 1236 jobs, 0 warnings, marker scan 0 hits in 5 files,
58 project declarations audited, all within {propext, Classical.choice, Quot.sound}. `#print axioms` covered 42 theorems and lemmas (19 in ControllerFiber + 23 in the projector); disallowed=0.
Timing: 1m05s wall in total (cache get 51s, build 7.9s). Logs: logs/verify_main/.
Stale committed .lake outputs: the default run deletes .lake/build, so every project module was recompiled from source. A second fresh clone run with REUSE_BUILD=1
(`verify_main_reuse/`, logs/verify_main_reuse/) also PASSES with identical results. In that run Lake reused the committed Basic/ControllerFiber oleans, because their traces
still match, and rebuilt ControllerFiberProjector and the root. So the stale outputs do not change the build result. However, any build rewrites the 8–11 tracked .lake files,
which leaves the working tree dirty and can cause `git pull` conflicts.
