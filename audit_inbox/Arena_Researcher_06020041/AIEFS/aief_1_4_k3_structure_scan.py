#!/usr/bin/env python3

"""
AIEF-1.4 K3 Structure Prevalence Scan

Answers: how many seeds in the frozen run have a K3 (triangle) component
with a partial-controller geometry similar to the exceptional seed?

For each seed:
  1. Replay to final step
  2. Identify all positive-support components (connected subgraphs with B_ij > 0)
  3. For each K3 component:
     - Compute the controller (winner) map for its three edges
     - Classify: full controller (all nodes control), partial (some don't)
     - Record: winner map, controller set, node loadings
  4. Report prevalence of each controller geometry class

Does NOT:
  - Build Jacobians
  - Compute eigenproblems
  - Claim invariant subspaces or slow bundles

Outputs:
  k3_prevalence.csv        — per-seed K3 component summary
  k3_prevalence_report.txt — prevalence statistics
  analysis_manifest.json
"""

from __future__ import annotations

import argparse, hashlib, json, math, os, sys, tempfile, re
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_k3_structure_scan"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_MAX_SEEDS = 40

def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as h:
        while b := h.read(1024*1024): d.update(b)
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

# ── Find connected components in the positive B matrix ────────────
def find_positive_components(B, tol=1e-15):
    """Return list of sets of node indices for each positive-B component."""
    N = B.shape[0]
    adj = B > tol
    visited = np.zeros(N, dtype=bool)
    components = []
    for start in range(N):
        if visited[start]:
            continue
        stack = [start]
        visited[start] = True
        comp = {start}
        while stack:
            v = stack.pop()
            for u in range(N):
                if adj[v, u] and not visited[u]:
                    visited[u] = True
                    comp.add(u)
                    stack.append(u)
        if len(comp) >= 3:   # only components with 3+ nodes can contain K3
            components.append(comp)
    return components

def find_k3s_in_component(B, comp_nodes, winners, edge_i, edge_j,
                          capacities, epsilon, tol=1e-15):
    """Find all K3 subgraphs within a component and classify them."""
    nodes = sorted(comp_nodes)
    n_idx = {n: i for i, n in enumerate(nodes)}
    k3_list = []
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            for k in range(j+1, len(nodes)):
                a, b, c = nodes[i], nodes[j], nodes[k]
                w_ab = B[a, b] > tol
                w_ac = B[a, c] > tol
                w_bc = B[b, c] > tol
                if not (w_ab and w_ac and w_bc):
                    continue
                # Find edge indices
                e_ab = None; e_ac = None; e_bc = None
                for e in range(len(edge_i)):
                    if (edge_i[e] == min(a,b) and edge_j[e] == max(a,b)) or \
                       (edge_i[e] == max(a,b) and edge_j[e] == min(a,b)):
                        e_ab = e
                    if (edge_i[e] == min(a,c) and edge_j[e] == max(a,c)) or \
                       (edge_i[e] == max(a,c) and edge_j[e] == min(a,c)):
                        e_ac = e
                    if (edge_i[e] == min(b,c) and edge_j[e] == max(b,c)) or \
                       (edge_i[e] == max(b,c) and edge_j[e] == min(b,c)):
                        e_bc = e
                if e_ab is None or e_ac is None or e_bc is None:
                    continue
                w_ab_n = int(winners[e_ab])
                w_ac_n = int(winners[e_ac])
                w_bc_n = int(winners[e_bc])
                # Controller set = set of nodes that win at least one K3 edge
                ctrl_set = set()
                if w_ab_n == a: ctrl_set.add(a)
                if w_ab_n == b: ctrl_set.add(b)
                if w_ac_n == a: ctrl_set.add(a)
                if w_ac_n == c: ctrl_set.add(c)
                if w_bc_n == b: ctrl_set.add(b)
                if w_bc_n == c: ctrl_set.add(c)
                full_ctrl = len(ctrl_set) == 3
                partial_ctrl = len(ctrl_set) == 2
                # Winner map signature
                wmap = f"({w_ab_n},{w_ac_n},{w_bc_n})"
                # Node loadings
                q_a = None; q_b = None; q_c = None
                try:
                    q_a = capacities[a] / (float(w_ab_n == a and B[a,b] or 0) + epsilon)
                except: pass
                k3_list.append({
                    "nodes": f"({a},{b},{c})",
                    "edges": f"({e_ab},{e_ac},{e_bc})",
                    "winner_map": wmap,
                    "controller_set": str(sorted(ctrl_set)),
                    "n_controllers": len(ctrl_set),
                    "full_controller": full_ctrl,
                    "partial_controller": partial_ctrl,
                    "is_727": (w_ab_n == 7 and w_ac_n == 2 and w_bc_n == 7) if \
                              {a,b,c} == {2,7,11} else False,
                })
    return k3_list

