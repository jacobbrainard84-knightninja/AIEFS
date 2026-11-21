#!/usr/bin/env python3
"""Auditor Seat 002 — exact (Fraction) check of the AIEF capacity-gate form.
Own code; does not import or run the engine or any deposited script.
Gate (main d7b9fac, aief_experiment_engine_v1.py advance_state):
  s_i = min(1, cap/(rowsum_i + eps)); B_ij *= min(s_i, s_j)
eps is set to 0 here (exact arithmetic; eps=1e-12 only shifts s by O(1e-12)).
Comparators:
  per-cell multiplicative (Miller & MacKay 1994: decay 'set for the cell as a whole'):
      row i scaled by s_i  -> B'_ij = s_i B_ij  (row-wise; not symmetric in general)
  global single factor: B' = (cap/max rowsum) B
"""
from fractions import Fraction as F
import json

def gate(B, cap):
    n=len(B); rs=[sum(r) for r in B]
    s=[min(F(1), cap/x) if x>0 else F(1) for x in rs]
    return [[B[i][j]*min(s[i],s[j]) for j in range(n)] for i in range(n)], s

def per_cell(B, cap):
    n=len(B); rs=[sum(r) for r in B]
    s=[min(F(1), cap/x) if x>0 else F(1) for x in rs]
    return [[B[i][j]*s[i] for j in range(n)] for i in range(n)], s

def rows(B): return [sum(r) for r in B]
def sym(B): return all(B[i][j]==B[j][i] for i in range(len(B)) for j in range(len(B)))
def row_factors(B0,B1,i): return sorted({B1[i][j]/B0[i][j] for j in range(len(B0)) if B0[i][j]!=0})
def s(x): return str(x)

out={}
cap=F(19,30)   # (A-DELTA)/Q = 0.95/1.5 on main
# W1: only node 0 binds; non-binding nodes 1,2 still lose weight on edges to 0 (spillover)
B=[[F(0),F(1,2),F(1,4)],
   [F(1,2),F(0),F(1,10)],
   [F(1,4),F(1,10),F(0)]]
G,sg=gate(B,cap); P,_=per_cell(B,cap)
out["W1_spillover"]={
 "B":[[s(x) for x in r] for r in B],"cap":s(cap),
 "rowsums_before":[s(x) for x in rows(B)],
 "scales":[s(x) for x in sg],
 "gate_rowsums_after":[s(x) for x in rows(G)],
 "gate_row_factors":{i:[s(x) for x in row_factors(B,G,i)] for i in range(3)},
 "gate_symmetric":sym(G),
 "percell_rowsums_after":[s(x) for x in rows(P)],
 "percell_symmetric":sym(P),
}
# W2: two binding rows with unequal scales -> a binding row ends strictly BELOW cap
B2=[[F(0),F(1,2),F(1,2)],[F(1,2),F(0),F(1,5)],[F(1,2),F(1,5),F(0)]]
G2,s2=gate(B2,cap); P2,_=per_cell(B2,cap)
out["W2_overshoot"]={"B":[[s(x) for x in r] for r in B2],
 "rowsums_before":[s(x) for x in rows(B2)],"scales":[s(x) for x in s2],
 "gate_rowsums_after":[s(x) for x in rows(G2)],
 "gate_binding_rows_below_cap":[i for i in range(3) if rows(B2)[i]>cap and rows(G2)[i]<cap],
 "percell_rowsums_after":[s(x) for x in rows(P2)],"percell_symmetric":sym(P2)}
# W3: uniform saturated clique (equal loads) -> gate == per-cell == global
B3=[[F(0) if i==j else F(2,5) for j in range(4)] for i in range(4)]
G3,s3=gate(B3,cap); P3,_=per_cell(B3,cap); f=cap/max(rows(B3))
out["W3_equal_loads"]={"scales":[s(x) for x in s3],
 "gate_equals_percell":G3==P3,
 "gate_equals_global":G3==[[x*f for x in r] for r in B3],
 "rowsums_after":[s(x) for x in rows(G3)]}

# W4: AUD-RATELAW one-step identity (conditions d,e) on a saturated K4, exact.
# Over-cap proposal X with equal loads -> all nodes are tied controllers (J = all), s_J equal.
# h in ker A_J: +1 on (0,1),(2,3), -1 on (0,2),(1,3): every node's row sum unchanged.
X=[[F(0) if i==j else F(1,4) for j in range(4)] for i in range(4)]
H=[[F(0)]*4 for _ in range(4)]
for (i,j),v in {(0,1):1,(2,3):1,(0,2):-1,(1,3):-1}.items(): H[i][j]=H[j][i]=F(v)
eps=F(1,1000)
GX,sX=gate(X,cap); GXh,sXh=gate([[X[i][j]+eps*H[i][j] for j in range(4)] for i in range(4)],cap)
out["W4_ratelaw_equal_scales"]={"s_J":s(sX[0]),"scales_unchanged":sX==sXh,
 "delta_equals_sJ_times_eps_h":all(GXh[i][j]-GX[i][j]==sX[0]*eps*H[i][j] for i in range(4) for j in range(4))}
# W5: same h, unequal controlling scales -> identity fails (condition (e) is essential)
X5=[[F(0),F(3,10),F(3,10),F(3,10)],[F(3,10),F(0),F(1,4),F(1,4)],[F(3,10),F(1,4),F(0),F(1,4)],[F(3,10),F(1,4),F(1,4),F(0)]]
G5,s5=gate(X5,cap); G5h,s5h=gate([[X5[i][j]+eps*H[i][j] for j in range(4)] for i in range(4)],cap)
d5=[[G5h[i][j]-G5[i][j] for j in range(4)] for i in range(4)]
out["W5_unequal_scales"]={"scales":[s(x) for x in s5],"scales_unchanged":s5==s5h,
 "delta_rowsums":[s(sum(r)) for r in d5],
 "delta_proportional_to_h":len({d5[i][j]/H[i][j] for i in range(4) for j in range(4) if H[i][j]!=0})==1}
print(json.dumps(out,indent=1))
