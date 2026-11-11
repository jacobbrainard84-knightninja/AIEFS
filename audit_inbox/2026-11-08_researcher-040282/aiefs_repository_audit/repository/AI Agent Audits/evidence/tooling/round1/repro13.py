# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import sys, time, numpy as np
sys.path.insert(0, '<repo-clone>')
import AIEF_1_3_falsification_updated as f
run=sys.argv[1]; cond=sys.argv[2]; idx=int(sys.argv[3])
import json
m=json.load(open(f'<repo-clone>/runs/{run}/manifest.json'))
seed=m['randomization']['paired_seeds'][idx]
t=time.time()
r=f.run_aief(cond, seed=seed, seed_index=idx, config_hash=run)
el=time.time()-t
s=np.load(f'<repo-clone>/runs/{run}/{cond}_seed_{seed}.npz')
maxdiff=max(float(np.max(np.abs(np.asarray(r[k])-s[k]))) for k in f.MATRIX_KEYS)
sd={k:(r[k], float(s[k])) for k in ['D_B','Corr_physical','Total_edge_weight','Effective_edges','P_degenerate']}
print(run,cond,idx,seed,f'{el:.1f}s','max|matrix diff|=',maxdiff, sd, flush=True)
