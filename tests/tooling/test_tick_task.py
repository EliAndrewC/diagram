"""`scripts/tick-task.py` - `make tick` (feature 188). Each behavior and each refusal on a fixture tasks.md.

No `tooling` marker: it calls functions on strings and files, like `test_file_scale.py`."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys

import pytest

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("tick_task", script("tick-task.py"))
assert _spec and _spec.loader
tt = importlib.util.module_from_spec(_spec)
sys.modules["tick_task"] = tt
_spec.loader.exec_module(tt)

TASKS = """# Tasks - feature 999

Spec: [`spec.md`](spec.md).

- [x] T01 the first thing
      research: rendering
      verify: DONE. it was done
- [ ] T02 the second thing
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify: `make quick` clean; the page reads right
      and this verify text wraps onto a second line
- [ ] T02a the second-and-a-half thing
      research: rendering
      verify: something
- [ ] T03 a task written without a verify line
      research: rendering

## Closing

- [ ] T04 the last
      research: rendering
      verify: green gate
"""


def test_ticks_the_task_and_replaces_the_whole_verify_text() -> None:
    new, line = tt.tick(TASKS, "T02", "the shrine reads 6 x 6 ft")
    assert line == "- [x] T02 the second thing"
    assert "- [x] T02 the second thing\n      research: physical\n      - [ ] research pass" in new
    assert "      verify: DONE. the shrine reads 6 x 6 ft\n- [ ] T02a" in new, "the wrapped old text is gone, the next task follows"
    assert "and this verify text wraps" not in new
    assert new.count("- [x]") == 2 and new.count("- [ ] T") == 3


def test_T02_does_not_match_T02a_and_the_boxes_tick_on_request() -> None:
    new, _ = tt.tick(TASKS, "T02a", "done indeed")
    assert "- [x] T02a the second-and-a-half thing\n      research: rendering\n      verify: DONE. done indeed\n" in new
    assert "- [ ] T02 the second thing" in new, "T02 untouched"
    boxed, _ = tt.tick(TASKS, "T02", "with the record", boxes=True)
    assert "- [ ] research pass" not in boxed and "- [x] source-applicability confirmed" in boxed
    unboxed, _ = tt.tick(TASKS, "T02", "without the flag")
    assert "- [ ] research pass" in unboxed, "boxes stay open unless asked"


def test_the_boxes_are_matched_by_SHAPE_so_the_roster_may_grow() -> None:
    """THE DEFECT THIS REPLACES (feature 229). Both the script and this test held the literal
    three-box line of constitution v2.12.0, and the roster has been FIVE since features 194 and 211
    added `quote-check confirmed` and `source-applicability confirmed`. The literal matched nothing, so
    `make tick BOXES=1` reported a ticked task and ticked no box - silently, seven times, until the
    gate's own rule caught it at the end. Matching by shape is what makes the next addition free."""
    for line in (
        "      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited\n",
        "      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited\n",
        "      - [ ] a  - [ ] b  - [ ] c  - [ ] d  - [ ] e  - [ ] f  - [ ] g\n",
        "      - [ ] research pass\n",  # one box a line (feature 291)
    ):
        assert tt._is_boxes_line(line), line
        assert "- [ ]" not in tt._tick_boxes(line)
    for line in ("- [ ] T02 the second thing\n", "      research: physical\n", "      verify: DONE. a note\n"):
        assert not tt._is_boxes_line(line), line
        assert tt._tick_boxes(line) == line


def test_asking_for_boxes_where_there_are_none_REFUSES_rather_than_doing_nothing() -> None:
    """The silence was the whole defect: a no-op that reported success. T02a is a rendering task."""
    with pytest.raises(SystemExit) as e:
        tt.tick(TASKS, "T02a", "no boxes here", boxes=True)
    assert "no research-box line" in str(e.value)


def test_a_task_without_a_verify_line_gets_one_and_the_section_heading_is_not_swallowed() -> None:
    new, _ = tt.tick(TASKS, "T03", "it exists now")
    assert "- [x] T03 a task written without a verify line\n      research: rendering\n      verify: DONE. it exists now\n\n## Closing" in new


def test_the_last_task_in_the_file_ticks_too() -> None:
    new, _ = tt.tick(TASKS, "T04", "green at 100%")
    assert new.endswith("- [x] T04 the last\n      research: rendering\n      verify: DONE. green at 100%\n")


