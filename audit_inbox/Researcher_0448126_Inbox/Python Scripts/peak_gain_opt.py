"""
Program 1: Norm-constrained low-rank peak-gain optimization.

Given D = -diag(d_1,...,d_n) with d_i > 0, maximize
    G(D+E) = sup_{t>=0} ||exp(t (D+E))||_2
over
    rank(E) <= r,  ||E||_F <= rho,  alpha(D+E) <= -delta.

We parameterize E = U V^T with U, V in R^{n x r} and optimize
over the stacked vector [U; V] using scipy.optimize with penalties
for the constraints (or SLSQP with explicit constraints).

Includes:
- peak_gain(A): compute sup_t ||e^{tA}||_2 by scanning t + local refinement
- spectral_abscissa(A): max real eigenvalue
- objective + constraint functions for SLSQP
- driver for small experiments (n=2,3,4)
"""

import numpy as np
from scipy.linalg import expm, eigvals
from scipy.optimize import minimize
import matplotlib.pyplot as plt


def spectral_abscissa(A):
    """max real part of eigenvalues of A"""
    return np.max(np.real(eigvals(A)))


def peak_gain(A, t_max=50.0, n_grid=2000, refine=True):
    """
    Compute G(A) = sup_{t>=0} ||e^{tA}||_2.
    Strategy:
      1. coarse grid scan over [0, t_max]
      2. if refine, do a local golden-section search around the best grid point
         (in log-t space to capture behavior near 0 and at large t)
    Returns (G, t_star).
    Assumes A is Hurwitz (spectral abscissa < 0) so norm -> 0 as t->infty.
    If A is not Hurwitz, returns (inf, 0.0) to signal infeasibility.
    """
    alpha = spectral_abscissa(A)
    if alpha >= 0:
        return np.inf, 0.0

    # choose t_max adaptively: need to see decay, ~5/|alpha| is usually enough
    t_max_eff = min(t_max, 8.0 / max(-alpha, 1e-6))
    # coarse grid, biased toward small t where transient growth usually happens
    t_grid = np.linspace(0.0, t_max_eff, n_grid)
    norms = np.empty_like(t_grid)
    for i, t in enumerate(t_grid):
        try:
            norms[i] = np.linalg.norm(expm(t * A), 2)
        except np.linalg.LinAlgError:
            norms[i] = np.inf
    i_best = int(np.argmax(norms))
    G = norms[i_best]
    t_star = t_grid[i_best]

    if np.isinf(G):
        return G, t_star

    if refine and i_best not in (0, n_grid - 1) and G > 1.0:
        # local refine on log scale around t_best
        lo = max(1e-8, t_grid[i_best - 1])
        hi = t_grid[i_best + 1]

        def neg_norm(log_t):
            tt = np.exp(log_t)
            try:
                return -np.linalg.norm(expm(tt * A), 2)
            except np.linalg.LinAlgError:
                return np.inf

        # golden section
        gr = (np.sqrt(5) - 1) / 2
        a, b = np.log(lo), np.log(hi)
        c = b - gr * (b - a)
        d = a + gr * (b - a)
        for _ in range(60):
            if neg_norm(c) < neg_norm(d):
                b = d
            else:
                a = c
            c = b - gr * (b - a)
            d = a + gr * (b - a)
        t_log = (a + b) / 2
        t_cand = np.exp(t_log)
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


def make_objective(D, r, rho, delta, penalty=1e6, t_max=30.0):
    n = D.shape[0]

    def fun(x):
        U, V = unpack_UV(x, n, r)
        E = U @ V.T
        A = D + E

        # hard constraint: spectral abscissa <= -delta
        alpha = spectral_abscissa(A)
        viol_alpha = max(0.0, alpha + delta)

        # soft constraint: Frobenius norm <= rho
        fro = np.linalg.norm(E, "fro")
        viol_fro = max(0.0, fro - rho)

        # rank is enforced by parameterization (exactly rank <= r)

        G, _ = peak_gain(A, t_max=t_max, n_grid=800, refine=False)

        # maximize G => minimize -G, plus penalties
        pen = penalty * (viol_alpha ** 2 + viol_fro ** 2)
        return -G + pen

    return fun


