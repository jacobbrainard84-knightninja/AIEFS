import numpy as np
from collections import deque
import time
import csv
import json
import os
import hashlib
import platform

# ============================================================
# AIEF-1.3 — Final Production-Ready Falsification Matrix
# (Robust checkpointing + configuration versioning)
# ============================================================

WORKFLOW_VERSION = "AIEF-1.3-production-10"

N = 12
T_sim = 800.0
dt = 0.01
tau = 0.5
omega = np.array([1.00, 1.02, 1.50, 2.00, 2.01,
                  1.01, 1.03, 1.51, 2.02, 2.00,
                  1.00, 1.04])
a = 1.0
q = 1.5
delta = 0.05
eta = 0.04
gamma = 0.015
mu = 0.03
T_window = 25.0 / np.mean(omega)
B_c = 0.12
B_init_scale = 0.0005
D_B_star = 0.30
alpha = np.exp(-dt / T_window)

N_SEEDS = 20
CONDITIONS = ["baseline", "shuffle_R", "no_delay", "no_mu", "no_gap"]
GAP_TOL = 1e-9

if len(omega) != N:
    raise ValueError("omega must contain exactly N frequencies")

delay_steps = int(round(tau / dt))
n_steps = int(round(T_sim / dt))
EDGES = np.triu_indices(N, k=1)

burn_end = int(0.20 * n_steps)
hist_end = int(0.60 * n_steps)

if not (0 <= burn_end < hist_end < n_steps):
    raise ValueError("Invalid analysis window boundaries")

SEEDS = [42 + s * 1000 for s in range(N_SEEDS)]

# Build manifest and config hash BEFORE creating run directory
manifest = {
    "workflow_version": WORKFLOW_VERSION,
    "N": N,
    "T_sim": T_sim,
    "dt": dt,
    "tau": tau,
    "omega": omega.tolist(),
    "a": a,
    "q": q,
    "delta": delta,
    "eta": eta,
    "gamma": gamma,
    "mu": mu,
    "T_window": float(T_window),
    "alpha": float(alpha),
    "B_c": B_c,
    "B_init_scale": B_init_scale,
    "D_B_star": D_B_star,
    "N_SEEDS": N_SEEDS,
    "seeds": SEEDS,
    "conditions": CONDITIONS,
    "delay_steps": delay_steps,
    "n_steps": n_steps,
    "burn_end": burn_end,
    "hist_end": hist_end,
    "GAP_TOL": GAP_TOL,
    "python_version": platform.python_version(),
    "numpy_version": np.__version__,
}

manifest_text = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
CONFIG_HASH = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()[:12]
RUN_DIR = os.path.join("runs", CONFIG_HASH)
os.makedirs(RUN_DIR, exist_ok=True)

