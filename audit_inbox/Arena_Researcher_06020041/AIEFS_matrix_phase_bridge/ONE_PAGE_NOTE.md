# Fixed-matrix phase bridge and exact counterexamples

**Session date:** 2026-09-11, Atlantic/Reykjavik. **Date conflict:** the relayed lead note is dated 2026-11-20, Europe/Tirane. Reconcile the project filing date and filename before upload; do not silently carry forward earlier dates.

**Status:** locally kernel-checked, unreviewed research candidate based on main `0a6a2f62ea9af147cac60a7be30d85d6b37fe52a`; no project files changed. The only project import is main's `AIEFGateCore.EngineStepRef`. This is a fixed-post-update-weight model, not a proof of the adaptive engine derivative.

## Results

For a supplied matrix W, the reference head is

`x⁺₀(i)=x₀(i)+dt[ω+∑ⱼ Wᵢⱼ sin(x_d(j)−x₀(i))]`.

Lean proves: (1) if W has zero diagonal and all off-diagonal entries are the same b≥0, this head equals main `EngineStepRef.phaseHead`; (2) under d>0 and theta/newest-history equality modulo 2π, an abstract engine-shaped step's retained history agrees on `Real.Angle` with the **matrix** reference, without a uniformity assumption; and (3) at a synchronized rotating history its directional head derivative, with W held fixed, is

`v₀(i)+dt∑ⱼ Wᵢⱼ cos(d·dt·Ω)[v_d(j)−v₀(i)]`.

The derivative and circle statements are actually proved for arbitrary real W, not just symmetric or zero-diagonal matrices. For interpreting W as the engine's post-update weights, zero diagonal and any other branch/physical conditions remain separate assumptions. The synchronized history need not be an orbit for a nonuniform W; e.g. unequal row sums generally produce unequal phase advances. The theorem does not assert orbit existence.

**Exact Lean witnesses:** for N=3, symmetric zero-diagonal edge weights 1,2,3 have mean 2; with one delayed phase π/2, the node-0 matrix head is 1 while the scalar mean-weight head is 2. A separate theorem gives an inconsistent theta/newest-history input whose k=1 output differs on `Real.Angle` from main's `phaseStep`. Direct definition-level examples check an unequal-adjacent-history shift and a delayed sine input. These are exact probes, not mutation-suite results.

## Scope and source correspondence

The matrix W is supplied **after** clipping, symmetrization and any capacity projection. This model neither performs nor proves anything about those operations, and W does not vary along the differentiated path. The code comments cite `aief_experiment_engine_v1.py` at the base SHA, particularly lines 823, 830–839 and 841–844. Circle wrapping is the mathematical exact-real `toIcoMod`, not an IEEE/NumPy proof. The abstract state/list relation, actual engine branch values and derivative contributions from varying W remain unproved. No full Fréchet theorem, adaptive network stability, transient bound, or production behavior is claimed. No definitionally true initialization/consistency lemmas are presented as results.

## Verification

Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: targeted build passed **2,191 jobs without warnings**; seven new axiom reports show only `propext`, `Classical.choice`, `Quot.sound`. Both direct examples compiled. Earlier attempts failed on concrete Fin simplification; final proofs were rebuilt. No `sorry`, new axiom, full project gate or mutation-suite run.

```sh
# From the directory containing MatrixPhaseBridge.lean; REPO is the base checkout.
cp MatrixPhaseBridge.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.MatrixPhaseBridge
```

`LOG_HASHES.txt` pins the source and final log. Main advanced during work to `d7b9fac600686477babf229ede70a19f1c2dfa13` and inbox to `b84f54d861524ed27d424c7b410f91d1fbe5166a`; the engine and `EngineStepRef.lean` bytes at those two main SHAs match, but the new head was **not** built or fully audited. No independent review, push, claim promotion or project mutation/guard/CI changes.
