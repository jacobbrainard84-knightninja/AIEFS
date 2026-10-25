#!/usr/bin/env bash
# Run from the AIEFS repo root:  bash "AI Agent Audits/evidence/run_all.sh"
# Python env used by the audit: see ENVIRONMENT.md (Python 3.13.5, numpy 2.5.1, scipy 1.18.1).
# Round 3 (2026-10-24): every script writes into a fresh temporary directory (AIEF_AUDIT_OUT=$(mktemp -d)); the
# committed results/ are NOT touched. At the end every committed result file is compared byte-for-byte with the
# fresh one, and the script exits nonzero if any step failed or any committed result differs or is missing.
#   UPDATE=1 bash ".../run_all.sh"   additionally copies the fresh results and logs into results/ and logs/.
#   PY=/path/to/python               selects the interpreter (default: python).
# Heavy steps (kappa_tw, kappa_cycle_kernel, delay_paired, omega_*, repro13) take about 0.5-6 min each on 7 cores;
# about 25 min total. Pool(7) is used; peak RAM about 3 GB.
set -uo pipefail
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BR="$(realpath -s --relative-to="$PWD" "$B")"
export PYTHONDONTWRITEBYTECODE=1
PY="${PY:-python}"
T="$(mktemp -d)"; export AIEF_AUDIT_OUT="$T"; mkdir -p "$T/logs"
FAIL=0
run(){ name=$1; shift; s=$1; shift
  echo "== $name: $(basename "$PY") $BR/scripts/$s $*" > "$T/logs/$name.log"
  "$PY" "$B/scripts/$s" "$@" >> "$T/logs/$name.log" 2>&1; rc=$?
  echo "exit $rc" >> "$T/logs/$name.log"
  # keep logs free of local absolute paths
  sed -i -e "s#$B#$BR#g" -e "s#$PWD/##g" "$T/logs/$name.log"
  if [ $rc -ne 0 ]; then echo "FAILED: $name (exit $rc)"; FAIL=1; else echo "ok: $name"; fi; }
# fast (seconds)
run mathcheck          mathcheck.py
run gate_idempotence   gate_idempotence.py
run freq_predictor     freq_predictor.py
run kappa_rows         kappa_rows.py
run matched_phase_check matched_phase_check.py
run ablation14_topology ablation14_topology.py
run archived13_closedform archived13_closedform.py
run evolution_checks   evolution_checks.py
# heavy
run kappa_tw           kappa_tw.py all
run analyze_kappa_tw   analyze_kappa_tw.py
run kappa_cycle_kernel kappa_cycle_kernel.py
run analyze_kappa_cycle_kernel analyze_kappa_cycle_kernel.py
run delay_paired       delay_paired_heldout.py
run analyze_delay      analyze_delay_heldout.py
run frozen_topology_check frozen_topology_check.py
run omega_random       omega_random.py
run omega_multistab    omega_multistab.py
run repro13            repro13.py
# Lean (optional; needs elan + network for the mathlib cache): bash "$BR/scripts/lean_check.sh"
echo "== comparing committed $BR/results with fresh outputs in the temp dir"
DIFF=0
for f in "$B"/results/*; do
  n="$(basename "$f")"
  if [ ! -f "$T/$n" ]; then echo "MISSING in fresh run: $n"; DIFF=1
  elif ! cmp -s "$f" "$T/$n"; then echo "DIFFERS: $n"; DIFF=1; fi
done
for f in "$T"/*; do [ -f "$f" ] && [ ! -f "$B/results/$(basename "$f")" ] && echo "NEW (not committed): $(basename "$f")" && DIFF=1; done
if [ "${UPDATE:-0}" = 1 ]; then
  mkdir -p "$B/results" "$B/logs"
  for f in "$T"/*; do [ -f "$f" ] && cp "$f" "$B/results/"; done
  cp "$T"/logs/*.log "$B/logs/"; echo "UPDATE=1: copied fresh results and logs into $BR"
fi
echo "fresh outputs kept in $T"
[ $FAIL -eq 0 ] && [ $DIFF -eq 0 ] && echo "ALL OK: every step exited 0 and every committed result is byte-identical" && exit 0
[ $FAIL -ne 0 ] && echo "SOME STEPS FAILED"; [ $DIFF -ne 0 ] && echo "RESULTS DIFFER FROM COMMITTED"; exit 1
