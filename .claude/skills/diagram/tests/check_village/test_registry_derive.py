"""Feature 109: the derived registry's guards, and the frozen-legacy equality oracle.

The registry stopped being hand-maintained data on 2026-08-16; these tests hold everything the
explicit roster used to provide (clause 14: move the safety property into tests proven to fire):

1. Fixture equality: every derived row equals its pre-collapse counterpart, by name, all six
   fields (`tests/fixtures/registry_legacy_rows.json`, frozen at the migration and never
   REGENERATED - a row is edited by hand, alone, only when its segment is deliberately changed, so
   the oracle keeps catching accidental drift in every other row. Edited so far: 2026-08-26,
   feature 133 T15 - four rows (0434, 0438.016/024/036) when the near-ring samplers and
   town_margins_clothed went onto the spatial index and their leaked loop names left).
   2026-08-29, feature 146 - one row (0232) when `village_cluster_compact`'s and the dispersed
   arm's residue was removed: three checks had been retired under 141 and their computations left
   standing, so `free`, `writes` and `needs` all shed the names those computations leaked.
   2026-08-29, feature 146 - FOURTEEN rows deleted (0097-0102, 0123-0126, 0128-0131) when the
   `wells_troughs_rails_clear_of_each_other` and `paddy_fan_gapless` derivations were removed. Both
   checks went under 141 and both left their whole derivation behind - a pairwise quad comparison and
   a grid scan of every paddy, running on every gate and read by nothing. A DELETION is the one edit
   the oracle cannot catch drifting, so it is spelled out here: those segments no longer exist.
   2026-08-29, feature 158 - TWENTY-FIVE rows deleted. Nineteen went with the four bridge checks the
   audit retired (`bridges_align_with_their_way`, `bridges_seat_on_water`, `bridges_span_their_water`,
   `bridges_clear_of_houses`): 0334-0338 and 0341-0344 in 06a, 0360-0363 in 06b, 0416-0419 in 07a -
   the four emitters plus the derivation subgraph that fed nothing else, including 0338's
   ways x waters double loop. The other six (0187, 0285.008, 0285.024, 0286.000, 0286.007, 0286.008)
   were ALREADY dead before this feature and are a defect fixed where it was found (Principle XIV):
   each computes a value that no surviving segment declares as an input, so the gate has been running
   them on every map for nothing. The cut was proved CLOSED before it was made - no surviving segment
   reads a name that only a deleted segment writes.
2. Order: the fixture's order is a subsequence of the derived order - the execution contract.
3. Structural invariants: literal-return shape, unique keys, needs within free, META_CHECKS.
4. Fire-proofs: every guard demonstrably fails on a synthetic violation (a checker never seen
   failing is not a check - same doctrine as tests/check_village/test_surface.py).
5. The cache is faithful (round-trip identical) and failure-soft (corruption -> re-derive).
"""

import json
from pathlib import Path

import pytest

from l7r.diagram import check_village
from l7r.diagram.check_village import registry as reg
from l7r.diagram.check_village.registry_analysis import _DerivationError, _derive_fields
from tests._scope import EXHAUSTIVE

HERE = Path(__file__).resolve().parent
FIXTURE = json.loads((HERE.parent / "fixtures" / "registry_legacy_rows.json").read_text())

FIELDS = ("free", "writes", "checks", "needs", "meta", "always")


def _diff_rows(fixture_rows: list[dict], derived_by_name: dict[str, reg._GateSeg]) -> list[tuple[str, str]]:
    """(segment, field) for every divergence between fixture and derived - including a fixture
    segment the derivation lost entirely (field 'missing'). The equality oracle's engine."""
    out: list[tuple[str, str]] = []
    for row in fixture_rows:
        seg = derived_by_name.get(row["name"])
        if seg is None:
            out.append((row["name"], "missing"))
            continue
        for f in FIELDS:
            want = tuple(row[f]) if isinstance(row[f], list) else row[f]
            if getattr(seg, f) != want:
                out.append((row["name"], f))
    return out


