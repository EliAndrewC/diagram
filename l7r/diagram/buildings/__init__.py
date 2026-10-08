"""Mode A building TYPES, declared once (feature 254, GM 2026-09-19).

A building type - the magistracy, the country shrine - is one object in `types.json`: its pool tier,
its program's required items with the label each is found by and the size band each is held to, the
per-type checks that apply, and whether its SVG is hand-drawn source. Everything that used to know
the magistracy by name derives from here: the pool classifier, the pool index, the ignore rule for
hand-drawn source, the audit's program and band checks, the gate's sweep. Adding a type is adding an
object here and a folder under `pool/`; the census test in `tests/test_building_types.py` refuses a
type name anywhere else in the engine.
"""

from .types import BuildingType, RequiredItem, by_tier, hand_drawn_tiers, load_types, tiers

__all__ = ["BuildingType", "RequiredItem", "by_tier", "hand_drawn_tiers", "load_types", "tiers"]
