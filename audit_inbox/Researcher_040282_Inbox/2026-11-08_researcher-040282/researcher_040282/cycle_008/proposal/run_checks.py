"""Preregistered actual-public-API008 red/green, finite census and mutants.
No simulation, real oracle run, source installation or authority mutation.
"""
import argparse
from collections import Counter
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import numpy as np

from load_reviewed import load,verify
from status_contract import (A,B,C,BASE,Bundle,Scenario,ContractMismatch,cases,checked,
                             condition_expected,invalid_rho_cases,sequences)
from test_status_contract import suite

MODES=('baseline','candidate','mutants')
RED={'test_candidate_duplicate','test_oracle_duplicate','test_shared_duplicate','test_status_in_key','test_alias_duplicate'}


def require(condition,message):
    if not condition:raise RuntimeError(message)


def save(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def census(api,bundle):
    seq=sequences();records=[];bad=[]
    for i,left in enumerate(seq):
        for j,right in enumerate(seq):
            case=Scenario(f'census_{i}_{j}','census',left,right)
            predicted=condition_expected(left,right)
            try:
                result=checked(api,bundle,case)
                observed=result['status']=='passed'
            except ContractMismatch as error:
                require(error.rule=='verdict','Unexpected nonverdict census violation: '+str(error))
                observed=error.observed
            row={'candidate_sequence':i,'oracle_sequence':j,'expected':predicted,'observed':observed}
            records.append(row)
            if predicted!=observed:bad.append(row)
    summary={'ordered_table_pairs':len(records),'expected_passes':sum(r['expected'] for r in records),
             'observed_passes':sum(r['observed'] for r in records),'mismatches':len(bad),
             'false_accepts':sum(not r['expected'] and r['observed'] for r in bad),
             'false_rejects':sum(r['expected'] and not r['observed'] for r in bad)}
    return summary,records,bad,seq


def mutant_worker(source,bundle):
    original,_=load(source,'baseline');candidate,_=load(source,'candidate')
    fixed=candidate._compare_condition_coverage
    npz_fixed=candidate._compare_npz
    def rows(a,b):
        return candidate._read_csv(a)[1],candidate._read_csv(b)[1]
    def triples(items,raw=False,no_status=False):
        return [(r['seed'],r['rho'] if raw else float(r['rho']))+
                (() if no_status else (r['status'],)) for r in items]
    def count_set(a,b,errors):
        left,right=rows(a,b)
        if len(left)!=len(right):errors.append('mutant row count')
        if set(triples(left))!=set(triples(right)):errors.append('mutant coverage')
        return len(left)
    def triple_identity(a,b,errors):
        left,right=rows(a,b);l,r=triples(left),triples(right)
        if len(left)!=len(right) or len(set(l))!=len(l) or len(set(r))!=len(r):errors.append('mutant triple duplicates/count')
        if set(l)!=set(r):errors.append('mutant coverage')
        return len(left)
    def order_sensitive(a,b,errors):
        count=fixed(a,b,errors);left,right=rows(a,b)
        if triples(left)!=triples(right):errors.append('mutant condition order')
        return count
    def raw_rho(a,b,errors):
        left,right=rows(a,b)
        if set(triples(left,raw=True))!=set(triples(right,raw=True)):errors.append('mutant rho text')
        return len(left)
    def ignore_status(a,b,errors):
        left,right=rows(a,b);l,r=triples(left,no_status=True),triples(right,no_status=True)
        if len(l)!=len(r) or len(set(l))!=len(l) or len(set(r))!=len(r) or set(l)!=set(r):errors.append('mutant key coverage')
        return len(left)
    def bypass_npz(a,b,errors):
        return len(candidate._load_npz(a))
    def deduplicate_input(a,b):
        path=Path(a)/'twindow_condition_status.csv'
        fields,items=candidate._read_csv(path);seen=[];kept=[]
        for row in items:
            key=(row['seed'],float(row['rho']))
            if key not in seen:seen.append(key);kept.append(row)
        with path.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(kept)
        return candidate.compare_twindow_run(a,b)
    controls=[
        ('legacy_set_collapse','baseline',None,Scenario('duplicate_append','mutant',BASE+(A,),BASE),'verdict'),
        ('count_plus_set_only','condition',count_set,Scenario('equal_count_shared_duplicate','mutant',BASE+(A,),BASE+(A,)),'verdict'),
        ('status_in_identity','condition',triple_identity,Scenario('conflicting_status_same_key','mutant',(A,C,B),(A,C,B)),'verdict'),
        ('require_condition_row_order','condition',order_sensitive,Scenario('valid_reordering','mutant',BASE[::-1],BASE),'verdict'),
        ('raw_rho_text_keys','condition',raw_rho,Scenario('valid_numeric_alias','mutant',(('s0','5e-1','success'),B),BASE),'verdict'),
        ('ignore_status','condition',ignore_status,Scenario('changed_status','mutant',(C,B),BASE),'verdict'),
        ('bypass_existing_npz_gate','npz',bypass_npz,Scenario('changed_npz_value','mutant',npz_variant='value'),'verdict'),
        ('rewrite_requested_input','rewrite',deduplicate_input,Scenario('deduplicate_before_answer','mutant',BASE+(A,),BASE),'input_preservation'),
    ]
    results=[]
    for name,kind,fn,case,rule in controls:
        candidate._compare_condition_coverage=fixed;candidate._compare_npz=npz_fixed
        if kind=='baseline':api=original.compare_twindow_run
        elif kind=='rewrite':api=fn
        else:
            if kind=='condition':candidate._compare_condition_coverage=fn
            else:candidate._compare_npz=fn
            api=candidate.compare_twindow_run
        before={'candidate_rows':case.left,'oracle_rows':case.right}
        try:
            try:checked(api,bundle,case)
            except ContractMismatch as error:
                require(error.rule==rule,'Wrong mechanism for '+name)
                results.append({'mutant':name,'detected':True,'reason':rule,'expected':error.expected,
                                'observed':error.observed,'precall_rows':before})
            else:raise RuntimeError('Undetected mutant: '+name)
        finally:
            candidate._compare_condition_coverage=fixed;candidate._compare_npz=npz_fixed
    require(len(results)==8,'Mutant inventory incomplete')
    return results


def child(args):
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter();bundle=Bundle(args.output)
    try:
        if args.child=='mutants':
            records=mutant_worker(args.source,bundle)
            value={'mode':'mutants','optimized_python':not __debug__,'detected':len(records),'records':records,
                   'setup_errors_credited':0,'public_sources_unchanged':len(verify(args.source)['modules']),
                   'elapsed_seconds':time.perf_counter()-start}
            save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
        module,boundary=load(args.source,args.child);api=module.compare_twindow_run
        stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(api,bundle))
        print(stream.getvalue(),end='')
        summary,records,bad,seq=census(api,bundle)
        save(args.output/'table_census.json',records);save(args.output/'census_mismatches.json',bad)
        save(args.output/'sequence_definitions.json',seq)
        advanced=[]
        if args.child=='candidate':
            for case in invalid_rho_cases():
                report=checked(api,bundle,case)
                require(any('invalid finite rho' in item for item in report['errors']), 'Invalid key lacks explicit failure')
                advanced.append({'case':case.name,'status':report['status'],'errors':report['errors']})
            save(args.output/'invalid_key_results.json',advanced)
        value={'mode':args.child,'optimized_python':not __debug__,'tests_run':result.testsRun,
               'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
               'failure_methods':sorted(test.id().split('.')[-1] for test,_ in result.failures),
               'error_methods':sorted(test.id().split('.')[-1] for test,_ in result.errors),
               'census':summary,'candidate_only_invalid_key_cases':len(advanced),
               'fixture_group_counts':dict(Counter(case.group for case in cases())),
               'boundary':boundary,'public_sources_unchanged':len(verify(args.source)['modules']),
               'elapsed_seconds':time.perf_counter()-start}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2))
        return 0 if result.wasSuccessful() else 1
    finally:bundle.close()


