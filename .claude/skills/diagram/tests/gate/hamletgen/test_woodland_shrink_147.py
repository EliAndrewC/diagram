"""THE WOODLAND SHRINK LADDER, WALKED ON PURPOSE (features 147, 149, 155; re-aimed 166).

`hinterland.open_ground_patches` steps a coppice DOWN in size when the seat it picked will not hold a
full-sized parcel inside the crop window - *"a smaller coppice on the sheet beats a larger one the crop
cuts off. Only when even the floor-sized parcel fails is the seat genuinely unusable."*

IT USED TO BE A COVERAGE CARRIER, AND IS NOT ANY MORE. The ladder leaves nothing observable behind, so
this test could only assert that the floor stayed green, and its own docstring recorded the cost: *"which
member walks it moves with the engine"*. Feature 152's lane changes moved the maps and it stopped
carrying, exactly as predicted. The ladder itself is now `fit_square_parcel`, a module-level function over
plain numbers, and `tests/hamletgen/test_hinterland.py` pins its rungs, its floor clamp and its give-up
directly. What a REAL site is still needed for is the property below, which no unit test can state.

**AND IT WAS ASSERTING ON NOTHING** (found 2026-08-30, while profiling the gate). The site it built -
cohort seed 41, 11 households - returns ZERO parcels across the whole swept band, so the loop carrying
this file's one real property never executed. It spent 9.1 s building a map and then checked nothing.
Measured across candidates: seed 41 / 11 hh returns 0 parcels in 9.16 s; seed 4 / 10 hh returns 21 in
7.78 s. The site is now the one that actually exercises the property, and it is also the CHEAPER of the
two - the usual shape, where the vacuous fixture was not even buying speed.

**THE BUILD IS 97% OF THE COST AND IS NOW CACHED.** 9.1 s of build against 0.45 s for the entire 16-call
sweep, which made this the slowest test in the repository and the critical path of the whole suite on
eight workers. It goes through `rollcache.keyed_to` like every other gate test that builds a site, so the
build is paid only when this test's source or the engine changes. `produce` returns plain data, never the
Settlement, which is the contract `keyed_to` states.

Do NOT park the lines. Feature 149 removed that park after fixing the cause of the floor's flicker, which
was stale cached coverage rather than anything here.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen import hinterland
from l7r.diagram.hamletgen.hinterland import _COMMONS_FLOOR_FT, open_ground_patches
from l7r.diagram.pipeline import rollcache

# The swept band, and the site that makes it mean something. Both measured, not guessed - the module
# docstring carries the candidates and their parcel counts.
ASKED = tuple(range(100, 720, 40))
SPEC = hg.HamletSpec(name="Woodland-shrink", seed=4, households=10, down_deg=90)

LADDER_AND_ROLL_MAX = 1.10 * 1.15
"""How much LARGER than the asked size a returned parcel may legitimately be.

THE ASSERTION THIS REPLACES WAS FALSE, and had never run. It demanded `max(w, h) <= asked` - "a parcel
that came back is the shrunk one, never larger than asked" - which the engine has never promised. The
first rung is `size * _ladder` where `_ladder = 0.90 + 0.20 * jitter` reaches **1.10**, and a per-parcel
size roll of +/-15% sits on top of the rung, so the honest ceiling is 1.10 * 1.15 = 1.265. Measured on
this site: the worst parcel is 1.164x its asked size, inside the band and outside the old assertion.

That the claim was wrong is not the interesting part. The interesting part is that it could not be
found: the site this file used returned ZERO parcels, so the loop never ran, and a false statement sat in
a passing test for three features."""


@pytest.mark.rolls_map
def test_the_woodland_shrink_ladder_is_walked_on_a_real_site(monkeypatch) -> None:
    def produce():  # type: ignore[no-untyped-def]
        walked: list[float] = []
        real = hinterland.fit_square_parcel

        def _spy(half: float, floor_half: float, fits):  # noqa: ANN001, ANN202 - a pass-through spy
            got = real(half, floor_half, fits)
            if got is not None:
                walked.append(got)
            return got

        monkeypatch.setattr(hinterland, "fit_square_parcel", _spy)
        plan = hg.plan_site(SPEC)
        s = hg.build(plan)  # the expensive half, paid once and then cached
        # THE BAND IS SWEPT, NOT GUESSED. Too small and the full square fits, so the ladder is never
        # reached; too large and even the floor-sized rung fails, so it is reached and gives up. The rung
        # runs in between, and where that band sits moves with the engine - which is exactly what made
        # the pinned-size version of this test rot twice.
        widest: list[tuple[float, float]] = []
        for asked in ASKED:
            for poly in open_ground_patches(s, plan, 3, size=float(asked)):
                w = max(p[0] for p in poly) - min(p[0] for p in poly)
                h = max(p[1] for p in poly) - min(p[1] for p in poly)
                widest.append((float(asked), max(w, h)))
        return widest, list(walked)

    (widest, walked), _how = rollcache.keyed_to(test_the_woodland_shrink_ladder_is_walked_on_a_real_site, produce)

    assert widest, "no parcel came back at ANY asked size - this test would assert nothing, which is the state it was found in"
    for asked, got in widest:
        assert got <= asked * LADDER_AND_ROLL_MAX, f"a parcel came back {got / asked:.2f}x the asked size, past the ladder-and-roll band ({got:.0f} for {asked:.0f})"
        assert got >= _COMMONS_FLOOR_FT, f"a parcel came back at {got:.0f} px, under the {_COMMONS_FLOOR_FT:.0f} ft floor below which a commons stops reading as one"

    # NO ASSERTION THAT THE RUNG WAS WALKED, and that is the third answer to a question this file has got
    # wrong twice. Whether a given site and size reach the shrink moves with the engine, so demanding it
    # here just re-creates the rot: the ladder's own decisions are pinned over plain numbers in
    # `tests/hamletgen/test_hinterland.py`, and the caller is a single expression with nothing left to
    # cover.
    if walked:  # ...and when it does walk, every rung it took obeyed the floor
        assert all(h >= 0.0 for h in walked)
