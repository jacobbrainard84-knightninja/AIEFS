"""Assemble owned010 standalone history note/optional packet; no upstream exec."""
from pathlib import Path
import argparse
import csv
import json
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
REPORT=ROOT/'2026-09-04_researcher040282_010_history-phase-contract.md'
ARCHIVE=ROOT/'researcher040282-cycle010-history-phase-contract.zip'
CRITICAL=('HistoryBuffer.lean','step_contract.py','check_engine.py','load_reviewed.py','check_lean.py',
          'prepare_lean.py','run_checks.py','source_modules.json','fetch_public_dependencies.py','extract_from_report.py')


def fence(text,language='text'):return '```'+language+'\n'+text.rstrip('\n')+'\n```\n'


def build_report():
    text=(HERE/'REPORT_BODY.md').read_text();blocks=[]
    for name in CRITICAL:
        language='lean' if name.endswith('.lean') else 'json' if name.endswith('.json') else 'python'
        blocks.append('### '+name+'\n\n<!-- BEGIN_CRITICAL_FILE: '+name+' -->\n'+
                      fence((HERE/'proposal'/name).read_text(),language)+'<!-- END_CRITICAL_FILE: '+name+' -->\n')
    text=text.replace('{{CRITICAL_FILES}}','\n'.join(blocks))
    for tag,path,language in (('{{RESULTS}}','checks/cycle_results.json','json'),
                              ('{{COMMON_LOG}}','checks/common_normal.log','text'),
                              ('{{FORMAL}}','checks/proof/result.json','json'),
                              ('{{MAIN_LEAN_LOG}}','checks/proof/compiler_logs/HistoryBuffer.log','text'),
                              ('{{WRONG_MODELS}}','checks/wrong_models_normal/wrong_models.json','json'),
                              ('{{DESIGN}}','preexecution_case_design.json','json'),
                              ('{{CORRESPONDENCE}}','SOURCE_CORRESPONDENCE.md','text')):
        text=text.replace(tag,fence((HERE/path).read_text(),language))
    records=[]
    for name in ('PLAN.md','proposal/INTEGRATION_NOTE.md','review_decision.json','nonduplication_check.json','compiler_setup.json'):
        records.append('### '+name+'\n\n'+fence((HERE/name).read_text(),'json' if name.endswith('.json') else 'text'))
    text=text.replace('{{RECORDS}}','\n'.join(records))
    logs=[]
    for name in ('false_youngest_read','false_extra_delay','false_append_old'):
        logs.append('### '+name+'\n\n'+fence((HERE/'checks/proof/compiler_logs'/(name+'.log')).read_text()))
    text=text.replace('{{FALSE_MATH_LOGS}}','\n'.join(logs))
    receipt=HERE/'standalone_reproduction.json'
    if receipt.exists():
        value=json.loads(receipt.read_text())
        if not value['actually_executed'] or value['runner_returncode']!=0:raise RuntimeError('Incomplete extracted rerun')
        status=('**Actually executed:** ten critical files extracted byte-identically, three public dependencies freshly fetched/verified, '
                'same disposable compiler; complete runner repeated. Science/four non-timing workers and all25 detailed proof/source/log '
                'records match. Submitter-local reproduction only, not independent-seat review.\n\n'+fence(receipt.read_text(),'json'))
    else:status='**PROVISIONAL: extracted-code rerun not executed yet. Do not deliver this draft.**'
    text=text.replace('{{STANDALONE}}',status)
    cleanup=HERE/'compiler_cleanup.json'
    text=text.replace('{{CLEANUP}}',fence(cleanup.read_text(),'json') if cleanup.exists() else '**Disposable compiler cleanup pending actual reproduction.**')
    with (ROOT/'CLAIM_LEDGER.csv').open(newline='') as stream:ledger=list(csv.DictReader(stream))
    text=text.replace('{{LEDGER}}',str(len(ledger))+' unique rows / '+str(sum(r['evidence_label']=='LEAN_COMPILED' for r in ledger))+' LEAN_COMPILED labels')
    if '{{' in text and any(tag in text for tag in ('{{STANDALONE}}','{{CRITICAL_FILES}}','{{RESULTS}}','{{RECORDS}}')):
        raise RuntimeError('Unexpanded assembly field')
    REPORT.write_text(text);print('Report written:',REPORT.name,'bytes',REPORT.stat().st_size)


