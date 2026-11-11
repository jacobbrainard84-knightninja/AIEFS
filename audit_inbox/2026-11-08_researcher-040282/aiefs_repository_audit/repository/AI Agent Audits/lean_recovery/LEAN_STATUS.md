# AIEFProofs Lean status — dangling `AIEFProofs.ControllerFiberProjector` import

> **UPDATE 2026-10-25 — RESOLVED by recovery, not by removing the import.**
> The missing file was found on the owner's own machine (two local copies: a 191-line older version and a
> 303-line newer version, "ControllerFiberProjector 01.lean"); it had simply never been committed.
> The owner's 303-line version, with proof steps (tactics only) fixed for Lean v4.33.1 / Mathlib `0df444a3…`
> and all theorem statements unchanged, is now committed as `lean/AIEFProofs/AIEFProofs/ControllerFiberProjector.lean`
> in commit `0b5b1082561b7717a0ea465d76bb9ebefa26b770`. The root import is kept; patch 0001 (remove import) and the
> candidate module 0002 are therefore **obsolete** and were not applied.
> Verification of main @ 0b5b108: `check_lean.sh` PASS (1236 jobs, 0 warnings, 0 markers, 58 declarations, axioms ⊆
> {propext, Classical.choice, Quot.sound}); also PASS with patch 0003 applied (check_lean.sh, `/.check_logs`, root workflow),
> which was then committed. Full recovery record: `AI Agent Audits/lean_recovery/` (RESULTS.md, originals, fixed files, patches, logs).
> The 30 committed `.lake` build outputs (problem 1 in §3) are untracked by the "Cleanup (n/48)" commits.
> The sections below are the original investigation of `60e6029` and are kept as written (one clarifying note added in §8).

Repo state examined: `main` @ `60e60297e6dd34887348e6f858c32b3829d72f69` (also `arena/d4a487cc-aiefs` @ `7edbab2`).
Nothing was committed or pushed. All evidence is in `logs/`.

## 1. Verdict: MISSING (never committed), not misplaced

| Where searched | Result | Log |
|---|---|---|
| Working tree, all extensions, case-insensitive `*projector*` | no such file; only `.lean` files are the 4 in `lean/AIEFProofs/` | `logs/03_fs_search.log` |
| Full git history, all refs (`git log -S`, `git log --all -- '*rojector*'`, `git grep` on every ref) | the string occurs **only** as the import line in `AIEFProofs.lean` (plus audit notes). No path containing "projector" ever existed | `logs/01_git_history.log`, `logs/02_git_grep.log` |
| Branches/tags | `main`, `arena/d4a487cc-aiefs`; no tags; same dangling import on both | `logs/01_git_history.log` |
| GitHub (read-only): branches, tags, PRs, issues, forks, gists | 2 branches, 0 tags, 0 PRs, 0 issues, 0 forks, 0 gists. Code search returned 0 even for the existing `ControllerFiber` (repo not indexed), so code search is **inconclusive** | `logs/05_github_connector.log` |
| 3 zips, all PDFs/ODTs (text-extracted) in the repo | no `.lean` files in zips; no "ControllerFiberProjector" anywhere | `logs/04_archives_pdfs.log` |
| Collaborator transcript | no mention of the module; discusses projectors mathematically (see §2) | — |

How it happened (evidence + inference):
* `add81e6` added `lean/AIEFProofs` as a **gitlink** (mode 160000 → nested-repo commit `27cbb2e`, no `.gitmodules`); that object is not on GitHub.
* `d2f8452` ("Add SSRH project") replaced the gitlink with the real tree; the root import of `ControllerFiberProjector` was **already present** in that first commit, and the file was not.
* The committed build artefact `lean/AIEFProofs/.lake/build/ir/AIEFProofs.c` lists imports `AIEFProofs.Basic`, `AIEFProofs.ControllerFiber` only → the last successful build predates the import line.
* Inference: the import was added in the owner's local nested repo (planned or uncommitted work). **Owner action:** check the local `lean/AIEFProofs/` (including its own `.git`, `git stash list`, untracked files, editor backups) for `AIEFProofs/ControllerFiberProjector.lean`.

No module or document references any declaration from `ControllerFiberProjector`. Nothing describes its contents.

