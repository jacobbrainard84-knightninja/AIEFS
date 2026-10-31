# Literature Review — Round 6: The Repository's Own Prior Art

**Round:** 6 · **Date:** 2026-10-31 · **New sources:** 1 (total 39) · **New leads:** 4 (4 open)
**Registry:** [`SOURCES.csv`](SOURCES.csv) · [`ADJUDICATION.csv`](ADJUDICATION.csv) · **Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md) · [R3](ROUND_03_FINDINGS.md) · [R4](ROUND_04_FINDINGS.md) · [R5](ROUND_05_FINDINGS.md)

---

## 0. What this round is

Not a search round. A **provenance repair round**, forced by a sweep of every branch
(`audit_inbox/2026-10-31_arena-agent_remote-content-vs-literature-open-questions.md`).

Round 5 closed with "the literature inbox is essentially complete". The remote sweep showed that
was wrong, and this round records why in the way that matters most: **the repository already cites
five prior-art sources for the novelty question, and six rounds of searching found none of them.**

That is not a search failure. It is a failure to read the repository's own audit record before
searching outward.

---

## 1. F33 — The novelty answer was already in the repository, and this inbox did not have it

`AI Agent Audits/AIEFS_audit_response.md`, point 12, responding to the critique "no new scientific
result", states the prior art directly and concedes:

> "The ingredients are prior art: Hebbian phase oscillators (**Seliger, Young & Tsimring, PRE
> 65:041906, 2002**); delay plus plasticity (**Timms & English, PRE 89:032906, 2014**);
> conserved-coupling normalisation (**Picallo & Riecke, PRE 83:036206, 2011**); review in
> **Berner et al., Phys. Rep. 1031 (2023)**; normalisation-as-decay (**Miller & MacKay 1994**).
> The exact combination (an EMA of the delay-compensated phasor as driver, plus a min-endpoint hard
> capacity cap) was **not found**, but the search was not exhaustive."

`AIEFS_salvage.md` adds Aoki & Aoyagi (*PRL* 102:034101, 2009) and Berner, Schöll & Yanchuk
(arXiv:1912.03922), and says of Seliger et al. that it is *"essentially AIEF minus delay and cap."*

**My 38-source bibliography contained none of these.** Round 2 built an adaptive-delay cluster
([LIT-0016], [LIT-0018], [LIT-0028]) by independent search while the repository's own audit had a
sharper, older and more on-point list sitting in the tree — including the statement that the closest
prior art is "AIEF minus delay and cap".

This is the round's central finding, and it is a finding about *my* method, not the project's:
**search outward before reading inward is the wrong order.**

### 1.1 The missing review was physically in the repository

**[LIT-0039] — Berner, Gross, Kuehn, Kurths & Yanchuk, *Adaptive Dynamical Networks*, arXiv:2304.05652
[nlin.AO], 12 Apr 2023 (later *Physics Reports* 1031).** Verified `VERIFIED_FULL` by fetching the
arXiv abstract page.

It has been committed the whole time as `Papers/2804.05652v1.pdf` — 3.5 MB, 120 pages — under an
**impossible identifier**: arXiv month codes run 01–12, so `2804` cannot exist. The repository
already knows: `AI Agent Audits/licensing_inventory/INVENTORY.md` records the correct ID and says
*"Filename typo: 2804 for 2304"*, and the audit's L7 flags it.

Why five rounds missed it: nothing loads the file, and **no Markdown in the working tree references
it**, so the Round 1 grep for `arxiv.org|arXiv:\d{4}|ISBN` across all tracked Markdown returned
empty — correctly. The bibliography hole was invisible to the method I was using.

**Why it matters more than any source in rounds 2–5.** It is the field-defining review of the exact
class AIEF belongs to: *"systems that can change their connectivity over time depending on their
dynamical state... their function depends on their structure and vice versa"*, including neuronal
synaptic plasticity among its applications. It supplies the framing half of `AUD-NOVELTY`.

**Scope note kept honest:** the repository cites the *Physics Reports* version (vol. 1031); I verified
the **arXiv** record, not the journal DOI. The citable identifier recorded is the arXiv one.

---

## 2. F34 — Four leads opened, deliberately not promoted

The other four prior-art citations were read **inside the repository**, not verified against the
publisher record. Per protocol they are leads, not sources: a citation found in an audit document is
not the same evidence as a fetched bibliographic record.

