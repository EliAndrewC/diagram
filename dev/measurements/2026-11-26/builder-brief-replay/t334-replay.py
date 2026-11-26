import json,re,subprocess,os,tempfile,sys,collections
HOOK='/diagram/.clones/diagram-backlog-t271/tests/hooks/builder-brief-hooks.sh'
d=[x for x in json.load(open('t334-dispatches.json')) if (x['ts'] or '').startswith('2026-11-26')]
pool=re.compile(r'/diagram/\.clones/diagram-backlog-(?:t\d+|b\d+)(?![A-Za-z0-9_-])')
trees=sorted({m for x in d for m in pool.findall(x['prompt'])})
W=tempfile.mkdtemp(prefix='t334-replay-')
os.makedirs(W+'/m/.clones/c/.git'); os.makedirs(W+'/h')
json.dump({'trees':[{'tree':t,'feature':'','tasks':[],'since':''} for t in trees]},open(W+'/m/.clones/c/.git/builder-pool.json','w'))
env=dict(os.environ,GUARD_LOG_DIR=W+'/log',CLONE_MAIN=W+'/m',HOME=W+'/h')
rows=[];by=collections.Counter()
for x in d:
    inp=json.dumps({'cwd':W+'/m/.clones/c','tool_name':'Agent','tool_input':{'subagent_type':x['type'],'model':x['model'],'prompt':x['prompt'],'description':x['desc']}})
    p=subprocess.run([HOOK,'pretool'],input=inp,capture_output=True,text=True,env=env)
    out=(p.stdout+p.stderr)
    rule='pass'
    if p.returncode==2:
        rule='no-marker' if 'has no BUILDER-BRIEF line' in out else out.strip().split('\n')[0][:80]
    by[(rule,x['type'] or '-')]+=1
    rows.append((x['ts'],x['type'] or '-',rule,x['desc']))
print('fixture pool trees:',len(trees),[t.split('-')[-1] for t in trees])
print('dispatches 2026-11-26 UTC:',len(d)); print(by)
with open('t334-replay.tsv','w') as f:
    for r in rows: f.write('\t'.join(r)+'\n')
for r in rows:
    if r[2]!='pass': print(r[0][11:16],r[2],'|',r[3])
