"""STAGE 7: the ground between everything - open-ground scan, woodland, windbreak.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

from __future__ import annotations

# `from .x import Name` binds `x` itself as an attribute of this package, so a `from <pkg> import *`
# in a parent carries the SUBMODULE NAMES too. Feature 173 made that bite: `hamletgen/__init__.py`
# star-imports both `hinterland` and `homesteads`, and both packages have a `bamboo.py` and a
# `stages.py` - so the second star silently shadowed the first, which
# `tests/hamletgen/test_surface.py::test_no_public_name_clashes` caught. `__all__` says what this
# package actually exports; it is DERIVED here rather than listed, per clause 14.
import types as _types

from .bamboo import BAMBOO_LEGIBLE_FT as BAMBOO_LEGIBLE_FT
from .bamboo import BAMBOO_THICKET_FT as BAMBOO_THICKET_FT
from .bamboo import bamboo_blocked as bamboo_blocked
from .bamboo import bamboo_seats as bamboo_seats
from .belt import belt_polygon as belt_polygon
from .frame import content_box as content_box
from .frame import title_pocket as title_pocket
from .parcels import _COMMONS_FLOOR_FT as _COMMONS_FLOOR_FT
from .parcels import CROP_MARGIN as CROP_MARGIN
from .parcels import WOODLAND_BBOX_FLOOR as WOODLAND_BBOX_FLOOR
from .parcels import _clear_gap as _clear_gap
from .parcels import _near_line as _near_line
from .parcels import _parcel_outline as _parcel_outline
from .parcels import fit_square_parcel as fit_square_parcel
from .parcels import open_ground_patches as open_ground_patches
from .parcels import parcel_bbox_ok as parcel_bbox_ok
from .stages import stage_bamboo as stage_bamboo
from .stages import stage_hinterland as stage_hinterland
from .stages import stage_windbreak as stage_windbreak
from .stages import stage_woodland as stage_woodland

__all__ = [_n for _n, _v in sorted(globals().items()) if not _n.startswith("_") and not isinstance(_v, _types.ModuleType)]
