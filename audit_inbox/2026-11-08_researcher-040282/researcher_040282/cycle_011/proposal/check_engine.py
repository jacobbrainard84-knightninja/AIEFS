"""Nine bounded full-engine phase methods and ten independent wrong models.
Normal/-O share exact code. All math expectations precede acquired import/calls.
No production simulation, source replacement, pre-call mutating compute_R or S01.
"""
import argparse
from dataclasses import asdict,dataclass
import io
import json
import math
from pathlib import Path
import unittest
import numpy as np
from load_reviewed import load,verify
from phase_contract import (ABS_TOL,MIN_WITNESS,STEPS,capacity_bound,control_witnesses,
                            design_record,drift,input_phasor,phasor,prepare_traces)

class ContractMismatch(AssertionError):
    def __init__(self,field,expected,observed,delta=None):
        self.field=field;self.delta=delta
        super().__init__(f'{field}: expected {expected}; observed {observed}; component difference {delta}')

def require(condition,message):
    if not condition:raise RuntimeError(message)

def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def error(want,got,field):
    want=np.asarray(want);got=np.asarray(got)
    if want.shape!=got.shape:raise ContractMismatch(field+'.shape',list(want.shape),list(got.shape))
    if not np.all(np.isfinite(want)) or not np.all(np.isfinite(got)):raise ContractMismatch(field+'.finite',True,False)
    if np.iscomplexobj(want) or np.iscomplexobj(got):
        return max(float(np.max(np.abs(got.real-want.real),initial=0.0)),float(np.max(np.abs(got.imag-want.imag),initial=0.0)))
    return float(np.max(np.abs(got-want),initial=0.0))

def close(want,got,field):
    delta=error(want,got,field)
    if delta>ABS_TOL:raise ContractMismatch(field,'absolute error <= '+str(ABS_TOL),delta,delta)
    return delta

def ownership(state):
    for i,h in enumerate(state.history):
        if np.shares_memory(h,state.theta) or any(np.shares_memory(h,other) for other in state.history[:i]):
            raise ContractMismatch('history_ownership','independent history/current vectors','shared allocation')

def real_tuple(value):return tuple(float(x) for x in value)
def complex_matrix(value):return tuple(tuple(complex(x) for x in row) for row in value)
def encoded(value):return [[[float(x.real),float(x.imag)] for x in row] for row in value]

@dataclass(frozen=True)
class Observation:
    theta_before:tuple
    theta_after:tuple
    innovation:tuple
    component_errors:tuple
    pre_violation:bool
    projection_active:bool
    row_sums:tuple

