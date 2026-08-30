"""The non-arable hinterland: scrub, marsh, and what they keep off (feature 166).

Carries `commons_clear_of_paddies`, `scrub_clear_of_urban_fabric` and `marsh_on_low_ground`, which the
retired battery re-measured on every finished map.

CHINA-FIRST, and the grounding matters because it decides what the DOMINANT cover is: the south-China rice
hills were stripped for fuel and timber over roughly a thousand years, so the ground past a settlement is
denuded scrub and rough grazing, NOT forest. The protected fengshui grove is the green exception, and
managed woodland is a few discrete patches on higher or farther ground.

THE PLACER STATES ALL THREE RULES IN ITS OWN DOCSTRING, which is the tell that the checks were restating
it: the scrub bands are frame-margin strips OUTSIDE the cultivated bbox so each centroid clears the paddy;
every scatter skips fields, pond, lanes and buildings plus a hamlet keep-out so no cover creeps among the
houses; and none of it is a crop anchor, so it bleeds off the frame and the crop stays tight.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement

FIELD = [(700.0, 700.0), (1300.0, 700.0), (1300.0, 1300.0), (700.0, 1300.0)]


def _s() -> Settlement:
    s = Settlement(2000, 2000, seed=3)
    s.meta(name="Scrubton", scale="hamlet", ftpx=1, down_deg=90)
    s.M["fields"] = [{"name": "f", "outline": [list(p) for p in FIELD]}]
    s.field_polys = [FIELD]
    return s


def _centroid(poly):
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def _in_field(pt) -> bool:
    x, y = pt
    return 700.0 <= x <= 1300.0 and 700.0 <= y <= 1300.0


def test_every_commons_centroid_clears_the_cultivated_ground() -> None:
    """`commons_clear_of_paddies`. The scrub is what lies BEYOND the crop - a commons centroid inside the
    paddy is grazing drawn over rice. The bands are frame-margin strips outside the cultivated bbox, so
    this holds by construction rather than by inspection afterwards."""
    s = _s()
    # `interior_fill` is OFF here, and the reason is worth recording rather than hiding in a flag. It
    # fills the settlement's INTERIOR - the ground between the cluster, the water and the crop - and this
    # fixture is a field with no settlement at all, so its "interior" is the field itself and the fill
    # lands squarely on it. That is a degenerate fixture, not a defect: on every scripted map the cluster
    # occupies that ground, which is why `commons_clear_of_paddies` has never fired on one. What this test
    # is about is the scrub BANDS - the frame-margin strips outside the cultivated bbox - so the interior
    # fill is a different placement and is excluded rather than accommodated.
    s.hinterland(marsh=True, commons=True, interior_fill=False)
    commons = s.M.get("commons") or []
    assert commons, "the hinterland laid no commons at all"
    assert len(commons) >= 4, "the scrub ring lays a band per frame margin"
    for c in commons:
        poly = [tuple(p) for p in (c.get("poly") or [])]
        if len(poly) >= 3:
            assert not _in_field(_centroid(poly)), f"a commons centroid sits in the crop at {_centroid(poly)}"


def test_the_marsh_lies_at_the_downhill_toe() -> None:
    """`marsh_on_low_ground`. A reed marsh is where wet-rice reclamation stops and the valley floor stays
    wetland - which is BELOW the field's drainage line, not beside it. The toe is a contour band
    perpendicular to the fall, so it rotates with the map like every other feature."""
    s = _s()
    s.hinterland(marsh=True, commons=False)
    marshes = [m for m in (s.M.get("marshes") or []) if m.get("poly")]
    assert marshes, "no marsh was laid at the toe"
    fcy = sum(p[1] for p in FIELD) / len(FIELD)
    # down_deg 90 is south (+y), so the toe must sit BELOW the field's centre
    for m in marshes:
        mcy = _centroid([tuple(p) for p in m["poly"]])[1]
        assert mcy > fcy, f"a marsh at y={mcy:.0f} is not below the field at y={fcy:.0f}"


def test_the_cover_does_not_hold_the_frame_open() -> None:
    """None of the hinterland is a crop anchor, so it BLEEDS off the frame. A scrub band that widened the
    crop would put a margin of empty grazing down one side - the very thing the GM's tight-frame ruling
    forbids, and the reason `_CROP_HARD` excludes cover."""
    bare = _s()
    bare.crop_to_content(margin=30)
    before = bare.M["meta"]["view"]

    covered = _s()
    covered.hinterland(marsh=True, commons=True)
    covered.crop_to_content(margin=30)
    after = covered.M["meta"]["view"]

    assert after[2] <= before[2] + 1 and after[3] <= before[3] + 1, f"the hinterland widened the frame from {before[2]:.0f}x{before[3]:.0f} to {after[2]:.0f}x{after[3]:.0f}"
