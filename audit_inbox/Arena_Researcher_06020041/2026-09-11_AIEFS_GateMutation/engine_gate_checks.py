"""Exercise the real engine or a supplied scratch mutant against fixed outputs."""
import importlib.util
import sys
import numpy as np

spec = importlib.util.spec_from_file_location('aiefs_gate_engine_under_test', sys.argv[1])
engine = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)

cfg = engine.ModelConfig(N=3, dt=1., tau=1., omega=(1., 1., 1.),
    a=1., q=1., delta=0., eta=1., mu=0., gamma=0., T_window=10.,
    B_c=0., B_init_scale=0., scale_epsilon=.25)
cfg.validate()
pre = np.array([[0., 1., .5], [1., 0., .25], [.5, .25, 0.]])
expected = np.array([[0., 4/7, 2/7], [4/7, 0., 1/6], [2/7, 1/6, 0.]])


def run_case(target):
    # The zero frequency-adjusted phase difference gives every input phasor +1.
    old_c = (target - (1. - cfg.alpha)) / cfg.alpha
    state = engine.DynamicState(theta=np.zeros(3), B=np.zeros((3, 3)),
        coherence_acc=old_c, history=[-np.ones(3), np.zeros(3)])
    state.validate(cfg)
    r, _, info = engine.advance_state(state, cfg, np.random.default_rng(0))
    state.validate(cfg)
    assert np.allclose(r, target, rtol=0., atol=1e-14)
    return state.B, info


actual, info = run_case(pre)
negative, info_negative = run_case(pre / 2)
negative_ok = (not info_negative['pre_violation'] and not info_negative['projection_active']
               and np.allclose(negative, pre / 2, rtol=0., atol=1e-14))
active_ok = (info['pre_violation'] and info['projection_active']
             and np.allclose(actual, expected, rtol=0., atol=1e-14))
print('active branch:', info['pre_violation'],
      'projection active:', info['projection_active'])
print('actual edge01:', repr(actual[0, 1]), 'expected:', repr(expected[0, 1]))
print('max absolute full-matrix error:', repr(float(np.max(np.abs(actual - expected)))))
print('active full-matrix oracle:', 'PASS' if active_ok else 'FAIL')
print('inactive branch control:', 'PASS' if negative_ok else 'FAIL')
raise SystemExit(0 if active_ok and negative_ok else 1)
