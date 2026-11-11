"""Run verify_inventory.py's [3/5] vocabulary rules (copied sets) on all registry CSVs, independent of [1/5]. Read-only."""
import csv, sys, re, pathlib
root = pathlib.Path(sys.argv[1])
src = (root/'audits/engineering/verify_inventory.py').read_text()
ns = {}; exec(re.search(r'VALID_STATUS = \{.*?\}\nVALID_SCOPE = \{.*?\}', src, re.S).group(0), ns)
bad = 0
for t in ("artifacts.csv", "claims.csv", "studies.csv", "relocation_map.csv"):
    rows = list(csv.DictReader((root/'registry'/t).open(encoding='utf-8', newline='')))
    b = sum(1 for r in rows if r['artifact_status'] not in ns['VALID_STATUS'] or r['evidence_scope'] not in ns['VALID_SCOPE'])
    un = sum(1 for r in rows if r['artifact_status'] == 'Unreviewed')
    print(f"{t}: rows={len(rows)} vocab_violations={b} unreviewed={un}"); bad += b
# claims audited_status vs README block
rd = (root/'registry/README.md').read_text()
blk = re.search(r'## Status vocabulary\s*```text\n(.*?)```', rd, re.S).group(1).split('\n')
voc = [x for x in blk if x.strip()]
rows = list(csv.DictReader((root/'registry/claims.csv').open(encoding='utf-8', newline='')))
ab = [r['claim_id'] for r in rows if r['audited_status'] not in voc]
print(f"README vocabulary: {len(voc)} statuses; claims audited_status violations: {len(ab)} {ab}")
print(f"claims: {len(rows)} rows x {len(rows[0])} cols; unique claim_id={len(set(r['claim_id'] for r in rows))}")
print("TOTAL verify_inventory-vocab violations:", bad)
