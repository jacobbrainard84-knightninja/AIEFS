"""Researcher 040282: exact finite-gate foundations and source cross-checks.

Exact Fraction tests are finite examples, not a Lean proof. The accompanying
note supplies general mathematical arguments. Engine tests isolate the
admissibility stage by setting eta=mu=gamma=0; these are synthetic one-step
controls, not new production trajectories or evidence of asymptotic locking.
"""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction as F
import json
import os
from pathlib import Path
import random
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = Path(os.environ.get('AIEFS_AUDIT_REPO', ROOT.parent / 'aiefs_repository_audit/repository')).resolve()
sys.path.insert(0, str(REPO))
import aief_experiment_engine_v1 as engine
import AIEF_1_4_actual_admissibility_branch_audit as actual
import AIEF_1_4_stationarity_perturbation_analysis_updated as base

ZERO=F(0);ONE=F(1)
C=F(19,30)
EPS=F(1,10**12)


def row_sums(w):
    return [sum(row,ZERO) for row in w]


def scales(w,caps,eps):
    return [min(ONE,c/(q+eps)) for c,q in zip(caps,row_sums(w),strict=True)]


def kernel(w,caps,eps):
    s=scales(w,caps,eps)
    return [[w[i][j]*min(s[i],s[j]) for j in range(len(w))] for i in range(len(w))]


def guarded_gate(w,caps,eps):
    if all(q<=c for q,c in zip(row_sums(w),caps,strict=True)):
        return [row.copy() for row in w]
    return kernel(w,caps,eps)


def single_edge(x,n=12):
    w=[[ZERO]*n for _ in range(n)]
    w[0][1]=w[1][0]=x
    return w


def value(fraction):
    return {'exact':str(fraction),'float':float(fraction)}


def exact_properties():
    rng=random.Random(40282)
    active=0;off=0;zero_capacity=0
    for case in range(300):
        n=1+case%7
        caps=[F(rng.randrange(0,31),10) for _ in range(n)]
        zero_capacity+=any(c==0 for c in caps)
        w=[[ZERO]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1,n):w[i][j]=w[j][i]=F(rng.randrange(0,41),40)
        before=row_sums(w)
        on=any(q>c for q,c in zip(before,caps,strict=True))
        y=guarded_gate(w,caps,EPS)
        after=row_sums(y)
        assert all(q<=c for q,c in zip(after,caps,strict=True))
        assert guarded_gate(y,caps,EPS)==y
        for i in range(n):
            assert y[i][i]==0
            for j in range(n):
                assert ZERO<=y[i][j]<=w[i][j]
                assert y[i][j]==y[j][i]
        if on:
            active+=1;s=scales(w,caps,EPS);s_min=min(s)
            for i in range(n):
                assert s_min*before[i] <= after[i] <= s[i]*before[i] <= caps[i]
                if caps[i]>0:assert after[i]<caps[i]
        else:
            off+=1;assert y==w
    return {'cases':300,'active':active,'inactive':off,
            'cases_with_zero_capacity':zero_capacity,
            'claims_checked':['nonnegativity','symmetry','zero diagonal','entrywise contraction',
                              'capacity bound','identity on feasible inputs','guarded idempotence',
                              'active row-sum sandwich']}


def counterexamples():
    caps=[C]*12
    boundary=single_edge(C)
    first=kernel(boundary,caps,EPS)[0][1]
    second=kernel(single_edge(first),caps,EPS)[0][1]
    assert guarded_gate(boundary,caps,EPS)==boundary
    assert second<first<C
    # Exact algebraic identity explaining why the second kernel pass rescales.
    assert first+EPS-C==EPS*EPS/(C+EPS)
    # A sequence approaching the guard boundary from above.
    n=1000
    x=C+EPS/n
    output=guarded_gate(single_edge(x),caps,EPS)[0][1]
    active_limit=C*C/(C+EPS)
    assert output-active_limit == C*EPS*(x-C)/((x+EPS)*(C+EPS))
    discontinuity_jump=C-active_limit
    assert discontinuity_jump==C*EPS/(C+EPS)>0
    x_near=C+EPS/2
    out_near=guarded_gate(single_edge(x_near),caps,EPS)[0][1]
    lipschitz_ratio=abs(out_near-C)/abs(x_near-C)
    assert lipschitz_ratio>1
    # Same strict active branch, unequal endpoint winners excluded: node 0
    # uniquely controls both nonzero edges and both leaves remain unscaled.
    u1=F(1,3);u2=F(2,5);v=F(2,5);um=(u1+u2)/2
    def star(u):
        w=[[ZERO]*12 for _ in range(12)]
        w[0][1]=w[1][0]=u;w[0][2]=w[2][0]=v
        s=scales(w,caps,EPS)
        assert s[0]<s[1]==s[2]==ONE
        assert row_sums(w)[0]>C
        return guarded_gate(w,caps,EPS)[0][1]
    jensen=star(um)-(star(u1)+star(u2))/2
    assert jensen!=0
    return {'capacity':value(C),'epsilon':value(EPS),
            'unconditional_kernel':{'at_capacity_first':value(first),'second':value(second),
                'first_minus_second':value(first-second),'idempotent':False},
            'guard_boundary':{'guarded_value_at_capacity':value(C),
                'one_sided_active_limit':value(active_limit),'nonzero_jump':value(discontinuity_jump),
                'sequence_n':n,'sequence_input':value(x),'sequence_output':value(output),
                'sequence_error_from_active_limit':value(output-active_limit),
                'nonexpansivity_counterexample_ratio':value(lipschitz_ratio)},
            'strict_branch_nonlinearity':{'u1':value(u1),'u2':value(u2),'v':value(v),
                'midpoint_minus_mean_output':value(jensen)}}


