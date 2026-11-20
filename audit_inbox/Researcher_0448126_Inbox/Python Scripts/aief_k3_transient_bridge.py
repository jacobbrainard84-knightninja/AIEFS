"""
AIEF K3 -> transient-gain bridge analysis.

Self-contained computational bridge between:
  (A) the AIEF-1.4 exceptional K3 analytic objects documented in
      AIEF_1_4_FORWARD_PLAN.md and AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md
      (analytic K3 pair u, v; raw defect E_*; biorthogonal closure),
  (B) the transient-gain framework G(A) = sup_t ||e^{tA}||_2 and the
      low-rank peak-gain optimization (Program 1 / Program 2).

Open question addressed (from biorthogonal_triangular_closure.py docstring):
  "decide whether direction-0 rollout failure is a Euclidean-coordinate
  artifact or requires an additional mode."

Method:
  1. Build a 3x3 upper-triangular generator D + c*E_* where D = -diag(d)
     is the slow-rate diagonal and E_* is the analytic raw defect
         [[-1, 0, -1],
          [0, 0, 0],
          [0, 0, 0]]
     (the defect preserves the right line but breaks the fixed-left relation,
      per the operator theory manuscript).
  2. Compute Euclidean peak gain G_E = sup_t ||e^{tA}||_2 and its maximizer t*.
  3. Compute the biorthogonal scalar amplitude using the analytic K3 pair
     v = (1,-1,-1)/sqrt(3), u = (sqrt(3)/2)(1,0,-1), u^T v = 1:
         a(t) = u^T e^{tA} x0,   x0 = v   (start in the late right direction)
     and its peak |a|_max.
  4. Compare G_E vs |a|_max. If |a|_max << G_E, the Euclidean peak is driven
     by a direction the biorthogonal scalar misses -> additional mode needed.
     If |a|_max ≈ G_E, the biorthogonal coordinate captures the transient.
  5. Sweep the defect coupling c and the stability margin delta to map the
     threshold where transient growth appears (analog of c^2 > 4 alpha beta).

No external data files required. Reproduces the 2x2 analytic threshold as a
sanity check, then extends to the 3x3 K3 defect structure.
"""

import numpy as np
from scipy.linalg import expm, eigvals


# ---------------------------------------------------------------------------
# Core linear algebra
# ---------------------------------------------------------------------------

def spectral_abscissa(A):
    return float(np.max(np.real(eigvals(A))))


def peak_gain(A, t_max=40.0, n_grid=4000, refine=True):
    """
    Compute G(A) = sup_{t>=0} ||e^{tA}||_2 via coarse grid + golden-section
    refinement in log-t around the best grid point. Returns (G, t_star).
    Assumes A is Hurwitz (spectral abscissa < 0).
    """
    alpha = spectral_abscissa(A)
    if alpha >= 0:
        return np.inf, 0.0
    t_max_eff = min(t_max, 10.0 / max(-alpha, 1e-8))
    t_grid = np.linspace(0.0, t_max_eff, n_grid)
    norms = np.empty(n_grid)
    for i, t in enumerate(t_grid):
        try:
            norms[i] = np.linalg.norm(expm(t * A), 2)
        except np.linalg.LinAlgError:
            return np.inf, 0.0
    i_best = int(np.argmax(norms))
    G = norms[i_best]
    t_star = t_grid[i_best]
    if np.isinf(G) or not refine or i_best in (0, n_grid - 1):
        return float(G), float(t_star)
    from scipy.optimize import minimize_scalar

    lo = max(1e-8, t_grid[i_best - 1])
    hi = t_grid[i_best + 1]

    def neg_norm(log_t):
        try:
            return -np.linalg.norm(expm(np.exp(log_t) * A), 2)
        except np.linalg.LinAlgError:
            return np.inf

    res = minimize_scalar(neg_norm, bounds=(np.log(lo), np.log(hi)),
                          method="bounded", options={"xatol": 1e-5})
    t_cand = float(np.exp(res.x))
    try:
        G_cand = float(np.linalg.norm(expm(t_cand * A), 2))
    except np.linalg.LinAlgError:
        G_cand = -np.inf
    if G_cand > G:
        G = G_cand
        t_star = t_cand
    return float(G), float(t_star)


