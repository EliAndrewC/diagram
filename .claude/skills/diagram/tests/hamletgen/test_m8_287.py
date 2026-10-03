"""Feature 287 M8 at the hamlet's placers: the seating's reservations handed to the registry of what stands, the parts laid
at seating held until they are drawn, the view that stops where the reed strip stops, and the connector's last resorts -
each on constructed input including the violating case."""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.hinterland import frame as hframe
from l7r.diagram.hamletgen.homesteads import holds
from l7r.diagram.hamletgen.homesteads.stages import reserve_the_seating
from l7r.diagram.hamletgen.ways import track
from l7r.diagram.settlement import Settlement

from ._builders import a_plan


def _hamlet(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s.standing.strict = True
    return s


# ---- the reed strip reaches the view's edge: the view decided to stop where it stops (water:W43) -------------------------


DIKE = [(800.0, 800.0), (1200.0, 800.0), (1200.0, 1200.0), (800.0, 1200.0)]


def _polder(faces: list[str]) -> Settlement:
    s = Settlement(2400, 2400, seed=4)
    s.meta(name="P", scale="hamlet", ftpx=1, waterward=faces)
    s.M["dikes"] = [{"outline": [list(p) for p in DIKE], "crest": [[790.0, 790.0], [790.0, 1210.0]], "w_min": 10.0, "w_max": 10.0}]
    return s


def test_the_decided_view_stops_where_each_water_facing_strip_stops() -> None:
    """The violating case: the content reaches 400 px west of a west strip 270 px deep, and the band between is all built
    ground, so no extension could reed it. The view is decided with its west edge at the strip's outer edge, and every
    strip reaches it; a strip already reaching an edge of its flank constrains nothing."""
    s = _polder(["W", "E", "N", "S"])
    west = [[520.0, 770.0], [790.0, 770.0], [790.0, 1220.0], [520.0, 1220.0]]
    east = [[1210.0, 770.0], [1480.0, 770.0], [1480.0, 1220.0], [1210.0, 1220.0]]
    north = [[770.0, 520.0], [1220.0, 520.0], [1220.0, 790.0], [770.0, 790.0]]
    south = [[770.0, 1210.0], [1220.0, 1210.0], [1220.0, 1490.0], [770.0, 1490.0]]
    for ring in (west, east, north, south):
        s.M["marshes"].append({"role": "waterside", "poly": ring})
    view = hframe.to_the_strips(s, (100.0, 100.0, 2000.0, 2000.0))
    assert view == (520, 520, 960, 970)
    assert all(hg.frame.strip_reaches_view(m["poly"], view, ["W", "E", "N", "S"]) for m in s.M["marshes"])
    reaching = hframe.to_the_strips(s, (600.0, 100.0, 1500.0, 2000.0))
    assert reaching[0] == 600 and reaching[2] == 880, "the west strip already reaches: only the east edge comes in"
    assert hframe.to_the_strips(Settlement(100, 100, seed=1), (0.0, 0.0, 50.0, 50.0)) == (0.0, 0.0, 50.0, 50.0)
    s.M["marshes"][0]["role"] = "toe"
    s.M["meta"]["waterward"] = ["E"]
    assert hframe.to_the_strips(s, (100.0, 100.0, 2000.0, 2000.0))[0] == 100, "a flank that faces no water keeps its edge"


def test_the_view_takes_in_every_households_reserved_wood() -> None:
    """The copse is planted after the view is decided: a household's seat past it was planted and partitioned off the page
    (cohort 1-60: 8 seats on two maps). The seats' crowns are content the view takes in."""
    s = _hamlet()
    plan = a_plan()
    s.M["houses"].append({"x": 500.0, "y": 500.0, "w": 40.0, "h": 28.0, "rot": 0.0, "wood_share": {"seats": [[1300.0, 90.0]], "r": 11.0}})
    plan.title_pocket = (0.0, 0.0, 0.0, 0.0)
    extras = hframe.frame_extras(s, plan)
    assert (1289.0, 79.0, 1311.0, 101.0) in extras


# ---- the seating's reservations and holds ------------------------------------------------------------------------------


def test_the_seatings_corridors_and_seats_are_kept_off_by_every_later_placer() -> None:
    s = _hamlet()
    s.M["access_corridors"] = [{"pts": [[100.0, 300.0], [400.0, 300.0]], "of": [100.0, 260.0]}, {"pts": [[400.0, 300.0], [400.0, 600.0]]}, {"pts": [[400.0, 600.0], [600.0, 600.0]], "field": True}]
    s.M["access_exit"] = [[600.0, 600.0], [900.0, 600.0]]
    s.M["houses"].append({"x": 100.0, "y": 260.0, "w": 40.0, "h": 28.0, "rot": 0.0, "wood_share": {"seats": [[900.0, 900.0]], "r": 11.0}})
    reserve_the_seating(s)
    res = s.standing.reserved
    assert len(res.corridors) == 4 and res.corridors[1][3] == [100.0, 260.0] and res.corridors[2][3] is None and res.seats == [(900.0, 900.0)]
    well = {"x": 400.0, "y": 450.0, "r": 8, "vr": 12.4}
    assert not s.admits("wells", well), "a wellhead on the tree's second leg"
    assert s.admits("wells", dict(well, x=500.0))
    assert not s.admits("byres", {"x": 750.0, "y": 600.0, "w": 16.0, "h": 11.0, "rot": 0.0}), "a shared shed on the exit strip"
    assert not s.admits("lanes", {"pts": [[850.0, 910.0], [950.0, 910.0]], "w": 3}), "a lane over a household's wood seat"
    assert not s.well_at(400.0, 450.0), "the communal well's placer asks it"


def test_a_corridor_is_reserved_as_the_web_will_draw_it() -> None:
    """Feature 318 (the reference at 40 households, seed 25): squaring a water crossing drops a bend in the water, so the drawn
    tread runs where the reserved one does not. `access.reserve` bars each drawn leg the reserved run lacks and records it
    (`access_drawn`, with the corridor's owner), and `reserve_the_seating` keeps every later placer off it too."""
    from types import SimpleNamespace

    from l7r.diagram.settlement.rolling import access

    s = _hamlet()
    added: list[Any] = []
    barred: list[Any] = []
    s._access = SimpleNamespace(add=lambda a, b: added.append((a, b)), bar=lambda a, b: barred.append((a, b)))  # type: ignore[assignment]
    run = ((100.0, 300.0), (400.0, 360.0), (400.0, 600.0))
    s._corridor_drawn = lambda corridor: [corridor[0], corridor[-1]]  # type: ignore[attr-defined]
    access.reserve(s, run, (100.0, 260.0))
    assert added == [(run[0], run[1]), (run[1], run[2])] and barred == [(run[0], run[2])], "the drawn chord barred, not a corridor"
    assert s.M["access_drawn"] == [{"pts": [[100.0, 300.0], [400.0, 600.0]], "of": [100.0, 260.0]}]
    reserve_the_seating(s)
    assert any(c[3] == [100.0, 260.0] and tuple(c[0]) == (100.0, 300.0) and tuple(c[1]) == (400.0, 600.0) for c in s.standing.reserved.corridors)
    assert not s.admits("wells", {"x": 250.0, "y": 450.0, "r": 8, "vr": 12.4}), "a wellhead on the drawn chord"
    t = _hamlet()
    t._access = s._access  # type: ignore[assignment]
    t._corridor_drawn = lambda corridor: list(corridor)  # type: ignore[attr-defined]
    access.reserve(t, run)
    assert "access_drawn" not in t.M, "drawn as reserved: nothing more to keep"


def test_the_parts_laid_at_seating_stand_until_drawn() -> None:
    s = _hamlet()
    s.M["houses"].append(
        {
            "x": 300.0,
            "y": 300.0,
            "w": 40.0,
            "h": 28.0,
            "rot": 0.0,
            "well_pocket": [360.0, 330.0],
            "fixtures": [{"kind": "privy", "x": 250.0, "y": 300.0, "w": 6.0, "h": 6.0, "box": [250.0, 300.0, 6.0, 6.0]}, {"kind": "persimmon", "x": 1.0, "y": 1.0, "box": [1, 1, 1, 1]}],
        }
    )
    assert holds.hold_laid_parts(s, s.M["houses"]) == 2
    assert not s.admits("lanes", {"pts": [[250.0, 250.0], [250.0, 350.0]], "w": 3}), "the privy stands for the ways laid before it is drawn"
    assert not s.admits("lanes", {"pts": [[360.0, 280.0], [360.0, 380.0]], "w": 3}), "...and the well pocket"
    holds.release_held(s, "wells", 360.0, 330.0)
    holds.release_held(s, "farm_fixtures", s.M["houses"][0]["fixtures"][0])
    holds.release_held(s, "farm_fixtures", {"not": "held"})
    assert s.admits("lanes", {"pts": [[250.0, 250.0], [250.0, 350.0]], "w": 3}) and s.admits("lanes", {"pts": [[360.0, 280.0], [360.0, 380.0]], "w": 3})


# ---- the connector's last resorts --------------------------------------------------------------------------------------


def test_a_gateway_walled_in_by_reserved_seats_leaves_along_the_exit_strip_then_over_a_seat(monkeypatch: pytest.MonkeyPatch) -> None:
    """The dry exit is walled by the seats; where that walls the gateway in, the connector runs out along the exit strip the
    seating reserved and the fill starts at its end; where even that fails, the way out takes the seats in its path and the
    manifest names them (`meta.wood_seats_to_the_connector`) - never no connector."""
    s = _hamlet()
    plan = a_plan()
    s.standing.reserved.reserve_seats([(-100.0, 0.0), (500.0, 500.0)], 22.0, 15.0)
    s.M["access_exit"] = [[50.0, 50.0], [300.0, 50.0]]
    monkeypatch.setattr(track, "route_around", lambda *a: None)  # ...so no swept track, from the gateway or the strip, is drawn
    monkeypatch.setattr(track, "connector_track", lambda plan_, start, **kw: [tuple(start), (-900.0, float(start[1]))])
    calls: list[tuple[float, float]] = []

    def dry(plan_: Any, start: Any, avoid: Any, *a: Any) -> list[tuple[float, float]]:
        calls.append(tuple(start))
        if len(calls) == 1:
            raise track.NoDryExit("walled in by the seats")
        return [tuple(start), (float(start[0]) - 400.0, float(start[1]))]

    monkeypatch.setattr(track, "connector_dry_exit", dry)
    run = track.connector_through(s, plan, [(60.0, 60.0), (-900.0, 60.0)], [], [], [], [])
    assert calls == [(60.0, 60.0), (300.0, 50.0)] and run[2] == (300.0, 50.0)
    assert run[0] == (60.0, 50.0), "its start set back on the strip it stood 10 ft off (`track.on_the_strip`)"
    assert "wood_seats_to_the_connector" not in s.M["meta"]
    calls.clear()

    def walled(plan_: Any, start: Any, avoid: Any, *a: Any) -> list[tuple[float, float]]:
        calls.append(tuple(start))
        if len(calls) < 3:
            raise track.NoDryExit("walled")
        return [(60.0, 0.0), (-400.0, 0.0)]

    monkeypatch.setattr(track, "connector_dry_exit", walled)
    run = track.connector_through(s, plan, [(60.0, 60.0), (-900.0, 60.0)], [], [], [], [])
    assert run == [(60.0, 0.0), (-400.0, 0.0)] and s.M["meta"]["wood_seats_to_the_connector"] == [[-100.0, 0.0]]
    assert s.standing.reserved.seats == [(500.0, 500.0)], "the seat the way out took is given up; the other stands"
    s2 = _hamlet()
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: [(60.0, 0.0), (-400.0, 0.0)])
    assert track.connector_through(s2, plan, [(60.0, 60.0), (-900.0, 60.0)], [], [], [], []) == [(60.0, 0.0), (-400.0, 0.0)]


