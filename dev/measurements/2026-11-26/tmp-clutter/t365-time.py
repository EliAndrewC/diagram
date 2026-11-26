# t365: time a command N times under the default TMPDIR and an empty one, alternating; median and 90th centile, ms.
import subprocess,time,os,sys,statistics,json
label,n,stdin_file=sys.argv[1],int(sys.argv[2]),sys.argv[3]; cmd=sys.argv[4:]
E='/tmp/t365-tmp/e'
res={'default':[],'empty':[]}; loads=[]
def run(mode):
    env=dict(os.environ); env.pop('TMPDIR',None)
    if mode=='empty': env['TMPDIR']=E
    inp=open(stdin_file,'rb') if stdin_file!='-' else subprocess.DEVNULL
    t=time.perf_counter(); r=subprocess.run(cmd,stdin=inp,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env); dt=(time.perf_counter()-t)*1e3
    return dt,r.returncode
run('default'); run('empty')  # warm-up, not counted
rcs=set()
for i in range(n):
    loads.append(float(open('/proc/loadavg').read().split()[0]))
    for mode in (('default','empty') if i%2==0 else ('empty','default')):
        dt,rc=run(mode); res[mode].append(dt); rcs.add(rc)
def q(v,p): v=sorted(v); return v[min(len(v)-1,int(round(p*(len(v)-1))))]
for m in res:
    v=res[m]; print(f"{label} {m:7s} n={len(v)} median_ms={statistics.median(v):.1f} p90_ms={q(v,0.9):.1f} min_ms={min(v):.1f} max_ms={max(v):.1f}")
print(f"{label} load1 min={min(loads)} max={max(loads)} exit_codes={sorted(rcs)} left_in_empty={os.listdir(E)}")