def biorthogonal_peak(A, u, v, t_max=40.0, n_grid=4000):
    """
    Peak of |a(t)| = |u^T e^{tA} v| over t in [0, t_max].
    Starts in the late right direction v, reads out through left covector u.
    Returns (peak_abs, t_at_peak, a_trace_sample).
    """
    alpha = spectral_abscissa(A)
    if alpha >= 0:
        return np.inf, 0.0, None
    t_max_eff = min(t_max, 10.0 / max(-alpha, 1e-8))
    t_grid = np.linspace(0.0, t_max_eff, n_grid)
    best = 0.0
    best_t = 0.0
    for t in t_grid:
        try:
            etA = expm(t * A)
        except np.linalg.LinAlgError:
            return np.inf, 0.0, None
        a_val = float(u @ etA @ v)
        av = abs(a_val)
        if av > best:
            best = av
            best_t = float(t)
    return float(best), float(best_t), None


# ---------------------------------------------------------------------------
# Analytic K3 objects (from AIEF_1_4_FORWARD_PLAN.md, section III.3)
# ---------------------------------------------------------------------------

SQRT3 = np.sqrt(3.0)
v = np.array([1.0, -1.0, -1.0]) / SQRT3                    # late right direction
u = (SQRT3 / 2.0) * np.array([1.0, 0.0, -1.0])             # left covector, u^T v = 1

print("u^T v =", float(u @ v), "(should be 1.0)")

# Analytic raw defect from Forward Plan section IV:
E_star_full = np.array([[-1.0, 0.0, -1.0],
                        [ 0.0, 0.0, 0.0],
                        [ 0.0, 0.0, 0.0]])
# Pure off-diagonal coupling defect (isolates the transient mechanism from
# the diagonal damping that E_star_full also carries):
E_star_off = np.array([[ 0.0, 0.0, -1.0],
                       [ 0.0, 0.0, 0.0],
                       [ 0.0, 0.0, 0.0]])
print("\nE_star_full (with diagonal damping) =\n", E_star_full)
print("E_star_off (pure coupling)        =\n", E_star_off)

# ---------------------------------------------------------------------------
# Sanity check: reproduce the 2x2 analytic threshold c^2 > 4 a b
# ---------------------------------------------------------------------------

def peak_gain_2x2(a, b, c):
    L = np.array([[-a, c], [0.0, -b]])
    return peak_gain(L, t_max=20.0, n_grid=3000, refine=True)


print("\n" + "=" * 60)
print("Sanity check: 2x2 transient-growth threshold c^2 > 4ab")
print("=" * 60)
for (a, b) in [(1.0, 2.0), (1.0, 1.0), (0.5, 3.0)]:
    c_crit = 2.0 * np.sqrt(a * b)
    for frac in [0.0, 0.9, 1.0, 1.1, 2.0]:
        c = frac * c_crit
        G, t_star = peak_gain_2x2(a, b, c)
        print(f"a={a:4.1f} b={b:4.1f} c/crit={frac:4.1f}  G={G:10.6f}  "
              f"t*={t_star:7.4f}  {'GROWTH' if G > 1.001 else 'contractive'}")

# ---------------------------------------------------------------------------
# Main experiment: K3 defect perturbation of a diagonal generator
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("K3 defect experiment: A = D + c * E_star, D = -diag(d)")
print("Testing whether biorthogonal scalar captures Euclidean peak gain")
print("=" * 60)

# Choose slow rates analogous to the K3 slow/fast spectral split.
# The K3 forward plan mentions a "slow bundle" and distinct decay rates.
# We parameterize d = (d_slow, d_mid, d_fast) with d_slow << d_fast.
d_sets = {
    "slow_split_1_5_20":   (1.0, 5.0, 20.0),
    "slow_split_1_3_10":   (1.0, 3.0, 10.0),
    "slow_split_0_5_2_8":  (0.5, 2.0, 8.0),
}

for label, d_tuple in d_sets.items():
    d = np.array(d_tuple, dtype=float)
    D = -np.diag(d)
    d_min = d.min()
    print(f"\n--- {label}: d = {d_tuple}, d_min = {d_min:.2f} ---")

    # The defect couples edge (2,7) and (7,11) in K3 indexing; in our 3D
    # reduction E_star_off[0,2] = -1 couples component 0 to component 2.
    # E_star_off is strictly upper triangular -> spectrum unchanged:
    # alpha(D + c E_star_off) = alpha(D) = -d_min.
    print("E_star_off^2 =\n", E_star_off @ E_star_off,
          "  (nilpotent -> spectrum preserved)")

    for c in [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]:
        A = D + c * E_star_off
        alpha = spectral_abscissa(A)
        G_E, t_E = peak_gain(A, t_max=30.0, n_grid=3000, refine=True)
        a_peak, t_a, _ = biorthogonal_peak(A, u, v, t_max=30.0, n_grid=3000)
        ratio = a_peak / G_E if G_E > 0 else np.inf
        print(f"  c={c:5.2f}  alpha={alpha: .6f}  G_E={G_E:10.6f}  "
              f"t*_E={t_E:7.4f}  |a|_max={a_peak:10.6f}  t*_a={t_a:7.4f}  "
              f"ratio={ratio:7.4f}")

    # Also test the full defect (with diagonal damping) at c=4 for contrast:
    A_full = D + 4.0 * E_star_full
    alpha_full = spectral_abscissa(A_full)
    G_full, t_full = peak_gain(A_full, t_max=30.0, n_grid=3000, refine=True)
    a_full, t_a_full, _ = biorthogonal_peak(A_full, u, v,
                                            t_max=30.0, n_grid=3000)
    print(f"  [full E_star, c=4] alpha={alpha_full: .6f}  G_E={G_full:10.6f}  "
          f"t*_E={t_full:7.4f}  |a|_max={a_full:10.6f}  ratio={a_full/G_full if G_full>0 else np.inf:7.4f}")

