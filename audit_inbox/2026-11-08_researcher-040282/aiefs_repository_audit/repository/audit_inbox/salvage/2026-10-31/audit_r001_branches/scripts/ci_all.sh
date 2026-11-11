#!/bin/bash
# usage: ci_all.sh <tree>  : run_ci.sh (copy, private tmp) + strict lint + claims regen + all pytest (fast+slow) + registry validator
T=$(cd "$1" && pwd); PY=/workspace/branches/venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
W=$(cd "$T" && ls -d workspace-019ff86e-*/ 2>/dev/null | head -1)
/workspace/audit_r001_branches/scripts/run_ci.sh "$T" \
 "$PY tools/ci/lint_claims.py --strict" \
 "$PY registry/reconciliation/build_claims_reconciliation.py && git diff --exit-code -- registry/claims.csv registry/lineage_reconciliation.csv" \
 "cd AIEF_Experiments/aief_modular_platform_v1_analysis_v4 && $PY -m pytest -q -p no:cacheprovider" \
 "cd AIEF_Experiments/aief_modular_platform_v1_analysis_v4 && AIEF_RUN_SLOW_TESTS=1 PYTHONPATH='$T' $PY -m pytest -q -p no:cacheprovider -rs" \
 "cd '$W' && $PY -m pytest -q -p no:cacheprovider -rs" \
 "cd '$W' && AIEF_RUN_SLOW_TESTS=1 $PY -m pytest -q -p no:cacheprovider -rs" \
 "$PY audits/engineering/validate_registry_against_tree.py" \
 "$PY audits/engineering/validate_registry_against_tree.py --edited-since 9d46d9b64580c90d4a9fdaf21635d7453ade9e01" \
 "test -z \"\$(git status --porcelain)\" || { git status --porcelain; false; }"
