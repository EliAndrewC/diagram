"""Where a hamlet's coarse grain grows (feature 287, water W36; research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.html, 0011; its map rules at research/contents.json#fields 0006).

The paddy is sized for the rice two-thirds of the diet (0017, the sizing rule), so the coarse third has to grow
somewhere. The record attests two places, and which one a hamlet used is the WINTER CROP knob of 0009 ("The
paddy through the rice year"): a double-cropped hamlet grew its barley on its own drained paddy between
the rice harvests; a single-cropped one grew it in dry fields. On a fan whose middle is still wild (`fan_middle`,
0006) the dry band holds only the toe's stretch, so a single-cropped hamlet's band is TOPPED UP into the middle,
nearest the toe first, until it holds the need - the middle cleared as far as the hamlet's grain needed and no further.
The knob is rolled only among the forms the site can feed (`_grows_on_this_ground`), so the band holds the need by
construction. Measured over cohort 1-60 and the pool (2026-09-29): the whole wild middle holds 36-124 acres against needs
of 8.5-17, so both forms are offered on every wild fan; a CLEARED fan's strip holds 2.5-5.2 acres, so it is offered
barley only - which its drained paddy (1.21-1.37 acres a household against a 0.85 need) always covers.

Classes (the four labels, research/CLAUDE.md):
- the two forms, winter barley on the drained paddy and dry fields: historically ACCURATE (0009, 0011);
- the weights between them: GUESS (0009: the drainage and the manure decide, and no share was read);
- the need per household (`COARSE_GRAIN_ACRES_PER_HOUSEHOLD`): a GUESS resting on the attested assessed rates; the winter
  crop counted acre for acre against it: GUESS (no yield for a winter barley crop was read; 0011 records the search);
- the order of the top-up, nearest the toe first: GUESS (no page read says from which end a fan's middle was cleared).

Research: plumbing - NONE: unit conversion and ring area
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from .._knobs import Knob, register_knob


# THE WINTER CROP (research/contents.json#fields 0009): "Two forms are attested, so this is a knob, rolled per settlement: one
# whose paddies carry a winter crop, and one whose paddies lie bare over the winter." An even weight is a GUESS.
#
# NARROWED TO WHAT THE SITE ALLOWS (feature 287, W36; as plan D4 narrowed the cluster shape): a form is offered only where
# the ground can grow the grain it leaves to dry fields - "none" only where the toe's strip and the whole wild middle
# (`waterfields/hem.py` `middle_reserve`) hold the whole need, "barley" only where they hold what the drained paddy
# leaves. The draw puts the hamlet's households, its drained acres and that room in the context; a context without them
# (anything else that resolves the knob) offers both. A site that allows neither is a loud error, never a short band.
def _grows_on_this_ground(form: str, context: Mapping[str, Any]) -> bool:
    """Research: forms the site can feed - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: a bare winter only where the toe and the whole wild middle hold the need"""
    if "grain_room_acres" not in context:
        return True
    return dry_need_acres(int(context["grain_households"]), float(context["grain_drained_acres"]), form) <= float(context["grain_room_acres"])


TOWN_NEARNESS = register_knob(Knob("town_nearness", ["near", "far"], default="far"))
"""Research: a town's nearness - GUESS: near or far, even odds; no hamlet spec records the distance to its market town"""

TOWN_FAR_FACTOR = 0.5
"""Research: a far town's weight on the winter barley - GUESS: half a near town's, the manure a second crop needed being
dearer to bring (0009: how drainage and a town's nearness weigh against each other is a GUESS)"""


