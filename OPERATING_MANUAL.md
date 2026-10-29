# Operating manual (read this at the start of every session)

This file is for every AI bot that works in this repository. It is short on purpose. If it conflicts with
another doc, follow this file and tell the owner about the conflict.

## 1. Goal

Build a system that reliably produces **true, checkable work** in which new mathematics *could* be found.
Correctness and checkability come first. Novelty is secondary. A small result that is correct and
reproducible is worth more than a large one that cannot be checked.

## 2. Roles

| Role | Does | Does not |
|---|---|---|
| **Researcher 001** (bot) | Proposes research, runs simulations, prepares changes on side branches, updates the claim ledger, writes errata | Approve its own work |
| **Auditor Seat 002** (bot) | Independently audits and reproduces Researcher 001's work; builds the automated checks | Approve its own work |
| **Other reviewers** (the owner's GPT and Arena AI teammates) | May review branches and claims | Approve on the owner's behalf |
| **Owner** | Sets direction; approves pushes and major changes (§5) | — |

Neither bot approves its own work. A claim that only its author has checked is not audited.

## 3. Claim labels

The rules are in `registry/README.md`: two axes, three status categories, and the exact allowed values.
In short:

- Every claim is a row in `registry/claims.csv` with `artifact_status`, `evidence_scope` and
  `audited_status` (with free-text detail in `audited_qualifier`). Cite a claim only at the scope its row gives.
- **Past origin hypotheses** (`SSRH-ORIG-01..07`) are labelled *Speculative / untested origin
  hypothesis*. They are not results, and they are not retired. They can be promoted once a testable
  form is stated and a test is run.
- **Current tested results** are labelled Supported, Exploratory and so on. Each label comes with its
  scope and caveats.
- **Future untested ideas** are labelled Conjecture or Not established. They are open questions.
- **Retired / Rejected / Quarantined** are only for claims that were **tested and failed, or were
  withdrawn**. Never use them for an idea that simply has not been tested.
- Use only the values in "## Status vocabulary" in `registry/README.md`.

Framing, used in `CURRENT_STATUS.md` §4:
- **where we've been**: origins, retired claims, past audits;
- **where we are**: current tested results and open review;
- **where we're going**: untested ideas and next steps.

## 4. Workflow

1. Work on a **side branch**. Never commit directly to `main`.
2. Open a **pull request into `main`**. A reviewer other than the author checks it (§2).
3. **Do not edit hash-pinned files**, i.e. files listed in `AI Agent Audits/evidence/` manifests or in
   `twindow_*hashes*.txt`. Put corrections in a dated **errata sidecar file**, for example
   `ERRATA_2026-10-28.md`, and in `registry/claims.csv`.
4. When a claim changes, update the ledger through
   `registry/reconciliation/build_claims_reconciliation.py`, not by hand.
5. Before handing off, run the validators and report the results exactly:
   - `python "AI Agent Audits/evidence/verify_manifest.py"` and the same with `--inputs`
   - `python audits/engineering/validate_registry_against_tree.py --base e47bad1 --edited-since <merge commit>`
   - `python audits/engineering/verify_inventory.py` (known to stop at check [1/5]; see `MERGE_PREP_REPORT.md`)
   - `lean/AIEFProofs/check_lean.sh` when Lean files change
6. Commits are small and clearly described. Never rewrite history unless the owner asks for it.
7. Report honestly. Say what was run and what was not, and do not claim a file exists without checking.

## 5. Approval levels (staged)

**CURRENT PHASE (in force now):**
- Ask the owner **before every push to GitHub, on any branch**.
- Local commits on side branches are fine without asking.

**NEXT PHASE.** This starts only when the owner declares it, after the owner, GPT and Arena AI
reviewers have reviewed the set-up branch.
- Bots may work, commit and push side branches freely.
- The owner approves only **major changes**.

**Definition of "major change": DRAFT, needs the owner's confirmation.** A change is major if it:
- merges anything into `main`;
- changes a claim's status to `Supported` or `Frozen`;
- retires, rejects or quarantines a claim;
- rewrites git history (rebase, amend or force-push of shared commits);
- touches privacy or PII in any way, including scrubbing;
- deletes files;
- changes this manual or the claim-label rules.

Until the owner confirms this list, treat anything unclear as major.

## 6. Privacy

- **Never commit personal details**: names, emails, street addresses, IPs, device names, home-directory
  paths, account usernames or private context. This applies to files, commit messages and reports.
- Known locations are listed in `PRIVACY_SCRUB_LIST.md`. That file gives **locations and types only,
  never values**. Keep it that way.
- Scrubbing and history rewrites are owner decisions (§5).

## 7. Automated checks

These are **present** in this branch. Auditor Seat 002 wrote them, and they were integrated unchanged. They have
not run on GitHub yet, because nothing has been pushed. Run them locally before every handoff.

- [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md): the form every PR fills in, covering what changed, claims affected, evidence, checks run, privacy and reviewer sign-off.
- [`.github/workflows/repo-checks.yml`](.github/workflows/repo-checks.yml): CI that runs the self-tests, the claims lint, the hygiene scan and the manifest check on every pull request. The Lean build and axiom allowlist stay in the existing [`.github/workflows/lean.yml`](.github/workflows/lean.yml).
- [`tools/ci/lint_claims.py`](tools/ci/lint_claims.py): checks every `artifact_status` and `audited_status` in `registry/claims.csv` against the `## Status vocabulary` block in `registry/README.md`.
- [`tools/ci/claim_statuses.txt`](tools/ci/claim_statuses.txt): a placeholder fallback list, used only if that README block is missing.
- [`tools/ci/hygiene_scan.py`](tools/ci/hygiene_scan.py): flags large files, secret files and patterns, and unexpected binaries (with `--pii`, also e-mail- and phone-like strings), printing only the type and `path:line`, never the value.
- [`tools/ci/hygiene_allow.txt`](tools/ci/hygiene_allow.txt): the folders where binary files are allowed. **This is a draft that the owner still needs to confirm.**
- [`tools/ci/check_manifest.py`](tools/ci/check_manifest.py): runs the audit-evidence hash check (`verify_manifest.py --inputs`).
- [`tools/ci/tests/test_ci_tools.py`](tools/ci/tests/test_ci_tools.py): unit tests for the scripts above (`pytest tools/ci/tests -q`).
- [`docs/REVIEWING.md`](docs/REVIEWING.md): a short guide for outside reviewers (GPT, Arena AI, humans) on running the checks and verifying claims.

## 8. Where things stand

- `CURRENT_STATUS.md` is the **single status file** (see §4 there: been / are / going).
- `MERGE_PREP_REPORT.md` covers the current merge-prep branch: commits, checks and open owner items.
- `ERRATA_2026-10-28.md` holds the corrections to hash-pinned files.
- `registry/claims.csv` is the per-claim ledger.