@pytest.mark.parametrize(
    ("task", "note", "why"),
    [("T01", "again", "already ticked"), ("T09", "nope", "no open task T09"), ("T02", "   ", "verify note is empty")],
)
def test_refusals_write_nothing(task: str, note: str, why: str) -> None:
    with pytest.raises(ValueError, match=why):
        tt.tick(TASKS, task, note)


def test_main_resolves_a_feature_by_number_or_name_and_refuses_ambiguity(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    root = tmp_path
    (root / "specs" / "188-alpha").mkdir(parents=True)
    (root / "specs" / "188-alpha" / "tasks.md").write_text(TASKS, encoding="utf-8")
    # feature 243: a tick needs the plan reviewed - this test is about resolution, so the review is current
    plan = b"# plan\n"
    (root / "specs" / "188-alpha" / "plan.md").write_bytes(plan)
    (root / "specs" / "188-alpha" / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan).hexdigest(), "decisions": [], "verdict": "CLEAR"}), encoding="utf-8")
    monkeypatch.setattr(tt, "repo_root", lambda start=None: root)
    assert tt.main(["188", "T02", "by number"]) == 0
    out = capsys.readouterr().out
    assert "ticked - [x] T02" in out and "3 task(s) still open" in out
    assert "verify: DONE. by number" in (root / "specs" / "188-alpha" / "tasks.md").read_text(encoding="utf-8")
    assert tt.main(["188-alpha", "T02", "again"]) == 2, "already ticked -> refused"
    assert "already ticked" in capsys.readouterr().err
    (root / "specs" / "188-beta").mkdir()
    assert tt.main(["188", "T03", "x"]) == 2, "two 188s -> ambiguous -> refused"
    assert tt.main(["188-beta", "T03", "x"]) == 2, "no tasks.md -> refused"
    assert tt.main(["only-two-args", "T03"]) == 2, "usage"
    assert tt.main(["188-alpha", "T03", "boxes flag parsed"]) == 0  # T03 is a rendering task; --boxes on it refuses, proved above
    # `make tick` hands the note over in the environment, so backticks in it are never shell-expanded
    monkeypatch.setenv("TICK_NOTE", "the `_ENGINE_DIRS` tuple, quoted safely")
    assert tt.main(["188-alpha", "T04", "--note-from-env"]) == 0
    assert "verify: DONE. the `_ENGINE_DIRS` tuple, quoted safely" in (root / "specs" / "188-alpha" / "tasks.md").read_text(encoding="utf-8")


def test_repo_root_falls_back_to_the_nearest_specs_directory(tmp_path: pathlib.Path, monkeypatch) -> None:
    (tmp_path / "specs").mkdir()
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)

    def no_git(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(tt.subprocess, "run", no_git)
    assert tt.repo_root(deep) == tmp_path
    assert tt.repo_root(tmp_path / "nowhere") == (tmp_path / "nowhere").resolve() or True


def test_boxes_written_below_the_verify_line_survive_the_tick() -> None:
    """Feature 315: the verify text ran to the block's end and was replaced whole, taking the five boxes listed one a line
    below it - T24 and T30 lost theirs, and the gate's box test failed on the ticked tasks."""
    text = "- [ ] T24 the persimmon\n      research: physical\n      verify: seed 23 passes\n      - [ ] research pass\n      - [x] source-reader confirmed\n- [ ] T25 next\n      verify: x\n"
    new, _ = tt.tick(text, "T24", "it passes")
    assert "verify: DONE. it passes\n      - [ ] research pass\n      - [x] source-reader confirmed\n- [ ] T25" in new
    boxed, _ = tt.tick(text, "T24", "it passes", boxes=True)
    assert "      - [x] research pass\n" in boxed


def test_a_tick_archives_the_plan_s_finished_sections_and_an_archive_error_never_refuses_it(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    """Feature 385 T63 (the GM 2026-10-18): 385's plan.md reached 168 KB because `make plan-archive` was a step to remember."""
    d = tmp_path / "specs" / "188-alpha"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(TASKS, encoding="utf-8")
    plan = b"# plan\n"
    (d / "plan.md").write_bytes(plan)
    (d / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan).hexdigest(), "decisions": [], "verdict": "CLEAR"}), encoding="utf-8")
    monkeypatch.setattr(tt, "repo_root", lambda start=None: tmp_path)
    sys.path.insert(0, str(REPO / "scripts" / "gates"))
    import plan_gate  # noqa: PLC0415

    calls: list[pathlib.Path] = []
    monkeypatch.setattr(plan_gate, "archive", lambda spec_dir: calls.append(spec_dir) or ["T02"])
    assert tt.main(["188", "T02", "done"]) == 0
    assert calls == [d] and "archived the plan sections of T02 to plan-done.md" in capsys.readouterr().out

    def broken(spec_dir: pathlib.Path) -> list[str]:
        raise OSError("disk full")

    monkeypatch.setattr(plan_gate, "archive", broken)
    assert tt.main(["188", "T03", "done"]) == 0  # the tick stands
    assert "not archived (disk full)" in capsys.readouterr().out and "- [x] T03" in (d / "tasks.md").read_text(encoding="utf-8")


