#!/usr/bin/env python3
"""AUD-RATELAW / ERRATA E5 / E22: step-size (delta) sweep on the single component that carries the ~2e-8 rate-law gap.

NEW unpinned research (2026-11-08, branch research/rate-law-delta-sweep). Nothing here edits or re-pins a frozen file.

Target (read-only, from the pinned `AI Agent Audits/evidence/results/kappa_cycle_kernel.json`, git blob a4536fb7):
  replay seed 4619122171158768524, rho 1.0 (T_w 17.50291715), component index 1, nodes [2, 7, 11] (K3, k = 2),
  controllers J = [2, 7], one tied edge, kernel_dim 1, historical step delta = 1.062225811e-09,
  rel_err_lam_vs_state = 2.038720579e-08, rel_err_lam_vs_closed_form = 2.071385042e-08.
This is the only resolved two-sided component with delta < 1e-6; it carries the census maxima in rate_law_census_r4.json.

How the pinned operator is reused (no second engine):
  * `kappa_cycle_kernel.py` (pinned) is IMPORTED, not copied. Its `job()` is run unchanged for the target replay as the
    historical witness, and its `step_B`, `vec2mat`, `mat2vec`, `nullspace`, `components`, `TIE_TOL`, `SUPP` are used for
    every sample. `step_B` calls the frozen engine's `aief_experiment_engine_v1.advance_state` on a clone.
  * The replayed base state is rebuilt with exactly the four lines `job()` uses (simulate_prefix, then
    round(T_TARGET/dt) advance_state steps with default_rng(0)); the witness check fails closed unless the
    sweep's own sample at the historical delta reproduces job()'s multiplier bit for bit.
  * Branch diagnostics (gate, clip, endpoint scales s, controller identity) come from `pregate()`, a line-by-line
    mirror of engine v1 `advance_state` :790-813 (proposal, clip, symmetrise, gate test, scales). It does not
    produce the measurement: every sample asserts that the mirror's gated output equals the engine's `step_B`
    output bit for bit on the component, otherwise the run fails closed.
  * Higher-precision path (stdlib `fractions`, no new dependency): the same one-step gate map evaluated in exact
    rational arithmetic on the engine's float64 inputs, (i) with the float-rounded perturbed input fl(B + delta H)
    the engine actually received, and (ii) with the ideal input B + delta H. (ii) is the exact branch multiplier.

Predeclared protocol (constants below are fixed before the sweep is run; nothing is chosen from the measured errors):
  * grid: 10^(k/4), k = -48..-16 (1e-12 .. 1e-4, 33 coarse points) + 16 dense points 10^(-9 + j/16) in [1e-9, 1e-8)
    + the historical delta. Every delta is run at +delta and -delta separately.
  * admissible sample: at BOTH signs the gate is on, the clip pattern (entries of the proposal clipped to 0), the
    support of the input B and the per-edge controller pattern on the component (tied within TIE_TOL / winning
    endpoint) are identical to the base state, and ||A_J h|| <= AJH_TOL. Anything else is a BRANCH CROSSING, reported
    as such, never as a numerical residual, and excluded from every fit.
  * branch window W: the maximal contiguous run of admissible grid points containing the historical delta.
  * primary estimator: the historical one (one-sided +delta, lam = <dB'/delta, h>), error relative to the state
    formula (1 - gamma dt) mean(s_J). Minus-side, central and input-corrected estimators are reported, not decided on.
  * decision (decide()): NARROWED only if controls pass (else INCONCLUSIVE) and C2 historical delta admissible,
    C3 W spans >= WINDOW_MIN_DECADES, C4 a plateau OR a roundoff model holds on W's coarse points, C5 the exact branch
    multiplier equals the state formula within RESOLVED_BOUND on all of W. Otherwise UNEXPLAINED, with reasons.
      plateau: >= PLATEAU_MIN_POINTS consecutive coarse points, max/min <= PLATEAU_MAX_RATIO,
               |log-log slope| <= PLATEAU_MAX_ABS_SLOPE, median <= RESOLVED_BOUND.
      roundoff: >= ROUNDOFF_MIN_POINTS coarse points, log-log slope in ROUNDOFF_SLOPE, R^2 >= ROUNDOFF_MIN_R2,
               A = median(err * delta) predicts the recorded historical error within ROUNDOFF_PRED_FACTOR, and the
               error at the LARGEST-delta coarse point of W is <= RESOLVED_BOUND (the gap actually closes on-branch).
  * RESOLVED_BOUND = 2.1e-10 is the E5 agreement bound of the other 263 resolved two-sided components (census max
    2.095213469e-10).

Run from anywhere:  python research/rate_law/rate_law_delta_sweep_v1.py [--quick] [--out PATH]
Default output: research/rate_law/results/rate_law_delta_sweep_v1.json (deterministic; no timestamps).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "AI Agent Audits" / "evidence" / "scripts"
KCK_JSON = REPO / "AI Agent Audits" / "evidence" / "results" / "kappa_cycle_kernel.json"
CENSUS_JSON = REPO / "AI Agent Audits" / "evidence" / "results" / "rate_law_census_r4.json"
DEFAULT_OUT = REPO / "research" / "rate_law" / "results" / "rate_law_delta_sweep_v1.json"

# sha256 of the read-only inputs (audit_manifest.json `inputs` for the engine / T_w module; files at main eb3933c).
PINNED_SHA256 = {
    "aief_experiment_engine_v1.py": "ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede",
    "AIEF_1_4_Twindow_sensitivity.py": "633d1a21502598021d456bff7ff39b4065b5e5d05218c4411a4f36d53e0956ee",
    "AI Agent Audits/evidence/scripts/kappa_cycle_kernel.py": "347276307142acb84214c156ccbc601b6729b804311cfa3a1270ac13d2a8e873",
    "AI Agent Audits/evidence/results/kappa_cycle_kernel.json": "78330914e4159c9afcc43b7985c5ff2d76c3bc496451f814a7b6fb896206e81b",
    "AI Agent Audits/evidence/results/rate_law_census_r4.json": "4f0b9ba73d9aa1d69c19bd8ed7fd326dd16d37432eb3bbf22602aace0ec8def2",
}

# ---- frozen target and control (values as stored, 10 significant digits) -------------------------------------------
TARGET = dict(seed=4619122171158768524, rho=1.0, comp_index=1, fiber_index=0, nodes=[2, 7, 11], J=[2, 7], k=2,
              T_w=17.50291715, delta=1.062225811e-09, delta_over_tied_gap=438.5625016, untied_gap_over_delta=438.5625016,
              rel_err_lam_vs_closed_form=2.071385042e-08, rel_err_lam_vs_state=2.038720579e-08,
              rel_err_r_vs_closed_form=1.64063597e-05, s_spread_J=2.422062551e-12, R_min=0.9999997063,
              kernel_dim=1, n_tied_edges=1)
# Well-resolved two-sided control from the SAME replay (same base state): K5, all edges tied, delta = 1e-5,
# recorded rel_err_lam_vs_state 1.275752945e-12 (mean over its 6 fiber directions); fiber direction 0 is used.
CONTROL = dict(seed=4619122171158768524, rho=1.0, comp_index=0, fiber_index=0, nodes=[0, 1, 5, 6, 10],
               delta=1e-05, rel_err_lam_vs_state=1.275752945e-12, kernel_dim=5)

# ---- predeclared constants ------------------------------------------------------------------------------------------
COARSE = [10.0 ** (k / 4) for k in range(-48, -15)]          # 1e-12 .. 1e-4, quarter decades
DENSE = [10.0 ** (-9 + j / 16) for j in range(16)]           # [1e-9, 1e-8)
QUICK_COARSE = [10.0 ** k for k in range(-12, -3)]           # tests: one point per decade
QUICK_DENSE = [10.0 ** (-9 + j / 4) for j in range(4)]
RESOLVED_BOUND = 2.1e-10
AJH_TOL = 1e-12
WINDOW_MIN_DECADES = 2.0
PLATEAU_MIN_POINTS, PLATEAU_MAX_RATIO, PLATEAU_MAX_ABS_SLOPE = 5, 10.0, 0.5
ROUNDOFF_MIN_POINTS, ROUNDOFF_SLOPE, ROUNDOFF_MIN_R2, ROUNDOFF_PRED_FACTOR = 8, (-1.3, -0.7), 0.9, 3.0
CONTROL_LARGE_DELTA = 1e-6            # E5's well-resolved population has delta >= 1e-6
SYNTH_LAMBDA = 0.9987382466           # synthetic exact affine branch multiplier (known)
SYNTH_TOL = 1e-10
LOG_FLOOR = 1e-18

NARROWED = "NARROWED_CONSISTENT_WITH_FD_ROUNDOFF"
UNEXPLAINED = "UNEXPLAINED"
INCONCLUSIVE = "INCONCLUSIVE_CONTROLS_FAILED"


# =====================================================================================================================
# loading the pinned operator
# =====================================================================================================================
def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_pins() -> dict:
    got = {k: sha256(REPO / k) for k in PINNED_SHA256}
    bad = {k: v for k, v in got.items() if v != PINNED_SHA256[k]}
    if bad:
        raise RuntimeError(f"pinned input changed, refusing to run: {sorted(bad)}")
    return got


_KCK = None


def load_kck():
    """Import the pinned kappa_cycle_kernel module. Its _common helper requires cwd = repo root (it only mkdirs the
    existing results/ folder at import; this script never calls its dump())."""
    global _KCK
    if _KCK is None:
        os.chdir(REPO)
        sys.path.insert(0, str(SCRIPTS))
        import kappa_cycle_kernel as kck  # noqa: E402  (pinned, read-only)
        _KCK = kck
    return _KCK


def load_frozen_component(spec: dict) -> tuple[dict, dict]:
    D = json.loads(KCK_JSON.read_text())
    rep = [r for r in D["replays"] if r["seed"] == spec["seed"] and r["rho"] == spec["rho"]]
    if len(rep) != 1:
        raise RuntimeError("frozen replay not found exactly once")
    return rep[0], rep[0]["comps"][spec["comp_index"]]


def replay_base(kck, seed: int, rho: float):
    """Exactly job()'s replay lines (kappa_cycle_kernel.py job(), first 4 statements)."""
    cfg = kck.tw.create_model_config(rho)
    prot = kck.tw.create_protocol_config()
    st, _ = kck.engine.simulate_prefix(seed, cfg, prot)
    rng = np.random.default_rng(0)
    for _ in range(int(round(kck.T_TARGET / cfg.dt))):
        kck.engine.advance_state(st, cfg, rng)
    S0 = st.clone()
    R0 = kck.engine.compute_R(S0.clone(), cfg)
    return cfg, S0, R0


