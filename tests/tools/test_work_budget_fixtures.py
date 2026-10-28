"""The `work-budget` agent's two fixtures and its bundles (feature 443 T05, plan D9-D11; FR-008, FR-009, SC-005).

Before its first real use the agent was dispatched once on each fixture (`tests/fixtures/work-budget/`); its first line is
`verdict.txt` beside the derivation. The design the GM approved (2026-10-28) requires today's homestead seat funnel ruled LOOSE or
OVER and a textbook grid-indexed placer ruled SOUND or WITHIN: an agent that passed the funnel, or refused the placer, does not
bite on the right thing.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pytest

from tests._scripts import script

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "tests" / "fixtures" / "work-budget"
AGENT = REPO / ".claude" / "agents" / "work-budget.md"

_spec = importlib.util.spec_from_file_location("work_budget_bundle", script("work_budget_bundle"))
assert _spec is not None and _spec.loader is not None
wbb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wbb)


def _verdict(name: str) -> str:
    return (FIX / name / "verdict.txt").read_text(encoding="utf-8").split()[0].strip("*:`").upper()


def test_the_funnel_is_ruled_loose_or_over_and_the_grid_placer_sound_or_within() -> None:
    """The funnel's ruling is its MODE AUDIT one - today's homesteads code and counters against the rubric's reference budget
    (`funnel/budget.json`): OVER is an audit verdict, and the MODE 1 ruling of 2026-10-28 held the design's literal set. Its MODE
    BUDGET rulings (UNDERIVED, twice) are kept beside it, `verdict-budget-*.txt`."""
    assert _verdict("funnel") in {"LOOSE", "OVER"}, "today's seat funnel must not pass"
    assert _verdict("grid-placer") in {"SOUND", "WITHIN"}, "a textbook indexed placer must not be refused"


def test_the_grid_placer_places_its_discs_apart_within_its_derived_count() -> None:
    """The fixture's code does what its derivation says: every pair at least `d` apart, nothing on blocked ground, and at most
    17 operations per disc placed (9 lookups and 8 marks), plus the blocked sites' flags and lookups, each once."""
    ns: dict = {}
    exec((FIX / "grid-placer" / "placer.py.txt").read_text(encoding="utf-8"), ns)  # noqa: S102 - the fixture's own text
    d, blocked = 10.0, [(0.0, 0.0, 30.0, 30.0)]
    placed, ops = ns["place"](100.0, 100.0, 60, d, blocked, seed=3)
    assert len(placed) == 60
    assert all(math.dist(a, b) >= d for i, a in enumerate(placed) for b in placed[i + 1 :])
    assert not any(x <= 30 and y <= 30 for x, y in placed)
    blocked_sites = (30 // 5 + 1) ** 2  # the d / 2 lattice's sites on the blocked square
    assert ops <= 60 * 17 + 2 * blocked_sites


def test_the_agent_asks_the_designs_questions() -> None:
    text = AGENT.read_text(encoding="utf-8")
    for q in ("Is each factor derived?", "Is there a standard, cheaper algorithm?", "Is any factor padded?", "Is each figure read at its source's size and unit?"):
        assert q in text, f"MODE BUDGET asks: {q}"
    for q in ("Are the counters within budget?", "Does a counter cover every inner loop (S5)?", "Is anything placed and then repaired (S4)?", "Is the growth linear (S6)?"):
        assert q in text, f"MODE AUDIT asks: {q}"
    for v in ("SOUND", "LOOSE", "UNDERIVED", "WITHIN", "OVER", "UNCOUNTED"):
        assert f"**{v}**" in text


@pytest.mark.parametrize(
    ("text", "why"),
    [
        ("## Contract\n\nx\n\n```python\nfor s in seats: pass\n```\n", "a fenced block of Python"),
        ("## Contract\n\nreads l7r/diagram/hamletgen/plan.py\n", "a path under l7r/"),
        ("## Contract\n\nx\n\ntoday it takes 180k calls per house\n", "a current count"),
        ("## Contract\n\nx\n\nops: 4000\n", "a current count"),
    ],
)
def test_a_budget_bundle_holding_code_or_todays_counts_is_refused(tmp_path: Path, text: str, why: str) -> None:
    (tmp_path / "d.md").write_text(text)
    rc, msg = wbb.budget_bundle(REPO, "web", str(tmp_path / "d.md"), tmp_path / "out")
    assert rc == 1 and why in msg and not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    ("edit", "why"),
    [
        (lambda t: t.replace("| factor | scope | value | reason | worst case |", "| factor | value | reason |"), "the columns factor | scope | value | reason | worst case"),
        (lambda t: t.replace("| marks per disc placed | per item |", "| marks per disc placed | per disc |"), "its scope is one of per item, over the run, once - not `per disc`"),
        (lambda t: t.replace("| a disc away from the edge, all 8 marked |", "|  |"), "`marks per disc placed`: every column filled"),
        (lambda t: t.replace("- incremental update: used", "- incremental updates: used"), "a line for `incremental update`"),
        (lambda t: t.replace("- priority queue: not used - no candidate is ranked; each is taken or refused on its own flag", "- priority queue:"), "a line for `priority queue`"),
        (lambda t: t.split("## The count, factor by factor")[0], "the `## The count, factor by factor` table"),
        (lambda t: t.replace("- Keeps: no two discs closer than `d`; every disc on open ground.", "- Keeps:"), "its `Keeps:` line, filled"),
        (lambda t: t.replace("- Reads: a rectangle", "- Takes: a rectangle"), "its `Reads:` line, filled"),
    ],
)
def test_a_derivation_short_of_a_template_field_is_refused_naming_it(tmp_path: Path, edit, why: str) -> None:  # noqa: ANN001
    """Feature 443 T13 (the GM 2026-10-28): each field an error of T05's grid fixture would have been refused at - a bound's scope,
    its worst case, the cheaper algorithms considered - is checked before any dispatch."""
    (tmp_path / "d.md").write_text(edit((FIX / "grid-placer" / "derivation.md").read_text(encoding="utf-8")))
    rc, msg = wbb.budget_bundle(REPO, "x", str(tmp_path / "d.md"), tmp_path / "out")
    assert rc == 1 and "short of the template's fields" in msg and why in msg, msg


