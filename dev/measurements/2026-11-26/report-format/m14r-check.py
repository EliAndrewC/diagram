#!/usr/bin/env python3
"""m14r stage 3: the twelve hand re-expressions against the originals - size, the frozen used-item check, the saving."""
import json,re,statistics as st
d=json.load(open('m14r-extract.json')); reps=d['reports']
fm={int(m.group(1)):b.strip() for b in re.split(r'\n(?=### R\d+)',open('m14r-formatted.md').read()) for m in [re.match(r'### R(\d+)\n',b)] if m}
fm={k:re.sub(r'^### R\d+\n','',v) for k,v in fm.items()}
LONG=[3,13,4,10,9,12,6,30]; TYP=[20,16,22,17]
# frozen before the format was drafted: items of each report the session went on to use (transcript line of the use)
USED={3:['T243-r2finisher.md','48','task-starts.jsonl','event-log phase','core/src/logs.rs','reviews/ledger.rs','amendment (h)','STATIC_OK','task_time.rs','task_time/','949.4','458.0','277.2','180.4','69.6','34.7','20.7','5.0','6.0','47.2','42.1','27.2','26.0','19.4','17.6','11.2','8.7','7.9','2.1','7.5','2340.3','2687.2','tt24-v3.log','14 commits'],
 13:['T259-ad4ec2d5908b8bdc4.md','dev/audits/','audit_register.rs','audit_register/','process-decisions.md','five detectors','declined kind','replay figures','T260','recount','Occasions line','make docs','make decide','round 2','STATIC_OK','request.md'],
 4:['T243-r5builder.md','Blocks: T4','T5','every task with blocking work in flight gets its own piece','two-task test','#T243@6','guess-accuracy or wording','accept','book/clue.rs','book/window.rs','diagram-backlog-land','Working at once','1,231.3','441.6','1,037.3'],
 10:['merge driver','4 files','about 39','merged clean','T256-D1','T254 to T257','merge.rs','merge/','elsewhere.rs','elsewhere/','diagram-backlog-t256','three-way','key by key','later','block_reviews','sync-in','make -C','names the tree','.gitattributes'],
 9:['158 lines in 32 files','land-tooling.sh` (3)','review-gate.sh` (3)','tests/hooks/seen.sh','check pipe-race',"hooks-test`'s tail",'exit code','no grep pipe','every shell file','CLEAR round 3',"451 T253 adds the pipe-race check to hooks-test's tail",'pipe_race.rs','pipe_race/','1.3 MB'],
 12:['ready to land','accept','405 D4','only where the push carries its edits','own tree','speckit/touch/','diagram-backlog-t254','GREEN','T254 and T255'],
 6:['make research-deferred REASON="the GM 2026-11-25: I would like to essentially defer all of it until at least tomorrow"','make research-open','deferred: UNRESEARCHED','lists what it touched','research-pass','make page-session','RESEARCH_OK','switches::write','tagging or cascade repairs','switches.rs','switches/','research_switch_hooks.rs','research_switch_hooks/','research-switch-hooks.sh','test-research-switch-hooks.sh','CLEAR round 1','message-check'],
 30:['NOT met','BLOCKED round 1','filed task ids','file the candidates','four items','7e8cc888b57fb2c2','6f2059b7c3ad8fc8','third round owes the arbiter','crate list','xargs git',"sh -c 'git",'quoted `"git"`','cargo','$GIT','claims-file','parked.rs','rust/guard/CLAUDE.md','a_clean_carry_is_verified','magistracy sheets','diagram-backlog-t270','spelled.rs','Built from the tree','make -C','disk-report-from-host'],
 20:['.git` is a file','gitdir','201 passed, 1 failed','202 passed','linked worktree','prereq.rs','prereq/scoped.rs','prereq/tree.rs','snapshot.rs','idle_tests','finished_run','review_round','escalation','pair_hooks','stall_watchdog','clone_sync_hooks.rs','archive/store.rs','unmeasured','diagram-backlog-t267','CLEAR'],
 16:['bare git mirror','0.03 s','newer','first sync-in','force push','29.3 MB in 8.7 s','tip back equal','scripts/state-sync.sh','tests/hooks/test-state-sync.sh','dev/audits/tooling-state.md','CLEAR','landing step no detector sees','diagram-backlog-t258','fixture'],
 22:['same','tree path','prefix scratch files','190 passed, 1 failed','191 passed','only if two trees decide the same task','814 s','450 s','209 s','1218 s','69 s','6 s','coordinating clone decides a task',"unprefixed write",'diagram-backlog-t271'],
 17:['honor the escape before asking the gate','records nothing','held','0.3','158','closing1.log','make task-start','by the record\'s `held`','task id','dev/audits/plan-gate-escape.md','diagram-backlog-t262','189 passed, 1 failed','CLEAR']}
