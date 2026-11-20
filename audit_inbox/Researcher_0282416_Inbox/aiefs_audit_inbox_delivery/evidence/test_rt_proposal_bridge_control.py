#!/usr/bin/env python3
"""Red-team negative control test: verify that the synthetic proposal bridge test
correctly detects when the self-test branch does not match the actual min(s_i, s_j) operator.

This directly settles Researcher 040282 Finding 3 / Item 0 (Standing Priority: built-in false results).
"""

import sys
import unittest
import numpy as np

def run_actual_engine_gate(x25, x29, x59, capacity, epsilon):
    """The true physical/numerical gate operator: min(s_i, s_j) * x_e."""
    q2 = x25 + x29
    q7 = x25 + x59
    q11 = x29 + x59
    s2 = min(1.0, capacity / (q2 + epsilon))
    s7 = min(1.0, capacity / (q7 + epsilon))
    s11 = min(1.0, capacity / (q11 + epsilon))

    actual_projected = {
        25: min(s2, s7) * x25,
        29: min(s2, s11) * x29,
        59: min(s7, s11) * x59,
    }
    return actual_projected, s2, s7, s11

def run_hardcoded_bridge_test(x25, x29, x59, capacity, epsilon):
    """The hardcoded winner map assumed in AIEF_1_4_proposal_equalization_bridge_analysis.py."""
    q2 = x25 + x29
    q7 = x25 + x59
    s2 = capacity / (q2 + epsilon)
    s7 = capacity / (q7 + epsilon)
    hardcoded_projected = {
        25: s7 * x25,  # <-- Assumes row 7 wins for edge 25=(2,7)
        29: s2 * x29,
        59: s7 * x59,
    }
    return hardcoded_projected

class TestProposalBridgeNegativeControl(unittest.TestCase):
    def test_residual_witness(self):
        capacity = 0.6333333333333333
        epsilon = 1e-12
        x25, x29, x59 = 0.41, 0.31, 0.27

        actual, s2, s7, s11 = run_actual_engine_gate(x25, x29, x59, capacity, epsilon)
        hardcoded = run_hardcoded_bridge_test(x25, x29, x59, capacity, epsilon)

        # For x25=0.41, x29=0.31, x59=0.27:
        # q2 = 0.72 > q7 = 0.68 => s2 < s7
        # Therefore min(s2, s7) is s2, but hardcoded self-test uses s7!
        residual = abs(actual[25] - hardcoded[25])
        
        # Verify the exact 0.0212 residual reported by Researcher 040282
        self.assertAlmostEqual(residual, 0.0212145969, places=6)
        print(f"PASS (Negative Control Confirmed): True operator vs self-test residual is {residual:.4f}")

    def test_branch_condition_discrepancy(self):
        """Verify the exact mathematical condition under which row 7 actually wins for edge 25."""
        capacity = 0.6333333333333333
        epsilon = 1e-12
        # For row 7 to win (s7 <= s2), we require q7 >= q2:
        # x25 + x59 >= x25 + x29  <=>  x59 >= x29.
        # But the self-test sets x29=0.31 and x59=0.27 (so x59 < x29)!
        x25, x29, x59 = 0.41, 0.31, 0.27
        self.assertTrue(x59 < x29, "Self-test chooses parameters where x59 < x29")
        
        # Consistent parameters where row 7 actually wins edge 25:
        x25_valid, x29_valid, x59_valid = 0.41, 0.27, 0.31
        actual_valid, _, _, _ = run_actual_engine_gate(x25_valid, x29_valid, x59_valid, capacity, epsilon)
        hardcoded_valid = run_hardcoded_bridge_test(x25_valid, x29_valid, x59_valid, capacity, epsilon)
        self.assertAlmostEqual(actual_valid[25], hardcoded_valid[25], places=12)

if __name__ == "__main__":
    unittest.main()