# =====================================================================================================================
# mirror of engine v1 advance_state :790-813 (diagnostics only; checked bit-for-bit against step_B on every sample)
# =====================================================================================================================
def pregate(B, R, cfg):
    z = B + cfg.dt * ((cfg.eta + cfg.mu) * R - cfg.mu - cfg.gamma * B)
    x = np.maximum(z, 0.0)
    x = 0.5 * (x + x.T)
    np.fill_diagonal(x, 0.0)
    q = np.sum(x, axis=1)
    g_min = float(np.min(cfg.a - cfg.q * q))
    gate_on = bool(g_min < cfg.delta)
    if gate_on:
        s = np.minimum(1.0, cfg.capacity / (q + cfg.scale_epsilon))
        y = x * np.minimum.outer(s, s)
        np.fill_diagonal(y, 0.0)
    else:
        s = np.ones(len(q))
        y = x
    return dict(z=z, x=x, q=q, g_min=g_min, gate_on=gate_on, s=s, y=y)


def edge_controllers(s, ed, tie_tol):
    ctrl = []
    for i, j in ed:
        g = abs(s[i] - s[j])
        ctrl.append("tie" if g <= tie_tol else int(i if s[i] < s[j] else j))
    return tuple(ctrl)


def branch_signature(B, R, cfg, ed, nodes, kck):
    pg = pregate(B, R, cfg)
    N = len(B)
    iu = np.triu_indices(N, 1)
    clip = frozenset(zip(*[a[pg["x"][iu] == 0.0] for a in iu]))
    supp = frozenset(zip(*[a[B[iu] > kck.SUPP] for a in iu]))
    ctrl = edge_controllers(pg["s"], ed, kck.TIE_TOL)
    gaps = [abs(pg["s"][i] - pg["s"][j]) for i, j in ed]
    tied = [g for g, c in zip(gaps, ctrl) if c == "tie"]
    untied = [g for g, c in zip(gaps, ctrl) if c != "tie"]
    J = sorted({n for (i, j), c in zip(ed, ctrl) for n in ((i, j) if c == "tie" else (c,))})
    sJ = [float(pg["s"][n]) for n in J]
    return dict(gate_on=pg["gate_on"], g_min_pre=pg["g_min"], clip=clip, supp=supp, ctrl=ctrl, J=J,
                max_tied_gap=max(tied) if tied else 0.0, min_untied_gap=min(untied) if untied else None,
                s_spread_J=max(sJ) - min(sJ), s_J=sJ,
                min_positivity_margin=float(min(pg["z"][i, j] for i, j in ed)), n_clipped=len(clip), pg=pg)


