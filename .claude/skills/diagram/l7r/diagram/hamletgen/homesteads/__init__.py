"""STAGE 5-6: the houses on their lane frontage, their appurtenances, and the wells.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

# `from .x import Name` binds `x` itself as an attribute of this package, so a `from <pkg> import *`
# in a parent carries the SUBMODULE NAMES too. Feature 173 made that bite: `hamletgen/__init__.py`
# star-imports both `hinterland` and `homesteads`, and both packages have a `bamboo.py` and a
# `stages.py` - so the second star silently shadowed the first, which
# `tests/hamletgen/test_surface.py::test_no_public_name_clashes` caught. `__all__` says what this
# package actually exports; it is DERIVED here rather than listed, per clause 14.
import types as _types

from .bamboo import HOUSEHOLD_BAMBOO_FT as HOUSEHOLD_BAMBOO_FT
from .bamboo import HOUSEHOLD_BAMBOO_PREVALENCE as HOUSEHOLD_BAMBOO_PREVALENCE
from .bamboo import _strip_blocked as _strip_blocked
from .bamboo import household_bamboo as household_bamboo
from .fixtures import FIXTURE_BANDS as FIXTURE_BANDS
from .fixtures import PRIVY_SUN_MAX_FT as PRIVY_SUN_MAX_FT
from .fixtures import PRIVY_SUN_MIN_FT as PRIVY_SUN_MIN_FT
from .fixtures import PRIVY_SUNNY_SHARE as PRIVY_SUNNY_SHARE
from .fixtures import _roll as _roll
from .fixtures import _trunk_blocked as _trunk_blocked
from .fixtures import farmstead_fixtures as farmstead_fixtures
from .fixtures import nearer_own_house as nearer_own_house
from .seats import _seat_allowed as _seat_allowed
from .seats import cluster_aspect as cluster_aspect
from .seats import front_row as front_row
from .seats import lane_frontage as lane_frontage
from .stages import FORM_BOUND as FORM_BOUND
from .stages import stage_appurtenances as stage_appurtenances
from .stages import stage_homesteads as stage_homesteads
from .wells import place_wells as place_wells
from .wells import well_target as well_target

__all__ = [_n for _n, _v in sorted(globals().items()) if not _n.startswith("_") and not isinstance(_v, _types.ModuleType)]
