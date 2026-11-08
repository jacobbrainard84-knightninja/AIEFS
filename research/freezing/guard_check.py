#!/usr/bin/env python3
"""Audit fix R2 check: the audit's float-margin OFF test (single edge driven to c, then u = B_c - m),
with the unguarded (guard=0) and guarded (MARGIN_GUARD) certificate. Writes guard_check.json here."""
import sys, json, math, numpy as np
sys.dont_write_bytecode=True
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); from freeze_check import *
e=0  # edge (0,1)
out=[]
for m in [1e-3,1e-6,1e-10,1e-13,0.0]:
    Rt=(MU+GAMMA*(BC-m))/(ETA+MU)
    def f(n,Rt=Rt):
        M=np.zeros((N,N)); M[0,1]=M[1,0]=1.0 if n<20000 else Rt; return M
    steps=20000+int(min(400000,(math.log(0.6/max(m,1e-13))/H)*1.1+2000))
    res=simulate(1,R_exo=f,steps=steps); T=20000
    L,final=last_change(res['B'])
    for g in (0.0,None):
        k,n=certificate(res['R'],res['B'],res['S'],T,guard=g)[e]
        ok=None if k is None else bool(L[e]<=T+n and (k=='on')==bool(final[e]))
        d=dict(margin=m,guard=('none' if g==0.0 else MARGIN_GUARD),cls=k,N=n,pred=(None if n is None else T+n),
               last_change=int(L[e]),final_on=bool(final[e]),ok=ok,B_end_minus_Bc=float(res['B'][-1,e]-BC))
        print(d,flush=True); out.append(d)
json.dump(out,open(os.path.join(HERE,'guard_check.json'),'w'),indent=1)
