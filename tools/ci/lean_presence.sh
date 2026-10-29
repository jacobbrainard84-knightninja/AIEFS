#!/usr/bin/env bash
# lean_presence.sh -- presence gate for one row of the .github/workflows/lean.yml matrix.
#
# Usage:  bash tools/ci/lean_presence.sh PROJECT_DIR CHECK_SCRIPT REQUIRED
#   PROJECT_DIR   Lake project directory relative to the repo root, e.g. lean/AIEFProofsKn
#   CHECK_SCRIPT  its check script file name, e.g. check_lean_kn.sh
#   REQUIRED      "true" or "false"
# Writes present=true|false to $GITHUB_OUTPUT (stdout if unset) and notes to $GITHUB_STEP_SUMMARY.
#
#   directory missing, REQUIRED=false             -> ::warning::, present=false, exit 0 (skip)
#   directory missing, REQUIRED=true              -> ::error::, exit 1
#   directory present, lakefile + script present  -> present=true, exit 0
#   directory present, lakefile or script missing -> ::error::, exit 1 (never a silent skip:
#                                                    deleting/renaming the check cannot disable it)
# A lakefile is lakefile.toml or lakefile.lean. Run from the repository root.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "::error::usage: lean_presence.sh PROJECT_DIR CHECK_SCRIPT REQUIRED(true|false)"
  exit 2
fi
dir=$1 script=$2 required=$3
case "$required" in true|false) ;; *) echo "::error::REQUIRED must be true or false, got '$required'"; exit 2 ;; esac
emit() {  # step output: $GITHUB_OUTPUT on Actions, plain stdout elsewhere
  if [ -n "${GITHUB_OUTPUT:-}" ]; then echo "$1" >> "$GITHUB_OUTPUT"; else echo "$1"; fi
}
note() {  # job summary line (Actions only)
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then echo "$1" >> "$GITHUB_STEP_SUMMARY"; fi
}

if [ ! -d "$dir" ]; then
  if [ "$required" = "true" ]; then
    echo "::error::$dir is missing but required"
    exit 1
  fi
  emit "present=false"
  echo "::warning::$dir is not on this branch; skipping its Lean check"
  note "SKIPPED: $dir is not on this branch (required: false)"
  exit 0
fi

missing=()
if [ ! -f "$dir/lakefile.toml" ] && [ ! -f "$dir/lakefile.lean" ]; then
  missing+=("lakefile.toml or lakefile.lean")
fi
if [ ! -f "$dir/$script" ]; then
  missing+=("$script")
fi
if [ "${#missing[@]}" -gt 0 ]; then
  joined=$(printf '%s, ' "${missing[@]}")
  echo "::error::$dir exists but is missing ${joined%, }; the Lean check cannot be skipped for a present project"
  exit 1
fi
emit "present=true"
