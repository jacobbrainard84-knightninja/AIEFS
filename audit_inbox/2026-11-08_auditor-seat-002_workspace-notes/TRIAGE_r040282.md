# Triage of the Researcher 040282 upload (first pass, Researcher 001 seat)

- Date: 2026-11-08, about 17:00 Europe/Tirane (UTC+1).
- Upload reviewed: `audit-inbox` @ `b18a27d`, folder `audit_inbox/2026-11-08_researcher-040282/` (local checkout `/tmp/wt_r040282_intake`, now at `228fae8`, which adds Auditor Seat 002's intake note; I did not edit it).
- Current main used for witnesses: **`942f8526daee5ac547f2e422101fa95c61eeef41`** (PR #9 merge, 2026-11-08 14:56 Europe/Tirane), read-only detached worktree `/tmp/wt_main_942`.
- Companion note: Auditor Seat 002 intake `/workspace/review_r040282/2026-11-08_auditor-seat-002_researcher-040282-intake.md` (inventory, PII scan, ledger/state drift). This note does not repeat that work.
- **Everything in the packets stays UNVERIFIED INPUT.** Below, "they claim" = the packet's statement; "I reproduced" = I ran my own witness on 942f852; "static" = I read current-main source but did not execute the scenario.
- Nothing pushed, no PR, no edits to `audit_inbox/TRIAGE.md` or any repo file, no contact with anyone. I did not run any of the packet's own Python/shell code. Witness scripts I wrote: `/workspace/review_r040282/witness/` (`w_analysis.py`, `w_bridge.py`, `w_nan.py`, `w_oracle.py` + `.out` logs).

## 1. Executive summary

**What matters**

1. **Proposal-bridge self-test prints PASS on a fixture whose branch it gets wrong (B-F4). I reproduced it exactly on main.** `AIEF_1_4_proposal_equalization_bridge_analysis.py:synthetic_self_test` hard-codes endpoint winners that the actual operator does not choose. Against the real `admissibility_from_nonnegative_proposal`, the asserted left identity has residual `-0.02121459694983044` (tolerance 1e-14), yet the self-test prints `Synthetic proposal-equalization bridge checks: PASS`. This is exactly the "built-in result" class we hunt. Scope: the `--self-test` synthetic check only. It does not by itself refute the conditional algebra or the saved real-data replay. The script is registry artifact ART-0050 ("Supported"), so the repair needs the erratum route, not an in-place edit.
2. **Sync uploader may overwrite an ignored local file before confirmation (B-F1), and it does not scan committed content or intermediate history (B-F2).** I confirmed statically on main (file unchanged since 5c1ffed): `upload_new.sh:84-85` runs `git pull --rebase --autostash` before the prompt at `:190-194`, with no ignored/untracked collision check. The downloader does have that check (`download_new.sh:74-104`). The unpushed-commit path at `:148-165` checks only names at HEAD and sizes at HEAD from `git diff --name-only BASE HEAD`, not blob content and not intermediate blobs. **I did not run it.** Auditor Seat 002 should reproduce it in a credential-free sandbox. Until then it is a precautionary owner item: don't rely on the uploader to protect ignored local files.
3. **Boundary-degenerate event-rate intervals (A-F2/B-F3). I reproduced the mechanism on main for v4 and v4.1:** 0/40 gives `[0,0]` and 40/40 gives `[1,1]`, labelled `..._pointwise_percentile_95pct`. The *real-data* count they report (222 of 240 S01 event-rate groups have zero width) I did not reproduce. The auditor's intake found it consistent with their supplied CSV only. This is an inference/wording issue: the intervals are fixed-cohort resampling diagnostics, not population 95% CIs at the boundary. Any S01 claim that reads them as population uncertainty needs a caveat.

**What is already known or lower value**

- The held-event floating-point boundary bug (A-F1/B-F5) is **already known**: v4.1's header (`..._v4_1.py:12-29`) documents and fixes it, with R026-S8 tracking its tolerance wording. I reproduced the v4 failure and that v4.1 fixes these witnesses. v4 is frozen and pinned. v4.1 is still CANDIDATE/UNAUDITED.
- Complex-NaN masking in the engine comparator (B-F6) is real: I reproduced it. The modular `validation.exact_equal_with_nan` already compares components separately, and its comment names this exact failure. It is latent: they claim, and I did not verify, that all saved complex arrays are finite.
- Duplicate condition-status rows accepted by the modular oracle (B-F7): I reproduced it through the public API on a minimal synthetic run. It is a latent validation hole for future modular-candidate certification, not a current false certificate.
- Older-CI claim (B, report :207): stale. Main has `repo-checks.yml` with CI-tool and v4.1/modular synthetic tests. CLI import path: already R026-S7.

**Lean packets:** useful intake. **I compiled them on the box** with the same pinned toolchain they claim (Lean 4.33.1, Mathlib `0df444a`, prebuilt locally, no network). All modules compile with **0 warnings and 0 errors**. Declaration counts match (22 / 44 / 22+6). Every printed axiom footprint is exactly `[propext, Classical.choice, Quot.sound]`. There are no `sorry`/`admit`/`axiom`, no `native_decide`, and no metaprogramming (`#eval`, `run_cmd`, etc.). The work fills gaps that main's own `FreezeCore.lean` header says are not formalised: the gate row-sum lemma, the EMA, and the R-hypotheses. Scope statements are honest. ON/OFF results are conditional on infinite-tail drive bands, and cycle 004 itself shows the coarse bound **cannot** certify ON at baseline constants. I verified that number independently.

**Urgent?** Nothing I found is a live false PASS in CI or a confirmed data loss. The one item with live data-loss potential is the uploader (B-F1), static only so far. The owner should treat the uploader as unsafe for ignored local files until the auditor has checked it. The bridge self-test is a real false PASS, but in an opt-in synthetic self-test, not a CI gate.

## 2. Cheap witnesses on current main 942f852 (my runs)

Environment: system Python 3.13, NumPy 2.5.4, pandas 3.0.6. Modules loaded by file path from `/tmp/wt_main_942`, with `sys.dont_write_bytecode`.

| Witness | Result on 942f852 | Matches their claim? |
|---|---|---|
| `_held_index`, block idx 32..67, duration 17.5 (`w_analysis.out`) | `t[32]=16.01`, `t[67]=33.51`, `t32+17.5=33.510000000000005`, `t67-t32=17.499999999999996`. **v4 → None; v4.1 → 32** | Yes (v4) |
| Same + later longer block idx 100..150 | **v4 → 100 (t=50.01, a delayed event); v4.1 → 32** | Yes (they say 50.01) |
| 35.0 witness, block idx 32..102 (`t102-t32 == 35.0` exactly) | **v4 → None; v4.1 → 32** | Yes |
| Translation sweep (every start, shortest sufficient span) | dur 17.5: v4 **32** false negatives, v4.1 0; dur 35.0: v4 **26**, v4.1 0; dur 8.75: 0/0 | Yes (32 and 26 exactly) |
| `pointwise_summary` 0/40, 40/40, 1/40, 2000 draws | v4 and v4.1: **0/40 → [0,0], 40/40 → [1,1]**, 1/40 → [0, 0.075]; label `joint-seed-resampling_pointwise_percentile_95pct` | Yes |
| Bridge self-test fixture (0.41, 0.31, 0.27) through actual `admissibility_from_nonnegative_proposal` (`w_bridge.out`) | Row sums (0.72, 0.68, 0.58); scales (0.8796, 0.9314, 1). Actual winner node per edge (25, 29, 59) = (node "2", "2", "7"); the test uses s7 on edge 25. Test-built y25 = 0.38186; actual y25 = 0.36065. **Left-identity residual = −0.02121459694983044.** `synthetic_self_test()` stdout: **"…checks: PASS"**. Positive control (0.41, 0.27, 0.31): residual 1.4e-17 | Yes |
| Engine `exact_array_equal_with_nan(nan+1j, nan+99j)` (`w_nan.out`) | **Engine True** (false equality); modular `validation.exact_equal_with_nan` False. Also `1+nanj` vs `5+nanj`: engine True, modular False. Controls: identical arrays True, finite difference False | Yes |
| Oracle `compare_twindow_run`, public API, minimal synthetic dirs (identical scalar CSV/NPZ; status 2 rows vs 3 with one duplicate) (`w_oracle.out`) | **duplicate → status=passed, condition_rows=3, errors=[]**; controls: missing row failed, changed status failed, duplicate replacing another key failed | Yes (mechanism); I did not use real S01 or 201-vs-200 |
| Coarse-ON fixed point, exact Fractions (c=19/30, ε=1e-12, h=3/20000, L=8/3) | D=88/3: fixed point 760000000/13200000003 ≈ 0.0576 < 3/25 (ON not certified); S=16/3: 760000000/2400000003 ≈ 0.3167 > 3/25 | Yes (both numbers exact) |
| A-F6 float witness | `17.333*0.75 = 12.999749999999999`, and `== 12.99975` is False; v4 `:335` and v4.1 `~:385` still use exact `!=` | Mechanism yes; they and the auditor report it does not fire on the real S01 manifest |
| A-F5 static | v4 `:1328` and v4.1 `:1452` compare the stored digest with the in-memory payload, not with the read-back `analysis_identity_payload` | Static yes |

Not run: the full 2000-replicate S01 reanalysis, the 4,800 held-case real-data cross-check, the one-condition replay, the uploader scenarios, and the input-mutation fault injection (A-F4).

## 3. Path and line drift, 5c1ffed → 942f852

`git diff --stat 5c1ffed 942f852` is **empty** for `tools/sync/upload_new.sh`, `aief_experiment_engine_v1.py`, `AIEF_1_4_proposal_equalization_bridge_analysis.py`, `AIEF_1_4_actual_admissibility_branch_audit.py`, `…/AIEF_1_4_Twindow_sensitivity_analysis_v4.py`, and `…/aief_modular/oracle.py`. Every cited line range still points at the same code: engine compare `:1755-1768`, held index `:541-558`, `pointwise_summary` `:977-1020`, oracle condition-coverage function `:97-111`, bridge fixture `:198-232`, operator `:211-252`. None of the leads is fixed on main except where the v4.1 candidate exists, which is a separate file. The source packet A `analysis_under_audit.py` matches main's v4 bytes (auditor intake, static). The packet C cycles cite main `ad58a46`; their `FreezeCore.lean` copy differs from main's only by five appended `#print axioms` lines.

## 4. Finding / claim map

Status key: KNOWN = already in AIEFS; NEW-P = new and plausible; NEW-OC = new but overclaimed or out of scope; N/A = not applicable to current main; AUD = needs Auditor Seat 002 reproduction (not blocking).

### Packet A — `aief_audit` (pasted Analysis v4, synthetic only)

| ID | They claim | Status | Evidence / where known |
|---|---|---|---|
| A-F1 | `_held_index` exact-boundary FP bug; rejects or delays events | **KNOWN**; I reproduced it on v4; v4.1 fixes my witnesses | v4.1 header `:12-29`; R026-S8 (tolerance wording); v4 frozen. The delay effect (later event chosen) is worth one line in the v4.1 audit |
| A-F2 | Percentile intervals collapse at 0/40, 40/40; n=1 gives [7,7]; empty draws not counted | **NEW-P** (method/wording); I reproduced 0/40 and 40/40 | `ANALYSIS_V4_DESIGN.md:139` just says "percentile-bootstrap 95%". n=1 and empty-replicate counting not tested by me |
| A-F3 | Saved-grid detection time is not interval-censored first physical crossing; held onset has a shorter observable horizon | **NEW-P** (estimand labelling), science decision for R001 | Overlaps R026-S8 "interval-censored wording not re-read" |
| A-F4 | Inputs can change between validation and use (TOCTOU) | NEW-P, low; **AUD** | Threat needs a concurrent writer; not tested |
| A-F5 | Staged manifest payload not checked against its own digest | **NEW-P**, low-medium; static yes on v4 and v4.1 | `v4:1328`, `v4_1:1452` |
| A-F6 | Exact nominal-window equality fragile across CSV round-trip | NEW-P, low; float mechanism reproduced | They and the auditor report it does not fire on real S01 |
| A-extras | Degenerate reference; empty topology aborts; five separately calibrated simultaneous families vs singular wording; fsync after rename; `elapsed_seconds`; `argv` | NEW-P hardening/wording, later | Not tested |

### Packet B — `aiefs_repository_audit` (5c1ffed + claimed real S01)

| ID | They claim | Status | Evidence |
|---|---|---|---|
| B-F1 | Uploader overwrites an ignored local file during integration, before confirmation | **NEW-P, P1; AUD** | Static on main: `upload_new.sh:84-85` before `:190`; no collision check (downloader has one at `:74-104`) |
| B-F2 | Committed content and intermediate-history blobs bypass content/size checks | **NEW-P, P1; AUD** | Static on main: `:148-165` checks names and HEAD sizes only, no `has_secret_content`, no per-commit blobs |
| B-F3 | 222/240 real S01 event-rate intervals zero width | Mechanism reproduced (=A-F2); real count **not reproduced** | Auditor: consistent with their CSV only |
| B-F4 | Bridge self-test uses the wrong branch, prints PASS, residual −0.0212146 | **NEW-P, I reproduced it exactly** | ART-0050 is pinned, so a fix needs the erratum route. Not in ERRATA/REDTEAM |
| B-F5 | Held-event bug; 0 mismatches in 4,800 real held cases | Bug KNOWN (=A-F1); real-data zero-impact claim **not reproduced** | Good news if true; the auditor could re-run cheaply only if the S01 NPZ is local |
| B-F6 | Engine complex-NaN masking gives false equality; saved arrays all finite | **Reproduced**; modular already fixed; KNOWN in modular | `validation.py:263-272` comment. Finite-array claim not verified |
| B-F7 | Public oracle passes 201 vs 200 status rows | **Mechanism reproduced** (synthetic 3 vs 2); real-S01 201/200 not run | `oracle.py:97-111` uses sets, row count not checked |
| B-misc | Old workflow had no Python CI | **N/A** (stale) | main `.github/workflows/repo-checks.yml` |
| B-misc | CLI `describe` import path fails | **KNOWN** R026-S7 | — |
| B-misc | Same-env modular = original for one condition; vs saved S01: 131 NPZ and 89 scalar diffs ≤4.4e-13 under a different NumPy | Claim only; **AUD** later | Plausible environment drift; not a certificate |
| B-misc | 108/108 sync shell checks, 40/2 modular, 9 pass / 8 xfail | Claims only | — |
| B-sci | Lean projector explicitly not the implemented map; no global convergence claimed | Agrees with main's own Lean headers | Not a defect |

### Packet C — `researcher_040282` (Lean/research)

| Cycle | Establishes (my reading + my compile) | Explicitly does NOT establish | Status |
|---|---|---|---|
| 001 gate-foundations (paper) | Guarded map is a retraction and idempotent (paper); unguarded kernel not idempotent; jump c·ε/(c+ε) at guard boundary ⇒ not globally continuous/nonexpansive; strict branches are rational and nonlinear; full row-sum fibre gives `G(W+H)−G(W)=D.*H` | Not compiled at the time; not the selected-controller AUD-RATELAW; no locking | Idempotence **KNOWN** (AUD-GATE). The counterexamples are elementary and NEW-P as explicit scope warnings. I did not recheck the 300 Fraction or 96 engine cases |
| 002 guarded capacity Lean | **22 theorems compile (I compiled them)**, standard axioms only: kernel nonnegativity, symmetry, zero diagonal, row sandwich, gate feasibility, fixes feasible, idempotent, full-row-fibre difference, rational examples | Lemma 1(b,c), gated-OFF certificate, delay/EMA, Python linkage | NEW-P formal coverage of a gap main's `FreezeCore.lean` header names ("gate row-sum sandwich (Lemma 1)" not formalised) |
| 003 weight-update bridge | **44 declarations compile (me)**: clipped, symmetrised, zero-diagonal proposal; row envelopes; applied-factor floors and ratio bounds on both guard branches; first-step and H0 feasibility; scalar edge recurrence *derived* from the matrix update; per-edge ∃N OFF/ON by reusing upstream FreezeCore | Infinite-tail drive bands are **hypotheses** (`hu : ∀ n, u n i j ≤ U`, `hL : ∀ n, L ≤ u n i j`); no network aggregation; no explicit N; no phase/EMA; 24 engine checks override `compute_R` | NEW-P; honest conditional scope. Reuse credit stated separately (22 local + 5 upstream) |
| 004 complex EMA | **22 + 6 declarations compile (me)**: unit-norm phase input; EMA keeps the unit disk for α∈[0,1]; reportedR symmetric, zero diagonal, in [0,1]; Lipschitz readout; forced-difference recurrence; same-input geometric forgetting; constant-input closed form and convergence (α<1); drive bound (N−1)η/γ feeding an applied-factor floor. The model matches `compute_R` (`engine:735-750`) in exact reals (delay = `history[0]`, mean-ω·τ term, magnitude, then symmetrise, then zero diagonal) | Coupled locking; actual future bands; delay-buffer and phase-step semantics; float64 (binary α can equal 1). The coarse bound **cannot** certify ON at baseline (I verified 0.0576 < 0.12) | NEW-P, honest. **Date anomaly** (header 2026-09-04 after Nov-07 cycles) and **state drift** (root STATE, README, QUEUE and LEDGER stop at 003; 78 vs 108 ledger rows): auditor intake §4.6-4.7 |
| Ledger/STATE | 78 rows; labels are self-assigned | No independent review | Treat labels as claims; my compile upgrades only "compiles + footprint" for the 94 decls I built, not fidelity |

Lean flags: no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern`, `unsafe`, `opaque`, `#eval`, `run_cmd`, or custom syntax/macro in the eight accepted sources. Only `set_option autoImplicit false` and `linter.style.header false`. Their negative controls (false payloads, proof hole, extra axiom, missing footprint) live in `check_cycle.py`, which **I did not run**, so those control outcomes are still their claim.

## 5. Recommended next actions

**Owner**
1. Until Auditor Seat 002 checks B-F1/B-F2, don't rely on `tools/sync/upload_new.sh` to protect ignored local files or to catch secrets already committed. Back up irreplaceable ignored files before using it.
2. Privacy: three `source_state/*main_branch*.json` files hold copied commit-author email metadata (see the auditor intake §5; I copied no values). Decide on handling before anything is shared further.
3. Decide whether B-F4 (bridge self-test) gets an erratum. ART-0050 is pinned, so a fix is a new file plus an erratum, not an edit.
4. Optionally ask the researcher, through the owner only, for a cycle-004 date/state addendum. Do not contact them yourself.

**Auditor Seat 002 (reproduction, in this order)**
1. B-F1 and B-F2 in a sandbox with local bare remotes, using your own fixtures.
2. B-F4: confirm my residual independently and check whether any saved bridge evidence relies on `--self-test`.
3. B-F7 with the real S01 status CSV (201 vs 200), and B-F6 finiteness of the real baseline/S01 complex arrays, if those files are local.
4. Low priority: A-F4 and A-F5 fault injection; B-F5's 4,800-case zero-impact claim.

**Later science (R001)**
- Write a short S01 inference caveat: event-rate percentile intervals are fixed-cohort resampling diagnostics. Consider an exact or boundary-aware rate interval and `bootstrap_valid_replicates`/`n<2` flags in a future v4.x. Choose the held-event estimand labels (A-F3) in the v4.1 audit.
- Lean intake: a candidate module set (GateFoundations → GateProposalBridge → CoherenceEMA → CoherenceDriveBridge) on a review branch. Before calling it library-grade, review statement fidelity: global guard, ε>0, H0, diagonal of drive = −μ/γ, h=γ·dt, positive config.q. Run your own negative controls (drop guard, ε=0, cosine substitute, wrong delay index) rather than theirs, and decide the namespace.
- Next real gap: delay-buffer and phase-step semantics, and a *sharp* local row envelope or band-derivation for ON. Gated-OFF and finite-network aggregation stay open.

**Ignore / no action:** the stale CI generalization; the CLI path issue (R026-S7 already); A-F6 for S01; the "zero-impact on S01" claims as evidence of correctness (nice if true, not a certificate).

## 6. Owner-facing paragraph

The new researcher's upload has three parts. Two are bug reports about our code, one is formal math. I re-ran the cheap checks on today's main. Three of their bugs are real there: a self-test that prints PASS while checking the wrong case, an engine comparison that treats two different complex values as equal when one part is missing, and an output checker that doesn't notice a duplicated row. None of these broke a published result as far as we know. One more report needs care: they say the upload helper can overwrite an ignored file on your computer before asking you. I can see why in the code but haven't tested it yet, so for now back up any irreplaceable local files before using the uploader. Their main statistics point is fair: for many S01 recovery rates the "95% intervals" collapse to a single point, so they shouldn't be read as population-level uncertainty. The math part compiles cleanly on our toolchain with no shortcuts, and it fills gaps our own Lean files say are missing. It's worth taking in after review, but it doesn't prove the network locks. Nothing needs your action now except holding off on the uploader and deciding how to handle some personal email metadata copied into three of their snapshot files.

## 7. Auditor-facing paragraph

On 942f852 (read-only, my own witnesses, no inbox code run) I reproduced B-F4 exactly: the actual operator picks winners (2,2,7), and `synthetic_self_test` prints PASS while the left-identity residual on the real operator is −0.02121459694983044. I also reproduced B-F6 (engine True, modular False for nan+1j vs nan+99j and 1+nanj vs 5+nanj), B-F7's mechanism via public `compare_twindow_run` on minimal synthetic dirs (3 vs 2 rows with one duplicate → passed; missing/changed controls fail), A-F1 on v4 (None at 17.5 and 35.0; delayed index 100; sweep 32/26 false negatives; v4.1 0/0), and A-F2 (0/40→[0,0], 40/40→[1,1] in v4 and v4.1). B-F1/B-F2 are static-only: autostash integration at `upload_new.sh:84-85` precedes confirmation, there's no ignored-collision check, and the commit path checks names/HEAD sizes only. Please reproduce those first in a sandbox. Then B-F7 on the real 201/200 S01 file and real-array finiteness for B-F6 if local. All six cited files are byte-unchanged since 5c1ffed. I compiled the 040282 Lean (Lean 4.33.1, Mathlib 0df444a, local prebuilt): 22/44/22+6 declarations, 0 warnings, footprints only propext/Classical.choice/Quot.sound, no sorry or metaprogramming. I did not run their `check_cycle.py` controls. Scripts and logs: `/workspace/review_r040282/witness/`.