# =====================================================================================================================
# exact rational evaluation of the same one-step gate map (higher-precision path)
# =====================================================================================================================
class ExactGate:
    def __init__(self, B, R, cfg, ed, nodes):
        F = Fraction
        self.N = len(B)
        self.B = [[F(float(B[i, j])) for j in range(self.N)] for i in range(self.N)]
        self.R = [[F(float(R[i, j])) for j in range(self.N)] for i in range(self.N)]
        self.dt, self.k1, self.mu, self.gam = F(cfg.dt), F(cfg.eta + cfg.mu), F(cfg.mu), F(cfg.gamma)
        self.a, self.qq, self.dl, self.c, self.eps = F(cfg.a), F(cfg.q), F(cfg.delta), F(cfg.capacity), F(cfg.scale_epsilon)
        self.ed, self.nodes = ed, nodes
        self.one_minus_gdt = 1 - self.dt * self.gam

    def y(self, Bm):
        N = self.N
        z = [[Bm[i][j] + self.dt * (self.k1 * self.R[i][j] - self.mu - self.gam * Bm[i][j]) for j in range(N)] for i in range(N)]
        Z = Fraction(0)   # NB: plain int 0 would make (0 + 0) / 2 a float and silently drop to float64 arithmetic
        x = [[(max(z[i][j], Z) + max(z[j][i], Z)) / 2 if i != j else Z for j in range(N)] for i in range(N)]
        assert all(isinstance(v, Fraction) for row in x for v in row)
        q = [sum(x[i]) for i in range(N)]
        gate = min(self.a - self.qq * qi for qi in q) < self.dl
        s = [min(Fraction(1), self.c / (qi + self.eps)) if gate else Fraction(1) for qi in q]
        return [x[i][j] * min(s[i], s[j]) for i, j in self.ed], s, gate

    def perturbed(self, delta, h, Bfloat_in=None):
        """Bfloat_in given: exact map at the float input the engine received; else ideal B + delta*h (exact)."""
        N = self.N
        if Bfloat_in is not None:
            return [[Fraction(float(Bfloat_in[i, j])) for j in range(N)] for i in range(N)]
        Bm = [row[:] for row in self.B]
        d = Fraction(delta)
        for e, (i, j) in enumerate(self.ed):
            v = d * Fraction(float(h[e]))
            Bm[i][j] += v
            Bm[j][i] += v
        return Bm