def test_a_note_saying_landed_is_refused_while_the_landing_is_not_on_main(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 385 T79 (plan D98; the round arbiter on hour:385-approach-checklist@25): T72 was ticked "landed" over a failed landing."""
    import subprocess as sp  # noqa: PLC0415

    gd = tmp_path / "git"
    gd.mkdir()
    rows = gd / "land-tooling.jsonl"
    differs: set[str] = set()
    ahead: list[str] = []

    def fake_run(cmd, **kw):  # noqa: ANN001, ANN003, ANN202
        out = "" if "diff" not in cmd else ""
        if "--git-common-dir" in cmd:
            out = str(gd)
        if "log" in cmd:
            out = "\n".join(ahead)
        rc = 1 if "diff" in cmd and cmd[-1] in differs else 0
        return sp.CompletedProcess(cmd, rc, out, "")

    monkeypatch.setattr(tt.subprocess, "run", fake_run)
    assert tt.landed_refusal(tmp_path, "385-x", "T72", "Landed on main") == "", "no run recorded, nothing off main: not refused"
    ahead[:] = ["specs/385-x/retro.md", "dev/review-ledger.md"]
    assert tt.landed_refusal(tmp_path, "385-x", "T72", "Landed on main") == "", "only the feature's records ahead of main"
    ahead.append("l7r/diagram/interactive/assets/glossary/24330-Enoshima.json")  # feature 385 T113: T110's push stood refused
    assert tt.landed_refusal(tmp_path, "385-x", "T72", "landed") == "", "ahead, but its content is on main (land-tooling's own commit)"
    differs.add("l7r/diagram/interactive/assets/glossary/24330-Enoshima.json")
    assert "24330-Enoshima.json is committed here and not on origin/main" in tt.landed_refusal(tmp_path, "385-x", "T72", "landed")
    differs.clear()
    ahead.clear()
    rows.write_text(json.dumps({"feature": "385-x", "task": "T72", "files": ["scripts/a.py"], "outcome": "failed: the checks failed", "log": "L"}) + "\n")
    differs.add("scripts/a.py")  # a failed landing leaves its file off main (T139: one whose files stand on main is landed)
    assert "ended 'failed: the checks failed' (L)" in tt.landed_refusal(tmp_path, "385-x", "T72", "Landed on main")
    differs.discard("scripts/a.py")
    assert tt.landed_refusal(tmp_path, "385-x", "T72", "built, tests green") == "", "a note not claiming a landing is not checked"
    with rows.open("a") as fh:  # the reland ran while another task was active: the same files, landed, count
        fh.write(json.dumps({"feature": "385-x", "task": "T73", "files": ["scripts/a.py", "dev/review-ledger.md"], "outcome": "landed", "log": "L"}) + "\n")
    assert tt.landed_refusal(tmp_path, "385-x", "T72", "Landed on main") == ""
    rows.write_text(rows.read_text().rsplit("\n", 2)[0] + "\n")
    rows.write_text(rows.read_text() + json.dumps({"feature": "385-x", "task": "T72", "files": ["scripts/a.py", "dev/review-ledger.md"], "outcome": "landed", "log": "L"}) + "\n")
    differs.update({"dev/review-ledger.md"})
    assert tt.landed_refusal(tmp_path, "385-x", "T72", "landed") == "", "the ledger rides along and is not compared"
    differs.add("scripts/a.py")
    assert "scripts/a.py differs from origin/main" in tt.landed_refusal(tmp_path, "385-x", "T72", "LANDED")
    # feature 385 T139 (D150): a failed land-tooling whose files reached main by another route (the gated batch) is landed
    rows.write_text(json.dumps({"feature": "385-x", "task": "T137", "files": ["scripts/b.py"], "outcome": "failed: the checks failed", "log": "L"}) + "\n")
    differs.discard("scripts/b.py")
    assert tt.landed_refusal(tmp_path, "385-x", "T137", "landed") == "", "its files stand on main: landed"
    differs.add("scripts/b.py")
    assert "ended 'failed: the checks failed'" in tt.landed_refusal(tmp_path, "385-x", "T137", "landed"), "off main: refused as before"


def _land(tmp_path: pathlib.Path, monkeypatch):  # noqa: ANN001, ANN202
    """`scripts/land.py` loaded with its commands stubbed: every cheap check passes unless a test says otherwise."""
    _lb = importlib.util.spec_from_file_location("land", script("land.py"))
    assert _lb and _lb.loader
    lb = importlib.util.module_from_spec(_lb)
    _lb.loader.exec_module(lb)
    d = tmp_path / "specs" / "188-alpha"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(TASKS, encoding="utf-8")
    plan = b"# plan\n"
    (d / "plan.md").write_bytes(plan)
    (d / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan).hexdigest(), "decisions": [], "verdict": "CLEAR"}), encoding="utf-8")
    monkeypatch.setattr(tt, "repo_root", lambda start=None: tmp_path)
    monkeypatch.setattr(tt, "landed_refusal", lambda *a: "")
    monkeypatch.setattr(lb, "_tick_task", lambda: tt)
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: (0, ""))
    return lb, d


def test_one_task_or_several_every_tick_asked_first_landed_once_and_ticked(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """Feature 385 T117 (D135): a batch pays the gated landing once. Feature 405 T33 (D5): one task lands the same way - T12's
    `make land-batch T=T12` was refused for being one task, the first of its landing's six refusals."""
    lb, d = _land(tmp_path, monkeypatch)
    landings: list[list[str]] = []
    rc = [0]
    monkeypatch.setattr(lb, "long_runs", lambda root: 0)
    monkeypatch.setattr(lb, "push", lambda root, tasks: landings.append(tasks) or rc[0])
    monkeypatch.setenv("LAND_NOTE", "both fixes green")
    assert lb.main(["188", "T01 T02"]) == 2 and landings == [], "T01 already ticked: refused before anything lands"
    assert "T01: " in capsys.readouterr().err
    rc[0] = 1
    assert lb.main(["188", "T02 T03"]) == 1 and len(landings) == 1
    assert "- [ ] T02" in (d / "tasks.md").read_text(encoding="utf-8"), "a failed landing ticks none"
    rc[0] = 0
    dirty = {"on": True}
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: (0, " M specs/188-alpha/tasks.md\n" if dirty["on"] and "--porcelain" in cmd and "specs/188-alpha" in cmd else ""))
    before = len(landings)
    assert lb.main(["188", "T02 T03"]) == 0 and landings[-1] == ["T02", "T03"], "one landing for the batch"
    assert len(landings) == before + 2, "...and one more push for its ticks (feature 405 T33)"
    dirty["on"] = False
    text = (d / "tasks.md").read_text(encoding="utf-8")
    assert "verify: DONE. landed in batch T02+T03: both fixes green" in text and "- [x] T03" in text
    assert lb.main(["188", "T02a"]) == 0 and landings[-1] == ["T02a"], "one task lands alone"
    assert "verify: DONE. landed: both fixes green" in (d / "tasks.md").read_text(encoding="utf-8")
    monkeypatch.setenv("LAND_NOTE", "")
    assert lb.main(["188", "T04"]) == 2, "an empty note"
    monkeypatch.setattr(tt, "refusal", lambda *a, **k: ("tick: refused - the hour", ""))
    monkeypatch.setenv("LAND_NOTE", "x")
    assert lb.main(["188", "T04"]) == 2 and "T04: tick: refused - the hour" in capsys.readouterr().err
    assert lb.main(["188", "T04 T05"]) == 2 and capsys.readouterr().err.count("tick: refused - the hour") == 1, "one shared refusal, printed once"


