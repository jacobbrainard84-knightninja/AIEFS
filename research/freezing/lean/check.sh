#!/usr/bin/env bash
# Checks the Lean formalisation of the freezing core (scalar comparison + per-edge OFF/ON).
# The source lives in the separate Lake project lean/AIEFFreezeCore (Mathlib only); this wrapper
# runs that project's 7-step check (toolchain, pins, imports, cache, build with 0 warnings,
# forbidden markers, axiom audit). Pass SKIP_CACHE=1 to skip `lake exe cache get` when offline.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$HERE/../../../lean/AIEFFreezeCore/check_lean_freeze.sh" "$HERE/../../../lean/AIEFFreezeCore"
