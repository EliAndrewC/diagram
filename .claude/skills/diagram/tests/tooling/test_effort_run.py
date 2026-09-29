"""`scripts/_effort_run.py` (feature 293): the effort experiment's launcher and the controls it enforces.

WHAT THESE PROVE. The pre-flight record is written once; every refusal fires on its own condition and nothing starts; the
memory gate reads the working set plus the measured offset (R5 D7); the arm reaches the session only as `--effort`, never as
`CLAUDE_CODE_EFFORT_LEVEL` (R1 D1); every session carries the one pinned `--agents` JSON (R1 D2); each run gets its own copy
of the sources snapshot (R6 D4) and a record of the claims file as it found it (R6 D6). Nothing here starts a real session:
`claude` and `page-session.sh` are fakes that record their argv and environment.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import subprocess
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_effort_run", REPO / "scripts" / "_effort_run.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


er = _load()
FEATURE = "specs/293-effort-level-experiment"
FAKE_CLAUDE = "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$FAKE_OUT/claude.argv\"\nenv > \"$FAKE_OUT/claude.env\"\n"
FAKE_PAGE_SESSION = "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$FAKE_OUT/page.argv\"\nenv > \"$FAKE_OUT/page.env\"\necho 'page-session: started'\n"


def _git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def _cgroup(tmp: pathlib.Path, current: int, inactive: int) -> pathlib.Path:
    cg = tmp / "cgroup"
    cg.mkdir(parents=True, exist_ok=True)
    (cg / "memory.current").write_text(f"{current}\n")
    (cg / "memory.stat").write_text(f"anon 1\nfile 9\ninactive_file {inactive}\nactive_file 3\n")
    return cg


@pytest.fixture
def world(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    """An origin repository holding the feature's frozen files and a fake page-session, a snapshot to copy, fakes on PATH."""
    origin = tmp_path / "origin"
    fdir = origin / FEATURE
    for rel in [*er.RUBRICS, *(p for ps in er.PROMPTS.values() for p in ps)]:
        (fdir / rel).parent.mkdir(parents=True, exist_ok=True)
        (fdir / rel).write_text(f"# {rel}\n", encoding="utf-8")
    (origin / "scripts").mkdir()
    (origin / "scripts" / "page-session.sh").write_text(FAKE_PAGE_SESSION)
    (origin / "scripts" / "page-session.sh").chmod(0o755)
    (origin / "container-scripts").mkdir()
    (origin / er.APPEND_PROMPT).write_text("STANDING AUTHORIZATION\n")
    _git("init", "-q", "-b", "main", cwd=origin)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=origin)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "start", cwd=origin)
    home = tmp_path / "sources-home"
    home.mkdir()
    (home / "sources-consulted.jsonl").write_text('{"url": "u"}\n')
    (home / "page-cache" / "ab").mkdir(parents=True)
    (home / "page-cache" / "ab" / "meta.json").write_text("{}")
    (home / "claims.jsonl").write_text("not a sources file\n")
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    (bin_ / "claude").write_text(FAKE_CLAUDE)
    (bin_ / "claude").chmod(0o755)
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.setenv("PATH", f"{bin_}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_OUT", str(out))
    monkeypatch.setenv("CLAUDE_CODE_EFFORT_LEVEL", "max")
    monkeypatch.setenv("SPECIFY_FEATURE", "293-effort-level-experiment")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    claims = tmp_path / "CLAIMS.md"
    claims.write_text("- 280 towns\n- 293 servants' quarters (run e0) | claim released\n")
    events = tmp_path / "events"
    events.mkdir()
    return {"origin": origin, "fdir": fdir, "home": home, "out": out, "tmp": tmp_path, "claims": claims, "events": events, "start": _git("rev-parse", "HEAD", cwd=origin)}


def _init(w: dict, seed: int = 7) -> dict:
    ns = argparse.Namespace(start=w["start"], seed=seed, offset=0.9, sources_home=str(w["home"]), snapshot=str(w["tmp"] / "snap"))
    return er.init(ns, w["origin"], 1_000_000.0)


