# Auditor's own independent check of Arena cycle 8-10 claims, using main's engine only.
import sys, numpy as np
sys.path.insert(0, '.')  # run from a checkout of main 871417d
import aief_experiment_engine_v1 as E
def cfg(N,eta,omega=1.42833):
    return E.ModelConfig(N=N,dt=.01,tau=.5,omega=(omega,)*N,a=1.0,q=1.5,delta=.05,
        eta=eta,mu=.03,gamma=.015,T_window=17.5,B_c=0.1,B_init_scale=0.1)
def solveOmega(w,K,tau):
    lo,hi=w-K-1,w+K+1
    for _ in range(200):
        m=(lo+hi)/2
        if m-w+K*np.sin(m*tau)>0: hi=m
        else: lo=m
    return (lo+hi)/2
def orbit(N,eta,branch,pert=0.0,steps=1000,seed=0):
    c=cfg(N,eta); m=N-1; C=(c.a-c.delta)/c.q; d=c.delay_steps
    if branch=='interior': b=eta/c.gamma
    else:
        t=1-c.dt*c.gamma; h=c.dt*eta; e=c.scale_epsilon
        A,Bq,Cq=m*t,m*h+e-C*t,-C*h; b=(-Bq+np.sqrt(Bq*Bq-4*A*Cq))/(2*A)
        assert m*(t*b+h)>C
    K=m*b; Om=solveOmega(c.omega[0],K,c.tau)
    hist=[np.full(N,np.mod(k*c.dt*Om,2*np.pi)) for k in range(-d,1)]
    rng=np.random.default_rng(seed)
    th=hist[-1].copy()+pert*rng.standard_normal(N); hist[-1]=th.copy()
    B=np.full((N,N),b); np.fill_diagonal(B,0)
    z=np.exp(1j*(Om-c.omega[0])*c.tau); Cc=np.full((N,N),z,dtype=complex)
    s=E.DynamicState(th,B,Cc,hist); r=np.random.default_rng(0)
    errs=[]; proj=0
    for n in range(1,steps+1):
        _,_,info=E.advance_state(s,c,r); proj+=info['pre_violation']
        ref=np.mod(n*c.dt*Om,2*np.pi)
        dev=np.angle(np.exp(1j*(s.theta-ref)))
        spread=np.angle(np.exp(1j*(s.theta-s.theta.mean())))
        errs.append((np.max(np.abs(dev)),np.max(np.abs(spread)),np.max(np.abs(s.B[~np.eye(N,dtype=bool)]-b))))
    return b,Om,proj,errs,c,K
for br,eta in [('interior',.0005),('projected',.04)]:
    b,Om,proj,errs,c,K=orbit(12,eta,br)
    print(br,'b=%.13f Om=%.11f proj=%d maxphase=%.2e maxB=%.2e Ktau=%.3f'%(b,Om,proj,max(e[0] for e in errs),max(e[2] for e in errs),K*c.tau))
    # cycle 9 polynomial: P(l)=l^(d+1)-(1-a)l^d-a, a=dt K cos(Om tau)
    d=c.delay_steps; a=c.dt*K*np.cos(Om*c.tau)
    P=np.zeros(d+2); P[0]=1; P[1]=-(1-a); P[-1]=-a
    rP=np.abs(np.roots(P)); rP=np.sort(rP)[::-1]
    print('  a=%.5f  P largest |roots|: %s'%(a,np.round(rP[:3],12)))
    # perturbation run (transverse spread)
    _,_,_,e2,_,_=orbit(12,eta,br,pert=1e-6,steps=20000)
    print('  spread after pert 1e-6: step1 %.2e step5000 %.2e step20000 %.2e'%(e2[0][1],e2[4999][1],e2[-1][1]))
