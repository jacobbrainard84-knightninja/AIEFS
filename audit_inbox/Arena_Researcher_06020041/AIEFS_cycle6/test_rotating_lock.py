"""Exact quarter-turn checks of independently transcribed P5 delay/EMA indices."""
import importlib.util
from fractions import Fraction as F
from pathlib import Path
import unittest
p = Path(__file__).resolve().parent.parent / 'AIEFS_cycle4' / 'test_delay_lock.py'
spec = importlib.util.spec_from_file_location('prior_exact_model', p)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class TestRotatingLock(unittest.TestCase):
    def test_nonzero_common_rotation(self):
        for d in range(1,5):
            for N in range(1,5):
                # Node-specific phase history; both rotate by pi/2 from N.
                def u(n,i):
                    if n >= N: return 1
                    return (n+i+1) % 4
                n0=N+d
                for i,j in ((0,1),(1,0)):
                    z0=m.z(d,u,n0,i,j)
                    self.assertTrue(all(m.z(d,u,n,i,j)==z0 for n in range(n0,n0+10)))
                    c=m.trace(F(2,3),d,u,i,j,(F(0),F(0)),n0+8)
                    for k in range(9):
                        self.assertEqual(m.sub(c[n0+k],z0),m.scale(F(2,3)**k,m.sub(c[n0],z0)))
    def test_reported_not_monotone_even_after_freezing(self):
        # Symmetric nodes: u_0=u_1=pi, then both freeze; d=1, alpha=1/2.
        u=lambda n,i: 2 if n<2 else 0
        c=m.trace(F(1,2),1,u,0,1,(F(0),F(0)),5)
        self.assertEqual(c[3], (F(-5,8),F(0)))
        self.assertEqual(c[4], (F(3,16),F(0)))
        self.assertEqual(m.z(1,u,3,0,1),m.z(1,u,4,0,1))
        # Both directions coincide, hence reported off-diagonal is |C|.
        self.assertEqual(c,m.trace(F(1,2),1,u,1,0,(F(0),F(0)),5))
        self.assertGreater(abs(c[3][0]),abs(c[4][0]))

if __name__ == '__main__': unittest.main(verbosity=2)
