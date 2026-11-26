import pickle,json,statistics as st,re
S=pickle.load(open('m2.pkl','rb'))
B={r['id']:r for r in pickle.load(open('m1.pkl','rb'))}
C={r['id']:r for r in json.load(open('m1-table.json'))}
def kind(r):
    s=' '.join(r['sample'])
    return 'code (rust/scripts/tests/Makefile/hooks)' if re.search(r'rust/|scripts/|tests/|Makefile|\.rs',s) else 'spec/plan/tasks/docs'
# only stretches since 11-24 vs all since 11-19
for label,flt in(('since 11-19',lambda r:True),('since 11-24',lambda r:r['when']>='11-24')):
    print('==',label)
    for k in ('code (rust/scripts/tests/Makefile/hooks)','spec/plan/tasks/docs'):
        x=[r for r in S if flt(r) and kind(r)==k and r['nagent']==0]
        if not x: continue
        f=lambda key:(st.median(r[key] for r in x),st.mean(r[key] for r in x))
        print(f"{k}: n={len(x)} total min {sum(r['min'] for r in x):.0f}; median/mean minutes {f('min')[0]:.1f}/{f('min')[1]:.1f}; out {f('out')[0]:.0f}/{f('out')[1]:.0f}; ctx growth {f('growth')[0]/1000:.0f}k/{f('growth')[1]/1000:.0f}k; later turns med {st.median(r['later'] for r in x)}; reread cost(0.1) {f('reread')[0]/1000:.0f}k/{f('reread')[1]/1000:.0f}k; own span cost {f('own')[0]/1000:.0f}k/{f('own')[1]/1000:.0f}k; total {st.median(r['own']+r['reread'] for r in x)/1000:.0f}k/{st.mean(r['own']+r['reread'] for r in x)/1000:.0f}k; mean files {st.mean(r['files'] for r in x):.1f}")
        # per file edited
        print('   per file edited: cost %.0fk, minutes %.1f'%(sum(r['own']+r['reread'] for r in x)/sum(r['files'] for r in x)/1000,sum(r['min'] for r in x)/sum(r['files'] for r in x)))
# builders small tasks: <60 calls, jobs<=3 ; and medium
print('== builders (since 11-24, n=%d)'%len(B))
def bstats(name,x):
    if not x: return
    # coordinator cost of brief: write once (1.25 x brief tokens) + dispatch output (5 x tokens, as it types it) + reread later turns (0.1 x tokens x ~later) ; report read similar
    bt=lambda r:r['plen']/3.5; rt=lambda r:r['replylen']/3.5
    LATER=300  # typical later main turns before compaction (m2: median ~ 400)
    coord=[5*bt(r)+1.25*(bt(r)+rt(r))+0.1*(bt(r)+rt(r))*LATER for r in x]
    own=[r['cost'] for r in x]
    print(f"{name}: n={len(x)} builder cost med {st.median(own)/1000:.0f}k mean {st.mean(own)/1000:.0f}k | coordinator brief+report cost med {st.median(coord)/1000:.0f}k | total med {st.median([a+b for a,b in zip(own,coord)])/1000:.0f}k | out med {st.median(r['out'] for r in x)/1000:.0f}k calls med {st.median(r['calls'] for r in x):.0f} files med {st.median(r['edited'] for r in x):.0f}")
allb=list(B.values())
bstats('all builders',allb)
bstats('small: <60 calls',[r for r in allb if r['calls']<60])
bstats('small: <60 calls and no handoff',[r for r in allb if r['calls']<60 and not r['handoff']])
bstats('mid: 60-119 calls',[r for r in allb if 60<=r['calls']<120])
bstats('big: 120+ calls',[r for r in allb if r['calls']>=120])
bstats('<=3 files edited & not hit',[r for r in allb if 1<=r['edited']<=3 and not r['hit']])
pickle.dump(S,open('m2.pkl','wb'))
