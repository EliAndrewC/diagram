"""Feature 284 (FR-004): the field's size search carves the largest fan only when two carves show the fan saturating, and a
fan that grows as it should never has its largest size carved."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from l7r.diagram.hamletgen.water import fit as F


def _plan() -> SimpleNamespace:
    return SimpleNamespace(
        W=2000.0,
        H=2000.0,
        down_deg=90.0,
        offtakes_a=(0.5,),
        offtakes_b=(0.5,),
        grain_drift=0.0,
        head_deg=None,
        head_lead=90.0,
        target_acres=20.0,
        ftpx=1.0,
        brook_side=0,
        fan_aspect=1.0,
    )


def _roll(monkeypatch: pytest.MonkeyPatch, acres_at) -> list[float]:
    ks: list[float] = []

    class Carve:
        def __init__(self, k: float) -> None:
            self.k, self.net = k, {"plots": [], "channels": []}

        def planted_area(self) -> float:
            return acres_at(self.k) * F.SQ_FT_PER_ACRE

    def carve_comb(W, H, sluice, seed, **kw):
        k = kw["field_fall"] / F.REF_FIELD_FALL * 1.0  # aspect 1.0
        ks.append(k)
        return Carve(k)

    monkeypatch.setattr(F, "carve_comb", carve_comb)
    monkeypatch.setattr(F, "tail_dangles", lambda net: False)
    monkeypatch.setattr(F, "net_bends_acutely", lambda net: False)
    F._fit_at_aspect(_plan(), (0.0, 0.0), 1, 48.0, (26.0, 36.0), 1.0, 0.06, 9)
    return ks


def test_a_fan_that_grows_is_never_carved_at_its_largest(monkeypatch: pytest.MonkeyPatch) -> None:
    ks = _roll(monkeypatch, lambda k: 14.0 * k * k)  # short at k = 1, grows as k ** 2
    assert ks[0] == pytest.approx(1.0) and len(ks) >= 2
    assert max(ks) < 2.2 - 0.01, ks  # the bracket's top was never carved


def test_a_saturating_fan_is_probed_at_its_largest(monkeypatch: pytest.MonkeyPatch) -> None:
    ks = _roll(monkeypatch, lambda k: min(14.0 * k * k, 15.0 + 0.1 * k))  # clamped near 15 acres against 20
    assert max(ks) > 2.2 - 0.01, ks  # the top was probed
    assert len(ks) <= 4, ks  # and the saturated aspect stopped soon after


def test_saturating_needs_a_larger_k_and_a_carved_first_fan() -> None:
    assert F.saturating((1.0, 10.0), (1.2, 10.5)) is True
    assert F.saturating((1.0, 10.0), (1.2, 14.4)) is False
    assert F.saturating((1.2, 10.0), (1.0, 5.0)) is False
    assert F.saturating((1.0, 0.0), (1.2, 5.0)) is False
