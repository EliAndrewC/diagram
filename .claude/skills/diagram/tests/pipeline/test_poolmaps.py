"""The pool discovery surface: which maps exist, in which tree, of which kind (feature 161).

WHY THIS MODULE EXISTS AT ALL. Before feature 161, ten consumers each independently hardcoded the
pool's two-level shape - a `glob("pool/*/*.gen.py")` in the render cache, the cache audit, the gate
sweep and the timings census; an `os.listdir` plus a join in `mapcheck`; a `$(wildcard)` in the
Makefile; a subprocess grep in `check_census`; a literal default path in `check_village.__main__`.
Every one restated a fact that belongs in one place, and they drifted exactly as `poolmaps`' own
docstring warned they would: `mapcheck._live_gens` carries a comment recording that Kuwabata was
converted to `hamletgen` and left in `LEGACY_FROZEN_GENS`, so `regen.py` regenerated it happily
while `make maps` never rolled it at all.

The contract is `specs/161-pool-per-map-folders/contracts/pool-discovery.md`. Its real content is
the TREE SELECTION rather than the file listing: a consumer must SAY which tree its job concerns,
because getting that wrong is silent - a sweep over too few maps is green. Feature 161's own
research found the one place where it would have been loud (the stale-render sweep's `assert
checked`) and recorded that being loud there was luck.

These tests build tiny trees under `tmp_path`, so they are fast, hermetic, and say what the surface
promises rather than what today's pool happens to contain.
"""

from __future__ import annotations

import os

import pytest

from l7r.diagram.pipeline import poolmaps

# A gen that imports a scripted engine is `scripted`; poolmaps detects it by SOURCE TEXT.
SCRIPTED_SRC = "from l7r.diagram.hamletgen import HamletSpec, generate\n"
PLAIN_SRC = "print('no engine import at all')\n"


def _mk(root, tree: str, tier: str, stem: str, src: str, extras: tuple[str, ...] = ()) -> str:
    """One map bundle on disk: <root>/<tree>/<tier>/<stem>/<stem>.gen.py plus any extras."""
    d = root / tree / tier / stem
    d.mkdir(parents=True, exist_ok=True)
    gen = d / f"{stem}.gen.py"
    gen.write_text(src)
    for ext in extras:
        (d / f"{stem}{ext}").write_text("x")
    return str(gen)


@pytest.fixture
def pool(tmp_path):
    """A skill dir holding both trees: two live maps, one compound, one frozen legacy map."""
    _mk(tmp_path, "pool", "hamlets", "sawada", SCRIPTED_SRC, (".json", ".notes.md"))
    _mk(tmp_path, "pool", "hamlets", "inashiro", SCRIPTED_SRC, (".json",))
    _mk(tmp_path, "pool", "magistracies", "ochiba-magistracy", PLAIN_SRC, (".svg",))
    _mk(tmp_path, "legacy-hand-authored-pool", "towns", "hoshizora", PLAIN_SRC, (".json", ".png"))
    # Not maps: the negative-fixture corpus and an interpreter dropping.
    (tmp_path / "pool" / "regressions").mkdir(parents=True)
    (tmp_path / "pool" / "regressions" / "some_check_fires.json").write_text("{}")
    (tmp_path / "pool" / "hamlets" / "__pycache__").mkdir(parents=True)
    return tmp_path


def _stems(bundles) -> list[str]:
    return [b.stem for b in bundles]


def test_both_trees_are_walked_by_default(pool):
    """The default sees EVERYTHING. A consumer that over-collects trips its own assertions; one that
    under-collects is green - so the safe default is the one that misses nothing."""
    assert _stems(poolmaps.bundles(skill_dir=str(pool))) == [
        "inashiro",
        "sawada",
        "ochiba-magistracy",
        "hoshizora",
    ]


def test_order_is_deterministic_live_tree_first(pool):
    """Sorted by (tree, tier, stem) with `pool` first, so any listing built from it is stable and two
    consumers can never disagree about order."""
    twice = [_stems(poolmaps.bundles(skill_dir=str(pool))) for _ in range(2)]
    assert twice[0] == twice[1]
    trees = [b.tree for b in poolmaps.bundles(skill_dir=str(pool))]
    assert trees == ["pool", "pool", "pool", "legacy-hand-authored-pool"]


def test_a_single_tree_can_be_asked_for(pool):
    assert _stems(poolmaps.bundles(trees=("pool",), skill_dir=str(pool))) == [
        "inashiro",
        "sawada",
        "ochiba-magistracy",
    ]
    assert _stems(poolmaps.bundles(trees=(poolmaps.LEGACY_TREE,), skill_dir=str(pool))) == ["hoshizora"]


