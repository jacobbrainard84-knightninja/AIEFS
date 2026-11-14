# AIEFS — project audit (external-agent snapshot)

**Classification under the project's own rules:** UNVERIFIED INPUT. This is an outside-agent review, not a finding, claim, erratum, or ledger change. Under `audit_inbox/README.md` it becomes evidence only after Researcher 001 / Auditor Seat 002 independently triage it. Nothing here has been pushed, committed, or merged.

**Snapshot audited:** `main` @ `a559e0d30458bb01989ac47225675d6baec518b8` (repo timestamp 2026-11-11), `audit-inbox` @ `69221804` (2026-11-12/13), and the tips of all 11 non-main branches. Local clone: `/home/user/AIEFS`.

> **Date note.** All dates below are repository/GitHub timestamps, which extend into November 2026. My session clock reports 2026-09-11. I have reported the repository's own chronology verbatim rather than reinterpreting it; treat all "latest" statements as relative to the repo's history, not my clock.

---

## 0. Executive summary

1. **The integrity layer is genuinely strong.** A 2,898-row SHA-256 artifact registry, a current-tree inventory, an 80-row claim ledger, hash-pinned audit evidence, four required Lean CI jobs, red-team negatives, and a mutation check all pass. I re-ran the Python/CI checks locally: essentially everything green.
2. **The scientific layer is honest but narrow.** The strongest results are conditional, single-cohort, or single-seed. Retired claims are preserved rather than hidden. Novelty is explicitly *not established*. The central open problem is **O1: closed-loop phase locking** — the freezing theorem assumes it; nothing proves it.
3. **The real bottleneck right now is integration and status truth, not correctness plumbing.** `main` has been frozen since 2026-11-11 with **zero open PRs**, while the active frontier (P5 Lean work, c014 trajectory safety, the north-star plan) sits on unmerged branches. The newest inbox review (2026-11-13) is untriaged. Meanwhile the two flagship status documents describe an October state.
4. **The "north-star" is not one document.** It exists in three places with different scopes, and two of them are not on `main`. That is a findability/governance problem before it is a research problem.
5. **Highest-leverage next work** is to (a) land and refresh the Lean P5 / c014 branches with a production-delay (`D = 50`) engine probe, (b) close the confirmed verification gaps (`check_modes` OOM, G2c trust anchor, red-team CI, 11 unresolved study entrypoints), and (c) reconcile the stale docs, ledger qualifiers and Issue #14 — then resume the O1 / dt / multi-seed science.

---

## 1. What I actually did

- Shallow-cloned `main`, then fetched all 11 other branch tips (`audit-inbox`, `research/lean-gate-p5`, `research/lean-gate-c014`, `research/aiefs-northstar-evaluation`, `arena/d4a487cc-aiefs`, etc.). Fetched historical base `e47bad1` separately so `verify_inventory.py` could run as designed.
- Queried the GitHub API for repo metadata, branches, PRs, Issue #14, PR #13, branch comparisons, and the 30 most recent Actions runs.
- Read the governing docs: `OPERATING_MANUAL.md`, `README.md`, `CURRENT_STATUS.md`, `REPRODUCING.md`, `registry/README.md` + `claims.csv` + `studies.csv`, `ERRATA_2026-10-28.md` (through E26), `AI Agent Audits/README.md`, `lean/AIEFGateCore/README.md`, `research/lean_gate/SPEC_P1_gate_identities.md`, `AIEF_1_4_FORWARD_PLAN.md`, `docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md`, and the `audit_inbox/briefing/` set (`NORTH_STAR.md`, `STATE.md`, `OPEN_QUESTIONS.md`, `RESEARCH_LEADS.md`, `README.md`).
- Ran the repository's own validators and test suites locally (§5). **Did not run any Lean build** — `lean`, `lake` and `elan` are not installed in this environment.

---

## 2. Repository state (verified facts)

