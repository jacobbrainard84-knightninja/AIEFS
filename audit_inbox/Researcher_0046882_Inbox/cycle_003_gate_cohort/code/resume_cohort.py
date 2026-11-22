"""Researcher0046882 / DIRECTION-2 / UNVERIFIED. Shared header: ../HEADER.txt.
Execution-only recovery driver; full source driver retained separately; source inspected helpers from cycle002 in common.py.
No main repository edits. Optional --scratch specifies an existing scratch parent.
"""
from pathlib import Path
import argparse, copy, csv, hashlib, json, os, platform, sys, tempfile, time, traceback
import numpy as np
import common as C
P=C.ROOT; M=C.META

def dump(path,obj): C.dump(path,obj)

def ah(a):
    return {'dtype':a.dtype.str,'shape':list(a.shape),'order':'C','sha256':hashlib.sha256(a.tobytes(order='C')).hexdigest(),'nbytes':a.nbytes}

def desc(v):
    out=C.distribution(v)
    out['mean']=float(np.mean(v)) if v.size else None
    return out

def append_vectors(scratch,group,window,vectors):
    root=scratch/'pools'/group/window;root.mkdir(parents=True,exist_ok=True)
    for name,a in vectors.items():
        with (root/(name+'.bin')).open('ab') as f: np.asarray(a,dtype='<f8').tofile(f)

def vecstats(path,event=False):
    if not path.exists() or path.stat().st_size==0:return C.distribution(np.array([]))
    a=np.memmap(path,dtype='<f8',mode='r')
    if event:a=a[a>M['event_threshold']]
    out=C.distribution(a)
    del a
    return out

def pool(scratch,group,window,rows):
    root=scratch/'pools'/group/window
    out={}
    for name in ['steps','gated_steps','projection_active_steps','zero_load_bystander_rowsteps_excluded']:
        out[name]=sum(x[name] for x in rows)
    out['gated_fraction']=C.ratio(out['gated_steps'],out['steps'])
    out['projection_active_fraction']=C.ratio(out['projection_active_steps'],out['steps'])
    for label,key in [('binding_rows_per_gated_step','bc'),('bystander_rows_per_gated_step','yc'),
                      ('own_scale_deficit_binding','b'),('extra_neighbor_loss_binding','e')]:
        out[label]=vecstats(root/(key+'.bin'))
    for label,key in [('spillover','d'),('bystander_loss','l')]:
        r={k:sum(x[label][k] for x in rows) for k in ['eligible_rowsteps','events','gated_steps_with_event']}
        r['row_frequency']=C.ratio(r['events'],r['eligible_rowsteps'])
        r['gated_step_frequency']=C.ratio(r['gated_steps_with_event'],out['gated_steps'])
        r['all_eligible']=vecstats(root/(key+'.bin'));r['event_only']=vecstats(root/(key+'.bin'),True)
        out[label]=r
    vals=[x['decomposition_abs_residual_max'] for x in rows if x['decomposition_abs_residual_max'] is not None]
    out['decomposition_abs_residual_max']=max(vals) if vals else None
    return out

def future_desc(seed,o):
    lo,hi=M['windows']['future']; sc=o.scale[lo:hi];q=o.pre[lo:hi]
    bm=(sc<1)&o.gated[lo:hi,None]
    bc=np.sum(bm,axis=1).astype(np.uint8); ms=np.min(sc,axis=1)
    spread=np.max(np.where(bm,q,-np.inf),axis=1)-np.min(np.where(bm,q,np.inf),axis=1)
    spread[bc==0]=np.nan
    valid=spread[bc>0];C.check_finite(valid,ms)
    path=P/'descriptors'/f'future_{seed}.npz'
    arrays={'binding_count':bc,'min_scale':ms,'binding_load_spread':spread,
            'pre_violation':o.gated[lo:hi], 'metadata_json':np.array(json.dumps(M))}
    np.savez_compressed(path,**arrays)
    return {'binding_count':desc(bc),'binding_count_histogram_0_to_12':np.bincount(bc,minlength=13).tolist(),
            'min_scale':desc(ms),'binding_load_spread':desc(valid),
            'binding_load_spread_over_capacity':desc(valid/o.cap),'missing_spread_steps':int(np.sum(bc==0)),
            'array_hashes':{k:ah(v) for k,v in arrays.items() if k!='metadata_json'}}

