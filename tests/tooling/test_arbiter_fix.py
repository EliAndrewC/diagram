"""An arbiter's tooling fix is made, not lost (feature 379, the GM 2026-10-10).

On 2026-10-10 the round arbiter ruled on the research clone's two overlapping red gates and wrote, in its `what`, "the gate
should refuse to start while another make done is running in the same clone. File that as a tooling row". Nothing filed it.
Each case is a step that let it be lost: the fix only in prose, nothing holding the session to it, nothing showing the GM.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

import pytest

from tests._scripts import script
from tests.tooling.test_modal_checks import _load

ha = _load("hm_arbiter")
cc = _load("close_check")

#: 378's ruling, replayed with its fix as the field (SC-001): the fix itself landed as scripts/gates/gate_lock.py
RULING_378 = {
    "ruling": "continue",
    "why": "The second trigger is the same event, since two gates ran at once in one clone.",
    "what": "Run exactly one make done, alone, in the foreground.",
    "tooling_fix": "the gate refuses to start while another make done is running in the same clone",
}
TRIGGER = "red-gate@2026-10-10T22:25:57Z"

def _clean_env() -> dict[str, str]:
    """The environment without the outer make's variables: a test run under `make arbiter-fix-done LAND=...` inherits LAND= through
    MAKEFLAGS, and a `make` the test runs would then land tooling for real (found 2026-10-18, T20's landing)."""
    import os

    return {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "MAKEOVERRIDES")}



@pytest.fixture
def root(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """A clone whose feature 900 has one task ticked and one open, a CLEAR plan review and its report."""
    monkeypatch.setattr(cc, "GRANDFATHERED", tmp_path / "none.txt")
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))
    r = tmp_path / "clone"
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    d = r / "specs" / "900-z"
    d.mkdir(parents=True)
    (d / "spec.md").write_text("# Feature 900\n")
    (d / "tasks.md").write_text("- [x] T01 a\n- [ ] T02 b\n      verify:\n- [ ] T03 c\n      verify:\n")
    plan = "# plan\n"
    (d / "plan.md").write_text(plan)
    (d / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan.encode()).hexdigest(), "plan_text": plan, "decisions": [], "verdict": "CLEAR"}))
    (d / "report.md").write_text("# report\n")
    (r / ".specify").mkdir()
    (r / ".specify" / "feature.json").write_text('{"feature_directory": "specs/900-z"}')
    (r / "tests" / "tooling").mkdir(parents=True)
    (r / "tests" / "tooling" / "test_gate_lock.py").write_text("def test_x():\n    pass\n")
    return r


def _tick(root: pathlib.Path, task: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(script("tick-task.py")), "900", task, "done it"], cwd=root, capture_output=True, text=True)


def test_the_fix_is_a_field_recorded_open_and_shown_to_the_gm(root: pathlib.Path) -> None:
    d = root / "specs" / "900-z"
    row = ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter", "2026-10-10T22:34:00Z")
    assert row["fix"] == "open" and row["tooling_fix"] == RULING_378["tooling_fix"]
    assert ha.open_fixes(d) == [(TRIGGER, RULING_378["tooling_fix"])]
    gm = json.loads((d / "gm-review.jsonl").read_text())
    assert gm["tooling_fix"] == RULING_378["tooling_fix"], "the GM sees the recommendation itself"
    assert list(ha.rulings(root)) == [TRIGGER]


def test_a_process_fault_names_its_fault_as_the_fix_and_files_nothing(root: pathlib.Path) -> None:
    d = root / "specs" / "900-z"
    with pytest.raises(ValueError, match="tooling_fix"):
        ha.record_ruling(root, "reversal:/a.md", {"ruling": "process-fault", "why": "an oscillation"}, "round-arbiter")
    ha.record_ruling(root, "reversal:/a.md", {"ruling": "process-fault", "why": "an oscillation", "tooling_fix": "the bundle keeps each round's reply"}, "round-arbiter")
    assert ha.open_fixes(d) == [("reversal:/a.md", "the bundle keeps each round's reply")]
    assert not (d / "found.jsonl").exists(), "the open item replaces the found row nothing enforced"


