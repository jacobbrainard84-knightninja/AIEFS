"""
Improved Program 1 optimizer with smart initialization.

Key fix: initialize E with a rank-1 perturbation on the slowest spectral pair
at coupling just above the 2x2 transient-growth threshold, then let SLSQP
refine. Also uses a continuation over rho and a basin-hopping-style restart
from structured (not random) initializations.
"""

import numpy as np
from scipy.linalg import expm, eigvals
from scipy.optimize import minimize, differential_evolution
from peak_gain_opt import peak_gain, spectral_abscissa, pack_UV, unpack_UV


def spectral_abscissa(A):
    return np.max(np.real(eigvals(A)))


def make_objective(D, r, rho, delta, penalty=1e7, t_max=25.0):
    n = D.shape[0]

    def fun(x):
        U, V = unpack_UV(x, n, r)
        E = U @ V.T
        A = D + E
        alpha = spectral_abscissa(A)
        viol_alpha = max(0.0, alpha + delta)
        fro = np.linalg.norm(E, "fro")
        viol_fro = max(0.0, fro - rho)
        G, _ = peak_gain(A, t_max=t_max, n_grid=1000, refine=False)
        if np.isinf(G):
            # unstable or overflow: heavy penalty
            return 1e10 + penalty * (viol_alpha ** 2 + viol_fro ** 2)
        pen = penalty * (viol_alpha ** 2 + viol_fro ** 2)
        return -G + pen

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
    """
    Build an initial E that is likely to produce transient growth.
    mode='slowest_pair': put rank-1 coupling between the two slowest decaying
        species at coupling c just above 2*sqrt(d_i*d_j).
    mode='random': small random low-rank.
    """
    n = D.shape[0]
    d = -np.diag(D)  # positive decay rates
    U = np.zeros((n, r))
    V = np.zeros((n, r))

    if mode == "slowest_pair" and r >= 1 and n >= 2:
        # slowest two decay rates (smallest d_i)
        idx = np.argsort(d)[:2]
        i, j = idx[0], idx[1]
        a, b = d[i], d[j]
        c_crit = 2.0 * np.sqrt(a * b)
        # use coupling slightly above threshold but within budget
        c = min(c_crit * 1.15, rho * 0.9)
        # ensure spectral abscissa constraint: triangular perturbation keeps
        # eigenvalues unchanged, so alpha(D+E) = alpha(D) = -min(d) <= -delta?
        # Need -min(d) <= -delta => delta <= min(d). Assume caller ensures this.
        U[i, 0] = c
        V[j, 0] = 1.0  # E[i,j] = c
    elif mode == "random":
        rng = np.random.default_rng(1)
        U = rng.normal(0, 0.3, size=(n, r))
        V = rng.normal(0, 0.3, size=(n, r))
        # scale to use a good fraction of budget
        fro = np.linalg.norm(U @ V.T, "fro")
        if fro > 0:
            U = U * (rho * 0.7 / fro)
            V = V * (rho * 0.7 / fro)  # this over-scales; fix below
            # actually just scale E
            E = U @ V.T
            fro = np.linalg.norm(E, "fro")
            if fro > 0:
                U = U * np.sqrt(rho * 0.7 / fro)

    return pack_UV(U, V)


def run_experiment_smart(n, d, r, rho, delta, n_restarts=6, seed=0, t_max=25.0):
    rng = np.random.default_rng(seed)
    D = -np.diag(d)
    constraints = make_constraints(D, r, rho, delta, n)
    fun = make_objective(D, r, rho, delta, t_max=t_max)

    best = None
    results = []

    # Initialization modes
    modes = ["slowest_pair"] + ["random"] * (n_restarts - 1)

    for k, mode in enumerate(modes):
        x0 = structured_init(D, r, rho, delta, mode=mode)

        res = minimize(
            fun,
            x0,
            method="SLSQP",
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-10, "disp": False},
        )

        U, V = unpack_UV(res.x, n, r)
        E = U @ V.T
        A = D + E
        alpha = spectral_abscissa(A)
        G, t_star = peak_gain(A, t_max=t_max, n_grid=3000, refine=True)

        results.append(
            {
                "restart": k,
                "mode": mode,
                "success": res.success,
                "G": G,
                "t_star": t_star,
                "alpha": alpha,
                "fro": np.linalg.norm(E, "fro"),
                "E": E,
                "U": U,
                "V": V,
            }
        )

        if best is None or G > best["G"]:
            best = results[-1]

    return best, results, D


