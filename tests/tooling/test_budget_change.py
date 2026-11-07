"""`scripts/budget_change.py` - the one writer of `dev/work-budget.json` (feature 443 T03, plan D6; FR-005, SC-003).

A first budget only from a SOUND MODE BUDGET verdict; every later change, and the program's budget, only with WORDS (the GM's,
checked by `budget-change-hooks.sh`, `tests/hooks/test-budget-change-hooks.sh`), and logged with them.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil

import pytest

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("budget_change", script("budget_change"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bc = _load()


@pytest.fixture
def root(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "dev").mkdir()
    shutil.copy(REPO / bc.TABLE, tmp_path / bc.TABLE)
    # The real table's stages, every one reset: the tests set budgets of their own on a table whose stages are the engine's.
    table = bc.load(tmp_path)
    table["stages"] = {k: {"status": "unbudgeted"} for k in table["stages"]}
    bc.save(tmp_path, table)
    (tmp_path / "d.md").write_text("the derivation\n")
    for word in ("SOUND", "LOOSE", "UNDERIVED"):
        (tmp_path / f"{word}.txt").write_text(f"{word} - the reason\n\nthe body\n")
    return tmp_path


@pytest.mark.parametrize("word", ["LOOSE", "UNDERIVED"])
def test_a_first_budget_needs_a_sound_verdict(root: pathlib.Path, word: str) -> None:
    why = bc.set_budget(root, "web", 40, 1.0, "d.md", f"{word}.txt")
    assert f"reads {word}, not SOUND" in why and "make work-budget-bundle MODE=budget" in why
    assert bc.load(root)["stages"]["web"] == {"status": "unbudgeted"}


def test_a_sound_verdict_sets_a_first_budget_and_a_second_set_is_refused(root: pathlib.Path) -> None:
    assert "no items at 20, 40, 80 households" in bc.set_budget(root, "web", 40, 1.1, "d.md", "SOUND.txt"), "the derivation's items are owed"
    assert bc.main(["--root", str(root), "set", "web", "40", "1.1", "d.md", "SOUND.txt", "--items-at-20", "10", "--items-at-40", "20", "--items-at-80", "40"]) == 0
    assert bc.load(root)["stages"]["web"] == {
        "status": "budgeted",
        "per_thing": 40,
        "exponent": 1.1,
        "derivation": "d.md",
        "verdict": "SOUND.txt",
        "items_at_20": 10,
        "items_at_40": 20,
        "items_at_80": 40,
    }
    why = bc.set_budget(root, "web", 30, 1.0, "d.md", "SOUND.txt")
    assert "budgeted already" in why and "make budget-change PHASE=web" in why, "a budgeted stage changes only with the GM's words"
    assert "no derivation at x.md" in bc.set_budget(root, "track", 1, 1, "x.md", "SOUND.txt")
    assert "no stage `nope`" in bc.set_budget(root, "nope", 1, 1, "d.md", "SOUND.txt")
    assert "reads nothing" in bc.set_budget(root, "track", 1, 1, "d.md", "missing.txt")


def _run(root: pathlib.Path, stage: str, ops_at_40: float) -> None:
    runs = root / bc.RUNS
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "20261028T000000Z-x.json").write_text(json.dumps({"summary": {"stages": {stage: {"per": {"40": {"ops": ops_at_40}}}}}}))


def test_a_pin_above_todays_count_needs_a_reason_and_every_pin_prints_the_program_per_house(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """ask:444-budget-standard (the GM 2026-10-28: "I thought the idea was to REDUCE the number of operations. Why would we be
    targeting something HIGHER?"): a budget at 40 above what the stage counts today is refused without a reason, and every pin
    prints the program's sum per household against the design's few thousand."""
    _run(root, "web", 500)
    items = ["--items-at-20", "10", "--items-at-40", "20", "--items-at-80", "40"]
    assert "above what the stage counts today, 500" in bc.set_budget(root, "web", 40, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40}), "800 > 500"
    assert bc.load(root)["stages"]["web"]["status"] == "unbudgeted"
    assert bc.main(["--root", str(root), "set", "web", "40", "1.0", "d.md", "SOUND.txt", *items, "--reason", "the web is laid twice today"]) == 0
    assert bc.load(root)["stages"]["web"]["reason"] == "the web is laid twice today"
    assert "a household against the design's few thousand" in capsys.readouterr().out, "the program per house, at every pin"
    assert bc.set_budget(root, "track", 10, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40}) == "", "no run counts track: no refusal"


def test_a_budget_is_lowered_without_words_and_never_raised(root: pathlib.Path) -> None:
    """A lowering re-pins (no GM words: it asks nothing of him); a raise through it is refused, and the lowering is logged."""
    assert bc.set_budget(root, "web", 40, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40}) == ""
    assert "no budget to lower" in bc.set_budget(root, "track", 1, 1.0, "d.md", "SOUND.txt", {20: 1, 40: 1, 80: 1}, lower=True)
    assert "would rise at 80 households" in bc.set_budget(root, "web", 30, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 60}, lower=True)
    assert bc.set_budget(root, "web", 30, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40}, lower=True) == ""
    assert bc.load(root)["stages"]["web"]["per_thing"] == 30
    row = json.loads((root / bc.LOG).read_text().splitlines()[-1])
    assert row["what"] == "lowered" and row["to"]["80"] == 1200


def test_a_change_needs_words_and_a_budget_and_is_logged_with_the_words(root: pathlib.Path) -> None:
    assert "no WORDS" in bc.change_budget(root, "web", 50, None, "  ")
    assert "make budget-set PHASE=web" in bc.change_budget(root, "web", 50, None, "the GM's words here")
    assert "no stage `nope`" in bc.change_budget(root, "nope", 50, None, "the GM's words here")
    bc.set_budget(root, "web", 40, 1.1, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40})
    assert bc.main(["--root", str(root), "change", "web", "50", "--words", "raise it to fifty", "--items-at-80", "45"]) == 0
    assert bc.load(root)["stages"]["web"]["items_at_80"] == 45 and bc.load(root)["stages"]["web"]["items_at_40"] == 20
    assert bc.load(root)["stages"]["web"]["per_thing"] == 50 and bc.load(root)["stages"]["web"]["exponent"] == 1.1
    assert bc.change_budget(root, "web", 55, 1.2, "and the exponent too") == ""
    rows = [json.loads(ln) for ln in (root / bc.LOG).read_text().splitlines()]
    assert [r["words"] for r in rows] == ["raise it to fifty", "and the exponent too"]
    assert rows[1]["from"] == {"per_thing": 50, "exponent": 1.1} and rows[1]["to"] == {"per_thing": 55, "exponent": 1.2}
    # the item counts a change moves are logged beside it (444#3: a raise by items alone logged only the per-thing figure)
    assert rows[0]["from"]["items_at_80"] == 40 and rows[0]["to"]["items_at_80"] == 45 and "items_at_40" not in rows[0]["to"]
    # a raise re-points the stage at the derivation it comes from (feature 444 FR-015), only at a SOUND verdict, naming both
    (root / "g.md").write_text("the greenfield derivation\n")
    (root / "g.verdict.txt").write_text("SOUND - x\n")
    (root / "g.loose.txt").write_text("LOOSE - x\n")
    assert "names both" in bc.change_budget(root, "web", 60, None, "raise it", None, "g.md", "")
    assert "no SOUND verdict" in bc.change_budget(root, "web", 60, None, "raise it", None, "g.md", "g.loose.txt")
    assert "no derivation at" in bc.change_budget(root, "web", 60, None, "raise it", None, "nope.md", "g.verdict.txt")
    assert bc.change_budget(root, "web", 60, None, "raise it", None, "g.md", "g.verdict.txt") == ""
    st = bc.load(root)["stages"]["web"]
    assert st["derivation"] == "g.md" and st["verdict"] == "g.verdict.txt" and "pinned_on" not in st and st["per_thing"] == 60


def test_the_programs_budget_needs_words_and_is_logged(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert bc.main(["--root", str(root), "program", "1000000", "1.2"]) == 1
    assert "no WORDS" in capsys.readouterr().err
    assert bc.main(["--root", str(root), "program", "1000000", "1.2", "--words", "a million at forty"]) == 0
    assert bc.load(root)["program"] == {"ops_at_40": 1000000, "exponent": 1.2}
    row = json.loads((root / bc.LOG).read_text().splitlines()[-1])
    assert row["what"] == "program" and row["words"] == "a million at forty"


def test_a_rebuilt_phase_is_accepted_only_within_its_budget_on_its_audits_within(root: pathlib.Path) -> None:
    """Feature 444 FR-005, checklist boxes 6-8: `budget-accept` records a stage accepted - its MODE AUDIT WITHIN, its counted
    operations at 40 and 80 in the newest run at most its budget - and the figures the push's ratchet then holds; over its budget it
    is refused with FR-006's two ways on, never accepted."""
    bc.set_budget(root, "web", 10, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40})
    (root / "a.txt").write_text("WITHIN - x\n")
    (root / "o.txt").write_text("OVER - x\n")
    assert "not WITHIN or LEEWAY" in bc.accept_stage(root, "web", "o.txt")
    runs = root / bc.RUNS
    runs.mkdir(parents=True, exist_ok=True)

    def run(name: str, per: dict[str, dict[str, float]]) -> None:
        (runs / name).write_text(json.dumps({"summary": {"stages": {"web": {"per": per}}}}))

    run("1.json", {"40": {"ops": 150}})
    assert "no roll at 80" in bc.accept_stage(root, "web", "a.txt")
    run("2.json", {"40": {"ops": 150}, "80": {"ops": 500}})
    why = bc.accept_stage(root, "web", "a.txt")
    assert "1.25 times its budget 400 - over it" in why and "make budget-change" in why and "RAISE=1" in why
    run("3.json", {"40": {"ops": 150}, "80": {"ops": 380}})
    assert bc.main(["--root", str(root), "accept", "web", "a.txt"]) == 0
    st = bc.load(root)["stages"]["web"]
    assert st["status"] == "accepted" and st["accepted"] == {"40": 150.0, "80": 380.0}
    assert json.loads((root / bc.LOG).read_text().splitlines()[-1])["what"] == "accepted"
    assert "no stage `nope`" in bc.accept_stage(root, "nope", "a.txt")