# =====================================================================================================================
# measurement on the real engine
# =====================================================================================================================
class EngineFiber:
    def __init__(self, kck, cfg, S0, R0, nodes, direction="fiber", fiber_index=0):
        self.kck, self.cfg, self.S0, self.R0, self.nodes = kck, cfg, S0, R0, nodes
        SUPP = kck.SUPP
        self.ed = [(i, j) for ii, i in enumerate(nodes) for j in nodes[ii + 1:] if S0.B[i, j] > SUPP]
        m = len(self.ed)
        A = np.zeros((len(nodes), m))
        for e, (i, j) in enumerate(self.ed):
            A[nodes.index(i), e] = A[nodes.index(j), e] = 1
        self.sig0 = branch_signature(S0.B, R0, cfg, self.ed, nodes, kck)
        if not self.sig0["gate_on"]:
            raise RuntimeError("gate off at the base state")
        J = self.sig0["J"]
        AJ = A[[nodes.index(i) for i in J]]
        K = kck.nullspace(AJ)
        if direction == "fiber":
            h = K[:, fiber_index]
        else:   # direction = ("onesided", c): v_c of kappa_cycle_kernel.py (+1 opposite c, -1 at c); NOT in ker A_J
            cn = direction[1]
            h = np.array([-1.0 if cn in e else 1.0 for e in self.ed])
        self.h = h / np.linalg.norm(h)
        self.A, self.AJ, self.J, self.kernel_dim = A, AJ, J, K.shape[1]
        self.AJh = float(np.linalg.norm(AJ @ self.h))
        self.Ah = float(np.linalg.norm(A @ self.h))
        self.H = kck.vec2mat(self.h, self.ed)
        self.base = kck.step_B(S0, cfg)
        mask = np.ones(S0.B.shape, bool)
        for i, j in self.ed:
            mask[i, j] = mask[j, i] = False
        self.mask = mask
        c, dt, eta, gam, eps = cfg.capacity, cfg.dt, cfg.eta, cfg.gamma, cfg.scale_epsilon
        k = max(int(sum(S0.B[i, j] > SUPP for j in range(len(S0.B)) if j != i)) for i in nodes)
        self.k = k
        self.lam_closed_form = (1 - gam * dt) * c / (c + dt * (k * eta - gam * c) + eps)
        self.lam_state = (1 - gam * dt) * float(np.mean(self.sig0["s_J"]))
        self.exact = ExactGate(S0.B, R0, cfg, self.ed, nodes)
        self.ex_y0, ex_s0, _ = self.exact.y(self.exact.B)
        hh = sum(Fraction(float(v)) ** 2 for v in self.h)
        sctrl = [min(ex_s0[i], ex_s0[j]) for i, j in self.ed]
        self.lam_exact_branch_formula = float(self.exact.one_minus_gdt * sum(Fraction(float(v)) ** 2 * sc for v, sc in zip(self.h, sctrl)) / hh)

    def freeze(self) -> dict:
        s0 = self.sig0
        cfg = self.cfg
        return dict(nodes=self.nodes, edges=[list(e) for e in self.ed], J=self.J, k=self.k, kernel_dim=self.kernel_dim,
                    h=[float(v) for v in self.h], AJh=self.AJh, Ah=self.Ah, gate_on=s0["gate_on"], g_min_pre=s0["g_min_pre"],
                    controllers=list(s0["ctrl"]), s_nodes={int(n): float(s0["pg"]["s"][n]) for n in self.nodes},
                    s_spread_J=s0["s_spread_J"], max_tied_gap=s0["max_tied_gap"], min_untied_gap=s0["min_untied_gap"],
                    n_clipped_pairs=s0["n_clipped"], min_positivity_margin=s0["min_positivity_margin"],
                    B_component={f"{i}-{j}": float(self.S0.B[i, j]) for i, j in self.ed},
                    rowsum_margin=[float(cfg.capacity - self.S0.B[i].sum()) for i in self.nodes],
                    R_min=float(min(self.R0[i, j] for i, j in self.ed)),
                    lam_state_formula=self.lam_state, lam_closed_form=self.lam_closed_form,
                    lam_exact_branch_formula=self.lam_exact_branch_formula,
                    rel_state_vs_closed_form=abs(self.lam_state - self.lam_closed_form) / self.lam_closed_form,
                    params=dict(capacity=cfg.capacity, dt=cfg.dt, eta=cfg.eta, mu=cfg.mu, gamma=cfg.gamma,
                                scale_epsilon=cfg.scale_epsilon, a=cfg.a, q=cfg.q, delta=cfg.delta, alpha=cfg.alpha,
                                T_window=cfg.T_window))

    def sample(self, delta: float, exact: bool = True) -> dict:
        kck, S0, cfg, ed, h = self.kck, self.S0, self.cfg, self.ed, self.h
        out = dict(delta=float(delta))
        reasons = []
        side = {}
        for sg, name in ((1, "plus"), (-1, "minus")):
            dB = sg * delta * self.H
            Bin = S0.B + dB                                  # what step_B feeds the engine (T.B = T.B + dB)
            Bout = kck.step_B(S0, cfg, dB)
            sig = branch_signature(Bin, self.R0, cfg, ed, self.nodes, kck)
            mirror_diff = float(max(abs(sig["pg"]["y"][i, j] - Bout[i, j]) for i, j in ed))
            if mirror_diff != 0.0:
                raise RuntimeError(f"pregate mirror differs from engine step_B by {mirror_diff} at delta={delta}")
            D = (Bout - self.base) / (sg * delta)            # identical expression to job()
            v = kck.mat2vec(D, ed)
            lam = float(v @ h)
            d_act = kck.mat2vec(Bin - S0.B, ed)              # the perturbation actually represented in float64
            dy = kck.mat2vec(Bout - self.base, ed)
            r = dict(lam=lam, lam_fsum=math.fsum(float(a) * float(b) for a, b in zip(v, h)),
                     lam_input_corrected=float(dy @ d_act / (d_act @ d_act)),
                     rel_residual=float(np.linalg.norm(v - lam * h) / np.linalg.norm(v)),
                     leak=float(np.abs(D[self.mask]).max()), gate_on=sig["gate_on"], g_min_pre=sig["g_min_pre"],
                     n_clipped=sig["n_clipped"], min_positivity_margin=sig["min_positivity_margin"],
                     min_untied_gap=sig["min_untied_gap"], max_tied_gap=sig["max_tied_gap"], s_spread_J=sig["s_spread_J"],
                     s_J_shift=float(max(abs(a - b) for a, b in zip(sig["s_J"], self.sig0["s_J"]))) if sig["J"] == self.sig0["J"] else None,
                     input_repr_rel_err=float(np.linalg.norm(d_act - sg * delta * h) / (delta * np.linalg.norm(h))))
            if not sig["gate_on"]:
                reasons.append(f"{name}:gate_off")
            if sig["clip"] != self.sig0["clip"]:
                reasons.append(f"{name}:clip_pattern_changed")
            if sig["supp"] != self.sig0["supp"]:
                reasons.append(f"{name}:support_changed")
            if sig["ctrl"] != self.sig0["ctrl"]:
                reasons.append(f"{name}:controller_changed")
            if exact:
                Bx = self.exact.perturbed(delta, h, Bfloat_in=Bin)
                yx, _, _ = self.exact.y(Bx)
                Bi = self.exact.perturbed(sg * delta, h)
                yi, _, _ = self.exact.y(Bi)
                Fd, Fh = Fraction(sg * delta), [Fraction(float(t)) for t in h]
                hh = sum(t * t for t in Fh)
                r["lam_exact_float_input"] = float(sum((a - b) * t for a, b, t in zip(yx, self.ex_y0, Fh)) / Fd)
                r["lam_exact_ideal_input"] = float(sum((a - b) * t for a, b, t in zip(yi, self.ex_y0, Fh)) / (Fd * hh))
            side[name] = (r, Bout)
            out[name] = r
        if self.AJh > AJH_TOL:
            reasons.append("direction_not_in_ker_A_J")
        out["admissible"] = not reasons
        out["label"] = "admissible" if not reasons else "branch_crossing:" + ",".join(reasons)
        vc = kck.mat2vec((side["plus"][1] - side["minus"][1]) / (2 * delta), ed)
        out["lam_central"] = float(vc @ h)
        out["pm_asym"] = float(np.linalg.norm(((side["plus"][1] - self.base) / delta) - ((side["minus"][1] - self.base) / -delta))
                               / np.linalg.norm((side["plus"][1] - self.base) / delta))
        for ref_name, ref in (("state", self.lam_state), ("closed_form", self.lam_closed_form)):
            for est, val in (("plus", out["plus"]["lam"]), ("minus", out["minus"]["lam"]), ("central", out["lam_central"]),
                             ("plus_input_corrected", out["plus"]["lam_input_corrected"])):
                out[f"abs_err_{est}_vs_{ref_name}"] = abs(val - ref)
                out[f"rel_err_{est}_vs_{ref_name}"] = abs(val - ref) / ref
            if exact:
                for est in ("lam_exact_float_input", "lam_exact_ideal_input"):
                    out[f"rel_err_plus_{est}_vs_{ref_name}"] = abs(out["plus"][est] - ref) / ref
        out["err"] = out["rel_err_plus_vs_state"]          # primary (decision) metric
        return out


