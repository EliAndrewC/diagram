"""The lane law: every rule a finished lane web must keep, each as ONE predicate (feature 287, M1).

A LIFT, NOT A RE-DERIVATION. Each predicate below is the body a finished-map test asserted - the lane network, the
cohort's lane rules, the crossings and the ways rows of feature 261's pool tests - moved into the engine. The placer that
owns a rule (`settle.settle_the_web`, the web's last pass, and the connector's `track.connector_through`) calls the same
predicate, and so does the placer's unit test on the violating case (`tests/hamletgen/ways/`); the finished-map tests
those unit tests made unnecessary are retired, each listed with its placer test in feature 287's research R8. That is
the skill's standing rule ("placement and its check must read the SAME source") made structural: there is one body per
rule, so the two cannot drift. The acceptance sweep (M9) runs `violations` over every finished map, so this module is the
registry of the rules.

Every predicate answers with what VIOLATES the rule - an empty list (or zero, or False) is a pass - so a test states the
found thing in its failure message and a placer knows where to cut.

WHERE THE PLACER AND ITS TEST READ A RULE DIFFERENTLY, the predicate is the TEST's reading, and the placers were moved onto
it (the ways phase of feature 287):

- the BEND (`bends_badly`): the tests sum the path between two 50 degree turns; `clearance._bends_badly`, which the web's
  passes asked, tested two turns separated by ONE segment - a lattice step of two short legs passed it and failed the test.
  Both read `clearance.kink_spans` (and the passes' copy went with them, feature 417 T26).
- the FORD (`off_ford_crossings`): the test allowed 45 ft from a recorded ford; the router gaps the brook at `FORD_HALF`
  (30 ft). The 45 ft was slack for `round_the_brooks` moving the course after the fords were set; the pool passes at the
  one constant, so the predicate reads `FORD_HALF` and the slack is gone.
- the END (`dangling_ends`): `tidy_lane_ends` asks `end_serves` against every other way; the pool test asks it against the
  other ways MINUS those at the lane's own far end (a lane counted as arriving because it was still within reach of the way
  it left). The stronger set is the predicate, and it serves both tests.
- the HOOK (`hooked_ends`): one test asked every lane, the other skipped the connector; the stricter reading is taken.
Research: plumbing and wrappers - NONE: each rule is claimed at the predicate that decides it
"""

from __future__ import annotations

from ..law_water import (  # noqa: F401 - re-exported: the law's callers reach the water rules and the lane helpers here
    DECK_NEAR_FT as DECK_NEAR_FT,
)
from ..law_water import (
    _bbox as _bbox,
)
from ..law_water import (
    _brooks as _brooks,
)
from ..law_water import (
    _crossings as _crossings,
)
from ..law_water import (
    _min_dist as _min_dist,
)
from ..law_water import (
    _ways as _ways,
)
from ..law_water import (
    boxes_meet as boxes_meet,
)
from ..law_water import (
    crossing_points as crossing_points,
)
from ..law_water import (
    deck_seats as deck_seats,
)
from ..law_water import (
    lane_pts as lane_pts,
)
from ..law_water import (
    oblique_at as oblique_at,
)
from ..law_water import (
    oblique_crossings as oblique_crossings,
)
from ..law_water import (
    off_ford_at as off_ford_at,
)
from ..law_water import (
    off_ford_crossings as off_ford_crossings,
)
from ..law_water import (
    off_square as off_square,
)
from ..law_water import (
    over_and_back as over_and_back,
)
from ..law_water import (
    plank_faults as plank_faults,
)
from ..law_water import (
    short_decks as short_decks,
)
from ..law_water import (
    unbridged_crossings as unbridged_crossings,
)
from ..law_water import (
    undeckable_crossings as undeckable_crossings,
)
from ..law_water import (
    water_courses as water_courses,
)
from .ends import *  # noqa: F403
from .ends import _walked_to as _walked_to
from .meet import *  # noqa: F403
from .meet import _tread_bearings as _tread_bearings
from .registry import *  # noqa: F403
from .shape import *  # noqa: F403
from .shape import _STEADING_PARTS as _STEADING_PARTS
