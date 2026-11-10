"""Import actual unchanged candidate and verified package, no copied functions.
Owned reviewed-code loader, not a security boundary for arbitrary submissions.
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
    for row in manifest['modules']+manifest['authority_metadata']:
        data=(source/row['path']).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if blob!=row['blob'] or len(data)!=row['bytes']:raise RuntimeError('Reviewed dependency changed: '+row['path'])
    return manifest


def authority_metadata(source):
    source=Path(source).resolve();manifest=verify(source);policy=manifest['authority']
    with (source/policy['inventory']).open(newline='') as stream:
        rows=[row for row in csv.DictReader(stream) if row['snapshot_artifact_id']==policy['artifact_id'] and row['path']==policy['manifest']]
    if len(rows)!=1:raise RuntimeError('Independent repository metadata anchor missing/ambiguous')
    pin=rows[0]['sha256'];path=source/policy['manifest'];actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if pin!=actual:raise RuntimeError('Committed manifest differs from acquired ART-2217 metadata')
    return pin,path,{'artifact_id':policy['artifact_id'],'committed_manifest_metadata_matches_inventory':True,
                     'genuine_five_file_S01_positive_executed':False,'scope':'METADATA_ONLY_NOT_AUTHORITY_ISSUANCE'}


def load(source):
    source=Path(source).resolve();manifest=verify(source)
    sys.path.insert(0,str(source/manifest['platform']));sys.path.insert(1,str(source))
    name='r040282_009_actual_candidate';spec=importlib.util.spec_from_file_location(name,source/manifest['candidate'])
    if spec is None or spec.loader is None:raise ImportError('Reviewed module cannot load')
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    try:spec.loader.exec_module(module)
    except Exception:sys.modules.pop(name,None);raise
    if Path(module.__file__).resolve()!=source/manifest['candidate']:raise RuntimeError('Wrong module imported')
    verify(source);return module