def test_an_open_fix_holds_every_tick_and_the_close(root: pathlib.Path) -> None:
    """SC-001, SC-002: on the old code this tick went through with the fix still open, as 378's T04 did at 18:49."""
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    r = _tick(root, "T02")
    assert r.returncode == 2 and "tooling fix is open" in r.stderr and TRIGGER in r.stderr
    assert "make arbiter-fix-done" in r.stderr and "make arbiter-fix-declined" in r.stderr
    assert "- [ ] T02" in (d / "tasks.md").read_text(), "a refused tick writes nothing"
    assert any("tooling fix is open" in why for why in cc.reasons(d, root / "specs")), "no route closes around it"


def test_made_with_its_test_it_settles_and_reaches_the_gm(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    with pytest.raises(ValueError, match="under tests/"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate", "scripts/x.py")
    with pytest.raises(ValueError, match="under tests/"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate")
    with pytest.raises(ValueError, match="two words"):
        ha.settle_fix(root, TRIGGER, "done", "done", "tests/tooling/test_gate_lock.py")
    with pytest.raises(ValueError, match="no open tooling fix"):
        ha.settle_fix(root, "red-gate@else", "done", "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py")
    with pytest.raises(ValueError, match="done or declined"):
        ha.settle_fix(root, TRIGGER, "maybe", "gate_lock.py refuses a second gate")
    # SC-004 (amendment 1, FR-006): made but not landed is not done
    with pytest.raises(ValueError, match="make land-tooling"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py")
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "tests"], check=True)
    subprocess.run([*git, "commit", "-qm", "the fix's test"], check=True)
    with pytest.raises(ValueError, match="not on main"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py")
    subprocess.run([*git, "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    monkeypatch.chdir(root)
    assert ha.main(["fix", "done", TRIGGER, "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py"]) == 0
    assert ha.open_fixes(d) == [] and _tick(root, "T02").returncode == 0
    rows = [json.loads(ln) for ln in (d / "gm-review.jsonl").read_text().splitlines()]
    assert rows[-1]["kind"] == "arbiter-fix-done" and rows[-1]["test"] == "tests/tooling/test_gate_lock.py"
    assert rows[-1]["tooling_fix"] == RULING_378["tooling_fix"] and "gate_lock.py" in rows[-1]["note"]
    assert ha.main(["fix", "done", TRIGGER, "again and again", "tests/tooling/test_gate_lock.py"]) == 1, "settled once"


def test_an_overhaul_is_declined_to_the_gm_never_filed(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    monkeypatch.chdir(root)
    assert ha.main(["fix", "declined", TRIGGER, "it rebuilds how every gate is scheduled"]) == 0
    row = json.loads((d / "gm-review.jsonl").read_text().splitlines()[-1])
    assert row["kind"] == "arbiter-fix-declined" and "rebuilds" in row["note"] and "test" not in row
    assert ha.open_fixes(d) == [] and not (d / "found.jsonl").exists()
    assert sorted(p.name for p in (root / "specs").iterdir()) == ["900-z"], "no feature filed"
    assert ha.fix_hold(d) == ""


def test_the_record_reads_through_noise_and_needs_a_feature(root: pathlib.Path) -> None:
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    (d / "arbiter.jsonl").write_text((d / "arbiter.jsonl").read_text() + "not json\n")
    assert ha.open_fixes(d) == [(TRIGGER, RULING_378["tooling_fix"])]
    assert ha.open_fixes(root / "specs" / "nowhere") == []
    (root / ".specify" / "feature.json").write_text("not json")
    with pytest.raises(ValueError, match="no active feature"):
        ha.settle_fix(root, TRIGGER, "declined", "it rebuilds every gate")


ab = _load("arbiter_bundle")


def test_a_process_question_goes_to_the_arbiter_first(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Amendment 2, SC-006 (the GM 2026-10-10: "things should go to the arbiter at the point where they were previously coming
    to me"): a regression the session cannot fix, put to the arbiter, is ruled once and lands on the GM's review."""
    d = root / "specs" / "900-z"
    (d / "request.md").write_text("the GM's words")
    monkeypatch.chdir(root)
    assert ha.main(["ask", "bad id!", "a real question here"]) == 2
    assert ha.main(["ask", "polder-regression", "fails"]) == 2, "the question needs two words"
    q = "the polder test fails on main too and cannot be fixed in this feature - waive it?"
    assert ha.main(["ask", "polder-regression", q]) == 0
    assert ha.owed(root)["ask:polder-regression"]["kind"] == "ask" and ha.blocking(root, "anything") == [], "it holds nothing"
    manifest = ab.bundle(root, "ask:polder-regression", tmp_path / "out").read_text()
    assert "## The question" in manifest and q in manifest
    ha.record_ruling(root, "ask:polder-regression", {"ruling": "accept", "why": "pre-existing and out of scope"}, "round-arbiter")
    assert json.loads((d / "gm-review.jsonl").read_text().splitlines()[-1])["trigger"] == "ask:polder-regression"
    assert ha.main(["ask", "polder-regression", q]) == 1, "one ruling per question"


def test_a_spec_review_trigger_points_the_arbiter_at_the_review_history(root: pathlib.Path, tmp_path: pathlib.Path) -> None:
    ha.trip(root, "round:spec-fidelity|900-z@6", "round", "spec-fidelity|900-z", "round 6 of specs/900-z's spec review")
    manifest = ab.bundle(root, "round:spec-fidelity|900-z@6", tmp_path / "out").read_text()
    assert "## Rounds - the spec review of 900-z" in manifest and "Review history" in manifest


def test_a_spec_ruling_stands_only_for_the_spec_it_ruled_on(root: pathlib.Path) -> None:
    """Amendment 2's plan review: an amended spec never ships on an earlier ruling, whichever clone pushes it."""
    d = root / "specs" / "900-z"
    ha.trip(root, "round:spec-fidelity|900-z#1@6", "round", "spec-fidelity|900-z", "round 6")
    row = ha.record_ruling(root, "round:spec-fidelity|900-z#1@6", {"ruling": "accept", "why": "the last round only reworded"}, "round-arbiter")
    assert row["spec_sha"] == ha.spec_body_sha(d) and ha.spec_ruled(d) == "round:spec-fidelity|900-z#1@6"
    (d / "spec.md").write_text((d / "spec.md").read_text() + "\n## Review history\n- the ruling recorded\n")
    assert ha.spec_ruled(d) and ha.main(["spec-ruled", str(d)]) == 0, "the Review history growing is no amendment"
    (d / "spec.md").write_text("# Feature 900\n**Status**: Done 2026-10-10 - landed\n" + (d / "spec.md").read_text().split("\n", 1)[1])
    assert ha.spec_ruled(d), "nor is a Status line rewritten at landing (plan review round 3)"
    (d / "spec.md").write_text("# Feature 900\n**Status**: Done 2026-10-10 - landed,\n  wrapped onto a second line\n")
    assert ha.spec_ruled(d), "nor a wrapped one (plan review round 4)"
    (d / "spec.md").write_text("# Feature 900, amended\n")
    assert ha.spec_ruled(d) == "" and ha.main(["spec-ruled", str(d)]) == 1
    (d / "arbiter.jsonl").write_text((d / "arbiter.jsonl").read_text() + "not json\n")
    assert ha.spec_ruled(root / "specs" / "nowhere") == ""


def _rounds(root: pathlib.Path, tmp_path: pathlib.Path, uids: tuple[str, ...], checks: tuple[str, ...] = ("modal-form",)) -> None:
    """Two kept rounds of each of `checks` (modal-form unless named) on each pop-up in `uids`, as the hooks record them in
    checks-open.json. A round trigger fires only when a dispatch is refused, so every check a test trips has rounds here: a
    round trigger with none is refused by the bundle (343's M1c rulings, 2026-10-11)."""
    disp, counted = {}, {}
    for i, uid in enumerate(uids):
        for c in checks:
            counted[f"{c}|modal:{uid}"] = 2  # the dispatch counter, as the hooks keep it: a named round is checked against it
            for r in (1, 2):
                reply = tmp_path / f"r-{i}-{c}-{r}.md"
                reply.write_text(f"1. finding {r} on {uid}\n")
                disp[f"t{i}{c}{r}"] = {"check": c, "subjects": [f"modal:{uid}"], "t": i * 10 + r, "state": "answered", "reply": str(reply)}
    feature = json.loads((root / ".specify" / "feature.json").read_text())["feature_directory"].rsplit("/", 1)[-1]
    (root / ".git" / "checks-open.json").write_text(json.dumps({"feature": feature, "rounds": counted, "dispatches": disp}))


def test_a_batch_at_the_cap_gets_one_bundle_and_one_ruling(root: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Feature 375 amendment 2, SC-009 (the GM 2026-10-11: "a whole batch of pop-ups reaching the round cap at once should get
    a single ruling"): every owed round trigger in one bundle, each with its rounds; one ruling, one exception, every trigger
    recorded and released, each a GM-review row."""
    d = root / "specs" / "900-z"
    _rounds(root, tmp_path, ("sheet/a", "sheet/b", "sheet/c"))
    trig = [f"round:modal-form|modal:sheet/{u}@3" for u in "abc"]
    for t in trig:
        ha.trip(root, t, "round", t[len("round:") : -2], "round 3")
    ha.trip(root, "red-gate", "red-gate", "", "two red gates")
    assert ab.batch_triggers(root) == trig, "round triggers only"
    manifest = ab.batch(root, tmp_path / "batch").read_text()
    assert all(f"`{t}`" in manifest for t in trig) and "ONE JSON object" in manifest and "BATCH=1" in manifest
    subs = sorted(p.read_text() for p in (tmp_path / "batch").glob("*/MANIFEST.md"))
    assert len(subs) == 3 and all("## Rounds - modal-form on modal:sheet/" in s and "finding 2 on" in s for s in subs)
    ruling = {"ruling": "accept", "why": "the form rounds only reword", "triggers": trig, "exceptions": {trig[1]: {"ruling": "continue", "why": "sheet/b's round 2 found a new gap"}}}
    with pytest.raises(PermissionError):
        ha.record_batch(root, ruling, "main")
    with pytest.raises(ValueError, match="does not carry"):
        ha.record_batch(root, {**ruling, "exceptions": {"round:x|y@3": {"ruling": "accept", "why": "w"}}}, "round-arbiter")
    with pytest.raises(ValueError, match="names its `triggers`"):
        ha.record_batch(root, {"ruling": "accept", "why": "w"}, "round-arbiter")
    rows = ha.record_batch(root, ruling, "round-arbiter")
    assert [r["ruling"] for r in rows] == ["accept", "continue", "accept"]
    assert set(ha.owed(root)) == {"red-gate"}, "each trigger released; the red gate not part of the batch"
    assert ha.closed(root, "round:modal-form|modal:sheet/a@") == "accept" and ha.continues(root, "round:modal-form|modal:sheet/b@") == 1
    assert sum(1 for ln in (d / "gm-review.jsonl").read_text().splitlines() if '"arbiter"' in ln) == 3
    with pytest.raises(ValueError, match="already ruled"):
        ha.record_batch(root, ruling, "round-arbiter")


def test_a_round_asked_ahead_of_the_guard_carries_its_rounds(root: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Feature 375 amendment 2, SC-010: 343's session asked the arbiter about form checks' third round before the cap recorded
    it, and each bundle reached the arbiter with no round history. The unit is read from the trigger."""
    _rounds(root, tmp_path, ("sheet/garden",))
    manifest = ab.bundle(root, "round:modal-form|modal:sheet/garden@3", tmp_path / "ahead").read_text()
    assert "(not in arbiter-owed.json)" in manifest and "## Rounds - modal-form on modal:sheet/garden" in manifest
    assert "finding 1 on sheet/garden" in manifest and "finding 2 on sheet/garden" in manifest
    assert ab.unit_of("round:modal-form|modal:sheet/garden@3") == "modal-form|modal:sheet/garden" and ab.unit_of("red-gate") == ""


def test_the_batch_command_line(root: pathlib.Path, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # noqa: ANN001
    monkeypatch.chdir(root)
    assert ab.main(["--root", str(root), "--batch", "--out", str(tmp_path / "b0")]) == 2 and "nothing to batch" in capsys.readouterr().err
    assert ab.main(["--root", str(root)]) == 2 and "BATCH=1" in capsys.readouterr().err
    _rounds(root, tmp_path, ("sheet/a",))
    ha.trip(root, "round:modal-form|modal:sheet/a@3", "round", "modal-form|modal:sheet/a", "round 3")
    assert ab.main(["--root", str(root), "--batch", "--out", str(tmp_path / "b1")]) == 0
    f = tmp_path / "ruling.json"
    f.write_text(json.dumps({"ruling": "accept", "why": "fine as it stands", "triggers": ["round:modal-form|modal:sheet/a@3"]}))
    assert ha.main(["ruled-batch", str(f), "--as", "main"]) == 2
    assert ha.main(["ruled-batch", str(f), "--as", "round-arbiter"]) == 0
    assert ha.main(["ruled-batch", str(f), "--as", "round-arbiter"]) == 1, "already ruled"
    assert "BATCH=1" in ha.refusal(["round:x|y@3"])


def test_the_tooling_steers_a_batch_to_one_ruling(root: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Feature 375 amendment 2, SC-009 (spec review round 1): 343's shape - pop-ups at the cap on two checks, one form round
    asked about ahead and named to join, a spec review's round apart. While the batch is owed the refusal names the batch and a
    single ruling is refused; the asked-ahead round joins the bundle, the spec review's round does not."""
    _rounds(root, tmp_path, ("sheet/a", "sheet/b"), ("modal-form", "modal-depiction", "modal-research"))
    owed_now = ["round:modal-depiction|modal:sheet/a@3", "round:modal-research|modal:sheet/a@3", "round:modal-depiction|modal:sheet/b@3"]
    for t in owed_now:
        ha.trip(root, t, "round", ha.unit_of(t), "round 3")
    ha.trip(root, "round:spec-fidelity|900-z#1@6", "round", "spec-fidelity|900-z", "round 6")
    ahead = "round:modal-form|modal:sheet/a@3"
    assert ha.batch_triggers(root) == sorted(owed_now), "a spec review's round is ruled alone"
    assert ha.batch_triggers(root, [ahead]) == sorted([*owed_now, ahead])
    text = ha.refusal([owed_now[0]], root)
    assert "3 round triggers are owed together" in text and "make arbiter-bundle BATCH=1" in text and "TRIGGERS=" in text
    assert "BATCH=1" not in ha.refusal(["round:spec-fidelity|900-z#1@6"], root).split("Several units")[0], "a spec round is named alone"
    with pytest.raises(ValueError, match="rule them together"):
        ha.record_ruling(root, owed_now[0], {"ruling": "accept", "why": "fine"}, "round-arbiter")
    ha.record_ruling(root, "round:spec-fidelity|900-z#1@6", {"ruling": "continue", "why": "one more round"}, "round-arbiter")
    manifest = ab.batch(root, tmp_path / "steer", "", (ahead,)).read_text()
    assert f"`{ahead}`" in manifest and "spec-fidelity" not in manifest and len(list((tmp_path / "steer").glob("*/MANIFEST.md"))) == 4
    rows = ha.record_batch(root, {"ruling": "accept", "why": "related and settled", "triggers": [*owed_now, ahead]}, "round-arbiter")
    assert {r["unit"] for r in rows} == {ha.unit_of(t) for t in [*owed_now, ahead]}, "the asked-ahead row keeps its unit"
    assert ha.owed(root) == {} and ha.closed(root, "round:modal-form|modal:sheet/a@") == "accept"


def test_a_batch_tooling_fix_is_one_fix_held_by_one_row(root: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """The plan review of 375's amendment 2: a batch `process-fault` records every trigger with its fix opened once; an
    exception on the first trigger does not drop the batch's fix; a reply with one bad exception writes nothing."""
    d = root / "specs" / "900-z"
    trig = [f"round:modal-form|modal:sheet/{u}@3" for u in "abc"]
    for t in trig:
        ha.trip(root, t, "round", ha.unit_of(t), "round 3")
    bad = {"ruling": "accept", "why": "w", "triggers": trig, "exceptions": {trig[2]: {"ruling": "maybe", "why": "w"}}}
    with pytest.raises(ValueError, match="one of"):
        ha.record_batch(root, bad, "round-arbiter")
    assert not (d / "arbiter.jsonl").exists(), "a bad row writes nothing"
    fault = {
        "ruling": "process-fault",
        "why": "the form rounds reverse each other",
        "tooling_fix": "the form check reads the drawing",
        "triggers": trig,
        "exceptions": {trig[0]: {"ruling": "accept", "why": "settled"}},
    }
    rows = ha.record_batch(root, fault, "round-arbiter")
    assert [r["ruling"] for r in rows] == ["accept", "process-fault", "process-fault"]
    assert rows[1]["tooling_fix"] == fault["tooling_fix"] and rows[2]["tooling_fix_on"] == trig[1] and "tooling_fix" not in rows[0]
    assert ha.open_fixes(d) == [(trig[1], fault["tooling_fix"])], "one fix, opened once, on the first trigger under the batch"
    with pytest.raises(ValueError, match="tooling_fix"):
        ha.record_ruling(root, "round:x|y@3", {"ruling": "process-fault", "why": "w", "tooling_fix_on": trig[1]}, "round-arbiter")


def test_a_batch_reply_is_refused_whole_and_never_drops_a_fix(root: pathlib.Path) -> None:
    """The plan review of 375's amendment 2, round 2: a repeated trigger writes no row; the batch's fix never overwrites an
    exception's own (it goes on the first exception without one); every exception carrying its own fix is ambiguous."""
    d = root / "specs" / "900-z"
    a, b = "round:modal-form|modal:sheet/a@3", "round:modal-form|modal:sheet/b@3"
    for t in (a, b):
        ha.trip(root, t, "round", ha.unit_of(t), "round 3")
    with pytest.raises(ValueError, match="named twice"):
        ha.record_batch(root, {"ruling": "accept", "why": "w", "triggers": [a, a, b]}, "round-arbiter")
    both = {
        "ruling": "accept",
        "why": "w",
        "tooling_fix": "F",
        "triggers": [a, b],
        "exceptions": {a: {"ruling": "process-fault", "why": "x", "tooling_fix": "G"}, b: {"ruling": "process-fault", "why": "y", "tooling_fix": "H"}},
    }
    with pytest.raises(ValueError, match="where does the batch's fix go"):
        ha.record_batch(root, both, "round-arbiter")
    assert not (d / "arbiter.jsonl").exists(), "a refused reply writes nothing"
    rows = ha.record_batch(root, {**both, "exceptions": {a: both["exceptions"][a], b: {"ruling": "continue", "why": "y"}}}, "round-arbiter")
    assert rows[0]["tooling_fix"] == "G" and rows[1]["tooling_fix"] == "F", "G kept; F on the first exception without a fix"
    assert sorted(ha.open_fixes(d)) == [(a, "G"), (b, "F")]


def test_several_fixes_one_change_made_settle_together(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """2026-10-11: 343 carried 36 open tooling fixes, many naming the same few bundle defects (one ruling each before the
    batch ruling). One command settles the ones a single change made; an unknown ID refuses the whole call, writing nothing."""
    d = root / "specs" / "900-z"
    a, b = "reversal:/a.md", "reversal:/b.md"
    for t in (a, b):
        ha.trip(root, t, "reversal", t, "A -> B -> A")
        ha.record_ruling(root, t, {"ruling": "process-fault", "why": "the bundle hid its rounds", "tooling_fix": f"bundle fix for {t}"}, "round-arbiter")
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "tests"], check=True)
    subprocess.run([*git, "commit", "-qm", "the test"], check=True)
    subprocess.run([*git, "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    monkeypatch.chdir(root)
    assert ha.main(["fix", "done", f"{a} reversal:/nope.md", "one bundle change", "tests/tooling/test_gate_lock.py"]) == 1
    assert len(ha.open_fixes(d)) == 2, "an unknown ID writes nothing"
    assert ha.main(["fix", "done", f"{a} {b}", "the bundle now carries every round", "tests/tooling/test_gate_lock.py"]) == 0
    assert ha.open_fixes(d) == []


def test_an_engine_fix_is_done_with_its_test_committed_and_lands_with_the_feature(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385: a fix in engine code cannot land first (`land-tooling` refuses engine files) and the tick it holds is the one
    that lets the feature land - a deadlock. With ENGINE=1 (`ARBITER_FIX_ENGINE`) it is done once its test is committed in the
    clone, and its row says it lands with the feature; uncommitted, or without the flag, it is still refused."""
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    monkeypatch.setenv("ARBITER_FIX_ENGINE", "1")
    with pytest.raises(ValueError, match="ENGINE=1"):
        ha.settle_fix(root, TRIGGER, "done", "rollcache keeps a crashed child's traceback", "tests/tooling/test_gate_lock.py")
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "tests"], check=True)
    subprocess.run([*git, "commit", "-qm", "the fix's test"], check=True)
    monkeypatch.delenv("ARBITER_FIX_ENGINE")
    with pytest.raises(ValueError, match="not on main"):
        ha.settle_fix(root, TRIGGER, "done", "rollcache keeps a crashed child's traceback", "tests/tooling/test_gate_lock.py")
    monkeypatch.setenv("ARBITER_FIX_ENGINE", "1")
    row = ha.settle_fix(root, TRIGGER, "done", "rollcache keeps a crashed child's traceback", "tests/tooling/test_gate_lock.py")
    assert "lands with the feature" in row["note"] and ha.open_fixes(d) == []


def test_one_command_lands_a_fix_and_settles_it(root: pathlib.Path) -> None:
    """Feature 385 amendment 5 (FR-018): T04 met the three-step order (land, settle, tick) as two refusals. `LAND=` runs
    land-tooling on the fix's files and its test, then settles; both refusals that named the steps name it."""
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    assert 'LAND="<the fix\'s files>" F=<feature> TICK=<the task>' in ha.fix_hold(root / "specs" / "900-z")
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests" / "test_x.py").write_text("def test_x():\n    pass\n")
    with pytest.raises(ValueError, match=r"the same make arbiter-fix-done with LAND="):
        ha.settle_fix(root, TRIGGER, "done", "the fix was built", "tests/test_x.py")
    repo = pathlib.Path(__file__).resolve().parents[2]
    dry = subprocess.run(["make", "-n", "-C", str(repo), "arbiter-fix-done", "ID=x", "NOTE=a b c d", "TEST=tests/t.py", "LAND=scripts/a.py"], capture_output=True, text=True, check=False, env=_clean_env()).stdout
    assert "scripts/land-tooling.sh scripts/a.py tests/t.py && git fetch -q origin &&" in dry
    ticked = subprocess.run(
        ["make", "-n", "-C", str(repo), "arbiter-fix-done", "ID=x", "NOTE=a b c d", "TEST=tests/t.py", "LAND=scripts/a.py", "F=385", "TICK=T18"], capture_output=True, text=True, check=False
    ).stdout
    assert 'fix done "x" "a b c d" "tests/t.py" && ' in ticked and '--no-print-directory tick F="385" T="T18"' in ticked, "lands, settles, ticks (whatever $(MAKE) expands to)"
    no_f = subprocess.run(["make", "-C", str(repo), "arbiter-fix-done", "ID=x", "NOTE=a b c d", "TEST=tests/t.py", "TICK=T18"], capture_output=True, text=True, check=False, env=_clean_env())
    assert no_f.returncode == 2 and "TICK= ticks a task of F=<feature>" in no_f.stderr
    plain = subprocess.run(["make", "-n", "-C", str(repo), "arbiter-fix-done", "ID=x", "NOTE=a b c d", "TEST=tests/t.py"], capture_output=True, text=True, check=False, env=_clean_env()).stdout
    line = next(ln for ln in plain.splitlines() if "hm_arbiter.py fix done" in ln)
    assert "land-tooling.sh" not in line, "without LAND= it settles alone"
