"""T208 derivation's own counting script - NOT the project's generator, never runs it.

Reads a sheet's SVG (the generated draft), recovers the generator's INPUT as the sheet shows it (envelope, divider,
gate openings, the reserved ground zones, the masses with their wall and size, the parts and what each is placed
against), then walks the pseudocode of the derivation over that input, counting each operation kind. Where a seat is
needed it takes the seat the sheet shows (the count is the work to REACH that seat by the derivation's search order).

usage: python3 -I count.py <svg> <sheet-name> [cell_ft] [start-variant]
"""
import sys, re, math, json, xml.etree.ElementTree as ET
from collections import defaultdict, Counter

NS = '{http://www.w3.org/2000/svg}'
PX = 3.0  # px per ft
svg, sheet = sys.argv[1], sys.argv[2]
CELL_FT = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
VARIANT = sys.argv[4] if len(sys.argv) > 4 else 'base'
C = CELL_FT * PX

def tag(e): return e.tag.replace(NS, '')

def bbox(e):
    t = tag(e); a = e.attrib
    f = lambda k: float(a.get(k, 0))
    if t == 'rect': return (f('x'), f('y'), f('x') + f('width'), f('y') + f('height'))
    if t == 'circle': return (f('cx') - f('r'), f('cy') - f('r'), f('cx') + f('r'), f('cy') + f('r'))
    if t == 'ellipse': return (f('cx') - f('rx'), f('cy') - f('ry'), f('cx') + f('rx'), f('cy') + f('ry'))
    if t == 'line': return (min(f('x1'), f('x2')), min(f('y1'), f('y2')), max(f('x1'), f('x2')), max(f('y1'), f('y2')))
    return None

# ---- read the sheet: drawn shapes (non-caption) and captions ----
root = ET.parse(svg).getroot()
shapes = []   # (kind, tag, box, id, fill, attrib)
captions = 0
decls = []
leaders = 0
seen_caption = False
def walk(e, kind):
    global captions, leaders, seen_caption
    k = e.attrib.get('data-kind', kind)
    t = tag(e)
    if t in ('defs', 'pattern', 'title'): return
    if t == 'g':
        for c in e: walk(c, k)
        return
    if t == 'text':
        if k != '-':
            seen_caption = True
            decls.append(1)
            if e.attrib.get('data-cont') != '1': captions += 1
        return
    if t == 'tspan': return
    if seen_caption and t == 'line':
        leaders += 1; return  # the caption placer's leader, not this stage's
    shapes.append((k, t, bbox(e), e.attrib.get('data-id', ''), e.attrib.get('fill', ''), e.attrib))
for c in root: walk(c, '?')

# ---- envelope from the compound wall ----
walls = [s for s in shapes if s[0] == 'compound wall']
xs = [b for s in walls for b in (s[2][0], s[2][2])]; ys = [b for s in walls for b in (s[2][1], s[2][3])]
X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
div = [s for s in shapes if s[0] == 'court divider']
YD = div[0][2][1]
FACE = 4.5  # half the 9 px wall
DFACE = 3.0  # half the 6 px divider
env_w, env_h = (X1 - X0) / PX, (Y1 - Y0) / PX

# gate openings: gaps along each wall side, and the divider's gap
def gaps(segs, horiz, lo, hi):
    iv = sorted((s[2][0], s[2][2]) if horiz else (s[2][1], s[2][3]) for s in segs)
    out = []; cur = lo
    for a, b in iv:
        if a > cur + 1: out.append((cur, a))
        cur = max(cur, b)
    if cur < hi - 1: out.append((cur, hi))
    return out
openings = []
for side, horiz, pos in (('N', True, Y0), ('S', True, Y1), ('W', False, X0), ('E', False, X1)):
    segs = [s for s in walls if (horiz and s[2][1] == s[2][3] == pos) or (not horiz and s[2][0] == s[2][2] == pos)]
    for a, b in gaps(segs, horiz, X0 if horiz else Y0, X1 if horiz else Y1):
        openings.append((side, a, b))
