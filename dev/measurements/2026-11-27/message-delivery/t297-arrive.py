import json,sys
o=json.load(open('t297-sends.json'))
by={}
for r in o:
    k=json.dumps(r['input'],sort_keys=True)
    if r['send'] and k not in by: by[k]=r
rows=sorted([r for r in by.values() if r['send']>='2026-11-26'],key=lambda r:r['send'])
D='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/subagents/'
def brief(b):
    if b.get('type')=='tool_use':
        i=b.get('input',{}); return 'TOOL '+b['name']+': '+str(i.get('command') or i.get('file_path') or i.get('description') or i)[:160]
    if b.get('type')=='text': return 'TEXT: '+b['text'][:300]
    if b.get('type')=='tool_result': return 'RESULT'
    return b.get('type')
for r in rows:
    a=r['input']['to']; msg=r['input']['message']; key=msg[:50]
    print('='*100); print('SEND',r['send'],a,r['input'].get('summary')); print('RESULT',r['result'][:600]); 
    lines=[json.loads(l) for l in open(D+'agent-'+a+'.jsonl')]
    lines=[d for d in lines if d.get('timestamp')]
    print('builder first',lines[0]['timestamp'],'last',lines[-1]['timestamp'],'n',len(lines))
    hit=None
    for i,d in enumerate(lines):
        if key in json.dumps(d.get('message',''))[:200000] and d.get('type')=='user' or (key in json.dumps(d.get('attachment','')) ):
            hit=i;break
    if hit is None:
        for i,d in enumerate(lines):
            if key in json.dumps(d): hit=i;break
    if hit is None: print('NOT FOUND'); continue
    d=lines[hit]
    m=d.get('message') or {}
    c=m.get('content')
    form = 'string' if isinstance(c,str) else [ (b.get('type'), ('has_msg' if key in json.dumps(b) else '')) for b in c] if isinstance(c,list) else 'n/a'
    print('ARRIVE',d['timestamp'],'type',d.get('type'),'keys',[k for k in d.keys() if k not in('message','uuid','parentUuid','sessionId','cwd','gitBranch','version','userType','entrypoint')],'form',form)
    if isinstance(c,list):
        for b in c:
            if key in json.dumps(b):
                s=json.dumps(b); j=s.find(key); print('  CONTEXT:',s[max(0,j-400):j+80])
    # preceding
    for k in range(hit-1,max(hit-6,-1),-1):
        p=lines[k]; pc=(p.get('message') or {}).get('content')
        if isinstance(pc,list): print('  PREV',p['timestamp'],p.get('type'),[brief(b) for b in pc][:2])
    for k in range(hit+1,min(hit+5,len(lines))):
        p=lines[k]; pc=(p.get('message') or {}).get('content')
        if isinstance(pc,list): print('  NEXT',p['timestamp'],p.get('type'),[brief(b) for b in pc][:2])
