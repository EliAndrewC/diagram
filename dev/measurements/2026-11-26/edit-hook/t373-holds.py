# t373: the share of the day's Bash calls made while a plan review held text, ESTIMATED from the event log copy: a hold is taken to run
# from a spec-fidelity agent's SubagentStart to its SubagentStop (by agent id); the union of those intervals; the Bash PreToolUse lines inside it.
import json,glob,os,collections
S=os.path.dirname(os.path.abspath(__file__)); D=S+'/w/diagram/.clones/diagram-backlog/.git/l7r-events'
lo,hi='2026-11-26T05:00','2026-11-27T05:00'
rows=[]
for f in glob.glob(D+'/*.jsonl'):
    if f.endswith('_unassigned.jsonl'): continue
    for l in open(f,errors='replace'):
        if '"t":"2026-11-2' not in l[:20]: continue
        try: r=json.loads(l)
        except Exception: continue
        if lo<=r.get('t','')<hi and not r.get('sid','').startswith(('t365-','t304-','t373-')): rows.append(r)
rows.sort(key=lambda r:r['t'])
print('fields of a SubagentStart:',sorted(next(r for r in rows if r['ev']=='SubagentStart').keys()))
start={}; iv=[]
for r in rows:
    aid=r.get('aid') or r.get('by')
    if r['ev']=='SubagentStart' and r.get('agent')=='spec-fidelity': start[r.get('aid')]=r['t']
    if r['ev']=='SubagentStop' and r.get('agent')=='spec-fidelity' and r.get('aid') in start: iv.append((start.pop(r['aid']),r['t']))
iv.sort(); merged=[]
for a,b in iv:
    if merged and a<=merged[-1][1]: merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
    else: merged.append((a,b))
from datetime import datetime
sec=lambda t: datetime.fromisoformat(t.replace('Z','+00:00')).timestamp()
held=sum(sec(b)-sec(a) for a,b in merged); span=sec(rows[-1]['t'])-sec(rows[0]['t'])
inside=collections.Counter(); total=collections.Counter()
for r in rows:
    if r['ev']=='PreToolUse':
        total[r.get('tool')]+=1
        if any(a<=r['t']<=b for a,b in merged): inside[r.get('tool')]+=1
print(f'spec-fidelity runs paired: {len(iv)} (unpaired starts {len(start)}); merged intervals {len(merged)}; held {held/60:.1f} min of the {span/3600:.1f} h the log spans')
for t in ('Bash','Edit','Write','Agent'): print(f'  {t}: {inside[t]} of {total[t]} PreToolUse calls inside a hold ({100*inside[t]/max(1,total[t]):.0f}%)')
