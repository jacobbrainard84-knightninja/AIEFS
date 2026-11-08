"""Independent branch audit: actual repository imports, no dependency stand-ins.

Known-defect tests use strict expected-failure markers so controls can also run.
Use pytest --runxfail to expose their actual failing assertions. Git tests only
operate on temporary LOCAL bare repositories; they never contact GitHub.
"""
from __future__ import annotations

import csv
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent
REPO = Path(os.environ.get('AIEFS_AUDIT_REPO', ROOT / 'repository')).resolve()
PKG = REPO / 'AIEF_Experiments/aief_modular_platform_v1_analysis_v4'
sys.path[:0] = [str(PKG), str(REPO)]
import AIEF_1_4_Twindow_sensitivity_analysis_v4 as analysis
import aief_experiment_engine_v1 as engine
from aief_modular.oracle import _compare_condition_coverage
from aief_modular.validation import exact_equal_with_nan


class GitWorld:
    def __init__(self, root):
        self.root = root
        self.remote = root / 'origin.git'
        self.mine = root / 'mine'
        self.other = root / 'other'
        self.env = os.environ.copy()
        home = root / 'isolated-home'; home.mkdir()
        self.env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM='1',
                        GIT_AUTHOR_NAME='Audit fixture',GIT_COMMITTER_NAME='Audit fixture',
                        GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_EMAIL='fixture@example.invalid')
        self.call(['git','init','--bare','--initial-branch=main',str(self.remote)],root)
        self.call(['git','clone',str(self.remote),str(self.mine)],root)
        self.git(self.mine,'config','user.name','Audit fixture')
        self.git(self.mine,'config','user.email','fixture@example.invalid')
        (self.mine / '.gitignore').write_text('*.log\n')
        (self.mine / 'README.md').write_text('initial\n')
        self.git(self.mine,'add','.gitignore','README.md')
        self.git(self.mine,'commit','-m','fixture base')
        self.git(self.mine,'push','origin','main')
        self.call(['git','clone',str(self.remote),str(self.other)],root)

    def call(self,args,cwd,check=True):
        return subprocess.run(args,cwd=cwd,env=self.env,stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,check=check)

    def git(self,where,*args):
        return self.call(['git',*args],where).stdout.strip()

    def remote_head(self):
        return self.git(self.root,'--git-dir='+str(self.remote),'rev-parse','main')

    def script(self,name,*args):
        return self.call(['bash',str(REPO/'tools/sync'/name),*args],self.mine,check=False)

    def upstream_ignored_collision(self):
        (self.mine / 'experiment.log').write_text('IRREPLACEABLE LOCAL OBSERVATIONS\n')
        (self.other / 'experiment.log').write_text('UPSTREAM CONTENT\n')
        self.git(self.other,'add','-f','experiment.log')
        self.git(self.other,'commit','-m','upstream adds ignored filename')
        self.git(self.other,'push','origin','main')


@pytest.fixture
def world(tmp_path):
    return GitWorld(tmp_path)


def test_downloader_rejects_ignored_collision_as_positive_control(world):
    world.upstream_ignored_collision()
    result=world.script('download_new.sh')
    assert result.returncode != 0
    assert (world.mine/'experiment.log').read_text() == 'IRREPLACEABLE LOCAL OBSERVATIONS\n'


@pytest.mark.xfail(strict=True,reason='uploader pull can silently overwrite an ignored local experiment file')
def test_uploader_preserves_ignored_file_when_upstream_now_tracks_it(world):
    world.upstream_ignored_collision()
    result=world.script('upload_new.sh','--yes')
    assert result.returncode == 0, result.stdout
    assert (world.mine/'experiment.log').read_text() == 'IRREPLACEABLE LOCAL OBSERVATIONS\n'


def test_uncommitted_secret_shaped_content_is_blocked_as_control(world):
    # Deliberately invalid, synthetic credential-shaped string; not a real key.
    (world.mine/'calibration_notes.txt').write_text('ghp_' + 'A'*40 + '\n')
    before=world.remote_head()
    result=world.script('upload_new.sh','--yes')
    assert result.returncode == 0, result.stdout
    assert world.remote_head() == before
    assert 'contents look like a key/token' in result.stdout


