"""FR-013 (feature 375): the advisor takes no instructions, so the patterns it should see are in what it reads - CLAUDE.md.

The tripwires and the arbiter are the monitor; CLAUDE.md names them, so a session (and an advisor call reading the session)
knows a loop is the arbiter's to judge, and hands it `make arbiter-bundle`'s MANIFEST.
"""

from __future__ import annotations

from pathlib import Path

CLAUDE = (Path(__file__).resolve().parents[2] / "CLAUDE.md").read_text(encoding="utf-8")


def test_claude_md_names_the_tripwires_and_the_arbiter_s_bundle() -> None:
    for term in (
        "third round on one subject",
        "coming back",
        "second red gate in a row",
        "1.0 a changed line",
        "round-arbiter",
        "make arbiter-bundle",
        "make feature-report F=NNN WRITE=1",
        "make decide",
        "make gm-review",
    ):
        assert term in CLAUDE, f"CLAUDE.md no longer names {term!r} (feature 375 FR-013)"


def test_room_before_packing_is_the_rule_and_the_arbiter_asks_it() -> None:
    """The GM, 2026-10-12: give features more room before packing them against a number nobody researched - in CLAUDE.md for
    the session, and in the round arbiter's contract, which launches without CLAUDE.md, for every ruling."""
    arbiter = (Path(__file__).resolve().parents[2] / ".claude" / "agents" / "round-arbiter.md").read_text(encoding="utf-8")
    assert "Room before packing" in CLAUDE, "CLAUDE.md no longer carries the GM's room-before-packing rule (2026-10-12)"
    for term in ("Ask of every ruling: is this packing?", "FIRST route", "UNRESEARCHED, a GUESS, a CONVENTION or a convenience"):
        assert term in arbiter, f"round-arbiter.md no longer asks {term!r} (the GM, 2026-10-12)"
