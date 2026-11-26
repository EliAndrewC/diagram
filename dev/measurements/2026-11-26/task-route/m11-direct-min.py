#!/usr/bin/env python3
"""m11-direct-min.py: for each taskless tooling change on main since 2026-11-19 (m11-direct.json, grouped by hand below),
minutes from the first Edit of one of its files (the last burst before the commit, gaps under 60 min) to its last commit,
and the make targets its session ran in between - from every clone's event logs."""
import json,glob,datetime,subprocess,collections,os
R='/diagram/.clones/diagram-backlog-land'
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
GROUPS={'footnote hold keeps its trip (arbiter ruling ask:454-c1b-fixloop-retrip)':['b598204378','e234fa56b3','bac0a34693','e0db6b1276'],
 'apply-edits: "EDIT: none" is no unread EDIT':['926e10e593','c3d8d57a36'],
 'land-tooling: 8 agent/tooling files':['f7c105b4a0'],
 '.gitignore *.profraw':['a872b46eff'],
 '449 arbiter fix: reversal tripwire holds its own session':['bce1e28014'],
 '449: plan archive keeps a bundle block':['38c3a1c8fa'],
 '449 arbiter fix: review dispatch refused while gate red':['6570db3de4'],
 'run-plausible history test floor':['ee2f44fbc5'],
 'land-alone seeds review verdicts':['4ceb12ad0f'],
 'bundle test formatting (with a claims record)':['46af955365']}
def show(h):
    o=subprocess.run(['git','-C',R,'show','--numstat','--format=%cI|%s',h],capture_output=True,text=True).stdout.strip().splitlines()
    d,s=o[0].split('|',1); fs=[l.split('\t') for l in o[1:] if l.strip()]
    return ts(d),s,[(int(a) if a!='-' else 0,int(b) if b!='-' else 0,p) for a,b,p in fs]
ev=[]
for f in glob.glob('/diagram/.clones/*/.git/l7r-events/*.jsonl')+glob.glob('/diagram/.git/l7r-events/*.jsonl'):
    if os.path.islink(f): continue
    for l in open(f):
        if '"t":"2026-11-2' not in l[:60] or ('"Edit"' not in l and '"Write"' not in l and '"make"' not in l): continue
        try: v=json.loads(l)
        except: continue
        if v.get('ev')!='PreToolUse' and not (v.get('ev')=='PostToolUse' and v.get('make')): continue
        ev.append((ts(v['t']),v.get('tool'),v.get('path',''),v.get('make'),v.get('sid'),v.get('ms',0),v.get('ev'),v.get('by')))
ev.sort()
print('| direct change | commits | code files | code lines | first edit -> last commit, min | follow-up commits (format, lint, coverage) | make targets its session ran in the span (count, summed min) |'); print('|---|---|---|---|---|---|---|')
allm=[]
for name,hs in GROUPS.items():
    cs=[show(h) for h in hs]; tend=max(c[0] for c in cs); files={p for c in cs for a,b,p in c[2] if not p.startswith(('specs/','dev/'))}
    lines=sum(a+b for c in cs for a,b,p in c[2] if not p.startswith(('specs/','dev/')))
    ed=[e for e in ev if e[1] in('Edit','Write') and e[6]=='PreToolUse' and any(e[2].endswith('/'+p) for p in files) and tend-6*3600<e[0]<=tend]
    if not ed: print('| %s | %d | %d | %d | no Edit event found (edited by a shell command, or another log) | %d | |'%(name,len(hs),len(files),lines,len(hs)-1)); continue
    start=ed[-1][0]
    for e in reversed(ed):
        if start-e[0]<3600: start=e[0]
    sid=ed[-1][4]
    mk=collections.Counter(); mm=collections.Counter()
    for e in ev:
        if e[6]=='PostToolUse' and e[3] and e[4]==sid and start<=e[0]<=tend+60: mk[e[3]]+=1; mm[e[3]]+=e[5]/60000
    allm.append((tend-start)/60)
    print('| %s | %d | %d | %d | %.0f | %d | %s |'%(name,len(hs),len(files),lines,(tend-start)/60,len(hs)-1,', '.join('%s %d/%.1f'%(k,n,mm[k]) for k,n in mk.most_common(8))))
import statistics as st
if allm: print('\nmedian first edit -> last commit: %.0f min over %d changes with Edit events (range %.0f-%.0f)'%(st.median(allm),len(allm),min(allm),max(allm)))
