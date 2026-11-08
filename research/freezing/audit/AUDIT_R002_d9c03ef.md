# AUDIT_R002_d9c03ef: copy of the Auditor Seat 002 audit of research/freezing @ d9c03ef

**What this is.** A copy of the read-only audit by **Auditor Seat 002** of branch `research/freezing` at
`d9c03ef`, dated **2026-10-31** (America/Toronto). Verdict: **CLEAN WITH NOTES**, no blockers; the revised
Corollary 4 is **CORRECT**. It was committed so that REPORT.md, README.md, CURRENT_STATUS.md and the
`RES-FREEZE-GATED` / `RES-FREEZE-NOVELTY` ledger rows can cite it. The text below the line is verbatim except
that the local worktree path was removed, local box paths of the auditor's scripts and Lean build logs were
replaced by "[local …]" markers, and one table row about personal details in commit metadata was omitted.
Nothing in the findings was changed. The auditor's scripts (`cor4_sanity.py`, `n0_check.py`) and logs are not in
the repo. The audit suggests the name `AUDIT_R002_COR4.md`; this file is that copy under the name
`AUDIT_R002_d9c03ef.md`.

**What changed since, on this branch** (REPORT.md §9, "Audit of d9c03ef"): notes N-a (start hypothesis "T ≥ 1,
or row sums ≤ c at start"), N-b (Thm 2 ON wording), N-c (re-audit wording), the stale `freeze_check.py:151`
comment, the three stale line refs, and the AUD-NOVELTY precedent are addressed. The `RES-FREEZE-NOVELTY`
vocabulary mapping is kept, as the audit recommends. The b2a95dfbfbe3 SHA256SUMS gap (§5) is pre-existing on main
and is not addressed here.

---

# Audit: research/freezing @ d9c03efde010ea608ca3a6983636783c793efd4b

Auditor Seat 002 (independent). Date: 2026-10-31. Read-only on the remote. Nothing was pushed or commented,
and no PR was opened.
Base: origin/main = 395ea53.

## Verdict: **CLEAN WITH NOTES**

* Corollary 4 (revised): **CORRECT.** I re-derived it independently, and the numerical sanity check
  passes 86/86, including the negative controls.
* Nothing blocks merging this branch.
* There is one repo-level CI GAP, which exists on main and is not introduced by this branch: the
  `b2a95dfbfbe3/SHA256SUMS` check (see §5).

---

## 1. SHA, ancestry, pins, privacy: PASS

| check | result |
|---|---|
| origin/research/freezing | d9c03efde010ea608ca3a6983636783c793efd4b ✔ |
| ancestry | 85ba0a6 (upload part 8/8) and 395ea53 (main) are both ancestors. 53e58eb is the merge of main. Fast-forward from 85ba0a6 ✔ |
| diff vs main | 34 files, +2866/−8 |
| hash-pinned files | none touched (`check_artifact_pins.py` PASS; `registry/artifacts.csv` snapshot unchanged) |
| `registry/artifacts_current.csv` | `build_current_inventory.py` regenerates it with no diff (3390 rows); `check_current_inventory` PASS |
| `registry/claims.csv` | `build_claims_reconciliation.py` regenerates it byte-identically (80 rows) |
| private data in added lines | no e-mail addresses and no tokens (ghp_/github_pat_/sk-/AKIA/private keys/xox). No absolute home paths. |
| commit metadata | [row omitted in this copy: it concerns personal details in commit metadata, not file contents; no finding about any file] |

## 2. Corollary 4: CORRECT

### Independent derivation (REPORT.md §3, lines 204–244)

1. **State-free lower bound.** Lemma 1(c) gives x⁺ ≥ (1/g)((1−h)x + h u^min) at every step n ≥ T ≥ 1, with
   ρ = (1−h)/g ∈ (0, 1−h] because g ≥ 1. The comparison sequence gives
   x_{T+k} ≥ x* − ρ^k (x* − x_T).
   * Since B ≥ 0 we have x_T ≥ 0, so (x* − x_T)⁺ ≤ x*.
   * For k ≥ N1, ρ^k ≤ ρ^{N1}, so B(T+k) ≥ (1−ρ^{N1}) x* = ℓ^0.
   * ℓ^0 is a valid bound that does not depend on B(T). It is **tight**: λ = 1/g, u = u^min and x_T = 0
     attain it exactly (checked in exact rational arithmetic, NC2b).
2. **Thm 3 with ℓ^0.** Thm 3 uses ℓ only as a lower bound for n ≥ T+N1, to get s_i ≥ σ_i and then
   λ_e ≤ κ_e. Since ℓ^0 ≤ ℓ (state-dependent), Thm 3 holds verbatim with ℓ^0, and its certificate is more conservative.
3. **Monotonicity.** All of these hold:
   * ℓ^0 = (h u^min/g) Σ_{k<N1} ρ^k is non-increasing in S⁺ (both factors are) and linear in u^min.
   * σ is non-decreasing in ℓ and u^min.
   * κ is non-increasing in σ.
   * f_u = κhU⁺/(1−κ(1−h)) is non-decreasing in κ and in U⁺. The denominator is ≥ h.
4. **Continuity.** Holds: g − 1 + h ≥ h > 0. κ is continuous (κ = 1 near σ ≤ c). ℓ^0 is written via max(u^min, 0).
5. **Order of choices.** Fix N1 first, using the limit data; then choose θ and T. This is correct. The old gap was that
   ℓ depended on B(T), which need not converge. The revision removes it, and the alternative liminf proof
   (Researcher 026) is also correct.
6. **Strictness.**
   * ON: ⌊ln r / ln(1/ρ)⌋ + 1 gives a strict >.
   * OFF and gated-OFF: give ≤ B_c, which matches the status definition `B > B_c`.
7. **Remark (a).** S̄_i ≤ Σ_j Ū_ij⁺ holds, because the limsup of a sum is at most the sum of the limsups.

### Numerical sanity check

Scripts: `cor4_sanity.py` and `n0_check.py` [local review scripts, not in the repo]. Logs: `cor4_check/*_log.txt` [local]. They are
independent re-implementations of the engine step, written from REPORT §1.2 and not importing the branch.
Runtime is 12 s.

**Results: 86/86 behaved as expected.**

* **S1 (ℓ^0 lower bound).** A 6-clique with R ∈ [0.999, 1] and the rest in [0.1, 0.3].
  * N1 ∈ {0, 500, 3000, 8000}.
  * Initial states:
    * B = 0;
    * engine-like;
    * **upper clip** (a perfect matching at B = c);
    * every row sum exactly c.
  * Adversarial R inside the band:
    * constant at the low end;
    * per-edge random bang-bang between the endpoints;
    * slow 1500-step blocks;
    * uniform.
  * Result: min(B − ℓ^0) ≥ 0 over all k ≥ N1 in every case, and row sums ≤ c for n ≥ 1.
* **S1 (Thm 2 ON, explicit N).** N_on = 944, last B ≤ B_c at step 307. ✔
* **S3 (Thm 2 OFF from the upper clip).** N_off = 11090, last B > B_c at step 2871. ✔
* **S2 (Thm 3 with ℓ^0).** A 7-clique with spread w ∈ {0, 1e-4}. The certificate is issued (κ ≈ 0.9964, f_u = 0.1056 / 0.1107).
  B ≤ B_c after N under R at the high end, bang-bang and uniform, from B = 0 and from the upper clip. ✔

**Negative controls.** Every control failed or was refused, as expected.

| control | result |
|---|---|
| NC1: R leaves the band (one ON edge dips to R = 0 for 4000 steps after N1) | ℓ^0 bound violated by 0.126 |
| NC1b: same dip | the ON edge flips 3 times |
| NC2: zero ON margin (x* = B_c exactly, exact rationals) | never ON after 400 steps; no finite N |
| NC3: zero gated-OFF margin (f_u = B_c) | never ≤ B_c |
| NC4: wide 7-clique band (w = 0.05) | Thm 3(ℓ^0) certificate **not** issued for N1 up to 32000 |
| NC5: OFF edge leaves the band on the high side after N_off | flips ON at step 11397 |

### Notes on Cor 4 and the theorems (non-blocking)

* **N-a: Lemma 1 at n = 0.** REPORT.md:152 says "for every n ≥ 1". Part (a) at n = 0 relies on the engine
  init (row sums ≤ 11·5e-4). For an arbitrary B(0) ∈ [0,c]^E, row sums can exceed c at n = 0. My example has
  row sums of 3.48, giving λ_0 = 0.18 < 1/g = 0.993, so Lemma 1(c) fails at that one step. From n = 1 on, row
  sums are ≤ c (verified). Thm 2/3 are applied "from T on". They need T ≥ 1, or the engine-init assumption,
  and should say so. This does not affect Cor 4, where T is large.
* **N-b: wording in the Thm 2 ON proof (REPORT.md:186).** "x* − ρ^k(x* − x_T) is non-decreasing in k" is
  only true for x_T ≤ x*. The conclusion is unaffected, since r < 1 gives N = 0.
* **N-c: REPORT.md:206.** The revised Cor 4 is still marked "not yet independently re-audited". So are the
  README table, CURRENT_STATUS.md:131–132 and the RES-FREEZE-GATED caveat. After this audit, the owner can
  update these to point to this file. I made no edits (read-only).

## 3. Claims rows: PASS. Keep the NOVELTY deviation.

* `lint_claims`: 80 rows, 0 violations. `validate_registry_against_tree`: exit 0. `verify_inventory_current`: ALL PASS.
* Rows (registry/claims.csv:71–74):

  | row | artifact_status | evidence_scope | audited_status |
  |---|---|---|---|
  | LEAN-FREEZE-CORE | Supported | Formalized theorem | Supported |
  | RES-FREEZE-GATED | Exploratory | Conditional theorem | — |
  | RES-FREEZE-NUM | Exploratory | Finite numerical observation | — |
  | RES-FREEZE-NOVELTY | Incomplete | Conjecture | Not established |

  * RES-FREEZE-GATED cites ℓ^0, has the re-audit caveat, and says promotion needs an independent audit. This is correct.
  * RES-FREEZE-NUM wording matches results.json: 1,412 certified (run, T), 249 with N > 0, 0 violations. I recounted this.
* Owner label rules: no Retired or Quarantined rows are used. The origin labels are untouched.
* **RES-FREEZE-NOVELTY deviation: acceptable, keep it.**
  * The audit label is in `audited_qualifier`, and "Scope: Literature assessment (non-exhaustive)" opens the caveat.
  * There is an exact precedent: **AUD-NOVELTY** (also a novelty row) already uses
    `Incomplete / Conjecture / Not established` (registry/README.md:83).
  * Minimal fix (non-blocking): cite AUD-NOVELTY instead of, or in addition to, AUD-B-SCAFFOLD in the
    reconciliation note, because AUD-NOVELTY is the closer precedent.
  * A vocab addition (evidence_scope `Literature assessment`) would be cleaner. If wanted, it belongs in a
    separate registry PR that migrates AUD-NOVELTY and RES-FREEZE-NOVELTY together, with
    registry/README.md Axis 2, verify_inventory.py and lint updated. It should not go in this PR.

## 4. Lean: PASS

* `SKIP_CACHE=1 check_lean_freeze.sh` was run on a local copy ([local build logs]):
  * toolchain and pins OK; mathlib 0df444a3 = pin;
  * 1669 jobs, 0 warnings;
  * markers scan 0 hits; no `sorry`, `admit` or `axiom` in the sources.
* Five declarations, all on [propext, Classical.choice, Quot.sound]. They are in
  lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean:
  * upper_geom (:36)
  * eventually_off (:54)
  * eventually_on (:74)
  * edge_eventually_off (:85)
  * edge_eventually_on (:113)
* These match the LEAN-FREEZE-CORE row and the README table. The Lean scope is per-edge ∃N only; Lemma 1,
  Thm 3, Cor 4 and the explicit N are not in Lean, and this is stated.
* GitHub "Lean proof check" on d9c03ef: success (run 41214901626; all 3 matrix rows including AIEFFreezeCore).

## 5. False-result hunt and local CI

**Local CI (all PASS):**

* unittest: 103 tests OK.
* lint_claims: 0 violations.
* hygiene_scan --base origin/main: 34 files, PASS.
* check_manifest: PASS. check_artifact_pins: PASS.
* check_modes --strict: PASS.
* check_current_inventory: PASS. verify_inventory_current: ALL PASS. validate_registry_against_tree: exit 0.

**Re-run of the numerics.**

* `freeze_check.py --crosscheck`: engine cross-check max|ΔB| = 0.0 over 3000 steps, and results.json is
  **byte-identical**.
* `guard_check.py`, `clique7_check.py` and `margins.py` rewrote their JSON byte-identically (git status clean).

**Hunt findings.** Nothing invalidates a result.

* **Tuned thresholds.**
  * MARGIN_GUARD = 1e-9 (freeze_check.py:26) was introduced after a found failure (1e-13). It only
    *removes* certificates, so it is conservative.
  * It is not a proven float error bound, and the README/REPORT say so. guard_check shows the OFF explicit
    N is attained to the step (pred = last_change at margins 1e-3, 1e-6 and 1e-10). So float rounding could
    in principle cost one step at any margin, if the real-arithmetic value at step N lands within a few ulp
    of B_c. This is documented as engineering-level, and is acceptable.
* **Always-pass checks.** None. The `ok` check in `analyse` (L ≤ pred and final class) can fail, and does
  fail unguarded at margin 1e-13. The negative controls in my script fail as expected.
* **Silent fallbacks and NaN.** A NaN in R would make min/max NaN, so every comparison is False and the edge
  is left uncertified. This fails safe. The `kap*(1-H)>=1` skip is dead code (κ ≤ 1), and harmless.
* **Seeds.** These are the 5 repo seeds, plus documented variants. No cherry-picking: all certified T are
  reported (1,412) and none violate.
* **Self-reference.** The R band is the realised range over the same finite window [T, 80000) that is then
  checked. The proofs are causal, so this is a valid finite-horizon test of the theorem. It is **not**
  evidence of closed-loop freezing on [T, ∞), and the README/RES-FREEZE-NUM state this. `--crosscheck`
  covers only the default engine configuration, for 3000 steps. The no-delay, random-ω, stress and reset
  variants are not engine modes, so they are not cross-checked.
* **Stale comment.** freeze_check.py:151 says "certificate expected to FAIL (c/11 < B_c)" for the stress
  run, but the run is fully certified (66 goff) and REPORT.md:293 says so.
* **Stale line refs in REPORT.md.** These are off by 3 since the MARGIN_GUARD block was added:
  * `simulate :26-53` (REPORT.md:101) is actually 29–56;
  * `certificate :55-96` (REPORT.md:202) is actually 58–99;
  * `:153-160` (REPORT.md:248) is actually 156–163.

**b2a95dfbfbe3 SHA256SUMS: confirmed, CI GAP (pre-existing on main).**

* `audits/reproductions/b2a95dfbfbe3/SHA256SUMS` lists `compare_b2a95dfbfbe3_v3.log`, which is absent on
  both main (395ea53) and this branch, so `sha256sum -c` fails.
* No tools/ci script or workflow verifies per-reproduction SHA256SUMS.
* main's latest "Repo checks" (run 41206475180, PR #2 merge, completed 2026-10-31 09:39 EDT) is **green**.
  Green CI while the check fails means a **GAP**.
* The branch neither introduces nor fixes it.
* Recommended fix, in a separate PR: restore the log or correct SHA256SUMS, and add a CI step that runs
  `sha256sum -c` in every `audits/reproductions/*/` folder that contains a SHA256SUMS file.

## 6. Merge to-dos

| item | state |
|---|---|
| lean.yml AIEFFreezeCore `required: true` | **done** (.github/workflows/lean.yml:49; comment at :16–18 updated) |
| scripts executable | `lean/AIEFFreezeCore/check_lean_freeze.sh` and `research/freezing/lean/check.sh` are 100755 ✔ (these are the only check_modes known-list entries; strict PASS). `research/freezing/{freeze_check,guard_check,clique7_check}.py` have shebangs but are 100644 (SHEBANG_NOT_EXEC warning only). They are documented as run via `python ...`. Optionally `chmod +x` them. |
| claims regenerated | **done**: regeneration is byte-identical (80 rows); RES-FREEZE-01 is replaced via REPLACED_IDS |
| Repo checks on the PR | have not run on this branch yet (push trigger is main-only; it runs on `pull_request`). Must be green on the PR. |

## What the PR still needs

None of the following blocks the merge.

1. Optionally, update the "not yet independently re-audited" wording for Cor 4 to cite this audit. It
   appears in REPORT.md:206, README, CURRENT_STATUS.md:131–132 and the RES-FREEZE-GATED caveat. Add this
   file as `research/freezing/audit/AUDIT_R002_COR4.md` if a copy is wanted.
2. Add a clause to REPORT.md Lemma 1 / Thm 2–3: "T ≥ 1, or B(0) with row sums ≤ c" (N-a). Fix the wording in N-b.
3. Fix the stale comment at freeze_check.py:151 and the 3 stale line refs in REPORT.md.
4. In the RES-FREEZE-NOVELTY reconciliation note, cite AUD-NOVELTY as the precedent.
5. Optionally `chmod +x` the three freezing .py scripts.
6. Separately from this PR, fix the b2a95dfbfbe3 SHA256SUMS issue and the CI GAP.
