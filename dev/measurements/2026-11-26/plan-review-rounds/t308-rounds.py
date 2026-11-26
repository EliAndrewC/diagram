import json,re,sys,difflib
from datetime import datetime
D='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/subagents/'
o=json.load(open('t308-sf.json'))
HEAD=re.compile(r"MODE 4: PLAN REVIEW of (one task's section - feature 451-time-retro-and-efficiency, task (T\d+[a-z]?)|\d+ changed block\(s\) of feature 451-time-retro-and-efficiency)")
R=[r for r in o if (r['first'] or '')>='2026-11-24' and r['prompt'] and HEAD.search(r['prompt'][:400])]
def T(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
rows=[]
for r in R:
    m=HEAD.search(r['prompt'][:400])
    task=m.group(2) or 'blocks:'+re.search(r'blocks-([\w-]+?)-[0-9a-f]{8}/',r['prompt']).group(1)[:9]
    sec=None;sha=None;verd=None;vjson=None;refusals=[]
    for line in open(D+r['id']):
        try:d=json.loads(line)
        except: continue
        c=(d.get('message') or {}).get('content')
        if not isinstance(c,list): continue
        for b in c:
            if b.get('type')=='tool_use':
                s=json.dumps(b['input'])
                if 'section_sha256' in s and 'decisions' in s: vjson=b['input'].get('command') or b['input'].get('content') or s
            if b.get('type')=='tool_result':
                t=b.get('content')
                if isinstance(t,list): t='\n'.join(x.get('text','') for x in t if isinstance(x,dict))
                t=t or ''
                mm=re.search(r'<!-- block "the section of [^"]*" sha256 ([0-9a-f]{64}) -->\n',t)
                if mm and sec is None:
                    sha=mm.group(1); rest=t[mm.end():]
                    if re.match(r'\s*\d+\t',rest): rest='\n'.join(re.sub(r'^\s*\d+\t','',l) for l in rest.split('\n'))
                    sec=None
                    import hashlib
                    pos=0
                    while True:  # the section is the prefix whose digest the block's own header states
                        nl=rest.find('\n',pos)
                        if nl<0:
                            cands=[rest,rest+'\n']
                        else: cands=[rest[:nl],rest[:nl+1]]
                        hit=[c for c in cands if hashlib.sha256(c.encode()).hexdigest()==sha]
                        if hit: sec=hit[0]; exact=True; break
                        if nl<0: break
                        pos=nl+1
                    if sec is None:
                        cut=re.search(r'\n=+ ?[\w.-]+ ?=*\n|\n=+ ?EARLIER|\n<!-- block |\n# Each changed block',rest)
                        sec=rest[:cut.start()] if cut else rest
                for v in re.findall(r'plan-verdict: (\w[\w-]*) recorded',t): verd=v
                for v in re.findall(r'plan-verdict: refused - ([^\n]*)',t): refusals.append(v[:200])
    if verd is None:
        mm=re.search(r'\b(NOT-REVIEWABLE|NOT REVIEWABLE|BLOCKED|CLEAR)\b',r['reply'] or '')
        verd=(mm.group(1)+'?') if mm else None
    extra=r['prompt'].split('and nothing in the repository.',1)[-1].strip()
    rows.append(dict(task=task,id=r['id'],first=r['first'],last=r['last'],mins=round((T(r['last'])-T(r['first'])).total_seconds()/60,2),verdict=verd,sha=sha,sec=sec,vjson=vjson,refusals=refusals,extra=extra,reply=r['reply'],type=r['type']))
json.dump(rows,open('t308-rounds.json','w'))
import collections
by=collections.defaultdict(list)
for x in rows: by[x['task']].append(x)
import hashlib
print('exact sections',sum(1 for x in rows if x['sec'] and hashlib.sha256(x['sec'].encode()).hexdigest()==x['sha']))
print('rounds',len(rows),'tasks',len(by),'non-first',sum(len(v)-1 for v in by.values()),'no sec',sum(1 for x in rows if not x['sec']),'verdicts',collections.Counter(x['verdict'] for x in rows))
print('tasks by rounds',collections.Counter(len(v) for v in by.values()))