def test_the_water_familys_derivations_pass_the_form_checks() -> None:
    """The round arbiter's note on ask:444-T07-plan-round-3: every derivation judged SOUND (its `verdict.txt` beside it) passes the
    form checks - a budget is pinned from it."""
    phases = REPO / "specs/444-work-budget-program/phases"
    done = [p for p in sorted(phases.glob("*.derivation.md")) if (phases / p.name.replace(".derivation.md", ".verdict.txt")).is_file()]
    assert done, "a derivation judged SOUND (its verdict.txt)"
    for p in done:
        assert wbb.form_problems(p.read_text(encoding="utf-8")) == [], p.name


def test_the_template_and_both_fixtures_hold_every_field() -> None:
    template = (REPO / wbb.TEMPLATE).read_text(encoding="utf-8")
    assert all(f"- {a}:" in template for a in wbb.STANDARD) and "| factor | scope | value | reason | worst case |" in template
    assert wbb.form_problems((FIX / "grid-placer" / "derivation.md").read_text(encoding="utf-8")) == []
    assert wbb.form_problems((FIX / "funnel" / "derivation.md").read_text(encoding="utf-8")) == []
    assert "derivation.md" in (REPO / ".specify/templates/phase-checklist.md").read_text(encoding="utf-8"), "box 2 names it"


def test_a_budget_bundle_holds_the_derivation_contract_and_rubric(tmp_path: Path) -> None:
    rc, manifest = wbb.budget_bundle(REPO, "funnel", str(FIX / "funnel" / "derivation.md"), tmp_path / "out")
    assert rc == 0 and Path(manifest).name == "MANIFEST.md"
    assert {p.name for p in (tmp_path / "out").iterdir()} == {"MANIFEST.md", "derivation.md", "contract.md", "rubric.md"}
    assert (tmp_path / "out" / "contract.md").read_text().startswith("## Contract")
    (tmp_path / "nc.md").write_text("no contract here\n")
    assert "no `## Contract` section" in wbb.budget_bundle(REPO, "x", str(tmp_path / "nc.md"), tmp_path / "o2")[1]
    assert wbb.budget_bundle(REPO, "x", str(tmp_path / "missing.md"), tmp_path / "o3")[0] == 2


