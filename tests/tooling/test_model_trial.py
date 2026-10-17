"""The model-trial tool's helpers on plain inputs (feature 383 amendment 3, plan D24; `scripts/measure/model_trial.py`)."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

from tests._scripts import script


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_model_trial", script("model_trial.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


mt = _load()


def test_the_tested_model_is_written_into_the_agent_file(tmp_path: pathlib.Path) -> None:
    f = tmp_path / "a.md"
    f.write_text("---\nname: a\nmodel: opus\neffort: high\n---\nbody model: here\n")
    mt.set_model(f, "claude-sonnet-5-5")
    assert f.read_text() == "---\nname: a\nmodel: claude-sonnet-5-5\neffort: high\n---\nbody model: here\n", "the frontmatter only"
    g = tmp_path / "b.md"
    g.write_text("---\nname: b\n---\nbody\n")
    mt.set_model(g, "x")
    assert "model: x" in g.read_text().split("\n---\n")[0]


def test_the_paths_a_prompt_names_outside_any_checkout() -> None:
    prompt = "Bundle: /tmp/l7r-check/x/MANIFEST.md. Read `/diagram/.clones/c/.git/review-snapshot/u/clone`, not /diagram/.clones/c/pool/m."
    assert mt.outside_paths(prompt) == ["/diagram/.clones/c/.git/review-snapshot/u/clone", "/tmp/l7r-check/x/MANIFEST.md"]


def test_a_clone_s_head_at_a_moment_comes_from_its_reflog(tmp_path: pathlib.Path) -> None:
    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(tmp_path), *a], capture_output=True, text=True, check=True).stdout.strip()

    git("init", "-q")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "a")
    first = git("rev-parse", "HEAD")
    when = float(git("log", "-g", "--date=unix", "--format=%gd", "HEAD").split("{")[1].rstrip("}"))
    assert mt.clone_head_at(tmp_path, when + 1) == first
    assert mt.clone_head_at(tmp_path, when - 100) == "", "before the reflog reaches"


def test_a_dispatch_is_read_back_from_the_recorded_transcript(tmp_path: pathlib.Path) -> None:
    unit = "building-review--x"
    body = f"UNIT: {unit}\nthe review.\nFollow it, then `make review-verdict ...`\nas your last act, and quote the line it prints.\n"
    lines = [
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "cat d"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "noise\n" + body}]}},
    ]
    t = tmp_path / "agent-x.jsonl"
    t.write_text("\n".join(json.dumps(x) for x in lines))
    assert mt.read_dispatch(t, unit) == body, "a cat serves as well as a Read"
    numbered = "\n".join(f"{i + 1:6}\t{ln}" for i, ln in enumerate(body.splitlines()))
    lines = [
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t2", "name": "Read", "input": {"file_path": f"/x/{unit}/dispatch.md"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t2", "content": numbered}]}},
    ]
    t.write_text("\n".join(json.dumps(x) for x in lines))
    assert mt.read_dispatch(t, unit) == body, "a Read's line numbers stripped"
