"""`l7r/diagram/ci/pool_readers.py` (feature 430 T01, D1): the one copy of the readers rule, for quick and for the gate."""

from pathlib import Path

from l7r.diagram.ci import pool_readers


def test_is_manifest_names_a_shipped_maps_manifest_only() -> None:
    assert pool_readers.is_manifest("pool/hamlets/inashiro/inashiro.json")
    assert not pool_readers.is_manifest("pool/hamlets/inashiro/other.json"), "a JSON not named for its map"
    assert not pool_readers.is_manifest("legacy-hand-authored-pool/x/x.json"), "the frozen tree is no shipped pool"
    assert not pool_readers.is_manifest("pool/hamlets/inashiro/inashiro.gen.py")


def test_readers_skips_the_named_trees_and_every_tier_tree(tmp_path: Path) -> None:
    for rel in ("tests/test_census.py", "tests/gate/test_g.py", "tests/soak/test_s.py", "tests/tier_city/test_c.py"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text('for tree in ("pool", "legacy-hand-authored-pool"):\n    pass\n', encoding="utf-8")
    (tmp_path / "tests" / "test_plain.py").write_text("x = 1\n", encoding="utf-8")
    assert pool_readers.readers(tmp_path) == ["tests/gate/test_g.py", "tests/test_census.py"]
    assert pool_readers.readers(tmp_path, ("gate", "soak")) == ["tests/test_census.py"]