# =====================================================================================================================
# synthetic exact affine branch (control) and its crossing
# =====================================================================================================================
class SyntheticAffine:
    """f(b) = lam * b on the branch u.b < t, and f(b) = lam_alt * b beyond it, for b in R^3 near 0.3 (similar
    magnitude, hence similar float64 rounding, to the real component). u = h, t = u.b0 + crossing, so the +delta side
    leaves the branch at delta = crossing. Exact multiplier along h on the branch: lam."""

    def __init__(self, lam=SYNTH_LAMBDA, lam_alt=0.5, crossing=1e-5):
        self.b0 = np.array([0.3166666666666, 0.2989999999, 0.3133333333])
        h = np.array([1.0, -1.0, -1.0])
        self.h = h / np.linalg.norm(h)
        self.lam, self.lam_alt = lam, lam_alt
        self.t = float(self.h @ self.b0) + crossing
        self.AJh = 0.0

    def f(self, b):
        return (self.lam if self.h @ b < self.t else self.lam_alt) * b

    def sample(self, delta, lam_ref):
        out = dict(delta=float(delta))
        reasons = []
        y0 = self.f(self.b0)
        for sg, name in ((1, "plus"), (-1, "minus")):
            b = self.b0 + sg * delta * self.h
            on = bool(self.h @ b < self.t)
            if not on:
                reasons.append(f"{name}:branch_changed")
            v = (self.f(b) - y0) / (sg * delta)
            out[name] = dict(lam=float(v @ self.h), branch_margin=float(self.t - self.h @ b))
        out["admissible"] = not reasons
        out["label"] = "admissible" if not reasons else "branch_crossing:" + ",".join(reasons)
        out["err"] = abs(out["plus"]["lam"] - lam_ref) / lam_ref
        return out


