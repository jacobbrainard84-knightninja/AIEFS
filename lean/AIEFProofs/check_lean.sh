#!/usr/bin/env bash
# check_lean.sh -- reproducible, auditable check of the AIEFProofs Lean project.
#
# Usage:   ./check_lean.sh [PROJECT_DIR]      (default: directory containing this script)
# Env:     LOG_DIR=<dir>        where logs go (default: PROJECT_DIR/.check_logs/<UTC timestamp>)
#          SKIP_CACHE=1         skip `lake exe cache get` (offline re-runs)
#          REUSE_BUILD=1        keep existing project build outputs (.lake/build); default is to delete
#                               them so every project module is recompiled from source (Mathlib
#                               oleans in .lake/packages are kept)
#          STRICT_ORPHANS=1     fail (instead of warn) when a .lean file is not reachable from the root
# Exit:    0 = all checks passed; nonzero = first failing step number (see summary.txt).
#
# Steps (each logged to its own file in LOG_DIR):
#   1 toolchain   lean-toolchain pin, elan/lake present, `lean --version` matches the pin
#   2 pins        lake-manifest mathlib rev/inputRev; optional sha256 lock file;
#                 REQUIRED source hash file AIEF_LEAN_SOURCE_SHA256SUMS.txt (every project .lean file
#                 and this script; fails on any mismatch, missing entry or unlisted .lean file).
#                 After an intentional source change, regenerate it from this directory with:
#                   sha256sum AIEFProofs.lean $(find AIEFProofs -name '*.lean' | sort) check_lean.sh \
#                     > AIEF_LEAN_SOURCE_SHA256SUMS.txt
#   3 imports     every `import AIEFProofs.X` in the root resolves to a file; orphan report
#   4 cache       `lake exe cache get` (prebuilt Mathlib oleans)
#   5 build       rm -rf .lake/build (unless REUSE_BUILD=1), then `lake build`; job count, warnings, errors
#   6 markers     no sorry / admit / sorryAx / native_decide / user `axiom` / `unsafe` / `@[implemented_by]`/`@[extern]` in project sources
#   7 axioms      every project declaration depends only on propext, Classical.choice, Quot.sound
#                 (+ human-readable `#print axioms` for every theorem/lemma)
set -uo pipefail

PROJ="$(cd "${1:-$(dirname "${BASH_SOURCE[0]}")}" && pwd)"
LIB="AIEFProofs"
EXPECTED_TOOLCHAIN="leanprover/lean4:v4.33.1"
EXPECTED_MATHLIB_REV="0df444a360eaa60ab8c11dca51a86af692955474"
ALLOWED_AXIOMS="propext Classical.choice Quot.sound"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_DIR="${LOG_DIR:-$PROJ/.check_logs/$TS}"
mkdir -p "$LOG_DIR"
SUMMARY="$LOG_DIR/summary.txt"
: > "$SUMMARY"

say()  { echo "$*" | tee -a "$SUMMARY"; }
fail() { say "FAIL step $1: $2"; say "RESULT: FAIL (logs in $LOG_DIR)"; exit "$1"; }
pass() { say "PASS step $1: $2"; }

cd "$PROJ" || exit 99
export PATH="$HOME/.elan/bin:$PATH"
say "check_lean.sh  project=$(basename "$PROJ")  utc=$TS"
command -v git >/dev/null && git rev-parse HEAD >/dev/null 2>&1 && say "git HEAD: $(git rev-parse HEAD)  dirty_files: $(git status --porcelain -- . | wc -l)"

# ---- 1 toolchain -----------------------------------------------------------
{
  echo "\$ cat lean-toolchain"; cat lean-toolchain
  echo "\$ elan --version"; elan --version
  echo "\$ lake --version"; lake --version
  echo "\$ lean --version"; lean --version
} > "$LOG_DIR/1_toolchain.log" 2>&1 || fail 1 "elan/lake/lean not runnable (install elan: https://lean-lang.org/install)"
TC="$(tr -d '[:space:]' < lean-toolchain)"
[ "$TC" = "$EXPECTED_TOOLCHAIN" ] || fail 1 "lean-toolchain is '$TC', expected '$EXPECTED_TOOLCHAIN' (update EXPECTED_TOOLCHAIN deliberately if the pin changed)"
VER="${TC##*:v}"
lean --version | grep -q "version $VER" || fail 1 "lean --version does not report $VER"
pass 1 "toolchain $TC"

