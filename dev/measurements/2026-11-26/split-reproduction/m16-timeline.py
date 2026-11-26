import json,sys,re,os,glob
D='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/subagents/'
S=os.path.dirname(os.path.abspath(__file__))
idx=json.load(open(S+'/m16-index.json'))
disp={x['id']:x for x in idx['dispatch'] if 'id' in x and x.get('ts')}
metas={}
for m in glob.glob(D+'*.meta.json'):
    j=json.load(open(m))
    if j.get('toolUseId') in disp and re.search(r'451|T2[5-9]\d|T250',j.get('description') or '') and (disp[j['toolUseId']]['ts'] or '')>='2026-11-24':
        metas[j['toolUseId']]=m.replace('.meta.json','.jsonl')
WR=[r"""\bp\s*=\s*['"]([^'"\n]+)['"]""",r"""cat\s*>>?\s*([^\s<;&|]+)""",r"""open\(['"]([^'"]+)['"],\s*['"][wa]""",r"""sed -i[^;|&]*?\s([\w./-]+\.\w+)\s*(?:;|&&|$)""",r"""(?:^|\s)>\s*((?:rust|scripts|tests|docs|\.claude|l7r|dev|research)/[^\s;&|]+)""",r"""git (?:mv|apply|checkout|restore|show [^>]*>)\s*([^\s;&|]+)"""]
def writes(cmd):
    out=[]
    for r in WR:
        for m in re.finditer(r,cmd): out.append(m.group(1))
    if 'apply_patch' in cmd or 'patch -p' in cmd: out.append('PATCH')
    return out
def short(name,i):
    if name in('Edit','Write','Read'): return i.get('file_path','').replace('/diagram/.clones/','')
    if name=='Bash': return (('[bg] ' if i.get('run_in_background') else '')+i.get('command','').replace('\n',' ; '))[:260]
    if name=='Agent': return '%s | %s'%(i.get('subagent_type'),i.get('description'))
    return json.dumps(i)[:160]
out={}
for tid,p in metas.items():
    ev=[];pend={}
    final=''
    for line in open(p):
        try:d=json.loads(line)
        except: continue
        ts=d.get('timestamp'); c=(d.get('message') or {}).get('content')
        if d.get('type')=='attachment':
            at=d.get('attachment') or {}
            if at.get('type')=='queued_command' and 'task-notification' in str(at.get('prompt')):
                m=re.search(r'<summary>(.*?)</summary>',str(at.get('prompt')),re.S); ev.append(dict(ts=ts,k='notif',s=(m.group(1) if m else '')))
            continue
        if isinstance(c,str):
            if 'task-notification' in c:
                m=re.search(r'<summary>(.*?)</summary>',c,re.S); ev.append(dict(ts=ts,k='notif',s=(m.group(1) if m else c[:120])))
            continue
        for b in c or []:
            if b.get('type')=='server_tool_use' and b.get('name')=='advisor':
                e=dict(ts=ts,k='advisor',s='advisor'); pend[b['id']]=e; ev.append(e); continue
            if b.get('type')=='advisor_tool_result':
                e=pend.get(b.get('tool_use_id'))
                if e: e['end']=ts
                continue
            if b.get('type')=='tool_use':
                e=dict(ts=ts,k=b['name'],s=short(b['name'],b['input']))
                if b['name']=='Bash': e['w']=writes(b['input'].get('command',''))
                if b['id'] in pend: continue
                pend[b['id']]=e; ev.append(e)
            elif b.get('type')=='tool_result':
                e=pend.get(b.get('tool_use_id'))
                if e:
                    e['end']=ts
                    t=b.get('content'); t=t if isinstance(t,str) else ' '.join(x.get('text','') for x in t if isinstance(x,dict))
                    e['r']=t[-200:].replace('\n',' ; ')
            elif b.get('type')=='text':
                if d.get('type')=='assistant': final=b['text']; ev.append(dict(ts=ts,k='say',s=b['text'][:200].replace('\n',' ')))
                elif 'task-notification' in b.get('text',''):
                    m=re.search(r'<summary>(.*?)</summary>',b['text'],re.S); ev.append(dict(ts=ts,k='notif',s=(m.group(1) if m else '')))
    out[tid]=dict(desc=disp[tid]['desc'],start=disp[tid]['ts'],prompt=disp[tid]['prompt'],events=ev,final=final,path=p)
json.dump(out,open(S+'/m16-builders.json','w'))
for tid,o in sorted(out.items(),key=lambda kv:kv[1]['start']):
    ev=o['events']; print(o['start'][:16],o['desc'],len(ev),ev[0]['ts'][11:16] if ev else '',ev[-1]['ts'][11:16] if ev else '',len(o['final']))
