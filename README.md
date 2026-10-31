# AIEFS — Adaptive Incidence & Emergent Fiber Systems

AIEFS is a research repository about a small adaptive oscillator network: 12 delayed Kuramoto
oscillators, an exponentially averaged coherence `R`, Hebbian edge weights `B`, and a capacity gate.
It holds simulation code, frozen run outputs, analyses, a small Lean 4 proof, and four rounds of
independent audits.

> **Status of this README (2026-10-28).** This README was rebuilt during a local merge of the
> `arena/d4a487cc-aiefs` organisation work into `main`. Every claim below is stated at the scope set
> by the audit rounds in [`AI Agent Audits/`](AI%20Agent%20Audits/). Where the audits did not settle
> a claim, the ledger says **"needs owner/auditor decision"**, and this README does not promote that claim.

## Start here

1. [`registry/claims.csv`](registry/claims.csv) is the single claim ledger. Each row has the
   `prior_status`, the `audited_status` (plus `audited_qualifier`), and the `audit_source` (file + section/line). The 1.4
   lineage rows are reconciled in
   [`registry/lineage_reconciliation.csv`](registry/lineage_reconciliation.csv). Dated corrections to
   hash-pinned documents are in [`ERRATA_2026-10-28.md`](ERRATA_2026-10-28.md) (the pinned files keep their bytes).
2. [`AI Agent Audits/AIEFS_audit_response_3.md`](AI%20Agent%20Audits/AIEFS_audit_response_3.md) is
   the latest audited claim ledger (round 4). [`AIEFS_salvage.md`](AI%20Agent%20Audits/AIEFS_salvage.md)
   holds the earlier verdict table.
3. [`CURRENT_STATUS.md`](CURRENT_STATUS.md) gives the status per study.
4. [`REPRODUCING.md`](REPRODUCING.md) has commands that were checked on 2026-10-28, and
   [`AI Agent Audits/evidence/REPRODUCE.md`](AI%20Agent%20Audits/evidence/REPRODUCE.md) has the
   audit evidence.

## What the audits support (scoped)

- **Phase-locked topology.** The final network topology is set mostly by the chosen natural
  frequencies `ω`. With the repository's hand-picked `ω`, `Corr_physical ≈ 0.995`. With random `ω`
  it is about 0.71 (uniform) or 0.59–0.63 (clustered). The audit verdict is "not a tautology, but
  dominated by persistence" (`AUD-CORR-0995`, `AUD-TOPO-OMEGA`).
- **AIEF-1.3 ablations (100 paired seeds).** In `shuffle_R`, mean ΔD_B = +0.305909, 95% CI
  [0.298939, 0.313030], d_z = 8.434. In `no_mu`, ΔD_B = +0.271061, d_z = 4.900. In `no_delay`,
  ΔD_B = −0.027424. These are valid necessity tests, but `shuffle_R` is forced by construction:
  the shuffled mean R falls below the edge threshold. The design was fixed in advance but not
  preregistered (`EMP-AIEF13-01/02`, `AUD-LABEL`). Reproduction: 500/500 runs are bit-exact on the
  headline arrays and scalars; 78/500 are bit-exact on all 38 keys (`AUD-REPRO13`).
- **AIEF-1.4 memory ablation (40 seeds).** Phase, history and EMA together are enough to rebuild
  the finite topology when `B` is reset (Jaccard 1.000). `B` predicts outcomes and acts as a
  conditional weight scaffold. No unique memory register has been identified. Also, 0 of 29,040
  edges change threshold status after the split (`EMP-AIEF14-01`, `AUD-FROZEN-TOPO`).
- **Rate law.** On complete, saturated, phase-locked components with equal controlling scales, the
  one-step multiplier on the unsigned-incidence controller kernel (row-sum-preserving edge kernel) `K = ker A_J` is `λ = (1−γdt)s_J`. Under the
  further ideal hypotheses (R = 1, row sum c) it is `λ_k = (1−γdt)c/(c+dt(kη−γc)+ε)`, and per
  component `κ_k = kη/c − 1/T_w` (k = 2…5). This is a *conditional* closed form fixed by parameters,
  not an emergent constant. `κ_k` matches the discrete rate within 5.3e-6 over 292 slow components
  (k = 2: 1, 3: 88, 4: 24, 5: 179) in 200 replays; `2η/c − 1/T_w = 0.069182` (T_w = 17.503) is the k = 2
  value and applies only to the single exceptional K3. Round-4 bounds: 264 two-sided fibers to κ 2.1e-6,
  and 110 all-tied K3 one-sided rays to κ 1.7e-5; a ~2e-8 relative gap in λ is unexplained. A within-step
  response of R to B is ruled out by the engine's update order (`ERRATA_2026-10-28.md` E5). Finite-difference/rounding error
  at one component with a tiny step is the most likely cause; the gap stays unexplained until a step-size sweep is run
  (`AUD-RATELAW`, `AUD-KAPPA-TW`, `AUD-CYCLE-KERNEL`).
