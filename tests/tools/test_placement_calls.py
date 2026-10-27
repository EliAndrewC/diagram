"""`tools/placement_calls.py` (feature 434): the placement-stages page's counts - the reference hamlet's in each heading and in
the table that ends the page, each stage row opening onto its steps and its own work; another map type beside a stage where
it spent more calls there or holds a stage the reference lacks; a dash where nothing holds it; no time anywhere."""

from pathlib import Path

from l7r.diagram.tools import placement_calls as pcl
from l7r.diagram.tools.perf_snapshot import REFERENCE
from l7r.diagram.tools.phase_calls import type_key

REF = type_key(REFERENCE)
RECORD = {
    REF: {
        "seed": 39,
        "households": 40,
        "date": "2026-10-27",
        "total": 1000,
        "stages": {
            "field": {"calls": 600, "own": 100, "steps": {"a.b.fit_field": 450, "a.b.net_acres": 50}},
            "waterward": {"calls": 2, "own": 2, "steps": {}},
        },
    },
    "nucleated/polder/offmap": {
        "seed": 4,
        "households": 40,
        "date": "2026-10-27",
        "total": 2000,
        "stages": {
            "field": {"calls": 500, "own": 500, "steps": {}},
            "waterward": {"calls": 300, "own": 300, "steps": {}},
            "pond_stock": {"calls": 40, "own": 40, "steps": {}},
        },
    },
}
STAGES = [
    (2, "stage_field", "The field", [("a.b.fit_field", "fit_field"), ("a.b.net_acres", "net_acres")]),
    (5, "stage_waterward", "The reed fringe", []),
    (9, "stage_pond_stock", "Pig sties", []),
    (23, "stage_labels", "The labels", []),
]


def test_a_heading_carries_the_references_calls_and_another_type_only_where_it_spent_more() -> None:
    assert "600 calls &middot; 60.0%" in pcl.heading(RECORD, "stage_field") and "polder" not in pcl.heading(RECORD, "stage_field")
    ww = pcl.heading(RECORD, "stage_waterward")
    assert "2 calls &middot; 0.2%" in ww and "nucleated/polder/offmap: 300 (15.0%)" in ww, "the polder beside, never in place"
    stock = pcl.heading(RECORD, "stage_pond_stock")
    assert stock.startswith(f'<span class="calls">{pcl.DASH} calls') and "40 (2.0%)" in stock, "the reference's dash, the polder beside"
    assert pcl.heading(RECORD, "stage_labels") == f'<span class="calls">{pcl.DASH} calls</span>', "nothing holds it: a dash"
    assert pcl.heading({}, "stage_field") == f'<span class="calls">{pcl.DASH} calls</span>'


def test_the_table_opens_each_stage_onto_its_steps_and_own_work() -> None:
    html = "\n".join(pcl.section(RECORD, STAGES))
    assert html.startswith('<section class="stage" id="calls">') and "<script>" in html
    assert '<tr class="stage-row" data-stage="s02"><td>02</td><td>The field</td><td>600</td><td></td><td>60.0%</td></tr>' in html
    assert '<tr class="step-row" data-of="s02" hidden><td></td><td>fit_field</td><td>450</td><td>75.0%</td><td>45.0%</td></tr>' in html
    assert "(the stage&#x27;s own work)</td><td>100</td><td>16.7%</td><td>10.0%</td>" in html
    assert '<tr class="stage-row"><td>23</td><td>The labels</td><td>' + pcl.DASH in html and 'data-of="s23"' not in html
    assert "1,000</td><td></td><td>100%" in html, "the total row is the reference's"
    assert " s<" not in html and "seconds" not in html, "no time anywhere"
    assert pcl.section({}, STAGES)[-1] == "</section>"


def test_the_record_loads_or_is_empty(tmp_path: Path) -> None:
    assert pcl.load(str(tmp_path / "none.json")) == {}
    p = tmp_path / "rec.json"
    p.write_text('{"x": {"total": 1}}')
    assert pcl.load(str(p)) == {"x": {"total": 1}}
