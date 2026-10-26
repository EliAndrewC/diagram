"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: lane sweep plumbing - NONE"""

from __future__ import annotations

from ..consts import (
    WEB_REACH_FT,
)
from .geom import (
    worked_ground_rings,  # noqa: F401 - re-exported: the gate test reads the sweep's own field from here
)

# A LINK that joins two halves of one settlement may wander further than a door path. Going round a
# paddy is legitimately indirect, and the thing being bought is the difference between a dozen houses
# reachable and a dozen houses not.


_SERVE_FT = WEB_REACH_FT  # ft: a way serves a house within this - `farmhouses_reach_a_way`'s own figure, so a dropped fragment never strands one
"""Research: a way serves a house - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 100 ft, as back lanes bring every farmhouse within 100 ft of one"""


from .tails import (  # noqa: E402, F401 - split out at the 1,000-line bar (feature 280); re-exported for the web and the tests
    _ALONG_DEG,
    _ALONG_FT,
    _DOUBLED_DEG,
    along_tail,
    cut_at_tail,
)
