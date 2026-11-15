"""Full-engine interior linearization and projected min-operator kink checks."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys, pathlib, unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'AIEFS_cycle8'))
from test_rotating_solution import config, fixed_weight, locked_frequency, e

class Model:
    def __init__(self,n,d,projected):
        self.c=config(n,.01,d,.04 if projected else .0005,17.5,1.4283333333333332)
        self.n=n; self.d=d; self.m=n-1; self.projected=projected
        self.b=fixed_weight(self.c,projected); self.O=locked_frequency(self.c,self.b)
        self.delta=self.c.dt*self.O; self.z=np.exp(1j*(self.O*self.c.tau-self.c.omega[0]*self.c.tau))
        self.edges=[(i,j) for i in range(n) for j in range(i+1,n)]
        self.p=n*(d+1); self.k=n*n; self.size=self.p+2*self.k+len(self.edges)
    def unpack(self,y):
        p,k,n=self.p,self.k,self.n
        x=y[:p].reshape(self.d+1,n);u=y[p:p+k].reshape(n,n);v=y[p+k:p+2*k].reshape(n,n)
        w=np.zeros((n,n))
        for i,(a,b) in enumerate(self.edges): w[a,b]=w[b,a]=y[p+2*k+i]
        return x,u,v,w
    def pack(self,x,u,v,w):
        return np.concatenate((x.ravel(),u.ravel(),v.ravel(),np.array([w[i,j] for i,j in self.edges])))
    def full_step(self,y):
        n,d=self.n,self.d;x,u,v,w=self.unpack(y);base=.42
        hist=[np.mod(base-j*self.delta+x[j],2*np.pi) for j in range(d,-1,-1)]
        B=self.b*(np.ones((n,n))-np.eye(n))+w
        state=e.DynamicState(hist[-1],B,self.z*(1+u+1j*v),hist)
        e.advance_state(state,self.c,np.random.default_rng(123),shuffle_driver=False)
        xx=np.stack([np.angle(np.exp(1j*(state.history[-1-j]-(base+(1-j)*self.delta)))) for j in range(d+1)])
        C=state.coherence_acc/self.z-1
        return self.pack(xx,C.real,C.imag,state.B-self.b*(np.ones((n,n))-np.eye(n)))
    def analytic_interior(self,y):
        x,u,v,w=self.unpack(y);n,d,m=self.n,self.d,self.m;c=self.c
        un=c.alpha*u
        vn=c.alpha*v+(1-c.alpha)*(x[0,:,None]-x[d,None,:])
        wn=(1-c.dt*c.gamma)*w+c.dt*(c.eta+c.mu)*c.alpha*(u+u.T)/2
        np.fill_diagonal(wn,0.)
        h=c.dt*self.b*np.cos(self.O*c.tau)
        xx=np.empty_like(x)
        xx[0]=(1-m*h)*x[0]+h*(np.sum(x[d])-x[d])-c.dt*np.sin(self.O*c.tau)*np.sum(wn,axis=1)
        xx[1:]=x[:-1]
        return self.pack(xx,un,vn,wn)
    def finite_matrix(self,h=1e-6):
        out=np.empty((self.size,self.size));v=np.zeros(self.size)
        for j in range(self.size):
            v[j]=h; plus=self.full_step(v);v[j]=-h;minus=self.full_step(v);v[j]=0
            out[:,j]=(plus-minus)/(2*h)
        return out
    def analytic_matrix(self):
        eye=np.eye(self.size)
        return np.column_stack([self.analytic_interior(eye[:,j]) for j in range(self.size)])

class Tests(unittest.TestCase):
    def test_full_network_interior(self):
        for d in (3,50):
            M=Model(3,d,False); analytic=M.analytic_matrix(); numerical=M.finite_matrix()
            err=np.max(abs(analytic-numerical)); eig=np.linalg.eigvals(analytic)
            idx=np.argmin(abs(eig-1));other=np.delete(eig,idx)
            phaseh=M.c.dt*M.b*np.cos(M.O*M.c.tau)
            print(f'interior N=3 d={d} dim={M.size} h={phaseh:.9g} Jacobian_error={err:.3g} neutral={eig[idx]} other_radius={max(abs(other)):.12g}')
            self.assertLess(err,3e-9);self.assertLess(abs(eig[idx]-1),1e-8)
            self.assertLess(max(abs(other)),1-1e-7)
            self.assertTrue(0<M.m*phaseh<1)
    def test_projected_directional_kink(self):
        M=Model(3,50,True);v=np.zeros(M.size);v[-len(M.edges)]=1.
        y0=np.zeros(M.size); f0=M.full_step(y0)
        diffs=[]
        for h in (1e-5,1e-6,1e-7):
            right=(M.full_step(h*v)-f0)/h
            left=(f0-M.full_step(-h*v))/h
            edge_count=len(M.edges)
            diff=max(abs(right[-edge_count:]-left[-edge_count:]));diffs.append(diff)
            print(f'projected N=3 d=50 h={h:g} weight-direction discrepancy={diff:.9g}, right={right[-edge_count:]}, left={left[-edge_count:]}')
        self.assertGreater(min(diffs),.1)
        self.assertLess(max(diffs)-min(diffs),.001)

if __name__=='__main__':unittest.main(verbosity=2)
