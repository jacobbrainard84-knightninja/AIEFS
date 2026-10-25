# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import sys, numpy as np
sys.path.insert(0,'<repo-clone>')
import AIEF_1_3_falsification_updated as f
from scipy.optimize import minimize
N=f.N; cap=(f.A-f.DELTA)/f.Q; EPS=f.ZERO_TOL
print("N",N,"cap",cap)
def admis(B):  # exact replica of lines 438-448
    B=B.copy(); rs=B.sum(1)
    if np.any(f.A-f.Q*rs < f.DELTA):
        s=np.minimum(1.0, cap/(rs+EPS)); B*=np.minimum.outer(s,s); np.fill_diagonal(B,0)
    return B
# (1) interior-output witness: all-equal proposal over capacity
t=1.5*cap/(N-1); X=np.full((N,N),t); np.fill_diagonal(X,0)
W=admis(X); m=cap-W.sum(1)
print("witness: input rowsum",X.sum(1)[0],"output rowsum",W.sum(1)[0],"margin",m[0],"min edge",W[W>0].min(),"output!=input",not np.allclose(W,X))
# (2) gate discontinuity: approach boundary from outside
for d in [1e-3,1e-9,1e-14]:
    Xd=np.full((N,N),(cap*(1+d))/(N-1)); np.fill_diagonal(Xd,0)
    print(f"  rowsum=cap*(1+{d}): scale applied",admis(Xd)[0,1]/Xd[0,1])
Xb=np.full((N,N),cap/(N-1)); np.fill_diagonal(Xb,0); print("  at boundary scale",admis(Xb)[0,1]/Xb[0,1])
# (3) KL projection onto C vs min rule (ideal eps=0), random positive proposals
rng=np.random.default_rng(0); iu=np.triu_indices(N,1); M=len(iu[0])
Inc=np.zeros((N,M)); Inc[iu[0],range(M)]=1; Inc[iu[1],range(M)]=1
def tomat(w): B=np.zeros((N,N)); B[iu]=w; return B+B.T
diffs=[];klgap=[]
for k in range(5):
    x=rng.uniform(0,2*cap/(N-1)*1.6,M)
    B=admis(tomat(x)); wa=B[iu]
    obj=lambda w: np.sum(w*np.log(np.maximum(w,1e-300)/x)-w+x)
    jac=lambda w: np.log(np.maximum(w,1e-300)/x)
    r=minimize(obj,np.minimum(x,wa)*0.99,jac=jac,method='SLSQP',bounds=[(1e-12,None)]*M,
               constraints=[{'type':'ineq','fun':lambda w: cap-Inc@w,'jac':lambda w:-Inc}],options={'ftol':1e-14,'maxiter':500})
    diffs.append(np.max(np.abs(r.x-wa))); klgap.append(obj(wa)-r.fun)
print("KL-proj vs AIEF map: max|diff| per trial",np.round(diffs,4),"KL(AIEF)-KL(proj) >0:",np.round(klgap,5))
# (4) fiber-affine identity: Ax=Ay=q => A(y)-A(x)=M(q)(y-x)
x=rng.uniform(0,0.15,M); X=tomat(x); q=X.sum(1)
# construct y on same fiber: add kernel direction of incidence (even cycle 0-1-2-3: +,-,+,-)
def eidx(i,j): i,j=min(i,j),max(i,j); return np.where((iu[0]==i)&(iu[1]==j))[0][0]
h=np.zeros(M); h[eidx(0,1)]=1;h[eidx(1,2)]=-1;h[eidx(2,3)]=1;h[eidx(3,0)]=-1
y=x+0.01*h; Y=tomat(y); print("same fiber:",np.allclose(Y.sum(1),q))
s=np.minimum(1,cap/(q+EPS)); Mq=np.minimum.outer(s,s)
print("fiber-affine residual:",np.max(np.abs((admis(Y)-admis(X))-Mq*(Y-X))))
# (5) K3 controller kernel from Lean file: [[1,1,0],[1,0,1]] v=(1,-1,-1)
C=np.array([[1,1,0],[1,0,1]]); print("C v =",C@np.array([1,-1,-1]))
# (6) Jordan lemma: E_{n+1}=a E_n + B a^{n+1} => E_n=(E0+nB)a^n
a=0.99;E=0.3;Bc=0.7
for n in range(200): E=a*E+Bc*a**(n+1)
print("Jordan residual",E-(0.3+200*Bc)*a**200)