def _by_name() -> dict[str, reg._GateSeg]:
    return {r.fn.__name__: r for r in reg.GATE_SEGMENTS}


def test_derived_rows_equal_frozen_legacy_fixture():
    assert _diff_rows(FIXTURE["rows"], _by_name()) == []


def test_meta_checks_equal_frozen_fixture():
    assert sorted(reg.META_CHECKS) == FIXTURE["meta_checks"]


def test_fixture_order_is_subsequence_of_derived_order():
    derived = [r.fn.__name__ for r in reg.GATE_SEGMENTS]
    it = iter(derived)
    missing = [row["name"] for row in FIXTURE["rows"] if row["name"] not in it]
    assert missing == [], f"fixture order not preserved at {missing[:3]}"


def test_structural_invariants():
    names = [r.fn.__name__ for r in reg.GATE_SEGMENTS]
    assert len(names) == len(set(names))
    for r in reg.GATE_SEGMENTS:
        assert set(r.needs) <= set(r.free), r.fn.__name__
    assert frozenset(c for r in reg.GATE_SEGMENTS if r.meta for c in r.checks) == reg.META_CHECKS
    assert len(reg._SEG_DEPS) == len(reg.GATE_SEGMENTS)
    assert all(d < i for i, deps in enumerate(reg._SEG_DEPS) for d in deps)


def test_package_surface_unchanged():
    assert check_village.GATE_SEGMENTS is reg.GATE_SEGMENTS
    assert check_village.META_CHECKS is reg.META_CHECKS


# ---- fire-proofs: each guard fails on a synthetic violation --------------------------------


def test_equality_guard_fires_on_flipped_meta_naming_segment_and_field():
    by_name = _by_name()
    victim = FIXTURE["rows"][0]["name"]
    by_name[victim] = by_name[victim]._replace(meta=not by_name[victim].meta)
    assert (victim, "meta") in _diff_rows(FIXTURE["rows"], by_name)


def test_equality_guard_fires_on_dropped_needs_name():
    by_name = _by_name()
    victim = next(r for r in reg.GATE_SEGMENTS if len(r.needs) > 1).fn.__name__
    by_name[victim] = by_name[victim]._replace(needs=by_name[victim].needs[1:])
    assert (victim, "needs") in _diff_rows(FIXTURE["rows"], by_name)


def test_equality_guard_fires_on_missing_segment():
    by_name = _by_name()
    victim = FIXTURE["rows"][-1]["name"]
    del by_name[victim]
    assert (victim, "missing") in _diff_rows(FIXTURE["rows"], by_name)


def test_order_guard_fires_on_swapped_placement_anchors():
    a, b = "_seg_0600__comb_floor_ends_at_the_collector", "_seg_0595__paddy_bunds_clear_the_supply_channels"
    swapped = dict(reg._PLACEMENTS)
    swapped[a], swapped[b] = swapped[b], swapped[a]
    names = {r.fn.__name__ for r in reg.GATE_SEGMENTS}
    # Since feature 141 retired the one independently-anchored placement (0596), every remaining entry hangs off
    # 0595's chain, so a swap either reorders the chain or closes it into a cycle - the guard fires either way.
    try:
        assert reg._ordered_names(names, swapped) != [r.fn.__name__ for r in reg.GATE_SEGMENTS]
    except _DerivationError as err:
        assert "cycle" in str(err) or "resolve" in str(err)


def test_order_guard_fires_on_stale_placement_entry():
    stale = dict(reg._PLACEMENTS)
    stale["_seg_9999__long_gone"] = "_seg_0317__dry_plot_furrows_vary"
    with pytest.raises(_DerivationError, match="names no live segment"):
        reg._ordered_names({r.fn.__name__ for r in reg.GATE_SEGMENTS}, stale)


