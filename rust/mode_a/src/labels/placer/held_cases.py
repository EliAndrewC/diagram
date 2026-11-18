"""The placer's held cases (feature 449 T151): seeded scenes, the Python placer's answers, written for the Rust's unit test.

KEPT AS THE RECORD OF HOW THE HELD ANSWERS WERE TAKEN (feature 449 T151): `held.json` beside this file is the Python's answers,
written from the tree's `l7r/diagram/labels/`, and the Rust placer's unit test reads it. This script goes when step 3b deletes that
Python; the answers stay as the record. NOT A BYTE-FOR-BYTE REPRODUCTION: `held.json` was written by a revision of this script that
was not kept, whose subject draws differ (its first scene's obstacles are this one's, its subject not); this revision, run as below, writes
sixty other scenes, which the Rust placer also answers as the Python does but which leave six of its lines unreached, so the
earlier file stays (measured 2026-11-18, part B of T151: the placer's tests green on both files, `make static`'s coverage red on
this one's).

    python3 -I rust/mode_a/src/labels/placer/held_cases.py rust/mode_a/src/labels/placer/held.json 449 60

Feature 449 T184 re-took the answers of the stored scenes, the scenes themselves unchanged, after its fixes to the Python placer:

    python3 -I rust/mode_a/src/labels/placer/held_cases.py --reanswer rust/mode_a/src/labels/placer/held.json

and feature 449 T188 again, the same way, after its own (four scenes' captions back on one line).
"""
import json, random, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[5]))  # the tree: <tree>/rust/mode_a/src/labels/<unit>/
from l7r.diagram.labels import Obstacle, ObstacleIndex, Subject, Way, circle_obstacle, place, caption_clears_ways
from l7r.diagram.labels.geom import rect
from l7r.diagram.labels.obstacles import stands_nearest
from l7r.diagram.labels.placer import NUDGE_REACH
from l7r.diagram.labels.standard import WEIGHT_OBSTACLE

def F(v): return None if v is None else "f:" + repr(float(v))
def P(pts): return [[F(x), F(y)] for x, y in pts]

TEXTS = ["notice board", "well", "Shrine of Benten", "INNER COURT", "the old granary of the east", "tax barge", "a b c d"]
GROUPS = [None, "grove", "temple", "funerary", "ministry", "gate"]

def scene(rng):
    obs = []
    for _ in range(rng.randint(0, 12) if rng.random() < 0.6 else rng.randint(20, 40)):
        r = rng.random()
        if r < 0.35:
            obs.append(circle_obstacle(round(rng.uniform(0, 200), 1), round(rng.uniform(0, 200), 1), round(rng.uniform(2, 50), 1), rng.choice([WEIGHT_OBSTACLE, 250.0, 0.0]), rng.choice(GROUPS)))
        else:
            r = (round(rng.uniform(0, 200), 1), round(rng.uniform(0, 200), 1), round(rng.uniform(1, 40), 1), round(rng.uniform(1, 40), 1), rng.choice([0.0, 0.0, 17.0, 45.0]))
            box = rect(*r)
            o = Obstacle(tuple(box), rng.choice([WEIGHT_OBSTACLE, 2000.0, 10000.0, 250.0]), rng.choice(GROUPS), named=rng.random() < 0.3,
                                inner=rng.random() < 0.2, keep=rng.choice([0.0, 0.0, 6.0]), soft=rng.random() < 0.4)
            RECTS[id(o)] = r
            KEEP.append(o)  # an id is unique only while its object lives
            obs.append(o)
    ways = [Way(tuple((round(rng.uniform(0, 200), 1), round(rng.uniform(0, 200), 1)) for _ in range(rng.randint(2, 4))), rng.choice([1.5, 4.0, 13.0]), soft=rng.random() < 0.5)
            for _ in range(rng.randint(0, 3))]
    return obs, ways

RECT, RECTS, KEEP = {}, {}, []
def ob_json(o):
    """[shape, ..., weight, group, flags, keep]: a disc "c" x y r or a rect "r" cx cy hw hh angle; flags n named, i inner, s soft."""
    shape = ["c", *o.circle] if o.circle is not None else ["r", *RECTS[id(o)]]
    flags = ("n" if o.named else "") + ("i" if o.inner else "") + ("s" if o.soft else "")
    return [*shape, o.weight, o.group, flags, o.keep]