for a, b in gaps(div, True, X0, X1):
    openings.append(('D', a, b))
APPROACH = 12 * PX  # a gate's held approach, inside (GUESS of this derivation, the passage's own width scale)
gate_zones = []
for side, a, b in openings:
    if side == 'N': gate_zones.append((a, Y0, b, Y0 + APPROACH))
    if side == 'S': gate_zones.append((a, Y1 - APPROACH, b, Y1))
    if side == 'W': gate_zones.append((X0, a, X0 + APPROACH, b))
    if side == 'E': gate_zones.append((X1 - APPROACH, a, X1, b))
    if side == 'D': gate_zones.append((a, YD - APPROACH, b, YD + APPROACH))

# ---- the reserved ground (the spine and the named yards), never the two precinct rects ----
GROUND = {'garden', 'vegetable garden', 'inner court', 'outer court', 'rear yard', 'hearing court', 'practice ground', 'cart yard'}
zones = [s for s in shapes if s[0] in GROUND and s[1] == 'rect' and s[5].get('id') != 'precinct' and s[3] and s[4].startswith('url(')]
if 'spine' in VARIANT:
    # the spine alone: garden, hearing court, practice ground, and the forecourt (the outer-court ground at the main gate)
    keep = [z for z in zones if z[0] in ('garden', 'hearing court', 'practice ground')]
    main = [o for o in openings if o[0] == 'S']
    mx = (main[0][1] + main[0][2]) / 2 if main else (X0 + X1) / 2
    fc = [z for z in zones if z[0] == 'outer court' and z[2][0] <= mx <= z[2][2]]
    zones = keep + fc[:1]
# ---- the masses ----
MASS = {'storehouse', 'kitchen', 'residence', 'gatehouse', "servants' quarters", 'stables', 'cell', 'granary',
        "retainers' quarters", 'barracks', 'compound shrine', 'guest quarters', 'office hall', 'tax archive',
        'cinnabar workshop', "karo's house", "clerks' room"}
masses = []
taken = set()
for s in shapes:
    k, t, b, i, f, a = s
    if k in MASS and t == 'rect' and i and f not in ('none', '') and i not in taken:
        # a mass is not inside another mass (a room of it)
        if any(m[2][0] <= b[0] and m[2][1] <= b[1] and m[2][2] >= b[2] and m[2][3] >= b[3] for m in masses):
            continue
        masses.append(s); taken.add(i)

def court_of(b): return 'inner' if (b[1] + b[3]) / 2 < YD else 'outer'
def wall_of(b):
    d = {'N': b[1] - (Y0 + FACE), 'S': (Y1 - FACE) - b[3], 'W': b[0] - (X0 + FACE), 'E': (X1 - FACE) - b[2]}
    if court_of(b) == 'inner': d['D'] = (YD - DFACE) - b[3]; d['N'] = d['N']
    else: d['D'] = b[1] - (YD + DFACE)
    if court_of(b) == 'inner': d.pop('S')
    else: d.pop('N')
    w = min(d, key=d.get)
    # a corner building: two faces within 2 ft - it hugs the wall its long side runs along
    near = [k for k in d if d[k] <= d[w] + 2 * PX]
    if len(near) > 1:
        long_horiz = (b[2] - b[0]) >= (b[3] - b[1])
        pick = [k for k in near if (k in ('N', 'S', 'D')) == long_horiz]
        if pick: w = pick[0]
    return w, d[w]

# the joined ell: a mass abutting the residence along its short side (the kitchen)
res = [m for m in masses if m[0] == 'residence'][0]
def abuts(a, b): return (abs(a[2] - b[0]) < 1 or abs(b[2] - a[0]) < 1) and min(a[3], b[3]) > max(a[1], b[1])
joins = [m for m in masses if m[0] == 'kitchen' and abuts(m[2], res[2])]

