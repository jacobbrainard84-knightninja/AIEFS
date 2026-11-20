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

**Actually executed.** Eight critical files were extracted byte-for-byte; two public dependency files were freshly fetched/verified. The extracted runner returned0 after repeating all original/candidate/modular normal/-O contracts and both mutant modes. Scientific summaries and per-target non-timing results match the original run. This is submitter-local self-reproduction, not independent-seat confirmation.

```json
{
  "actually_executed": true,
  "runner_returncode": 0,
  "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "critical_file_count": 8,
  "critical_files": [
    "comparison_contract.py",
    "componentwise_exact.py",
    "extract_from_report.py",
    "fetch_public_dependencies.py",
    "load_reviewed.py",
    "run_checks.py",
    "source_modules.json",
    "test_comparison_contract.py"
  ],
  "all_extracted_files_byte_identical": true,
  "fresh_public_source_files_fetched_and_verified": 2,
  "scientific_summary_matches_original": true,
  "all_ten_child_nontiming_results_match_original": true,
  "all_eight_target_census_files_byte_identical": true,
  "normal_and_optimized_baseline_failures": [
    4,
    4
  ],
  "baseline_errors": [
    0,
    0
  ],
  "candidate_engine_leaf_modular_pass_counts_each_mode": [
    11,
    11,
    11
  ],
  "mutants_detected_each_mode": [
    8,
    8
  ],
  "original_elapsed_seconds": 5.770836757999973,
  "extracted_elapsed_seconds": 5.784219223000036,
  "command": "python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks",
  "result": "cycle_007/standalone/checks/cycle_results.json",
  "log": "cycle_007/standalone/reproduction.log",
  "scope": "Submitter-local exact-note reproduction, not independent controls/review, a production fix, full-engine equivalence certification, real-array finiteness or a Lean theorem"
}
```


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

### componentwise_exact.py

<!-- BEGIN_CRITICAL_FILE: componentwise_exact.py -->
```python
"""Proposed comparison helper only; no installation or authority modification.

Reuse the existing modular helper's component split for an authorized successor
or verification companion. Importing this file patches nothing. No simulation,
lock check, saved-run comparison certificate or dtype-policy expansion is supplied.
"""
import numpy as np


def exact_array_equal_with_nan(a: np.ndarray, b: np.ndarray) -> bool:
    """Value-level exact equality: matching shape/dtype and per-component NaNs.

    Signed zeros compare equal; NaN payload bits need not match. A missing real
    component never hides a different imaginary component, or conversely.
    """
    a = np.asarray(a)
    b = np.asarray(b)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if np.issubdtype(a.dtype, np.complexfloating):
        return exact_array_equal_with_nan(a.real, b.real) and exact_array_equal_with_nan(a.imag, b.imag)
    if np.issubdtype(a.dtype, np.floating):
        a_nan = np.isnan(a)
        b_nan = np.isnan(b)
        if not np.array_equal(a_nan, b_nan):
            return False
        finite = ~a_nan
        return np.array_equal(a[finite], b[finite])
    return np.array_equal(a, b)
```
<!-- END_CRITICAL_FILE: componentwise_exact.py -->

### comparison_contract.py