## 2. What it was probably meant to contain (INFERENCE, labelled)
From the project histories and docs, the next Lean steps planned after `ControllerFiber` were: (i) `ker CCtrl = span_ℚ{vCtrl}` as a `LinearMap`/submodule equality (planned name `AIEF.ControllerFiber.kernel_eq_span`), (ii) a real-valued corollary with the unit generator `(1/√3)(1,−1,−1)`. The docs/collaborator note discuss three projectors onto the fiber `span{v}`, `v=(1,−1,−1)`:
* Euclidean `P = v vᵀ/(vᵀv) = (1/3) v vᵀ`;
* biorthogonal `Q = v u*ᵀ/(u*ᵀv)`, `u* ∝ (1,0,−1)` → `Q = (1/2) v (1,0,−1)`;
* H-orthogonal `P_H = v vᵀH/(vᵀHv)` (needs a specific H).
Which (if any) was intended is **unknown**.

## 3. Lean setup (as committed)
* Project: `lean/AIEFProofs/` (Lake, `lakefile.toml`, lib `AIEFProofs`, default target `AIEFProofs`; options `relaxedAutoImplicit=false`, `weak.linter.mathlibStandardSet=true`, `maxSynthPendingDepth=3`).
* Toolchain: `leanprover/lean4:v4.33.1` (via elan). Mathlib `v4.33.1` = `0df444a360eaa60ab8c11dca51a86af692955474` (manifest; deps plausible, LeanSearchClient, importGraph, proofwidgets, aesop, Qq, batteries, Cli all pinned by commit). `AIEF_LEAN_PROJECT_LOCK_HASHES.txt` sha256 of toolchain/manifest/lakefile — verified OK.
* Modules: `AIEFProofs.lean` (root: imports Basic, ControllerFiber, **ControllerFiberProjector ✗**), `Basic.lean` (`hello`), `ControllerFiber.lean` (CCtrl/vCtrl kernel theorems, 148 lines), `Smoke.lean` (**orphan**: not imported, never built by `lake build`).
* Problems found besides the import:
  1. 30 `.lake/build` artefacts are **committed** despite `.gitignore` `/.lake`. Every local build modifies them (shown in `logs/50_final_end_to_end`), so the owner's periodic `git pull` would hit local-change conflicts. They're also stale.
  2. `lean/AIEFProofs/.github/workflows/*` (template CI) never runs: GitHub only reads workflows from the repo-root `.github/workflows/`.

## 4. Builds (fresh sparse clone from GitHub, fresh Mathlib cache dir each time)
| Run | Result | Time |
|---|---|---|
| As committed: `lake exe cache get` + `lake build` | cache OK (8690 files); **build FAILS** in 1.2 s: `bad import 'AIEFProofs.ControllerFiberProjector'` | cache get 1m02s (`logs/10_baseline_as_committed.log`) |
| Fix (a), first script run | build PASS (1235 jobs, 0 warnings); markers 0 hits; axiom audit hit a bug in my generated Lean meta-code (fixed) | `logs/20_fix_a_check*` |
| Fix (a), corrected script | **PASS**: 26 project declarations audited, all ⊆ {propext, Classical.choice, Quot.sound} | `logs/21_*` |
| Fix (a), project `.lake/build` deleted → every project module recompiled from source | PASS (Basic, ControllerFiber, root rebuilt) | `logs/22_*`, `logs/23_*` |
| **Final end-to-end**: new clone → `git apply` 0001+0003 → `./check_lean.sh` | **PASS, exit 0, 1m23s wall** (cache 1235 jobs, 0 warnings, 0 markers, 26 decls clean) | `logs/50_final_end_to_end/` |
| Same with no Mathlib cache (`SKIP_CACHE=1`, builds the needed Mathlib slice from source) | PASS, 1243 jobs, 5m10s wall on this box | `logs/51_*` |
| Candidate projector module (option c′, see below) imported from root | PASS, 1236 jobs, 0 warnings, 48 decls clean | `logs/40_*`, `logs/41_*` |

`#print axioms` for every ControllerFiber theorem: `[propext, Classical.choice, Quot.sound]` (simp lemmas on literals: `[propext, Quot.sound]`). Full list: `logs/50_final_end_to_end/*/7_axioms.log` and `7_axioms_summary.txt`.

