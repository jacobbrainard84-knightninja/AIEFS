#!/usr/bin/env python3
"""Artifact pin check: registry/artifacts.csv sha256 pins against the tree.

Plain Python 3 standard library (plus the `git` command when available). Run from the repo root:

    python3 tools/ci/check_artifact_pins.py
    python3 tools/ci/check_artifact_pins.py --repo PATH
    python3 tools/ci/check_artifact_pins.py --no-git     # hash files on disk instead of tracked files

Every row of registry/artifacts.csv is checked against the tree:
  container "worktree"     the file at `path` (git-tracked files only, when the repo is a git work
                           tree, so local build output such as __pycache__/ is not mistaken for a
                           tracked file) must have the pinned sha256.
  container "zip:<archive>" the member `path` inside the tracked archive must have the pinned sha256.

The registry's own convention (registry/README.md, ERRATA_2026-10-28.md E7) is that the sha256
column is the registration snapshot at e47bad15 and is NOT re-pinned; drift is recorded in
`tree_check_2026_10_28` instead. This check therefore does not edit or trust that column. It
hard-codes the drift known when the check was added (at 9d46d9b) and fails on anything else:

  KNOWN_CHANGED   the 7 rows flagged PRESENT_CHANGED_SHA. Each is allowed only with the exact
                  sha256 it has in the tree at 9d46d9b, so a further edit to one of these files
                  also fails until this list is updated in review.
  KNOWN_MISSING   the 52 rows flagged MISSING_DELETED_ON_MAIN. They may stay absent; if one comes
                  back it must match its pinned sha256.

The CSV itself is pinned here too (EXPECTED_CSV_SHA256, EXPECTED_ROWS), so pins cannot be
bypassed by re-pinning a row, deleting a row, or deleting the CSV. A deliberate change to
registry/artifacts.csv therefore means updating those two constants in the same reviewed PR.

Files are hashed as they are on disk (git-tracked paths only in git mode). In CI that equals the
committed blob; locally, uncommitted edits to a pinned file are reported too.

Findings
  ERROR   REGISTRY_CHANGED     registry/artifacts.csv does not have EXPECTED_CSV_SHA256, or its row
                               count is not EXPECTED_ROWS
  ERROR   REGISTRY_MISSING     registry/artifacts.csv is not tracked / not present (git mode)
  ERROR   PIN_MISMATCH         a row's file or zip member has a sha256 that is not allowed
  ERROR   PIN_MISSING          a row's file, archive or zip member is absent and not KNOWN_MISSING
  ERROR   ALLOWLIST_DRIFT      an allowlisted artifact_id now has a different path in the CSV,
                               or is no longer in the CSV
  ERROR   BAD_ROW              duplicate artifact_id, unknown container, or malformed sha256
  NOTICE  STALE_ALLOWLIST      an allowlisted row matches its pin again; the entry can be removed
  NOTICE  FLAG_DISAGREES       tree_check_2026_10_28 disagrees with what was observed (info only)

If registry/artifacts.csv is absent: ERROR in git mode; with --no-git (fixtures) a notice and pass.
Under GitHub Actions (GITHUB_ACTIONS=true) errors are also printed as ::error annotations.

Exit status: 0 = pass, 1 = at least one ERROR, 2 = usage / read error.
"""
import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
import zipfile

ARTIFACTS = "registry/artifacts.csv"
REQUIRED_COLUMNS = ("artifact_id", "container", "path", "sha256")
FLAG_COLUMN = "tree_check_2026_10_28"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

# registry/artifacts.csv as of 9d46d9b (2,898 rows, LF). Per ERRATA E7 the CSV is a frozen snapshot;
# if it is changed on purpose, update both constants in the same reviewed change.
EXPECTED_CSV_SHA256 = "90508a0db6371155968b360f039979931de9cf8d634b1389a349a544c4e3b9ef"
EXPECTED_ROWS = 2898
UPDATE_HINT = ("if artifacts.csv was changed on purpose, update EXPECTED_CSV_SHA256 and EXPECTED_ROWS "
               "in tools/ci/check_artifact_pins.py in the same reviewed change")
