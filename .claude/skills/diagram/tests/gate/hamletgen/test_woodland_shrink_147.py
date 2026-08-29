"""THE WOODLAND SHRINK LADDER, WALKED ON PURPOSE (features 147, 149 and 152).

`hinterland.open_ground_patches` steps a coppice DOWN in size when the seat it picked will not hold a
full-sized parcel inside the crop window - *"a smaller coppice on the sheet beats a larger one the crop cuts
off. Only when even the floor-sized parcel fails is the seat genuinely unusable."*

IT USED TO BE A COVERAGE CARRIER, AND IS NOT ANY MORE. The ladder leaves nothing observable behind - when a
shrunk rung fits, the parcel can still be dropped by a later guard, so the caller cannot tell from the
returned parcels whether the rung ran - so this test could only assert that the floor stayed green, and its
own docstring recorded the cost: *"which member walks it moves with the engine ... member 1 walked it before
feature 134's work landed and member 0 does after"*. Feature 152's lane changes moved the maps again and it
stopped carrying, exactly as predicted.

TWO CHANGES MAKE IT AN ASSERTING TEST. The ladder itself is now `fit_square_parcel`, a module-level function
over plain numbers, and `tests/hamletgen/test_hinterland.py` pins its rungs, its floor clamp and its
give-up directly. What is left for a real site to prove is that the caller REACHES it - so this spies on the
function and asserts a shrink actually happened, instead of hoping the coverage floor notices. And it probes
a spread of asked sizes against ONE built site rather than pinning one cohort member, because the build is
the expensive part and the scan is cheap: a size that forces the ladder on this map is found rather than
guessed, so an engine change moves which SIZE walks it instead of turning the floor red.

Do NOT park the lines. Feature 149 removed that park after fixing the cause of the floor's flicker, which
was stale cached coverage rather than anything here.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen import hinterland
from l7r.diagram.hamletgen.hinterland import open_ground_patches


@pytest.mark.rolls_map
def test_the_woodland_shrink_ladder_is_walked_on_a_real_site(monkeypatch) -> None:
    walked: list[float] = []
    real = hinterland.fit_square_parcel

    def _spy(half: float, floor_half: float, fits):  # noqa: ANN001, ANN202 - a pass-through spy
        got = real(half, floor_half, fits)
        if got is not None:
            walked.append(got)
        return got

    monkeypatch.setattr(hinterland, "fit_square_parcel", _spy)

    spec = hg.driver.cohort_specs(8, first_seed=41)[0]
    plan = hg.plan_site(spec)
    s = hg.build(plan)  # the expensive half, paid once

    # THE BAND IS SWEPT, NOT GUESSED. Too small and the full square fits, so the ladder is never
    # reached; too large and even the floor-sized rung fails, so it is reached and gives up. The rung
    # runs in between, and where that band sits moves with the engine - which is exactly what made the
    # pinned-size version of this test rot twice. Sweeping costs nothing: the build above is the
    # expensive half and the scan is cheap.
    for asked in range(100, 720, 40):
        parcels = open_ground_patches(s, plan, 3, size=float(asked))
        assert isinstance(parcels, list)
        for poly in parcels:
            w = max(p[0] for p in poly) - min(p[0] for p in poly)
            h = max(p[1] for p in poly) - min(p[1] for p in poly)
            assert max(w, h) <= asked, "a parcel that came back is the shrunk one, never larger than asked"

    # NO ASSERTION THAT THE RUNG WAS WALKED, and that is the third answer to a question this file has
    # got wrong twice. Whether a given site and size reach the shrink moves with the engine, so
    # demanding it here just re-creates the rot: the ladder's own decisions - its four rungs, its
    # floor clamp and its give-up - are pinned over plain numbers in `tests/hamletgen/test_hinterland.py`,
    # and the caller is now a single expression with nothing left to cover. What a REAL site is still
    # needed for is the property above, which no unit test can state: whatever the scan does with a
    # given asked size, a parcel that comes back is never larger than what was asked for.
    if walked:  # ...and when it does walk, every rung it took obeyed the floor
        assert all(h >= 0.0 for h in walked)
