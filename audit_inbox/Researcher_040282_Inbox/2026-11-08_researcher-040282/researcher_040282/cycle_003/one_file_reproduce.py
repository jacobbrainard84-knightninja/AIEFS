"""Actually execute critical code extracted from the standalone Markdown.

The executed proof/source checker files come only from the note. The existing
public Lean/Mathlib installation and reviewed public engine are explicit external
dependencies, not private proof imports.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CYCLE=Path(__file__).resolve().parent
NAME='2026-11-07_researcher040282_003_weight-update-bridge.md'
REPORT=CYCLE.parent/NAME
CACHE=Path(os.environ.get('R040282_CACHE',Path.home()/'.cache/researcher040282')).expanduser().resolve()
EXPECTED={'GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','check_cycle.py','compare_source.py'}


def main():
    for name in ['standalone_manifest.json','standalone_results.json','standalone_source_results.json']:
        (CYCLE/name).unlink(missing_ok=True)
    pattern=r"<!-- FILE: (GateFoundations\.lean|FreezeCore\.lean|GateProposalBridge\.lean|check_cycle\.py|compare_source\.py) -->\n```[^\n]*\n(.*?)\n```"
    matches=re.findall(pattern,REPORT.read_text(),re.S)
    assert len(matches)==5 and set(dict(matches))==EXPECTED
    CACHE.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r040282-c003-standalone-',dir=CACHE) as tmp:
        out=Path(tmp)
        for name,content in matches:(out/name).write_text(content+'\n')
        same=all((out/name).read_bytes()==(CYCLE/name).read_bytes() for name in EXPECTED)
        assert same
        env=os.environ.copy();env['R040282_CACHE']=str(CACHE)
        env['R040282_MATHLIB']=str(Path(env.get('R040282_MATHLIB',CACHE/'mathlib4')).expanduser().resolve())
        env['R040282_LEAN_BIN']=str(Path(env.get('R040282_LEAN_BIN',CACHE/'lean-4.33.1-linux/bin/lean')).expanduser().absolute())
        env['R040282_AIEFS_ENGINE']=str(Path(env.get('R040282_AIEFS_ENGINE',CYCLE/'source_state/main/aief_experiment_engine_v1.py')).expanduser().resolve())
        env['PYTHONOPTIMIZE']='0';env['PYTHONDONTWRITEBYTECODE']='1'
        print('Running the proof checker extracted from the standalone note.',flush=True)
        run=subprocess.run([sys.executable,str(out/'check_cycle.py')],cwd=out,env=env,text=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900)
        (CYCLE/'standalone_reproduction.log').write_text(run.stdout);print(run.stdout,end='',flush=True)
        assert run.returncode==0
        proof=json.loads((out/'cycle_results.json').read_text())
        assert proof['control_count']==17 and proof['all_controls_passed']
        for name,value in proof['source_files'].items():assert value==hashlib.sha256((out/name).read_bytes()).hexdigest()
        assert proof['harness_sha256']==hashlib.sha256((out/'check_cycle.py').read_bytes()).hexdigest()
        shutil.copyfile(out/'cycle_results.json',CYCLE/'standalone_results.json')
        destination=CYCLE/'standalone_checks'
        if destination.exists():shutil.rmtree(destination)
        shutil.copytree(out/'checks',destination)
        print('Running the extracted source checker with the reviewed public engine.',flush=True)
        source_run=subprocess.run([sys.executable,str(out/'compare_source.py')],cwd=out,env=env,text=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
        (CYCLE/'standalone_source.log').write_text(source_run.stdout)
        assert source_run.returncode==0,source_run.stdout
        source=json.loads((out/'source_comparison_results.json').read_text())
        assert source['case_count']==24 and source['all_passed'] and source['maximum_absolute_error']<=5e-15
        shutil.copyfile(out/'source_comparison_results.json',CYCLE/'standalone_source_results.json')
    manifest={'report':NAME,'critical_files':sorted(EXPECTED),'critical_blocks_match_sources':same,
        'runner_exit':run.returncode,'source_runner_exit':source_run.returncode,
        'controls':proof['control_count'],'all_control_outcomes_repeated':proof['all_controls_passed'],
        'source_case_count':source['case_count'],'all_source_comparisons_repeated':source['all_passed'],
        'scope':'Local self-reproduction with public dependencies, not independent review, publication, or integration'}
    (CYCLE/'standalone_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Single-note proof and controlled-source reproduction passed.',flush=True)


if __name__=='__main__':main()
