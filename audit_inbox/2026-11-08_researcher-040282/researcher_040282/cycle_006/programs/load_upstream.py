"""Load only the reviewed candidate with its verified public dependencies.
Owned-report tooling, not a sandbox for arbitrary submitted code.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def manifest():
    return json.loads((HERE / 'source_modules.json').read_text())


def verify_sources(source):
    data = manifest()
    source = Path(source).resolve()
    for record in data['modules']:
        content = (source / record['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if blob != record['blob'] or len(content) != record['bytes']:
            raise RuntimeError('Acquired source changed: ' + record['path'])
    return data


def load(source):
    source = Path(source).resolve()
    data = verify_sources(source)
    platform = source / data['platform']
    sys.path.insert(0, str(platform))
    sys.path.insert(1, str(source))
    name = 'r040282_reviewed_v41'
    specification = importlib.util.spec_from_file_location(name, source / data['candidate'])
    if specification is None or specification.loader is None:
        raise ImportError('Unable to load reviewed candidate')
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module  # dataclass registration must precede execution
    try:
        specification.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module
