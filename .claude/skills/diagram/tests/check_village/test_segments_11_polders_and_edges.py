"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

import math

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import _WHY, _feature_022_manifest, _waived_map, f_only

# ---- dwellings must not sit in the WET low toe below the field's drainage ditch (feature 005 / GM 2026-07) ----


def test_polder_field_must_fill_its_bbox():
    # a field declared field_archetype=polder_grid must FILL its bounding box (a surveyed rectangle); a fan-shaped
    # outline covering only a fraction of its bbox fires.
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}}
    rect = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[100, 100], [900, 100], [900, 1300], [100, 1300]], "bbox": [100, 100, 900, 1300]}]}
    assert "polder_fills_its_bbox" not in f_only(rect, "polder_fills_its_bbox")
    fan = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[500, 100], [900, 1300], [100, 1300]], "bbox": [100, 100, 900, 1300]}]}  # a triangle covers ~half its bbox
    assert "polder_fills_its_bbox" in f_only(fan, "polder_fills_its_bbox")


def test_structures_clear_of_dike():
    # GM 2026-07-22: no farmhouse and no windbreak clump may sit ON the perimeter dike earthwork band.
    dike = [[100, 100], [900, 100], [900, 900], [100, 900]]
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}, "dikes": [{"outline": dike, "w_min": 14.0, "w_max": 38.0}]}
    assert "structures_clear_of_dike" in f_only({**base, "houses": [{"x": 500, "y": 500, "w": 40, "h": 26, "rot": 0, "kind": "plain"}]}, "structures_clear_of_dike")  # house on the dike
    assert "structures_clear_of_dike" in f_only({**base, "village_groves": [{"clumps": [[500, 500], [1200, 1200]]}]}, "structures_clear_of_dike")  # a clump on the dike
    assert "structures_clear_of_dike" not in f_only(
        {**base, "houses": [{"x": 1200, "y": 500, "w": 40, "h": 26, "rot": 0, "kind": "plain"}], "village_groves": [{"clumps": [[1200, 1200]]}]}, "structures_clear_of_dike"
    )
    # a non-polder map (no dike) never trips it
    assert "structures_clear_of_dike" not in f_only(
        {"meta": {"scale": "hamlet", "field_archetype": "valley_paddy"}, "houses": [{"x": 500, "y": 500, "w": 40, "h": 26, "rot": 0, "kind": "plain"}]}, "structures_clear_of_dike"
    )


def test_polder_channels_clear_of_dike():
    # GM 2026-07-22: the polder ring canal runs on the INNER TOE of the dike (field side); an irrigation
    # channel buried in the dike band fires (>4 points), a couple of sluice crossings are fine.
    dike = [[100, 100], [900, 100], [900, 900], [100, 900]]  # a simple square "band" outline
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}, "dikes": [{"outline": dike, "w_min": 14.0, "w_max": 38.0}]}
    inside = {"poly": [[200, 200], [300, 200], [400, 200], [500, 200], [600, 200], [700, 200]], "role": "main", "field": "p"}  # 6 pts in the band
    assert "polder_channels_clear_of_dike" in f_only({**base, "field_ditches": [inside]}, "polder_channels_clear_of_dike")
    outside = {"poly": [[200, 50], [500, 50], [800, 50], [200, 1000]], "role": "main", "field": "p"}  # all outside the band
    assert "polder_channels_clear_of_dike" not in f_only({**base, "field_ditches": [outside]}, "polder_channels_clear_of_dike")
    sluices = {"poly": [[200, 150], [500, 1000], [800, 150]], "role": "drain", "field": "p"}  # 2 crossings <= 4
    assert "polder_channels_clear_of_dike" not in f_only({**base, "field_ditches": [sluices]}, "polder_channels_clear_of_dike")
    # a non-polder archetype never trips it, and no dike -> polder_dike_is_earthwork owns that case
    assert "polder_channels_clear_of_dike" not in f_only(
        {"meta": {"scale": "hamlet", "field_archetype": "valley_paddy"}, "dikes": base["dikes"], "field_ditches": [inside]}, "polder_channels_clear_of_dike"
    )