def sweep_rho_smart():
    print("=" * 60)
    print("Smart initialization: n=3, d=[1,2,4], r=1, delta=0.1, sweep rho")
    print("Slowest pair (1,2): c_crit = 2*sqrt(2) = 2.828")
    print("=" * 60)
    for rho in [1.0, 2.0, 2.9, 3.5, 5.0, 8.0, 15.0]:
        best, results, D = run_experiment_smart(
            n=3, d=[1.0, 2.0, 4.0], r=1, rho=rho, delta=0.1,
            n_restarts=4, seed=100, t_max=20.0,
        )
        print(f"\nrho = {rho:5.2f}:  best G = {best['G']:.6f}  t* = {best['t_star']:.4f}")
        print(f"   alpha = {best['alpha']: .6f}  ||E||_F = {best['fro']:.6f}")
        print(f"   E* = {np.round(best['E'].ravel(), 4)}")


def optimizer_structure_smart():
    print("\n" + "=" * 60)
    print("Structure: n=3, d=[1,10,100], r=1, rho=6, delta=0.1")
    print("Slowest pair (1,2): c_crit = 2*sqrt(10) = 6.32. rho=6 < c_crit,")
    print("so no growth expected from just that pair. But rank-1 can couple")
    print("through the middle mode. Let's see what optimizer finds.")
    print("=" * 60)
    best, results, D = run_experiment_smart(
        n=3, d=[1.0, 10.0, 100.0], r=1, rho=6.0, delta=0.1,
        n_restarts=5, seed=7, t_max=20.0,
    )
    print(f"Best G = {best['G']:.6f} at t* = {best['t_star']:.4f}")
    print(f"alpha = {best['alpha']: .6f}, ||E||_F = {best['fro']:.6f}")
    print("E* =")
    print(np.round(best["E"], 4))


def continuation_rho():
    """
    Continuation: start at large rho where growth is easy, then decrease rho,
    warm-starting from the previous solution. Tracks how G* and E* evolve.
    """
    print("\n" + "=" * 60)
    print("Continuation in rho: n=3, d=[1,2,4], r=1, delta=0.1")
    print("=" * 60)
    n, d, r, delta = 3, [1.0, 2.0, 4.0], 1, 0.1
    D = -np.diag(d)
    constraints = make_constraints(D, r, 99.0, delta, n)  # loose for first

    x_prev = structured_init(D, r, 99.0, delta, mode="slowest_pair")

    for rho in [9.0, 6.0, 4.0, 3.2, 2.9, 2.83, 2.8, 2.0, 1.0]:
        fun = make_objective(D, r, rho, delta, t_max=20.0)
        constraints = make_constraints(D, r, rho, delta, n)
        res = minimize(
            fun, x_prev, method="SLSQP", constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-10, "disp": False},
        )
        x_prev = res.x
        U, V = unpack_UV(res.x, n, r)
        E = U @ V.T
        A = D + E
        alpha = spectral_abscissa(A)
        G, t_star = peak_gain(A, t_max=20.0, n_grid=3000, refine=True)
        print(f"rho={rho:5.2f}: G={G:9.6f}  t*={t_star:6.4f}  "
              f"alpha={alpha: .6f}  ||E||_F={np.linalg.norm(E,'fro'):.6f}")


if __name__ == "__main__":
    sweep_rho_smart()
    optimizer_structure_smart()
    continuation_rho()