def test_the_growth_cap_is_held_by_the_tool(root: pathlib.Path) -> None:
    """Rubric S6, the GM 2026-10-29 ("if we allow polynomial growth but with a high exponent like n cubed ... that is really going to
    not work"): a pin growing past 1.15 from 20 to 80 names its reason, and an accepted phase grows no faster than its budget."""
    (root / "d.md").write_text("x\n")
    (root / "SOUND.txt").write_text("SOUND - x\n")
    steep = {20: 10, 40: 40, 80: 160}  # an exponent of 2.0
    why = bc.set_budget(root, "web", 1, 2.0, "d.md", "SOUND.txt", steep)
    assert "exponent of 2.00" in why and "GROWTH_REASON" in why
    assert bc.set_budget(root, "web", 1, 2.0, "d.md", "SOUND.txt", steep, growth_reason="the gaps are bounded by the lattice") == ""
    assert bc.load(root)["stages"]["sties"]["status"] == "unbudgeted"
    assert bc.set_budget(root, "sties", 10, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40}) == ""
    (root / "a.txt").write_text("WITHIN - x\n")
    runs = root / bc.RUNS
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "1.json").write_text(json.dumps({"summary": {"stages": {"sties": {"per": {"20": {"ops": 20}, "40": {"ops": 100}, "80": {"ops": 390}}}}}}))
    why = bc.accept_stage(root, "sties", "a.txt")
    assert "exponent of 2.14" in why and "past its budget's 1.00" in why
    assert bc.growth(0, 5) == 0.0


