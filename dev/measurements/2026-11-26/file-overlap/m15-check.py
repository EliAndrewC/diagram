"""m15 checks: anchors; co-activity pairs rebuilt from the event log (task + by = a subagent working a task); Rust exposure under carried commits."""
import json,re,collections,itertools,subprocess,datetime,bisect
R='/diagram/.clones/diagram-backlog'
def git(*a): return subprocess.run(['git','-C',R,*a],capture_output=True,text=True,check=True).stdout
units=json.load(open('m15-units.json'))
by={u['name']:u for u in units}
print('T270 holds audit code:', any('rust/' in f for f in by['451 T270']['files']), '| T272 units:', sum('T272' in u['name'].split() for u in units))
t101=[u for u in units if 'T101' in u['name'].split() and u['name'].startswith('451')][0]
print('T101 landed', datetime.datetime.utcfromtimestamp(t101['ct']), 'UTC (the T83/T87 refusal was 11-22 02:01 UTC)')
# builder activity: per (feature, task), minutes in which a subagent ('by') ran a tool for it
act=collections.defaultdict(set)
for feat in ('449-rust-codebase','451-time-retro-and-efficiency'):
    for l in open(R+'/.git/l7r-events/%s.jsonl'%feat,errors='replace'):
        if '"by"' not in l or '"task"' not in l: continue
        try: d=json.loads(l)
        except ValueError: continue
        if d.get('ev') not in('PreToolUse','PostToolUse') or not d.get('by') or not d.get('task'): continue
        if d['t']<'2026-11-19': continue
        act[(feat[:3],d['task'])].add(d['t'][:15])  # ten-minute buckets
def uact(u):
    f=u['name'][:3]; s=set()
    for t in u['name'].split()[1:]: s|=act.get((f,t),set())
    return s
for u in units: u['act']=uact(u)
print('units with builder activity in the event log:',sum(1 for u in units if u['act']),'of',len(units))
BOOK=re.compile(r'^(specs/[^/]+/(tasks|tasks-done|plan|plan-done)\.md|specs/[^/]+/(plan-review\.json|arbiter\.jsonl|found\.jsonl)|dev/review-ledger\.md|dev/(bypass-log|run-log|session-records)/|dev/deferred-reviews\.jsonl)')
REG=re.compile(r'^(Makefile|docs/guards\.md|docs/make-targets\.html|dev/guard-messages\.tsv|(.*/)?CLAUDE\.md|rust/gate/src/(lib|main)\.rs|rust/guard/src/(lib|guards|main)\.rs|scripts/container/builder-brief\.md|docs/process-decisions\.md|dev/audits/|dev/claims-(index|pages)\.json|rust/.*Cargo\.(toml|lock))')
GEN={'docs/make-targets.html','dev/claims-index.json','dev/claims-pages.json'}
def kl(f): return 'BOOK' if BOOK.match(f) else 'REG' if REG.match(f) else 'RUST' if f.startswith('rust/') and f.endswith('.rs') else 'OTHER'
def crate(f):
    m=re.match(r'^(rust/gate/crates/[^/]+|rust/guard/(?:shared|src)|rust/[^/]+)/',f); return m.group(1) if m else None
def tier(a,b):
    sh=set(a['files'])&set(b['files']); ks={kl(f) for f in sh}
    ca={crate(f) for f in a['files'] if kl(f)=='RUST'}; cb={crate(f) for f in b['files'] if kl(f)=='RUST'}
    if 'RUST' in ks: return 'rust-same-file'
    if ca&cb: return 'rust-same-crate-other-file'
    if any(kl(f)=='REG' and f not in GEN for f in sh): return 'registry (hand-edited)'
    if 'REG' in ks: return 'registry (generated only)'
    if ks-{'BOOK'}: return 'other shared'
    return 'bookkeeping-only' if ks else 'none'
for need in (1,3):
    ps=[(a,b) for a,b in itertools.combinations(units,2) if len(a['act']&b['act'])>=need]
    c=collections.Counter(tier(a,b) for a,b in ps)
    print('\nCO-ACTIVE pairs (builders of both ran tools in >=%d of the same ten-minute buckets; different ticks): %d'%(need,len(ps)))
    for k,v in c.most_common(): print('  %-28s %4d %5.1f%%'%(k,v,100*v/len(ps)))
    single=[(a,b) for a,b in ps if len(a['name'].split())==2 and len(b['name'].split())==2]
    c=collections.Counter(tier(a,b) for a,b in single)
    print('  single-task units only: %d pairs: %s'%(len(single),', '.join('%s %d (%.0f%%)'%(k,v,100*v/len(single)) for k,v in c.most_common())))
    if need==3:
        mk=sum(1 for a,b in ps if 'Makefile' in set(a['files'])&set(b['files'])); print('  share the Makefile: %d (%.1f%%)'%(mk,100*mk/len(ps)))
        print('  rust-same-file examples:'); 
        for a,b in [p for p in ps if tier(*p)=='rust-same-file'][:6]:
            print('   ',a['name'][:40],'||',b['name'][:40],':',', '.join(sorted(f.split('/')[-1] for f in set(a['files'])&set(b['files']) if kl(f)=='RUST'))[:120])
def name(ts): return [u['name'] for u in units if any(t in u['name'].split()[1:] for t in ts) and u['name'].startswith(ts[-1])]
print('\nknown co-running builders (transcript): 451 T118/T129/T89 buckets shared:', len(act[('451','T118')]&act[('451','T129')]), len(act[('451','T118')]&act[('451','T89')]), '| 449 T158/T240:', len(act[('449','T158')]&act[('449','T240')]))
# Rust exposure under carried commits: Rust-editing commits by OTHER tasks landing on main while each carried code commit's task was out
