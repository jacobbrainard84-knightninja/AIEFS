# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import sys, json, numpy as np
from multiprocessing import Pool
sys.path.insert(0,'<round1-scratch>/deep'); sys.path.insert(0,'<repo-clone>')
from omega_random import setomega, predictor, f
E=f.EDGES
def job(a):
    k,om,cond,seed=a; setomega(om)
    r=f.run_aief(cond,seed=seed,seed_index=0,config_hash='ms')
    return k,cond,seed,(r['B_final'][E]>f.B_C).tolist(),float(r['Corr_physical']),float(np.mean(r['R_physical_past'][E]))
if __name__=='__main__':
    rng=np.random.default_rng(777); jobs=[]; oms=[]
    for k in range(10):
        om=list(rng.uniform(1,2,12)); oms.append(om)
        for s in range(1,5): jobs.append((k,om,'baseline',s))
        jobs.append((k,om,'no_delay',1))
    with Pool(7) as p: res=p.map(job,jobs)
    J=lambda a,b: (a&b).sum()/max((a|b).sum(),1)
    js=[];jd=[];distinct=[]
    for k in range(10):
        b=[np.array(x[3]) for x in res if x[0]==k and x[1]=='baseline']; nd=[np.array(x[3]) for x in res if x[0]==k and x[1]=='no_delay'][0]
        js+= [J(b[i],b[j]) for i in range(4) for j in range(i+1,4)]; jd+=[J(x,nd) for x in b]
        distinct.append(len({tuple(x) for x in b}))
    print('random omega: mean pairwise Jaccard between 4 seeds (baseline)=%.3f'%np.mean(js),' distinct topologies per omega (of 4):',distinct,' Jaccard(baseline,no_delay)=%.3f'%np.mean(jd))
    json.dump(res,open('<round1-scratch>/deep/omega_multistab.json','w'))
