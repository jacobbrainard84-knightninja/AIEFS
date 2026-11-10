"""Independent scalar specification of the synthetic non-shuffled primitive.
No NumPy, acquired module, RNG, engine helper or engine-derived expected output.
Immutable tuple inputs. Fixed finite absolute comparison tolerance elsewhere.
"""
from dataclasses import dataclass, replace
import cmath
import math

ABS_TOL=5e-13
MIN_CONTROL_WITNESS=1e-7
PROJECTION_ACTIVE_TOL=1e-14  # reviewed source diagnostic threshold, NOT ABS_TOL

@dataclass(frozen=True)
class Parameters:
    N:int
    dt:float
    tau:float
    omega:tuple[float,...]
    a:float=1.0
    q:float=1.5
    delta:float=0.1
    eta:float=0.2
    mu:float=0.05
    gamma:float=0.2
    T_window:float=0.5
    B_c:float=0.0
    B_init_scale:float=0.0
    scale_epsilon:float=1e-12

@dataclass(frozen=True)
class Case:
    name:str
    p:Parameters
    theta:tuple[float,...]
    B:tuple[tuple[float,...],...]
    C:tuple[tuple[complex,...],...]
    history:tuple[tuple[float,...],...]

@dataclass(frozen=True)
class Prediction:
    theta:tuple[float,...]
    B:tuple[tuple[float,...],...]
    C:tuple[tuple[complex,...],...]
    history:tuple[tuple[float,...],...]
    R:tuple[tuple[float,...],...]
    B_unprojected:tuple[tuple[float,...],...]
    minimum_raw_offdiagonal_proposal:float
    pre_violation:bool
    projection_active:bool
    g_min_pre:float
    g_min:float


def matrix(n,function):return tuple(tuple(function(i,j) for j in range(n)) for i in range(n))


def reference(case,wrong=None):
    """One scalar step; wrong chooses ONE explicitly named incorrect model.
    Wrong models are oracle falsifiers, not modifications of frozen source.
    """
    p=case.p;n=p.N
    delayed=case.history[-1] if wrong=='newest' else case.history[1] if wrong=='second_oldest' else case.history[0]
    alpha=math.exp(-p.dt/p.T_window)
    def new_c(i,j):
        offset=p.omega[i] if wrong=='individual_frequency' else (p.omega[i]+p.omega[j])/2.0
        z=cmath.exp(1j*(case.theta[i]-delayed[j]-offset*p.tau))
        return alpha*case.C[i][j]+(1.0-alpha)*z
    C=matrix(n,new_c)
    if wrong=='old_C_for_R':R=matrix(n,lambda i,j:0.0 if i==j else (abs(case.C[i][j])+abs(case.C[j][i]))/2.0)
    elif wrong=='symmetrize_C_first':R=matrix(n,lambda i,j:0.0 if i==j else abs((C[i][j]+C[j][i])/2.0))
    else:R=matrix(n,lambda i,j:0.0 if i==j else (abs(C[i][j])+abs(C[j][i]))/2.0)
    raw=matrix(n,lambda i,j:case.B[i][j]+p.dt*((p.eta+p.mu)*R[i][j]-p.mu-p.gamma*case.B[i][j]))
    clipped=matrix(n,lambda i,j:max(raw[i][j],0.0))
    before=matrix(n,lambda i,j:0.0 if i==j else (clipped[i][j]+clipped[j][i])/2.0)
    rows=tuple(sum(row) for row in before)
    pre=min(p.a-p.q*row for row in rows);violation=pre<p.delta
    if violation or wrong=='unconditional_gate':
        capacity=(p.a-p.delta)/p.q
        scales=tuple(min(1.0,capacity/(row+p.scale_epsilon)) for row in rows)
        B=matrix(n,lambda i,j:0.0 if i==j else before[i][j]*min(scales[i],scales[j]))
    else:B=before
    correction=math.sqrt(sum((B[i][j]-before[i][j])**2 for i in range(n) for j in range(n)))
    phase_B=case.B if wrong=='old_B_for_phase' else before if wrong=='unprojected_B_for_phase' else B
    def next_theta(i):
        coupling=sum(phase_B[i][j]*math.sin((case.theta[i]-delayed[j]) if wrong=='reversed_sine' else (delayed[j]-case.theta[i])) for j in range(n))
        return (case.theta[i]+p.dt*(p.omega[i]+coupling))%math.tau
    theta=tuple(next_theta(i) for i in range(n))
    fresh=case.theta if wrong=='append_old_theta' else theta
    history=case.history[1:]+(fresh,)
    offdiag=[raw[i][j] for i in range(n) for j in range(n) if i!=j]
    return Prediction(theta,B,C,history,R,before,min(offdiag,default=0.0),violation,
                      correction>PROJECTION_ACTIVE_TOL,pre,min(p.a-p.q*sum(row) for row in B))