| Lead | Citation as the repository gives it | Why it matters |
|---|---|---|
| `LEAD-0008` | Seliger, Young & Tsimring, *PRE* 65:041906 (2002) | Called "essentially AIEF minus delay and cap" — the closest prior art in the tree |
| `LEAD-0009` | Timms & English, *PRE* 89:032906 (2014) | The delay-plus-plasticity ingredient |
| `LEAD-0010` | Picallo & Riecke, *PRE* 83:036206 (2011) | Conserved-coupling normalisation — bears on `CF01`–`CF03` and `AUD-GATE` |
| `LEAD-0011` | Miller & MacKay, *Neural Computation* 6:100 (1994) | Salvage says multiplicative normalisation "is exactly what produces the k·η/c rates" — anchors `AUD-RATELAW`/`AUD-KAPPA-TW` to a classical result |

I am not promoting these on the strength of the repository's own citation. That would be exactly the
second-hand sourcing Round 1 flagged as a defect in [LIT-0026] and Round 4 corrected in [LIT-0030].

---

## 3. F35 — The archive inventory was wrong, and the answer is still "never committed"

Round 3 recorded "three archives" and corrected an earlier memory of "two". The true count on `main`
is **seven**:

| Archive | Size | On my branch? |
|---|---|---|
| `Project Histories/workspace-019fb8fc-….zip` | 11.7 MB, 40 entries | **no** |
| `Project Histories/workspace-019fc7dc-….zip` | 326 KB, 15 entries | **no** |
| `Project Histories/workspace-019ff425-….zip` | 19.7 MB, 166 entries | **no** |
| `workspace-019ff402-….zip` | 1.9 MB, 70 entries | yes |
| `workspace-019ff86e-….zip` | 134 KB, 29 entries | yes |
| `AIEF_Experiments/aief_modular_platform_v1_analysis_v4.zip` | 85 KB, 42 entries | yes |
| `AI Agent Audits/evidence/Data from …Meteorites/bb24282657_1_1.tar` | 42.5 MB | **no** |

Three were added by `6b49a7b` ("Upload via upload_new.sh", 2026-10-27) and are main-only. I opened all
of them. They contain real work — `aief_1_4_operator_compression.py`,
`aief_1_4_observable_jacobian.py`, `aief_1_4_k3_structure_scan.py`,
`aief_1_4_coupling_lock_audit.py`, `AIEF_1_4_memory_ablation_updated_REAL.py` — but **no missing
entrypoint and no `AIEF_1_0/1_1/1_2` file**.

### 3.1 The verdict is now exhaustive, not just "absent from the tips"

The clone was shallow (194 commits visible). `git fetch --unshallow` succeeded — **198 commits,
3,145 distinct paths ever in the repository's history**. Against full history:

- **zero commits ever touched any of the 8 missing entrypoint filenames** — not added, not deleted,
  not renamed;
- **no path matching `AIEF_1_[012]_` has ever existed** in any commit.

Combined with all 11 branch tips and all 7 archives, F16's "genuinely absent" now means
*never committed to this repository*, not *missing from the current checkout*. The two are different
claims and only the first was true.

---

## 4. F36 — Correction: one of my "phantom entrypoints" was a false positive

`registry/studies.csv` lists `AI Agent Audits/evidence/run_all.sh` and
`AI Agent Audits/evidence/verify_manifest.py` as entrypoints of `AI_AGENT_AUDITS_2026_10`. My
working-tree check reported both missing.

**Both exist on `main`.** My branch simply does not contain the `AI Agent Audits/` directory at all
(149 files, main-only), so every path into it resolved false. The bug was checking my checkout
instead of the branch that owns the study.

Corrected status of the six studies:

| Study | Verdict |
|---|---|
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | genuinely absent everywhere — **never committed** |
| `AIEF_1_3_DISJOINT_100SEED` | stale names; real script is `AIEF_1_3_falsification_updated.py`, registered nowhere |
| `AIEF_1_4_MATCHED_PHASE_ABLATION` | `AIEF_1_4_driver_mechanism.py` genuinely absent |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | 3 names genuinely absent (and 3 *different* names also absent on `integration/round5`) |
| `AIEF_1_4_CONTROLLER_FIBER` | stale name; `AIEF_1_4_intertwining_controller_analysis.py` + outputs exist |
| `AI_AGENT_AUDITS_2026_10` | **false positive — both files exist on `main`** |

---

## 5. F37 — The audit corpus independently corroborates four adjudications and challenges a fifth

