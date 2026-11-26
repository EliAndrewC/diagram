# Replays today's `make decide` (the lint and the approach gate) over a historical section, in a scratch tree.
import json,collections,os,subprocess,sys,re
S=os.path.dirname(os.path.abspath(__file__))
W=os.environ.get('T308_TREE','/diagram/.clones/diagram-backlog-t271')
D=W+'/specs/451-time-retro-and-efficiency/'
rows=json.load(open(S+'/t308-rounds.json'))
by=collections.defaultdict(list)
for x in rows:
    if x['first']<'2026-11-26T19:42': by[x['task']].append(x)
def replay(task,i,request=None):
    sec=by[task][i]['sec']
    if not sec: return None
    R=f'{S}/t308-replay/{task}-{i}'
    d=R+'/specs/451-t308-replay'
    os.makedirs(d,exist_ok=True)
    open(d+'/plan.md','w').write('# plan\n\n## Task sections\n\n'+sec.rstrip('\n')+'\n')
    open(d+'/request.md','w').write(request if request is not None else open(D+'request.md').read())
    open(d+'/tasks.md','w').write(open(D+'tasks.md').read())
    if not os.path.exists(R+'/.git'): subprocess.run(['git','init','-q',R])
    p=subprocess.run([W+'/scripts/gates/l7r-gate.sh','plan','decide','451',task],cwd=R,capture_output=True,text=True)
    return p.returncode,p.stdout,p.stderr
if __name__=='__main__':
    for a in sys.argv[1:]:
        t,i=a.split(':'); r=replay(t,int(i))
        print('#####',a,r[0]); print(r[1][:300]); print(r[2][:int(os.environ.get('N','2500'))])

def all_first():
    from concurrent.futures import ThreadPoolExecutor
    keys=[(t,0) for t in by if not t.startswith('blocks') and by[t][0]['sec']]
    keys+=[(t,i) for t in by for i in range(1,len(by[t])) if not t.startswith('blocks') and by[t][i]['sec']]
    with ThreadPoolExecutor(8) as ex: res=list(ex.map(lambda k:replay(*k),keys))
    out={f'{t}:{i}':dict(code=r[0],err=r[2]) for (t,i),r in zip(keys,res)}
    json.dump(out,open(S+'/t308-replay.json','w'),indent=0)
    return out
