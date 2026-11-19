"""T198 sim 2: an efficient placer for 0242/0330, written blind from the rules, run on each sheet's input to measure the
TYPICAL case (S8). Per caption: the inside seat (when the block fits the feature's box); the usual gap's eight ranked seats,
each clean one asked the nearness test; then a continuous sweep outward per ranked direction from just past the usual gap,
chunk by chunk, all eight advanced together and stopped at the first chunk where one is clean (branch and bound), the
nearest free offset winning, rank breaking ties. Wrap reading A: the declared block first, 2 then 3 lines only where no
clean seat lies within reach. Reading B (WRAP=B): at every rejected ring-1 seat and every swept direction, 2 then 3 lines too."""
import sys, json, math
sys.path.insert(0, '/tmp/t198')
import inventory as inv
from inventory import GROUND, CROSS
from simulate import RANKS, ov, contains, bdist, Grid, seat
from hybrid import interval

def layouts(c, k):
    """the caption's blocks: the declared one, then the min-max cut into 2 and 3 lines where it has the words (0242)."""
    out = [(c['wN']*k, c['hN'])]
    words = c['words'].split()
    if len(c['lines']) == 1 and len(words) >= 2:
        kk = 0.58 if c['bold'] else 0.52
        wl = lambda ws: len(' '.join(ws)) * (c['fs']*kk + c['ls']) * k
        for n in (2, 3):
            if len(words) < n: break
            best = None
            import itertools
            for cut in itertools.combinations(range(1, len(words)), n-1):
                parts = [words[a:b] for a, b in zip((0,)+cut, cut+(len(words),))]
                m = max(wl(p) for p in parts)
                if best is None or m < best: best = m
            out.append((best, n*c['fs']*1.15))
    return out

