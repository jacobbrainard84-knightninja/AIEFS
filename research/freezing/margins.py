"""Certificate margins at the split step T=48000 (start of the audited future window) for the repo seeds."""
import sys, os; sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(HERE,'freeze_check.py')).read().split("if __name__=='__main__':")[0]; exec(src)
import json
out=[]
for s in [10431384713483787270,10856823803646276806,11242426753702356865,12123519807951751650,1230287949579537403]:
    r=simulate(s); T=48000; R,B,Sx=r['R'],r['B'],r['S']
    u=((ETA+MU)*R[T:]-MU)/GAMMA; umin=u.min(0); umax=u.max(0); Sp=Sx[T:].max(0)
    on=B[-1]>BC
    fps=[]
    for e in np.nonzero(on)[0]:
        i,j=IU[0][e],IU[1][e]; g=max(1.0,((1-H)*CAP+H*Sp[i]+EPS)/CAP,((1-H)*CAP+H*Sp[j]+EPS)/CAP); fps.append(H*umin[e]/(g-1+H))
    d=dict(seed=s,on_edges=int(on.sum()),min_on_fixedpoint_lower_bound=float(min(fps)),min_B_on_final=float(B[-1][on].min()),
           max_off_Uplus=float(max(0,umax[~on].max())),max_R_off_future=float(R[T:][:,~on].max()),R_c_ungated=(MU+GAMMA*BC)/(ETA+MU),
           min_R_on_future=float(R[T:][:,on].min()),max_S=float(Sp.max()))
    print(d,flush=True); out.append(d)
json.dump(out,open(os.path.join(HERE,'margins.json'),'w'),indent=1)