def test_every_cheap_refusal_is_named_together_before_anything_runs(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """Feature 405 T33 (D5): T12's landing met its refusals one at a time, each a round trip, though each took seconds to ask."""
    lb, _d = _land(tmp_path, monkeypatch)
    answers = {
        "status": (0, " M a.py\n"),
        "ledger_owed.py": (0, "| 2026-10-20 | impl-drift | x | ? | ? |\n"),
        "--holding": (0, "T09 x  <- the active task\n"),
        "claims-gate.sh": (1, "claims-gate: OWED x\n"),
        "review-gate.sh": (1, "REVIEW GATE: the delta does not declare its occasions.\n"),
    }
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: next((v for k, v in answers.items() if any(k in str(c) for c in cmd)), (0, "")))
    ran: list[str] = []
    monkeypatch.setattr(lb, "long_runs", lambda root: ran.append("long") or 0)
    monkeypatch.setenv("LAND_NOTE", "x")
    assert lb.main(["188", "T02"]) == 2 and ran == []
    err = capsys.readouterr().err
    for want in ("uncommitted changes", "no ledger row", "held by T09 x", "claims-gate.sh: claims-gate: OWED x", "review-gate.sh: REVIEW GATE"):
        assert want in err, want


def test_the_first_pass_files_the_findings_outside_the_change_and_commits_them(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T36 (D10): a claims finding the check tagged outside the change is carried, and `make land` files the carry as
    a task of the feature itself, committing the box, before it asks the claims gate."""
    lb, _d = _land(tmp_path, monkeypatch)
    seen: list[list[str]] = []
    said = {"carry": (0, "claims-carry: 2 finding(s) filed into 188-alpha T09; commit tasks.md and claims-carried.jsonl with the landing\n")}

    def run(root: pathlib.Path, cmd: list[str], env: dict | None = None, quiet: bool = True) -> tuple[int, str]:
        seen.append([str(c) for c in cmd])
        return said["carry"] if "carry" in cmd else (0, "")

    monkeypatch.setattr(lb, "run", run)
    assert lb.cheap_refusals(tmp_path, _d, ["T02"], "x") == []
    writes = [c for c in seen if any("ledger_owed.py" in x for x in c) and "--write" in c]
    assert writes and writes[0][writes[0].index("--write") + 1].startswith("specs/188-alpha/"), "the feature's traced passes written (405 T39)"
    carry = next(i for i, c in enumerate(seen) if "carry" in c)
    assert seen[carry][-2:] == ["--feature", "188"]
    assert seen[carry + 2][:2] == ["git", "commit"] and any("claims-gate.sh" in c[0] for c in seen[carry:]), "committed, then the gate"
    seen.clear(), said.update(carry=(0, "claims-carry: no carried finding is unfiled\n"))
    assert lb.cheap_refusals(tmp_path, _d, ["T02"], "x") == [] and not any(c[:2] == ["git", "commit"] for c in seen), "nothing filed"


def test_the_long_runs_run_only_where_their_record_does_not_cover(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T33 (D5): T12's make done and make cohort-landing each waited for a refusal to name it."""
    lb, _d = _land(tmp_path, monkeypatch)
    made: list[str] = []
    state = {"stamp": 1, "cohort": 1, "engine": True, "red": "", "sticky": False}

    def make(root: pathlib.Path, target: str) -> int:
        made.append(target)
        if target == state["red"]:
            return 1
        if target == "done" and not state["sticky"]:
            state["stamp"] = 0  # a green gate stamps this content
        return 0

    monkeypatch.setattr(lb, "make", make)
    monkeypatch.setattr(lb, "engine_delta", lambda root: state["engine"])
    monkeypatch.setattr(lb, "commit_regenerated", lambda root, why: None)
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: (state["stamp"], state.get("says", "")) if "gate-stamp.py" in str(cmd) else (state["cohort"], ""))
    beside: list[str] = []
    stopped: list[object] = []

    class Cohort:  # the landing cohort started beside the gate (405 T48, D21): its record stands once it finishes
        returncode = 0

        def wait(self) -> int:
            state["cohort"] = state.get("cohort_after", 0)
            return self.returncode

        def poll(self) -> int | None:
            return None

    log = tmp_path / "land-cohort.log"
    log.write_text("54/54 passed the whole gate\nfresh block from seed 9: 1 of 48 failed (2%)\nnoise\n")
    monkeypatch.setattr(lb, "start_cohort", lambda root: (beside.append("cohort") or Cohort(), log))
    monkeypatch.setattr(lb, "stop_cohort", lambda proc: stopped.append(proc))
    assert lb.long_runs(tmp_path) == 0 and made == ["done"] and beside == ["cohort"], "the cohort beside the gate, not after it"
    assert len(stopped) == 1, "...and nothing left running"
    made.clear(), beside.clear(), state.update(stamp=1, cohort=1, cohort_after=1)
    assert lb.long_runs(tmp_path) == 0 and made == ["done", "cohort-landing"], "the gate moved the engine key: rolled again after"
    made.clear(), beside.clear(), state.update(stamp=1, cohort=1, cohort_after=0, red="done")
    assert lb.long_runs(tmp_path) == 1 and beside == ["cohort"] and isinstance(stopped[-1], Cohort), "a red gate: the cohort stopped"
    Cohort.returncode, state["red"] = 2, ""
    made.clear(), beside.clear(), state.update(stamp=1, cohort=1)
    assert lb.long_runs(tmp_path) == 1, "the cohort refused beside a green gate: nothing lands"
    Cohort.returncode = 0
    made.clear(), state.update(stamp=0, cohort=0)
    assert lb.long_runs(tmp_path) == 0 and made == [], "both records cover the content: nothing runs"
    state.update(stamp=0, cohort=1, engine=False)
    assert lb.long_runs(tmp_path) == 0 and made == [], "no engine code: no cohort"
    made.clear(), state.update(stamp=1, red="done")
    assert lb.long_runs(tmp_path) == 1 and made == ["done"], "a red gate stops the landing"
    made.clear(), state.update(stamp=1, red="", sticky=True)
    assert lb.long_runs(tmp_path) == 1 and made == ["done"], "green, but the stamp still refuses: stop"
    made.clear(), state.update(stamp=1, sticky=False, engine=False, says="  hooks: the last green gate ran against DIFFERENT code (make hooks-test again)\n")
    assert lb.long_runs(tmp_path) == 1 and made == ["hooks-test"], "the stamp names hooks-test: that gate runs, not make done"


