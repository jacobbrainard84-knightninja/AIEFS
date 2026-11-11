"""Independent recount of Researcher 001's claims_map.csv plus auditor's re-derived evidence levels.
Read-only on Researcher files; writes only under /workspace/audit_project_map/evidence/."""
import csv, json, collections
SRC='/workspace/research/project_map/claims_map.csv'
rows=list(csv.DictReader(open(SRC)))
C=collections.Counter
out={}
out['rows']=len(rows)
out['registry']=sum(r['registry']=='registered' for r in rows)
out['unregistered']=len(rows)-out['registry']
out['by_evidence_all']=C(r['evidence_level'] for r in rows)
out['by_evidence_registry']=C(r['evidence_level'] for r in rows if r['registry']=='registered')
out['by_type_all']=C(r['type'] for r in rows)
out['conditional_yes']=sum(r['conditional']=='yes' for r in rows)
out['conditional_yes_registry']=sum(r['conditional']=='yes' and r['registry']=='registered' for r in rows)
out['validation']=C(r['independent_rediscovery_validation'].split(' ')[0].split('(')[0].strip(';,') for r in rows)
out['validation_ids']={k:[r['id'] for r in rows if r['independent_rediscovery_validation'].lower().startswith(k)] for k in ['yes','partial','unclear']}
OVR={
 'AUD-CYCLE-KERNEL':('argument only','Main statement (round-2 matrix is not a Jacobian; correct object is the multiplier on K) is a derivation; only the dim K sub-part is Lean-proved. Registry scope itself says "Conditional theorem" from kappa_tw_summary.json.'),
 'U-THRESH':('argument only','Closed-form algebra (3/7 and 0.4543) is a hand derivation, not a machine exact computation; no script or Lean proof of it.'),
 'AUD-RESP1-UNIFORM':('floating-point numerics','Live, Supported erratum of the audit table (finite numerical re-read); it was not withdrawn, so it should not be counted in "withdrawn or corrected" claims.'),
 'AUD-KAPPA-TW':('argument only','The claim is a formula identity (a derivation); the 292-component census is a numerical check of it. Mixed; weakest supporting proof is the paper derivation.'),
 'U-MODEL':('floating-point numerics','"Matches the engine exactly (0.0)" is a bitwise float64 agreement over finite runs, not exact (rational/symbolic) arithmetic.'),
}
NOTES={
 'U-MS-8.1':'Agree argument only overall; dimension sub-part is Lean-proved (K3 in CI; all n only on research/lean-kn). Its "spectrally silent" wording is retired (README:73) but survives at manuscript:1248.',
 'LEAN-KN-01':'Agree Lean-proved under the brief definition (builds; project SHA256SUMS verify; no sorry/axiom; standard axioms only, 52 declarations reproduced). Not in CI and only on a branch.',
 'CF06':'Agree Lean-proved for the kernel identity; mapping the observed winner pattern to the matrix is argument (rests on CF05, single seed).',
 'LEAN-R4':'Reproduced: check_lean.sh 7/7 PASS, 115 declarations, 1591 jobs, 0 warnings (my copy, 2026-10-29 19:37 Toronto).',
 'LEAN-CF-01':'Reproduced build and axioms.',
 'RES-FREEZE-01':'Agree argument only: Lean covers only per-edge existential-N core (5 theorems); Lemma 1, Thm 3, Cor 4 not in Lean; AIEFFreezeCore not in CI.',
 'U-FLOATGATE':'Agree exact computation (rational comparison).',
}
conf=collections.Counter(); dis=[]
with open('/workspace/audit_project_map/evidence/evidence_levels_auditor.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['id','registry','researcher_level','auditor_level','agree','reason_or_note'])
    for r in rows:
        mine,why=OVR.get(r['id'],(r['evidence_level'],NOTES.get(r['id'],'')))
        conf[(r['evidence_level'],mine)]+=1
        w.writerow([r['id'],r['registry'],r['evidence_level'],mine,r['evidence_level']==mine,why])
        if r['evidence_level']!=mine: dis.append((r['id'],r['evidence_level'],mine,why))
levels=['Lean-proved','exact computation','argument only','floating-point numerics','unverified','retracted/corrected']
lines=['| Researcher \\ Auditor | '+' | '.join(levels)+' | row total |','|'+'---|'*(len(levels)+2)]
for a in levels:
    lines.append(f'| {a} | '+' | '.join(str(conf[(a,b)]) for b in levels)+f' | {sum(conf[(a,b)] for b in levels)} |')
lines.append('| column total | '+' | '.join(str(sum(conf[(a,b)] for a in levels)) for b in levels)+f' | {sum(conf.values())} |')
open('/workspace/audit_project_map/evidence/confusion_table.md','w').write('\n'.join(lines)+'\n')
out['auditor_by_evidence_all']=C(OVR.get(r['id'],(r['evidence_level'],))[0] for r in rows)
out['disagreements']=dis
json.dump(out,open('/workspace/audit_project_map/evidence/independent_count.json','w'),indent=1,default=dict)
print(json.dumps(out,indent=1,default=dict)); print('\n'.join(lines))