_DEFAULT = object()

# artifact_id -> (path, sha256 of the file in the tree at 9d46d9b). The pinned value in the CSV is
# the e47bad15 snapshot; these files were changed afterwards on main or in merge prep (ERRATA E7).
KNOWN_CHANGED = {
    "ART-0001": (".gitignore",
                 "6a81afd0237eaa19418b6e8a398ba08ca5048cc369d4fbdf19777505905591d8"),
    "ART-0712": ("lean/AIEFProofs/.gitignore",
                 "6484ea2efc7072fcb81d945c13e5f78d0ee2e6c9853f4750a7c59e53ab639359"),
    "ART-0743": ("lean/AIEFProofs/AIEFProofs.lean",
                 "a2937f75f0c84b850a8b764f719677b61bde3dbed094783d7406783cd8e52831"),
    "ART-0744": ("lean/AIEFProofs/AIEFProofs/Basic.lean",
                 "06a589efff4562434d8f4aa641f0832abd8be9f2acf96e7e04f8a3defd19436d"),
    "ART-0745": ("lean/AIEFProofs/AIEFProofs/ControllerFiber.lean",
                 "b51e07e83ac173decfbe276afd48a4871caf34edd20aad643a8897addec63411"),
    "ART-0746": ("lean/AIEFProofs/AIEFProofs/Smoke.lean",
                 "563a6e7d34a6e56379904956bf556df3df933a2dcfa67c69426eb49b52858f3b"),
    # Pinned 1391738e... (as added in d2f8452); main commit ec3a84b (2026-10-25, "README documents
    # checks and licence") changed it to 04c8ae17.... The CSV keeps the snapshot and flags the row.
    "ART-0748": ("lean/AIEFProofs/README.md",
                 "04c8ae17ccbc703101399c09ea08d346a46fd45d3dc6a936b660523c6c7f8f0f"),
}

