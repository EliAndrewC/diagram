import json,sys,glob,os
P=os.path.expanduser('~/.claude/projects/-diagram/')
out=[];results={}
for f in glob.glob(P+'*.jsonl'):
    sess=os.path.basename(f)[:8]
    for line in open(f,errors='replace'):
        if '"Agent"' not in line and '"Task"' not in line and 'tool_result' not in line: continue
        try: r=json.loads(line)
        except Exception: continue
        ts=r.get('timestamp') or ''
        m=r.get('message') or {}
        c=m.get('content')
        if not isinstance(c,list): continue
        for b in c:
            if not isinstance(b,dict): continue
            if b.get('type')=='tool_use' and b.get('name') in('Agent','Task') and '2026-11-20'<=ts[:10]<='2026-11-27':
                i=b.get('input') or {}
                out.append({'sess':sess,'id':b.get('id'),'ts':ts,'type':i.get('subagent_type',''),'model':i.get('model',''),'desc':i.get('description',''),'prompt':i.get('prompt','')})
            elif b.get('type')=='tool_result':
                tr=r.get('toolUseResult')
                if isinstance(tr,dict) and tr.get('agentId'):
                    results[b.get('tool_use_id')]=tr.get('agentId')
for d in out: d['agent']=results.get(d['id'])
json.dump(out,open('t353-dispatches.json','w'))
print(len(out), sum(1 for d in out if d['agent']))
