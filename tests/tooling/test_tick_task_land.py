"""`make land` and its long runs (feature 188, 405), split from `test_tick_task.py` at the 1,000-line bar."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

from tests._scripts import script
from tests.tooling.test_tick_task import REPO, TASKS, VERIFIED, _land, tt


def test_a_stopped_landing_runs_its_cleanup(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T79: stopped with SIGTERM, a landing exited without its `finally`, leaving its gate and the cohort beside it
    running; it raises SystemExit on SIGTERM so the cleanup (`stop_cohort`) runs."""
    import signal

    lb, _d = _land(tmp_path, monkeypatch)
    got: dict = {}
    groups: list[int] = []
    monkeypatch.setattr(signal, "signal", lambda sig, fn: got.setdefault(sig, fn))
    monkeypatch.setattr(lb.os, "killpg", lambda pg, sig: groups.append(pg))
    monkeypatch.setenv("LAND_NOTE", "")
    assert lb.main(["188", "T02"]) == 2
    with pytest.raises(SystemExit) as stop:
        got[signal.SIGTERM]()
    assert stop.value.code == 143 and groups == [lb.os.getpgrp()], "the landing's group - its gate - stopped too"


def test_a_landing_is_found_by_its_python_process_not_the_shell_above_it(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """405 T90: the first process match was the recipe's `sh -c`, not the python, so the SIGTERM skipped the landing's cleanup
    and its gate ran on. Only a python running `scripts/land.py` in this tree is a landing."""
    lb, _d = _land(tmp_path, monkeypatch)
    root, other, proc = tmp_path / "tree", tmp_path / "other", tmp_path / "proc"
    root.mkdir()
    other.mkdir()
    for pid, args, cwd in (
        ("11", [b"/bin/sh", b"-c", b"python3 /t/scripts/land.py 405 T1"], root),
        ("12", [b"/usr/bin/python3", b"/t/scripts/land.py", b"405", b"T1"], root),
        ("13", [b"/usr/bin/python3", b"/t/scripts/land.py", b"405", b"T1"], other),
        ("14", [b"make", b"land"], root),
        ("self", [b"x"], root),
    ):
        (proc / pid).mkdir(parents=True)
        (proc / pid / "cmdline").write_bytes(b"\0".join(args) + b"\0")
        (proc / pid / "cwd").symlink_to(cwd)
    assert lb.landing_pids(root, proc) == [12]
    monkeypatch.setattr(lb.os, "getpid", lambda: 12)
    assert lb.landing_pids(root, proc) == [], "the stopping command's own python is no landing"
    assert lb.landing_pids(root, tmp_path / "none") == []


def test_a_physical_task_with_a_box_unticked_is_refused_before_it_is_ticked() -> None:
    """405 batch 8: 408's T01/T02 were ticked with four of five research boxes open, and only the gate's box test saw it -
    after the push, failing the next session's landing. The tick refuses it, unless the tick ticks them (BOXES=1)."""
    text = "- [ ] T01 a page\n      research: physical\n      - [x] research pass\n      - [ ] source-reader confirmed\n- [ ] T02 next\n      research: rendering\n"
    assert "BOXES=1" in tt.boxes_refusal(text, "T01")
    assert tt.boxes_refusal(text, "T01", boxes=True) == ""
    assert tt.boxes_refusal(text, "T02") == "", "a rendering task owes no boxes"
    assert tt.boxes_refusal(text.replace("- [ ] source", "- [x] source"), "T01") == ""
    assert tt.boxes_refusal(text, "T09") == ""


def test_land_passes_BOXES_on_to_the_tick(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 410 T01: `make land` refused a physical task with its research boxes open and pointed at BOXES=1, which it did
    not pass on - only a hand edit of tasks.md got it through."""
    lb, d = _land(tmp_path, monkeypatch)
    (d / "tasks.md").write_text(TASKS, encoding="utf-8")
    monkeypatch.delenv("LAND_BOXES", raising=False)
    refused = lb.cheap_refusals(tmp_path, d, ["T02"], "x")
    assert refused and "make land ... BOXES=1" in refused[0], "the refusal names the landing's own escape"
    assert lb._box_flag(tt, d, "T02") == []
    monkeypatch.setenv("LAND_BOXES", "1")
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == []
    assert lb._box_flag(tt, d, "T02") == ["--boxes"]
    (d / "tasks.md").write_text(VERIFIED, encoding="utf-8")
    assert lb._box_flag(tt, d, "T02") == [], "no open box: no --boxes, which would refuse"


def test_the_gate_s_own_lint_is_committed_and_any_other_change_left(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """The GM 2026-10-24: T07's landing waited out the claims wait's 20 min on a test whose imports the gate's `ruff check --fix`
    had sorted. A file that is its HEAD copy run through the gate's ruff is committed; a real edit is left for the wait to name."""
    import subprocess  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("land_real", script("land.py"))
    assert spec and spec.loader
    lb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lb)  # its commands real: the commit is asked of a real repository
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "pyproject.toml").write_text('[tool.ruff.lint]\nselect = ["I"]\n', encoding="utf-8")
    messy = "import sys\nimport os\n\nprint(os, sys)\n"
    (repo / "tests" / "test_a.py").write_text(messy, encoding="utf-8")
    (repo / "tests" / "test_b.py").write_text(messy, encoding="utf-8")
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
        subprocess.run(["git", "-C", str(repo), *cmd], check=True, env={**__import__("os").environ, **env})
    monkeypatch.setenv("GIT_AUTHOR_NAME", "t"), monkeypatch.setenv("GIT_AUTHOR_EMAIL", "t@t")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "t"), monkeypatch.setenv("GIT_COMMITTER_EMAIL", "t@t")
    (repo / "tests" / "test_a.py").write_text("import os\nimport sys\n\nprint(os, sys)\n", encoding="utf-8")  # the gate's sort
    (repo / "tests" / "test_b.py").write_text("import os\nimport sys\n\nprint(sys, os)\n", encoding="utf-8")  # an edit too
    assert lb.commit_gate_formatting(repo) == ["tests/test_a.py"]
    left = lb.run(repo, ["git", "status", "--porcelain"])[1]
    assert "test_a.py" not in left and "test_b.py" in left, "the sort committed, the edit left for the wait"
    assert lb.commit_gate_formatting(repo) == [], "nothing of the gate's left: no commit"