def test_polder_edges_wander():
    # GM 2026-07-22 (issue 4): a polder's dikes must WANDER (a hand-dug fish-scale polder), not run axis-perfect.
    # A dead-straight axis-aligned outline fires; an outline that runs mostly off-axis passes.
    dike = [{"outline": [[100, 100], [900, 100], [900, 1300], [100, 1300]], "w_min": 14.0, "w_max": 38.0, "gaps": []}]
    base = {"meta": {"scale": "hamlet", "down_deg": 90, "field_archetype": "polder_grid"}, "dikes": dike}
    # an axis-aligned rectangle - with a leading ZERO-LENGTH segment the check skips - scores 0% off-axis
    rect = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[100, 100], [100, 100], [900, 100], [900, 1300], [100, 1300], [100, 100]], "bbox": [100, 100, 900, 1300]}]}
    assert "polder_edges_wander" in f_only(rect, "polder_edges_wander")
    wavy = [(100 + 45 * math.sin(i / 3.0), 100 + i * 24) for i in range(50)] + [(900 + 45 * math.sin(i / 3.0), 1300 - i * 24) for i in range(50)]
    wavy.append(wavy[0])
    passd = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[round(x, 1), round(y, 1)] for x, y in wavy], "bbox": [55, 100, 945, 1300]}]}
    assert "polder_edges_wander" not in f_only(passd, "polder_edges_wander")


def test_polder_dike_gapped_at_sluices():
    # GM 2026-07-22 (issue 1): a THROUGH-CROSSER (a water line running from the field, through the dike band,
    # to outside the field outline) must have a recorded dike gap near where it enters the band; no gap fires.
    band = [[100, 100], [900, 100], [900, 1300], [100, 1300]]
    outline = [[150, 150], [850, 150], [850, 1250], [150, 1250]]  # the field outline sits inside the band
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}, "fields": [{"name": "p", "kind": "paddy", "outline": outline, "bbox": [150, 150, 850, 1250]}]}
    crosser = {"poly": [[500, 700], [500, 120], [500, 50]], "role": "main", "field": "p"}  # field -> through band -> outside
    assert "polder_dike_gapped_at_sluices" in f_only({**base, "dikes": [{"outline": band, "w_min": 14.0, "w_max": 38.0, "gaps": []}], "field_ditches": [crosser]}, "polder_dike_gapped_at_sluices")
    assert "polder_dike_gapped_at_sluices" not in f_only(
        {**base, "dikes": [{"outline": band, "w_min": 14.0, "w_max": 38.0, "gaps": [[500, 110]]}], "field_ditches": [crosser]}, "polder_dike_gapped_at_sluices"
    )


