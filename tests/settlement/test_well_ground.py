"""Where a wellhead may be sunk (feature 166).

Carries `wells_off_the_wet_toe`, which the retired battery re-measured on every finished map, and the
placement half of the paddy rule that went with it. The placer's own docstring names the relationship:
`_well_ground_clear` is "the placement half of `wells_clear_of_paddies`" and of `wells_off_the_wet_toe`.

THE RULE IN ONE LINE: you do not dig a well in a watercourse, in the middle of a crop plot, or in a bog.

Each leg was earned. The overlap matrix (feature 017) found four wells standing in ditches, a channel and
a hatake plot across three maps - placement had predicted lanes, compounds, the bound and its neighbours,
and never the water or the crop. The bog leg came from settlement-review on Akagahara: a wellhead among
the drawn reed glyphs about 50 ft from the drainage pond. And the paddy leg is the GM's own ruling
(2026-07-27): *"wells on dry crops are okay, but not in rice paddies, surely"* - a paddy is a puddled,
bunded basin under standing water, so a head sunk there stands in the water it is an alternative to.

Tested against the DRAWN head (`_well_vr`), because what a reader sees is ink on ink.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement


def _s() -> Settlement:
    s = Settlement(1200, 1200, seed=1)
    s.meta(name="Wellton", scale="hamlet", ftpx=1, down_deg=90)
    return s


def test_open_dry_ground_takes_a_wellhead() -> None:
    assert _s()._well_ground_clear(600.0, 600.0), "somewhere has to be diggable, or the rest proves nothing"


def test_a_wellhead_is_refused_in_the_pond() -> None:
    """A well sunk in open water is not a well. The pond is recorded as an ellipse, and the head is
    tested against it inflated by the DRAWN radius rather than the true one."""
    s = _s()
    s.M["pond"] = [600.0, 600.0, 120.0, 80.0]
    assert not s._well_ground_clear(600.0, 600.0), "the middle of the pond"
    assert s._well_ground_clear(600.0, 900.0), "and dry ground well clear of it"


def test_a_wellhead_is_refused_on_a_dry_crop_plot() -> None:
    """The hatake leg. A well in the middle of a plot is a well nobody can reach without walking
    through the crop, and one of the four the overlap matrix originally found."""
    s = _s()
    s.M["dry_plots"] = [{"poly": [[400.0, 400.0], [800.0, 400.0], [800.0, 700.0], [400.0, 700.0]], "crop": "barley"}]
    assert not s._well_ground_clear(600.0, 550.0), "the middle of the plot"
    assert s._well_ground_clear(1000.0, 1000.0), "and ground away from it"


def test_the_refusal_is_measured_against_the_DRAWN_head_not_a_point() -> None:
    """`_well_vr` is the drawn radius, and the head is refused when its INK laps the feature - not only
    when its centre is inside. A point test would let a wellhead overhang the pond it stands beside,
    which is what a reader would see."""
    s = _s()
    s.M["pond"] = [600.0, 600.0, 100.0, 100.0]
    vr = s._well_vr()
    assert vr > 0, "the drawn head has a radius"
    assert not s._well_ground_clear(600.0 + 100.0 + vr * 0.5, 600.0), "the head laps the pond's rim"
    assert s._well_ground_clear(600.0 + 100.0 + vr * 3.0, 600.0), "and clear of it by its own width, it is fine"


# ---- the pond reserves its own water (feature 166) ------------------------------------------------
# Carries the placement side of `pond_clear_of_field` and `pond_clear_of_paddies`: nothing is seated in
# open water, and the pond makes that true by registering its ellipse where every placer already looks.


def test_a_drawn_pond_registers_the_ellipse_that_placement_consults() -> None:
    """Both halves of the chain, as with every other reservation in this engine: drawing the pond must
    REGISTER it, and the placer must consult the registry. A test of either alone passes while the other
    rots."""
    s = _s()
    before = len(s.ellipses)
    s.pond(600.0, 600.0, 120.0, 80.0)
    assert len(s.ellipses) == before + 1, "a drawn pond reserves its water"
    assert s.M["pond"] == [600.0, 600.0, 120.0, 80.0], "and records it for the manifest"


def test_nothing_is_seated_in_the_pond() -> None:
    """`pond_clear_of_field` / `pond_clear_of_paddies`, from the placement side. `_in_blocked` reads the
    ellipse registry, so a pond refuses ground to everything that asks - not only to the features whose
    own check happened to mention it."""
    s = _s()
    s.pond(600.0, 600.0, 120.0, 80.0)
    assert s._in_blocked(600.0, 600.0), "the middle of the water"
    assert s._in_blocked(690.0, 600.0), "and inside its rim"
    assert not s._in_blocked(600.0, 1100.0), "dry ground elsewhere is free"
