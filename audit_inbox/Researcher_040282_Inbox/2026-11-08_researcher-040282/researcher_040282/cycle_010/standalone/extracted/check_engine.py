"""Nine common actual-engine methods and eleven independent wrong models.
Only immutable synthetic primitive inputs; no production simulation entry point.
All checks survive -O. AssertionError subclass only for semantic mismatches;
import/validation/runtime/setup errors are never credited control detections.
"""
import argparse
from dataclasses import asdict,replace
import io
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
from load_reviewed import load,verify
from step_contract import (ABS_TOL,MIN_CONTROL_WITNESS,base_case,cases,control_cases,
                           drift_case,reference,shadow_after)


class ContractMismatch(AssertionError):
    def __init__(self,field,expected,observed,delta=None):
        self.field=field;self.expected=expected;self.observed=observed;self.delta=delta
        super().__init__(f'{field}: expected {expected}; observed {observed}; component difference {delta}')


def require(condition,message):
    if not condition:raise RuntimeError(message)


def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def field_arrays(prediction):
    return {'C':prediction.C,'R_physical':prediction.R,'R_driver':prediction.R,
            'B':prediction.B,'theta':prediction.theta,'history':prediction.history}


def actual_arrays(state,physical,driver):
    return {'C':state.coherence_acc,'R_physical':physical,'R_driver':driver,
            'B':state.B,'theta':state.theta,'history':state.history}


def component_error(expected,observed,field):
    want=np.asarray(expected);got=np.asarray(observed)
    if want.shape!=got.shape:raise ContractMismatch(field+'.shape',list(want.shape),list(got.shape))
    if not np.all(np.isfinite(want)) or not np.all(np.isfinite(got)):
        raise ContractMismatch(field+'.finite',True,False)
    # Real/imag components each compared, never a NaN-masking whole-element max.
    if np.iscomplexobj(want) or np.iscomplexobj(got):
        return max(float(np.max(np.abs(got.real-want.real),initial=0.0)),
                   float(np.max(np.abs(got.imag-want.imag),initial=0.0)))
    return float(np.max(np.abs(got-want),initial=0.0))


def storage_ownership(state):
    for i,h in enumerate(state.history):
        if np.shares_memory(h,state.theta):raise ContractMismatch('storage_ownership','independent history/theta','shared theta/history '+str(i))
        for j in range(i):
            if np.shares_memory(h,state.history[j]):raise ContractMismatch('storage_ownership','independent history vectors',f'shared history {j}/{i}')


def compare(prediction,state,physical,driver,info):
    errors={}
    for field,want in field_arrays(prediction).items():
        error=component_error(want,actual_arrays(state,physical,driver)[field],field);errors[field]=error
        if error>ABS_TOL:raise ContractMismatch(field,'absolute error <= '+str(ABS_TOL),error,error)
    for field in ('pre_violation','projection_active'):
        observed=info[field]
        if type(observed) is not bool or observed!=getattr(prediction,field):
            raise ContractMismatch(field,getattr(prediction,field),observed)
    for field in ('g_min_pre','g_min'):
        error=component_error(getattr(prediction,field),info[field],field);errors[field]=error
        if error>ABS_TOL:raise ContractMismatch(field,getattr(prediction,field),info[field],error)
    theta=np.asarray(state.theta)
    if np.any(theta<0.0) or np.any(theta>=math.tau):raise ContractMismatch('phase_range','[0,2*pi)',theta.tolist())
    B=np.asarray(state.B)
    if not np.array_equal(B,B.T) or np.any(np.diag(B)!=0.0) or np.any(B<0.0):
        raise ContractMismatch('B_structure','symmetric/zero diagonal/nonnegative',B.tolist())
    storage_ownership(state)
    return errors


def materialize(prediction,alias=False):
    theta=np.array(prediction.theta,dtype=float)
    state=SimpleNamespace(theta=theta,B=np.array(prediction.B,dtype=float),
                          coherence_acc=np.array(prediction.C,dtype=complex),
                          history=[np.array(h,dtype=float) for h in prediction.history])
    if alias:state.history[-1]=theta
    info={key:getattr(prediction,key) for key in ('pre_violation','projection_active','g_min_pre','g_min')}
    return state,np.array(prediction.R),np.array(prediction.R),info


