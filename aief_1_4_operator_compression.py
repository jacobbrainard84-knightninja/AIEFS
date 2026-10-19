#!/usr/bin/env python3

"""
AIEF-1.4 Operator Compression onto the Slow Subspace

Given the real orthonormal basis Q_slow for the 4-dimensional slow invariant
subspace (from the Jacobian eigendecomposition), this script compresses each
constituent update operator onto that subspace.

For each operator T (full Jacobian, EMA block, B block, coherence block):
  1.  Compressed:       Π_slow · T · Π_slow   (dynamics within slow bundle)
  2.  Leakage norm:     ‖(I−Π_slow) · T · Π_slow‖  (slow→fast coupling)
  3.  Commutator norm:  ‖[T, T_EMA]‖   (non-commutation with EMA)

Also computes the eigenvalues of each compressed operator — do they match
the EMA rate, or are there hidden fast components within the slow bundle?

Key questions:
  - Does the full Jacobian, when compressed, have EMA-rate eigenvalues?
  - Does any individual update leak substantially out of the slow subspace?
  - Do the update operators commute with the EMA update?

Outputs:
  - compression_report.txt
  - compressed_eigenvalues.csv
"""

from __future__ import annotations

import argparse, hashlib, json, math, os, sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_operator_compression"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_PERTURBATION = 1e-8

K3_NODES = [2, 7, 11]
K3_EDGE_LIST = [(2,7,25), (2,11,29), (7,11,59)]
DIRECTED_PAIRS = [(2,7),(7,2),(2,11),(11,2),(7,11),(11,7)]

# ── utilities ──────────────────────────────────────────────────────
def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as h:
        while b := h.read(1024*1024): d.update(b)
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

# ── state I/O ───────────────────────────────────────────────────────
def snapshot_state(state):
    hl = list(state.history)
    return {"B": state.B.copy(), "coherence_acc": state.coherence_acc.copy(),
            "history": [e.copy() for e in hl]}

def restore_state(state, snap):
    state.B[:] = snap["B"]
    state.coherence_acc[:] = snap["coherence_acc"]
    state.history.clear()
    for e in snap["history"]: state.history.append(e)

def extract_fundamental(state):
    hl = list(state.history)
    ho = hl[0] if hl else np.zeros(len(state.B))
    Bm, Cm = state.B, state.coherence_acc
    v = [float(ho[i]) for i in K3_NODES]
    for _,_,e in K3_EDGE_LIST:
        ia,ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        v.append(float(Bm[ia,ib]))
    for ia,ib in DIRECTED_PAIRS:
        c = Cm[ia,ib]; v.append(float(c.real)); v.append(float(c.imag))
    return np.array(v, dtype=float)

def inject_fundamental(state, vec):
    vec = np.asarray(vec, dtype=float)
    Bm, Cm = state.B, state.coherence_acc
    idx = 0
    ho = {i: float(vec[idx+i2]) for i2,i in enumerate(K3_NODES)}; idx += 3
    hl = list(state.history)
    if hl:
        oldest = hl[0].copy()
        for i in K3_NODES: oldest[i] = ho[i]
        hl[0] = oldest; state.history.clear()
        for e in hl: state.history.append(e)
    for _,_,e in K3_EDGE_LIST:
        ia,ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        Bm[ia,ib] = Bm[ib,ia] = float(vec[idx]); idx += 1
    for ia,ib in DIRECTED_PAIRS:
        Cm[ia,ib] = complex(float(vec[idx]), float(vec[idx+1])); idx += 2