- **Capacity gate.** `s_i = min(1, c/(q_i+ε))` is multiplicative normalisation. It is idempotent
  but **not** a projection (`AUD-GATE`).
- **Lean proof.** `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean` checks a 2×3 kernel identity.
  It is correct but trivial linear algebra and says nothing about the dynamics (`LEAN-CF-01`). The
  round-4 package (Lean `v4.33.1`, 6 modules, 115 declarations, standard axioms only) passed the audit's
  `check_lean.sh` run (`LEAN-R4`).

## Scope limits and retired claims

- **The AIEF-1.4 operator/cocycle/Duhamel/controller-fiber pipeline is a single-seed case study**
  (one exceptional seed, 1 of 40). Do not generalise it to the 40-seed cohort (`AUD-SCOPE-1.4`).
- **Matched-phase counterfactuals (`test_output/`) are Exploratory** (controlled exploratory analysis
  with fixed recorded design). The arena had labelled them "Frozen / Controlled" and said delayed
  history "mediates recovery"; that causal wording is withdrawn. `P_mean_late` is negative
  (−0.018 [−0.027, −0.009]) (`EMP-AIEF14-02`).
- **"The EMA pole is the unique slow pole" is quarantined — invalid derivation; do not cite.** The
  18-coordinate map omits θ. An audit proposal on the closed 966-dimensional state (one replay,
  finite-difference, not a proof) gives NO: 10 rates lie in the gap (`AUD-SLOWPOLE`, errata E2).
- **"Strict K3 components are spectrally silent" is retired.** They have one-sided selection rays,
  not eigenmodes (`AUD-K3`).
- **Novelty is not established.** No literature review has been done (`AUD-NOVELTY`).
- **The pre-AIEF SSRH origin hypotheses** (e.g. r = 0.92, ⁶⁰Fe r = 0.85, "10⁸ amplification") are
  **Speculative / untested origin hypotheses** (`SSRH-ORIG-01..07`). They have no supporting data or
  analysis in this repository, so they are not cited as results. They are not retired either: they are
  kept as origins and possible future directions, and can be promoted once a testable form is stated
  and a test is run. See the status categories in [`registry/README.md`](registry/README.md).
- Retired interpretations S01–S18 appear in `registry/claims.csv`. The older prose lists point there.

## Install and quick checks

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# audit evidence integrity (hash manifest):
.venv/bin/python "AI Agent Audits/evidence/verify_manifest.py"
# modular platform tests (expected: 41 passed, 1 skipped; ~15 s; without AIEF_RUN_SLOW_TESTS=1: 40 passed, 2 skipped):
PYTHONDONTWRITEBYTECODE=1 AIEF_RUN_SLOW_TESTS=1 PYTHONPATH="$PWD:$PWD/AIEF_Experiments/aief_modular_platform_v1_analysis_v4" \
  .venv/bin/pytest -q AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests_modular
```

> `audits/engineering/verify_inventory.py` (from the arena branch) currently **fails at check 1/5**
> on the merged tree. It conserves the file list of commit `e47bad1`, and `main` has since deleted
> or moved files, and 261 tracked files are not inventoried (2,969 tracked, as of the CI integration). See
> [`MERGE_PREP_REPORT.md`](MERGE_PREP_REPORT.md) and the `tree_check_2026_10_28` column in
> `registry/artifacts.csv`.

## Licensing and privacy

The code and Lean proofs are under Apache-2.0, and the documents are under CC BY 4.0. Third-party
papers are not licensed by this project. See [`LICENSING.md`](LICENSING.md) and [`NOTICE`](NOTICE).
The Lean headers ("Copyright … All rights reserved. Released under Apache 2.0 license …") are the
standard Mathlib header form and do not conflict with Apache-2.0. Whether generated datasets should get a
separate data licence (CC BY 4.0 or CC0) is an open owner decision. See `PRIVACY_SCRUB_LIST.md` for personal-data and third-party-copyright locations
to review before the repository is promoted more widely.
