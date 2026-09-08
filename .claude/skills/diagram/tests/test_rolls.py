"""The roster of rolled hamlets (`tests/rolls.py`, feature 213): well formed, and every key unique."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

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


def test_every_pool_gen_names_a_shipped_generator_and_only_the_sweep_may_roll_it() -> None:
    skill = Path(__file__).resolve().parents[1]
    keys = Counter(p.key for p in rolls.POOL_GENS)
    assert [k for k, n in keys.items() if n > 1] == []
    for p in rolls.POOL_GENS:
        assert (skill / p.gen).is_file(), p.gen
        assert p.test == rolls.POOL_TEST and p.test.startswith("tests/full/")
    assert len(rolls.POOL_GENS) == 5, "one per live scripted hamlet in the pool"
    for e in rolls.IN_PROCESS:
        assert isinstance(e.stub, bool)


def test_every_roll_and_duplicate_points_at_the_audit_that_justified_it() -> None:
    """Feature 217 (GM 2026-09-08): a row's reason used to be free text, written in ten seconds; now it points at the
    research section that RECORDS the `make roll-audit` run which justified it - a section that exists only if the
    audit was run. The path is repository-relative, the anchor a research heading (`#R2`)."""
    repo = Path(__file__).resolve().parents[4]
    for r in (*rolls.ROLLS, *rolls.DUPLICATES):
        assert r.audit, f"{r.key}: a roll must point at the audit that justified it (specs/NNN-<slug>/research.md#R<k>)"
        path, _, anchor = r.audit.partition("#")
        f = repo / path
        assert f.is_file() and path.startswith("specs/") and path.endswith("research.md"), r.audit
        text = f.read_text(encoding="utf-8")
        assert anchor and f"## {anchor}" in text, f"{r.audit}: the anchor must be a research heading"
        section = text.split(f"## {anchor}", 1)[1].split("\n## ", 1)[0]
        assert "roll audit:" in section or "unique of" in section, f"{r.audit}: the section must carry the audit's output"
