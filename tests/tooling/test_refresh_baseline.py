"""The baseline refreshed off the landing's path (feature 415 T05, D8; FR-006)."""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sqlite3
import time

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("refresh_baseline", script("refresh_baseline.py"))
assert _spec and _spec.loader
rb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rb)


def _baseline(d: pathlib.Path, root: str) -> None:
    d.mkdir(parents=True)
    con = sqlite3.connect(str(d / "coverage.db"))
    con.execute("create table file (id integer primary key, path text)")
    con.executemany("insert into file (path) values (?)", [(f"{root}/l7r/a.py",), (f"{root}/l7r/b.py",), ("/elsewhere/c.py",)])
    con.commit()
    con.close()
    (d / "manifest.json").write_text("{}", encoding="utf-8")


def test_a_refreshed_baseline_is_installed_with_its_paths_rewritten_unless_a_newer_one_stands(tmp_path: pathlib.Path) -> None:
    """The worktree's coverage paths move under the clone's root; a clone baseline saved after the refresh started stands."""
    src, dst = tmp_path / "wt-git" / "gate-baseline", tmp_path / "clone-git" / "gate-baseline"
    _baseline(src, "/tmp/wt")
    _baseline(dst, "/clone")
    started = time.time() - 60
    os.utime(dst / "manifest.json", (started - 10, started - 10))
    assert rb.install(src, dst, pathlib.Path("/tmp/wt"), pathlib.Path("/clone"), started) == "installed, 2 coverage path(s) rewritten"
    paths = sorted(p for (p,) in sqlite3.connect(str(dst / "coverage.db")).execute("select path from file"))
    assert paths == ["/clone/l7r/a.py", "/clone/l7r/b.py", "/elsewhere/c.py"]
    assert "stands" in rb.install(src, dst, pathlib.Path("/tmp/wt"), pathlib.Path("/clone"), started), "the clone's is newer now"
    assert rb.install(tmp_path / "none", dst, pathlib.Path("/tmp/wt"), pathlib.Path("/clone"), time.time() + 60) == "the refresh saved no baseline"
    assert rb.main([]) == 2


def test_a_refresh_is_due_when_this_landings_gate_selected_a_quarter_of_its_baseline(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """D8: an incremental landing gate that selected at least `REFRESH_FRACTION` of its baseline owes a refresh; under it, a full
    run, or a result older than the landing, does not."""
    from tests.tooling.test_tick_task import _land

    lb, _d = _land(tmp_path, monkeypatch)
    gd = tmp_path / "git"
    (gd / "gate-baseline").mkdir(parents=True)
    monkeypatch.setattr(lb, "run", lambda root, cmd, env=None, quiet=True: (0, str(gd)))
    (gd / "gate-baseline" / "tests.json").write_text(json.dumps({f"t::{i}": [] for i in range(100)}), encoding="utf-8")
    res = gd / "gate-baseline" / "result.json"
    since = time.time() - 5
    res.write_text(json.dumps({"mode": "incremental", "selected": [f"t::{i}" for i in range(30)]}), encoding="utf-8")
    assert lb.refresh_due(tmp_path, since) == "refresh: 30 of 100 baseline tests selected"
    res.write_text(json.dumps({"mode": "incremental", "selected": [f"t::{i}" for i in range(20)]}), encoding="utf-8")
    assert lb.refresh_due(tmp_path, since) == "", "under a quarter"
    res.write_text(json.dumps({"mode": "full", "selected": [f"t::{i}" for i in range(90)]}), encoding="utf-8")
    assert lb.refresh_due(tmp_path, since) == "", "a full run is itself the baseline"
    res.write_text(json.dumps({"mode": "incremental", "selected": [f"t::{i}" for i in range(90)]}), encoding="utf-8")
    assert lb.refresh_due(tmp_path, time.time() + 60) == "", "an older run's result"
    started: list[list[str]] = []
    monkeypatch.setattr(lb.subprocess, "Popen", lambda cmd, **kw: started.append(cmd) or None)
    assert lb.start_refresh(tmp_path, "refresh: x") == gd / "land-refresh.log" and started[0][1].endswith("refresh_baseline.py")