def test_order_guard_fires_on_missing_anchor():
    broken = dict(reg._PLACEMENTS)
    broken["_seg_0600__comb_floor_ends_at_the_collector"] = "_seg_9999__long_gone"
    with pytest.raises(_DerivationError, match="anchor"):
        reg._ordered_names({r.fn.__name__ for r in reg.GATE_SEGMENTS}, broken)


def test_order_guard_fires_on_placement_cycle():
    names = {"_seg_0001__a", "_seg_0002__b", "_seg_0003__c"}
    cyclic = {"_seg_0002__b": "_seg_0003__c", "_seg_0003__c": "_seg_0002__b"}
    with pytest.raises(_DerivationError, match="chain"):
        reg._ordered_names(names, cyclic)


def test_order_guard_fires_on_duplicate_numeric_key():
    with pytest.raises(_DerivationError, match="duplicate numeric key"):
        reg._ordered_names({"_seg_0001__a", "_seg_0001__b"}, {})


def test_numeric_key_rejects_unkeyed_name():
    with pytest.raises(_DerivationError, match="numeric key"):
        reg._numeric_key("_seg_nokey__x")


def test_derive_guard_fires_on_stale_needs_override():
    names = {r.fn.__name__ for r in reg.GATE_SEGMENTS}
    orig = reg._NEEDS_OVERRIDES
    try:
        reg._NEEDS_OVERRIDES = {**orig, "_seg_9999__long_gone": ("M",)}
        with pytest.raises(_DerivationError, match="override"):
            reg._derive_rows(names)
    finally:
        reg._NEEDS_OVERRIDES = orig


def test_derive_guard_fires_on_override_outside_free():
    names = {r.fn.__name__ for r in reg.GATE_SEGMENTS}
    orig = reg._NEEDS_OVERRIDES
    try:
        reg._NEEDS_OVERRIDES = {**orig, "_seg_0324_500__comb_supply_commands_both_flanks": ("not_a_param",)}
        with pytest.raises(_DerivationError, match="subset"):
            reg._derive_rows(names)
    finally:
        reg._NEEDS_OVERRIDES = orig


def test_dropping_the_needs_override_diverges_from_the_fixture():
    """The 0324_500 override is load-bearing: without it the derived needs is the conservative
    superset and the fixture oracle catches the divergence (research.md R5)."""
    fields = reg._cached_fields(reg._source_key()) or _derive_fields(reg._PKG_DIR)  # the cache is the same fields when its key matches (T19)
    derived = fields["_seg_0324_500__comb_supply_commands_both_flanks"].needs
    frozen = next(tuple(r["needs"]) for r in FIXTURE["rows"] if r["name"] == "_seg_0324_500__comb_supply_commands_both_flanks")
    assert derived != frozen
    assert set(frozen) < set(derived)


def test_segment_shape_guard_fires_on_nonliteral_return(tmp_path):
    bad = tmp_path / "segments_99_bad.py"
    bad.write_text("def _seg_9998__bad(*, check=None):\n    names = ('x',)\n    return _kept(locals(), names)\n")
    with pytest.raises(_DerivationError, match="literal"):
        _derive_fields(tmp_path)


def test_segment_shape_guard_fires_on_missing_kept_return(tmp_path):
    bad = tmp_path / "segments_99_bad.py"
    bad.write_text("def _seg_9998__bad(*, check=None):\n    return {}\n")
    with pytest.raises(_DerivationError, match="_kept"):
        _derive_fields(tmp_path)


def test_segment_shape_guard_fires_on_nonstring_kept_names(tmp_path):
    bad = tmp_path / "segments_99_bad.py"
    bad.write_text("def _seg_9998__bad(*, check=None):\n    return _kept(locals(), (1,))\n")
    with pytest.raises(_DerivationError, match="strings"):
        _derive_fields(tmp_path)


