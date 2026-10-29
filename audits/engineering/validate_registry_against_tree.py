#!/usr/bin/env python3
"""Check registry/artifacts.csv and registry/relocation_map.csv against the current git tree.

Added 2026-10-28 (local merge-prep reconciliation, Researcher 001).

The arena checker `verify_inventory.py` conserves the file list of commit e47bad1, so it stops at
check [1/5] once `main` deletes or moves files. This script does not fail on that. Instead it
records, for each registry row, what is true now. The result goes in one added column,
`tree_check_2026_10_28`, and a free-text column, `tree_check_note`. No other cell is changed.

Flags (artifacts.csv):
  PRESENT_SAME_SHA        path tracked at HEAD, SHA-256 equal to the registry value
  PRESENT_CHANGED_SHA     path tracked at HEAD, content differs (note says if the merge-prep edited it)
  MOVED_ON_MAIN           path gone, but a tracked file with the same SHA-256 exists elsewhere (note = new path)
  MISSING_DELETED_ON_MAIN path existed at the merge base and is absent from HEAD
  MISSING_OTHER           path absent and not in the merge base either
  ZIP_MEMBER_PRESENT      zip present and member has the registry SHA-256
  ZIP_MEMBER_CHANGED      zip present, member present, SHA differs
  ZIP_MEMBER_MISSING      zip present, member absent
  ZIP_MISSING             the containing zip is not tracked at HEAD
Flags (relocation_map.csv, which is per path or directory):
  PRESENT_SAME_COUNT / PRESENT_COUNT_CHANGED / MISSING_DELETED_ON_MAIN / MISSING_OTHER

Usage:  python3 audits/engineering/validate_registry_against_tree.py [--write] [--base e47bad1]
Without --write it only prints counts. With --write it rewrites the two CSVs (CRLF, same column order + 2 columns).
"""
import argparse, collections, csv, hashlib, io, json, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COL, NOTE = "tree_check_2026_10_28", "tree_check_note"

def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, check=True, capture_output=True).stdout

def tracked(rev):
    return [p for p in git("ls-tree", "-r", "--name-only", "-z", rev).decode().split("\0") if p]

def sha_file(p):
    h = hashlib.sha256()
    with open(ROOT / p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--base", default="e47bad1", help="merge base used by the arena inventory")
    ap.add_argument("--edited-since", default="ce8cced", help="merge commit; files changed after it are noted as merge-prep edits")
    a = ap.parse_args()
    if git("status", "--porcelain", "--untracked-files=no").strip():
        sys.exit("working tree has uncommitted changes to tracked files; commit or stash first")
    head = tracked("HEAD"); head_set = set(head)
    base_set = set(tracked(a.base))
    edited = set(p for p in git("diff", "--name-only", "-z", a.edited_since, "HEAD").decode().split("\0") if p)
    sha = {p: sha_file(p) for p in head}
    by_sha = collections.defaultdict(list)
    for p, h in sha.items():
        by_sha[h].append(p)
    zcache = {}

    def zmember(zpath, member):
        if zpath not in zcache:
            zcache[zpath] = zipfile.ZipFile(ROOT / zpath) if zpath in head_set else None
        z = zcache[zpath]
        if z is None:
            return "ZIP_MISSING", None
        try:
            return "OK", hashlib.sha256(z.read(member)).hexdigest()
        except KeyError:
            return "ZIP_MEMBER_MISSING", None

    def check_art(r):
        p, want = r["path"], r["sha256"]
        if r["container"].startswith("zip:"):
            st, got = zmember(r["container"][4:], p)
            if st != "OK":
                return st, ""
            return ("ZIP_MEMBER_PRESENT", "") if got == want else ("ZIP_MEMBER_CHANGED", "")
        if p in head_set:
            if sha[p] == want:
                return "PRESENT_SAME_SHA", ""
            return "PRESENT_CHANGED_SHA", ("edited by merge-prep after the merge (see git log)" if p in edited else "changed on main or in the merge")
        if want in by_sha:
            return "MOVED_ON_MAIN", "same SHA-256 now at: " + "; ".join(sorted(by_sha[want])[:3])
        if p in base_set:
            return "MISSING_DELETED_ON_MAIN", ""
        return "MISSING_OTHER", ""

    def check_reloc(r):
        p = r["current_path"].rstrip("/")
        n = sum(1 for q in head if q == p or q.startswith(p + "/"))
        nb = sum(1 for q in base_set if q == p or q.startswith(p + "/"))
        want = int(r["file_count"] or 0)
        if n == 0:
            return ("MISSING_DELETED_ON_MAIN" if nb else "MISSING_OTHER"), f"files now 0; at base {nb}; registry {want}"
        if n == want:
            return "PRESENT_SAME_COUNT", ""
        return "PRESENT_COUNT_CHANGED", f"files now {n}; registry {want}"

    summary = {}
    for name, fn in (("artifacts.csv", check_art), ("relocation_map.csv", check_reloc)):
        path = ROOT / "registry" / name
        raw = path.read_bytes().decode("utf-8")
        rows = list(csv.DictReader(io.StringIO(raw)))
        fields = [f for f in rows[0].keys() if f not in (COL, NOTE)] + [COL, NOTE]
        cnt = collections.Counter()
        for r in rows:
            r[COL], r[NOTE] = fn(r)
            cnt[r[COL]] += 1
        summary[name] = {"rows": len(rows), "flags": dict(sorted(cnt.items()))}
        if a.write:
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
                w.writeheader(); w.writerows(rows)
    inv_paths = {r["path"] for r in csv.DictReader((ROOT / "registry" / "artifacts.csv").open(encoding="utf-8")) if r["container"] == "worktree"}
    not_inv = sorted(p for p in head if p not in inv_paths)
    top = collections.Counter(p.split("/")[0] for p in not_inv)
    summary["tracked_files_at_HEAD"] = len(head)
    summary["tracked_files_not_in_artifacts_csv"] = len(not_inv)
    summary["not_in_inventory_by_top_level"] = dict(top.most_common())
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
