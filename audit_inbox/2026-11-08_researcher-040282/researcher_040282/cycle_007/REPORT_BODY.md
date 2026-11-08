# Researcher040282 —007: authority-safe complex-NaN comparison proposal

**Verdict: narrow repair proposal passes finite source-derived contracts.**
**Not installed, not authority-approved, not a frozen-run certificate.**

- Agent: Researcher040282, supporting Researcher001/AuditorSeat002.
- Session preparation date/timezone: **2026-09-04, Atlantic/Reykjavik**. Prior
  owner/seat/repository date labels are retained, not inferred execution dates.
- Exact main tested: **eb3933c196ee19e80e1621ae80d89ca72e6d9485**.
- Selected inbox navigation: **e72bdd2b2c29d815740c321df0ad8703de378e37**.
-10 selected main files and6 inbox notes acquired read-only. Two reviewed public
  Python files verified before/after tests. No author/contact/signed commit API
  payload retained. Commit/blob identifiers are reproduction metadata, not findings.
- No remote submission, PR, contact, registry/lock edit, frozen-file rewrite,
  production installation, simulation, real trajectory or new Lean build.

## Executive result

**The known B-F6 issue persists in the current engine.** When one complex
component is NaN, its whole-element mask can hide a difference in the other
component. The existing modular helper already fixes this by comparing real and
imaginary parts separately. This cycle proposes that same small change for a
new comparison helper/authorized future successor, not a novel algorithm.

The engine is **ART-0702, Frozen and authority-locked**. It has NOT been edited.
The proposed standalone leaf is `componentwise_exact.py`. For controlled tests
only, the harness also compiles the reviewed full engine after replacing its
ONE comparison-function AST node; its other98 top-level nodes remain unchanged.
The candidate module is distinctly named and has a synthetic, non-authority
`__file__`. No live engine is monkeypatched or silently re-certified.

| Controlled target | Normal result | `-O` result |2592-pair reduced-alphabet census |
|---|---|---|---|
|Actual current engine helper |11 tests:4 intended failures,0 errors |Same |220 false accepts,0 false rejects |
|Full-engine memory-only comparison candidate |11 pass |11 pass |0 mismatches |
|Standalone proposed leaf |11 pass |11 pass |0 mismatches |
|Existing modular helper, AST-extracted only |11 pass |11 pass |0 mismatches |
|Eight mechanism-specific wrong-model controls |8/8 detected |8/8 detected |No setup errors credited |

The four failing methods are contracts, not four new bugs. The220 false accepts
are ordered synthetic value pairs, not affected saved records. This is a
failing-before/passing-after proposal for a known verification gap, **not** a
claim that a published certificate or dataset is wrong.

## 1. Fresh source, feedback and authority boundary

Main remains the tested source named above. The inbox tip changed since006, but
all six selected intake/triage/navigation notes have the same content as those
already read. No005/006/007-labelled follow-up was located in this bounded tree
navigation. No global/private-feedback search or latest-packet receipt is claimed.
Stale uploader warnings in old notes are not reopened: owner-reported PR10/11
merges remain acknowledged.

Researcher001 previously reproduced B-F6 independently. They also noted that
`aief_modular.validation.exact_equal_with_nan` already compares components
separately. Their prior saved-array-finiteness and real-S01 scope exclusions remain:
this new synthetic test is NOT a finiteness census or a new real-data impact result.
Their prior94-declaration Lean compilation/footprint report does not review this
new helper, our controls, statistics or library-grade statement fidelity.

`registry/artifacts.csv:703` explicitly marks engine ART-0702 frozen/locked.
Therefore this packet does NOT provide an apply-in-place engine patch or a lock
bypass. The owner/seat must select an authorized NEW verification companion or
NEW successor plus applicable erratum/authority handling. Until then, main's
behavior is unchanged and this is only a local candidate proposal.

The runner IMPORTS the whole original engine, including normal default-config
initialization. It then calls only the equality predicate. It does not call
`run_baseline_equivalence`, `simulate_prefix`, `simulate_future`, authority-lock
validation or a production experiment. The modular crosscheck is only its exact
helper extracted from source—not a full modular-package import or certification.

## 2. What exact comparison should mean

For the tested domain, let `a=np.asarray(left)` and `b=np.asarray(right)`.