def selected_files():
    extensions={'.md','.csv','.json','.py','.lean','.log','.sh','.txt','.yml','.yaml','.toml'}
    excluded={'__pycache__','.cache','.git','node_modules','.venv'};files=[]
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.is_symlink() or not (path.suffix in extensions or path.name=='lean-toolchain'):continue
        relative=path.relative_to(ROOT)
        if excluded.intersection(relative.parts) or (path.name=='REPORT_BODY.md' and path.parent!=HERE):continue
        files.append(path)
    return sorted(files)


def build_indices():
    with (ROOT/'CLAIM_LEDGER.csv').open(newline='') as stream:ledger=list(csv.DictReader(stream))
    selected={str(path.relative_to(ROOT)):path for path in selected_files()}
    references=sorted({value.strip() for row in ledger for value in row['evidence_files'].split(';') if value.strip()})
    records=[]
    for reference in references:
        path=ROOT/reference
        if path.is_file():members=[reference] if reference in selected else []
        elif path.is_dir():members=sorted(name for name in selected if name.startswith(reference.rstrip('/')+'/'))
        else:members=[]
        if not members:raise FileNotFoundError('Missing unpacked evidence: '+reference)
        records.append({'referenced_as':reference,'availability':'UNPACKED','packet_members':['researcher_040282/'+name for name in members]})
    logs=sorted(name for name in selected if name.endswith('.log'))
    index={'ledger_rows':len(ledger),'completed004_rows':108,'completed005_rows':109,'completed006_rows':111,
           'completed007_rows':112,'completed008_rows':113,'completed009_rows':114,
           'unique_ledger_references':len(references),'all_ledger_references_unpacked':True,'archive_only_ledger_references':0,
           'unpacked_log_count':len(logs),'log_packet_members':['researcher_040282/'+name for name in logs],
           'ledger_evidence':records,'note':'Historical ZIPs are not nested; cited logs remain unchanged and unpacked. Historical closure receipts concern their own frozen cycle, not current live root.'}
    (ROOT/'EVIDENCE_INDEX.json').write_text(json.dumps(index,indent=2)+'\n');rows=[]
    for old in sorted(ROOT.glob('*.zip')):
        if old==ARCHIVE:continue
        with zipfile.ZipFile(old) as archive:
            for member in archive.namelist():
                if not member.endswith('.log'):continue
                if not member.startswith('researcher_040282/'):raise RuntimeError('Unexpected old log root')
                relative=member.removeprefix('researcher_040282/')
                if relative not in selected or selected[relative].read_bytes()!=archive.read(member):raise RuntimeError('Old log not preserved unpacked: '+relative)
                rows.append({'historical_archive':old.name,'historical_log_member':member,'now_unpacked_at':member,
                             'content_matches_historical_member':'TRUE','archive_only_in_this_handoff':'FALSE'})
    with (ROOT/'HISTORICAL_ARCHIVE_LOG_MAP.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['historical_archive','historical_log_member','now_unpacked_at',
                              'content_matches_historical_member','archive_only_in_this_handoff']);writer.writeheader();writer.writerows(rows)
    print('Index:',len(references),'references,',len(logs),'unpacked logs,',len(rows),'historical log mappings')


def package():
    build_indices();files=selected_files()
    with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in files:archive.write(path,'researcher_040282/'+str(path.relative_to(ROOT)))
    print('Package written:',ARCHIVE.name,'files',len(files),'bytes',ARCHIVE.stat().st_size)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--package',action='store_true');args=parser.parse_args()
    build_report()
    if args.package:package()


if __name__=='__main__':main()