# tier order (docs/buildings.md): N/S rows, then E/W columns, then the divider; within a tier, larger first
TIER = {'N': 0, 'S': 0, 'W': 1, 'E': 1, 'D': 2}
# the round-trip sheet's walls and orders are its gen.py's program (declared input); the county example's program is
# not readable blind, so its walls are read off the sheet and its order is size
DECLARED = {'ochiba-roundtrip-test': {
    'residence': ('N', 10), "servants' quarters": ('S', 7), 'storehouse': ('N', 8), 'compound shrine': ('E', 5),
    'cinnabar workshop': ('E', 4), "karo's house": ('D', 3), 'office hall': ('D', 10), 'tax archive': ('W', 6),
    "retainers' quarters": ('W', 4), 'granary': ('E', 6), 'barracks': ('E', 4), 'cell': ('E', 1), 'gatehouse': ('S', 8),
    'stables': ('S', 5), "clerks' room": ('W', 3)}}
plan = []
for m in masses:
    if m in joins: continue
    w, off = wall_of(m[2])
    area = (m[2][2] - m[2][0]) * (m[2][3] - m[2][1])
    key = -area
    if sheet in DECLARED:
        w, order = DECLARED[sheet][m[0]]
        key = (-order, -area)
        bb = m[2]
        off = {'N': bb[1] - (Y0 + FACE), 'S': (Y1 - FACE) - bb[3], 'W': bb[0] - (X0 + FACE), 'E': (X1 - FACE) - bb[2],
               'D': (bb[1] - (YD + DFACE)) if court_of(bb) == 'outer' else ((YD - DFACE) - bb[3])}[w]
    else:
        key = (0, -area)
    plan.append((TIER[w], key, m, w, off))
plan.sort(key=lambda p: (p[0], p[1]))
if VARIANT == 'rev':
    plan.sort(key=lambda p: (p[0], tuple(-x for x in p[1])))

# ---- the grid ----
class Cat(Counter):
    cat = 'once'
    def __init__(self):
        super().__init__(); self.by = defaultdict(Counter)
    def __setitem__(self, k, v):
        old = self.get(k, 0); super().__setitem__(k, v); self.by[self.cat][k] += v - old
cnt = Cat()
grid = defaultdict(list)
def cells(b):
    i0, j0 = int(math.floor(b[0] / C)), int(math.floor(b[1] / C))
    i1, j1 = int(math.floor((b[2] - 1e-9) / C)), int(math.floor((b[3] - 1e-9) / C))
    return [(i, j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)]
def insert(b, what):
    e = (b, what)
    for c in cells(b):
        grid[c].append(e); cnt['index_insert'] += 1
