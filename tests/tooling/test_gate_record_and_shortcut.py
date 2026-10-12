"""Feature 375 amendment 7: the gate commits its own run record (FR-033, SC-026), its shortcut runs `hooks-test` when that
stamp is stale (FR-032, SC-025), and `make perf` runs no census (FR-030, SC-023)."""

from __future__ import annotations

import os
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "gates" / "commit-run-record.sh"


def _git(d: pathlib.Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True).stdout


def _repo(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "r"
    d.mkdir()
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@t")
    _git(d, "config", "user.name", "t")
    (d / "a.txt").write_text("a\n", encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    return d


def _run(d: pathlib.Path, result: str = "green", pointer: str = "", **env: str) -> subprocess.CompletedProcess[str]:
    e = {k: v for k, v in os.environ.items() if k != "CODEBUILD_BUILD_ID"} | env
    return subprocess.run(["bash", str(SCRIPT), result, *([pointer] if pointer else [])], cwd=d, capture_output=True, text=True, env=e, check=False)


def _point(d: pathlib.Path, path: pathlib.Path, pointer: str = "last-run-record") -> None:
    (d / ".git" / pointer).write_text(str(path), encoding="utf-8")


def test_the_record_is_committed_alone_and_the_sessions_staged_work_stays_staged(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path)
    rec = d / "dev" / "run-log" / "2026-10" / "20261012T000000000000-1.json"
    rec.parent.mkdir(parents=True)
    rec.write_text('{"result": "green"}\n', encoding="utf-8")
    other = d / "dev" / "run-log" / "2026-10" / "remote-entry.json"
    other.write_text("{}\n", encoding="utf-8")
    _point(d, rec)
    (d / "a.txt").write_text("the session's edit\n", encoding="utf-8")
    _git(d, "add", "a.txt")
    (d / "b.txt").write_text("untracked work\n", encoding="utf-8")
    p = _run(d)
    assert p.returncode == 0 and "record committed (green)" in p.stdout
    assert _git(d, "log", "-1", "--format=%s").strip() == "the gate's run record (green)"
    assert _git(d, "show", "--name-only", "--format=", "HEAD").split() == ["dev/run-log/2026-10/20261012T000000000000-1.json"]
    status = _git(d, "status", "--porcelain")
    assert "M  a.txt" in status and "?? b.txt" in status, "the session's staged and untracked work are left as they were"
    assert "remote-entry.json" in status, "another writer's file under dev/run-log is not this run's record (the plan review)"
    assert not (d / ".git" / "last-run-record").exists(), "the pointer is spent"


def test_a_cohort_record_in_the_clone_is_committed_from_a_worktree(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path)
    wt = tmp_path / "base"
    _git(d, "worktree", "add", "-q", "--detach", str(wt))
    rec = d / "dev" / "cohort-log" / "x.json"
    rec.parent.mkdir(parents=True)
    rec.write_text("{}\n", encoding="utf-8")
    gitdir = pathlib.Path(_git(wt, "rev-parse", "--absolute-git-dir").strip())
    (gitdir / "last-cohort-record").write_text(str(rec), encoding="utf-8")
    p = _run(wt, "pass", "last-cohort-record")
    assert p.returncode == 0 and _git(d, "log", "-1", "--format=%s").strip() == "the cohort's record (pass)"


def test_nothing_to_commit_and_a_build_and_no_repository_do_nothing(tmp_path: pathlib.Path) -> None:
    d = _repo(tmp_path)
    head = _git(d, "rev-parse", "HEAD")
    assert _run(d).returncode == 0 and _git(d, "rev-parse", "HEAD") == head, "no pointer: no commit"
    rec = d / "dev" / "run-log" / "x.json"
    rec.parent.mkdir(parents=True)
    rec.write_text("{}\n", encoding="utf-8")
    _point(d, rec)
    assert _run(d, CODEBUILD_BUILD_ID="b-1").returncode == 0 and _git(d, "rev-parse", "HEAD") == head, "a build's checkout is not the session's"
    _point(d, d / "gone.json")
    assert _run(d).returncode == 0 and _git(d, "rev-parse", "HEAD") == head, "a pointer to nothing commits nothing"
    outside = tmp_path / "plain"
    outside.mkdir()
    assert _run(outside).returncode == 0


def _recipe(target: str) -> str:
    text = (REPO / "Makefile").read_text(encoding="utf-8").split("\n")
    start = next(i for i, ln in enumerate(text) if ln.startswith(f"{target}:"))
    end = next(i for i in range(start + 1, len(text)) if text[i] and not text[i].startswith(("\t", "#")))
    return "\n".join(text[start:end])


def test_the_shortcut_runs_hooks_test_when_its_stamp_is_stale_and_every_outcome_commits_its_record() -> None:
    done = _recipe("done")
    shortcut = done[done.index("verified-done") : done.index("already verified - nothing the gate exercises")]
    assert "--fresh hooks" in shortcut and "hooks-test" in shortcut, "FR-032: a stale hooks stamp is earned, not skipped"
    assert shortcut.index("--fresh hooks") < shortcut.index("already-verified;"), "...before the shortcut answers green"
    assert done.count("$(COMMIT_RUN_RECORD)") == 6, "already-verified, its hooks failure, the reference failure, both red sites and green"


def test_make_perf_runs_no_census() -> None:
    perf = _recipe("perf")
    assert "census" not in "\n".join(ln for ln in perf.split("\n") if ln.startswith("\t")), "FR-030: the census only when asked"
    assert "overlap_census" in _recipe("census")
