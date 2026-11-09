#!/usr/bin/env python3
"""Lean P1 cross-check: evaluate the statements of lean/AIEFGateCore against the pinned engine.

NEW unpinned research (2026-11-09, branch research/lean-gate-identities). Edits nothing pinned.

What is checked (replay seed 4619122171158768524, rho 1.0, t = 250, exactly kappa_cycle_kernel.job()'s replay lines):

  F  Model fidelity. `lean_step` below is a line-by-line transcription of the Lean definitions
     `pre`, `prop`, `incAct`, `scale`, `sc`, `gated`, `GateOn`, `stepB` (lean/AIEFGateCore/AIEFGateCore/GateMap.lean)
     on the 66 edges of the 12-node complete graph. Evaluated in EXACT rational arithmetic (stdlib fractions) on the
     engine's float64 inputs, it must agree with the pinned engine's float output (kappa_cycle_kernel.step_B ->
     aief_experiment_engine_v1.advance_state) to FIDELITY_TOL on every edge, at the base state and at every perturbed
     input fl(B + delta H) actually given to the engine.
  H  Hypotheses. For each sample, the hypotheses of `stepB_add_smul_of_branch` are decided exactly (Fractions):
     clip (pre >= 0 on supp h at both states), same gate decision, InCtrlKer (A h)_{ctrl e} = 0 for all e, IsCtrl at
     both states (ctrl = exact argmin endpoint, ties -> src).
  T  Theorem instance. Whenever H holds, the exact identity stepB(B + d h) = stepB(B) + d (1-γdt) branchScale h must
     hold with residual exactly 0 (it is a theorem; a nonzero residual would mean the transcription is wrong).
  E  Engine agreement. The Lean branch multiplier lam_branch = (1-γdt) Σ branchScale_e h_e² / Σ h_e² is compared with
     the engine's one-sided finite-difference multiplier <(step_B(B + d H) - step_B(B))/d, h>/<h,h> at an on-branch
     step with small rounding (ENGINE_DELTA), tolerance ENGINE_TOL (= ERRATA E5/E22 resolved bound 2.1e-10).
     For the gate component also: K3_gate_component_multiplier's closed form a(min(s0,s1)+s0+s1)/3 equals lam_branch
     exactly, and lam_branch - lam_state = -a|s0-s1|/6 exactly (K3_gate_branch_sub_state).
  N  Negative controls (each must be DETECTED, else the run fails):
     N1 wrong constant (factor 1-γdt dropped) disagrees with the engine by >> ENGINE_TOL;
     N2 wrong controller set (mean scale over all component nodes, i.e. node 11 counted as a controller);
     N3 off-fiber direction (gate component, v = (+1 on (7,11), -1 on (2,7),(2,11))): InCtrlKer fails and the affine
        identity has a nonzero exact residual;
     N4 branch crossing: at least one gate-component sample with H false has a nonzero exact residual.

Components: GATE = nodes [2, 7, 11] (the AUD-RATELAW gap component; J = [2, 7]); CONTROL = well-resolved K5
nodes [0, 1, 5, 6, 10] (all tied, J = all) with the exact kernel 4-cycle h = e(0,1) - e(1,5) + e(5,6) - e(0,6).

Run from anywhere:  python research/lean_gate/lean_gate_crosscheck_v1.py [--out PATH]
Default output: research/lean_gate/results/lean_gate_crosscheck_v1.json (deterministic, no timestamps). Exit 0 iff
every positive check passes and every negative control is detected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "AI Agent Audits" / "evidence" / "scripts"
KCK_JSON = REPO / "AI Agent Audits" / "evidence" / "results" / "kappa_cycle_kernel.json"
DEFAULT_OUT = REPO / "research" / "lean_gate" / "results" / "lean_gate_crosscheck_v1.json"
PINNED_SHA256 = {
    "aief_experiment_engine_v1.py": "ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede",
    "AIEF_1_4_Twindow_sensitivity.py": "633d1a21502598021d456bff7ff39b4065b5e5d05218c4411a4f36d53e0956ee",
    "AI Agent Audits/evidence/scripts/kappa_cycle_kernel.py": "347276307142acb84214c156ccbc601b6729b804311cfa3a1270ac13d2a8e873",
    "AI Agent Audits/evidence/results/kappa_cycle_kernel.json": "78330914e4159c9afcc43b7985c5ff2d76c3bc496451f814a7b6fb896206e81b",
}
SEED, RHO = 4619122171158768524, 1.0
GATE_NODES = [2, 7, 11]
CONTROL_NODES = [0, 1, 5, 6, 10]
DELTAS = [1e-9, 1e-8, 1e-7, 1e-6, 1e-5]
ENGINE_DELTA = 1e-5
ENGINE_TOL = 2.1e-10
FIDELITY_TOL = 1e-15        # absolute, on B' values of size <= ~0.4 (a few float64 ulps)
NEG_MIN_FACTOR = 100.0      # a negative control is "detected" if its error exceeds NEG_MIN_FACTOR * ENGINE_TOL
N = 12
EDGES = [(i, j) for i in range(N) for j in range(i + 1, N)]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_pins() -> None:
    bad = [k for k, v in PINNED_SHA256.items() if sha256(REPO / k) != v]
    if bad:
        raise SystemExit(f"pinned input changed, refusing to run: {bad}")


def load_kck():
    os.chdir(REPO)
    os.environ.setdefault("AIEF_AUDIT_OUT", str(Path(os.environ.get("TMPDIR", "/tmp")) / "lean_gate_kck_out"))
    sys.path.insert(0, str(SCRIPTS))
    import kappa_cycle_kernel as kck  # pinned, read-only; dump() is never called
    return kck


# ------------------------------------------------------------------------------------------------------------------
# Transcription of the Lean definitions (GateMap.lean). Works for float or Fraction scalars.
# ------------------------------------------------------------------------------------------------------------------
class P:  # Lean `Params`
    def __init__(self, cfg, F):
        self.dt, self.g, self.cap, self.eps = F(cfg.dt), F(cfg.gamma), F(cfg.capacity), F(cfg.scale_epsilon)
        self.gapA, self.gapQ, self.gapDelta = F(cfg.a), F(cfg.q), F(cfg.delta)


def pre(p, drive, B):            # B e + dt * (drive e - γ * B e)
    return [B[e] + p.dt * (drive[e] - p.g * B[e]) for e in range(len(EDGES))]


def prop(p, drive, B):           # max (pre) 0
    return [max(v, 0 * v) for v in pre(p, drive, B)]


def incAct(h):                   # (A h)_i = Σ_e (1[src e = i] + 1[dst e = i]) h_e
    out = [0 * h[0]] * N
    for e, (i, j) in enumerate(EDGES):
        out[i] = out[i] + h[e]
        out[j] = out[j] + h[e]
    return out


def ldiv(a, b):                  # Lean/Mathlib real division: a / 0 = 0 (never hit by the engine, where ε > 0)
    return 0 * a if b == 0 else a / b


def scale(p, q):                 # min 1 (cap / (q + ε))
    return min(1 + 0 * q, ldiv(p.cap, q + p.eps))


def sc(p, x):
    return [scale(p, q) for q in incAct(x)]


def gate_on(p, x):               # ∃ i, gapA - gapQ * q_i < gapDelta
    return any(p.gapA - p.gapQ * q < p.gapDelta for q in incAct(x))


def lean_step(p, drive, B):      # stepB
    x = prop(p, drive, B)
    if not gate_on(p, x):
        return x
    s = sc(p, x)
    return [x[e] * min(s[i], s[j]) for e, (i, j) in enumerate(EDGES)]


def ctrl_of(s):                  # exact argmin endpoint; ties -> src
    return [i if s[i] <= s[j] else j for (i, j) in EDGES]


def is_ctrl(s, ctrl):
    return all(s[c] <= s[i] and s[c] <= s[j] and c in (i, j) for c, (i, j) in zip(ctrl, EDGES))


# ------------------------------------------------------------------------------------------------------------------
def engine_inputs(kck):
    cfg = kck.tw.create_model_config(RHO)
    prot = kck.tw.create_protocol_config()
    st, _ = kck.engine.simulate_prefix(SEED, cfg, prot)
    rng = np.random.default_rng(0)
    for _ in range(int(round(kck.T_TARGET / cfg.dt))):
        kck.engine.advance_state(st, cfg, rng)
    S0 = st.clone()
    R0 = kck.engine.compute_R(S0.clone(), cfg)
    return cfg, S0, R0


def edge_vec(M):
    return [float(M[i, j]) for (i, j) in EDGES]


def hvec(pairs):
    v = [Fr(0)] * len(EDGES)
    for (i, j), c in pairs.items():
        v[EDGES.index((min(i, j), max(i, j)))] = Fr(c)
    return v


def hypotheses(p, drive, B, Bt, h, ctrl):
    pre0, pre1 = pre(p, drive, B), pre(p, drive, Bt)
    x0, x1 = prop(p, drive, B), prop(p, drive, Bt)
    s0, s1 = sc(p, x0), sc(p, x1)
    Ah = incAct(h)
    return dict(
        clip=all(pre0[e] >= 0 and pre1[e] >= 0 for e in range(len(EDGES)) if h[e] != 0),
        same_gate=gate_on(p, x0) == gate_on(p, x1),
        in_ctrl_ker=all(Ah[c] == 0 for c in ctrl),
        is_ctrl_base=is_ctrl(s0, ctrl),
        is_ctrl_pert=is_ctrl(s1, ctrl),
    )


def branch_scale(p, drive, B, ctrl):
    x = prop(p, drive, B)
    if not gate_on(p, x):
        return [Fr(1)] * len(EDGES)
    s = sc(p, x)
    return [s[c] for c in ctrl]


def engine_multiplier(kck, cfg, S0, base, hf, d):
    H = np.zeros((N, N))
    for e, (i, j) in enumerate(EDGES):
        H[i, j] = H[j, i] = hf[e]
    out = kck.step_B(S0, cfg, d * H)
    dv = (out - base) / d
    v = np.array([dv[i, j] for (i, j) in EDGES])
    h = np.array(hf)
    return float(v @ h / (h @ h)), out, H


def run() -> dict:
    check_pins()
    kck = load_kck()
    cfg, S0, R0 = engine_inputs(kck)
    pf, pq = P(cfg, float), P(cfg, Fr)
    a = 1 - pq.g * pq.dt
    Bf = edge_vec(S0.B)
    # drive in float64 exactly as the engine forms it: (eta + mu) * R - mu  (then - gamma*B inside pre)
    drv_f = edge_vec((cfg.eta + cfg.mu) * R0 - cfg.mu)
    Bq, drq = [Fr(v) for v in Bf], [Fr(v) for v in drv_f]
    base_eng = kck.step_B(S0, cfg)
    report = dict(schema="lean-gate-crosscheck/1", seed=SEED, rho=RHO, deltas=DELTAS, engine_delta=ENGINE_DELTA,
                  engine_tol=ENGINE_TOL, fidelity_tol=FIDELITY_TOL, neg_min_factor=NEG_MIN_FACTOR,
                  lean_project="lean/AIEFGateCore", checks={}, components={})
    fails = []

    # ---- F at base -------------------------------------------------------------------------------------------
    base_lean = lean_step(pq, drq, Bq)
    fid0 = max(abs(float(base_lean[e]) - float(base_eng[i, j])) for e, (i, j) in enumerate(EDGES))
    report["checks"]["F_base_max_abs_diff"] = fid0
    if not fid0 <= FIDELITY_TOL:
        fails.append("F_base")
    x0 = prop(pq, drq, Bq)
    s0 = sc(pq, x0)
    report["checks"]["gate_on_base"] = gate_on(pq, x0)
    ctrl = ctrl_of(s0)

    comps = dict(
        GATE=dict(nodes=GATE_NODES, h={(2, 7): 1, (2, 11): -1, (7, 11): -1}),
        CONTROL=dict(nodes=CONTROL_NODES, h={(0, 1): 1, (1, 5): -1, (5, 6): 1, (0, 6): -1}),
    )
    for name, c in comps.items():
        h = hvec(c["h"])
        hf = [float(v) for v in h]
        bs = branch_scale(pq, drq, Bq, ctrl)
        hh = sum(v * v for v in h)
        lam_branch = a * sum(bs[e] * h[e] * h[e] for e in range(len(EDGES))) / hh
        J = sorted({ctrl[e] for e in range(len(EDGES)) if h[e] != 0})
        lam_state = a * sum(s0[i] for i in J) / len(J)
        lam_all_nodes = a * sum(s0[i] for i in c["nodes"]) / len(c["nodes"])
        rec = dict(nodes=c["nodes"], h={f"{i}-{j}": v for (i, j), v in c["h"].items()}, J=J,
                   lam_branch=float(lam_branch), lam_state=float(lam_state),
                   branch_minus_state=float(lam_branch - lam_state), samples=[])
        if name == "GATE":
            s2, s7, s11 = s0[2], s0[7], s0[11]
            k3 = a * (min(s2, s7) + s2 + s7) / 3
            rec["K3_closed_form_equals_lam_branch"] = (k3 == lam_branch)
            rec["branch_minus_state_equals_minus_a_abs_s0_s1_over_6"] = (lam_branch - lam_state == -a * abs(s2 - s7) / 6)
            rec["s"] = {"2": float(s2), "7": float(s7), "11": float(s11)}
            rec["s11_minus_min_s2_s7"] = float(s11 - min(s2, s7))
            if not (rec["K3_closed_form_equals_lam_branch"] and rec["branch_minus_state_equals_minus_a_abs_s0_s1_over_6"]):
                fails.append("GATE_K3_identities")
            D = json.loads(KCK_JSON.read_text())
            rep = [r for r in D["replays"] if r["seed"] == SEED and r["rho"] == RHO][0]
            rc = [cc for cc in rep["comps"] if cc["nodes"] == GATE_NODES][0]
            rec["recorded_lam_state_formula"] = rc["lam_state_formula"]
            rec["recorded_fiber_lam"] = rc["fiber"][0]["lam"]
            rec["lam_state_vs_recorded_rel"] = abs(float(lam_state) - rc["lam_state_formula"]) / rc["lam_state_formula"]
        # ---- samples: H, T, F at perturbed inputs ----
        for d in DELTAS:
            for sg in (1, -1):
                dd = sg * d
                # exact ideal input B + dd h  (Lean statement) ...
                Bt = [Bq[e] + Fr(dd) * h[e] for e in range(len(EDGES))]
                H = hypotheses(pq, drq, Bq, Bt, h, ctrl)
                out = lean_step(pq, drq, Bt)
                resid = max(abs(out[e] - base_lean[e] - Fr(dd) * a * bs[e] * h[e]) for e in range(len(EDGES)))
                # ... and the float input fl(B + dd H) the engine actually receives: model fidelity there
                lam_eng, out_eng, Hm = engine_multiplier(kck, cfg, S0, base_eng, hf, dd)
                Bfl = edge_vec(S0.B + dd * Hm)
                out_fl = lean_step(pq, drq, [Fr(v) for v in Bfl])
                fid = max(abs(float(out_fl[e]) - float(out_eng[i, j])) for e, (i, j) in enumerate(EDGES))
                ok = all(H.values())
                rec["samples"].append(dict(delta=dd, hypotheses=H, all_hypotheses=ok, exact_residual=float(resid),
                                           exact_residual_is_zero=(resid == 0), fidelity_max_abs_diff=fid,
                                           lam_engine=lam_eng, lam_engine_minus_lam_branch=lam_eng - float(lam_branch)))
                if ok and resid != 0:
                    fails.append(f"T_{name}_{dd}")
                if not fid <= FIDELITY_TOL:
                    fails.append(f"F_{name}_{dd}")
        # ---- E: engine agreement at an on-branch sample with small rounding ----
        on = [s for s in rec["samples"] if s["all_hypotheses"] and abs(s["delta"]) == ENGINE_DELTA]
        if not on:
            fails.append(f"E_{name}_no_on_branch_sample_at_engine_delta")
        else:
            smp = on[0]
            err = abs(smp["lam_engine"] - float(lam_branch)) / float(lam_branch)
            rec["E"] = dict(delta=smp["delta"], rel_err_engine_vs_lam_branch=err, passes=err <= ENGINE_TOL)
            if not err <= ENGINE_TOL:
                fails.append(f"E_{name}")
            # N1 wrong constant, N2 wrong controller set
            lam_wrong_const = float(lam_branch / a)
            n1 = abs(smp["lam_engine"] - lam_wrong_const) / float(lam_branch)
            n2 = abs(smp["lam_engine"] - float(lam_all_nodes)) / float(lam_branch)
            rec["N1_wrong_constant_rel_err"] = n1
            rec["N1_detected"] = n1 > NEG_MIN_FACTOR * ENGINE_TOL
            rec["N2_all_nodes_rel_err"] = n2
            rec["N2_detected"] = n2 > NEG_MIN_FACTOR * ENGINE_TOL
            if not rec["N1_detected"]:
                fails.append(f"N1_{name}_not_detected")
            if name == "GATE" and not rec["N2_detected"]:
                fails.append("N2_GATE_not_detected")
        report["components"][name] = rec

    # ---- N3 off-fiber direction on the gate component ----
    v = hvec({(7, 11): 1, (2, 7): -1, (2, 11): -1})
    bs = branch_scale(pq, drq, Bq, ctrl)
    n3 = []
    for d in (1e-7, -1e-7):
        Bt = [Bq[e] + Fr(d) * v[e] for e in range(len(EDGES))]
        H = hypotheses(pq, drq, Bq, Bt, v, ctrl)
        out = lean_step(pq, drq, Bt)
        resid = max(abs(out[e] - base_lean[e] - Fr(d) * a * bs[e] * v[e]) for e in range(len(EDGES)))
        n3.append(dict(delta=d, in_ctrl_ker=H["in_ctrl_ker"], exact_residual=float(resid)))
    det3 = all((not r["in_ctrl_ker"]) and r["exact_residual"] > 0 for r in n3)
    report["checks"]["N3_off_fiber"] = dict(samples=n3, detected=det3)
    if not det3:
        fails.append("N3_not_detected")
    # ---- N4 branch crossing ----
    cross = [s for s in report["components"]["GATE"]["samples"] if not s["all_hypotheses"]]
    det4 = any(s["exact_residual"] > 0 for s in cross)
    report["checks"]["N4_branch_crossing"] = dict(n_crossing_samples=len(cross),
                                                  crossing_deltas=[s["delta"] for s in cross],
                                                  detected=det4)
    if not det4:
        fails.append("N4_not_detected")
    report["fails"] = fails
    report["result"] = "PASS" if not fails else "FAIL"
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()
    rep = run()
    Path(args.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: rep[k] for k in ("result", "fails")}))
    sys.exit(0 if rep["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
