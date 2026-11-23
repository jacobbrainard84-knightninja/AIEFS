# AIEFS_GateMutation — actual gate-form mutant

**Status:** prepared for owner deposit; not deposited or independently reviewed. Base main `7865ab19282ceae49df9aa70b396d60ada38d3c2`. Audit-inbox checked at `08e139bf33b3c52f8e2c01bc20114a329df85078`; DIRECTION-10 was the latest direction in the lead folder. No repository file or prior deposit was edited.

**GMT date:** session date 2026-09-11. UNEXPLAINED: the container clock read `2026-11-23 19:26:14 GMT`; the two dates conflict.

## Correction and objective

The earlier gate-form witness remains valid, but the two earlier checks described as mutants merely compared precomputed values. They did not alter the gate implementation and should **not** be counted as mutation evidence. This wave replaces that evidence with an actual changed formula and recomputed projections. It does not revise or delete the old deposit.

## Actual engine mutation — ran

A scratch copy of the exact base-main `aief_experiment_engine_v1.py` was changed at its sole occurrence of

```python
np.minimum.outer(scale, scale)
```

to

```python
np.multiply.outer(scale, scale)
```

The original engine SHA-256 was `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`; the changed scratch copy's SHA-256 was `975c8e2bff786aaa375f5762542421a127a9178aa91972d59c87c55d7b103c3f`. They were not included in this package; the mutation is fully specified above.

The **same test**, `engine_gate_checks.py`, imported and ran each implementation's `advance_state`, checked the full output matrix against a fixed min-gate oracle, and checked an inactive-branch negative control. Both used the same valid non-production configuration (`N=3`, `dt=τ=1`, `a=q=1`, `delta=0`, `eta=1`, `mu=gamma=0`, `T_window=10`, `scale_epsilon=1/4`). B starts at zero. A constructed finite coherence accumulator and phase history cause the update to produce the specified pre-projection matrix. `config.validate` and `state.validate` before and after the engine step passed for both implementations.

| Run | Active branch | Actual B₀₁ | Expected B₀₁ | Full-matrix oracle | Inactive control | Exit |
|---|---|---:|---:|---|---|---:|
| Unmodified engine | yes | 0.5714285714285714 | 0.5714285714285714 | PASS | PASS | 0 |
| Product-form engine mutant | yes | 0.38095238095238093 | 0.5714285714285714 | FAIL | PASS | 1 |

The mutated engine's maximum absolute full-matrix error was `0.19047619047619047`. The inactive control uses half the pre-projection matrix, triggers no capacity violation, and returns it unchanged in both runs. The active matrix is

```
[[0,   1,   1/2],
 [1,   0,   1/4],
 [1/2, 1/4, 0  ]]
```

The expected projected matrix is `[[0,4/7,2/7],[4/7,0,1/6],[2/7,1/6,0]]`. This is a controlled validator-accepted constructed state, **not** a claim of reachability from standard initialization or of production behavior. The float comparison uses absolute tolerance `1e-14` and zero relative tolerance. Python 3.13.18, NumPy 2.3.5. `engine_checks.log.txt` is the output.

## Exact recomputation — ran

`exact_gate_checks.py` implements the branch, recomputes scales and every projected entry using exact rational arithmetic, and passes either `min` or multiplication as the combining function to the **same** full-matrix test. The min implementation passes; the changed formula gives `B₀₁=8/21` instead of `4/7` and fails with exit 1. The inactive B/2 control passes both. This supports the numerical test but is not the project mutation suite or a Lean proof.

## Reproduction and scope

After obtaining the base engine under `$ENGINE_REF`, make a scratch copy `$ENGINE_MUTANT` with exactly the replacement above. From this folder:

```sh
python exact_gate_checks.py min       # expected exit 0
python exact_gate_checks.py product   # expected exit 1
python engine_gate_checks.py "$ENGINE_REF"     # expected exit 0
python engine_gate_checks.py "$ENGINE_MUTANT"  # expected exit 1
```

The results are included so intake need not run scripts. `SHA256SUMS.txt` pins the scripts, this note, and `.log.txt` output. No full project suite, independent review, broader normalization/rate-law conclusion, or claim promotion is asserted. The optional C012 finite-sum equivalence was not attempted in this cycle.