class Context:
    def __init__(self,module,traces):
        self.module=module;self.traces=traces;self.observed={};self.records=[];self.ratios=[];self.calls=0
        self.stats={};self.winding_stats={};self.maximum_ratio_error=0.0
    def run_traces(self):
        unchanged=repr(self.traces)
        for trace in self.traces:
            first=trace.initial;p=first.p;cfg=self.module.ModelConfig(**asdict(p));cfg.validate()
            require(cfg.delay_steps>=1 and cfg.delay_steps*cfg.dt==cfg.tau,'Invalid source delay domain')
            state=self.module.DynamicState(np.array(first.theta),np.array(first.B),np.array(first.C),[np.array(h) for h in first.history])
            rng=np.random.default_rng(1040282);rng_before=json.dumps(rng.bit_generator.state,sort_keys=True);items=[]
            for n,frame in enumerate(trace.frames):
                state.validate(cfg);ownership(state)
                for field,want,got in (('theta_before',frame.case.theta,state.theta),('B_before',frame.case.B,state.B),
                                       ('C_before',frame.case.C,state.coherence_acc),('history_before',frame.case.history,state.history)):
                    close(want,got,field)
                old_c=state.coherence_acc.copy();old_theta=real_tuple(state.theta)
                # Sole actual target call. Expected frame was built BEFORE module import.
                self.calls+=1;physical,driver,info=self.module.advance_state(state,cfg,rng,shuffle_driver=False)
                state.validate(cfg);ownership(state)
                prediction=frame.prediction;errors={}
                for field,want,got in (('C',prediction.C,state.coherence_acc),('B',prediction.B,state.B),('theta',prediction.theta,state.theta),
                                       ('history',prediction.history,state.history),('R_physical',prediction.R,physical),('R_driver',prediction.R,driver)):
                    errors[field]=close(want,got,field)
                for flag in ('pre_violation','projection_active'):
                    if type(info[flag]) is not bool or info[flag]!=getattr(prediction,flag):raise ContractMismatch(flag,getattr(prediction,flag),info[flag])
                for field in ('g_min_pre','g_min'):errors[field]=close(getattr(prediction,field),info[field],field)
                if np.any(state.theta<0) or np.any(state.theta>=math.tau):raise ContractMismatch('phase_range','[0,2pi)',state.theta.tolist())
                if not np.array_equal(state.B,state.B.T) or np.any(state.B<0) or np.any(np.diag(state.B)!=0):raise ContractMismatch('B_structure','symmetric nonnegative diag0','bad')
                if rng_before!=json.dumps(rng.bit_generator.state,sort_keys=True):raise ContractMismatch('rng','unchanged','changed')
                # Observed data extraction; NEVER used as independent expected input.
                innovation=complex_matrix((state.coherence_acc-cfg.alpha*old_c)/(1-cfg.alpha))
                errors['input_innovation']=close(frame.input_phasor,innovation,'input_innovation')
                item=Observation(old_theta,real_tuple(state.theta),innovation,tuple(sorted(errors.items())),info['pre_violation'],info['projection_active'],real_tuple(np.sum(state.B,axis=1)))
                items.append(item);self.records.append({'case':first.name,'n':n,'N':p.N,'D':cfg.delay_steps,'theta_before':item.theta_before,
                    'theta_after':item.theta_after,'decoded_input_innovation':encoded(innovation),'component_errors':dict(item.component_errors),
                    'pre_violation':item.pre_violation,'projection_active':item.projection_active,'row_sums':item.row_sums,
                    'independent_expected_trace_before_import':True,'rng_unchanged':True,'independent_history_storage':True})
            self.observed[first.name]=tuple(items)
        require(unchanged==repr(self.traces),'Immutable independent expectations changed')
    def pairs(self):
        for trace in self.traces:
            obs=self.observed[trace.initial.name]
            for n in range(STEPS-1):
                for i in range(trace.initial.p.N):
                    for j in range(trace.initial.p.N):yield trace,obs,n,i,j


