# 009 integration boundary — externally anchored admission companion only

Known GPT6-P1. Fresh feedback reports a colleague's copied-function full-schema
negative control; do not claim novelty or duplicate its downstream calculations.
This proposal's new evidence uses actual full-module discover_inputs/validate_run,
not copied/AST-extracted/mocked validators, and independently generated toy data.

The guard requires the CALLER to supply an independently trusted manifest digest.
It pins exact root bytes BEFORE unchanged validate_run is called, delegates all
existing child-hash/schema checks, returns the same object and post-checks the
manifest as a persistent-change tripwire. Trusted roots/unchanged inputs/hash
binding are explicit assumptions. A hash is not its own trust source; bad caller
policy remains bad policy. Invalid anchor configuration is a separate error.
No certificate schema, NPZ validator, baseline engine or estimand fix is bundled.

For an S01-only policy the owner must choose the independently trusted ART-2217
manifest record or an approved immutable authority profile, NOT read an expected
value from the input directory or self-declared field. The acquired committed
manifest matches that inventory entry in a metadata-only check. No full genuine
five-file S01 validation was run; all validation positives here are TEST-owned
synthetic authorities, not permission to certify toy values or future runs.

Example for an independently selected/approved anchor:

    validated = validate_anchored(
        reviewed_module.discover_inputs(run_dir),
        expected_manifest_sha256=independently_trusted_anchor,
        validate_run=reviewed_module.validate_run,
    )

This is NOT wired into current run_analysis/CLI. Do not run an isolated preflight
then invoke unchanged CLI and call that an installed or race-safe repair. A future
authorized integration must thread the guarded admission/result through the actual
analysis boundary and decide immutable-input/read-once handling, real-S01 positive
validation, baseline/lineage policy and independent review. None was changed here.
Keep unaudited warnings/default CLI refusal. Frozen Analysis v4, ART-0702 engine,
ART-0050 bridge, registry/locks and all acquired source bytes remain untouched.

Observed each normal/-O: original4/9method failures/0errors and7unanchored accepts
among18declared cases relative to proposed policy; guard9pass,7early root rejects,
8old hash/schema rejects preserved,3synthetic positives.8wrong models detected,
including after-only admission_order and input rewrite;4configuration errors
separate. Complete toy NPZ2600keys independently inspected, but validate_run
itself only hashes NPZ. No full analysis/real outputs/CLI or colleague code run.

Owner/seat request: accept/revise the exact admission contract and external trust
source, independently reproduce the note, review controls and select an authorized
new companion/integration route. This agent made no PR/push/contact/upload or
installation. Prior94 compilations do not approve009 or other new proposals.
