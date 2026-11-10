"""Independent pairwise condition contract and small public-API toy bundles.
All expected rows are immutable and expected truth/file snapshots precede calls.
"""
import csv
from dataclasses import dataclass
import itertools
import math
from pathlib import Path
import tempfile
import numpy as np

FIELDS = ('seed','rho','status','elapsed_seconds')
A = ('s0','0.5','success')
B = ('s1','1','success')
C = ('s0','0.5','failed')
BASE = (A,B)
SIX = tuple((f's{i}',rho,'success') for i in range(3) for rho in ('0.5','1'))
SCALAR_FIELDS = ('seed_index','seed','rho','branch','metric')
SCALAR_ROWS = (('0','s0','0.5','continue','0.25'),('1','s1','1','reset_ema','0.75'))


class ContractMismatch(RuntimeError):
    def __init__(self, rule, name, expected, observed):
        self.rule,self.case,self.expected,self.observed = rule,name,expected,observed
        super().__init__(f'{rule}: {name}; expected={expected!r}, observed={observed!r}')


@dataclass(frozen=True)
class Scenario:
    name: str
    group: str
    left: tuple = BASE
    right: tuple = BASE
    left_fields: tuple = FIELDS
    right_fields: tuple = FIELDS
    scalar_variant: str = 'same'
    npz_variant: str = 'same'
    auxiliary_difference: bool = False


def condition_expected(left, right, left_fields=FIELDS, right_fields=FIELDS):
    for fields in (left_fields,right_fields):
        if not all(name in fields for name in ('seed','rho','status')):
            return False
    if len(left) !=len(right):
        return False
    normalized = []
    for rows in (left,right):
        current = []
        for seed,text,status in rows:
            try:
                rho = float(text)
            except (TypeError,ValueError):
                return False
            if not math.isfinite(rho):
                return False
            key = (seed,rho)
            if any(key ==earlier[0] for earlier in current):
                return False
            current.append((key,status))
        normalized.append(current)
    for key,status in normalized[0]:
        if not any(key ==other_key and status ==other_status for other_key,other_status in normalized[1]):
            return False
    return True


def expected(case):
    return (condition_expected(case.left,case.right,case.left_fields,case.right_fields) and
            case.scalar_variant =='same' and case.npz_variant =='same')


def write_status(path, rows, fields=FIELDS, alternate_metadata=False):
    with Path(path).open('w',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore')
        writer.writeheader()
        for seed,rho,status in rows:
            writer.writerow({'seed':seed,'rho':rho,'status':status,
                             'elapsed_seconds':'999' if alternate_metadata else '0.01',
                             'error':'different auxiliary metadata' if alternate_metadata else ''})


class Bundle:
    def __init__(self, parent=None):
        self.temp = tempfile.TemporaryDirectory(prefix='r040282_008_',dir=parent)
        self.root = Path(self.temp.name)
        self.left,self.right = self.root/'candidate',self.root/'oracle'
        self.left.mkdir();self.right.mkdir()

    def close(self):
        self.temp.cleanup()

    def prepare(self, case):
        for directory,is_left,rows,fields in ((self.left,True,case.left,case.left_fields),
                                              (self.right,False,case.right,case.right_fields)):
            scalar_rows = [dict(zip(SCALAR_FIELDS,row)) for row in SCALAR_ROWS]
            scalar_fields = list(SCALAR_FIELDS)
            if is_left:
                if case.scalar_variant =='value':scalar_rows[0]['metric']='0.250001'
                elif case.scalar_variant =='branch':scalar_rows[0]['branch']='wrong_branch'
                elif case.scalar_variant =='columns':scalar_fields=scalar_fields[::-1]
                elif case.scalar_variant !='same':raise ValueError('Unknown scalar fixture')
            path = directory/'AIEF_1_4_Twindow_sensitivity_SYNTHETIC_scalar_summary.csv'
            with path.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=scalar_fields);writer.writeheader();writer.writerows(scalar_rows)
            payload={'weights':np.array([[.2,.3],[.4,.6]],dtype=np.float64),
                     'partial_complex':np.array([complex(math.nan,1),complex(2,3)],dtype=np.complex128)}
            if is_left:
                if case.npz_variant =='value':payload['weights'][0,1]=np.nextafter(payload['weights'][0,1],math.inf)
                elif case.npz_variant =='dtype':payload['weights']=payload['weights'].astype(np.float32)
                elif case.npz_variant =='shape':payload['weights']=payload['weights'].reshape(4)
                elif case.npz_variant =='key':payload['wrong_key']=payload.pop('weights')
                elif case.npz_variant =='nan_component':payload['partial_complex'][0]=complex(math.nan,99)
                elif case.npz_variant !='same':raise ValueError('Unknown NPZ fixture')
            np.savez(directory/'AIEF_1_4_Twindow_sensitivity_SYNTHETIC_branch_diagnostics.npz',**payload)
            write_status(directory/'twindow_condition_status.csv',rows,fields,
                         is_left and case.auxiliary_difference)

    def snapshot(self):
        return {str(p.relative_to(self.root)):p.read_bytes() for p in sorted(self.root.rglob('*')) if p.is_file()}


