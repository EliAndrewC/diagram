"""SC-002's one re-runnable probe (feature 286, measurements.json `sc_002`): Hayakawa's Ebisu altar note is placed at
its hand seat with the hand's own leader, and what that leader crosses is what its after-cost is.

Run from the skill root, on the declared sheet:

    PYTHONPATH=. python3 ../../../specs/286-hand-sheet-labels-placed/ebisu_probe.py pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.svg

It prints, for each subject the note is tried against, the placer's seat, cost and leader, and the cost of the hand
leader's band - the line the sheet drew at x=776 from y=184 to 218 before feature 286 - in the placement index and in
the leader index. Observed 2026-09-28: the point seat's leader is the hand leader exactly, and its 1,000 is the
leader index's price of that same line.
"""

import sys

from l7r.diagram.labels import hand_sheet as sl
from l7r.diagram.labels import standard as st
from l7r.diagram.labels.geom import rect

real = sl.place


def spy(text, size, sub, index, view, **kw):
    p = real(text, size, sub, index, view, **kw)
    if text.startswith("(was"):
        band = rect(776, 201, 17, 0.5, 90.0)
        clear = st.CLEAR_EM * size
        print(sub.kind, "placer", p.position, p.ring, p.cost, p.leader, "| hand leader: in index", index.cost(band, clear, list(sub.poly), text, sub.civic), "in leader index", kw["leader_index"].cost(band, clear, list(sub.poly), text, sub.civic))
    return p


sl.place = spy
sl.seat(open(sys.argv[1]).read())