def base_case(name='inactive_D1',d=1,active=False):
    theta=(0.31,1.27,4.13);oldest=(5.91,0.81,2.24)
    history=tuple(tuple(oldest[j]+(theta[j]-oldest[j])*k/d for j in range(3)) for k in range(d))+(theta,)
    return Case(name,Parameters(3,0.125,d*0.125,(0.5,1.0,1.5),eta=3.0 if active else 0.2),theta,
                ((0.0,0.08,0.23),(0.08,0.0,0.32),(0.23,0.32,0.0)),
                ((0.17+0.23j,-0.42+0.18j,0.11-0.56j),
                 (0.37-0.25j,-0.2+0.09j,0.61+0.13j),
                 (-0.08+0.33j,-0.48-0.27j,0.26-0.19j)),history)


def drift_case(d=1):
    return Case('dyadic_D'+str(d),Parameters(1,0.125,d*0.125,(1.0,),eta=0.0,mu=0.0,gamma=0.0),
                (0.25,),((0.0,),),((0j,),),tuple((0.25,) for _ in range(d+1)))


def cases():
    inactive=base_case();active=base_case('active_D2',2,True);active3=base_case('active_D3',3,True)
    zero=base_case('zero_C_new_drive_D2',2);zero=replace(zero,C=matrix(3,lambda i,j:0j))
    wrap=base_case('phase_wrap_D1');wrap=replace(wrap,theta=(math.tau-0.015,0.011,6.27),
                                               history=(wrap.history[0],(math.tau-0.015,0.011,6.27)))
    boundary=Case('exact_capacity_N2',Parameters(2,0.125,0.125,(0.5,1.0),q=1.0,delta=0.5,
                                               eta=0.0,mu=0.0,gamma=0.0,scale_epsilon=0.01),
                  (0.31,1.27),((0.0,0.5),(0.5,0.0)),((0j,0j),(0j,0j)),((5.91,0.81),(0.31,1.27)))
    clipped=base_case('negative_proposal_clipped',2);clipped=replace(clipped,p=replace(clipped.p,eta=0.0,mu=8.0,gamma=8.0),C=matrix(3,lambda i,j:0j))
    theta4=(0.31,1.27,4.13,2.71);old4=(5.91,0.81,2.24,4.61)
    directed=Case('directed_C_N4_D4',Parameters(4,0.125,0.5,(0.5,1.0,1.5,1.25),eta=3.0),theta4,
                  matrix(4,lambda i,j:0.0 if i==j else 0.04*(1+i+j)),
                  matrix(4,lambda i,j:complex(0.11*(i+1)-0.07*j,0.09*(j+1)-0.13*i)),
                  tuple(tuple(old4[j]+(theta4[j]-old4[j])*k/4 for j in range(4)) for k in range(4))+(theta4,))
    return (inactive,active,active3,zero,wrap,boundary,clipped,directed,drift_case())


def shadow_after(case,prediction):
    return replace(case,theta=prediction.theta,B=prediction.B,C=prediction.C,history=prediction.history)


def control_cases():
    active=base_case('fixed_active_control',2,True)
    return tuple((name,active if name!='unconditional_gate' else cases()[5],field) for name,field in (
        ('newest','C'),('second_oldest','C'),('individual_frequency','C'),('old_C_for_R','R_physical'),
        ('symmetrize_C_first','R_physical'),('old_B_for_phase','theta'),('unprojected_B_for_phase','theta'),
        ('reversed_sine','theta'),('append_old_theta','history'),('alias_new_theta','storage_ownership'),
        ('unconditional_gate','B')))
