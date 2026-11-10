# 008 preregistration — condition-key multiplicity in the public oracle

Researcher040282; session preparation2026-09-04, Atlantic/Reykjavik. Prior owner/
repository date labels are not inferred execution timestamps. Deterministic tests;
no RNG or change to old seeds. This plan precedes all acquired-code execution.

## Source, coordination and one finding

Fresh main eb3933c196ee19e80e1621ae80d89ca72e6d9485. Inbox
fef8b0262c31cbdd23f9668a55fffb43b2dc1002. Initially11 main/6 selected inbox files;
static package import acquisition now19 main selections/12 Python source modules.
No acquired code imported during acquisition. Six selected notes: intake/targeted
R001 note unchanged; general TRIAGE updated with other agents' static reviews.
No005–008 named follow-up found. Public open-PR list empty;15 public branch names
seen, none matching oracle/duplicate/uniqueness. Limited public navigation only.

B-F7 is KNOWN: R001 previously reproduced the public3-vs2 toy mechanism, not the
real201-vs200 S01 witness. Main oracle.py still turns condition rows into sets.
runner.py:385–398,664–699 writes one status row per condition with seed/rho/status.
Natural condition identity is (seed text, float(rho)); status is a VALUE, not part
of identity. Scalar/NPZ content, elapsed/error metadata and whole-study validity
are separate questions. No renewed uploader/bridge/engine repair in this branch.

ART-0076 (current oracle.py) is Supported, lock_status=none. Proposal may be a
normal one-function review-branch change, but no live upstream/source-cache edit,
registry update, PR or installation is authorized. Frozen engine/real artifacts
stay unchanged. Deliver a complete separate oracle_candidate.py, derived from
current source with only _compare_condition_coverage replaced; all other AST
nodes and public entry point remain unchanged. Import ACTUAL package/oracle and
candidate module, call actual compare_twindow_run; do not mock its CSV/NPZ stages.
No runner/simulation, real NPZ, baseline certificate or Lean build.

## Declared contract, before tests

Required status columns seed,rho,status. Seed is exact text, unchanged from
current API (do not coerce numeric-looking seeds). Rho normalization is the
EXISTING Python float parsing/equality policy, not raw text and not a tolerance.
Require finite parsed rho to make semantic keys well-defined; malformed/nonfinite
rho produces explicit failed comparison on either side. Positivity, full cohort,
200-condition design and all status-file metadata are not newly validated here.

For each side, each normalized (seed,rho) key must appear exactly once, even if
repeated rows have different statuses. Enforce row-count equality explicitly;
compare coverage/status values as before. Order of condition rows is irrelevant;
numeric rho spellings that parse to the same float remain equivalent. Missing/
changed coverage/status, schema failure, duplicates on either side or row-count
mismatch must reject. Both header-only status tables retain prior logical-empty
behavior: not a real-study certificate. Elapsed/error auxiliary metadata remains
ignored; scalar CSV and NPZ comparison logic must stay unchanged and active.
No numeric comparison tolerance is changed (exact).

Independent oracle: from IMMUTABLE original row tuples/header declarations,
normalize keys by the declared float policy, check finiteness, use nested PAIRWISE
comparisons for uniqueness and matching key/status values. Do not call candidate,
_read_csv, set/Counter validation or returned source answers for expected truth.
Expected answer and snapshots of all six toy input files precede target call;
reject any input rewrite, even if the target returns the now-matching answer.

## Same12 common contracts, normal and -O

1 Unique nontrivial six-condition match.
2 Reordered condition rows and numeric rho aliases still match (seed stays text).
3 Candidate-only exact duplicate appended rejects.
4 Oracle-only duplicate appended rejects.
5 Equal row counts with matching duplicates on both sides reject (count alone is insufficient).
6 Matching tables with conflicting statuses at ONE key reject (status is not key).
7 Missing/changed seed/rho/status, duplicate replacing another key, required column
  loss and text-seed distinction reject; do not mistake them for new findings.
8 Existing scalar CSV value/branch/column gates still reject corruption.
9 Existing NPZ value/dtype/shape/key/partial-NaN-component gates still reject.
10 Auxiliary condition metadata ignored and logical-empty comparison preserved.
11 Returned scalar/NPZ/condition counts accurate, files unchanged on valid cases.
12 Numeric-alias duplicates reject under normalized key identity.

Expect original exactly5 failing methods (3,4,5,6,12),0 errors; candidate all12
pass. Invalid/malformed rho is outside the original well-formed common domain:
add candidate-only validation for NaN,Inf,-Inf,not-numeric,empty rho on each side
(10 cases). Do not count original parse exceptions as semantic red success.

## Exhaustive small-table census, also public API

Alphabet A=(s0,.5,success), B=(s1,1,success), C=(s0,.5,failed).
All ordered sequences length0..3:40 per side;1600 ordered table pairs. Every pair
runs actual public API with nontrivial matching scalar CSV (2 rows) and NPZ
(2 entries), not only the private condition helper. Independent contract predicts
12 accepted pairings: empty1; three singleton self-pairs3; permutations of AB and
BC give4 each. Current set-based source predicts256 accepted pairings:1 +3*3^2
+3*8^2 +6^2. Thus244 false accepts,0 false rejects. Record actual mismatches;
this finite alphabet is not all CSVs, all real runs or affected production records.
Write/reuse small temporary toy bundles, then remove them; persist complete census
results/witnesses, not1600 redundant copies of NPZ files.

## Distinct wrong-model controls

Require intended ContractMismatch for: original set collapse; count+set only;
uniqueness of (seed,rho,status) instead of condition key; order-sensitive status
comparison; raw-rho-text identity; ignoring status; bypassing the existing NPZ
gate; mutating/deduplicating requested CSV before comparison. Same8 controls in
normal and optimized workers. Only truth/input-preservation/count failures count;
import/setup/unrelated exceptions block, never count as semantic detections.
No false claim that removing redundant guards is detectable from status alone.

## Closeout

All12 reviewed public source modules unchanged before/after. Only one candidate
function AST differs; public API/other validators untouched. Return1 original red
runs expected only for exactly the intended failures; return0 candidate/control
workers and whole runner only when preregistered outcomes observed. No Python
assert acceptance that disappears under -O. No original control weaken/tolerance
change after observing results.

Standalone numbered Markdown with full critical files and essential actual output;
extract to fresh dir, fetch12 reviewed public dependencies and repeat entire
normal/-O runner, compare science and non-timing worker/census records. Preserve
prior112 ledger rows/94 formal labels and completed007 state; one bounded new
proposal record. Metadata minimal, cited logs unpacked/indexed. Do not restore
user-deleted Lua audit. No contact/push/PR/upload, frozen edit or unattended work.

Fresh triage also confirms v4.1 self-supplied-manifest trust-root risk but no
runtime false-accept reproduction; proposed next009 is an isolated boundary
negative control after fresh source/feedback, not a second finding in008.
Do NOT duplicate the existing rate-law delta sweep on the reported research
branch. No documentation cleanup duplicates of the Chronicler deposit.