<!-- BEGIN_CRITICAL_FILE: comparison_contract.py -->
```python
"""Independent scalar-component spec and deterministic finite007 fixtures.
No candidate helper, complex-wide missingness mask or approximate oracle.
"""
from dataclasses import dataclass
import math
from typing import Any
import numpy as np


class ContractMismatch(RuntimeError):
    def __init__(self, rule, name, expected, observed):
        self.rule = rule
        self.case = name
        self.expected = expected
        self.observed = observed
        super().__init__(f'{rule}: {name}; expected={expected}, observed={observed}')


@dataclass
class Case:
    group: str
    name: str
    left: Any
    right: Any
    watch: tuple = ()


def real_equal(x, y):
    x, y = float(x), float(y)
    return math.isnan(y) if math.isnan(x) else not math.isnan(y) and x == y


def specification(left, right):
    a, b = np.asarray(left), np.asarray(right)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    for x, y in zip(a.flat, b.flat):
        if a.dtype.kind == 'c':
            if not real_equal(x.real, y.real) or not real_equal(x.imag, y.imag):
                return False
        elif a.dtype.kind == 'f':
            if not real_equal(x, y):
                return False
        elif not bool(x == y):
            return False
    return True


def fingerprint(value):
    a = np.asarray(value)
    return (a.shape, a.dtype.str, a.strides, a.flags.writeable, a.tobytes(order='C'))


def checked(target, case):
    objects = (case.left, case.right) + case.watch
    snapshots = tuple(fingerprint(value) for value in objects)
    expected = specification(case.left, case.right)  # MUST precede target call.
    answer = target(case.left, case.right)
    after = tuple(fingerprint(value) for value in objects)
    if snapshots != after:
        raise ContractMismatch('input_preservation', case.name, 'unchanged', 'mutated')
    if not isinstance(answer, (bool, np.bool_)):
        raise ContractMismatch('boolean_return', case.name, 'scalar boolean', type(answer).__name__)
    answer = bool(answer)
    if answer != expected:
        raise ContractMismatch('truth_value', case.name, expected, answer)
    return answer


def cases():
    out = []
    def add(group, name, left, right, watch=()):
        out.append(Case(group, name, left, right, watch))
    for dtype in (np.complex64, np.complex128):
        tag = np.dtype(dtype).name
        def z(r, i):
            return np.array([complex(r, i)], dtype=dtype)
        add('missing_real', tag + '_missing_real_changed_imag', z(math.nan, 1), z(math.nan, 99))
        add('missing_imag', tag + '_missing_imag_changed_real', z(1, math.nan), z(5, math.nan))
        add('nan_positions', tag + '_swapped_missing_component', z(math.nan, 1), z(1, math.nan))
        alphabet = (math.nan, -math.inf, -1.0, 0.0, 1.0, math.inf)
        values = [complex(r, i) for r in alphabet for i in alphabet]
        for i, left in enumerate(values):
            for j, right in enumerate(values):
                add('reduced_alphabet', tag + f'_alphabet_{i}_{j}',
                    np.array([left], dtype=dtype), np.array([right], dtype=dtype))
        add('complex_exactness', tag + '_matching_inf_components', z(math.inf, -math.inf), z(math.inf, -math.inf))
        add('complex_exactness', tag + '_opposite_inf_components', z(math.inf, 1), z(-math.inf, 1))
        add('complex_exactness', tag + '_signed_zero_values', z(-0.0, 0.0), z(0.0, -0.0))
        component = np.float32 if dtype is np.complex64 else np.float64
        neighbor = float(np.nextafter(component(1), component(2)))
        add('complex_exactness', tag + '_imaginary_one_ulp', z(1, 1), z(1, neighbor))
        add('complex_exactness', tag + '_real_one_ulp', z(1, 1), z(neighbor, 1))
        uint = np.uint32 if dtype is np.complex64 else np.uint64
        nan1 = 0x7fc00001 if dtype is np.complex64 else 0x7ff8000000000001
        nan2 = 0xffc00002 if dtype is np.complex64 else 0xfff8000000000002
        one = np.array([component(1)], dtype=component).view(uint)[0]
        a = np.array([nan1, one], dtype=uint).view(dtype)
        b = np.array([nan2, one], dtype=uint).view(dtype)
        add('complex_exactness', tag + '_nan_payload_sign_ignored', a, b)
    for dtype in (np.float16, np.float32, np.float64):
        tag = np.dtype(dtype).name
        a = np.array([1.0], dtype=dtype)
        neighbor = np.nextafter(a, np.array([2.0], dtype=dtype))
        subnormal = np.nextafter(np.array([0.0], dtype=dtype), np.array([1.0], dtype=dtype))
        add('real_exactness', tag + '_one_ulp', a, neighbor)
        add('real_exactness', tag + '_nonzero_subnormal', np.array([0], dtype=dtype), subnormal)
        add('real_exactness', tag + '_same_nan_inf_zero', np.array([math.nan, math.inf, -math.inf, -0.0], dtype=dtype),
            np.array([math.nan, math.inf, -math.inf, 0.0], dtype=dtype))
        add('real_exactness', tag + '_nan_position', np.array([math.nan, 1], dtype=dtype), np.array([1, math.nan], dtype=dtype))
        add('real_exactness', tag + '_inf_sign', np.array([math.inf], dtype=dtype), np.array([-math.inf], dtype=dtype))
    for dtype in (np.float64, np.complex128, np.int64):
        a = np.arange(6, dtype=np.float64).astype(dtype).reshape(2, 3)
        add('guards', str(dtype) + '_shape_not_flattened', a, a.reshape(6))
        add('guards', str(dtype) + '_shape_not_broadcast', np.ones((1, 3), dtype=dtype), np.ones((2, 3), dtype=dtype))
    for left, right in ((np.int32, np.int64), (np.float32, np.float64), (np.complex64, np.complex128), (np.uint32, np.int32)):
        add('guards', str(left) + '_dtype', np.array([1, 2], dtype=left), np.array([1, 2], dtype=right))
        add('guards', str(left) + '_empty_dtype', np.array([], dtype=left), np.array([], dtype=right))
    for shape in ((), (0,), (0, 3), (2, 0, 3), (1,), (2, 3, 4), (12, 12)):
        for dtype in (np.float64, np.complex128, np.int64):
            add('empty_scalar', str(shape) + str(dtype), np.zeros(shape, dtype=dtype), np.zeros(shape, dtype=dtype))
    add('empty_scalar', 'python_float_nan', math.nan, math.nan)
    add('empty_scalar', 'python_complex_nan', complex(math.nan, 1), complex(math.nan, 1))
    add('empty_scalar', 'numpy_complex_scalar', np.complex64(complex(1, math.nan)), np.complex64(complex(1, math.nan)))
    for kind in ('transpose', 'reverse', 'stride', 'readonly'):
        base = np.arange(60, dtype=np.float64).reshape(3, 4, 5)
        a = {'transpose': base.transpose(2, 0, 1), 'reverse': base[:, ::-1, :],
             'stride': base[:, ::2, ::2], 'readonly': base.view()}[kind]
        if kind == 'readonly':
            a.flags.writeable = False
        b = a.copy()
        add('views', kind + '_equal', a, b, (base,))
        add('views', kind + '_finite_difference', a, b + 1, (base,))
    for dtype, values in ((np.bool_, [True, False]), (np.int8, [-1, 0, 1]),
                          (np.int64, [2**53, 2**53 + 1]), (np.uint64, [2**64 - 2, 2**64 - 1]),
                          ('U2', ['a', 'bb']), ('S2', [b'a', b'bb'])):
        a = np.array(values, dtype=dtype)
        add('fallback', str(dtype) + '_equal', a, a.copy())
        add('fallback', str(dtype) + '_different', a, a[::-1].copy())
    for dtype in (np.float32, np.float64, np.complex64, np.complex128):
        a = np.array([1, 2, 3], dtype=dtype)
        add('preservation', str(dtype) + '_equal_inputs_preserved', a, a.copy())
    return out


def group_names():
    return ('missing_real', 'missing_imag', 'nan_positions', 'reduced_alphabet',
            'real_exactness', 'complex_exactness', 'guards', 'empty_scalar',
            'views', 'fallback', 'preservation')
```
<!-- END_CRITICAL_FILE: comparison_contract.py -->