# artifact_id -> path, rows flagged MISSING_DELETED_ON_MAIN at 9d46d9b (deleted on main).
KNOWN_MISSING = {
    'ART-0002': '.~lock.AI_AGENT_HANDOFF_PROMPT.md#',
    'ART-0256': 'Papers/2804.05652v1.pdf',
    'ART-0257': 'Papers/H-Atom_Paper 3 Geometric Radius Scaling Law 19.Jul.2026_v1.0.pdf',
    'ART-0258': 'Papers/The Holland Atom_Paper 2 Radius Variation 23.Jun.2026_v1.0.pdf',
    'ART-0259': 'Papers/The Holland Atom_Paper_1_30.May.2026_v1.pdf',
    'ART-0283': '__pycache__/AIEF_1_4_Twindow_sensitivity.cpython-313.pyc',
    'ART-0284': '__pycache__/AIEF_1_4_Twindow_sensitivity_analysis_v3.cpython-313.pyc',
    'ART-0285': '__pycache__/AIEF_1_4_actual_admissibility_branch_audit.cpython-313.pyc',
    'ART-0286': '__pycache__/AIEF_1_4_augmented_tangent_cocycle_analysis.cpython-313.pyc',
    'ART-0287': '__pycache__/AIEF_1_4_component_controller_audit.cpython-313.pyc',
    'ART-0288': '__pycache__/AIEF_1_4_exceptional_K3_transition_audit.cpython-313.pyc',
    'ART-0289': '__pycache__/AIEF_1_4_exceptional_tangent_analysis.cpython-313.pyc',
    'ART-0290': '__pycache__/AIEF_1_4_face_spectrum_analysis.cpython-313.pyc',
    'ART-0291': '__pycache__/AIEF_1_4_frozen_driver_cocycle_analysis.cpython-313.pyc',
    'ART-0292': '__pycache__/AIEF_1_4_matched_phase_memory_ablation.cpython-313.pyc',
    'ART-0293': '__pycache__/AIEF_1_4_memory_ablation_updated.cpython-313.pyc',
    'ART-0294': '__pycache__/AIEF_1_4_nested_operator_family_audit.cpython-313.pyc',
    'ART-0295': '__pycache__/AIEF_1_4_proposal_equalization_bridge_analysis.cpython-313.pyc',
    'ART-0296': '__pycache__/AIEF_1_4_stationarity_perturbation_analysis_updated.cpython-313.pyc',
    'ART-0297': '__pycache__/AIEF_1_4_tangent_spectrum_switch_analysis.cpython-313.pyc',
    'ART-0298': '__pycache__/AIEF_1_4_trajectory_recovery_equivalence.cpython-313.pyc',
    'ART-0299': '__pycache__/aief_experiment_engine_v1.cpython-313.pyc',
    'ART-0713': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs.c',
    'ART-0714': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs.c.hash',
    'ART-0715': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs.setup.json',
    'ART-0716': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs/Basic.c',
    'ART-0717': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs/Basic.c.hash',
    'ART-0718': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs/Basic.setup.json',
    'ART-0719': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs/ControllerFiber.c',
    'ART-0720': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs/ControllerFiber.c.hash',
    'ART-0721': 'lean/AIEFProofs/.lake/build/ir/AIEFProofs/ControllerFiber.setup.json',
    'ART-0722': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs.ilean',
    'ART-0723': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs.ilean.hash',
    'ART-0724': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs.olean',
    'ART-0725': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs.olean.hash',
    'ART-0726': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs.trace',
    'ART-0727': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/Basic.ilean',
    'ART-0728': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/Basic.ilean.hash',
    'ART-0729': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/Basic.olean',
    'ART-0730': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/Basic.olean.hash',
    'ART-0731': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/Basic.trace',
    'ART-0732': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/ControllerFiber.ilean',
    'ART-0733': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/ControllerFiber.ilean.hash',
    'ART-0734': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/ControllerFiber.olean',
    'ART-0735': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/ControllerFiber.olean.hash',
    'ART-0736': 'lean/AIEFProofs/.lake/build/lib/lean/AIEFProofs/ControllerFiber.trace',
    'ART-0737': 'lean/AIEFProofs/.lake/config/1/lakefile.olean',
    'ART-0738': 'lean/AIEFProofs/.lake/config/1/lakefile.olean.lock',
    'ART-0739': 'lean/AIEFProofs/.lake/config/1/lakefile.olean.trace',
    'ART-0740': 'lean/AIEFProofs/.lake/config/5/lakefile.olean',
    'ART-0741': 'lean/AIEFProofs/.lake/config/5/lakefile.olean.lock',
    'ART-0742': 'lean/AIEFProofs/.lake/config/5/lakefile.olean.trace',
}

IN_GHA = os.environ.get("GITHUB_ACTIONS") == "true"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_files(repo):
    """Set of tracked paths, or None if repo is not a git work tree (or git is unavailable)."""
    try:
        p = subprocess.run(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True)
        if p.returncode != 0 or p.stdout.strip() != "true":
            return None
        p = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True)
    except OSError:
        return None
    if p.returncode != 0:
        return None
    return {x for x in p.stdout.decode("utf-8", "surrogateescape").split("\0") if x}


