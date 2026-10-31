"""Red-team negative controls with NO existing repo checker behind them:

1. Settle threshold. Nothing in CI recomputes the edge settle threshold R* = (mu + gamma*B_c)/(eta + mu)
   (0.4543 with the frozen constants). This file adds an independent check: it reads the frozen
   constants from aief_experiment_engine_v1.py with `ast` (no import, nothing executed) and runs
   the engine's own ungated edge update B <- max(0, B + dt*((eta+mu)*R - mu - gamma*B)) at constant R.
   Fabricated thresholds 0.40 and 0.50 must be rejected; 0.4543 must be accepted.
2. Swapped expected/actual. The comparator's cmp_arrays / mask_mismatches (extracted with `ast`
   from the hash-pinned script, not executed as a script) must give the same verdict either way.
"""
import ast
import os
import unittest

import numpy as np

from rtcommon import REPO

ENGINE = os.path.join(REPO, "aief_experiment_engine_v1.py")
CMP = os.path.join(REPO, "audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.py")


def module_constants(path, names):
    with open(path) as f:
        tree = ast.parse(f.read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in names:
                out[node.targets[0].id] = ast.literal_eval(node.value)
    missing = set(names) - set(out)
    if missing:
        raise AssertionError(f"constants not found: {missing}")
    return out


def load_functions(path, names, consts):
    with open(path) as f:
        tree = ast.parse(f.read())
    keep = [n for n in tree.body if
            (isinstance(n, ast.FunctionDef) and n.name in names) or
            (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in consts)]
    ns = {"np": np}
    exec(compile(ast.Module(body=keep, type_ignores=[]), path, "exec"), ns)
    return ns


C = module_constants(ENGINE, ["FROZEN_DT", "FROZEN_ETA", "FROZEN_GAMMA", "FROZEN_MU", "FROZEN_B_C"])


def settles_above_bc(R, steps=200_000):
    """True if an edge driven at constant R ends above B_c (engine update rule, ungated)."""
    eta, mu, gam, bc, dt = C["FROZEN_ETA"], C["FROZEN_MU"], C["FROZEN_GAMMA"], C["FROZEN_B_C"], C["FROZEN_DT"]
    R = np.asarray(R, dtype=float)
    B = np.zeros_like(R)
    for _ in range(steps):
        B = np.maximum(0.0, B + dt * ((eta + mu) * R - mu - gam * B))
    return B > bc


def threshold_claim_holds(claimed, probe=0.005):
    """A claimed threshold holds if edges just below it do not settle and edges just above do."""
    below, above = settles_above_bc([claimed - probe, claimed + probe])
    return (not below) and above


class SettleThreshold(unittest.TestCase):
    def test_00_control_true_threshold_accepted(self):
        eta, mu, gam, bc = C["FROZEN_ETA"], C["FROZEN_MU"], C["FROZEN_GAMMA"], C["FROZEN_B_C"]
        rstar = (mu + gam * bc) / (eta + mu)
        self.assertAlmostEqual(rstar, 0.4543, places=4)
        self.assertTrue(threshold_claim_holds(0.4543))

    def test_fabricated_threshold_0_40_rejected(self):
        self.assertFalse(threshold_claim_holds(0.40))

    def test_fabricated_threshold_0_50_rejected(self):
        self.assertFalse(threshold_claim_holds(0.50))


class SwappedExpectedActual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ns = load_functions(CMP, {"mask_mismatches", "cmp_arrays"}, {"MASKS", "TOL"})
        cls.cmp, cls.TOL = staticmethod(ns["cmp_arrays"]), ns["TOL"]

    def both(self, x, y):
        return self.cmp(np.array(x), np.array(y)), self.cmp(np.array(y), np.array(x))

    def test_inf_vs_finite_rejected_both_ways(self):
        a, b = self.both([1.0, np.inf], [1.0, 2.0])
        self.assertIsInstance(a, str); self.assertIsInstance(b, str)

    def test_nan_vs_finite_rejected_both_ways(self):
        a, b = self.both([np.nan], [0.0])
        self.assertEqual(a, b); self.assertIsInstance(a, str)

    def test_over_tolerance_rejected_both_ways(self):
        a, b = self.both([1.0], [1.0 + 1e-11])
        self.assertGreater(a, self.TOL); self.assertGreater(b, self.TOL)

    def test_shape_mismatch_rejected_both_ways(self):
        a, b = self.both([1.0, 2.0], [1.0])
        self.assertEqual((a, b), ("shape", "shape"))


if __name__ == "__main__":
    unittest.main()
