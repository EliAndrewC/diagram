"""How many sides a farmstead's grove takes, and which (feature 291; research/homesteads.html, "Was the homestead grove
there before 1868, and what size and shape was it?").

The record reports three forms, each of one region: the grove on the windward pair of faces (the Sendai plain's north and
west, planted so under the first Sendai lord and kept for centuries), on three faces with the front left open (the Tonami
plain's open east front) and all the way round (the Izumo plain's ring before Meiji, tied to its flood banks). No source
counts farmsteads by shape, so the side count is a knob rolled once per settlement (`hamletgen/consts.py` `GROVE_SIDES`).

A farmstead is laid out in ONE canonical frame - the cold wind from the northwest, the grove's deep bands on the north
and west, the threshing yard on the south front, the garden on the east - and carried to the map's wind by a symmetry of
the square (`bundle_turn`). So the faces are named in the canonical frame and turned, and every rule reads them turned.
"""

from __future__ import annotations

# A face is the unit vector pointing out of the house through it (y grows southward on the map).
N, E, S, W = (0, -1), (1, 0), (0, 1), (-1, 0)
Face = tuple[int, int]
Turn = tuple[int, int, int, int]  # (a, b, c, d): a face (x, y) goes to (a*x + b*y, c*x + d*y)

# THE ROLL TABLES. Rolled once per settlement - grove shape is reported as regional custom - and the same at every farm.
# No source counts farmsteads by shape, so the weights are a GUESS, the GM's ruling of 2026-09-29 (*"Your suggestions
# sound great, so yes, please go with all of that. Both the percentage split and the flood ground adjustment."*):
# two sides 50%, three 30%, four 20% - two the form reported in the most regions and the only one with a general
# statement and an early-Edo date, three Tonami's, four Izumo's.
GROVE_SIDES = (2, 2, 2, 2, 2, 3, 3, 3, 4, 4)
# ...and where the farms stand on flood-prone ground the ring rises to 40%, the other two keeping their 5 : 3
# (37.5 / 22.5 / 40): the Izumo ring's own stated cause was flood (the same ruling; the scaling a GUESS).
GROVE_SIDES_FLOOD = (2,) * 15 + (3,) * 9 + (4,) * 16
# ...and for a map whose declared wind is a single cardinal, which flank completes the windward pair (`windward_pair`):
# rolled per settlement, even odds - nothing says which.
GROVE_FLANKS = (-1, 1)

# A THIN BAND IS ONE TREE DEEP: two mean crown radii (`CANOPY_R_FT` = 8.5 ft, research/vegetation.html "Forest density and
# crown size"). The sides of a grove away from the wind are a band of lesser trees (Tonami's east side: flowering trees,
# persimmon, fig; its west-to-north side hackberry and alder), far thinner than the windward stand (1.57 house depths -
# 44 ft at the pool's median house); how deep it was is on no page read, so one tree is a GUESS.
THIN_BAND_FT = 17.0

_LETTER = {"N": N, "E": E, "S": S, "W": W}
_CLOCKWISE = (N, E, S, W)

# THE SYMMETRY THAT CARRIES THE CANONICAL FARMSTEAD TO A DIAGONAL WIND. Each takes {N, W} to the windward pair and puts
# the yard (canonical S) on the lee face nearest the south, where it keeps the most sun:
#   NW - as laid out: yard south.
#   NE - mirrored east-west: yard south, garden west.
#   SW - a quarter turn counterclockwise: yard east - the Tonami plain's own arrangement, whose tall trees stood from the
#        south round to the west and whose east side was the entrance and the garden (research/homesteads.html, "Which
#        side of the house did the windbreak stand on").
#   SE - the mirror across the anti-diagonal: yard west, the afternoon sun (a half turn would put it north, in the house's
#        shadow all day).
_TURNS: dict[str, Turn] = {
    "NW": (1, 0, 0, 1),
    "NE": (-1, 0, 0, 1),
    "SW": (0, 1, -1, 0),
    "SE": (0, -1, -1, 0),
}


def turn_face(t: Turn, f: Face) -> Face:
    """A canonical face carried by the turn `t`."""
    a, b, c, d = t
    return (a * f[0] + b * f[1], c * f[0] + d * f[1])


def turns_axes(t: Turn) -> bool:
    """Whether `t` exchanges the axes (a quarter turn or the anti-diagonal mirror) - a rect's width and height swap."""
    return t[0] == 0


def windward_pair(windward: str, flank: int) -> str:
    """The diagonal key whose two faces are the windward pair. A diagonal wind is its own pair; a cardinal wind's pair is
    its face and one flank - `flank` -1 the face a quarter turn counterclockwise of it (W for a north wind), +1 the one
    clockwise (E) - because two sides is the least a farmstead grove takes (the GM, 2026-09-29: "It seems like two sides
    is the minimum")."""
    key = windward.upper().strip()
    if key in _TURNS:
        return key
    if key not in _LETTER:
        return "NW"
    i = _CLOCKWISE.index(_LETTER[key])
    other = _CLOCKWISE[(i + (1 if flank > 0 else -1)) % 4]
    pair = {_LETTER[key], other}
    for diag in _TURNS:
        if {_LETTER[diag[0]], _LETTER[diag[1]]} == pair:
            return diag
    raise AssertionError(pair)  # pragma: no cover - every adjacent pair of faces is one of the four diagonals


def bundle_turn(windward: str, flank: int) -> Turn:
    """The symmetry carrying the canonical farmstead (wind from the NW) to this map's wind."""
    return _TURNS[windward_pair(windward, flank)]


def grove_faces(windward: str, sides: int, flank: int) -> tuple[tuple[Face, ...], tuple[Face, ...], Face]:
    """(deep faces, thin faces, the front) of a farmstead grove of `sides` sides under this wind.

    Two sides is the windward pair, both deep. Three adds the one face left that is not the FRONT - the lee face where the
    yard and the way in are, which a three-sided grove leaves open (Tonami's east front). Four adds the front too and
    closes the ring (Izumo's). The added faces are thin bands of lesser trees; the windward ones stay the deep stand
    (Tonami's tall cedar on its windward faces, lesser trees elsewhere; for the ring a GUESS)."""
    if sides not in (2, 3, 4):
        raise ValueError(f"a farmstead grove takes 2, 3 or 4 sides, not {sides!r}")
    t = bundle_turn(windward, flank)
    deep = (turn_face(t, N), turn_face(t, W))
    thin = (turn_face(t, E),) if sides >= 3 else ()
    if sides == 4:
        thin += (turn_face(t, S),)
    return deep, thin, turn_face(t, S)
