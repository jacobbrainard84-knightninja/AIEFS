# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import sys,time,json; sys.argv=['x']; sys.path.insert(0,'<v3-staging>/AI Agent Audits/evidence/scripts')
import os; os.environ['AIEF_AUDIT_OUT']='<tmp>/v3out'
import kappa_cycle_kernel as K
t=time.time(); r=K.job((K.EXC,1.0)); print(time.time()-t)
for c in r['comps']:
    print({k:v for k,v in c.items() if k not in ('fiber','K3_one_sided','rowsum_margin')})
    for f in c['fiber']: print('  ',f)
    if 'K3_one_sided' in c:
        for f in c['K3_one_sided']: print('  K3',f)
