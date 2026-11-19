"""T198: my own minimal ranked-seat search over each pool sheet's input, to measure the TYPICAL case (rubric S8) an efficient
placer meets: seats tried to the first clean one, index cells and entries read per seat, nearness and leader work.
It is not the project's placer and reads none of it; it implements 0242/0330 as the derivation's pseudocode states."""
import sys, json, math
sys.path.insert(0, '/tmp/t198')
from inventory import inventory, GROUND, CROSS
RANKS = [(0,-1),(0,1),(1,0),(1,-1),(1,1),(-1,0),(-1,-1),(-1,1)]   # above, below, right, UR, LR, left, UL, LL (0242)

def ov(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
def contains(a, b): return a[0] <= b[0] and a[1] <= b[1] and a[2] >= b[2] and a[3] >= b[3]
def bdist(a, b):
    dx = max(a[0]-b[2], b[0]-a[2], 0); dy = max(a[1]-b[3], b[1]-a[3], 0); return math.hypot(dx, dy)

class Grid:
    def __init__(s, cell): s.c = cell; s.cells = {}; s.inserts = 0
    def keys(s, b):
        for i in range(int(b[0]//s.c), int(b[2]//s.c)+1):
            for j in range(int(b[1]//s.c), int(b[3]//s.c)+1): yield (i, j)
    def add(s, o):
        for k in s.keys(o['box']): s.cells.setdefault(k, []).append(o); s.inserts += 1
    def query(s, b, st):
        st['queries'] += 1; seen = {}
        for k in s.keys(b):
            st['cells'] += 1
            for o in s.cells.get(k, ()):
                st['entries'] += 1; seen[id(o)] = o
        return seen.values()

def seat(fb, w, h, dirn, d):
    dx, dy = dirn
    fcx, fcy = (fb[0]+fb[2])/2, (fb[1]+fb[3])/2
    cx = fcx if dx == 0 else (fb[2]+d+w/2 if dx > 0 else fb[0]-d-w/2)
    cy = fcy if dy == 0 else (fb[3]+d+h/2 if dy > 0 else fb[1]-d-h/2)
    return (cx-w/2, cy-h/2, cx+w/2, cy+h/2)

def run(path, cell, kmax=30):
    vb, shapes, caps = inventory(path)
    ext = (vb[0], vb[1], vb[0]+vb[2], vb[1]+vb[3])
    g = Grid(cell)
    for s in shapes:
        if s['kind'] in GROUND: continue
        g.add(dict(box=s['box'], w=0.5 if s['kind'] in CROSS else 1.0, src=s, segs=s['segs']))
    setup_inserts = g.inserts
    st = dict(queries=0, cells=0, entries=0, exact=0, seats=0, near_dist=0, leader_dist=0, leader_cross=0)
    per = []
    for c in caps:
        if c['fbox'] is None: continue
        fb = c['fbox']; own = set(id(s) for s in c['fshapes'])
        w, h = c['wN'], c['hN']; gap = c['fs']/2
        def clean(b):
            st['seats'] += 1
            if not contains(ext, b): return False
            hit = False
            for o in g.query(b, st):
                if o.get('src') is not None and (id(o['src']) in own or contains(o['box'], fb)): continue
                if ov(o['box'], b): st['exact'] += 1; hit = True
            return not hit
        def near_ok(b):
            # 0242: at the usual gap, nearer its own feature than any other: neighbors within the gap of the box
            infl = (b[0]-gap, b[1]-gap, b[2]+gap, b[3]+gap)
            for o in g.query(infl, st):
                if o.get('src') is None or id(o['src']) in own or contains(o['box'], fb): continue
                st['near_dist'] += 1
                if bdist(o['box'], b) < gap - 1e-6: return False
            return True
        s0 = st['seats']; how = None
        fw, fh = fb[2]-fb[0], fb[3]-fb[1]
        if w <= fw and h <= fh:
            b = seat(fb, w, h, (0, 0), 0)
            if clean(b): how = ('inside', 0)
        if how is None:
            for k in range(1, kmax+1):
                d = gap * k
                for r in RANKS:
                    b = seat(fb, w, h, r, d)
                    if clean(b) and (k > 1 or near_ok(b)): how = ('beside', k); break
                if how: break
        if how is None: how = ('fallback', None)
        if how[0] == 'beside' and how[1] > 2:
            # 0330: nearest drawn point of the feature, over its parts' segments
            st['leader_dist'] += sum(s['segs'] for s in c['fshapes'])
            # leader against captions/buildings it would cross: cells along the leader
            L = gap*how[1]; n = max(1, int(L//cell)+1); st['leader_cross'] += n
        g.add(dict(box=b if how[0] != 'fallback' else seat(fb, w, h, (0, 0), 0), w=1.0, src=None, segs=4))
        per.append(dict(how=how, seats=st['seats']-s0))
    return dict(captions=len(per), setup_inserts=setup_inserts, caption_inserts=g.inserts-setup_inserts, **st,
                inside=sum(1 for p in per if p['how'][0] == 'inside'),
                ring1=sum(1 for p in per if p['how'] == ('beside', 1)),
                ring2=sum(1 for p in per if p['how'] == ('beside', 2)),
                leader=sum(1 for p in per if p['how'][0] == 'beside' and p['how'][1] > 2),
                fallback=sum(1 for p in per if p['how'][0] == 'fallback'),
                rings_leader=[p['how'][1] for p in per if p['how'][0] == 'beside' and p['how'][1] > 2],
                seats_hist=sorted(p['seats'] for p in per))

if __name__ == '__main__':
    cell = float(sys.argv[1])
    tot = {}
    for p in sys.argv[2:]:
        r = run(p, cell)
        name = p.split('/')[-1][:-4]
        print(name, json.dumps({k: v for k, v in r.items() if k != 'seats_hist'}))
        print('   seats per caption:', r['seats_hist'])
