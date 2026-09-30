"""Where a hamlet's coarse grain grows (feature 287, water W36; research/fields.html 'Where did a hamlet at a fan's toe
grow its coarse grain while the fan's middle was still wild?', fields/165).

The paddy is sized for the rice two-thirds of the diet (fields/110, the sizing rule), so the coarse third has to grow
somewhere. The record attests two places, and which one a hamlet used is the WINTER CROP knob of fields/300 ("Did a
paddy grow a second crop over the winter?"): a double-cropped hamlet grew its barley on its own drained paddy between
the rice harvests; a single-cropped one grew it in dry fields. On a fan whose middle is still wild (`fan_middle`,
fields/160) the dry band holds only the toe's stretch, so a single-cropped hamlet's band is TOPPED UP into the middle,
nearest the toe first, until it holds the need - the middle cleared as far as the hamlet's grain needed and no further.
The knob is rolled only among the forms the site can feed (`_grows_on_this_ground`), so the band holds the need by
construction. Measured over cohort 1-60 and the pool (2026-09-29): the whole wild middle holds 36-124 acres against needs
of 8.5-17, so both forms are offered on every wild fan; a CLEARED fan's strip holds 2.5-5.2 acres, so it is offered
barley only - which its drained paddy (1.21-1.37 acres a household against a 0.85 need) always covers.

Classes (the four labels, research/CLAUDE.md):
- the two forms, winter barley on the drained paddy and dry fields: historically ACCURATE (fields/300, fields/165);
- the weights between them: GUESS (fields/300: the drainage and the manure decide, and no share was read);
- the need per household (`COARSE_GRAIN_ACRES_PER_HOUSEHOLD`): a GUESS resting on the attested assessed rates; the winter
  crop counted acre for acre against it: GUESS (no yield for a winter barley crop was read; fields/165 records the search);
- the order of the top-up, nearest the toe first: GUESS (no page read says from which end a fan's middle was cleared).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from .._knobs import Knob, register_knob


# THE WINTER CROP (research/fields.html fields/300): "Two forms are attested, so this is a knob, rolled per settlement: one
# whose paddies carry a winter crop, and one whose paddies lie bare over the winter." An even weight is a GUESS.
#
# NARROWED TO WHAT THE SITE ALLOWS (feature 287, W36; as plan D4 narrowed the cluster shape): a form is offered only where
# the ground can grow the grain it leaves to dry fields - "none" only where the toe's strip and the whole wild middle
# (`waterfields/hem.py` `middle_reserve`) hold the whole need, "barley" only where they hold what the drained paddy
# leaves. The draw puts the hamlet's households, its drained acres and that room in the context; a context without them
# (anything else that resolves the knob) offers both. A site that allows neither is a loud error, never a short band.
def _grows_on_this_ground(form: str, context: Mapping[str, Any]) -> bool:
    if "grain_room_acres" not in context:
        return True
    return dry_need_acres(int(context["grain_households"]), float(context["grain_drained_acres"]), form) <= float(context["grain_room_acres"])


WINTER_CROP = register_knob(Knob("winter_crop", ["barley", "none"], default="none", typing_rule=_grows_on_this_ground, weights={"barley": 0.5, "none": 0.5}))

# THE COARSE-GRAIN NEED, in acres of dry field per household (fields/165). The sizing rule (fields/110) gives ~0.8-1.0
# tan of gross paddy a person for rice's two-thirds of the diet, which is the engine's 1.3 acres a household
# (`hamletgen/consts.py` GROSS_ACRES_PER_HOUSEHOLD); the coarse third is half as much again in grain. The land surveys
# assessed a middle paddy at 1 koku 3 to a tan and, in the Edo period, an upper dry field at 1 koku 2 to, stepping down
# 2 to a grade (fields/165, kokumori-jawiki) - so a middle dry field at 1 koku, and the third needs half the paddy's
# ground times 1.3: 0.65 x 1.3 = 0.85 acre. That is the early-Edo rung; the mid-Edo reset (upper dry field 1 koku 1 to,
# so a middle one 9 to) would give 0.94. Assessed rates in rice-equivalent koku, not harvests; the middle grade on both
# sides is this project's reading, so the figure is a GUESS resting on attested rates.
COARSE_GRAIN_ACRES_PER_HOUSEHOLD = 0.85
SQ_FT_PER_ACRE = 43560.0


def dry_need_acres(households: int, drained_acres: float, winter_crop: str) -> float:
    """The acres of dry field a hamlet's coarse grain needs: the whole need where the paddy lies bare over the winter, and
    what the drained paddy's winter barley leaves where it does not - counted acre for acre (a GUESS, module docstring).
    A wet paddy carries no barley (fields/300), so only the drained acres count."""
    need = households * COARSE_GRAIN_ACRES_PER_HOUSEHOLD
    if winter_crop == "barley":
        need -= drained_acres
    return max(0.0, need)


def top_up(drawn_px2: float, reserve: Sequence[dict[str, Any]], need_px2: float, refused: Callable[[Any], bool]) -> list[dict[str, Any]]:
    """The reserve plots that bring a dry band of `drawn_px2` up to `need_px2`: taken in the reserve's order (nearest the
    toe first), each one `refused` skipped (a plot on water or another fan's rice is no field), until the band holds the
    need. The placer's guarantee: the band returned holds the need, or every plot the ground offers is in it."""
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
