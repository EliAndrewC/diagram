# T308-D1 replayed with the RULE AS BUILT (`l7r-gate plan decide`, lint/task_line.rs), not t308-gmwords.py's Python sketch of it:
# each task's round-1 section in a scratch tree whose tasks.md is today's tasks.md + tasks-done*.md and whose request.md is
# (i) the one committed before the task's first round, (ii) the one its surviving review bundle holds (the last round's).
import json,collections,os,subprocess,glob,re
from concurrent.futures import ThreadPoolExecutor
S=os.path.dirname(os.path.abspath(__file__))
W='/diagram/.clones/diagram-backlog-t271'; F='specs/451-time-retro-and-efficiency/'
rows=[x for x in json.load(open(S+'/t308-rounds.json')) if x['first']<'2026-11-26T19:42']
by=collections.defaultdict(list)
for x in rows: by[x['task']].append(x)
TASKS=open(W+'/'+F+'tasks.md').read()+''.join(open(f).read() for f in sorted(glob.glob(W+'/'+F+'tasks-done*.md')))
def req_at(ts):
    c=subprocess.run(['git','-C',W,'log','-1','--format=%H','--before='+ts,'--',F+'request.md'],capture_output=True,text=True).stdout.strip()
    return subprocess.run(['git','-C',W,'show',c+':'+F+'request.md'],capture_output=True,text=True).stdout
def run(task,tag,request):
    sec=by[task][0]['sec']
    R=f'{S}/t308-replay/{task}-d1{tag}'; d=R+'/specs/451-t308-replay'
    os.makedirs(d,exist_ok=True)
    open(d+'/plan.md','w').write('# plan\n\n## Task sections\n\n'+sec.rstrip('\n')+'\n')
    open(d+'/request.md','w').write(request); open(d+'/tasks.md','w').write(TASKS)
    if not os.path.exists(R+'/.git'): subprocess.run(['git','init','-q',R])
    p=subprocess.run([W+'/scripts/gates/l7r-gate.sh','plan','decide','451',task],cwd=R,capture_output=True,text=True)
    return re.findall(r"line of tasks\.md: '([^\n]*)",p.stdout+p.stderr)
def one(task):
    if not by[task][0]['sec']: return task,None,None
    a=run(task,'c',req_at(by[task][0]['first']))
    b=None
    f='/tmp/l7r-check/plan-451-time-retro-and-efficiency-'+task+'/request.md'
    if os.path.exists(f): b=run(task,'b',open(f).read())
    return task,a,b
keys=[t for t in by if not t.startswith('blocks')]
with ThreadPoolExecutor(8) as ex: res=list(ex.map(one,keys))
n=[r for r in res if r[1] is not None]
print('tasks replayed',len(n),'with a bundle request.md',sum(1 for r in n if r[2] is not None))
print('fires, request.md as committed before round 1:',sum(1 for r in n if r[1]))
print('fires, request.md of the surviving bundle:',sum(1 for r in n if r[2]))
for t,a,b in n:
    if a or b: print(t,[ (r['verdict']) for r in by[t]],'| committed:',len(a),[q[:70] for q in a],'| bundle:',None if b is None else (len(b),[q[:70] for q in b]))
