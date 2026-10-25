"""Response point 6 (round 2), corrected in round 3 (response-2 point 3). Recompute the matched-phase seed-level contrasts
from the SUCCESSFUL full-cohort output test_output/ (40/40 seeds) and record its provenance.

Provenance (round-3 correction): the earlier version of this script attached
aief_1_4_matched_phase_memory_ablation/analysis_manifest.json as the 'canonical' manifest. That directory is a FAILED
1-seed partial run (anchor validation failed, run_scope=partial) and is NOT the source of the numbers. The numbers come from
test_output/, whose own analysis_manifest.json reports a successful full cohort. This script now
  * reads the test_output manifest's status/validation fields (absolute paths in it are reduced to repo-relative names),
  * checks the source and dependency sha256 recorded there against the repo files,
  * hashes test_output/analysis_manifest.json and every CSV it consumes,
  * records the other directory only as 'failed_partial_run_elsewhere' with its status fields."""
import sys, os, json, hashlib, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
D = 'test_output'
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
rel = lambda p: p.split('/SSRH/', 1)[1] if '/SSRH/' in p else os.path.basename(p)   # strip the author's absolute prefix
consumed = [f'{D}/matched_phase_paired_contrasts.csv', f'{D}/matched_phase_seed_status.csv']
pc = pd.read_csv(consumed[0], dtype={'seed': str}); st = pd.read_csv(consumed[1], dtype={'seed': str})
rng = np.random.default_rng(0); out = {}; warn = []
for oc in ['P_mean_late', 'Weighted_similarity_late', 'Retention_selected_late', 'Emergence_unselected_late', 'D_B_final', 'Minimum_similarity']:
    w = pc[pc.outcome == oc].pivot(index='seed', columns='reset_source', values='contrast')
    sv = 0.5 * (w.iloc[:, 0] + w.iloc[:, 1]); v = sv.values
    bs = [rng.choice(v, len(v)).mean() for _ in range(10000)]
    out[oc] = dict(n=len(v), mean=float(v.mean()), ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                   n_pos=int((v > 0).sum()), n_neg=int((v < 0).sum()), per_source_means={k: float(w[k].mean()) for k in w.columns})
out['seed_status_counts'] = st.iloc[:, 1].value_counts().to_dict() if st.shape[1] > 1 else {}
M = json.load(open(f'{D}/analysis_manifest.json'))
src_ok = {rel(M['source']['path']): sha(rel(M['source']['path'])) == M['source']['sha256']}
src_ok |= {rel(v['path']): sha(rel(v['path'])) == v['sha256'] for v in M['dependencies'].values()}
out['provenance'] = dict(
    source_directory=D,
    manifest=dict(path=f'{D}/analysis_manifest.json', sha256=sha(f'{D}/analysis_manifest.json'),
                  analysis=M.get('analysis'), version=M.get('version'), run_metadata=M.get('run_metadata'),
                  success_count=M.get('success_count'), failure_count=M.get('failure_count'), failed_seeds=M.get('failed_seeds'),
                  freezeable=M.get('freezeable'),
                  validation={k: v for k, v in M.get('validation', {}).items() if k != 'split_state_immutability'}
                             | {'split_state_immutability_all_passed': M.get('validation', {}).get('split_state_immutability', {}).get('all_passed')},
                  frozen_authorities={k: dict(path=rel(v['path']), sha256=v['sha256']) for k, v in M['frozen_authorities'].items()},
                  note='absolute paths in the manifest were reduced to repo-relative names'),
    source_and_dependency_sha256_match_repo=src_ok,
    frozen_authorities_sha256_match_repo={k: sha(rel(v['path'])) == v['sha256'] for k, v in M['frozen_authorities'].items() if os.path.exists(rel(v['path']))},
    consumed_files={p: sha(p) for p in consumed})
F = json.load(open('aief_1_4_matched_phase_memory_ablation/analysis_manifest.json'))
out['failed_partial_run_elsewhere'] = dict(path='aief_1_4_matched_phase_memory_ablation/analysis_manifest.json',
    sha256=sha('aief_1_4_matched_phase_memory_ablation/analysis_manifest.json'),
    status=F.get('status'), run_scope=F.get('run_scope'), seeds_requested=len(F.get('seeds_requested', [])),
    anchor_failed=F.get('anchor_failed'), full_cohort=F.get('full_cohort'),
    note='a failed 1-seed partial run; NOT the source of the numbers above (round-3 correction)')
if not all(src_ok.values()): warn.append('source/dependency sha256 mismatch vs repo')
for k, v in out.items(): print(k, v)
dump('matched_phase_check.json', out, status='ok_with_warnings' if warn else 'ok', warnings=warn)
