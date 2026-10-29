#!/usr/bin/env python3
"""Numerical check of the conditional finite-time support-freezing certificate (REPORT.md, Thm 2).

Self-contained re-implementation of the AIEF-1.4 engine step
(aief_experiment_engine_v1.py:721-845, frozen constants :63-80), using the identical floating-point
expressions. Optionally cross-checked bit-for-bit against the repo engine (imported read-only, no
bytecode written). By default writes only results.json next to this script
(research/freezing/ in the AIEFS repo).

Indexing: B[n] is the weight matrix BEFORE step n; step n computes R[n] from theta[n] and the
delayed phase, then B[n+1] = F(B[n], R[n]).  status[n] = B[n] > B_c.
"""
import sys, json, math, argparse, os
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))            # research/freezing/
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))           # repo root (engine lives here)

N=12; DT=0.01; TAU=0.5
OMEGA0=np.array([1.00,1.02,1.50,2.00,2.01,1.01,1.03,1.51,2.02,2.00,1.00,1.04])
A=1.0; Q=1.5; DELTA=0.05; ETA=0.04; GAMMA=0.015; MU=0.03; BC=0.12; BINIT=0.0005; EPS=1e-12
CAP=(A-DELTA)/Q; D=int(round(TAU/DT)); H=GAMMA*DT
# Audit fix R2: float64 rounding in the B update (~1 ulp per step, /h ~ 1e-13 shift of the fixed point) can break
# the real-arithmetic N bound at tiny margins (OFF margin 1e-13: violation). Only issue a certificate when its
# margin (B_c - U+, x* - B_c, or B_c - f_u) is at least MARGIN_GUARD. The explicit N is for the real-arithmetic map.
MARGIN_GUARD=1e-9
IU=np.triu_indices(N,1); E=len(IU[0])

def simulate(seed, omega=OMEGA0, steps=80000, no_delay=False, R_exo=None, reset_B_at=None):
    TW=25.0/float(np.mean(omega)); alpha=float(np.exp(-DT/TW))
    rng=np.random.default_rng(np.random.SeedSequence(seed).spawn(2)[0])   # engine make_prefix_rng
    th=rng.random(N)*2*np.pi
    B=BINIT*rng.random((N,N)); B=0.5*(B+B.T); np.fill_diagonal(B,0.0)
    z=np.zeros((N,N),complex); hist=[th.copy() for _ in range(D+1)]
    Rs=np.empty((steps,E)); Bs=np.empty((steps+1,E)); lam=np.empty((steps,E)); S=np.empty((steps,N))
    Bs[0]=B[IU]
    tau_eff=0.0 if no_delay else TAU
    for n in range(steps):
        if reset_B_at is not None and n==reset_B_at: B=np.zeros((N,N)); Bs[n]=0.0
        dl=th if no_delay else hist[0]
        dphi=th[:,None]-dl[None,:]-((omega[:,None]+omega[None,:])/2.0)*tau_eff
        z[:]=alpha*z+(1.0-alpha)*np.exp(1j*dphi)
        R=np.abs(z); R=0.5*(R+R.T); np.fill_diagonal(R,0.0)
        if R_exo is not None: R=R_exo(n)
        U=B+DT*((ETA+MU)*R-MU-GAMMA*B)
        U=np.maximum(U,0.0); U=0.5*(U+U.T); np.fill_diagonal(U,0.0)
        s=U.sum(1); sc=np.ones(N)
        if float(np.min(A-Q*s))<DELTA:
            sc=np.minimum(1.0,CAP/(s+EPS)); Bn=U*np.minimum.outer(sc,sc); np.fill_diagonal(Bn,0.0)
        else: Bn=U
        u=((ETA+MU)*R-MU)/GAMMA; np.fill_diagonal(u,0.0)
        Rs[n]=R[IU]; lam[n]=np.minimum.outer(sc,sc)[IU]; S[n]=np.maximum(u,0).sum(1)
        B=Bn; Bs[n+1]=B[IU]
        cpl=np.sum(B*np.sin(dl[None,:]-th[:,None]),axis=1)
        th=np.mod(th+DT*(omega+cpl),2*np.pi); hist.append(th.copy()); hist.pop(0)
    return dict(R=Rs,B=Bs,lam=lam,S=S)