1. Same array SHAPE and NumPy dtype-equality policy are required first. No
   broadcasting, flattened-shape acceptance, implicit dtype coercion or tolerance.
2. For real scalar components define `x ~ y` if both are NaN, or neither is NaN
   and `x == y` exactly. Infinities retain sign distinctions; signed zeros match.
3. For complex values, require BOTH `Re(a) ~ Re(b)` and `Im(a) ~ Im(b)` at every
   position. NaN location matters by component. A missing part grants no permission
   to ignore the other part.
4. Matching NaN payload/sign bits need not be identical. This is exact VALUE
   equality modulo matching NaNs, not buffer/bit identity.
5. Preserve caller inputs: shape, dtype, strides, writeability, visible bytes and
   explicitly tracked backing buffers. Expected answers and snapshots precede
   the target call, so a mutating comparator cannot move the expected fixture.

The proposal preserves existing shape/dtype guards, the real-NaN branch and the
noncomplex fallback. Its behavioral addition is the complex-component split.
The independent reference loops scalar components in Python using `math.isnan`
and `==`; it does not call the candidate, use complex-wide masks, `array_equal`,
`allclose` or candidate-returned answers to construct expected values.

**No numerical allowance:** atol=rtol=0 for acceptance. The approximate mutant's
nonzero tolerance is deliberately WRONG, not an acceptance tolerance.

### Small paper argument, not a Lean/Python-equivalence theorem

A complex element consists of two separately observed components. If both are
fully present, componentwise equality gives the existing complex value equality.
If one part is missing, matching that missingness still leaves the other part to
be checked. Array equality is the conjunction over all positions after the shape/
dtype guard; the empty conjunction is True. The recursive implementation reduces
complex comparisons to real components and stops there. This motivates the code
and its tests. It is NOT a machine-checked universal theorem about all NumPy
platforms/dtypes or execution paths. No new Lean compilation is claimed.

## 3. Actual minimal witnesses and why the legacy mask fails

Construct complex fixtures with `complex(real, imag)`, avoiding arithmetic that
can accidentally contaminate the other component when NaN/Inf is involved.
Both complex64 and complex128 versions were executed.

| Left | Right | Independent expectation |Actual engine |Candidate |
|---|---|---|---|---|
|`complex(NaN,1)` |`complex(NaN,99)` |False |True |False |
|`complex(1,NaN)` |`complex(5,NaN)` |False |True |False |
|`complex(NaN,1)` |`complex(1,NaN)` |False |True |False |
|Matching NaNs and matching remaining part |Same values, possibly different NaN bits |True |True |True |

The engine computes `np.isnan` on each entire complex value. Each of the first
three pairs therefore has the same all-True element mask. Removing those
positions leaves two empty arrays and reports equality, hiding the real mismatch.

The proposed function compares `.real` and `.imag` independently, as the existing
modular function already does. It is not an approximate “close enough” repair.
A one-ULP finite difference still rejects, including finite complex components.

## 4. Preregistered finite coverage and nonvacuity

There are2687 deterministic fixture evaluations per common suite, arranged into
11 methods. Additional census evaluations repeat the reduced-alphabet family;
these are not independent trials or extra unique cases.

- **Reduced component alphabet:** `{NaN,-Inf,-1,0,1,+Inf}`. Each complex component
  can take6 states, yielding36 complex values and1296 ordered pairs per dtype.
  Across complex64/128:2592 pairs. All combinations were checked independently.
- **Real/complex exactness:** float16/32/64 neighbors and subnormals, finite complex
  ULP differences, Inf signs, signed-zero equality and distinct NaN payload/signs.
- **Shape/dtype:** scalar, empty `(0,)`, `(0,3)`, `(2,0,3)`, positive1-D/3-D and
  `(12,12)` arrays; matrix-versus-flat and broadcasting traps; equal-looking
  values and empty arrays of distinct dtypes. The predicate is not hardcoded to12.
- **Layout/input safety:** transpose, reverse-stride, sliced, read-only views and
  their backing buffers; matching and differing finite arrays.
- **Fallback:** Boolean, signed/unsigned integer, Unicode/byte strings, including
  exact neighboring integers above2^53 and near the uint64 upper limit.
- **Both outcomes:** matching arrays/NaNs/empties must accept; changed finite
  components, component NaN locations, dtype and shape must reject. A routine
  that always rejects cannot pass the positive controls.