### load_reviewed.py

<!-- BEGIN_CRITICAL_FILE: load_reviewed.py -->
```python
"""Verify two reviewed public sources and load isolated007 test targets.
Not a sandbox for arbitrary submissions; never install/patch the frozen engine.
"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import numpy as np

HERE = Path(__file__).resolve().parent
ENGINE_FUNCTION = 'exact_array_equal_with_nan'


def verify(source):
    manifest = json.loads((HERE / 'source_modules.json').read_text())
    for record in manifest['modules']:
        data = (source / record['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != record['blob'] or len(data) != record['bytes']:
            raise RuntimeError('Reviewed source differs: ' + record['path'])
    return manifest


def function_node(tree, name):
    found = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(found) != 1:
        raise RuntimeError('Need exactly one reviewed top-level function: ' + name)
    return found[0]


def make_module(name, filename, tree, namespace=None):
    module = types.ModuleType(name)
    module.__file__ = filename
    if namespace:
        module.__dict__.update(namespace)
    sys.modules[name] = module  # Must precede dataclass execution.
    exec(compile(tree, filename, 'exec'), module.__dict__)
    return module


def load_target(source, mode):
    source = Path(source).resolve()
    manifest = verify(source)
    engine = source / manifest['engine']
    boundary = {'mode': mode, 'simulation_or_validation_entrypoints_called': False}
    if mode in ('baseline', 'candidate-engine'):
        tree = ast.parse(engine.read_text())
        original = function_node(tree, ENGINE_FUNCTION)
        boundary['original_function_lines'] = [original.lineno, original.end_lineno]
        if mode == 'candidate-engine':
            proposal = ast.parse((HERE / 'componentwise_exact.py').read_text())
            replacement = copy.deepcopy(function_node(proposal, ENGINE_FUNCTION))
            position = tree.body.index(original)
            unchanged = [ast.dump(node, include_attributes=False) for i, node in enumerate(tree.body) if i != position]
            tree.body[position] = replacement
            after = [ast.dump(node, include_attributes=False) for i, node in enumerate(tree.body) if i != position]
            if unchanged != after:
                raise RuntimeError('Candidate changed more than the one comparison function')
            boundary.update({'only_one_function_ast_replaced': True,
                             'noncomparison_top_level_nodes_preserved': len(unchanged),
                             'authority_certified': False})
            filename = '<R040282_COMPARISON_ONLY_MEMORY_CANDIDATE_NOT_AUTHORITY>'
        else:
            filename = str(engine)
        module = make_module('_r040282_007_' + mode.replace('-', '_'), filename, ast.fix_missing_locations(tree))
        target = getattr(module, ENGINE_FUNCTION)
    elif mode == 'candidate-leaf':
        path = HERE / 'componentwise_exact.py'
        spec = importlib.util.spec_from_file_location('_r040282_007_leaf', path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        target = getattr(module, ENGINE_FUNCTION)
        boundary['no_patch_on_import'] = True
    elif mode == 'modular-extracted':
        path = source / manifest['modular_validation']
        text = path.read_text()
        node = function_node(ast.parse(text), 'exact_equal_with_nan')
        code = 'from __future__ import annotations\n' + ast.get_source_segment(text, node) + '\n'
        module = make_module('_r040282_007_modular_helper_only', str(path) + ':AST-EXTRACTED-HELPER-ONLY',
                             ast.parse(code), {'np': np})
        target = module.exact_equal_with_nan
        boundary['full_modular_package_imported'] = False
        boundary['extracted_helper_lines'] = [node.lineno, node.end_lineno]
    else:
        raise ValueError('Unknown controlled test mode')
    verify(source)
    return target, boundary
```
<!-- END_CRITICAL_FILE: load_reviewed.py -->

### test_comparison_contract.py

<!-- BEGIN_CRITICAL_FILE: test_comparison_contract.py -->
```python
"""Same11 contracts on original and proposed predicates; safe under python -O."""
import unittest
from comparison_contract import cases, checked, ContractMismatch, group_names


def make_suite(target):
    fixtures = cases()
    class ComparisonContract(unittest.TestCase):
        pass
    def method(group):
        def test(self):
            selected = [case for case in fixtures if case.group == group]
            self.assertTrue(selected, 'No positive fixture for group ' + group)
            violations = []
            for case in selected:
                try:
                    checked(target, case)
                except ContractMismatch as error:
                    violations.append(str(error))
            self.assertEqual(len(violations), 0,
                             str(len(violations)) + ' contract mismatches; first3=' + repr(violations[:3]))
        return test
    for group in group_names():
        setattr(ComparisonContract, 'test_' + group, method(group))
    return unittest.defaultTestLoader.loadTestsFromTestCase(ComparisonContract)
```
<!-- END_CRITICAL_FILE: test_comparison_contract.py -->

### run_checks.py

