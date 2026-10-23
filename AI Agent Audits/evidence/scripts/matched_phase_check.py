"""NEW (response round). Point 6: recompute matched-phase seed-level contrasts from test_output CSVs and check against
test_output/matched_phase_report.txt; record provenance status of the canonical output directory."""
import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
pc = pd.read_csv('test_output/matched_phase_paired_contrasts.csv', dtype={'seed': str})
st = pd.read_csv('test_output/matched_phase_seed_status.csv', dtype={'seed': str})
rng = np.random.default_rng(0); out = {}
for oc in ['P_mean_late', 'Weighted_similarity_late', 'Retention_selected_late', 'Emergence_unselected_late', 'D_B_final', 'Minimum_similarity']:
    w = pc[pc.outcome == oc].pivot(index='seed', columns='reset_source', values='contrast')
    sv = 0.5 * (w.iloc[:, 0] + w.iloc[:, 1]); v = sv.values
    bs = [rng.choice(v, len(v)).mean() for _ in range(10000)]
    out[oc] = dict(n=len(v), mean=float(v.mean()), ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                   n_pos=int((v > 0).sum()), n_neg=int((v < 0).sum()), per_source_means={k: float(w[k].mean()) for k in w.columns})
out['seed_status_counts'] = st.iloc[:, 1].value_counts().to_dict() if st.shape[1] > 1 else {}
out['canonical_dir_manifest'] = json.load(open('aief_1_4_matched_phase_memory_ablation/analysis_manifest.json'))
for k, v in out.items(): print(k, v)
dump('matched_phase_check.json', out)
