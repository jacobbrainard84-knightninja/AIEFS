"""009 preregistered actual-module admission tests and new-file anchor guard.
Synthetic only. No run_analysis/main/writer/engine/real S01 or incoming code exec.
"""
import argparse
from collections import Counter
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import numpy as np
import pandas as pd

from anchored_admission import (ManifestTrustError,TrustConfigurationError,require_manifest_anchor,validate_anchored)
from admission_contract import Target,checked,scenarios,ContractMismatch
from synthetic_cohort import Fixture,FILES,sha
from load_reviewed import load,verify,authority_metadata
from test_admission import suite

MODES=('baseline','candidate','mutants')
RED={'test_scalar_repin','test_certificate_repin','test_manifest_repin','test_official_pin'}


def require(condition,message):
    if not condition:raise RuntimeError(message)


def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def mutants(module,fixture,official_pin):
    by_action={case.action:case for case in scenarios()}
    def legacy(target,inputs,pin):return target.delegate(inputs)
    def self_anchor(target,inputs,pin):
        return validate_anchored(inputs,expected_manifest_sha256=sha(inputs.manifest),validate_run=target.delegate)
    def claimed_field(target,inputs,pin):
        value=json.loads(inputs.manifest.read_text())
        if value.get('authority_manifest_sha256')!=pin:raise ManifestTrustError()
        return target.delegate(inputs)
    base_object=json.loads(fixture.base_manifest)
    def canonical_root(target,inputs,pin):
        if json.loads(inputs.manifest.read_text())!=base_object:raise ManifestTrustError()
        return target.delegate(inputs)
    def skip_child_validator(target,inputs,pin):
        require_manifest_anchor(inputs.manifest,pin);return object()
    def reject_everything(target,inputs,pin):raise ManifestTrustError()
    def check_after_only(target,inputs,pin):
        result=target.delegate(inputs);require_manifest_anchor(inputs.manifest,pin);return result
    def rewrite_requested_scalar(target,inputs,pin):
        result=validate_anchored(inputs,expected_manifest_sha256=pin,validate_run=target.delegate)
        with inputs.scalar_csv.open('ab') as stream:stream.write(b'\n')
        return result
    controls=(('no_external_anchor',legacy,'scalar_repin','verdict'),
              ('self_derived_expected_anchor',self_anchor,'certificate_minimal','verdict'),
              ('trust_caller_claimed_field',claimed_field,'manifest_claim','verdict'),
              ('canonical_JSON_instead_of_exact_bytes',canonical_root,'manifest_whitespace','verdict'),
              ('skip_actual_child_validator',skip_child_validator,'hash_scalar_csv','verdict'),
              ('reject_all_inputs',reject_everything,'base','verdict'),
              ('anchor_check_after_delegation',check_after_only,'scalar_repin','admission_order'),
              ('rewrite_input_after_valid_answer',rewrite_requested_scalar,'base','input_preservation'))
    records=[]
    for name,implementation,action,rule in controls:
        target=Target(module,'mutant',implementation);witness=[]
        try:checked(target,fixture,official_pin,by_action[action],witness)
        except ContractMismatch as error:
            require(error.rule==rule,'Wrong mutant mechanism: '+name+'/'+error.rule)
            records.append({'mutant':name,'detected':True,'mechanism':error.rule,
                            'expected':error.expected,'observed':error.observed,'witness':witness[0]})
        else:raise RuntimeError('Undetected wrong model: '+name)
    require(len(records)==8,'Mutant inventory incomplete');return records


