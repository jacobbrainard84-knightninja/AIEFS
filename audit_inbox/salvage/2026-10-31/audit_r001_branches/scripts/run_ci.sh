#!/bin/bash
# usage: run_ci.sh <repo> [extra_cmd...]   runs the full local CI against base 9d46d9b
cd "$1" || exit 2; shift
PY=/workspace/branches/venv/bin/python
BASE=9d46d9b64580c90d4a9fdaf21635d7453ade9e01
run() { echo "=== $*"; "$@" > $CI_OUT 2>&1; rc=$?; tail -4 $CI_OUT | sed 's/^/    /'; echo "    -> rc=$rc"; [ $rc -eq 0 ] || FAIL="$FAIL|$*"; }
FAIL=""; CI_OUT=$(mktemp)
run $PY tools/ci/lint_claims.py
run $PY tools/ci/hygiene_scan.py
run $PY tools/ci/hygiene_scan.py --base $BASE --pii --private-patterns /workspace/v3/private_literals.txt
run $PY tools/ci/check_manifest.py
run $PY tools/ci/check_modes.py
[ -f tools/ci/check_artifact_pins.py ] && run $PY tools/ci/check_artifact_pins.py
run $PY -m pytest -q tools/ci/tests
run $PY -m unittest discover -s tools/ci/tests
run $PY "AI Agent Audits/evidence/verify_manifest.py" --inputs
for c in "$@"; do run bash -c "$c"; done
echo "FAILURES: ${FAIL:-none}"
