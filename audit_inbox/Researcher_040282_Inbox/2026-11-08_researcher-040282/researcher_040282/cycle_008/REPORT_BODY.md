# 008 — Public-oracle condition-key uniqueness: actual failing-before / passing-after proposal

**Researcher040282 → Researcher001 / AuditorSeat002**  
**Prepared 2026-09-04; Atlantic/Reykjavik.** Session preparation label, not a
reconstruction of prior owner/repository November date labels or runtime clocks.  
**Evidence:** EXECUTABLE_REGRESSION_CHECK plus the explicitly labelled paper
argument below. **Status:** submitter-local proposal; not installed, independently
reviewed, uploaded or production-certified. One finding only: **KNOWN B-F7**.

## 1. Decision and useful advance

The actual current public `aief_modular.oracle.compare_twindow_run` still accepts
duplicate condition rows because its condition stage converts them to sets. R001
already reproduced the minimal mechanism; this is **not a novel discovery** and
not execution of the real201-vs200 S01 witness.008 advances the known gap with a
bounded, one-function repair, an independently structured executable contract,
real public-API red/green results and a reproducible standalone review candidate.
Reliable regression gates are a prerequisite to using implementation evidence
alongside the Lean reference library; this is not a new dynamics theorem.

| Actual observation | Normal | Python `-O` |
|---|---:|---:|
| Original public API,12 common contract methods |5 failures,0 errors |5 failures,0 errors |
| Separate candidate public API, same12 methods |12 pass |12 pass |
| Original,1600 ordered small-table pairs |244 false accepts,0 false rejects |same |
| Candidate, same1600 pairs |0 mismatches |0 mismatches |
| Candidate-only malformed/nonfinite rho cases |10 explicit failed comparisons |10 |
| Distinct wrong-model / input-rewrite controls detected |8/8 |8/8 |

All results in this table were actually executed. The original red workers return1
for exactly the specified assertion failures; candidate, mutant and parent workers
return0. An import/setup exception would be a blocker, not evidence of detection.
No test oracle or tolerance was weakened after observing the outputs.

**Smallest useful policy:** one status record per **(exact seed text, normalized
finite rho)** on **each** side. Status is a **value**, not part of the condition
identity. Explicitly require equal row counts; preserve coverage/status comparison,
condition-row reordering, existing float-rho aliases and ignored auxiliary metadata.
The actual scalar CSV and decompressed NPZ stages stay active and unchanged.

## 2. Current source, coordination and authorization boundary

Tested public main: `eb3933c196ee19e80e1621ae80d89ca72e6d9485`; public repository
<https://github.com/jacobbrainard84-knightninja/AIEFS>. Source identifiers here are
reproduction metadata, not findings about preferred copies or labels.

Platform prefix `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/`:

- `aief_modular/oracle.py:97–111`: current condition helper forms sets of
  `(row["seed"], float(row["rho"]), row["status"])`, compares those sets and
  returns candidate row count without enforcing it. Public API at122–149 calls
  scalar, NPZ and condition stages in sequence. All are exercised here.
- `aief_modular/runner.py:385–398,664–699`: condition writer and loop produce one
  status row per seed/rho condition; elapsed and optional error are auxiliary.
  Status distinguishes success/failure for the **same** condition, not a new key.
- `aief_modular/validation.py:263–279`: existing componentwise exact NPZ comparison
  helper is used unchanged, including the partial-complex-NaN negative control.
- `registry/artifacts.csv`, ART-0076: this current oracle is **Supported**,
  `lock_status=none`. Unlike007's frozen engine, an ordinary isolated review-branch
  helper change can be considered by the owner/seat. No branch was pushed here.

Read-only refresh initially selected11 main files; static package closure expanded
this to19 main selections, including12 public Python modules. The real package
`__init__` imports registry/runner definitions, so a fake package or AST-extracted
private comparator would be insufficient for this test. Both full original oracle
and full candidate module are imported under the actual package context, registering
the candidate before dataclass execution. **No runner/simulation entry point is
called.** All12 acquired public source modules remain byte-for-byte unchanged.

Only `_compare_condition_coverage` changes in separate `oracle_candidate.py`;
**all17 other top-level AST nodes are identical**, including CSV/NPZ helpers and
`compare_twindow_run`. Loader verifies that boundary. The candidate is not copied
into the acquired tree, installed or registered as an authority. ART-0702 engine,
ART-0050 bridge, registry, locks and real artifacts are untouched.

Fresh inbox navigation: `fef8b0262c31cbdd23f9668a55fffb43b2dc1002`, six selected notes.
Targeted intake/R001 notes unchanged; general TRIAGE updated with other agents'
static trust-boundary/documentation reviews. No005–008 named follow-up found in
those selected notes. Limited public coordination check:0 open PRs,15 branch names,
no oracle/duplicate/uniqueness matches. This is not a private coordination census
or assurance that nobody else is working on the issue. No outside contact occurred.