def test_dikepond_water_within_banks_and_rounded():
    # GM 2026-07-22 (issues 3 + 5): each 桑基魚塘 pond's water sits INSIDE its parcel with ROUNDED corners
    # recorded as many sampled vertices. Water spilling past the parcel fires within_banks; a 4-vertex sharp
    # quad fires corners_rounded; no recorded dikeponds fires both.
    field = {"name": "p", "kind": "paddy", "outline": [[100, 100], [900, 100], [900, 1300], [100, 1300]], "bbox": [100, 100, 900, 1300]}
    base = {"meta": {"scale": "hamlet", "field_archetype": "mulberry_dike_fishpond"}, "fields": [field]}

    def parcel(cx, cy):
        return [[cx - 50, cy - 50], [cx + 50, cy - 50], [cx + 50, cy + 50], [cx - 50, cy + 50]]

    def rounded(cx, cy):
        return [[cx + 30 * math.cos(a), cy + 30 * math.sin(a)] for a in [i * math.pi / 6 for i in range(12)]]

    good = [{"parcel": parcel(200 + 120 * i, 300), "water": rounded(200 + 120 * i, 300)} for i in range(12)]
    assert "dikepond_water_within_banks" not in f_only({**base, "dikeponds": good}, "dikepond_water_within_banks")
    assert "dikepond_corners_rounded" not in f_only({**base, "dikeponds": good}, "dikepond_corners_rounded")
    # no recorded dikeponds at all -> both fire
    assert "dikepond_water_within_banks" in f_only(base, "dikepond_water_within_banks")
    assert "dikepond_corners_rounded" in f_only(base, "dikepond_corners_rounded")
    # water spilling past its parcel -> within_banks fires (a rounded ring blown up to r=80, past the +-50 bank)
    spill = [
        {"parcel": parcel(200 + 120 * i, 300), "water": [[cx, cy] for cx, cy in [(200 + 120 * i + 80 * math.cos(a), 300 + 80 * math.sin(a)) for a in [j * math.pi / 6 for j in range(12)]]]}
        for i in range(12)
    ]
    assert "dikepond_water_within_banks" in f_only({**base, "dikeponds": spill}, "dikepond_water_within_banks")
    # a 4-vertex sharp quad (inside its parcel) -> corners_rounded fires
    sharp = [{"parcel": parcel(200 + 120 * i, 300), "water": [[190 + 120 * i, 290], [210 + 120 * i, 290], [210 + 120 * i, 310], [190 + 120 * i, 310]]} for i in range(12)]
    assert "dikepond_corners_rounded" in f_only({**base, "dikeponds": sharp}, "dikepond_corners_rounded")


def test_mulberry_banks_clear_of_channels():
    # GM 2026-07-23: the bank crowns are coppiced BUSHES on the dike; the canals are open water at its toe.
    # A channel centerline penetrating >1.5 px inside a recorded bank fires (bushes standing in the canal);
    # a channel skirting the bank edge passes (the canal genuinely runs along the dike toe); a pond missing
    # its `bank` record fires (the record is what gives the check teeth).
    field = {"name": "p", "kind": "paddy", "outline": [[100, 100], [1700, 100], [1700, 500], [100, 500]], "bbox": [100, 100, 1700, 500]}
    base = {"meta": {"scale": "hamlet", "field_archetype": "mulberry_dike_fishpond"}, "fields": [field]}

    def parcel(cx, cy):
        return [[cx - 50, cy - 50], [cx + 50, cy - 50], [cx + 50, cy + 50], [cx - 50, cy + 50]]

    def rounded(cx, cy):
        return [[cx + 30 * math.cos(a), cy + 30 * math.sin(a)] for a in [i * math.pi / 6 for i in range(12)]]

    def bank(cx, cy):
        return [[cx - 55, cy - 55], [cx + 55, cy - 55], [cx + 55, cy + 55], [cx - 55, cy + 55]]

    ponds = [{"parcel": parcel(200 + 120 * i, 300), "water": rounded(200 + 120 * i, 300), "bank": bank(200 + 120 * i, 300)} for i in range(12)]
    clear = {"poly": [[100, 380], [1700, 380]], "role": "lateral", "field": "p"}  # runs BELOW every bank (banks end at y=355)
    assert "mulberry_banks_clear_of_channels" not in f_only({**base, "dikeponds": ponds, "field_ditches": [clear]}, "mulberry_banks_clear_of_channels")
    grazing = {"poly": [[100, 355], [1700, 355]], "role": "lateral", "field": "p"}  # runs ON the bank edge - the dike toe
    assert "mulberry_banks_clear_of_channels" not in f_only({**base, "dikeponds": ponds, "field_ditches": [grazing]}, "mulberry_banks_clear_of_channels")
    through = {"poly": [[100, 300], [1700, 300]], "role": "lateral", "field": "p"}  # runs THROUGH the middle of every bank
    assert "mulberry_banks_clear_of_channels" in f_only({**base, "dikeponds": ponds, "field_ditches": [through]}, "mulberry_banks_clear_of_channels")
    # a pond whose bank went unrecorded fires - the record is the teeth, dropping it cannot disable the check
    unrecorded = [{k: v for k, v in p.items() if k != "bank"} for p in ponds]
    assert "mulberry_banks_clear_of_channels" in f_only({**base, "dikeponds": unrecorded, "field_ditches": [clear]}, "mulberry_banks_clear_of_channels")