def meet(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
def query(b, circle=False):
    cnt['index_query'] += 1
    hits = {}
    for c in cells(b):
        cnt['index_cell'] += 1
        for e in grid[c]:
            cnt['index_entry'] += 1
            if meet(e[0], b): hits[id(e)] = e
    if circle: cnt['exact_test'] += len(hits)
    return list(hits.values())

cnt.cat = 'zone'
for z in zones:
    query(z[2]); cnt['rule_check'] += 1  # inside its court, clear of the zones filed before it
    insert(z[2], 'zone')
cnt.cat = 'once'
div_gates = [g for g, o in zip(gate_zones, openings) if o[0] == 'D']
for g, o in zip(gate_zones, openings):
    if o[0] != 'D': insert(g, 'gate')
cnt['seat'] += 0

# ---- masses: a wall span search per mass, advancing a cell column at a time from the tier's start ----
GAP = 6 * PX   # a wooden fire gap, 6-8 ft (0116's drawing page); a kura's 6-10
def span_search(m, w, off):
    b = m[2]
    horiz = w in ('N', 'S', 'D')
    lo_court = (Y0 if court_of(b) == 'inner' else YD), (YD if court_of(b) == 'inner' else Y1)
    if horiz:
        a0, a1 = X0 + FACE, X1 - FACE        # along x
        if w == 'N': d0, d1 = Y0 + FACE, b[3]
        elif w == 'S': d0, d1 = b[1], Y1 - FACE
        elif court_of(b) == 'inner': d0, d1 = b[1], YD - DFACE
        else: d0, d1 = YD + DFACE, b[3]
        s0, s1 = b[0], b[2]
    else:
        a0, a1 = lo_court[0] + (FACE if court_of(b) == 'inner' else DFACE), lo_court[1] - (DFACE if court_of(b) == 'inner' else FACE)
        if w == 'W': d0, d1 = X0 + FACE, b[2]
        else: d0, d1 = b[0], X1 - FACE
        s0, s1 = b[1], b[3]
    # the start: N/S rows from the west corner, E/W columns from the court's north end, the divider tier from the middle
    if VARIANT == 'flip':
        start = 'hi' if w != 'D' else 'mid'
    else:
        start = 'lo' if w != 'D' else 'mid'
    span = []
    # THE WALL'S ROW (incremental): the rank-1 buildings already seated against this wall, as intervals along it. Each touches the
    # wall's face, so each blocks every later band on the wall whatever its depth: the search resumes at the first gap in the row
    # long enough for this building, never re-reading the filled stretch (S3).
    key_w = (w, court_of(b))
    row = rows_by_wall.setdefault(key_w, [])
    L = s1 - s0
    lo_start = a0
    if start == 'lo' and 'corner' not in VARIANT:
        cur = a0
        for a, bb in row:
            cnt['span_compare'] += 1
            if a - cur >= L: break
            cur = max(cur, bb)
        if cur > s0 + 1: clamps.append(m[0])
        lo_start = min(cur, s0)
    if start == 'lo': reach = [(lo_start, s1 + GAP)]
    elif start == 'hi': reach = [(s0 - GAP, a1)]
    else:
        mid = (a0 + a1) / 2; r = max(abs(s1 + GAP - mid), abs(mid - (s0 - GAP)))
        reach = [(mid - r, mid + r)]
    # chunks of one cell column along the wall: count cells and entries over the reached stretch
    lo, hi = reach[0]
    lo, hi = max(lo, a0), min(hi, a1)
    box = (lo, d0, hi, d1) if horiz else (d0, lo, d1, hi)
    ncols = max(1, int(math.ceil((hi - lo) / C)))
    cnt['span_query'] += ncols
    hits = query(box)
    cnt['index_query'] -= 1  # the strip is counted as span_query chunks, not one query
    global early, verdict
    full = (a0, d0, a1, d1) if horiz else (d0, a0, d1, a1)
    allhits = [e for c_ in cells(full) for e in grid[c_] if meet(e[0], full)]
    uniq = {id(e): e for e in allhits}.values()
    blocked = []
    for e in uniq:
        lo_, hi_ = (e[0][0], e[0][2]) if horiz else (e[0][1], e[0][3])
        g = GAP if e[1] == 'mass' else 0
        blocked.append((lo_ - g, hi_ + g))
    blocked.sort()
    merged = []
    for x0_, x1_ in blocked:
        if merged and x0_ <= merged[-1][1]: merged[-1] = (merged[-1][0], max(merged[-1][1], x1_))
        else: merged.append((x0_, x1_))
    frees = []; cur_ = a0
    for x0_, x1_ in merged:
        if x0_ > cur_: frees.append((cur_, x0_))
        cur_ = max(cur_, x1_)
    if cur_ < a1: frees.append((cur_, a1))
    Lb = s1 - s0
    fits = [f_ for f_ in frees if f_[1] - f_[0] >= Lb - 0.5]
    seat_free = any(f_[0] - 0.5 <= s0 and s1 <= f_[1] + 0.5 for f_ in frees)
    if start == 'mid':
        mid_ = (a0 + a1) / 2
        cand = [max(f_[0], min(mid_ - Lb / 2, f_[1] - Lb)) for f_ in fits]
        first = min(cand, key=lambda x: abs(x + Lb / 2 - mid_)) if cand else None
    else:
        first = fits[0][0] if fits else None
    if not seat_free: verdict = 'seat blocked'
    elif first is None: verdict = 'no span'
    elif abs(first - s0) <= GAP: verdict = 'first free'
    elif (start != 'mid' and first < s0) or (start == 'mid' and abs(first + Lb/2 - (a0+a1)/2) < abs(s0 + Lb/2 - (a0+a1)/2)): verdict = 'earlier span (%.0f ft)' % ((s0 - first) / PX)
    else: verdict = 'other'
    L = (s1 - s0)
    iv = sorted(((e[0][0], e[0][2]) if horiz else (e[0][1], e[0][3])) for e in hits)
    iv = [(a - (GAP if wh != 'zone' else 0), b + (GAP if wh != 'zone' else 0)) for (a, b), wh in zip(iv, [e[1] for e in sorted(hits, key=lambda e: (e[0][0], e[0][2]) if horiz else (e[0][1], e[0][3]))])]
    early = None
    if start in ('lo',):
        cur = a0
        for a, b in sorted(iv):
            if a - cur >= L and cur + 1 < s0: early = (cur, a); break
            cur = max(cur, b)
    n = len(hits)
    cnt['span_interval'] += n
    cnt['span_compare'] += (int(math.ceil(n * math.log2(n))) if n > 1 else 0) + n + 1
    cnt['seat'] += 1
    if off <= 2 * PX:  # touches the wall (its 1.5 ft clearance): it blocks every later band on this wall
        row.append((s0 - GAP, s1 + GAP)); row.sort()
        cnt['span_compare'] += max(1, int(math.ceil(math.log2(len(row) + 1))))  # the row's sorted insert
    return n

per_mass = []
clamps = []
rows_by_wall = {}
cnt.cat = 'mass'
for tier, _, m, w, off in plan:
    before = sum(cnt.values()); snap = dict(cnt)
    n = span_search(m, w, off)
    cnt['rule_check'] += 5   # band w, band h, court zoning, wall-hugging, coverage sum
    insert(m[2], 'mass')
    cnt['write'] += 0
    per_mass.append((m[0], w, n, sum(cnt.values()) - before, verdict, {k: cnt.get(k, 0) - snap.get(k, 0) for k in ('span_query', 'index_cell', 'index_entry', 'span_interval', 'span_compare', 'index_insert')}))
    if m[0] == 'office hall':
        for g in div_gates: cnt['rule_check'] += 1; insert(g, 'gate')  # the middle gate fixed behind the hall, its approach held
    if m is res:
        cnt.cat = 'ell'
        for j in joins:  # the ell: the two ends of the house, the near one first (one query each tried)
            cnt['seat'] += 1; query(j[2]); cnt['rule_check'] += 5; insert(j[2], 'mass')
        cnt.cat = 'mass'

# ---- doors: the seat from the spec's face and fraction (O(1)); its approach asked of the grid; filed ----
doors = [s for s in shapes if s[0] == 'door' and s[1] == 'rect']
cnt.cat = 'door'
for d in doors:
    b = d[2]
    ap = (b[0] - 3, b[1] - 3, b[2] + 3, b[3] + 3)  # the door's mouth and a step before it
    cnt['seat'] += 1; query(ap); insert(ap, 'door'); cnt['rule_check'] += 1  # on its wall, inside its building

# ---- parts: each against its anchor face, faces in rank order, one face-strip query per face tried ----
def nearest_mass(b):
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    def dist(m):
        mb = m[2]; dx = max(mb[0] - cx, 0, cx - mb[2]); dy = max(mb[1] - cy, 0, cy - mb[3]); return math.hypot(dx, dy)
    return min(masses, key=dist)
def face_strip(anchor, part, reach_px):
    """the strip along the anchor's face that the part touches, reach_px either side of the part's own span"""
    a = anchor; p = part
    cx, cy = (p[0] + p[2]) / 2, (p[1] + p[3]) / 2
    dists = {'N': abs(cy - a[1]), 'S': abs(cy - a[3]), 'W': abs(cx - a[0]), 'E': abs(cx - a[2])}
    f = min(dists, key=dists.get)
    if f in ('N', 'S'):
        return f, (max(a[0], p[0] - reach_px), min(p[1], a[1] if f == 'N' else a[3]), min(a[2], p[2] + reach_px), max(p[3], a[1] if f == 'N' else a[3]))
    return f, (min(p[0], a[0] if f == 'W' else a[2]), max(a[1], p[1] - reach_px), max(p[2], a[0] if f == 'W' else a[2]), min(a[3], p[3] + reach_px))
def place_part(b, faces_tried, circle, reach_px, label):
    anchor = nearest_mass(b)
    for _ in range(faces_tried):
        f, strip = face_strip(anchor[2], b, reach_px)
        cnt['seat'] += 1
        hits = query(strip, circle)
        n = len(hits)
        cnt['span_interval'] += n
        cnt['span_compare'] += (int(math.ceil(n * math.log2(n))) if n > 1 else 0) + n + 1
    cnt['rule_check'] += 2
    insert(b, label)

wells = [s for s in shapes if s[0] == 'well' and s[1] == 'rect' and s[3]]
tubs = [s for s in shapes if s[0] == 'fire-water tubs' and s[1] == 'circle']
privies = [s for s in shapes if s[0] == 'latrine' and s[1] == 'rect' and s[4] == '#7E726A']
board = [s for s in shapes if s[0] == 'notice board' and s[1] == 'rect']
tree = [s for s in shapes if s[0] == 'sacred tree']
bath = [s for s in shapes if s[0] == 'bath' and s[1] == 'rect' and s[3]]
rack = [s for s in shapes if s[0] == 'weapon rack']
posts = [s for s in shapes if s[0] == 'striking posts' and s[1] == 'circle']
stones = [s for s in shapes if s[0] == 'garden' and s[1] in ('ellipse',)] + [s for s in shapes if s[3] == 'd74' and s[0] == 'garden']

# the tub's rule: beside a door of its building, within 10.5 ft, against the wall - the door's face first, then
# round the nearer corner. Measured on the sheet: is the tub on its door's face?
def tub_faces(t):
    b = t[2]; cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    best = min(doors, key=lambda d: math.hypot((d[2][0] + d[2][2]) / 2 - cx, (d[2][1] + d[2][3]) / 2 - cy))
    db = best[2]
    horiz_door = (db[2] - db[0]) > (db[3] - db[1])
    if horiz_door: on_face = abs(cy - (db[1] + db[3]) / 2) < 10 * PX / 3 + 6
    else: on_face = abs(cx - (db[0] + db[2]) / 2) < 10 * PX / 3 + 6
    return 1 if on_face else 2
REACH_TUB = 10.5 * PX
order_parts = []
order_parts += [(b[2], 1, False, 5 * PX, 'bath') for b in bath]
tub_face_counts = [tub_faces(t) for t in tubs]
for w in wells: order_parts.append((w[2], 1, False, 20 * PX, 'well'))
for t, f in zip(tubs, tub_face_counts): order_parts.append((t[2], f, True, REACH_TUB, 'tub'))
for p in privies: order_parts.append((p[2], 1, False, 15 * PX, 'privy'))  # the box grown by 15 ft finds any well
for b in board: order_parts.append((b[2], 1, False, 15 * PX, 'board'))
for t in tree: order_parts.append((t[2], 1, True, 15 * PX, 'tree'))
for r in rack: order_parts.append((r[2], 1, False, 0, 'rack'))
for p in posts: order_parts.append((p[2], 1, True, 0, 'post'))
cnt.cat = 'part'
for b, f, circ, reach, lab in order_parts:
    place_part(b, f, circ, reach, lab)
# the kitchen garden's sun (garden_sun): the ground south of it that could shade it, about 20 ft, asked once
veg = [s for s in shapes if s[0] == 'vegetable garden' and s[1] == 'rect']
for v in veg:
    b = v[2]; query((b[0], b[3], b[2], b[3] + 20 * PX)); cnt['rule_check'] += 1
cnt.cat = 'roji'
# the roji: stepping stones on one line from the middle gate to the shoe stone, one query of the line's box
if stones:
    xs_ = [s[2][0] for s in stones] + [s[2][2] for s in stones]; ys_ = [s[2][1] for s in stones] + [s[2][3] for s in stones]
    query((min(xs_), min(ys_), max(xs_), max(ys_)))
    cnt['seat'] += len(stones)

cnt.cat = 'once'
# which masses take a tub (wooden, the kura none, the kitchen two) and which zones owe a privy: one decision a mass
cnt['rule_check'] += len(masses) + 3
# ---- the open ground: per court, slabs between the masses' x-edges; free y-intervals; adjacency for the cart route ----
def slabs(court_box, items):
    xe = sorted(set([court_box[0], court_box[2]] + [x for b in items for x in (b[0], b[2]) if court_box[0] < x < court_box[2]]))
    n = len(xe); cnt['sweep_op'] += int(math.ceil(n * math.log2(max(n, 2))))
    rects = []
    for i in range(len(xe) - 1):
        a, b_ = xe[i], xe[i + 1]
        cross = sorted((b[1], b[3]) for b in items if b[0] < b_ and a < b[2])
        cnt['sweep_op'] += len(cross) + 1
        cur = court_box[1]
        for y0, y1 in cross:
            if y0 > cur: rects.append((a, cur, b_, y0))
            cur = max(cur, y1)
        if cur < court_box[3]: rects.append((a, cur, b_, court_box[3]))
    # adjacency between neighbouring slabs (merge-walk of sorted intervals)
    by_x = defaultdict(list)
    for r in rects: by_x[r[0]].append(r)
    edges = 0
    for i in range(len(xe) - 2):
        L = by_x[xe[i]]; R = by_x[xe[i + 1]]
        cnt['graph_edge'] += len(L) + len(R)
    cnt['graph_edge'] += len(rects)  # BFS visits each free rectangle once
    return rects
mb = [m[2] for m in masses]
inner = (X0 + FACE, Y0 + FACE, X1 - FACE, YD - DFACE); outer = (X0 + FACE, YD + DFACE, X1 - FACE, Y1 - FACE)
r_in = slabs(inner, [b for b in mb if court_of(b) == 'inner'])
r_out = slabs(outer, [b for b in mb if court_of(b) == 'outer'])

# ---- composition checks once: coverage, hierarchy pairs ----
cnt['rule_check'] += 12  # the hierarchy pairs of the checklist's size sweep
# ---- rolls: the knobs and each well's gear and roof ----
cnt['roll'] += 6 + 2 * len(wells)
# ---- writes: every drawn shape of this stage (captions and leaders are the placer's) ----
cnt['write'] += len(shapes)
cnt['decl_write'] += len(decls)  # each caption's declaration (words, face, size, what it names); its seat is the placer's

total = sum(cnt.values())
sizes = dict(decls=len(decls), env_ft=f'{env_w:.0f} x {env_h:.0f}', masses=len(masses), joins=len(joins), zones=len(zones),
             gates=len(openings), doors=len(doors), wells=len(wells), tubs=len(tubs), privies=len(privies),
             board=len(board), tree=len(tree), bath=len(bath), rack=len(rack), posts=len(posts), stones=len(stones),
             shapes=len(shapes), captions=captions, leaders=leaders, free_rects=len(r_in) + len(r_out),
             tub_round_corner=sum(1 for f in tub_face_counts if f == 2))
by = {k: dict(sorted(v.items())) for k, v in cnt.by.items()}
print(json.dumps(dict(sheet=sheet, cell_ft=CELL_FT, variant=VARIANT, sizes=sizes, counts=dict(sorted(cnt.items())), total=total, by=by, nparts=len(order_parts), face_queries=sum(o[1] for o in order_parts), circle_parts=sum(1 for o in order_parts if o[2]))))
if '-v' in sys.argv:
    for row in per_mass: print(row)
    print('verdicts:', Counter(r[4].split(' (')[0] for r in per_mass)); print('clamped:', clamps)