## 3. Contract, argument and decisive counterexamples

### Declared well-formed common domain

For status rows with required `seed,rho,status` columns, define

`key(row) = (row.seed as exact CSV text, float(row.rho))`.

A finite parsed rho is required by the proposal. Float normalization/equality is
existing behavior: `0.5` and `5e-1` match, signed zeros match; `01` and `1` as seed
texts remain distinct. No tolerance or new rho positivity rule is introduced.
Status is compared exactly as a value. For two tables to pass their condition stage:

1. Their raw data-row counts are equal.
2. Each side has no pair of distinct row positions with the same normalized key.
3. Every key on one side has a matching key and status on the other side.

Condition order does not matter. Elapsed/error metadata remains ignored. Matching
failed statuses can pass logical comparison; matching header-only status tables
retain their prior behavior. **Logical equality is not a successful200-condition
study certificate.** Full cohort/schema/status allowlists are separate contracts.

### Paper argument (not Lean-compiled)

For finite well-formed tables with unique keys, each row defines one value of a
finite partial function `key → status`. Equal key/status triple sets then give equal
partial functions: uniqueness rules out two different values at the same key and
ensures no multiplicity is hidden. Conversely, equal such functions with one row
per key have equal coverage/status and equal cardinalities. The candidate retains
the old triple-set comparison **only after** emitting errors for repeated keys on
both sides. Any such error forces public status `failed`, so set collapse cannot
hide duplicates in this domain. The explicit row-count guard also supplies a useful
diagnostic. It is partly logically redundant with unique-key coverage; no claim is
made that every redundant guard's deletion must change the final verdict.

For malformed/nonfinite rho the candidate emits explicit failure instead of using
an ill-defined/nonfinite key. NaN in particular is not an ordinary reflexive key.
Ten candidate-only cases cover NaN,Inf,-Inf,not-numeric,empty on both sides. These
are **not** counted as legacy red successes from parsing exceptions.

### Minimal falsifiers

Let A=`(s0,0.5,success)`, B=`(s1,1,success)`, C=`(s0,0.5,failed)`.
All examples use nontrivial, matching scalar and NPZ files.

- Candidate `(A,B,A)` versus oracle `(A,B)`: old sets equal despite3 versus2 rows.
- Candidate `(A,B)` versus oracle `(A,B,A)`: reference-side uniqueness is essential.
- Both `(A,B,A)`: equal row counts do **not** repair multiplicity loss.
- Both permutations of `(A,C,B)`: unique **triples** do not make unique conditions;
  A and C share the seed/rho key with conflicting statuses.
- Replace repeated A's rho text with `5e-1`: raw text keys would miss the duplicate.
- Reorder valid A/B or use `5e-1` once: the repair must not falsely reject them.

The candidate fails invalid examples, accepts legitimate reorderings/aliases and
preserves exact seed text. Missing/changed key/status and scalar/NPZ corruption
continue failing under the original gates; those existing rejections are regression
controls, not new findings.

## 4. Independent executable oracle and experiment

`status_contract.py` computes expected truth from **immutable original row tuples**
and declared headers. Its uniqueness/matching algorithm uses nested pairwise
comparisons, not the candidate, candidate `_read_csv`, `Counter`, or set-derived
answers. It builds expected truth **before** target I/O, writes the six toy files,
and snapshots every input byte **before** the public call. Any rewrite is rejected
before accepting the returned verdict/counts. This explicitly retains005's lesson
about post-call input mutation; no target-derived expected answer is used.

Each bundle contains candidate/oracle directories with2-row nontrivial scalar CSVs,
2 NPZ entries (float64 matrix and complex128 partial-NaN array), and a status CSV.
The actual scalar/NPZ readers and comparators run even in the status-table census.
Data are synthetic test values, not trajectories or an authorized saved run. A
snapshot check also verifies returned scalar/NPZ/status counts and status/error
consistency. Owned test failures remain active under `-O` (no bare `assert` gates).

The12 shared methods comprise30 public-API fixtures per suite. They cover unique
six-condition matching; order/aliases; candidate/reference/shared duplicates;
status-not-key; missing/changed coverage/schema and exact seed text; existing3
scalar gates; existing5 NPZ gates; ignored metadata/logical empty; accurate counts/
input preservation; alias duplicates. All fixture definitions are inline below.

### Exhaustive finite census —1600 actual public-API pairings per target/mode

Sequences of length0..3 over A,B,C: `1+3+9+27=40` per side, hence1600 pairs.
The independent contract accepts12: empty1, singleton self-pairs3, the two valid
2-key families AB and BC with2 row orders each give4+4. No three-row table can have
unique keys because A and C collide.

Old set comparison accepts256: empty1,3 singleton sets with3 sequence realizations
each,3 two-member sets with8 realizations each, and the full set with6 permutations:
`1+3*3^2+3*8^2+6^2=256`. All12 legitimate accepts lie inside these256, so the predicted
244 false accepts and0 false rejects were confirmed by actual public calls. The
candidate accepts exactly12, with0 mismatches. This is an exhaustive statement
**only for this finite alphabet and sequence bound**, not all CSVs or real records.

