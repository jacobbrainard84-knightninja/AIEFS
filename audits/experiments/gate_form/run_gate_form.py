#!/usr/bin/env python3
"""Three-way comparison of capacity-enforcement rules on the AIEF model.

THE QUESTION
------------
Round 8 flagged that AUD-GATE calls the capacity gate "node-strength
multiplicative normalisation". Round 9 read the implementation:

    scale = np.minimum(1.0, cap / (row_sum_pre + ZERO_TOL))
    B *= np.minimum.outer(scale, scale)

and concluded from the code that each EDGE is scaled by the minimum of two
node-specific factors, so this is not Miller & MacKay's (LIT-0043)
multiplicative enforcement -- which applies ONE GLOBAL factor -- and therefore
their convergence theorem does not apply.

That conclusion was reached by reading. This script tests it.

PART A -- EXACT, NO SIMULATION
------------------------------
Miller & MacKay's multiplicative case rescales the whole weight matrix by a
single factor. Direction preservation is what makes their result a statement
about the principal eigenvector. So: does each rule preserve the direction of
B in weight space? This is a property of the map and is settled exactly.

PART B -- INDICATIVE, SIMULATION
--------------------------------
Run the actual AIEF dynamics (ETA, GAMMA, MU, delay, EMA-of-delay-compensated-
phasor driver) swapping ONLY the enforcement rule, and compare which attractor
each selects.

SCOPE AND HONESTY
-----------------
This is a MINIMAL REPLICA, not the AIEF engine:
  * pure Python, stdlib only (numpy is not installed in this environment);
  * T_SIM reduced from 800 to 200 for runtime -- the real engine runs 80,000 steps;
  * full all-to-all support, not the hypergraph the repository uses.
Part A's result does not depend on any of that, because it is a statement about
the rescaling map. Part B's result is indicative and must not be quoted as a
measurement of the AIEF attractor.

Constants are copied from AIEF_1_3_falsification_updated.py lines 51-88.
"""

from __future__ import annotations

import json
import math
import pathlib
import random
from collections import deque

HERE = pathlib.Path(__file__).resolve().parent

# ---- constants copied verbatim from AIEF_1_3_falsification_updated.py -------
N = 12
T_SIM = 200.0          # real: 800.0, reduced for runtime (see docstring)
DT = 0.01
TAU = 0.5
OMEGA = [1.00, 1.02, 1.50, 2.00, 2.01, 1.01,
         1.03, 1.51, 2.02, 2.00, 1.00, 1.04]
A = 1.0
Q = 1.5
DELTA = 0.05
ETA = 0.04
GAMMA = 0.015
MU = 0.03
T_WINDOW = 25.0 / (sum(OMEGA) / len(OMEGA))
B_C = 0.12
B_INIT_SCALE = 0.0005
ZERO_TOL = 1e-12

CAP = (A - DELTA) / Q
ALPHA = math.exp(-DT / T_WINDOW)
DELAY_STEPS = int(round(TAU / DT))
N_STEPS = int(round(T_SIM / DT))


# ============================ Part A: the maps ==============================

def row_sums(B):
    return [sum(row) for row in B]


def max_row_sum(B):
    return max(row_sums(B))


def enforce_global_multiplicative(B, cap):
    """Miller & MacKay multiplicative: ONE factor for the whole matrix.

    Rescale so the most-violating row meets the cap; every other row is then
    below it. This is exactly 'multiply the weight vector by a common factor',
    which is what preserves direction and what their theorem is about.
    """
    m = max_row_sum(B)
    if m <= cap:
        return [row[:] for row in B], 1.0
    f = cap / m
    return [[v * f for v in row] for row in B], f


def enforce_subtractive(B, cap):
    """Miller & MacKay subtractive: subtract a common constant, floor at 0.

    Symmetric by construction (a single `a` for all edges), so the only thing
    varying between the three rules is the enforcement geometry.
    """
    if max_row_sum(B) <= cap:
        return [row[:] for row in B], 0.0
    lo, hi = 0.0, max(max(r) for r in B)
    for _ in range(200):
        a = 0.5 * (lo + hi)
        trial = [[max(v - a, 0.0) for v in row] for row in B]
        if max_row_sum(trial) <= cap:
            hi = a
        else:
            lo = a
    a = hi
    return [[max(v - a, 0.0) for v in row] for row in B], a


