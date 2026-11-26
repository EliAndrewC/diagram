import re
L=open('task-time.txt').read().split('\n')
i=L.index('## The whole window')
cats=[];tg=[];mode=0
for l in L[i:]:
    if not l.startswith('|') or l.startswith('|---'): continue
    c=[x.strip() for x in l.strip('|').split('|')]
    if c[0]=='category': mode=1;continue
    if c[0]=='make target or program': mode=2;continue
    if mode==1: cats.append((c[0],float(c[1]),float(c[4])))
    if mode==2: tg.append((c[0],c[1],int(c[2]),float(c[3]),float(c[6])))
WT,WB=4610.3,1309.1
print('TOP15 by blocking');
for r in sorted(tg,key=lambda r:-r[4])[:15]: print(f'{r[0]:38s} {r[1][:30]:30s} runs {r[2]:5d} min {r[3]:7.1f} ({100*r[3]/WT:4.1f}%) blk {r[4]:6.1f} ({100*r[4]/WB:4.1f}%)')
print('TOP15 by minutes')
for r in sorted(tg,key=lambda r:-r[3])[:15]: print(f'{r[0]:38s} {r[1][:30]:30s} runs {r[2]:5d} min {r[3]:7.1f} ({100*r[3]/WT:4.1f}%) blk {r[4]:6.1f} ({100*r[4]/WB:4.1f}%)')
G={}
def grp(n):
    if n=='the GM': return 'GM'
    if n.startswith('waiting') or n.startswith('wait loops'): return 'waiting/idle'
    if 'agents' in n or n.startswith('other review agents'): return 'agent spans (review/check)'
    if n.startswith('builders:') or n.startswith('main session:'): return 'model turns'
    return 'tooling execution'
for n,m,b in cats:
    if n=='all' or n.startswith('working'): continue
    g=grp(n); G.setdefault(g,[0,0,[]]); G[g][0]+=m;G[g][1]+=b;G[g][2].append((n,b))
tot=sum(v[1] for k,v in G.items() if k!='GM')
print('blocking groups (excl GM, denominator %.1f)'%tot)
for k,v in G.items(): print(f'{k:28s} min {v[0]:7.1f} blk {v[1]:7.1f} {100*v[1]/tot if k!="GM" else 0:5.1f}% of non-GM blocking')
print([ (n,b) for n,b in G['tooling execution'][2]])
act=tot-G['waiting/idle'][1]
print('excluding waiting: tooling %.1f%% model %.1f%% agents %.1f%%'%tuple(100*G[k][1]/act for k in ['tooling execution','model turns','agent spans (review/check)']))
