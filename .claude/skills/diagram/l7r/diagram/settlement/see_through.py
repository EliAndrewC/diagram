"""THE MARKS DRAWN SEE-THROUGH, EACH WITH ITS REASON (feature 294 B5, the review's "translucency and draw order" class).

The reviews caught a mark drawn faintly where it should read solid four times - the title placard at 0.94 and a field grave's
mound at 0.9 (features 145 and 150), each ghosting the ground through it. A mark drawn below `SOLID` opacity is a choice,
and here it is declared: its class, the faintest it is drawn at, and why it is see-through - a map drawing convention every
one (research/contents.json#map-conventions: a mark drawn so the map reads). `tools/see_through.translucent_marks` reads a page's marks and the
gate holds every shipped map to this table (`tests/gate/test_review_rules_294.py`); a class drawn see-through that is not
here, or fainter than its floor, fails it."""

from __future__ import annotations

#: at or above this effective opacity a mark is solid
SOLID = 0.95

#: class key -> (the faintest effective opacity its marks are drawn at, why the mark is see-through)
SEE_THROUGH: dict[str, tuple[float, str]] = {
    "millet": (0.8, "the crop's furrow rows are a texture laid over the plot's fill, which shows between them"),
    "soy": (0.8, "the crop's furrow rows are a texture laid over the plot's fill"),
    "barley": (0.8, "the crop's furrow rows are a texture laid over the plot's fill"),
    "buckwheat": (0.8, "the crop's furrow rows are a texture laid over the plot's fill"),
    "field pond": (0.8, "the plot rows that run up to the pond are a texture over its edge"),
    "farm holding": (0.8, "a holding's bounding line is a hint over the plots it encloses, not a fence"),
    "irrigation ditch": (0.85, "the late water block is laid over the paddy, which tints its bed at the edges"),
    "drainage ditch": (0.85, "the late water block is laid over the paddy, which tints its bed at the edges"),
    "pond canal": (0.85, "the late water block is laid over the dike-pond's banks"),
    "stream": (0.55, "the water's sheen and glints lie over its bed, which shows through them"),
    "pond": (0.55, "the water's sheen and glints lie over its bed, which shows through them"),
    "bund beans": (0.85, "the beans along a bund are a scatter over the bund's own line"),
    "farmhouse": (0.85, "the threshold step's shade over the house's front"),
    "retirement house": (0.85, "the threshold step's shade over the house's front"),
    "well": (0.55, "the wellhead's shelter roof, drawn so the curb and the water under it read"),
    "byre": (0.6, "the roof ridge line over the stall's roof"),
    "footbridge": (0.55, "the plank seams over the deck"),
    "village lane": (0.4, "the worn-earth shoulder either side of the packed tread, which is drawn at 0.9 over it"),
    "mulberry dike": (0.35, "the mulberry canopy's mottled patches over the dike's earth"),
    "perimeter dike": (0.4, "the dike crest's mottling and its worn path over the bank"),
}