class WinterCropKnob(Knob):
    """The winter crop, its odds set by the site (0009: "A settlement's drainage and the nearness of a town, whose manure a
    second crop needed, set the odds"): barley weighs the drained share of the paddy, times `TOWN_FAR_FACTOR` where the town
    is far; a bare winter takes the rest. A context without the site's figures rolls even odds.

    Research: winter-crop weights - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: the drainage and a town's nearness set the odds; how they weigh is a GUESS"""

    def weights_for(self, context: Mapping[str, Any]) -> dict[Any, float] | None:
        """Barley's odds: the drained share of the paddy, times `TOWN_FAR_FACTOR` where the town is far; the knob's own even
        weights where the site's figures are missing.

        Research: the odds from the site - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: drainage and a town's nearness set the odds, how they weigh a GUESS"""
        paddy = float(context.get("grain_paddy_acres") or 0.0)
        if paddy <= 0.0:
            return self.weights
        share = min(1.0, float(context.get("grain_drained_acres") or 0.0) / paddy)
        barley = share * (1.0 if context.get("grain_town") == "near" else TOWN_FAR_FACTOR)
        return {"barley": barley, "none": 1.0 - barley}


WINTER_CROP = register_knob(WinterCropKnob("winter_crop", ["barley", "none"], default="none", typing_rule=_grows_on_this_ground, weights={"barley": 0.5, "none": 0.5}))
"""
Research:
    winter-crop forms - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html, research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: barley on the drained paddy, or a bare winter
    winter-crop weights - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: set by the site (`WinterCropKnob`); even odds only where the site's figures are missing
"""

# THE COARSE-GRAIN NEED, in acres of dry field per household (0011). The sizing rule (0017) gives ~0.8-1.0
# tan of gross paddy a person for rice's two-thirds of the diet, which is the engine's 1.3 acres a household
# (`hamletgen/consts.py` GROSS_ACRES_PER_HOUSEHOLD); the coarse third is half as much again in grain. The land surveys
# assessed a middle paddy at 1 koku 3 to a tan and, in the Edo period, an upper dry field at 1 koku 2 to, stepping down
# 2 to a grade (0011, kokumori-jawiki) - so a middle dry field at 1 koku, and the third needs half the paddy's
# ground times 1.3: 0.65 x 1.3 = 0.85 acre. That is the early-Edo rung; the mid-Edo reset (upper dry field 1 koku 1 to,
# so a middle one 9 to) would give 0.94. Assessed rates in rice-equivalent koku, not harvests; the middle grade on both
# sides is this project's reading, so the figure is a GUESS resting on attested rates.
COARSE_GRAIN_ACRES_PER_HOUSEHOLD = 0.85
"""Research: coarse-grain need - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: 0.85 acre of dry field a household"""
SQ_FT_PER_ACRE = 43560.0


def dry_need_acres(households: int, drained_acres: float, winter_crop: str) -> float:
    """The acres of dry field a hamlet's coarse grain needs: the whole need where the paddy lies bare over the winter, and
    what the drained paddy's winter barley leaves where it does not - counted acre for acre (a GUESS, module docstring).
    A wet paddy carries no barley (0009), so only the drained acres count.

    Research:
        need by winter crop - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the whole need on a bare winter, the need less the drained acres on barley
        barley acre for acre - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: one drained acre of winter barley spares one acre of dry field
        drained acres only - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: a wet paddy carries no winter barley"""
    need = households * COARSE_GRAIN_ACRES_PER_HOUSEHOLD
    if winter_crop == "barley":
        need -= drained_acres
    return max(0.0, need)


def top_up(drawn_px2: float, reserve: Sequence[dict[str, Any]], need_px2: float, refused: Callable[[Any], bool]) -> list[dict[str, Any]]:
    """The reserve plots that bring a dry band of `drawn_px2` up to `need_px2`: taken in the reserve's order (nearest the
    toe first), each one `refused` skipped (a plot on water or another fan's rice is no field), until the band holds the
    need. The placer's guarantee: the band returned holds the need, or every plot the ground offers is in it.

    Research:
        dry-field count - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: reserve plots added until the band holds the need, and no further
        top-up order - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: nearest the toe first
        refused ground - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot on water or on another fan's rice is skipped"""
    out: list[dict[str, Any]] = []
    for p in reserve:
        if drawn_px2 >= need_px2:
            break
        if refused(p["poly"]):
            continue
        out.append(p)
        drawn_px2 += poly_area(p["poly"])
    return out


def poly_area(poly: Sequence[Sequence[float]]) -> float:
    """The shoelace area of a ring, in its own units squared."""
    n = len(poly)
    return abs(sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))) / 2.0
