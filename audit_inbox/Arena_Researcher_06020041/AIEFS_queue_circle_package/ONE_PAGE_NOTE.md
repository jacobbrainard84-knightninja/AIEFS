# Queue-to-circle phase bridge and a nonuniform N=3 check

**Status:** locally kernel-checked abstract bridge plus finite Python-engine checks; not independently reviewed, wired or an adaptive-engine derivative theorem. One Lean file imports main's `AIEFGateCore.EngineStepRef` directly, with no unmerged dependencies. This addresses the review of the earlier N=2-only queue check.

## N=3 actual-engine checks

`check_engine_n3.py` runs one step with N=3, d=1, dt=0.1, homogeneous ω=0, eta=mu=gamma=0, consistent history and no shuffle. With symmetric zero-diagonal weights the update preserves B; both examples have strict capacity slack. The scalar reference is evaluated with the **mean off-diagonal weight** of the actual matrix.

| Post-update weights | Max engine vs weighted formula | Max engine vs scalar reference |
|---|---:|---:|
| All off-diagonals 0.1 | 0 | 0 radians |
| Edges 0.05, 0.10, 0.20 | 0 | **0.00668114265541 radians** |

These float64 cases show why uniformity matters for this example; they do not prove every nonuniform case differs. The numbers are circular principal-angle errors, not coordinate differences across the 2π cut. The engine source bytes have SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede` and match main `8b49f15407ec76c5701476c7caf035ee03e827d2`. The script is evidence, not a substitute for the mathematical argument.

## Lean statement

`QueueCircleBridge.lean` defines an **abstract engine-shaped** exact-real state containing separate current theta and newest-first history, an arbitrary supplied **post-update** weight matrix B, a sine phase update, reduction to `[0,2π)`, and an append/shift. It proves:

1. Initialization with every history entry equal to theta is consistent on `Real.Angle = ℝ/(2πℤ)`; every abstract step outputs consistent theta/newest history, even from an inconsistent input.
2. If d>0, the input is consistent modulo 2π, B has zero diagonal and uniform off-diagonal b≥0, then for each retained k≤d and node i the output history on `Real.Angle` equals main `EngineStepRef.phaseStep` applied to the appropriate input lifts. The head is separately proved equal as a real expression before wrapping.

Source comments map the assumptions/operations to the pinned engine: separate theta and history lines 582–598, initialization 699–713, weight symmetrization and diagonal erasure 795–797 and post-update assignment 823, phase 830–839, and queue 841–844. In particular the engine's validator at lines 613–680 does not enforce input consistency. The abstract step's weights are **supplied**, not derived from the EMA, clipping, symmetrization or gate. The input lift uses theta at index 0 and history at positive indices; k=1 is exactly where consistency is needed.

`Real.Angle` is the mathematical circle and `toIcoMod` is exact-real wrapping, not literal NumPy float modulo. Equality of the abstract function to the actual Python transition and its finite list semantics is not machine-proved. The result is a **pointwise conditional** bridge: it cannot be differentiated as an adaptive-engine identity without controlling how post-update B changes under perturbations. It proves no full Fréchet derivative, nonlinear stability, heterogeneous-frequency result, or production attraction.

## Evidence and reproducibility

On sparse main `8b49f15407ec76c5701476c7caf035ee03e827d2`, Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: final targeted build passed **2,191 jobs without warnings**; four new theorem axiom reports contain only `propext`, `Classical.choice`, `Quot.sound`. First build failed because `initialize` is a Lean keyword; the definition was renamed and rebuilt. The N=3 script passed with NumPy 2.3.5 (`check.log`). Neither the full gate nor mutation suite was run; mutation proposals are separate.

```sh
# From this package directory; REPO is the cited main checkout.
cp QueueCircleBridge.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.QueueCircleBridge
# Separately, with the pinned engine at ../AIEFS/:
# OPENBLAS_NUM_THREADS=1 python check_engine_n3.py
```

`LOG_HASHES.txt` pins the source and logs. Inbox was `0c2155cb240a93cc09e85119e4770902a2f70d15`. No project guard, root import, inventory, pinned repository hash file or mutation script was changed; no independent review, push or claim promotion.
