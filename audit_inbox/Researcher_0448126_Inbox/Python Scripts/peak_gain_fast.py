"""
Fast prototype for Program 1.

Design:
  - Cheap objective during optimization: coarse grid (n_grid=200), no refine,
    adaptive t_max based on spectral abscissa.
  - Fine evaluation only for the final best solution.
  - Smart initialization from the 2x2 threshold on the slowest pair.
  - Continuation over rho as an option.
"""

import numpy as np
from scipy.linalg import expm, eigvals
from scipy.optimize import minimize


def spectral_abscissa(A):
    return np.max(np.real(eigvals(A)))


def peak_gain_fast(A, t_max=20.0, n_grid=200):
    """Cheap peak gain: coarse grid only. Returns (G, t_star)."""
    alpha = spectral_abscissa(A)
    if alpha >= 0:
        return np.inf, 0.0
    t_max_eff = min(t_max, 6.0 / max(-alpha, 1e-8))
    t_grid = np.linspace(0.0, t_max_eff, n_grid)
    best_G = 1.0
    best_t = 0.0
    for t in t_grid:
        try:
            g = np.linalg.norm(expm(t * A), 2)
        except np.linalg.LinAlgError:
            return np.inf, 0.0
        if g > best_G:
            best_G = g
            best_t = t
    return best_G, best_t


def peak_gain_fine(A, t_max=25.0, n_grid=2000):
    """Fine peak gain with log-scale refinement around the best grid point."""
    from scipy.optimize import golden

    alpha = spectral_abscissa(A)
    if alpha >= 0:
        return np.inf, 0.0
    t_max_eff = min(t_max, 8.0 / max(-alpha, 1e-8))
    t_grid = np.linspace(0.0, t_max_eff, n_grid)
    norms = np.empty(n_grid)
    for i, t in enumerate(t_grid):
        try:
            norms[i] = np.linalg.norm(expm(t * A), 2)
        except np.linalg.LinAlgError:
            norms[i] = np.inf
    i_best = int(np.argmax(norms))
    G = norms[i_best]
    t_star = t_grid[i_best]
    if np.isinf(G) or i_best in (0, n_grid - 1):
        return G, t_star

    lo = max(1e-6, t_grid[i_best - 1])
    hi = t_grid[i_best + 1]

    def neg_norm(log_t):
        try:
            return -np.linalg.norm(expm(np.exp(log_t) * A), 2)
        except np.linalg.LinAlgError:
            return np.inf

    res = golden(neg_norm, brack=(np.log(lo), np.log(hi)), tol=1e-4, full_output=True)
    t_cand = np.exp(res[0])
    try:
        G_cand = np.linalg.norm(expm(t_cand * A), 2)
    except np.linalg.LinAlgError:
        G_cand = -np.inf
    if G_cand > G:
        G = G_cand
        t_star = t_cand
    return G, t_star


def pack_UV(U, V):
    return np.concatenate([U.ravel(), V.ravel()])


def unpack_UV(x, n, r):
    U = x[: n * r].reshape(n, r)
    V = x[n * r :].reshape(n, r)
    return U, V


def make_objective(D, r, rho, delta, penalty=1e8, t_max=15.0):
    n = D.shape[0]

    def fun(x):
        U, V = unpack_UV(x, n, r)
        E = U @ V.T
        A = D + E
        alpha = spectral_abscissa(A)
        viol_alpha = max(0.0, alpha + delta)
        fro = np.linalg.norm(E, "fro")
        viol_fro = max(0.0, fro - rho)
        G, _ = peak_gain_fast(A, t_max=t_max, n_grid=150)
        if np.isinf(G):
            return 1e10 + penalty * (viol_alpha ** 2 + viol_fro ** 2)
        return -G + penalty * (viol_alpha ** 2 + viol_fro ** 2)

    return fun


def make_constraints(D, r, rho, delta, n):
    def cons_alpha(x):
        U, V = unpack_UV(x, n, r)
        return -(spectral_abscissa(D + U @ V.T) + delta)

    def cons_fro(x):
        U, V = unpack_UV(x, n, r)
        return rho - np.linalg.norm(U @ V.T, "fro")

    return [
        {"type": "ineq", "fun": cons_alpha},
        {"type": "ineq", "fun": cons_fro},
    ]


