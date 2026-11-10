#!/usr/bin/env python3
"""Fail-closed validator for registry/studies.csv canonical_entrypoints."""
from __future__ import annotations
import argparse,csv,fnmatch,subprocess,sys
from pathlib import Path,PurePosixPath

def validate_rows(rows,tracked):
    tracked=set(tracked); errors=[]; seen=set()
    for line,row in enumerate(rows,start=2):
        sid=(row.get("study_id") or "").strip()
        if not sid: errors.append(f"line {line}: empty study_id"); continue
        if sid in seen: errors.append(f"line {line}: duplicate study_id {sid}")
        seen.add(sid)
        raw=row.get("canonical_entrypoints")
        if raw is None: errors.append(f"line {line} ({sid}): missing canonical_entrypoints column"); continue
        tokens=[t.strip() for t in raw.split(";")]
        if not tokens or any(not t for t in tokens):
            errors.append(f"line {line} ({sid}): empty entrypoint token"); continue
        for token in tokens:
            p=PurePosixPath(token)
            if p.is_absolute() or ".." in p.parts or "\\" in token:
                errors.append(f"line {line} ({sid}): unsafe token {token!r}"); continue
            if any(ch in token for ch in "*?["):
                matches=[path for path in tracked if fnmatch.fnmatchcase(path,token)
                         and ("/" not in token or path.count("/") == token.count("/"))]
                if not matches: errors.append(f"line {line} ({sid}): glob has no tracked-file match: {token}")
            elif token not in tracked:
                errors.append(f"line {line} ({sid}): exact entrypoint is not tracked: {token}")
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",type=Path,default=Path.cwd())
    ap.add_argument("--studies",default="registry/studies.csv"); a=ap.parse_args(); repo=a.repo.resolve()
    try:
        with (repo/a.studies).open(encoding="utf-8",newline="") as f:
            reader=csv.DictReader(f)
            if not {"study_id","canonical_entrypoints"}.issubset(reader.fieldnames or []):
                print("FAIL: required studies.csv columns missing",file=sys.stderr); return 1
            rows=list(reader)
        proc=subprocess.run(["git","ls-files","-z"],cwd=repo,check=True,capture_output=True)
        tracked=[x.decode("utf-8") for x in proc.stdout.split(bytes([0])) if x]
    except (OSError,subprocess.CalledProcessError,UnicodeError) as e:
        print(f"ERROR: {e}",file=sys.stderr); return 2
    errors=validate_rows(rows,tracked)
    if errors:
        for e in errors: print("ENTRYPOINT_ERROR: "+e,file=sys.stderr)
        print(f"ENTRYPOINTS=FAIL errors={len(errors)}",file=sys.stderr); return 1
    print(f"ENTRYPOINTS=PASS studies={len(rows)} tracked_files={len(tracked)}"); return 0
if __name__=="__main__": raise SystemExit(main())
