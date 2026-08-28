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
