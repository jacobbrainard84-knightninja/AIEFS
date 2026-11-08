"""Build an evidence-checked standalone note and optional supporting archive."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

CYCLE=Path(__file__).resolve().parent
ROOT=CYCLE.parent
NAME='2026-11-07_researcher040282_003_weight-update-bridge.md'
REPORT=ROOT/NAME
CODE_FILES=['GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','check_cycle.py','compare_source.py']
ALLOWED={'propext','Classical.choice','Quot.sound'}


def validate_proofs(result,sources):
    assert result['control_count']==17 and result['all_controls_passed']
    assert all(r['control_passed'] for r in result['controls'])
    assert result['mathlib_revision']=='0df444a360eaa60ab8c11dca51a86af692955474'
    for name,value in result['source_files'].items():
        assert value==hashlib.sha256(sources[name].encode()).hexdigest()
    assert result['harness_sha256']==hashlib.sha256(sources['check_cycle.py'].encode()).hexdigest()
    counts={'GateFoundations':22,'FreezeCore':5}
    for d in result['dependency_builds']:
        assert d['raw_lean_exit']==0 and d['verified'] and not d['problems']
        assert d['declaration_count']==counts[d['module']]
        assert len(d['axiom_footprints'])==counts[d['module']]
        assert all(set(v)<=ALLOWED for v in d['axiom_footprints'].values())
    controls={c['case']:c for c in result['controls']}
    p=controls['positive'];assert p['verified'] and p['raw_lean_exit']==0 and p['declaration_count']==44 and not p['problems']
    assert len(p['axiom_footprints'])==44 and all(set(v)<=ALLOWED for v in p['axiom_footprints'].values())
    false=[c for c in result['controls'] if c['kind']=='false_math'];assert len(false)==5
    assert all(c['raw_lean_exit']!=0 and c['mathematical_error_observed'] and not c['dependency_error_observed'] for c in false)
    assert sum(c['kind'] in ['positive','positive_exact'] for c in result['controls'])==5
    assert controls['exact_fraction_suite']['cases']==384
    return controls


def validate_source(result):
    assert result['all_passed'] and result['case_count']==24 and result['active']==4 and result['inactive']==20
    assert result['absolute_tolerance']==5e-15 and result['relative_tolerance']==0
    assert result['maximum_absolute_error']<=5e-15
    assert all(c['gap_boundary_distance']>1e-8 for c in result['cases'])
    assert all(c['max_absolute_error']<=5e-15 for c in result['cases'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package',action='store_true');args=parser.parse_args()
    sources={name:(CYCLE/name).read_text() for name in CODE_FILES}
    assert all(s==s.rstrip()+'\n' for s in sources.values())
    r=json.loads((CYCLE/'cycle_results.json').read_text());controls=validate_proofs(r,sources)
    sr=json.loads((CYCLE/'source_comparison_results.json').read_text());validate_source(sr)
    assert sr['source_sha256']==hashlib.sha256((CYCLE/'source_state/main/aief_experiment_engine_v1.py').read_bytes()).hexdigest()
    upstream=(CYCLE/'source_state/main/lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean').read_text()
    assert sources['FreezeCore.lean'].startswith(upstream)
    assert sources['GateFoundations.lean']==(ROOT/'cycle_002/GateFoundations.lean').read_text()
    text=(CYCLE/'REPORT_BODY.md').read_text().rstrip()+'\n\n'
    text+='## 9. Actual fresh-build evidence\n\n'
    text+='**Compiler:** `'+r['compiler_version']+'`.\n\n'
    text+=('| Module | Credit / role | Checked declarations | Raw Lean exit | Accepted |\n'
           '|---|---|---:|---:|---|\n'
           '| GateFoundations | Prior local core, unchanged | 22 | 0 | Yes |\n'
           '| FreezeCore | Existing upstream core; proof body unchanged | 5 | 0 | Yes |\n'
           '| GateProposalBridge | New bridge, including helper lemmas | 44 | 0 | Yes |\n\n'
           'Each accepted module has complete requested/printed axiom coverage, '
           'no compiler warnings/errors, and no footprint outside the allowed '
           'standard set. The final local runner exited `0`.\n\n')
    text+='### Control outcomes\n\n| Case | Raw Lean exit | Observed outcome |\n|---|---:|---|\n'
    for c in r['controls']:
        if c['kind']=='positive':out='Accepted, 44/44 allowed footprints'
        elif c['kind']=='false_math':out='Rejected mathematically; no dependency error'
        elif c['kind'] in ['sorry_payload','extra_axiom_payload','missing_footprint']:
            out='Rejected: `'+ '; '.join(c['problems'])+'`'
        elif c['kind']=='positive_exact':out='Exact positive checks passed'
        elif c['kind']=='exact_counterexample':out='Wrong/dropped-hypothesis variant refuted exactly'
        else:out='Optimized Python rejected before assertions can be bypassed (exit 2)'
        text+=f"| `{c['case']}` | {c.get('raw_lean_exit','not a Lean case')} | {out} |\n"
    text+='\n### Recorded runner output\n\n```text\n'+(CYCLE/'cycle_checks.log').read_text().strip()+'\n```\n\n'
    text+='### Complete accepted-module axiom output\n\n'
    for name,logname,count in [('GateFoundations','GateFoundations',22),('FreezeCore','FreezeCore',5),('GateProposalBridge','positive',44)]:
        log=(CYCLE/'checks'/(logname+'.log')).read_text().strip()
        assert len(log.splitlines())==count and all('depends on axioms:' in line for line in log.splitlines())
        text+='**'+name+'**\n\n```text\n'+log+'\n```\n\n'
    if (CYCLE/'standalone_manifest.json').exists():
        manifest=json.loads((CYCLE/'standalone_manifest.json').read_text())
        validate_proofs(json.loads((CYCLE/'standalone_results.json').read_text()),sources)
        validate_source(json.loads((CYCLE/'standalone_source_results.json').read_text()))
        assert manifest['runner_exit']==0 and manifest['source_runner_exit']==0 and manifest['critical_blocks_match_sources']
        text+=('### Single-Markdown reproduction was also executed\n\n'
               'All five critical files below were extracted from this standalone '
               'Markdown into a fresh directory. The extracted proof checker '
               'freshly rebuilt its two dependency modules and ran all 17 controls: '
               'exit `0`, all intended outcomes repeated. The extracted source '
               'checker was also run with the reviewed public engine as an explicit '
               'external dependency: exit `0`, all 24 comparisons passed again. '
               'The extracted code matches the final supplied code exactly. '
               '**This is local self-reproduction, not independent-seat review.**\n\n')
    else:
        text+=('### Single-Markdown reproduction status\n\n'
               'All critical code is inline. A separate extraction/run has not yet '
               'been recorded; the results above are the observed fresh local runs.\n\n')
    sections=[('A','GateFoundations.lean','lean','Prior local core, unchanged'),
              ('B','FreezeCore.lean','lean','Upstream scalar comparison core; only audit queries appended'),
              ('C','GateProposalBridge.lean','lean','Complete new bridge'),
              ('D','check_cycle.py','python','Complete bounded proof/exact checker'),
              ('E','compare_source.py','python','Complete optional controlled-source checker')]
    for letter,name,lang,label in sections:
        text+=f'## Appendix {letter} — {label}\n\n<!-- FILE: {name} -->\n```{lang}\n'+sources[name].rstrip()+'\n```\n\n'
    REPORT.write_text(text.rstrip()+'\n');print(f'Wrote {REPORT.name}: {REPORT.stat().st_size:,} bytes')
    if args.package:
        files=[REPORT,ROOT/'cycle_002/GateFoundations.lean']+[ROOT/name for name in ['README.md','WORKFLOW.md','RESEARCH_QUEUE.md','STATE.json','CLAIM_LEDGER.csv']]
        files+=[CYCLE/name for name in CODE_FILES]
        files+=[CYCLE/name for name in ['PLAN.md','SOURCE_COMPARISON_PLAN.md','REPORT_BODY.md','build_packet.py','one_file_reproduce.py','validate_packet.py','cycle_results.json','cycle_checks.log','exact_results.json','exact_checks.log','source_comparison_results.json','source_comparison.log','standalone_manifest.json','standalone_results.json','standalone_reproduction.log','standalone_source_results.json','standalone_source.log','upstream_core_provenance.json','prepare_lean.py','prepare_mathlib.sh','lean_release.json','lean_installation.json','lean_setup.log','mathlib_setup.log','planned_declarations.json']]
        files+=sorted((CYCLE/'checks').glob('*.log'))+sorted((CYCLE/'standalone_checks').glob('*.log'))
        files+=[CYCLE/'source_state'/name for name in ['main_selected.json','inbox_selected.json','main/aief_experiment_engine_v1.py','main/lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean','main/lean/AIEFProofs/lean-toolchain','main/lean/AIEFProofs/lake-manifest.json']]
        assert all(p.is_file() for p in files)
        archive=ROOT/'researcher040282-cycle003-weight-update-bridge.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for p in files:z.write(p,(Path('researcher_040282')/p.relative_to(ROOT)).as_posix())
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None and len(z.namelist())==len(files)
        print(f'ZIP CRC passed: {len(files)} files; {archive.stat().st_size:,} bytes')


if __name__=='__main__':main()
