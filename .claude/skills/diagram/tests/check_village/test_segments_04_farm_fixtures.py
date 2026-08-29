from tests.check_village._builders import f, f_only, house, manifest  # noqa: F401

"""The farmstead fixtures (feature 133 T53-T59): the annex rule and the declaration rule."""


_H = house(x=400, y=400)  # w 46, h 28, rot 0
_META = {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 1000, "farm_fixtures": {"privy": 0.9, "woodpile": 0.8, "manure": 0.5, "bath": 0.3, "coop": 0.6, "shrine": 0.05, "persimmon": 0.9}}


def _fix(kind, x, y, w=6, h=6, of=(400, 400)):
    return {"kind": kind, "x": x, "y": y, "w": w, "h": h, "rot": 0, "of": list(of)}


def test_tree_crowns_not_subsumed_fires_and_passes():
    """No canopy tree's center under another crown (GM 2026-08-28: no tree "entirely subsumed within the
    branch structure of a different tree"); edge overlap is fine."""
    bad = manifest(tree_crowns=[100.0, 100.0, 10.0, 103.0, 102.0, 5.0])  # the small crown sits wholly inside the big one
    assert "tree_crowns_not_subsumed" in f_only(bad, "tree_crowns_not_subsumed"), "a subsumed crown must fire"
    under = manifest(tree_crowns=[100.0, 100.0, 10.0, 108.0, 100.0, 9.0])  # centers 8 apart, the larger radius is 10: the second center is under the first crown
    assert "tree_crowns_not_subsumed" in f_only(under, "tree_crowns_not_subsumed")
    good = manifest(tree_crowns=[100.0, 100.0, 10.0, 114.0, 100.0, 9.0, 300.0, 300.0, 8.0])  # 14 apart: the canopies interlace (14 < 19) but neither center is under the other
    assert "tree_crowns_not_subsumed" not in f_only(good, "tree_crowns_not_subsumed"), "edge overlap must pass"
    assert "tree_crowns_not_subsumed" not in f_only(manifest(tree_crowns=[]), "tree_crowns_not_subsumed")
