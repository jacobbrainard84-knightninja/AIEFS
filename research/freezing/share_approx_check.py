"""Approximation error of the §2 gated-share heuristic (REPORT.md L138), on seeded synthetic constant-R mixes.

Deposited 2026-11-21 (Researcher 001) after audit R1 on docs/freezing-report-fixes. This is NOT the engine: it iterates only
the weight map with the min-endpoint capacity gate (same law as aief_experiment_engine_v1.py L811-812 and freeze_check.py :49),
with R held constant, to the fixed point, and compares each edge's equilibrium B_e with
  two-endpoint form  u_e+ * min(1, c/max(S_i, S_j))          (REPORT after the fix)
  one-endpoint forms min(u_e+, c*u_e+/S_i) and the same with S_j (REPORT before the fix),
where S_k = sum_j u_kj+. Reports per mix: max |error| over edges with u_e > 0, status (B > B_c) disagreements, ON edges and
the smallest |B_e - B_c|. Deterministic (fixed seeds); numpy only.

    python research/freezing/share_approx_check.py            # writes share_approx_check.json next to this file
"""
import json
import os

import numpy as np

ETA, MU, GAM, H, A, Q, D, EPS, BC = 0.04, 0.03, 0.015, 0.00015, 1.0, 1.5, 0.05, 1e-12, 0.12   # REPORT §1.1, h = gamma*dt
CAP = (A - D) / Q
N = 12
GROUPS = [range(0, 6), range(6, 10), range(10, 12)]
MAX_STEPS, CHECK_EVERY, TOL = 400_000, 10_000, 1e-15


def fixed_point(R):
    u = ((ETA + MU) * R - MU) / GAM
    np.fill_diagonal(u, 0.0)
    B = np.zeros_like(R)
    steps = 0
    while steps < MAX_STEPS:
        prev = B.copy()
        for _ in range(CHECK_EVERY):
            U = np.maximum(0.0, (1 - H) * B + H * u)
            np.fill_diagonal(U, 0.0)
            s = U.sum(1)
            if np.min(A - Q * s) < D:
                sc = np.minimum(1.0, CAP / (s + EPS))
                B = U * np.minimum.outer(sc, sc)
            else:
                B = U
        steps += CHECK_EVERY
        if np.max(np.abs(B - prev)) < TOL:
            break
    return B, u, steps, float(np.max(np.abs(B - prev)))


def compare(R, label):
    B, u, steps, resid = fixed_point(R)
    up = np.maximum(u, 0.0)
    np.fill_diagonal(up, 0.0)
    S = up.sum(1)
    iu = np.triu_indices(N, 1)
    x, ue, Si, Sj = B[iu], up[iu], S[iu[0]], S[iu[1]]
    forms = {
        "two_endpoint": ue * np.minimum(1.0, CAP / np.maximum(Si, Sj)),
        "one_endpoint_i": np.minimum(ue, CAP * ue / Si),
        "one_endpoint_j": np.minimum(ue, CAP * ue / Sj),
    }
    m = ue > 0
    out = {"mix": label, "steps": steps, "last_step_change": resid, "on_edges": int(np.sum(x > BC)),
           "min_abs_B_minus_Bc": float(np.min(np.abs(x - BC)))}
    for k, f in forms.items():
        out[k] = {"max_abs_err": float(np.max(np.abs(f[m] - x[m]))),
                  "status_flips": int(np.sum((f > BC) != (x > BC)))}
    return out


def original_mixes():
    """The 3 mixes first reported on dd6ba0c (inline script, reproduced verbatim): one shared rng(1), cross 0.55/0.60/0.65."""
    rng = np.random.default_rng(1)
    res = []
    for trial in range(3):
        R = np.full((N, N), 0.2)
        for g in GROUPS:
            for i in g:
                for j in g:
                    R[i, j] = 1.0
        R[np.ix_(range(0, 6), range(6, 10))] = R[np.ix_(range(6, 10), range(0, 6))] = 0.55 + 0.05 * trial
        R = R + rng.uniform(-0.02, 0.0, (N, N))
        R = np.minimum(1, (R + R.T) / 2)
        np.fill_diagonal(R, 1)
        res.append(compare(R, f"original-{trial}"))
    return res


def sweep_mix(seed):
    """Auditor-style mix: within-cluster R in [0.97, 1], 6-4 cross R in [0.55, 0.65], all other pairs R in [0.10, 0.15]."""
    rng = np.random.default_rng(1000 + seed)
    R = rng.uniform(0.10, 0.15, (N, N))
    for g in GROUPS:
        idx = np.ix_(g, g)
        R[idx] = rng.uniform(0.97, 1.0, (len(g), len(g)))
    R[np.ix_(range(0, 6), range(6, 10))] = rng.uniform(0.55, 0.65, (6, 4))
    R = np.triu(R, 1)
    R = R + R.T
    np.fill_diagonal(R, 1.0)
    return compare(R, f"sweep-{seed}")


def summary(rows):
    s = {}
    for k in ("two_endpoint", "one_endpoint_i", "one_endpoint_j"):
        e = [r[k]["max_abs_err"] for r in rows]
        s[k] = {"max_abs_err_min": min(e), "max_abs_err_max": max(e),
                "status_flips_total": sum(r[k]["status_flips"] for r in rows),
                "mixes_with_a_flip": sum(r[k]["status_flips"] > 0 for r in rows)}
    s["min_abs_B_minus_Bc"] = min(r["min_abs_B_minus_Bc"] for r in rows)
    s["on_edges_range"] = [min(r["on_edges"] for r in rows), max(r["on_edges"] for r in rows)]
    return s


def main():
    orig = original_mixes()
    sweep = [sweep_mix(k) for k in range(40)]
    report = {"params": {"eta": ETA, "mu": MU, "gamma": GAM, "h": H, "a": A, "q": Q, "delta": D, "eps": EPS, "B_c": BC,
                         "cap": CAP, "N": N, "clusters": [6, 4, 2], "max_steps": MAX_STEPS, "tol": TOL,
                         "sweep_seeds": "numpy default_rng(1000+k), k=0..39"},
              "original": orig, "original_summary": summary(orig),
              "sweep": sweep, "sweep_summary": summary(sweep)}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "share_approx_check.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
        f.write("\n")
    for name in ("original_summary", "sweep_summary"):
        print(name, json.dumps(report[name]))


if __name__ == "__main__":
    main()
