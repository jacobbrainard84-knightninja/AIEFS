"""Test a scalar reduction of actual AIEFS engine, using synthetic symmetric states.
Requires ../AIEFS/aief_experiment_engine_v1.py and numpy. No production artifacts edited.
"""
import importlib.util, pathlib, sys, unittest
import numpy as np

path = pathlib.Path(__file__).resolve().parent.parent / 'AIEFS/aief_experiment_engine_v1.py'
spec = importlib.util.spec_from_file_location('aiefs_engine', path)
e = importlib.util.module_from_spec(spec); sys.modules[spec.name] = e; spec.loader.exec_module(e)

def config(n, dt, d, eta, window, omega=1.3):
    c=e.ModelConfig(N=n, dt=dt, tau=d*dt, omega=(omega,)*n, a=1., q=1.5,
                    delta=.05, eta=eta, mu=.03, gamma=.015, T_window=window,
                    B_c=.12, B_init_scale=.0005)
    c.validate(); return c

def state(c, angle, b):
    m=np.ones((c.N,c.N))-np.eye(c.N)
    return e.DynamicState(np.full(c.N, angle), b*m,
                          np.zeros((c.N,c.N), dtype=complex),
                          [np.full(c.N, angle) for _ in range(c.delay_steps+1)])

class Scalar:
    def __init__(self,c,angle,b):
        self.p=c; self.theta=angle; self.b=b; self.c=0j
        self.hist=[angle]*(c.delay_steps+1)
    def step(self):
        p=self.p; old=self.hist[0]
        self.c=p.alpha*self.c+(1-p.alpha)*np.exp(1j*(self.theta-old-p.omega[0]*p.tau))
        r=abs(self.c)
        b=max(0.,self.b+p.dt*((p.eta+p.mu)*r-p.mu-p.gamma*self.b))
        row=(p.N-1)*b
        projected=p.a-p.q*row < p.delta
        if projected:
            s=min(1.,p.capacity/(row+p.scale_epsilon)); b=b*s
        self.b=b
        self.theta=np.mod(self.theta+p.dt*(p.omega[0]+(p.N-1)*b*np.sin(old-self.theta)),2*np.pi)
        self.hist.append(self.theta)
        if len(self.hist)>p.delay_steps+1: self.hist.pop(0)
        return r, projected

def run_case(c,b,steps):
    full=state(c,.42,b); s=Scalar(c,.42,b); rng=np.random.default_rng(123)
    eye=np.eye(c.N,dtype=bool); max_err=0.; projections=0; theta_increments=[]
    for t in range(steps):
        oldtheta=s.theta
        R, driver, info=e.advance_state(full,c,rng,shuffle_driver=False)
        r,projected=s.step()
        projections+=int(projected)
        assert bool(info['pre_violation']) == projected
        expected=np.full((c.N,c.N),s.b); np.fill_diagonal(expected,0.)
        errors=[np.max(np.abs(full.theta-s.theta)), np.max(np.abs(full.B-expected)),
                np.max(np.abs(full.coherence_acc-s.c)),np.max(np.abs(R[~eye]-r)),
                np.max(np.abs(R[eye])),np.max(np.abs(driver-R)),
                np.max(np.abs(np.asarray(full.history)-np.asarray(s.hist)[:,None]))]
        max_err=max(max_err,*errors)
        if max(errors)>2e-12: raise AssertionError((t,errors))
        theta_increments.append((s.theta-oldtheta)%(2*np.pi))
    return max_err,projections,theta_increments

class TestScalarReduction(unittest.TestCase):
    def test_d50_closed_loop(self):
        c=config(12,.01,50,.04,17.5)
        err,p,inc=run_case(c,.01,300)
        self.assertEqual(p,0)
        self.assertGreater(max(inc)-min(inc),1e-6)
        print(f' D50: 300 steps, max error={err:.3g}, projections={p}, increment range={max(inc)-min(inc):.6g}')
    def test_projection_branch(self):
        c=config(4,.1,3,10.,.1)
        err,p,inc=run_case(c,.1,80)
        self.assertGreater(p,0)
        print(f' projection: 80 steps, max error={err:.3g}, projected steps={p}')
    def test_clip_branch(self):
        from dataclasses import replace
        c=replace(config(4,.1,3,0.,1.), mu=1.)
        c.validate()
        full=state(c,.42,.001); s=Scalar(c,.42,.001)
        R, driver, info=e.advance_state(full,c,np.random.default_rng(123))
        r, projected=s.step()
        self.assertEqual(s.b,0.)
        self.assertTrue(np.all(full.B==0.))
        self.assertFalse(projected)
        err,p,inc=run_case(c,.001,40)
        print(f' clip: 40 steps, max error={err:.3g}, projected steps={p}')
    def test_nonuniform_frequency_breaks_synchrony(self):
        c=config(3,.1,2,.04,1.)
        from dataclasses import replace
        c=replace(c,omega=(1.3,1.4,1.3)); c.validate()
        f=state(c,.42,.01)
        e.advance_state(f,c,np.random.default_rng(123))
        self.assertGreater(np.ptp(f.theta),.009)
        print(f' heterogeneous omega: phase spread after one step={np.ptp(f.theta):.6g}')

if __name__=='__main__': unittest.main(verbosity=2)