def build_real_slow_basis(evecs_complex, slow_idx, tol=1e-12):
    real_basis = []
    used = set()
    for i in slow_idx:
        if i in used: continue
        v = evecs_complex[:, i]
        if abs(v.imag).max() < tol:
            real_basis.append(np.asarray(v.real, dtype=float).copy())
            used.add(i)
        else:
            partner = None
            for j in slow_idx:
                if j == i or j in used: continue
                w = evecs_complex[:, j]
                if np.allclose(v.real, w.real, atol=tol) and \
                   np.allclose(v.imag, -w.imag, atol=tol):
                    partner = j; break
            real_basis.append(np.asarray(v.real, dtype=float).copy())
            real_basis.append(np.asarray(v.imag, dtype=float).copy())
            used.add(i)
            if partner is not None: used.add(partner)
    if not real_basis: return np.zeros((evecs_complex.shape[0], 0), dtype=float)
    Q, _ = np.linalg.qr(np.column_stack(real_basis))
    return Q

def finite_diff_col(J, col, state, snap_fs, caps, model, A, edges_mat, eps_sc,
                    aug, v_after, pert, n_vars):
    """Compute one column of a Jacobian by perturbing variable `col`."""
    restore_state(state, snap_fs)
    vc = extract_fundamental(state)
    delta = pert * max(1.0, abs(vc[col]))
    vc[col] += delta
    inject_fundamental(state, vc)
    inter_p = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_p)
    vp = extract_fundamental(state)
    return (vp - v_after) / delta

# ── CLI ─────────────────────────────────────────────────────────────
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

