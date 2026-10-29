#!/usr/bin/env bash
# lean_presence.sh -- presence gate for one row of the .github/workflows/lean.yml matrix.
#
# Usage:  bash tools/ci/lean_presence.sh PROJECT_DIR CHECK_SCRIPT REQUIRED
#   PROJECT_DIR   Lake project directory relative to the repo root, e.g. lean/AIEFProofsKn
#   CHECK_SCRIPT  its check script file name, e.g. check_lean_kn.sh
#   REQUIRED      "true" or "false"
# Writes present=true|false to $GITHUB_OUTPUT (stdout if unset) and notes to $GITHUB_STEP_SUMMARY.
#
#   nothing at PROJECT_DIR, REQUIRED=false       -> ::warning::, present=false, exit 0 (skip)
#   nothing at PROJECT_DIR, REQUIRED=true        -> ::error::, exit 1
#   PROJECT_DIR is a file or a symlink (even a dangling one or one to a directory) -> ::error::, exit 1
#   directory with non-empty lakefile + non-empty script -> present=true, exit 0
#   directory with a lakefile or script missing, empty or not a regular file -> ::error::, exit 1
#                                                   (never a silent skip: deleting, renaming or
#                                                   emptying the check cannot disable it)
# A lakefile is lakefile.toml or lakefile.lean; any that is present must be non-empty.
# Only present=true and present=false are ever emitted. Run from the repository root.
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

# Skip only when NOTHING exists at the path (not even a dangling symlink).
if [ ! -e "$dir" ] && [ ! -L "$dir" ]; then
  if [ "$required" = "true" ]; then
    echo "::error::$dir is missing but required"
    exit 1
  fi
  emit "present=false"
  echo "::warning::$dir is not on this branch; skipping its Lean check"
  note "SKIPPED: $dir is not on this branch (required: false)"
  exit 0
fi
# Something exists: it must be a real directory (a symlink, even to a directory, or a plain file is an error).
if [ -L "$dir" ] || [ ! -d "$dir" ]; then
  echo "::error::$dir exists but is not a plain directory (symlink or file); the Lean check cannot be skipped"
  exit 1
fi

missing=()
# Lakefile: at least one of lakefile.toml / lakefile.lean, and every one present must be a non-empty file.
have_lakefile=0
for lf in lakefile.toml lakefile.lean; do
  if [ -e "$dir/$lf" ] || [ -L "$dir/$lf" ]; then
    if [ -f "$dir/$lf" ] && [ -s "$dir/$lf" ]; then
      have_lakefile=1
    else
      missing+=("a non-empty $lf (it is empty or not a regular file)")
    fi
  fi
done
if [ "$have_lakefile" -eq 0 ] && [ "${#missing[@]}" -eq 0 ]; then
  missing+=("lakefile.toml or lakefile.lean")
fi
# Check script: must be a non-empty regular file (a 0-byte script would "pass" by doing nothing).
if [ ! -f "$dir/$script" ]; then
  missing+=("$script")
elif [ ! -s "$dir/$script" ]; then
  missing+=("a non-empty $script (it is 0 bytes)")
fi
if [ "${#missing[@]}" -gt 0 ]; then
  joined=$(printf '%s, ' "${missing[@]}")
  echo "::error::$dir exists but is missing ${joined%, }; the Lean check cannot be skipped for a present project"
  exit 1
fi
emit "present=true"
