"""`scripts/_review_prereq.py`, each decision proven both ways (feature 240, FR-003 to FR-006).

The GM (2026-09-13): *"procedures which rely on someone, whether it's a human or an LLM, remembering to do
something are flawed"*. Every decision here reads a RECORD, never prose, and the case that matters most is
SC-002: feature 230's pass-13 dispatch with every figure removed must still be refused, because a rule a
session can pass by saying nothing is a rule that relies on remembering.

No `tooling` marker: it writes small files in a tmp directory and calls functions.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("review_prereq", REPO / "scripts" / "_review_prereq.py")
assert _spec and _spec.loader
prereq = importlib.util.module_from_spec(_spec)
sys.modules["review_prereq"] = prereq
_spec.loader.exec_module(prereq)


def _clone(tmp: pathlib.Path) -> pathlib.Path:
    (tmp / ".git").mkdir()
    (tmp / "specs" / "240-x").mkdir(parents=True)
    return tmp


def _verdict(clone: pathlib.Path, name: str, verdict: str, *ids: str) -> None:
    d = clone / ".git" / "review-verdicts"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps({"map": name, "engine_key": "k", "verdict": verdict, "findings": [{"id": i, "severity": "error", "what": "x"} for i in ids]}))


def _records(clone: pathlib.Path, **entries: dict) -> None:
    (clone / "specs" / "240-x" / "measurements.json").write_text(json.dumps(entries))


# ---- FR-003 --------------------------------------------------------------------------------------------------


def test_a_finding_with_no_record_is_unverified_and_a_verifying_record_or_an_acceptance_disposes_of_it(tmp_path: pathlib.Path) -> None:
    clone = _clone(tmp_path)
    _verdict(clone, "sawada", "NEEDS-WORK", "E1", "E2", "E3")
    assert prereq.unverified_findings(clone, "sawada") == ["E1", "E2", "E3"], "nothing recorded: every finding is open"

    _records(clone, **{"board-canopy": {"value": 0.6, "unit": "ft", "verifies": "E1", "subject": "sawada", "source": "tree_crowns"}})
    assert prereq.unverified_findings(clone, "sawada") == ["E1", "E2", "E3"], "SC-007: a record with no `quantity` verifies nothing"
    _records(clone, **{"board-canopy": {"value": 0.6, "unit": "ft", "verifies": "E1", "subject": "sawada", "quantity": "board to crown edge"}})
    assert prereq.unverified_findings(clone, "sawada") == ["E1", "E2", "E3"], "SC-007: nor one with no `source` for the reviewer to judge"
    _records(clone, **{"board-canopy": {"value": 0.6, "unit": "ft", "verifies": "E1", "subject": "sawada", "source": "tree_crowns", "quantity": "board to crown edge"}})
    assert prereq.unverified_findings(clone, "sawada") == ["E2", "E3"], "a record that verifies E1 for THIS map disposes of it"

    _records(clone, **{"board-canopy": {"value": 0.6, "unit": "ft", "verifies": "E1", "subject": "mizuguchi"}})
    assert "E1" in prereq.unverified_findings(clone, "sawada"), "a record about another map does not"

    d = clone / ".git" / "review-dispositions"
    d.mkdir()
    (d / "sawada.json").write_text(json.dumps({"accepted": [{"finding": "E2", "reason": "the byre sits 2.2 ft off, as village_grove intends"}, {"finding": "E3", "reason": "ok"}]}))
    assert prereq.unverified_findings(clone, "sawada") == ["E1", "E3"], "E2 is accepted with a reason; E3's one-word reason does not count"


def test_a_not_reviewable_verdict_raises_no_findings_and_no_verdict_means_nothing_to_verify(tmp_path: pathlib.Path) -> None:
    clone = _clone(tmp_path)
    assert prereq.unverified_findings(clone, "inashiro") == [] and not prereq.has_findings(clone, "inashiro")
    _verdict(clone, "inashiro", "NOT-REVIEWABLE", "P1")
    assert prereq.unverified_findings(clone, "inashiro") == [] and not prereq.has_findings(clone, "inashiro")
    (clone / ".git" / "review-verdicts" / "inashiro.json").write_text("not json")
    assert prereq.latest_verdict(clone, "inashiro") is None, "an unreadable record is no record"


# ---- FR-005 --------------------------------------------------------------------------------------------------


def test_a_map_is_stale_when_its_key_moved_or_an_artifact_is_missing(tmp_path: pathlib.Path) -> None:
    skill = tmp_path / ".claude" / "skills" / "diagram"
    m = skill / "pool" / "hamlets" / "kuwabata"
    m.mkdir(parents=True)
    (m / "kuwabata.gen.py").write_text("")
    for ext in (".json", ".svg", ".png", ".html"):
        (m / f"kuwabata{ext}").write_text("")
    assert prereq.stale_maps(skill, ["kuwabata"], lambda gen: True) == []
    moved = prereq.stale_maps(skill, ["kuwabata"], lambda gen: False)[0]
    assert "generation key has moved" in moved and "`make map GEN=pool/hamlets/kuwabata/kuwabata.gen.py`" in moved
    (m / "kuwabata.png").unlink()
    assert "missing .png" in prereq.stale_maps(skill, ["kuwabata"], lambda gen: True)[0], "feature 230's pass 12: renders evicted"
    # the gate evicts the pool's renders mid-run; a review beside it reads the snapshot taken before, which is whole
    snap = tmp_path / ".git" / "review-snapshot" / "kuwabata" / "clone"
    snap.mkdir(parents=True)
    for ext in (".json", ".svg", ".png"):
        (snap / f"kuwabata{ext}").write_text("")
    assert "missing .png" in prereq.stale_maps(skill, ["kuwabata"], lambda gen: True)[0], "each place names what it lacks; the nearer-whole one is reported"
    (snap / "kuwabata.html").write_text("")
    assert prereq.stale_maps(skill, ["kuwabata"], lambda gen: True) == [], "a whole snapshot is a whole map for the reviewer"
    assert "no pool generator" in prereq.stale_maps(skill, ["nowhere"], lambda gen: True)[0]


# ---- FR-006 --------------------------------------------------------------------------------------------------


def test_a_quoted_figure_resolves_by_key_or_one_shot_label_and_a_named_one_is_skipped(tmp_path: pathlib.Path) -> None:
    records = [{"key": "board-canopy", "value": 0.57, "unit": "ft"}]
    assert prereq.unresolved_figures("The plank stands 6.6 ft clear of the nearest crown.", records) == ["6.6 ft"], "a guess"
    assert prereq.unresolved_figures("The plank stands 0.57 ft clear (`m:board-canopy`).", records) == [], "cited, and the value matches"
    assert prereq.unresolved_figures("The plank stands 6.6 ft clear (`m:board-canopy`).", records) == ["6.6 ft"], "cited, but the value does not"
    assert prereq.unresolved_figures("A run took 145 ms (observed 2026-09-13; method, two runs).", records) == [], "239's one-shot label"
    assert prereq.unresolved_figures("The constant `BROOK_SKIRT` is `34 ft` in the code.", records) == [], "named in backticks, not claimed"


# ---- the check, and SC-002 -----------------------------------------------------------------------------------


def _pool_map(clone: pathlib.Path, name: str) -> None:
    m = clone / ".claude" / "skills" / "diagram" / "pool" / "hamlets" / name
    m.mkdir(parents=True)
    (m / f"{name}.gen.py").write_text("")
    for ext in (".json", ".svg", ".png", ".html"):
        (m / f"{name}{ext}").write_text("")


def test_feature_230s_pass_13_dispatch_is_refused_even_with_every_figure_removed(tmp_path: pathlib.Path) -> None:
    """SC-002. Pass 12 raised the board-in-the-belt finding; the fix was verified against clump bases, not drawn
    crowns, and pass 13 spent a full round finding that. Strip every figure out of the dispatch and it must STILL
    be refused - naming the finding - because the refusal reads the findings record, not the prompt."""
    clone = _clone(tmp_path)
    _pool_map(clone, "sawada")
    _verdict(clone, "sawada", "NEEDS-WORK", "E2-board-in-belt")
    silent = "Verify pass 12's fixes on Sawada: the notice board no longer stands in the windbreak canopy."
    problems = prereq.check(clone, ["sawada"], silent, gate_green=True, current=lambda g: True)
    assert any("E2-board-in-belt" in p and p.startswith("FR-003") for p in problems), problems

    _records(
        clone,
        **{
            "sawada-board-canopy": {
                "value": 0.57,
                "unit": "ft",
                "verifies": "E2-board-in-belt",
                "subject": "sawada",
                "source": "tree_crowns",
                "quantity": "plank glyph edge to nearest drawn crown edge",
            }
        },
    )
    assert prereq.check(clone, ["sawada"], silent, gate_green=True, current=lambda g: True) == [], "recorded: it may go"


def test_a_review_of_fixes_needs_a_green_gate_and_a_first_review_does_not(tmp_path: pathlib.Path) -> None:
    clone = _clone(tmp_path)
    _pool_map(clone, "inashiro")
    assert prereq.check(clone, ["inashiro"], "first look", gate_green=False, current=lambda g: True) == [], "a first review keeps feature 151's overlap"
    _verdict(clone, "inashiro", "NEEDS-WORK", "E1")
    _records(clone, **{"x": {"value": 1, "unit": "ft", "verifies": "E1", "subject": "inashiro", "quantity": "gap", "source": "svg ink"}})
    problems = prereq.check(clone, ["inashiro"], "verify the fix", gate_green=False, current=lambda g: True)
    assert [p for p in problems if p.startswith("FR-004")], problems
    assert prereq.check(clone, ["inashiro"], "verify the fix", gate_green=True, current=lambda g: True) == []


def test_the_cli_exits_nonzero_and_prints_each_reason(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    clone = _clone(tmp_path)
    _pool_map(clone, "mizuguchi")
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("The outfall now takes 166.6 ft to reach the pond.")
    monkeypatch.setattr(prereq, "_gencache_current", lambda: lambda g: True)
    assert prereq.main(["check", "--clone", str(clone), "--maps", "mizuguchi", "--prompt-file", str(prompt), "--gate-green", "yes"]) == 1
    assert "166.6 ft" in capsys.readouterr().out
    prompt.write_text("Look at the outfall.")
    assert prereq.main(["check", "--clone", str(clone), "--maps", "mizuguchi", "--prompt-file", str(prompt)]) == 0


def test_an_acceptance_needs_a_reason_and_a_real_finding_and_then_disposes_of_it(tmp_path: pathlib.Path) -> None:
    """FR-003's `accepted` disposition, held to an escape's floor and to the findings the verdict actually raised."""
    clone = _clone(tmp_path)
    _verdict(clone, "kuwabata", "NEEDS-WORK", "E2-byre")
    assert "REASON" in (prereq.accept(clone, "kuwabata", "E2-byre", "ok") or ""), "a bare token is refused"
    assert "raised no finding" in (prereq.accept(clone, "kuwabata", "E9", "left as village_grove documents it") or ""), "an id nobody reported"
    assert prereq.accept(clone, "kuwabata", "E2-byre", "crowns hug the eaves 2.2 ft off, as village_grove intends") is None
    assert prereq.unverified_findings(clone, "kuwabata") == [], "and the finding is dispositioned"
    assert prereq.accept(clone, "kuwabata", "E2-byre", "a second, revised reason for the same finding") is None
    assert len(json.loads((clone / ".git" / "review-dispositions" / "kuwabata.json").read_text())["accepted"]) == 1, "re-accepting replaces, never duplicates"
    assert prereq.main(["accept", "--clone", str(clone), "--map", "kuwabata", "--finding", "E2-byre", "--reason", "no"]) == 1
    assert prereq.main(["accept", "--clone", str(clone), "--map", "kuwabata", "--finding", "E2-byre", "--reason", "still left, as documented"]) == 0


def test_the_paired_gate_is_green_on_its_stamp_running_on_a_live_gate_target_and_red_otherwise(tmp_path: pathlib.Path) -> None:
    clone = _clone(tmp_path)
    assert prereq.gate_state(clone, fresh=lambda c: True, live=lambda c: []) == "green"
    assert prereq.gate_state(clone, fresh=lambda c: False, live=lambda c: ["done"]) == "running"
    # the reviewer's own `make review-paired-gate` is a live make in the clone too, and is not a gate
    assert prereq.gate_state(clone, fresh=lambda c: False, live=lambda c: ["review-paired-gate"]) == "red"
    assert prereq.gate_state(clone, fresh=lambda c: False, live=lambda c: []) == "red"


def test_the_verdict_record_copies_the_dispatch_key_and_a_red_gate_makes_it_not_reviewable(tmp_path: pathlib.Path) -> None:
    clone = _clone(tmp_path)
    (clone / ".git" / "pairing-state.json").write_text(json.dumps({"review_dispatch_key": "abc123"}))
    got, rec = prereq.write_verdict(clone, "m", "NEEDS-WORK", [{"severity": "error", "what": "canopy over the board"}], "green")
    assert got == "NEEDS-WORK" and rec["engine_key"] == "abc123" and rec["findings"][0]["id"] == "F1"
    assert prereq.recorded(clone, ["m"], "abc123") and not prereq.recorded(clone, ["m"], "other")
    # SC-006: green at dispatch, red by verdict time - recorded NOT-REVIEWABLE, and the pair stays open
    got, rec = prereq.write_verdict(clone, "m", "PASS", [], "red")
    assert got == "NOT-REVIEWABLE" and rec["concluded"] == "PASS"
    assert not prereq.recorded(clone, ["m"], "abc123")
    try:
        prereq.write_verdict(clone, "m", "LGTM", [], "green")
    except ValueError:
        pass
    else:
        raise AssertionError("an unknown verdict must not be recorded")


def test_the_verdict_cli_reads_a_findings_file(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    clone = _clone(tmp_path)
    (clone / ".git" / "pairing-state.json").write_text(json.dumps({"review_dispatch_key": "k"}))
    monkeypatch.setattr(prereq, "gate_state", lambda c: "green")
    f = tmp_path / "findings.json"
    f.write_text(json.dumps([{"id": "A", "severity": "flag", "what": "x"}]))
    assert prereq.main(["verdict", "--clone", str(clone), "--map", "m", "--verdict", "NEEDS-WORK", "--findings-file", str(f)]) == 0
    assert "recorded NEEDS-WORK for m" in capsys.readouterr().out
    assert prereq.unverified_findings(clone, "m") == ["A"]
    f.write_text("{}")
    assert prereq.main(["verdict", "--clone", str(clone), "--map", "m", "--verdict", "PASS", "--findings-file", str(f)]) == 2
    monkeypatch.setattr(prereq, "gate_state", lambda c: "red")
    assert prereq.main(["gate-state", "--clone", str(clone)]) == 0 and capsys.readouterr().out.strip().endswith("red")
