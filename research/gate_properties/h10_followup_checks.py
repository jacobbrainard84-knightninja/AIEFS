"""H10 audit follow-up checks (Researcher 001; Auditor Seat 002 CLEAN WITH NOTES on f31da4c). Stdlib + numpy.

- m504_breakdown(): why M504 (eps dropped) is killed: single-application value deviation vs the eps > 0 oracle (P2),
  and where binding rows land relative to fl(cap) (P5 re-triggers). Audit note N1.
- spillover_rule(): checks that a below-cap row loses weight iff it has an edge to an over-cap row (the per-edge
  min-endpoint gate, E27), in both directions, on the H10 case set. Audit note N3.
- m506_ulp_scan(): the float scan behind M506: no float64 x within +-K ulps of fl(cap) gives fl(1 - 1.5 x) == 0.05.
  Audit note N7.
"""
from fractions import Fraction as F

import numpy as np

import gate_h10 as g


def m504_breakdown():
    block = g.engine_block()
    m504 = g.make_gate(g.mutate(block, g.MUTANTS["M504_scale_epsilon_dropped"]))
    capf = (1.0 - 0.05) / 1.5
    p2_cases, p5_cases, max_rel = 0, 0, 0.0
    ulp_hist = {}
    for M in g.random_cases():
        Bp, pv, err = m504(M)
        assert err is None
        ox, opv, s = g.oracle(g.to_frac(M))
        o = np.array([[float(v) for v in r] for r in ox])
        if not np.allclose(Bp, o, rtol=1e-12, atol=1e-15):
            p2_cases += 1
        nz = o != 0
        if nz.any():
            max_rel = max(max_rel, float(np.max(np.abs(Bp[nz] - o[nz]) / np.abs(o[nz]))))
        Bp2, _, _ = m504(Bp)
        if not np.array_equal(Bp2, Bp):
            p5_cases += 1
        if pv:
            rs_in = M.sum(axis=1)
            rs_out = Bp.sum(axis=1)
            for i in range(g.N):
                if rs_in[i] > capf:                       # binding row (own scale < 1 with eps = 0)
                    d = int(np.int64(np.float64(rs_out[i]).view(np.int64)) - np.int64(np.float64(capf).view(np.int64)))
                    key = d if d >= -2 else "below_by_more_than_2_ulps"
                    ulp_hist[key] = ulp_hist.get(key, 0) + 1
    return {"p2_cases": p2_cases, "p5_cases": p5_cases, "max_rel_dev": max_rel,
            "binding_row_ulps_vs_fl_cap": ulp_hist}


def spillover_rule():
    n_proj = n_below = lose = lose_with_over_nbr = nbr_no_loss = lose_own_band = 0
    worst_gap = F(0)
    for M in g.random_cases():
        Mx = g.to_frac(M)
        ox, pv, s = g.oracle(Mx)
        if not pv:
            continue
        n_proj += 1
        rs = [sum(r) for r in Mx]
        for i in range(g.N):
            after = sum(ox[i])
            if rs[i] <= g.CAP:
                n_below += 1
                lost = after < rs[i]
                has_over = any(Mx[i][j] > 0 and rs[j] > g.CAP for j in range(g.N) if j != i)
                lose += lost
                lose_with_over_nbr += lost and has_over
                nbr_no_loss += has_over and not lost
                lose_own_band += lost and not has_over and s[i] < 1
            else:
                worst_gap = max(worst_gap, g.CAP - after)
    return {"projected_cases": n_proj, "below_cap_rows": n_below, "below_cap_rows_losing": lose,
            "losing_with_over_cap_neighbour": lose_with_over_nbr,
            "over_cap_neighbour_but_no_loss": nbr_no_loss, "losing_only_via_own_eps_band": lose_own_band,
            "max_over_cap_row_gap_below_cap": float(worst_gap)}


def m506_ulp_scan(k=2_000_000):
    capf = np.float64((1.0 - 0.05) / 1.5)
    xs = (capf.view(np.int64) + np.arange(-k, k + 1, dtype=np.int64)).view(np.float64)
    gs = 1.0 - 1.5 * xs
    exact = int(np.count_nonzero(gs == 0.05))
    d_ulps = np.abs(gs.view(np.int64) - np.float64(0.05).view(np.int64))
    return {"scanned_ulps_each_side": k, "x_with_g_equal_delta": exact, "closest_g_in_ulps_of_delta": int(d_ulps.min())}


if __name__ == "__main__":
    print("M504:", m504_breakdown())
    print("spillover:", spillover_rule())
    print("M506 scan:", m506_ulp_scan())
