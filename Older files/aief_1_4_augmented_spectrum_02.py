#!/usr/bin/env python3

"""
AIEF-1.4 Augmented Spectral Audit (v2 — Fundamental-State Restriction)

Tests: Does the true augmented phase–history–weight–EMA linearization
      have any eigenvalue between r_EMA (0.057) and mu_phase (0.690)?

Method: Finite-difference Jacobian of the production one-step map,
        restricted to the FUNDAMENTAL K3 state variables only:

  h_old_i   (i=2,7,11)               — oldest history deque entry  [3 vars]
  B_e       (e=25,29,59)             — undirected edge weights     [3 vars]
  C_dir     (6 directed edges)       — EMA coherence real+imag    [12 vars]
                                     Total:                        18 vars

theta_i is NOT independently perturbed — it is derived from the phase_factor,
which the production code computes from history and model parameters.
Perturbing theta independently would create off-manifold states.

After perturbing the fundamental variables, the production code's
base_intermediates + advance_base_state are called to obtain the one-step
response.  The resulting 18x18 Jacobian has no coordinate redundancy.

If no eigenvalue has rate in (0.057, 0.690), alpha is the unique slow pole
of the true augmented dynamics on this replay.

Evidence class: diagnostic mechanism exploration.
"""

from __future__ import annotations

import argparse, copy, hashlib, json, math, os, sys, tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_augmented_spectrum"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_PERTURBATION = 1e-8

K3_NODES = [2, 7, 11]
K3_EDGE_LIST = [(2,7,25), (2,11,29), (7,11,59)]
DIRECTED_PAIRS = [(2,7),(7,2),(2,11),(11,2),(7,11),(11,7)]

def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as h:
        while b := h.read(1024*1024):
            d.update(b)
    return d.hexdigest()

def compute_module_sha256(m):
    if m is None or not hasattr(m, "__file__") or m.__file__ is None:
        return "not_available"
    return file_sha256(Path(m.__file__).resolve())

def load_production_modules():
    import AIEF_1_4_stationarity_perturbation_analysis_updated as base
    import AIEF_1_4_component_controller_audit as ca
    import AIEF_1_4_augmented_tangent_cocycle_analysis as aug
    return base, ca, aug

def safe_atomic_write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tp = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(tp, path)
    except Exception:
        if os.path.exists(tp): os.remove(tp)
        raise

def safe_atomic_write_csv(path, df):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tp = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False); f.flush(); os.fsync(f.fileno())
        os.replace(tp, path)
    except Exception:
        if os.path.exists(tp): os.remove(tp)
        raise

# ---------------------------------------------------------------------------
# State snapshot / restore (fundamental variables only)
# ---------------------------------------------------------------------------

def snapshot_state(state):
    """Deep-copy the mutable K3 portions of a DynamicState."""
    history_list = list(state.history)
    return {
        "B": state.B.copy(),
        "coherence_acc": state.coherence_acc.copy(),
        "history": [entry.copy() for entry in history_list],
    }

def restore_state(state, snap):
    """Restore K3 state from snapshot."""
    state.B[:] = snap["B"]
    state.coherence_acc[:] = snap["coherence_acc"]
    state.history.clear()
    for entry in snap["history"]:
        state.history.append(entry.copy())

# ---------------------------------------------------------------------------
# Extraction / injection of 18 fundamental K3 variables
# ---------------------------------------------------------------------------

def extract_fundamental_vars(state):
    """
    Extract fundamental K3 variables:
      h_old_i  (3),  B_e (3),  C real+imag (12)  -> 18-vector.
    theta is NOT extracted — it is derived from phase_factor.
    """
    history_list = list(state.history)
    h_old = history_list[0] if len(history_list) > 0 else np.zeros(len(state.B))

    B_mat = state.B
    C_mat = state.coherence_acc

    vec = []
    # h_old for K3 nodes
    for i in K3_NODES:
        vec.append(float(h_old[i]))
    # B for K3 edges (undirected, symmetric — perturb one sets both)
    for _, _, e in K3_EDGE_LIST:
        ia, ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        vec.append(float(B_mat[ia, ib]))
    # C real+imag for 6 directed edges
    for ia, ib in DIRECTED_PAIRS:
        c = C_mat[ia, ib]
        vec.append(float(c.real))
        vec.append(float(c.imag))
    return np.array(vec)