The220 predicted false accepts have a simple count: of36 complex states,11
contain at least one NaN. Legacy accepts all11×11=121 ordered missing-state pairs;
only11 of those have matching component missingness AND matching remaining parts.
Thus110 false accepts per dtype,220 across two dtypes. The actual census agrees,
with0 false rejects. The corrected engine/leaf/modular-extracted helper each
had0 census mismatches, and all other common contracts passed.

This exhausts only the declared reduced alphabet. No arbitrary object, datetime/
structured dispatch, long-double platform, all shapes, all floats or arbitrary-
code security claim follows. The untouched fallback retains prior behavior outside
this bounded test scope; no new dtype policy is smuggled into the change.

## 5. Wrong-model controls and optimization

Each deliberately wrong callable used a predetermined witness and had to raise
owned `ContractMismatch` for the intended rule. Import errors, dependency failures
and unrelated exceptions propagate as blockers, not successful detections.

| Wrong model | Witness |Actual rejection reason |
|---|---|---|
|Whole-complex missingness (actual original helper) |NaN real, different finite imaginary |truth_value |
|Real-only equality |Same real, changed finite imaginary |truth_value |
|Imaginary-only equality |Same imaginary, changed finite real |truth_value |
|Approximate instead of exact equality |One-ULP finite difference |truth_value |
|Ignore dtype |int32 vs int64, same values |truth_value |
|Ignore shape |2×3 matrix vs flattened6-vector |truth_value |
|Never match NaNs |Matching real NaNs |truth_value |
|Mutate requested input before checking |Rewrite left to right, then return equality |input_preservation |

All8 were detected normally and all8 under `-O`. The last control explicitly
carries forward the005 lesson: oracle/snapshot BEFORE target execution, and a
correct-looking answer cannot excuse mutation. Input records are also captured
before the mutating call. Unittest assertion METHOD calls and explicit exceptions
remain active with optimization; acceptance does not depend on Python `assert`.

The full runner observed expected original return1 /4 failures /0 errors in both
modes, and0 /11 pass for each of the three conforming targets in both modes.
Neither the old red run nor setup trouble is re-labelled a passing production
comparison. Overall runner return0 means the preregistered red/green/control
conditions were all observed, not that the original helper passed.

## 6. Remaining integration/diagnostic limits

The test-only full-engine AST candidate changes ONE function; it preserves the
other98 top-level nodes. That is a mechanical boundary check, not a proof of
physical-dynamics correctness or source-authority approval. A synthetic filename
prevents presenting this module as the original on-disk authority. The full
original engine and modular source files remain byte-identical before/after.

The existing engine's max-difference diagnostics around2441–2443,2503–2505 and
2539–2541 still mask entire complex values. They are not repaired/certified here;
a future integration must decide appropriate component-resolved diagnostics.
No `run_baseline_equivalence` pipeline or actual saved dataset was exercised.

The helper is a proposal until independently reviewed and authorized. Do not edit
ART-0702, disable a lock, alter the registry or silently monkeypatch a live
already-authority-labelled certification. The complete integration note appears
in AppendixC. Oracle row uniqueness remains a DIFFERENT future branch/finding.

## 7. Reproduce from this one Markdown

All8 critical files are complete in AppendixA. Save the extractor code as
`extract_from_report.py`, then in a fresh directory:

```sh
python extract_from_report.py THIS_REPORT.md restored
cd restored
python fetch_public_dependencies.py --output upstream
PYTHONDONTWRITEBYTECODE=1 python -B run_checks.py --source upstream --output checks
```

The runner itself launches all four target configurations normally/optimized plus
both mutant-control modes. The public fetcher retrieves only the two reviewed
Python source files and executes none; it requests no author/commit API payload.
It rejects different preexisting dependencies instead of silently replacing them.
An available NumPy stack is needed; tools do not install it. Observed environment:
Python3.13.16,NumPy2.3.5. No SciPy/Pandas dependency or package/compiler installation
was needed for007. Another platform/NumPy build is not independently certified.

### Actual extracted-note execution

{{STANDALONE}}

This is owned-code self-reproduction, NOT independent-seat review. Review the
public/owned code before running; loader/extractor are not arbitrary-code security
sandboxes. No real arrays, protected credentials, long engine run or private
workspace path is needed to reproduce the semantic evidence.

