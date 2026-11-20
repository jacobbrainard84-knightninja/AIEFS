"""Execute the exact critical files extracted from the single cycle-004 Markdown.
Public Lean/Mathlib and the reviewed public engine are external dependencies.
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

ROOT=Path(__file__).resolve().parent
REPORT=ROOT.parent/'2026-09-04_researcher040282_004_complex-ema.md'
CACHE=Path(os.environ.get('R040282_CACHE',Path.home()/'.cache/researcher040282')).expanduser().resolve()
FILES={'GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean','check_cycle.py','compare_source.py'}


def main():
    if not __debug__:raise SystemExit('Assertions must be enabled')
    for name in ['standalone_manifest.json','standalone_results.json','standalone_source_results.json']:(ROOT/name).unlink(missing_ok=True)
    pattern=r"<!-- FILE: ([A-Za-z_][A-Za-z0-9_]*\.(?:lean|py)) -->\n```[^\n]*\n(.*?)\n```"
    matches=re.findall(pattern,REPORT.read_text(),re.S);assert len(matches)==7 and set(dict(matches))==FILES
    CACHE.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r040282-c004-standalone-',dir=CACHE) as tmp:
        out=Path(tmp)
        for name,content in matches:(out/name).write_text(content+'\n')
        same=all((out/name).read_bytes()==(ROOT/name).read_bytes() for name in FILES);assert same
        env=os.environ.copy();env['R040282_CACHE']=str(CACHE)
        env['R040282_MATHLIB']=str(Path(env.get('R040282_MATHLIB',CACHE/'mathlib4')).expanduser().resolve())
        env['R040282_LEAN_BIN']=str(Path(env.get('R040282_LEAN_BIN',CACHE/'lean-4.33.1-linux/bin/lean')).expanduser().absolute())
        env['R040282_AIEFS_ENGINE']=str(Path(env.get('R040282_AIEFS_ENGINE',ROOT/'source_state/main/aief_experiment_engine_v1.py')).expanduser().resolve())
        env['PYTHONOPTIMIZE']='0';env['PYTHONDONTWRITEBYTECODE']='1'
        print('Running extracted proof/exact checker in a fresh directory.',flush=True)
        run=subprocess.run([sys.executable,str(out/'check_cycle.py')],cwd=out,env=env,text=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900)
        (ROOT/'standalone_reproduction.log').write_text(run.stdout);print(run.stdout,end='',flush=True)
        assert run.returncode==0
        proof=json.loads((out/'cycle_results.json').read_text());assert proof['control_count']==18 and proof['all_controls_passed']
        assert all(value==hashlib.sha256((out/name).read_bytes()).hexdigest() for name,value in proof['source_files'].items())
        assert proof['harness_sha256']==hashlib.sha256((out/'check_cycle.py').read_bytes()).hexdigest()
        shutil.copyfile(out/'cycle_results.json',ROOT/'standalone_results.json')
        destination=ROOT/'standalone_checks'
        if destination.exists():shutil.rmtree(destination)
        shutil.copytree(out/'checks',destination)
        print('Running extracted actual-source checker with explicit reviewed engine.',flush=True)
        source_run=subprocess.run([sys.executable,str(out/'compare_source.py')],cwd=out,env=env,text=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
        (ROOT/'standalone_source.log').write_text(source_run.stdout);assert source_run.returncode==0,source_run.stdout
        source=json.loads((out/'source_comparison_results.json').read_text())
        assert source['case_count']==34 and source['compute_R_calls']==253 and source['all_passed']
        assert len(source['sensitivity_controls'])==6 and len(source['configuration_controls'])==1
        assert source['checker_sha256']==hashlib.sha256((out/'compare_source.py').read_bytes()).hexdigest()
        shutil.copyfile(out/'source_comparison_results.json',ROOT/'standalone_source_results.json')
    manifest={'report':REPORT.name,'critical_files':sorted(FILES),'critical_blocks_match_sources':same,
        'runner_exit':run.returncode,'source_runner_exit':source_run.returncode,'controls':18,'all_control_outcomes_repeated':True,
        'source_case_count':34,'source_calls':253,'source_wrong_model_detections':6,'expected_configuration_rejections':1,
        'scope':'Local single-note self-reproduction with public dependencies, not independent review/publication/integration'}
    (ROOT/'standalone_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Single-note proof and actual-source component reproduction passed.',flush=True)


if __name__=='__main__':main()