# ── Single seed analysis ──────────────────────────────────────────
def analyze_seed(seed_id, base, aug, model, caps, A, edges_mat, eps_sc, fs, npz_path):
    """Return list of K3 component dicts for one seed."""
    with np.load(npz_path, allow_pickle=False) as data:
        state = base.load_split_state(data, seed_id)
    for _ in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)
    inter_final = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    winners = inter_final["winner_code"]
    edge_i, edge_j = edges_mat
    comps = find_positive_components(state.B)
    all_k3s = []
    for comp in comps:
        k3s = find_k3s_in_component(state.B, comp, winners, edge_i, edge_j,
                                     caps, eps_sc)
        all_k3s.extend(k3s)
    return all_k3s

# ── CLI ────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--npz", default=DEFAULT_NPZ)
    p.add_argument("--manifest", default=DEFAULT_MANIFEST)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    p.add_argument("--max-seeds", type=int, default=DEFAULT_MAX_SEEDS)
    return p.parse_args()

# ── main ───────────────────────────────────────────────────────────
def main():
    args = parse_args()
    base, ca, aug = load_production_modules()
    with open(args.manifest) as h: manifest = json.load(h)
    model = manifest["model"]
    dt = float(model["dt"])
    cap = (float(model["a"])-float(model["delta"]))/float(model["q"])
    caps = np.full(int(model["N"]), cap)
    N = int(model["N"])
    A, edges = base.incidence_matrix(N)
    fs = int(manifest["protocol"]["future_steps"])
    eps_sc = args.scale_epsilon

    # Seed discovery: keys are continue_seed_NNNN_B_final (underscores, not slashes)
    with np.load(args.npz, allow_pickle=False) as data:
        all_keys = list(data.keys())
    pattern = re.compile(r"^continue_seed_(\d+)_B_final$")
    seed_keys = sorted({m.group(1) for k in all_keys if (m := pattern.match(k))},
                       key=int)
    n_available = len(seed_keys)
    n_seeds = min(n_available, args.max_seeds)
    print(f"Found {n_available} seeds in NPZ. Scanning up to {n_seeds}.")

    all_rows = []
    for si, seed_id in enumerate(seed_keys[:n_seeds]):
        try:
            k3s = analyze_seed(seed_id, base, aug, model, caps, A, edges,
                               eps_sc, fs, args.npz)
            for k3 in k3s:
                k3["seed"] = seed_id
            all_rows.extend(k3s)
            n_k3 = len(k3s)
            wmaps = ", ".join(k["winner_map"] for k in k3s[:3])
            print(f"  [{si+1:>2}/{n_seeds}] {seed_id}: {n_k3} K3(s)"
                  + (f"  maps={wmaps}" if wmaps else ""),
                  flush=True)
        except Exception as e:
            print(f"  [{si+1:>2}/{n_seeds}] {seed_id}: FAILED — {type(e).__name__}: {e}",
                  flush=True)

    df = pd.DataFrame(all_rows)

    # ── Report ──
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    if len(df) > 0:
        safe_atomic_write_csv(od/"k3_prevalence.csv", df)

    n_seeds_with_k3 = df["seed"].nunique() if len(df) > 0 else 0
    n_727 = int((df["is_727"] == True).sum()) if "is_727" in df.columns and len(df) > 0 else 0
    n_partial = int((df["partial_controller"] == True).sum()) if "partial_controller" in df.columns and len(df) > 0 else 0
    n_full = int((df["full_controller"] == True).sum()) if "full_controller" in df.columns and len(df) > 0 else 0

    lines = [
        "="*70,
        "AIEF-1.4 K3 Structure Prevalence Scan",
        "="*70,
        f"Seeds scanned: {n_seeds}/{n_available}",
        f"Seeds with >=1 K3 component: {n_seeds_with_k3}",
        f"Total K3 components found: {len(df)}",
        "",
        f"Partial-controller K3s (2 controllers): {n_partial}",
        f"Full-controller K3s (3 controllers):    {n_full}",
        f"(7,2,7) winner map on {{2,7,11}}:         {n_727}",
        "",
        "─"*70,
        "Controller-Set Distribution:",
        "─"*70,
    ]
    if len(df) > 0 and "n_controllers" in df.columns:
        for nc, count in df["n_controllers"].value_counts().sort_index().items():
            lines.append(f"  {int(nc)}-controller K3s: {count}")
    lines.append("")

    if len(df) > 0 and "winner_map" in df.columns:
        lines.extend([
            "─"*70,
            "Winner Map Distribution (top 12):",
            "─"*70,
        ])
        for wm, count in df["winner_map"].value_counts().head(12).items():
            lines.append(f"  {wm}: {count}")
    lines.append("")

    if n_727 == 1 and n_seeds_with_k3 > 1:
        lines.append("CONCLUSION: The (7,2,7) partial-controller K3 is EXCEPTIONAL.")
        lines.append("It appears in exactly 1 seed.  No multi-seed bundle exists.")
        lines.append("The single-seed analysis characterizes a unique attractor state,")
        lines.append("not a robust geometric structure common across the ensemble.")
    elif n_727 > 1:
        lines.append(f"CONCLUSION: The (7,2,7) pattern appears in {n_727} seeds.")
        lines.append("A multi-seed cross comparison may be warranted.")
    elif n_partial > 0:
        lines.append(f"CONCLUSION: {n_partial} partial-controller K3s exist across seeds.")
        lines.append("The partial-controller geometry is not unique to one seed,")
        lines.append(f"but the specific (7,2,7) map on nodes {{2,7,11}} is not universal.")
    else:
        lines.append("CONCLUSION: No partial-controller K3s found in the scan.")
        lines.append("The exceptional seed's geometry is not reproduced elsewhere.")

    lines.extend([
        "",
        "Evidence class: structure prevalence scan.",
        "No Jacobians.  No eigenvalues.  No invariant subspaces claimed.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"k3_prevalence_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 K3 structure prevalence scan",
        "seed": "multi-seed",
        "n_seeds_scanned": n_seeds,
        "n_seeds_with_k3": n_seeds_with_k3,
        "n_727": n_727,
        "n_partial_controller": n_partial,
        "n_full_controller": n_full,
        "parameters": {"dt": dt, "scale_epsilon": eps_sc},
        "source_hashes": {
            Path(__file__).name: file_sha256(Path(__file__).resolve()),
            "base": compute_module_sha256(base),
        },
        "inputs": {
            "npz": {"path": str(Path(args.npz).resolve()),
                     "sha256": file_sha256(args.npz)},
            "manifest": {"path": str(Path(args.manifest).resolve()),
                         "sha256": file_sha256(args.manifest)},
        },
        "outputs": ["k3_prevalence.csv", "k3_prevalence_report.txt",
                     "analysis_manifest.json"],
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report, flush=True)
    print(f"\nDone. → {od.resolve()}", flush=True)

if __name__ == "__main__":
    main()