def parent(args):
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter();manifest=verify(args.source)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);runs=[]
    for mode in MODES:
        for opt in (False,True):
            name=mode+('_optimized' if opt else '_normal');directory=args.output/name
            command=[sys.executable]+(['-O'] if opt else [])+['-B',str(Path(__file__).resolve()),'--child',mode,
                     '--source',str(args.source.resolve()),'--output',str(directory.resolve())]
            run=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=90)
            (args.output/(name+'.log')).write_text(run.stdout)
            require((directory/'result.json').is_file(),'Child failed before results: '+name)
            value=json.loads((directory/'result.json').read_text())
            require(value['optimized_python'] is opt and value['public_sources_unchanged']==12,'Source/optimization mismatch')
            if mode=='baseline':
                require(run.returncode==1 and value['tests_run']==12 and value['failures']==5 and
                        value['errors']==0 and value['skipped']==0 and set(value['failure_methods'])==RED,
                        'Original did not fail exactly the intended contracts; stop/reassess')
                require(value['census']=={'ordered_table_pairs':1600,'expected_passes':12,'observed_passes':256,
                                         'mismatches':244,'false_accepts':244,'false_rejects':0},'Original census differs from protocol')
            elif mode=='candidate':
                require(run.returncode==0 and value['tests_run']==12 and value['failures']==value['errors']==value['skipped']==0 and
                        value['census']=={'ordered_table_pairs':1600,'expected_passes':12,'observed_passes':12,
                                         'mismatches':0,'false_accepts':0,'false_rejects':0} and
                        value['candidate_only_invalid_key_cases']==10,'Candidate acceptance incomplete')
            else:
                require(run.returncode==0 and value['detected']==8 and value['setup_errors_credited']==0,'Mutant controls incomplete')
            value['observed_returncode']=run.returncode;runs.append(value)
            print(name,'return',run.returncode,'science verified',flush=True)
    for mode in MODES:
        a,b=[row for row in runs if row['mode']==mode]
        omit={'optimized_python','elapsed_seconds'}
        require({k:v for k,v in a.items() if k not in omit}=={k:v for k,v in b.items() if k not in omit},
                'Normal/optimized mismatch: '+mode)
    save(args.output/'worker_results.json',runs)
    science={'tested_main':manifest['commit'],'common_contract_methods':12,
             'original_expected_failures_each_mode':5,'original_errors_each_mode':0,
             'candidate_passes_each_mode':12,'public_api_table_pairs_each_target':1600,
             'independent_expected_accepts':12,'original_accepted':256,'original_false_accepts':244,
             'original_false_rejects':0,'candidate_accepted':12,'candidate_mismatches':0,
             'candidate_only_invalid_key_cases_each_mode':10,'mutants_detected_each_mode':8,
             'all_workers_nontiming_results_equal_under_optimization':True,
             'reviewed_public_source_files_unchanged':len(verify(args.source)['modules']),
             'no_simulation_real_data_or_new_lean':True,'proposal_not_installed_no_remote_changes':True,
             'all_preregistered_acceptance_conditions_met':True}
    record={'science':science,'python':sys.version,'numpy':np.__version__,
            'elapsed_seconds':time.perf_counter()-start,
            'scope':'Actual compare_twindow_run on synthetic CSV/NPZ/status bundles, original and separate one-function candidate. No mocked reader/NPZ stage, real S01, engine, baseline certificate, full study validity or independent approval.'}
    save(args.output/'cycle_results.json',record);print(json.dumps(record,indent=2));return 0


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--child',choices=MODES);args=p.parse_args()
    try:return child(args) if args.child else parent(args)
    except Exception as error:
        args.output.mkdir(parents=True,exist_ok=True)
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_rejection_credited':False})
        raise


if __name__=='__main__':raise SystemExit(main())
