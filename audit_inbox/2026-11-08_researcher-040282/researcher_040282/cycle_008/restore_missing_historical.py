"""Administrative missing-only historical restoration; no science rerun.
Do not restore user-deleted legacy Lua audit or overwrite any existing content.
"""
from pathlib import Path
import json
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RELATIVE='cycle_006/source_state/main/.github/workflows/repo-checks.yml'
ARCHIVE='researcher040282-cycle007-complex-nan-comparator.zip'


def main():
    path=ROOT/RELATIVE
    if path.exists():raise RuntimeError('Missing-only restoration refuses existing file')
    with zipfile.ZipFile(ROOT/ARCHIVE) as archive:
        data=archive.read('researcher_040282/'+RELATIVE)
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    if path.read_bytes()!=data:raise RuntimeError('Restoration differs')
    if Path('/home/user/audit').exists():raise RuntimeError('User-deleted legacy audit must remain absent')
    result={'kind':'ADMINISTRATIVE_MISSING_ONLY_RESTORATION_NOT_SCIENTIFIC_REEXECUTION',
            'reason':'Prior007 archive comparison found this one old006 workflow absent in current workspace; cause not inferred',
            'path':RELATIVE,'delivered_archive':ARCHIVE,'restored_bytes':len(data),
            'restored_content_matches_delivered_member':True,'existing_source_or_log_overwritten':False,
            'scientific008_inputs_code_results_changed':False,'historical_science_rerun':False,
            'user_deleted_legacy_lua_audit_remains_absent':True}
    (HERE/'historical_restoration.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