def test_an_audit_bundle_holds_the_code_counts_chains_and_budget(tmp_path: Path) -> None:
    rc, _manifest = wbb.audit_bundle(REPO, "homesteads", tmp_path / "out")
    assert rc == 0
    names = {p.name for p in (tmp_path / "out").iterdir()}
    assert names == {"MANIFEST.md", "code", "counts.json", "chains.txt", "budget.json", "rubric.md"}
    assert any(p.name == "__init__.py" for p in (tmp_path / "out" / "code").iterdir()), "the stage's own package"
    assert wbb.audit_bundle(REPO, "no_such_stage", tmp_path / "o2")[0] == 2


def test_an_audit_bundle_takes_a_budget_file_in_place_of_the_tables(tmp_path: Path) -> None:
    rc, _m = wbb.audit_bundle(REPO, "homesteads", tmp_path / "out", "tests/fixtures/work-budget/funnel/budget.json")
    assert rc == 0 and '"status": "fixture"' in (tmp_path / "out" / "budget.json").read_text()


def test_the_chains_say_when_no_fanout_report_is_kept(tmp_path: Path) -> None:
    assert "no `make perf-fanout` report is kept" in wbb.fanout_section(tmp_path, "web")
    (tmp_path / "dev" / "perf-log").mkdir(parents=True)
    (tmp_path / "dev" / "perf-log" / "x-fanout-y.txt").write_text("field: 1 calls\n  a\nweb: 2 calls\n  chain\ntrack: 3 calls\n")
    assert wbb.fanout_section(tmp_path, "web").endswith("web: 2 calls\n  chain\n")
    assert "no section for sink" in wbb.fanout_section(tmp_path, "sink")


