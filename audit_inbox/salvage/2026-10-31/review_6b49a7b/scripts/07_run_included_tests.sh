#!/usr/bin/env bash
# Time-boxed run of the small self-tests shipped inside zip 019fb8fc, on a COPY (scratch/run_copy).
# Logs: results/run_logs/*.log. Each command capped at 120 s.
set -u
cd "$(dirname "$0")/.."
SRC=scratch/zips/workspace-019fb8fc-d3d9-784a-82a5-03d4ec3f136c
rm -rf scratch/run_copy && mkdir -p scratch/run_copy results/run_logs && cp "$SRC"/*.py scratch/run_copy/
cd scratch/run_copy
for t in test_aief.py test_alignment.py test_alignment_v2.py test_alignment_v3.py test_phase_cancellation.py; do
  timeout 120 python3 "$t" > ../../results/run_logs/${t%.py}.log 2>&1; echo "$t exit=$?"
done
for s in aief_1_4_phase_cancellation_analyzer.py aief_1_4_two_channel_alignment_v5.py aief_1_4_two_channel_alignment_v2.py; do
  timeout 120 python3 "$s" --self-test > ../../results/run_logs/${s%.py}_selftest.log 2>&1; echo "$s --self-test exit=$?"
done