def way_json(w):
    return [[list(p) for p in w.pts], w.half_width, w.soft]

def subject(rng):
    kind = rng.choice(["point", "point", "area", "line"])
    cx, cy = 100 + round(rng.uniform(-40, 40), 1), 100 + round(rng.uniform(-40, 40), 1)
    if kind == "line":
        pts = tuple((round(rng.uniform(0, 200), 1), round(rng.uniform(0, 200), 1)) for _ in range(rng.choice([1, 2, 2, 3, 4])))
        hint = (round(rng.uniform(0, 200), 1), round(rng.uniform(0, 200), 1)) if rng.random() < 0.6 else None
        return Subject("line", pts, half_width=rng.choice([1.5, 6.0]), hint=hint)
    ang = rng.choice([0.0, 30.0, 126.0])
    r = (cx, cy, round(rng.uniform(3, 50), 1), round(rng.uniform(2, 40), 1), ang)
    s = Subject(kind, tuple(rect(*r)), angle=ang if kind == "point" else rng.choice([0.0, 90.0]), civic=rng.random() < 0.3)
    SUBJ[id(s)] = r
    KEEP.append(s)
    return s
SUBJ = {}

def subject_json(s):
    shape = {"rect": list(SUBJ[id(s)])} if id(s) in SUBJ else {"poly": [list(p) for p in s.poly]}
    return {**shape, "kind": s.kind, "angle": F(s.angle), "half_width": s.half_width, "hint": None if s.hint is None else list(s.hint), "civic": s.civic}

def placement_json(p):
    if p is None:
        return None
    return {"x": F(p.x), "y": F(p.y), "angle": F(p.angle), "lines": list(p.lines), "block": P(p.block), "ring": p.ring, "rank": p.rank, "position": p.position,
            "cost": F(p.cost), "leader": None if p.leader is None else P(p.leader)}

def reanswer(path):
    """Feature 449 T184: the stored scenes of `held.json` answered again by the tree's placer from their own inputs - the scenes kept,
    each answer and refusal re-taken - so a fix to the Python is held by the same sixty scenes the Rust is (the revision that rolled them
    was not kept, and a re-roll loses coverage). Prints each case whose answer moved."""
    from dataclasses import replace
    from l7r.diagram.labels import Subject as S

    def num(v):
        return float(v[2:]) if isinstance(v, str) else v

    def obstacle(a):
        at = 4 if a[0] == "c" else 6
        weight, group, flags, keep = a[at], a[at + 1], a[at + 2], a[at + 3]
        base = circle_obstacle(*a[1:4], weight, group) if a[0] == "c" else Obstacle(tuple(rect(*a[1:6])), weight, group)
        return replace(base, named="n" in flags, inner="i" in flags, soft="s" in flags, keep=keep)

    held = json.load(open(path))
    moved = []
    for k, c in enumerate(held["cases"]):
        idx = ObstacleIndex([obstacle(a) for a in c["obstacles"]], [Way(tuple(tuple(p) for p in w[0]), w[1], soft=w[2]) for w in c["ways"]])
        lead = None if c["leader_obstacles"] is None else ObstacleIndex([obstacle(a) for a in c["leader_obstacles"]])
        sj = c["subject"]
        poly = tuple(rect(*sj["rect"])) if "rect" in sj else tuple(tuple(p) for p in sj["poly"])
        sub = S(sj["kind"], poly, angle=num(sj["angle"]), half_width=sj["half_width"], hint=None if sj["hint"] is None else tuple(sj["hint"]), civic=sj["civic"])
        if "rect" in sj:
            SUBJ[id(sub)] = sj["rect"]
        accept = (lambda p: p.rank != 0) if c["refuse_rank0"] else None
        frame = None if c["frame"] is None else tuple(c["frame"])
        try:
            p = place(c["text"], c["size"], sub, idx, frame, lines=c["lines"], char_w=c["char_w"], leader_index=lead, line_sizes=c["line_sizes"],
                      extended=c["extended"], strict=c["strict"], max_ring=c["max_ring"], accept=accept)
            answer, raises = placement_json(p), None
        except (ZeroDivisionError, ValueError, AssertionError) as e:
            answer, raises = None, f"{type(e).__name__}: {e}"
        if (answer, raises) != (c["answer"], c["raises"]):
            moved.append(k)
        c["answer"], c["raises"] = answer, raises
    json.dump(held, open(path, "w"), separators=(",", ":"))
    print("moved", len(moved), moved, file=sys.stderr)


