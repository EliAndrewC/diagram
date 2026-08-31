"""pack_audit.py - packing / whitespace report for a Mode A compound plan.

Read-only. Parses a hand-authored compound SVG and reports the numbers that make
"is there too much empty space?" objective, WITHOUT the misleading ones:

  - building-COVERAGE % of the walled interior (the historical anchor; a jin'ya
    runs ~37-42% built, the rest intentional courtyard - see buildings.md
    grounding "Packing: a jin'ya is mostly open..."). Coverage, NOT "total empty
    %", is the realism signal: a courtyard compound is SUPPOSED to be mostly open.
  - the TOP-N genuinely-vacant rectangles (+ orientation + location): the real
    "a whole region sits empty" signal. Reporting only the single largest hid a
    big secondary void behind the legitimate forecourt (GM caught this, 2026-07),
    so the report lists several - each judged forecourt-feature vs slack.
  - PER-REGION density: the interior tiled into a grid, so a locally-sparse
    quadrant is visible even when the GLOBAL coverage is comfortably in-band
    (a compound can be 37% overall while one quarter is ~68% empty).
  - ALIGNED BUILDING GAPS: pairs of buildings stacked on a shared edge with empty
    ground between them. A ~6 ft fire-gap around a plaster KURA is correct; a
    12-16 ft gap between ordinary wooden service buildings is loose slack.
  - STRUCTURES ON WALLS: a footprint drawn across the INK of a compound wall or a
    court divider. A wall is a built object with real thickness, so a structure
    either abuts it or stands clear - it can never occupy the same ground.

"Empty %" and "largest empty CONNECTED region" are deliberately NOT the headline
numbers: the open ground is one connected blob (courtyard network), so a
connected-component count is degenerate, and a high open % is expected, not a
defect. Coverage + top-N vacant RECTANGLES + per-region density + aligned gaps
are the actionable set.

Usage:  python3 -m l7r.diagram.tools.pack_audit pool/<subject>.svg [more.svg ...]
"""

from __future__ import annotations

from .checks import DARK_MIN_OVERLAP_PX as DARK_MIN_OVERLAP_PX
from .checks import DOOR_FLUSH_TOL_PX as DOOR_FLUSH_TOL_PX
from .checks import DOOR_NEAR_PX as DOOR_NEAR_PX
from .checks import GROUP_LABEL_GLYPHS as GROUP_LABEL_GLYPHS
from .checks import GROUP_LABEL_MAX_FT as GROUP_LABEL_MAX_FT
from .checks import LABEL_DARK_LUMA as LABEL_DARK_LUMA
from .checks import LABEL_OVERLAP_MIN_PX as LABEL_OVERLAP_MIN_PX
from .checks import NOTICE_BOARD_MAX_FT as NOTICE_BOARD_MAX_FT
from .checks import NUDGE_MAX_PX as NUDGE_MAX_PX
from .checks import NUDGE_STEP_PX as NUDGE_STEP_PX
from .checks import OCCLUSION_MIN_PX as OCCLUSION_MIN_PX
from .checks import OPENING_MAX_PX as OPENING_MAX_PX
from .checks import PASSAGE_CLEAR_MIN_PX as PASSAGE_CLEAR_MIN_PX
from .checks import PASSAGE_DEPTH_PX as PASSAGE_DEPTH_PX
from .checks import TUB_BLDG_MIN_PX as TUB_BLDG_MIN_PX
from .checks import TUB_MAX_GAP_FT as TUB_MAX_GAP_FT
from .checks import TUB_WELL_MIN_PX as TUB_WELL_MIN_PX
from .checks import WALL_OVERLAP_MIN_PX as WALL_OVERLAP_MIN_PX
from .checks import DarkOnDark as DarkOnDark
from .checks import FloatingDoor as FloatingDoor
from .checks import Gap as Gap
from .checks import LabelClash as LabelClash
from .checks import MisplacedBoard as MisplacedBoard
from .checks import Occluded as Occluded
from .checks import OrphanLabel as OrphanLabel
from .checks import PassageBlocker as PassageBlocker
from .checks import StructureOnWall as StructureOnWall
from .checks import TubAdrift as TubAdrift
from .checks import TubInBuilding as TubInBuilding
from .checks import TubOnWell as TubOnWell
from .checks import WallOpening as WallOpening
from .checks import _gate_openings as _gate_openings
from .checks import _overlap_px as _overlap_px
from .checks import _point_rect_dist as _point_rect_dist
from .checks import aligned_gaps as aligned_gaps
from .checks import dark_on_dark_labels as dark_on_dark_labels
from .checks import fire_water_adrift as fire_water_adrift
from .checks import floating_doors as floating_doors
from .checks import gap_tag as gap_tag
from .checks import notice_board_adrift as notice_board_adrift
from .checks import occluded_foreground as occluded_foreground
from .checks import orphan_group_labels as orphan_group_labels
from .checks import overlapping_labels as overlapping_labels
from .checks import passage_blockers as passage_blockers
from .checks import structures_on_walls as structures_on_walls
from .checks import tubs_in_buildings as tubs_in_buildings
from .checks import tubs_on_wells as tubs_on_wells
from .checks import wall_openings as wall_openings
from .grids import FTPX as FTPX
from .grids import Grid as Grid
from .grids import RegionTile as RegionTile
from .grids import VacantRect as VacantRect
from .grids import _perimeter_band as _perimeter_band
from .grids import coverage as coverage
from .grids import perimeter_hugging_pct as perimeter_hugging_pct
from .grids import region_density as region_density
from .grids import top_vacant_rects as top_vacant_rects
from .parse import BUILDING_FILLS as BUILDING_FILLS
from .parse import BUILDING_PATTERNS as BUILDING_PATTERNS
from .parse import CAPS_RATIO as CAPS_RATIO
from .parse import CHAR_W_BOLD as CHAR_W_BOLD
from .parse import CHAR_W_BOLD_MIXED as CHAR_W_BOLD_MIXED
from .parse import CHAR_W_FRAC as CHAR_W_FRAC
from .parse import DARK_FILLS as DARK_FILLS
from .parse import DIVIDER_STROKE as DIVIDER_STROKE
from .parse import DOOR_MAX_AREA_PX as DOOR_MAX_AREA_PX
from .parse import FIRE_WATER_FILL as FIRE_WATER_FILL
from .parse import FURNITURE_MAX_AREA_PX as FURNITURE_MAX_AREA_PX
from .parse import INTERIOR_FILL as INTERIOR_FILL
from .parse import KURA_FILLS as KURA_FILLS
from .parse import MIN_BLDG_AREA_PX as MIN_BLDG_AREA_PX
from .parse import MIN_DARK_AREA_PX as MIN_DARK_AREA_PX
from .parse import OPEN_PATTERNS as OPEN_PATTERNS
from .parse import STRUCTURE_FILLS as STRUCTURE_FILLS
from .parse import UTILITY_FILLS as UTILITY_FILLS
from .parse import WALL_KIND as WALL_KIND
from .parse import WALL_STROKE as WALL_STROKE
from .parse import WELL_FILL as WELL_FILL
from .parse import Label as Label
from .parse import ParsedPlan as ParsedPlan
from .parse import Rect as Rect
from .parse import _bold_char_w as _bold_char_w
from .parse import _luma as _luma
from .parse import parse_svg as parse_svg
from .report import format_report as format_report
from .report import main as main
