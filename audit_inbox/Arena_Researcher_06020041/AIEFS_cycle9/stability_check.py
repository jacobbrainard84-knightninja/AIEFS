"""Check linearization of Cycle 8 scalar map; this is NOT the full-network Jacobian."""
import math, pathlib, sys, unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'AIEFS_cycle8'))
from test_rotating_solution import config, fixed_weight, locked_frequency


def setup(projected):
    c=config(12,.01,50,.04 if projected else .0005,17.5,1.4283333333333332)
    b=fixed_weight(c,projected); O=locked_frequency(c,b)
    return c,b,O


def nonlinear(y,c,b,O):
    # y[:d+1] are phase deviations x_n,...,x_{n-d} in a co-rotating frame.
    d=c.delay_steps; m=c.N-1; q=d+1
    x=y[:q]; u,v,db=y[q:q+3]; delta=O*c.dt
    z=np.exp(1j*(O*c.tau-c.omega[0]*c.tau))
    cnew=c.alpha*z*(1+u+1j*v)+(1-c.alpha)*z*np.exp(1j*(x[0]-x[d]))
    beta=max(0.,b+db+c.dt*((c.eta+c.mu)*abs(cnew)-c.mu-c.gamma*(b+db)))
    if c.a-c.q*m*beta<c.delta:
        bp=beta*min(1.,c.capacity/(m*beta+c.scale_epsilon))
    else: bp=beta
    out=np.zeros_like(y)
    out[0]=x[0]+c.dt*(c.omega[0]+m*bp*np.sin(-d*delta+x[d]-x[0]))-delta
    out[1:q]=x[:d]
    out[q]=np.real(cnew/z)-1;out[q+1]=np.imag(cnew/z);out[q+2]=bp-b
    return out


def jacobian(c,b,O,projected):
    d=c.delay_steps;m=c.N-1;q=d+1;J=np.zeros((q+3,q+3))
    a=c.dt*m*b*math.cos(O*c.tau)
    beta=b+c.dt*(c.eta-c.gamma*b)
    gp=(c.capacity*c.scale_epsilon/(m*beta+c.scale_epsilon)**2) if projected else 1.
    t=1-c.dt*c.gamma
    # b' = gp*[t*db + dt*(eta+mu)*alpha*u]
    bu=gp*c.dt*(c.eta+c.mu)*c.alpha; bb=gp*t
    J[0,0]=1-a; J[0,d]=a
    J[0,q]=-c.dt*m*math.sin(O*c.tau)*bu
    J[0,q+2]=-c.dt*m*math.sin(O*c.tau)*bb
    for j in range(1,q): J[j,j-1]=1
    J[q,q]=c.alpha
    J[q+1,0]=1-c.alpha; J[q+1,d]=-(1-c.alpha);J[q+1,q+1]=c.alpha
    J[q+2,q]=bu;J[q+2,q+2]=bb
    return J,a,bb


def finite_jac(c,b,O,h=1e-6):
    n=c.delay_steps+4; zero=np.zeros(n); mat=np.zeros((n,n))
    for j in range(n):
        y=zero.copy();y[j]=h
        mat[:,j]=(nonlinear(y,c,b,O)-nonlinear(-y,c,b,O))/(2*h)
    return mat

class TestLocalStability(unittest.TestCase):
    def run_case(self,projected):
        c,b,O=setup(projected);J,a,bb=jacobian(c,b,O,projected)
        residual=np.max(np.abs(nonlinear(np.zeros(c.delay_steps+4),c,b,O)))
        err=np.max(np.abs(J-finite_jac(c,b,O)))
        eig=np.linalg.eigvals(J); idx=np.argmin(np.abs(eig-1)); others=np.delete(eig,idx)
        print(f'projected={projected}: fixed={residual:.3g}, jac-error={err:.3g}, a={a:.9g}, alpha={c.alpha:.9g}, weight-eig={bb:.9g}, neutral-eig={eig[idx]}, other spectral radius={max(abs(others)):.12g}')
        self.assertLess(residual,2e-14);self.assertLess(err,2e-9)
        self.assertTrue(0<a<1 and 0<c.alpha<1 and 0<=bb<1)
        self.assertLess(abs(eig[idx]-1),1e-8);self.assertLess(max(abs(others)),1-1e-7)
    def test_interior(self): self.run_case(False)
    def test_projected(self): self.run_case(True)
    def test_nonlinear_symmetric_perturbations(self):
        for projected in (False,True):
            c,b,O=setup(projected); d=c.delay_steps
            y=np.random.default_rng(42).normal(0,1e-4,d+4)
            def quotient_norm(y):
                return max(np.max(np.abs(y[1:d+1]-y[0])),np.max(np.abs(y[d+1:])))
            start=quotient_norm(y)
            for _ in range(40000): y=nonlinear(y,c,b,O)
            end=quotient_norm(y)
            print(f'symmetric nonlinear projected={projected}: quotient initial={start:.6g}, final={end:.6g}, ratio={end/start:.6g}')
            self.assertLess(end/start,.03)
    def test_delay_sign_control(self):
        # Negative a makes P'(1)=1+ad and produces an eigenvalue above 1 for this choice.
        d=3;a=-0.5
        M=np.zeros((d+1,d+1));M[0,0]=1-a;M[0,d]=a
        for k in range(1,d+1):M[k,k-1]=1
        eig=np.linalg.eigvals(M);rad=max(abs(eig))
        print(f'negative-a control: d={d}, a={a}, spectral radius={rad:.9g}')
        self.assertGreater(rad,1.01)

if __name__=='__main__': unittest.main(verbosity=2)