def exact_dict(a,b):
    if isinstance(a,dict):return a.keys()==b.keys() and all(exact_dict(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(exact_dict(x,y) for x,y in zip(a,b))
    return a==b

def main():
    # Execution-only recovery: preserve declared cohort and recompute aggregates from checked raw.
    oldenv=json.loads((P/'evidence/attempt1_environment.json').read_text())
    oldrows=json.loads((P/'evidence/attempt1_per_seed_summary.json').read_text())['per_seed']
    oldhashes=json.loads((P/'evidence/attempt1_raw_array_hashes.json').read_text())['seeds']
    oldscratch=Path(oldenv['temporary_cache'])
    completed=len(oldrows)
    assert list(oldrows)==[str(x) for x in M['seed_list'][:completed]]
    assert list(oldhashes)==list(oldrows)
    print('RECOVERY: first',completed,'seeds have durable summaries; validate each cached array before reuse. First seed rerun for noninterference.',flush=True)
    parser=argparse.ArgumentParser();parser.add_argument('--scratch',default=str(Path.home()/'.cache'/'r0046882'));args=parser.parse_args()
    scratch_parent=Path(args.scratch);scratch_parent.mkdir(parents=True,exist_ok=True)
    scratch=Path(tempfile.mkdtemp(prefix='cycle003_',dir=scratch_parent));(scratch/'raw').mkdir()
    start=time.perf_counter();ph=(P/'PROTOCOL.sha256').read_text().split()[0]
    assert C.hfile(P/'PROTOCOL.md')==ph
    manifest=json.loads((P/'inputs/production_manifest.json').read_text())
    assert C.hfile(P/'inputs/production_manifest.json')==M['manifest_sha256']
    assert M['seed_list']==manifest['randomization']['paired_seeds'] and len(M['seed_list'])==40
    dump('evidence/environment.json',{'metadata':M,'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),
        'command':'python -u code/resume_cohort.py','recovery_source':str(oldscratch),'recovered_seed_count':completed,'temporary_cache':str(scratch),'protocol_sha256':ph,
        'thread_environment':{k:os.getenv(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']}})
    print('PREDECLARED',ph,'K40',M['seed_list'],flush=True)
    C.controls()
    orig=C.load_engine('r0046882_original','engine_original.py',M['original_engine_sha256'])
    inst=C.load_engine('r0046882_instrumented','engine_instrumented.py',M['instrumented_engine_sha256'])
    cfg,proto,_=C.configure(orig,manifest)
    import dataclasses
    dump('evidence/configuration.json',{'model':dataclasses.asdict(cfg),'protocol':dataclasses.asdict(proto),'metadata':M})
    pilot_hashes=json.loads((P/'inputs/pilot_array_hashes.json').read_text())
    pilot_summary=json.loads((P/'inputs/pilot_summary.json').read_text())
    print('ORIGINAL first seed start',flush=True)
    original,ho=C.simulate(orig,M['seed_list'][0],manifest)
    perseed={}; hashes={}; descriptors={};pilotchecks={};traces={}
    for index,seed in enumerate(M['seed_list']):
        print('START',index+1,seed,flush=True)
        o=C.Observer(80000,12)
        if 0 < index < completed:
            with np.load(oldscratch/'raw'/f'seed_{seed}.npz',allow_pickle=False) as z:
                for key,ref in oldhashes[str(seed)].items():
                    got=ah(z[key])
                    assert got==ref,('recovery raw mismatch',seed,key)
                o.pre[:]=z['row_sum_pre'];o.post[:]=z['r_post'];o.scale[:]=z['scale']
                o.gated[:]=z['pre_violation'];o.active[:]=z['projection_active'];o.cap=float(z['capacity']);o.k=80000
            result=None
            trace={'status':'reused hash-validated raw observations; state stream digest not durably saved before attempt1 log failure'}
            print('REUSED verified raw',seed,flush=True)
        else:
            result,trace=C.simulate(inst,seed,manifest,o)
        traces[str(seed)]=trace
        assert o.k==80000
        if index==0:
            a,b,bad=C.exact_compare(original,result)
            matched=not bad and ho==trace
            dump('evidence/no_instrumentation.json',{'metadata':M,'status':'PASS' if matched else 'INVALID',
              'compared_leaves':len(a),'mismatched_leaves':bad,'original_trace':ho,'instrumented_trace':trace})
            np.savez_compressed(P/'evidence/original_outputs.npz',**a)
            np.savez_compressed(P/'evidence/instrumented_outputs.npz',**b)
            assert matched,'STOP: instrumentation mismatch'
            # Real comparator negative control, not just a standalone byte inequality.
            changed=copy.deepcopy(result);changed['final_state']['B'].reshape(-1).view(np.uint64)[0]^=np.uint64(1)
            assert C.exact_compare(original,changed)[2], 'one-bit corruption not rejected'
            del original,a,b,changed
            print('NONINTERFERENCE PASS 101 leaves +80000-step stream; one-bit mutant rejected',flush=True)
        del result
        arrays={'row_sum_pre':o.pre,'r_post':o.post,'scale':o.scale,'pre_violation':o.gated,
                'projection_active':o.active,'capacity':np.array(o.cap)}
        hashes[str(seed)]={k:ah(v) for k,v in arrays.items()}
        np.savez_compressed(scratch/'raw'/f'seed_{seed}.npz',**arrays)
        if index<4:
            for k,ref in pilot_hashes[str(seed)].items():
                got=hashes[str(seed)][k]
                assert all(got[f]==ref[f] for f in ['sha256','dtype','shape']),('pilot mismatch',seed,k)
        rows={}
        for window,(lo,hi) in M['windows'].items():
            pre=o.pre[lo:hi];sc=o.scale[lo:hi];post=o.post[lo:hi];gate=o.gated[lo:hi]
            rows[window]=C.summarize(pre,sc,post,gate,o.active[lo:hi],o.cap)
            bm,ym,d,l,base,extra=C.metrics(pre[gate],sc[gate],post[gate],o.cap)
            vec={'d':d,'l':l,'b':base,'e':extra,'bc':np.sum(bm,axis=1),'yc':np.sum(sc[gate]==1,axis=1)}
            append_vectors(scratch,'full40',window,vec)
            if index<4:append_vectors(scratch,'pilot4',window,vec)
        if index < completed:
            assert exact_dict(rows,oldrows[str(seed)]),('recovery summary mismatch',seed)
        perseed[str(seed)]=rows
        descriptors[str(seed)]=future_desc(seed,o)
        if index<4:
            same=exact_dict(rows,pilot_summary['per_seed'][str(seed)])
            assert same,('pilot summary mismatch',seed)
            pilotchecks[str(seed)]={'raw_arrays_match':True,'all_window_summaries_match':True}
        # Durable incremental evidence; a crash is explicitly incomplete, never a successful smaller cohort.
        dump('evidence/per_seed_summary.json',{'metadata':M,'status':'IN_PROGRESS','per_seed':perseed})
        dump('evidence/raw_array_hashes.json',{'metadata':M,'hash_definition':'SHA256 of contiguous C-order bytes, dtype/shape separately recorded','seeds':hashes})
        dump('evidence/future_descriptors.json',{'metadata':M,'seeds':descriptors})
        f=rows['future'];print('DONE',index+1,seed,'future d/l events',f['spillover']['events'],f['bystander_loss']['events'],flush=True)
        del o,arrays
    dump('evidence/pilot_check.json',{'metadata':M,'per_seed':pilotchecks,'status':'PASS'})
    dump('evidence/state_trace_hashes.json',{'metadata':M,'seeds':traces})
    print('ALL40 SIMULATIONS COMPLETE; exact pooled quantiles next',flush=True)
    pools={}
    for group,seeds in [('full40',M['seed_list']),('pilot4',M['pilot_seeds'])]:
        pools[group]={}
        for window in M['windows']:
            pools[group][window]=pool(scratch,group,window,[perseed[str(seed)][window] for seed in seeds])
            print('POOL',group,window,'complete',flush=True)
    assert exact_dict(pools['pilot4'],pilot_summary['pooled']),'pilot pooled summary mismatch'
    dump('evidence/pooled_summary.json',{'metadata':M,'groups':pools})
    dump('evidence/per_seed_summary.json',{'metadata':M,'status':'COMPLETE_40; UNVERIFIED by seats','per_seed':perseed})
    columns=['seed_index','seed','pilot','window','steps','gated_steps','gated_fraction','binding_eligible','binding_events','binding_event_frequency','max_d',
       'bystander_eligible','bystander_events','bystander_event_frequency','max_l','binding_gated_steps_with_event','bystander_gated_steps_with_event',
       'zero_load_bystanders','b_median','b_max','e_median','e_max']
    with (P/'evidence/per_seed_windows.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for idx,seed in enumerate(M['seed_list']):
            for name,r in perseed[str(seed)].items():
                d=r['spillover'];l=r['bystander_loss'];bb=r['own_scale_deficit_binding'];ee=r['extra_neighbor_loss_binding']
                w.writerow(dict(zip(columns,[idx+1,str(seed),idx<4,name,r['steps'],r['gated_steps'],r['gated_fraction'],d['eligible_rowsteps'],d['events'],d['row_frequency'],d['all_eligible']['max'],
                  l['eligible_rowsteps'],l['events'],l['row_frequency'],l['all_eligible']['max'],d['gated_steps_with_event'],l['gated_steps_with_event'],r['zero_load_bystander_rowsteps_excluded'],bb['median'],bb['max'],ee['median'],ee['max']])))
    groups={label:[] for label in ['any_event','no_event','binding_event','bystander_event']}
    for seed in M['seed_list']:
        f=perseed[str(seed)]['future'];d=f['spillover']['events']>0;l=f['bystander_loss']['events']>0
        groups['any_event' if d or l else 'no_event'].append(seed)
        if d:groups['binding_event'].append(seed)
        if l:groups['bystander_event'].append(seed)
    comparisons={}
    for metric in ['binding_count','min_scale','binding_load_spread','binding_load_spread_over_capacity']:
        for stat in ['median','max']:
            vals={g:[descriptors[str(seed)][metric][stat] for seed in groups[g] if descriptors[str(seed)][metric][stat] is not None] for g in ['any_event','no_event']}
            ranges={g:{'min':min(v),'max':max(v),'n':len(v)} if v else None for g,v in vals.items()}
            e,n=ranges['any_event'],ranges['no_event'];separation='not_evaluable'
            if e and n:
                separation='event_lower' if e['max']<n['min'] else ('event_higher' if n['max']<e['min'] else 'overlap_or_touch')
            comparisons[metric+'/'+stat]={'ranges':ranges,'strict_range_separation':separation}
    dump('evidence/associations.json',{'metadata':M,'groups':groups,'comparisons':comparisons,'interpretation':'Descriptive observed associations only; cause UNEXPLAINED'})
    print('FUTURE EVENT GROUPS',json.dumps(groups),flush=True)
    print('ALL',json.dumps(pools['full40']['all']),flush=True)
    dump('evidence/completion.json',{'metadata':M,'status':'COMPLETE_40','measured_steps':3200000,'elapsed_seconds':time.perf_counter()-start,
        'pilot_pool_match':True,'scratch_path':str(scratch),'raw_npz_retention':'temporary cache only, not delivered or guaranteed persistent'})
    print('COMPLETE seconds',time.perf_counter()-start,flush=True)

if __name__=='__main__':
    try:main()
    except Exception:
        dump('evidence/FAILURE.json',{'status':'INVALID_OR_INCOMPLETE','metadata':M,'traceback':traceback.format_exc()})
        traceback.print_exc();raise
