import sys,re
sys.path.insert(0,'.')
from sec import *
f=sys.argv[1]
for t in sys.argv[2:]:
    r=revs(f,t,'2026-11-19','2026-12-31')
    if not r: print('##',t,'NO SECTION'); continue
    s=r[-1][3]; k=0
    print('##',t)
    for sent in re.split(r'(?<=[.;])\s+|\n',s):
        if re.search(r"plan review|spec-fidelity|first round|round 1|round 2|reviewer|BLOCKED|the review's|review found|MODE 4",sent,re.I) and k<4:
            print('   ',sent.strip()[:260]); k+=1
