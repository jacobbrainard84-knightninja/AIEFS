"""Independent deterministic COMPLETE MINIMUM consumed-schema toy cohort.
Never engine-produced, never S01, never an issued production certificate.
"""
import csv
from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
import numpy as np

SEEDS=tuple(f'toy009_{i:03d}' for i in range(40))
RHOS=(0.5,0.75,1.0,1.5,2.0)
BRANCHES=('continue','reset_ema','reset_B','future_shuffle')
OUTCOMES=('Weighted_similarity_late_fixed_physical','Retention_contrast_late_fixed_physical',
          'P_mean_late_fixed_physical','Weighted_similarity_late_normalized_EMA',
          'Retention_contrast_late_normalized_EMA','P_mean_late_normalized_EMA')
SCALAR_FIELDS=('seed','seed_index','rho','T_window','branch','D_B_final')+OUTCOMES
SCALAR_NAME='AIEF_1_4_Twindow_sensitivity_SYNTHETIC_009_scalar_summary.csv'
NPZ_NAME='AIEF_1_4_Twindow_sensitivity_SYNTHETIC_009_branch_diagnostics.npz'
FILES={'scalar_csv':SCALAR_NAME,'branch_npz':NPZ_NAME,'manifest':'manifest.json',
       'condition_status':'twindow_condition_status.csv','baseline_certificate':'baseline_equivalence_certificate.json'}
HASH_LABELS={'scalar_csv':'scalar_csv','branch_npz':'branch_npz',
             'condition_status':'condition_status_csv','baseline_certificate':'baseline_certificate'}
TIMES=(np.arange(0,32000,50,dtype=float)+1.0)*0.01
T_STAR=25.0
B_C=0.12


def require(condition,message):
    if not condition:raise RuntimeError(message)


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def dump(path,value,indent=2):
    Path(path).write_text(json.dumps(value,sort_keys=True,indent=indent,allow_nan=False)+'\n')


def write_csv(path,fields,rows):
    with Path(path).open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def read_csv(path):
    with Path(path).open(newline='') as stream:
        reader=csv.DictReader(stream);return tuple(reader.fieldnames),list(reader)


def key(branch,seed,rho,field):return f'{branch}_seed_{seed}_rho_{rho}_{field}'


def full_npz(path):
    ramp=np.arange(640,dtype=float)/639.0
    expected=[]
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        def save(name,value):
            buffer=io.BytesIO();np.save(buffer,value,allow_pickle=False)
            info=zipfile.ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=0o600<<16
            archive.writestr(info,buffer.getvalue());expected.append(name)
        for index,seed in enumerate(SEEDS):
            for rho in RHOS:
                for branch_index,branch in enumerate(BRANCHES):
                    density=.25+.25*ramp+.002*index+.01*branch_index+.005*rho
                    similarity=.1+.8*ramp-.001*index-.005*branch_index
                    for field,value in (('sample_times',TIMES),('density_trajectory',density),('similarity_trajectory',similarity)):
                        save(key(branch,seed,rho,field),value)
                matrix=np.full((12,12),.2+.001*(index+int(4*rho)),dtype=float);np.fill_diagonal(matrix,0)
                save(key('continue',seed,rho,'B_final'),matrix)
    require(len(expected)==2600,'Generator key inventory incomplete')
    return tuple(expected)


def inspect_npz(path,expected):
    counts={'trajectory_arrays':0,'continue_matrices':0}
    with np.load(path,allow_pickle=False) as archive:
        require(len(archive.files)==2600 and set(archive.files)==set(expected),'Toy NPZ keyset incomplete')
        for name in archive.files:
            value=archive[name];require(np.all(np.isfinite(value)),'Nonfinite toy payload')
            if name.endswith('_B_final'):
                require(value.shape==(12,12) and np.array_equal(value,value.T) and np.any(value>0),'Bad toy matrix')
                counts['continue_matrices']+=1
            else:
                require(value.shape==(640,),'Bad toy trajectory shape')
                if name.endswith('_sample_times'):require(np.array_equal(value,TIMES),'Bad toy saved schedule')
                elif name.endswith('_density_trajectory'):require(np.all((value>=0)&(value<=1)) and value[0]!=value[-1],'Bad toy density')
                else:require(np.all((value>=-1)&(value<=1)) and value[0]!=value[-1],'Bad toy similarity')
                counts['trajectory_arrays']+=1
    return dict(counts,npz_total_keys=2600,samples_per_trajectory=640,
                all_keys_shapes_finiteness_and_ranges_checked=True,synthetic_not_engine_trajectories=True)


