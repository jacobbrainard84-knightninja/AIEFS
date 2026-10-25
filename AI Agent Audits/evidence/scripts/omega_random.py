import sys, os, json, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_3_falsification_updated as f
E=f.EDGES
def setomega(om):
    f.OMEGA=np.array(om); f.T_WINDOW=25.0/float(np.mean(om)); f.ALPHA=float(np.exp(-f.DT/f.T_WINDOW))
def predictor(om):
    a=float(np.exp(-f.DT/(25.0/np.mean(om))))
    dw=np.abs(np.subtract.outer(om,om))[E]
    return np.abs((1-a)/(1-a*np.exp(1j*dw*f.DT))), f.MU/(f.ETA+f.MU)
def job(args):
    kind,k,om,cond,seed=args
    setomega(om)
    try:
        r=f.run_aief(cond,seed=seed,seed_index=0,config_hash='omega_test')
    except Exception as e:
        return dict(kind=kind,k=k,cond=cond,seed=seed,error=repr(e)[:200])
    Rp,thr=predictor(np.array(om)); pred=Rp>thr
    act=r['B_final'][E]>f.B_C
    tp=int((act&pred).sum()); fp=int((act&~pred).sum()); fn=int((~act&pred).sum())
    P=r['P_future'][E]
    c=np.corrcoef(P,Rp)[0,1] if P.std()>0 else np.nan
    return dict(kind=kind,k=k,cond=cond,seed=seed,n_pred=int(pred.sum()),n_act=int(act.sum()),tp=tp,fp=fp,fn=fn,
                exact=bool(np.all(act==pred)),subset=bool(np.all(pred[act])),D_B=r['D_B'],Corr_physical=r['Corr_physical'],
                corr_P_Rpred=c,W=r['Total_edge_weight'])
if __name__=='__main__':
    rng=np.random.default_rng(12345); jobs=[]
    for k in range(20):
        om=list(rng.uniform(1.0,2.0,12))
        for cond,seed in [('no_delay',1),('baseline',1),('baseline',2)]: jobs.append(('uniform',k,om,cond,seed))
    for k in range(20):
        centers=rng.uniform(1.0,2.0,rng.integers(2,5)); om=list(rng.choice(centers,12)+rng.normal(0,0.02,12))
        for cond,seed in [('no_delay',1),('baseline',1),('baseline',2)]: jobs.append(('clustered',k,om,cond,seed))
    with Pool(7) as p: res=p.map(job,jobs)
    dump('omega_random.json', dict(jobs=[j[:2]+(list(map(float,j[2])),)+j[3:] for j in jobs],res=res), indent=0)
    import collections
    for kind in ['uniform','clustered']:
        for cond in ['no_delay','baseline']:
            rr=[x for x in res if x['kind']==kind and x['cond']==cond and 'error' not in x]
            err=[x for x in res if x['kind']==kind and x['cond']==cond and 'error' in x]
            if not rr: print(kind,cond,'all errors',err[:1]); continue
            tp=sum(x['tp'] for x in rr); fp=sum(x['fp'] for x in rr); fn=sum(x['fn'] for x in rr)
            print(f"{kind:9s} {cond:8s} n={len(rr)} err={len(err)} exact={sum(x['exact'] for x in rr)} subset={sum(x['subset'] for x in rr)} "
                  f"precision={tp/max(tp+fp,1):.3f} recall={tp/max(tp+fn,1):.3f} meanD_B={np.mean([x['D_B'] for x in rr]):.3f} "
                  f"mean n_pred={np.mean([x['n_pred'] for x in rr]):.1f} n_act={np.mean([x['n_act'] for x in rr]):.1f} "
                  f"Corr_phys={np.nanmean([x['Corr_physical'] for x in rr]):.3f} corr(P,Rpred)={np.nanmean([x['corr_P_Rpred'] for x in rr]):.3f}")
