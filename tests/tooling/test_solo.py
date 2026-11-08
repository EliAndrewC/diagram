"""`scripts/hooks/lib/solo.py` - is this the only Claude Code session in the container (feature 444 T36; the GM 2026-11-07: "We
should make sure not to count our own subagents, of course")."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("l7r_solo", ROOT / "scripts" / "hooks" / "lib" / "solo.py")
assert _spec is not None and _spec.loader is not None
solo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(solo)

# a tmux server (1) running a parent session (10), which started this session (20); this session's hook (21) and a page session it
# started (22, under a bash 23); an unrelated session (30); a process of another name (40)
TREE = {1: (0, "tmux: server"), 10: (1, "claude"), 20: (10, "claude"), 23: (20, "bash"), 22: (23, "claude"), 21: (20, "bash"), 30: (1, "claude"), 40: (1, "python3")}


def test_a_session_it_started_is_its_own_and_another_or_its_parent_is_not() -> None:
    assert solo.session(TREE, 21) == 20, "the hook's session is its nearest claude ancestor"
    assert solo.others(TREE, 20) == [10, 30], "the page session (22) is this one's; the parent (10) and the unrelated (30) are others"
    alone = {1: (0, "tmux: server"), 20: (1, "claude"), 23: (20, "bash"), 22: (23, "claude")}
    assert solo.others(alone, 20) == [], "a session with only its own descendants is alone"
    assert solo.session(TREE, 40) is None and solo.others(alone, None) == [20, 22], "outside a session every claude is another"


def test_the_answer_is_kept_five_minutes_per_session(tmp_path: Path) -> None:
    calls: list[int] = []

    def procs() -> dict[int, tuple[int, str]]:
        calls.append(1)
        return {1: (0, "init"), 20: (1, "claude")}

    assert solo.solo(20, tmp_path, 1000.0, procs) is True
    assert solo.solo(20, tmp_path, 1000.0 + solo.CACHE_S - 1, lambda: TREE) is True and len(calls) == 1, "kept: no look"
    assert solo.solo(20, tmp_path, 1000.0 + solo.CACHE_S + 1, lambda: TREE) is False, "stale: looked again, and another runs"
    (tmp_path / next(p.name for p in tmp_path.glob("solo-*.json"))).write_text("not json", encoding="utf-8")
    assert solo.solo(20, tmp_path, 5000.0, procs) is True, "an unreadable cache is a miss"


def test_an_unwritable_cache_still_answers(tmp_path: Path) -> None:
    blocked = tmp_path / "file"
    blocked.write_text("", encoding="utf-8")
    assert solo.solo(20, blocked / "cache", 1.0, lambda: {20: (1, "claude")}) is True


def test_the_process_table_and_the_chain_read_a_proc_tree(tmp_path: Path) -> None:
    for pid, ppid, name in ((1, 0, "init"), (20, 1, "claude"), (21, 20, "odd) name (x")):
        (tmp_path / str(pid)).mkdir()
        (tmp_path / str(pid) / "stat").write_text(f"{pid} ({name}) S {ppid} 0 0\n", encoding="utf-8")
    (tmp_path / "99").mkdir()  # a process gone between the listing and the read
    (tmp_path / "self").mkdir()
    assert solo.processes(tmp_path) == {1: (0, "init"), 20: (1, "claude"), 21: (20, "odd) name (x")}
    assert solo.chain(21, tmp_path) == {21: (20, "odd) name (x"), 20: (1, "claude")}, "the chain stops at pid 1"


@pytest.mark.parametrize(("forced", "code"), [("1", 0), ("0", 1)])
def test_the_override_answers_without_looking(forced: str, code: int, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("L7R_SOLO", forced)
    assert solo.main([]) == code


def test_main_names_its_session_and_answers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_SOLO", raising=False)
    monkeypatch.setattr(solo.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(solo, "chain", lambda start: {start: (1, "bash")})
    monkeypatch.setattr(solo, "processes", lambda: {1: (0, "init")})
    assert solo.main([]) == 0, "no claude anywhere: alone"
