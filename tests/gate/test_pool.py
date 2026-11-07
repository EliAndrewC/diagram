"""`tests/gate/_pool.py` (feature 215): a shipped spec is read from the pool's map, any other goes to the roll cache.
Feature 219: the gate rolls no spec of its own, so the roll-cache branches are proved on stubs here."""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from tests import rolls
from tests.gate import _pool


@pytest.fixture(autouse=True)
def _integrated(monkeypatch: pytest.MonkeyPatch) -> None:
    """These tests prove the helper's branches on stubs, as at `integrated`; the rust-only skip has its own test below."""
    monkeypatch.setattr(_pool, "python_maps_off", lambda: False)


def test_at_rust_only_a_pool_map_or_a_roll_is_skipped_never_rolled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 444 FR-023, the GM 2026-11-07: at `rust-only` no Python map is rolled or read; the test that asks one is skipped."""
    monkeypatch.setattr(_pool, "python_maps_off", lambda: True)
    monkeypatch.setattr(_pool.gencache, "gate_obtain", lambda g: (_ for _ in ()).throw(AssertionError("rolled")))
    monkeypatch.setattr(rollcache, "hamlet", lambda s: (_ for _ in ()).throw(AssertionError("rolled")))
    for ask in (lambda: _pool.obtain_full("pool/x/x.gen.py"), lambda: _pool.rolled_map(hg.HamletSpec(name="Probe", seed=3, households=10))):
        with pytest.raises(pytest.skip.Exception, match="rust-only"):
            ask()


def test_a_spec_the_pool_does_not_carry_goes_to_the_roll_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = hg.HamletSpec(name="Probe", seed=3, households=10)
    assert _pool.gen_of(spec) is None and _pool.gen_of(rolls.REFERENCE) is not None
    monkeypatch.setattr(rollcache, "hamlet", lambda s: ("plan", {"M": s.seed}))
    monkeypatch.setattr(rollcache, "report", lambda s: ("report", "HIT"))
    assert _pool.rolled_map(spec) == ("plan", {"M": 3})
    assert _pool.rolled_report(spec) == "report"


def test_a_pool_map_read_twice_by_one_test_is_obtained_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 417 T44 (the round arbiter's tooling fix on ask:417-T31-C2-regression): `rolled_map` then `rolled_report` read a
    stale pool map twice in one test, and each read regenerated it - the roll census then refused an otherwise-green landing.
    The second read is served what the first obtained."""
    calls: list[str] = []
    monkeypatch.setattr(_pool.gencache, "gate_obtain", lambda g: (calls.append(g), (f"/tmp/{g}.json", "REGENERATED", 1.0))[1])
    monkeypatch.setattr(_pool, "refresh_census", lambda m: False)
    first = _pool.obtain_full("pool/x/x.gen.py")
    again = _pool.obtain_full("pool/x/x.gen.py")
    assert calls == ["pool/x/x.gen.py"], "the map is rolled once"
    assert first[0] == again[0] and again[1] == "CACHED"


def test_a_refused_pool_map_is_rolled_once_a_run_and_its_refusal_re_raised(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # noqa: ANN001
    """Feature 444 T16's gate: Sawada's roll, refused until a later stage's port (a strict xfail), wrote no manifest to share, so
    its twelve readers each rolled it again and the census failed the gate. The refusal is shared across the run's workers."""
    calls: list[str] = []

    def refuse(g: str) -> tuple[str, str, float]:
        calls.append(g)
        raise ValueError("SeatRefused: no seat")

    monkeypatch.setattr(_pool.gencache, "gate_obtain", refuse)
    monkeypatch.setattr(rollcache, "_run_share_path", lambda key: str(tmp_path / "share" / key[0]))
    for _ in range(2):
        _pool._OBTAINED.clear()  # a fresh test, as `tests/conftest.py` empties it
        with pytest.raises(Exception, match="SeatRefused"):
            _pool.obtain_full("pool/s/s.gen.py")
    assert calls == ["pool/s/s.gen.py"], "rolled once; the second reader is handed the first one's refusal"