# ── main ────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    for p in (args.npz, args.manifest):
        if not os.path.isfile(p): raise FileNotFoundError(f"Missing: {p}")

    base, ca, aug = load_production_modules()
    with open(args.manifest) as h: manifest = json.load(h)
    model = manifest["model"]
    dt = float(model["dt"])
    alpha = math.exp(-dt/float(model["T_window"]))
    r_ema = -np.log(alpha)/dt
    cap = (float(model["a"])-float(model["delta"]))/float(model["q"])
    caps = np.full(int(model["N"]), cap)
    N = int(model["N"])
    A, edges_mat = base.incidence_matrix(N)
    fs = int(manifest["protocol"]["future_steps"])
    eps_sc, pert = args.scale_epsilon, args.perturbation

    # ── Replay to final step ──
    print("Replaying to final step …")
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)

    # ── Full 18×18 Jacobian ──
    print("Building 18×18 augmented Jacobian …")
    snap_fs = snapshot_state(state)
    inter_base = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_base)
    v_after = extract_fundamental(state)
    n_vars = len(v_after)
    J_full = np.zeros((n_vars, n_vars))
    for col in range(n_vars):
        J_full[:, col] = finite_diff_col(
            J_full, col, state, snap_fs, caps, model, A, edges_mat, eps_sc, aug,
            v_after, pert, n_vars)
    print("  done.")

    # ── Eigendecomposition → slow subspace ──
    evals, evecs_r = np.linalg.eig(J_full)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300))/dt
    slow_mask = (rates > r_ema*0.99) & (rates < r_ema*1.01) & (abs_evals < 1.0)
    slow_idx = np.where(slow_mask)[0]
    Q_slow = build_real_slow_basis(evecs_r, slow_idx)
    slow_dim = Q_slow.shape[1]
    Pi_slow = Q_slow @ Q_slow.T                     # projector (18×18)
    Pi_fast = np.eye(n_vars) - Pi_slow
    print(f"  Slow subspace dimension: {slow_dim}")

    # ── Block Jacobians via finite differences ──
    # EMA-only: perturb C only, measure C response
    # B-only:   perturb B only, measure B response
    # h-only:   perturb h_old only, measure h_old response

    def block_jacobian(perturb_cols, measure_cols, label):
        """Finite-difference Jacobian block: perturb `perturb_cols`, measure `measure_cols`."""
        Jb = np.zeros((len(measure_cols), len(perturb_cols)))
        for j, pcol in enumerate(perturb_cols):
            Jb[:, j] = finite_diff_col(
                None, pcol, state, snap_fs, caps, model, A, edges_mat, eps_sc, aug,
                v_after, pert, n_vars)[measure_cols]
        # Pad to 18×18 for compression
        Jfull = np.zeros((n_vars, n_vars))
        for j, pcol in enumerate(perturb_cols):
            Jfull[measure_cols, pcol] = Jb[:, j]
        return Jfull

    # Variable indices: h_old [0:3], B [3:6], C [6:18]
    h_cols = list(range(0, 3))
    B_cols = list(range(3, 6))
    C_cols = list(range(6, 18))

    print("Building block Jacobians …")
    J_EMA  = block_jacobian(C_cols, C_cols, "EMA")     # C → C
    J_B    = block_jacobian(B_cols, B_cols, "B")       # B → B
    J_h    = block_jacobian(h_cols, h_cols, "h")       # h → h

    # Also: C → B coupling (how coherence drives weights)
    J_CtoB = block_jacobian(C_cols, B_cols, "C→B")

    # ── Compress each operator ──
    operators = {
        "J_full": J_full,
        "J_EMA (C→C)": J_EMA,
        "J_B (B→B)": J_B,
        "J_h (h→h)": J_h,
        "J_CtoB (C→B)": J_CtoB,
    }

    comp_rows = []
    for name, T in operators.items():
        # Compressed operator on slow subspace (slow_dim × slow_dim)
        T_comp = Q_slow.T @ T @ Q_slow          # Π_slow · T · Π_slow  in slow coords
        # Leakage: slow → fast
        leakage = Pi_fast @ T @ Q_slow           # (I−Π_slow) · T · Π_slow
        leak_norm = float(np.linalg.norm(leakage, ord=2))
        # Leakage fraction: ||leakage|| / ||T_comp||
        comp_norm = float(np.linalg.norm(T_comp, ord=2))
        leak_frac = leak_norm / (comp_norm + 1e-30)

        # Commutator with J_EMA compressed
        J_EMA_comp = Q_slow.T @ J_EMA @ Q_slow
        comm = T_comp @ J_EMA_comp - J_EMA_comp @ T_comp
        comm_norm = float(np.linalg.norm(comm, ord=2))

        # Eigenvalues of compressed operator → continuous-time rates
        evals_comp = np.linalg.eigvals(T_comp)
        rates_comp = -np.log(np.maximum(np.abs(evals_comp), 1e-300)) / dt
        rates_comp_sorted = sorted(rates_comp)

        comp_rows.append({
            "operator": name,
            "comp_norm": comp_norm,
            "leakage_norm": leak_norm,
            "leakage_fraction": leak_frac,
            "commutator_norm": comm_norm,
            "slowest_comp_rate": float(rates_comp_sorted[0]) if rates_comp_sorted else np.nan,
            "fastest_comp_rate": float(rates_comp_sorted[-1]) if rates_comp_sorted else np.nan,
            "n_fast_modes": int(np.sum(np.array(rates_comp_sorted) > r_ema * 2)),
            "n_slow_modes": int(np.sum(np.array(rates_comp_sorted) < r_ema * 2)),
            "comp_evals_real": [float(e.real) for e in evals_comp],
        })

    comp_df = pd.DataFrame(comp_rows)

    # ── Output ──
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"operator_compression.csv", comp_df)

    # ── Report ──
    lines = [
        "="*70,
        "AIEF-1.4 Operator Compression onto Slow Subspace",
        "="*70,
        f"r_EMA: {r_ema:.6f}   alpha: {alpha:.12g}   dt: {dt}",
        f"Slow subspace dimension: {slow_dim}",
        "",
        "Π_slow = Q_slow · Q_slow^T    (projector onto slow invariant subspace)",
        "Π_fast = I − Π_slow           (fast complement)",
        "",
        "For each operator T:",
        "  Compressed:  Π_slow · T · Π_slow   (dynamics within slow bundle)",
        "  Leakage:     Π_fast · T · Π_slow   (slow → fast coupling)",
        "  Commutator:  [T_comp, J_EMA_comp]  (non-commutation with EMA)",
        "",
        "─"*70,
        "Operator Compression Summary:",
        "─"*70,
        f"  {'Operator':<22} {'‖comp‖':>10} {'‖leak‖':>10} {'leak%':>8} "
        f"{'‖[·,EMA]‖':>10} {'slow':>6} {'fast':>6}",
        f"  {'-'*22} {'-'*10} {'-'*10} {'-'*8} {'-'*10} {'-'*6} {'-'*6}",
    ]
    for _, r in comp_df.iterrows():
        lines.append(
            f"  {r['operator']:<22} {r['comp_norm']:>10.4f} {r['leakage_norm']:>10.4f} "
            f"{r['leakage_fraction']*100:>8.1f} {r['commutator_norm']:>10.4f} "
            f"{r['n_slow_modes']:>6} {r['n_fast_modes']:>6}"
        )
    lines.extend([
        "",
        "  'slow'/'fast' counts: eigenvalues of compressed operator with",
        "  rate below/above 2× r_EMA.  Slow modes inside the compressed",
        "  operator mean that operator's restricted dynamics are EMA-rate.",
        "  Fast modes mean the operator has fast internal dynamics even",
        "  within the slow subspace.",
        "",
    ])

    # Interpretation
    full_row = comp_df[comp_df["operator"] == "J_full"].iloc[0]
    ema_row  = comp_df[comp_df["operator"] == "J_EMA (C→C)"].iloc[0]
    B_row    = comp_df[comp_df["operator"] == "J_B (B→B)"].iloc[0]
    h_row    = comp_df[comp_df["operator"] == "J_h (h→h)"].iloc[0]
    CB_row   = comp_df[comp_df["operator"] == "J_CtoB (C→B)"].iloc[0]

    if ema_row["leakage_fraction"] < 0.01:
        lines.append("  J_EMA is essentially closed within the slow subspace.")
        lines.append("  The EMA dynamics are internal to the slow bundle.")
    else:
        lines.append("  J_EMA has non-negligible leakage to fast modes.")

    if B_row["leakage_fraction"] < 0.01:
        lines.append("  J_B is essentially closed within the slow subspace.")
    else:
        lines.append(f"  J_B leaks {B_row['leakage_fraction']*100:.1f}% out of the slow subspace.")
        lines.append("  Weight dynamics are not confined to the slow bundle.")

    if CB_row["comp_norm"] > 0.01 * full_row["comp_norm"]:
        lines.append("  J_CtoB has significant compressed norm — coherence drives weights")
        lines.append("  through the slow subspace.  This is the C→B slaving channel.")

    if ema_row["commutator_norm"] < 0.01:
        lines.append("  J_EMA approximately commutes with itself (trivial).")
    if B_row["commutator_norm"] > 0.01:
        lines.append("  J_B does NOT commute with J_EMA — weight and EMA dynamics")
        lines.append("  are non-commuting operators on the slow subspace.")

    lines.extend([
        "",
        "─"*70,
        "Compressed Eigenvalue Rates (slowest → fastest):",
        "─"*70,
    ])
    for _, r in comp_df.iterrows():
        rates_list = sorted([float(x) for x in r["comp_evals_real"]],
                            key=lambda x: -math.log(max(abs(x),1e-300))/dt
                            if abs(x) > 1e-14 else float('inf'))
        rates_str = ", ".join(
            f"{-math.log(max(abs(x),1e-300))/dt:.4f}" if abs(x) > 1e-14
            else "~0"
            for x in rates_list[:6]
        )
        lines.append(f"  {r['operator']:<22} → [{rates_str}]")

    report = "\n".join(lines)
    safe_atomic_write_text(od/"operator_compression_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 operator compression onto slow subspace",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha, "perturbation":pert},
        "slow_dim": slow_dim,
        "outputs": ["operator_compression.csv",
                     "operator_compression_report.txt",
                     "analysis_manifest.json"],
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report)
    print(f"\nDone. → {od.resolve()}")

if __name__ == "__main__":
    main()