def test_dikeponds_fed_and_drained():
    # GM 2026-07-23: down_deg=90 -> downhill is +y. Every 桑基魚塘 pond needs a FEED (network-end UPHILL =
    # smaller y) AND a DRAIN (network-end DOWNHILL = larger y) on its water, both reaching the network, not
    # crossing. Sealed / one-way / wrongly-angled / crossing ponds fire.
    field = {"name": "p", "kind": "paddy", "outline": [[50, 50], [400, 50], [400, 1300], [50, 1300]], "bbox": [50, 50, 400, 1300]}
    canal = {"poly": [[100, 50], [100, 1250]], "role": "lateral", "seg": "lateral", "field": "p"}  # a vertical canal at x=100
    base = {"meta": {"scale": "hamlet", "down_deg": 90, "field_archetype": "mulberry_dike_fishpond"}, "fields": [field], "field_ditches": [canal]}

    def rect(cx, cy):
        return [[cx - 20, cy - 30], [cx + 20, cy - 30], [cx + 20, cy + 30], [cx - 20, cy + 30]]

    ponds = [{"parcel": rect(200, 120 + i * 90), "water": rect(200, 120 + i * 90)} for i in range(12)]

    def good_sl():
        out = []
        for i in range(12):
            cy = 120 + i * 90
            out.append({"a": [200, cy - 30], "b": [100, cy - 50], "kind": "feed"})  # feed: network-end uphill, on the canal
            out.append({"a": [200, cy + 30], "b": [100, cy + 50], "kind": "drain"})  # drain: network-end downhill, on the canal
        return out

    assert "dikeponds_fed_and_drained" not in f_only({**base, "dikeponds": ponds, "dikepond_sluices": good_sl()}, "dikeponds_fed_and_drained")
    assert "dikeponds_fed_and_drained" in f_only({**base, "dikeponds": ponds}, "dikeponds_fed_and_drained")  # no sluices -> sealed
    bad_feed = good_sl()
    bad_feed[0] = {"a": [200, 90], "b": [100, 130], "kind": "feed"}  # pond0 feed network-end DOWNHILL -> one-way (drain only)
    assert "dikeponds_fed_and_drained" in f_only({**base, "dikeponds": ponds, "dikepond_sluices": bad_feed}, "dikeponds_fed_and_drained")
    bad_drain = good_sl()
    bad_drain[1] = {"a": [200, 150], "b": [100, 110], "kind": "drain"}  # pond0 drain network-end UPHILL -> drains uphill
    assert "dikeponds_fed_and_drained" in f_only({**base, "dikeponds": ponds, "dikepond_sluices": bad_drain}, "dikeponds_fed_and_drained")
    bad_reach = good_sl()
    bad_reach[0] = {"a": [200, 90], "b": [2000, 70], "kind": "feed"}  # feed far-end reaches nothing
    assert "dikeponds_fed_and_drained" in f_only({**base, "dikeponds": ponds, "dikepond_sluices": bad_reach}, "dikeponds_fed_and_drained")
    crossing = good_sl()
    crossing[0] = {"a": [220, 150], "b": [100, 90], "kind": "feed"}  # pond0: feed goes up-left...
    crossing[1] = {"a": [220, 90], "b": [100, 150], "kind": "drain"}  # ...drain goes down-left, so the two cross
    assert "dikeponds_fed_and_drained" in f_only({**base, "dikeponds": ponds, "dikepond_sluices": crossing}, "dikeponds_fed_and_drained")


