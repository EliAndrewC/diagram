#!/usr/bin/env python3
"""m14r: extract builders' final reports (2026-11-25/26 UTC) and what followed. Read-only."""
import json,re,sys
P='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
START=99000  # line index before 2026-11-25
reports=[]; compacts=[]; api_ids=[]  # (line, msgid)
seen_ids=set(); rows=[]; usages=[]; seenrep=set()
def walk(o,out):
    if isinstance(o,str): out.append(o)
    elif isinstance(o,dict):
        for v in o.values(): walk(v,out)
    elif isinstance(o,list):
        for v in o: walk(v,out)
with open(P) as f:
    for i,l in enumerate(f):
        if i<START: continue
        if '"type":"assistant"' not in l and '"type":"user"' not in l and 'compact_boundary' not in l and not ('"type":"attachment"' in l and 'task-notification' in l): continue
        try: d=json.loads(l)
        except Exception: continue
        if d.get('isSidechain'): continue
        t=d.get('type'); ts=d.get('timestamp','')
        if t=='system' and d.get('subtype')=='compact_boundary': compacts.append(i); continue
        if t=='assistant':
            m=d['message']; mid=m.get('id')
            if mid not in seen_ids:
                seen_ids.add(mid); api_ids.append(i); usages.append((i,m.get('usage',{})))
            for c in m.get('content',[]):
                if c['type']=='text': rows.append((i,ts,'text',c['text']))
                elif c['type']=='tool_use':
                    j=json.dumps(c['input'],ensure_ascii=False)
                    keep=c['name'] in('Agent','SendMessage') or re.search(r'make land|git add|NOTE=|commit|append|task-add|file-task',j)
                    rows.append((i,ts,'tool',c['name']+' '+(j if keep else j[:1500])))
        elif t in('user','attachment'):
            if t=='user':
                m=d.get('message',{}).get('content')
                parts=[m] if isinstance(m,str) else [c.get('text','') for c in m if isinstance(c,dict) and c.get('type')=='text']
            else:
                parts=[]; walk(d.get('attachment',d),parts)
            for s in parts:
                if '<task-notification>' not in s:
                    if t=='user' and s.strip() and not d.get('isMeta') and 'tool_result' not in l[:300]: rows.append((i,ts,'user',s[:1500]))
                    continue
                for blk in re.findall(r'<task-notification>(.*?)</task-notification>',s,re.S):
                    sm=re.search(r'<summary>Agent "((?:Build|Finish) 451 T[^"]*)" (finished|is waiting on its own background work)</summary>',blk)
                    if not sm or ts[:10] not in('2026-11-25','2026-11-26'): continue
                    r=re.search(r'<result>(.*)</result>',blk,re.S); res=r.group(1) if r else ''
                    tid=re.search(r'<task-id>(.*?)</task-id>',blk).group(1)
                    # a report is the builder's long message, whichever label the harness gave it (a final report can arrive
                    # labeled interim, or as an attachment); short waiting notes are not reports
                    if len(res)<1000 or (tid,res) in seenrep: continue
                    seenrep.add((tid,res))
                    u=re.search(r'<subagent_tokens>(\d+).*?<tool_uses>(\d+).*?<duration_ms>(\d+)',blk,re.S)
                    reports.append(dict(tid=tid,line=i,ts=ts,name=sm.group(1),label=sm.group(2)[:8],via=t,result=res,
                        tokens=int(u.group(1)) if u else None,tools=int(u.group(2)) if u else None,ms=int(u.group(3)) if u else None))
                    rows.append((i,ts,'REPORT',sm.group(1)))
last=i
for r in reports:
    nxt=min([c for c in compacts if c>r['line']],default=None)
    r['turns']=sum(1 for a in api_ids if a>r['line'] and (nxt is None or a<nxt))
    r['until']='compaction' if nxt else 'end'
    r['chars']=len(r['result'])
json.dump(dict(reports=reports,rows=rows,compacts=compacts,usages=usages),open('m14r-extract.json','w'))
for r in reports: print(r['line'],r['ts'][:16],r['chars'],r['chars']//4,r['turns'],r['until'],r['tokens'],r['tid'][:6],r['label'],r['via'],r['name'])
print(len(reports),compacts)
