"""H12 red team: does the LeanPool-style joint energy decrease along the AIEFS engine in a non-degenerate regime?

Candidate energy (the LeanPool `hebbianL` shape mapped to AIEFS; c = eta + mu; theta unwrapped, tau = 0):
    E(theta, B) = -sum_i w_i theta_i - sum_{i<j} B_ij cos(theta_j - theta_i) + (1/c) sum_{i<j} (mu B_ij + gamma B_ij^2 / 2)
where w_i is the frequency used in the rotating frame (w = omega for regime A; w = 0 after removing the common
frequency for regime B). If the weight drive were c*cos(theta_j - theta_i), the engine's tau = 0 vector field F
would be a (scaled) negative gradient of E and dE/dt = grad E . F <= 0 exactly. AIEFS uses (eta+mu) R_ij with R the
modulus of a complex EMA instead. We evaluate the exact continuous-time rate s = grad E . F at engine states (no
discretisation error), with F_B projected to 0 where B_ij = 0 and F_B < 0 (the engine's clip).

The trajectory is produced by a COPY of the SHA-locked engine (sha256 checked; the pinned file is never imported or
edited). tau = 0 is set with dataclasses.replace on the config; ModelConfig.validate() would reject tau = 0, so this is
a red-team regime outside the engine's validated domain (disclosed). Only steps before the first gate trigger count
("gate inactive"). Stdlib + numpy. Run under `unshare -rn`.
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "aief_experiment_engine_v1.py"
ENGINE_SHA256 = "ca4593fda86a1b0a"  # prefix; full value checked against the registry pin below
SEEDS = range(5)
STEPS = 9000          # > 5 * T_window / dt = 8751 (EMA warm-up)
WARMUP = 8751
REL_TOL = 1e-9        # s counts as an increase iff s > REL_TOL * (|grad E| * |F|)

# Predeclared before the first run (commit 1). Outcome vocabulary: INCREASE FOUND / NO INCREASE / NOT REACHED.
PREDECLARED = {
    "M600_engine_identical_omega_all_steps": "INCREASE FOUND",
    "M601_engine_identical_omega_after_warmup": "NOT REACHED",  # gate expected to fire (~1e3 steps) before warm-up
    "M602_engine_production_omega_all_steps": "NO INCREASE",
    "N600_control_weight_drive_is_cos": "NO INCREASE",
    "N601_control_weight_drive_is_minus_cos": "INCREASE FOUND",
}


def load_engine_copy():
    data = ENGINE.read_bytes()
    full = hashlib.sha256(data).hexdigest()
    assert full.startswith(ENGINE_SHA256), full
    tmp = Path(tempfile.mkdtemp(prefix="h12_engine_copy_"))
    copy = tmp / "aief_engine_copy_h12.py"
    shutil.copyfile(ENGINE, copy)
    spec = importlib.util.spec_from_file_location("aief_engine_copy_h12", copy)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod, full


def rate(theta, B, R, w, cfg, drive):
    """grad E . F at the state. drive in {'engine', 'cos', 'minus_cos'} selects the weight drive in F."""
    c = cfg.eta + cfg.mu
    d = theta[None, :] - theta[:, None]                 # d[i, j] = theta_j - theta_i
    F_th = np.asarray(cfg.omega) - np.mean(cfg.omega) * (w is None) + np.sum(B * np.sin(d), axis=1)
    if drive == "engine":
        W = c * R
    elif drive == "cos":
        W = c * np.cos(d)
    else:
        W = -c * np.cos(d)
    F_B = W - cfg.mu - cfg.gamma * B
    np.fill_diagonal(F_B, 0.0)
    F_B = np.where((B <= 0.0) & (F_B < 0.0), 0.0, F_B)
    w_vec = np.zeros_like(theta) if w is None else w
    # dE/dtheta_i = -w_i + sum_j B_ij sin(theta_i - theta_j) = -w_i - sum_j B_ij sin(d_ij)
    g_th = -w_vec - np.sum(B * np.sin(d), axis=1)
    g_B = -np.cos(d) + (cfg.mu + cfg.gamma * B) / c       # per unordered pair (i<j)
    iu = np.triu_indices(len(theta), 1)
    s = float(g_th @ F_th + np.sum(g_B[iu] * F_B[iu]))
    scale = float(np.sqrt(g_th @ g_th + np.sum(g_B[iu] ** 2)) * np.sqrt(F_th @ F_th + np.sum(F_B[iu] ** 2)))
    return s, scale


def trajectory(mod, cfg, seed, frame, drive, steps=STEPS):
    """Yield (step, s, scale) at engine states before the first gate trigger."""
    state = mod.initialize_state(seed, cfg)
    rng = np.random.default_rng(seed)
    unwrapped = state.theta.copy()
    captured = {}
    orig = mod.compute_R

    def spy(st, cf):
        R = orig(st, cf)
        captured["R"] = R
        return R

    mod.compute_R = spy
    try:
        for n in range(steps):
            th_before = state.theta.copy()
            B_before = state.B.copy()
            _, _, info = mod.advance_state(state, cfg, rng)
            if info["pre_violation"]:
                return
            w = None if frame == "rotating" else np.asarray(cfg.omega)
            if frame == "rotating":
                th_frame = unwrapped - np.mean(cfg.omega) * n * cfg.dt
            else:
                th_frame = unwrapped
            s, scale = rate(th_frame, B_before, captured["R"], w, cfg, drive)
            yield n, s, scale
            step = np.mod(state.theta - th_before + np.pi, 2 * np.pi) - np.pi
            unwrapped = unwrapped + step
    finally:
        mod.compute_R = orig


def evaluate(mod, cfg, frame, drive, start=0):
    worst = None
    counted = 0
    increases = 0
    for seed in SEEDS:
        for n, s, scale in trajectory(mod, cfg, seed, frame, drive):
            if n < start:
                continue
            counted += 1
            if s > REL_TOL * scale:
                increases += 1
                if worst is None or s > worst[2]:
                    worst = (seed, n, s, scale)
    if counted == 0:
        return "NOT REACHED", dict(counted=0)
    out = "INCREASE FOUND" if increases else "NO INCREASE"
    return out, dict(counted=counted, increases=increases, worst=worst)


def run(verbose=True):
    mod, full = load_engine_copy()
    base = dataclasses.replace(mod.DEFAULT_MODEL_CONFIG, tau=0.0)
    assert base.delay_steps == 0 and 0.0 < base.alpha < 1.0
    ident = dataclasses.replace(base, omega=tuple([float(np.mean(base.omega))] * base.N))
    cases = {
        "M600_engine_identical_omega_all_steps": (ident, "rotating", "engine", 0),
        "M601_engine_identical_omega_after_warmup": (ident, "rotating", "engine", WARMUP),
        "M602_engine_production_omega_all_steps": (base, "lab", "engine", 0),
        "N600_control_weight_drive_is_cos": (ident, "rotating", "cos", 0),
        "N601_control_weight_drive_is_minus_cos": (ident, "rotating", "minus_cos", 0),
    }
    results = {}
    for name, (cfg, frame, drive, start) in cases.items():
        results[name] = evaluate(mod, cfg, frame, drive, start)
        if verbose:
            got, det = results[name]
            print(f"{name}: {got} (predeclared {PREDECLARED[name]}) {det}")
    if verbose:
        print("engine copy sha256:", full, "alpha:", base.alpha)
    return results


if __name__ == "__main__":
    res = run()
    ok = all(res[k][0] == v for k, v in PREDECLARED.items())
    print("RESULT:", "AS PREDECLARED" if ok else "DEVIATION(S) - see above")
