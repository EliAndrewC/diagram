import json,re
from datetime import datetime
P='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
T=lambda s: datetime.fromisoformat(s.replace('Z','+00:00'))
pend={};out=[]
for line in open(P):
    if 'carry' not in line and 'cherry-pick' not in line and 'tool_result' not in line: continue
    try:d=json.loads(line)
    except: continue
    ts=d.get('timestamp'); c=(d.get('message') or {}).get('content')
    if not ts or not isinstance(c,list) or ts<'2026-11-25T16': continue
    for b in c:
        if b.get('type')=='tool_use' and b.get('name')=='Bash' and re.search(r'make (-C \S+ )?carry|git[^;|&]*cherry-pick',b['input'].get('command','')):
            pend[b['id']]=(ts,b['input']['command'][:160].replace('\n',' '))
        elif b.get('type')=='tool_result' and b.get('tool_use_id') in pend:
            t0,cmd=pend.pop(b['tool_use_id']); t=b.get('content'); t=t if isinstance(t,str) else ' '.join(x.get('text','') for x in t if isinstance(x,dict))
            out.append((t0,round((T(ts)-T(t0)).total_seconds(),1),cmd,('conflict' in t.lower() or 'CONFLICT' in t),t[-120:].replace('\n',' ')))
print(len(out))
import statistics as st
print('median s',st.median(o[1] for o in out),'conflicts',sum(o[3] for o in out))
for o in out: print(o[0][5:16],o[1],o[3],o[2][:110])