| Item | Value |
|---|---|
| Default branch / head | `main` @ `a559e0d` (merge of PR #30) |
| History | 315 commits; created 2026-08-24; **0 tags, 0 releases** |
| Tracked files / size | **3,095 files**, ~1.6 GB working tree |
| Composition | 2,006 `.npz`, 339 `.csv`, 270 `.py`, 138 `.json`, 89 `.txt`, 73 `.md`, 52 `.log`, **36 `.lean`**, 19 `.pdf`, 14 `.diff`, 13 `.sh`, 6 `.zip`, 5 `.yml` |
| Branches | **12**; several are stale/merged remnants |
| Open PRs / merged PRs | **0 open**; PRs through #30 merged; PR #13 closed **unmerged** |
| Open issues | **1** — #14, "resolve controller-fiber rate-law residual with a branch-aware step-size sweep" |
| CI | 191 Actions runs; all 30 most recent are `success` (18 Lean, 12 Repo checks); latest green on `a559e0d`, 2026-11-11 12:01Z |
| Workflows | `.github/workflows/lean.yml` (4 required Lake projects), `.github/workflows/repo-checks.yml` (9 jobs) |
| Community | 0 stars, 0 forks, Apache-2.0 code / CC BY 4.0 docs; single-owner hobby project |
| External input | Repo description: outside notes only as unverified input via the `audit-inbox` branch |

`lean.yml` requires `AIEFProofs`, `AIEFProofsKn`, `AIEFFreezeCore`, `AIEFGateCore`, with forbidden-marker scans and an axiom allowlist (`propext`, `Classical.choice`, `Quot.sound`); the `AIEFGateCore` row also runs `lean_mutation_check.py`.

---

## 3. The north-star is three different documents

| Source | Status | What it says |
|---|---|---|
| `OPERATING_MANUAL.md` §1 | **On `main`, governing** | "Build a system that reliably produces **true, checkable work** in which new mathematics *could* be found. Correctness and checkability come first. Novelty is secondary." |
| `audit_inbox/briefing/NORTH_STAR.md` | Navigation-only, **not authority**, updated 2026-11-11 | "Build a **machine-checked Lean 4 reference library for adaptive oscillator networks**" — formalize the *actual dynamics*: delayed Kuramoto, coherence/EMA, Hebbian weights, capacity gate, conditional rate laws, fiber/kernel properties, restricted convergence. Includes a living 7-row checklist and a theorem-level dependency chain. |
| `research/northstar/AIEFS_NORTHSTAR_EVALUATION_2026-11-08.md` | **Only on `research/aiefs-northstar-evaluation`**; PR #13 closed unmerged; branch is 1 ahead / 62 behind `main` | Publication-grade framing: "a mathematically precise, computationally falsifiable theory of when delayed phase/EMA feedback and a capacity-constrained adaptive coupling map create, preserve and reconstruct sparse topology — and which statements survive seeds, frequency ensembles, time step and admissibility branch", with a P0–P5 programme and a 6-stage delivery table. |

**Finding:** `research/northstar/` does not exist on `main`. A new agent reading only `main` sees the general goal and the 2026-10-19 `AIEF_1_4_FORWARD_PLAN.md`, but not the Lean library checklist nor the P0–P5 research programme. The project's direction is currently split across a protected doc, a briefing marked "navigation only", and an abandoned PR.

---

## 4. Governance constraints that bind the next phase

From `OPERATING_MANUAL.md`, `audit_inbox/README.md`, `PROJECT_CHRONICLER_AGENT.md`, and `audit_inbox/briefing/OPEN_QUESTIONS.md`:

- **Side branch + PR + independent reviewer.** Never commit to `main`; the author never approves their own work.
- **Ask the owner before every push, on any branch** (current phase). Local commits on side branches are allowed. No GitHub connector is connected in this session, so I have worked read-only; I will not push.
- **Never edit hash-pinned files** (audit-evidence manifests, `twindow_*hashes*.txt`, Lean source-sums, frozen runs). Corrections go in dated errata sidecars + `registry/claims.csv` via `registry/reconciliation/build_claims_reconciliation.py`.
- **No PII, no secrets, no outreach** (contacting researchers is owner-only), no history rewrites, no deleting files, no privacy scrubbing without owner approval.
- **External notes** go only into `audit_inbox/` as new files named `YYYY-MM-DD_<agent>_<topic>.md`, with agent/date/commit/scope headers and file:line:sha citations; they are UNVERIFIED INPUT until triaged. `audit-inbox` and `arena/d4a487cc-aiefs` trees must **never be merged into `main`**.
- **Standing owner priority:** hunt for code that builds in the hoped-for result (hard-coded constants, always-pass tests, silent fallbacks, loosened tolerances, self-comparison). Feed checks known-false input; they must FAIL. Never silently loosen a pass/fail rule.
- Every new numerical result needs source/input hashes, seed and parameter provenance, output hashes and a reproduction command.

---

## 5. Verification I ran on `main`

| Check | Result | Notes |
|---|---|---|
| `AI Agent Audits/evidence/verify_manifest.py` | **PASS** | 145 published files; 2 post-manifest logs listed but unhashed (by design) |
| `tools/ci/check_manifest.py` | **PASS** | isolated `--inputs` run; 145 + 24 inputs |
| `tools/ci/lint_claims.py` | **PASS** | 80 rows, 14 statuses, 0 violations |
| `tools/ci/check_sha256sums.py` | **PASS** | 8 SUMS files, 82 entries, 0 errors |
| `tools/ci/check_artifact_pins.py` | **PASS** | 2,898 rows: 2,838 match, 7 known-changed, 53 known-missing; **1 notice**: `FLAG_DISAGREES ART-2717 test_01.py` absent but flagged present |
| `tools/ci/check_current_inventory.py` | **PASS** | committed CSV is current |
| `tools/ci/check_pinned_restatement.py` | **PASS** | 4 Pinned modules byte-equivalent to `AIEFProofs` sources |
| `audits/engineering/verify_inventory_current.py` | **PASS** | 5/5 gates incl. live authority lock |
| `audits/engineering/verify_inventory.py` | **FAIL (known)** | Stops at `[1/5]`: 52 files from `e47bad1` deleted/moved (`Papers/`, `__pycache__/`, `.lake/`, an editor lock). Documented in `REPRODUCING.md` / `MERGE_PREP_REPORT.md`; I confirmed by fetching the base commit |
| `tools/ci/hygiene_scan.py` | **PASS** | 3 `BIG_FILE` warnings (56.0 / 63.5 / 51.4 MiB CSVs); 30 files >10 MiB were size-checked only |
| `tools/ci/check_modes.py` (plain and `--strict`) | **OOM-killed, exit 137** | Reproduced in a ~2 GiB sandbox. `shebang_objects()` buffers the entire `git cat-file --batch` output just to read 2 bytes per blob; `OPEN_QUESTIONS.md` §15 reports ~2.4 GiB peak RSS. CI passes on GitHub runners. **Real portability defect, already known, not fixed** |
| `python -m unittest discover -s tools/ci/tests` | **183 OK** | unclosed-file `ResourceWarning`s only |
| `pytest research/lean_gate/tests` | **54 passed** | |
| `pytest` v4.1 held-event + trust-anchor | **45 passed** | ~59 s |
| `pytest tests_modular` (default) | **60 passed, 2 skipped, 2 xfailed** | 64 collected |
| `pytest tests_modular` (`AIEF_RUN_SLOW_TESTS=1`, root `PYTHONPATH`) | **61 passed, 1 skipped, 2 xfailed** | ~20 s |
| Lean builds (`check_lean*.sh`) | **NOT RUN** | no `elan`/`lake`/`lean` installed. CI reports 4/4 required projects green; I have not independently reproduced a `lake build` |

**Doc drift in expected test counts:** `README.md` says 44/43 passed with/without slow tests; `REPRODUCING.md` §3 says 41 passed, 1 skipped; `repo-checks.yml` comment says 43 passed, 2 skipped, 2 xfailed. Actual: **61 / 60 passed**. All three are stale by ~17 tests.

---

## 6. Scientific state: the claim ledger

`registry/claims.csv` has **80 rows**, two-axis classified:

- `artifact_status`: 35 Supported, 18 Superseded, 11 Incomplete, 7 Exploratory, 6 Rejected, 3 Frozen.
- `evidence_scope`: 40 Finite numerical observation, 14 Conditional theorem, 13 Conjecture, 6 Implementation identity, 4 Formalized theorem, 3 Controlled experimental result.
- `audited_status`: 33 Supported, 18 Retired/Superseded, 7 Speculative/untested origin hypothesis, 5 Finite numerical observation, 5 Rejected, 4 Exploratory, 4 Not established, 2 Conjecture/Exploratory, 1 Controlled exploratory, 1 Quarantined.

**Supported, with caveats:** 100-seed AIEF-1.3 paired ablations (`shuffle_R` is forced by construction); 40-seed AIEF-1.4 split-state memory ablation (topology rebuilds from phase/history/EMA when `B` is reset; no unique memory carrier); conditional rate law on controller-kernel fibers; gate is multiplicative normalisation, **not** a projection; Lean linear-algebra/incidence results.

**Retired / quarantined:** "EMA pole is the unique slow pole", "strict K3 components are spectrally silent", causal mediation wording, universal rate claims, `Corr_physical ≈ 0.995` as a generic fact (it holds only for hand-picked `ω`).

**Untested, explicitly kept:** 7 SSRH origin hypotheses (`SSRH-ORIG-01..07`), `CF11`/`CF12` persistence conjectures, `AUD-NOVELTY`, `AUD-TIMESTEP`, `AUD-B-SCAFFOLD`.

**Rate-law residual — important status correction.** Issue #14, `README.md:53` and `registry/claims.csv:50` still say the ~2e-8 gap "stays unexplained until a step-size sweep is run" and "No sweep has been run". That is **stale**: `ERRATA_2026-10-28.md` **E22** / PR #18 (merged 2026-11-09) ran a predeclared 46-point sweep on the exact gap component (seed `4619122171158768524`, ρ=1.0, K3 `[2,7,11]`, historical δ=1.062225811e-9). The committed JSON `research/rate_law/results/rate_law_delta_sweep_v1.json` records `"label": "UNEXPLAINED"` because `C4 closes_on_branch` failed (2.1698e-10 vs a 2.1e-10 bound). Exact-rational evaluation matches the state formula to 4.04e-13 and the float error scales as 1/δ; the rule was deliberately **not** loosened. The verdict is correct; the *status text* in three places is not.

**Biggest science gaps:** O1 closed-loop phase locking; no dt/2, dt/4 timestep study; the operator/cocycle pipeline is a single-seed case study (1 of 40); CF11/CF12 unproved; RES-FREEZE novelty is "known variant, narrow residual plausibly new, search non-exhaustive"; Arena round-10 vs AUD-RATELAW adjudication is open; a v2 predeclared rate-law rule would be post hoc unless reviewed before running.

---

## 7. Frontier: work that exists but is not on `main`

| Branch | Relation to `main` | Content / status |
|---|---|---|
| `research/lean-gate-p5` | **4 ahead / 3 behind**, merge base `75f2b74` | P5 Lean ports: `HistoryBuffer.lean`, `PhaseIncrement.lean`, `PhaseCoherence.lean`; mutants M37–M58; SPEC §11; 707 declarations, 58/58 mutants reported locally. Local gate PASS, but branch predates PR #30, has 6-file merge conflicts, and its docs are stale. **No open PR.** |
| `research/lean-gate-c014` | **1 ahead / 8 behind** | `TrajectoryInvariants.lean` → `AIEFGate.TrajectorySafety` (all-step structural/capacity/envelope safety under arbitrary feedback drive). Local gate PASS 677 decls; awaits independent audit; planned to land after P5. |
| `research/aiefs-northstar-evaluation` | **1 ahead / 62 behind** | The single north-star evaluation doc; PR #13 closed unmerged. |
| `audit-inbox` | separate tree | ~27 top-level review notes plus hundreds of nested evidence/artifact files; newest `2026-11-13_gpt-6_p5-delay-buffer-audit.md` has **no `TRIAGE.md` row yet**. |
| `arena/d4a487cc-aiefs` | 2026-10-31 | Arena rounds 5–10 including `ROUND_10_FINDINGS.md` (gate is edge-dependent, not a global rescaling). Never merge. |
| Others | `fix/lean-mutation-step-guard*`, `research/engine-step-order*`, `fix/manifest-nonempty`, `docs/lean-gate-doc-drift` | Mostly merged/superseded remnants; `fix/manifest-nonempty` is an owner item, do not delete. |

**I independently triaged the three claims in the newest (2026-11-13) inbox note — all CONFIRMED:**

1. **Production delay is untested.** `aief_experiment_engine_v1.py:64-65,95` gives `dt=0.01`, `tau=0.5` → `delay_steps = 50`; `:711` builds a 51-entry history; `:729` `compute_R` reads `history[0]`; `:830-835` coupling reads `history[0]`; `:843-844` append/pop. But `research/lean_gate/tests/test_engine_step_order.py:40` hard-asserts `c.delay_steps == 1`, so all four step-order probes use a two-slot queue. The Lean P5 `HistoryBuffer` theorems are general in `D`, but are abstract sequences, not Python list/aliasing equivalence. **Confirmed coverage gap, not a runtime bug.**
2. **P5 doc drift.** On the P5 branch, `SPEC_P1_gate_identities.md` §11.6 still says "the mutation check is not run in CI", while `.github/workflows/lean.yml:93-102` runs it; P5's `lean/AIEFGateCore/README.md` still describes 23 statement + 16 definition mutants and one expected survivor, while `lean_mutation_check.py` has M57–M58, 20 `DEF_MUTANTS`, `KNOWN_SURVIVORS = []`, and SPEC §11.7 records 38 + 20 = 58 mutants.
3. **Branch freshness** — confirmed via GitHub compare API (4 ahead / 3 behind).

---

## 8. Confirmed drift / gap register (prioritised)

| # | Finding | Evidence | Why it matters |
|---|---|---|---|
| G1 | **Frontier work stranded off `main`** | 0 open PRs; P5, c014, northstar plan unmerged; `main` frozen 2026-11-11 | North-star components 1–2 (delay, EMA) exist only on branches; nothing can be cited as a result |
| G2 | **Status docs stale** | `CURRENT_STATUS.md` "Last Verified 2026-10-23", "75 rows" (actual 80), no mention of E22, P1–P5, PRs #18–#30; `README.md` last touched 2026-10-31; `REPRODUCING.md` 2026-10-29 | A new agent following `main` docs gets a wrong map; the project's own "single status file" is no longer single-source truth |
| G3 | **Rate-law sweep status stale** | Issue #14 "No sweep has been run"; `README.md:53`, `claims.csv:50`, `CURRENT_STATUS.md:101` say sweep pending; E22/PR #18 ran it 2026-11-08/09 | Wastes the next cycle on an already-executed protocol; hides a good negative result |
| G4 | **Ledger qualifier false** | `claims.csv:71` `LEAN-FREEZE-CORE` says "branch-only, not yet on main"; it landed via PR #3 and is a required CI row | Authoritative ledger contains a false scope statement |
| G5 | **Lean README false** | `lean/AIEFProofsKn/README.md:80` says "This project is not yet in CI"; `lean.yml` has it `required: true` | Misleads reviewers about verification coverage |
| G6 | **`check_modes.py` OOM** | Reproduced exit 137 locally; `OPEN_QUESTIONS.md` §15 documents ~2.4 GiB peak | A CI gate cannot be reproduced on modest hardware; `--strict` in CI passes only because runners have more RAM |
| G7 | **Study entrypoints unresolved** | 15 study rows, 37 entrypoint tokens, **11 unresolved** (wildcards `AIEF_1_0_*.py` etc., deleted `Papers/`, missing tangent/fiber scripts). `CURRENT_STATUS.md` cites 11 absent paths. Architecture doc says "14 studies / 43 claims" (actual 15 / 80) | No CI check covers this; the "reproduce each study" story is not actually executable |
| G8 | **Red-team suite outside CI** | `tools/redteam/` exists; no workflow references it | Known-false-input negative controls are not continuously enforced |
| G9 | **G2c trust anchor open** | North-star evaluation §P5 item 1 and briefing `STATE.md`: a re-pinned verifier stub can pass the manifest wrapper because manifest+verifier are not pinned outside themselves | Self-referential trust root; reported by others, **not independently reproduced by me** |
| G10 | **Newest inbox note untriaged** | `2026-11-13_gpt-6_p5-delay-buffer-audit.md` absent from `TRIAGE.md` | Confirmed coverage gap is not yet in the project's triage record |
| G11 | **Minor integrity notices** | `check_artifact_pins.py` `FLAG_DISAGREES ART-2717 test_01.py`; 3 hygiene `BIG_FILE` warnings; `verify_inventory.py` known `[1/5]` fail | Small, but worth clearing in the same docs/engineering PR |
| G12 | **Root clutter / no release tags** | 78 top-level dirs, ~270 root-level `.py` files, 6 root `.zip`s, 0 tags/releases | Makes onboarding and citation harder; not a correctness issue |

---

## 9. What "continue" should attack first (proposed self-directed cycles)

Ordered by leverage toward a machine-checked reference library of the *actual* dynamics, while respecting the guardrails in §4. Each cycle is one deliverable, with hashes/provenance and an explicit "verified / not verified" note.

1. **Cycle 1 — make the frontier landable.** Refresh `research/lean-gate-p5` onto current `main` (merge, no rebase), fix the §11.6/README mutant-count drift, add the missing **production-delay `D = 50` Python probes** (initialisation length 51, oldest-slot = phase at `max(0, n−50)`, append/pop aging, first live delayed value at n = 50), keep the d=1 probes labelled as unit-delay probes. Produce a delta-audit report. This directly closes G1/G10 and the confirmed inbox finding.
2. **Cycle 2 — close the trust gaps.** Stream `check_modes.shebang_objects` (2-byte prefix instead of buffering all blobs), bring the safe `tools/redteam` subset into CI, and design a G2c fix that pins the verifier outside the self-referential manifest. Each gets a known-false negative control that must FAIL.
3. **Cycle 3 — status truth on `main`.** A reviewed docs/claims PR: update `CURRENT_STATUS.md` to the current head, correct the 75→80 claim count, 14→15 studies, the 43→80 claims figure, the stale test counts, `LEAN-FREEZE-CORE`'s "branch-only" qualifier, `AIEFProofsKn/README.md`'s CI claim, the AUD-RATELAW/E22 wording, and resolve Issue #14 (sweep run, verdict UNEXPLAINED). Add the north-star definition to `main` so direction is findable. **Corrections only — no claim promotion/demotion** (owner decision).
4. **Cycle 4 — the closed-loop Lean core.** Port 040282 cycle 015 `ClosedLoopCore` with the auditor-noted fixes (delayed read in phase coupling, dt pinning), connect `phase → C → R → B → phase` as one recursion, with value probes at engine `α` and `D = 50`. Then land c014 `TrajectorySafety`. Requires a local Lean toolchain (see decision below).
5. **Cycle 5 — the science programme.** Only after the above: a predeclared, independently reviewed v2 rate-law protocol; a versioned dt, dt/2, dt/4 study; a preselected multi-seed replication of the AIEF-1.4 pipeline with seed-level inference; an Arena round-10 adjudication; a literature review for novelty and O1 routes (Ha–Li–Xue, Ha–Ryoo + Correction, Dong–Ha–Kim, Cho–Dong–Ha).

**Guardrails for every cycle:** side branch, no push without owner approval, no hash-pinned edits, errata sidecars, ledger updates only through the reconciliation script, independent review, no forced positive conclusions, preserve negative results, treat all inbox/arena material as unverified input.

---

## 10. Limitations of this audit

- **No Lean build was run** (`lake`/`elan` absent). All Lean claims here are from source inspection, local check scripts that don't need Lean, and CI metadata. Axiom footprints, declaration counts and mutant-kill results are *reported*, not reproduced.
- Shallow clone: branch divergence counts come from the GitHub compare API, not local history; I fetched only the tips plus `e47bad1`.
- I did **not** re-run the frozen production simulations, the 100-seed/40-seed analyses, the v4 analysis, or cross-`glibc` comparisons; I ran the repository's own test suites and validators.
- I did **not** perform a literature/novelty review or verify any external DOI.
- G2c and the Arena round-10 dispute are reported from project documents; I have not independently adjudicated them.
- I made **no** repository changes. The clone in `/home/user/AIEFS` is a read-only inspection copy (aside from Git fetch objects).

---

## 11. Decision needed before "continue"

Three things materially change what I do next:

1. **Which north-star?** the Lean 4 reference library (`briefing/NORTH_STAR.md`), the publication-grade P0–P5 science programme (unmerged northstar evaluation), the general "true, checkable work" goal (`OPERATING_MANUAL.md` §1), or a cycle-by-cycle choice of the highest-leverage gap.
2. **Where should my work land?** workspace-only files (default), local commits on a side branch in the clone (no push), or additionally a correctly-formatted `audit-inbox` note draft for you to push.
3. **Should I install a Lean 4 toolchain locally** (elan + Mathlib cache, large download) so I can actually `lake build` new proofs, or stay Python/structural-only and rely on CI?

**Decisions recorded (answered by the owner after this audit):**

| Question | Choice |
|---|---|
| North-star | **Cycle-by-cycle**: I pick the highest-leverage gap on each "continue", balancing all three framings. |
| Where work lands | **Audit-inbox draft**: workspace-only deliverables, plus a correctly formatted `audit_inbox/YYYY-MM-DD_<agent>_<topic>.md` note prepared for the owner to push. I will not push. |
| Lean toolchain | **Authorised**: I may install `elan` + the Mathlib cache locally so Lean cycles can run real `lake build` / axiom audits. |

No research phase has started yet. The workflow is: this audit is delivered; the owner says **continue**; then one self-directed cycle runs, produces its deliverable and evidence note, and stops.

---

## Addendum A — 040282 cycles 12–16 review note (owner-supplied guidance)

**Source.** The owner supplied a note addressed to the now-retired Researcher 040282. I matched it against `audit_inbox/2026-11-11_auditor-seat-002_lean-candidate-reviews/2026-11-11_audit_040282_c012_c016.md` on `audit-inbox` (Auditor Seat 002, 2026-11-11, Europe/Tirane) and `audit_inbox/TRIAGE.md` rows `R040282-C012` / `R040282-C016` (lines 152–153). Under the repo's rules this is **UNVERIFIED INPUT**; the auditor's compile results are reported, not reproduced by me (no Lean toolchain installed yet).

**Sha housekeeping.** The note cites `710258d` as the push containing the review and triage rows. GitHub shows `710258df` = "briefing: fix STATE 040282 table rows" (2026-11-11 03:58Z); the review/triage deposit is `18c2dd30` ("triage: Auditor review of 040282 cycles 012 and 016; …"), with a later triage update `5d91c098`. Branch tip is `69221804` (2026-11-13). Cite the right sha in future notes.

**Verdicts, as reported (not independently re-run):**

- **c016 `CoherenceMotion.lean` — ADOPT WITH NOTES.** `|R_{n+1} − R_n| ≤ min(1, 2(1−α))`; at engine `α = exp(−0.01/17.5029…) = 0.99942883`, the bound is **0.00114 per step**, so 0→1 needs ≥ ~875 steps (≈8.75 time units). Compiles against unmodified P5 @ `54037ea`, 0 warnings, 21/21 declarations on the three standard axioms; each hypothesis shown necessary by a value counterexample. Limitation: it is the triangle inequality on an EMA with unit-norm inputs — **no phases, delay, ω or B** — so it holds for any unit input sequence. It is a *speed limit*, not dynamics. Node-uniform probes do not exercise symmetrisation; float `α` is not exact; it depends on unmerged P5. Port is small: `AIEFGateCore/CoherenceMotion.lean` plus one mutant (e.g. bound `(1−α)/2`).
- **c012 `EMATracking.lean` (99 lines) — ADOPT WITH NOTES, low priority.** Correct textbook linear-filter bound; "float α rounds to exactly 1" needs `T_window ~10²⁰` and is irrelevant at engine settings. Deposited as 233 files including an 11 MB zip, packet builders and self-check JSON (the current `cycle_012/` tree totals ~8.5 MB of blobs); review cost is out of proportion to the science.
- **c013 / c014 / c015 `.lean` files are byte-identical** to the previously reviewed copies (md5 `410275ad`, `c6914623`, `25306518`). The separate c015 audit (`…/2026-11-11_audit_040282_c015.md`) records **F1** (delayed sine read unpinned), **F2** (`dt = 1` in every probe), **F3** (full-reset probe does not exercise old-`B` carry), **F6** (flat imports must be retargeted) and **F7** (no convergence claim; do not cite as "closed-loop proved").
- `DATE_PROVENANCE.csv` now marks the "2026-09-04" filenames as **legacy labels, not execution dates** — the cycle-004 date question is settled without renaming anything.

**The two directives, applied to my own cycles:**

1. **Minimal deliverable:** one `.lean` file + a one-page note + the exact compile command. No 233-file packets, zip bundles, or self-validation JSON sprawl.
2. **The next result must actually use the phases or the delay** — e.g. a condition under which `R` can only increase — not another bound that holds for any unit-norm input sequence.

**Effect on the cycle plan (§9):**

- **Cycle 1** (P5 merge-refresh + `D = 50` production-delay probes) is now explicitly the **prerequisite** for c016 and c015; the Python probe makes the Lean delay model checkable against the real 51-slot queue.
- **New Cycle 1b:** port c016 as `AIEFGateCore/CoherenceMotion.lean` once P5 lands, add the single mutant, and keep the "speed limit, not dynamics" caveat in the claim text.
- **c012:** defer; port only if a later "R tracks a slowly moving input" lemma needs it, and only as the 99-line file.
- **Cycle 4 (c015):** fix F1/F2 before porting (`probe_delayed_sine`, `probe_dt_scales`), retarget imports to P5/c014 namespaces, and add an old-`B`-carry probe to cover F3.
- **First genuinely new theorem:** phase/delay-dependent, with "R monotone-up under stated conditions" as the candidate target named in the note.
- **Privacy:** the owner's note contains an account email and a device name. Per `OPERATING_MANUAL.md` §6 and `PRIVACY_SCRUB_LIST.md`, those values are **not** recorded in any repo-facing file; the local `git config user.email` correction is an owner-only action.

---

## Addendum B — Cycle 1 completed (2026-11-13 repository chronology)

Deliverables are in `/home/user/AIEFS_cycle1/` (index: `README.md`; full report: `DELTA_AUDIT.md`). Summary:

- **P5 merge refresh** produced `p5_refresh.patch` (11 files, 2,036 lines, `git apply --check` OK) from `main` `a559e0d` to the refreshed P5 tree, with a clean three-way merge of README/SPEC and `registry/artifacts_current.csv` deliberately excluded for regeneration by the owner.
- **Doc drift repaired**: P5 README/SPEC now state the verified 38 statement + 20 definition = 58 mutants, 10 equivalence / 3 typo / 2 statement controls, zero survivors, and that the mutation check runs in CI since PR #27. PR #30's affine-note corrections were preserved.
- **New production-delay probes** `research/lean_gate/tests/test_engine_production_delay.py`: 3 tests pass (7 with existing step-order probes); a known-false mutant engine makes 2 of 3 fail. They pin the Python 51-slot queue at `D = 50`, not Lean/Python equivalence.
- **Independent local Lean gate PASS (7/7)**: installed Lean 4.33.1 from the pinned toolchain, fetched the Mathlib cache, fresh `lake build` — 2,299 jobs, 0 warnings, 20 files / 0 forbidden markers, 707 declarations on `propext`, `Classical.choice`, `Quot.sound`. This reproduces SPEC §11.7's numbers off-CI.
- **No push, no commit, no claim change, no hash-pinned edit.** An `audit_inbox/` note draft is prepared at `AIEFS_cycle1/audit_inbox/2026-11-13_arena-agent_cycle1-p5-refresh-and-production-delay.md` for the owner to push.

Next "continue" → Cycle 1b: port c016 `CoherenceMotion.lean` (one `.lean`, one-page note, exact compile command, one mutant), keeping the "speed limit, not dynamics" caveat.

---

## Addendum C — Cycle 2 completed (2026-11-13 repository chronology)

Deliverables: `/home/user/AIEFS_cycle2/` (index `README.md`, full report `DELTA_AUDIT.md`, one-page note `ONE_PAGE_NOTE.md`, patch `c016_port.patch`, inbox note draft). Summary:

- **Ported c016 `CoherenceMotion.lean`** into `AIEFGateCore` with the auditor's "speed limit, not dynamics" caveat intact (no phases/delay/`ω`/`B`; `2(1−α) = 0.00114…` per step at engine `α`). One `.lean`, one-page note, exact compile command — the minimal-deliverable rule was followed.
- **Wiring:** root import, SUMS 24 → 25, new mutant **M59** (`trace_step_abs_le` bound halved, refuted by new `false_trace_step_abs_le_half`), count pins 39 statement + 20 definition = **59**, README and new SPEC §11.8. The generated refutation file needed `open AIEFGate.CoherenceMotion (rTrace)` in `OPENS` — a real defect found and fixed by the isolated M59 check.
- **Full local Lean gate PASS 7/7**: 2,300 jobs, 0 warnings, 21 files / 0 forbidden markers, **739 declarations** on `propext`, `Classical.choice`, `Quot.sound`. `pytest research/lean_gate/tests`: 70 passed. `git apply --check` OK.
- **Honest gap:** the full 59-mutant suite was **not** completed locally (each `lake env lean` reloads the Mathlib import graph, ~2 min/call in a 2 GiB sandbox; a 49-minute run was stopped). M59 was verified in isolation with the harness's own build/refutation/term-specificity checks. The full suite remains a CI/owner step (`lean.yml`, AIEFGateCore row). No 59/59 pass is claimed.
- **No push, no commit, no claim change, no hash-pinned edit.** The `registry/artifacts_current.csv` regeneration follow-up from Cycle 1 still applies.

Next "continue" → Cycle 3: the direction note's second rule — a genuinely new theorem using phases/delay, candidate `input_constant_after_lock` (phase increments vanish from `N` ⇒ `coherenceInput` constant for `n ≥ N + d`) and the resulting monotone-up / geometric-convergence condition for `R`.