Negative tests (the checker must fail): `sorry` → exit 6; user `axiom` → 6; `native_decide` → 6; `sorryAx` via macro → 6; missing import → 3; type error → 5. Independently of the text scan, the semantic `collectAxioms` audit reports `myAx` and `sorryAx` and fails (`logs/30_negative_tests/`). Note: plain `lake build` **succeeds** with `sorry` (warning only); that's why the extra steps exist.

## 5. Fix options
* **(a) Remove the dangling import** — `0001-remove-dangling-ControllerFiberProjector-import.patch`. Tested; restores a green build with no change to any proof. **Recommended now.**
* **(b) Restore the file** — not possible from anything on GitHub or the box. Possible only if the owner finds it locally (§1).
* **(c) Write a stub with `sorry`** — rejected (would pass `lake build` but is not a proof).
* **(c′) Optional, new formalization (NOT a recovery):** `0002-OPTIONAL-candidate-ControllerFiberProjector-module.patch` (= `candidate/ControllerFiberProjector.candidate.lean`). Fully proved, no sorry: Euclidean `PEuc` and biorthogonal `QBi` over ℚ are idempotent (`PEuc` symmetric), `CCtrl * P = 0`, `P v = v`, and `CCtrl x = 0 ↔ P x = x`. Apply only if the owner wants this content; then keep the import (skip 0001), otherwise apply 0001.

## 6. Proposed file changes (repo-relative)
1. `lean/AIEFProofs/AIEFProofs.lean` — delete `import AIEFProofs.ControllerFiberProjector` (patch 0001), **or** add `lean/AIEFProofs/AIEFProofs/ControllerFiberProjector.lean` (patch 0002 / owner's local file).
2. Add `lean/AIEFProofs/check_lean.sh` (mode 755) and append `/.check_logs` to `lean/AIEFProofs/.gitignore` (patch 0003).
3. Add `.github/workflows/lean.yml` at repo root (patch 0003; also `workflow/lean.yml`). Uses SHA-pinned `actions/checkout` (v5), `leanprover/lean-action` v1.6.2 (Mathlib cache, build, built-in axiom audit with allow-list), then `check_lean.sh`, uploads logs as an artifact; `permissions: contents: read`. **Not yet run on GitHub** (would require pushing); YAML parses.
4. Owner decisions (not in patches): `git rm -r --cached lean/AIEFProofs/.lake` (recommended); import or delete `Smoke.lean`; delete/move the inert `lean/AIEFProofs/.github/`.

Apply locally: `git apply 0001-*.patch 0003-*.patch` (checked against `60e6029`: 0001, 0002, 0003 apply cleanly, separately or together).

## 7. Owner-side procedure (your machine)
One-time: install elan (`curl https://elan.lean-lang.org/elan-init.sh -sSf | sh -s -- -y --default-toolchain none`), plus `git`, `python3`, `curl`. Then:
```
git pull                       # or clone the repo
cd lean/AIEFProofs
./check_lean.sh                # exit 0 = PASS; otherwise exit code = failing step (1..7)
```
Logs: `lean/AIEFProofs/.check_logs/<UTC>/` (`summary.txt` first). Options: `SKIP_CACHE=1` (offline), `REUSE_BUILD=1` (don't recompile project modules), `STRICT_ORPHANS=1` (fail on unimported `.lean` files), `LOG_DIR=…`. First run downloads ~440 MB of Mathlib cache; `.lake` grows to ~7.5 GB. Steps: 1 toolchain pin, 2 Mathlib rev + lock-hash file, 3 import graph (missing = fail, orphan = warn), 4 `lake exe cache get`, 5 clean `lake build` (job count, warnings), 6 sorry/admit/axiom/native_decide/unsafe/extern scan (comments and strings stripped), 7 `Lean.collectAxioms` over every project declaration + `#print axioms` per theorem, then `source_sha256.txt`.
The same script runs on this box (it's how every result above was produced), and in CI if the root workflow is added.

## 8. Deliverables in this folder
`0001-…patch`, `0002-OPTIONAL-…patch`, `0003-…patch`, `check_lean.sh`, `workflow/lean.yml`, `candidate/ControllerFiberProjector.candidate.lean`, `logs/`, `SHA256SUMS`. The logs contain local scratch paths of this box; the patch, script, workflow and candidate files contain no personal or host-specific data.
(Repo copy: only this file is committed, under `AI Agent Audits/lean_recovery/`; the `logs/NN_*` referenced above stay in the investigation workspace, except the build logs listed in that folder's RESULTS.md.)
