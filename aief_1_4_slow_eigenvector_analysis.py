#!/usr/bin/env python3

"""
AIEF-1.4 Slow Eigenvector Analysis

Builds the 18x18 augmented Jacobian (fundamental-state restriction, as in the
spectral audit v3) and extracts the eigenvectors associated with the slow
EMA cluster (rates within 1% of r_EMA).

For each slow eigenvector, computes:
1.  Variable-group decomposition: % contribution from h_old, B, C
2.  Pairwise absolute inner products between all slow eigenvectors
3.  Participation factors: (left_i * right_i) — which state variables
    are most involved in each slow mode
4.  Whether the slow eigenvectors span a low-dimensional subspace
    (via SVD of the stacked eigenvector matrix)

Key question: are the 7 slow EMA-cluster eigenvectors nearly parallel
(one nearly-defective mode), or do they span genuinely distinct directions?

Outputs:
  - slow_eigenvectors.csv   (all slow eigenvectors, full 18-component)
  - eigenvector_overlaps.csv (pairwise |inner| matrix)
  - eigenvector_decomposition.csv (variable-group fractions)
  - slow_eigenvector_report.txt

Evidence class: diagnostic mechanism exploration.
"""

from __future__ import annotations

import argparse, copy, hashlib, json, math, os, sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_slow_eigenvector_analysis"
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
# State snapshot / restore (same as v3 augmented spectrum)
# ---------------------------------------------------------------------------
def snapshot_state(state):
    history_list = list(state.history)
    return {
        "B": state.B.copy(),
        "coherence_acc": state.coherence_acc.copy(),
        "history": [entry.copy() for entry in history_list],
    }

def restore_state(state, snap):
    state.B[:] = snap["B"]
    state.coherence_acc[:] = snap["coherence_acc"]
    state.history.clear()
    for entry in snap["history"]:
        state.history.append(entry.copy())

def extract_fundamental_vars(state):
    history_list = list(state.history)
    h_old = history_list[0] if len(history_list) > 0 else np.zeros(len(state.B))
    B_mat = state.B
    C_mat = state.coherence_acc
    vec = []
    for i in K3_NODES:
        vec.append(float(h_old[i]))
    for _, _, e in K3_EDGE_LIST:
        ia, ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        vec.append(float(B_mat[ia, ib]))
    for ia, ib in DIRECTED_PAIRS:
        c = C_mat[ia, ib]
        vec.append(float(c.real))
        vec.append(float(c.imag))
    return np.array(vec)