def checked(api, bundle, case):
    answer_expected = expected(case)  # From original immutable rows, before I/O/target.
    bundle.prepare(case)
    before = bundle.snapshot()
    result = api(bundle.left,bundle.right)
    if before !=bundle.snapshot():
        raise ContractMismatch('input_preservation',case.name,'all six files unchanged','modified')
    counts = (result.scalar_rows,result.npz_entries,result.condition_rows)
    wanted = (len(SCALAR_ROWS),2,len(case.left))
    if counts !=wanted:
        raise ContractMismatch('counts',case.name,wanted,counts)
    if result.status not in ('passed','failed') or bool(result.errors) !=(result.status =='failed'):
        raise ContractMismatch('status_errors',case.name,'consistent status/errors',(result.status,result.errors))
    answer = result.status =='passed'
    if answer !=answer_expected:
        raise ContractMismatch('verdict',case.name,answer_expected,answer)
    return {'status':result.status,'condition_rows':result.condition_rows,'errors':list(result.errors)}


def cases():
    return [
        Scenario('six_unique_conditions','unique',SIX,SIX),
        Scenario('reordered','order_alias',BASE[::-1],BASE),
        Scenario('rho_aliases','order_alias',(('s0','5e-1','success'),('s1','1.00','success')),BASE),
        Scenario('condition_header_order','order_alias',left_fields=('status','rho','seed','elapsed_seconds')),
        Scenario('signed_zero_key_policy','order_alias',(('s0','-0.0','success'),B),(('s0','0.0','success'),B)),
        Scenario('candidate_duplicate3v2','candidate_duplicate',BASE+(A,),BASE),
        Scenario('oracle_duplicate2v3','oracle_duplicate',BASE,BASE+(A,)),
        Scenario('shared_duplicate3v3','shared_duplicate',BASE+(A,),BASE+(A,)),
        Scenario('shared_duplicate_permuted','shared_duplicate',(A,A,B),(B,A,A)),
        Scenario('status_is_not_condition_identity','status_in_key',(A,C,B),(B,A,C)),
        Scenario('missing_condition','coverage',BASE[:1],BASE),
        Scenario('changed_seed','coverage',(('s2','0.5','success'),B),BASE),
        Scenario('changed_rho','coverage',(('s0','0.75','success'),B),BASE),
        Scenario('changed_status','coverage',(C,B),BASE),
        Scenario('duplicate_replaces_other_key','coverage',(A,A),BASE),
        Scenario('required_status_column_missing','coverage',left_fields=('seed','rho','elapsed_seconds')),
        Scenario('numeric_seed_text_distinction','coverage',(('01','0.5','success'),B),(('1','0.5','success'),B)),
        *[Scenario('scalar_'+kind,'scalar',scalar_variant=kind) for kind in ('value','branch','columns')],
        *[Scenario('npz_'+kind,'npz',npz_variant=kind) for kind in ('value','dtype','shape','key','nan_component')],
        Scenario('aux_metadata_ignored','metadata',right_fields=FIELDS+('error',),auxiliary_difference=True),
        Scenario('logical_empty_not_a_study_certificate','metadata',(),()),
        Scenario('counts_and_file_preservation','counts',SIX,SIX),
        Scenario('normalized_duplicate3v2','alias_duplicate',(A,('s0','5e-1','success'),B),BASE),
        Scenario('normalized_duplicates_both','alias_duplicate',(A,('s0','5e-1','success'),B),
                 (('s0','.50','success'),A,B)),
    ]


def groups():
    return ('unique','order_alias','candidate_duplicate','oracle_duplicate','shared_duplicate',
            'status_in_key','coverage','scalar','npz','metadata','counts','alias_duplicate')


def sequences():
    return tuple(rows for length in range(4) for rows in itertools.product((A,B,C),repeat=length))


def invalid_rho_cases():
    out=[]
    for bad in ('NaN','Inf','-Inf','not-numeric',''):
        rows=(('s0',bad,'success'),B)
        out.append(Scenario('invalid_candidate_rho_'+repr(bad),'candidate_only',rows,BASE))
        out.append(Scenario('invalid_oracle_rho_'+repr(bad),'candidate_only',BASE,rows))
    return out
