import numpy as np
import pandas as pd
import os

# ============================================================
# AIEF-1.3 Post-Run Analysis (Final Corrected Version)
# ============================================================

NPZ_PATH = "runs/c3da1ac707bf/AIEF_1_3_c3da1ac707bf_edge_diagnostics.npz"
OUTPUT_CSV = os.path.join(os.path.dirname(NPZ_PATH), "AIEF_1_3_analysis_results.csv")

def load_edge_data(npz_path):
    results = {}
    with np.load(npz_path, allow_pickle=False) as data:
        for key in data.files:
            if "_seed_" not in key:
                continue
            condition, remainder = key.split("_seed_", 1)
            seed_text, metric = remainder.split("_", 1)
            seed = int(seed_text)
            results.setdefault(condition, {})
            results[condition].setdefault(seed, {})
            results[condition][seed][metric] = data[key].copy()
    return results

def effective_number(weights, eps=1e-12):
    weights = np.asarray(weights, dtype=float)
    total = np.sum(weights)
    if total <= eps:
        return 0.0
    return total**2 / np.sum(weights**2)

def gini_coefficient(weights, eps=1e-12):
    x = np.sort(np.asarray(weights, dtype=float))
    if np.sum(x) <= eps:
        return 0.0
    n = len(x)
    ranks = np.arange(1, n + 1)
    return (2.0 * np.dot(ranks, x) / (n * np.sum(x))) - (n + 1.0) / n

def weight_entropy(weights, eps=1e-12):
    weights = np.asarray(weights, dtype=float)
    total = np.sum(weights)
    if total <= eps:
        return 0.0
    p = weights / total
    positive = p > 0
    entropy = -np.sum(p[positive] * np.log(p[positive]))
    return entropy / np.log(len(weights))

def residualize(y, *controls):
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, dtype=float) for c in controls])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return y - X @ beta

def partial_corr(x, y, *controls):
    arrays = (
        [
            np.asarray(x, dtype=float),
            np.asarray(y, dtype=float),
        ]
        + [
            np.asarray(c, dtype=float)
            for c in controls
        ]
    )
    combined = np.column_stack(arrays)
    valid = np.all(np.isfinite(combined), axis=1)
    combined = combined[valid]
    if len(combined) < len(controls) + 3:
        return np.nan
    x_clean = combined[:, 0]
    y_clean = combined[:, 1]
    controls_clean = [combined[:, i] for i in range(2, combined.shape[1])]
    rx = residualize(x_clean, *controls_clean)
    ry = residualize(y_clean, *controls_clean)
    if np.std(rx) < 1e-12 or np.std(ry) < 1e-12:
        return np.nan
    return np.corrcoef(rx, ry)[0, 1]

data = load_edge_data(NPZ_PATH)
summary_rows = []
shuffle_values = []

