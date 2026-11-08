"""Validate the supplied research packet against its current workspace copies.

This is a bounded artifact consistency check, not secure intake of arbitrary
archives or independent mathematical review. Run with assertions enabled.
"""
if not __debug__:
    raise SystemExit('Assertions must be enabled; do not use -O/-OO.')

from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import zipfile

CYCLE=Path(__file__).resolve().parent
ROOT=CYCLE.parent
REPORT='2026-11-07_researcher040282_003_weight-update-bridge.md'
ARCHIVE='researcher040282-cycle003-weight-update-bridge.zip'
EXPECTED={'GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','check_cycle.py','compare_source.py'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,default=ROOT/ARCHIVE);args=parser.parse_args()
    note=(ROOT/REPORT).read_text()
    pattern=r"<!-- FILE: (GateFoundations\.lean|FreezeCore\.lean|GateProposalBridge\.lean|check_cycle\.py|compare_source\.py) -->\n```[^\n]*\n(.*?)\n```"
    matches=re.findall(pattern,note,re.S)
    assert len(matches)==5 and set(dict(matches))==EXPECTED
    assert all((content+'\n').encode()==(CYCLE/name).read_bytes() for name,content in matches)
    assert 'Single-Markdown reproduction was also executed' in note
    assert 'has not yet' not in note
    proof=json.loads((CYCLE/'cycle_results.json').read_text());repro=json.loads((CYCLE/'standalone_results.json').read_text())
    allowed={'propext','Classical.choice','Quot.sound'}
    for r in [proof,repro]:
        assert r['control_count']==17 and r['all_controls_passed']
        assert len(r['controls'])==17 and all(c['control_passed'] for c in r['controls'])
        assert r['mathlib_revision']=='0df444a360eaa60ab8c11dca51a86af692955474'
        positive=next(c for c in r['controls'] if c['case']=='positive')
        assert positive['raw_lean_exit']==0 and positive['verified'] and positive['declaration_count']==44 and not positive['problems']
        assert len(positive['axiom_footprints'])==44 and all(set(v)<=allowed for v in positive['axiom_footprints'].values())
        assert {d['module']:d['declaration_count'] for d in r['dependency_builds']}=={'GateFoundations':22,'FreezeCore':5}
        assert all(d['raw_lean_exit']==0 and d['verified'] and not d['problems'] and len(d['axiom_footprints'])==d['declaration_count'] and all(set(v)<=allowed for v in d['axiom_footprints'].values()) for d in r['dependency_builds'])
        assert all(value==hashlib.sha256((CYCLE/name).read_bytes()).hexdigest() for name,value in r['source_files'].items())
        assert r['harness_sha256']==hashlib.sha256((CYCLE/'check_cycle.py').read_bytes()).hexdigest()
    for name in ['source_comparison_results.json','standalone_source_results.json']:
        s=json.loads((CYCLE/name).read_text())
        assert s['case_count']==24 and s['all_passed'] and s['active']==4 and s['inactive']==20
        assert s['absolute_tolerance']==5e-15 and s['relative_tolerance']==0 and s['maximum_absolute_error']<=5e-15
    with (ROOT/'CLAIM_LEDGER.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==78 and len({r['claim_id'] for r in rows})==78
    assert sum(r['cycle']=='3' and r['evidence_label']=='LEAN_COMPILED' for r in rows)==44
    state=json.loads((ROOT/'STATE.json').read_text())
    assert state['current_status']=='completed' and state['current_cycle']==3 and not state['research_processes_running']
    queue=(ROOT/'RESEARCH_QUEUE.md').read_text()
    assert 'All five critical files' in queue and 'Range bounds' in queue
    with zipfile.ZipFile(args.archive) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))
        for name in names:
            p=(ROOT.parent/name).resolve();assert p.is_relative_to(ROOT)
            assert p.is_file() and p.read_bytes()==z.read(name)
    result={'archive':args.archive.name,'file_count':len(names),'zip_crc_passed':True,
        'all_members_match_workspace':True,'critical_inline_files_match_workspace':True,
        'critical_file_count':5,'new_compiled_declarations':44,'recompiled_prior_local_declarations':22,
        'recompiled_upstream_declarations':5,'original_and_extracted_controls':17,
        'original_and_extracted_source_cases':24,'claim_ledger_records':78,
        'report_bytes':(ROOT/REPORT).stat().st_size,'archive_bytes':args.archive.stat().st_size,
        'validation_record_is_outside_archive':True,'review_boundary':'Local artifact validation and self-reproduction; independent approval/integration/publication not confirmed'}
    (CYCLE/'packet_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