def test_a_form_of_a_stage_is_budgeted_at_its_bounded_n(root: pathlib.Path) -> None:
    """The round arbiter's ruling on ask:444-polder-sizes (route a): the polder - a form of the field stage, drawn at 10-20
    households alone (0019) - is pinned as `field.polder` at 10 and 20, from a derivation stating its bounded n; it stays out of the
    program's sum at 40, and the table's item check reads its own sizes."""
    (root / "p.md").write_text("- Bounds: a bounded n: households 10-20 (0019)\n")
    assert "no items at 20 households" in bc.set_budget(root, "field.polder", 245, 0.5, "p.md", "SOUND.txt", {10: 19})
    assert "no stage `nope.polder`" in bc.set_budget(root, "nope.polder", 1, 1, "p.md", "SOUND.txt", {10: 1, 20: 2})
    before = bc.per_house(root)
    assert bc.set_budget(root, "field.polder", 245, 0.5, "p.md", "SOUND.txt", {10: 19, 20: 38}) == ""
    st = bc.load(root)["stages"]["field.polder"]
    assert st["sizes"] == [10, 20] and st["items_at_10"] == 19 and "items_at_40" not in st
    after = bc.per_house(root)
    # the sum at 40 unmoved; the count of stages not yet budgeted rightly one fewer
    assert after.split(";")[0] == before.split(";")[0], f"a form at a bounded n holds no figure at 40: {before!r} -> {after!r}"
    assert bc.growth(100, 141, 2) == pytest.approx(0.496, abs=0.01)
    # the table's item check reading a form's own sizes is `tests/tools/test_work_budget.py`'s (it lands with the engine)
    # raised at its own top size (feature 444 T29: the raise path read the budget at 40, which a bounded form has none of)
    (root / "p.md").write_text(f"- Bounds: a bounded n: households 10-20 (0019)\n\n{bc.MISSED}\n\n- the strip drawing's passes\n")
    assert bc.set_budget(root, "field.polder", 400, 0.5, "p.md", "SOUND.txt", {10: 19, 20: 38}, raise_=True) == ""
    st = bc.load(root)["stages"]["field.polder"]
    assert st["first"] == {"10": 245 * 19, "20": 245 * 38} and st["per_thing"] == 400
    assert "budget at 20, 11,400, is no raise on 15,200" in bc.set_budget(root, "field.polder", 300, 0.5, "p.md", "SOUND.txt", {10: 19, 20: 38}, raise_=True)


