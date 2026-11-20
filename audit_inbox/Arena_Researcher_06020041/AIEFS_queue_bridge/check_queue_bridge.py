"""Limited float64 checks of queue indexing and conditional phase correspondence.
Requires the separately supplied unmodified engine file in ../AIEFS/.
No proof of derivatives or adaptive dynamics is claimed.
"""
import importlib.util
import pathlib
import sys
import numpy as np

p = pathlib.Path(__file__).resolve().parent.parent / 'AIEFS' / 'aief_experiment_engine_v1.py'
spec = importlib.util.spec_from_file_location('aiefs_engine', p)
e = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = e
spec.loader.exec_module(e)

def config():
    c = e.ModelConfig(N=2, dt=0.1, tau=0.1, omega=(0., 0.), a=1., q=1.5,
                      delta=.05, eta=.005, mu=0., gamma=.1, T_window=1.,
                      B_c=.12, B_init_scale=.0005)
    c.validate()
    return c

def state(theta, oldest, newest):
    return e.DynamicState(np.array(theta, dtype=float),
        np.array([[0., .05], [.05, 0.]]), np.ones((2,2), complex),
        [np.array(oldest, dtype=float), np.array(newest, dtype=float)])

def close_circle(a, b):
    return np.max(np.abs(np.exp(1j*np.asarray(a))-np.exp(1j*np.asarray(b))))

def test_consistent_case():
    c=config(); theta=np.array([2*np.pi-.02, .3]); old=np.array([.02, 6.1])
    s=state(theta, old, theta); s.validate(c)
    _,_,info=e.advance_state(s,c,np.random.default_rng(42),shuffle_driver=False)
    b=s.B[0,1]; assert s.B[1,0]==b and np.all(np.diag(s.B)==0)
    ref=theta+c.dt*(np.asarray(c.omega)+b*np.sin(old[::-1]-theta))
    assert close_circle(s.theta,ref)<1e-13
    assert close_circle(s.history[-1],s.theta)<1e-13
    assert close_circle(s.history[-2],theta)<1e-13
    print(f'consistent: pre_violation={info["pre_violation"]}, phase circle error={close_circle(s.theta,ref):.3g}, history error={close_circle(s.history[-2],theta):.3g}')

def test_inconsistent_but_valid():
    c=config(); theta=np.zeros(2); wrong=np.array([1.,0.]); s=state(theta,[0.,0.],wrong)
    s.validate(c)  # Validator does not compare theta with newest history.
    e.advance_state(s,c,np.random.default_rng(42),shuffle_driver=False)
    discrepancy=close_circle(s.history[-2],theta)
    assert discrepancy>0.9
    assert close_circle(s.history[-1],s.theta)<1e-13
    print(f'inconsistent-but-validated: old-current/shifted-history circular discrepancy={discrepancy:.9g}; newest repaired={close_circle(s.history[-1],s.theta):.3g}')

def test_representative_invariance():
    c=config(); theta=np.array([.2,.8]); old=np.array([.4,.1]); b=.05
    base=theta+c.dt*b*np.sin(old[::-1]-theta)
    theta2=theta+2*np.pi*np.array([1,-2]); old2=old+2*np.pi*np.array([-3,4])
    lifted=theta2+c.dt*b*np.sin(old2[::-1]-theta2)
    err=close_circle(base,lifted)
    assert err<1e-13
    print(f'phase lift representative discrepancy={err:.3g}')

if __name__ == '__main__':
    test_consistent_case(); test_inconsistent_but_valid(); test_representative_invariance()
    print('PASS: 3 finite checks; not a general proof')
