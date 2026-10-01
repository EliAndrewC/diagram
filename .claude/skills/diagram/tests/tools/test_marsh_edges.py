"""Feature 294 B2: how ruled a marsh's visible free edge is (`tools/marsh_edges.py`)."""

from __future__ import annotations

import pytest

from l7r.diagram.tools import marsh_edges

pytestmark = pytest.mark.renders  # it renders tiny synthetic id maps on purpose

RULES = {"tol": 3.1, "share": 0.4, "min_len": 300.0, "eps_deg": 1.6, "axis_run": 150.0}
RECT = [(100.0, 100.0), (600.0, 100.0), (600.0, 160.0), (100.0, 160.0)]  # a long strip: each long side 500 ft of 1,120


def _page(marsh: list, extra: str = "") -> str:
    pts = " ".join(f"{x},{y}" for x, y in marsh)
    return (
        '<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 500">'
        '<g class="f f-scrub-and-rough-grazing" data-k="scrub and rough grazing"><rect x="0" y="0" width="700" height="500" fill="#C8C080"/></g>'
        f'<g class="f f-marsh" data-k="marsh"><polygon class="hit" points="{pts}" fill="none" style="pointer-events: fill"/></g>'
        f"{extra}</svg>"
    )


def test_a_ruled_axis_marsh_in_the_scrub_fires_both_rules() -> None:
    """Seeded: the recorded case's shape - a toe marsh laid as an axis-aligned strip meeting the scrub on ruled lines."""
    runs = marsh_edges.free_runs(_page(RECT), [RECT], 1.0)
    assert runs is not None and len(runs[0]) >= 1
    got = marsh_edges.ruled_edges(runs[0], 1.0, RULES)
    assert any("straight run" in g for g in got) and any("screen axis" in g for g in got)


def test_an_edge_beside_another_feature_or_the_frame_is_not_the_marsh_s() -> None:
    dike = '<g class="f f-perimeter-dike" data-k="perimeter dike"><rect x="80" y="80" width="540" height="15" fill="#776655"/></g>'
    runs = marsh_edges.free_runs(_page(RECT, dike), [RECT], 1.0)
    assert runs is not None
    tops = [p for r in runs[0] for p in r if abs(p[1] - 100.0) < 1.0 and 105.0 < p[0] < 595.0]
    assert not tops, "the top edge runs beside the dike: it is the dike's edge"
    framed = [(0.0, 0.0), (700.0, 0.0), (700.0, 500.0), (0.0, 500.0)]
    assert marsh_edges.free_runs(_page(framed), [framed], 1.0) == [[]], "the frame clipping a marsh is no edge of it"


def test_a_waved_edge_passes_and_the_short_cases() -> None:
    wavy = [(100.0 + 10 * k, 100.0 + 30 * ((k % 4) in (1, 2))) for k in range(41)] + [(500.0, 300.0), (100.0, 300.0)]
    assert marsh_edges.axis_run_ft([(0.0, 0.0), (5.0, 3.0)], 1.0, 1.6) == 0.0
    runs = marsh_edges.free_runs(_page(wavy), [wavy], 1.0)
    assert runs is not None
    assert marsh_edges.axis_run_ft([(0.0, 0.0), (10.0, 0.0), (10.0, 5.0)], 1.0, 1.6) == 10.0, "a corner ends the stretch"
    assert marsh_edges.ruled_edges([], 1.0, RULES) == []
    assert marsh_edges.free_runs('<svg id="map"></svg>', [RECT], 1.0) is None


def test_no_renderer_no_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.interactive import raster

    monkeypatch.setattr(raster, "id_map", lambda *_a, **_k: (None, {}))
    assert marsh_edges.free_runs(_page(RECT), [RECT], 1.0) is None