def enforce_aief(B, cap):
    """The AIEF gate, verbatim: per-edge min of two node factors."""
    rs = row_sums(B)
    if max(rs) <= cap:
        return [row[:] for row in B], 1.0
    scale = [min(1.0, cap / (s + ZERO_TOL)) for s in rs]
    out = [[B[i][j] * min(scale[i], scale[j]) for j in range(N)] for i in range(N)]
    return out, scale


RULES = {
    "global_multiplicative": enforce_global_multiplicative,
    "subtractive": enforce_subtractive,
    "aief_per_edge_cap": enforce_aief,
}


def flat(B):
    return [B[i][j] for i in range(len(B)) for j in range(len(B))]


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def direction_residual(B0, B1):
    """sin of the angle between vec(B0) and vec(B1) -- 0 iff exactly proportional.

    This is the quantity that decides whether a principal-eigenvector argument
    can transfer. Computed as the relative residual of the best positive scaling
    rather than via a dot product, so it is well conditioned.
    """
    a, b = flat(B0), flat(B1)
    nb = norm(b)
    if nb == 0.0:
        return 0.0
    d = sum(x * y for x, y in zip(a, b))
    nn = sum(x * x for x in a)
    lam = max(d / nn, 0.0) if nn > 0 else 0.0
    return norm([y - lam * x for x, y in zip(a, b)]) / nb


def distinct_factors(B0, B1):
    """How many distinct per-edge scale factors were applied."""
    a, b = flat(B0), flat(B1)
    seen = set()
    for x, y in zip(a, b):
        if x > 1e-15:
            seen.add(round(y / x, 10))
    return len(seen)


def run_part_a(trials=200, seed=20261031):
    rng = random.Random(seed)
    out = {}
    for name, rule in RULES.items():
        res, fac = [], []
        feasible = True
        for _ in range(trials):
            # a symmetric, non-negative matrix with a row-sum violation
            B = [[0.0] * N for _ in range(N)]
            for i in range(N):
                for j in range(i + 1, N):
                    v = rng.random() * 0.9
                    B[i][j] = B[j][i] = v
            if max_row_sum(B) <= CAP:
                B = [[v * 3.0 for v in row] for row in B]
            B1, _ = rule(B, CAP)
            if max_row_sum(B1) > CAP + 1e-9:
                feasible = False
            res.append(direction_residual(B, B1))
            fac.append(distinct_factors(B, B1))
        res.sort()
        fac_sorted = sorted(fac)
        out[name] = {
            "direction_residual_median": median(res),
            "direction_residual_max": res[-1],
            "direction_residual_min": res[0],
            # number of DISTINCT PER-EDGE SCALE FACTORS applied, per trial
            "distinct_scale_factors_median": int(median(fac_sorted)),
            "distinct_scale_factors_min": fac_sorted[0],
            "distinct_scale_factors_max": fac_sorted[-1],
            "constraint_satisfied_after": feasible,
            "exactly_proportional_trials": sum(1 for r in res if r < 1e-12),
            "trials": trials,
        }
    return out


def median(xs):
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


# ========================== Part B: the dynamics ============================

