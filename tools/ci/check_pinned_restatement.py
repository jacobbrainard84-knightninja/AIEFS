#!/usr/bin/env python3
"""Check that lean/AIEFGateCore/AIEFGateCore/Pinned/*.lean are verbatim copies of the pinned
lean/AIEFProofs controller-fiber modules (Lean P3 bridge; fail-closed, stdlib only).

Run from the repository root:

    python3 tools/ci/check_pinned_restatement.py              # this checkout
    python3 tools/ci/check_pinned_restatement.py --repo PATH  # another work tree

Why: lean/AIEFGateCore may not depend on lean/AIEFProofs through a Lake path dependency
(check_lean_gate.sh step 2 rejects path dependencies), so the Lean P3 bridge (AIEFGateCore/Bridge.lean)
compiles the pinned modules a second time, as restated copies. A restatement is only worth something if
it is the pinned text. For every pair in PAIRS this checker requires:

  1. the pinned source has the sha256 hard-coded in PAIRS, and the same digest is listed for it in
     lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt (so the pinned file did not change under us);
  2. the restated file is byte-for-byte equal to the pinned file after applying exactly the whole-line
     substitutions in LINE_SUBS (namespace `AIEFProofs` -> `AIEFGate`, and the internal
     `import AIEFProofs.X` -> `import AIEFGateCore.Pinned.X`); nothing else may differ (not a comment, not
     whitespace, not a trailing newline), and at least one substitution must apply;
  3. the directory lean/AIEFGateCore/AIEFGateCore/Pinned contains exactly the restated files of PAIRS
     (an extra, unchecked "pinned" file is an error).

All failures are reported. Exit status: 0 = PASS, 1 = any failure, 2 = usage error.

Checker isolation as in check_sha256sums.py (Researcher 001 audit of 18e542c, S-B1): run as a script, this
file re-executes itself as `python -I -B` before importing anything a sibling file could shadow.
"""
import sys as _sys
if __name__ == "__main__" and not _sys.flags.isolated:
    import os as _os
    _os.execv(_sys.executable, [_sys.executable, "-I", "-B", _os.path.abspath(__file__)] + _sys.argv[1:])
import argparse
import hashlib
import os
import sys

PINNED_DIR = "lean/AIEFProofs"
PINNED_SUMS = "lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt"
RESTATED_DIR = "lean/AIEFGateCore/AIEFGateCore/Pinned"

# (pinned path relative to PINNED_DIR, restated file name in RESTATED_DIR, expected pinned sha256)
PAIRS = [
    ("AIEFProofs/ControllerFiber.lean", "ControllerFiber.lean",
     "b51e07e83ac173decfbe276afd48a4871caf34edd20aad643a8897addec63411"),
    ("AIEFProofs/ControllerFiberProjector.lean", "ControllerFiberProjector.lean",
     "8199407d24d1da7d436d348b1a26d57a03bcf4d6d673503c9d1f6f561b2d27ec"),
    ("AIEFProofs/ControllerFiberQuotient.lean", "ControllerFiberQuotient.lean",
     "bdb0c8135a58e4d62bd339161b647fdfec2eacf2bc86e4e96aeceb4e02c035d2"),
    ("AIEFProofs/CompleteGraphIncidence.lean", "CompleteGraphIncidence.lean",
     "f138220428095721f814d2b5de4ec97ef29bed36d8ae48eabbcfd53900bb4458"),
]

# The only allowed differences: whole lines (without the trailing newline), pinned -> restated.
LINE_SUBS = {
    "namespace AIEFProofs": "namespace AIEFGate",
    "end AIEFProofs": "end AIEFGate",
    "import AIEFProofs.ControllerFiber": "import AIEFGateCore.Pinned.ControllerFiber",
    "import AIEFProofs.ControllerFiberProjector": "import AIEFGateCore.Pinned.ControllerFiberProjector",
}


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def substitute(pinned):
    """Apply LINE_SUBS to whole lines of `pinned` (bytes). Returns (bytes, set of applied keys)."""
    out, used = [], set()
    for line in pinned.decode("utf-8").splitlines(keepends=True):
        body = line[:-1] if line.endswith("\n") else line
        nl = line[len(body):]
        if body in LINE_SUBS:
            used.add(body)
            body = LINE_SUBS[body]
        out.append(body + nl)
    return "".join(out).encode("utf-8"), used


def read_sums(path):
    sums = {}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if not ln.strip() or ln.startswith("#"):
                continue
            digest, _, name = ln.partition("  ")
            sums[name.lstrip("*")] = digest.lower()
    return sums


def check(repo):
    """Return a list of error strings (empty = PASS) and a list of info lines."""
    errs, info = [], []
    try:
        sums = read_sums(os.path.join(repo, PINNED_SUMS))
    except OSError as e:
        return [f"cannot read {PINNED_SUMS}: {e}"], info
    for rel, name, expected in PAIRS:
        ppath = os.path.join(repo, PINNED_DIR, rel)
        rpath = os.path.join(repo, RESTATED_DIR, name)
        try:
            pinned = read_bytes(ppath)
        except OSError as e:
            errs.append(f"{PINNED_DIR}/{rel}: cannot read pinned source ({e})")
            continue
        d = sha(pinned)
        if d != expected:
            errs.append(f"{PINNED_DIR}/{rel}: sha256 {d} != hard-coded pin {expected}")
        if sums.get(rel) != d:
            errs.append(f"{PINNED_DIR}/{rel}: not listed with sha256 {d} in {PINNED_SUMS}")
        try:
            restated = read_bytes(rpath)
        except OSError as e:
            errs.append(f"{RESTATED_DIR}/{name}: cannot read restated file ({e})")
            continue
        want, used = substitute(pinned)
        if not used:
            errs.append(f"{RESTATED_DIR}/{name}: no namespace/import substitution applied (unexpected)")
        if restated != want:
            a, b = want.decode("utf-8").splitlines(), restated.decode("utf-8", "replace").splitlines()
            first = next((i for i in range(max(len(a), len(b)))
                          if i >= len(a) or i >= len(b) or a[i] != b[i]), None)
            where = f"line {first + 1}" if first is not None else "trailing bytes / newline"
            errs.append(f"{RESTATED_DIR}/{name}: differs from substituted {PINNED_DIR}/{rel} at {where}")
        else:
            info.append(f"OK {RESTATED_DIR}/{name} == {PINNED_DIR}/{rel} (sha256 {d[:12]}...) "
                        f"with {len(used)} line substitution(s): {sorted(used)}")
    try:
        present = sorted(f for f in os.listdir(os.path.join(repo, RESTATED_DIR)))
    except OSError as e:
        errs.append(f"{RESTATED_DIR}: cannot list ({e})")
        present = []
    extra = sorted(set(present) - {n for _, n, _ in PAIRS})
    if extra:
        errs.append(f"{RESTATED_DIR}: files not covered by this checker: {extra}")
    return errs, info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    args = ap.parse_args(argv)
    if not os.path.isdir(os.path.join(args.repo, PINNED_DIR)):
        print(f"usage error: {args.repo} has no {PINNED_DIR}", file=sys.stderr)
        return 2
    errs, info = check(args.repo)
    for line in info:
        print(line)
    for e in errs:
        print("ERROR " + e)
    print(f"== result: {len(PAIRS)} pinned module(s), {len(errs)} error(s) -> {'PASS' if not errs else 'FAIL'}")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