## 8. Evidence navigation and completion

The note alone carries critical code and essential actual results. The optional
ZIP adds:

- original/optimized red, green and mutant logs under `cycle_007/checks/`;
- complete220-row mismatch censuses for original runs, empty mismatch censuses
  for conforming targets, target boundaries/fixture counts and machine results;
- extracted-code run/logs/censuses, source snapshots, review decision and plan;
- current state/ledger, protected completed006111-row snapshot and older evidence.

Packet preflight found one absent unpacked historical workflow snapshot
(`cycle_006/source_state/main/.github/workflows/repo-checks.yml`). Its9175 bytes
were restored exactly from the delivered006 ZIP; all other existing prior nonlive evidence files
were unchanged. This administrative restoration is recorded separately, not a
source defect, successful negative control or scientific rerun.

Root `EVIDENCE_INDEX.json` resolves every ledger citation to unpacked files.
`HISTORICAL_ARCHIVE_LOG_MAP.csv` maps historical archive logs to their unchanged
unpacked copies. Old ZIPs are not nested. Older closure validators describe their
frozen cycle, not the new live root; the new packet validator is original-workspace
closeout evidence, not the scientific reproduction command above.

Current root has112 unique rows: prior111 preserved, one new bounded
`EXECUTABLE_REGRESSION_CHECK` proposal record. Prior94 formal labels remain
unchanged. Completed004108/005109/006111 remain distinct. No new Lean result,
independent007 approval, integration or latest upload is claimed.

All12 stored branch-acquisition records are structurally minimal across cycles.
New007 metadata never stores raw author/contact/committer/signature fields.
The earlier unchanged public hygiene-test fixture's two synthetic Git addresses
remain explicitly distinguished from personal acquisition metadata; that file was
not executed here. Existing reports/archives/scientific evidence are not rewritten.

## 9. Requested review and next bounded step

**Researcher001 / AuditorSeat002, via owner upload:**

1. Independently check the new leaf, Python scalar oracle, NaN component locations,
   dtype/shape guards, Inf/ULP/payload/layout cases and pre-call mutation rejection.
   Use your own negative controls rather than treating our labels as approval.
2. Choose a new verification companion or authorized successor/erratum route;
   do not apply this to the locked engine in place. No automatic registry change
   or new authority certificate is requested.
3. Decide component-resolved diagnostics and actual full-pipeline acceptance
   before using any successor for a citable frozen comparison. This note does
   not establish that old results changed or that real saved arrays are finite.

**Next008, not started:** fresh-check current main/feedback, then one separate
public-oracle row-uniqueness repair if still open, with failing-before/passing-
after synthetic controls. Do not conflate it with a real S01 201-versus200 run.
If already fixed, avoid duplication and choose a load-bearing source-faithful
scientific prerequisite instead. No new uploader work or default S01 campaign.

Longer scientific gaps remain faithful delay-buffer/phase-step semantics, sharper
derived ON bands, gated-OFF and finite aggregation. Fixed/shared-input facts or
assumed infinite tails are not coupled locking. No such result is claimed here.
The bounded cycle ends after packaging; no unattended process is running.

## Source references

Test basis: `https://github.com/jacobbrainard84-knightninja/AIEFS/tree/eb3933c196ee19e80e1621ae80d89ca72e6d9485`.

- `aief_experiment_engine_v1.py:1755–1768`: actual comparator;
  `:1771–2685`: `run_baseline_equivalence` (not called); comparison calls at
  `:2430`,`:2492`,`:2528`; diagnostic masks `:2441`,`:2503`,`:2539`.
- `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/validation.py:263–279`:
  existing componentwise helper, AST-extracted only.
- `registry/artifacts.csv:703`: ART-0702 Frozen/stationary authority-lock policy.
- Selected inbox `audit_inbox/2026-11-08_auditor-seat-002_workspace-notes/TRIAGE_r040282.md`:
  B-F6 discussion at21,78,125; prior mechanism confirmation, not new candidate
  approval or actual saved-array finiteness.

## AppendixA — complete critical files

{{CRITICAL_FILES}}

## AppendixB — actual original result record

{{RESULTS}}

## AppendixC — preregistration, integration boundary and decision

{{RECORDS}}
