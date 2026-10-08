"""The overlap taxonomy and matrix - WHICH FEATURES MAY LIE ON WHICH, and why (feature 166).

This package was `check_village/common_01_geometry.py` and `common_02_overlap_policy.py` until the check
battery was retired. It moved rather than died because it is not a check: it is the ENGINE's own
classification of the map's features, the one place that records that a garden may lie inside its own
homestead's yard and may not lie inside a neighbor's, that a channel may reach the field it feeds, that a
trade work's private well stands inside its own court.

WHY IT LIVED IN THE WRONG PLACE, WHICH IS THE POINT OF THE FEATURE THAT MOVED IT. A placer needs this
table to decide where a thing may go; the battery needed it to decide, afterwards, whether the thing had
gone somewhere allowed. Only the first of those is load-bearing, and keeping the table inside the battery
meant the placer's own doctrine was stored in the thing that audited the placer.

`matrix_policy(ka, kb)` answers "may a `ka` and a `kb` overlap, and on whose authority" for any pair of
manifest keys, from ONE classification (`OVERLAP_CLASS` plus the permission tables) rather than from a
per-pair rule. That is why a new footprint feature needs a row here and nothing else: membership alone
gates it off every hazard the matrix knows about.
"""

from .matrix import *  # noqa: F403
from .taxonomy import *  # noqa: F403

# UNDERSCORE NAMES DO NOT TRAVEL BY STAR IMPORT, and two of the rosters are consumed by name outside
# this package: `tests/settlement/test_homestead_parts.py` censuses `_OVERLAP_STRUCTS` to prove every
# roofed feature is a canopy keep-out, and `_OVERLAP_EXEMPT` carries the reasons the exceptions exist.
# They keep their leading underscore because they are a roster to READ, never a surface to extend by
# import - the way to add to them is to edit the table with its reason beside it.
from .taxonomy import (
    _LABEL_GROUP as _LABEL_GROUP,
)
from .taxonomy import (
    _OVERLAP_EXEMPT as _OVERLAP_EXEMPT,
)
from .taxonomy import (
    _OVERLAP_LINEAR as _OVERLAP_LINEAR,
)
from .taxonomy import (
    _OVERLAP_STRUCTS as _OVERLAP_STRUCTS,
)
from .taxonomy import (
    _OVERLAP_TARGETS as _OVERLAP_TARGETS,
)
