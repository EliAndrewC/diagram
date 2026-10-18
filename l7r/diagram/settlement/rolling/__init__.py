"""The rolling / homestead-solver subsystem of the Mode B settlement engine.

Split from the 1,197-line settlement/rolling.py by feature 118 (constitution Principle X clause 13).
See CLAUDE.md in this directory for which submodule holds what.

Unlike structures/ and civic_grounds/, this package was NEVER a residue bucket. It is one cohesive
CHAIN - generate candidate seats, shape a homestead bundle, test whether it fits, find it a spot, draw
it - and the core submodules are its links, in that order (its head, the feature-005 roller, was retired by
feature 388). The test of
the partition is that real tasks stay inside one link: adding a settlement form reads seeds.py alone,
the standing rotated-footprint debt lands in fit.py alone, changing what the flush draws is
farmsteads.py alone.

`RollingMixin` exists ONLY to preserve settlement/core.py's single import and its position in the
`class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin
methods reach each other through `self.` on the composed Settlement, so a cross-submodule call needs
no import and the partition can be re-cut later without touching core.py.

place.py is the HUB (fit and farmsteads both reach placement directly),
and bundle.py is a pure LEAF that calls nothing - which is why the researched dimension numbers live
there, where a change cannot ripple sideways. The full measured graph is in CLAUDE.md; it was
computed from the AST rather than reasoned about, because the chain diagram above makes fit.py look
like the hub and it is not.

The base order below is source order and is behaviorally irrelevant - no name is defined twice, which
is what the composed-surface guard's second assertion exists to keep true.

Research: package composition - NONE
"""

from .bundle import BundleGeomMixin
from .farmsteads import FarmsteadFlushMixin
from .fit import BundleFitMixin
from .place import PlacerMixin
from .seeds import SeedFormsMixin


class RollingMixin(
    SeedFormsMixin,
    BundleGeomMixin,
    BundleFitMixin,
    PlacerMixin,
    FarmsteadFlushMixin,
):
    """The composed rolling surface. No members of its own by design - see the module docstring."""

    # The compact-bundle flag the bundle, the placer and the byres read through `getattr(..., False)`; a generator sets it
    # before its homesteads (`hamletgen/water/skeleton.py`). An annotation only, not a member: a map that never sets it
    # reads False as before (feature 388 - the retired roller was the one assignment pyrefly had seen it by).
    _nucleated: bool