def _run_args(w: dict, task: str, run: str = "e1", arm: str = "xhigh", ws_gb: float = 2.0) -> argparse.Namespace:
    cg = _cgroup(w["tmp"] / f"cg-{run}-{ws_gb}", int((ws_gb + 1) * er.GB), er.GB)
    return argparse.Namespace(
        task=task, run=run, arm=arm, order=1, origin=str(w["origin"]), clones=str(w["tmp"] / "clones"), claims=str(w["claims"]), cgroup=str(cg), events=str(w["events"]), host_diag=""
    )


def test_init_records_what_every_run_shares_once(world: dict) -> None:
    exp = _init(world)
    assert exp["start_commit"] == world["start"] and exp["offset_gb"] == 0.9
    assert set(exp["hashes"]) == {*er.RUBRICS, "prompts/R-write.md", "prompts/R-check.md", "prompts/I.md"}
    assert exp["agents_sha256"] == er.sha256(er.agents_json()) and exp["sources_snapshot_sha256"]
    assert (pathlib.Path(exp["sources_snapshot"]) / "sources-consulted.jsonl").is_file()
    snap = pathlib.Path(exp["sources_snapshot"])
    assert (snap / "page-cache" / "ab" / "meta.json").is_file() and not (snap / "claims.jsonl").exists(), "the sources only"
    with pytest.raises(er.Refused, match="written once"):
        _init(world)


def test_the_arms_alternate_between_the_tasks() -> None:
    for seed in range(20):
        order = er.arm_order(seed)
        assert sorted(order["R"]) == sorted(er.ARMS) and order["I"] == order["R"][::-1]
    assert {tuple(er.arm_order(s)["R"]) for s in range(20)} == {("medium", "xhigh"), ("xhigh", "medium")}


def test_the_working_set_leaves_out_inactive_page_cache(tmp_path: pathlib.Path) -> None:
    assert er.working_set(_cgroup(tmp_path, 9_230, 1_810)) == 7_420
    (tmp_path / "cgroup" / "memory.stat").write_text("anon 5\n")
    assert er.working_set(tmp_path / "cgroup") == 9_230, "no inactive_file line: the raw figure"


def test_a_warning_is_fresh_for_15_minutes(tmp_path: pathlib.Path) -> None:
    assert er.fresh_warning(tmp_path / "missing", 0.0) == ""
    ev = tmp_path / "events"
    ev.mkdir()
    (ev / "9.txt").write_text("LOW MEMORY WARNING")
    mtime = (ev / "9.txt").stat().st_mtime
    assert er.fresh_warning(ev, mtime + 60) == "9.txt"
    assert er.fresh_warning(ev, mtime + er.WARNING_FRESH_S + 1) == ""


def test_each_refusal_fires_on_its_own_condition(world: dict) -> None:
    exp = _init(world)
    fdir, now = world["fdir"], time.time()
    ok = _run_args(world, "I")
    assert er.refusal(exp, fdir, "I", pathlib.Path(ok.cgroup), world["events"], now)[0] == ""
    high = _run_args(world, "I", ws_gb=3.7)
    why, reading = er.refusal(exp, fdir, "I", pathlib.Path(high.cgroup), world["events"], now)
    assert "retry later" in why and reading["working_set_gb"] == 3.7, "3.7 + 0.9 is over 4.5"
    assert er.refusal(exp, fdir, "Z", pathlib.Path(ok.cgroup), world["events"], now)[0] == "no task Z"
    (world["events"] / "9.txt").write_text("warning")
    assert "memwatch warning" in er.refusal(exp, fdir, "I", pathlib.Path(ok.cgroup), world["events"], time.time())[0]
    (world["events"] / "9.txt").unlink()
    bad_agents = exp | {"agents_sha256": "x"}
    assert "--agents" in er.refusal(bad_agents, fdir, "I", pathlib.Path(ok.cgroup), world["events"], now)[0]
    (fdir / "rubrics" / "research.md").write_text("edited after the freeze\n")
    assert "rubrics/research.md" in er.refusal(exp, fdir, "I", pathlib.Path(ok.cgroup), world["events"], now)[0]
    (fdir / "rubrics" / "research.md").write_text("# rubrics/research.md\n")
    (fdir / "runs").mkdir()
    (fdir / "runs" / "e1.json").write_text(json.dumps({"ended": None}))
    assert "e1" in er.refusal(exp, fdir, "I", pathlib.Path(ok.cgroup), world["events"], now)[0]