def certificate(R,B,S,T,gated_off=True,guard=None):
    """Certificates of Thm 2 (OFF, ON) and Thm 3 (gated OFF), using only R over [T,end) and B[T].
    Returns per-edge (cls, N_e), cls in {'off','on','goff',None}.
    guard: minimum certificate margin (default MARGIN_GUARD; pass 0.0 for the unguarded pre-audit behaviour)."""
    G=MARGIN_GUARD if guard is None else guard
    u=((ETA+MU)*R[T:]-MU)/GAMMA; umin=u.min(0); umax=u.max(0); Splus=S[T:].max(0)
    xT=B[T]; out=[None]*E
    # lower comparison data for every edge with umin>0 (Lemma 2 / Thm 2 ON part)
    fp=np.zeros(E); rho=np.ones(E)
    for e in range(E):
        i,j=IU[0][e],IU[1][e]
        if umin[e]>0:
            g=max(1.0,((1-H)*CAP+H*Splus[i]+EPS)/CAP,((1-H)*CAP+H*Splus[j]+EPS)/CAP)
            fp[e]=H*umin[e]/(g-1+H); rho[e]=(1-H)/g
    for e in range(E):
        Up=max(umax[e],0.0)
        if BC-Up>=G and Up<BC:
            Ne=0 if xT[e]<=BC else math.ceil(math.log((xT[e]-Up)/(BC-Up))/(-math.log1p(-H)))
            out[e]=('off',Ne)
        elif umin[e]>0 and fp[e]>BC and fp[e]-BC>=G:
            ratio=(fp[e]-xT[e])/(fp[e]-BC)
            out[e]=('on',0 if ratio<1 else math.floor(math.log(ratio)/math.log(1/rho[e]))+1)
    if gated_off:
        best={}
        for N1 in (0,1000,2000,4000,8000,16000,32000,64000):
            lhat=np.where(umin>0, fp-(rho**N1)*np.maximum(fp-xT,0.0), 0.0); lhat=np.maximum(lhat,0.0)
            sig=np.zeros(N)
            for e in range(E):
                i,j=IU[0][e],IU[1][e]; t=max(0.0,(1-H)*lhat[e]+H*umin[e]) if umin[e]>0 else 0.0
                sig[i]+=t; sig[j]+=t
            for e in range(E):
                if out[e] is not None: continue
                i,j=IU[0][e],IU[1][e]; Up=max(umax[e],0.0)
                kap=min(1.0,CAP/sig[i] if sig[i]>0 else 1.0,CAP/sig[j] if sig[j]>0 else 1.0)
                if kap*(1-H)>=1: continue
                fu=kap*H*Up/(1-kap*(1-H))
                if fu>=BC or BC-fu<G: continue
                z0=CAP                      # a-priori bound: B_e <= row sum <= c (Lemma 1)
                Ne=N1+math.ceil(math.log((z0-fu)/(BC-fu))/math.log(1/(kap*(1-H))))
                if e not in best or Ne<best[e]: best[e]=Ne
        for e,Ne in best.items(): out[e]=('goff',Ne)
    return [o if o is not None else (None,None) for o in out]

def last_change(B):
    st=B>BC; ch=np.nonzero((st[1:]!=st[:-1]))  # change between n-1 and n -> index n
    L=np.full(E,0);
    for n,e in zip(ch[0]+1,ch[1]): L[e]=max(L[e],n)
    return L, st[-1]

