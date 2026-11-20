"""Audit-only stand-ins for missing aief_modular dependencies.

The user's function bodies are executed unchanged. Only their unavailable
imports are omitted from the AST, with the five imported names injected here.
These stand-ins do NOT validate the real aief_modular package.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import types
from pathlib import Path

SOURCE = Path(__file__).with_name('analysis_under_audit.py')


class ArtifactIntegrityError(RuntimeError):
    pass


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.audit_helper_' + path.name + '.tmp')
    try:
        with open(tmp, 'w', encoding='utf-8') as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_write_json(path, value):
    atomic_write_text(path, json.dumps(value, indent=2, allow_nan=False))


def load_analysis():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'), filename=str(SOURCE))
    tree.body = [
        node for node in tree.body
        if not (
            isinstance(node, ast.ImportFrom)
            and (node.module or '').startswith('aief_modular')
        ) and not (
            isinstance(node, ast.Import)
            and any(alias.name.startswith('aief_modular') for alias in node.names)
        )
    ]
    name = 'pasted_aief_analysis_audit'
    module = types.ModuleType(name)
    module.__file__ = str(SOURCE)
    module.__dict__.update(
        ArtifactIntegrityError=ArtifactIntegrityError,
        file_sha256=file_sha256,
        atomic_write_text=atomic_write_text,
        atomic_write_json=atomic_write_json,
        modular_artifacts=types.SimpleNamespace(__file__=__file__),
        modular_validation=types.SimpleNamespace(__file__=__file__),
    )
    sys.modules[name] = module
    exec(compile(tree, str(SOURCE), 'exec'), module.__dict__)
    return module
