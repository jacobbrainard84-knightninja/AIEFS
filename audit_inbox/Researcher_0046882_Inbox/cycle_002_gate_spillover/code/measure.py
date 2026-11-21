"""Researcher 0046882 (Arena.ai), cycle 002, DIRECTION-1.
UNVERIFIED by project seats. Date/time, main SHA and both engine hashes:
../METADATA.json and ../HEADER.txt (shared header for generated/binary evidence).
Run from the cycle directory: python code/measure.py
Independent measurement/control code; never imports deposited adjudication scripts.
"""
from pathlib import Path
from fractions import Fraction as F
import dataclasses
import hashlib
import importlib.util
import json
import platform
import struct
import sys
import time
import traceback
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'METADATA.json').read_text())
THRESHOLD = META['event_threshold']


def dump(path, obj):
    (ROOT / path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def hfile(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_finite(*arrays):
    if any(not np.isfinite(a).all() for a in arrays):
        raise ValueError('Nonfinite measurement: invalid run')


def metrics(pre, scales, post, cap):
    check_finite(pre, scales, post, np.array(cap))
    binding = scales < 1
    bystander = (scales == 1) & (pre > 0)
    d = (cap - post[binding]) / cap
    loss = (pre[bystander] - post[bystander]) / pre[bystander]
    b = (cap - scales[binding] * pre[binding]) / cap
    extra = (scales[binding] * pre[binding] - post[binding]) / cap
    return binding, bystander, d, loss, b, extra


def fractions_gate(X, cap, eps):
    n = len(X)
    rows = [sum(row, F(0)) for row in X]
    on = any(q > cap for q in rows)
    scales = [min(F(1), cap / (q + eps)) if q + eps else F(1) for q in rows]
    out = [[X[i][j] * min(scales[i], scales[j]) if on else X[i][j]
            for j in range(n)] for i in range(n)]
    post = [sum(row, F(0)) for row in out]
    d = [(cap - post[i]) / cap if on and scales[i] < 1 else None for i in range(n)]
    l = [(rows[i] - post[i]) / rows[i] if on and scales[i] == 1 and rows[i] > 0 else None for i in range(n)]
    extra = [(scales[i] * rows[i] - post[i]) / cap if on and scales[i] < 1 else None for i in range(n)]
    return dict(on=on, rows=rows, scales=scales, post=post, d=d, l=l, extra=extra)


def stringify(obj):
    if isinstance(obj, F): return str(obj)
    if isinstance(obj, dict): return {k: stringify(v) for k, v in obj.items()}
    if isinstance(obj, list): return [stringify(v) for v in obj]
    return obj


def controls():
    cap = F(19, 30)
    W1 = [[F(0), F(1, 2), F(1, 4)], [F(1, 2), F(0), F(1, 10)], [F(1, 4), F(1, 10), F(0)]]
    W2 = [[F(0), F(1, 2), F(1, 2)], [F(1, 2), F(0), F(1, 5)], [F(1, 2), F(1, 5), F(0)]]
    expected = [[cap, F(47, 90), F(14, 45)], [cap, F(209, 420), F(209, 420)]]
    cases = {}
    mutation_rejected = []
    for name, X, want in zip(['W1', 'W2'], [W1, W2], expected):
        r = fractions_gate(X, cap, F(0))
        assert r['post'] == want
        # A wrong row-only operator cannot pass these exact witnesses.
        wrong = [r['rows'][i] * r['scales'][i] for i in range(3)]
        assert wrong != want
        mutation_rejected.append(name)
        # The float summary masks/metrics also detect the exact positive controls.
        met = metrics(np.array([float(v) for v in r['rows']]),
                      np.array([float(v) for v in r['scales']]),
                      np.array([float(v) for v in r['post']]), float(cap))
        if name == 'W1':
            assert all(v > F(1, 10**9) for v in r['l'] if v is not None)
            assert np.count_nonzero(met[3] > THRESHOLD) == 2
        else:
            assert r['d'][1] > F(1, 10**9) and r['d'][2] > F(1, 10**9)
            assert np.count_nonzero(met[2] > THRESHOLD) == 2
        cases[name] = r
    eq = [[F(0) if i == j else F(2, 5) for j in range(4)] for i in range(4)]
    z = fractions_gate(eq, cap, F(0))
    assert z['d'] == [F(0)] * 4 and z['extra'] == [F(0)] * 4
    cases['equal_load_epsilon_zero'] = z
    eps = F(1, 10**12)
    z = fractions_gate(eq, cap, eps)
    expected_depth = eps / (F(6, 5) + eps)
    assert z['d'] == [expected_depth] * 4
    assert F(0) < expected_depth < F(1, 10**9)
    assert z['extra'] == [F(0)] * 4
    cases['equal_load_production_epsilon'] = z
    small = [[F(0) if i == j else F(1, 10) for j in range(4)] for i in range(4)]
    z = fractions_gate(small, cap, eps)
    assert not z['on'] and z['rows'] == z['post']
    cases['feasible_no_gate'] = z
    assert not bool(np.float64(THRESHOLD) > THRESHOLD)
    assert bool(np.nextafter(THRESHOLD, np.inf) > THRESHOLD)
    # zero-load bystanders are excluded from division, not turned into NaNs.
    met = metrics(np.array([0.]), np.array([1.]), np.array([0.]), float(cap))
    assert len(met[3]) == 0
    for bad in [np.nan, np.inf, -np.inf]:
        try:
            metrics(np.array([bad]), np.array([1.]), np.array([0.]), float(cap))
        except ValueError:
            pass
        else:
            raise AssertionError('nonfinite negative control accepted')
    dump('evidence/controls.json', {'metadata': META, 'cases': stringify(cases),
         'row_only_mutants_rejected': mutation_rejected, 'threshold_and_nonfinite_tests': 'PASS',
         'positive_controls': 'PASS', 'negative_controls': 'PASS',
         'epsilon_correction': 'equal binding loads have strictly positive d for eps>0; extra=0 exactly'})
    print('CONTROLS PASS: W1/W2 exact; zero/positive epsilon controls; row-only mutants rejected', flush=True)


def load_engine(name, filename, expected):
    path = ROOT / 'code' / filename
    assert hfile(path) == expected
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def configure(module, manifest):
    model = manifest['model']
    kwargs = {f.name: model[f.name] for f in dataclasses.fields(module.ModelConfig) if f.name in model}
    kwargs['omega'] = tuple(kwargs['omega'])
    config = module.ModelConfig(**kwargs)
    assert config.scale_epsilon == META['epsilon']
    assert config.N == 12 and config.dt == .01
    branches = tuple(manifest['protocol']['branches'])
    protocol = module.ProtocolConfig(T_sim=model['T_sim'], burn_end_time=160.,
              split_time=480., future_duration=320., diagnostic_stride=manifest['protocol']['diagnostic_stride'],
              branches=branches)
    config.validate(); protocol.validate(config)
    assert protocol.n_steps(config) == 80000 and protocol.hist_end(config) == 48000
    return config, protocol, branches


def update_hash(h, value):
    if isinstance(value, np.ndarray):
        h.update(b'A' + value.dtype.str.encode() + repr(value.shape).encode() + value.tobytes(order='C'))
    elif isinstance(value, dict):
        h.update(b'D')
        for k in sorted(value):
            update_hash(h, str(k)); update_hash(h, value[k])
    elif isinstance(value, (list, tuple)):
        h.update(b'L' + str(len(value)).encode())
        for v in value: update_hash(h, v)
    elif isinstance(value, (float, np.floating)):
        h.update(b'F' + struct.pack('>d', float(value)))
    else:
        h.update(type(value).__name__.encode() + repr(value).encode())


def state_dict(state):
    return {k: np.asarray(v).copy() for k, v in vars(state).items()}


class Observer:
    def __init__(self, n_steps, N):
        self.k = 0
        self.pre = np.empty((n_steps, N), dtype=np.float64)
        self.post = np.empty_like(self.pre)
        self.scale = np.empty_like(self.pre)
        self.gated = np.zeros(n_steps, dtype=bool)
        self.active = np.zeros(n_steps, dtype=bool)
        self.cap = None

    def __call__(self, gated, active, pre, scale, projected, cap):
        post = np.sum(projected, axis=1)
        check_finite(pre, scale, post)
        if self.cap is None: self.cap = cap
        assert self.cap == cap
        k = self.k
        self.pre[k] = pre; self.post[k] = post; self.scale[k] = scale
        self.gated[k] = gated; self.active[k] = active
        self.k += 1

    def save(self, seed):
        assert self.k == len(self.gated)
        np.savez_compressed(ROOT / 'raw' / f'seed_{seed}.npz',
            row_sum_pre=self.pre, r_post=self.post, scale=self.scale,
            pre_violation=self.gated, projection_active=self.active, capacity=np.array(self.cap),
            metadata_json=np.array(json.dumps(META)))


def simulate(module, seed, manifest, observer=None):
    config, protocol, branches = configure(module, manifest)
    stream = hashlib.sha256()
    count = 0
    last_state = None
    original_advance = module.advance_state
    module._GATE_OBSERVER = observer
    def tracked(state, *args, **kwargs):
        nonlocal count, last_state
        result = original_advance(state, *args, **kwargs)
        update_hash(stream, state_dict(state))
        update_hash(stream, result)
        last_state = state
        count += 1
        return result
    module.advance_state = tracked
    try:
        split, prefix = module.simulate_prefix(seed, config, protocol)
        split_snapshot = state_dict(split)
        rng = module.make_branch_rngs(seed, branches)['continue']
        future = module.simulate_future(split, prefix, 'continue', config, protocol, rng)
        assert count == 80000
        result = dict(prefix=prefix, future=future, split_state=split_snapshot,
                      final_state=state_dict(last_state), final_rng=rng.bit_generator.state)
        return result, {'post_step_state_and_return_stream_sha256': stream.hexdigest(), 'steps': count}
    finally:
        module.advance_state = original_advance
        module._GATE_OBSERVER = None


def flatten(value, prefix='root'):
    if isinstance(value, dict):
        out = {}
        for k in sorted(value): out.update(flatten(value[k], prefix + '/' + str(k)))
        return out
    if isinstance(value, (list, tuple)):
        out = {}
        for i,v in enumerate(value): out.update(flatten(v, prefix + '/' + str(i)))
        return out
    if isinstance(value, np.ndarray): return {prefix: value}
    if isinstance(value, (bool, int, float, np.number, str)):
        # Huge integer RNG state must remain exact, not object arrays needing pickle.
        if isinstance(value, int) and not -(2**63) <= value < 2**63:
            return {prefix: np.array(str(value))}
        return {prefix: np.asarray(value)}
    raise TypeError(type(value))


def exact_compare(a, b):
    a = flatten(a); b = flatten(b)
    assert a.keys() == b.keys()
    bad = [k for k in a if a[k].dtype != b[k].dtype or a[k].shape != b[k].shape
           or a[k].tobytes() != b[k].tobytes()]
    # A one-bit alteration must be rejected by this exact comparator.
    x = np.array([1.0]); y = x.copy(); y.view(np.uint64)[0] ^= np.uint64(1)
    assert x.tobytes() != y.tobytes()
    return a, b, bad


def distribution(a):
    if a.size == 0: return {'n': 0, 'min': None, 'median': None, 'p95': None, 'max': None}
    check_finite(a)
    return {'n': int(a.size), 'min': float(np.min(a)), 'median': float(np.quantile(a,.5,method='linear')),
            'p95': float(np.quantile(a,.95,method='linear')), 'max': float(np.max(a))}


def ratio(n, d): return n/d if d else None


def summarize(pre, scale, post, gated, active, cap):
    gp, gs, go = pre[gated], scale[gated], post[gated]
    bm, ym, d, l, base, extra = metrics(gp, gs, go, cap)
    bd = (cap-go)/cap
    yl = np.zeros_like(gp); np.divide(gp-go, gp, out=yl, where=gp>0)
    ds = np.any(bm & (bd > THRESHOLD),axis=1)
    ls = np.any(ym & (yl > THRESHOLD),axis=1)
    ng = int(np.sum(gated)); n = len(gated)
    nd = int(np.count_nonzero(d > THRESHOLD)); nl = int(np.count_nonzero(l > THRESHOLD))
    return {'steps': n, 'gated_steps': ng, 'gated_fraction': ratio(ng,n),
            'projection_active_steps': int(np.sum(active)), 'projection_active_fraction': float(np.mean(active)),
            'binding_rows_per_gated_step': distribution(np.sum(bm,axis=1)),
            'bystander_rows_per_gated_step': distribution(np.sum(gs==1,axis=1)),
            'zero_load_bystander_rowsteps_excluded': int(np.count_nonzero((gs==1)&(gp==0))),
            'spillover': {'eligible_rowsteps':len(d),'events':nd,'row_frequency':ratio(nd,len(d)),
              'gated_steps_with_event':int(ds.sum()),'gated_step_frequency':ratio(int(ds.sum()),ng),
              'all_eligible':distribution(d),'event_only':distribution(d[d>THRESHOLD])},
            'bystander_loss': {'eligible_rowsteps':len(l),'events':nl,'row_frequency':ratio(nl,len(l)),
              'gated_steps_with_event':int(ls.sum()),'gated_step_frequency':ratio(int(ls.sum()),ng),
              'all_eligible':distribution(l),'event_only':distribution(l[l>THRESHOLD])},
            'extra_neighbor_loss_binding':distribution(extra), 'own_scale_deficit_binding':distribution(base),
            'decomposition_abs_residual_max':float(np.max(np.abs(d-base-extra))) if d.size else None}


def main():
    start = time.perf_counter()
    expected_protocol_hash = (ROOT/'PROTOCOL.sha256').read_text().split()[0]
    assert hfile(ROOT/'PROTOCOL.md') == expected_protocol_hash
    manifest = json.loads((ROOT/'inputs/production_manifest.json').read_text())
    assert hfile(ROOT/'inputs/production_manifest.json') == META['manifest_sha256']
    assert META['seed_list'] == manifest['randomization']['paired_seeds'][:META['K']]
    dump('evidence/environment.json',{'metadata':META,'python':sys.version,'numpy':np.__version__,
        'platform':platform.platform(),'command':'python code/measure.py','protocol_sha256':expected_protocol_hash})
    print('PROTOCOL',expected_protocol_hash,'SEEDS',META['seed_list'],flush=True)
    controls()
    orig=load_engine('r0046882_original','engine_original.py',META['original_engine_sha256'])
    inst=load_engine('r0046882_instrumented','engine_instrumented.py',META['instrumented_engine_sha256'])
    config, protocol, _ = configure(orig,manifest)
    dump('evidence/configuration.json',{'metadata':META,'model':dataclasses.asdict(config),
         'protocol':dataclasses.asdict(protocol),'measured_branch':'continue','capacity':config.capacity})
    first=META['seed_list'][0]
    print('FIRST SEED original start',first,flush=True)
    a,ha=simulate(orig,first,manifest)
    print('FIRST SEED original complete',ha,flush=True)
    observer=Observer(80000,12)
    b,hb=simulate(inst,first,manifest,observer)
    fa,fb,bad=exact_compare(a,b)
    equal_stream=ha==hb
    report={'metadata':META,'seed':first,'compared_leaves':len(fa),'mismatched_leaves':bad,
        'original_trace':ha,'instrumented_trace':hb,'trace_equal':equal_stream,
        'exact_byte_comparison':True,'one_bit_negative_control':'rejected',
        'status':'PASS' if not bad and equal_stream else 'INVALID'}
    dump('evidence/no_instrumentation.json',report)
    np.savez_compressed(ROOT/'evidence/original_outputs.npz',**fa)
    np.savez_compressed(ROOT/'evidence/instrumented_outputs.npz',**fb)
    if bad or not equal_stream:
        raise RuntimeError('Instrumentation changes outputs: invalid run; stopping')
    print('NO-INSTRUMENTATION PASS',len(fa),'leaves; complete post-step trace equal',flush=True)
    observer.save(first)
    del a,b,fa,fb,observer
    for seed in META['seed_list'][1:]:
        print('MEASUREMENT start',seed,flush=True)
        observer=Observer(80000,12)
        _,h=simulate(inst,seed,manifest,observer)
        observer.save(seed)
        dump(f'evidence/trace_{seed}.json',{'metadata':META,'seed':seed,**h})
        print('MEASUREMENT complete',seed,h,flush=True)
    # Aggregation starts only after all declared trajectories and equality pass.
    perseed={}; collected=[]
    for seed in META['seed_list']:
        with np.load(ROOT/'raw'/f'seed_{seed}.npz',allow_pickle=False) as z:
            d={k:z[k] for k in ['row_sum_pre','scale','r_post','pre_violation','projection_active']}
            cap=float(z['capacity'])
        perseed[str(seed)]={}
        for w,(lo,hi) in META['windows'].items():
            perseed[str(seed)][w]=summarize(d['row_sum_pre'][lo:hi],d['scale'][lo:hi],d['r_post'][lo:hi],
                 d['pre_violation'][lo:hi],d['projection_active'][lo:hi],cap)
        collected.append(d)
    pooled={}
    for w,(lo,hi) in META['windows'].items():
        cat={k:np.concatenate([d[k][lo:hi] for d in collected]) for k in collected[0]}
        pooled[w]=summarize(cat['row_sum_pre'],cat['scale'],cat['r_post'],cat['pre_violation'],cat['projection_active'],cap)
    dump('evidence/summary.json',{'metadata':META,'status':'COMPLETED; UNVERIFIED by seats',
         'quantile_method':'linear','per_seed':perseed,'pooled':pooled,'elapsed_seconds':time.perf_counter()-start})
    print('SUMMARY pooled',json.dumps(pooled['all'],indent=2),flush=True)
    print('COMPLETE elapsed_seconds',time.perf_counter()-start,flush=True)

if __name__=='__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        dump('evidence/FAILURE.json',{'status':'INVALID_OR_INCOMPLETE','traceback':traceback.format_exc(),'metadata':META})
        raise
