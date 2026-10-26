"""The impl-drift agent's rubric holds the round arbiter's rulings on how a claim is judged (it launches without CLAUDE.md)."""

from __future__ import annotations

from pathlib import Path

RUBRIC = (Path(__file__).resolve().parents[2] / ".claude" / "agents" / "impl-drift.md").read_text(encoding="utf-8")


def test_a_filed_departure_is_judged_once_never_relabeled() -> None:
    """ask:417-T49-claims (2026-10-26): a claim stating its departure and the open task carrying its fix is a known defect - DRIFTED
    with a `known (NNN Tnn)` note, and no further label asked of it (three rounds relabeled one bund claim)."""
    for term in ("A FILED DEPARTURE is judged once, never relabeled", "a departure the code keeps until", "`known (NNN Tnn): <the departure>`", "you ask for no other label"):
        assert term in RUBRIC, f"impl-drift.md no longer carries {term!r} (round arbiter, ask:417-T49-claims)"
