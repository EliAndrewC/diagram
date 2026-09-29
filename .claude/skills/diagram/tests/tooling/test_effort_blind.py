"""`scripts/_effort_blind.py` (feature 293, FR-009): the two outputs of a task, stripped, labeled A/B, the key kept apart.

WHAT THESE PROVE. A planted run id, clone path, session id, commit trailer and effort setting are gone from every exported
file; `medium` in ordinary prose survives; the key names both runs and is not in the bundle; the A/B order follows the seed;
task R exports the research files, task I the diff, the moved pictures and notes and the last `make done` output; a task
without exactly two valid runs is refused.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_effort_blind", REPO / "scripts" / "_effort_blind.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


eb = _load()
FEATURE = "specs/293-effort-level-experiment"


def _git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def _clone(tmp: pathlib.Path, run_id: str, arm: str) -> tuple[pathlib.Path, str]:
    clone = tmp / "clones" / f"diagram-exp-{run_id}"
    (clone / "research" / "buildings").mkdir(parents=True)
    (clone / "pool" / "hamlets").mkdir(parents=True)
    (clone / "README").write_text("start\n")
    _git("init", "-q", "-b", "main", cwd=clone)
    _git("add", "-A", cwd=clone)
    _git("commit", "-qm", "start", cwd=clone)
    start = _git("rev-parse", "HEAD", cwd=clone)
    (clone / "research" / "buildings" / "900-servants.html").write_text(f"<p>A medium-sized room in {clone}; run {run_id} ran with --effort {arm}, effort: {arm}; xhigh noted.</p>\n")
    (clone / "pool" / "hamlets" / "inashiro.png").write_bytes(b"\x89PNG fake")
    (clone / "pool" / "hamlets" / "inashiro.notes.md").write_text(f"path added by diagram-exp-{run_id}\n")
    (clone / "l7r.py").write_text(f"WIDTH = 4  # {run_id}\n")
    _git("add", "-A", cwd=clone)
    _git("commit", "-qm", f"the path\n\nCo-Authored-By: Claude <noreply@anthropic.com>\nrun {run_id}", cwd=clone)
    return clone, start


def _world(tmp: pathlib.Path, task: str) -> dict:
    repo = tmp / "session"
    fdir = repo / FEATURE
    (fdir / "runs").mkdir(parents=True)
    (fdir / "rubrics").mkdir()
    (fdir / eb.RUBRIC[task]).write_text("# rubric\n")
    _git("init", "-q", "-b", "main", cwd=repo)
    projects = tmp / "projects"
    for run_id, arm in (("e1", "medium"), ("e2", "xhigh")):
        clone, start = _clone(tmp, run_id, arm)
        (fdir / "runs" / f"{run_id}.json").write_text(json.dumps({"run_id": run_id, "task": task, "arm": arm, "clone": str(clone), "start_commit": start, "status": "valid"}))
        project = projects / str(clone).replace("/", "-").replace(".", "-")
        project.mkdir(parents=True)
        recs = [
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"d-{run_id}", "name": "Bash", "input": {"command": "make done"}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": f"d-{run_id}", "content": f"gate: green in {clone} sid-{run_id}"}]}},
        ]
        (project / f"sid-{run_id}.jsonl").write_text("\n".join(json.dumps(r) for r in recs) + "\nnot json\n")
    (fdir / "runs" / "e3.json").write_text(json.dumps({"run_id": "e3", "task": task, "status": "void"}))
    return {"repo": repo, "projects": projects}


def _all_text(bundle: pathlib.Path) -> str:
    return "\n".join(p.read_text(errors="replace") for p in bundle.rglob("*") if p.is_file() and p.suffix != ".png")


@pytest.mark.parametrize("task", ["R", "I"])
def test_nothing_that_names_the_arm_or_the_run_reaches_the_bundle(tmp_path: pathlib.Path, task: str) -> None:
    w = _world(tmp_path, task)
    bundle, key = eb.blind(w["repo"], task, 11, tmp_path / "out", w["projects"])
    text = _all_text(bundle)
    for leak in ("diagram-exp-e1", "diagram-exp-e2", "--effort medium", "effort: xhigh", "xhigh", "Co-Authored-By", "sid-e1", str(tmp_path / "clones")):
        assert leak not in text, leak
    assert "e1" not in text.replace("<", " ") or "run <run>" in text
    assert sorted([key["A"], key["B"]]) == ["e1", "e2"] and key["seed"] == 11
    assert "e1" not in (bundle / "MANIFEST.md").read_text() and (bundle / "rubric.md").is_file()
    assert json.loads((w["repo"] / ".git" / "effort-keys" / f"{task}.json").read_text()) == key
    assert not list(bundle.rglob("*.json")), "the key is not in the bundle"
    if task == "R":
        assert "A medium-sized room" in text, "ordinary prose keeps the word"
        assert {p.name for p in bundle.rglob("*.html")} == {"900-servants.html"}
    else:
        assert (bundle / "A" / "changes.diff").is_file() and "WIDTH = 4" in text and "gate: green in <clone> <session>" in text
        assert {p.name for p in bundle.rglob("inashiro.*")} == {"inashiro.png", "inashiro.notes.md"}
        assert "900-servants" in (bundle / "A" / "changes.diff").read_text()


def test_the_order_follows_the_seed_and_a_rerun_replaces_the_bundle(tmp_path: pathlib.Path) -> None:
    w = _world(tmp_path, "R")
    orders = {tuple(eb.blind(w["repo"], "R", s, tmp_path / "out", w["projects"])[1].values())[:2] for s in range(12)}
    assert orders == {("e1", "e2"), ("e2", "e1")}


def test_a_task_without_two_valid_runs_is_refused(tmp_path: pathlib.Path) -> None:
    w = _world(tmp_path, "R")
    (w["repo"] / FEATURE / "runs" / "e2.json").unlink()
    with pytest.raises(SystemExit, match="1 valid runs"):
        eb.blind(w["repo"], "R", 1, tmp_path / "out", w["projects"])


def test_the_command_prints_only_the_manifest_path(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    w = _world(tmp_path, "I")
    monkeypatch.chdir(w["repo"])
    assert eb.main(["--task", "I", "--seed", "2", "--out", str(tmp_path / "o"), "--projects", str(w["projects"])]) == 0
    assert capsys.readouterr().out.strip() == str(tmp_path / "o" / "I" / "MANIFEST.md")
    assert eb.last_done_summary([]) == ""