def run_dynamics(rule_name: str, seed: int) -> dict:
    """One AIEF trajectory with the enforcement rule swapped."""
    rule = RULES[rule_name]
    rng = random.Random(seed)

    theta = [rng.random() * 2.0 * math.pi for _ in range(N)]
    B = [[B_INIT_SCALE * rng.random() for _ in range(N)] for _ in range(N)]
    B = [[0.5 * (B[i][j] + B[j][i]) if i != j else 0.0 for j in range(N)] for i in range(N)]

    cre = [[0.0] * N for _ in range(N)]
    cim = [[0.0] * N for _ in range(N)]
    history = deque((theta[:] for _ in range(DELAY_STEPS + 1)), maxlen=DELAY_STEPS + 1)

    gate_steps = 0
    gate_norm_max = 0.0
    ones = 1.0 - ALPHA
    half_tau = 0.5 * TAU

    for _ in range(N_STEPS):
        delayed = history[0]

        # --- R: EMA of the delay-compensated phasor (compute_R verbatim) ---
        for i in range(N):
            ti = theta[i]
            wi = OMEGA[i]
            cr, ci = cre[i], cim[i]
            for j in range(N):
                dphi = ti - delayed[j] - (wi + OMEGA[j]) * half_tau
                cr[j] = ALPHA * cr[j] + ones * math.cos(dphi)
                ci[j] = ALPHA * ci[j] + ones * math.sin(dphi)
        R = [[math.hypot(cre[i][j], cim[i][j]) for j in range(N)] for i in range(N)]

        # --- Hebbian update (line 433-435 verbatim) ---
        coef = ETA + MU
        for i in range(N):
            Bi = B[i]
            Ri = R[i]
            for j in range(N):
                v = Bi[j] + DT * (coef * Ri[j] - MU - GAMMA * Bi[j])
                Bi[j] = v if v > 0.0 else 0.0
        for i in range(N):
            for j in range(i + 1, N):
                s = 0.5 * (B[i][j] + B[j][i])
                B[i][j] = B[j][i] = s
            B[i][i] = 0.0

        # --- capacity enforcement (the only thing that differs) ---
        if max_row_sum(B) > CAP:
            B_before = [row[:] for row in B]
            B, _ = rule(B, CAP)
            for i in range(N):
                B[i][i] = 0.0
            gate_steps += 1
            gate_norm_max = max(gate_norm_max, norm(
                [B[i][j] - B_before[i][j] for i in range(N) for j in range(N)]))

        # --- phase update (line 477-481 verbatim) ---
        new_theta = []
        for i in range(N):
            coupling = 0.0
            Bi = B[i]
            for j in range(N):
                coupling += Bi[j] * math.sin(delayed[j] - theta[i])
            new_theta.append((theta[i] + DT * (OMEGA[i] + coupling)) % (2.0 * math.pi))
        theta = new_theta
        history.append(theta[:])

    # --- final-state measures ---
    zr = sum(math.cos(t) for t in theta) / N
    zi = sum(math.sin(t) for t in theta) / N
    order = math.hypot(zr, zi)
    labels, seen = [], 0
    assign = [-1] * N
    for i in range(N):
        if assign[i] >= 0:
            continue
        assign[i] = seen
        for j in range(i + 1, N):
            if assign[j] < 0:
                d = abs(theta[i] - theta[j]) % (2.0 * math.pi)
                if min(d, 2.0 * math.pi - d) < 0.15:
                    assign[j] = seen
        seen += 1
    labels = sorted(assign)

    return {
        "rule": rule_name,
        "seed": seed,
        "order_parameter": round(order, 6),
        "n_clusters": seen,
        "final_theta": [round(t, 6) for t in theta],
        "cluster_partition": labels,
        "gate_active_steps": gate_steps,
        "gate_max_change_frobenius": round(gate_norm_max, 9),
        "final_max_row_sum": round(max_row_sum(B), 9),
        "final_B": [[round(B[i][j], 8) for j in range(N)] for i in range(N)],
    }


def matrix_gap(B1, B2):
    a, b = flat(B1), flat(B2)
    d = norm([x - y for x, y in zip(a, b)])
    s = max(norm(a), norm(b))
    return d / s if s > 0 else 0.0


