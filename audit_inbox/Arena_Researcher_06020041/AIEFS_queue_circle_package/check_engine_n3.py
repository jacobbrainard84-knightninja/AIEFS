"""N=3 engine checks; engine file expected at ../AIEFS/; NumPy required."""
import importlib.util, pathlib, sys
import numpy as np
p=pathlib.Path(__file__).resolve().parent.parent/'AIEFS/aief_experiment_engine_v1.py'
s=importlib.util.spec_from_file_location('engine_for_queue',p)
e=importlib.util.module_from_spec(s); sys.modules[s.name]=e; s.loader.exec_module(e)

def circ_error(x,y): return float(np.max(np.abs(np.angle(np.exp(1j*(x-y))))))

def run(label,B):
    c=e.ModelConfig(N=3,dt=.1,tau=.1,omega=(0.,0.,0.),a=1.,q=1.5,delta=.05,
        eta=0.,mu=0.,gamma=0.,T_window=1.,B_c=.12,B_init_scale=.0005)
    c.validate()
    theta=np.array([.1,.7,1.2]); old=np.array([1.,.2,1.8])
    s=e.DynamicState(theta,B,np.zeros((3,3),complex),[old,theta]);s.validate(c)
    e.advance_state(s,c,np.random.default_rng(1),shuffle_driver=False)
    b=np.sum(B)/6
    true=theta+c.dt*np.sum(B*np.sin(old[None,:]-theta[:,None]),axis=1)
    uniform=theta+c.dt*b*np.sum((1-np.eye(3))*np.sin(old[None,:]-theta[:,None]),axis=1)
    actual_error=circ_error(s.theta,true); ref_error=circ_error(s.theta,uniform)
    assert actual_error<1e-13 and circ_error(s.history[0],theta)<1e-13
    print(f'{label}: offdiag mean={b:.12g} actual-vs-weighted={actual_error:.12g} actual-vs-uniform={ref_error:.12g} radians')
    return ref_error

uniform=.1*(np.ones((3,3))-np.eye(3))
hetero=np.array([[0.,.05,.10],[.05,0.,.20],[.10,.20,0.]])
u=run('uniform',uniform);h=run('nonuniform',hetero)
assert u<1e-13 and h>1e-4
print('PASS: N=3 uniform match; nonuniform matrix differs from same-mean scalar reference')