OLD={int(k):v for k,v in json.load(open('m14r-oldnum.json')).items()}; BY={r['line']:r for r in reps}
def R(n): return BY[OLD[n]]
SHORT=[11,31]
def unesc(t): return t.replace('&lt;','<').replace('&gt;','>').replace('&amp;','&')
def window(r):
    """the session's own rows that followed this report, up to its landing (+2 later mentions) or its successor's brief - full text"""
    tasks=re.findall(r'T(\d+)',r['name']); pat=re.compile(r'T(?:%s)\b'%'|'.join(tasks)); out=[]; first=True; post=0
    for (i,ts,k,t) in d['rows']:
        if i<=r['line']: continue
        if k in('REPORT','user'): first=False; continue
        hit=pat.search(t)
        if post:
            if k=='text' and hit: out.append(t); post-=1
            if not post or i>r['line']+3000: break
            continue
        if not(first or hit): continue
        out.append(t)
        if k=='tool' and hit and re.match(r'Agent \{"description": "(Finish|Fix)',t): break
        if k=='tool' and hit and re.search(r'make land(-batch)? ',t) and 'land-tooling' not in t: post=2
        if i>r['line']+2500: break
    return '\n'.join(out).replace('\\"','"').replace('\\\\','\\').replace('\\n','\n')
TOK=re.compile(r'`[^`\n]{2,80}`|[\w./-]+/[\w./-]+\.\w+|\bT\d{2,3}\b|\b[0-9a-f]{12,16}\b|\b\d[\d,]*\.\d+\b|\b\d{2,}[\d,]*\b')
def norm(x): return x.strip('`').replace(',','')
rep=[]; ok=True; mech={}
for n in LONG+TYP+SHORT:
    r=R(n); f=fm[n]; o=r['chars']; orig=unesc(r['result']); w=window(r); fn=f.replace(',','')
    miss=[u for u in USED.get(n,[]) if u not in f]
    both=sorted({norm(t) for t in TOK.findall(orig) if norm(t) and norm(t) in w.replace(',','')})
    mm=[t for t in both if t not in fn]; mech[n]=(len(both),mm)
    rep.append((n,r['name'][:34],o,len(f),round(100*len(f)/o),r['turns'],miss)); 
    if miss: ok=False
print('R | name | orig | fmt | % | turns | hand-listed used items missing')
for x in rep: print(*x,sep=' | ')
print('hand-listed used items all present:',ok, 'n =',sum(len(v) for v in USED.values()))
print('MECHANICAL: tokens (backticked spans, paths, T-ids, hex keys, numbers) found in BOTH the original report and the session\'s following rows, and absent from the re-expression:')
for n in LONG+TYP+SHORT: print(' R%d: %d shared tokens, %d absent: %s'%(n,mech[n][0],len(mech[n][1]),mech[n][1]))
def S(ns): return sum(R(n)['chars'] for n in ns), sum(len(fm[n]) for n in ns)
for name,ns in [('eight longest',LONG),('eight longest without R3',LONG[1:]),('four typical',TYP),('two short',SHORT),('all fourteen',LONG+TYP+SHORT)]:
    o,f=S(ns); print(f"{name}: {o} -> {f} chars ({100*f/o:.0f}%)")
to,tf=S(TYP); tr=tf/to
done={OLD[n]:len(fm[n]) for n in fm}
def newsize(r): return done[r['line']] if r['line'] in done else (r['chars'] if r['chars']<3000 else r['chars']*tr)
raw=sum((r['chars']-newsize(r))/4*r['turns'] for r in reps); meas=sum((r['chars']-newsize(r))/4*r['turns'] for r in reps if r['line'] in done)
ctx=sum(r['chars']/4*r['turns'] for r in reps); arr=sum((r['chars']-newsize(r))/4 for r in reps)
us=d['usages']; allin=sum(x[1].get('cache_read_input_tokens',0)+x[1].get('cache_creation_input_tokens',0)+x[1].get('input_tokens',0) for x in us if x[0]>reps[0]['line'])
print(f"reports: {len(reps)}; token-turns today {ctx:,.0f} = {100*ctx/allin:.2f}% of the session's {allin:,} input tokens over those turns")
print(f"saved token-turns raw {raw:,.0f} (the fourteen measured {meas:,.0f}; R3 alone {(R(3)['chars']-len(fm[3]))/4*R(3)['turns']:,.0f}; other {len(reps)-len(done)} estimated {raw-meas:,.0f}: under 3,000 chars no cut, else {100*(1-tr):.0f}%) = {100*raw/allin:.2f}%; weighted x0.1 {raw*0.1:,.0f}; at arrival {arr:,.0f} tokens (x1.25 = {arr*1.25:,.0f})")
tools=sum(x['tools'] or 0 for x in reps); fc=(len(open('m14r-format.txt').read())-146)/4
print(f"format in every brief: {fc:.0f} tokens x {tools} builder tool uses = {fc*tools:,.0f} token-turns ({100*fc*tools/raw:.0f}% of the saving); read once at the stop point: about {fc*2*len(reps):,.0f}")
print('turns per report: median',st.median([r['turns'] for r in reps]),'range',min(r['turns'] for r in reps),max(r['turns'] for r in reps))
