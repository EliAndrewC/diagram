"""STAGES 1-2: the irrigation skeleton, the field the water shapes, and the brook that feeds it.

Split from the 1,175-line `hamletgen/water.py` by feature 230 (constitution Principle X clause 13 -
the cost being managed is context-window tokens), following the `hamletgen/ways/` exemplar. Bodies
are verbatim; `from .water import ...` and `hamletgen.stage_field` resolve exactly as before, through
the star imports below (clause 14 - a re-export `__init__` is derived, never a maintained roster).

| file | look here when |
|---|---|
| `skeleton.py` | the sluice, the fall or the canvas is wrong - STAGE 1, `stage_water_frame` |
| `brook.py` | the stream's own COURSE, its intake, or the weir glyph - feature 230's `brook_skirt`, `feed_brook`, `draw_intake` and the four helpers that keep the course off the crop and inside the frame |
| (STAGE 2, the field) | rebuilt in Rust by feature 444 T16: `hamletgen/field_stage.py`, `rust/phases/src/field/` |
| `waterward.py` | STAGE `stage_waterward`, the waterward reed fringe on a polder's flanks, and the crossings' caps (`polder_crossing_caps`); the polder itself is Rust's (feature 444 T16) |

Research: package index - NONE: re-exports only
"""

from .brook import *  # noqa: F403
from .skeleton import *  # noqa: F403

# THE UNDERSCORE NAMES THE TESTS CONSUME, carried explicitly: a star import skips a leading underscore, so
# these would vanish from `hamletgen.water` on the split and take their unit tests with them (the same aliased
# block `hamletgen/__init__.py` keeps, constitution X clause 14).
from .waterward import *  # noqa: F403
