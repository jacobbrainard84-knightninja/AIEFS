#!/usr/bin/env python3
"""CI check: verify that all canonical_entrypoints in registry/studies.csv resolve or carry explicit classification tags.

Usage:
    python3 -I tools/ci/check_studies.py [--repo REPO] [--strict]
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import sys

ALLOWED_PREFIXES = (
    "historical_missing:",
    "planned:",
    "alias_of:",
    "superseded_by:",
)


def check_studies(repo_root: str, strict: bool = False) -> tuple[int, list[str]]:
    csv_path = os.path.join(repo_root, "registry", "studies.csv")
    if not os.path.exists(csv_path):
        return 2, [f"ERROR: missing {csv_path}"]

    errors = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "study_id" not in reader.fieldnames or "canonical_entrypoints" not in reader.fieldnames:
            return 2, ["ERROR: studies.csv missing required header columns"]

        for row_idx, row in enumerate(reader, start=2):
            sid = row.get("study_id", f"row_{row_idx}")
            raw_eps = row.get("canonical_entrypoints", "")
            tokens = [t.strip() for t in raw_eps.split(";") if t.strip()]

            for token in tokens:
                # Check for explicit classification tags
                if any(token.startswith(p) for p in ALLOWED_PREFIXES):
                    continue

                # Check for physical path / wildcard resolution
                target = os.path.join(repo_root, token)
                if "*" in token or "?" in token:
                    matches = glob.glob(target)
                    if not matches:
                        errors.append(f"Row {row_idx} ({sid}): wildcard pattern '{token}' matched 0 files")
                else:
                    if not os.path.exists(target):
                        errors.append(f"Row {row_idx} ({sid}): canonical entrypoint '{token}' does not exist on disk")

    if errors:
        return (1 if strict else 0), errors
    return 0, []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root path")
    parser.add_argument("--strict", action="store_true", help="exit with non-zero status on missing entrypoints")
    args = parser.parse_args(argv)

    rc, errors = check_studies(args.repo, strict=args.strict)
    if errors:
        for err in errors:
            print(f"{'FAIL' if args.strict else 'WARN'}: {err}")
        print(f"\nTotal unresolved canonical entrypoints: {len(errors)}")
        if not args.strict:
            print("Note: run with --strict to enforce as a blocking CI gate.")
    else:
        print("OK: all canonical entrypoints in registry/studies.csv are valid and resolved.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