class Checker:
    def __init__(self, repo, tracked, known_changed, known_missing):
        self.repo, self.tracked = repo, tracked
        self.known_changed, self.known_missing = known_changed, known_missing
        self.errors, self.notices = [], []
        self.zips = {}
        self.counts = {"ok": 0, "known_changed": 0, "known_missing": 0}

    def error(self, kind, aid, msg):
        self.errors.append((kind, aid, msg))

    def notice(self, kind, aid, msg):
        self.notices.append((kind, aid, msg))

    def present(self, rel):
        if self.tracked is not None and rel not in self.tracked:
            return False
        return os.path.isfile(os.path.join(self.repo, rel))

    def actual_sha(self, container, rel):
        """sha256 of the row's bytes, or None if absent; raises ValueError on a broken archive."""
        if container == "worktree":
            return sha256_file(os.path.join(self.repo, rel)) if self.present(rel) else None
        archive = container[len("zip:"):]
        if archive not in self.zips:
            if not self.present(archive):
                self.zips[archive] = None
            else:
                try:
                    zf = zipfile.ZipFile(os.path.join(self.repo, archive))
                except (zipfile.BadZipFile, OSError) as e:
                    raise ValueError(f"cannot open archive {archive}: {e}")
                self.zips[archive] = (zf, set(zf.namelist()))
        entry = self.zips[archive]
        if entry is None or rel not in entry[1]:
            return None
        return hashlib.sha256(entry[0].read(rel)).hexdigest()

    def check_row(self, row):
        aid, container, rel = row["artifact_id"], row["container"], row["path"]
        pinned, flag = row["sha256"].strip().lower(), (row.get(FLAG_COLUMN) or "").strip()
        where = rel if container == "worktree" else f"{container[4:]}!{rel}"
        if not SHA_RE.match(pinned):
            self.error("BAD_ROW", aid, f"{where}: sha256 is not 64 hex characters"); return
        if container != "worktree" and not container.startswith("zip:"):
            self.error("BAD_ROW", aid, f"{where}: unknown container {container!r}"); return
        try:
            actual = self.actual_sha(container, rel)
        except ValueError as e:
            self.error("PIN_MISSING", aid, str(e)); return
        changed_ok = self.known_changed.get(aid)
        if changed_ok is not None and changed_ok[0] != rel:
            self.error("ALLOWLIST_DRIFT", aid,
                       f"KNOWN_CHANGED lists path {changed_ok[0]!r} but the CSV row has {rel!r}")
            changed_ok = None
        missing_ok = self.known_missing.get(aid)
        if missing_ok is not None and missing_ok != rel:
            self.error("ALLOWLIST_DRIFT", aid,
                       f"KNOWN_MISSING lists path {missing_ok!r} but the CSV row has {rel!r}")
            missing_ok = None
        if actual is None:
            if missing_ok is not None:
                self.counts["known_missing"] += 1
                if flag and not flag.startswith("MISSING"):
                    self.notice("FLAG_DISAGREES", aid, f"{where}: absent but flagged {flag}")
                return
            self.error("PIN_MISSING", aid, f"{where}: not in the tree (pinned {pinned[:12]}...)")
            return
        if actual == pinned:
            self.counts["ok"] += 1
            if aid in self.known_changed or aid in self.known_missing:
                self.notice("STALE_ALLOWLIST", aid,
                            f"{where}: matches its pin again; the allowlist entry can be removed")
            elif flag and flag not in ("PRESENT_SAME_SHA", "ZIP_MEMBER_PRESENT"):
                self.notice("FLAG_DISAGREES", aid, f"{where}: matches its pin but flagged {flag}")
            return
        if changed_ok is not None and actual == changed_ok[1]:
            self.counts["known_changed"] += 1
            if flag and flag != "PRESENT_CHANGED_SHA":
                self.notice("FLAG_DISAGREES", aid, f"{where}: known change but flagged {flag}")
            return
        extra = ""
        if changed_ok is not None:
            extra = f"; KNOWN_CHANGED allows only {changed_ok[1][:12]}..."
        self.error("PIN_MISMATCH", aid,
                   f"{where}: sha256 {actual[:12]}... != pinned {pinned[:12]}...{extra}")

    def close(self):
        for entry in self.zips.values():
            if entry is not None:
                entry[0].close()


