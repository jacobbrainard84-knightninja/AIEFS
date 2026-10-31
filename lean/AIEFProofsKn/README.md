# AIEFProofsKn — `dim ker = C(n,2) − n` for every `n ≥ 3`

A small Lean 4 project that generalizes `lean/AIEFProofs/AIEFProofs/CompleteGraphIncidence.lean`
(which proves the cases `n = 3, …, 6` one by one) to every `n ≥ 3`. Research branch
`research/lean-kn`, 2026-10-29. Not audited. Ledger row `LEAN-KN-01`; errata `ERRATA_2026-10-28.md` E11.

This is linear algebra of fixed matrices. It says nothing about which edges the AIEF dynamics keep,
that the capacity gate selects these kernels, or anything else about the dynamics.

## Why a separate project

`lean/AIEFProofs` is hash-pinned: `AIEFProofs.lean` (ART-0743 and the audit manifest), `lakefile.toml`
(ART-0750 and `AIEF_LEAN_PROJECT_LOCK_HASHES.txt`), `README.md` (ART-0748), and `check_lean.sh`
(listed in `AIEF_LEAN_SOURCE_SHA256SUMS.txt`). New modules under `lean/AIEFProofs/AIEFProofs/` would
have to be imported by the pinned root (otherwise `STRICT_ORPHANS=1` in CI fails), so they live here.
This project depends on `lean/AIEFProofs` as a Lake **path** dependency (`../AIEFProofs`) and imports
`AIEFProofs.CompleteGraphIncidence` unchanged. Nothing in `lean/AIEFProofs/` is edited, and its own
`check_lean.sh` still passes.

Same toolchain and Mathlib pin as the base project: `leanprover/lean4:v4.33.1`, Mathlib
`0df444a360eaa60ab8c11dca51a86af692955474` (`lake-manifest.json` is the base manifest plus the path entry).

## Main statements

All about the repository's own `inc`, `IsCompleteEdgeList` and `rinv` (namespace
`AIEFProofs.CompleteGraphIncidence`). For `src dst : Fin m → Fin n` with `IsCompleteEdgeList src dst`:

| theorem (namespace `AIEFProofs.CompleteGraphKn`) | statement |
|---|---|
| `inc_mulVecLin_surjective` | `n ≥ 3 →` `(inc src dst).mulVecLin` is surjective (full row rank `n`) over ℚ |
| `card_eq_choose_two` | `m = n.choose 2` |
| `finrank_ker_inc`, `finrank_ker_inc_eq_choose` | `n ≥ 3 →` `dim ker (inc src dst) = m − n = C(n,2) − n` |
| `finrank_ker_inc_eq_half` (+ `two_mul_choose_two_sub`, `choose_two_sub_eq`; module `KernelDimFormula`, added 2026-10-29 by the AIEFS merge-prep agent, not by Researcher 001, pending their audit) | `n ≥ 3 →` `dim ker (inc src dst) = n * (n − 3) / 2` in ℕ (exact: `2 * (C(n,2) − n) = n * (n − 3)`) |
| `inc_mul_rinv` | `n ≥ 3 →` `inc src dst * rinv src dst = 1` |
| `finrank_ker_K12_eq_54` | the lexicographic 12-node, 66-edge list: `dim ker = 54` |
| `finrank_ker_K3_general` … `finrank_ker_K6_general` | the repository's n = 3…6 values recovered from the general theorem |
| `not_surjective_char_two`, `exists_left_kernel_K2` | the hypotheses `char ≠ 2` and `n ≥ 3` cannot simply be dropped |

General graph lemmas (namespace `AIEFProofs.IncMatrixRank`, Mathlib `SimpleGraph` API):
`eq_zero_of_forall_adj_add_eq_zero`, `incMatrix_mulVecLin_surjective`, `rank_incMatrix`,
`edgeIncMatrix`, `finrank_ker_edgeIncMatrix` (`#E − #V`), `finrank_ker_edgeIncMatrix_top`
(`C(n,2) − n`). An explicit right inverse for `K_n` built from `(MMᵀ)⁻¹ = (1/(n−2))(I − J/(2(n−1)))`
is in `AIEFProofs.CompleteGraphRightInverse`.

## Scope of the hypotheses

- **Connected and non-bipartite is sufficient, not necessary.** Over a field of characteristic ≠ 2,
  the rank of the unsigned incidence matrix is `#V − (number of bipartite connected components)`. Only the
  connected non-bipartite case is proved here; `K_n` with `n ≥ 3` is such a graph.
- **Characteristic 2.** There the unsigned and signed incidence matrices coincide and the rank drops;
  for `K_3` over `ZMod 2` the map is not surjective (`not_surjective_char_two`).
- **Mathlib's `incMatrix` is `Sym2`-indexed.** `SimpleGraph.incMatrix K G : Matrix V (Sym2 V) K` has a
  column for every `s(a, b)`, including the diagonal `s(v, v)` and every non-edge, and those columns are
  zero. Its kernel is therefore larger (`finrank_ker_incMatrix_top`: `#Sym2 (Fin n) − n = C(n,2)` for `K_n`).
  The matching statement uses the edge-restricted `edgeIncMatrix : Matrix V G.edgeSet K`; the repository's
  `inc` already has one column per listed edge (`inc_apply_eq_incMatrix`).

## Build and check

From this directory, with elan installed:

```bash
lake exe cache get          # prebuilt Mathlib oleans (skip if .lake/packages is already populated)
lake build                  # builds ../AIEFProofs modules it imports, then AIEFProofsKn
./check_lean_kn.sh          # 7 steps; SKIP_CACHE=1 to skip `lake exe cache get`
```

`check_lean_kn.sh` is adapted from the pinned `../AIEFProofs/check_lean.sh` (not edited): toolchain pin;
Mathlib pin plus the base project's pins (`AIEF_LEAN_SOURCE_SHA256SUMS.txt`, `AIEF_LEAN_PROJECT_LOCK_HASHES.txt`)
plus this project's `AIEF_LEAN_KN_SOURCE_SHA256SUMS.txt`; imports with orphans fatal; cache; clean build
that fails on any warning; forbidden markers (`sorry`, `admit`, `native_decide`, user `axiom`, …); and an
axiom audit of every declaration in `AIEFProofsKn.*` modules (allowed: `propext`, `Classical.choice`,
`Quot.sound`). After an intentional source change, regenerate the hash file with the command in the
script header.

Local result (2026-10-29, `SKIP_CACHE=1`): 7/7 PASS, 1,879 build jobs, 0 warnings, 52 declarations
audited, standard axioms only.

`.github/workflows/lean.yml` (repository root) builds only `lean/AIEFProofs`. This project is not yet in
CI. A second job with `lake-package-directory: lean/AIEFProofsKn` and `./check_lean_kn.sh` as the check
step would add it; that has not been written or tested.

## Licence

Apache License 2.0 (repository-root `LICENSE`). Each `.lean` file carries the same header and
`SPDX-License-Identifier: Apache-2.0` line as the base project.