`AI Agent Audits/` (149 files: 22 reproduction scripts, 39 logs, 20 results, 4 proposals) is the most
carefully argued material in the repository, and rounds 1–5 read none of it.

**Corroborations:**

- `M2`: *"The 1.4 memory/operator claims rest on one frozen replay of one exceptional seed
  (4619122171158768524)"* — independent agreement with Round 3's F17 scope finding, from a
  different author, naming the same seed.
- `H3`: *"The only substantive theorem is ker[[1,1,0],[1,0,1]] = span(1,−1,−1)"* — agrees with
  Round 5's `LEAN-CF-01` verdict that the result is a specialization, not new mathematics.
- `M1` + `AUD-GATE`: the capacity gate is *"an exact no-go, not an ε artifact"* — consistent with
  Round 5's `CF01`–`CF03` treatment, which never claimed the gate was a projection.
- `M3` + `AUD-MODULAR-ORACLE`: the two skipped tests are the only numerical/oracle ones — exact
  agreement with the `AUD-MODULAR-ORACLE` claim and with Round 4's [LIT-0038] artifact-badge point.

**One challenge, and it is against `EMP-AIEF13-01`:**

`H1`/`H2` and the responses argue that the sparse topology is largely *set by the chosen ω through a
closed-form threshold* — with delay there are 16 distinct baseline topologies at the repo's ω, for
random ω the outcome is multistable, and the closed-form set is an informative predictor
(precision 0.59–0.98, **recall 0.18–0.57**), not a guaranteed superset. `AUD-CORR-0995-SCOPE` then
says `Corr_physical ≈ 0.995` is specific to the hand-picked frequency vector (random ω: ~0.71).

My Round 5 adjudication of `EMP-AIEF13-01` was `SUPPORTED_WITH_SCOPE` (LOW) on **inference** grounds
only, and did not record that the *mechanism interpretation* — "destroying historical alignment
structure" — is contested by the repository's own audit. **That is a scope condition my adjudication
omitted**, and it is worth more than the bootstrap finding I did make.

I have not changed the verdict: the numbers and the inference stand, and the challenge is to the
interpretation, which lives in `AUD-TOPO-OMEGA`/`AUD-CORR-0995-SCOPE` — claims that do not exist in
my 43-claim baseline (F24-adjacent, Round 5 §5).

---

## 6. F38 — The registry is not merely stale, it is a strict subset of an unmerged one

Restated here because it governs every coverage number this inbox publishes:

| File | `main` | my branch | `audit/nanfix-v2` | `integration/round5` |
|---|---|---|---|---|
| `registry/claims.csv` | **absent** | 43 | 75 | **76** |
| `registry/studies.csv` | absent | 14 | — | 15 |

The 33 claims absent from my baseline are 24 `AUD-*`, 2 `LEAN-*`, 7 `SSRH-ORIG-*`. Two of my 24
adjudications carry a status that has since moved (`EMP-AIEF14-02` → `Exploratory`, `CF05` →
`Supported`), and the vocabulary gained `Incomplete`, which my adjudication's closed vocabulary does
not carry.

**Until the literature inbox is re-baselined onto the 76-claim registry, every "24/43" and "24/76"
figure should be read as provisional.**

---

## 7. State

| Measure | R1 | R2 | R3 | R4 | R5 | **R6** |
|---|---|---|---|---|---|---|
| Sources | 16 | 28 | 33 | 38 | 38 | **39** |
| Claims with a source | 19/43 | 22/43 | 24/43 | 24/43 | 24/43 | **24/43** |
| Claims adjudicated | 0 | 0 | 0 | 0 | 24/24 | **24/24** |
| Open leads | 3 | 3 | 1 | 0 | 0 | **4** |
| Verifier gates | 7 | 7 | 7 | 7 | 8 | **8** |

Open leads went **up**, from 0 to 4, and that is the correct direction: four real citations are now
known to exist that I have not verified. A lead queue that empties because nobody looked is worth
less than one that fills because somebody did.

## 8. What Round 6 did not do

- Did not promote `LEAD-0008`–`LEAD-0011` on the repository's own say-so.
- Did not verify the *Physics Reports* DOI for [LIT-0039]; only the arXiv record.
- Did not read the 8 origin-document PDFs in `Project Origins/` (31 MB) or the 4 audit-response
  ledgers in full — the `SSRH-ORIG-01…07` claims remain outside the literature layer.
- Did not alter any file outside `audits/literature/`.
