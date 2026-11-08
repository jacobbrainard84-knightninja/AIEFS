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