def test_an_accept_naming_a_form_pins_it(root: pathlib.Path) -> None:
    """An arbiter's accept of the polder's derivation names it `polder` (ask:444-polder-round-3): the form `field.polder` answers to
    its own name, and to its greenfield derivation's."""
    spec = root / "specs" / "444-x"
    (spec / "phases").mkdir(parents=True)
    (spec / "phases" / "polder_greenfield.derivation.md").write_text("- Bounds: a bounded n: households 10-20\n")
    (spec / "arbiter.jsonl").write_text(json.dumps({"trigger": "ask:444-polder-round-3", "ruling": "accept", "what": "the polder stands"}) + "\n")
    d = "specs/444-x/phases/polder_greenfield.derivation.md"
    assert bc.accepted_by(root, d, "field.polder", "ask:444-polder-round-3")
    assert not bc.accepted_by(root, d, "field.dikepond", "ask:444-polder-round-3"), "another form's name is not this accept's"


def test_a_form_is_accepted_from_its_own_audit_run_at_its_bounded_n(root: pathlib.Path) -> None:
    """Feature 444 T29: a form at its bounded n (`waterward.polder`, 10-20) is accepted from `make work-budget SPEC=`'s run (`-spec.json`),
    under its stage's name, at its own sizes; a stage is never accepted from a form's run, which rolls another form of it."""
    (root / "p.md").write_text("- Bounds: a bounded n: households 10-20 (0019)\n")
    (root / "w.txt").write_text("WITHIN - x\n")
    assert bc.set_budget(root, "field.polder", 100, 0.5, "p.md", "SOUND.txt", {10: 10, 20: 14}) == ""
    runs = root / bc.RUNS
    runs.mkdir(parents=True, exist_ok=True)
    assert "no `make work-budget SPEC=` run counts `field.polder`" in bc.accept_stage(root, "field.polder", "w.txt")
    (runs / "20261104T000000Z-x-spec.json").write_text(json.dumps({"summary": {"stages": {"field": {"per": {"10": {"ops": 900}, "20": {"ops": 1300}}}}}}))
    (runs / "20261103T000000Z-x.json").write_text(json.dumps({"summary": {"stages": {"field": {"per": {"40": {"ops": 1}}}}}}))
    assert bc.accept_stage(root, "field.polder", "w.txt") == ""
    assert bc.load(root)["stages"]["field.polder"]["accepted"] == {"10": 900.0, "20": 1300.0}
    # the stage itself reads the reference run, never the newer form's
    bc.set_budget(root, "field", 1, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40}, reason="a test")
    assert "no roll at 80" in bc.accept_stage(root, "field", "w.txt")
    (runs / "20261104T000000Z-x-spec.json").write_text(json.dumps({"summary": {"stages": {"field": {"per": {"10": {"ops": 500}, "20": {"ops": 1300}}}}}}))
    assert "from 10 to 20 households" in bc.accept_stage(root, "field.polder", "w.txt")


