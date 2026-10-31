# Is the capacity gate "multiplicative"? — an exact test

**Date:** 2026-10-31 · **Script:** [`run_gate_form.py`](run_gate_form.py) · **Data:** [`results.json`](results.json)
**Question from:** literature rounds 8 and 9 · **Answer:** no, and the difference is measurable

---

## The question

`AUD-GATE` states: *"The capacity gate `s_i = min(1, c/(q_i+eps))` is node-strength multiplicative
normalisation."*

Miller & MacKay (1994), *The Role of Constraints in Hebbian Learning*, compare two ways of enforcing a
weight constraint:

- **multiplicative** — rescale the whole weight vector by **one common factor**. Their result: the
  dynamics converge to the principal eigenvector of the unconstrained operator.
- **subtractive** — subtract a constant. Their result: almost every weight ends at a bound.

The AIEF gate is:

```python
scale = np.minimum(1.0, cap / (row_sum_pre + ZERO_TOL))
B *= np.minimum.outer(scale, scale)
```

Each edge is multiplied by the **minimum of two node-specific factors**. Round 9 concluded from
reading that this is neither of the two methods, so Miller & MacKay's theorem cannot apply. This
script measures whether that is true.

---

## Part A — exact, no simulation

Direction preservation is *the* property that makes Miller & MacKay's argument work: their theorem is
a statement about which vector the dynamics converge to, and a rule that preserves direction only
rescales the answer. So: apply each rule to 200 random symmetric non-negative matrices with a row-sum
violation, and measure the angle between `vec(B)` and `vec(B')`.

Reported as `sin θ`, the relative residual of the best positive scaling. **Zero means exactly
proportional.**

| rule | distinct per-edge factors | `sin θ` median | `sin θ` max | exactly proportional |
|---|---:|---:|---:|---:|
| global multiplicative | **1** | `3.1e-16` | `1.2e-15` | **200 / 200** |
| AIEF per-edge cap | **11** | `1.0e-01` | `2.0e-01` | **0 / 200** |
| subtractive | 11–27 (median 17) | `7.2e-01` | `8.0e-01` | **0 / 200** |

All three satisfy the capacity constraint afterwards (`cap_ok = True` in every trial), so the
comparison is fair — the rules differ only in *how* they restore feasibility.

**The result is unambiguous.** The global rule applies one factor and is proportional to machine
precision (residual at `1e-15`, i.e. floating-point zero). The AIEF gate applies eleven distinct
factors and lands ~6° away in weight space. The subtractive rule lands ~46° away.

Eleven distinct factors for twelve nodes is what the `min` form predicts: the scale values are
per-node, and taking `min` across symmetric edges collapses them to essentially one value per node.

**So `AUD-GATE`'s sentence is false as a statement about Miller & MacKay's term.** The gate does
multiply (it is not additive), and the factor does come from node strength, but it is not *a* factor —
and the single-factor property is exactly what their convergence theorem rests on.

---

## Part B — simulation (indicative, not a measurement of AIEF)

Same dynamics, same seed, same ω, same delay — **only the enforcement rule swapped**. 12 nodes,
20,000 steps, 3 seeds.

| seed | global multiplicative | subtractive | AIEF per-edge cap |
|---|---:|---:|---:|
| 11 | r = 0.602, 3 clusters | r = 0.308, 4 clusters | **r = 0.977**, 3 clusters |
| 22 | r = 0.276, 4 clusters | **r = 0.638**, 6 clusters | r = 0.541, 3 clusters |
| 33 | r = 0.517, 4 clusters | r = 0.662, 4 clusters | **r = 0.679**, 4 clusters |

Pairwise divergence of the selected coupling matrices: relative Frobenius gap **0.60–0.73**. Cluster
partitions identical in only **3 of 9** pairwise comparisons.

**Two honest readings, and one thing this does not show.**

1. **The rules are distinguishable.** Different final `B`, different cluster structure in six of nine
   comparisons. The enforcement geometry reaches the attractor.
2. **The rules are not orderable.** Every rule is the most synchronized in at least one seed
   (`global`: never first; `subtractive`: seed 22; `per-edge`: seeds 11 and 33). Mean `r` is
   0.73 / 0.54 / 0.47 for per-edge / subtractive / global, but with ranks `[1,2,1]` for the per-edge
   rule, three seeds are not enough to claim an ordering. **Do not quote the mean.**
3. **This does not measure the AIEF attractor.** `T_SIM` is 200 here versus 800 in the engine, support
   is all-to-all rather than the repository's hypergraph, and this is a 12-node pure-Python replica.
   Part A survives all of that because it is a property of the map; Part B does not.

A useful sanity check appeared on its own: the gate binds on **17,744–17,784 of 20,000 steps**
(89%), and the final maximum row sum equals `cap = 0.633333` exactly for every rule. The constraint
is active almost always, not occasionally — so the enforcement geometry is not a corner case in these
runs.

---

## What this establishes, and what it does not

**Established:** the AIEF capacity gate is not multiplicative in Miller & MacKay's sense, and
Miller & MacKay's convergence theorem therefore does not apply to it. This is now measured
(200/200 vs 0/200), not inferred.

**Established:** swapping the enforcement rule changes the selected state in this model.

**Not established:** that the AIEF engine's attractors differ under the three rules. That needs the
real engine, full `T_SIM`, and the hypergraph — an engineering task, not a replica's job.

**Not established:** any ordering of synchronization strength across rules.

---

## Reproduce

```bash
python3 audits/experiments/gate_form/run_gate_form.py
```

Pure Python standard library — no numpy, no network, no randomness beyond fixed seeds. Runtime ~3.5
minutes on one core. Deterministic: the same command reproduces `results.json` byte-for-byte, and the
script's constants are copied with their line numbers from
`AIEF_1_3_falsification_updated.py` (lines 51–88).
