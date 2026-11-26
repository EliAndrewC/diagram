import json,re,subprocess,os,tempfile
HOOK='/diagram/.clones/diagram-backlog-t271/tests/hooks/builder-brief-hooks.sh'
d=[x for x in json.load(open('t334-dispatches.json')) if (x['ts'] or '').startswith('2026-11-26')]
cases=[('Build 451 T316','T316'),('Build 451 T308','T308'),('Measure then fix: 451 T347','T347'),('Measure 451 T315','T315'),('Build 451 T298','T298'),('Build 451 T285','T285')]
W=tempfile.mkdtemp(prefix='t334-replay2-'); os.makedirs(W+'/m/.clones/c/.git'); os.makedirs(W+'/h')
env=dict(os.environ,GUARD_LOG_DIR=W+'/log',CLONE_MAIN=W+'/m',HOME=W+'/h')
for key,task in cases:
    x=[y for y in d if y['desc'].startswith(key)][0]
    tree=re.search(r'/diagram/\.clones/diagram-backlog-(?:t\d+|b\d+)',x['prompt']).group(0)
    json.dump({'trees':[{'tree':tree,'feature':'451','tasks':[task],'since':''}]},open(W+'/m/.clones/c/.git/builder-pool.json','w'))
    for kind in ['measurement','build-half']:
        prompt=f'BUILDER-BRIEF 451 {task} KIND={kind} JOBS=2 TREE={tree}\n'+x['prompt']
        inp=json.dumps({'cwd':W+'/m/.clones/c','tool_name':'Agent','tool_input':{'subagent_type':'','prompt':prompt}})
        p=subprocess.run([HOOK,'pretool'],input=inp,capture_output=True,text=True,env=env)
        print(task,kind,'rc',p.returncode,(p.stdout+p.stderr).strip().split('\n')[0][:230])
