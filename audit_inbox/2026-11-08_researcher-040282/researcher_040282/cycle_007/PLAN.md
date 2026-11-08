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