def advanced(module,fixture,official_pin,official_path):
    base=next(case for case in scenarios() if case.name=='test_owned_trusted_synthetic')
    paths,pin=fixture.prepare(base,official_pin);inputs=module.discover_inputs(fixture.work)
    target=Target(module,'candidate');records=[]
    before={name:sha(path) for name,path in paths.items()}
    for label,bad in (('none',None),('empty',''),('nonhex64','g'*64),('shorthex63','a'*63)):
        try:target(inputs,bad)
        except TrustConfigurationError:
            require(target.calls==0,'Bad policy reached validator')
            records.append({'configuration':label,'TrustConfigurationError':True,'delegate_calls':0,
                            'semantic_negative_detection_credited':False})
        else:raise RuntimeError('Invalid caller policy accepted')
    require(before=={name:sha(path) for name,path in paths.items()},'Configuration checks mutated input')
    require(require_manifest_anchor(official_path,official_pin)==official_pin,'Committed metadata-only anchor failed')
    return records,{'committed_manifest_metadata_anchor_passed':True,'full_genuine_S01_positive_executed':False,
                    'scope':'Only committed manifest bytes authenticated; no genuine child files opened or validate_run call'}


def child(args):
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    policy,official_path,metadata=authority_metadata(args.source);module=load(args.source)
    fixture=Fixture(args.output)
    try:
        if args.child=='mutants':
            records=mutants(module,fixture,policy)
            value={'mode':'mutants','optimized_python':not __debug__,'detected':len(records),'records':records,
                   'setup_errors_credited':0,'fixture_inspection':fixture.inspection,
                   'public_source_files_unchanged':len(verify(args.source)['modules']),
                   'authority_metadata_files_unchanged':len(verify(args.source)['authority_metadata']),
                   'elapsed_seconds':time.perf_counter()-start}
            save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
        records=[];target=Target(module,args.child);stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(target,fixture,policy,records))
        print(stream.getvalue(),end='');save(args.output/'admission_observations.json',records)
        require(len(records)==18,'Incomplete actual-call inventory; setup errors cannot pass')
        mismatches=[row for row in records if row['expected_accept']!=row['observed_accept']]
        summary={'admission_calls':len(records),'expected_accepts':sum(r['expected_accept'] for r in records),
                 'observed_accepts':sum(r['observed_accept'] for r in records),
                 'false_accepts':sum(not r['expected_accept'] and r['observed_accept'] for r in records),
                 'false_rejects':sum(r['expected_accept'] and not r['observed_accept'] for r in records),
                 'delegate_calls':target.calls,'mismatched_verdicts':len(mismatches)}
        save(args.output/'verdict_mismatches.json',mismatches)
        configurations=[];positive_metadata=None
        if args.child=='candidate':
            configurations,positive_metadata=advanced(module,fixture,policy,official_path)
            save(args.output/'configuration_results.json',configurations);save(args.output/'metadata_only_anchor.json',positive_metadata)
        value={'mode':args.child,'optimized_python':not __debug__,'tests_run':result.testsRun,
               'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
               'failure_methods':sorted(test.id().split('.')[-1] for test,_ in result.failures),
               'error_methods':sorted(test.id().split('.')[-1] for test,_ in result.errors),
               'observations':summary,'fixture_group_counts':dict(Counter(case.group for case in scenarios())),
               'fixture_inspection':fixture.inspection,'authority_metadata':metadata,
               'configuration_rejections_not_semantic_detections':len(configurations),
               'candidate_only_metadata_anchor':positive_metadata,
               'source_boundary':{'actual_full_module_imported':True,'actual_discover_inputs_and_validate_run_called':True,
                                  'source_functions_copied_replaced_or_edited':False,
                                  'new_guard_installed':False,'run_analysis_main_or_writer_called':False,
                                  'genuine_S01_five_file_validation_executed':False},
               'public_source_files_unchanged':len(verify(args.source)['modules']),
               'authority_metadata_files_unchanged':len(verify(args.source)['authority_metadata']),
               'elapsed_seconds':time.perf_counter()-start}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0 if result.wasSuccessful() else 1
    finally:fixture.close()


