"""Check a proposed neutral-phase functional against actual-engine finite differences.
Depends on Cycle 10 Model, Cycle 8 helper and the pinned engine; see note.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'AIEFS_cycle10'))
from full_network_check import Model

def functional(M):
    n,d,c=M.n,M.d,M.c
    alpha=c.alpha; rho=1-c.dt*c.gamma
    h=c.dt*M.b*np.cos(M.O*c.tau); q=(n-1)*h
    D=1+d*q
    A=c.dt*np.sin(M.O*c.tau)/D
    k=c.dt*(c.eta+c.mu)
    row=np.zeros(M.size)
    row[:n]=1/(n*D)
    row[n:M.p]=q/(n*D)
    for i in range(n):
        for j in range(n):
            if i!=j:
                row[M.p+i*n+j]=-A*k*alpha/((1-rho)*(1-alpha)*n)
    row[-len(M.edges):]=-A*rho/(1-rho)*2/n
    return row

def run():
    rng=np.random.default_rng(1826)
    for d in (3,50):
        M=Model(3,d,False); left=functional(M)
        J=M.analytic_matrix(); F=M.finite_matrix()
        neutral=M.pack(np.ones((d+1,M.n)),np.zeros((M.n,M.n)),np.zeros((M.n,M.n)),np.zeros((M.n,M.n)))
        err_exact=np.max(np.abs(left@J-left)); err_finite=np.max(np.abs(left@F-left))
        assert abs(left@neutral-1)<1e-12
        assert err_exact<1e-11 and err_finite<2e-6
        # Directional linearization of actual full engine, with all state families perturbed.
        direction=rng.normal(size=M.size)
        eps=1e-6
        delta=(M.full_step(eps*direction)-M.full_step(-eps*direction))/(2*eps)
        directional=abs(left@delta-left@direction)
        assert directional<3e-6
        # Ignoring coupled weight/real-EMA channels must not yield an invariant functional.
        incomplete=left.copy(); incomplete[M.p:]=0
        negative=np.max(abs(incomplete@J-incomplete))
        assert negative>1e-6
        print(f'd={d}: analytic residual {err_exact:.3g}; engine finite-difference residual {err_finite:.3g}; mixed direction {directional:.3g}; omit-coupling residual {negative:.3g}')
    print('PASS: normalization, two full-engine finite-difference cases and coupling negative controls')
if __name__=='__main__': run()
