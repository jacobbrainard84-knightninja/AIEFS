"""Finite actual-compute_R comparisons; no patched coherence function or coupled run.
Protocol: SOURCE_COMPARISON_PLAN.md. Run with assertions enabled.
"""
from __future__ import annotations
import sys
if not __debug__:
    raise SystemExit('Python assertions must be enabled; do not use -O/-OO.')
import cmath
from dataclasses import replace
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('R040282_AIEFS_ENGINE',ROOT/'source_state/main/aief_experiment_engine_v1.py')).expanduser().resolve()
ATOL=2e-14
SEED=2026090404


def load_source():
    spec=importlib.util.spec_from_file_location('r040282_ema_engine',SOURCE)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def readout(C):
    n=len(C);R=np.zeros((n,n),dtype=float)
    for i in range(n):
        for j in range(n):
            if i!=j:R[i,j]=(abs(complex(C[i,j]))+abs(complex(C[j,i])))/2
    return R


def oracle(C,theta,delayed,cfg,mode=None):
    n=len(theta);result=np.empty((n,n),dtype=complex);alpha=cfg.alpha
    for i in range(n):
        for j in range(n):
            phase=float(theta[i])-float(delayed[j])
            if mode!='omit_omega_tau':phase-=(float(cfg.omega[i])+float(cfg.omega[j]))/2*cfg.tau
            z=cmath.rect(1.0,phase)
            a,b=(1-alpha,alpha) if mode=='swapped_alpha_weights' else (alpha,1-alpha)
            result[i,j]=a*complex(C[i,j])+b*z
    R=readout(result)
    if mode=='old_R_before_update':R=readout(C)
    if mode=='magnitude_after_complex_average':
        for i in range(n):
            for j in range(n):
                if i!=j:R[i,j]=abs((complex(result[i,j])+complex(result[j,i]))/2)
    if mode=='zero_complex_diagonal':np.fill_diagonal(result,0)
    return result,R


def make_state(module,cfg,theta,delayed,C):
    history=[np.array(delayed,dtype=float).copy() for _ in range(cfg.delay_steps+1)]
    history[-1]=np.array(theta,dtype=float).copy()
    return module.DynamicState(theta=np.array(theta,dtype=float).copy(),B=np.zeros((cfg.N,cfg.N)),
        coherence_acc=np.array(C,dtype=complex).copy(),history=history)


def evaluate(module,name,cfg,theta,delayed,C,calls,closed_form=False):
    cfg.validate();state=make_state(module,cfg,theta,delayed,C)
    saved_theta=state.theta.copy();saved_B=state.B.copy();saved_history=[x.copy() for x in state.history]
    reference=state.coherence_acc;expected=np.array(C,dtype=complex).copy()
    c_error=0.;r_error=0.;formula_error=0.;max_c=0.;max_r=0.
    for count in range(1,calls+1):
        expected,expected_R=oracle(expected,theta,saved_history[0],cfg)
        observed=module.compute_R(state,cfg)
        ce=float(np.max(np.abs(state.coherence_acc-expected)));re=float(np.max(np.abs(observed-expected_R)))
        c_error=max(c_error,ce);r_error=max(r_error,re)
        assert ce<=ATOL and re<=ATOL,(name,count,ce,re)
        assert state.coherence_acc is reference
        assert np.array_equal(observed,observed.T) and np.all(np.diag(observed)==0)
        assert np.array_equal(state.theta,saved_theta) and np.array_equal(state.B,saved_B)
        assert all(np.array_equal(x,y) for x,y in zip(state.history,saved_history)) and len(state.history)==len(saved_history)
        max_c=max(max_c,float(np.max(np.abs(state.coherence_acc))));max_r=max(max_r,float(np.max(observed)))
        assert float(np.min(observed))>=0 and max_c<=1+ATOL and max_r<=1+ATOL
        if closed_form:
            off=observed[~np.eye(cfg.N,dtype=bool)]
            fe=float(np.max(np.abs(off-(1-cfg.alpha**count))))
            formula_error=max(formula_error,fe);assert fe<=ATOL,(name,count,fe)
    return {'case':name,'N':cfg.N,'alpha':cfg.alpha,'calls':calls,'maximum_C_error':c_error,
        'maximum_R_error':r_error,'maximum_fixed_input_formula_error':formula_error,
        'maximum_C_norm':max_c,'maximum_R':max_r,'all_passed':True}


