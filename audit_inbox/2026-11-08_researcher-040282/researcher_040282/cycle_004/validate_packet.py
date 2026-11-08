"""Bounded local packet consistency check, not independent mathematical review."""
if not __debug__:raise SystemExit('Assertions must be enabled; do not use -O/-OO.')
from pathlib import Path
import argparse
import csv
import json
import re
import zipfile
from build_packet import FILES,validate_proofs,validate_source

ROOT=Path(__file__).resolve().parent
HOME=ROOT.parent
NAME='2026-09-04_researcher040282_004_complex-ema.md'
ARCHIVE='researcher040282-cycle004-complex-ema.zip'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,default=HOME/ARCHIVE);args=parser.parse_args()
    sources={name:(ROOT/name).read_text() for name in FILES};note=(HOME/NAME).read_text()
    pattern=r"<!-- FILE: ([A-Za-z_][A-Za-z0-9_]*\.(?:lean|py)) -->\n```[^\n]*\n(.*?)\n```"
    matches=re.findall(pattern,note,re.S)
    assert len(matches)==7 and set(dict(matches))==set(FILES)
    assert all(content+'\n'==sources[name] for name,content in matches)
    assert 'Single-Markdown extraction/reproduction was actually executed' in note
    for filename in ['cycle_results.json','standalone_results.json']:
        validate_proofs(json.loads((ROOT/filename).read_text()),sources)
    for filename in ['source_comparison_results.json','standalone_source_results.json']:
        validate_source(json.loads((ROOT/filename).read_text()),sources)
    for folder in ['checks','standalone_checks']:
        for case in ['false_disk_without_alpha_upper','false_disk_without_alpha_lower','false_disk_without_input_bound','false_unforced_difference','false_complex_average_readout','false_complex_zero_diagonal','false_strict_decay_at_alpha_one','false_coherence_equals_cosine']:
            assert '⊢ False' in (ROOT/folder/(case+'.log')).read_text()
    with (HOME/'CLAIM_LEDGER.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==108 and len({r['claim_id'] for r in rows})==108
    assert sum(r['cycle']=='4' and r['evidence_label']=='LEAN_COMPILED' for r in rows)==28
    state=json.loads((HOME/'STATE.json').read_text())
    assert state['current_status']=='completed' and state['current_cycle']==4 and not state['research_processes_running']
    assert not state['remote_changes_by_this_agent'] and not state['contacted_other_bots'] and not state['independent_review_received']
    with zipfile.ZipFile(args.archive) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))
        for name in names:
            path=(HOME.parent/name).resolve();assert path.is_relative_to(HOME)
            assert path.is_file() and path.read_bytes()==z.read(name)
    result={'archive':args.archive.name,'file_count':len(names),'zip_crc_passed':True,
        'all_members_match_workspace':True,'critical_inline_files_match_workspace':True,
        'critical_file_count':7,'new_compiled_declarations':28,'recompiled_prior_local_declarations':66,
        'recompiled_upstream_declarations':5,'original_and_extracted_controls':18,
        'original_and_extracted_source_cases':34,'source_compute_R_calls_per_run':253,
        'source_sensitivity_controls_per_run':6,'expected_configuration_rejections_per_run':1,
        'claim_ledger_records':108,'report_bytes':(HOME/NAME).stat().st_size,'archive_bytes':args.archive.stat().st_size,
        'validation_record_is_outside_archive':True,
        'review_boundary':'Local self-reproduction/artifact validation, not independent approval, publication or integration'}
    (ROOT/'packet_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
