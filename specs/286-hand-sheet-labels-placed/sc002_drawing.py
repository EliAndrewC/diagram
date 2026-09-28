"""SC-002, measured on the drawing (feature 286): does any caption cover more of the sheet's ink at its placed seat than
at its hand seat?

Both seats are priced the same way: the caption's block against the placer's index of the DRAWING for its subject
(`classify`, no other caption in it - the other captions moved, so a seat taken by one now says nothing about the hand's
choice), plus its leader against the leader index of the drawing (`leader_blockers` with nothing placed). The hand seat
is the caption's `<text>` in the sheet as it stood before the feature (git `dddd838b5`) and the `data-leader` line that
began at it; the placed seat is `hand_sheet.seat` on the declared sheet. Texts are paired by their order in the
document, which the migration kept.

Run from the skill root:

    PYTHONPATH=. python3 ../../../specs/286-hand-sheet-labels-placed/sc002_drawing.py <before.svg> <declared.svg>
"""

import math
import sys

from l7r.diagram.labels import hand_sheet as sl
from l7r.diagram.labels import standard as st
from l7r.diagram.labels.geom import bbox, inside, rect


def band(seg):
    (ax, ay), (bx, by) = seg
    return rect((ax + bx) / 2, (ay + by) / 2, math.dist((ax, ay), (bx, by)) / 2, 0.5, math.degrees(math.atan2(by - ay, bx - ax)))


def price(shapes, view, skip, idx, sub, own, block, leader, text, size):
    head = shapes[idx[0]]
    light = sl._luma(head.element.get("fill") if head.element is not None else None) > sl.LIGHT
    index = sl.classify(shapes, view, skip, after=idx[0], group=head.group, kind=head.kind, subject=list(sub.poly), area=sub.kind == "area", dark_inside=not light)
    clear = st.CLEAR_EM * size
    cost = index.cost(block, clear, list(sub.poly), text, sub.civic)
    if sub.kind == "area" and not all(inside(q[0], q[1], sub.poly) for q in block):
        cost += st.WEIGHT_OBSTACLE
    if leader is not None and math.dist(*leader) > 1e-6:
        cost += sl.leader_blockers(shapes, skip, [], sub, own).cost(band(leader), clear, list(sub.poly), text, sub.civic)
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
    placed = {caps[0].at: (p, per) for caps, p, per in sl.seat(open(declared_path).read())}
    worse = []
    for idx in caps_of:
        head = shapes[idx[0]]
        own = sl.declared_parts(head, shapes, alone=per_group[head.group] == 1)
        p, _per = placed[head.at]
        text = " ".join(ln for i in idx for ln in shapes[i].lines)
        hands = [hand_texts[order[id(shapes[i])]] for i in idx]
        x0, y0, x1, y1 = bbox([q for h in hands for q in h.poly])
        hblock = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
        reach = head.size
        def gap(ld):
            return min(math.hypot(max(0.0, x0 - q[0], q[0] - x1), max(0.0, y0 - q[1], q[1] - y1)) for q in (ld.poly[0], ld.poly[-1]))

        hl = min((ld for ld in leaders if gap(ld) <= reach), key=gap, default=None)
        hleader = (hl.poly[0], hl.poly[-1]) if hl is not None else None
        # each seat is priced as what it is: a block whose middle lies inside the subject is its area caption, and pays
        # for spilling out of it; one outside is beside it
        hmid = ((x0 + x1) / 2, (y0 + y1) / 2)
        best_hand = min(price(shapes, view, skip, idx, sub, own, hblock, hleader, text, head.size) for sub in sl.subjects(own, head.size) if (sub.kind == "area") == inside(hmid[0], hmid[1], sub.poly))
        mine = min(price(shapes, view, skip, idx, sub, own, p.block, p.leader, text, head.size) for sub in sl.subjects(own, head.size) if (sub.kind == "area") == (p.position == "inside"))
        if mine > best_hand:
            worse.append((text, best_hand, mine, p.position))
            if "-v" in sys.argv:
                print("   hand", [round(v) for v in hblock[0] + hblock[2]], hleader, "| placed", [round(v) for v in bbox(p.block)], p.leader)
    print(f"{declared_path.split('/')[-1]}: {len(caps_of)} captions; covering more of the drawing than the hand seat: {worse}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])  # -v: each seat that covers more, and the hand's