def test_polder_floor_is_ring_interior():
    # GM 2026-07-22: the polder's green field floor must be the ring-canal INTERIOR (hug the outermost
    # channels), not the dike-boundary envelope. A floor vertex >8 px off the ring fires; a floor on the ring
    # passes. (No ring channels or no floor recorded -> the check is simply skipped.)
    ring = [
        {"poly": [[100, 100], [300, 100]], "role": "main", "seg": "feeder", "field": "p"},
        {"poly": [[300, 100], [300, 300]], "role": "lateral", "seg": "e_toe", "field": "p"},
        {"poly": [[300, 300], [100, 300]], "role": "drain", "seg": "drain", "field": "p"},
        {"poly": [[100, 300], [100, 100]], "role": "lateral", "seg": "w_toe", "field": "p"},
    ]
    base = {
        "meta": {"scale": "hamlet", "field_archetype": "polder_grid"},
        "field_ditches": ring,
        "dikes": [{"outline": [[90, 90], [310, 90], [310, 310], [90, 310]], "w_min": 14.0, "w_max": 38.0, "gaps": []}],
        "fields": [{"name": "p", "kind": "paddy", "outline": [[100, 100], [300, 100], [300, 300], [100, 300]], "bbox": [100, 100, 300, 300]}],
    }
    on_ring = {**base, "comb_floors": {"p": [[100, 100], [300, 100], [300, 300], [100, 300]]}}  # the floor IS the ring loop
    assert "polder_floor_is_ring_interior" not in f_only(on_ring, "polder_floor_is_ring_interior")
    off_ring = {**base, "comb_floors": {"p": [[50, 50], [350, 50], [350, 350], [50, 350]]}}  # the dike-boundary envelope, ~50 px out
    assert "polder_floor_is_ring_interior" in f_only(off_ring, "polder_floor_is_ring_interior")


def test_polder_dike_is_earthwork():
    # GM 2026-07-22: a polder/dike-pond map must record a perimeter-dike earthwork band of VARYING width;
    # a missing dike or a uniform-width one (the reverted post-1949 ruled rectangle) fires.
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}}
    assert "polder_dike_is_earthwork" in f_only(base, "polder_dike_is_earthwork")  # no dike recorded at all
    assert "polder_dike_is_earthwork" in f_only({**base, "dikes": [{"outline": [], "w_min": 20.0, "w_max": 22.0}]}, "polder_dike_is_earthwork")  # near-uniform width
    assert "polder_dike_is_earthwork" not in f_only({**base, "dikes": [{"outline": [], "w_min": 14.0, "w_max": 38.0}]}, "polder_dike_is_earthwork")
    assert "polder_dike_is_earthwork" in f_only({"meta": {"scale": "hamlet", "field_archetype": "mulberry_dike_fishpond"}}, "polder_dike_is_earthwork")
    # a non-polder archetype never trips it
    assert "polder_dike_is_earthwork" not in f_only({"meta": {"scale": "hamlet", "field_archetype": "valley_paddy"}}, "polder_dike_is_earthwork")


def test_torii_avenue_pitch_capped():
    # GM 2026-07-25 after the spacing research: Rokugan's sando is the 1/3/7 SET of formal gateways,
    # not a donation row (a designated-site special case) and not ranked ichi/ni/san gates (200 m -
    # 1.3 km apart), so the pitch is a house rule - ~20 ft, never more than two rail-spans (32 ft).
    # The motivating cases were town/city avenues at 45-114 ft; the village avenues at ~30 ft pass.
    def m(pitch_px, n=3, ftpx=1, **rel):
        return {
            "meta": {"scale": "town", "ftpx": ftpx},
            "religious": [{"kind": "monastery", "x": 500, "y": 500, "w": 40, "h": 28, **rel}],
            "torii": [[500, 560 + pitch_px * i, 9] for i in range(n)],
        }

    assert "torii_avenue_pitch_capped" in f_only(m(61), "torii_avenue_pitch_capped")  # Hirameki's Bishamon, the town case
    assert "torii_avenue_pitch_capped" in f_only(m(38, ftpx=3), "torii_avenue_pitch_capped")  # Tango's Bishamon at 114 ft, the widest in the pool
    assert "torii_avenue_pitch_capped" not in f_only(m(20), "torii_avenue_pitch_capped")  # the house pitch
    assert "torii_avenue_pitch_capped" not in f_only(m(16, ftpx=2), "torii_avenue_pitch_capped")  # a village avenue at 32 ft sits AT the cap and passes
    assert "torii_avenue_pitch_capped" in f_only(m(17, ftpx=2), "torii_avenue_pitch_capped")  # ... 34 ft does not
    assert "torii_avenue_pitch_capped" not in f_only(m(61, torii_outlier=True), "torii_avenue_pitch_capped")  # a designated donation-row site is exempt
    assert "torii_avenue_pitch_capped" not in f_only(m(61, n=1), "torii_avenue_pitch_capped")  # a lone arch has no pitch to measure