def fixed_row_fiber():
    w=[[ZERO if i==j else F(2,5) for j in range(4)] for i in range(4)]
    h=[[ZERO]*4 for _ in range(4)]
    for i,j,a in [(0,1,1),(1,2,-1),(2,3,1),(0,3,-1)]:h[i][j]=h[j][i]=F(a,100)
    wh=[[w[i][j]+h[i][j] for j in range(4)] for i in range(4)]
    assert row_sums(h)==[ZERO]*4
    caps=[C]*4;s=scales(w,caps,EPS)
    y=guarded_gate(w,caps,EPS);yh=guarded_gate(wh,caps,EPS)
    for i in range(4):
        for j in range(4):assert yh[i][j]-y[i][j]==min(s[i],s[j])*h[i][j]
    return {'exact_fixed_row_fiber_identity':'passed','nonzero_perturbation':True}


def engine_crosscheck():
    # ModelConfig validates these as allowed nonnegative rates. The purpose is
    # to isolate the gate, not claim production dynamics use these rates.
    config=replace(engine.DEFAULT_MODEL_CONFIG,eta=0.,mu=0.,gamma=0.)
    config.validate();n=config.N
    A,edges=base.incidence_matrix(n)
    rng=random.Random(40282)
    max_engine_error=0.;max_helper_error=0.;active=0
    cases=96
    atol=5e-15 # Fixed small-N cross-method rounding allowance, not an exact-float theorem.
    for case in range(cases):
        w=[[ZERO]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1,n):w[i][j]=w[j][i]=F(rng.randrange(0,21),200)
        # The 1/200 grid stays at least 1/600 away from capacity 19/30,
        # separating these rounding comparisons from guard-boundary semantics.
        proposed=np.array(w,dtype=float)
        state=engine.DynamicState(theta=np.zeros(n),B=proposed.copy(),
            coherence_acc=np.zeros((n,n),dtype=complex),
            history=[np.zeros(n) for _ in range(config.delay_steps+1)])
        _,_,info=engine.advance_state(state,config,np.random.default_rng(40282+case))
        reference=np.array(guarded_gate(w,[C]*n,EPS),dtype=float)
        err=float(np.max(np.abs(state.B-reference)))
        max_engine_error=max(max_engine_error,err)
        assert err<=atol
        expected_active=any(q>C for q in row_sums(w))
        assert info['pre_violation']==expected_active
        active+=expected_active
        actual_y,details=actual.admissibility_from_nonnegative_proposal(
            proposed[edges],np.full(n,config.capacity),A,edges,config.scale_epsilon)
        err=float(np.max(np.abs(actual_y-reference[edges])))
        max_helper_error=max(max_helper_error,err)
        assert err<=atol
        assert details['gate_on']==expected_active
    return {'synthetic_isolated_one_step_cases':cases,'active_cases':active,'inactive_cases':cases-active,
            'model_rates_for_isolation':{'eta':0,'mu':0,'gamma':0},
            'engine_max_entry_abs_difference':max_engine_error,
            'pure_helper_max_entry_abs_difference':max_helper_error,
            'absolute_rounding_allowance':atol,
            'float64_equivalence_theorem':False,'production_trajectories_regenerated':False}


def main():
    result={'agent':'Researcher 040282','scope':'exact-real gate foundation with exact-rational examples and synthetic source cross-checks',
            'general_proofs':'written in companion note; not Lean-checked',
            'exact_rational_properties':exact_properties(),'counterexamples':counterexamples(),
            'fixed_row_fiber':fixed_row_fiber(),'source_crosscheck':engine_crosscheck()}
    (ROOT/'gate_foundations_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