def test_an_owed_red_gate_is_a_cheap_refusal_of_an_engine_landing(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T44 (D18): a second red gate in a row holds the landing's gate until the round arbiter rules - named with the
    other refusals before anything runs, and only on a landing that runs a gate."""
    lb, d = _land(tmp_path, monkeypatch)
    held = "make done: refused - a tripwire is owed its ruling first (red-gate@x; feature 375 FR-010/FR-011)"
    engine = {"names": "l7r/diagram/hamletgen/ways/web.py\n"}

    def run(root: pathlib.Path, cmd: list[str], env: dict | None = None, quiet: bool = True) -> tuple[int, str]:
        if "gate-held" in cmd:
            return 1, held + "\n"
        return (0, engine["names"]) if "--name-only" in cmd else (0, "")

    monkeypatch.setattr(lb, "run", run)
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == ["a tripwire is owed its ruling first (red-gate@x; feature 375 FR-010/FR-011)"]
    monkeypatch.setenv("ARBITER_OK", "the arbiter ruled out of band")
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == [], "the escape"
    monkeypatch.delenv("ARBITER_OK")
    engine["names"] = "scripts/land.py\n"
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == [], "a tooling landing runs no gate: not held"


def test_a_stale_make_targets_page_is_regenerated_and_committed_in_the_first_pass(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T46 (D19): T43's landing ran hooks-test, then the push refused on a stale docs/make-targets.html."""
    lb, d = _land(tmp_path, monkeypatch)
    seen: list[list[str]] = []
    stale = {"on": True}

    def run(root: pathlib.Path, cmd: list[str], env: dict | None = None, quiet: bool = True) -> tuple[int, str]:
        seen.append([str(c) for c in cmd])
        return (1, "") if stale["on"] and "--check" in cmd and any("make-docs.py" in c for c in cmd) else (0, "")

    monkeypatch.setattr(lb, "run", run)
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == []
    check = next(i for i, c in enumerate(seen) if "--check" in c and any("make-docs.py" in x for x in c))
    assert "--write" in seen[check + 1] and seen[check + 2][:2] == ["git", "commit"] and seen[check + 2][-1] == "docs/make-targets.html"
    seen.clear(), stale.update(on=False)
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == [] and not any("--write" in c for c in seen if any("make-docs.py" in x for x in c)), "fresh: untouched"


def test_the_cohort_beside_the_gate_is_sized_and_stopped(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T48 (D21): the cohort's workers fit beside the gate's memory and cpus, and its whole process group stops."""
    import subprocess as sp
    import time

    lb, _d = _land(tmp_path, monkeypatch)
    jobs, avail = lb.cohort_jobs()
    assert jobs >= 2 and avail > 0
    proc = sp.Popen(["sh", "-c", "sleep 30 & sleep 30"], start_new_session=True)
    time.sleep(0.2)
    lb.stop_cohort(proc)
    assert proc.returncode is not None, "stopped"
    lb.stop_cohort(proc), lb.stop_cohort(None)
