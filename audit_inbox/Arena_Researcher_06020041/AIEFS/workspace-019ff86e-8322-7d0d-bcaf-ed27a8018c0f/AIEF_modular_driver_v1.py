#!/usr/bin/env python3
"""AIEF Modular Experiment Driver Platform v1 command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aief_modular.catalog import rebuild_catalog
from aief_modular.registry import REGISTRY, load_builtin_studies
from aief_modular.runner import dry_run, execute
from aief_modular.spec import canonical_data, canonical_json, spec_sha256
from aief_modular.validation import (
    AIEFModularError,
    ArtifactIntegrityError,
    BaselineGateError,
    CatalogError,
    ConditionSchemaError,
    SpecValidationError,
    UnsupportedPolicyError,
)


def _add_authority_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("study_id", help="registered study ID")
    parser.add_argument("--frozen-manifest", required=True)
    parser.add_argument("--frozen-npz", required=True)
    parser.add_argument("--frozen-scalar", required=True)
    parser.add_argument("--output-root", default="experiments")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="unsupported in v1; produces a clear failure",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-studies", help="list trusted registered studies")

    describe = subparsers.add_parser("describe", help="print canonical study specification")
    describe.add_argument("study_id")

    dry = subparsers.add_parser("dry-run", help="validate without creating output")
    dry.add_argument("study_id")

    baseline = subparsers.add_parser("baseline-only", help="run mandatory frozen baseline gate only")
    _add_authority_arguments(baseline)

    run = subparsers.add_parser("run", help="run baseline gate and complete production grid")
    _add_authority_arguments(run)

    catalog = subparsers.add_parser("catalog", help="rebuild non-authoritative catalog")
    catalog.add_argument("--output-root", default="experiments")
    catalog.add_argument(
        "--replace-catalog",
        action="store_true",
        help="explicitly replace existing derived catalog files",
    )
    return parser


def _registration(study_id: str):
    try:
        return REGISTRY.get(study_id)
    except KeyError as exc:
        raise SpecValidationError(str(exc)) from exc


def _list_studies() -> None:
    for entry in REGISTRY.entries():
        print(
            "\t".join(
                (
                    entry.study_id,
                    entry.slug,
                    entry.version,
                    entry.title,
                    entry.source_module,
                )
            )
        )


def _describe(study_id: str) -> None:
    spec = _registration(study_id).build()
    output = {
        "canonical_spec": canonical_data(spec),
        "spec_sha256": spec_sha256(spec),
        "expected_counts": {
            "seeds": spec.seed_design.count,
            "conditions": spec.artifact_policy.expected_condition_count,
            "scalar_rows": spec.artifact_policy.expected_scalar_row_count,
            "condition_checkpoints": spec.artifact_policy.expected_condition_count,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    load_builtin_studies()
    args = build_parser().parse_args(argv)

    if args.command == "list-studies":
        _list_studies()
        return 0
    if args.command == "describe":
        _describe(args.study_id)
        return 0
    if args.command == "dry-run":
        result = dry_run(_registration(args.study_id))
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    if args.command == "catalog":
        csv_path, json_path = rebuild_catalog(
            args.output_root,
            replace=args.replace_catalog,
        )
        print(f"Catalog CSV: {csv_path}")
        print(f"Catalog JSON: {json_path}")
        return 0
    if args.command in {"baseline-only", "run"}:
        paths = execute(
            _registration(args.study_id),
            mode="baseline" if args.command == "baseline-only" else "production",
            frozen_manifest=args.frozen_manifest,
            frozen_npz=args.frozen_npz,
            frozen_scalar=args.frozen_scalar,
            output_root=args.output_root,
            resume=args.resume,
        )
        print(f"Execution directory: {paths.leaf}")
        print(f"Manifest: {paths.manifest}")
        return 0
    raise AssertionError(args.command)


def cli() -> None:
    try:
        raise SystemExit(main())
    except BaselineGateError as exc:
        print(f"BASELINE GATE FAILED: {exc}", file=sys.stderr)
        raise SystemExit(4)
    except ConditionSchemaError as exc:
        print(f"CONDITION SCHEMA FAILED: {exc}", file=sys.stderr)
        raise SystemExit(5)
    except (ArtifactIntegrityError, CatalogError) as exc:
        print(f"ARTIFACT ERROR: {exc}", file=sys.stderr)
        raise SystemExit(3)
    except (SpecValidationError, UnsupportedPolicyError) as exc:
        print(f"SPECIFICATION ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    except AIEFModularError as exc:
        print(f"AIEF MODULAR ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
