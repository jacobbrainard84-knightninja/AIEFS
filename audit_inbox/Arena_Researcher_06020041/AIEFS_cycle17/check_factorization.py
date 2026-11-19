#!/usr/bin/env python3
"""Exact finite checks of the phase-block characteristic factorization; not a proof."""
import sympy as s
z = s.symbols('z')

def phase_matrix(n, d, h, include_self=False):
    # Coordinates ordered (history index, node). Accumulation matters when d=0.
    M = s.zeros(n * (d + 1))
    for i in range(n):
        M[i, i] += 1 - (n - 1) * h
        for j in range(n):
            if i != j or include_self:
                M[i, d*n+j] += h
    for k in range(1, d+1):
        for i in range(n):
            M[k*n+i, (k-1)*n+i] = 1
    return M

def factors(n, d, h):
    a = 1 - (n-1)*h
    common = z**(d+1) - a*z**d - (n-1)*h
    transverse = z**(d+1) - a*z**d + h
    return common, transverse

count=0
for n in range(2, 6):
    for d in range(4):
        h = s.Rational(1, 2*n)
        M = phase_matrix(n,d,h)
        pc, pt = factors(n,d,h)
        actual = M.charpoly(z).as_expr()
        assert s.Poly(actual-pc*pt**(n-1),z).is_zero
        assert pc.subs(z,1)==0 and s.diff(pc,z).subs(z,1)==1+d*(n-1)*h
        assert pt.subs(z,1)==n*h != 0
        assert len((M-s.eye(M.rows)).nullspace())==1
        count += 1
# This deliberately wrong no-self implementation must not pass the factorization.
n,d,h=3,2,s.Rational(1,6)
pc,pt=factors(n,d,h)
assert not s.Poly(phase_matrix(n,d,h,True).charpoly(z).as_expr()-pc*pt**(n-1),z).is_zero
# Strict mh<1 matters: at n=2, d=1, h=1, transverse roots are +/- i.
pc,pt=factors(2,1,s.Integer(1))
assert s.expand(pt)==z*z+1
assert s.expand(pc)==z*z-1
print(f'PASS: {count} exact matrix characteristic polynomials, including d=0; neutral multiplicity and nullity')
print('PASS: diagonal-inclusion negative control rejected')
print('PASS: n=2, d=1, h=1 boundary has transverse roots ±i')