def test_task_i_is_one_full_session_at_the_arm_effort_with_the_pinned_judge(world: dict) -> None:
    _init(world)
    rec = er.launch(_run_args(world, "I", run="e1", arm="medium"), world["origin"], time.time())
    for _ in range(100):
        if (world["out"] / "claude.env").exists() and (world["out"] / "claude.env").read_text():
            break
        time.sleep(0.05)
    argv = (world["out"] / "claude.argv").read_text().split("\n")
    env = (world["out"] / "claude.env").read_text()
    assert argv[argv.index("--effort") + 1] == "medium" and argv[argv.index("-n") + 1] == "diagram-exp-e1"
    assert argv[argv.index("--agents") + 1] == er.agents_json()
    assert argv[argv.index("--append-system-prompt") + 1] == "STANDING AUTHORIZATION"
    assert "CLAUDE_CODE_EFFORT_LEVEL" not in env, "R1 D1: the env var would override the checkers' pinned effort"
    assert f"L7R_SOURCES_HOME={world['tmp']}/clones/.runs-293/e1/sources" in env and "SPECIFY_FEATURE" not in env
    assert rec["arm"] == "medium" and rec["sessions"][0]["effort"] == "medium" and rec["ended"] is None
    assert "<prompts/I.md sha256" in " ".join(rec["argv"]), "the record names the prompt by hash"
    assert rec["shared_state"]["claims_lines_at_start"] == ["- 293 servants' quarters (run e0) | claim released"]
    saved = json.loads((world["fdir"] / "runs" / "e1.json").read_text())
    assert saved["run_id"] == "e1" and saved["memory_at_launch"]["working_set_gb"] == 2.0
    with pytest.raises(er.Refused, match="live or unmeasured"):
        er.launch(_run_args(world, "I", run="e2"), world["origin"], time.time())


def test_task_r_is_the_two_page_sessions_through_the_runner_with_effort_and_agents(world: dict) -> None:
    _init(world)
    rec = er.launch(_run_args(world, "R", run="e3", arm="xhigh"), world["origin"], time.time())
    argv = (world["out"] / "page.argv").read_text().split("\n")
    clone = world["tmp"] / "clones" / "diagram-exp-e3"
    assert argv[0] == f"{clone}/handoffs/293/R-write.md {clone}/handoffs/293/R-check.md", "a neutral path (FR-004)"
    assert (clone / "handoffs" / "293" / "R-write.md").read_text() == (clone / FEATURE / "prompts" / "R-write.md").read_text()
    assert argv[1:4] == ["diagram-exp-e3", "", "xhigh"] and pathlib.Path(argv[4]).read_text() == er.agents_json()
    assert "CLAUDE_CODE_EFFORT_LEVEL" not in (world["out"] / "page.env").read_text()
    assert [s["effort"] for s in rec["sessions"]] == ["xhigh", "xhigh"] and "page-session: started" in rec["runner_stdout"]
    assert _git("rev-parse", "HEAD", cwd=clone) == world["start"]


def test_a_used_run_id_and_a_refusing_runner_start_nothing(world: dict) -> None:
    _init(world)
    (world["tmp"] / "clones" / "diagram-exp-e5").mkdir(parents=True)
    with pytest.raises(er.Refused, match="used once"):
        er.launch(_run_args(world, "I", run="e5"), world["origin"], time.time())
    (world["origin"] / "scripts" / "page-session.sh").write_text("#!/bin/sh\necho 'page-session: no brief' >&2\nexit 2\n")
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "refuse", cwd=world["origin"])
    exp = json.loads((world["fdir"] / "experiment.json").read_text())
    exp["start_commit"] = _git("rev-parse", "HEAD", cwd=world["origin"])
    (world["fdir"] / "experiment.json").write_text(json.dumps(exp))
    with pytest.raises(er.Refused, match="page-session refused: page-session: no brief"):
        er.launch(_run_args(world, "R", run="e6"), world["origin"], time.time())
    assert not (world["fdir"] / "runs" / "e6.json").exists()
    assert not (world["tmp"] / "clones" / "diagram-exp-e6").exists() and not (world["tmp"] / "clones" / ".runs-293" / "e6").exists()


