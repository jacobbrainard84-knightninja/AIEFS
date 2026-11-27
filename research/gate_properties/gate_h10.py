"""H10: gate property checks against an independent exact Fraction oracle (stdlib + numpy only; no new dependency).

The oracle is written from the SPEC/control flow, not imported from the engine: projection runs only if
`pre_violation` (min_i (a - q*rowsum_i) < delta); then s_i = min(1, cap/(rowsum_i + eps)), cap = (a - delta)/q,
B'_ij = min(s_i, s_j) * B_ij, zero diagonal. The float side is a verbatim COPY of the engine's projection block,
extracted at run time from the SHA-locked engine file (never imported, never edited) and checked against the pin.

Mutants M500-M506 and the equivalence control E500 are applied textually to the copy; their predeclared outcomes are
in PREDECLARED (committed before the first run). A mutant is KILLED iff at least one property fails on it.
"""
import hashlib
import random
import textwrap
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace

import numpy as np

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "aief_experiment_engine_v1.py"
ENGINE_SHA256 = "ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede"
BLOCK_START = "    # Check gap constraint\n"
BLOCK_END = "        raise RuntimeError(f\"Gap projection failed: g_min={g_min}\")\n"
# production constants (engine FROZEN_*), as exact decimals
A, Q, DELTA, EPS = F("1.0"), F("1.5"), F("0.05"), F("1e-12")
CAP = (A - DELTA) / Q                                   # 19/30
N = 12
FROZEN_PROJECTION_NORM_TOL, FROZEN_ZERO_TOL, FROZEN_GAP_TOL = 1e-14, 1e-12, 1e-9


def engine_block():
    src = ENGINE.read_bytes()
    assert hashlib.sha256(src).hexdigest() == ENGINE_SHA256, "engine is not the pinned file"
    s = src.decode()
    i, j = s.index(BLOCK_START), s.index(BLOCK_END) + len(BLOCK_END)
    assert s.count(BLOCK_START) == 1 and s.count(BLOCK_END) == 1
    return textwrap.dedent(s[i:j])


def make_gate(block):
    """Compile the (possibly mutated) block into gate(Bu) -> (B_projected, pre_violation, error_or_None)."""
    code = compile("def _gate(B_unprojected, config):\n" + textwrap.indent(block, "    ") +
                   "\n    return B_projected, pre_violation\n", "<engine-gate-copy>", "exec")
    ns = {"np": np, "FROZEN_PROJECTION_NORM_TOL": FROZEN_PROJECTION_NORM_TOL, "FROZEN_ZERO_TOL": FROZEN_ZERO_TOL,
          "FROZEN_GAP_TOL": FROZEN_GAP_TOL, "proposed_update_norm": 1.0, "state": SimpleNamespace(B=None)}
    exec(code, ns)
    cfg = SimpleNamespace(a=float(A), q=float(Q), delta=float(DELTA), scale_epsilon=float(EPS), capacity=float(CAP))
    cfg.capacity = (cfg.a - cfg.delta) / cfg.q          # engine property: (a - delta) / q, in float

    def gate(Bu):
        ns["proposed_update_norm"] = 1.0
        try:
            Bp, pv = ns["_gate"](np.array(Bu, dtype=float), cfg)
            return Bp, pv, None
        except RuntimeError as e:
            return None, None, str(e)
    return gate


def oracle(Bx):
    """Exact gate on a Fraction matrix (list of lists). Returns (B', pre_violation, scales)."""
    n = len(Bx)
    rs = [sum(r) for r in Bx]
    pre = min(A - Q * x for x in rs) < DELTA
    if not pre:
        return [r[:] for r in Bx], False, [F(1)] * n
    s = [min(F(1), CAP / (x + EPS)) for x in rs]
    out = [[(min(s[i], s[j]) * Bx[i][j] if i != j else F(0)) for j in range(n)] for i in range(n)]
    return out, True, s


def to_frac(Bf):
    return [[F(float(v)) for v in row] for row in Bf]     # exact value of each float64 input


def random_cases(seed=20261126, count=150):
    """Seeded symmetric nonnegative zero-diagonal matrices: sparse/dense, row sums spread around the cap, ties."""
    rng = random.Random(seed)
    cases = []
    for k in range(count):
        dens = rng.choice([0.2, 0.5, 1.0])
        M = np.zeros((N, N))
        for i in range(N):
            for j in range(i + 1, N):
                if rng.random() < dens:
                    M[i, j] = M[j, i] = rng.random()
        rs = M.sum(axis=1)
        target = rng.choice([0.3, 0.6, 0.633, 0.64, 0.8, 1.5]) * float(CAP) / 0.6333
        if rs.max() > 0:
            M *= target / rs.max()
        if k % 10 == 0:                                   # exact ties between endpoint scales
            M[0, :] = M[:, 0] = M[1, :] = M[:, 1] = 0
            M[0, 2] = M[2, 0] = M[1, 3] = M[3, 1] = 0.5
            M[0, 4] = M[4, 0] = M[1, 4] = M[4, 1] = 0.4
        cases.append(M)
    return cases


