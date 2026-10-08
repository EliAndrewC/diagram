"""Feature 287, water W32: the fit's legality commands both flanks of the fork (`flanks_commanded`)."""

from __future__ import annotations

from l7r.diagram.hamletgen.water.fit import flanks_commanded


def _net(reach_b: float, extent_b: float = 400.0) -> dict:
    # the fall runs +y (down_deg 90), so the cross axis is x: flank A to the -x side of the fork at x=0, flank B to the +x
    plots = [{"poly": [(-400.0, 100.0), (-10.0, 100.0), (-10.0, 120.0)]}, {"poly": [(10.0, 100.0), (extent_b, 100.0), (10.0, 120.0)]}]
    channels = [{"role": "main", "pts": [(0.0, 0.0), (-300.0, 50.0)]}, {"role": "main", "pts": [(0.0, 0.0), (reach_b, 50.0)]}, {"role": "drain", "pts": [(0.0, 0.0), (900.0, 0.0)]}]
    return {"fork": (0.0, 0.0), "plots": plots, "channels": channels}


def test_a_flank_whose_supply_is_trimmed_short_is_uncommanded() -> None:
    """Canal B trimmed to 60 ft on a wide fan: its flank's 400 ft of plots are owed 120 ft of supply - illegal. The drain's
    reach counts for nothing."""
    assert not flanks_commanded(_net(60.0), 90.0)
    assert flanks_commanded(_net(130.0), 90.0)


def test_a_one_sided_fan_commands_no_second_flank_and_a_net_with_no_fork_is_not_judged() -> None:
    assert not flanks_commanded(_net(130.0, extent_b=120.0), 90.0), "120 ft of plots on the B side: no flank there"
    assert flanks_commanded({"plots": [], "channels": []}, 90.0)


# ---- the fit refuses what it cannot bring inside the rules (feature 287, FR-005: water W32 and the acreage band) ------------


def _fake_fit(monkeypatch, *, ceiling: float = 10.0, net_of=None, finish_scale=None, acres_of=None):  # type: ignore[no-untyped-def]
    """Stand the carve and the finish in: a fan whose acreage is 9 k^2 up to `ceiling`, whose net is `net_of(aspect)` (a
    commanded fan by default) - the fit's own predicates judge it. Returns the carves and the finishes it saw."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.water import fit as w
    from l7r.diagram.sitegen.geom import SQ_FT_PER_ACRE

    carves: list[tuple[float, float]] = []
    finishes: list[float] = []

    def carve(W: float, H: float, sluice: object, seed: int, **kw: object) -> SimpleNamespace:
        fall, canal = float(kw["field_fall"]) / w.REF_FIELD_FALL, float(kw["canal_a_len"][0]) / w.REF_CANAL_A[0]  # type: ignore[arg-type, index]
        k, aspect = (fall * canal) ** 0.5, round((canal / fall) ** 0.5, 2)  # the fall is k / aspect, the canal k * aspect
        carves.append((aspect, k))
        acres = acres_of(k) if acres_of else min(9.0 * k**2, ceiling)
        net = dict(net_of(aspect) if net_of else _net(130.0))
        net.update(acres=acres, aspect=aspect)
        return SimpleNamespace(net=net, region=SimpleNamespace(area=acres * SQ_FT_PER_ACRE))

    def finish(c: SimpleNamespace) -> dict:
        finishes.append(c.net["aspect"])
        net = dict(c.net)
        if finish_scale:
            net["acres"] *= finish_scale(c.net["aspect"])
        return net

    monkeypatch.setattr(w, "carve_comb", carve)
    monkeypatch.setattr(w, "finish_comb", finish)
    monkeypatch.setattr(w, "tail_dangles", lambda net: False)
    monkeypatch.setattr(w, "net_bends_acutely", lambda net: False)
    monkeypatch.setattr(w, "net_acres", lambda net, ftpx: net["acres"])
    return carves, finishes


def _plan(target: float):  # type: ignore[no-untyped-def]
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.consts import FAN_ASPECTS

    return SimpleNamespace(
        W=1000.0, H=1000.0, down_deg=90.0, offtakes_a=(), offtakes_b=(), grain_drift=0.0, fan_aspect=FAN_ASPECTS[0], target_acres=target, ftpx=1.0, head_deg=55.0, head_lead=105.0, brook_side=1
    )


def test_a_fan_no_aspect_can_bring_into_its_acreage_band_is_refused_after_every_aspect_is_searched_in_full(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The violating case: the envelope clamps every aspect at 10 acres against a 16-acre need (38% short). The fit used to
    keep the closest miss; it now searches every aspect in full, without the probe, and then refuses the site by name."""
    import pytest

    from l7r.diagram.hamletgen.water.fit import FieldRefused, fit_field

    carves, finishes = _fake_fit(monkeypatch)
    with pytest.raises(FieldRefused, match="16.0 acres within 15%"):
        fit_field(_plan(16.0), (0.0, 0.0), 1, 20.0, (30.0, 40.0))  # type: ignore[arg-type]
    per_aspect: dict[float, int] = {}
    for a, _k in carves:
        per_aspect[a] = per_aspect.get(a, 0) + 1
    assert len(per_aspect) == 5 and min(per_aspect.values()) > 3, per_aspect  # the widened search: every aspect past its probe
    assert not finishes, "no fan outside the band is ever finished"