<!-- BEGIN_CRITICAL_FILE: run_checks.py -->
```python
"""Run preregistered007 red/green/-O comparison contracts and eight mutants.

Source/child setup errors are blockers, never successful red evidence. No real
trajectory, frozen-run validation, installation or authority-file edit occurs.
"""
import argparse
from collections import Counter
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import numpy as np

from comparison_contract import Case, ContractMismatch, cases, checked
from load_reviewed import load_target, verify
from test_comparison_contract import make_suite

HERE = Path(__file__).resolve().parent
MODES = ('baseline', 'candidate-engine', 'candidate-leaf', 'modular-extracted')
EXPECTED_RED = {'test_missing_real', 'test_missing_imag', 'test_nan_positions', 'test_reduced_alphabet'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def store(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def describe(value):
    a = np.asarray(value)
    return {'shape':list(a.shape), 'dtype':str(a.dtype), 'values_repr':repr(a.tolist())}


def census(target):
    selected = [case for case in cases() if case.group == 'reduced_alphabet']
    mismatches = []
    for case in selected:
        left, right = describe(case.left), describe(case.right)
        try:
            checked(target, case)
        except ContractMismatch as error:
            require(error.rule == 'truth_value', 'Unexpected nontruth census violation')
            mismatches.append({'case':case.name, 'expected':error.expected, 'observed':error.observed,
                               'left':left, 'right':right})
    summary = {'ordered_pairs':len(selected), 'mismatches':len(mismatches),
               'false_accepts':sum(not row['expected'] and row['observed'] for row in mismatches),
               'false_rejects':sum(row['expected'] and not row['observed'] for row in mismatches)}
    return summary, mismatches


def mutant_check(source):
    fixed, _ = load_target(source, 'candidate-engine')
    original, _ = load_target(source, 'baseline')
    def real_only(a, b):
        return fixed(np.asarray(a).real, np.asarray(b).real)
    def imag_only(a, b):
        return fixed(np.asarray(a).imag, np.asarray(b).imag)
    def approximate(a, b):
        a, b = np.asarray(a), np.asarray(b)
        return a.shape == b.shape and a.dtype == b.dtype and bool(np.allclose(a, b, rtol=1e-5, atol=1e-8, equal_nan=True))
    def ignore_dtype(a, b):
        return fixed(np.asarray(a, dtype=np.complex128), np.asarray(b, dtype=np.complex128))
    def ignore_shape(a, b):
        return fixed(np.asarray(a).reshape(-1), np.asarray(b).reshape(-1))
    def never_match_nan(a, b):
        return bool(np.array_equal(a, b))
    def mutate_input(a, b):
        a[...] = b
        return fixed(a, b)
    def pair(name, a, b):
        return Case('mutant_witness', name, a, b)
    def z(r, i):
        return np.array([complex(r, i)], dtype=np.complex128)
    mutants = [
        ('whole_complex_missingness', original, pair('missing_real_masks_finite_imag', z(math.nan, 1), z(math.nan, 99)), 'truth_value'),
        ('real_only', real_only, pair('imag_changes', z(1, 1), z(1, 2)), 'truth_value'),
        ('imaginary_only', imag_only, pair('real_changes', z(1, 1), z(2, 1)), 'truth_value'),
        ('approximate_equality', approximate, pair('one_ulp_not_equal', np.array([1.]), np.nextafter(np.array([1.]), np.array([2.]))), 'truth_value'),
        ('ignore_dtype', ignore_dtype, pair('int32_vs_int64', np.array([1], dtype=np.int32), np.array([1], dtype=np.int64)), 'truth_value'),
        ('ignore_shape', ignore_shape, pair('matrix_vs_flat', np.arange(6).reshape(2, 3), np.arange(6)), 'truth_value'),
        ('never_match_nan', never_match_nan, pair('matching_float_nan', np.array([math.nan]), np.array([math.nan])), 'truth_value'),
        ('mutate_requested_input', mutate_input, pair('precall_original_inputs', np.array([1., 2.]), np.array([3., 4.])), 'input_preservation'),
    ]
    records = []
    for label, target, case, intended in mutants:
        before = {'left':describe(case.left), 'right':describe(case.right)}
        try:
            checked(target, case)
        except ContractMismatch as error:
            require(error.rule == intended, 'Wrong rejection reason for mutant ' + label)
            records.append({'mutant':label, 'detected':True, 'reason':error.rule,
                            'expected':error.expected, 'observed':error.observed, 'precall_input':before})
        else:
            raise RuntimeError('Undetected controlled mutant: ' + label)
    require(len(records) ==8, 'Mutant inventory incomplete')
    verify(source)
    return records


def child(args):
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    if args.child == 'mutants':
        records = mutant_check(args.source)
        value = {'mode':'mutants', 'mutants_detected':len(records), 'setup_errors_credited_as_detections':0,
                 'records':records, 'optimized_python':not __debug__, 'verified_source_files_unchanged':len(verify(args.source)['modules']),
                 'elapsed_seconds':time.perf_counter() - start}
        store(args.output / 'result.json', value)
        print(json.dumps(value, indent=2))
        return 0
    target, boundary = load_target(args.source, args.child)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(make_suite(target))
    print(stream.getvalue(), end='')
    summary, mismatches = census(target)
    store(args.output / 'reduced_alphabet_mismatches.json', mismatches)
    failure_names = [test.id().split('.')[-1] for test, _ in result.failures]
    error_names = [test.id().split('.')[-1] for test, _ in result.errors]
    records = {'mode':args.child, 'optimized_python':not __debug__,
               'tests_run':result.testsRun, 'failures':len(result.failures), 'errors':len(result.errors),
               'skipped':len(result.skipped), 'failure_methods':sorted(failure_names), 'error_methods':sorted(error_names),
               'reduced_alphabet':summary, 'fixture_group_counts':dict(Counter(case.group for case in cases())),
               'source_boundary':boundary,
               'verified_source_files_unchanged':len(verify(args.source)['modules']),
               'elapsed_seconds':time.perf_counter() - start}
    store(args.output / 'result.json', records)
    print(json.dumps(records, indent=2))
    return 0 if result.wasSuccessful() else 1


def parent(args):
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    manifest = verify(args.source)
    runs = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    environment.pop('PYTHONOPTIMIZE', None)
    modes = MODES + ('mutants',)
    for mode in modes:
        for optimized in (False, True):
            name = mode + ('_optimized' if optimized else '_normal')
            directory = args.output / name
            command = [sys.executable] + (['-O'] if optimized else []) + ['-B', str(Path(__file__).resolve()),
                       '--child', mode, '--source', str(args.source.resolve()), '--output', str(directory.resolve())]
            completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, env=environment, timeout=90)
            (args.output / (name + '.log')).write_text(completed.stdout)
            require((directory / 'result.json').is_file(), 'Child setup/run failed before result: ' + name)
            result = json.loads((directory / 'result.json').read_text())
            require(result['optimized_python'] is optimized and result['verified_source_files_unchanged'] ==2,
                    'Optimization/source-preservation record mismatch')
            if mode == 'mutants':
                require(completed.returncode ==0 and result['mutants_detected'] ==8 and
                        result['setup_errors_credited_as_detections'] ==0, 'Mutant sensitivity incomplete')
            elif mode == 'baseline':
                require(completed.returncode ==1 and result['tests_run'] ==11 and result['failures'] ==4 and
                        set(result['failure_methods']) == EXPECTED_RED and result['errors'] ==0 and result['skipped'] ==0,
                        'Original did not fail exactly the preregistered semantic contracts; stop/reassess')
                require(result['reduced_alphabet'] == {'ordered_pairs':2592, 'mismatches':220, 'false_accepts':220, 'false_rejects':0},
                        'Original finite census differs from preregistration')
            else:
                require(completed.returncode ==0 and result['tests_run'] ==11 and result['failures'] ==0 and
                        result['errors'] ==0 and result['skipped'] ==0 and result['reduced_alphabet']['mismatches'] ==0,
                        'Candidate/crosscheck not conforming')
            result['observed_returncode'] = completed.returncode
            runs.append(result)
            print(name, 'rc=' + str(completed.returncode), 'science checked', flush=True)
    for mode in modes:
        pair = [record for record in runs if record['mode'] ==mode]
        ignored = {'elapsed_seconds', 'optimized_python'}
        require({k:v for k,v in pair[0].items() if k not in ignored} ==
                {k:v for k,v in pair[1].items() if k not in ignored}, 'Normal/-O result mismatch: ' + mode)
    unchanged = len(verify(args.source)['modules'])
    store(args.output / 'target_runs.json', runs)
    science = {'tested_main':manifest['commit'], 'target_contract_tests':11,
               'baseline_tests':{'failures':4, 'errors':0, 'same_under_optimization':True},
               'candidate_engine_tests':{'pass':11, 'same_under_optimization':True},
               'candidate_leaf_tests':{'pass':11, 'same_under_optimization':True},
               'modular_ast_extracted_tests':{'pass':11, 'same_under_optimization':True},
               'reduced_alphabet_ordered_pairs_each_target':2592,
               'baseline_false_accepts':220, 'baseline_false_rejects':0,
               'candidate_engine_leaf_modular_mismatches':[0,0,0],
               'mutants_detected_normal':8, 'mutants_detected_optimized':8,
               'verified_public_source_files_unchanged':unchanged,
               'no_frozen_source_edit_or_authority_certificate':True,
               'no_real_data_or_simulation_or_new_lean':True,
               'all_preregistered_acceptance_conditions_met':True}
    store(args.output / 'science_summary.json', science)
    record = {'science':science, 'python':sys.version, 'numpy':np.__version__,
              'elapsed_seconds':time.perf_counter() - start,
              'source_execution_scope':'Full engine import only; replacement of ONE comparison AST node for memory-only candidate; existing modular helper only AST-extracted. No engine dynamics/certification call.',
              'proposal_status':'LOCAL_NEW_FILE_PROPOSAL;NOT_INSTALLED_OR_AUTHORITY_APPROVED;NO_INDEPENDENT_REVIEW'}
    store(args.output / 'cycle_results.json', record)
    print(json.dumps(record, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--child', choices=MODES + ('mutants',))
    args = parser.parse_args()
    try:
        return child(args) if args.child else parent(args)
    except Exception as error:
        args.output.mkdir(parents=True, exist_ok=True)
        store(args.output / 'failure.json', {'type':type(error).__name__, 'message':str(error),
                                           'counts_as_semantic_rejection':False})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
```
<!-- END_CRITICAL_FILE: run_checks.py -->

