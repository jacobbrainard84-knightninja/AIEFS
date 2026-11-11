# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import numpy as np, json, sys
sys.path.insert(0,'<repo-clone>')
import AIEF_1_3_falsification_updated as f
OM=f.OMEGA; E=f.EDGES; a=f.ALPHA; dt=f.DT
dw=np.abs(OM[:,None]-OM[None,:])[E]
# steady-state EMA magnitude of a phasor rotating at dw, no coupling
Rpred=np.abs((1-a)/(1-a*np.exp(1j*dw*dt)))
thr_pos = f.MU/(f.ETA+f.MU)
thr_Bc = (f.B_C*f.GAMMA+f.MU)/(f.ETA+f.MU)
print('R threshold for B>0:',thr_pos,' for B>B_c (uncapped):',thr_Bc)
print('edges with uncoupled R_pred > thr_pos:', int((Rpred>thr_pos).sum()), ' > thr_Bc:', int((Rpred>thr_Bc).sum()), 'of', len(dw))
for run in ['c3da1ac707bf','73dca37cf93f']:
    m=json.load(open(f'runs/{run}/manifest.json')); seeds=m['randomization']['paired_seeds']
    d=np.load(f'runs/{run}/AIEF_1_3_{run}_edge_diagnostics.npz')
    cs=[];cR=[];sub=[];DB=[];topo=set();Pall=[]
    for s in seeds:
        P=d[f'baseline_seed_{s}_P_future'][E]; Rp=d[f'baseline_seed_{s}_R_physical_past'][E]
        Bf=d[f'baseline_seed_{s}_B_final'][E]
        cs.append(np.corrcoef(P,-dw)[0,1]); cR.append(np.corrcoef(P,Rpred)[0,1])
        act=Bf>f.B_C; topo.add(tuple(np.flatnonzero(act)))
        sub.append(bool(np.all(Rpred[act]>thr_pos)))
        DB.append(act.mean()); Pall.append(P)
        Pall_arr=np.array(Pall)
    Pm=np.array(Pall).mean(0)
    print(run,'mean corr(P_future, -|dw|)=%.3f'%np.mean(cs),' mean corr(P_future, uncoupled R_pred)=%.3f'%np.mean(cR),
          ' active edges all within freq-near set:',sum(sub),'/',len(sub),' distinct topologies:',len(topo),' mean D_B=%.3f'%np.mean(DB))
    print('   corr(seed-averaged P, R_pred)=%.3f'%np.corrcoef(Pm,Rpred)[0,1], ' edges ever active:',int((Pm>0).sum()))
