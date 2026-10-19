"""The structures subsystem of the Mode B settlement engine.

Split from the 1,459-line settlement/structures.py by feature 114 (constitution Principle X clause
13). See CLAUDE.md in this directory for which submodule holds what.

Unlike settlement/fields/ and settlement/city/, this package was never ONE subsystem: structures.py
was feature 025's residue bucket, holding everything that was neither field, nor way, nor homestead,
nor funerary ground. So the submodules are grouped by what a session comes here to CHANGE, and
they are deliberately uneven in size - a partition tuned for equal files would have to cut a cluster
that no task cuts.

`StructuresMixin` exists ONLY to preserve settlement/core.py's single import and its position in the
`class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin
methods reach each other through `self.` on the composed Settlement, so a cross-submodule call needs
no import and the partition can be re-cut later without touching core.py. (Feature 392 retired the compounds, the
packers, the servant ranges and the city fixtures, which only the frozen legacy maps called.)

The base order below is source order and is behaviorally irrelevant - no name is defined twice, which
is what the composed-surface guard's second assertion exists to keep true.

Research: plumbing - NONE: the composed mixin surface
"""

from .captions import CaptionProbesMixin
from .fixtures import PublicFixturesMixin
from .ground import GroundMixin


class StructuresMixin(
    GroundMixin,
    CaptionProbesMixin,
    PublicFixturesMixin,
):
    """The composed structures surface. No members of its own by design - see the module docstring."""