# ---- 2 pins ----------------------------------------------------------------
python3 - "$EXPECTED_MATHLIB_REV" > "$LOG_DIR/2_pins.log" 2>&1 <<'PY' || fail 2 "lake-manifest.json mathlib pin mismatch (see 2_pins.log)"
import json, sys
m = json.load(open("lake-manifest.json"))
pk = {p["name"]: p for p in m["packages"]}
for n, p in sorted(pk.items()):
    print(f"{n:18} rev={p['rev']} inputRev={p.get('inputRev')} inherited={p.get('inherited')}")
ml = pk.get("mathlib")
assert ml, "mathlib not in manifest"
assert ml["rev"] == sys.argv[1], f"mathlib rev {ml['rev']} != expected {sys.argv[1]}"
print("mathlib pin OK")
PY
if [ -f AIEF_LEAN_PROJECT_LOCK_HASHES.txt ]; then
  sha256sum -c AIEF_LEAN_PROJECT_LOCK_HASHES.txt >> "$LOG_DIR/2_pins.log" 2>&1 || fail 2 "AIEF_LEAN_PROJECT_LOCK_HASHES.txt does not match"
fi
SUMS=AIEF_LEAN_SOURCE_SHA256SUMS.txt
[ -f "$SUMS" ] || fail 2 "$SUMS is missing (see the regeneration command in the header of check_lean.sh)"
{ echo "\$ sha256sum -c --strict $SUMS"; sha256sum -c --strict "$SUMS"; } >> "$LOG_DIR/2_pins.log" 2>&1 \
  || fail 2 "$SUMS does not match the sources (see 2_pins.log); if the change is intentional, regenerate it"
UNLISTED="$( { echo "$LIB.lean"; find "$LIB" -name '*.lean' | sort; echo check_lean.sh; } \
  | while read -r f; do awk '{print $2}' "$SUMS" | sed 's/^\*//' | grep -qxF -- "$f" || echo "$f"; done )"
[ -z "$UNLISTED" ] || fail 2 "files not covered by $SUMS: $(echo $UNLISTED)"
echo "source hashes OK: $(wc -l < "$SUMS") entries" >> "$LOG_DIR/2_pins.log"
pass 2 "mathlib rev $EXPECTED_MATHLIB_REV; $SUMS verified ($(wc -l < "$SUMS") files)"

# ---- 3 imports / orphans ---------------------------------------------------
python3 - "$LIB" > "$LOG_DIR/3_imports.log" 2>&1 <<'PY'
import re, sys, pathlib
lib = sys.argv[1]
root = pathlib.Path(f"{lib}.lean")
def mod_file(m): return pathlib.Path(*m.split(".")).with_suffix(".lean")
def imports(p): return re.findall(rf"^\s*(?:public\s+)?import\s+({lib}(?:\.\w+)+)\s*$", p.read_text(), re.M)
missing, seen, todo = [], set(), [lib]
while todo:
    m = todo.pop(); f = mod_file(m)
    if m in seen: continue
    seen.add(m)
    if not f.exists(): missing.append((m, str(f))); continue
    for i in imports(f): print(f"{m} imports {i}"); todo.append(i)
