# AIEFS_TransientPlan — one-step delay-coordinate amplification

**Status:** prepared for owner deposit; seat approval or redirection requested before proofs. Base main `7865ab19282ceae49df9aa70b396d60ada38d3c2`; inbox checked at `1d507588f5a3867b4ad4fb84b0351b23bcd30494`. Folder label from `date -u +%F`; container clock reported `2026-11-23 21:26:04 GMT`.

## Falsifiable question

In the exact-real, fixed-weight phase/history **linearization**, can a stable mean-zero mode have one-step Euclidean amplification? Specifically: N=3, delay d=1, dt=1/4, symmetric zero-diagonal weights b=1, synchronized phase 1, Ω=ω=0. Let current perturbation be `(1,−1,0)` and delayed perturbation `(0,0,0)`. Does the full six-coordinate phase/history perturbation grow in squared Euclidean norm from 2 to 5/2, although the eigenvalues of its mean-zero two-slot mode have modulus 1/2? The full phase system also has a neutral common-phase mode; no claim is made that its entire spectrum is strictly stable.

## Source and formalization targets — read, not yet proved

Main engine `aief_experiment_engine_v1.py`: weight update/clip/symmetrize and capacity decision L790–813; phase update reads oldest history L830–839; append/pop L841–844. With η=μ=γ=0, fixed b=1 and capacity strictly above row sum 2, the intended comparison is the inactive-gate fixed-weight branch. This is a proposed source correspondence, **not** a Python-refinement or floating-point claim.

Main `AIEFGateCore.EngineStepRef`: `head_derivative_block` and `history_derivative` for the uniform fixed-weight phase and queue; `AIEFGateCore.DelayRoots` is a possible stability cross-check. Earlier candidate `MatrixPhaseBridge` and `QueueComposition` are inbox dependencies, **not main modules**; use only if needed and identify them explicitly. Do not import held cycles or change engine/CI.

## Smallest witness and mutant — proposed, not run

Use the mean-zero two-slot matrix `A=[[1/2,−1/4],[1,0]]`. Prove exact squared-norm growth for input `(1,0)` and that its two complex eigenvalues `(1±i√3)/4` have norm 1/2. Link this matrix to the `EngineStepRef` directional head and history shift under the stated uniform-weight hypotheses; if the link cannot be proved, report the matrix witness as a stipulated model only. Mutate the queue shift from retaining the previous current perturbation to zero: the same squared-norm witness must fail. No Lean will be written until the seat approves or redirects this plan.

## Ran / limits / negative result

Read the cited base engine and checked its SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede` using `curl -fsSL https://raw.githubusercontent.com/jacobbrainard84-knightninja/AIEFS/7865ab19282ceae49df9aa70b396d60ada38d3c2/aief_experiment_engine_v1.py | sha256sum`. Ran the rational arithmetic check below; output: input squared norm `2`, output squared norm `5/2`, gain squared `5/4`. It checks the proposed vector arithmetic, not the derivative or eigenvalues:

```sh
python -c 'from fractions import Fraction as F; x=(1,-1,0); h=F(1,4); a=sum(v*v for v in x); b=sum(((1-2*h)*v)**2 for v in x)+a; print(a,b,b/a)'
```

If the proposed Lean witness or engine-shaped linkage fails, identify the failed assumption or counterexample and withdraw the stated instance; that alone would not rule out other norms, initial perturbations, delay lengths, or transient amplification elsewhere. No nonlinear, adaptive, production, or global stability conclusion is intended.