def test_kinds_filter_is_exactly_the_classification(pool):
    """The filter is not allowed to be a second, subtly different rule - that is how `mapcheck` and
    `regen.py` came to disagree about Kuwabata."""
    every = poolmaps.bundles(skill_dir=str(pool))
    for kind in ("scripted", "legacy", "compound"):
        assert _stems(poolmaps.bundles(kinds={kind}, skill_dir=str(pool))) == [b.stem for b in every if b.kind == kind]


def test_the_gate_sweeps_live_scripted_maps_only(pool):
    """The exact request `tests/test_villages.py` makes: a frozen map is never regenerated and a
    compound has no manifest to gate."""
    got = poolmaps.bundles(trees=("pool",), kinds={"scripted"}, skill_dir=str(pool))
    assert _stems(got) == ["inashiro", "sawada"]


def test_a_bundle_round_trips_to_its_own_files(pool):
    (one,) = poolmaps.bundles(trees=("pool",), kinds={"compound"}, skill_dir=str(pool))
    assert os.path.dirname(one.gen) == one.directory
    assert os.path.basename(one.directory) == one.stem == "ochiba-magistracy"
    assert one.path(".gen.py") == one.gen
    assert one.path(".svg") == os.path.join(one.directory, "ochiba-magistracy.svg")
    assert one.tier == "magistracies"


def test_path_answers_for_a_render_that_does_not_exist(pool):
    """A live map's renders are gitignored and absent in a clean checkout, so `path` must describe
    where a file WOULD be rather than only where one is."""
    (ina,) = [b for b in poolmaps.bundles(skill_dir=str(pool)) if b.stem == "inashiro"]
    assert ina.path(".png").endswith("inashiro/inashiro.png")
    assert not os.path.exists(ina.path(".png"))


def test_every_bundles_tree_agrees_with_its_kind(pool):
    """The invariant the ratchet enforces on the real pool (FR-013a), stated here on a toy tree."""
    for b in poolmaps.bundles(skill_dir=str(pool)):
        expected = {"pool": {"scripted", "compound"}, poolmaps.LEGACY_TREE: {"legacy"}}[b.tree]
        assert b.kind in expected, f"{b.stem} in {b.tree} classifies {b.kind}"


def test_classify_is_unchanged_one_level_deeper(pool):
    """FR-011. It holds by construction - the lists are basename-keyed - and the point of pinning it
    is that a future change to `classify` cannot break it silently."""
    deep = _mk(pool, "legacy-hand-authored-pool", "hamlets", "moritono", PLAIN_SRC)
    assert poolmaps.classify(deep) == "legacy"
    flat = pool / "moritono.gen.py"
    flat.write_text(PLAIN_SRC)
    assert poolmaps.classify(str(flat)) == "legacy"


def test_non_maps_are_never_bundles(pool):
    """`pool/regressions/` holds 107 negative fixtures and no map bundle; `__pycache__` is a
    dropping. Both are excluded HERE so the index and the sweeps cannot disagree about it."""
    got = poolmaps.bundles(skill_dir=str(pool))
    assert "regressions" not in {b.tier for b in got}
    assert not [b for b in got if "__pycache__" in b.directory]


def test_an_absent_tree_contributes_nothing_rather_than_raising(tmp_path):
    """`pool/capitals/` does not exist yet, and a fixture that builds one tree must not have to build
    the other."""
    _mk(tmp_path, "pool", "hamlets", "inashiro", SCRIPTED_SRC)
    assert _stems(poolmaps.bundles(skill_dir=str(tmp_path))) == ["inashiro"]
    assert poolmaps.bundles(trees=(poolmaps.LEGACY_TREE,), skill_dir=str(tmp_path)) == []


def test_an_empty_skill_dir_is_empty_not_an_error(tmp_path):
    assert poolmaps.bundles(skill_dir=str(tmp_path)) == []


# THE TEST AGAINST THE REAL POOL LIVES IN `tests/test_villages.py`, NOT HERE - deliberately, and it
# is worth saying why rather than leaving a reader to wonder where it went. That file already owns
# the RATCHET ("every pool gen is classified"), which is the same assertion over the same tree, and
# splitting it across two files is how two guards come to disagree. Feature 161 widened the ratchet
# to cover BOTH trees (spec FR-013a); this file stays hermetic, so it says what the surface PROMISES
# rather than what today's pool happens to contain.
