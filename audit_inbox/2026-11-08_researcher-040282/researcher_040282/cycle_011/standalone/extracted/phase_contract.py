"""Independent immutable011 phase-input design. Pure math/cmath, no NumPy/engine.
The010 scalar step is reused explicitly; phase factors use analytic age indices,
not source outputs. All seven full traces are built before the acquired import.
"""
from dataclasses import dataclass,replace
import cmath
import math
from step_contract import Case,Parameters,Prediction,base_case,drift_case,matrix,reference,shadow_after

ABS_TOL=5e-13
MIN_WITNESS=1e-7
STEPS=8

@dataclass(frozen=True)
class Frame:
    case:Case
    prediction:Prediction
    increment:tuple[float,...]
    input_phasor:tuple[tuple[complex,...],...]
    windings:tuple[int,...]

@dataclass(frozen=True)
class Trace:
    initial:Case
    frames:tuple[Frame,...]
    phase_values:tuple[tuple[float,...],...]


def phasor(value):return cmath.exp(1j*value)


def source_cases():
    base=base_case('active_D2',2,True)
    def constant(case):return replace(case,C=matrix(case.p.N,lambda i,j:0j),history=tuple(case.theta for _ in range(round(case.p.tau/case.p.dt)+1)))
    wrap=base_case('positive_wrap_D1',1,True);wrap=replace(wrap,theta=(math.tau-0.015,1.27,4.13))
    d3=base_case('active_D3',3,True)
    theta4=(0.31,1.27,4.13,2.71)
    n4=Case('coupled_N4_D4',Parameters(4,0.125,0.5,(0.5,1.0,1.5,1.25),eta=3.0),theta4,
            matrix(4,lambda i,j:0.0 if i==j else 0.04*(1+i+j)),matrix(4,lambda i,j:0j),())
    negative=replace(base,name='negative_wrap_D2',p=replace(base.p,omega=(-1.0,0.75,1.5)),theta=(0.01,1.27,4.13))
    multi=replace(base,name='multiwrap_D2',p=replace(base.p,omega=(161.0,-143.0,27.0)))
    drift=drift_case(3);drift=replace(drift,name='free_drift_N1_D3',theta=(6.1,))
    return tuple(constant(case) for case in (wrap,base,d3,n4,negative,multi,drift))


def increment(case,prediction,which='new_gated'):
    p=case.p;n=p.N
    B=case.B if which=='old_B' else prediction.B_unprojected if which=='unprojected_B' else prediction.B
    return tuple(p.dt*(p.omega[i]+sum(B[i][j]*math.sin(case.history[0][j]-case.theta[i]) for j in range(n))) for i in range(n))


def input_phasor(case,delayed,omit_offset=False):
    return matrix(case.p.N,lambda i,j:phasor(case.theta[i]-delayed[j]-(0.0 if omit_offset else (case.p.omega[i]+case.p.omega[j])/2.0*case.p.tau)))


def prepare_traces():
    traces=[]
    for initial in source_cases():
        d=round(initial.p.tau/initial.p.dt);shadow=initial;frames=[];values=[initial.theta]
        for n in range(STEPS):
            if shadow.history[0]!=values[max(0,n-d)]:raise RuntimeError('Independent shadow/history-age design disagreement')
            prediction=reference(shadow);u=increment(shadow,prediction)
            z=input_phasor(shadow,values[max(0,n-d)])
            windings=tuple(math.floor((shadow.theta[i]+u[i])/math.tau) for i in range(shadow.p.N))
            frames.append(Frame(shadow,prediction,u,z,windings))
            values.append(prediction.theta);shadow=shadow_after(shadow,prediction)
        traces.append(Trace(initial,tuple(frames),tuple(values)))
    return tuple(traces)