### source_modules.json

<!-- BEGIN_CRITICAL_FILE: source_modules.json -->
```json
{
  "repo": "jacobbrainard84-knightninja/AIEFS",
  "commit": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "engine": "aief_experiment_engine_v1.py",
  "modular_validation": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/validation.py",
  "modules": [
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/validation.py",
      "blob": "9afffc1c0e3d1f8e0ad726e33d3b059e9337a1da",
      "bytes": 11178
    },
    {
      "path": "aief_experiment_engine_v1.py",
      "blob": "0d116e83a0d2f6b3f6be0e21d8a730c0aec3b689",
      "bytes": 119493
    }
  ],
  "scope": "Two public source files verified: full engine import; modular helper only AST-extracted. Original frozen engine never edited."
}
```
<!-- END_CRITICAL_FILE: source_modules.json -->

### fetch_public_dependencies.py

<!-- BEGIN_CRITICAL_FILE: fetch_public_dependencies.py -->
```python
"""Fetch the two reviewed public source files; no source execution/author API."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('upstream'))
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parent / 'source_modules.json').read_text())
    def fetch(record):
        relative = Path(record['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.suffix != '.py':
            raise ValueError('Unexpected public dependency path')
        target = args.output / relative
        if target.exists():
            data = target.read_bytes()
        else:
            url = ('https://raw.githubusercontent.com/' + manifest['repo'] + '/' + manifest['commit'] + '/' +
                   quote(record['path'], safe='/'))
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != record['blob'] or len(data) != record['bytes']:
            raise RuntimeError('Dependency differs from reviewed source: ' + record['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return str(relative)
    with ThreadPoolExecutor(max_workers=2) as pool:
        files = list(pool.map(fetch, manifest['modules']))
    print(json.dumps({'tested_main':manifest['commit'], 'public_sources_fetched_and_verified':len(files),
                      'source_executed_by_fetcher':False, 'raw_commit_author_metadata_requested':False}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: fetch_public_dependencies.py -->

### extract_from_report.py

<!-- BEGIN_CRITICAL_FILE: extract_from_report.py -->
```python
"""Extract the eight named critical007 files. Does not execute/fetch anything."""
import argparse
import json
from pathlib import Path
import re

