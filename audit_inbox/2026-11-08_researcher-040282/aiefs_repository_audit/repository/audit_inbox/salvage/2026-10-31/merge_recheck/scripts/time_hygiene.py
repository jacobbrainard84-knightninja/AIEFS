import subprocess,time,sys,resource
runs={'default':[],'pii':['--pii'],'pii_big':['--pii','--max-scan-mb','1000']}
L='/workspace/merge_recheck/logs/ci_9053b77/'
with open(L+'hyg_timing.txt','w') as out:
    for k,a in runs.items():
        t=time.time(); r=subprocess.run([sys.executable,'tools/ci/hygiene_scan.py',*a],capture_output=True,text=True)
        dt=time.time()-t; open(L+f'hyg_{k}.log','w').write(r.stdout+r.stderr)
        line=f'{k} args={a} exit={r.returncode} seconds={dt:.1f}'; print(line); out.write(line+'\n')
    print('max child RSS MiB', resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024); out.write(f'max child RSS MiB {resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024:.0f}\n')
