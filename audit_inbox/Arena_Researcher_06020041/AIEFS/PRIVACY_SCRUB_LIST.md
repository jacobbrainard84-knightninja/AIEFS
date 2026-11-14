# Privacy & copyright scrub list (merge-prep, 2026-10-28)

Prepared locally by Researcher 001 on branch `merge-prep/arena-reconciled`. **Nothing was removed, redacted or
rewritten**: this is a list for the owner and auditor to decide on. Values are **never** reproduced. Each item gives
only its type and location (file + page:line or line). Page:line positions come from `pdftotext` output (default mode
unless marked "layout"), so other PDF viewers may differ by a line or two.

Builds on `AI Agent Audits/licensing_inventory/INVENTORY.md` (round-4 licence/content inventory, "INVENTORY" below).
Items marked **[re-checked]** were confirmed again on the merged tree on 2026-10-28. The rest are carried over from
INVENTORY with its line reference.

---

## 1. Personal information in the current (merged) tree

| # | Type | Location | Status / note |
|---|---|---|---|
| P1 | Owner's personal email address | `Project Histories/Project Lead History 10.pdf` p.277, p.291, p.292 (3 occurrences) | **[re-checked]** Same address as in the git commit metadata (see §4). Redacting it changes this PDF's SHA-256 (it is inventoried in `registry/artifacts.csv`). |
| P2 | Downloader IP address in publisher download stamps (6 stamps, IP twice per stamp) | `Project Origins/grok ice 4009942.pdf` (layout mode) p.18:2–3, p.19:14–15, p.20:31–32, p.22:19–20, p.25:16–18, p.27:20–21 | **[re-checked]** PNAS "Downloaded from … by <IP> on March 22, 2026 from IP address <IP>" stamps. INVENTORY (line 112) says this is likely the owner's IP. |
| P3 | Third-party authors' institutional emails, two third-party personal webmail addresses, street-address patterns (author blocks of pasted papers) | `Project Origins/SSRH 001 stuff.pdf` (webmail p.25:31, p.431:18; street address p.512:16; institutional emails at the pages in INVENTORY lines 74–84; ORCID iDs p.647:4–5 (INVENTORY line 74)); `Project Origins/SSH history part 002461.pdf` (INVENTORY lines 70–73); `Project Origins/grok ice 4009942.pdf` (street address p.34:34 and p.35:1, INVENTORY line 89; other items INVENTORY lines 85–89); `Project Histories/SSRH 000244 Stuff.odt` (INVENTORY lines 65–69); `Project Origins/Origin Document.pdf` (1 email address in the author block of the pasted MMS article, p.133; pdftotext text line ~4309) | From INVENTORY; not re-checked one by one. These are other people's published contact details. They go away if the pasted-paper pages are removed (see §2). |
| P4 | Home-directory paths. Corrected 2026-10-28: in 40 of the 42 occurrences in arena-merged files the username matches an entry on the owner's private-literal list, so treat it as personal; only the 2 in `aief_1_3_disjoint_100seed_analysis_manifest.json` are a generic sandbox user | 292 occurrences in tracked text files (`git grep`). Files added by the arena merge: `audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md` lines 32, 34, 35; `audits/engineering/python_path_dependencies.csv` lines 3, 4, 7, 8, 140; `audits/github_reconciliation/GITHUB_TREE_AND_ZIP_RECONCILIATION.md` lines 49–52; `audits/github_reconciliation/zip_vs_tree_comparison.csv` lines 70, 71, 73, 74; `audits/github_reconciliation/recovered_from_workspace_019ff402/diffs_vs_root/*.diff` (4 files, lines 7–15); `audits/scientific/revalidated_summaries/aief_1_3_disjoint_100seed_analysis_manifest.json` lines 8, 14; `registry/artifacts.csv` lines 2830, 2831, 2833, 2834. Inside `Project Histories/workspace-019ff425-…zip`: 129 occurrences in 44 members. Other files: INVENTORY lines 91–108. `Project Origins/Origin Document 02.pdf`: a device-default terminal prompt with a home path, 40 occurrences (text lines ~7928–13243) | **[re-checked]** Not low risk where the username is the owner's (see Type). `REPRODUCING.md` no longer contains one (fixed in this branch). |
| P5 | Named personal device / OS | `audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md` lines 32, 34, 45, 50–54; `registry/artifacts.csv` lines 2729, 2730 (notes column); `registry/relocation_map.csv` lines 218, 219; `registry/claims.csv` row IMPL-MODULAR-01 (statement and caveat; **scrubbed 2026-10-28** to "a second Linux host", in the generated ledger and its build script); device type in `Project Origins/Origin Document 01.pdf` (10 occurrences) and `Project Origins/Origin Document 02.pdf` (20 occurrences); `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/PROJECT_INTEGRATION_MAP.md` lines 3, 224; inside `AIEF_Experiments/aief_modular_platform_v1_analysis_v4.zip` (1 member) and `Project Histories/workspace-019fb8fc-…zip` (`plot_numpy_data.py`) | **[re-checked]** Low risk. Removed from `REPRODUCING.md` in this branch; elsewhere left as is. |
| P6 | Code that records the computer's hostname into run manifests | `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/artifacts.py:315` (`socket.gethostname()`), `…/aief_modular/runner.py:244` (`platform.node()`); copies at `workspace-019ff86e-…/aief_modular/artifacts.py:225`, `runner.py:225`, and inside both platform zips | **[re-checked]** No tracked output file contains a recorded `"host":` value (only these 4 code lines match). Future runs *would* record it. Suggest a code change (not made here, because `aief_modular` is hash-locked by `authority.py`). |
| P7 | GitHub username | Repository URLs in many docs | Public by design, but **treat it as personal data** (owner decision 2026-10-28): do not add it to new files beyond the repository URL. |
| P8 | Personal context (occupation, background, device type) | `Project Origins/Origin Document 02.pdf`, ~7 occurrences at pdftotext text lines ~10046–10152 | Added 2026-10-28 (MERGE_CHECK Q7 #1; review hygiene scan). Not re-checked one by one. |
| P9 | Third-party author emails and ORCID iDs inside the deleted `Papers/` PDFs (see C6) | Git history only (INVENTORY lines 56–63) | Added 2026-10-28 (MERGE_CHECK Q7 #8). Not in the current tree; only a history rewrite (§4) removes them. |

No passwords, API keys or tokens were found (INVENTORY line 117; not re-scanned in full here).

## 2. Third-party copyrighted material

Licence context: `LICENSING.md` and `NOTICE` (added on `main` in 115e99e, 2026-10-24) already state that third-party
papers are not licensed by the project. That disclaimer does **not** give anyone a right to redistribute those papers.

| # | Item | Location | How much | Note |
|---|---|---|---|---|
| C1 | **PNAS article**, Dalal et al. 2015, doi 10.1073/pnas.1421042112, with publisher download stamps | `Project Origins/grok ice 4009942.pdf`, about pp.17–35 (article DOI first appears at p.17:42, layout mode; stamp lines as in P2) | Near-complete article | **[re-checked]** Highest-priority copyright item. It also carries the IP addresses in P2. |
| C2 | Several full or near-full pasted papers (AAS 2005 p.24; Phys. Rev. Lett. 2019 p.53; Science Advances 2025 pp.~497–512, copyright line p.512:17; and others) | `Project Origins/SSRH 001 stuff.pdf` | Substantial | From INVENTORY line 33 and lines 145–150. |
| C3 | Pasted paper excerpts, with copyright line p.108:4 and a CC BY article at p.453 | `Project Origins/SSH history part 002461.pdf` | ~45 of 763 pp. (heuristic) | From INVENTORY line 32 and lines 143–144. |
| C4 | Pasted papers/abstracts (AIMS Press 2025 CC BY, Springer 2020, …); copyright line at line 3135 | `Project Histories/SSRH 000244 Stuff.odt` | ~54 blocks (heuristic) | From INVENTORY line 31 and lines 139–142. |
| C5 | AI summaries / short quotes only | `Project Origins/SSRH stuff.pdf`, `Project Origins/grok ice 400994202.pdf`, `Project Histories/Project Lead History 03.pdf` | Minimal | From INVENTORY lines 34, 36, 30. Probably fine as is. |
| C6 | **Four standalone third-party papers, deleted from the tree but still in git history** (3 papers by one self-published author, each with "© … All rights reserved"; 1 arXiv paper) | Former `Papers/` (4 PDFs). Added in the first commit `add81e6` (2026-10-18); removed in `d12b08c`, `15feb9b`, `aae9e75`, `17f2cf7` (2026-10-24) | Whole papers | **[re-checked]** Anyone can still get them from any commit before the removals. Only a history rewrite removes them (§4). In `registry/artifacts.csv` they are flagged `MISSING_DELETED_ON_MAIN`. |
| C7 | "All rights reserved" headers on Apache-2.0 Lean files (own work, not third-party) | `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean:2`, `ControllerFiberProjector.lean:2`, `ControllerFiberQuotient.lean`, `CompleteGraphIncidence.lean`; also `AI Agent Audits/lean_recovery/**` (INVENTORY lines 123–130) | — | Not a conflict (corrected 2026-10-28). "Copyright … All rights reserved. Released under Apache 2.0 license …" is the standard Mathlib header form and is compatible with Apache-2.0. No privacy issue and no owner decision needed. |
| C8 | Pasted MMS foreshock article (journal article text with its author block) | End of `Project Origins/Origin Document.pdf` (around p.133) | Article-length | Added 2026-10-28 (MERGE_CHECK Q7 #5; review hygiene notes). Its author email is listed under P3. |
| C9 | Pasted YouTube video transcript | `Project Origins/Origin Document 02.pdf`, pdftotext text lines ~10238–10580 | Transcript-length | Added 2026-10-28 (MERGE_CHECK Q7 #5). |

INVENTORY line citations above were corrected on 2026-10-28 against the INVENTORY file (MERGE_CHECK Q7 table).

## 3. Misleading artifacts (look like passing results but are synthetic)

| # | Location | What it is | Recommendation |
|---|---|---|---|
| M1 | `Project Histories/workspace-019fb8fc-d3d9-784a-82a5-03d4ec3f136c.zip` (sha256 `037d984e3389…`) → member `output_audit/analysis_manifest.json` line 8 (`"mode": "synthetic_replay_generator"`), line 20 (`"gate_status": "PASSED"`) | Output of the proposal-bridge audit run on **generated synthetic replay data** (`aief_proposal_bridge.generate_synthetic_replay_data`, used by `test_aief.py`), not on a real simulation run. The manifest *looks* like a real-run "PASSED" gate. | **[re-checked]** Do not cite. Mark it as a synthetic test fixture in the registry (it has no row today, because zips under `Project Histories/` were added after the arena inventory). Do not edit inside the zip. |
| M2 | Same zip → member `output_alignment_decomposition/analysis_manifest.json` line 8 (`"mode": "synthetic_aligned_replay_generator"`), line 20 (`"cone_invariance_passed": true`) | Same pattern for the directed-alignment decomposition. Line 31 itself says "saved/synthetic replay". | **[re-checked]** Same as M1. |

Both members carry a real-looking `seed_id`, which makes them easier to mistake for production output.

## 4. Git history: what a rewrite would involve (NOT performed)

Two things cannot be fixed by editing files, because every earlier commit keeps them:

1. **Owner's personal Gmail in commit metadata.** 119 of the 128 commits on `origin/main` (as fetched for this
   merge-prep) carry it as author and/or committer; the rest use the GitHub no-reply address. The arena commit `7edbab2`
   uses the no-reply address. **[re-checked]**
2. **Blobs of removed or redacted files** (C6, and the old versions of P1/P2/C1 if those PDFs are later redacted or
   removed). They stay retrievable from history.

How it would be done (for the owner to decide; nothing here was run):

- Use `git filter-repo` on a **fresh mirror clone**:
  - `--mailmap` (or `--email-callback`) to replace the Gmail with the no-reply address on all commits;
  - `--path Papers/ --invert-paths` to drop the four papers;
  - optionally `--replace-text` / `--blob-callback` or path removal for the PDFs in §1–2.
- Then force-push every branch and tag, and ask GitHub Support to purge cached views and pull-request refs. Forks,
  existing clones, and any copies elsewhere keep the old data. A rewrite cannot recall them.

Consequences to weigh:

- **Every commit hash changes**, because the papers were added in the very first commit `add81e6`. So:
  - Audit records that cite commit hashes become stale. Examples:
    - `AI Agent Audits/evidence/audit_manifest.json` cites `6b49a7b`.
    - 17 tracked files cite the arena merge base `e47bad1`.
    - `registry/artifacts.csv` describes the tree "at `e47bad15`".
    - `audits/engineering/verify_inventory.py` uses `e47bad1` as its conservation base.
  - The audits would need a short note mapping old hash → new hash.
- **File SHA-256 pins change only for files whose content is changed.**
  - Rewriting only the email metadata leaves every file hash valid.
  - Redacting P1/P2/C1 changes those PDFs' hashes in `registry/artifacts.csv`.
  - Editing `Project Histories/workspace-019ff425-…zip` (P4) would break the audit reproduction `AUD-REPRO-B2A95`.
    `audit_manifest.json` pins that zip (sha256 `281bf33b…`). **Recommend leaving that zip as is.**
- This merge-prep branch itself was committed locally as "Researcher 001 (local)" (with a local placeholder committer email).
  If it is accepted, the owner may want to re-author those commits before any push.

## 5. Decisions needed (owner)

1. Remove or redact C1 (PNAS article and IP stamps), and decide on C2–C4 (pasted papers inside chat exports).
2. Redact P1 (own email in a chat-export PDF), or accept it.
3. Rewrite history (§4) to drop the Gmail metadata and the four `Papers/` PDFs, or accept that they stay public.
4. Mark M1/M2 as synthetic fixtures in the registry.
5. Change the hostname capture (P6) for future runs. This needs an `authority.py` lock update.
6. (Closed 2026-10-28.) The Lean header wording (C7) is the standard Mathlib form, not a conflict.
7. Decide on P8 (personal context) and C8–C9 (pasted MMS article, YouTube transcript) in the Origin Documents.
8. Treat the GitHub username as personal (P7) in any future text.
