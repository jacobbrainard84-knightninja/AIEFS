#!/usr/bin/env bash
# Usage: build_bundle.sh MAIN_ROOT INBOX_RESEARCHER_ROOT modules.tsv
# Run only in a fresh disposable sparse checkout with mathlib cache installed.
set -euo pipefail
main=$(cd "$1" && pwd)
inbox=$(cd "$2" && pwd)
map=$(realpath "$3")
cd "$main"
test "$(git rev-parse HEAD)" = 7865ab19282ceae49df9aa70b396d60ada38d3c2
test -z "$(git status --porcelain --untracked-files=no)"
cd lean/AIEFGateCore
modules=()
while IFS=$'\t' read -r module path; do
  test ! -e "AIEFGateCore/$module.lean"
  test ! -e ".lake/build/lib/lean/AIEFGateCore/$module.olean"
  cp "$inbox/$path" "AIEFGateCore/$module.lean"
  cmp "$inbox/$path" "AIEFGateCore/$module.lean"
  modules+=("AIEFGateCore.$module")
  printf 'copied %s: ' "$module"; sha256sum "AIEFGateCore/$module.lean"
done < "$map"
cmp "$inbox/AIEFS_CausalEMATracking/CausalEMATracking.lean" \
    "$inbox/2026-09-11_AIEFS_EMAFiniteSum/CausalEMATracking.lean"
echo 'Dependency duplicate CausalEMATracking: byte-identical'
# Sequential first builds avoid concurrent Lean memory pressure. Every candidate
# is new in this one checkout; dependencies from main/mathlib may already be built.
for m in "${modules[@]}"; do
  echo "=== Fresh target $m ==="
  unshare -rn lake build "$m"
done
echo '=== Combined target invocation ==='
unshare -rn lake build "${modules[@]}"
# Import all twelve simultaneously, without editing a root import or adding theorems.
test ! -e AIEFGateCore/BundleCheck.lean
for m in "${modules[@]}"; do printf 'import %s\n' "$m"; done > AIEFGateCore/BundleCheck.lean
echo '=== Simultaneous import check ==='
unshare -rn lake env lean AIEFGateCore/BundleCheck.lean
echo '=== Tracked main files unchanged ==='
git diff --exit-code
echo 'BUNDLE BUILD AND IMPORT CHECK EXIT 0'
