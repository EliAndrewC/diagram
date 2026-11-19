"""T198: the hybrid an efficient placer would use - the inside seat, the usual gap (ring 1, with the nearness test) and twice
it (ring 2) as single seats; past twice the gap (a leader owed anyway) a sweep per ranked direction, chunk by chunk outward,
all eight directions advanced together and stopped at the first chunk where one has a clean ring (branch and bound, S9)."""
import sys, json, math
sys.path.insert(0, '/tmp/t198')
from inventory import inventory, GROUND, CROSS
from simulate import RANKS, ov, contains, bdist, Grid, seat

def interval(fb, w, h, r, o, gap):
    """the offsets d where seat(d) overlaps box o: seat x-range and y-range are linear in d."""
    lo, hi = -math.inf, math.inf
    for axis in (0, 1):
        dd = r[axis]
        a0, a1 = (fb[0], fb[2]) if axis == 0 else (fb[1], fb[3])
        size = w if axis == 0 else h
        o0, o1 = (o[0], o[2]) if axis == 0 else (o[1], o[3])
        if dd == 0:
            c = (a0+a1)/2; s0, s1 = c-size/2, c+size/2
            if not (s0 < o1 and o0 < s1): return None
        elif dd > 0:   # seat spans [a1+d, a1+d+size]
            lo = max(lo, o0 - a1 - size); hi = min(hi, o1 - a1)
        else:          # seat spans [a0-d-size, a0-d]
            lo = max(lo, a0 - o1 - size); hi = min(hi, a0 - o0)
    return (lo, hi) if lo < hi else None

def run(path, cell, chunk_rings=8, max_chunks=12):
    vb, shapes, caps = inventory(path)
    ext = (vb[0], vb[1], vb[0]+vb[2], vb[1]+vb[3])
    g = Grid(cell)
    for s in shapes:
        if s['kind'] in GROUND: continue
        g.add(dict(box=s['box'], src=s))
    setup = g.inserts
    st = dict(exact_segs=0, q_inside=0, q_r1=0, q_near=0, q_r2=0, q_sweep=0, queries=0, cells=0, entries=0, exact=0, seats=0, near_dist=0, sweep_intervals=0, leader_dist=0, leader_cells=0,
              captions=0, tried_inside=0, inside=0, ring1=0, ring2=0, swept=0, fallback=0)
    for c in caps:
        if c['fbox'] is None: continue
        st['captions'] += 1
        fb = c['fbox']; own = set(id(s) for s in c['fshapes'])
        w, h = c['wN'], c['hN']; gap = c['fs']/2
        skip = lambda o: o.get('src') is not None and (id(o['src']) in own or contains(o['box'], fb))
        def clean(b):
            st['seats'] += 1
            if not contains(ext, b): return False
            hit = False
            for o in g.query(b, st):
                if skip(o): continue
                if ov(o['box'], b): st['exact'] += 1; st['exact_segs'] += (o['src']['segs'] if o.get('src') else 4); hit = True
            return not hit
        def near_ok(b):
            infl = (b[0]-gap, b[1]-gap, b[2]+gap, b[3]+gap)
            for o in g.query(infl, st):
                if o.get('src') is None or skip(o): continue
                st['near_dist'] += 1
                if bdist(o['box'], b) < gap - 1e-6: return False
            return True
        placed = None
        if w <= fb[2]-fb[0] and h <= fb[3]-fb[1]:
            st['tried_inside'] += 1
            b = seat(fb, w, h, (0, 0), 0); q0 = st['queries']
            ok = clean(b); st['q_inside'] += st['queries'] - q0
            if ok: placed = b; st['inside'] += 1
        if placed is None:
            for r in RANKS:
                b = seat(fb, w, h, r, gap); q0 = st['queries']
                ok = clean(b); st['q_r1'] += st['queries'] - q0; q0 = st['queries']
                ok = ok and near_ok(b); st['q_near'] += st['queries'] - q0
                if ok: placed = b; st['ring1'] += 1; break
        if placed is None:
            for r in RANKS:
                b = seat(fb, w, h, r, 2*gap); q0 = st['queries']
                ok = clean(b); st['q_r2'] += st['queries'] - q0
                if ok: placed = b; st['ring2'] += 1; break
        if placed is None:
            ivs = {r: [] for r in RANKS}
            for j in range(max_chunks):
                d0 = 2*gap + j*chunk_rings*gap; d1 = d0 + chunk_rings*gap
                best = None
                for ri, r in enumerate(RANKS):
                    a, bb = seat(fb, w, h, r, d0), seat(fb, w, h, r, d1)
                    swept = (min(a[0], bb[0]), min(a[1], bb[1]), max(a[2], bb[2]), max(a[3], bb[3]))
                    st['q_sweep'] += 1
                    for o in g.query(swept, st):
                        if skip(o): continue
                        iv = interval(fb, w, h, r, o['box'], gap); st['sweep_intervals'] += 1
                        if iv: ivs[r].append(iv)
                    for k in range(1, chunk_rings+1):
                        d = d0 + k*gap; st['seats'] += 1
                        if any(lo < d < hi for lo, hi in ivs[r]): continue
                        if not contains(ext, seat(fb, w, h, r, d)): continue
                        if best is None or (d, ri) < best[:2]: best = (d, ri, r)
                        break
                if best:
                    placed = seat(fb, w, h, best[2], best[0]); st['swept'] += 1
                    st['leader_dist'] += sum(s['segs'] for s in c['fshapes'])
                    st['leader_cells'] += max(1, int(best[0]//cell)+1)
                    break
            if placed is None: st['fallback'] += 1; placed = seat(fb, w, h, (0, 0), 0)
        g.add(dict(box=placed, src=None))
    st['setup_inserts'] = setup; st['caption_inserts'] = g.inserts - setup
    return st

if __name__ == '__main__':
    cell = float(sys.argv[1]); tot = {}
    for p in sys.argv[2:]:
        r = run(p, cell); name = p.split('/')[-1][:-4]
        print(name, json.dumps(r))
        for k, v in r.items(): tot[k] = tot.get(k, 0) + v
    print('TOTAL', json.dumps(tot))