def test_main_builds_and_refuses(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "o"
    assert wbb.main(["budget", "grid-placer", "--derivation", str(FIX / "grid-placer" / "derivation.md"), "--out", str(out)]) == 0
    assert wbb.main(["budget", "grid-placer", "--derivation", str(FIX / "grid-placer" / "derivation.md"), "--out", str(out)]) == 0, "a stale bundle is replaced"
    assert wbb.main(["budget", "web", "--out", str(out)]) == 2 and "needs DERIVATION" in capsys.readouterr().err
    assert wbb.main(["budget", "", "--out", str(out)]) == 2
    assert wbb.main(["audit", "homesteads", "--out", str(tmp_path / "a")]) == 0
    empty = tmp_path / "empty"
    (empty / "l7r" / "diagram" / "hamletgen").mkdir(parents=True)
    (empty / "l7r" / "diagram" / "hamletgen" / "x.py").write_text("def stage_web(s, plan):\n    pass\n")
    assert wbb.audit_bundle(empty, "web", tmp_path / "b")[1].endswith("run it first")


@pytest.mark.parametrize(
    ("edit", "why"),
    [
        (lambda t: t.replace("- at 40: 40 x (9 x 1 + 8) x 1 + 4 x 40 = 840\n", ""), "a line for 40 households"),
        (lambda t: t.replace("- at 80: 80 x (9 x 1 + 8) x 1 + 4 x 80 = 1680", "- at 80: 80 x (9 x 1 + 8) x 1 + 4 x 80 = 1681"), "is 1,680, not 1681"),
        (lambda t: t.replace("- at 40: 40 x (9 x 1 + 8) x 1 + 4 x 40 = 840", "- at 40: 40 x (9 x 1 + 8) x 1 = 680"), "figure 4 is not in the expression"),
        (lambda t: t.replace("- at 20: 20 x (9 x 1 + 8) x 1 + 4 x 20 = 420", "- at 20: nine x 20 = 420"), "is not arithmetic"),
        (lambda t: t.split("## Totals")[0] + "## Cheaper" + t.split("## Cheaper")[1], "a `## Totals` section"),
        (lambda t: t.replace("| lookups: the lattice cells examined (S2) |", "| lookups (S2) |"), "a row counting the index cells examined"),
        (lambda t: t.replace("| marks per disc placed | per item | at most 8 |", "| marks per disc placed | per item | the conflict set |"), "no figure at 20 households"),
        (
            lambda t: t.replace("| slack | per item | 1 |", "| slack | per item | 1 |").replace("- at 20: 20 x (9 x 1 + 8) x 1 + 4 x 20 = 420", "- at 20: 20 x (9 x 1 + 8) + 4 x 20 = 420"),
            "`slack`'s figure 1 is not in the expression",
        ),
    ],
)
def test_a_derivations_totals_are_evaluated_and_its_index_cells_counted(tmp_path: Path, edit, why: str) -> None:  # noqa: ANN001
    """Feature 444 T07 (the GM's rule on a repeated error, 2026-10-28): a sum written wrong, a total leaving out a term, a size
    left out, and an index whose cells are not counted - each refused before any dispatch."""
    (tmp_path / "d.md").write_text(edit((FIX / "grid-placer" / "derivation.md").read_text(encoding="utf-8")))
    rc, msg = wbb.budget_bundle(REPO, "x", str(tmp_path / "d.md"), tmp_path / "out")
    assert rc == 1 and why in msg, msg


def test_the_arithmetic_reader_takes_numbers_and_the_four_operators_alone() -> None:
    import ast as _ast

    assert wbb._arith(_ast.parse("-(2 + 3) * 4 / 2 - 1", mode="eval").body) == -11
    with pytest.raises(ValueError):
        wbb._arith(_ast.parse("2 ** 3", mode="eval").body)


@pytest.mark.parametrize(
    ("edit", "why"),
    [
        (lambda t: t.split("## Indexes")[0] + "## The count" + t.split("## The count", 1)[1], "an `## Indexes` section"),
        (lambda t: t.replace("cells of 5 ft (d / 2", "cells of d / 2 ("), "its cell size in ft"),
        (lambda t: t.replace("from a smallest side of 5 ft", "from a smallest area of 25 sq ft"), "from a smallest side in ft"),
        (lambda t: t.replace("| lookups: the lattice cells examined (S2) |", "| lookups: the cells examined (S2) |"), "a row counting the lattice's cells"),
        (lambda t: t.replace("## Contract", "## Contract\n\nA 30 px border.", 1), "`30 px`: a px figure with no ft"),
    ],
)
def test_every_index_has_its_own_row_and_every_px_its_ft(tmp_path: Path, edit, why: str) -> None:  # noqa: ANN001
    """The round arbiter's tooling fix on ask:444-T02-water-round-6: T07's index check held once a derivation, so one cells row passed
    while each index a rewrite added went unchecked (field round 5, pond_bank round 3); it now holds per index - its cell size in ft, its
    densest case from a side, never an area, its own row - and every px figure carries its ft."""
    (tmp_path / "d.md").write_text(edit((FIX / "grid-placer" / "derivation.md").read_text(encoding="utf-8")))
    rc, msg = wbb.budget_bundle(REPO, "x", str(tmp_path / "d.md"), tmp_path / "out")
    assert rc == 1 and why in msg, msg
    assert wbb.index_problems("A 30 px (30 ft) corridor.") == [], "a px figure with its ft passes"


def test_every_earlier_finding_is_answered_before_the_bundle_builds(tmp_path: Path) -> None:
    """The round arbiter's tooling fix on ask:444-T02-field-round-8: a finding left open under one verdict's "Also" came back as the
    next verdict's headline (field verdict-5 to verdict-7). Each finding of each earlier verdict is answered - fixed or disputed with
    its reason - or the bundle is refused; the earlier verdicts travel in the bundle for the judge to confirm."""
    d = tmp_path / "x.derivation.md"
    d.write_text((FIX / "grid-placer" / "derivation.md").read_text(encoding="utf-8"))
    (tmp_path / "x.verdict-1.txt").write_text("UNDERIVED - the first thing.\n\n(Also: a second thing; a third thing.)\n")
    assert wbb.findings_of((tmp_path / "x.verdict-1.txt").read_text()) == ["UNDERIVED - the first thing.", "a second thing", "a third thing"]
    rc, msg = wbb.budget_bundle(REPO, "x", str(d), tmp_path / "out")
    assert rc == 1 and msg.count("unanswered") == 3, msg
    d.write_text(d.read_text() + "\n## Earlier findings\n\n- verdict-1, finding 1: fixed - done\n- verdict-1, finding 2: disputed - because\n")
    rc, msg = wbb.budget_bundle(REPO, "x", str(d), tmp_path / "out")
    assert rc == 1 and "verdict-1, finding 3 unanswered" in msg and "finding 2 unanswered" not in msg
    d.write_text(d.read_text() + "- verdict-1, finding 3: fixed - also done\n")
    rc, manifest = wbb.budget_bundle(REPO, "x", str(d), tmp_path / "out")
    assert rc == 0 and (tmp_path / "out" / "x.verdict-1.txt").is_file(), "the earlier verdict travels in the bundle"
    assert wbb.findings_of("") == []