@pytest.mark.xfail(strict=True,reason='unpublished committed blobs are not content-scanned')
def test_committed_secret_shaped_content_is_also_blocked(world):
    (world.mine/'calibration_notes.txt').write_text('ghp_' + 'A'*40 + '\n')
    world.git(world.mine,'add','calibration_notes.txt')
    world.git(world.mine,'commit','-m','local commit with synthetic credential-shaped contents')
    before=world.remote_head()
    result=world.script('upload_new.sh','--yes')
    assert world.remote_head() == before, 'Uploader advanced local bare remote with credential-shaped committed content'


@pytest.mark.xfail(strict=True,reason='only base-to-tip file differences are scanned, not all blobs sent in commit history')
def test_oversized_blob_deleted_before_tip_is_not_pushed(world):
    (world.mine/'large_scratch.bin').write_bytes(b'x'*(2*1024*1024))
    world.git(world.mine,'add','large_scratch.bin')
    world.git(world.mine,'commit','-m','large intermediate object')
    world.git(world.mine,'rm','large_scratch.bin')
    (world.mine/'README.md').write_text('small current tip\n')
    world.git(world.mine,'add','README.md')
    world.git(world.mine,'commit','-m','remove large object from tip')
    before=world.remote_head()
    result=world.script('upload_new.sh','--yes','--max-size-mb','1')
    assert world.remote_head() == before, 'Uploader sent a 2 MiB historical blob despite its 1 MiB upload limit'


def test_actual_postpositivity_gate_satisfies_conditional_k3_identities():
    branch=importlib.import_module('AIEF_1_4_actual_admissibility_branch_audit')
    base=importlib.import_module('AIEF_1_4_stationarity_perturbation_analysis_updated')
    bridge=importlib.import_module('AIEF_1_4_proposal_equalization_bridge_analysis')
    A,edges=base.incidence_matrix(12)
    capacity=.6333333333333333; epsilon=1e-12
    x=np.zeros(66); x[[25,29,59]]=[.41,.27,.31] # Correct strict branch: x25 > x59 > x29.
    y,info=branch.admissibility_from_nonnegative_proposal(x,np.full(12,capacity),A,edges,epsilon)
    assert tuple(info['winner_code'][[25,29,59]]) == (7,2,7)
    s7=info['scales'][7]
    assert y[25]-y[59] == pytest.approx(s7*(x[25]-x[59]),abs=1e-15)
    sigma=bridge.right_projection_coefficient(x[25],x[29],x[59],capacity,epsilon)
    assert y[59]-y[29] == pytest.approx(sigma*(x[59]-x[29]),abs=1e-15)


@pytest.mark.xfail(strict=True,reason='bridge self-test hardcodes a projected answer for an out-of-branch proposal')
def test_bridge_selftest_fixture_matches_the_implemented_gate():
    branch=importlib.import_module('AIEF_1_4_actual_admissibility_branch_audit')
    base=importlib.import_module('AIEF_1_4_stationarity_perturbation_analysis_updated')
    bridge=importlib.import_module('AIEF_1_4_proposal_equalization_bridge_analysis')
    bridge.synthetic_self_test() # Reports PASS with the following proposal.
    A,edges=base.incidence_matrix(12)
    capacity=.6333333333333333; epsilon=1e-12
    x=np.zeros(66);x[[25,29,59]]=[.41,.31,.27]
    y,info=branch.admissibility_from_nonnegative_proposal(x,np.full(12,capacity),A,edges,epsilon)
    assumed_y25=info['scales'][7]*x[25]
    assert y[25] == pytest.approx(assumed_y25,rel=0,abs=1e-14)


def test_saved_grid_hold_nonboundary_control():
    c=np.zeros(640,bool);c[32:69]=True
    assert analysis._held_index(analysis.EXPECTED_SAMPLE_TIMES,c,17.5) == 32


@pytest.mark.xfail(strict=True,reason='addition/searchsorted can reject a true block spanning exactly 17.5 saved-grid units')
def test_saved_grid_hold_exact_boundary_translation():
    c=np.zeros(640,bool);c[32:68]=True
    assert analysis._held_index(analysis.EXPECTED_SAMPLE_TIMES,c,17.5) == 32