for cond in sorted(data.keys()):
    print(f"\n=== {cond} ===")
    for seed in sorted(data[cond].keys()):
        run = data[cond][seed]

        required = {
            "P_future", "R_physical_past", "R_driver_past",
            "B_at_split", "R_driver_future", "B_final"
        }
        missing = required - run.keys()
        if missing:
            raise KeyError(f"{cond}, seed={seed}: missing matrices {sorted(missing)}")

        P = run["P_future"]
        R_past = run["R_physical_past"]
        R_drv_past = run["R_driver_past"]
        B_split = run["B_at_split"]
        R_drv_future = run["R_driver_future"]
        n = P.shape[0]
        edges = np.triu_indices(n, k=1)

        p_edge = P[edges]
        r_phys_edge = R_past[edges]
        r_driv_edge = R_drv_past[edges]
        b_split_edge = B_split[edges]
        r_future_drv_edge = R_drv_future[edges]

        # Degeneracy metrics (NaN-safe)
        finite_p = p_edge[np.isfinite(p_edge)]
        if len(finite_p) == 0:
            p_mean = np.nan
            p_var = np.nan
            p_degen = True
        else:
            p_mean = np.mean(finite_p)
            p_var = np.var(finite_p)
            p_degen = np.std(finite_p) < 1e-12

        valid_phys = np.isfinite(p_edge) & np.isfinite(r_phys_edge)
        if np.sum(valid_phys) < 2:
            cov_phys = np.nan
        else:
            px = p_edge[valid_phys]
            rx = r_phys_edge[valid_phys]
            cov_phys = np.mean((px - np.mean(px)) * (rx - np.mean(rx)))

        valid_drv = np.isfinite(p_edge) & np.isfinite(r_driv_edge)
        if np.sum(valid_drv) < 2:
            cov_drv = np.nan
        else:
            px = p_edge[valid_drv]
            rx = r_driv_edge[valid_drv]
            cov_drv = np.mean((px - np.mean(px)) * (rx - np.mean(rx)))

        # Partial correlations (conditional association diagnostics)
        part_b = partial_corr(r_phys_edge, p_edge, b_split_edge)
        part_b_future = partial_corr(r_phys_edge, p_edge, b_split_edge, r_future_drv_edge)

        # Concentration metrics (unique undirected edges)
        Bf = run["B_final"]
        weights = Bf[edges]
        eff_n = effective_number(weights)
        gini = gini_coefficient(weights)
        entropy = weight_entropy(weights)

        row_sums = np.sum(Bf, axis=1)
        total_weight = float(np.sum(weights))
        mean_row_sum = float(np.mean(row_sums))
        max_row_sum = float(np.max(row_sums))
        nonzero_fraction = float(np.mean(weights > 1e-12))

        summary_rows.append({
            "condition": cond, "seed": seed,
            "P_mean": p_mean, "P_variance": p_var, "P_degenerate": p_degen,
            "Cov_physical": cov_phys, "Cov_driver": cov_drv,
            "Partial_Corr_given_Bsplit": part_b,
            "Partial_Corr_given_B_and_Rfuture": part_b_future,
            "Effective_edges": eff_n, "Gini": gini, "Weight_entropy": entropy,
            "Total_edge_weight": total_weight,
            "Mean_row_sum": mean_row_sum,
            "Max_row_sum": max_row_sum,
            "Nonzero_edge_fraction": nonzero_fraction,
        })

        if cond == "shuffle_R":
            finite_p = p_edge[np.isfinite(p_edge)]
            shuffle_values.append(finite_p)

    if cond == "shuffle_R" and shuffle_values:
        all_shuffle = np.concatenate(shuffle_values)
        hist, bin_edges = np.histogram(all_shuffle, bins=np.linspace(0.0, 1.0, 11))
        print("\nShuffle persistence histogram across all seeds:")
        for index, (left, right, count) in enumerate(zip(bin_edges[:-1], bin_edges[1:], hist)):
            closing = "]" if index == len(hist) - 1 else ")"
            print(f"  [{left:.2f}, {right:.2f}{closing}: {count}")

df = pd.DataFrame(summary_rows)
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved analysis results to {OUTPUT_CSV}")

# Descriptive pooled regression (explicitly labeled)
print("\n=== Descriptive pooled regression (P_future ~ R_past + B_split + R_driver_future) ===")
print("Note: This is descriptive only. Edges within seeds are dependent — do not interpret coefficients or SEs inferentially.")
for cond in ["baseline", "no_mu"]:
    if cond not in data:
        continue
    all_p, all_r, all_b, all_rdrv = [], [], [], []
    for seed in data[cond]:
        run = data[cond][seed]
        edges = np.triu_indices(run["P_future"].shape[0], k=1)
        all_p.extend(run["P_future"][edges])
        all_r.extend(run["R_physical_past"][edges])
        all_b.extend(run["B_at_split"][edges])
        all_rdrv.extend(run["R_driver_future"][edges])

    if len(all_p) > 10:
        y = np.asarray(all_p, dtype=float)
        X = np.column_stack([
            np.ones(len(y)),
            np.asarray(all_r, dtype=float),
            np.asarray(all_b, dtype=float),
            np.asarray(all_rdrv, dtype=float),
        ])
        valid = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
        X = X[valid]
        y = y[valid]
        if len(y) > X.shape[1]:
            print(f"\n{cond} design matrix condition number: {np.linalg.cond(X):.2e}")
            print(f"{cond} matrix rank: {np.linalg.matrix_rank(X)}")
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            print(f"Coefficients: intercept={beta[0]:.4f}, R_past={beta[1]:.4f}, B_split={beta[2]:.4f}, R_driver_future={beta[3]:.4f}")
