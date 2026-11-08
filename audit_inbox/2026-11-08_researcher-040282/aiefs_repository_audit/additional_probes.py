"""Collect independent quantitative witnesses using actual repository modules.

All Git writes target temporary local bare repositories. No real key is used.
The scientific probes import the unmodified branch, not audit replacements.
"""
from __future__ import annotations
import contextlib
import io
import json
import tempfile
from pathlib import Path

import numpy as np
import test_deep_audit as audit

ROOT=Path(__file__).resolve().parent
REPO=audit.REPO
EVIDENCE=ROOT/'evidence'


def science():
    import AIEF_1_4_proposal_equalization_bridge_analysis as bridge
    import AIEF_1_4_actual_admissibility_branch_audit as actual
    import AIEF_1_4_stationarity_perturbation_analysis_updated as base
    A,edges=base.incidence_matrix(12)
    x=np.zeros(66);x[[25,29,59]]=[.41,.31,.27]
    cap=.6333333333333333;eps=1e-12
    y,info=actual.admissibility_from_nonnegative_proposal(x,np.full(12,cap),A,edges,eps)
    printed=io.StringIO()
    with contextlib.redirect_stdout(printed):returned=bridge.synthetic_self_test()
    result={'bridge_selftest_stdout':printed.getvalue().strip(),'bridge_selftest_return_value':returned,
            'fixture':{'x25':.41,'x29':.31,'x59':.27},
            'node_rows':{str(k):float(info['q'][k]) for k in [2,7,11]},
            'node_scales':{str(k):float(info['scales'][k]) for k in [2,7,11]},
            'actual_winners':info['winner_code'][[25,29,59]].tolist(),'assumed_winners':[7,2,7],
            'left_identity_real_operator_residual':float((y[25]-y[59])-info['scales'][7]*(x[25]-x[59])),
            'actual_y':y[[25,29,59]].tolist(),
            'assumed_y':[info['scales'][7]*x[25],info['scales'][2]*x[29],info['scales'][7]*x[59]],
            'iid_bernoulli_boundary_example':{'n':40,'p':.01,'prob_all_zero':.99**40,
                'coverage_upper_bound':1-.99**40,'exact_95pct_two_sided_upper_at_zero':1-.025**(1/40)}}
    finite={}
    for label,path in [('baseline',REPO/'runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz'),
                       ('S01',REPO/'runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz')]:
        if not path.exists():
            finite[label]={'status':'not available locally'};continue
        with np.load(path,allow_pickle=False) as z:
            keys=[k for k in z.files if np.iscomplexobj(z[k])]
            bad=[k for k in keys if not np.isfinite(z[k]).all()]
            finite[label]={'complex_array_count':len(keys),'nonfinite_complex_arrays':bad}
    result['actual_complex_arrays']=finite
    (EVIDENCE/'independent_scientific_probes.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def shell():
    summary={}
    with tempfile.TemporaryDirectory(prefix='isolated-git-probes-',dir=ROOT) as temp:
        base=Path(temp)
        def world(name):
            directory=base/name;directory.mkdir();return audit.GitWorld(directory)
        w=world('ignored-upload');w.upstream_ignored_collision()
        before=(w.mine/'experiment.log').read_text();result=w.script('upload_new.sh','--yes')
        (EVIDENCE/'upload_ignored_collision.txt').write_text(result.stdout)
        summary['ignored_file_collision']={'exit_code':result.returncode,'original_content':before,
            'content_after':(w.mine/'experiment.log').read_text(),
            'stash_list_after':w.git(w.mine,'stash','list'),
            'local_file_lost':(w.mine/'experiment.log').read_text()!=before}
        w=world('ignored-download');w.upstream_ignored_collision()
        before=(w.mine/'experiment.log').read_text();result=w.script('download_new.sh')
        (EVIDENCE/'download_ignored_collision_control.txt').write_text(result.stdout)
        summary['downloader_positive_control']={'exit_code':result.returncode,
            'original_content_preserved':(w.mine/'experiment.log').read_text()==before}
        w=world('committed-content');fake='ghp_'+'A'*40
        (w.mine/'calibration_notes.txt').write_text(fake+'\n')
        w.git(w.mine,'add','calibration_notes.txt');w.git(w.mine,'commit','-m','synthetic content fixture')
        before=w.remote_head();result=w.script('upload_new.sh','--yes')
        (EVIDENCE/'upload_committed_content.txt').write_text(result.stdout)
        remote_content=w.git(w.root,'--git-dir='+str(w.remote),'show','main:calibration_notes.txt')
        summary['committed_content']={'synthetic_only':True,'exit_code':result.returncode,
            'remote_advanced':w.remote_head()!=before,'remote_contains_synthetic_key_shape':fake in remote_content}
        w=world('historical-size')
        (w.mine/'large_scratch.bin').write_bytes(b'x'*(2*1024*1024))
        w.git(w.mine,'add','large_scratch.bin');w.git(w.mine,'commit','-m','large intermediate blob')
        w.git(w.mine,'rm','large_scratch.bin');(w.mine/'README.md').write_text('small final tip\n')
        w.git(w.mine,'add','README.md');w.git(w.mine,'commit','-m','remove intermediate blob at tip')
        before=w.remote_head();result=w.script('upload_new.sh','--yes','--max-size-mb','1')
        (EVIDENCE/'upload_historical_blob.txt').write_text(result.stdout)
        size=int(w.git(w.root,'--git-dir='+str(w.remote),'cat-file','-s','main~1:large_scratch.bin'))
        summary['historical_oversize_blob']={'exit_code':result.returncode,
            'configured_limit_bytes':1048576,'remote_historical_blob_bytes':size,
            'remote_advanced':w.remote_head()!=before}
    (EVIDENCE/'local_git_safety_probes.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    EVIDENCE.mkdir(exist_ok=True)
    print(json.dumps({'scientific_probes':science(),'local_git_probes':shell()},indent=2))