def drift(trace,n,i,j,wrong=None):
    d=round(trace.initial.p.tau/trace.initial.p.dt);current=trace.frames[n].increment[i]
    delayed=0.0 if n<d else trace.frames[n-d].increment[j]
    if wrong=='omit_startup_guard':delayed=trace.frames[max(0,n-d)].increment[j]
    elif wrong=='one_step_early':delayed=0.0 if n+1<d else trace.frames[n+1-d].increment[j]
    elif wrong=='current_delayed_increment':delayed=0.0 if n<d else trace.frames[n].increment[j]
    elif wrong=='one_extra_delay':delayed=0.0 if n<d+1 else trace.frames[n-d-1].increment[j]
    elif wrong=='old_B_increment':current=increment(trace.frames[n].case,trace.frames[n].prediction,'old_B')[i]
    elif wrong=='unprojected_B_increment':current=increment(trace.frames[n].case,trace.frames[n].prediction,'unprojected_B')[i]
    return delayed-current if wrong=='reverse_difference' else current-delayed


def capacity_bound(trace,n,i,j):
    p=trace.initial.p;c=(p.a-p.delta)/p.q;d=round(p.tau/p.dt)
    return p.dt*(abs(p.omega[i])+c) if n<d else p.dt*(abs(p.omega[i]-p.omega[j])+2*c)


def component_difference(a,b):
    if isinstance(a,tuple):return max((component_difference(x,y) for x,y in zip(a,b)),default=0.0)
    if isinstance(a,complex) or isinstance(b,complex):return max(abs(a.real-b.real),abs(a.imag-b.imag))
    return abs(a-b)


def control_witnesses(traces):
    by={trace.initial.name:trace for trace in traces};base=by['active_D2'];multi=by['multiwrap_D2'];out=[]
    specs=(('omit_startup_guard',0),('one_step_early',1),('current_delayed_increment',3),('one_extra_delay',2),
           ('reverse_difference',3),('old_B_increment',0),('unprojected_B_increment',0))
    for name,n in specs:
        expected=phasor(drift(base,n,0,1));wrong=phasor(drift(base,n,0,1,name))
        out.append((name,'factor',expected,wrong,{'case':base.initial.name,'n':n,'i':0,'j':1}))
    case=base.frames[0].case
    out.append(('omit_mean_offset','absolute_input',base.frames[0].input_phasor[0][1],input_phasor(case,case.history[0],True)[0][1],
                {'case':base.initial.name,'n':0,'i':0,'j':1}))
    out.append(('next_step_C_input','absolute_input',base.frames[0].input_phasor[0][1],base.frames[1].input_phasor[0][1],
                {'case':base.initial.name,'n':0,'i':0,'j':1}))
    raw=multi.phase_values[1][0]-multi.phase_values[0][0]
    out.append(('raw_angle_increment','real_increment',multi.frames[0].increment[0],raw,{'case':multi.initial.name,'n':0,'i':0}))
    return tuple(out)


def design_record(traces):
    controls=[{'model':name,'field':field,'component_difference':component_difference(expected,wrong),'witness':witness}
              for name,field,expected,wrong,witness in control_witnesses(traces)]
    coordinates=sum(trace.initial.p.N**2 for trace in traces)
    return {'phase':'Independent scalar design before acquired-engine import/advance; not source observations',
            'cases':[{'name':t.initial.name,'N':t.initial.p.N,'D':round(t.initial.p.tau/t.initial.p.dt),
                      'first_increment':t.frames[0].increment,'first_windings':t.frames[0].windings,
                      'first_pre_violation':t.frames[0].prediction.pre_violation,
                      'first_projection_active':t.frames[0].prediction.projection_active} for t in traces],
            'actual_advances_planned':len(traces)*STEPS,'input_complex_coordinates_planned':coordinates*STEPS,
            'adjacent_complex_coordinates_planned':coordinates*(STEPS-1),
            'startup_adjacent_coordinates_planned':sum(round(t.initial.p.tau/t.initial.p.dt)*t.initial.p.N**2 for t in traces),
            'ten_fixed_control_witnesses':controls,'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,
            'positive_equivalences_not_misclassified_as_mutants':['stored-angle-difference versus unwrapped increment inside phasor',
                                                               'constant mean-frequency offset cancels in adjacent input ratio']}