allf = {".".join(p.with_suffix("").parts) for p in pathlib.Path(lib).rglob("*.lean")} | {lib}
orphans = sorted(allf - seen)
for m, f in missing: print(f"MISSING {m} -> {f} does not exist")
for o in orphans: print(f"ORPHAN {o} (not reachable from {lib}.lean, so `lake build` does not check it)")
open(".reachable_modules.tmp","w").write("\n".join(sorted(m for m in seen if mod_file(m).exists()))+"\n")
sys.exit(1 if missing else 0)
PY
RC=$?; [ -f .reachable_modules.tmp ] && mv .reachable_modules.tmp "$LOG_DIR/3_reachable_modules.txt"
sed 's/^/  /' "$LOG_DIR/3_imports.log" >> "$SUMMARY"
[ $RC -eq 0 ] || fail 3 "root imports a module whose file does not exist: $(grep MISSING "$LOG_DIR/3_imports.log" | tr '\n' ' ')"
if grep -q ORPHAN "$LOG_DIR/3_imports.log"; then
  ORPH="$(grep ORPHAN "$LOG_DIR/3_imports.log" | awk '{print $2}' | paste -sd' ')"
  [ "${STRICT_ORPHANS:-0}" = 1 ] && fail 3 "orphan .lean files are not built: $ORPH"
  say "WARN step 3: orphan files NOT checked by lake build: $ORPH"
fi
pass 3 "all root imports resolve"

# ---- 4 cache ---------------------------------------------------------------
if [ "${SKIP_CACHE:-0}" != 1 ]; then
  ( time lake exe cache get ) > "$LOG_DIR/4_cache.log" 2>&1 || fail 4 "lake exe cache get failed (network? see 4_cache.log)"
  pass 4 "mathlib cache: $(grep -iE 'Decompressed|unpacked|already|Completed' "$LOG_DIR/4_cache.log" | tail -1)"
else
  say "SKIP step 4 (SKIP_CACHE=1)"
fi

# ---- 5 build ---------------------------------------------------------------
if [ "${REUSE_BUILD:-0}" != "1" ]; then
  rm -rf -- "$PROJ/.lake/build"   # project outputs only; never trust stale/committed oleans
  say "INFO step 5: removed project build outputs (.lake/build); recompiling project modules from source"
fi
( time lake build ) > "$LOG_DIR/5_build.log" 2>&1
RC=$?
JOBS="$(grep -oE 'Build completed successfully( \([0-9]+ jobs\))?' "$LOG_DIR/5_build.log" | tail -1)"
NWARN="$(grep -cE '^warning:' "$LOG_DIR/5_build.log")"
grep -E '^(warning|error):' "$LOG_DIR/5_build.log" > "$LOG_DIR/5_build_diagnostics.txt"
[ $RC -eq 0 ] || fail 5 "lake build exit $RC: $(grep -m3 '^error' "$LOG_DIR/5_build.log" | tr '\n' ' ')"
pass 5 "$JOBS; warnings=$NWARN (listed in 5_build_diagnostics.txt)"

# ---- 6 forbidden markers ---------------------------------------------------
python3 - "$LIB" > "$LOG_DIR/6_markers.log" 2>&1 <<'PY'
import re, sys, pathlib
lib = sys.argv[1]
files = [pathlib.Path(f"{lib}.lean")] + sorted(pathlib.Path(lib).rglob("*.lean"))
def strip(src):  # remove nested /- -/ comments, -- comments, and string literals
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith("/-", i): depth += 1; i += 2; continue
        if depth and src.startswith("-/", i): depth -= 1; i += 2; continue
        if depth: out.append("\n" if src[i] == "\n" else " "); i += 1; continue
        if src.startswith("--", i):
            j = src.find("\n", i); i = n if j < 0 else j; continue
        if src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"': j += 2 if src[j] == "\\" else 1
            out.append('""'); i = j + 1; continue
        out.append(src[i]); i += 1
    return "".join(out)
pat = re.compile(r"\b(sorry|admit|sorryAx|native_decide|unsafe|implemented_by|extern)\b|^\s*(?:private\s+|protected\s+)?axiom\b|\bdecide\s*\+\s*native|\bofReduceBool\b|\bLean\.trustCompiler\b", re.M)
bad = 0
for f in files:
    s = strip(f.read_text())
    for m in pat.finditer(s):
        ln = s.count("\n", 0, m.start()) + 1
        print(f"HIT {f}:{ln}: {f.read_text().splitlines()[ln-1].strip()}"); bad += 1
print(f"scanned {len(files)} files, hits={bad}")
sys.exit(1 if bad else 0)
PY
[ $? -eq 0 ] || fail 6 "forbidden marker found: $(grep HIT "$LOG_DIR/6_markers.log" | head -3 | tr '\n' ' ')"
pass 6 "$(tail -1 "$LOG_DIR/6_markers.log")"

