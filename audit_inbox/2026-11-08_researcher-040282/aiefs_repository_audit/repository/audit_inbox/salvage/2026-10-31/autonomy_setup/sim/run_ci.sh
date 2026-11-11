#!/bin/bash
# Replays the repo-checks.yml steps locally in a checkout ($1) against base ($2).
cd "$1" || exit 2
export GITHUB_ACTIONS=true
r=0
step(){ echo; echo "### $1"; shift; "$@"; rc=$?; echo "### exit $rc"; [ $rc -ne 0 ] && r=1; }
step "ci-tool-tests" python3 -m unittest discover -s tools/ci/tests
step "claims-lint" python3 tools/ci/lint_claims.py
step "hygiene (changed vs $2, --pii)" python3 tools/ci/hygiene_scan.py --base "$2" --pii
step "hygiene (full)" python3 tools/ci/hygiene_scan.py
step "manifest" python3 tools/ci/check_manifest.py
echo; echo "OVERALL: $([ $r -eq 0 ] && echo PASS || echo FAIL)"; exit $r
