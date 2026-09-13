"""STAGES 1-2: the irrigation skeleton, the field the water shapes, and the brook that feeds it.

Split from the 1,175-line `hamletgen/water.py` by feature 230 (constitution Principle X clause 13 -
the cost being managed is context-window tokens), following the `hamletgen/ways/` exemplar. Bodies
are verbatim; `from .water import ...` and `hamletgen.stage_field` resolve exactly as before, through
the star imports below (clause 14 - a re-export `__init__` is derived, never a maintained roster).

| file | look here when |
|---|---|
| `skeleton.py` | the sluice, the fall or the canvas is wrong - STAGE 1, `stage_water_frame` |
| `fit.py` | the field comes out the wrong SIZE, or a fan is refused as illegal - the acreage search (`fit_field`, `_fit_at_aspect`, `_predict_k`), the head sluice, and the two predicates that disqualify a fan (`tail_dangles`, `net_bends_acutely`) |
| `brook.py` | the stream's own COURSE, its intake, or the weir glyph - feature 230's `brook_skirt`, `feed_brook`, `draw_intake` and the four helpers that keep the course off the crop and inside the frame |
| `comb.py` | STAGE 2 itself: the fitted comb drawn, the head race taken off the brook's bank, the intake set on it |
| `polder.py` | anything about the reclaimed block - both polder archetypes, the perimeter dike and its gaps, the flanks, and the waterward reed fringe |
"""

from .brook import *  # noqa: F403
from .comb import *  # noqa: F403
from .fit import *  # noqa: F403

# THE UNDERSCORE NAMES THE TESTS CONSUME, carried explicitly: a star import skips a leading underscore, so
# these would vanish from `hamletgen.water` on the split and take their unit tests with them (the same aliased
# block `hamletgen/__init__.py` keeps, constitution X clause 14).
from .fit import _fit_at_aspect as _fit_at_aspect  # noqa: E402
from .fit import _predict_k as _predict_k  # noqa: E402
from .polder import *  # noqa: F403
from .skeleton import *  # noqa: F403