def main(argv=None, known_changed=None, known_missing=None,
         expected_sha=_DEFAULT, expected_rows=_DEFAULT):
    """CLI entry. Tests may pass their own allowlists; expected_sha / expected_rows = None
    disables that registry check for synthetic fixtures (the command line cannot do this)."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--no-git", action="store_true",
                    help="hash files on disk even if they are not tracked by git")
    a = ap.parse_args(argv)
    known_changed = KNOWN_CHANGED if known_changed is None else known_changed
    known_missing = KNOWN_MISSING if known_missing is None else known_missing
    expected_sha = EXPECTED_CSV_SHA256 if expected_sha is _DEFAULT else expected_sha
    expected_rows = EXPECTED_ROWS if expected_rows is _DEFAULT else expected_rows
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        print(f"ERROR   --repo {a.repo} is not a directory"); return 2
    print(f"== check_artifact_pins: {repo}")
    csv_path = os.path.join(repo, ARTIFACTS)
    tracked = None if a.no_git else tracked_files(repo)
    csv_present = os.path.isfile(csv_path) and (tracked is None or ARTIFACTS in tracked)
    if not csv_present:
        if tracked is not None:
            msg = f"REGISTRY_MISSING {ARTIFACTS} is not in the tree; {UPDATE_HINT}"
            print(f"ERROR   {msg}")
            if IN_GHA:
                print(f"::error file={ARTIFACTS}::{msg}")
            print("== result: 1 error(s), 0 notice(s) -> FAIL")
            return 1
        print(f"NOTICE  {ARTIFACTS} not found; artifact pin check skipped (--no-git)")
        if IN_GHA:
            print(f"::notice::{ARTIFACTS} not found; artifact pin check skipped")
        return 0
    registry_errors = []
    actual_csv_sha = sha256_file(csv_path)
    if expected_sha is not None and actual_csv_sha != expected_sha:
        registry_errors.append(("REGISTRY_CHANGED", "-",
                                f"{ARTIFACTS} sha256 {actual_csv_sha} != expected {expected_sha}; "
                                f"{UPDATE_HINT}"))
    try:
        with open(csv_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames or []
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        print(f"ERROR   cannot read {ARTIFACTS}: {e}")
        for kind, aid, msg in registry_errors:
            print(f"ERROR   {kind} {aid} {msg}")
        return 2
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in cols]
    if missing_cols:
        print(f"ERROR   {ARTIFACTS}: missing column(s) {', '.join(missing_cols)}")
        for kind, aid, msg in registry_errors:
            print(f"ERROR   {kind} {aid} {msg}")
        return 2
    if expected_rows is not None and len(rows) != expected_rows:
        registry_errors.append(("REGISTRY_CHANGED", "-",
                                f"{ARTIFACTS} has {len(rows)} row(s), expected {expected_rows}; "
                                f"{UPDATE_HINT}"))
    print(f"files: {'git-tracked only' if tracked is not None else 'on disk (no git)'}; "
          f"allowlist: {len(known_changed)} known-changed, {len(known_missing)} known-missing row(s)")
    chk = Checker(repo, tracked, known_changed, known_missing)
    chk.errors.extend(registry_errors)
    seen = set()
    try:
        for row in rows:
            aid = (row.get("artifact_id") or "").strip()
            if not aid or aid in seen:
                chk.error("BAD_ROW", aid or "?", "empty or duplicate artifact_id"); continue
            seen.add(aid)
            chk.check_row(row)
    finally:
        chk.close()
    for aid in sorted((set(known_changed) | set(known_missing)) - seen):
        chk.error("ALLOWLIST_DRIFT", aid, "allowlisted artifact_id is no longer in the CSV")
    for kind, aid, msg in chk.notices:
        print(f"NOTICE  {kind} {aid} {msg}")
    for kind, aid, msg in chk.errors:
        print(f"ERROR   {kind} {aid} {msg}")
        if IN_GHA:
            print(f"::error file={ARTIFACTS}::{kind} {aid} {msg}")
    c = chk.counts
    print(f"checked {len(rows)} row(s): {c['ok']} match, {c['known_changed']} known-changed, "
          f"{c['known_missing']} known-missing")
    print(f"== result: {len(chk.errors)} error(s), {len(chk.notices)} notice(s) -> "
          f"{'FAIL' if chk.errors else 'PASS'}")
    return 1 if chk.errors else 0


if __name__ == "__main__":
    sys.exit(main())