def test_a_spur_the_registry_refuses_is_recorded_dropped(monkeypatch: pytest.MonkeyPatch) -> None:
    from .ways._builders import _walled_settlement

    s, plan = _walled_settlement()
    plan.seat = hg.seat_cluster(plan)
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: [(1384.0, 700.0), (1600.0, 700.0)])
    monkeypatch.setattr(track, "_thread_the_fabric", lambda s_, plan_, run: run)
    monkeypatch.setattr(track, "spur_cut_at_the_fold", lambda pts, env: (pts, None))
    monkeypatch.setattr(s, "admits_lane", lambda pts, width: False)  # a dry plot or a part on every run the spur could take
    track.stage_track(s, plan)
    assert "overlap matrix refuses the spur" in s.M["meta"]["field_spur_swept"]
    assert not [ln for ln in s.M.get("lanes") or [] if ln.get("spur")]


def test_the_title_pocket_is_never_reserved_over_a_households_wood_or_a_corridor() -> None:
    """The copse refuses a clump inside the title's pocket grown by its radius, so a pocket over a reserved seat took the seat
    (cohort 1-60: 95 of them). The pocket's own predicate refuses such a box."""
    s = _hamlet()
    s.standing.reserved.reserve_seats([(500.0, 500.0)], 22.0, 15.0)
    s.standing.reserved.reserve_corridor((100.0, 900.0), (300.0, 900.0), 7.0)
    assert not hframe.pocket_clear_of_features((400.0, 400.0, 489.5, 600.0), s.M, 0.0), "a seat within a crown of its edge"
    assert hframe.pocket_clear_of_features((400.0, 400.0, 480.0, 600.0), s.M, 0.0)
    assert not hframe.pocket_clear_of_features((150.0, 850.0, 250.0, 950.0), s.M, 0.0), "a corridor through it"


