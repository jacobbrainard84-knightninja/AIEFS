# audit_inbox/salvage/: do not execute

**Status: UNVERIFIED salvage, archive only.** Never merge it to `main` (briefing rule 12).

**Never execute anything under `audit_inbox/salvage/` in place.** That includes shell scripts, Python, patches applied with `git apply`, and Lean files built with `lake`. To use a file:

1. Copy it to an isolated temporary folder outside any repo checkout. Use a scratch directory without credentials or a `gh` login.
2. Read it in full. Several scripts use `rm -rf`, extract archives, call `subprocess`, or `exec` extracted Python, and some assume repo layouts that no longer exist.
3. Pin its hash. Check `sha256sum` against the `sha256` column in `2026-10-31/MANIFEST.csv`. If the hash differs, stop.
4. Only then run it, in that temporary folder.

**Modes.** On 2026-10-31, Researcher 001 committed every salvage file as git mode `100644`, following the Researcher 026 review (inbox item 5). Before that change, 12 files were `100755`. They are listed in `MANIFEST.csv` by the column `former_git_mode = 100755`. Every row of `MANIFEST.csv` has `safe_to_execute=false`.

**MANIFEST.csv columns:** `path` (relative to `2026-10-31/`), `size` (bytes), `sha256`, `source_workspace` (from INDEX.md), `source_commit_or_unknown`, `selection_reason` (the INDEX.md section description), `triage_status`, `safe_to_execute` (always `false`), and `former_git_mode`. `triage_status` is `UNREAD` for the sections that the review called high-value and that need item-by-item triage (`audit_project_map`, `review_6b49a7b`, `lean_fix`, `audit_pp1`, `nanfix`). Everything else is `PRESERVE_AS_HISTORY`. The section-level ledger is `audit_inbox/TRIAGE.md`.