if sys.argv[1] == "--reanswer":
    reanswer(sys.argv[2])
    sys.exit(0)

rng = random.Random(int(sys.argv[2]))
cases, queries = [], []
for k in range(int(sys.argv[3])):
    obs, ways = scene(rng)
    lead_obs, _ = scene(rng)
    idx = ObstacleIndex(obs, ways)
    lead = ObstacleIndex(lead_obs) if rng.random() < 0.4 else None
    sub = subject(rng)
    text = rng.choice(TEXTS)
    size = rng.choice([8.0, 12.0])
    frame = rng.choice([None, (0.0, 0.0, 200.0, 200.0), (60.0, 60.0, 140.0, 140.0), (95.0, 95.0, 105.0, 105.0)])
    lines = rng.choice([None, None, ["BATH", "xxxx"], []])
    line_sizes = [12.0, 8.0] if lines and rng.random() < 0.5 else None
    char_w = rng.choice([0.55, 0.74])
    strict = rng.random() < 0.35
    max_ring = rng.choice([None, None, 0, 1])
    extended = rng.random() < 0.85
    refuse = rng.random() < (0.5 if strict else 0.15)
    accept = (lambda p: p.rank != 0) if refuse else None
    try:
        p = place(text, size, sub, idx, frame, lines=lines, char_w=char_w, leader_index=lead, line_sizes=line_sizes, extended=extended,
                  strict=strict, max_ring=max_ring, accept=accept)
        raises = None
    except (ZeroDivisionError, ValueError, AssertionError) as e:
        p, raises = None, f"{type(e).__name__}: {e}" 
    cases.append({"obstacles": [ob_json(o) for o in obs], "ways": [way_json(w) for w in ways], "leader_obstacles": None if lead is None else [ob_json(o) for o in lead_obs],
                  "subject": subject_json(sub), "text": text, "size": size, "frame": frame, "lines": lines,
                  "line_sizes": line_sizes, "char_w": char_w, "strict": strict, "max_ring": max_ring,
                  "extended": extended, "refuse_rank0": refuse, "answer": placement_json(p), "raises": raises})
    for _ in range(4):
        br = (round(rng.uniform(0, 200), 1), round(rng.uniform(0, 200), 1), round(rng.uniform(2, 30), 1), round(rng.uniform(2, 8), 1), rng.choice([0.0, 30.0]))
        block = rect(*br)
        clear = rng.choice([2.0, 4.0, 6.0])
        own = list(sub.poly) if sub.kind != "line" and rng.random() < 0.7 else None
        if len(sub.poly) < 2:
            continue
        own_gap = rng.choice([None, 3.0, 9.0])
        text = rng.choice(TEXTS + ["shrine", "graveyard", "guard house", "the ministry"])
        civic = rng.random() < 0.3
        cost, hard = idx.score(block, clear, own, text, civic, own_gap)
        queries.append({"case": k, "block": list(br), "clear": clear, "own": own is not None, "own_gap": own_gap, "text": text,
                        "civic": civic, "score": [F(cost), hard], "blocked": idx.blocked(block, clear, NUDGE_REACH, own, text, civic),
                        "nearer": idx.nearer_than(block, 4.0, list(sub.poly)), "stands": stands_nearest(block, list(sub.poly), idx),
                        "clears": caption_clears_ways(block, ways)})
json.dump({"cases": cases, "queries": queries}, open(sys.argv[1], "w"), separators=(",", ":"))
print(sum(c['raises'] is not None for c in cases), len(cases), sum(c["answer"] is None for c in cases), len(queries), sum(q["blocked"] for q in queries), sum(q["nearer"] for q in queries),
      sum(q["score"][1] for q in queries), sum(c["answer"] is not None and c["answer"]["leader"] is not None for c in cases), file=sys.stderr)