def main() -> None:
    print(f"cap = (A-DELTA)/Q = {CAP:.6f}   ALPHA = {ALPHA:.8f}")
    print(f"T_SIM {T_SIM} (real 800) -> {N_STEPS} steps, N = {N}\n")

    part_a = run_part_a()
    print("PART A -- direction preservation under capacity enforcement")
    print(f"{'rule':24s} {'median sin(theta)':>18s} {'exact prop.':>12s} "
          f"{'factors/edge':>12s} {'cap ok':>7s}")
    for name in RULES:
        r = part_a[name]
        print(f"{name:24s} {r['direction_residual_median']:18.3e} "
              f"{r['exactly_proportional_trials']:>7d}/{r['trials']:<4d} "
              f"{r['distinct_scale_factors_median']:>12d} "
              f"{str(r['constraint_satisfied_after']):>7s}")

    seeds = [11, 22, 33]
    runs = []
    print("\nPART B -- AIEF dynamics, enforcement rule swapped, everything else fixed")
    for seed in seeds:
        for name in RULES:
            r = run_dynamics(name, seed)
            runs.append(r)
            print(f"  seed {seed}  {name:22s} r={r['order_parameter']:.4f} "
                  f"clusters={r['n_clusters']:2d} gate_steps={r['gate_active_steps']:5d} "
                  f"maxrow={r['final_max_row_sum']:.6f}")

    pairs = {}
    for seed in seeds:
        by = {r["rule"]: r for r in runs if r["seed"] == seed}
        for a, b in (("global_multiplicative", "subtractive"),
                     ("global_multiplicative", "aief_per_edge_cap"),
                     ("subtractive", "aief_per_edge_cap")):
            key = f"{a} vs {b}"
            pairs.setdefault(key, []).append({
                "seed": seed,
                "relative_B_gap": round(matrix_gap(by[a]["final_B"], by[b]["final_B"]), 6),
                "same_partition": by[a]["cluster_partition"] == by[b]["cluster_partition"],
                "order_parameter_diff": round(abs(by[a]["order_parameter"] - by[b]["order_parameter"]), 6),
            })

    print("\n  pairwise divergence of selected states")
    for key, vals in pairs.items():
        gaps = [v["relative_B_gap"] for v in vals]
        same = sum(1 for v in vals if v["same_partition"])
        print(f"    {key:44s} B gap median {median(sorted(gaps)):.4f}  "
              f"same partition {same}/{len(vals)}")

    # Does any rule consistently select the most (or least) synchronized state?
    ranking = {}
    for name in RULES:
        rs = [r["order_parameter"] for r in runs if r["rule"] == name]
        ranking[name] = {
            "order_parameters": rs,
            "mean": round(sum(rs) / len(rs), 6),
            "rank_per_seed": [
                sorted(RULES, key=lambda n: -next(
                    r["order_parameter"] for r in runs if r["rule"] == n and r["seed"] == s)
                ).index(name) + 1
                for s in seeds
            ],
        }
    consistent = any(set(v["rank_per_seed"]) == {1} for v in ranking.values())
    parts_same = sum(1 for v in pairs.values() for e in v if e["same_partition"])
    parts_total = sum(len(v) for v in pairs.values())

    out = {
        "generated": "2026-10-31",
        "purpose": (
            "Test whether the AIEF capacity gate is multiplicative in Miller & MacKay's "
            "(LIT-0043) sense, and whether their convergence theorem can apply to it."),
        "scope": (
            "Minimal replica, pure Python. Part A is exact (a property of the rescaling map). "
            "Part B is INDICATIVE ONLY: T_SIM reduced 800 -> 200, full support not hypergraph. "
            "Part B must not be quoted as a measurement of the AIEF attractor."),
        "constants": {"N": N, "T_SIM": T_SIM, "DT": DT, "TAU": TAU, "A": A, "Q": Q,
                      "DELTA": DELTA, "ETA": ETA, "GAMMA": GAMMA, "MU": MU,
                      "T_WINDOW": T_WINDOW, "CAP": CAP, "ALPHA": ALPHA},
        "part_a_direction_preservation": part_a,
        "part_b_runs": runs,
        "part_b_pairwise": pairs,
        "part_b_ranking": ranking,
        "part_b_ordering_consistent": consistent,
        "part_b_partition_agreement": f"{parts_same}/{parts_total}",
    }
    (HERE / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("\n  does any rule consistently select the most synchronized state?")
    for name, v in ranking.items():
        print(f"    {name:24s} mean r={v['mean']:.4f}  rank per seed {v['rank_per_seed']}")
    print(f"    -> any rule ranked first in every seed: {consistent}")
    print(f"    -> pairwise cluster partitions identical: {parts_same}/{parts_total}")
    print(f"\nwrote {HERE / 'results.json'}")


if __name__ == "__main__":
    main()