def inject_fundamental_vars(state, vec):
    B_mat = state.B
    C_mat = state.coherence_acc
    idx = 0
    h_old_vals = {}
    for i in K3_NODES:
        h_old_vals[i] = vec[idx]; idx += 1
    history_list = list(state.history)
    if len(history_list) > 0:
        oldest = history_list[0].copy()
        for i in K3_NODES:
            oldest[i] = h_old_vals[i]
        history_list[0] = oldest
        state.history.clear()
        for entry in history_list:
            state.history.append(entry)
    for _, _, e in K3_EDGE_LIST:
        ia, ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        val = vec[idx]; idx += 1
        B_mat[ia, ib] = val
        B_mat[ib, ia] = val
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

    # ---- Baseline ----
    snap_fs = snapshot_state(state)
    inter_base = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_base)
    vec_after_baseline = extract_fundamental_vars(state)
    n_vars = len(vec_after_baseline)

    # ---- Jacobian ----
    J = np.zeros((n_vars, n_vars))
    for col in range(n_vars):
        restore_state(state, snap_fs)
        vec_current = extract_fundamental_vars(state)
        delta = pert * max(1.0, abs(vec_current[col]))
        vec_current[col] += delta
        inject_fundamental_vars(state, vec_current)
        inter_p = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter_p)
        vec_pert_after = extract_fundamental_vars(state)
        J[:, col] = (vec_pert_after - vec_after_baseline) / delta
        if (col + 1) % 4 == 0 or col == n_vars - 1:
            print(f"  Column {col+1}/{n_vars} done")

    # ---- Eigendecomposition ----
    evals, evecs_right = np.linalg.eig(J)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300)) / dt

    # Identify slow cluster: rates within 1% of r_ema AND |λ| < 1 (contracting)
    slow_mask = (rates > r_ema * 0.99) & (rates < r_ema * 1.01) & (abs_evals < 1.0)
    slow_indices = np.where(slow_mask)[0]
    n_slow = len(slow_indices)

    print(f"  Found {n_slow} slow EMA-cluster eigenvectors.")

    # Sort slow indices by rate
    slow_order = np.argsort(rates[slow_indices])
    slow_indices = slow_indices[slow_order]

    # Extract slow right eigenvectors (columns of evecs_right)
    slow_evecs = evecs_right[:, slow_indices]  # shape (18, n_slow)
    slow_rates = rates[slow_indices]
    slow_evals = evals[slow_indices]
    slow_abs = abs_evals[slow_indices]

    # Also compute left eigenvectors for participation factors
    # Left eigenvectors = rows of inverse(evecs_right)
    try:
        evecs_left = np.linalg.inv(evecs_right)  # rows are left eigenvectors
        slow_left = evecs_left[slow_indices, :]   # shape (n_slow, 18)
    except np.linalg.LinAlgError:
        print("  WARNING: eigenvector matrix singular, using pseudo-inverse")
        evecs_left = np.linalg.pinv(evecs_right)
        slow_left = evecs_left[slow_indices, :]

    # ---- Variable-group labels ----
    var_labels = []
    for i in K3_NODES:
        var_labels.append(f"h_old_{i}")
    for _, _, e in K3_EDGE_LIST:
        var_labels.append(f"B_{e}")
    for ia, ib in DIRECTED_PAIRS:
        var_labels.append(f"C_{ia}{ib}_re")
        var_labels.append(f"C_{ia}{ib}_im")

    # ---- 1. Variable-group decomposition ----
    decomp_rows = []
    for k in range(n_slow):
        v = slow_evecs[:, k]
        # Normalize to unit norm
        vn = v / (np.linalg.norm(v) + 1e-300)
        # Power fractions by group
        h_pwr = np.sum(np.abs(vn[0:3])**2)
        B_pwr = np.sum(np.abs(vn[3:6])**2)
        C_pwr = np.sum(np.abs(vn[6:18])**2)
        total = h_pwr + B_pwr + C_pwr + 1e-300
        decomp_rows.append({
            "slow_mode": k,
            "rate": float(slow_rates[k]),
            "abs_eval": float(slow_abs[k]),
            "eval_real": float(slow_evals[k].real),
            "eval_imag": float(slow_evals[k].imag),
            "frac_h_old": float(h_pwr/total),
            "frac_B": float(B_pwr/total),
            "frac_C": float(C_pwr/total),
            "norm": float(np.linalg.norm(v)),
        })
    decomp_df = pd.DataFrame(decomp_rows)

    # ---- 2. Pairwise overlaps ----
    # Normalize eigenvectors first
    slow_evecs_norm = slow_evecs / (np.linalg.norm(slow_evecs, axis=0) + 1e-300)
    overlap_matrix = np.abs(slow_evecs_norm.T.conj() @ slow_evecs_norm)  # shape (n_slow, n_slow)

    overlap_rows = []
    for i in range(n_slow):
        for j in range(n_slow):
            overlap_rows.append({
                "mode_i": i, "mode_j": j,
                "rate_i": float(slow_rates[i]),
                "rate_j": float(slow_rates[j]),
                "abs_inner_product": float(overlap_matrix[i, j]),
            })
    overlap_df = pd.DataFrame(overlap_rows)

    # ---- 3. Participation factors ----
    # participation_i = |left_i[j] * right_i[j]|  for each state variable j
    part_rows = []
    for k in range(n_slow):
        rv = slow_evecs[:, k]
        lv = slow_left[k, :]
        # Normalize so sum of participations = 1
        raw_part = np.abs(lv * rv)
        if np.sum(raw_part) > 1e-300:
            raw_part = raw_part / np.sum(raw_part)
        for j in range(n_vars):
            part_rows.append({
                "slow_mode": k,
                "rate": float(slow_rates[k]),
                "var_index": j,
                "var_label": var_labels[j],
                "var_group": "h_old" if j < 3 else ("B" if j < 6 else "C"),
                "participation": float(raw_part[j]),
                "right_component": float(np.abs(rv[j])),
                "left_component": float(np.abs(lv[j])),
            })
    part_df = pd.DataFrame(part_rows)

    # ---- 4. SVD of eigenvector stack ----
    U, S, Vh = np.linalg.svd(slow_evecs_norm, full_matrices=False)
    # Singular values tell us the effective rank of the slow subspace
    sv_rows = []
    for i, s in enumerate(S):
        sv_rows.append({
            "singular_value_index": i,
            "singular_value": float(s),
            "cumulative_fraction": float(np.sum(S[:i+1]**2) / np.sum(S**2)),
        })
    sv_df = pd.DataFrame(sv_rows)

    # Effective dimension: number of singular values needed for 95% variance
    cumvar = np.cumsum(S**2) / np.sum(S**2)
    eff_dim = int(np.sum(cumvar < 0.95)) + 1

    # ---- Output ----
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"slow_eigenvectors.csv", decomp_df)
    safe_atomic_write_csv(od/"eigenvector_overlaps.csv", overlap_df)
    safe_atomic_write_csv(od/"participation_factors.csv", part_df)
    safe_atomic_write_csv(od/"singular_values.csv", sv_df)

    # ---- Build report ----
    lines = [
        "="*70,
        "AIEF-1.4 Slow Eigenvector Analysis",
        "="*70,
        "",
        f"r_EMA:  {r_ema:.6f}    alpha: {alpha:.12g}    dt: {dt}",
        f"Number of slow EMA-cluster eigenvectors: {n_slow}",
        f"Effective dimension of slow subspace (95% var): {eff_dim}",
        "",
        "-"*70,
        "Variable-Group Decomposition of Slow Eigenvectors:",
        "-"*70,
        f"  {'Mode':>5} {'rate':>10} {'% h_old':>10} {'% B':>10} {'% C':>10}",
        f"  {'-'*5} {'-'*10} {'-'*10} {'-'*10} {'-'*10}",
    ]
    for _, r in decomp_df.iterrows():
        lines.append(
            f"  {r['slow_mode']:>5} {r['rate']:>10.6f} "
            f"{r['frac_h_old']*100:>10.1f} {r['frac_B']*100:>10.1f} "
            f"{r['frac_C']*100:>10.1f}"
        )
    lines.append("")

    # Interpretation of decomposition
    mean_h = float(np.mean(decomp_df["frac_h_old"]))
    mean_B = float(np.mean(decomp_df["frac_B"]))
    mean_C = float(np.mean(decomp_df["frac_C"]))
    lines.extend([
        f"  Mean fractions: h_old={mean_h*100:.1f}%  B={mean_B*100:.1f}%  C={mean_C*100:.1f}%",
        "",
    ])
    if mean_C > 0.7:
        lines.append("  → Slow bundle is EMA/coherence-dominated.")
    elif mean_h > 0.7:
        lines.append("  → Slow bundle is history-dominated.")
    elif mean_B > 0.7:
        lines.append("  → Slow bundle is weight-dominated.")
    else:
        lines.append("  → Slow bundle is mixed across variable groups.")

    # ---- Pairwise overlaps ----
    lines.extend([
        "",
        "-"*70,
        "Pairwise Absolute Inner Products |<v_i|v_j>|:",
        "-"*70,
    ])
    # Compact matrix
    omat = np.zeros((n_slow, n_slow))
    for _, r in overlap_df.iterrows():
        omat[int(r["mode_i"]), int(r["mode_j"])] = r["abs_inner_product"]

    # Off-diagonal statistics
    offdiag = []
    for i in range(n_slow):
        for j in range(n_slow):
            if i != j:
                offdiag.append(omat[i, j])
    min_off = float(np.min(offdiag)) if offdiag else 0.0
    max_off = float(np.max(offdiag)) if offdiag else 0.0
    mean_off = float(np.mean(offdiag)) if offdiag else 0.0

    lines.append(f"  Off-diagonal range: [{min_off:.6f}, {max_off:.6f}]")
    lines.append(f"  Off-diagonal mean:  {mean_off:.6f}")
    lines.append("")
    if mean_off > 0.9:
        lines.append("  → All slow eigenvectors are nearly parallel.")
        lines.append("    Consistent with one nearly-defective Jordan chain.")
    elif mean_off > 0.5:
        lines.append("  → Moderate overlap.  Slow modes share significant")
        lines.append("    components but are not identical.")
    else:
        lines.append("  → Low overlap.  Slow modes span distinct directions.")
        lines.append(f"    The slow subspace is genuinely {eff_dim}-dimensional.")

    # Show a few off-diagonal entries
    lines.append("")
    lines.append(f"  {'i':>4} {'j':>4} {'|<vi|vj>|':>12}")
    lines.append(f"  {'-'*4} {'-'*4} {'-'*12}")
    count = 0
    for _, r in overlap_df.iterrows():
        if r["mode_i"] != r["mode_j"]:
            lines.append(f"  {r['mode_i']:>4} {r['mode_j']:>4} {r['abs_inner_product']:>12.6f}")
            count += 1
            if count >= 15:
                break

    # ---- Singular values ----
    lines.extend([
        "",
        "-"*70,
        "Singular Values of Slow Eigenvector Stack:",
        "-"*70,
        f"  {'Index':>6} {'Singular Value':>16} {'Cumulative %':>14}",
        f"  {'-'*6} {'-'*16} {'-'*14}",
    ])
    for _, r in sv_df.iterrows():
        lines.append(
            f"  {r['singular_value_index']:>6} {r['singular_value']:>16.6e} "
            f"{r['cumulative_fraction']*100:>14.1f}"
        )
    lines.extend([
        "",
        f"  Effective dimension (95% variance): {eff_dim}",
        f"  Total slow modes: {n_slow}",
        "",
    ])
    if eff_dim == 1:
        lines.append("  → The slow subspace is effectively 1-dimensional.")
        lines.append("    All 7 eigenvectors are nearly parallel.  The true")
        lines.append("    slow dynamics are rank-1.  This is consistent with")
        lines.append("    a nearly-defective Jordan block or a single physical")
        lines.append("    slow mode represented by multiple numerical eigenvectors.")
    elif eff_dim <= 3:
        lines.append(f"  → The slow subspace is low-dimensional (eff. rank {eff_dim}).")
        lines.append("    A few genuinely distinct slow mechanisms exist.")
    else:
        lines.append(f"  → The slow subspace is genuinely {eff_dim}-dimensional.")
        lines.append("    Multiple independent slow mechanisms coexist.")

    # ---- Participation factors (top per mode) ----
    lines.extend([
        "",
        "-"*70,
        "Top Participation Factors per Slow Mode:",
        "-"*70,
    ])
    for k in range(min(n_slow, 5)):  # show first 5 modes
        sub = part_df[part_df["slow_mode"] == k].sort_values("participation", ascending=False)
        lines.append(f"  Mode {k} (rate={slow_rates[k]:.6f}):")
        for _, r in sub.head(5).iterrows():
            lines.append(
                f"    {r['var_label']:>12}  part={r['participation']:.4f}  "
                f"|right|={r['right_component']:.4f}  |left|={r['left_component']:.4f}"
            )
    if n_slow > 5:
        lines.append(f"  ... ({n_slow - 5} more modes, see participation_factors.csv)")

    # ---- Final summary ----
    lines.extend([
        "",
        "-"*70,
        "Summary:",
        "-"*70,
        "",
        f"  Slow EMA-cluster modes: {n_slow}",
        f"  Effective subspace dimension: {eff_dim}",
        f"  Mean pairwise overlap: {mean_off:.4f}",
        f"  Dominant variable group: {'C (EMA/coherence)' if mean_C > max(mean_h, mean_B) else ('h_old (history)' if mean_h > mean_B else 'B (weights)')}",
        "",
    ])

    if eff_dim == 1 and mean_off > 0.9:
        lines.append("  CONCLUSION: The slow bundle is effectively rank-1.")
        lines.append("  The 7 numerical eigenvectors are nearly parallel —")
        lines.append("  consistent with a single physical slow mode represented")
        lines.append("  by a nearly-defective Jordan chain.  The replay's")
        lines.append("  single-rate observables are therefore following one")
        lines.append("  dominant direction within what appears numerically as")
        lines.append("  a cluster but is structurally a single slow manifold.")
    elif eff_dim <= 2:
        lines.append("  CONCLUSION: The slow bundle has low effective dimension.")
        lines.append("  A small number of distinct slow mechanisms exist, but")
        lines.append("  the replay may primarily excite one combination.")
    else:
        lines.append("  CONCLUSION: The slow bundle is genuinely multidimensional.")
        lines.append("  Multiple independent slow mechanisms coexist at similar")
        lines.append("  rates.  The replay's single-rate observables may be")
        lines.append("  following one particular direction through this subspace.")
        lines.append("  The downstream EMA-rate inheritance may be more complex")
        lines.append("  than a single-pole projection.")

    lines.extend([
        "",
        "Evidence class: diagnostic mechanism exploration.",
        "No interpretation is forced.  The eigenvectors speak.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"slow_eigenvector_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 slow eigenvector analysis",
        "evidence_class": "diagnostic mechanism exploration",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha, "perturbation":pert},
        "state_variables": "h_old(3) + B(3) + C(12) = 18 fundamental vars",
        "n_slow_modes": n_slow,
        "effective_slow_dimension": eff_dim,
        "mean_pairwise_overlap": mean_off,
        "outputs": [
            "slow_eigenvectors.csv",
            "eigenvector_overlaps.csv",
            "participation_factors.csv",
            "singular_values.csv",
            "slow_eigenvector_report.txt",
            "analysis_manifest.json",
        ],
        "not_a_proof": True,
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")

    print(report)
    print(f"\n[SUCCESS] Artifacts saved to: '{od.resolve()}'")

if __name__ == "__main__":
    main()