def test_a_connector_swept_over_a_reserved_seat_runs_out_along_the_exit_strip_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cohort seeds 3, 12 and 17: the track swept from the gateway ran its first leg over a household's reserved seat. Before
    any flood fill, the track is swept again from the exit strip's outer end - the strip every seat keeps off - and drawn from
    the gateway along the strip."""
    s = _hamlet()
    plan = a_plan()
    s.standing.reserved.reserve_seats([(20.0, 60.0)], 22.0, 15.0)
    s.M["access_exit"] = [[60.0, 200.0], [60.0, 400.0]]
    monkeypatch.setattr(track, "route_around", lambda poly, path, margin: path)
    monkeypatch.setattr(track, "_thread_the_fabric", lambda s_, plan_, run: run)
    monkeypatch.setattr(track, "connector_track", lambda plan_, start, **kw: [tuple(start), (float(start[0]), 2000.0)])
    monkeypatch.setattr(track, "connector_dry_exit", lambda *a: pytest.fail("no flood fill is needed"))
    run = track.connector_through(s, plan, [(60.0, 60.0), (-900.0, 60.0)], [], [], [], [])
    assert run[0] == (60.0, 60.0) and (60.0, 400.0) in run and run[-1] == (60.0, 2000.0)
    assert track._dedup_run([(0.0, 0.0), (0.0, 0.0), (1.0, 0.0)]) == [(0.0, 0.0), (1.0, 0.0)]
