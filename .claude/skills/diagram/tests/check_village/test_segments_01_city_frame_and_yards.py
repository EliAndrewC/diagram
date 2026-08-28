"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from l7r.diagram import check_village
from tests.check_village._builders import (
    _crop_map,
    _mx_map,
    bldg,
    f,
    f_only,
    garden,
    house,
    manifest,
    yard,
)


def test_a_paid_matrix_debt_fires_so_the_line_gets_deleted(monkeypatch):
    """An _MATRIX_OUTSTANDING line is WORK OWED. Once the defect is fixed the line does not just rot -
    it goes on tolerating that many real overlaps of that pair for ever. Minami's five were fixed
    while the entry recording them stayed behind."""
    monkeypatch.setitem(check_village._MATRIX_OUTSTANDING, "Nowhere", {("dry_plots", "manors"): 2})
    M = manifest(meta={"scale": "village", "ftpx": 1, "W": 1000, "H": 1000, "name": "Nowhere"})
    assert "matrix_debts_still_owed" in f_only(M, "matrix_debts_still_owed")  # the map draws neither, so the debt is paid


def test_an_unpaid_matrix_debt_stays_quiet(monkeypatch):
    monkeypatch.setitem(check_village._MATRIX_OUTSTANDING, "Nowhere", {})
    M = manifest(meta={"scale": "village", "ftpx": 1, "W": 1000, "H": 1000, "name": "Nowhere"})
    assert "matrix_debts_still_owed" not in f_only(M, "matrix_debts_still_owed")


def test_hard_features_within_frame_fires_on_a_feature_clipped_by_the_crop():
    # a set-apart graveyard placed past the tight WEST frame edge (its west edge x=310 < the view's x0=400).
    # the torii (list branch) and well (radius branch) sit INSIDE the frame - only the graveyard is clipped.
    M = {
        "meta": {"scale": "village", "view": [400, 100, 1000, 800]},
        "torii": [[500, 300, 1]],
        "wells": [{"x": 600, "y": 300, "r": 8}],
        "cemeteries": [{"x": 360, "y": 500, "w": 100, "h": 70, "rot": 0}],
    }
    assert "hard_features_within_frame" in f_only(M, "hard_features_within_frame")