def run_experiment(n, d, r, rho, delta, n_restarts=5, seed=0, t_max=30.0):
    """
    Run multiple random restarts of the optimization.
    d: array of decay rates (positive), D = -diag(d)
    """
    rng = np.random.default_rng(seed)
    D = -np.diag(d)

    best = None
    results = []

    for k in range(n_restarts):
        # random initialization: small random low-rank perturbation
        U0 = rng.normal(0, 0.1, size=(n, r))
        V0 = rng.normal(0, 0.1, size=(n, r))
        x0 = pack_UV(U0, V0)

        fun = make_objective(D, r, rho, delta, t_max=t_max)

        # constraints: spectral_abscissa(D+E) + delta <= 0  (inequality >= 0 form)
        #            rho - ||E||_F >= 0
        def cons_alpha(x):
            U, V = unpack_UV(x, n, r)
            return -(spectral_abscissa(D + U @ V.T) + delta)  # >= 0

        def cons_fro(x):
            U, V = unpack_UV(x, n, r)
            return rho - np.linalg.norm(U @ V.T, "fro")  # >= 0

        constraints = [
            {"type": "ineq", "fun": cons_alpha},
            {"type": "ineq", "fun": cons_fro},
        ]

        res = minimize(
            fun,
            x0,
            method="SLSQP",
            constraints=constraints,
            options={"maxiter": 300, "ftol": 1e-9, "disp": False},
        )

        U, V = unpack_UV(res.x, n, r)
        E = U @ V.T
        A = D + E
        alpha = spectral_abscissa(A)
        G, t_star = peak_gain(A, t_max=t_max, n_grid=2000, refine=True)

        results.append(
            {
                "restart": k,
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


def test_trivial_regime(n=4, seed=1):
    """
    Verify: if rho <= min(d_i), then G = 1 for all admissible E.
    """
    print("=" * 60)
    print("Trivial small-budget regime test")
    print("=" * 60)
    rng = np.random.default_rng(seed)
    d = np.array([1.0, 2.0, 3.0, 5.0])[:n]
    d_min = d.min()
    D = -np.diag(d)
    rho = 0.5 * d_min  # safely below d_min
    delta = 0.1
    r = 2

    # random admissible E with small norm
    U = rng.normal(0, 0.1, size=(n, r))
    V = rng.normal(0, 0.1, size=(n, r))
    E = U @ V.T
    E = E * (rho / (2 * np.linalg.norm(E, "fro")))  # scale down
    A = D + E
    G, t_star = peak_gain(A, t_max=20.0)
    print(f"d = {d}, d_min = {d_min}, rho = {rho}")
    print(f"rho <= d_min? {rho <= d_min}")
    print(f"spectral abscissa of A = {spectral_abscissa(A):.6f}")
    print(f"G(A) = {G:.8f} (should be ~1.0)")
    print(f"t_star = {t_star:.6f}")
    print()


def test_unbounded_without_budget(n=3, seed=2):
    """
    Verify: without Frobenius budget, rank-one triangular perturbation
    E_c = c e_i e_j^T (i != j) leaves eigenvalues unchanged but peak gain
    grows without bound as |c| -> infinity.
    """
    print("=" * 60)
    print("Unboundedness without norm budget (rank-one triangular)")
    print("=" * 60)
    rng = np.random.default_rng(seed)
    d = np.array([1.0, 2.0, 4.0])[:n]
    D = -np.diag(d)
    i, j = 0, 1  # i != j

    for c in [0.1, 1.0, 10.0, 50.0, 200.0]:
        E = np.zeros((n, n))
        E[i, j] = c
        A = D + E
        alpha = spectral_abscissa(A)
        # eigenvalues of D+E are same as D (triangular with same diagonal)
        G, t_star = peak_gain(A, t_max=10.0)
        print(f"c = {c:6.1f}  alpha = {alpha: .6f}  G = {G:10.4f}  t* = {t_star:.4f}")
    print("Eigenvalues unchanged (triangular), but G grows with |c|.")
    print()


if __name__ == "__main__":
    test_trivial_regime()
    test_unbounded_without_budget()

    # Example optimization run
    print("=" * 60)
    print("Example optimization: n=3, d=[1,2,4], r=1, rho=2.0, delta=0.2")
    print("=" * 60)
    best, results, D = run_experiment(
        n=3, d=[1.0, 2.0, 4.0], r=1, rho=2.0, delta=0.2,
        n_restarts=3, seed=42, t_max=20.0,
    )
    print(f"Best G = {best['G']:.6f} at t* = {best['t_star']:.4f}")
    print(f"alpha = {best['alpha']:.6f} (constraint: <= -0.2)")
    print(f"||E||_F = {best['fro']:.6f} (constraint: <= 2.0)")
    print("E* =")
    print(np.round(best["E"], 4))
    print()
