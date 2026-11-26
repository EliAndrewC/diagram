import subprocess,re,json,glob,collections,datetime,os
C='/diagram/.clones/diagram-backlog'
def iso(s): return datetime.datetime.fromisoformat(s).timestamp()
out=subprocess.run(['git','-C',C,'log','--since=2026-09-25','--name-only','--format=@@%cI|%s'],capture_output=True,text=True).stdout
first={};last={};ticks=collections.defaultdict(list)
cur=None
for l in out.splitlines():
    if l.startswith('@@'):
        t,s=l[2:].split('|',1);cur=iso(t)
        m=re.match(r'(\d{3}-[a-z0-9-]+): ((?:T\d+ ?)+)ticked \(make land\)',s)
        if m: ticks[m.group(1)].append(cur)
    elif l.startswith('specs/'):
        d=l.split('/')[1]
        first[d]=min(first.get(d,cur),cur);last[d]=max(last.get(d,cur),cur)
# bypass counts by target feature
esc=collections.Counter();escw=collections.defaultdict(list)
for f in glob.glob(C+'/dev/bypass-log/2026-1*/*.json'):
    d=json.load(open(f));t=d.get('target') or ''
    m=re.match(r'plan-gate (?:tick|decide-defer) (\d{3}-[a-z0-9-]+)',t)
    if m: esc[m.group(1)]+=1
rows=[]
for d in sorted(os.listdir(C+'/specs')):
    if int(d[:3])<380 and d[:3] not in ('449','451'): pass
    p=C+'/specs/'+d
    n=0
    for fn in('tasks.md','tasks-done.md'):
        if os.path.exists(p+'/'+fn):
            n+=len(set(re.findall(r'(?m)^- \[[ xX]\] (T\d+)',open(p+'/'+fn).read())))
    if d not in first: continue
    nt=len(ticks.get(d,[]))
    rows.append((d,n,nt,((max(ticks[d]) if ticks.get(d) else last[d])-first[d])/86400,esc.get(d,0)))
print('feature | tasks | make-land landings | days (first..last commit touching specs dir) | plan-gate tick escapes | escapes/landing')
for r in rows:
    if (1<=r[1]<=5 and r[2]>=1) or r[0][:3] in('449','451','452'):
        print(f'{r[0][:45]:45s} {r[1]:4d} {r[2]:3d} {r[3]:6.1f} {r[4]:3d} {r[4]/r[2] if r[2] else float("nan"):.2f}')
