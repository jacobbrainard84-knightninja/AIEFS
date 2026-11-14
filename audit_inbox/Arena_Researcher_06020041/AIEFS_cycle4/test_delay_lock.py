"""Exact quarter-turn model of P5 indexing; independent executable check, not Lean/Python equivalence."""
import unittest
from fractions import Fraction as F

# Gaussian rationals are pairs. Angles are integer multiples of pi/2.
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def scale(q, a): return (q * a[0], q * a[1])
def mul(a, b): return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])
def unit(k): return ((1,0),(0,1),(-1,0),(0,-1))[k % 4]

def phase(u, node, n):
    return sum(u(t, node) for t in range(n)) % 4

def z(d, u, n, i, j):
    # x0=0, omega=0, tau=0, oldest history = phase(max(0,n-d)).
    return unit(phase(u, i, n) - phase(u, j, max(0, n-d)))

def trace(alpha, d, u, i, j, c0, length):
    c = c0
    result = [c]
    for n in range(length):
        c = add(scale(alpha, c), scale(1-alpha, z(d,u,n,i,j)))
        result.append(c)
    return result

class Tests(unittest.TestCase):
    def test_sharp_boundary_family(self):
        # At exactly N+d-1 the last pre-lock update arrives at source j.
        for N in range(1, 9):
            for d in range(1, 9):
                u = lambda n, node: 2 if n == N-1 and node == 1 else 0
                n = N+d-1
                self.assertTrue(all(u(t,node) == 0 for t in range(N,N+d+4) for node in (0,1)))
                self.assertEqual(z(d,u,n,0,1), (1,0))
                self.assertEqual(z(d,u,n+1,0,1), (-1,0))
                self.assertTrue(all(z(d,u,t,0,1) == (-1,0) for t in range(n+1,n+6)))
    def test_n_zero_special_case(self):
        for d in range(6):
            u = lambda n,node: 0
            self.assertTrue(all(z(d,u,n,0,1) == (1,0) for n in range(10)))
    def test_geometric_error_after_lock(self):
        for N in range(1,5):
            for d in range(1,5):
                u = lambda n,node: 1 if n == N-1 and node == 1 else 0
                alpha = F(3,4); n0 = N+d
                c = trace(alpha,d,u,0,1,(F(1,3),F(-1,5)),n0+9)
                target = z(d,u,n0,0,1)
                for k in range(10):
                    self.assertEqual(sub(c[n0+k],target), scale(alpha**k,sub(c[n0],target)))

if __name__ == '__main__': unittest.main(verbosity=2)
