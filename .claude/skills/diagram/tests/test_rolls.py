"""The roster of rolled hamlets (`tests/rolls.py`, feature 213): well formed, and every key unique."""

from __future__ import annotations

from collections import Counter

from tests import rolls


def test_every_roster_key_is_unique_and_every_row_says_what_it_carries() -> None:
    keys = Counter(r.key for r in rolls.ROLLS)
    dup = [k for k, n in keys.items() if n > 1]
    assert dup == [], f"two roster rows share a (name, seed): {dup}"
    for r in rolls.ROLLS:
        assert len(r.carries) > 20, f"{r.key}: a roll must say what it uniquely carries"
        assert r.rolled_by, f"{r.key}: a roll must say where it is requested from"
    assert rolls.by_key()[("Inashiro", 4)].spec.households == 15


def test_every_stated_duplicate_and_exception_points_at_something_real() -> None:
    keys = set(rolls.by_key())
    for d in rolls.DUPLICATES:
        assert d.key in keys, f"a stated duplicate must be of a rostered spec: {d.key}"
        assert d.test.startswith("tests/") and "::" in d.test and d.reason
    for e in rolls.IN_PROCESS:
        assert e.module.startswith("tests/") and e.module.endswith(".py") and e.reason
