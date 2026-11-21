"""Researcher 0046882 (Arena.ai). UNVERIFIED by project seats.
Shared date/time, main/copy hashes and DIRECTION-1 scope: ../HEADER.txt.
Post-measurement supplemental validation, NOT a protocol or threshold change.
Independent scalar-loop aggregation of saved observations. Does not import measure.py.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np

P=Path(__file__).resolve().parents[1]
meta=json.loads((P/'METADATA.json').read_text())
reported=json.loads((P/'evidence/summary.json').read_text())['pooled']['all']
D=[]; L=[]; ng=0; na=0; ds=0; ls=0; excluded=0; nr=0
scale_mismatches=0
for seed in meta['seed_list']:
    with np.load(P/'raw'/f'seed_{seed}.npz',allow_pickle=False) as z:
        pre=z['row_sum_pre']; post=z['r_post']; sc=z['scale']; gate=z['pre_violation']; active=z['projection_active']; cap=float(z['capacity'])
    assert pre.shape==post.shape==sc.shape==(80000,12)
    assert gate.shape==active.shape==(80000,)
    assert np.isfinite(pre).all() and np.isfinite(post).all() and np.isfinite(sc).all()
    nr+=len(gate);na+=sum(bool(a) for a in active)
    for k in range(len(gate)):
        if not gate[k]:
            assert pre[k].tobytes()==post[k].tobytes()
            assert all(float(v)==1.0 for v in sc[k])
            continue
        ng+=1; ed=False; el=False
        for i in range(12):
            q=float(pre[k,i]); r=float(post[k,i]); s=float(sc[k,i])
            expected=min(1.,cap/(q+meta['epsilon']))
            if s!=expected:scale_mismatches+=1
            if s<1:
                d=(cap-r)/cap;D.append(d)
                if d>1e-9:ed=True
            elif s==1:
                if q==0:excluded+=1
                else:
                    l=(q-r)/q;L.append(l)
                    if l>1e-9:el=True
            else:raise AssertionError('scale exceeds one')
        ds+=ed;ls+=el
assert scale_mismatches==0

def qlinear(x,p):
    t=(len(x)-1)*p;k=math.floor(t);f=t-k
    return x[k] if k==len(x)-1 else x[k]+f*(x[k+1]-x[k])

def describe(x):
    x.sort()
    return {'n':len(x),'min':x[0] if x else None,'median':qlinear(x,.5) if x else None,
            'p95':qlinear(x,.95) if x else None,'max':x[-1] if x else None}

out={'steps':nr,'gated_steps':ng,'projection_active_steps':na,
     'spillover_events':sum(v>1e-9 for v in D),'bystander_events':sum(v>1e-9 for v in L),
     'spillover_gated_steps':ds,'bystander_gated_steps':ls,'zero_load_bystanders':excluded,
     'spillover_all_eligible':describe(D),'bystander_all_eligible':describe(L),
     'scale_recomputation_mismatches':scale_mismatches}
assert out['steps']==reported['steps'] and ng==reported['gated_steps'] and na==reported['projection_active_steps']
assert excluded==reported['zero_load_bystander_rowsteps_excluded']
for name,ev,st in [('spillover','spillover_events','spillover_gated_steps'),('bystander_loss','bystander_events','bystander_gated_steps')]:
    r=reported[name]; q=out['spillover_all_eligible' if name=='spillover' else 'bystander_all_eligible']
    assert out[ev]==r['events'] and out[st]==r['gated_steps_with_event']
    assert q['n']==r['all_eligible']['n']
    for k in ['min','median','p95','max']:
        # Quantile interpolation can differ in final rounding; never used for event classification.
        assert math.isclose(q[k],r['all_eligible'][k],rel_tol=2e-15,abs_tol=0), (name,k,q[k],r['all_eligible'][k])

# Independently compare all deposited original/instrumented output leaves using bytes.
def files_equal(a,b):
    if sorted(a)!=sorted(b):return False
    return all(a[k].dtype==b[k].dtype and a[k].shape==b[k].shape and a[k].tobytes()==b[k].tobytes() for k in a)
with np.load(P/'evidence/original_outputs.npz',allow_pickle=False) as z:a={k:z[k] for k in z.files}
with np.load(P/'evidence/instrumented_outputs.npz',allow_pickle=False) as z:b={k:z[k] for k in z.files}
assert files_equal(a,b)
c={k:v.copy() for k,v in b.items()}
key=next(k for k in c if c[k].dtype==np.float64 and c[k].size>0)
c[key].reshape(-1).view(np.uint64)[0]^=np.uint64(1)
assert not files_equal(a,c)
out['exact_output_comparison']='PASS';out['one_bit_mutant_rejected_at']=key
out['metadata']=meta;out['status']='PASS; UNVERIFIED by seats'
(P/'evidence/crosscheck.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps(out,indent=2))
