"""Variant of sc002_drawing.py: each seat priced in its own era's full context - the drawing PLUS every other caption
(hand blocks and hand leaders for the hand seat; placed blocks and leaders for the placed seat)."""
import math, sys
from l7r.diagram.labels import hand_sheet as sl
from l7r.diagram.labels import standard as st
from l7r.diagram.labels import Obstacle, ObstacleIndex
from l7r.diagram.labels.geom import bbox, inside, rect

def band(seg):
    (ax, ay), (bx, by) = seg
    return rect((ax + bx) / 2, (ay + by) / 2, math.dist((ax, ay), (bx, by)) / 2, 0.5, math.degrees(math.atan2(by - ay, bx - ax)))

def price(shapes, view, skip, idx, sub, own, block, leader, text, size, others):
    head = shapes[idx[0]]
    light = sl._luma(head.element.get("fill") if head.element is not None else None) > sl.LIGHT
    base = sl.classify(shapes, view, skip, after=idx[0], group=head.group, kind=head.kind, subject=list(sub.poly), area=sub.kind == "area", dark_inside=not light, named=frozenset(shapes[i[0]].kind for i in sl.captions_of(shapes)))
    index = ObstacleIndex(list(base.obstacles), list(base.ways))
    for ob, ol in others:
        index.add(Obstacle(tuple(ob), sl.WEIGHT_TEXT))
        if ol is not None and math.dist(*ol) > 1e-6:
            index.add(Obstacle(tuple(sl._band(ol[0], ol[1], 1.0)), sl.WEIGHT_TEXT))
    clear = st.CLEAR_EM * size
    cost = index.cost(block, clear, list(sub.poly), text, sub.civic)
    if sub.kind == "area" and not all(inside(q[0], q[1], sub.poly) for q in block):
        cost += st.WEIGHT_OBSTACLE
    if leader is not None and math.dist(*leader) > 1e-6:
        li = sl.leader_blockers(shapes, skip, [], sub, own)
        for ob, _ in others:
            li.add(Obstacle(tuple(ob), sl.WEIGHT_TEXT))
        cost += li.cost(band(leader), clear, list(sub.poly), text, sub.civic)
    return cost

def main(before_path, declared_path):
    before = sl.read_sheet(open(before_path).read())[0]
    shapes, view = sl.read_sheet(open(declared_path).read())
    hand_texts = [s for s in before if s.tag == "text"]
    leaders = [s for s in before if s.leader]
    order = {id(s): k for k, s in enumerate(s for s in shapes if s.tag == "text")}
    caps_of = sl.captions_of(shapes)
    skip = {i for idx in caps_of for i in idx}
    per_group = {}
    for idx in caps_of:
        per_group[shapes[idx[0]].group] = per_group.get(shapes[idx[0]].group, 0) + 1
    placed = {caps[0].at: p for caps, p, per in sl.seat(open(declared_path).read())}
    hand = {}
    for idx in caps_of:
        head = shapes[idx[0]]
        hands = [hand_texts[order[id(shapes[i])]] for i in idx]
        x0, y0, x1, y1 = bbox([q for h in hands for q in h.poly])
        def gap(ld):
            return min(math.hypot(max(0.0, x0 - q[0], q[0] - x1), max(0.0, y0 - q[1], q[1] - y1)) for q in (ld.poly[0], ld.poly[-1]))
        hl = min((ld for ld in leaders if gap(ld) <= head.size), key=gap, default=None)
        hand[idx[0]] = (((x0, y0), (x1, y0), (x1, y1), (x0, y1)), (hl.poly[0], hl.poly[-1]) if hl is not None else None)
    worse = []; nb = na = 0
    for idx in caps_of:
        head = shapes[idx[0]]
        own = sl.declared_parts(head, shapes, alone=per_group[head.group] == 1)
        p = placed[head.at]
        text = " ".join(ln for i in idx for ln in shapes[i].lines)
        hblock, hleader = hand[idx[0]]
        hothers = [v for k, v in hand.items() if k != idx[0]]
        pothers = [(placed[shapes[k[0]].at].block, placed[shapes[k[0]].at].leader) for k in caps_of if k[0] != idx[0]]
        hmid = ((hblock[0][0] + hblock[2][0]) / 2, (hblock[0][1] + hblock[2][1]) / 2)
        hs = [price(shapes, view, skip, idx, sub, own, hblock, hleader, text, head.size, hothers) for sub in sl.subjects(own) if (sub.kind == "area") == inside(hmid[0], hmid[1], sub.poly)]
        ps = [price(shapes, view, skip, idx, sub, own, p.block, p.leader, text, head.size, pothers) for sub in sl.subjects(own) if (sub.kind == "area") == (p.position == "inside")]
        bh = min(hs) if hs else float("nan"); mp = min(ps) if ps else float("nan")
        nb += bh > 0; na += mp > 0
        if mp > bh:
            worse.append((text, bh, mp, p.position))
    print(f"{declared_path.split('/')[-1]}: {len(caps_of)} captions; hand seats covering ink {nb}, placed {na}; placed covers more in context: {worse}")

main(sys.argv[1], sys.argv[2])