def structured_init(D, r, rho, delta, mode="slowest_pair"):
    n = D.shape[0]
    d = -np.diag(D)
    U = np.zeros((n, r))
    V = np.zeros((n, r))
    if mode == "slowest_pair" and r >= 1 and n >= 2:
        idx = np.argsort(d)[:2]
        i, j = int(idx[0]), int(idx[1])
        a, b = d[i], d[j]
        c_crit = 2.0 * np.sqrt(a * b)
        c = min(c_crit * 1.2, rho * 0.9)
        U[i, 0] = c
        V[j, 0] = 1.0
    elif mode == "random":
        rng = np.random.default_rng(3)
        U = rng.normal(0, 0.3, size=(n, r))
        V = rng.normal(0, 0.3, size=(n, r))
        E = U @ V.T
        fro = np.linalg.norm(E, "fro")
        if fro > 0:
            scale = np.sqrt(rho * 0.5 / fro)
            U = U * scale
            V = V * scale
    return pack_UV(U, V)


def run_experiment(n, d, r, rho, delta, n_restarts=5, seed=0, t_max=15.0):
    rng = np.random.default_rng(seed)
    D = -np.diag(d)
    constraints = make_constraints(D, r, rho, delta, n)
    fun = make_objective(D, r, rho, delta, t_max=t_max)

    best = None
    results = []
    modes = ["slowest_pair"] + ["random"] * (n_restarts - 1)

    for k, mode in enumerate(modes):
        x0 = structured_init(D, r, rho, delta, mode=mode)
        res = minimize(
            fun, x0, method="SLSQP", constraints=constraints,
            options={"maxiter": 200, "ftol": 1e-9, "disp": False},
        )
        U, V = unpack_UV(res.x, n, r)
        E = U @ V.T
        A = D + E
        alpha = spectral_abscissa(A)
        G, t_star = peak_gain_fine(A, t_max=t_max)
        results.append(
            {"restart": k, "mode": mode, "success": res.success, "G": G,
             "t_star": t_star, "alpha": alpha,
             "fro": np.linalg.norm(E, "fro"), "E": E, "U": U, "V": V}
        )
        if best is None or G > best["G"]:
            best = results[-1]
    return best, results, D


def sweep_rho():
    print("=" * 60)
    print("n=3, d=[1,2,4], r=1, delta=0.1: sweep rho (fast version)")
    print("Slowest pair (1,2): c_crit = 2*sqrt(2) = 2.828")
    print("=" * 60)
    for rho in [1.0, 2.0, 2.8, 2.83, 2.9, 3.2, 3.5, 4.0, 5.0, 8.0]:
        best, results, D = run_experiment(
            n=3, d=[1.0, 2.0, 4.0], r=1, rho=rho, delta=0.1,
            n_restarts=4, seed=100, t_max=15.0,
        )
        print(f"rho={rho:5.2f}: G={best['G']:9.6f}  t*={best['t_star']:6.4f}  "
              f"alpha={best['alpha']: .6f}  ||E||_F={best['fro']:.6f}  "
              f"mode={best['mode']}")
        if best["G"] > 1.001:
            print(f"   E* = {np.round(best['E'].ravel(), 4)}")


def rank2_example():
    """
    n=3, d=[1,2,4], r=2. With rank 2, we can couple both (1,2) and (2,3)
    or use a richer structure. See if G > 1 at lower rho than rank 1.
    """
    print("\n" + "=" * 60)
    print("Rank comparison: n=3, d=[1,2,4], delta=0.1, rho=3.0")
    print("r=1 c_crit(pair 1,2) = 2.828; rho=3.0 barely above")
    print("=" * 60)
    for r in [1, 2]:
        best, results, D = run_experiment(
            n=3, d=[1.0, 2.0, 4.0], r=r, rho=3.0, delta=0.1,
            n_restarts=4, seed=55, t_max=15.0,
        )
        print(f"r={r}: G={best['G']:9.6f}  t*={best['t_star']:6.4f}  "
              f"alpha={best['alpha']: .6f}  ||E||_F={best['fro']:.6f}")
        if best["G"] > 1.001:
            print(f"   E* = {np.round(best['E'].ravel(), 4)}")


if __name__ == "__main__":
    sweep_rho()
    rank2_example()
