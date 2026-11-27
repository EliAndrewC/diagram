# t373: the dirty test's price in the sandbox clone, 20 runs each after 2 warm-ups, GIT_OPTIONAL_LOCKS=0, interleaved. ms.
import subprocess,time,statistics,os,sys
S=os.path.dirname(os.path.abspath(__file__)); C=S+'/w/diagram/.clones/diagram-backlog'; F=C+'/dev/measurements/2026-11-26/tmp-clutter/t365-glob.txt'
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
cmds={'status --porcelain (today)':['status','--porcelain'],'status --porcelain -uno (tracked only)':['status','--porcelain','-uno'],
      'diff-index --quiet HEAD -- (tracked only)':['diff-index','--quiet','HEAD','--'],'ls-files --others --exclude-standard (untracked only)':['ls-files','--others','--exclude-standard']}
def q(v,p): v=sorted(v); return v[min(len(v)-1,int(round(p*(len(v)-1))))]
for state in ('dirty (one tracked file changed)','clean'):
    subprocess.run(['git','-C',C,'checkout','-q','--','dev/measurements/2026-11-26/tmp-clutter/t365-glob.txt'],check=True)
    if state.startswith('dirty'): open(F,'a').write('t373 dirty\n')
    res={k:[] for k in cmds}
    for i in range(22):
        for k,a in cmds.items():
            t=time.perf_counter(); r=subprocess.run(['git','-C',C,*a],capture_output=True,env=env); dt=(time.perf_counter()-t)*1e3
            if i>=2: res[k].append(dt); rc=r.returncode
            res.setdefault(k+'#',[]).append((r.returncode,len(r.stdout)))
    for k in cmds: print(f'{state:34s} {k:55s} median_ms={statistics.median(res[k]):6.1f} p90_ms={q(res[k],0.9):6.1f} exit,bytes={res[k+"#"][-1]}')
subprocess.run(['git','-C',C,'checkout','-q','--','dev/measurements/2026-11-26/tmp-clutter/t365-glob.txt'],check=True)
print('load1',open('/proc/loadavg').read().split()[0])