def inject_fundamental_vars(state, vec):
    """Write the 18-vector back into the K3 portions of the state."""
    B_mat = state.B
    C_mat = state.coherence_acc

    idx = 0
    # h_old
    h_old_vals = {}
    for i in K3_NODES:
        h_old_vals[i] = vec[idx]; idx += 1

    # Update the oldest history entry for K3 nodes only
    history_list = list(state.history)
    if len(history_list) > 0:
        oldest = history_list[0].copy()
        for i in K3_NODES:
            oldest[i] = h_old_vals[i]
        history_list[0] = oldest
        state.history.clear()
        for entry in history_list:
            state.history.append(entry)

    # B (undirected — set both directions)
    for _, _, e in K3_EDGE_LIST:
        ia, ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        val = vec[idx]; idx += 1
        B_mat[ia, ib] = val
        B_mat[ib, ia] = val
    # C
    for ia, ib in DIRECTED_PAIRS:
        re = vec[idx]; im = vec[idx+1]; idx += 2
        C_mat[ia, ib] = complex(re, im)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--npz", default=DEFAULT_NPZ)
    p.add_argument("--manifest", default=DEFAULT_MANIFEST)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--seed", default=DEFAULT_SEED)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    p.add_argument("--perturbation", type=float, default=DEFAULT_PERTURBATION)
    return p.parse_args()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing: {path}")

    base, ca, aug = load_production_modules()
    with open(args.manifest) as h:
        manifest = json.load(h)
    model = manifest["model"]
    dt = float(model["dt"])
    alpha = math.exp(-dt/float(model["T_window"]))
    r_ema = -np.log(alpha)/dt

    cap = (float(model["a"])-float(model["delta"]))/float(model["q"])
    caps = np.full(int(model["N"]), cap)
    N = int(model["N"])
    A, edges_mat = base.incidence_matrix(N)
    fs = int(manifest["protocol"]["future_steps"])
    eps_sc = args.scale_epsilon
    pert = args.perturbation

    # ---- Replay to final step ----
    print("Replaying to final time step...")
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)

    print(f"At final step t={fs*dt:.0f}.  Building augmented Jacobian...")

    # ---- Baseline: one full production step from current state ----
    # Snapshot at step fs (before the hypothetical next step)
    snap_fs = snapshot_state(state)

    # Advance one step from the snapshot to get the baseline response
    inter_base = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_base)
    # Extract post-step state
    vec_after_baseline = extract_fundamental_vars(state)

    n_vars = len(vec_after_baseline)
    print(f"  Fundamental state dimension: {n_vars}")
    print(f"  (3 h_old + 3 B + 12 C_realimag)")
    print(f"  theta NOT included — it is derived, not fundamental.")

    # ---- Jacobian via finite differences ----
    J = np.zeros((n_vars, n_vars))

    for col in range(n_vars):
        # Restore snapshot
        restore_state(state, snap_fs)

        # Extract current fundamental vars
        vec_current = extract_fundamental_vars(state)

        # Perturb one variable
        delta = pert * max(1.0, abs(vec_current[col]))
        vec_current[col] += delta

        # Inject perturbed state
        inject_fundamental_vars(state, vec_current)

        # Advance one step
        inter_p = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter_p)
        vec_pert_after = extract_fundamental_vars(state)

        # Jacobian column
        J[:, col] = (vec_pert_after - vec_after_baseline) / delta

        if (col + 1) % 4 == 0 or col == n_vars - 1:
            print(f"  Column {col+1}/{n_vars} done")

    # ---- Analyze eigenvalues ----
    evals = np.linalg.eigvals(J)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300)) / dt

    sorted_idx = np.argsort(rates)
    sorted_evals = evals[sorted_idx]
    sorted_rates = rates[sorted_idx]
    sorted_abs = abs_evals[sorted_idx]

    # Filter out numerical zeros and extremely fast modes
    relevant = (sorted_abs > 1e-14) & (sorted_rates < 100.0)

    # Gap check
    mu_phase_ref = 0.689918
    gap_lower = r_ema
    gap_upper = mu_phase_ref
    in_gap = (sorted_rates > gap_lower) & (sorted_rates < gap_upper) & relevant
    n_in_gap = int(np.sum(in_gap))

    # Also find eigenvalues near r_EMA (within 10%)
    near_ema = (sorted_rates > r_ema * 0.9) & (sorted_rates < r_ema * 1.1) & relevant
    n_near_ema = int(np.sum(near_ema))

    # ---- Output ----
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)

    eval_rows = []
    for i in range(n_vars):
        if relevant[i]:
            eval_rows.append({
                "index": i,
                "eval_real": float(sorted_evals[i].real),
                "eval_imag": float(sorted_evals[i].imag),
                "abs_eval": float(sorted_abs[i]),
                "rate": float(sorted_rates[i]),
                "in_gap": bool(in_gap[i]),
                "near_ema": bool(near_ema[i]),
            })
    eval_df = pd.DataFrame(eval_rows)
    safe_atomic_write_csv(od/"augmented_eigenvalues.csv", eval_df)

    # ---- Report ----
    lines = [
        "="*70,
        "AIEF-1.4 Augmented Spectral Audit (v2 — Fundamental-State Restriction)",
        "="*70,
        "",
        f"r_EMA:     {r_ema:.6f}",
        f"mu_phase:  {mu_phase_ref:.6f}",
        f"alpha:     {alpha:.12g}",
        f"dt:        {dt}",
        f"perturb:   {pert:.1e}",
        f"dimension: {n_vars} (fundamental: h_old, B, C only)",
        "",
        "theta_i is NOT independently perturbed — it is derived.",
        "The 18 variables parameterize the true K3 state manifold.",
        "",
        f"Gap interval: ({gap_lower:.6f}, {gap_upper:.6f})",
        f"  discrete:  [{math.exp(-gap_upper*dt):.6f}, {math.exp(-gap_lower*dt):.6f}]",
        "",
        "-"*70,
        f"Eigenvalues in the gap: {n_in_gap}",
        f"Eigenvalues near r_EMA (within 10%): {n_near_ema}",
        "-"*70,
        "",
    ]

    if n_in_gap == 0 and n_near_ema == 1:
        lines.append("  VERDICT: SUPPORTED.")
        lines.append("  No eigenvalues in the gap and exactly one near r_EMA.")
        lines.append("  The EMA pole alpha IS the unique slow pole.")
        lines.append("  The augmented system has one slow mode, and it is EMA.")
    elif n_in_gap == 0:
        lines.append("  VERDICT: PARTIAL.")
        lines.append("  No eigenvalues in the gap, but the slow-pole structure")
        lines.append(f"  is not clear (found {n_near_ema} eigenvalues near r_EMA).")
    elif n_in_gap > 0:
        lines.append(f"  VERDICT: REVISED.  {n_in_gap} eigenvalue(s) in the gap.")
        lines.append("  There IS a mode slower than phase sync but faster than EMA.")
        lines.append("  The single-EMA-pole interpretation is not supported.")
        lines.append("  The following eigenvalues are in the gap:")
        gap_mask = eval_df["in_gap"]
        for _, r in eval_df[gap_mask].iterrows():
            lines.append(
                f"    λ = {r['eval_real']:.6e} + {r['eval_imag']:.6e}i,  "
                f"|λ| = {r['abs_eval']:.6e},  rate = {r['rate']:.6f}"
            )

    lines.extend([
        "",
        "-"*70,
        "All Relevant Eigenvalues (sorted by rate, slowest first):",
        "-"*70,
        f"  {'rate':>10} {'|λ|':>12} {'real':>14} {'imag':>14} {'gap?':>6}",
        f"  {'-'*10} {'-'*12} {'-'*14} {'-'*14} {'-'*6}",
    ])
    for _, r in eval_df.iterrows():
        marker = "  ***" if r["in_gap"] else ("  EMA" if r["near_ema"] else "")
        lines.append(
            f"  {r['rate']:>10.6f} {r['abs_eval']:>12.6e} "
            f"{r['eval_real']:>14.6e} {r['eval_imag']:>14.6e} "
            f"{str(r['in_gap']):>6}{marker}"
        )

    lines.extend([
        "",
        "-"*70,
        "Reference rates:",
        "-"*70,
        f"  Phase transverse (slowest):  {mu_phase_ref:.6f}",
        f"  Weight cocycle lambda_L:     {-math.log(0.998738)/dt:.6f}",
        f"  Weight cocycle lambda_R:     {-math.log(0.499369)/dt:.6f}",
        f"  EMA (alpha):                 {r_ema:.6f}",
        "",
        "What this establishes:",
        "  - Whether any linear mode exists between phase sync and EMA.",
        "  - Whether alpha is the unique slow pole of the true dynamics.",
        "",
        "What this does NOT establish:",
        "  - The nonlinear basin of attraction.",
        "  - Generality across seeds or branches.",
        "  - The dynamical mechanism producing each eigenvalue.",
        "",
        "Evidence class: diagnostic mechanism exploration.",
        "No interpretation is forced.  The eigenvalues speak.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"augmented_spectrum_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 augmented spectral audit v2 (fundamental-state restriction)",
        "evidence_class": "diagnostic mechanism exploration",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha,
                        "mu_phase":mu_phase_ref, "perturbation":pert},
        "state_variables": "h_old(3) + B(3) + C(12) = 18 fundamental vars",
        "outputs": ["augmented_eigenvalues.csv",
                     "augmented_spectrum_report.txt",
                     "analysis_manifest.json"],
        "tested_hypothesis": "No eigenvalue in (r_EMA, mu_phase); alpha is unique slow pole",
        "not_a_proof": True,
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")

    print(report)
    print(f"\n[SUCCESS] Artifacts saved to: '{od.resolve()}'")

if __name__ == "__main__":
    main()
