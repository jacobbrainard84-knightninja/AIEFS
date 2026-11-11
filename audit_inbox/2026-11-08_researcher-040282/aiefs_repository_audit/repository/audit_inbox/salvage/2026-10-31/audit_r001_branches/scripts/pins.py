"""List all hash-pinned repo paths: audit_manifest (branch + main 853498f), artifacts.csv, *SHA256SUMS*."""
import json, csv, subprocess, sys, os, io, re
R = sys.argv[1] if len(sys.argv) > 1 else "."
pins = {}
def add(p, why): pins.setdefault(p, set()).add(why)
def manifest(txt, tag):
    M = json.loads(txt)
    for rel in M["files_sha256"]: add("AI Agent Audits/" + rel, f"audit_manifest[{tag}].files")
    for k in M["inputs_sha256"]: add(k.split(" (")[0], f"audit_manifest[{tag}].inputs")
    for k in M.get("post_manifest_logs", []): add("AI Agent Audits/" + k, f"audit_manifest[{tag}].post_logs")
manifest(open(os.path.join(R, "AI Agent Audits/evidence/audit_manifest.json"), encoding="utf-8").read(), "branch")
manifest(subprocess.check_output(["git", "-C", R, "show", "853498f:AI Agent Audits/evidence/audit_manifest.json"]).decode(), "main853498f")
for r in csv.DictReader(open(os.path.join(R, "registry/artifacts.csv"), newline="", encoding="utf-8")):
    if r["container"] == "worktree": add(r["path"], "artifacts.csv " + r["artifact_id"])
files = subprocess.check_output(["git", "-C", R, "ls-files"]).decode().splitlines()
for f in files:
    if "SHA256SUMS" in os.path.basename(f):
        base = os.path.dirname(f)
        for line in open(os.path.join(R, f), encoding="utf-8", errors="replace"):
            m = re.match(r"^([0-9a-f]{64})\s+\*?(.+)$", line.strip())
            if m:
                p = m.group(2)
                cand = [os.path.normpath(os.path.join(base, p)), os.path.normpath(p)]
                for c in cand:
                    if c in files or os.path.exists(os.path.join(R, c)): add(c, "SHA256SUMS " + f)
                else: add(os.path.normpath(os.path.join(base, p)), "SHA256SUMS(guess) " + f)
if __name__ == "__main__":
    q = sys.argv[2:]
    for p in q:
        hits = [k for k in pins if k == p or k.startswith(p.rstrip("/") + "/")] if p.endswith("/") else ([p] if p in pins else [])
        print(f"{p}: " + ("; ".join(f"{h} <- {sorted(pins[h])}" for h in hits[:10]) if hits else "NOT PINNED"))
