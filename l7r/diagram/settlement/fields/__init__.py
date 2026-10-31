"""The field subsystem of the Mode B settlement engine.

Split from the 1,511-line settlement/fields.py by feature 112 (constitution Principle X clause 13).
See CLAUDE.md in this directory for which submodule holds what.

`FieldsMixin` exists ONLY to preserve settlement/core.py's single import and its position in the
`class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin
methods reach each other through `self.` on the composed Settlement, so a cross-submodule call
needs no import and the partition can be re-cut later without touching core.py.

Research: package composition - NONE: the field mixins composed
"""

from . import grain  # noqa: F401 - registers the field's knobs (winter_crop, town_nearness, fan_middle) at import; the old comb module imported it
from .drawing import FieldDrawingMixin
from .landuse import LandUseMixin
from .paddy import PaddyMixin


class FieldsMixin(PaddyMixin, FieldDrawingMixin, LandUseMixin):
    """The composed field surface. No members of its own by design - see the module docstring."""
