#!/usr/bin/env python3
"""m11-tt-small.py: make task-time's own per-task tables (m11-tt72.txt) for the small tasks, categories grouped into the route's steps."""
import re,collections,statistics as st,os
S=os.path.dirname(os.path.abspath(__file__))+'/'
tt=open(S+'m11-tt72.txt').read()
SMALL=['T252','T263','T267','T268','T269','T270','T271','T272']
def grp(c):
    if c.startswith('plan review'): return 'd plan review (agents + commands)'
    if c.startswith('claims'): return 'e claims round'
    if c in('compile','tests','hook suites','gate','static checks','coverage') or c.startswith('the gate binary'): return 'f+g compile, tests, hook suites, gate'
    if c=='landing' or c=='git': return 'g landing, git'
    if c.startswith('builders'): return 'b/c builder model turns (code, plan text, commands)'
    if c.startswith('main session'): return 'h main session turns'
    if c.startswith('spec-kit'): return 'a spec-kit step (task-add, task-start, decide)'
    if c.startswith('wait') or c.startswith('waiting'): return 'waits'
    if c=='the GM': return 'the GM'
    return 'other: '+c
tab={}
for T in SMALL:
    m=re.search(r'## 451-time-retro-and-efficiency %s \(landed[^\n]*\n\n(Its whole[^\n]*)\n\n((?:\|[^\n]*\n)+)'%T,tt)
    g=collections.defaultdict(lambda:[0.0,0.0])
    for l in m.group(2).splitlines()[2:]:
        c=[x.strip() for x in l.strip('|').split('|')]
        if c[0].startswith('working'): continue
        if c[0]=='all': g['all'][0]=float(c[1]); g['all'][1]=float(c[4]); continue
        k=grp(c[0]); g[k][0]+=float(c[1]); g[k][1]+=float(c[4])
    tab[T]=g
keys=sorted({k for g in tab.values() for k in g if k!='all'},key=lambda k:-sum(tab[T][k][0] for T in SMALL))+['all']
tot=sum(tab[T]['all'][0] for T in SMALL); totb=sum(tab[T]['all'][1] for T in SMALL)
print('| group (make task-time categories) | median machine min | share of the 8 tasks\' machine min | median blocking min | share of blocking | per task: '+' '.join(SMALL)+' |'); print('|---|---|---|---|---|---|')
for k in keys:
    a=[tab[T][k][0] for T in SMALL]; b=[tab[T][k][1] for T in SMALL]
    print('| %s | %.1f | %.0f%% | %.1f | %.0f%% | %s |'%(k,st.median(a),100*sum(a)/tot,st.median(b),100*sum(b)/totb if totb else 0,' '.join('%.0f'%x for x in a)))
