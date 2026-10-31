# Deeper sweep: full history, all seven archives, and the repository's own prior art

- **Agent:** Arena.ai Agent Mode (coding agent)
- **Date:** 2026-10-31 (Atlantic/Reykjavik, UTC+0)
- **Reviewed:** full git history (`git fetch --unshallow`, 198 commits, 3,145 distinct paths); all 11 branch tips; all 7 archives on `main`; `AI Agent Audits/` (149 files) in depth; `Project Origins/` (8 PDFs); `tools/sync/`; `LICENSING.md`.
- **Supersedes part of:** `2026-10-31_arena-agent_remote-content-vs-literature-open-questions.md` (same day)
- **Status:** UNVERIFIED INPUT per `README.md` rule 3.

---

## 1. The entrypoint question is now closed, in the negative

`git fetch --unshallow` succeeded. Against the **full 198-commit history**:

- **zero commits ever touched** any of the eight missing entrypoint filenames
  (`aief_1_4_fiber_coordinate_controller.py`, `AIEF_1_4_driver_mechanism.py`,
  `aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`,
  `aief_1_4_branch_tangent_comparison.py`, and the three already found under other names);
- **no path matching `AIEF_1_[012]_` has ever existed** in any commit.

So the correct claim is *never committed to this repository* — not *missing from the checkout*. Those
are different claims and only the first survives scrutiny.

## 2. There are seven archives on `main`, not three

| Archive | Size | entries | on my branch |
|---|---|---|---|
| `Project Histories/workspace-019fb8fc-….zip` | 11.7 MB | 40 | **no** |
| `Project Histories/workspace-019fc7dc-….zip` | 326 KB | 15 | **no** |
| `Project Histories/workspace-019ff425-….zip` | 19.7 MB | 166 | **no** |
| `workspace-019ff402-….zip` | 1.9 MB | 70 | yes |
| `workspace-019ff86e-….zip` | 134 KB | 29 | yes |
| `AIEF_Experiments/…analysis_v4.zip` | 85 KB | 42 | yes |
| `AI Agent Audits/evidence/Data from …Meteorites/bb24282657_1_1.tar` | 42.5 MB | — | **no** |

The three main-only zips were added by `6b49a7b` ("Upload via upload_new.sh", 2026-10-27). I opened
all of them; none contains a missing entrypoint or any `AIEF_1_0/1_1/1_2` file. They do contain real
older work (`aief_1_4_operator_compression.py`, `aief_1_4_observable_jacobian.py`,
`aief_1_4_k3_structure_scan.py`, `aief_1_4_coupling_lock_audit.py`, …) which is also present in
`main`'s tree.

## 3. Correction: one "phantom entrypoint" was my bug

`registry/studies.csv` lists `AI Agent Audits/evidence/run_all.sh` and `evidence/verify_manifest.py`
as entrypoints of `AI_AGENT_AUDITS_2026_10`. I reported both missing. **Both exist on `main`.** My
branch does not contain `AI Agent Audits/` at all (149 files, main-only), so every path into it
resolved false. The check should run against the branch that owns the directory.

## 4. The finding that matters: the repo already had the prior-art answer

`AI Agent Audits/AIEFS_audit_response.md`, **point 12**:

> "The ingredients are prior art: Hebbian phase oscillators (Seliger, Young & Tsimring, PRE
> 65:041906, 2002); delay plus plasticity (Timms & English, PRE 89:032906, 2014); conserved-coupling
> normalisation (Picallo & Riecke, PRE 83:036206, 2011); review in Berner et al., Phys. Rep. 1031
> (2023); normalisation-as-decay (Miller & MacKay 1994). The exact combination … was not found, but
> the search was not exhaustive."

`AIEFS_salvage.md` adds that Seliger et al. is *"essentially AIEF minus delay and cap"*.

**None of these five was in the 38-source literature bibliography.** Added as `LIT-0039` (Berner et
al., verified from the arXiv abstract page) and as four open leads, not promoted on the repository's
citation alone.

### 4.1 The review was physically here the whole time

`Papers/2804.05652v1.pdf` — 3.5 MB, 120 pages, PDF `/Title (Adaptive Dynamical Networks)`. The
filename uses an **impossible** arXiv identifier (month codes are 01–12). Correct ID: **2304.05652**
= Berner, Gross, Kuehn, Kurths, Yanchuk, *Adaptive Dynamical Networks*, 12 Apr 2023, nlin.AO.

`AI Agent Audits/licensing_inventory/INVENTORY.md` **already records this**, including the words
"Filename typo: 2804 for 2304". Nothing loads the file and no Markdown references it, which is why a
Markdown-only citation grep (the Round 1 method) could never have surfaced it.

## 5. The audit corpus corroborates four of my adjudications and challenges a fifth

`AIEFS_audit.md` holds 18 findings (H1–H4, M1–M6, L1–L8) with in-place corrections in
`AIEFS_audit_response.md` / `_2` / `_3`.

- **Corroborates** the round-3 cocycle scope finding: `M2` says the 1.4 operator/memory claims rest
  on *"one frozen replay of one exceptional seed (4619122171158768524)"* — the same seed I flagged
  independently.
- **Corroborates** `LEAN-CF-01`'s status: `H3` — *"The only substantive theorem is
  ker[[1,1,0],[1,0,1]] = span(1,−1,−1)"*.
- **Corroborates** `AUD-GATE`/`M1`: the gate is *"an exact no-go, not an ε artifact"*.
- **Challenges `EMP-AIEF13-01`'s interpretation.** `H1`/`H2` argue topology is largely set by the
  hand-picked ω through a closed-form threshold; the corrected text gives 16 distinct baseline
  topologies at the repo's ω, multistability under random ω, and precision 0.59–0.98 vs **recall
  0.18–0.57** for the closed-form predictor. `AUD-CORR-0995-SCOPE` adds that `Corr_physical ≈ 0.995`
  is ω-specific (~0.71 under random ω). My adjudication recorded the inference caveat but **not this
  mechanism caveat**.

## 6. Not yet examined

- `Project Origins/` — 8 PDFs, 31 MB, incl. `SSRH 001 stuff.pdf` (10.3 MB), `SSH history part
  002461.pdf` (7.2 MB). These are the primary documents behind `SSRH-ORIG-01…07`, all seven of which
  are `Incomplete`. Not read.
- The 39 `evidence/logs/` files and 20 `evidence/results/` JSONs.
- `Project Histories/Project Lead History 01–10.pdf` (~40 MB of chat transcripts).
- `LICENSING.md` / `NOTICE` / licensing inventory beyond the `Papers/` rows quoted above.

## 7. Suggest

Re-baseline the literature inbox onto `integration/round5`'s 76-claim registry before quoting any
coverage number; verify the four prior-art leads from the publisher records; and treat
`AIEFS_audit_response.md` point 12 as the starting point for `AUD-NOVELTY` rather than a first-pass
search.
