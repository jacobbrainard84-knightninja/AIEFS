import numpy as np
from aief_experiment_engine_v1 import ModelConfig, DynamicState, advance_state

cfg = ModelConfig(N=3, dt=1., tau=1., omega=(1.,1.,1.), a=1., q=1.,
                  delta=0., eta=1., mu=0., gamma=0., T_window=10.,
                  B_c=0., B_init_scale=0., scale_epsilon=.25)
cfg.validate()
# All input phasors equal one: current theta 0, oldest history -1, omega*tau 1.
target = np.array([[0.,1.,.5],[1.,0.,.25],[.5,.25,0.]])
C = (target - (1. - cfg.alpha)) / cfg.alpha
s = DynamicState(theta=np.zeros(3), B=np.zeros((3,3)), coherence_acc=C,
                 history=[-np.ones(3),np.zeros(3)])
s.validate(cfg)
r, driver, info = advance_state(s, cfg, np.random.default_rng(0))
s.validate(cfg)
expected = np.array([[0.,4/7,2/7],[4/7,0.,1/6],[2/7,1/6,0.]])
assert np.allclose(r, target, atol=1e-14, rtol=0.)
assert np.allclose(s.B, expected, atol=1e-14, rtol=0.)
assert info['projection_active']
print('config.validate: PASS; input and output state.validate: PASS')
print('R=', r.tolist())
print('projection_active=', info['projection_active'])
print('projected B=', s.B.tolist())
print('max absolute difference vs exact-rational projection=', np.max(np.abs(s.B-expected)))
print('FLOAT ENGINE PROBE: PASS (constructed state; no reachability claim)')