@pytest.mark.xfail(strict=True,reason='empirical percentile bootstrap interval collapses at a zero-event sample boundary')
def test_rate_interval_does_not_assert_zero_population_uncertainty():
    seeds=tuple(str(i) for i in range(40))
    frame=pd.DataFrame({'seed':seeds,'group':'one','value':0.})
    result=analysis.pointwise_summary(frame,group_columns=('group',),value_column='value',
                                      seeds=seeds,draws=analysis.bootstrap_draws(seeds,2000,91)).iloc[0]
    assert result.pointwise_ci_upper > 0


def test_oracle_rejects_changed_condition_coverage(tmp_path):
    left=tmp_path/'left.csv';right=tmp_path/'right.csv'
    left.write_text('seed,rho,status\n10,0.5,success\n')
    right.write_text('seed,rho,status\n11,0.5,success\n')
    errors=[];_compare_condition_coverage(left,right,errors)
    assert errors


@pytest.mark.xfail(strict=True,reason='set-based oracle coverage comparison erases duplicate condition rows')
def test_oracle_rejects_duplicate_condition_records(tmp_path):
    left=tmp_path/'left.csv';right=tmp_path/'right.csv'
    left.write_text('seed,rho,status\n10,0.5,success\n10,0.5,success\n')
    right.write_text('seed,rho,status\n10,0.5,success\n')
    errors=[];_compare_condition_coverage(left,right,errors)
    assert errors


def test_modular_complex_nan_comparator_rejects_changed_finite_component():
    a=np.array([complex(float('nan'),1.)]);b=np.array([complex(float('nan'),99.)])
    assert not exact_equal_with_nan(a,b)


@pytest.mark.xfail(strict=True,reason='engine complex NaN mask hides a changed finite real/imaginary component')
def test_engine_complex_nan_comparator_rejects_changed_finite_component():
    a=np.array([complex(float('nan'),1.)]);b=np.array([complex(float('nan'),99.)])
    assert not engine.exact_array_equal_with_nan(a,b)


def test_identity_checks_reject_false_and_nan_inputs():
    channel=importlib.import_module('aief_1_4_two_channel_alignment_v5')
    correct=channel.test_proposal_identity(np.array([2.]),1.,np.array([1.]),1.,np.array([1.]))
    wrong=channel.test_proposal_identity(np.array([3.]),1.,np.array([1.]),1.,np.array([1.]))
    missing=channel.test_proposal_identity(np.array([np.nan]),1.,np.array([1.]),1.,np.array([1.]))
    assert correct['identity_passes']
    assert not wrong['identity_passes']
    assert not missing['identity_passes']


def test_complete_graph_lineality_dimensions_by_exact_rational_rank():
    import sympy as sp
    expected={3:0,4:2,5:5,6:9,7:14,8:20}
    for n,dimension in expected.items():
        edges=[(i,j) for i in range(n) for j in range(i+1,n)]
        A=sp.zeros(n,len(edges))
        for k,(i,j) in enumerate(edges):A[i,k]=A[j,k]=1
        assert len(edges)-A.rank() == dimension


def test_row_sum_fiber_identity_and_nonfiber_negative_control():
    branch=importlib.import_module('AIEF_1_4_actual_admissibility_branch_audit')
    base=importlib.import_module('AIEF_1_4_stationarity_perturbation_analysis_updated')
    A,edges=base.incidence_matrix(4)
    x=np.full(6,.4);caps=np.full(4,.6333333333333333)
    # K4 alternating four-cycle: each node's incident perturbations sum to zero.
    h=np.zeros(6)
    for pair,value in [((0,1),1),((1,2),-1),((2,3),1),((0,3),-1)]:
        k=next(k for k,(i,j) in enumerate(zip(*edges)) if (int(i),int(j))==pair)
        h[k]=value
    h*=.01
    np.testing.assert_allclose(A@h,0,atol=1e-15)
    y,info=branch.admissibility_from_nonnegative_proposal(x,caps,A,edges,1e-12)
    yh,_=branch.admissibility_from_nonnegative_proposal(x+h,caps,A,edges,1e-12)
    np.testing.assert_allclose(yh-y,info['edge_scales']*h,atol=1e-15,rtol=0)
    bad=h.copy();bad[0]+=.02
    yb,_=branch.admissibility_from_nonnegative_proposal(x+bad,caps,A,edges,1e-12)
    assert np.linalg.norm((yb-y)-info['edge_scales']*bad) > 1e-5
