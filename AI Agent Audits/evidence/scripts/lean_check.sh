#!/usr/bin/env bash
# Run from the AIEFS repo root: bash "AI Agent Audits/evidence/scripts/lean_check.sh"
# Builds lean/AIEFProofs as committed (expected to FAIL on a missing import), then a copy with the
# dangling import line removed (expected to succeed). Works on a temporary copy; the repo is not modified.
set -uo pipefail
B="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T="$(mktemp -d)"; cp -r lean/AIEFProofs "$T/"; cd "$T/AIEFProofs"
lake exe cache get > /dev/null 2>&1; echo "CACHE_EXIT $?"
{ lake build 2>&1; echo "BUILD_EXIT $?"; } | sed "s#$T#<tmpcopy>#g" > "$B/logs/lean_build_original.log"
sed -i '/^import AIEFProofs.ControllerFiberProjector$/d' AIEFProofs.lean
{ lake build 2>&1; echo "BUILD_EXIT $?"; } | sed "s#$T#<tmpcopy>#g" > "$B/logs/lean_build_patched.log"
{ grep -rnw -e sorry -e axiom -e admit AIEFProofs AIEFProofs.lean; echo "GREP_EXIT $? (1 = no sorry/axiom/admit)"; } > "$B/logs/lean_sorry_grep.log"
tail -n 2 "$B/logs/lean_build_original.log" "$B/logs/lean_build_patched.log"