# ---- 7 axioms --------------------------------------------------------------
AX="$LOG_DIR/7_axioms_check.lean"
{
  sed 's/^/import /' "$LOG_DIR/3_reachable_modules.txt"
  cat <<'LEAN'
open Lean Elab Command in
/-- For every constant defined in a project module, collect its axioms and
fail if any is outside the allowed set. Prints one line per declaration. -/
elab "#aief_axiom_audit" : command => do
  let env ← getEnv
  let allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]
  let mut bad : Array (Name × Array Name) := #[]
  let mut count : Nat := 0
  for (c, _) in env.constants.toList do
    let some idx := env.getModuleIdxFor? c | continue
    let modName := env.header.moduleNames[idx.toNat]!
    unless (`AIEFProofs).isPrefixOf modName do continue
    if c.isInternal then continue
    count := count + 1
    let axs ← liftCoreM (Lean.collectAxioms c)
    let extra := axs.filter (fun a => !allowed.contains a)
    logInfo m!"AXIOMS {c} [{modName}]: {axs.toList}"
    unless extra.isEmpty do bad := bad.push (c, extra)
  logInfo m!"AUDITED {count} project declarations"
  unless bad.isEmpty do
    throwError m!"DISALLOWED AXIOMS: {bad.toList}"

#aief_axiom_audit
LEAN
  # human-readable #print axioms for every theorem/lemma, fully qualified via namespaces
  python3 - "$LOG_DIR/3_reachable_modules.txt" <<'PY'
import re, sys, pathlib
for mod in open(sys.argv[1]).read().split():
    f = pathlib.Path(*mod.split(".")).with_suffix(".lean")
    ns = []
    for line in f.read_text().splitlines():
        m = re.match(r"\s*namespace\s+(\S+)", line)
        if m: ns.append(m.group(1)); continue
        m = re.match(r"\s*end\s+(\S+)", line)
        if m and ns and ns[-1] == m.group(1): ns.pop(); continue
        m = re.match(r"\s*(?:@\[[^\]]*\]\s*)?(?:protected\s+)?(?:theorem|lemma)\s+([^\s:({\[]+)", line)
        if m and not re.match(r"\s*private", line): print(f"#print axioms {'.'.join(ns + [m.group(1)])}")
PY
} > "$AX"
( lake env lean "$AX" ) > "$LOG_DIR/7_axioms.log" 2>&1
RC=$?
[ $RC -eq 0 ] || fail 7 "axiom audit failed: $(grep -m3 -E 'error|DISALLOWED' "$LOG_DIR/7_axioms.log" | tr '\n' ' ')"
grep -q "AUDITED" "$LOG_DIR/7_axioms.log" || fail 7 "axiom audit produced no result"
python3 - "$LOG_DIR/7_axioms.log" > "$LOG_DIR/7_axioms_summary.txt" <<'PY' || fail 7 "#print axioms reports a disallowed axiom (see 7_axioms_summary.txt)"
import re, sys
allowed = {"propext", "Classical.choice", "Quot.sound"}
log = open(sys.argv[1]).read()
bad = 0
for name, body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", log):
    axs = {a.strip() for a in body.replace("\n", " ").split(",") if a.strip()}
    flag = "" if axs <= allowed else "  <-- DISALLOWED"
    bad += bool(flag)
    print(f"{name}: {sorted(axs)}{flag}")
for name in re.findall(r"'([^']+)' does not depend on any axioms", log):
    print(f"{name}: []")
print(f"disallowed={bad}")
sys.exit(1 if bad else 0)
PY
pass 7 "$(grep -o 'AUDITED [0-9]* project declarations' "$LOG_DIR/7_axioms.log"); allowed: $ALLOWED_AXIOMS"

# ---- record source hashes ---------------------------------------------------
{ sha256sum lean-toolchain lakefile.toml lake-manifest.json "$LIB.lean"; find "$LIB" -name '*.lean' | sort | xargs sha256sum; } > "$LOG_DIR/source_sha256.txt"
say "RESULT: PASS (logs in $LOG_DIR)"
exit 0
