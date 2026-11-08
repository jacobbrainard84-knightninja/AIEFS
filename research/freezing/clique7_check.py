#!/usr/bin/env python3
"""Audit fix R1 check: locked 7-group with i.i.d. R in [1-w,1] on its 21 edges (exogenous R), T=20000, 60000 steps.
Is the Thm 3 gated-OFF certificate issued (guarded), and does the group stay OFF? Writes clique7_check.json here."""
import sys, json, numpy as np
sys.dont_write_bytecode=True
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); from freeze_check import *
eidx={(int(i),int(j)):k for k,(i,j) in enumerate(zip(*IU))}
nodes=list(range(7)); ce=[eidx[(0,1)],eidx[(2,5)]]; out=[]
for w in [0.0,1e-4,2e-4,3e-4,5e-4,1e-3]:
    rr=np.random.default_rng(5)
    def f(n):
        M=np.zeros((N,N)); X=rr.uniform(1-w,1.0,(7,7)); X=np.triu(X,1); X=X+X.T
        M[np.ix_(nodes,nodes)]=X; np.fill_diagonal(M,0.0); return M
    res=simulate(1,R_exo=f,steps=60000); T=20000; c=certificate(res['R'],res['B'],res['S'],T); L,final=last_change(res['B'])
    d=dict(R_spread=w,edges=[dict(edge=(int(IU[0][e]),int(IU[1][e])),cls=c[e][0],N=c[e][1],last_change=int(L[e]),
           final_on=bool(final[e]),B_max_after_T=float(res['B'][T:,e].max())) for e in ce])
    print(d,flush=True); out.append(d)
json.dump(out,open(os.path.join(HERE,'clique7_check.json'),'w'),indent=1)
