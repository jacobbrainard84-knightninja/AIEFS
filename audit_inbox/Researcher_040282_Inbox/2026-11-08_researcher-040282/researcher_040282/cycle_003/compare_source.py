"""Preregistered finite controlled-R check of actual adaptive engine B updates.

The actual compute_R is deliberately replaced for a single call, then restored.
This is NOT a coupled coherence/EMA/delay/phase trajectory or a float64 theorem.
"""
from __future__ import annotations
import sys
if not __debug__:
    raise SystemExit('Run with Python assertions enabled, without -O/-OO.')
from fractions import Fraction as F
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import random
import time
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('R040282_AIEFS_ENGINE',ROOT/'source_state/main/aief_experiment_engine_v1.py')).expanduser().resolve()
ABS_TOL=5e-15
GAP_MARGIN=1e-8
SEED=2026110703

def zeros(n):return [[F(0) for _ in range(n)] for _ in range(n)]
def fraction(x):return F.from_float(float(x))

def oracle(b,r,cfg):
    n=len(b);b=[[fraction(x) for x in row] for row in b];r=[[fraction(x) for x in row] for row in r]
    dt,eta,mu,gamma,a,q,delta,eps,cap=[fraction(getattr(cfg,name)) for name in
        ['dt','eta','mu','gamma','a','q','delta','scale_epsilon','capacity']]
    p=[[F(0) if i==j else max(F(0),b[i][j]+dt*((eta+mu)*r[i][j]-mu-gamma*b[i][j]))
        for j in range(n)] for i in range(n)]
    rows=[sum(row,F(0)) for row in p]
    gap=min(a-q*row for row in rows)
    active=any(row>cap for row in rows)
    assert active==(gap<delta)
    distance=abs(gap-delta)
    assert distance>fraction(GAP_MARGIN), 'Preregistered guard separation failed; do not discard this case'
    scale=[min(F(1),cap/(row+eps)) for row in rows] if active else [F(1)]*n
    out=[[p[i][j]*min(scale[i],scale[j]) for j in range(n)] for i in range(n)]
    return np.array([[float(x) for x in row] for row in out]),active,float(distance)


def main():
    (ROOT/'source_comparison_results.json').unlink(missing_ok=True)
    started=time.perf_counter();assert SOURCE.is_file()
    spec=importlib.util.spec_from_file_location('r040282_cycle003_engine',SOURCE)
    engine=importlib.util.module_from_spec(spec);sys.modules[spec.name]=engine;spec.loader.exec_module(engine)
    cfg=engine.ModelConfig(
        N=engine.FROZEN_N, dt=engine.FROZEN_DT, tau=engine.FROZEN_TAU,
        omega=tuple(float(x) for x in engine.FROZEN_OMEGA), a=engine.FROZEN_A,
        q=engine.FROZEN_Q, delta=engine.FROZEN_DELTA, eta=engine.FROZEN_ETA,
        mu=engine.FROZEN_MU, gamma=engine.FROZEN_GAMMA, T_window=engine.FROZEN_T_WINDOW,
        B_c=engine.FROZEN_B_C, B_init_scale=engine.FROZEN_B_INIT_SCALE)
    cfg.validate();n=cfg.N;assert n==12 and cfg.gamma>0
    cap=fraction(cfg.capacity);cases=[]
    for k in [3,4,6,12]:
        b=zeros(n);r=zeros(n)
        for i in range(k):
            for j in range(i):b[i][j]=b[j][i]=cap/(k-1);r[i][j]=r[j][i]=F(1)
        cases.append(('active_clique_'+str(k),b,r,True))
    for level in [F(0),F(3,7),F(1,2),F(1)]:
        b=zeros(n);r=zeros(n)
        for i in range(n):
            for j in range(i):b[i][j]=b[j][i]=cap/(4*11);r[i][j]=r[j][i]=level
        cases.append(('inactive_dense_R_'+str(level),b,r,False))
    rng=random.Random(SEED)
    for index in range(16):
        b=zeros(n);r=zeros(n)
        for i in range(n):
            for j in range(i):
                b[i][j]=b[j][i]=cap/(2*11)*F(rng.randint(0,16),16)
                r[i][j]=r[j][i]=F(rng.randint(0,16),16)
        cases.append(('inactive_random_'+str(index),b,r,False))
    assert len(cases)==24
    recorded=[]
    for index,(label,b,r,expected_active) in enumerate(cases):
        b=np.array([[float(x) for x in row] for row in b]);r=np.array([[float(x) for x in row] for row in r])
        expected,active,distance=oracle(b,r,cfg);assert active==expected_active
        state=engine.initialize_state(index,cfg);state.B[:]=b
        original=engine.compute_R
        engine.compute_R=lambda state,config:r.copy()
        try:
            _,_,info=engine.advance_state(state,cfg,np.random.default_rng(index),shuffle_driver=False)
        finally:engine.compute_R=original
        error=float(np.max(np.abs(state.B-expected)))
        assert bool(info['pre_violation'])==active
        assert error<=ABS_TOL,(label,error)
        recorded.append({'case':label,'active':active,'gap_boundary_distance':distance,'max_absolute_error':error})
    assert sum(x['active'] for x in recorded)==4
    result={'agent':'Researcher 040282','cycle':3,'source':str(SOURCE),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'scope':'finite controlled-R actual-engine weight steps; compute_R overridden only in process; not coupled dynamics or a float64 theorem',
        'python':sys.version.split()[0],'numpy':np.__version__,'pandas':importlib.metadata.version('pandas'),
        'case_count':len(recorded),'active':4,'inactive':20,'all_passed':True,
        'absolute_tolerance':ABS_TOL,'relative_tolerance':0,'guard_separation_required':GAP_MARGIN,
        'maximum_absolute_error':max(x['max_absolute_error'] for x in recorded),
        'random_case_seed':SEED,'seconds':time.perf_counter()-started,'cases':recorded}
    (ROOT/'source_comparison_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