# =====================================================================================================================
# reporter / decision rule (pure functions of the sample table; never hardcodes the outcome)
# =====================================================================================================================
def _loglog_fit(pts):
    x = np.log10([p["delta"] for p in pts])
    y = np.log10([max(p["err"], LOG_FLOOR) for p in pts])
    if len(pts) < 2 or np.ptp(x) == 0:
        return None, None
    slope, icpt = np.polyfit(x, y, 1)
    ss_res = float(np.sum((y - (slope * x + icpt)) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(slope), float(r2)


def branch_window(points, hist_delta):
    pts = sorted(points, key=lambda p: p["delta"])
    idx = [i for i, p in enumerate(pts) if p["delta"] == hist_delta]
    if not idx or not pts[idx[0]]["admissible"]:
        return None
    lo = hi = idx[0]
    while lo > 0 and pts[lo - 1]["admissible"]:
        lo -= 1
    while hi < len(pts) - 1 and pts[hi + 1]["admissible"]:
        hi += 1
    return pts[lo:hi + 1]


def find_plateaus(coarse_pts):
    found = []
    n = len(coarse_pts)
    for i in range(n):
        for j in range(i + PLATEAU_MIN_POINTS, n + 1):
            run = coarse_pts[i:j]
            e = [max(p["err"], LOG_FLOOR) for p in run]
            slope, _ = _loglog_fit(run)
            med = float(np.median(e))
            if max(e) / min(e) <= PLATEAU_MAX_RATIO and slope is not None and abs(slope) <= PLATEAU_MAX_ABS_SLOPE and med <= RESOLVED_BOUND:
                found.append(dict(delta_lo=run[0]["delta"], delta_hi=run[-1]["delta"], n=len(run), median_err=med, slope=slope))
    # keep maximal runs only
    return [p for p in found if not any(q is not p and q["delta_lo"] <= p["delta_lo"] and q["delta_hi"] >= p["delta_hi"] and q["n"] > p["n"] for q in found)]


def roundoff_model(coarse_pts, hist_delta, hist_err):
    res = dict(n=len(coarse_pts))
    if len(coarse_pts) < 2:
        res.update(ok=False, reason="fewer than 2 coarse points in window")
        return res
    slope, r2 = _loglog_fit(coarse_pts)
    A = float(np.median([p["err"] * p["delta"] for p in coarse_pts]))
    pred = A / hist_delta
    top = max(coarse_pts, key=lambda p: p["delta"])
    res.update(slope=slope, r2=r2, A_median_err_times_delta=A, predicted_hist_err=pred, recorded_hist_err=hist_err,
               pred_over_recorded=pred / hist_err if hist_err else None, top_delta=top["delta"], err_at_top_delta=top["err"])
    checks = dict(enough_points=len(coarse_pts) >= ROUNDOFF_MIN_POINTS,
                  slope_in_range=slope is not None and ROUNDOFF_SLOPE[0] <= slope <= ROUNDOFF_SLOPE[1],
                  r2_ok=r2 is not None and r2 >= ROUNDOFF_MIN_R2,
                  predicts_hist=bool(hist_err) and 1 / ROUNDOFF_PRED_FACTOR <= pred / hist_err <= ROUNDOFF_PRED_FACTOR,
                  closes_on_branch=top["err"] <= RESOLVED_BOUND)
    res["checks"] = checks
    res["ok"] = all(checks.values())
    return res


def decide(points, hist_delta, hist_err, controls_ok, exact_key="rel_err_plus_lam_exact_ideal_input_vs_state", coarse=None):
    """Return dict(label, reasons, evidence). points: sample dicts with delta, admissible, err and optionally exact_key.
    coarse: the set of coarse-grid deltas (default: all points)."""
    rep = dict(reasons=[], evidence={})
    W = branch_window(points, hist_delta)
    cset = set(coarse) if coarse is not None else {p["delta"] for p in points}
    n_cross = sum(1 for p in points if not p["admissible"])
    rep["evidence"]["n_points"] = len(points)
    rep["evidence"]["n_branch_crossing"] = n_cross
    if not controls_ok:
        rep["label"] = INCONCLUSIVE
        rep["reasons"].append("one or more required controls failed (fail closed)")
        return rep
    if W is None:
        rep["label"] = UNEXPLAINED
        rep["reasons"].append("C2: historical delta is not an admissible (same-branch) sample")
        return rep
    decades = math.log10(W[-1]["delta"] / W[0]["delta"])
    rep["evidence"]["window"] = dict(delta_lo=W[0]["delta"], delta_hi=W[-1]["delta"], decades=decades, n=len(W))
    cw = [p for p in W if p["delta"] in cset]
    plateaus = find_plateaus(cw)
    rm = roundoff_model(cw, hist_delta, hist_err)
    rep["evidence"]["plateaus"] = plateaus
    rep["evidence"]["roundoff_model"] = rm
    ok = True
    if decades < WINDOW_MIN_DECADES:
        ok = False
        rep["reasons"].append(f"C3: branch window spans {decades:.2f} < {WINDOW_MIN_DECADES} decades")
    if not plateaus and not rm["ok"]:
        ok = False
        rep["reasons"].append("C4: no plateau and no roundoff model on the branch window")
    ex = [p.get(exact_key) for p in W]
    if any(v is None for v in ex):
        ok = False
        rep["reasons"].append("C5: exact branch multiplier not evaluated on the whole window")
    else:
        rep["evidence"]["max_exact_rel_err_on_window"] = max(ex)
        if max(ex) > RESOLVED_BOUND:
            ok = False
            rep["reasons"].append("C5: exact branch multiplier differs from the state formula by more than RESOLVED_BOUND")
    rep["evidence"]["C4_basis"] = "plateau" if plateaus else ("roundoff_model" if rm["ok"] else None)
    rep["label"] = NARROWED if ok else UNEXPLAINED
    return rep


def validate_report(report: dict) -> None:
    """Reject a report whose label is not what decide() returns on its own stored samples (e.g. a hand-edited
    'explained' label, or a claim without the admissibility / plateau evidence)."""
    t = report.get("target_sweep")
    if not t or "samples" not in t:
        raise ValueError("report has no target sample table")
    for p in t["samples"]:
        if "admissible" not in p or "label" not in p:
            raise ValueError("sample without admissibility check")
    ctrl_ok = bool(report.get("controls", {}).get("all_pass"))
    again = decide(t["samples"], t["hist_delta"], t["hist_err"], ctrl_ok, coarse=t["coarse_grid"])
    if again["label"] != report.get("decision", {}).get("label"):
        raise ValueError(f"decision label {report.get('decision', {}).get('label')!r} does not follow from the samples ({again['label']!r})")
    if again["label"] == NARROWED and again["evidence"].get("C4_basis") is None:
        raise ValueError("NARROWED without a plateau or roundoff model")


# =====================================================================================================================
# orchestration
# =====================================================================================================================
def grid(quick=False, hist=TARGET["delta"]):
    c = QUICK_COARSE if quick else COARSE
    d = QUICK_DENSE if quick else DENSE
    return c, sorted(set(c) | set(d) | {hist})


def run_synthetic(lam_ref=SYNTH_LAMBDA, quick=False):
    syn = SyntheticAffine()
    c, g = grid(quick)
    pts = [syn.sample(d, lam_ref) for d in g]
    W = branch_window(pts, TARGET["delta"])
    top = max(W, key=lambda p: p["delta"]) if W else None
    crossed = [p for p in pts if not p["admissible"]]
    res = dict(lam_true=syn.lam, lam_ref=lam_ref, crossing_delta=1e-5,
               window=[W[0]["delta"], W[-1]["delta"]] if W else None,
               top_err=top["err"] if top else None,
               n_crossed=len(crossed), crossed_min_delta=min(p["delta"] for p in crossed) if crossed else None,
               crossed_max_err=max(p["err"] for p in crossed) if crossed else None,
               samples=pts)
    res["recovers_lambda"] = bool(top is not None and top["err"] <= SYNTH_TOL)
    res["crossings_rejected"] = bool(crossed) and all(p["delta"] >= 1e-5 * 0.99 for p in crossed) and all(
        p["admissible"] for p in pts if p["delta"] < 1e-5 * 0.99)
    res["pass"] = res["recovers_lambda"] and res["crossings_rejected"]
    return res


def run(quick=False, exact=True, verbose=True):
    pins = check_pins()
    kck = load_kck()
    rep_t, comp_t = load_frozen_component(TARGET)
    _, comp_c = load_frozen_component(CONTROL)
    for key in ("nodes", "J", "delta", "rel_err_lam_vs_state", "rel_err_lam_vs_closed_form", "kernel_dim"):
        if comp_t[key] != TARGET[key]:
            raise RuntimeError(f"frozen target field {key} differs from the brief: {comp_t[key]} != {TARGET[key]}")
    log = (lambda *a: print(*a, flush=True)) if verbose else (lambda *a: None)
    log("running pinned kappa_cycle_kernel.job for the witness ...")
    job = kck.job((TARGET["seed"], TARGET["rho"]))
    jt, jc = job["comps"][TARGET["comp_index"]], job["comps"][CONTROL["comp_index"]]
    cfg, S0, R0 = replay_base(kck, TARGET["seed"], TARGET["rho"])
    tgt = EngineFiber(kck, cfg, S0, R0, TARGET["nodes"])
    ctl = EngineFiber(kck, cfg, S0, R0, CONTROL["nodes"], fiber_index=CONTROL["fiber_index"])
    off = EngineFiber(kck, cfg, S0, R0, TARGET["nodes"], direction=("onesided", 2))
    hist_delta = jt["delta"]
    coarse, g = grid(quick, hist_delta)
    # ---- target sweep
    log(f"target sweep: {len(g)} deltas x 2 signs")
    samples = [tgt.sample(d, exact=exact) for d in g]
    hist = next(p for p in samples if p["delta"] == hist_delta)
    witness = dict(
        job_delta=jt["delta"], job_lam=jt["fiber"][0]["lam"], sweep_lam_at_hist=hist["plus"]["lam"],
        bit_identical=hist["plus"]["lam"] == jt["fiber"][0]["lam"],
        job_rel_err_lam_vs_state=jt["rel_err_lam_vs_state"], sweep_rel_err_at_hist=hist["err"],
        job_rel_err_lam_vs_closed_form=jt["rel_err_lam_vs_closed_form"],
        job_rel_residual=jt["fiber"][0]["rel_residual"], sweep_rel_residual=hist["plus"]["rel_residual"],
        job_pm_asym=jt["fiber"][0]["pm_asym"], sweep_pm_asym=hist["pm_asym"],
        job_lam_state=jt["lam_state_formula"], sweep_lam_state=tgt.lam_state,
        job_lam_closed_form=jt["lam_closed_form"], sweep_lam_closed_form=tgt.lam_closed_form,
        stored_10sig=dict(delta=comp_t["delta"], rel_err_lam_vs_state=comp_t["rel_err_lam_vs_state"],
                          rel_err_lam_vs_closed_form=comp_t["rel_err_lam_vs_closed_form"], lam=comp_t["fiber"][0]["lam"]),
        job_matches_stored_10sig=all(float(f"{jt[k]:.10g}") == comp_t[k] for k in ("delta", "rel_err_lam_vs_state", "rel_err_lam_vs_closed_form", "s_spread_J", "R_min")),
    )
    witness["ok"] = bool(witness["bit_identical"] and witness["job_matches_stored_10sig"] and witness["sweep_lam_state"] == witness["job_lam_state"]
                         and witness["sweep_rel_residual"] == witness["job_rel_residual"])
    # ---- control: well-resolved fiber, same replay
    log("control sweep (well-resolved K5 fiber) ...")
    csamples = [ctl.sample(d, exact=exact) for d in g]
    c_hist = next(p for p in csamples if p["delta"] == CONTROL["delta"]) if CONTROL["delta"] in g else ctl.sample(CONTROL["delta"], exact=exact)
    c_rec_err = abs(jc["fiber"][CONTROL["fiber_index"]]["lam"] - jc["lam_state_formula"]) / jc["lam_state_formula"]
    c_large = [p for p in csamples if p["delta"] >= CONTROL_LARGE_DELTA]
    c_dec = decide(csamples, CONTROL["delta"], c_rec_err, True, coarse=coarse)
    control = dict(
        component=dict(nodes=ctl.nodes, J=ctl.J, kernel_dim=ctl.kernel_dim, fiber_index=CONTROL["fiber_index"], AJh=ctl.AJh,
                       lam_state=ctl.lam_state, stored_rel_err_lam_vs_state_mean_over_fiber=comp_c["rel_err_lam_vs_state"]),
        witness_lam_job=jc["fiber"][CONTROL["fiber_index"]]["lam"], witness_lam_sweep=c_hist["plus"]["lam"],
        witness_bit_identical=c_hist["plus"]["lam"] == jc["fiber"][CONTROL["fiber_index"]]["lam"],
        recorded_fiber_rel_err_vs_state=c_rec_err,
        all_large_delta_admissible=all(p["admissible"] for p in c_large),
        max_err_large_delta=max(p["err"] for p in c_large) if c_large else None,
        decision=c_dec, samples=csamples)
    control["pass"] = bool(control["witness_bit_identical"] and control["all_large_delta_admissible"] and c_large
                           and control["max_err_large_delta"] <= RESOLVED_BOUND and c_dec["label"] == NARROWED)
    # ---- crossed-boundary controls
    log("crossed-boundary controls ...")
    osamples = [off.sample(d, exact=False) for d in coarse]
    crossed_target = [p for p in samples if not p["admissible"]]
    crossing = dict(
        off_fiber_direction=dict(direction="one-sided v_2 (not in ker A_J)", AJh=off.AJh,
                                 n=len(osamples), n_rejected=sum(not p["admissible"] for p in osamples),
                                 lam_at_hist_like=[(p["delta"], p["plus"]["lam"]) for p in osamples][:3]),
        target_large_delta=dict(n_rejected=len(crossed_target),
                                min_rejected_delta=min((p["delta"] for p in crossed_target), default=None),
                                labels=sorted({p["label"] for p in crossed_target}),
                                max_err_rejected=max((p["err"] for p in crossed_target), default=None)))
    crossing["off_fiber_all_rejected"] = crossing["off_fiber_direction"]["n_rejected"] == len(osamples)
    ad = [p["delta"] for p in samples if p["admissible"]]
    crossing["target_rejections_contiguous_above_window"] = bool(crossed_target) and min(p["delta"] for p in crossed_target) > max(
        (d for d in ad if d < min(p["delta"] for p in crossed_target)), default=0.0) and all(
        not p["admissible"] for p in samples if p["delta"] >= min(p2["delta"] for p2 in crossed_target))
    crossing["pass"] = bool(crossing["off_fiber_all_rejected"] and crossing["target_rejections_contiguous_above_window"])
    # ---- synthetic
    log("synthetic affine controls ...")
    syn = run_synthetic(quick=quick)
    syn_mut = run_synthetic(lam_ref=SYNTH_LAMBDA * (1 + 1e-8), quick=quick)
    synthetic = dict(true=dict({k: v for k, v in syn.items() if k != "samples"}),
                     mutated_reference=dict({k: v for k, v in syn_mut.items() if k != "samples"}))
    synthetic["pass"] = bool(syn["pass"] and not syn_mut["recovers_lambda"])
    # ---- known-false fixtures through the same decide()
    kf = known_false_fixtures()
    controls = dict(witness=witness["ok"], well_resolved=control["pass"], synthetic=synthetic["pass"],
                    crossed_boundary=crossing["pass"], known_false_rejected=kf["all_rejected"])
    controls["all_pass"] = all(controls.values())
    dec = decide(samples, hist_delta, TARGET["rel_err_lam_vs_state"], controls["all_pass"], coarse=coarse)
    # error-vs-delta summary for both references
    adm = [p for p in samples if p["admissible"]]
    summary = dict(
        n_samples=len(samples), n_admissible=len(adm), n_branch_crossing=len(samples) - len(adm),
        max_admissible_delta=max(p["delta"] for p in adm), min_admissible_delta=min(p["delta"] for p in adm),
        rows=[dict(delta=p["delta"], admissible=p["admissible"], rel_err_plus_vs_state=p["rel_err_plus_vs_state"],
                   rel_err_plus_vs_closed_form=p["rel_err_plus_vs_closed_form"], rel_err_minus_vs_state=p["rel_err_minus_vs_state"],
                   rel_err_central_vs_state=p["rel_err_central_vs_state"],
                   rel_err_input_corrected_vs_state=p["rel_err_plus_input_corrected_vs_state"],
                   rel_err_exact_float_input_vs_state=p.get("rel_err_plus_lam_exact_float_input_vs_state"),
                   rel_err_exact_ideal_vs_state=p.get("rel_err_plus_lam_exact_ideal_input_vs_state"),
                   rel_err_exact_ideal_vs_closed_form=p.get("rel_err_plus_lam_exact_ideal_input_vs_closed_form"),
                   input_repr_rel_err_plus=p["plus"]["input_repr_rel_err"], label=p["label"]) for p in samples if p["delta"] in set(coarse) or p["delta"] == hist_delta])
    for key in ("rel_err_minus_vs_state", "rel_err_central_vs_state", "rel_err_plus_input_corrected_vs_state", "rel_err_plus_vs_closed_form"):
        pts = [dict(delta=p["delta"], err=p[key]) for p in adm if p["delta"] in set(coarse)]
        s_, r2_ = _loglog_fit(pts)
        summary[f"loglog_slope_{key}"] = s_
        summary[f"loglog_r2_{key}"] = r2_
    report = dict(
        schema="aiefs-research-rate-law-delta-sweep/1", script="research/rate_law/rate_law_delta_sweep_v1.py",
        quick=quick, numpy=np.__version__, python=sys.version.split()[0], pinned_inputs_sha256=pins,
        frozen_target=dict(spec=TARGET, stored_record={k: v for k, v in comp_t.items() if k != "K3_one_sided"},
                           replay=dict(seed=rep_t["seed"], rho=rep_t["rho"], T_w=rep_t["T_w"], r_g=rep_t["r_g"], gate_on=rep_t["gate_on"]),
                           T_TARGET=kck.T_TARGET, TIE_TOL=kck.TIE_TOL, SUPP=kck.SUPP, D_MIN=kck.D_MIN, D_MAX=kck.D_MAX,
                           base=tgt.freeze()),
        predeclared=dict(coarse_grid=coarse, dense_grid=[d for d in g if d not in set(coarse)], RESOLVED_BOUND=RESOLVED_BOUND,
                         AJH_TOL=AJH_TOL, WINDOW_MIN_DECADES=WINDOW_MIN_DECADES, PLATEAU=[PLATEAU_MIN_POINTS, PLATEAU_MAX_RATIO, PLATEAU_MAX_ABS_SLOPE],
                         ROUNDOFF=[ROUNDOFF_MIN_POINTS, list(ROUNDOFF_SLOPE), ROUNDOFF_MIN_R2, ROUNDOFF_PRED_FACTOR],
                         CONTROL_LARGE_DELTA=CONTROL_LARGE_DELTA, SYNTH_TOL=SYNTH_TOL, primary_metric="rel_err_plus_vs_state"),
        witness=witness, control_well_resolved={k: v for k, v in control.items() if k != "samples"},
        control_crossed_boundary=crossing, control_synthetic=synthetic, control_known_false=kf, controls=controls,
        target_sweep=dict(hist_delta=hist_delta, hist_err=TARGET["rel_err_lam_vs_state"], coarse_grid=coarse, samples=samples),
        control_samples=csamples, summary=summary, decision=dec)
    validate_report(report)
    return report


def known_false_fixtures():
    """Error tables that must NOT be accepted by decide()."""
    hd, he = TARGET["delta"], TARGET["rel_err_lam_vs_state"]
    c, g = grid(False, hd)
    cases = {}
    # (a) no plateau / flat at the historical gap, one cherry-picked tiny value
    pts = [dict(delta=d, admissible=True, err=he if d != 1e-6 else 1e-13, x=1e-13) for d in g]
    for p in pts:
        p["ex"] = 1e-13
    cases["flat_gap_one_cherry_picked_point"] = decide(pts, hd, he, True, exact_key="ex", coarse=c)["label"]
    # (b) perfect 1/delta roundoff but every point above the historical delta crosses the branch
    pts = [dict(delta=d, admissible=d <= hd, err=2.2e-17 / d, ex=1e-13) for d in g]
    cases["roundoff_but_branch_crossed_above_hist"] = decide(pts, hd, he, True, exact_key="ex", coarse=c)["label"]
    # (c) perfect roundoff and branch, but exact multiplier disagrees (a real branch-level gap)
    pts = [dict(delta=d, admissible=True, err=2.2e-17 / d, ex=2e-8) for d in g]
    cases["roundoff_but_exact_multiplier_off"] = decide(pts, hd, he, True, exact_key="ex", coarse=c)["label"]
    # (d) everything fine but controls failed
    pts = [dict(delta=d, admissible=True, err=2.2e-17 / d, ex=1e-13) for d in g]
    cases["controls_failed"] = decide(pts, hd, he, False, exact_key="ex", coarse=c)["label"]
    # (e) historical delta itself not admissible
    pts = [dict(delta=d, admissible=d != hd, err=2.2e-17 / d, ex=1e-13) for d in g]
    cases["hist_delta_not_on_branch"] = decide(pts, hd, he, True, exact_key="ex", coarse=c)["label"]
    # positive fixture (sanity: the rule CAN say narrowed)
    pts = [dict(delta=d, admissible=True, err=2.2e-17 / d, ex=1e-13) for d in g]
    pos = decide(pts, hd, he, True, exact_key="ex", coarse=c)["label"]
    return dict(cases=cases, positive_fixture=pos,
                all_rejected=all(v != NARROWED for v in cases.values()) and pos == NARROWED)


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (frozenset, set)):
        return sorted(_jsonable(v) for v in o)
    return o


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true", help="one coarse point per decade (tests)")
    ap.add_argument("--no-exact", action="store_true", help="skip the exact rational path")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    rep = run(quick=a.quick, exact=not a.no_exact)
    out = Path(a.out)
    if out.resolve().is_relative_to((REPO / "AI Agent Audits").resolve()):
        sys.exit("refusing to write under 'AI Agent Audits/' (frozen evidence)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(_jsonable(rep), indent=1, sort_keys=False) + "\n")
    d = rep["decision"]
    print("controls:", json.dumps(rep["controls"]))
    print("decision:", d["label"], "|", "; ".join(d["reasons"]) or "-")
    print("window:", json.dumps(d["evidence"].get("window")))
    print("roundoff model:", json.dumps({k: v for k, v in d["evidence"].get("roundoff_model", {}).items()}))
    print("plateaus:", json.dumps(d["evidence"].get("plateaus")))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
