"""Researcher0046882 / DIRECTION-2; UNVERIFIED; shared HEADER.txt.
Supplemental independent consistency check after the declared measurement.
No imports of common.py or run_cohort.py; no thresholds or estimands changed.
Checks reconstructed scalar/column events from temporary raw arrays, exact bytes,
all descriptors, and summation of per-seed populations into full/pilot pools.
"""
from pathlib import Path
import hashlib,json
import numpy as np
P=Path(__file__).resolve().parents[1]
M=json.loads((P/'METADATA.json').read_text())
S=json.loads((P/'evidence/per_seed_summary.json').read_text())['per_seed']
POOLS=json.loads((P/'evidence/pooled_summary.json').read_text())['groups']
H=json.loads((P/'evidence/raw_array_hashes.json').read_text())['seeds']
completion=json.loads((P/'evidence/completion.json').read_text())
assert completion['status']=='COMPLETE_40' and len(S)==40
scratch=Path(completion['scratch_path'])
checks=0;seed_events=[]
for seed in M['seed_list']:
    with np.load(scratch/'raw'/f'seed_{seed}.npz',allow_pickle=False) as z:
        raw={k:z[k] for k in z.files}
    for k,a in raw.items():
        ref=H[str(seed)][k]
        assert a.dtype.str==ref['dtype'] and list(a.shape)==ref['shape']
        assert hashlib.sha256(a.tobytes()).hexdigest()==ref['sha256']
        assert np.isfinite(a).all()
    pre,post,scale=raw['row_sum_pre'],raw['r_post'],raw['scale']
    gate=raw['pre_violation'];cap=float(raw['capacity'])
    assert pre.shape==post.shape==scale.shape==(80000,12)
    expected_scales=np.minimum(1.,cap/(pre[gate]+M['epsilon']))
    assert expected_scales.tobytes()==scale[gate].tobytes()
    assert pre[~gate].tobytes()==post[~gate].tobytes()
    for window,(lo,hi) in M['windows'].items():
        r=S[str(seed)][window];active=raw['projection_active'][lo:hi];g=gate[lo:hi]
        assert r['steps']==hi-lo and r['gated_steps']==int(g.sum()) and r['projection_active_steps']==int(active.sum())
        dvals=[];lvals=[];nde=0;nle=0;ex=0;ds=np.zeros(hi-lo,dtype=bool);ls=ds.copy()
        for i in range(12):
            q=pre[lo:hi,i];o=post[lo:hi,i];s=scale[lo:hi,i]
            bind=g&(s<1);byst=g&(s==1)&(q>0)
            dv=(cap-o[bind])/cap;lv=(q[byst]-o[byst])/q[byst]
            dvals.append(dv);lvals.append(lv)
            nde+=int(np.sum(dv>1e-9));nle+=int(np.sum(lv>1e-9));ex+=int(np.sum(g&(s==1)&(q==0)))
            ds[np.flatnonzero(bind)[dv>1e-9]]=True;ls[np.flatnonzero(byst)[lv>1e-9]]=True
        d=np.concatenate(dvals);l=np.concatenate(lvals)
        for name,arr,n,st in [('spillover',d,nde,int(ds.sum())),('bystander_loss',l,nle,int(ls.sum()))]:
            assert r[name]['events']==n and r[name]['eligible_rowsteps']==len(arr)
            assert r[name]['gated_steps_with_event']==st
            assert r[name]['all_eligible']['max']==(float(arr.max()) if len(arr) else None)
            assert r[name]['all_eligible']['min']==(float(arr.min()) if len(arr) else None)
        assert r['zero_load_bystander_rowsteps_excluded']==ex
        checks+=1
    with np.load(P/'descriptors'/f'future_{seed}.npz',allow_pickle=False) as z:
        bd=scale[48000:]<1;counts=bd.sum(axis=1).astype(np.uint8)
        assert counts.tobytes()==z['binding_count'].tobytes()
        assert np.min(scale[48000:],axis=1).tobytes()==z['min_scale'].tobytes()
        # Independent loop over future steps for spread; avoid reusing np.where implementation.
        spread=np.empty(32000)
        for j in range(32000):
            vals=pre[j+48000][bd[j]]
            spread[j]=float(max(vals)-min(vals)) if len(vals) else np.nan
        assert np.array_equal(spread,z['binding_load_spread'],equal_nan=True)
    if S[str(seed)]['future']['spillover']['events'] or S[str(seed)]['future']['bystander_loss']['events']:seed_events.append(seed)
    print('VALIDATED',seed,'7 windows,6 raw arrays,future descriptors',flush=True)
for group,seeds in [('full40',M['seed_list']),('pilot4',M['pilot_seeds'])]:
    for w in M['windows']:
        r=POOLS[group][w]
        for field in ['steps','gated_steps','projection_active_steps','zero_load_bystander_rowsteps_excluded']:
            assert r[field]==sum(S[str(seed)][w][field] for seed in seeds)
        for effect in ['spillover','bystander_loss']:
            for field in ['events','eligible_rowsteps','gated_steps_with_event']:
                assert r[effect][field]==sum(S[str(seed)][w][effect][field] for seed in seeds)
            vals=[S[str(seed)][w][effect]['all_eligible']['max'] for seed in seeds]
            vals=[v for v in vals if v is not None]
            assert r[effect]['all_eligible']['max']==(max(vals) if vals else None)
with np.load(P/'evidence/original_outputs.npz',allow_pickle=False) as za,np.load(P/'evidence/instrumented_outputs.npz',allow_pickle=False) as zb:
    assert sorted(za.files)==sorted(zb.files)
    assert all(za[k].dtype==zb[k].dtype and za[k].shape==zb[k].shape and za[k].tobytes()==zb[k].tobytes() for k in za.files)
assert seed_events==json.loads((P/'evidence/associations.json').read_text())['groups']['any_event']
out={'metadata':M,'status':'PASS; UNVERIFIED by seats','seed_windows_validated':checks,'raw_arrays_hashed':240,
     'future_descriptor_steps_validated':1280000,'future_event_seeds':seed_events,
     'scope_limit':'Consistency check, not independent simulation. Pooled quantiles not independently regenerated here; raw-array hashes support external reproduction.'}
(P/'evidence/validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',checks,'seed-window tables;240 raw array hashes;1,280,000 future descriptor steps',flush=True)