def test_torii_count_canonical_numerology():
    # counts are exactly {1, 3, 7} at every proper hall (GM 2026-07-21 numerology ruling; supersedes
    # the retired torii_full_avenue_is_seven and its {1, 2, 7} set): 2 and 4 fire (Hikari's old Benten
    # pair, Hirameki's old unfinished four), 0 fires (the floor - every proper hall has a gate),
    # 1/3/7 pass, an explicitly marked outlier is exempt, and a small_shrine neither needs gates nor
    # absorbs a neighbor's (the misattribution that hid Tango's 2-arch Daikoku entrance).
    def m(n, kind="monastery", **rel_extra):
        return {
            "meta": {"scale": "town"},
            "religious": [{"kind": kind, "x": 500, "y": 500, "w": 40, "h": 28, **rel_extra}],
            "torii": [[500, 560 + 30 * i, 9] for i in range(n)],
        }

    for bad in (2, 4, 8, 0):
        assert "torii_count_canonical" in f_only(m(bad), "torii_count_canonical"), bad
    for ok in (1, 3, 7):
        assert "torii_count_canonical" not in f_only(m(ok), "torii_count_canonical"), ok
    assert "torii_count_canonical" not in f_only(m(4, torii_outlier=True), "torii_count_canonical")  # marked outlier - always with a story
    M = m(3)
    M["religious"].append({"kind": "small_shrine", "x": 510, "y": 585, "w": 12, "h": 9})  # nearer the arches than the hall
    assert "torii_count_canonical" not in f_only(M, "torii_count_canonical")  # exempt AND excluded from attribution


def test_mulberry_dike_fishpond_needs_a_block_of_ponds():
    base = {"meta": {"scale": "hamlet", "field_archetype": "mulberry_dike_fishpond"}}
    rect_ol = [[100, 100], [900, 100], [900, 1300], [100, 1300]]
    good = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": rect_ol, "bbox": [100, 100, 900, 1300]}], "land_use": [{"overlay": "mulberry_fishpond", "count": 40}]}
    assert "dikepond_is_ponds_in_a_block" not in f_only(good, "dikepond_is_ponds_in_a_block")
    no_ponds = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": rect_ol, "bbox": [100, 100, 900, 1300]}]}  # a block but no fishponds
    assert "dikepond_is_ponds_in_a_block" in f_only(no_ponds, "dikepond_is_ponds_in_a_block")


def test_the_waiver_meta_checks_cannot_themselves_be_waived():
    """Otherwise the hatch swallows its own guard: one waiver silencing waivers_are_live would let
    every other waiver rot unreported."""
    M = _waived_map({"waivers_are_live": _WHY, "tanning_yard_on_watr": _WHY})
    assert "waivers_are_live" in f_only(M, "waivers_are_live")


def test_feature_022_gate_refuses_a_meta_check_in_targeted_mode():
    # measured (census 2026-08-15): waivers_are_documented reads only the DECLARED waivers (pure
    # manifest input), so it is legitimately targetable; waivers_are_live reads what actually
    # FIRED this run and is the true meta-check.
    assert "waivers_are_live" in set(check_village.META_CHECKS)
    with pytest.raises(ValueError, match="waivers_are_live"):
        check_village.gate(_feature_022_manifest(), verbose=False, only={"waivers_are_live"})
