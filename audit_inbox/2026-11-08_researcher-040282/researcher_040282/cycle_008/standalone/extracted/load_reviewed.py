"""Verified actual package/public-API loads, no AST-extracted or mocked oracle.
Never run simulations/baseline/authority gates. Not arbitrary-code intake security.
"""
import ast
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def verify(source):
    source=Path(source).resolve()
    manifest=json.loads((HERE/'source_modules.json').read_text())
    for row in manifest['modules']:
        data=(source/row['path']).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=row['blob'] or len(data)!=row['bytes']:
            raise RuntimeError('Reviewed public dependency differs: '+row['path'])
    return manifest


def load(source, mode):
    source=Path(source).resolve();manifest=verify(source)
    sys.path.insert(0,str(source/manifest['platform']))
    original=importlib.import_module('aief_modular.oracle')
    if Path(original.__file__).resolve()!=source/manifest['oracle']:
        raise RuntimeError('Wrong public package source imported')
    if mode=='baseline':
        return original,{'actual_public_api':True,'simulation_or_runner_entrypoints_called':False}
    if mode!='candidate':raise ValueError('Unknown controlled mode')
    before=ast.parse((source/manifest['oracle']).read_text())
    path=HERE/'oracle_candidate.py';after=ast.parse(path.read_text())
    name='_compare_condition_coverage'
    def unchanged(tree):
        return [ast.dump(n,include_attributes=False) for n in tree.body if not(isinstance(n,ast.FunctionDef) and n.name==name)]
    for tree in (before,after):
        if sum(isinstance(n,ast.FunctionDef) and n.name==name for n in tree.body)!=1:
            raise RuntimeError('Missing/duplicate proposal function')
    if unchanged(before)!=unchanged(after):raise RuntimeError('Proposal altered another public-API gate')
    spec=importlib.util.spec_from_file_location('aief_modular._r040282_oracle_candidate',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    verify(source)
    return module,{'actual_public_api':True,'only_changed_function':name,
                   'other_top_level_nodes_preserved':len(unchanged(before)),
                   'simulation_or_runner_entrypoints_called':False,'proposal_installed':False}
