#!/usr/bin/env python3
"""m11-direct.py: commits on origin/main since 2026-11-19 that name NO task, classed by what they change."""
import subprocess,re,collections,sys,json
R='/diagram/.clones/diagram-backlog-land'
out=subprocess.run(['git','-C',R,'log','origin/main','--since=2026-11-19T00:00:00Z','--no-merges','--numstat','--format=@@%h|%cI|%an|%s'],capture_output=True,text=True).stdout
commits=[];cur=None
for l in out.splitlines():
    if l.startswith('@@'):
        h,d,an,s=l[2:].split('|',3); cur={'h':h,'d':d,'s':s,'files':[]}; commits.append(cur)
    elif l.strip():
        a,b,p=l.split('\t'); cur['files'].append((0 if a=='-' else int(a),0 if b=='-' else int(b),p))
def cls(p):
    if p.startswith('specs/'): return 'spec'
    if p.startswith('dev/') or p.startswith('.specify/') : return 'record'
    if p.startswith('research/'): return 'research'
    if p.startswith('pool/'): return 'pool'
    if p.startswith('rust/phases') or p.startswith('rust/mode_a') or p.startswith('l7r/'): return 'engine' if p.endswith('.rs') or p.endswith('.py') or p.endswith('.json') else 'doc'
    if p.endswith('.md') and not p.startswith('.claude/agents') and not p.startswith('scripts/container'): return 'doc'
    if p.endswith('.html'): return 'doc'
    if p.startswith(('rust/','scripts/','tests/','.claude/','Makefile','.cargo','.git')) or p=='Makefile': return 'tooling'
    return 'other'
TASK=re.compile(r'\bT\d{2,3}\b')
rows=[]
for c in commits:
    k=collections.Counter(); ln=collections.Counter()
    for a,b,p in c['files']: k[cls(p)]+=1; ln[cls(p)]+=a+b
    c['k']=k; c['ln']=ln
    c['task']=bool(TASK.search(c['s'])) or 'ticked (make land)' in c['s']
    c['code']=k['tooling']+k['engine']
all_n=len(commits)
notask=[c for c in commits if not c['task']]
code=[c for c in notask if c['code']>0]
print('commits since 2026-11-19:',all_n,'naming no task:',len(notask),'of those touching tooling/engine code files:',len(code))
kinds=collections.Counter()
for c in notask:
    kinds['+'.join(sorted(k for k in c['k'] if c['k'][k])) or 'empty']+=1
print('no-task commits by what they touch:',kinds.most_common(12))
import statistics as st
if code:
    print('code-touching no-task commits: files median',st.median([c['code'] for c in code]),'max',max(c['code'] for c in code),'lines median',st.median([c['ln']['tooling']+c['ln']['engine'] for c in code]),'max',max(c['ln']['tooling']+c['ln']['engine'] for c in code))
for c in code:
    print(c['h'],c['d'][:16],dict(c['k']),'lines',c['ln']['tooling']+c['ln']['engine'],'|',c['s'][:150],'|',[p for a,b,p in c['files'] if cls(p) in('tooling','engine')][:5])
json.dump([{k:(dict(v) if isinstance(v,collections.Counter) else v) for k,v in c.items()} for c in code],open(sys.argv[1],'w'))
