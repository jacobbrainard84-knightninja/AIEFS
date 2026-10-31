# Repo automation drop-in for AIEFS (local only, not pushed)

Built by Auditor Seat 002 on 2026-10-28 for `jacobbrainard84-knightninja/AIEFS`. Nothing here has been pushed,
and no branch or PR has been created. The owner approves any push. Paths below are repo-relative.

## Files

| Path | What it is |
|---|---|
| `.github/PULL_REQUEST_TEMPLATE.md` | PR form: what changed; claims affected (before → after status); evidence and reproduction commands; checks run; Lean axiom result; privacy/hygiene checklist; "Major change?" checkboxes (DRAFT definition); reviewer sign-off table. Points at `CURRENT_STATUS.md`, `registry/README.md`, `OPERATING_MANUAL.md`, `docs/REVIEWING.md`. |
| `.github/workflows/repo-checks.yml` | CI on pull_request, push to `main`, and manual run. Four jobs: self-tests, claims lint, hygiene scan, manifest check. Actions are pinned to commit SHAs; read-only permissions; no stored credentials. The Lean build and axiom allowlist stay in the existing `lean.yml` (not duplicated, not edited). |
| `tools/ci/lint_claims.py` | Checks `artifact_status` and `audited_status` in `registry/claims.csv` against the list under `## Status vocabulary` in `registry/README.md` (exact match, one label per cell). Also: empty/duplicate `claim_id`, malformed rows, warns if the Speculative label is missing from the list, warns if an `SSRH-ORIG-*` row is Retired / Rejected / Quarantined. `audited_qualifier` is free text and is not checked. No `claims.csv` → notice, pass. |
| `tools/ci/claim_statuses.txt` | Fallback status list, used only if the README block is missing. A marked PLACEHOLDER with no values; the README is the single source. |
| `tools/ci/hygiene_scan.py` | Errors: file over 95 MiB; secret files (`.env*`, `*.pem`, `*.key`, keystores, SSH keys, `.netrc`, credential JSON); secret patterns (private-key blocks, AWS/GitHub/Slack/Stripe/Google/Hugging Face/xAI/OpenAI-style keys, JWTs); with `--base`, new binaries added outside the allowed folders. Warnings: files over 50 MiB, key/password assignments, binaries outside allowed folders (full scan), and with `--pii` e-mail/phone-like strings. Prints type and `path:line` only, never the matched text. `--private-patterns FILE` takes an owner-held list kept outside the repo. |
| `tools/ci/hygiene_allow.txt` | Folders where binaries (npz, pdf, zip, png, …) are allowed. DRAFT: owner to confirm. |
| `tools/ci/check_manifest.py` | Runs `AI Agent Audits/evidence/verify_manifest.py --inputs` (hash check of the published audit evidence). Notice and pass if the verifier is absent. |
| `tools/ci/tests/test_ci_tools.py` | 15 stdlib unit tests for the scripts above (fake secrets are built at run time, so the repo never contains one). |
| `docs/REVIEWING.md` | Short guide for GPT / Arena AI / human reviewers: run the checks, verify claims, privacy rules, DRAFT "major" definition. |
| `notes/status_suggestions.md` | **Not for the repo.** Suggested additions to `CURRENT_STATUS.md` §4, with cited paths, for its author to take or leave. |
| `README_AUTONOMY_SETUP.md` | This file. **Not for the repo.** |

## Dropping it into a branch (after owner approval)

```bash
cd <AIEFS checkout>               # e.g. the merge-prep worktree, on a side branch
SRC=/workspace/autonomy_setup/out
cp -r "$SRC/.github" "$SRC/tools" "$SRC/docs" .   # adds files; does not touch .github/workflows/lean.yml
python3 -m unittest discover -s tools/ci/tests
python3 tools/ci/lint_claims.py && python3 tools/ci/hygiene_scan.py && python3 tools/ci/check_manifest.py
git add .github/PULL_REQUEST_TEMPLATE.md .github/workflows/repo-checks.yml tools/ci docs/REVIEWING.md
git commit -m "ci: PR template, claims lint, hygiene scan, manifest check, reviewer guide"
# push only with the owner's approval
```

`tools/` already exists on `main` (`tools/sync/`); `tools/ci/` is new. Then update `OPERATING_MANUAL.md` §7
(owned by its author) to link the files and drop the "pending" note. Do not copy `notes/` or this README.

## Local test commands

```bash
python3 tools/ci/lint_claims.py [--repo PATH] [--strict]
python3 tools/ci/hygiene_scan.py [--repo PATH] [--base origin/main] [--pii] [--untracked] [--strict]
python3 tools/ci/check_manifest.py [--repo PATH] [--no-inputs]
python3 -m unittest discover -s tools/ci/tests -v
actionlint .github/workflows/repo-checks.yml     # optional workflow lint
```

Exit codes: 0 pass, 1 failure, 2 usage error. `--strict` makes warnings fail.