def test_crop_hugs_content_fires_when_the_frame_is_held_open():
    # Kikuta's defect in miniature: the north view edge sits ~385px above the northernmost
    # frame-setting content because the crop was holding the windbreak grove fully in frame
    M = {
        "meta": {"scale": "village", "view": [150, -300, 120, 455]},
        "houses": [{"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
        "village_groves": [{"poly": [[100, -290], [300, -290], [300, 60], [100, 60]], "role": "windbreak"}],
    }
    assert "crop_hugs_content" in f_only(M, "crop_hugs_content")


def test_crop_hugs_content_counts_the_windbreaks_inner_face_but_not_its_depth():
    """GM 2026-08-26 (feature 133 T10): the belt's inner FACE is frame-setting, the belt behind it is
    not - so a view opened 48 px past the front row of crowns passes, and one opened past the
    whole belt (Kikuta's defect) still fires."""
    belt = {"role": "windbreak", "r": 14, "clumps": [[x, y] for x in (150, 200, 250) for y in (-200, -150, -100, -50)], "poly": [[100, -220], [300, -220], [300, -30], [100, -30]]}
    house = {"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}
    face = -50 + 14  # the southernmost clump row's crowns end here, facing the house
    snug = {"meta": {"scale": "village", "view": [150, face - 48, 120, 115 - (face - 48)]}, "houses": [house], "village_groves": [belt]}
    assert "crop_hugs_content" not in f_only(snug, "crop_hugs_content"), "48 px past the face is the margin, not slack"
    wide = {"meta": {"scale": "village", "view": [150, -300, 120, 415]}, "houses": [house], "village_groves": [belt]}
    assert "crop_hugs_content" in f_only(wide, "crop_hugs_content"), "the belt's depth still may not hold the frame open"


def test_crop_hugs_content_passes_on_a_snug_frame():
    M = {
        "meta": {"scale": "village", "view": [150, 45, 120, 110]},
        "houses": [{"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
    }
    assert "crop_hugs_content" not in f_only(M, "crop_hugs_content")


def test_crop_hugs_content_reveals_only_a_band_of_a_canvas_filling_forest():
    # a wood drawn to the canvas edge is frame-setting only to FOREST_REVEAL_FT past its TREE LINE
    # (deeper in it is identical crowns), so a frame that stops there is snug, not "held open"...
    # (deeper in it is identical crowns), so a view opened 190px past the tree line is HELD OPEN
    M = {
        "meta": {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 500, "view": [150, 45, 550, 110]},
        "houses": [{"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
        "forest": [[400, 0], [400, 500], [1000, 500], [1000, 0]],
        "forest_edge": [[400, 0], [400, 500]],
    }
    assert "crop_hugs_content" in f_only(M, "crop_hugs_content")
    assert "crop_hugs_content" not in f_only({**M, "meta": {**M["meta"], "view": [150, 45, 360, 110]}}, "crop_hugs_content")  # snug: the reveal band exactly
    # a wood recorded WITHOUT its tree line keeps the legacy rule - the whole clamped polygon is
    # frame-setting, so the same wide view reads as snug
    assert "crop_hugs_content" not in f_only({**M, "forest_edge": None}, "crop_hugs_content")


def test_crop_hugs_content_is_not_excused_by_a_forest_running_off_both_canvas_ends():
    # the wood's N-S tree line runs off BOTH ends of the canvas - it is running ALONG that axis, not
    # bounding anything, so it cannot excuse a frame held open to the canvas top (GM 2026-07-25: this
    # is what pinned Moritono's north edge 127px past the northernmost real content). The house is the
    # only vertical content, so a full-height view is loose and a snug one passes.
    M = {
        "meta": {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 500, "view": [150, 0, 360, 500]},
        "houses": [{"x": 200, "y": 300, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
        "forest": [[400, -10], [400, 510], [1000, 510], [1000, -10]],
        "forest_edge": [[400, -10], [400, 510]],
    }
    assert "crop_hugs_content" in f_only(M, "crop_hugs_content")
    assert "crop_hugs_content" not in f_only({**M, "meta": {**M["meta"], "view": [150, 255, 360, 90]}}, "crop_hugs_content")


def test_hard_features_within_frame_lets_the_windbreak_clip_but_not_vanish():
    # a windbreak POKING past the frame edge is fine (part visible = "the wood continues";
    # the crop no longer holds the frame open for it) ...
    M = {
        "meta": {"scale": "village", "view": [0, 0, 400, 300]},
        "village_groves": [{"poly": [[100, -200], [300, -200], [300, 80], [100, 80]], "role": "windbreak"}],
    }
    assert "hard_features_within_frame" not in f_only(M, "hard_features_within_frame")
    # ... but one ENTIRELY outside the view is a lost feature and still fires
    M2 = {
        "meta": {"scale": "village", "view": [0, 0, 400, 300]},
        "village_groves": [{"poly": [[100, -200], [300, -200], [300, -40], [100, -40]], "role": "windbreak"}],
    }
    assert "hard_features_within_frame" in f_only(M2, "hard_features_within_frame")


def test_crop_not_held_open_fires_on_a_lone_small_feature_far_out():
    # one 28px-tall building ~400px south of everything else: it alone makes the image taller
    M = _crop_map(buildings=[bldg(500, 500), bldg(540, 500), bldg(520, 900)])
    assert "crop_not_held_open_by_one_feature" in f_only(M, "crop_not_held_open_by_one_feature")


def test_crop_not_held_open_spares_a_LARGE_outlying_feature():
    # a pond out on its own is the outlying CONTENT - big, and meant to be there. This is the
    # case that made the rule a RATIO rather than a flat gap (ponds measured 1.03-1.35x in the pool)
    M = _crop_map(pond=[520, 900, 200, 200])
    assert "crop_not_held_open_by_one_feature" not in f_only(M, "crop_not_held_open_by_one_feature")


def test_crop_not_held_open_honors_the_declared_opt_out():
    M = _crop_map(buildings=[bldg(500, 500), bldg(540, 500), bldg(520, 900)])
    M["meta"]["crop_outlier_ok"] = True
    assert "crop_not_held_open_by_one_feature" not in f_only(M, "crop_not_held_open_by_one_feature")


# ---- found by the settlement-review agent, 2026-07-26 -------------------------------------------


def test_features_do_not_overlap_catches_a_crop_plot_in_a_watercourse():
    """The defect this feature was opened for, caught by the GENERAL rule with no pair-specific code."""
    plot = [[500, 500], [560, 500], [560, 560], [500, 560]]
    M = _mx_map(dry_plots=[{"poly": plot, "crop": "barley", "theta": 0}], streams=[{"poly": [[530, 400], [530, 700]], "w": 9}])
    assert "features_do_not_overlap" in f_only(M, "features_do_not_overlap")
    M["streams"] = [{"poly": [[900, 400], [900, 700]], "w": 9}]  # moved clear
    assert "features_do_not_overlap" not in f_only(M, "features_do_not_overlap")


def test_matrix_permits_an_annex_on_its_OWN_parent_only():
    """Strictly stronger than the blanket exemption it replaces: a kura behind its own shop is fine,
    the same kura drawn across a NEIGHBOR's building is a defect - which the blanket form could not
    express, and which the first pool run duly found twice."""
    own = _mx_map(buildings=[bldg(500, 500)], storehouses=[{"x": 500, "y": 512, "w": 20, "h": 14, "of": [500, 500]}])
    other = _mx_map(buildings=[bldg(500, 500), bldg(560, 500)], storehouses=[{"x": 556, "y": 500, "w": 20, "h": 14, "of": [500, 500]}])
    assert "features_do_not_overlap" not in f_only(own, "features_do_not_overlap")
    assert "features_do_not_overlap" in f_only(other, "features_do_not_overlap")


def test_matrix_permits_two_annexes_of_one_household_to_abut():
    M = _mx_map(
        houses=[house(500, 500)],
        threshing_yards=[yard(500, 540, of=(500, 500))],
        gardens=[garden(500, 552, of=(500, 500))],
    )
    assert "features_do_not_overlap" not in f_only(M, "features_do_not_overlap")


def test_matrix_permits_a_ditch_on_its_own_field_but_not_another():
    M = _mx_map(
        fields=[
            {
                "name": "west",
                "kind": "paddy",
                "outline": [[400, 400], [700, 400], [700, 700], [400, 700]],
                "bbox": [400, 400, 700, 700],
                "vis_bbox": [400, 400, 700, 700],
                "plots": [[60, 60, 550, 550, 4, 4]],
            }
        ],
        field_ditches=[{"poly": [[550, 400], [550, 700]], "w": 1.5, "field": "west", "role": "main"}],
        houses=[house(551, 480)],
    )
    fails = f(M)
    assert "features_do_not_overlap" in fails  # the HOUSE is on the ditch, and it is nobody's annex


def test_every_feature_classified_for_matrix_is_the_ratchet(monkeypatch):
    """A drawn key with no class must fail BY NAME - the whole promise is 'add one line and you are
    protected', which only holds if forgetting the line is loud."""
    M = _mx_map(houses=[house(500, 500)])
    assert "every_feature_classified_for_matrix" not in f_only(M, "every_feature_classified_for_matrix")
    monkeypatch.delitem(check_village.OVERLAP_CLASS, "houses")
    assert "every_feature_classified_for_matrix" in f_only(M, "every_feature_classified_for_matrix")


def test_matrix_reads_drawn_extents_not_envelopes():
    """A commons is an ENVELOPE around a sparse scatter and is permissive besides, so it is never
    even extracted; testing envelopes is what made the motivating survey over-report ~2x."""
    M = _mx_map(commons=[{"x": 500, "y": 500, "w": 400, "h": 400, "rot": 0, "role": "grazing", "poly": [[300, 300], [700, 300], [700, 700], [300, 700]]}], houses=[house(500, 500)])
    assert "features_do_not_overlap" not in f_only(M, "features_do_not_overlap")
    assert not [e for e in check_village.matrix_extents(M) if e[0] == "commons"]
