# 451 T353: every Agent dispatch of the week (t353-dispatches.json) through the built builder-brief guard, on a fixture pool of the
# pool trees the prompts name, all free; each stop-point-no-marker refusal joined to whether its agent wrote (t353-week.tsv).
import json,re,subprocess,os,tempfile,collections,sys
HOOK=sys.argv[1]
d=json.load(open('t353-dispatches.json'))
pool=re.compile(r'/diagram/\.clones/diagram-backlog-(?:t\d+|b\d+)(?![A-Za-z0-9_-])')
trees=sorted({m for x in d for m in pool.findall(x['prompt'])})
W=tempfile.mkdtemp(prefix='t353-replay-')
os.makedirs(W+'/m/.clones/c/.git'); os.makedirs(W+'/h')
json.dump({'trees':[{'tree':t,'feature':'','tasks':[],'since':''} for t in trees]},open(W+'/m/.clones/c/.git/builder-pool.json','w'))
env=dict(os.environ,GUARD_LOG_DIR=W+'/log',CLONE_MAIN=W+'/m',HOME=W+'/h')
wrote={}
for l in open('t353-week.tsv'):
    f=l.rstrip('\n').split('\t'); wrote[(f[0],f[5])]=f[2]
by=collections.Counter()
for x in d:
    inp=json.dumps({'cwd':W+'/m/.clones/c','tool_name':'Agent','tool_input':{'subagent_type':x['type'],'prompt':x['prompt'],'description':x['desc']}})
    p=subprocess.run([HOOK,'pretool'],input=inp,capture_output=True,text=True,env=env)
    out=p.stdout+p.stderr
    rule='pass' if p.returncode!=2 else ('stop-point-no-marker' if 'a STOP POINT line and no BUILDER-BRIEF' in out else ('no-marker' if 'has no BUILDER-BRIEF line' in out else out.strip().split('\n')[0][:60]))
    if rule=='stop-point-no-marker':
        by[(rule,wrote.get((x['ts'][:16],x['desc'][:60]),'?'))]+=1
    else: by[(rule,)]+=1
for k,v in sorted(by.items()): print(v,*k,sep='\t')
