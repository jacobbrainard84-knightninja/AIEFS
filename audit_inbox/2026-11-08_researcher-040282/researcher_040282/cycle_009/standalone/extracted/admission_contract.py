"""Immutable external-admission scenarios, independent pre-call facts/snapshots.
Original observations are relative to this proposed contract, not an old pin arg.
"""
from dataclasses import dataclass
from anchored_admission import ManifestTrustError,validate_anchored
from synthetic_cohort import SEEDS,RHOS,BRANCHES,B_C,T_STAR,sha


@dataclass(frozen=True)
class Scenario:
    name:str
    group:str
    action:str='base'
    accepted:bool=True
    stage:str='accepted'
    reason:str=''
    delegate_calls:int=1


class ContractMismatch(RuntimeError):
    def __init__(self,rule,case,expected,observed):
        self.rule,self.case,self.expected,self.observed=rule,case,expected,observed
        super().__init__(f'{rule}: {case}; expected={expected!r}, observed={observed!r}')


def scenarios():
    root=lambda name,group,action:Scenario(name,group,action,False,'root','manifest_not_anchored',0)
    cases=[Scenario('test_owned_trusted_synthetic','positive'),Scenario('byte_identical_relocation','relocation','relocate'),
           root('finite_scalar_changed_and_resealed','scalar_repin','scalar_repin'),
           root('two_field_certificate_resealed','certificate_repin','certificate_minimal'),
           root('invented_lineage_changed_resealed','certificate_repin','certificate_lineage'),
           root('finite_Bc_manifest_change','manifest_repin','manifest_model'),
           root('caller_claims_expected_anchor','manifest_repin','manifest_claim'),
           root('same_JSON_different_bytes','manifest_repin','manifest_whitespace'),
           root('fabricated_cohort_against_repository_S01_pin','official_pin','official_pin')]
    for field,label in (('scalar_csv','scalar_csv'),('branch_npz','branch_npz'),
                        ('condition_status','condition_status_csv'),('baseline_certificate','baseline_certificate')):
        cases.append(Scenario('child_hash_'+field,'child_hash','hash_'+field,False,'child_hash','Input hash mismatch for '+label,1))
    for action,reason in (('schema_scalar','duplicate seed/rho/branch'),('schema_status','200 unique conditions'),
                         ('schema_certificate','passing 40-seed certificate'),('schema_freezeable','not explicitly freezeable')):
        cases.append(Scenario('test_anchored_'+action,'schema',action,False,'schema',reason,1))
    cases.append(Scenario('returned_object_counts_hashes_files','counts'))
    return tuple(cases)


def groups():return ('positive','relocation','scalar_repin','certificate_repin','manifest_repin','official_pin','child_hash','schema','counts')


class Target:
    def __init__(self,module,mode,implementation=None):
        self.module=module;self.mode=mode;self.calls=0;self.last_result=None;self.implementation=implementation
    def delegate(self,inputs):
        self.calls+=1;self.last_result=self.module.validate_run(inputs);return self.last_result
    def __call__(self,inputs,pin):
        if self.implementation is not None:return self.implementation(self,inputs,pin)
        if self.mode=='baseline':return self.delegate(inputs)
        if self.mode=='candidate':return validate_anchored(inputs,expected_manifest_sha256=pin,validate_run=self.delegate)
        raise ValueError('Unknown controlled target')


def snapshot(paths,root):
    return {'digests':{name:sha(path) if path.is_file() else None for name,path in paths.items()},
            'file_inventory':sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())}


def checked(target,fixture,official_pin,case,records=None):
    expected=(case.accepted,case.stage,case.reason,case.delegate_calls)  # Fixed BEFORE target call.
    paths,pin=fixture.prepare(case,official_pin)
    inputs=target.module.discover_inputs(fixture.work)
    if any(getattr(inputs,name)!=path for name,path in paths.items()):
        raise RuntimeError('Actual discovery differs from independently constructed file paths')
    before=snapshot(paths,fixture.work);calls_before=target.calls
    if len(before['file_inventory'])!=5 or any(v is None for v in before['digests'].values()):
        raise RuntimeError('Fixture setup failed; not credited as rejection')
    result=None;stage='accepted';reason=''
    try:
        result=target(inputs,pin);observed=True
    except ManifestTrustError as error:
        observed=False;stage='root';reason=error.code
    except target.module.ArtifactIntegrityError as error:
        observed=False;reason=str(error);stage='child_hash' if 'Input hash mismatch for ' in reason else 'schema'
    after=snapshot(paths,fixture.work)
    record={'case':case.name,'group':case.group,'action':case.action,'expected_accept':expected[0],
            'observed_accept':observed,'expected_stage':expected[1],'observed_stage':stage,
            'observed_reason':reason,'expected_delegate_calls':expected[3],
            'observed_delegate_calls':target.calls-calls_before,
            'expected_external_anchor':pin,'precall_input_digests':before['digests'],
            'manifest_matches_external_anchor_before_call':before['digests']['manifest']==pin,
            'all_five_input_files_and_inventory_unchanged':before==after}
    if records is not None:records.append(record)
    if before!=after:raise ContractMismatch('input_preservation',case.name,'all requested files unchanged','modified')
    if observed!=expected[0]:raise ContractMismatch('verdict',case.name,expected[0],observed)
    if stage!=expected[1] or expected[2] not in reason:
        raise ContractMismatch('rejection_reason',case.name,(expected[1],expected[2]),(stage,reason))
    if target.calls-calls_before!=expected[3]:
        raise ContractMismatch('admission_order',case.name,expected[3],target.calls-calls_before)
    if observed:
        wanted_hashes={('simulation_manifest' if name=='manifest' else name):value for name,value in before['digests'].items()}
        counts=(len(result.scalar),len(result.seeds),result.rho_values,result.branches,result.b_c,result.t_star)
        wanted=(800,40,RHOS,BRANCHES,B_C,T_STAR)
        if counts!=wanted or result.seeds!=SEEDS or result.input_hashes!=wanted_hashes:
            raise ContractMismatch('accepted_result',case.name,'pre-call cohort/count/hash facts match',counts)
        if result is not target.last_result:
            raise ContractMismatch('result_identity',case.name,'exact actual validate_run result','replaced')
        record.update(returned_scalar_rows=800,returned_seed_count=40,reported_input_hashes_match_precall=True,
                      exact_delegated_object_returned=True)
    return record