NAMES = {'componentwise_exact.py', 'comparison_contract.py', 'load_reviewed.py',
         'test_comparison_contract.py', 'run_checks.py', 'source_modules.json',
         'fetch_public_dependencies.py', 'extract_from_report.py'}
PATTERN = re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                     r'<!-- END_CRITICAL_FILE: \1 -->', re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    pairs = PATTERN.findall(args.report.read_text())
    if len(pairs) !=len(NAMES) or {name for name, _ in pairs} !=NAMES:
        raise RuntimeError('Missing/duplicate/unexpected critical file')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, body in pairs:
        if Path(name).name !=name:
            raise RuntimeError('Unsafe extraction path')
        target = args.output / name
        text = body + '\n'
        if target.exists() and target.read_text() !=text:
            raise RuntimeError('Existing different file: ' + name)
        target.write_text(text)
    print(json.dumps({'critical_files_extracted':len(pairs), 'code_executed':False}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: extract_from_report.py -->


## AppendixB — actual original result record

```json
{
  "science": {
    "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
    "target_contract_tests": 11,
    "baseline_tests": {
      "failures": 4,
      "errors": 0,
      "same_under_optimization": true
    },
    "candidate_engine_tests": {
      "pass": 11,
      "same_under_optimization": true
    },
    "candidate_leaf_tests": {
      "pass": 11,
      "same_under_optimization": true
    },
    "modular_ast_extracted_tests": {
      "pass": 11,
      "same_under_optimization": true
    },
    "reduced_alphabet_ordered_pairs_each_target": 2592,
    "baseline_false_accepts": 220,
    "baseline_false_rejects": 0,
    "candidate_engine_leaf_modular_mismatches": [
      0,
      0,
      0
    ],
    "mutants_detected_normal": 8,
    "mutants_detected_optimized": 8,
    "verified_public_source_files_unchanged": 2,
    "no_frozen_source_edit_or_authority_certificate": true,
    "no_real_data_or_simulation_or_new_lean": true,
    "all_preregistered_acceptance_conditions_met": true
  },
  "python": "3.13.16 (main, Oct  6 2026, 04:38:44) [GCC 14.2.0]",
  "numpy": "2.3.5",
  "elapsed_seconds": 5.770836757999973,
  "source_execution_scope": "Full engine import only; replacement of ONE comparison AST node for memory-only candidate; existing modular helper only AST-extracted. No engine dynamics/certification call.",
  "proposal_status": "LOCAL_NEW_FILE_PROPOSAL;NOT_INSTALLED_OR_AUTHORITY_APPROVED;NO_INDEPENDENT_REVIEW"
}
```


## AppendixC — preregistration, integration boundary and decision

### PLAN.md

```text
# 007 preregistration — authority-safe complex-NaN comparator proposal

Researcher040282. Session preparation date2026-09-04, Atlantic/Reykjavik.
Prior owner/seat/repository date labels are preserved, not reconstructed execution
dates. No inference from runtime clocks/compiler build strings. No RNG planned.

## Fresh source and nonduplication, before acquired-code execution

Read-only main: eb3933c196ee19e80e1621ae80d89ca72e6d9485,10 selected files.
Read-only inbox: e72bdd2b2c29d815740c321df0ad8703de378e37,6 selected notes.
All six selected notes unchanged from previously read intake/triage; no005/006/007
named follow-up located in this bounded navigation. Inbox tip changed; main did
not. Do not claim an exhaustive private-feedback search or latest-packet receipt.

B-F6 is KNOWN and R001 previously reproduced it. This is a repair proposal, not
novel discovery or a repeated real-array finiteness census. Static source shows:
- engine exact_array_equal_with_nan:1755–1768 uses whole-complex np.isnan;
- modular validation.exact_equal_with_nan:263–279 already splits components;
- registry/artifacts.csv ART-0702 marks engine Frozen and authority-locked.
The frozen engine WILL NOT be rewritten. No new oracle-uniqueness repair, uploader
work, full S01, simulation, real trajectory, CLI validation certificate or Lean
compilation is part of007.

## One proposed change and permissible test vehicle

Deliver a small NEW standalone componentwise comparison helper with the engine's
public function name/signature. For controlled tests only, parse a fresh complete
engine source into an AST, replace that ONE top-level function with the proposed
function, and execute it in a distinctly named, memory-only candidate module.
Require all other AST nodes identical; label candidate __file__ as synthetic,
not the original authority path. Do not claim an authority-lock pass from it.
No patched frozen path, automatic installation, disk patch or registry mutation.
Owner/seat must decide an authorized successor/verification-companion route.

Test full original engine helper, this full-engine comparison-only memory
candidate, the standalone leaf helper, and AST-EXTRACTED existing modular helper.
The modular package is not imported/validated; its existing method is a crosscheck,
not the independent expected-answer oracle. Two public Python sources suffice.
None of the simulation/validate_frozen_run/real-run entry points will be called.

## Contract and independent oracle, before tests

1. Convert inputs with np.asarray as existing helper does. Same shape and SAME
   NumPy dtype-equality policy required. No broadcasting, flattening away shape,
   implicit dtype conversion or approximate numeric acceptance.
2. For float values, corresponding NaNs match; otherwise scalar equality exactly.
   For complex values, apply that rule INDEPENDENTLY to real/imaginary parts.
   Infinities match only identical sign; signed zeros compare equal as in existing
   np.array_equal. NaN payload/sign bits are ignored by this value-level policy.
   “Exact” is NOT whole-buffer bit identity.
3. Preserve noncomplex fallback behavior on tested bool/integer/string arrays;
   do not introduce a new object/datetime/structured dtype policy on this branch.
4. No input shape/dtype/strides/writeability/visible bytes or explicitly tracked
   backing buffers may change. Expected answers/snapshots are obtained BEFORE the
   target call; reject input mutation even if the returned answer is correct.
5. Independent spec: check shape/dtype, then loop scalar components in Python with
   math.isnan and ==. No candidate helper call, complex-wide np.isnan, array_equal,
   allclose or returned candidate answer is used to obtain expected truth.

All acceptance comparisons are EXACT, atol=rtol=0. An allclose mutant may use
nonzero tolerances solely as an intentionally wrong model. No tolerance tuning.
Supported test domain: bool/int/uint, float16/32/64, complex64/128, fixed strings,
NumPy arrays/scalars and immutable Python numeric scalars. Arbitrary object,
datetime/structured dtype dispatch, platform long-double formats and arbitrary
code security are NOT established.

## Fixed tests and falsifiers

Same11 unittest contracts on each target:
1. NaN real must not hide a changed finite imaginary component.
2. NaN imaginary must not hide a changed finite real component.
3. Real-versus-imaginary NaN positions must match componentwise.
4. Exhaust component alphabet {NaN,-Inf,-1,0,1,+Inf} on each component:36 complex
   values,1296 ordered pairs, each at complex64 and complex128 =2592 scalar pairs.
   Independently predict220 original false accepts,0 false rejects; record actual
   counts. This is exhaustive only for this reduced alphabet, not all floats.
5. Real exactness, NaN pattern, finite neighbors/subnormal and Inf distinctions.
6. Finite complex neighbors, Inf sign, signed-zero equality and differing NaN
   payloads with matching other components.
7. Shape and dtype guards including equal-looking values of different dtype.
8. Empty/scalar cases, including empty dimensions and0-D.
9. Noncontiguous, transposed, reversed, read-only views; tracked backing buffers.
10. Bool/integer/string fallback (including neighboring integers above2^53).
11. Input preservation on matching numeric arrays.

Expect original to fail precisely contracts1–4 (4 failures,0 errors), while its
other contracts pass. Candidate-engine, standalone leaf and modular-extracted
helper should pass all11. Run each target normally and with python -O; unittest
method calls and explicit exceptions must not disappear as Python assert does.
If source behavior is already corrected or another unexpected failure occurs,
keep the observation and stop/reassess rather than manufacturing an old defect.

Eight distinct wrong models, with predetermined mechanism-specific witnesses:
whole-complex missingness; real-only; imaginary-only; allclose instead of exact;
ignore dtype; ignore shape; never match NaNs; mutate requested input before
comparison. Each must raise owned ContractMismatch for the intended truth/input-
preservation reason. Import/dependency errors and unrelated exceptions are NOT
successful detections. Repeat this sensitivity check under optimization.

## Evidence/closeout

Save original red/green/optimized logs, complete reduced-alphabet mismatch census,
semantic witnesses, manifest, AST replacement boundary and source byte-preservation
records. No present/past real certificate corruption or saved-array impact claim.
Existing engine max-difference diagnostics are outside the predicate-only proposal;
they still use whole-element masks and are NOT certified by this change.

Standalone numbered Markdown: full critical code, essential actual outputs,
reproduction instructions and owner/seat request inline. Extract the note into
a fresh directory, fetch2 reviewed public Python sources, execute the full runner
(including optimized targets and mutants), compare scientific results. Preserve
all prior111 ledger rows/94 formal labels and completed006 state; update new
state/queue only from actual outcomes. Personal metadata omitted at acquisition;
logs cited unpacked/indexed. No contact, remote push/PR, automatic upload or
unattended work. No code acquisition is itself an independent-seat approval.
```

### proposal/INTEGRATION_NOTE.md

```text
# Proposed007 comparison helper — owner/seat integration decision required

One finding only: B-F6, the already-known engine complex-NaN false-equality
mechanism. Reuse the existing modular helper's component split, retaining the
engine function's shape/dtype/real/fallback behavior. No new algorithm/novelty or
saved-data impact is claimed.

**Do not edit or replace `aief_experiment_engine_v1.py` in place.** On tested main
it is ART-0702, Frozen and authority-locked (`registry/artifacts.csv:703`).
Do not update/disable a lock to make this proposal pass. Importing
`componentwise_exact.py` installs/patches nothing.

Permissible future routes, after explicit owner/seat review:

1. A NEW verification companion that calls this predicate at a clearly documented
   comparison boundary, with its own provenance and authority status; or
2. An authorized NEW engine successor whose comparison function uses this code,
   with explicit erratum/registry/lock handling and independently reviewed tests.

This packet chooses neither authority route and does not produce a production
patch, frozen-run certificate or approved successor. Do not silently monkeypatch
an already-authority-labelled live run and describe it as the frozen engine.

The test-only `candidate-engine` mode compiles the reviewed full engine AST after
replacing just its comparison function. The other98 top-level nodes are preserved;
its name and `__file__` identify a **memory-only, non-authority candidate**. Only
its comparison predicate is called; `run_baseline_equivalence`, simulations and
lock validation are NOT run. This is a controlled failing-before/passing-after
vehicle, not a reusable certified engine artifact.

The direct leaf and existing modular AST-extracted helper are tested against the
SAME independent scalar-component specification. The full modular package is not
imported or certified. Noncomplex fallback remains unchanged; no object/datetime/
structured-dtype policy is introduced. Exact value equality is not byte identity:
signed zeros match and matching NaN payload/sign bits are ignored.

**Unchanged limits:** engine max-difference diagnostics at2441–2443,2503–2505 and
2539–2541 still apply whole-element missingness masks; no component-resolved error
report is supplied/approved here. No full equivalence-validation pipeline, array
census, real trajectory or production result is changed or rechecked. Four red
contract methods and220 reduced-alphabet false accepts are synthetic checks, not
four new bugs or220 affected production records.

Request: Researcher001/AuditorSeat002 independently review the new helper,
pre-call oracle/input-preservation checks, exact dtype/shape policy, arbitrary-
shape and partial-NaN/Inf/ULP counterexamples. Choose an authorized integration
route and any needed diagnostics before using it for a citable certificate.
Keep any oracle-uniqueness change on a separate branch. Owner uploads this note;
no remote push/PR/contact/upload has been performed by Researcher040282.
```

### review_decision.json

```json
{
  "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "disposition": "REPAIR_PROPOSAL_FINITE_CONTRACTS_PASS;NOT_INSTALLED_OR_AUTHORITY_APPROVED",
  "known_issue": "B-F6 already independently reproduced by R001; modular helper already uses this mechanism. No novelty claim.",
  "target": "aief_experiment_engine_v1.py:1755-1768",
  "frozen_authority_route": "ART-0702 frozen engine unchanged; new helper only; owner/seat selects new verification companion or authorized successor/erratum route",
  "source_code_execution_scope": "Original full engine module imported; candidate full engine AST changes one predicate only; existing modular helper AST-extracted, no full modular import",
  "test_only_replacement_boundary": {
    "function_nodes_replaced": 1,
    "other_top_level_nodes_preserved": 98,
    "candidate_file_identity": "synthetic memory-only; not the original authority path"
  },
  "normal_optimized_science_agree": true,
  "source_frozen_bytes_unchanged": true,
  "oracle": "pre-call scalar Python component loop with math.isnan and exact equality, not candidate output",
  "not_approved": [
    "any edit of frozen source, lock/registry update or production installation",
    "full run_baseline_equivalence, simulations or frozen-run certificate",
    "actual saved-array finiteness, data corruption or production false-certificate claim",
    "all NumPy/platform/dtype correctness or arbitrary-code security",
    "existing max-difference diagnostic masks",
    "new007 independent-seat approval or any coupled-dynamics/Lean result"
  ],
  "next_review_actions": [
    "independently review source/oracle/mutants, including component locations, Inf, one ULP, dtype/shape and input preservation",
    "select authorized new-file companion/successor and applicable erratum handling; never silently override frozen authority",
    "separately decide component-resolved diagnostics and actual pipeline acceptance before citable certification"
  ],
  "current_cycle_external_review_received": false,
  "remote_write_contact_or_upload": false
}
```

### historical_restoration.json

```json
{
  "initial_packet_preflight_returncode": 1,
  "initial_failure_reason": "Previously delivered workflow snapshot absent unpacked; existing prior NONLIVE evidence-file bytes all unchanged",
  "missing_member_restored": "researcher_040282/cycle_006/source_state/main/.github/workflows/repo-checks.yml",
  "restored_from": "researcher040282-cycle006-v41-contract-review.zip",
  "restored_bytes": 9175,
  "restored_content_matches_delivered_member": true,
  "scientific007_inputs_code_results_changed": false,
  "scope": "Administrative missing-file restoration only; not a new finding, source patch, run, date reconstruction or independent review",
  "previously_existing_prior_nonlive_members_changed": 0,
  "existing_source_or_log_overwritten": false,
  "scientific_or_historical_program_executed_during_restoration": false
}
```