def suite(context):
    class PhaseContract(unittest.TestCase):
        def test_01_seven_complete_traces(self):context.run_traces()
        def test_02_startup_has_zero_delayed_increment(self):
            count=0
            for trace,obs,n,i,j in context.pairs():
                if n<round(trace.initial.p.tau/trace.initial.p.dt):
                    close(phasor(trace.frames[n].increment[i]),obs[n+1].innovation[i][j]/obs[n].innovation[i][j],'startup_factor');count+=1
            require(count==157,'Startup inventory mismatch')
            trace=next(t for t in context.traces if t.initial.name=='free_drift_N1_D3')
            for n,item in enumerate(context.observed[trace.initial.name]):
                close(phasor(-max(0,3-n)*0.125),item.innovation[0][0],'N1_frozen_prehistory_not_drifting')
            context.stats['startup_coordinates']=count
        def test_03_first_live_read_is_n_equals_D(self):
            count=0;nonzero=0.0
            for trace,obs,n,i,j in context.pairs():
                if n==round(trace.initial.p.tau/trace.initial.p.dt):
                    close(phasor(drift(trace,n,i,j)),obs[n+1].innovation[i][j]/obs[n].innovation[i][j],'first_live_factor')
                    nonzero=max(nonzero,error(phasor(drift(trace,n,i,j)),phasor(trace.frames[n].increment[i]),'nonvacuity'));count+=1
            require(count==62 and nonzero>MIN_WITNESS,'First-live witness vacuous/incomplete')
            context.stats.update(first_live_coordinates=count,first_live_versus_extra_delay_difference=nonzero)
        def test_04_later_live_uses_aged_increment(self):
            count=0
            for trace,obs,n,i,j in context.pairs():
                if n>round(trace.initial.p.tau/trace.initial.p.dt):
                    close(phasor(drift(trace,n,i,j)),obs[n+1].innovation[i][j]/obs[n].innovation[i][j],'later_live_factor');count+=1
            require(count==215,'Later-live inventory mismatch');context.stats['later_live_coordinates']=count
        def test_05_windings_and_valid_representative_phasor(self):
            positive=negative=multiple=0;maximum_raw=0.0;maximum_phasor=0.0
            for trace in context.traces:
                for n,item in enumerate(context.observed[trace.initial.name]):
                    frame=trace.frames[n]
                    for i,k in enumerate(frame.windings):
                        raw=item.theta_after[i]-item.theta_before[i];u=frame.increment[i]
                        close(u-math.tau*k,raw,'integer_winding_residual')
                        maximum_phasor=max(maximum_phasor,close(phasor(u),phasor(raw),'representative_phasor_positive'))
                        positive+=k>0;negative+=k<0;multiple+=abs(k)>1;maximum_raw=max(maximum_raw,abs(raw-u))
            require(positive>0 and negative>0 and multiple>0 and maximum_raw>math.tau,'Winding probes vacuous')
            context.winding_stats={'positive_windings':positive,'negative_windings':negative,'multiple_turn_windings':multiple,
                                   'maximum_raw_representative_increment_discrepancy':maximum_raw,'maximum_valid_representative_phasor_error':maximum_phasor,
                                   'representative_difference_phasor_is_valid_not_a_wrong_model':True}
        def test_06_chord_and_capacity_specialization(self):
            tight=0;maximum_excess=0.0;maximum_factor=0.0
            for trace,obs,n,i,j in context.pairs():
                v=drift(trace,n,i,j);z=obs[n].innovation[i][j];zn=obs[n+1].innovation[i][j]
                factor=zn/z;delta=close(phasor(v),factor,'input_ratio_factor');maximum_factor=max(maximum_factor,delta)
                chord=abs(zn-z);bound=abs(v);cap=capacity_bound(trace,n,i,j)
                if chord>bound+ABS_TOL:raise ContractMismatch('chord_bound',bound,chord,chord-bound)
                if bound>cap+ABS_TOL:raise ContractMismatch('capacity_specialization',cap,bound,bound-cap)
                maximum_excess=max(maximum_excess,chord-bound);tight+=chord>MIN_WITNESS and bound<2.0
                context.ratios.append({'case':trace.initial.name,'n':n,'i':i,'j':j,'startup':n<round(trace.initial.p.tau/trace.initial.p.dt),
                    'signed_increment':v,'expected_factor':[phasor(v).real,phasor(v).imag],
                    'observed_factor':[factor.real,factor.imag],'component_error':delta,'observed_chord':chord,'signed_increment_bound':bound,
                    'paper_capacity_bound':cap})
            for trace in context.traces:
                c=(trace.initial.p.a-trace.initial.p.delta)/trace.initial.p.q
                if any(row>c+ABS_TOL for item in context.observed[trace.initial.name] for row in item.row_sums):raise ContractMismatch('post_gate_capacity',c,'exceeded')
            require(tight>0 and len(context.ratios)==434,'Chord checks vacuous/incomplete')
            context.maximum_ratio_error=maximum_factor;context.stats.update(nonzero_chords_with_bound_below_two=tight,maximum_one_sided_chord_excess=maximum_excess)
        def test_07_absolute_offset_and_valid_ratio_cancellation(self):
            maximum_absolute=maximum_ratio=0.0
            for trace,obs,n,i,j in context.pairs():
                f=trace.frames[n];g=trace.frames[n+1]
                wrong0=input_phasor(f.case,f.case.history[0],True)[i][j];wrong1=input_phasor(g.case,g.case.history[0],True)[i][j]
                maximum_absolute=max(maximum_absolute,error(f.input_phasor[i][j],wrong0,'omitted_offset'))
                maximum_ratio=max(maximum_ratio,close(phasor(drift(trace,n,i,j)),wrong1/wrong0,'offset_ratio_cancellation_positive'))
            require(maximum_absolute>MIN_WITNESS,'Absolute offset probe vacuous')
            context.stats.update(omitted_offset_absolute_difference=maximum_absolute,offset_cancellation_ratio_error=maximum_ratio,
                                 constant_offset_ratio_invariance_is_valid_not_a_wrong_model=True)
        def test_08_new_gated_B_storage_and_rng(self):
            trace=next(t for t in context.traces if t.initial.name=='active_D2');frame=trace.frames[0]
            require(frame.prediction.pre_violation and frame.prediction.projection_active,'Forcing gate probe inactive')
            for name in ('old_B_increment','unprojected_B_increment'):
                require(error(phasor(drift(trace,0,0,1)),phasor(drift(trace,0,0,1,name)),name)>MIN_WITNESS,'Vacuous gated forcing control')
            require(len(context.records)==56 and all(r['rng_unchanged'] and r['independent_history_storage'] for r in context.records),'Storage/RNG incomplete')
        def test_09_C_input_is_pre_phase_and_exact_inventory(self):
            trace=next(t for t in context.traces if t.initial.name=='active_D2')
            require(error(trace.frames[0].input_phasor[0][1],trace.frames[1].input_phasor[0][1],'C_timing')>MIN_WITNESS,'C timing probe vacuous')
            require(context.calls==56 and len(context.records)==56,'Unexpected source advance count')
            require(sum(len(item.innovation)**2 for values in context.observed.values() for item in values)==496,'Input coordinate inventory mismatch')
    return unittest.defaultTestLoader.loadTestsFromTestCase(PhaseContract)


