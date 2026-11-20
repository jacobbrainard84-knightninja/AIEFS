"""
Program 1 sweep: explore nontrivial regime and compare with analytic 2x2 result.

For L = [[-a, c],[0, -b]] with a,b>0:
  transient growth iff c^2 > 4 a b   (from the user's note)
  G > 1 exactly when |c| > 2 sqrt(a b)

We verify:
1. The 2x2 numeric peak gain matches the analytic threshold.
2. For n>2 with rank-1 budget rho, we can find E giving G > 1 when rho is large enough.
3. Structure of the optimizer: does it concentrate on the slowest pair?
"""

import numpy as np
from scipy.linalg import expm, eigvals
from peak_gain_opt import peak_gain, spectral_abscissa, run_experiment, unpack_UV, pack_UV


def analytic_2x2_threshold(a, b):
    return 2.0 * np.sqrt(a * b)


def numeric_2x2_gain(a, b, c):
    """Build L = [[-a, c],[0, -b]] and compute G numerically."""
    L = np.array([[-a, c], [0.0, -b]])
    return peak_gain(L, t_max=20.0, n_grid=2000, refine=True)


def sweep_2x2():
    print("=" * 60)
    print("2x2 analytic vs numeric threshold: c_crit = 2*sqrt(a*b)")
    print("=" * 60)
    for (a, b) in [(1.0, 2.0), (1.0, 1.0), (0.5, 3.0)]:
        c_crit = analytic_2x2_threshold(a, b)
        print(f"\na={a}, b={b}, c_crit = {c_crit:.4f}")
        for c in [0.0, 0.5 * c_crit, 0.9 * c_crit, c_crit, 1.1 * c_crit, 2.0 * c_crit]:
            G, t_star = numeric_2x2_gain(a, b, c)
            flag = "GROWTH" if G > 1.001 else "contractive"
            print(f"  c={c:8.4f}  G={G:10.6f}  t*={t_star:7.4f}  {flag}")


def sweep_rank1_n3():
    """
    n=3, d=[1,2,4], r=1. Vary rho. The slowest pair is (d1,d2)=(1,2)
    with c_crit = 2*sqrt(2) ≈ 2.828. With rho just above that, we should
    see G > 1 from a rank-1 perturbation coupling species 1 and 2.
    """
    print("\n" + "=" * 60)
    print("n=3, d=[1,2,4], r=1, delta=0.1: sweep rho")
    print("Slowest pair (1,2): c_crit = 2*sqrt(1*2) = 2.828")
    print("=" * 60)
    for rho in [1.0, 2.0, 2.9, 3.5, 5.0, 8.0]:
        best, results, D = run_experiment(
            n=3, d=[1.0, 2.0, 4.0], r=1, rho=rho, delta=0.1,
            n_restarts=4, seed=100, t_max=20.0,
        )
        print(f"\nrho = {rho:5.2f}:  best G = {best['G']:.6f}  t* = {best['t_star']:.4f}")
        print(f"   alpha = {best['alpha']: .6f}  ||E||_F = {best['fro']:.6f}")
        print(f"   E* = {np.round(best['E'].ravel(), 4)}")


def optimizer_structure():
    """
    Look at whether the optimizer aligns E with the slowest spectral direction.
    For d=[1, 10, 100], the slow mode is d1=1. Rank-1 E coupling 1->2 should
    dominate over coupling to faster modes.
    """
    print("\n" + "=" * 60)
    print("Optimizer structure: n=3, d=[1,10,100], r=1, rho=5, delta=0.1")
    print("=" * 60)
    best, results, D = run_experiment(
        n=3, d=[1.0, 10.0, 100.0], r=1, rho=5.0, delta=0.1,
        n_restarts=5, seed=7, t_max=20.0,
    )
    print(f"Best G = {best['G']:.6f} at t* = {best['t_star']:.4f}")
    print(f"alpha = {best['alpha']: .6f}, ||E||_F = {best['fro']:.6f}")
    print("E* =")
    print(np.round(best["E"], 4))
    print("Left factor U* =", np.round(best["U"].ravel(), 4))
    print("Right factor V* =", np.round(best["V"].ravel(), 4))


if __name__ == "__main__":
    sweep_2x2()
    sweep_rank1_n3()
    optimizer_structure()
