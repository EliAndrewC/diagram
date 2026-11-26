#!/usr/bin/env python3
"""m11-main.py: one streaming pass over the coordinating session's transcript since 2026-11-25T17Z; keeps each line's time,
API message id, usage, tool calls (name, id, 4000 chars of input) and tool-result ids. -> m11-main.pkl"""
import json,pickle,os
F='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
rows=[]
for l in open(F):
    if '"timestamp":"2026-11-2' not in l: continue
    i=l.find('"timestamp":"'); t=l[i+13:i+37]
    if t<'2026-11-25T17': continue
    if '"type":"assistant"' not in l and '"type":"user"' not in l: continue
    try: r=json.loads(l)
    except: continue
    if r.get('type') not in('assistant','user') or r.get('isSidechain'): continue
    m=r.get('message') if isinstance(r.get('message'),dict) else {}
    c=m.get('content')
    row={'t':r['timestamp'],'type':r['type'],'mid':m.get('id'),'u':m.get('usage'),'tools':[],'res':[],'text':''}
    if isinstance(c,str): row['text']=c[:600]
    else:
        for x in c or []:
            if not isinstance(x,dict): continue
            if x.get('type')=='tool_use':
                i=x.get('input') or {}
                row['tools'].append((x['id'],x['name'],(i.get('command') or i.get('prompt') or i.get('message') or i.get('file_path') or json.dumps(i))[:4000],i.get('subagent_type'),bool(i.get('run_in_background'))))
            elif x.get('type')=='tool_result': row['res'].append(x.get('tool_use_id'))
            elif x.get('type')=='text': row['text']+=x.get('text','')[:600]
    rows.append(row)
pickle.dump(rows,open(os.path.dirname(os.path.abspath(__file__))+'/m11-main.pkl','wb'))
print(len(rows),rows[0]['t'],rows[-1]['t'])
