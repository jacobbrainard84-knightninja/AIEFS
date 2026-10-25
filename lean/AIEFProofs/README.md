# AIEFProofs

A small Lean 4 / Mathlib project. It checks a few exact linear-algebra facts used by the AIEF
audit. All objects are fixed matrices over `ℚ`. **Nothing here formalizes the AIEF dynamics.**

## Build

From this directory (`lean/AIEFProofs`):

```
bash check_lean.sh
```

`check_lean.sh` is committed with its executable bit (mode 100755, commit `1a81cb6`), so `./check_lean.sh` also works.

`check_lean.sh` runs these steps and fails on the first error:

1. Toolchain pin.
2. Mathlib pin, plus `AIEF_LEAN_SOURCE_SHA256SUMS.txt`. The source hashes are verified, and an
   unlisted `.lean` file is an error.
3. Root imports and orphans. `STRICT_ORPHANS=1`, as set in CI, makes an orphan fatal.
4. `lake exe cache get`.
5. A clean `lake build`, with job and warning counts.
6. Forbidden markers: `sorry`, `admit`, `native_decide`, `axiom`, `unsafe`, `extern`, …
7. An axiom audit of every project declaration.

Logs go to `.check_logs/<UTC>/`, which is git-ignored. Useful variables are `SKIP_CACHE=1`,
`REUSE_BUILD=1` and `LOG_DIR=…`.

After an *intentional* source change, regenerate the hash file from this directory:

```
sha256sum AIEFProofs.lean $(find AIEFProofs -name '*.lean' | sort) check_lean.sh \
  > AIEF_LEAN_SOURCE_SHA256SUMS.txt
```

CI: `.github/workflows/lean.yml` at the repository root. The nested
`lean/AIEFProofs/.github/workflows/` files are the Mathlib project template, and GitHub never
runs them.

## Pins and allowed axioms

- Toolchain: `leanprover/lean4:v4.33.1` (`lean-toolchain`).
- Mathlib: tag `v4.33.1`, rev `0df444a360eaa60ab8c11dca51a86af692955474` (`lake-manifest.json`).
  The pin files are hashed in `AIEF_LEAN_PROJECT_LOCK_HASHES.txt`.
- Allowed axioms: `propext`, `Classical.choice`, `Quot.sound` only. Step 7 fails on anything
  else.

## What is proved

Here `CCtrl` is the 2×3 unsigned incidence of controller nodes `{2,7}` on the K3 edges
`((2,7),(2,11),(7,11))`, and `vCtrl = (1,−1,−1)`.

`ControllerFiber`
- `CCtrl · vCtrl = 0`, and `vCtrl ≠ 0`.
- `CCtrl · x = 0` ⇔ `x₀+x₁ = 0 ∧ x₀+x₂ = 0` ⇔ `x₁ = −x₀ ∧ x₂ = −x₀` ⇔ `x = a·vCtrl` for some `a`.
  So the kernel is exactly the line spanned by `vCtrl`.

`ControllerFiberProjector`
- Definitions: `PPar = (1/3)·vCtrl vCtrlᵀ` and `PPerp = I − PPar`.
- Both are entrywise symmetric. `PPar` is self-adjoint for the standard dot product.
- Both are idempotent, `PPar·PPerp = PPerp·PPar = 0`, and their images are orthogonal.
- `x = PPar x + PPerp x`, and the two images meet only at `0`.
- The range of `PPar` is exactly `ker CCtrl`.
- `CCtrl·PPerp x = CCtrl x`.
- `PPerp = SPerp ∘ CCtrl`, where `SPerp` is an explicit right inverse with `CCtrl·SPerp y = y`.

`ControllerFiberQuotient` (new)
- For all `x, y ∈ ℚ³` these are equivalent: `CCtrl x = CCtrl y`; `x − y = a·vCtrl` for some
  `a`; `PPerp x = PPerp y`; `PPar (x−y) = x−y`.
  The theorems are `CCtrl_eq_iff_exists_smul`, `CCtrl_eq_iff_PPerp_eq`,
  `PPerp_eq_iff_PPar_sub` and `controller_fiber_tfae`.

`CompleteGraphIncidence` (new)
- For any matrix `M` (n×m over ℚ) with a right inverse, `dim ker M = m − n` (rank–nullity).
- For the lexicographic edge lists of `K₃, K₄, K₅, K₆`:
  - `decide` certifies that each list contains every pair `i<j` exactly once.
  - An explicit right inverse of the unsigned incidence is verified.
  - Hence `dim ker = C(n,2) − n`, which is 0, 2, 5 and 9.
- K3:
  - The kernel is `{0}` (zero lineality).
  - For each node `c`, the ray `v_c` (`+1` on the edge opposite `c`, `−1` on the two edges at
    `c`) has row `c` of `inc·v_c` equal to `−2` and the other rows equal to `0`. So `−v_c` raises
    row `c` by 2.
  - `inc·v_c ≠ 0`.
  - Rows `{0,1}` of the K3 incidence are `CCtrl`, and `v_2 = vCtrl`.
- Smoke: two `ring` examples that check the Mathlib import. It has no declarations.

## What is NOT proved

The following are not formalized anywhere in this project.

Some come only from numerical runs: the audit's finite-difference and replay evidence.
- Engine v1 emits `CCtrl` (or any incidence above) as its controller matrix.
- Persistence of the controller branch or of the winner map.
- Delayed contraction, delay effects and multistability.
- EMA asymptotics, and the EMA rate `r_ema`.
- Invariance of the fiber under any dynamical operator `K`: `PPerp·K·PPar = 0` is not proved.
- The one-sided K3 result: that the gate's directional derivative along `+v_c` is
  `λ₂·v_c` and along `−v_c` is not slow.
- The clique multiplier `λ_k = (1−γdt)c/(c+dt(kη−γc)+ε)` and its conditions, and any `κ` value.
- The memory mechanism, and any statement about B, phase, history or EMA as memory.

Others are open problems.
- `dim ker = C(n,2) − n` for general `n ≥ 3` (only n = 3..6 are proved).
- A `LinearMap`/`Submodule` form `ker CCtrl = span ℚ {vCtrl}`.
- Real-valued versions of the statements above.
- Any link between the gate (`min(1, c/(q+ε))` scaling) and these matrices.

## Licence

The Lean sources are licensed under the Apache License 2.0 (repository-root `LICENSE`; see `LICENSING.md` and `NOTICE`). Copyright 2026 Jacob Brainard and AIEF contributors. Each project `.lean` file except `Basic.lean` and `Smoke.lean` carries the header and an `SPDX-License-Identifier: Apache-2.0` line.
