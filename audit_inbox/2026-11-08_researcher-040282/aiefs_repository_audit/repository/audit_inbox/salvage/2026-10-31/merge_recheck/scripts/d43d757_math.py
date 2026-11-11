"""Independent checks for d43d757: unsigned-incidence kernel dims, K4 unequal-edge tie ratios."""
import itertools, numpy as np, math
def inc(n, edges, signed=False):
    A=np.zeros((n,len(edges)))
    for e,(i,j) in enumerate(edges): A[i,e]=1; A[j,e]=-1 if signed else 1
    return A
def kdim(A): return A.shape[1]-np.linalg.matrix_rank(A)
print("graph | n m | dim ker unsigned | dim ker signed (cycle space) | bipartite")
G={}
for n in range(3,8): G[f"K{n}"]=(n,list(itertools.combinations(range(n),2)))
G["C4 (bipartite)"]=(4,[(0,1),(1,2),(2,3),(3,0)])
G["K2,3 (bipartite)"]=(5,[(i,j) for i in (0,1) for j in (2,3,4)])
G["C5 (odd cycle)"]=(5,[(i,(i+1)%5) for i in range(5)])
G["K4 minus edge"]=(4,[e for e in itertools.combinations(range(4),2) if e!=(2,3)])
for name,(n,E) in G.items():
    A=inc(n,E); S=inc(n,E,True); m=len(E)
    # bipartite test: unsigned rank n-1 <=> bipartite (connected)
    print(f"{name:18s}| {n} {m:2d} | {kdim(A):2d} (m-n={m-n}) | {kdim(S):2d} (m-n+1={m-n+1}) | {np.linalg.matrix_rank(A)==n-1}")
# K4 tie-pattern, independent one-sided derivative with my own gate (R=1, saturated)
c,dt,eta,gam,eps=0.6333333333333333,0.01,0.04,0.015,1e-12
a=1-gam*dt
def gate(B):
    x=a*B+eta*dt*(B>0); np.fill_diagonal(x,0); s=np.minimum(1,c/(x.sum(1)+eps)); y=x*np.minimum.outer(s,s); np.fill_diagonal(y,0); return y
def ratios(W, h1e, h2e, t=1e-9):
    n=len(W); ed=list(itertools.combinations(range(n),2)); base=gate(W)
    def D(v):
        P=np.zeros_like(W)
        for e,(i,j) in enumerate(ed): P[i,j]=P[j,i]=v[e]
        y=(gate(W+t*P)-base)/t; return np.array([y[i,j] for i,j in ed])
    I=np.eye(len(ed)); h1=I[ed.index(h1e)]; h2=I[ed.index(h2e)]
    D1,D2,D12,Dm=D(h1),D(h2),D(h1+h2),D(-h1)
    return np.linalg.norm(D12-D1-D2)/np.linalg.norm(D1+D2), np.linalg.norm(D1+Dm)/np.linalg.norm(D1)
def K4(w1,w2,w3):
    W=np.zeros((4,4)); tot=w1+w2+w3
    for (i,j),v in {(0,1):w1,(2,3):w1,(0,2):w2,(1,3):w2,(0,3):w3,(1,2):w3}.items(): W[i,j]=W[j,i]=v*c/tot
    return W
k=3
print("formula K4: nonadd %.4f odd %.4f"%(1/math.sqrt(2*k*(k-1)),math.sqrt(2/(k+1))))
print("equal-edge K4 (one step from c/k):      nonadd %.4f odd %.4f"%ratios(K4(1,1,1),(0,1),(0,2)))
for pair in [((0,1),(0,2)),((0,1),(0,3)),((0,3),(0,2))]:
    print("unequal 0.3:0.2:0.1, h1=%s h2=%s: nonadd %.4f odd %.4f"%(pair[0],pair[1],*ratios(K4(.3,.2,.1),*pair)))
W=K4(.3,.2,.1); print("unequal K4 row sums equal:",np.allclose(W.sum(1)[:4],W.sum(1)[0]),"; is it a gate fixed point? max|gate(W)-W| = %.2e"%np.abs(gate(W)-W).max())
