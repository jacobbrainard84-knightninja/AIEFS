"""Pure immutable012 tracking oracle. No NumPy or acquired engine import.
Old scalar/phasor definitions reused explicitly; full expectations precede import.
"""
from dataclasses import dataclass,replace
import math
from step_contract import Case,Parameters,base_case,drift_case,matrix,reference,shadow_after
from phase_contract import Frame,increment,input_phasor,phasor

ABS_TOL=5e-13
MIN_WITNESS=1e-7
STEPS=10

@dataclass(frozen=True)
class Trace:
    initial:Case
    frames:tuple[Frame,...]
    phase_values:tuple[tuple[float,...],...]

def alpha(trace):return math.exp(-trace.initial.p.dt/trace.initial.p.T_window)

def cases():
    active=base_case('active_N3_D2',2,True);active=replace(active,theta=(math.tau-.015,1.27,4.13))
    slow=base_case('slow_negative_N3_D3',3,True)
    slow=replace(slow,p=replace(slow.p,omega=(-1.0,.75,1.5),T_window=2.0),theta=(.01,1.27,4.13))
    theta=(.31,1.27,4.13,2.71)
    fast=Case('fast_multiwrap_N4_D4',Parameters(4,.125,.5,(161.0,-143.0,27.0,1.25),eta=3.0,T_window=.125),theta,
              matrix(4,lambda i,j:0.0 if i==j else .04*(1+i+j)),matrix(4,lambda i,j:0j),())
    matched=drift_case(3);matched=replace(matched,name='matched_start_N1_D3',theta=(6.1,),C=((phasor(-.375),),))
    endpoint=drift_case(2);endpoint=replace(endpoint,name='rounded_alpha1_N1_D2',theta=(6.1,),p=replace(endpoint.p,T_window=1e20),C=((.3+.4j,),))
    tail=drift_case(1);tail=replace(tail,name='fast_tail_N1_D1',p=replace(tail.p,T_window=.0625))
    return tuple(replace(c,history=tuple(c.theta for _ in range(round(c.p.tau/c.p.dt)+1))) for c in (active,slow,fast,matched,endpoint,tail))

def prepare_traces():
    out=[]
    for first in cases():
        shadow=first;values=[first.theta];frames=[];d=round(first.p.tau/first.p.dt)
        for n in range(STEPS):
            if shadow.history[0]!=values[max(0,n-d)]:raise RuntimeError('Independent history-age design mismatch')
            prediction=reference(shadow);u=increment(shadow,prediction);z=input_phasor(shadow,values[max(0,n-d)])
            frames.append(Frame(shadow,prediction,u,z,tuple(math.floor((shadow.theta[i]+u[i])/math.tau) for i in range(shadow.p.N))))
            values.append(prediction.theta);shadow=shadow_after(shadow,prediction)
        out.append(Trace(first,tuple(frames),tuple(values)))
    return tuple(out)

def error(trace,n,i,j):return trace.frames[n].case.C[i][j]-trace.frames[n].input_phasor[i][j]
def delta(trace,k,i,j):return trace.frames[k+1].input_phasor[i][j]-trace.frames[k].input_phasor[i][j]
def signed_drift(trace,k,i,j,drifting_prehistory=False):
    d=round(trace.initial.p.tau/trace.initial.p.dt)
    late=trace.frames[max(0,k-d)].increment[j] if drifting_prehistory or k>=d else 0.0
    return trace.frames[k].increment[i]-late

def budget(trace,n,i,j,kind='input'):
    a=alpha(trace)
    def variation(k):
        return abs(delta(trace,k,i,j)) if kind=='input' else abs(signed_drift(trace,k,i,j,kind=='drifting_prehistory'))
    return a**n*abs(error(trace,0,i,j))+sum(a**(n-1-k)*variation(k) for k in range(n))

def complex_unroll(trace,n,i,j,reverse=False):
    a=alpha(trace)
    return a**n*error(trace,0,i,j)-sum(a**(k if reverse else n-1-k)*delta(trace,k,i,j) for k in range(n))