def run(path, cell=48.0, k=1.0, wrap='A', reach_chunks=12, start=1.5, first_to=2.0, chunk_g=None, chunk_px=48.0, reach_g=96.0):
    vb, shapes, caps = inv.inventory(path)
    ext = (vb[0], vb[1], vb[0]+vb[2], vb[1]+vb[3])
    g = Grid(cell)
    for s in shapes:
        if s['kind'] in GROUND: continue
        g.add(dict(box=s['box'], src=s))
    st = dict(captions=0, setup_inserts=g.inserts, seats=0, queries=0, cells=0, entries=0, exact=0, exact_segs=0,
              near_dist=0, sweep_intervals=0, sweep_cmp=0, leader_dist=0, inserts=0, cuts=0,
              tried_inside=0, inside=0, ring1=0, within2g=0, leader=0, fallback=0, q_sweep=0, first_strips=0, later_chunks=0, stop_first=0, stop_later=0, first_cells=0, first_entries=0, q_near=0, near_cells=0, near_entries=0, sweep_cells=0, sweep_entries=0, r1_seats=0, reach_r1=0, chunks=0, wrapped=0)
    for c in caps:
        if c['fbox'] is None: continue
        st['captions'] += 1
        fb = c['fbox']; own = set(id(s) for s in c['fshapes']); gap = c['fs']/2
        skip = lambda o: o.get('src') is not None and (id(o['src']) in own or contains(o['box'], fb))
        L = layouts(c, k); st['cuts'] += max(0, len(L)-1)
        def clean(b):
            st['seats'] += 1
            if not contains(ext, b): return False
            hit = False
            for o in g.query(b, st):
                if skip(o): continue
                if ov(o['box'], b): st['exact'] += 1; st['exact_segs'] += (o['src']['segs'] if o.get('src') else 4); hit = True
            return not hit
        def near_ok(b):
            st['q_near'] += 1; c0, e0 = st['cells'], st['entries']
            try:
                return _near(b)
            finally:
                st['near_cells'] += st['cells']-c0; st['near_entries'] += st['entries']-e0
        def _near(b):
            infl = (b[0]-gap, b[1]-gap, b[2]+gap, b[3]+gap)
            for o in g.query(infl, st):
                if o.get('src') is None or skip(o): continue
                st['near_dist'] += 1
                if bdist(o['box'], b) < gap - 1e-6: return False
            return True
        def search(lays):
            # lays: the layouts tried at each seat (A: one; B: all)
            (w, h) = lays[0]
            if w <= fb[2]-fb[0] and h <= fb[3]-fb[1]:
                st['tried_inside'] += 1
                b = seat(fb, w, h, (0, 0), 0)
                if clean(b): return b, 'inside'
            st['reach_r1'] += 1
            for r in RANKS:
                for (w, h) in lays:
                    b = seat(fb, w, h, r, gap); st['r1_seats'] += 1
                    if clean(b) and near_ok(b): return b, 'ring1'
            ivs = {(r, lw): [] for r in RANKS for lw in lays}
            # the chunk schedule: a first strip from START*g to FIRST_TO*g (0242's no-leader zone), then chunks of a fixed length
            bounds = [start*gap]
            if first_to: bounds.append(first_to*gap)
            L = chunk_g*gap if chunk_g else chunk_px
            while bounds[-1] < reach_g*gap: bounds.append(bounds[-1] + L)
            for j in range(len(bounds)-1):
                st['chunks'] += 1
                if j == 0: st['first_strips'] += 1
                else: st['later_chunks'] += 1
                d0 = bounds[j]; d1 = bounds[j+1]
                best = None
                for ri, r in enumerate(RANKS):
                    for (w, h) in lays:
                        a, bb = seat(fb, w, h, r, d0), seat(fb, w, h, r, d1)
                        sw = (min(a[0], bb[0]), min(a[1], bb[1]), max(a[2], bb[2]), max(a[3], bb[3]))
                        st['q_sweep'] += 1; c0, e0 = st['cells'], st['entries']
                        lst = ivs[(r, (w, h))]; new = []
                        qq = list(g.query(sw, st)); st['sweep_cells'] += st['cells']-c0; st['sweep_entries'] += st['entries']-e0
                        if j == 0: st['first_cells'] += st['cells']-c0; st['first_entries'] += st['entries']-e0
                        for o in qq:
                            if skip(o): continue
                            iv = interval(fb, w, h, r, o['box'], gap); st['sweep_intervals'] += 1
                            if iv and iv[1] > d0: new.append(iv)
                        n = len(new); st['sweep_cmp'] += n*max(1, math.ceil(math.log2(n+1))) + n if n else 0
                        # the extent as an interval of allowed offsets
                        ex = interval(fb, w, h, r, ext, gap)
                        lo_ok, hi_ok = (ex if ex else (math.inf, -math.inf))
                        # need box INSIDE extent: approximate by testing candidate below
                        lst.extend(new); lst.sort()
                        d = d0 + 1e-6
                        for lo, hi in lst:
                            if hi <= d: continue
                            st['sweep_cmp'] += 1
                            if lo < d < hi: d = hi + 1e-6
                            elif lo >= d: break
                        st['seats'] += 1
                        if d <= d1 and contains(ext, seat(fb, w, h, r, d)):
                            if best is None or (d, ri) < best[:2]: best = (d, ri, r, w, h)
                if best:
                    st['stop_first' if j == 0 else 'stop_later'] += 1
                    d, ri, r, w, h = best
                    return seat(fb, w, h, r, d), ('within2g' if d <= 2*gap else 'leader')
            return None, 'fallback'
        if wrap == 'B':
            b, how = search(L)
        else:
            b, how = search(L[:1])
            if how == 'fallback':
                for lay in L[1:]:
                    st['wrapped'] += 1
                    b, how = search([lay])
                    if how != 'fallback': break
        st[how] += 1
        if how == 'leader': st['leader_dist'] += sum(s['segs'] for s in c['fshapes'])
        if b is None: b = seat(fb, L[0][0], L[0][1], (0, 0), 0)
        n0 = g.inserts; g.add(dict(box=b, src=None)); st['inserts'] += g.inserts - n0
    return st

KEYS = ['seats','queries','cells','entries','exact_segs','near_dist','sweep_intervals','sweep_cmp','leader_dist','inserts','cuts']
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--k', type=float, default=1.0); ap.add_argument('--wrap', default='A')
    ap.add_argument('--cell', type=float, default=48.0); ap.add_argument('--quiet', action='store_true'); ap.add_argument('svgs', nargs='+')
    a = ap.parse_args(); tot = {}
    for p in a.svgs:
        r = run(p, a.cell, a.k, a.wrap); name = p.split('/')[-1][:-4]
        r['work'] = sum(r[x] for x in KEYS)
        if not a.quiet: print(name, json.dumps(r))
        for kk, v in r.items(): tot[kk] = tot.get(kk, 0) + v
    print('TOTAL', json.dumps(tot))
