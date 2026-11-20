"""Actual intact engine import for synthetic primitive probes, no authority run.
Reviewed-code loader, not a security boundary for arbitrary source submissions.
"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def verify(source):
    source=Path(source).resolve();manifest=json.loads((HERE/'source_modules.json').read_text())
    for row in manifest['modules']+manifest['metadata']:
        data=(source/row['path']).read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if len(data)!=row['bytes'] or blob!=row['blob']:raise RuntimeError('Reviewed public dependency changed: '+row['path'])
    with (source/'registry/artifacts.csv').open(newline='') as stream:
        rows=[r for r in csv.DictReader(stream) if r['artifact_id']=='ART-0702']
    if len(rows)!=1 or rows[0]['path']!=manifest['engine'] or rows[0]['artifact_status']!='Frozen' or 'authority.lock.json' not in rows[0]['lock_status']:
        raise RuntimeError('Frozen engine policy not acknowledged')
    return manifest


def load(source):
    source=Path(source).resolve();manifest=verify(source);name='r040282_010_unchanged_engine'
    spec=importlib.util.spec_from_file_location(name,source/manifest['engine'])
    if spec is None or spec.loader is None:raise ImportError('Unable to import reviewed engine')
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    try:spec.loader.exec_module(module)
    except Exception:sys.modules.pop(name,None);raise
    if Path(module.__file__).resolve()!=source/manifest['engine']:raise RuntimeError('Wrong engine source')
    verify(source);return module