def test_a_fan_whose_supply_leaves_a_flank_uncommanded_is_never_returned(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Water W32 on the violating case: at the rolled aspect canal B is trimmed to 60 ft on a 400 ft flank - the fit takes
    the next aspect's commanded fan; where every aspect leaves the flank uncommanded, the site is refused."""
    import pytest

    from l7r.diagram.hamletgen.consts import FAN_ASPECTS
    from l7r.diagram.hamletgen.water.fit import FieldRefused, fan_legal, fit_field

    rolled = round(FAN_ASPECTS[0], 2)
    _fake_fit(monkeypatch, net_of=lambda a: _net(60.0) if a == rolled else _net(130.0))
    net = fit_field(_plan(9.0), (0.0, 0.0), 1, 20.0, (30.0, 40.0))  # type: ignore[arg-type]
    assert net["aspect"] != rolled and fan_legal(net, 90.0)
    _fake_fit(monkeypatch, net_of=lambda a: _net(60.0))
    with pytest.raises(FieldRefused):
        fit_field(_plan(9.0), (0.0, 0.0), 1, 20.0, (30.0, 40.0))  # type: ignore[arg-type]


def test_a_fan_the_finish_moves_out_of_its_band_is_replaced_by_the_widened_search(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The band is judged on the FINISHED net: where the finish of the winner lands outside it, the next aspect's fan is
    finished and returned - never the finished miss."""
    from l7r.diagram.hamletgen.consts import FAN_ASPECTS
    from l7r.diagram.hamletgen.water.fit import field_acres_in_band, fit_field

    rolled = round(FAN_ASPECTS[0], 2)
    _carves, finishes = _fake_fit(monkeypatch, finish_scale=lambda a: 0.5 if a == rolled else 1.0)
    net = fit_field(_plan(9.0), (0.0, 0.0), 1, 20.0, (30.0, 40.0))  # type: ignore[arg-type]
    assert finishes[0] == rolled and net["aspect"] != rolled
    assert field_acres_in_band(net["acres"], 9.0) and not field_acres_in_band(4.5, 9.0)


def test_the_best_aspect_searched_in_full_replaces_what_the_probe_kept_when_it_lands_better(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """A fan whose acreage peaks inside the bracket (10.8 acres at k = 1.6) and falls away at its top: the probe - k = 1,
    then the bracket's top - keeps 9 acres at every aspect, 18% short of 11 and outside the band; the rolled aspect's full
    search finds the peak, which lands inside it and is the fan returned."""
    from l7r.diagram.hamletgen.water.fit import field_acres_in_band, fit_field

    _fake_fit(monkeypatch, acres_of=lambda k: 10.8 - 7.0 * (k - 1.6) ** 2)
    net = fit_field(_plan(11.0), (0.0, 0.0), 1, 20.0, (30.0, 40.0))  # type: ignore[arg-type]
    assert field_acres_in_band(net["acres"], 11.0) and net["acres"] > 9.5
