#!/usr/bin/env python3
"""Resolve registry/studies.csv tokens against tracked repository tree."""
import csv
import glob
import os
import subprocess
import sys

def resolve_token(repo_dir, token):
    p = os.path.join(repo_dir, token)
    if os.path.exists(p):
        return True, [token]
    matches = glob.glob(p)
    if matches:
        return True, [os.path.relpath(m, repo_dir) for m in matches]
    return False, []

def main():
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "/home/user/aiefs_git"
    csv_path = os.path.join(repo_dir, "registry/studies.csv")

    resolved = []
    unresolved = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["study_id"]
            eps = [t.strip() for t in row.get("canonical_entrypoints", "").split(";") if t.strip()]
            evs = [t.strip() for t in row.get("canonical_evidence_paths", "").split(";") if t.strip()]
            for t in eps:
                ok, m = resolve_token(repo_dir, t)
                if ok:
                    resolved.append((sid, "canonical_entrypoints", t, m))
                else:
                    unresolved.append((sid, "canonical_entrypoints", t))
            for t in evs:
                ok, m = resolve_token(repo_dir, t)
                if ok:
                    resolved.append((sid, "canonical_evidence_paths", t, m))
                else:
                    unresolved.append((sid, "canonical_evidence_paths", t))

    print(f"Total resolved tokens: {len(resolved)}")
    print(f"Total unresolved tokens: {len(unresolved)}")
    print("\nUnresolved tokens with git provenance:")
    for sid, field, t in unresolved:
        clean_t = t.rstrip("/").split("*")[0].rstrip("/")
        cmd = ["git", "log", "--all", "-n", "1", "--format=%H %cd %s", "--", clean_t if clean_t else t]
        res = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
        out = res.stdout.strip()
        prov = out if out else "UNEXPLAINED (never committed in git history)"
        print(f"[{sid}] {field} -> {t} | {prov}")

if __name__ == "__main__":
    main()