def test_the_changed_modules_coverage_runs_beside_the_gate_and_stops_it(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 415 (FR-004, D6; the GM 2026-10-24): `cover_changed.py` no longer runs before the gate (48 s on T26's landing)
    but beside it, and a refusal stops the gate at once and refuses the landing with its lines; COVER_OK skips it."""
    monkeypatch.delenv("COVER_OK", raising=False)  # a landing run with the escape set must not skip the check under test (417 T44)
    lb, d = _land(tmp_path, monkeypatch)
    seen: list[list[str]] = []
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: seen.append([str(c) for c in cmd]) or (0, str(tmp_path) if "rev-parse" in cmd else ""))
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == [] and not any("cover_changed.py" in " ".join(c) for c in seen), "not before the gate"
    monkeypatch.setattr(lb, "COVER_POLL_S", 0.01)
    # ...a STAND-IN for the check: the real one, started here inside a gate, found the repository and ran a nested coverage
    # run in it that overwrote the gate's own coverage data (415 T05's first gate: "no such table: context", 812 errors)
    (tmp_path / "gates").mkdir()
    (tmp_path / "gates" / "cover_changed.py").write_text("print('cover-changed: a stand-in')\n")
    monkeypatch.setattr(lb, "HERE", tmp_path)
    cover = lb.start_cover(tmp_path)
    assert cover is not None and cover[0] in lb.RUNNING
    cover[0].wait()
    lb.RUNNING.remove(cover[0])
    script = tmp_path / "Makefile"
    script.write_text("slow:\n\tsleep 30\nquick:\n\ttrue\n")

    class Refused:  # a check that has refused
        returncode = 1

        def poll(self) -> int:
            return 1

    log = tmp_path / "cover.log"
    log.write_text("cover-changed: l7r/x.py - added lines its tests (tests/x) do not reach: 3\nnoise\n")
    assert lb.cover_refusal((Refused(), log)) == "cover-changed: l7r/x.py - added lines its tests (tests/x) do not reach: 3"
    import time  # noqa: PLC0415

    t = time.monotonic()
    assert lb.run_gate(tmp_path, "slow", (Refused(), log)) == lb.COVER_STOPPED and time.monotonic() - t < 10, "the gate stopped at once"
    assert lb.run_gate(tmp_path, "quick", None) == 0 and not lb.RUNNING, "a gate with no check beside it runs to its end"
    monkeypatch.setenv("COVER_OK", "a line only the rolls reach")
    assert lb.start_cover(tmp_path) is None


def test_the_fresh_block_starts_after_the_push_under_a_lock(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 415 (FR-003, D5): the cohort's fresh block is a rate, never a refusal - it rolls after the push, under a lock a
    later landing's block waits on, never skipped."""
    lb, _d = _land(tmp_path, monkeypatch)
    started: list[list[str]] = []
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: (0, str(tmp_path)))
    monkeypatch.setattr(lb.subprocess, "Popen", lambda cmd, **kw: started.append(cmd) or None)
    log = lb.start_fresh_block(tmp_path)
    assert log == tmp_path / "land-fresh.log" and started[0][:2] == ["flock", str(tmp_path / "land-fresh.lock")]
    assert started[0][2:6] == ["make", "--no-print-directory", "cohort", "N=0"] and "FRESH=48" in started[0], "the fresh block alone"


def _cover():  # noqa: ANN202 - `gates/cover_changed.py` by path
    spec = importlib.util.spec_from_file_location("cover_changed", script("cover_changed.py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cover_changed_reads_the_mirrored_test_directory(tmp_path: pathlib.Path) -> None:
    cc = _cover()
    (tmp_path / "tests" / "a").mkdir(parents=True)
    assert cc.mirrored(tmp_path, "l7r/diagram/a/b.py") == "tests/a"
    assert cc.mirrored(tmp_path, "l7r/diagram/a/deep/c.py") == "tests/a", "climbs to the nearest that exists"
    assert cc.mirrored(tmp_path, "l7r/diagram/z/c.py") == "tests"
    (tmp_path / "tests" / "tooling" / "ci").mkdir(parents=True)
    assert cc.mirrored(tmp_path, "l7r/diagram/ci/incremental.py") == "tests/tooling/ci", "the gate's machinery is tested as tooling"
    assert "not rolls_map" in cc.WITH_TOOLING and "not rolls_map" in cc.WITHOUT_TOOLING, "no rolls (the lines asked: feature 430 T03)"


def test_the_coverage_check_writes_its_coverage_data_in_its_own_directory(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 415 T05's third red gate: beside a landing's gate, in the same tree, the check's run wrote `.coverage` files
    where the gate's workers wrote theirs; its data goes to its own temporary directory."""
    cc = _cover()
    seen: dict = {}

    def run(cmd, cwd=None, capture_output=True, text=True, env=None):  # noqa: ANN001, ANN202
        seen["env"], seen["cmd"] = env or {}, cmd
        rc = next(c.split("=", 1)[1] for c in cmd if c.startswith("--cov-config="))
        seen["rc"] = pathlib.Path(rc).read_text(encoding="utf-8")
        return type("R", (), {"stdout": "", "stderr": "", "returncode": 0})()

    monkeypatch.setattr(cc.subprocess, "run", run)
    monkeypatch.setenv("COVERAGE_FILE", "/elsewhere/.coverage")
    import contextlib  # noqa: PLC0415

    with contextlib.suppress(RuntimeError):  # no report written by the stand-in: the run itself is what is asked
        cc.uncovered(tmp_path, ["l7r/x.py"], None)
    data = pathlib.Path(next(ln.split("=", 1)[1].strip() for ln in seen["rc"].splitlines() if ln.startswith("data_file")))
    assert data.name == ".coverage" and tmp_path not in data.parents and str(data.parent) != str(pathlib.Path.cwd())
    assert "COVERAGE_FILE" not in seen["env"], "feature 430 T03: in a config file of its own, never the environment every child inherits"


def test_a_delta_changing_the_gates_machinery_runs_the_tooling_tests_not_a_gate(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """The round arbiter's process-fault on ask:430-machinery-gate (2026-10-26): a delta touching `land.py`, `scripts/gates/` or the
    Makefile whose green-gate stamp passes ran a `make done` the done recipe's reuse branch always short-circuits (the GM's
    2026-08-25 rule: scripts/ owe no make done) - no test ran, and land said a gate did. It now runs the tooling tests, and
    hooks-test where the hooks stamp is stale; a red one lands nothing. A docs delta runs neither."""
    lb, _d = _land(tmp_path, monkeypatch)
    made: list[str] = []
    ran: list[list[str]] = []
    delta = {"names": "scripts/gates/cover_changed.py\ndocs/x.md\n", "hooks_fresh": 0, "tooling_rc": 0}

    def run(root, cmd, env=None, quiet=True):  # noqa: ANN001, ANN202
        if "l7r-gate.sh" in str(cmd):
            return (delta["hooks_fresh"], "") if "--fresh" in cmd else (0, "")
        if cmd[:2] == ["git", "diff"]:
            return (0, delta["names"])
        if cmd[:1] == ["make"]:
            ran.append(cmd[2:])
            return (delta["tooling_rc"] if "test-file" in cmd else 0, "")
        return (0, "")

    monkeypatch.setattr(lb, "run", run)
    monkeypatch.setattr(lb, "run_gate", lambda root, target, cover: made.append(target) or 0)
    monkeypatch.setattr(lb, "start_cover", lambda root: None)
    monkeypatch.setattr(lb, "engine_delta", lambda root: False)
    monkeypatch.setattr(lb, "commit_regenerated", lambda root, why: None)
    assert lb.gate_machinery_delta(tmp_path) == ["scripts/gates/cover_changed.py"]
    assert lb.long_runs(tmp_path) == 0 and made == [] and ran == [["test-file", "FILE=tests/tooling"]], "no gate claimed: the tooling tests"
    ran.clear(), delta.update(hooks_fresh=1)
    assert lb.long_runs(tmp_path) == 0 and ran == [["hooks-test"], ["test-file", "FILE=tests/tooling"]], "a stale hooks stamp: hooks-test first"
    ran.clear(), delta.update(hooks_fresh=0, tooling_rc=1)
    assert lb.long_runs(tmp_path) == 1, "a red tooling test: nothing lands"
    ran.clear(), delta.update(names="docs/x.md\n", tooling_rc=0)
    assert lb.long_runs(tmp_path) == 0 and made == [] and ran == [], "a docs delta: the stamp decides"


def test_a_delta_of_scripts_runs_the_tooling_tests_that_name_them(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 446 T03 (2026-10-28): T02's `scripts/record/` delta was no gate machinery, so no tooling test ran and a stub of
    `owed` in `test_known_drift.py` broke on main. A delta of scripts now runs the tooling test files naming a changed script, and
    each changed tooling test; a red one lands nothing; a script no test names, and a docs delta, run none."""
    lb, _d = _land(tmp_path, monkeypatch)
    (tmp_path / "tests" / "tooling").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests" / "tooling" / "test_a.py").write_text("import claims_counters\n")
    (tmp_path / "tests" / "tooling" / "test_b.py").write_text("import claims_countersx\n")
    ran: list[list[str]] = []
    delta = {"names": "scripts/record/claims_counters.py\n", "rc": 0}

    def run(root, cmd, env=None, quiet=True):  # noqa: ANN001, ANN202
        if cmd[:2] == ["git", "diff"]:
            return (0, delta["names"])
        if cmd[:1] == ["make"]:
            ran.append(cmd[2:])
            return (delta["rc"], "")
        return (0, "")

    monkeypatch.setattr(lb, "run", run)
    monkeypatch.setattr(lb, "run_gate", lambda root, target, cover: 0)
    monkeypatch.setattr(lb, "start_cover", lambda root: None)
    monkeypatch.setattr(lb, "engine_delta", lambda root: False)
    monkeypatch.setattr(lb, "commit_regenerated", lambda root, why: None)
    assert lb.long_runs(tmp_path) == 0 and ran == [["test-file", "FILE=tests/tooling/test_a.py"]], "the test naming the script, by word"
    ran.clear(), delta.update(names="scripts/record/other.py\ntests/tooling/test_b.py\n")
    assert lb.long_runs(tmp_path) == 0 and ran == [["test-file", "FILE=tests/tooling/test_b.py"]], "a changed tooling test runs itself"
    ran.clear(), delta.update(names="scripts/record/claims_counters.py\n", rc=1)
    assert lb.long_runs(tmp_path) == 1, "a red one: nothing lands"
    ran.clear(), delta.update(names="scripts/record/other.py\ndocs/x.md\n", rc=0)
    assert lb.long_runs(tmp_path) == 0 and ran == [], "no tooling test names it: none run"


def test_a_counter_only_landing_rolls_no_fresh_block(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 446 FR-002: the fresh 48-seed block after the push follows an engine landing, never a counter-only one."""
    lb, _d = _land(tmp_path, monkeypatch)
    started: list[pathlib.Path] = []
    monkeypatch.setattr(lb, "start_fresh_block", lambda root: started.append(root) or root / "fresh.log")
    monkeypatch.setattr(lb, "_port", lambda root: "integrated")
    assert "counter-only" in lb.fresh_block_after(tmp_path, True, True) and started == []
    assert "fresh block started" in lb.fresh_block_after(tmp_path, True, False) and started == [tmp_path]
    assert lb.fresh_block_after(tmp_path, False, False) == ""
    monkeypatch.setattr(lb, "_port", lambda root: "rust-only")
    assert lb.fresh_block_after(tmp_path, True, False) == "" and started == [tmp_path], "no Python cohort at rust-only (444 T41)"
    asked: list[list[str]] = []
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: asked.append([str(c) for c in cmd]) or (0, ""))
    assert lb.counter_only(tmp_path) and asked[-1][-2:] == ["cohort", "counter-only"] and asked[-1][0].endswith("l7r-gate.sh")
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: (1, ""))
    assert not lb.counter_only(tmp_path)


def test_a_444_phase_task_lands_only_with_its_checklist_whole_and_ticked(tmp_path: pathlib.Path) -> None:
    """Feature 443 T06 (FR-010, SC-006): a `phase: <stage>` task of feature 444 is refused with no checklist, with one short of the
    template's eight boxes, and with one unticked; it passes ticked whole, and no other task or feature is read."""
    _lb = importlib.util.spec_from_file_location("land_phase", script("land.py"))
    assert _lb and _lb.loader
    lb = importlib.util.module_from_spec(_lb)
    _lb.loader.exec_module(lb)
    (tmp_path / ".specify" / "templates").mkdir(parents=True)
    template = (REPO / lb.PHASE_TEMPLATE).read_text(encoding="utf-8")
    (tmp_path / lb.PHASE_TEMPLATE).write_text(template)
    d = tmp_path / "specs" / "444-work-budget-program"
    (d / "phases").mkdir(parents=True)
    tasks = "- [ ] T01 rebuild the water frame\n      phase: water_frame\n      research: rendering\n- [ ] T02 the docs\n      research: rendering\n"
    assert lb.phase_refusal(tmp_path, d, tasks, "T02") == "", "a task with no phase line is not read"
    assert "no checklist at specs/444-work-budget-program/phases/water_frame.md" in lb.phase_refusal(tmp_path, d, tasks, "T01")
    ticked = template.replace("- [ ] ", "- [x] ")
    (d / "phases" / "water_frame.md").write_text(ticked.replace("- [x] 5. **Rebuild.**", "- [x] 5. **Rebuilt.**"))
    assert "lacks the box `5. **Rebuild.**`" in lb.phase_refusal(tmp_path, d, tasks, "T01"), "short of a box"
    (d / "phases" / "water_frame.md").write_text(ticked.replace("- [x] 7. ", "- [ ] 7. "))
    assert "has `7. **Audit review, MODE AUDIT.**` unticked" in lb.phase_refusal(tmp_path, d, tasks, "T01")
    (d / "phases" / "water_frame.md").write_text(ticked)
    assert lb.phase_refusal(tmp_path, d, tasks, "T01") == "", "ticked whole: it lands"
    other = tmp_path / "specs" / "443-x"
    other.mkdir()
    assert lb.phase_refusal(tmp_path, other, tasks, "T01") == "", "only feature 444's phases are held"
    assert len(lb._BOX.findall(template)) == 8, "the template holds the design's eight boxes"


def test_the_landing_asks_the_phase_refusal_with_its_other_cheap_refusals(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    lb, _d = _land(tmp_path, monkeypatch)
    d = tmp_path / "specs" / "444-work-budget-program"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(
        VERIFIED.replace("- [ ] T02a the second-and-a-half thing\n      research: rendering", "- [ ] T02a the second-and-a-half thing\n      research: rendering\n      phase: water_frame")
    )
    (tmp_path / ".specify" / "templates").mkdir(parents=True)
    (tmp_path / lb.PHASE_TEMPLATE).write_text((REPO / lb.PHASE_TEMPLATE).read_text(encoding="utf-8"))
    assert "phase: water_frame" in lb._task_block((d / "tasks.md").read_text(), "T02a")
    stops = lb.cheap_refusals(tmp_path, d, ["T02a"], "verified: the phase")
    assert any("no checklist at specs/444-work-budget-program/phases/water_frame.md" in s for s in stops), stops


def test_every_refusal_is_listed_together_not_the_first_of_a_chain(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 444 T20 (D2): the tick's checks were an `or`-chain, so T19's landing took four rounds, one refusal each. Each is
    asked now, and every refusal is listed, numbered, in one message; one refusal reads as before."""
    d = tmp_path / "specs" / "999-x"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(TASKS, encoding="utf-8")
    sys.path.insert(0, str(REPO / "scripts" / "gates"))
    import plan_door as plan_gate  # noqa: PLC0415
    import wording  # noqa: PLC0415

    monkeypatch.setattr(plan_gate, "tick_permitted", lambda *_a: (False, "the plan review is stale"))
    monkeypatch.setattr(tt, "waits_or_marks", lambda *_a: "")
    monkeypatch.setattr(tt, "checkpoint_hold", lambda *_a: "the hour's checkpoint")
    monkeypatch.setattr(tt, "_arbiter", lambda: type("A", (), {"fix_hold": staticmethod(lambda _d: "")}))
    monkeypatch.setattr(plan_gate, "approach_refusal", lambda *_a: "part B's items 8, 9 unanswered")
    monkeypatch.setattr(wording, "refusal", lambda *_a: "")
    why, message = tt.refusal(tmp_path, d, "T02", "done", landed=False)
    assert message == "" and why.startswith("tick: refused - \n  (1) the plan review is stale"), why
    assert "(2) T02 is a `research: physical` task" in why and "(3) the hour's checkpoint" in why and "(4) part B's items 8, 9" in why
    monkeypatch.setattr(plan_gate, "tick_permitted", lambda *_a: (True, "plan review current"))
    monkeypatch.setattr(tt, "checkpoint_hold", lambda *_a: "")
    monkeypatch.setattr(plan_gate, "approach_refusal", lambda *_a: "")
    assert tt.refusal(tmp_path, d, "T02", "done", landed=False)[0].startswith("tick: refused - T02 is a `research: physical`"), "one refusal: as before"
    assert tt.refusal(tmp_path, d, "T01", "done", landed=False) == ("", "plan review current"), "none: the plan gate's message alone"


def test_a_stale_coverage_exempt_entry_is_a_cheap_refusal(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 448 D4: a stale entry of `dev/coverage-exempt.json` is refused in seconds, naming its cure, not at the gate's floor."""
    lb, d = _land(tmp_path, monkeypatch)
    assert lb.stale_exempt_refusal(tmp_path) == ""
    (tmp_path / "dev").mkdir()
    (tmp_path / "dev" / "coverage-exempt.json").write_text(json.dumps({"entries": [{"path": "l7r/gone.py", "stages": ["sink"], "why": "t"}]}), encoding="utf-8")
    assert lb.cheap_refusals(tmp_path, d, ["T02"], "x") == ["dev/coverage-exempt.json names 1 stale entry (l7r/gone.py) - make coverage-exempt PRUNE=1"]