# Write manifest immediately
with open(os.path.join(RUN_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)

def summarize(values):
    x = np.asarray(values, dtype=float)
    valid = np.isfinite(x)
    if not np.any(valid):
        return np.nan, np.nan, 0
    return np.mean(x[valid]), np.std(x[valid]), int(np.sum(valid))

def load_checkpoint(path):
    result = {}
    with np.load(path, allow_pickle=False) as data:
        for key in data.files:
            value = data[key]
            if value.ndim == 0:
                result[key] = value.item()
            else:
                result[key] = value.copy()
    return result

def save_checkpoint_atomic(path, result):
    temp_path = path + ".tmp.npz"
    np.savez_compressed(temp_path, **result)
    os.replace(temp_path, path)

def run_aief(condition, seed):
    np.random.seed(seed)

    theta = np.random.rand(N) * 2 * np.pi
    B = B_init_scale * np.random.rand(N, N)
    B = 0.5 * (B + B.T)
    np.fill_diagonal(B, 0.0)

    coherence_acc = np.zeros((N, N), dtype=complex)
    history = deque([theta.copy()] * (delay_steps + 1), maxlen=delay_steps + 1)

    R_physical_sum = np.zeros((N, N))
    R_driver_sum = np.zeros((N, N))
    P_sum = np.zeros((N, N))
    R_future_sum = np.zeros((N, N))
    R_driver_future_sum = np.zeros((N, N))
    r_history = []
    G_min_over_time = np.inf
    G_min_pre_over_time = np.inf
    B_at_split = None

    for step in range(n_steps):
        if step == hist_end:
            B_at_split = B.copy()

        if condition == "no_delay" or len(history) <= delay_steps:
            theta_delayed = theta.copy()
        else:
            theta_delayed = history[-delay_steps - 1]

        tau_eff = 0.0 if condition == "no_delay" else tau
        R_physical = compute_R(theta, theta_delayed, omega, tau_eff, coherence_acc, alpha)
        R_physical = 0.5 * (R_physical + R_physical.T)
        np.fill_diagonal(R_physical, 0.0)

        R_driver = R_physical
        if condition == "shuffle_R":
            values = R_physical[EDGES].copy()
            np.random.shuffle(values)
            R_driver = np.zeros_like(R_physical)
            R_driver[EDGES] = values
            R_driver[(EDGES[1], EDGES[0])] = values

        mu_eff = 0.0 if condition == "no_mu" else mu
        B += dt * ((eta + mu_eff) * R_driver - mu_eff - gamma * B)
        B = np.maximum(B, 0.0)
        B = 0.5 * (B + B.T)
        np.fill_diagonal(B, 0.0)

        row_sum_pre = np.sum(B, axis=1)
        G_pre = a - q * row_sum_pre
        G_min_pre_over_time = min(G_min_pre_over_time, np.min(G_pre))

        if condition != "no_gap":
            row_sum = np.sum(B, axis=1)
            cap = (a - delta) / q
            scale = np.minimum(1.0, cap / (row_sum + 1e-12))
            B *= np.minimum.outer(scale, scale)
            np.fill_diagonal(B, 0.0)

        row_sum = np.sum(B, axis=1)
        G = a - q * row_sum
        G_min_over_time = min(G_min_over_time, np.min(G))

        if condition != "no_gap" and G_min_over_time < delta - GAP_TOL:
            raise RuntimeError(
                f"Dominance-gap violation in {condition}, seed={seed}: "
                f"{G_min_over_time}"
            )

        if burn_end <= step < hist_end:
            R_physical_sum += R_physical
            R_driver_sum += R_driver
        if step >= hist_end:
            P_sum += (B > B_c).astype(float)
            R_future_sum += R_physical
            R_driver_future_sum += R_driver

        coupling = np.sum(B * np.sin(theta_delayed[None, :] - theta[:, None]), axis=1)
        theta += dt * (omega + coupling)
        theta = np.mod(theta, 2 * np.pi)
        history.append(theta.copy())

        if step % 50 == 0:
            r_complex = np.mean(np.exp(1j * theta))
            r_history.append(np.abs(r_complex))

    R_physical_bar = R_physical_sum / (hist_end - burn_end)
    R_driver_bar = R_driver_sum / (hist_end - burn_end)
    P = P_sum / (n_steps - hist_end)
    R_future_bar = R_future_sum / (n_steps - hist_end)
    R_driver_future_bar = R_driver_future_sum / (n_steps - hist_end)

    p_edge = P[EDGES]
    r_phys_edge = R_physical_bar[EDGES]
    r_driv_edge = R_driver_bar[EDGES]

    def safe_corr(x, y):
        if np.std(x) < 1e-12 or np.std(y) < 1e-12:
            return np.nan
        return np.corrcoef(x, y)[0, 1]

    corr_physical = safe_corr(p_edge, r_phys_edge)
    corr_driver   = safe_corr(p_edge, r_driv_edge)

    r_mean = np.mean(r_history)
    D_B = np.sum(np.triu((B > B_c), k=1)) / (N * (N - 1) / 2.0)
    Phi = np.nan if D_B < 1e-12 else r_mean * (D_B_star / D_B)

    L_final = np.diag(np.sum(B, axis=1)) - B
    evals_f = np.clip(np.linalg.eigvalsh(L_final), 0.0, None)
    total = np.sum(evals_f)
    if total < 1e-12:
        S_final = 0.0
    else:
        p_f = evals_f / total
        positive = p_f > 0
        S_final = -np.sum(p_f[positive] * np.log(p_f[positive]))

    row_sum_final = np.sum(B, axis=1)
    G_min_final = np.min(a - q * row_sum_final)

    P_mean = float(np.mean(p_edge))
    P_variance = float(np.var(p_edge))
    P_degenerate = bool(np.std(p_edge) < 1e-12)
    cov_physical = float(np.mean((p_edge - P_mean) * (r_phys_edge - np.mean(r_phys_edge))))
    cov_driver   = float(np.mean((p_edge - P_mean) * (r_driv_edge - np.mean(r_driv_edge))))

    return {
        "seed": seed,
        "condition": condition,
        "config_hash": CONFIG_HASH,
        "D_B": D_B,
        "Corr_physical": corr_physical,
        "Corr_driver": corr_driver,
        "Phi": Phi,
        "r_mean": r_mean,
        "S_spectral": S_final,
        "G_min_final": G_min_final,
        "G_min_over_time": G_min_over_time,
        "G_min_pre_over_time": G_min_pre_over_time,
        "P_mean": P_mean,
        "P_variance": P_variance,
        "P_degenerate": P_degenerate,
        "Cov_physical": cov_physical,
        "Cov_driver": cov_driver,
        "B_at_split": B_at_split,
        "P_future": P,
        "R_physical_past": R_physical_bar,
        "R_driver_past": R_driver_bar,
        "R_physical_future": R_future_bar,
        "R_driver_future": R_driver_future_bar,
        "B_final": B.copy(),
    }

def compute_R(theta_now, theta_delayed, omega, tau, coherence_acc, alpha):
    dphi = (theta_now[:, None] - theta_delayed[None, :]
            - ((omega[:, None] + omega[None, :]) / 2.0) * tau)
    z_inst = np.exp(1j * dphi)
    coherence_acc[:] = alpha * coherence_acc + (1 - alpha) * z_inst
    return np.abs(coherence_acc)

# ---------------- Run with robust checkpointing ----------------
print("Running AIEF-1.3 (final production workflow)...")
results = {cond: [] for cond in CONDITIONS}
start_time = time.time()

for cond in CONDITIONS:
    for s, seed in enumerate(SEEDS):
        run_file = os.path.join(RUN_DIR, f"{cond}_seed_{seed}.npz")

        if os.path.exists(run_file):
            print(f"  Loading existing {run_file}")
            try:
                res = load_checkpoint(run_file)
                if res.get("config_hash") != CONFIG_HASH:
                    raise RuntimeError("Configuration hash mismatch")
                if res["condition"] != cond or int(res["seed"]) != seed:
                    raise RuntimeError("Checkpoint identity mismatch")
            except Exception as exc:
                print(f"  Invalid checkpoint {run_file}: {exc} — recomputing")
                os.remove(run_file)
                res = run_aief(cond, seed=seed)
                res["config_hash"] = CONFIG_HASH
                save_checkpoint_atomic(run_file, res)
        else:
            res = run_aief(cond, seed=seed)
            res["config_hash"] = CONFIG_HASH
            save_checkpoint_atomic(run_file, res)

        results[cond].append(res)
        if (s + 1) % 5 == 0:
            print(f"  {cond}: {s+1}/{N_SEEDS} seeds available")

print(f"Total runtime: {time.time() - start_time:.1f} s\n")

# ---------------- Build aggregate outputs ----------------
matrix_output = {}
scalar_rows = []

for cond, runs in results.items():
    for run in runs:
        prefix = f"{cond}_seed_{run['seed']}"
        for key in ["B_at_split", "P_future", "R_physical_past", "R_driver_past",
                    "R_physical_future", "R_driver_future", "B_final"]:
            matrix_output[f"{prefix}_{key}"] = run[key]

        scalar_rows.append({
            "condition": cond,
            "seed": run["seed"],
            "D_B": run["D_B"],
            "Corr_physical": run["Corr_physical"],
            "Corr_driver": run["Corr_driver"],
            "Phi": run["Phi"],
            "r_mean": run["r_mean"],
            "S_spectral": run["S_spectral"],
            "G_min_final": run["G_min_final"],
            "G_min_over_time": run["G_min_over_time"],
            "G_min_pre_over_time": run["G_min_pre_over_time"],
            "P_mean": run["P_mean"],
            "P_variance": run["P_variance"],
            "P_degenerate": run["P_degenerate"],
            "Cov_physical": run["Cov_physical"],
            "Cov_driver": run["Cov_driver"],
        })

np.savez_compressed(
    os.path.join(RUN_DIR, f"AIEF_1_3_{CONFIG_HASH}_edge_diagnostics.npz"),
    **matrix_output
)

csv_file = os.path.join(RUN_DIR, f"AIEF_1_3_{CONFIG_HASH}_scalar_summary.csv")
with open(csv_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=scalar_rows[0].keys())
    writer.writeheader()
    writer.writerows(scalar_rows)

print("Saved to", RUN_DIR)
print(f"  manifest.json")
print(f"  AIEF_1_3_{CONFIG_HASH}_edge_diagnostics.npz")
print(f"  AIEF_1_3_{CONFIG_HASH}_scalar_summary.csv")
print(f"  runs/ (per-seed checkpoints)")

# ---------------- Summary ----------------
print("=" * 155)
print("AIEF-1.3 FALSIFICATION MATRIX — Summary (mean ± std, NaN-safe)")
print("=" * 155)
print(f"{'Condition':<18} {'D_B':>10} {'Corr_phys':>11} {'Corr_drv':>10} {'Phi':>10} {'r_mean':>10} {'S_spectral':>11} {'G_min_fin':>10} {'G_min_traj':>11} {'G_min_pre':>10}  valid")
print("-" * 155)

for cond in CONDITIONS:
    vals = results[cond]
    c_phys_m, c_phys_s, n_phys = summarize([v["Corr_physical"] for v in vals])
    c_drv_m,  c_drv_s,  n_drv  = summarize([v["Corr_driver"] for v in vals])
    phi_m,    phi_s,    n_phi  = summarize([v["Phi"] for v in vals])

    print(f"{cond:<18} "
          f"{np.nanmean([v['D_B'] for v in vals]):6.3f}±{np.nanstd([v['D_B'] for v in vals]):4.3f}  "
          f"{c_phys_m:6.3f}±{c_phys_s:4.3f}  "
          f"{c_drv_m:6.3f}±{c_drv_s:4.3f}  "
          f"{phi_m:6.3f}±{phi_s:4.3f}  "
          f"{np.nanmean([v['r_mean'] for v in vals]):5.3f}±{np.nanstd([v['r_mean'] for v in vals]):4.3f}  "
          f"{np.nanmean([v['S_spectral'] for v in vals]):6.3f}±{np.nanstd([v['S_spectral'] for v in vals]):4.3f}  "
          f"{np.nanmean([v['G_min_final'] for v in vals]):6.3f}±{np.nanstd([v['G_min_final'] for v in vals]):4.3f}  "
          f"{np.nanmean([v['G_min_over_time'] for v in vals]):6.3f}±{np.nanstd([v['G_min_over_time'] for v in vals]):4.3f}  "
          f"{np.nanmean([v['G_min_pre_over_time'] for v in vals]):6.3f}±{np.nanstd([v['G_min_pre_over_time'] for v in vals]):4.3f}   "
          f"Cp:{n_phys} Cd:{n_drv} Φ:{n_phi}")

print("=" * 155)
print("\nNote: Corr_physical = past physical resonance → future persistence (non-overlapping windows).")
print("      Corr_driver = actual adaptation driver (identical except in shuffle_R).")
print("      All edge-level matrices saved for mediation / partial-correlation analysis.")
print("      G_min_pre = minimum pre-projection gap pressure.")
print("      Degeneracy metrics (P_variance, Cov_*) available when correlation is undefined.")
print(f"      Run directory: {RUN_DIR}")
