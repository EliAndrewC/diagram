"""Split from `parcels.py` at the 1,000-line bar (feature 417 T38, the GM 2026-10-21: a package of submodules whose `__init__`
re-exports every name). `patches` is the open-ground scan, `bounds` the lot lines and the region.

Research: parcels package - NONE: re-exports only
"""

from .bounds import LANE_LOT_LINE as LANE_LOT_LINE
from .bounds import LOT_BOUND_REACH as LOT_BOUND_REACH
from .bounds import STREAM_LOT_LINE as STREAM_LOT_LINE
from .bounds import Bound as Bound
from .bounds import _bound_margin as _bound_margin
from .bounds import _crop_refuses as _crop_refuses
from .bounds import _follows as _follows
from .bounds import _lines_at as _lines_at
from .bounds import _near_line as _near_line
from .bounds import bounds_near as bounds_near
from .bounds import follow_the_bounds as follow_the_bounds
from .bounds import lot_bounds as lot_bounds
from .bounds import lot_follows_its_bounds as lot_follows_its_bounds
from .bounds import open_ground_region as open_ground_region
from .bounds import ring_span as ring_span
from .patches import _CHAIN_OFF as _CHAIN_OFF
from .patches import _COMMONS_FLOOR_FT as _COMMONS_FLOOR_FT
from .patches import _COMMONS_REACH as _COMMONS_REACH
from .patches import CROP_MARGIN as CROP_MARGIN
from .patches import FIELD_BESIDE_FT as FIELD_BESIDE_FT
from .patches import LOW_BY_WATER_FT as LOW_BY_WATER_FT
from .patches import WET_SHARE_CAP as WET_SHARE_CAP
from .patches import WOODLAND_BBOX_FLOOR as WOODLAND_BBOX_FLOOR
from .patches import WaterZone as WaterZone
from .patches import _beyond_the_fields as _beyond_the_fields
from .patches import _parcel_outline as _parcel_outline
from .patches import _patch_keepouts as _patch_keepouts
from .patches import crop_edge_points as crop_edge_points
from .patches import crossed_through as crossed_through
from .patches import crossed_through_many as crossed_through_many
from .patches import field_height_near as field_height_near
from .patches import fit_square_parcel as fit_square_parcel
from .patches import house_floor as house_floor
from .patches import in_a_ruled_line as in_a_ruled_line
from .patches import low_by_the_water as low_by_the_water
from .patches import off_the_row as off_the_row
from .patches import open_ground_patches as open_ground_patches
from .patches import parcel_bbox_ok as parcel_bbox_ok
from .patches import parcel_inside_share as parcel_inside_share
from .patches import parcel_wet_share as parcel_wet_share
from .patches import reached_across as reached_across
from .patches import seat_off_the_row as seat_off_the_row
from .patches import woodland_tier as woodland_tier