def analyse(tag,res,grid=500,start=0):
    R,B,S=res['R'],res['B'],res['S']; steps=len(R)
    L,final=last_change(B[start:]); L=np.where(L>0,L+start,0)
    rows=[]; first=None; viol=[]; tested=[]
    for T in range(start,steps-grid,grid):
        c=certificate(R,B,S,T)
        if all(k is not None for k,_ in c):
            pred=np.array([T+n for _,n in c]); cls=np.array([k=='on' for k,_ in c])
            Ns=np.array([n for _,n in c]); kinds={k:sum(1 for kk,_ in c if kk==k) for k in ('on','off','goff')}
            tested.append(dict(T=T,maxN=int(Ns.max()),nposN=int((Ns>0).sum()),kinds=kinds,ok=bool(np.all(L<=pred) and np.all(cls==final))))
            ok=bool(np.all(L<=pred) and np.all(cls==final))
            # also: status constant on [T+N_e, end] -> implied by L<=pred and final class match
            if not ok: viol.append(T)
            if first is None: first=dict(T=T,pred_freeze=int(pred.max()),ok=ok,n_on=int(cls.sum()),kinds=kinds,maxN=int(Ns.max()))
    ncert_edges_at_first=None
    out=dict(tag=tag,steps=steps,observed_last_change=int(L.max()),n_on_final=int(final.sum()),
             edges_ever_changing_after_step_48000=int((L>48000).sum()),
             first_certified=first,violations=viol,
             max_gate_factor_deficit=float(1-res['lam'].min()),n_certified_T=len(tested),n_certified_T_with_positive_N=sum(1 for t in tested if t['nposN']>0),max_N_any=max([t['maxN'] for t in tested],default=None),all_certified_T_ok=all(t['ok'] for t in tested))
    if first is None:
        c=certificate(R,B,S,steps-2*grid)
        out['uncertified_edges_late']=[ (int(IU[0][e]),int(IU[1][e]),float(B[-1,e]),float(R[-2*grid:,e].min()))
                                       for e,(k,_) in enumerate(c) if k is None]
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default=os.path.join(HERE,'results.json'))
    ap.add_argument('--crosscheck',action='store_true'); a=ap.parse_args()
    results=[]
    seeds=[10431384713483787270,10856823803646276806,11242426753702356865,12123519807951751650,1230287949579537403]
    if a.crosscheck:
        sys.path.insert(0,REPO_ROOT); import aief_experiment_engine_v1 as eng   # in-repo engine, read-only
        cfg=eng.DEFAULT_MODEL_CONFIG; st=eng.initialize_state(seeds[0],cfg); r0=np.random.default_rng(0)
        Bref=[st.B[IU].copy()]
        for n in range(3000): eng.advance_state(st,cfg,r0); Bref.append(st.B[IU].copy())
        mine=simulate(seeds[0],steps=3000)['B']
        print('crosscheck max|B_mine-B_engine| over 3000 steps:',float(np.abs(np.array(Bref)-mine).max()))
    for s in seeds:
        results.append(analyse(f'repo_omega/delay/seed={s}',simulate(s))); print(results[-1],flush=True)
    s=seeds[0]; results.append(analyse(f'repo_omega/no_delay/seed={s}',simulate(s,no_delay=True))); print(results[-1],flush=True)
    rr=np.random.default_rng(7)
    for k in range(2):
        om=np.sort(rr.uniform(1.0,2.0,N)); r=analyse(f'random_omega_U[1,2]#{k}/seed={seeds[k]}',simulate(seeds[k],omega=om))
        r['omega']=om.tolist(); results.append(r); print(r,flush=True)
    # stress: near-identical frequencies (one 12-cluster), certificate expected to FAIL (c/11 < B_c)
    om=1.0+0.001*np.arange(N); r=analyse(f'stress_near_identical/seed={seeds[0]}',simulate(seeds[0],omega=om)); r['omega']=om.tolist(); results.append(r); print(r,flush=True)
    # reset_B branch: B:=0 at split step 48000 (EMA kept), certificate tested only for T>=48000
    for s in seeds[:3]:
        r=analyse(f'reset_B_at_48000/seed={s}',simulate(s,reset_B_at=48000),start=48000); results.append(r); print(r,flush=True)
    # exogenous-R counterexample to an UNCONDITIONAL statement: R=1 on a triangle for 20000 steps, 0 for 20000, repeat
    def Rex(n):
        M=np.zeros((N,N))
        if (n//20000)%2==0: M[np.ix_([0,1,2],[0,1,2])]=1.0; np.fill_diagonal(M,0.0)
        return M
    res=simulate(seeds[0],R_exo=Rex,steps=200000); st=res['B'][:,0]>BC
    r=dict(tag='exogenous_periodic_R_counterexample(edge 0-1)',status_changes=int(np.sum(st[1:]!=st[:-1])),
           Bmax=float(res['B'][:,0].max()),Bmin_after_20000=float(res['B'][20000:,0].min())); results.append(r); print(r,flush=True)
    json.dump(results,open(a.out,'w'),indent=1)
