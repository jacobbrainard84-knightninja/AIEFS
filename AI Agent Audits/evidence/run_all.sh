#!/usr/bin/env bash
# Run from the AIEFS repo root:  bash "AI Agent Audits/evidence/run_all.sh"
# Python env used by the audit: see ENVIRONMENT.md (Python 3.13.5, numpy 2.5.1, scipy 1.18.1).
# Results are written to <evidence>/results, logs to <evidence>/logs.
# Heavy steps (kappa_tw, delay_paired, omega_*, repro13) take about 0.5-5 min each on 7 cores; about 15 min total.
set -euo pipefail
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BR="$(realpath --relative-to="$PWD" "$B")"
export PYTHONDONTWRITEBYTECODE=1
PY="${PY:-python}"
mkdir -p "$B/logs" "$B/results"
run(){ name=$1; shift; s=$1; shift; echo "== $name: $PY $BR/scripts/$s $*" | tee "$B/logs/$name.log"; "$PY" "$B/scripts/$s" "$@" >> "$B/logs/$name.log" 2>&1; echo "exit $?" >> "$B/logs/$name.log"; }
# fast (seconds)
run mathcheck          mathcheck.py
run gate_idempotence   gate_idempotence.py
run freq_predictor     freq_predictor.py
run kappa_rows         kappa_rows.py
run matched_phase      matched_phase_check.py
run ablation14         ablation14_topology.py
run archived13         archived13_closedform.py
# heavy
run kappa_tw           kappa_tw.py all
run analyze_kappa_tw   analyze_kappa_tw.py
run delay_paired       delay_paired_heldout.py
run analyze_delay      analyze_delay_heldout.py
run omega_random       omega_random.py
run omega_multistab    omega_multistab.py
run repro13            repro13.py
# Lean (optional; needs elan + network for the mathlib cache): bash "$BR/scripts/lean_check.sh"