def eps_band_witness():
    """Every row sum <= cap but row 0/1 in the eps-band: float rowsum 0.6333333333333333 gives g_min_pre =
    0.050000000000000044 >= delta (no projection), while cap/(rowsum + eps) < 1 (so 'always project' changes B)."""
    M = np.zeros((N, N))
    M[0, 1] = M[1, 0] = 0.6333333333333333
    return M


def properties(gate, cases):
    """List of (property, case index) failures for a gate implementation."""
    fails = []
    capf = float(CAP)
    for idx, M in enumerate(cases + [eps_band_witness()]):
        Bp, pv, err = gate(M)
        if err is not None:
            fails.append(("P0_no_post_check_error", idx)); continue
        ox, opv, s = oracle(to_frac(M))
        if bool(pv) != opv:
            fails.append(("P1_trigger_matches_oracle", idx))
        o = np.array([[float(v) for v in r] for r in ox])
        if not np.allclose(Bp, o, rtol=1e-12, atol=1e-15):
            fails.append(("P2_values_match_oracle", idx))
        if not (np.allclose(Bp, Bp.T, rtol=0, atol=0) and (Bp >= 0).all() and not np.diag(Bp).any()):
            fails.append(("P3_symmetric_nonneg_zero_diag", idx))
        if (Bp.sum(axis=1) > capf * (1 + 1e-12)).any():
            fails.append(("P4_rows_le_cap", idx))
        Bp2, _, err2 = gate(Bp)
        if err2 is not None or not np.array_equal(Bp2, Bp):
            fails.append(("P5_idempotent_float", idx))
        oo, _, _ = oracle(ox)
        if oo != ox:
            fails.append(("P6_idempotent_exact", idx))
        if opv and not all(max(ox[i]) == 0 or sum(ox[i]) < CAP for i in range(N)):
            fails.append(("P7_exact_binding_rows_strictly_below_cap", idx))
    return fails


def spillover_observation(cases):
    """OBSERVATION (not a pass/fail rule): on projected cases, how often a non-binding row (rowsum <= cap) loses
    weight, and how far binding rows end below the cap. Impact on real runs stays UNEXPLAINED."""
    n_proj = n_rows_nb = n_nb_lose = 0
    worst_gap = F(0)
    for M in cases:
        Mx = to_frac(M)
        ox, pv, s = oracle(Mx)
        if not pv:
            continue
        n_proj += 1
        for i in range(N):
            before, after = sum(Mx[i]), sum(ox[i])
            if before <= CAP:
                n_rows_nb += 1
                n_nb_lose += after < before
            else:
                worst_gap = max(worst_gap, CAP - after)
    return {"projected_cases": n_proj, "nonbinding_rows": n_rows_nb, "nonbinding_rows_losing_weight": n_nb_lose,
            "max_binding_row_gap_below_cap": float(worst_gap)}


MS = "        B_projected = B_unprojected * np.minimum.outer(scale, scale)\n"
MUTANTS = {
    "M500_always_project": [("if pre_violation:\n", "if True:\n")],
    "M501_one_endpoint_factor": [(MS.lstrip(), "B_projected = B_unprojected * scale[:, None]\n")],
    "M502_max_endpoint_factor": [(MS.lstrip(), "B_projected = B_unprojected * np.maximum.outer(scale, scale)\n")],
    "M503_cap_plus_one_percent": [("config.capacity / (row_sum_pre", "1.01 * config.capacity / (row_sum_pre")],
    "M504_scale_epsilon_dropped": [("(row_sum_pre + config.scale_epsilon)", "(row_sum_pre)")],
    "M505_diagonal_not_rezeroed": [("    np.fill_diagonal(B_projected, 0.0)\n", "    pass\n")],
    "M506_trigger_le": [("g_min_pre < config.delta", "g_min_pre <= config.delta")],
}
EQUIV = {"E500_outer_transposed": [(MS.lstrip(), "B_projected = B_unprojected * np.minimum.outer(scale, scale).T\n")]}
# Predeclared before the first run (commit 1 of research/h10-gate-properties):
PREDECLARED = {
    "M500_always_project": "KILLED",          # only the eps-band witness separates it (P1/P2 on the witness)
    "M501_one_endpoint_factor": "KILLED",     # asymmetric (P3) and off-oracle (P2)
    "M502_max_endpoint_factor": "KILLED",     # rows exceed the cap (P4), off-oracle (P2)
    "M503_cap_plus_one_percent": "KILLED",    # off-oracle (P2); post-check or P4 on binding rows
    "M504_scale_epsilon_dropped": "SURVIVES", # changes values by ~cap*eps/rowsum ~ 1e-12 relative: below the float
                                              # comparison tolerance; disclosed limitation, not a pass
    "M505_diagonal_not_rezeroed": "SURVIVES", # equivalent: B_unprojected already has a zero diagonal
    "M506_trigger_le": "SURVIVES",            # float-equivalent at production a, q, delta: no float64 row sum gives
                                              # g_min_pre == delta exactly (+-50 ulps around cap scanned)
    "E500_outer_transposed": "NOT KILLED",    # equivalence control: must not be killed
}