# ---------------------------------------------------------------------------
# Threshold mapping: minimal c for G_E > 1 (transient-growth onset)
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("Threshold mapping: minimal c giving G_E > 1.001 (transient onset)")
print("=" * 60)

for label, d_tuple in d_sets.items():
    d = np.array(d_tuple, dtype=float)
    D = -np.diag(d)
    # bisection on c in [0, 20]
    lo, hi = 0.0, 20.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        A = D + mid * E_star_off
        G_E, _ = peak_gain(A, t_max=30.0, n_grid=2000, refine=False)
        if G_E > 1.001:
            hi = mid
        else:
            lo = mid
    c_thresh = 0.5 * (lo + hi)
    A_thresh = D + c_thresh * E_star_off
    G_thresh, t_thresh = peak_gain(A_thresh, t_max=30.0, n_grid=4000, refine=True)
    a_peak_thresh, t_a_thresh, _ = biorthogonal_peak(A_thresh, u, v,
                                                      t_max=30.0, n_grid=4000)
    print(f"{label:22s} c_thresh={c_thresh:8.4f}  G_E={G_thresh:10.6f}  "
          f"t*={t_thresh:7.4f}  |a|_max={a_peak_thresh:10.6f}  "
          f"ratio={a_peak_thresh/G_thresh if G_thresh>0 else np.inf:7.4f}")

# ---------------------------------------------------------------------------
# Triangular closure test (discrete analogue)
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("Discrete triangular closure check: a[n+1] = lambda_n a[n] + g[n]")
print("Using K_n = I + h A (Euler step) with the K3 defect, h=0.01")
print("=" * 60)

h = 0.01
d = np.array([1.0, 5.0, 20.0])
D = -np.diag(d)
c = 4.0
A = D + c * E_star_off
K = np.eye(3) + h * A

# Iterate the scalar closure: a_{n+1} = lambda_n a_n + g_n
# where lambda_n = u^T K_n v, g_n = u_{n+1}^T f_n (here f_n = 0, no forcing)
# so a_{n+1} = lambda_n a_n, a_0 = 1.
# Compare with the true Euclidean norm growth of K^n v.
n_steps = 2000
a_scalar = 1.0
a_scalar_trace = [a_scalar]
x = v.copy()
euclid_trace = [np.linalg.norm(x, 2)]
for n in range(n_steps):
    lambda_n = float(u @ K @ v)
    a_scalar = lambda_n * a_scalar
    a_scalar_trace.append(a_scalar)
    x = K @ x
    euclid_trace.append(np.linalg.norm(x, 2))

a_scalar_trace = np.array(a_scalar_trace)
euclid_trace = np.array(euclid_trace)

print(f"lambda_n (constant, since K fixed) = {float(u @ K @ v):.8f}")
print(f"Max |a_scalar| over {n_steps} steps = {np.max(np.abs(a_scalar_trace)):.8f}")
print(f"Max ||K^n v||_2 over {n_steps} steps = {np.max(euclid_trace):.8f}")
print(f"Ratio max_Euclid / max_scalar = "
      f"{np.max(euclid_trace) / np.max(np.abs(a_scalar_trace)):.6f}")
print()
print("If ratio >> 1, the Euclidean transient is NOT captured by the "
      "biorthogonal scalar coordinate -> additional mode required.")
print("If ratio ≈ 1, the biorthogonal scalar closure is sufficient.")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("Bridge analysis complete. Key deliverables:")
print("  1. 2x2 analytic threshold c^2 > 4ab reproduced numerically.")
print("  2. K3 defect peak gain computed in Euclidean norm.")
print("  3. Biorthogonal scalar peak computed via analytic u, v.")
print("  4. Threshold c for transient onset mapped per d-split.")
print("  5. Discrete triangular closure tested; ratio reported.")
print("=" * 60)
