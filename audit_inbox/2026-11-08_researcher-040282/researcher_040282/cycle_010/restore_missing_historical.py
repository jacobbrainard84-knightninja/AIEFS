"""Administrative missing-only9175B old CI restoration from delivered009 ZIP.
No historical science execution, overwrite of existing content, remote fetch or
restoration of the user-deleted legacy Lua audit.
"""
from pathlib import Path
import json
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RELATIVE='cycle_006/source_state/main/.github/workflows/repo-checks.yml'
ARCHIVE=ROOT/'researcher040282-cycle009-anchored-cohort-admission.zip'


def main():
    target=ROOT/RELATIVE
    with zipfile.ZipFile(ARCHIVE) as archive:data=archive.read('researcher_040282/'+RELATIVE)
    if len(data)!=9175:raise RuntimeError('Unexpected delivered historical member')
    existed=target.exists()
    if existed and target.read_bytes()!=data:raise RuntimeError('Existing historical file differs: refuse overwrite')
    if not existed:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    value={'restored_path':RELATIVE,'source_delivered_archive':ARCHIVE.name,'missing_before_this_administrative_step':not existed,
           'restored_bytes':0 if existed else len(data),'restored_content_matches_delivered_member':target.read_bytes()==data,
           'existing_source_or_log_overwritten':False,'historical_science_rerun':False,
           'scientific010_inputs_code_results_changed':False,'user_deleted_legacy_lua_audit_remains_absent':not Path('/home/user/audit').exists(),
           'scope':'Exact missing-only old evidence recovery; no new finding, old-source audit, source repair or chronology reconstruction'}
    (HERE/'historical_restoration.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))


if __name__=='__main__':main()
