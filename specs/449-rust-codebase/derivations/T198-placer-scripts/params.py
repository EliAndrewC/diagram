import sys, json, math
sys.path.insert(0, '/tmp/t198')
import inventory as inv, sim2
from inventory import GROUND
c = 48.0
for p in sys.argv[1:]:
    vb, shapes, caps = inv.inventory(p)
    caps = [x for x in caps if x['fbox']]
    N = len(caps); A = vb[2]*vb[3]
    w = sum(x['wN'] for x in caps)/N; h = sum(x['hN'] for x in caps)/N; g = sum(x['fs'] for x in caps)/N/2
    parts = sum(x['parts'] for x in caps)/N
    blk = [s for s in shapes if s['kind'] not in GROUND]
    segs_blk = sum(s['segs'] for s in blk); segs_all = sum(s['segs'] for s in shapes)
    ids = sum(1 for s in shapes if s['ids'])
    # index build: cells each blocking shape's box overlaps
    I0 = sum((int(s['box'][2]//c)-int(s['box'][0]//c)+1)*(int(s['box'][3]//c)-int(s['box'][1]//c)+1) for s in blk)
    rho = I0/(A/c/c)
    Ks = (1+w/c)*(1+h/c)
    # instrument seat vs sweep query cost
    st = sim2.run(p, c)
    qs = st['queries']-st['q_sweep']
    multiword = sum(1 for x in caps if len(x['lines']) == 1 and len(x['words'].split()) >= 2)
    print(json.dumps(dict(sheet=p.split('/')[-1][:-4], N=N, A=A, cells_extent=round(A/c/c,1), shapes=len(shapes), blocking=len(blk),
        blk_segs=segs_blk, all_segs=segs_all, ids=ids, I0=I0, rho_mean=round(rho,2), w=round(w,1), h=round(h,1), g=round(g,2),
        Ks=round(Ks,2), parts=round(parts,2), multiword_single=multiword,
        q_seat=qs, q_sweep=st['q_sweep'], cells_per_q=round(st['cells']/st['queries'],2), entries_per_cell=round(st['entries']/st['cells'],2))))