# Recorded AFTER the first run (commit 2). PREDECLARED above is left exactly as committed before the run; a deviation is
# a finding about the prediction, listed here with its observed outcome and reason, never by editing PREDECLARED.
OBSERVED_DEVIATIONS = {
    "M504_scale_epsilon_dropped": ("KILLED",
        "prediction wrong: with eps = 0 a binding row lands on the cap in float (often 1 ulp above), so the re-applied "
        "gate re-triggers (P5 float idempotence) and values differ from the eps>0 oracle beyond rtol 1e-12 (P2)"),
}

# FOLLOW-UP PREDECLARATION (audit follow-up, commit 4 of this branch; committed BEFORE the witness/tie tests exist or
# have run). Informed by Auditor Seat 002's red team on f31da4c (its X7 and R14), so these are not blind predictions.
MUTANTS_FOLLOWUP = {
    # trigger loosened by the engine's own gap tolerance: projection only once g_min_pre < delta - 1e-9
    "M507_trigger_loosened_delta_minus_1e-9": [("g_min_pre < config.delta", "g_min_pre < config.delta - 1e-9")],
}
CASESET_MUTANTS_FOLLOWUP = {
    # test-set mutation, not a gate edit: the k % 10 == 0 exact-tie construction is removed from random_cases()
    "M508_tie_cases_removed": "random_cases(ties=False)",
}
PREDECLARED_FOLLOWUP = {
    "M507_trigger_loosened_delta_minus_1e-9": "KILLED",   # by a fixed above-cap witness: one edge at
                                                           # nextafter(fl(cap), 1); engine and oracle project, M507 not (P1)
    "M508_tie_cases_removed": "NOT DETECTED",              # predicted: the tie cases add no detection power; every
                                                           # predeclared outcome (incl. M507) stays the same without them
}


def expected(name):
    return OBSERVED_DEVIATIONS.get(name, (PREDECLARED[name], ""))[0]


def mutate(block, edits):
    out = block
    for old, new in edits:
        assert out.count(old) == 1, (old, out.count(old))
        out = out.replace(old, new)
    return out


def run(verbose=True):
    block = engine_block()
    cases = random_cases()
    results = {}
    base = properties(make_gate(block), cases)
    results["UNMUTATED"] = "PASS" if not base else f"FAIL {base[:3]}"
    for name, edits in {**MUTANTS, **EQUIV}.items():
        f = properties(make_gate(mutate(block, edits)), cases)
        killed = bool(f)
        if name.startswith("E"):
            results[name] = ("KILLED" if killed else "NOT KILLED", sorted({p for p, _ in f})[:3])
        else:
            results[name] = ("KILLED" if killed else "SURVIVES", sorted({p for p, _ in f})[:3])
    obs = spillover_observation(cases)
    ok = results["UNMUTATED"] == "PASS" and all(results[k][0] == expected(k) for k in PREDECLARED)
    if verbose:
        print("unmutated:", results["UNMUTATED"])
        for k, v in PREDECLARED.items():
            dev = " [DEVIATION from predeclared, recorded in OBSERVED_DEVIATIONS]" if k in OBSERVED_DEVIATIONS else ""
            print(f"{k}: {results[k][0]} (predeclared {v}) failing={results[k][1]} ->"
                  f" {'AS EXPECTED' if results[k][0] == expected(k) else 'MISMATCH'}{dev}")
        print("spillover observation:", obs)
        print("RESULT:", "PASS" if ok else "FAIL")
    return ok, results, obs


if __name__ == "__main__":
    import sys
    sys.exit(0 if run()[0] else 1)