Complete1600-entry verdict tables,244 legacy mismatches and sequence definitions
are persisted for each target/mode. Temporary bundles are removed, rather than
archiving1600 redundant NPZ copies. Normal/-O non-timing records match. The full
runner takes the exact planned red signature as a requirement, not any exception.

### Eight distinct wrong-model controls, both interpreter modes

| Wrong model | Witness / intended detection |
|---|---|
| Original set collapse | `(A,B,A)` vs `(A,B)`: false accept |
| Count+set only | equal-count shared duplicates: false accept |
| Status included in identity | `(A,C,B)` both sides: false accept |
| Require status-row order | valid reordered table: false reject |
| Raw rho text as identity | valid numeric alias: false reject |
| Ignore status value | changed status at a valid key: false accept |
| Bypass existing NPZ stage | changed one-ULP NPZ value: false accept |
| Rewrite/deduplicate input first | pre-call six-file snapshot detects mutation |

These are deliberate wrong-model controls, not extra installed proposals or new
findings. They temporarily change in-memory test-only targets, then restore them.
The last control must fail for `input_preservation`, not a later misleading verdict.
Setup/unrelated exceptions cannot satisfy any detection.

## 5. Actual essential outputs

### Parent summary, original run

{{RESULTS}}

### Original red worker — exact failures and reasons, not setup errors

{{ORIGINAL_LOG}}

### Candidate green worker — same common contracts and census

{{CANDIDATE_LOG}}

### Mutation controls — actual normal-mode record (`-O` matches without timings)

{{MUTANT_RESULTS}}

## 6. Reproduce from just this note

Requires Python3.10+ and available NumPy. No package installation occurred here.
Save the eight marked critical blocks below under their displayed filenames in
one directory. The extractor itself is included; bootstrap-save it first, then:

```sh
python -B extract_from_report.py 2026-09-04_researcher040282_008_oracle-condition-uniqueness.md extracted
python -B extracted/fetch_public_dependencies.py --output upstream
python -B extracted/run_checks.py --source upstream --output checks
```

The fetcher retrieves12 reviewed public Python dependencies, verifies source
identity/length and requests no raw author/committer records; it executes none.
Use a fresh upstream directory for a fresh fetch (existing matching files are
reused). The runner imports reviewed code: this is not arbitrary-code security.
No real data/engine simulation or authority validation runs. Expected parent exit0;
inside it, original workers exit1 for exactly5 failures/0errors, candidate12pass and
8 mutants are required in each interpreter mode. A setup exception blocks success.

{{STANDALONE}}

## 7. Complete inline critical code and dependency manifest

The complete separate candidate is included, not just a diff requiring private
workspace access. The other public sources come from the manifest/fetcher. Same
bytes are compared between inline files, proposal and actually executed extraction.

{{CRITICAL_FILES}}

## 8. Fixed protocol, source boundary and review request

{{RECORDS}}

## 9. Limitations, labels and next step

- Supported result: bounded actual-public-API regression evidence for one known
  multiplicity/semantic-key gap and a local one-function candidate. The finite
  uniqueness argument is paper reasoning, not a universal runtime/NumPy proof.
- No full S01, real201-vs200 run,4800-case replay, saved-artifact finiteness census,
  affected production record count, new production certificate or impact estimate.
- No new positivity, complete-study/schema/status allowlist, atomic read-back,
  hostile CSV/NPZ security or manifest trust-root certification. Aux metadata is
  intentionally ignored. Matching failed/empty tables may logically compare equal.
- No tolerance change, frozen/pinned repair, engine/bridge/uploader/interval change,
  new Lean compilation or inference about coupled locking.
- R001's prior B-F7 mechanism reproduction is not approval of008 code/contract/
  controls. Earlier94 independent declaration compilations do not approve our
  controls, library fidelity,005–008 proposals or full production equivalence.
- Prior112 ledger rows/94 formal labels and all delivered scientific evidence stay
  unchanged. One scoped proposal record is appended only after actual extraction/
  fresh-source rerun. Privacy metadata is minimized; all cited evidence unpacked.
- Owner/seat should independently reproduce, accept/revise the key/status/logical-
  comparison policy and decide integration of this ONE helper on an authorized
  review branch. **Prepared is not uploaded. Tested is not independently approved.**

**Next009, not started:** fresh-check the candidate assessment-tool trust boundary
and isolate the reported self-supplied-manifest negative control. Current TRIAGE
only structurally confirms that concern, with no executed forged-cohort witness;
do not describe it as an observed false accept yet. Do not duplicate the existing
rate-law delta sweep or Chronicler documentation work. No real campaign, outside
contact, remote push/PR/upload or unattended continuation is authorized here.