def main():
    destination=ROOT/'source_comparison_results.json';destination.unlink(missing_ok=True)
    module=load_source();base=module.DEFAULT_MODEL_CONFIG;rng=np.random.default_rng(SEED)
    cases=[];control_input=None
    for n in [1,2,3,6,12]:
        for rho in [.5,1.,2.]:
            cfg=replace(base,N=n,omega=tuple(float(x) for x in np.linspace(1.,2.,n)),T_window=rho*base.T_window)
            for initial in ['zero','random']:
                theta=rng.uniform(0,2*math.pi,n);delayed=rng.uniform(0,2*math.pi,n)
                C=np.zeros((n,n),dtype=complex) if initial=='zero' else rng.random((n,n))*np.exp(1j*rng.uniform(-math.pi,math.pi,(n,n)))
                name=f'N{n}_rho{rho:g}_{initial}'
                cases.append(evaluate(module,name,cfg,theta,delayed,C,2))
                if n==3 and rho==1 and initial=='random':control_input=(cfg,theta.copy(),delayed.copy(),C.copy())
    for label,offset in [('aligned',0.),('quarter_turn',math.pi/2),('anti_phase',math.pi)]:
        cfg=replace(base,N=2,omega=(1.,1.),T_window=base.dt/math.log(2))
        theta=np.array([0.,offset]);delayed=np.mod(theta-cfg.tau,2*math.pi)
        cases.append(evaluate(module,'fixed_offset_'+label,cfg,theta,delayed,np.zeros((2,2),complex),64,True))
    configuration_controls=[]
    for label,Tw in [('alpha_rounds_to_one',1e30),('alpha_underflows_to_zero',1e-30)]:
        cfg=replace(base,N=2,omega=(1.,1.),T_window=Tw)
        if label=='alpha_underflows_to_zero':
            # Protocol correction is recorded, not silently counted as a numerical pass.
            try:cfg.validate()
            except ValueError as exc:
                assert cfg.alpha==0 and 'alpha=' in str(exc) and '(0, 1]' in str(exc)
                configuration_controls.append({'case':label,'expected_rejection_observed':True,'reason':str(exc),'compute_R_called':False})
            else:raise AssertionError('Expected alpha=0 configuration rejection')
            continue
        theta=np.array([.2,1.4]);delayed=np.array([1.1,.3])
        case=evaluate(module,label,cfg,theta,delayed,np.zeros((2,2),complex),1)
        assert cfg.alpha==1.
        case['interpretation']='Valid binary alpha=1, not a defect; exact-real strict-alpha theorem does not transfer to every binary config.'
        cases.append(case)
    assert control_input is not None
    cfg,theta,delayed,C=control_input;expected_C,expected_R=oracle(C,theta,delayed,cfg)
    sensitivities=[]
    for mode in ['last_history_instead_of_oldest','omit_omega_tau','swapped_alpha_weights','old_R_before_update','magnitude_after_complex_average','zero_complex_diagonal']:
        if mode=='last_history_instead_of_oldest':wrong_C,wrong_R=oracle(C,theta,theta,cfg)
        else:wrong_C,wrong_R=oracle(C,theta,delayed,cfg,mode)
        distance=max(float(np.max(np.abs(wrong_C-expected_C))),float(np.max(np.abs(wrong_R-expected_R))))
        assert distance>1e-8,(mode,distance)
        sensitivities.append({'wrong_translation':mode,'maximum_separation':distance,'detected':True})
    assert len(cases)==34 and len(sensitivities)==6 and len(configuration_controls)==1 and sum(c['calls'] for c in cases)==253
    result={'agent':'Researcher 040282','cycle':4,'scope':'Finite component comparisons of actual compute_R on controlled/clamped states; no advance_state or coupled-trajectory theorem',
        'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seed':SEED,
        'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
        'absolute_tolerance':ATOL,'relative_tolerance':0,'case_count':len(cases),'compute_R_calls':sum(c['calls'] for c in cases),
        'maximum_C_error':max(c['maximum_C_error'] for c in cases),'maximum_R_error':max(c['maximum_R_error'] for c in cases),
        'all_passed':True,'cases':cases,'sensitivity_controls':sensitivities,'configuration_controls':configuration_controls}
    destination.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