class Fixture:
    def __init__(self,parent=None):
        self.temp=tempfile.TemporaryDirectory(prefix='r040282_009_',dir=parent)
        self.root=Path(self.temp.name);self.base=self.root/'trusted_SYNTHETIC';self.base.mkdir()
        rows=[];status=[]
        for index,seed in enumerate(SEEDS):
            for rho in RHOS:
                status.append({'seed':seed,'rho':rho,'status':'success'})
                for branch_index,branch in enumerate(BRANCHES):
                    row={'seed':seed,'seed_index':index,'rho':rho,'T_window':rho*T_STAR,
                         'branch':branch,'D_B_final':.4+.001*index+.005*branch_index}
                    row.update({name:.2+.001*index+.01*rho+.005*branch_index+.002*j for j,name in enumerate(OUTCOMES)})
                    rows.append(row)
        write_csv(self.base/SCALAR_NAME,SCALAR_FIELDS,rows)
        write_csv(self.base/FILES['condition_status'],('seed','rho','status'),status)
        expected=full_npz(self.base/NPZ_NAME)
        dump(self.base/FILES['baseline_certificate'],{'status':'passed','n_seeds':40,'SYNTHETIC_TEST_ONLY':True,
             'frozen_input_hashes':{'frozen_production_source':hashlib.sha256(b'invented toy009 lineage').hexdigest()}})
        manifest={'freezeable':True,'completion':{'status':'completed'},'baseline_equivalence':{'status':'passed'},
                  'randomization':{'paired_seeds':list(SEEDS)},'study':{'rho_values':list(RHOS)},
                  'protocol':{'branches':list(BRANCHES)},'model':{'T_star':T_STAR,'B_c':B_C},
                  'config_hash':'SYNTHETIC_TOY009','SYNTHETIC_TEST_ONLY':True}
        self.seal(self.base,manifest)
        self.base_pin=sha(self.base/FILES['manifest'])  # TEST authority issued before target calls.
        self.base_manifest=(self.base/FILES['manifest']).read_bytes()
        self.inspection=dict(inspect_npz(self.base/NPZ_NAME,expected),scalar_rows=len(rows),
                             successful_condition_rows=len(status),unique_seed_count=len(SEEDS),
                             fixture_npz_bytes=(self.base/NPZ_NAME).stat().st_size)
        self.work=None

    def close(self):self.temp.cleanup()

    def seal(self,directory,manifest):
        manifest['output_hashes']={label:sha(directory/FILES[field]) for field,label in HASH_LABELS.items()}
        dump(directory/FILES['manifest'],manifest)

    def prepare(self,scenario,official_pin):
        if self.work is not None:shutil.rmtree(self.work)
        self.work=self.root/('relocated_request' if scenario.action=='relocate' else 'request')
        shutil.copytree(self.base,self.work)
        mpath=self.work/FILES['manifest'];manifest=json.loads(mpath.read_text());action=scenario.action
        if action=='scalar_repin':
            fields,rows=read_csv(self.work/SCALAR_NAME);rows[0][OUTCOMES[0]]='0.123456789'
            write_csv(self.work/SCALAR_NAME,fields,rows);self.seal(self.work,manifest)
        elif action in ('certificate_minimal','certificate_lineage'):
            value={'status':'passed','n_seeds':40}
            if action=='certificate_lineage':value.update({'SYNTHETIC_TEST_ONLY':True,'frozen_input_hashes':{
                'frozen_production_source':hashlib.sha256(b'different invented toy009 lineage').hexdigest()}})
            dump(self.work/FILES['baseline_certificate'],value);self.seal(self.work,manifest)
        elif action=='manifest_model':manifest['model']['B_c']=.23;dump(mpath,manifest)
        elif action=='manifest_claim':manifest['authority_manifest_sha256']=self.base_pin;dump(mpath,manifest)
        elif action=='manifest_whitespace':dump(mpath,manifest,indent=4)
        elif action.startswith('hash_'):
            field=action[5:]
            with (self.work/FILES[field]).open('ab') as stream:stream.write(b'\n')
        elif action=='schema_scalar':
            fields,rows=read_csv(self.work/SCALAR_NAME);rows[-1]=dict(rows[0]);write_csv(self.work/SCALAR_NAME,fields,rows)
            self.seal(self.work,manifest)
        elif action=='schema_status':
            fields,rows=read_csv(self.work/FILES['condition_status']);rows[-1]=dict(rows[0])
            write_csv(self.work/FILES['condition_status'],fields,rows);self.seal(self.work,manifest)
        elif action=='schema_certificate':
            dump(self.work/FILES['baseline_certificate'],{'status':'failed','n_seeds':40});self.seal(self.work,manifest)
        elif action=='schema_freezeable':manifest['freezeable']=False;dump(mpath,manifest)
        elif action not in ('base','relocate','official_pin'):raise ValueError('Unknown fixture action')
        pin=official_pin if action=='official_pin' else (sha(mpath) if action.startswith('schema_') else self.base_pin)
        paths={field:self.work/name for field,name in FILES.items()}
        return paths,pin
