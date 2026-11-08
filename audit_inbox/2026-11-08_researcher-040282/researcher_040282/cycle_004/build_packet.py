"""Assemble the cycle 004 note from verified sources/results, plus optional ZIP."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parent
HOME=ROOT.parent
NAME='2026-09-04_researcher040282_004_complex-ema.md'
REPORT=HOME/NAME
FILES=['GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean','check_cycle.py','compare_source.py']
ALLOWED={'propext','Classical.choice','Quot.sound'}
COUNTS={'GateFoundations':22,'FreezeCore':5,'GateProposalBridge':44,'CoherenceEMA':22,'CoherenceDriveBridge':6}


def validate_proofs(result,sources):
    assert result['control_count']==18 and result['all_controls_passed'] and all(c['control_passed'] for c in result['controls'])
    assert result['mathlib_revision']=='0df444a360eaa60ab8c11dca51a86af692955474'
    assert all(value==hashlib.sha256(sources[name].encode()).hexdigest() for name,value in result['source_files'].items())
    assert result['harness_sha256']==hashlib.sha256(sources['check_cycle.py'].encode()).hexdigest()
    modules=result['dependency_builds']+[c for c in result['controls'] if c['kind']=='positive']
    assert len(modules)==5
    for module in modules:
        n=COUNTS[module['module']]
        assert module['raw_lean_exit']==0 and module['verified'] and not module['problems']
        assert module['declaration_count']==n and len(module['axiom_footprints'])==n
        assert all(set(axioms)<=ALLOWED for axioms in module['axiom_footprints'].values())
    false=[c for c in result['controls'] if c['kind']=='false_math'];assert len(false)==8
    assert all(c['raw_lean_exit']==1 and c['mathematical_error_observed'] and not c['dependency_error_observed'] for c in false)
    assert sum(c['kind'] in ['positive','positive_exact'] for c in result['controls'])==5
    return modules


def validate_source(result,sources):
    assert result['all_passed'] and result['case_count']==34 and result['compute_R_calls']==253
    assert result['absolute_tolerance']==2e-14 and result['relative_tolerance']==0
    assert result['maximum_C_error']<=2e-14 and result['maximum_R_error']<=2e-14
    assert len(result['sensitivity_controls'])==6 and all(c['detected'] and c['maximum_separation']>1e-8 for c in result['sensitivity_controls'])
    assert len(result['configuration_controls'])==1 and result['configuration_controls'][0]['expected_rejection_observed']
    assert not result['configuration_controls'][0]['compute_R_called']
    assert result['checker_sha256']==hashlib.sha256(sources['compare_source.py'].encode()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package',action='store_true');args=parser.parse_args()
    sources={name:(ROOT/name).read_text() for name in FILES};assert all(s==s.rstrip()+'\n' for s in sources.values())
    result=json.loads((ROOT/'cycle_results.json').read_text());modules=validate_proofs(result,sources)
    source=json.loads((ROOT/'source_comparison_results.json').read_text());validate_source(source,sources)
    assert source['source_sha256']==hashlib.sha256((ROOT/'source_state/main/aief_experiment_engine_v1.py').read_bytes()).hexdigest()
    for name in ['GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean']:
        prior=HOME/'cycle_003'/name
        if prior.exists():assert sources[name]==prior.read_text()
    upstream=ROOT/'source_state/main/lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean'
    assert sources['FreezeCore.lean'].startswith(upstream.read_text())
    text=(ROOT/'REPORT_BODY.md').read_text().rstrip()+'\n\n## 9. Observed fresh-build and control evidence\n\n'
    text+='Compiler: `'+result['compiler_version']+'`.\n\n'
    text+='| Module | Credit | Declarations / footprints | Raw Lean exit | Accepted |\n|---|---|---:|---:|---|\n'
    for row in modules:
        name=row['module'];credit='New (helpers included)' if name.startswith('Coherence') else ('Existing upstream, unchanged proof body' if name=='FreezeCore' else 'Prior local, unchanged')
        text+=f"| {name} | {credit} | {row['declaration_count']} / {len(row['axiom_footprints'])} | {row['raw_lean_exit']} | Yes |\n"
    text+='\nAll accepted modules have complete footprint coverage, no warnings/errors, and no axioms outside the allowed standard set. The local full runner exited `0`, with **18 intended outcomes: five positive and thirteen negative**. Its measured elapsed time was '+f"{result['elapsed_seconds']:.2f}"+' seconds; runtime is environment-dependent.\n\n'
    text+='| Control | Raw Lean exit | Intended outcome observed |\n|---|---:|---|\n'
    for c in result['controls']:
        kind=c['kind']
        if kind=='positive':out='Accepted with complete allowed footprints'
        elif kind=='false_math':
            assert '⊢ False' in (ROOT/'checks'/(c['case']+'.log')).read_text()
            out='Rejected at a mathematical goal `False`; no dependency error'
        elif kind in ['sorry_payload','extra_axiom_payload','missing_footprint']:out='Raw compilation accepted, verification policy rejected'
        elif kind=='positive_exact':out='Exact finite properties passed'
        elif kind=='exact_counterexample':out='All eight wrong-variant witnesses refuted exactly'
        else:out='Python optimization rejected explicitly (Python exit 2)'
        text+=f"| `{c['case']}` | {c.get('raw_lean_exit','not a Lean case')} | {out} |\n"
    text+='\n### Actual runner output\n\n```text\n'+(ROOT/'cycle_checks.log').read_text().strip()+'\n```\n\n'
    text+='### Accepted axiom footprints (parsed from actual compiler output)\n\n'
    for row in modules:
        text+='**'+row['module']+'**\n\n```text\n'
        text+='\n'.join(name+': ['+', '.join(axioms)+']' for name,axioms in row['axiom_footprints'].items())+'\n```\n\n'
    if (ROOT/'standalone_manifest.json').exists():
        m=json.loads((ROOT/'standalone_manifest.json').read_text())
        validate_proofs(json.loads((ROOT/'standalone_results.json').read_text()),sources)
        validate_source(json.loads((ROOT/'standalone_source_results.json').read_text()),sources)
        assert m['runner_exit']==m['source_runner_exit']==0 and m['critical_blocks_match_sources']
        text+=('### Single-Markdown extraction/reproduction was actually executed\n\n'
               'All seven critical files below were extracted from this Markdown into a new directory and matched the supplied sources exactly. '
               'The extracted checker freshly rebuilt all five proof modules and repeated all 18 intended control outcomes (exit `0`). '
               'The extracted source checker was also executed with the reviewed public engine as an explicit external dependency: '
               '34 comparisons / 253 calls, six wrong-model detections and the separate expected configuration rejection passed again (exit `0`). '
               '**This is local self-reproduction, not independent-seat review.**\n\n')
    else:text+='### Single-Markdown reproduction status\n\nExtraction/rerun has not yet been recorded. The evidence above is the actual fresh local run.\n\n'
    labels=['Prior guarded finite-map core, unchanged','Existing upstream scalar core with audit queries','Prior proposal/applied-factor bridge, unchanged','New complex EMA/readout component','New reported-drive/gate bridge','Complete bounded proof/exact checker','Complete optional actual-source component checker']
    for letter,name,label in zip('ABCDEFG',FILES,labels):
        lang='lean' if name.endswith('.lean') else 'python'
        text+=f'## Appendix {letter} — {label}\n\n<!-- FILE: {name} -->\n```{lang}\n'+sources[name].rstrip()+'\n```\n\n'
    REPORT.write_text(text.rstrip()+'\n');print('Wrote',REPORT.name,REPORT.stat().st_size,'bytes')
    if args.package:
        entries=[REPORT]+[HOME/name for name in ['README.md','WORKFLOW.md','RESEARCH_QUEUE.md','STATE.json','CLAIM_LEDGER.csv']]
        entries+=[ROOT/name for name in FILES]
        entries+=[ROOT/name for name in ['PLAN.md','SOURCE_COMPARISON_PLAN.md','REPORT_BODY.md','refresh_sources.py','source_refresh.log','build_packet.py','one_file_reproduce.py','validate_packet.py','cycle_results.json','cycle_checks.log','exact_results.json','exact_checks.log','source_comparison_results.json','source_comparison.log','standalone_manifest.json','standalone_results.json','standalone_reproduction.log','standalone_source_results.json','standalone_source.log','prepare_lean.py','prepare_mathlib.sh','lean_release.json','lean_installation.json','lean_setup.log','mathlib_setup.log','upstream_core_provenance.json','planned_declarations.json']]
        entries+=sorted((ROOT/'checks').glob('*.log'))+sorted((ROOT/'standalone_checks').glob('*.log'))
        entries+=[ROOT/'source_state'/name for name in ['main_selected.json','inbox_selected.json','main/aief_experiment_engine_v1.py','main/lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean','main/lean/AIEFProofs/lean-toolchain','main/lean/AIEFProofs/lake-manifest.json']]
        # Keep the failed source-validation attempt paired with its explicit correction.
        entries+=[ROOT/'source_comparison_initial.log']
        assert all(p.is_file() for p in entries)
        archive=HOME/'researcher040282-cycle004-complex-ema.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for p in entries:z.write(p,(Path('researcher_040282')/p.relative_to(HOME)).as_posix())
        with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==len(entries)
        print('ZIP CRC passed:',len(entries),'files;',archive.stat().st_size,'bytes')


if __name__=='__main__':main()