def test_a_rebuilt_phase_is_accepted_on_the_arbiters_accept_in_place_of_a_within(root: pathlib.Path) -> None:
    """Feature 444 T16: the field's sixth MODE AUDIT, final for box 7, came back UNCOUNTED; the round arbiter accepted the cheaper
    rebuild that followed (ask:444-T16-field-after-audit-6) in place of a seventh. `budget-accept ARBITER=` takes that accept - only
    one the log holds naming the phase - and every budget check still holds."""
    feat = root / "specs" / "444-x"
    (feat / "phases").mkdir(parents=True)
    d = "specs/444-x/phases/web.derivation.md"
    (root / d).write_text("the derivation\n")
    bc.set_budget(root, "web", 10, 1.0, d, "SOUND.txt", {20: 10, 40: 20, 80: 40})
    (root / "u.txt").write_text("UNCOUNTED - x\n")
    runs = root / bc.RUNS
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "1.json").write_text(json.dumps({"summary": {"stages": {"web": {"per": {"20": {"ops": 100}, "40": {"ops": 150}, "80": {"ops": 380}}}}}}))
    assert "not WITHIN or LEEWAY" in bc.accept_stage(root, "web", "u.txt"), "an UNCOUNTED alone accepts nothing"
    assert "holds no accept at ask:444-T16-web-after-6" in bc.accept_stage(root, "web", "u.txt", "ask:444-T16-web-after-6")
    (feat / "arbiter.jsonl").write_text(json.dumps({"trigger": "ask:444-T16-track-after-6", "ruling": "accept", "what": "the track stands"}) + "\n")
    assert "holds no accept" in bc.accept_stage(root, "web", "u.txt", "ask:444-T16-track-after-6"), "another phase's accept"
    (feat / "arbiter.jsonl").write_text(json.dumps({"trigger": "ask:444-T16-web-after-6", "ruling": "accept", "what": "box 7 closes on this rebuild"}) + "\n")
    (runs / "2.json").write_text(json.dumps({"summary": {"stages": {"web": {"per": {"20": {"ops": 100}, "40": {"ops": 150}, "80": {"ops": 500}}}}}}))
    assert "1.25 times its budget 400" in bc.accept_stage(root, "web", "u.txt", "ask:444-T16-web-after-6"), "the budget still holds: an accept is no LEEWAY"
    (runs / "3.json").write_text(json.dumps({"summary": {"stages": {"web": {"per": {"20": {"ops": 100}, "40": {"ops": 150}, "80": {"ops": 380}}}}}}))
    assert bc.main(["--root", str(root), "accept", "web", "u.txt", "--arbiter", "ask:444-T16-web-after-6"]) == 0
    st = bc.load(root)["stages"]["web"]
    assert st["status"] == "accepted" and st["accept"] == "ask:444-T16-web-after-6"


def test_a_stage_is_accepted_at_up_to_twice_its_budget_on_its_audits_leeway(root: pathlib.Path) -> None:
    """Feature 444 FR-022 rule 1, SC-015 (the GM 2026-11-03: "I would frankly be okay with things that are 50% higher or even twice
    as high"): over its budget a stage is accepted only on the MODE AUDIT's LEEWAY, never past twice it on either word, and its
    growth holds it as before."""
    bc.set_budget(root, "web", 10, 1.0, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40})
    (root / "w.txt").write_text("WITHIN - x\n")
    (root / "l.txt").write_text("LEEWAY - the brook's rounding unpriced, counted and linear\n")
    runs = root / bc.RUNS
    runs.mkdir(parents=True, exist_ok=True)

    def run(name: str, at20: float, at40: float, at80: float) -> None:
        (runs / name).write_text(json.dumps({"summary": {"stages": {"web": {"per": {"20": {"ops": at20}, "40": {"ops": at40}, "80": {"ops": at80}}}}}}))

    run("1.json", 150, 300, 600)  # 1.5 times at every size
    assert "1.50 times its budget 200 - over it, a phase is accepted on the MODE AUDIT's LEEWAY" in bc.accept_stage(root, "web", "w.txt")
    run("2.json", 300, 500, 900)  # 2.5 times at 40
    assert "past the leeway's 2 times" in bc.accept_stage(root, "web", "l.txt"), "past twice it, even on LEEWAY"
    run("3.json", 40, 300, 600)  # within the band, but growing at 1.94 against the budget's 1.00
    assert "past its budget's 1.00" in bc.accept_stage(root, "web", "l.txt"), "no leeway on growth (FR-022 rule 3)"
    run("4.json", 150, 300, 600)
    assert bc.accept_stage(root, "web", "l.txt") == ""
    assert bc.load(root)["stages"]["web"]["accepted"] == {"40": 300.0, "80": 600.0}


