import sys,re
sys.path.insert(0,'.')
from sec import *
f=sys.argv[1]
for t in sys.argv[2:]:
    r=revs(f,t,'2026-11-19','2026-12-31')
    if not r: print('##',t,'NO SECTION'); continue
    s=r[-1][3]
    print('##',t,r[-1][0][:10],len(s))
    for sent in re.split(r'(?<=[.;:])\s+|\n',s):
        if re.search(r'round|BLOCKED|reviewer|spec-fidelity|plan review|dropped|withdrawn|replaced|instead of|backed out|removed',sent,re.I):
            print('   ',sent.strip()[:330])