def test_claims_at_start_without_a_claims_file(tmp_path: pathlib.Path) -> None:
    assert er.claims_at_start(str(tmp_path / "none")) == {"claims_sha256_at_start": None, "claims_lines_at_start": []}


def test_the_command_line_refuses_and_reports(world: dict, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(world["origin"])
    snap = str(world["tmp"] / "snap2")
    assert er.main(["init", "--start", world["start"], "--seed", "3", "--offset", "0.9", "--sources-home", str(world["home"]), "--snapshot", snap]) == 0
    assert "experiment recorded" in capsys.readouterr().out
    assert er.main(["init", "--start", world["start"], "--seed", "3", "--offset", "0.9", "--sources-home", str(world["home"]), "--snapshot", snap + "x"]) == 2
    assert "REFUSED" in capsys.readouterr().err
    a = _run_args(world, "R", run="e7")
    assert (
        er.main(
            [
                "run",
                "--task",
                "R",
                "--run",
                "e7",
                "--arm",
                "medium",
                "--order",
                "1",
                "--origin",
                a.origin,
                "--clones",
                a.clones,
                "--claims",
                a.claims,
                "--cgroup",
                a.cgroup,
                "--events",
                a.events,
                "--host-diag",
                "",
            ]
        )
        == 0
    )
    assert "e7 started (R)" in capsys.readouterr().out
    (world["fdir"] / "runs" / "e7.json").write_text(json.dumps({"ended": "done"}))
    assert (
        er.main(
            [
                "run",
                "--task",
                "I",
                "--run",
                "e8",
                "--arm",
                "xhigh",
                "--order",
                "2",
                "--origin",
                a.origin,
                "--clones",
                a.clones,
                "--claims",
                a.claims,
                "--cgroup",
                a.cgroup,
                "--events",
                a.events,
                "--host-diag",
                "",
            ]
        )
        == 0
    )
    assert "transcript" in capsys.readouterr().out


def test_the_shared_cgroup_is_read_through_the_host_tool(tmp_path: pathlib.Path) -> None:
    """R5 D7 revised: the cap is one host cgroup; its working set is `memory.current` less `inactive_file`."""
    assert er.parse_working_set("8584552448\nanon 1\ninactive_file 4388712448\n") == 8584552448 - 4388712448
    assert er.parse_working_set("") is None and er.parse_working_set("12\nanon 1\n") is None
    tool = tmp_path / "host-diag"
    tool.write_text("#!/bin/sh\nprintf '9000\\nfile 5\\ninactive_file 4000\\n'\n")
    tool.chmod(0o755)
    assert er.shared_working_set(str(tool)) == 5000
    tool.write_text("#!/bin/sh\nexit 255\n")
    assert er.shared_working_set(str(tool)) is None, "an unreachable host falls back"
    assert er.shared_working_set(str(tmp_path / "missing")) is None


def test_with_the_shared_figure_the_gate_reads_it_and_a_raw_warning_does_not_block(world: dict) -> None:
    exp = _init(world)
    cg = pathlib.Path(_run_args(world, "I", ws_gb=4.4).cgroup)
    (world["events"] / "12.txt").write_text("LOW MEMORY WARNING")
    why, reading = er.refusal(exp, world["fdir"], "I", cg, world["events"], time.time(), shared=int(4.2 * er.GB))
    assert why == "" and reading == {"source": "shared-slice", "working_set_gb": 4.2, "offset_gb": 0.0, "threshold_gb": er.THRESHOLD_GB, "fresh_warning": ""}
    why, _ = er.refusal(exp, world["fdir"], "I", cg, world["events"], time.time(), shared=int(4.6 * er.GB))
    assert "4.6 GB (shared-slice)" in why
    why, reading = er.refusal(exp, world["fdir"], "I", cg, world["events"], time.time())
    assert "memwatch warning" in why and reading["source"] == "container+offset", "without the host: the old rule"