class Context:
    def __init__(self,module):
        self.module=module;self.records=[];self.calls=0;self.initializations=0
        self.domain_records=[];self.trace_states=0;self.trace_coordinates=0
        self.oldest_pair=None;self.interior_pair=None
    def config(self,case):
        cfg=self.module.ModelConfig(**asdict(case.p));cfg.validate();return cfg
    def state(self,case):
        return self.module.DynamicState(np.array(case.theta),np.array(case.B),np.array(case.C),
                                        [np.array(h) for h in case.history])
    def checked(self,case,label,state=None):
        frozen_before=repr(case)
        # The reference is evaluated BEFORE target advance, including state reuse.
        prediction=reference(case);cfg=self.config(case)
        if state is None:state=self.state(case)
        state.validate(cfg)
        rng=np.random.default_rng(1040282);rng_before=json.dumps(rng.bit_generator.state,sort_keys=True)
        self.calls+=1
        physical,driver,info=self.module.advance_state(state,cfg,rng,shuffle_driver=False)
        state.validate(cfg)
        if rng_before!=json.dumps(rng.bit_generator.state,sort_keys=True):
            raise ContractMismatch('rng_preservation','unchanged for non-shuffle','changed')
        errors=compare(prediction,state,physical,driver,info)
        if frozen_before!=repr(case):raise ContractMismatch('immutable_case_preservation','unchanged','changed')
        self.records.append({'label':label,'case':case.name,'N':case.p.N,'D':round(case.p.tau/case.p.dt),
                             'component_errors':errors,'maximum_component_error':max(errors.values()),
                             'flags':{k:info[k] for k in ('pre_violation','projection_active')},
                             'theta':state.theta.tolist(),'g_min_pre':float(info['g_min_pre']),'g_min':float(info['g_min']),
                             'input_case_unchanged':True,'rng_unchanged':True,'independent_history_storage':True})
        return prediction,state,(physical,driver,info)


def suite(context):
    class EngineContract(unittest.TestCase):
        def test_01_nine_scalar_steps(self):
            for case in cases():
                with self.subTest(case=case.name):context.checked(case,'one_step/'+case.name)
        def test_02_oldest_is_immediate_input(self):
            first=base_case('oldest_pair_base',2,True)
            changed=replace(first,name='oldest_pair_changed',history=((0.19,4.77,5.38),)+first.history[1:])
            a,_,_=context.checked(first,'oldest/base');b,_,_=context.checked(changed,'oldest/changed')
            cdelta=component_error(a.C,b.C,'C');tdelta=component_error(a.theta,b.theta,'theta')
            require(cdelta>MIN_CONTROL_WITNESS and tdelta>MIN_CONTROL_WITNESS,'Oldest-read probe is vacuous')
            context.oldest_pair={'C_change':cdelta,'theta_change':tdelta}
        def test_03_interior_is_latent_not_discarded(self):
            first=base_case('interior_pair_base',2,True)
            changed=replace(first,name='interior_pair_changed',history=(first.history[0],(0.22,3.44,5.55),first.history[2]))
            a,_,_=context.checked(first,'interior/base');b,_,_=context.checked(changed,'interior/changed')
            immediate={field:component_error(getattr(a,field),getattr(b,field),field) for field in ('C','R','B','theta')}
            latent=component_error(a.history,b.history,'history')
            require(all(value==0.0 for value in immediate.values()) and latent>MIN_CONTROL_WITNESS,'Interior age probe failed')
            context.interior_pair={'instantaneous_changes':immediate,'shifted_history_change':latent}
        def test_04_reachable_dyadic_histories(self):
            for d in range(1,6):
                shadow=drift_case(d);state=context.state(shadow)
                for n in range(13):
                    want=np.array([[0.25+max(0,n+i-d)*0.125] for i in range(d+1)])
                    if not np.array_equal(np.array(state.history),want):
                        raise ContractMismatch('exact_history_trace',want.tolist(),np.array(state.history).tolist())
                    if not np.array_equal(state.theta,np.array([0.25+n*0.125])):
                        raise ContractMismatch('exact_current_trace',[0.25+n*0.125],state.theta.tolist())
                    storage_ownership(state);context.trace_states+=1;context.trace_coordinates+=d+1
                    if n<12:
                        prediction,state,_=context.checked(shadow,f'dyadic/D{d}/step{n+1}',state=state)
                        # Next expected state comes from independent spec, not observed target.
                        shadow=shadow_after(shadow,prediction)
        def test_05_phase_uses_new_gated_B(self):
            case=base_case('new_gated_B',2,True);prediction,_,_=context.checked(case,'phase/new_gated_B')
            require(prediction.pre_violation and prediction.projection_active,'Active phase probe never gates')
            for wrong in ('old_B_for_phase','unprojected_B_for_phase'):
                require(component_error(prediction.theta,reference(case,wrong).theta,'theta')>MIN_CONTROL_WITNESS,'Vacuous phase order control')
        def test_06_updated_directed_C_then_magnitude(self):
            case=base_case('updated_directed_C',2,True);prediction,_,_=context.checked(case,'C/updated_then_magnitude')
            for wrong in ('old_C_for_R','symmetrize_C_first'):
                require(component_error(prediction.R,reference(case,wrong).R,'R')>MIN_CONTROL_WITNESS,'Vacuous C order control')
        def test_07_wrap_clipping_and_ranges(self):
            case=cases()[6];prediction,_,_=context.checked(case,'clipping/negative_raw')
            require(prediction.minimum_raw_offdiagonal_proposal<0 and all(v==0 for row in prediction.B for v in row),'Clipping probe is vacuous')
            wrap=next(row for row in context.records if row['label']=='one_step/phase_wrap_D1')
            require(wrap['theta'][0]<1.0 and wrap['theta'][2]<1.0,'Wrap probe did not cross modulo boundary')
            require(all(0<=v<math.tau for row in context.records for v in row['theta']),'Range probe failed')
        def test_08_initializer_and_copy_ownership(self):
            case=base_case('copy_probe',2,True);cfg=context.config(case)
            initialized=context.module.initialize_state(1040282,cfg);context.initializations+=1;initialized.validate(cfg)
            require(len(initialized.history)==3 and all(np.array_equal(h,initialized.theta) for h in initialized.history),'Constant prehistory initializer correspondence failed')
            storage_ownership(initialized)
            _,state,_=context.checked(case,'ownership/current_mutation')
            saved=[h.copy() for h in state.history];state.theta[0]+=0.5
            require(all(np.array_equal(a,b) for a,b in zip(saved,state.history)),'Current phase mutation leaked into history')
            _,state,_=context.checked(base_case('copy_probe_D3',3,True),'ownership/history_mutation')
            theta=state.theta.copy();others=[h.copy() for h in state.history[:-1]];state.history[-1][0]+=0.5
            require(np.array_equal(state.theta,theta) and all(np.array_equal(a,b) for a,b in zip(others,state.history[:-1])),'History mutation leaked to current/other history')
        def test_09_exact_delay_validation_domain(self):
            for case in cases():
                cfg=context.config(case)
                require(cfg.delay_steps>=1 and cfg.delay_steps*cfg.dt==cfg.tau,'Invalid planned source domain')
            for tau in (0.2,0.1875):
                p=replace(base_case().p,tau=tau);cfg=context.module.ModelConfig(**asdict(p))
                try:cfg.validate()
                except ValueError as error:
                    require('must equal tau' in str(error),'Domain rejected for unintended reason')
                    context.domain_records.append({'tau':tau,'dt':p.dt,'rejected_for_exact_delay':True,'semantic_negative_detection_credited':False})
                else:raise ContractMismatch('exact_delay_validation','ValueError',None)
    return unittest.defaultTestLoader.loadTestsFromTestCase(EngineContract)