def parent(args):
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter();manifest=verify(args.source)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);runs=[]
    for mode in MODES:
        for optimized in (False,True):
            name=mode+('_optimized' if optimized else '_normal');directory=args.output/name
            command=[sys.executable]+(['-O'] if optimized else [])+['-B',str(Path(__file__).resolve()),'--child',mode,
                      '--source',str(args.source.resolve()),'--output',str(directory.resolve())]
            run=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=120)
            (args.output/(name+'.log')).write_text(run.stdout)
            require((directory/'result.json').is_file(),'Worker failed before result: '+name)
            value=json.loads((directory/'result.json').read_text())
            require(value['optimized_python'] is optimized and value['public_source_files_unchanged']==12 and
                    value['authority_metadata_files_unchanged']==2,'Optimization/source preservation mismatch')
            if mode=='baseline':
                require(run.returncode==1 and value['tests_run']==9 and value['failures']==4 and value['errors']==value['skipped']==0 and
                        set(value['failure_methods'])==RED,'Original failed for unplanned reason; stop/reassess')
                require(value['observations']=={'admission_calls':18,'expected_accepts':3,'observed_accepts':10,
                                               'false_accepts':7,'false_rejects':0,'delegate_calls':18,'mismatched_verdicts':7},
                        'Original actual-API witness inventory differs from protocol')
            elif mode=='candidate':
                require(run.returncode==0 and value['tests_run']==9 and value['failures']==value['errors']==value['skipped']==0 and
                        value['observations']=={'admission_calls':18,'expected_accepts':3,'observed_accepts':3,
                                               'false_accepts':0,'false_rejects':0,'delegate_calls':11,'mismatched_verdicts':0} and
                        value['configuration_rejections_not_semantic_detections']==4 and
                        value['candidate_only_metadata_anchor']['committed_manifest_metadata_anchor_passed'],
                        'Guard/source-validation acceptance incomplete')
            else:require(run.returncode==0 and value['detected']==8 and value['setup_errors_credited']==0,'Controls incomplete')
            value['observed_returncode']=run.returncode;runs.append(value)
            print(name,'return',run.returncode,'preregistered outcomes verified',flush=True)
    for mode in MODES:
        rows=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in runs if row['mode']==mode]
        require(rows[0]==rows[1],'Normal/optimized non-timing outcome differs: '+mode)
    save(args.output/'worker_results.json',runs)
    science={'tested_main':manifest['commit'],'common_contract_methods':9,'admission_fixtures_each_suite':18,
             'original_expected_failures_each_mode':4,'original_errors_each_mode':0,'candidate_passes_each_mode':9,
             'original_false_accepts_relative_to_proposed_anchor_policy':7,'original_false_rejects':0,
             'candidate_verdict_mismatches':0,'expected_positive_test_owned_synthetic_cases':3,
             'untrusted_root_rejections_before_delegation':7,'preserved_child_hash_and_schema_rejections':8,
             'mutants_detected_each_mode':8,'invalid_anchor_configuration_rejections_each_candidate_mode':4,
             'configuration_errors_credited_as_semantic_detections':0,
             'actual_full_module_import_no_copied_or_replaced_source_functions':True,
             'complete_synthetic_NPZ_keys':2600,'reviewed_source_files_unchanged':12,'authority_metadata_files_unchanged':2,
             'normal_and_optimized_nontiming_results_match':True,
             'committed_manifest_anchor_check_is_metadata_only':True,'genuine_S01_five_file_positive_not_executed':True,
             'no_real_data_simulation_CLI_bundle_writer_new_Lean_or_installation':True,
             'new_guard_local_proposal_not_independently_approved_or_uploaded':True,
             'all_preregistered_acceptance_conditions_met':True}
    record={'science':science,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,
            'elapsed_seconds':time.perf_counter()-start,
            'scope':'Actual discover_inputs/validate_run on complete synthetic minimum-consumed-schema cohort. Original accepts relative to proposed external-anchor policy, not a claimed existing anchor argument. Guard delegates unchanged validator for matching roots. No genuine S01 positive, run_analysis, certificate/bundle issuance or independent guard approval.'}
    verify(args.source);save(args.output/'cycle_results.json',record);print(json.dumps(record,indent=2));return 0


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--child',choices=MODES);args=p.parse_args()
    try:return child(args) if args.child else parent(args)
    except Exception as error:
        args.output.mkdir(parents=True,exist_ok=True);save(args.output/'failure.json',{
            'type':type(error).__name__,'message':str(error),'semantic_negative_detection_credited':False});raise


if __name__=='__main__':raise SystemExit(main())
