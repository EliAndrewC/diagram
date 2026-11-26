"""m15: each commit carried over onto main (author time != commit time by > 60 s): which of its files main changed
between the task's start mark and the carry-over (other subjects' commits only), by class, and whether the hunks meet.
The builder's own base commit is gone with its worktree for 22 of 24, so the window stands in for it (error: a start
mark earlier than the worktree's base overcounts; a builder that synced mid-way overcounts too)."""
import subprocess,re,collections,json,datetime
R='/diagram/.clones/diagram-backlog'; PIN='248d6f919f'
def git(*a): return subprocess.run(['git','-C',R,*a],capture_output=True,text=True,check=True).stdout
BOOK=re.compile(r'^(specs/[^/]+/(tasks|tasks-done|plan|plan-done)\.md|specs/[^/]+/(plan-review\.json|arbiter\.jsonl|found\.jsonl)|dev/review-ledger\.md|dev/(bypass-log|run-log|session-records)/|dev/deferred-reviews\.jsonl)')
REG=re.compile(r'^(Makefile|docs/guards\.md|docs/make-targets\.html|dev/guard-messages\.tsv|(.*/)?CLAUDE\.md|rust/gate/src/(lib|main)\.rs|rust/guard/src/(lib|guards|main)\.rs|scripts/container/builder-brief\.md|docs/process-decisions\.md|dev/audits/|dev/claims-(index|pages)\.json|rust/.*Cargo\.(toml|lock))')
def kl(f): return 'BOOK' if BOOK.match(f) else 'REG' if REG.match(f) else 'RUST' if f.startswith('rust/') and f.endswith('.rs') else 'TESTS' if f.startswith('tests/') else 'RESEARCH' if f.startswith('research/') else 'OTHER'
cs=[]
for blk in git('log',PIN,'--no-merges','--since=2026-11-19','--format=@@%H%x09%at%x09%ct%x09%s','--name-only').split('@@')[1:]:
    ls=blk.split('\n'); h,at,ct,s=ls[0].split('\t',3); cs.append(dict(h=h,at=int(at),ct=int(ct),s=s,files=[f for f in ls[1:] if f]))
cs.reverse()
starts=collections.defaultdict(list)
for l in open(R+'/.git/task-starts.jsonl'):
    try: d=json.loads(l)
    except ValueError: continue
    starts[(d['feature'][:3],d['task'])].append(datetime.datetime.strptime(d['utc'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp())
def tasks(s):
    m=re.match(r'^(\d{3})\S* ',s); return {(m.group(1),t) for t in re.findall(r'T\d+',s.split(':')[0])} if m else set()
def hunks(h,f,side):
    out=[]
    for m in re.finditer(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',git('show','-U0','--format=',h,'--',f),re.M):
        o,n=(int(m.group(1)),int(m.group(2) or 1)) if side=='old' else (int(m.group(3)),int(m.group(4) or 1)); out.append((o,o+max(n,1)-1))
    return out
tot=collections.Counter(); n=0
for i,c in enumerate(cs):
    if c['ct']-c['at']<=60: continue
    n+=1; tk=tasks(c['s'])
    st=max([x for t in tk for x in starts.get(t,[]) if x<=c['at']],default=c['at']-7200)
    res=[]
    for f in c['files']:
        others=[j for j in range(i) if st<cs[j]['ct'] and f in cs[j]['files'] and not (tasks(cs[j]['s'])&tk)]
        if not others: tot[kl(f)+' untouched underneath']+=1; continue
        a=hunks(c['h'],f,'old'); b=hunks(cs[others[-1]]['h'],f,'new')
        gap=min((max(x0-y1,y0-x1,0) for x0,x1 in a for y0,y1 in b),default=99)
        v='MEET' if gap<=1 else 'apart'; tot[kl(f)+' changed underneath, hunks '+v]+=1; res.append('%s=%s(%d)'%(f.split('/')[-1],v,len(others)))
    print('%s %s | window %d min | files %d | %s'%(c['h'][:10],c['s'][:46],(c['ct']-st)//60,len(c['files']),' '.join(res) or '-'))
print('\ncarried commits:',n)
for k,v in sorted(tot.items()): print('%4d %s'%(v,k))
