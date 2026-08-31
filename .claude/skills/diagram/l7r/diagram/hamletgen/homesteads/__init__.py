"""STAGE 5-6: the houses on their lane frontage, their appurtenances, and the wells.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

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
