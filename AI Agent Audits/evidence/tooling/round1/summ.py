# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import re,ast,collections
rows=collections.defaultdict(list); n=0; exact=0; bad=[]
for l in open('<round1-scratch>/repro13.log'):
    m=re.match(r"(\w+) (\w+) (\d+) (\d+) [\d.]+s max\|matrix diff\|= (\S+) (\{.*\})",l)
    if not m: continue
    run,c,i,s,md,d=m.groups(); d=ast.literal_eval(d.replace('nan','None')); n+=1
    ok=float(md)==0.0 and all((a==b) or (a is None and b is None) or (isinstance(a,float) and abs(a-b)<1e-12) for k,(a,b) in d.items() if k!='P_degenerate')
    exact+=ok
    if not ok: bad.append(l[:120])
    rows[c].append(d)
print("runs",n,"exact",exact,"mismatch",len(bad)); [print(b) for b in bad[:5]]
import numpy as np
for c,v in rows.items():
    print(c,len(v),{k:(round(float(np.mean([x[k][0] for x in v if x[k][0] is not None])),4) if any(x[k][0] is not None for x in v) else "nan") for k in ['D_B','Corr_physical','Total_edge_weight','Effective_edges']})