def controls(traces):
    by={x.initial.name:x for x in traces};m=by['matched_start_N1_D3'];active=by['active_N3_D2'];endpoint=by['rounded_alpha1_N1_D2']
    a=alpha(m);d=delta(m,0,0,0);e0=error(m,0,0,0)
    out=[]
    def equality(name,field,trace,n,i,j,want,wrong):
        out.append({'model':name,'kind':'equality','field':field,'case':trace.initial.name,'n':n,'i':i,'j':j,'expected':want,'wrong':wrong})
    def upper(name,trace,n,i,j,wrong):
        out.append({'model':name,'kind':'upper_bound','field':'tracking_envelope','case':trace.initial.name,'n':n,'i':i,'j':j,'expected':abs(error(trace,n,i,j)),'wrong':wrong})
    equality('drift_beta','causal_error',m,1,0,0,error(m,1,0,0),a*e0-(1-a)*d)
    equality('drift_plus','causal_error',m,1,0,0,error(m,1,0,0),a*e0+d)
    f=active.frames[0];aa=alpha(active)
    equality('future_input_update','updated_C',active,0,0,1,f.prediction.C[0][1],aa*f.case.C[0][1]+(1-aa)*active.frames[1].input_phasor[0][1])
    upper('omit_variation',m,1,0,0,a*abs(e0))
    upper('newest_weight_alpha',m,1,0,0,a*abs(d))
    equality('reverse_weights','complex_error_unroll',m,2,0,0,error(m,2,0,0),complex_unroll(m,2,0,0,True))
    upper('omit_initial',active,0,0,1,0.0)
    upper('drifting_prehistory',m,1,0,0,budget(m,1,0,0,'drifting_prehistory'))
    equality('alpha1_forced_decay','stationary_tail_error',endpoint,3,0,0,error(endpoint,3,0,0),.5*error(endpoint,2,0,0))
    old_R=(abs(f.case.C[0][1])+abs(f.case.C[1][0]))/2
    equality('stale_reported_R','reported_R',active,0,0,1,f.prediction.R[0][1],old_R)
    return tuple(out)

def difference(row):
    if row['kind']=='upper_bound':return row['expected']-row['wrong']
    a=row['expected'];b=row['wrong']
    return max(abs(a.real-b.real),abs(a.imag-b.imag)) if isinstance(a,complex) or isinstance(b,complex) else abs(a-b)

def control_design(row):
    return {k:v for k,v in row.items() if k not in ('expected','wrong')}|{'intended_witness':difference(row)}

def design_record(traces):
    return {'phase':'Independent pure math/cmath design before acquired module import/advance',
            'cases':[{'name':x.initial.name,'N':x.initial.p.N,'D':round(x.initial.p.tau/x.initial.p.dt),'alpha':alpha(x),'one_minus_alpha':1-alpha(x),
                      'initial_error_max':max(abs(error(x,0,i,j)) for i in range(x.initial.p.N) for j in range(x.initial.p.N)),
                      'first_windings':x.frames[0].windings,'first_gate_active':x.frames[0].prediction.projection_active,
                      'input_channel':'prestate_formula_only_beta0_no_division' if alpha(x)==1 else 'prestate_formula_and_actual_C_innovation'} for x in traces],
            'actual_advances_planned':60,'input_tracking_complex_coordinates_planned':370,'consumed_input_complex_coordinates_planned':370,
            'adjacent_error_recurrences_planned':333,'startup_adjacent_coordinates_planned':115,'first_live_adjacent_coordinates_planned':37,
            'decoded_C_innovation_coordinates_planned':360,'alpha1_reconstructed_input_coordinates_planned':10,
            'reported_R_offdiag_bound_coordinates_planned':240,'reported_R_diag_zero_coordinates_planned':130,
            'ten_wrong_models':[control_design(r) for r in controls(traces)],'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,
            'alpha0_formal_only_not_source_valid':True,'float_alpha1_source_valid_not_ideal_exp_strictly_less_than_one':True}

@dataclass(frozen=True)
class Cell:
    case:str
    n:int
    i:int
    j:int
    tracking_error:complex
    consumed_error:complex
    complex_unroll:complex
    input_budget:float
    phase_budget:float
    reported_R_bound:float
    next_error_rhs:complex|None
    phase_factor:complex|None
    signed_increment:float|None


def prepare_expectations(traces):
    """All derived budgets/unrolls also completed BEFORE acquired import."""
    out=[]
    for trace in traces:
        a=alpha(trace)
        for n in range(STEPS):
            frame=trace.frames[n]
            for i in range(trace.initial.p.N):
                for j in range(trace.initial.p.N):
                    signed=signed_drift(trace,n,i,j) if n<STEPS-1 else None
                    out.append(Cell(trace.initial.name,n,i,j,error(trace,n,i,j),frame.prediction.C[i][j]-frame.input_phasor[i][j],
                        complex_unroll(trace,n,i,j),budget(trace,n,i,j),budget(trace,n,i,j,'phase'),
                        a*(budget(trace,n,i,j,'phase')+budget(trace,n,j,i,'phase'))/2,
                        a*error(trace,n,i,j)-delta(trace,n,i,j) if n<STEPS-1 else None,
                        phasor(signed) if signed is not None else None,signed))
    return tuple(out)