def test_derive_guard_fires_on_duplicate_segment_def(tmp_path):
    src = "def _seg_9998__dup(*, check=None):\n    return _kept(locals(), ())\n"
    (tmp_path / "segments_98_a.py").write_text(src)
    (tmp_path / "segments_99_b.py").write_text(src)
    with pytest.raises(_DerivationError, match="duplicate segment name"):
        _derive_fields(tmp_path)


# ---- cache ---------------------------------------------------------------------------------


@pytest.mark.skipif(
    not EXHAUSTIVE,
    reason="derives the registry from the AST to PROVE the cache faithful (~2.5 s); the proof runs under EXHAUSTIVE=1 and at every gate that sets it (GM 2026-08-26, T20) - last exhaustive green 2026-08-26",
)
def test_cache_round_trip_and_failure_soft(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_CACHE_PATH", tmp_path / "sub" / "registry_rows.json")
    names = {r.fn.__name__ for r in reg.GATE_SEGMENTS}
    rows = reg._derive_rows(names, fresh=True)  # the proof must derive, not read the cache it is proving
    # A ROUND TRIP NEEDS ROWS, NOT ALL 1,371 OF THEM (feature 135, third pass): the derivation is ~2 s and this
    # test is about store/load/staleness, so the round trip below runs on ten rows; the full-size derivation
    # still happens once above (the disagreement guard in `_derive_rows` needs the whole name set) and
    # `test_cached_rows_rebuild_identical_registry` proves the full rebuild at the gate.
    rows = rows[:10]
    names = {r["name"] for r in rows}
    key = reg._source_key()
    assert reg._load_cached(key, names) is None  # cold: no file yet
    reg._store_cache(key, rows)
    assert reg._load_cached(key, names) == rows  # warm: identical rows
    assert reg._load_cached("other-key", names) is None  # stale key
    assert reg._load_cached(key, names - {rows[0]["name"]}) is None  # segment set moved
    reg._CACHE_PATH.write_text("{ not json")
    assert reg._load_cached(key, names) is None  # corrupt -> derive live


@pytest.mark.skipif(
    not EXHAUSTIVE,
    reason="derives the registry from the AST to PROVE the cache faithful (~2.5 s); the proof runs under EXHAUSTIVE=1 and at every gate that sets it (GM 2026-08-26, T20) - last exhaustive green 2026-08-26",
)
def test_cached_rows_rebuild_identical_registry():
    rows = reg._derive_rows({r.fn.__name__ for r in reg.GATE_SEGMENTS}, fresh=True)
    rebuilt = tuple(reg._row(d, reg._fns) for d in rows)
    assert rebuilt == reg.GATE_SEGMENTS


def test_cache_store_is_failure_soft_when_unwritable(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(reg, "_CACHE_PATH", tmp_path / "blocked" / "cache.json")
    (tmp_path / "blocked").write_text("a file where the cache dir should be")
    with caplog.at_level("WARNING"):
        reg._store_cache("k", [])
    assert "not written" in caplog.text


@pytest.mark.skipif(not EXHAUSTIVE, reason="a forced cache miss derives from the AST (~1.6 s) to prove the miss path; under EXHAUSTIVE=1 (GM 2026-08-26, T20) - last exhaustive green 2026-08-26")
def test_assemble_derives_on_cache_miss_and_loads_on_hit(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_CACHE_PATH", tmp_path / "cache.json")
    names = {r.fn.__name__ for r in reg.GATE_SEGMENTS}
    cold = reg._assemble(names)  # miss: derive + store
    warm = reg._assemble(names)  # hit: load
    assert cold == warm
    assert (tmp_path / "cache.json").exists()


def test_cached_fields_is_failure_soft(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    import json

    from l7r.diagram.check_village import registry as r

    missing = tmp_path / "rows.json"
    monkeypatch.setattr(r, "_CACHE_PATH", missing)
    assert r._cached_fields("k") is None  # OSError
    missing.write_text(json.dumps({"key": "other", "rows": []}))
    assert r._cached_fields("k") is None  # a stale key
