"""The farmstead fixtures (feature 133 T53-T59): the annex rule and the declaration rule."""

from tests.check_village._builders import f_only, house, manifest

_H = house(x=400, y=400)  # w 46, h 28, rot 0
_META = {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 1000, "farm_fixtures": {"privy": 0.9, "woodpile": 0.8, "manure": 0.5, "bath": 0.3, "coop": 0.6, "shrine": 0.05, "persimmon": 0.9}}


def _fix(kind, x, y, w=6, h=6, of=(400, 400)):
    return {"kind": kind, "x": x, "y": y, "w": w, "h": h, "rot": 0, "of": list(of)}


def test_farm_fixtures_attached_fires_on_a_stray_privy_and_passes_at_the_wall():
    """Nipponica: the farm privy was an independent building at the back door, by the naya or at the
    gate - a household's own, at its wall. One 60 ft from every house (or naming none) is a placer
    fault; one 3 ft behind the back wall is right. The persimmon has the longer reach of a crown."""
    stray = manifest(meta=_META, houses=[_H], farm_fixtures=[_fix("privy", 400, 480)])
    assert "farm_fixtures_attached" in f_only(stray, "farm_fixtures_attached")
    orphan = manifest(meta=_META, houses=[_H], farm_fixtures=[dict(_fix("privy", 410, 380), of=[900, 900])])
    assert "farm_fixtures_attached" in f_only(orphan, "farm_fixtures_attached")
    good = manifest(meta=_META, houses=[_H], farm_fixtures=[_fix("privy", 414, 380), _fix("shrine", 363, 372, 3, 3)], persimmons=[{"x": 442, "y": 402, "r": 9, "of": [400, 400]}])
    assert "farm_fixtures_attached" not in f_only(good, "farm_fixtures_attached")
    far_tree = manifest(meta=_META, houses=[_H], persimmons=[{"x": 480, "y": 402, "r": 9, "of": [400, 400]}])
    assert "farm_fixtures_attached" in f_only(far_tree, "farm_fixtures_attached")


def test_farm_fixtures_as_declared_fires_on_the_undeclared_the_doubled_and_the_common_shrine():
    """The GM (T58): the household shrine is "very rare, but notable" - Sugiura counts 3 per 100
    households, so a sheet with two on eight houses at a 0.05 share drew a common thing; a kind
    drawn but not rolled, or two privies on one house, is the placer disagreeing with itself."""
    hs = [house(x=200 + 90 * i, y=400) for i in range(8)]
    undeclared = manifest(meta={**_META, "farm_fixtures": {"privy": 0.9}}, houses=hs, farm_fixtures=[_fix("coop", 214, 380, of=(200, 400))])
    assert "farm_fixtures_as_declared" in f_only(undeclared, "farm_fixtures_as_declared")
    doubled = manifest(meta=_META, houses=hs, farm_fixtures=[_fix("privy", 214, 380, of=(200, 400)), _fix("privy", 186, 380, of=(200, 400))])
    assert "farm_fixtures_as_declared" in f_only(doubled, "farm_fixtures_as_declared")
    common = manifest(meta=_META, houses=hs, farm_fixtures=[_fix("privy", 214, 380, of=(200, 400)), _fix("shrine", 163, 372, 3, 3, of=(200, 400)), _fix("shrine", 253, 372, 3, 3, of=(290, 400))])
    assert "farm_fixtures_as_declared" in f_only(common, "farm_fixtures_as_declared")
    no_privy = manifest(meta=_META, houses=hs, farm_fixtures=[_fix("coop", 214, 380, of=(200, 400))])
    assert "farm_fixtures_as_declared" in f_only(no_privy, "farm_fixtures_as_declared")
    good = manifest(
        meta=_META, houses=hs, farm_fixtures=[_fix("privy", 214, 380, of=(200, 400)), _fix("shrine", 163, 372, 3, 3, of=(200, 400))], persimmons=[{"x": 332, "y": 402, "r": 9, "of": [290, 400]}]
    )
    assert "farm_fixtures_as_declared" not in f_only(good, "farm_fixtures_as_declared")
    assert "farm_fixtures_as_declared" not in f_only(manifest(meta={"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 1000}, houses=hs), "farm_fixtures_as_declared"), (
        "a map with none declared and none drawn passes"
    )
