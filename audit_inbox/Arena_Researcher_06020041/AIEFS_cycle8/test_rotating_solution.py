"""Construct synchronized rotating solutions and compare against the actual engine."""
import math, pathlib, sys, unittest
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent/'AIEFS_cycle7'))
from symmetric_reduction_test import e, config
from dataclasses import replace


def fixed_weight(c, projected):
    m=c.N-1; C=c.capacity
    if not projected:
        b=c.eta/c.gamma
        assert m*b<C
        return b
    # Solve the branch equation b = C*beta/(m*beta+epsilon), beta=b+dt*(eta-gamma*b).
    # Selected test parameters have beta>0 and 0<dt*gamma<1.
    def beta(b): return b+c.dt*(c.eta-c.gamma*b)
    def f(b):
        x=beta(b)
        return C*x/(m*x+c.scale_epsilon)-b
    lo=0.; hi=C/m
    assert f(lo)>0 and f(hi)<0
    for _ in range(100):
        mid=(lo+hi)/2
        if f(mid)>0: lo=mid
        else: hi=mid
    b=(lo+hi)/2
    assert m*beta(b)>C
    assert abs(f(b))<1e-14
    return b


def locked_frequency(c,b):
    m=c.N-1; omega=c.omega[0]; K=m*b
    assert K*c.tau<1
    def f(x): return x-omega+K*math.sin(x*c.tau)
    lo=omega-K-1.; hi=omega+K+1.
    assert f(lo)<0 and f(hi)>0
    for _ in range(100):
        mid=(lo+hi)/2
        if f(mid)<0: lo=mid
        else: hi=mid
    result=(lo+hi)/2
    assert abs(f(result))<1e-14
    return result


def initial(c,b,O):
    delta=c.dt*O; theta=.42
    hist=[np.full(c.N,(theta+(t-c.delay_steps)*delta)%(2*np.pi))
          for t in range(c.delay_steps+1)]
    z=np.exp(1j*(c.delay_steps*delta-c.omega[0]*c.tau))
    weights=b*(np.ones((c.N,c.N))-np.eye(c.N))
    return e.DynamicState(np.full(c.N,theta),weights,np.full((c.N,c.N),z),hist),z


def run(projected,steps):
    c=config(12,.01,50,.04 if projected else .0005,17.5,1.4283333333333332)
    b=fixed_weight(c,projected); O=locked_frequency(c,b)
    st,z=initial(c,b,O); rng=np.random.default_rng(1)
    mask=~np.eye(c.N,dtype=bool); max_theta=max_b=max_c=max_r=0.; proj=0
    for n in range(steps):
        r,driver,info=e.advance_state(st,c,rng,shuffle_driver=False)
        proj+=int(info['pre_violation'])
        expected=(.42+(n+1)*c.dt*O)%(2*np.pi)
        max_theta=max(max_theta,np.max(np.abs(np.exp(1j*st.theta)-np.exp(1j*expected))))
        max_b=max(max_b,np.max(np.abs(st.B[mask]-b)))
        max_c=max(max_c,np.max(np.abs(st.coherence_acc-z)))
        max_r=max(max_r,np.max(np.abs(r[mask]-1)))
        assert not np.any(r[~mask])
    print(f'projected={projected} b={b:.15g} Omega={O:.15g} Ktau={(c.N-1)*b*c.tau:.8g} projection_steps={proj} errors theta={max_theta:.3g}, B={max_b:.3g}, C={max_c:.3g}, R={max_r:.3g}')
    return max_theta,max_b,max_c,max_r,proj

class TestRotatingSolutions(unittest.TestCase):
    def test_interior(self):
        *errs,p=run(False,1000); self.assertEqual(p,0);self.assertLess(max(errs),2e-11)
    def test_capacity_projected(self):
        *errs,p=run(True,1000); self.assertEqual(p,1000);self.assertLess(max(errs),2e-11)
    def test_wrong_frequency_is_not_solution(self):
        c=config(12,.01,50,.04,17.5,1.4283333333333332)
        b=fixed_weight(c,True); O=locked_frequency(c,b)
        st,z=initial(c,b,c.omega[0]); before=st.theta[0]
        e.advance_state(st,c,np.random.default_rng(2))
        actual=(st.theta[0]-before)%(2*np.pi)
        self.assertGreater(abs(actual-c.dt*c.omega[0]),1e-4)
        print(f'negative control: natural-frequency guess residual {abs(actual-c.dt*c.omega[0]):.6g}; true Omega={O:.9g}')

if __name__=='__main__': unittest.main(verbosity=2)
