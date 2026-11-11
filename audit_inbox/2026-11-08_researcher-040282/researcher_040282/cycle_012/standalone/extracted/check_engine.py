"""Nine012 source/causal tracking methods +ten explicit independent wrong models.
All expectations BEFORE acquired import. No source mutation, pre-call compute_R,
production/baseline/S01/CLI/certificate or setup error credited as a falsifier.
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
from tracking_contract import (ABS_TOL,MIN_WITNESS,STEPS,alpha,budget,complex_unroll,controls,delta,design_record,
                               error as expected_error,phasor,prepare_traces,signed_drift)

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
    C_before:tuple
    C_after:tuple
    z:tuple
    decoded_innovation:tuple|None
    R:tuple
    theta_before:tuple
    theta_after:tuple
    row_sums:tuple
    errors:tuple
    pre_violation:bool
    projection_active:bool


def snapshot_input(theta,oldest,omega,tau):
    return tuple(tuple(phasor(theta[i]-oldest[j]-(omega[i]+omega[j])/2*tau) for j in range(len(theta))) for i in range(len(theta)))


def packed(z):return [float(z.real),float(z.imag)]


class Context:
    def __init__(self,module,traces,cells):
        self.module=module;self.traces=traces;self.cells=cells;self.lookup={(c.case,c.n,c.i,c.j):c for c in cells}
        self.observed={};self.records=[];self.tracking=[];self.calls=0;self.stats={};self.recurrence_errors={}
    def run_traces(self):
        saved=repr((self.traces,self.cells))
        for trace in self.traces:
            first=trace.initial;cfg=self.module.ModelConfig(**asdict(first.p));cfg.validate();a=alpha(trace)
            close(a,cfg.alpha,'configuration_alpha');require(cfg.delay_steps>=1 and cfg.delay_steps*cfg.dt==cfg.tau,'Invalid planned exact delay')
            state=self.module.DynamicState(np.array(first.theta),np.array(first.B),np.array(first.C),[np.array(h) for h in first.history])
            rng=np.random.default_rng(1040282);rng_before=json.dumps(rng.bit_generator.state,sort_keys=True);items=[]
            for n,frame in enumerate(trace.frames):
                state.validate(cfg);ownership(state)
                for field,want,got in (('pre_C',frame.case.C,state.coherence_acc),('pre_theta',frame.case.theta,state.theta),('pre_B',frame.case.B,state.B),('pre_history',frame.case.history,state.history)):
                    close(want,got,field)
                old_c=state.coherence_acc.copy();theta=real_tuple(state.theta);oldest=real_tuple(state.history[0])
                z=snapshot_input(theta,oldest,cfg.omega,cfg.tau);errors={'input_argument_formula':close(frame.input_phasor,z,'input_argument_formula')}
                # Only target call. ALL expected traces/cells already computed before module import.
                self.calls+=1;physical,driver,info=self.module.advance_state(state,cfg,rng,shuffle_driver=False)
                state.validate(cfg);ownership(state);prediction=frame.prediction
                for field,want,got in (('C',prediction.C,state.coherence_acc),('B',prediction.B,state.B),('theta',prediction.theta,state.theta),('history',prediction.history,state.history),('R_physical',prediction.R,physical),('R_driver',prediction.R,driver)):
                    errors[field]=close(want,got,field)
                for flag in ('pre_violation','projection_active'):
                    if type(info[flag]) is not bool or info[flag]!=getattr(prediction,flag):raise ContractMismatch(flag,getattr(prediction,flag),info[flag])
                for field in ('g_min_pre','g_min'):errors[field]=close(getattr(prediction,field),info[field],field)
                if np.any(state.theta<0) or np.any(state.theta>=math.tau):raise ContractMismatch('phase_range','[0,2pi)',state.theta.tolist())
                if not np.array_equal(state.B,state.B.T) or np.any(state.B<0) or np.any(np.diag(state.B)!=0):raise ContractMismatch('B_structure','nonnegative/symmetric/diag0','bad')
                if rng_before!=json.dumps(rng.bit_generator.state,sort_keys=True):raise ContractMismatch('RNG','unchanged','changed')
                decoded=None
                if a<1:
                    require(1-a>=.05,'Unplanned ill-conditioned innovation extraction')
                    decoded=complex_matrix((state.coherence_acc-cfg.alpha*old_c)/(1-cfg.alpha))
                    errors['decoded_C_innovation']=close(frame.input_phasor,decoded,'decoded_C_innovation')
                else:
                    require(a==1 and cfg.alpha==1,'Unplanned alpha endpoint')
                    if not np.array_equal(old_c,state.coherence_acc):raise ContractMismatch('alpha1_no_update','C unchanged','changed')
                item=Observation(complex_matrix(old_c),complex_matrix(state.coherence_acc),z,decoded,tuple(real_tuple(r) for r in physical),theta,real_tuple(state.theta),real_tuple(np.sum(state.B,axis=1)),tuple(sorted(errors.items())),info['pre_violation'],info['projection_active'])
                items.append(item);self.records.append({'case':first.name,'n':n,'N':first.p.N,'D':cfg.delay_steps,'alpha':a,'C_before':encoded(item.C_before),'C_after':encoded(item.C_after),
                    'input_from_observed_arguments':encoded(z),'decoded_C_innovation':None if decoded is None else encoded(decoded),
                    'input_channel':'formula_only_beta0_unidentifiable_in_C' if decoded is None else 'formula_and_actual_C_innovation',
                    'R_physical':item.R,'theta_before':theta,'theta_after':item.theta_after,'row_sums':item.row_sums,'component_errors':dict(item.errors),
                    'pre_violation':item.pre_violation,'projection_active':item.projection_active,'all_expectations_before_import':True,'rng_unchanged':True,'independent_history_storage':True})
            self.observed[first.name]=tuple(items)
        require(saved==repr((self.traces,self.cells)),'Immutable independent traces/budgets changed')
    def all_cells(self):
        for trace in self.traces:
            obs=self.observed[trace.initial.name]
            for n in range(STEPS):
                for i in range(trace.initial.p.N):
                    for j in range(trace.initial.p.N):yield trace,obs,n,i,j,self.lookup[(trace.initial.name,n,i,j)]


def current_error(item,i,j):return item.C_before[i][j]-item.z[i][j]


def suite(context):
    class TrackingContract(unittest.TestCase):
        def test_01_six_full_independent_traces(self):context.run_traces()
        def test_02_exact_causal_tracking_error(self):
            count=0;maximum=0.0
            for trace,obs,n,i,j,cell in context.all_cells():
                if n<STEPS-1:
                    got=current_error(obs[n+1],i,j);rhs=alpha(trace)*current_error(obs[n],i,j)-(obs[n+1].z[i][j]-obs[n].z[i][j])
                    residual=close(rhs,got,'causal_relational_error');close(cell.next_error_rhs,got,'independent_causal_prediction')
                    context.recurrence_errors[(trace.initial.name,n+1,i,j)]=residual;count+=1;maximum=max(maximum,residual)
            require(count==333,'Recurrence inventory mismatch');context.stats.update(adjacent_causal_coordinates=count,maximum_causal_component_residual=maximum)
        def test_03_complex_unroll_and_two_budgets(self):
            count=0;maximum=0.0;small_nonzero=0;max_excess=0.0
            for trace,obs,n,i,j,cell in context.all_cells():
                got=current_error(obs[n],i,j);close(cell.tracking_error,got,'independent_current_error')
                residual=close(cell.complex_unroll,got,'independent_complex_unroll');maximum=max(maximum,residual)
                norm=abs(got)
                if norm>cell.input_budget+ABS_TOL:raise ContractMismatch('input_variation_budget',cell.input_budget,norm,norm-cell.input_budget)
                if cell.input_budget>cell.phase_budget+ABS_TOL:raise ContractMismatch('phase_composition_budget',cell.phase_budget,cell.input_budget,cell.input_budget-cell.phase_budget)
                max_excess=max(max_excess,norm-cell.input_budget);small_nonzero+=norm>MIN_WITNESS and cell.phase_budget<2
                context.tracking.append({'case':trace.initial.name,'n':n,'i':i,'j':j,'alpha':alpha(trace),'observed_current_error':packed(got),
                    'expected_current_error':packed(cell.tracking_error),'expected_complex_unroll':packed(cell.complex_unroll),'unroll_component_error':residual,
                    'observed_error_norm':norm,'input_variation_budget':cell.input_budget,'phase_increment_budget':cell.phase_budget,
                    'reported_R_bound':cell.reported_R_bound,'consumed_input_error':packed(obs[n].C_after[i][j]-obs[n].z[i][j]),
                    'expected_consumed_error':packed(cell.consumed_error),'causal_residual_from_previous':context.recurrence_errors.get((trace.initial.name,n,i,j))})
                count+=1
            require(count==370 and small_nonzero>0,'Budget checks vacuous/incomplete');context.stats.update(tracking_coordinates=count,maximum_unroll_component_residual=maximum,
                nonzero_tracking_bounds_below_two=small_nonzero,maximum_one_sided_input_budget_excess=max_excess)
        def test_04_consumed_input_is_not_next_input(self):
            maximum=0.0;count=0
            for trace,obs,n,i,j,cell in context.all_cells():
                got=obs[n].C_after[i][j]-obs[n].z[i][j];rhs=alpha(trace)*current_error(obs[n],i,j)
                maximum=max(maximum,close(rhs,got,'consumed_current_error'));close(cell.consumed_error,got,'independent_consumed_error');count+=1
            require(count==370,'Consumed-error count differs');context.stats.update(consumed_input_coordinates=count,maximum_consumed_component_residual=maximum)
        def test_05_startup_and_first_live_phase_budget(self):
            startup=live=first=0
            for trace,obs,n,i,j,cell in context.all_cells():
                if n==STEPS-1:continue
                factor=obs[n+1].z[i][j]/obs[n].z[i][j];close(cell.phase_factor,factor,'phase_increment_factor')
                d=round(trace.initial.p.tau/trace.initial.p.dt)
                if n<d:startup+=1
                else:live+=1
                first+=n==d
            require((startup,live,first)==(115,218,37),'Startup/live inventory differs');context.stats.update(startup_adjacent_coordinates=startup,live_adjacent_coordinates=live,first_live_coordinates=first)
        def test_06_constant_input_tail_and_alpha1(self):
            stable=[];endpoint=None
            for trace in context.traces:
                if trace.initial.p.N!=1:continue
                d=round(trace.initial.p.tau/trace.initial.p.dt);obs=context.observed[trace.initial.name];a=alpha(trace)
                for n in range(d,STEPS):
                    close(1+0j,obs[n].z[0][0],'N1_stationary_tail_input')
                    close(a**(n-d)*current_error(obs[d],0,0),current_error(obs[n],0,0),'stationary_tail_error_decay')
                if a<1:stable.append({'case':trace.initial.name,'first_tail_error':abs(current_error(obs[d],0,0)),'last_tail_error':abs(current_error(obs[-1],0,0))})
                else:
                    require(a==1 and all(item.decoded_innovation is None for item in obs),'Alpha1 channel/dynamics mismatch')
                    require(all(item.C_before==item.C_after==obs[0].C_before for item in obs),'Alpha1 C not EXACTLY unchanged')
                    endpoint=abs(current_error(obs[-1],0,0));require(endpoint>.8,'Alpha1 nondecay witness vacuous')
            require(len(stable)==2 and all(x['last_tail_error']<x['first_tail_error']-MIN_WITNESS for x in stable) and endpoint is not None,'Tail checks incomplete/vacuous')
            context.stats.update(alpha_less_one_stationary_tails=stable,rounded_alpha1_tail_error=endpoint,alpha1_C_exactly_constant=True,alpha1_not_strict_contraction=True)
        def test_07_reported_R_is_after_C_and_enveloped(self):
            off=diag=tight=0;maximum_excess=0.0
            for trace,obs,n,i,j,cell in context.all_cells():
                got=obs[n].R[i][j]
                if i==j:
                    if got!=0.0:raise ContractMismatch('reported_R_diagonal',0,got)
                    diag+=1
                else:
                    residual=abs(got-1);maximum_excess=max(maximum_excess,residual-cell.reported_R_bound)
                    if residual>cell.reported_R_bound+ABS_TOL:raise ContractMismatch('reported_R_envelope',cell.reported_R_bound,residual,residual-cell.reported_R_bound)
                    off+=1;tight+=residual>MIN_WITNESS and cell.reported_R_bound<1 and abs(residual-cell.reported_R_bound)<=ABS_TOL
            require((off,diag)==(240,130) and tight>0,'R bound incomplete/vacuous');context.stats.update(reported_R_offdiag_bound_coordinates=off,reported_R_exact_diag_coordinates=diag,
                tight_nonzero_reported_R_bounds_below_one=tight,maximum_one_sided_R_bound_excess=maximum_excess)
        def test_08_nonzero_C_gate_windings_and_decoder_channels(self):
            decoded=endpoint=positive=negative=multiple=active=0
            for trace in context.traces:
                active+=trace.frames[0].prediction.projection_active
                for n,item in enumerate(context.observed[trace.initial.name]):
                    amount=trace.initial.p.N**2
                    if item.decoded_innovation is None:endpoint+=amount
                    else:decoded+=amount
                    for k in trace.frames[n].windings:positive+=k>0;negative+=k<0;multiple+=abs(k)>1
            require((decoded,endpoint)==(360,10) and active==3 and positive>0 and negative>0 and multiple>0,'Nonvacuity/channel inventory mismatch')
            context.stats.update(decoded_C_innovation_coordinates=decoded,alpha1_formula_only_input_coordinates=endpoint,first_active_gate_cases=active,
                positive_windings=positive,negative_windings=negative,multiple_turn_windings=multiple,beta0_divisions=0,source_alpha0_configs=0)
        def test_09_counts_preservation_and_no_extra_source_calls(self):
            require(context.calls==len(context.records)==60 and len(context.tracking)==370 and len(context.cells)==370,'Actual source/expected table counts differ')
            require(all(x['all_expectations_before_import'] and x['rng_unchanged'] and x['independent_history_storage'] for x in context.records),'Preservation proof incomplete')
    return unittest.defaultTestLoader.loadTestsFromTestCase(TrackingContract)


def wrong_models(traces):
    out=[]
    for row in controls(traces):
        try:
            if row['kind']=='upper_bound':
                violation=row['expected']-row['wrong']
                if violation>ABS_TOL:raise ContractMismatch(row['field'],'upper bound '+str(row['wrong']),row['expected'],violation)
            else:close(row['expected'],row['wrong'],row['field'])
        except ContractMismatch as problem:
            require(problem.field==row['field'] and problem.delta is not None and problem.delta>MIN_WITNESS,'Wrong mechanism/tolerance fuzz: '+row['model'])
            out.append({'model':row['model'],'kind':row['kind'],'detected':True,'intended_field':row['field'],'detected_field':problem.field,'numeric_witness':problem.delta,
                        'case':row['case'],'n':row['n'],'i':row['i'],'j':row['j'],'setup_errors_credited':0})
        else:raise RuntimeError('Undetected incorrect model: '+row['model'])
    require(len(out)==10,'Wrong-model count differs');return out


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--kind',choices=('common','wrong_models'),required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        from tracking_contract import prepare_expectations
        traces=prepare_traces();cells=prepare_expectations(traces);design=design_record(traces);save(args.output/'preexecution_design.json',design)
        require(len(cells)==370 and all(x['intended_witness']>MIN_WITNESS for x in design['ten_wrong_models']),'Preimport expectations/witness invalid')
        manifest=verify(args.source)
        if args.kind=='wrong_models':
            records=wrong_models(traces);save(args.output/'wrong_models.json',records)
            value={'kind':'wrong_models','optimized_python':not __debug__,'detected':len(records),'records':records,'actual_engine_advances':0,'actual_engine_imported':False,
                   'setup_errors_credited':0,'source_files_unchanged':len(manifest['modules']),'metadata_files_unchanged':len(manifest['metadata'])}
        else:
            context=Context(load(args.source),traces,cells);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(context));print(stream.getvalue(),end='')
            save(args.output/'advance_observations.json',context.records);save(args.output/'tracking_observations.json',context.tracking)
            value={'kind':'common','optimized_python':not __debug__,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
                   'actual_engine_advances':context.calls,'source_initializations':0,'source_cases':len(traces),'precomputed_tracking_cells':len(cells),
                   'maximum_component_error':max((v for r in context.records for v in r['component_errors'].values()),default=0.0),'tracking_stats':context.stats,
                   'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,'all_expected_traces_and_derived_budgets_before_import':True,
                   'explicit_compute_R_calls_by_harness':0,'source_files_unchanged':len(verify(args.source)['modules']),'metadata_files_unchanged':len(manifest['metadata']),
                   'actual_full_engine_import_no_function_copy_replacement_or_edit':True,'production_simulation_baseline_CLI_or_certificate_called':False,
                   'immutable_inputs_expected_tables_rng_and_history_ownership_verified':True,'alpha1_not_decoded_or_assumed_strictly_less_than_one':True}
            if not result.wasSuccessful():save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 1
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
