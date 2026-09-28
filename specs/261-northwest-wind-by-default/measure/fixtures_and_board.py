"""Per pool hamlet: homestead plots, fixtures and persimmons across a lane from their house, unseated fixtures, the board seat."""
import json,sys
import os as _os
POOL = "pool/hamlets" if _os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
sys.path.insert(0,'.')
def cross(p,q,a,b):
    def o(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    return o(p,q,a)*o(p,q,b)<0 and o(a,b,p)*o(a,b,q)<0
for m in ['inashiro','kashikawa','kuwabata','mizuguchi','sawada']:
    M=json.load(open(POOL + f'/{m}/{m}.json'))
    hf=[d for d in M.get('dry_plots',[]) if d.get('homestead')]
    across=0; tot=0
    for key in ('farm_fixtures','persimmons'):
        for r in M.get(key,[]):
            of=r.get('of')
            if not of: continue
            tot+=1
            if any(cross(tuple(of),(r['x'],r['y']),tuple(l['pts'][k]),tuple(l['pts'][k+1])) for l in M['lanes'] for k in range(len(l['pts'])-1)): across+=1
    k=M['kosatsuba'][-1]
    print(m,'homestead plots',len(hf),'fixtures',tot,'across lane',across,'unseated',M['meta'].get('farm_fixtures_unseated'),'board',round(k['x']),round(k['y']),k.get('rot'),'caption',M['meta'].get('kosatsuba_caption_level'),'roll',M['meta'].get('roll_attempt'))