def test_a_budget_is_raised_on_a_sound_rederivation_naming_its_missed_work(root: pathlib.Path) -> None:
    """Feature 444 FR-022 rule 2, SC-015 (the GM 2026-11-03: "if we discover that there are things that we didn't take into account,
    then it makes sense to raise the operations budget"): RAISE=1 raises a budgeted stage on a SOUND derivation with its missed-work
    section, logged with the items; refused without the section, on a figure no higher, and past ten times the first budget at 40."""
    items = {20: 10, 40: 20, 80: 40}
    bc.set_budget(root, "web", 10, 1.0, "d.md", "SOUND.txt", items)  # 200 at 40
    assert "names no work its first derivation missed" in bc.set_budget(root, "web", 20, 1.0, "d.md", "SOUND.txt", items, raise_=True)
    (root / "r.md").write_text(f"# x\n\n{bc.MISSED}\n\n- the brook rounded at the stage's end\n- the off-map route's search\n\n## Growth\n\n- not an item\n")
    assert bc.missed_work(root, "r.md") == ["the brook rounded at the stage's end", "the off-map route's search"]
    assert "not SOUND" in bc.set_budget(root, "web", 20, 1.0, "r.md", "LOOSE.txt", items, raise_=True)
    assert "is no raise" in bc.set_budget(root, "web", 10, 1.0, "r.md", "SOUND.txt", items, raise_=True)
    assert "together" in bc.set_budget(root, "web", 20, 1.0, "r.md", "SOUND.txt", items, raise_=True, lower=True)
    _run(root, "web", 100)  # today's count below the raise: a raise owes no REASON, its section is the reason
    assert bc.main(["--root", str(root), "set", "web", "18", "1.0", "r.md", "SOUND.txt", "--raise", *[f"--items-at-{h}={n}" for h, n in items.items()]]) == 0
    st = bc.load(root)["stages"]["web"]
    assert st["per_thing"] == 18 and st["first"] == {"20": 100.0, "40": 200.0, "80": 400.0} and st["derivation"] == "r.md"
    # raised on one SOUND, LEEWAY stops at twice the FIRST 200, not twice the raised 360
    (root / "l.txt").write_text("LEEWAY - x\n")
    (root / bc.RUNS / "20261028T120000Z-x.json").write_text(json.dumps({"summary": {"stages": {"web": {"per": {"20": {"ops": 225}, "40": {"ops": 450}, "80": {"ops": 900}}}}}}))
    assert "past 2 times its first budget 200" in bc.accept_stage(root, "web", "l.txt") and "SECOND=" in bc.accept_stage(root, "web", "l.txt")
    row = json.loads((root / bc.LOG).read_text().splitlines()[-1])
    assert row["what"] == "raised" and row["to"]["40"] == 360 and len(row["missed"]) == 2
    # past twice the FIRST 200 (not the standing 360): the rigorous analysis, a second SOUND from a distinct dispatch
    why = bc.set_budget(root, "web", 60, 1.0, "r.md", "SOUND.txt", items, raise_=True)
    assert "6.0 times its first, 200" in why and "SECOND=" in why
    assert "SECOND=" in bc.set_budget(root, "web", 60, 1.0, "r.md", "SOUND.txt", items, raise_=True, second="SOUND.txt"), "the same verdict twice is one"
    assert "LOOSE.txt reads LOOSE" in bc.set_budget(root, "web", 60, 1.0, "r.md", "SOUND.txt", items, raise_=True, second="LOOSE.txt")
    (root / "SOUND2.txt").write_text("SOUND - the second reading\n")
    why = bc.set_budget(root, "web", 101, 1.0, "r.md", "SOUND.txt", items, raise_=True, second="SOUND2.txt")  # 2,020 > 10 x 200
    assert "past 10 times its first, 200" in why and "make budget-change" in why
    assert bc.set_budget(root, "web", 60, 1.0, "r.md", "SOUND.txt", items, raise_=True, second="SOUND2.txt") == ""
    st = bc.load(root)["stages"]["web"]
    assert st["first"]["40"] == 200.0 and st["second"] == "SOUND2.txt", "the first figure survives a second raise"
    # the leeway does not stack past ten times the first: 1.9 x 1,200 at 40 is 2,280, past 2,000
    (root / bc.RUNS / "20261029T000000Z-x.json").write_text(json.dumps({"summary": {"stages": {"web": {"per": {"20": {"ops": 1140}, "40": {"ops": 2280}, "80": {"ops": 4560}}}}}}))
    assert "past 10 times its first budget 200" in bc.accept_stage(root, "web", "l.txt")
    assert "unbudgeted - RAISE=1 raises a budgeted stage" in bc.set_budget(root, "track", 1, 1.0, "r.md", "SOUND.txt", items, raise_=True)