def wrong_models(traces):
    out=[]
    for name,field,expected,wrong,witness in control_witnesses(traces):
        try:close(expected,wrong,field)
        except ContractMismatch as problem:
            require(problem.field==field and problem.delta is not None and problem.delta>MIN_WITNESS,'Wrong control mechanism/tiny witness')
            out.append({'model':name,'detected':True,'intended_field':field,'detected_field':problem.field,'component_difference':problem.delta,
                        'witness':witness,'setup_errors_credited':0})
        else:raise RuntimeError('Undetected wrong model: '+name)
    require(len(out)==10,'Wrong-model inventory mismatch');return out


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--kind',choices=('common','wrong_models'),required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        # NO acquired engine import until ALL immutable math expectations are complete.
        traces=prepare_traces();design=design_record(traces);save(args.output/'preexecution_design.json',design);manifest=verify(args.source)
        require(all(r['component_difference']>MIN_WITNESS for r in design['ten_fixed_control_witnesses']),'Vacuous control before target')
        if args.kind=='wrong_models':
            records=wrong_models(traces);save(args.output/'wrong_models.json',records)
            value={'kind':'wrong_models','optimized_python':not __debug__,'detected':len(records),'records':records,'actual_engine_advances':0,
                   'actual_engine_imported':False,'setup_errors_credited':0,'source_files_unchanged':len(manifest['modules']),'metadata_files_unchanged':len(manifest['metadata'])}
        else:
            context=Context(load(args.source),traces);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(context));print(stream.getvalue(),end='')
            save(args.output/'advance_observations.json',context.records);save(args.output/'input_ratio_observations.json',context.ratios)
            value={'kind':'common','optimized_python':not __debug__,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                   'skipped':len(result.skipped),'actual_engine_advances':context.calls,'source_initializations':0,'source_cases':len(traces),
                   'input_complex_coordinates':sum(len(item.innovation)**2 for values in context.observed.values() for item in values),
                   'adjacent_complex_coordinates':len(context.ratios),'maximum_component_error':max((v for r in context.records for v in r['component_errors'].values()),default=0),
                   'maximum_ratio_component_error':context.maximum_ratio_error,'age_and_chord_stats':context.stats,'winding_stats':context.winding_stats,
                   'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,'source_files_unchanged':len(verify(args.source)['modules']),
                   'metadata_files_unchanged':len(manifest['metadata']),'independent_expected_trace_built_before_import':True,
                   'explicit_compute_R_calls_by_harness':0,'actual_full_engine_import_no_function_copy_replacement_or_edit':True,
                   'production_simulation_baseline_CLI_or_certificate_called':False,'immutable_cases_rng_and_history_ownership_verified':True}
            if not result.wasSuccessful():save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 1
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
