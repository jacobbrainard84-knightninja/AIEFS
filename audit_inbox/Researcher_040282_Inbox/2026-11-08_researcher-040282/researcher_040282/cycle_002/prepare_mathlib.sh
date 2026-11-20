#!/usr/bin/env bash
# Public read-only dependency setup in an excluded disposable cache.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CACHE="$(cd "$ROOT/../.." && pwd)/.cache/researcher040282"
export PATH="$CACHE/lean-4.33.1-linux/bin:$PATH"
export GIT_TERMINAL_PROMPT=0
MATHLIB="$CACHE/mathlib4"
if [ ! -d "$MATHLIB/.git" ]; then
  git clone --depth 1 --branch v4.33.1 https://github.com/leanprover-community/mathlib4.git "$MATHLIB"
fi
expected="0df444a360eaa60ab8c11dca51a86af692955474"
actual="$(git -C "$MATHLIB" rev-parse HEAD)"
[ "$actual" = "$expected" ] || { echo 'Unexpected mathlib source'; exit 1; }
cd "$MATHLIB"
lean --version
lake exe cache get \
  Mathlib/Algebra/Order/BigOperators/Group/Finset.lean \
  Mathlib/Algebra/BigOperators/Ring/Finset.lean \
  Mathlib/Algebra/Order/Field/Basic.lean \
  Mathlib/Data/Real/Basic.lean \
  Mathlib/Tactic/NormNum.lean