def wrong_models():
    records=[]
    for name,case,intended in control_cases():
        expected=reference(case)
        wrong=reference(case,None if name=='alias_new_theta' else name)
        state,physical,driver,info=materialize(wrong,alias=name=='alias_new_theta')
        try:compare(expected,state,physical,driver,info)
        except ContractMismatch as error:
            require(error.field==intended,'Wrong detection mechanism: '+name+'/'+error.field)
            if intended!='storage_ownership':require(error.delta is not None and error.delta>MIN_CONTROL_WITNESS,'Control witness too small')
            records.append({'model':name,'detected':True,'intended_field':intended,'detected_field':error.field,
                            'maximum_component_difference':error.delta,'minimum_numeric_witness_required':None if intended=='storage_ownership' else MIN_CONTROL_WITNESS,
                            'setup_errors_credited':0})
        else:raise RuntimeError('Undetected wrong model: '+name)
    require(len(records)==11 and len({r['model'] for r in records})==11,'Wrong-model inventory incomplete')
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--kind',choices=('common','wrong_models'),required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        if args.kind=='wrong_models':
            # Source verification, but NO engine calls necessary for independent falsifiers.
            manifest=verify(args.source);records=wrong_models()
            value={'kind':'wrong_models','optimized_python':not __debug__,'detected':len(records),'records':records,
                   'actual_engine_advances':0,'setup_errors_credited':0,'source_files_unchanged':len(manifest['modules']),
                   'metadata_files_unchanged':len(manifest['metadata'])}
            save(args.output/'wrong_models.json',records);save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
        module=load(args.source);context=Context(module);stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(context));print(stream.getvalue(),end='')
        save(args.output/'advance_observations.json',context.records);save(args.output/'domain_checks.json',context.domain_records)
        value={'kind':'common','optimized_python':not __debug__,'tests_run':result.testsRun,'failures':len(result.failures),
               'errors':len(result.errors),'skipped':len(result.skipped),'actual_engine_advances':context.calls,
               'source_initializations':context.initializations,'reference_compared_transitions':len(context.records),
               'maximum_component_error':max((r['maximum_component_error'] for r in context.records),default=0.0),
               'oldest_pair':context.oldest_pair,'interior_pair':context.interior_pair,
               'dyadic_exact_states':context.trace_states,'dyadic_exact_stored_coordinates':context.trace_coordinates,
               'invalid_exact_delay_configs_rejected_not_semantic_detections':len(context.domain_records),
               'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,'immutable_cases_rng_and_history_ownership_verified':True,
               'source_files_unchanged':len(verify(args.source)['modules']),'metadata_files_unchanged':len(verify(args.source)['metadata']),
               'actual_full_engine_import_no_source_function_copy_replacement_or_edit':True,
               'production_simulation_baseline_CLI_or_certificate_called':False}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0 if result.wasSuccessful() else 1
    except Exception as error:
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_negative_detection_credited':False});raise


if __name__=='__main__':raise SystemExit(main())
