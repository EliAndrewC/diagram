"""The two halves of feature 234 - the report that names a stale modal, and the heading check.

WHAT THESE PROVE. The decision itself is `named_pairs`, lifted to take plain dicts so a test needs no
git repository, no engine import and no research page. The parsers and the heading check are exercised
against the real tree, because their whole job is to agree with it.

WHY BOTH SURFACES GET A NON-VACUITY TEST (FR-011). This feature ships two things that match text, and a
matcher that has silently stopped matching passes every assertion about what it does NOT find. Each one
is therefore asserted to still find something.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]
SKILL = REPO / ".claude/skills/diagram"


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name.replace('_', '-') if name.startswith('check') else name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


eo = _load("_entry_owed")
ceh = _load("check_entry_headings")

A, B = "archetypes.html#one", "archetypes.html#two"


def test_a_moved_section_under_unchanged_prose_is_named():
    """The rule, in its simplest form (SC-001)."""
    out = eo.named_pairs({A}, {"k": {A}}, {"k": "prose"}, {"k": "prose"}, {"k": "f.py:1"})
    assert out == ["k - archetypes.html#one - prose at f.py:1"]


def test_prose_that_moved_in_the_same_delta_is_not_named():
    """The exemption: a changed explanation IS the revisit the GM asked about (SC-002)."""
    assert eo.named_pairs({A}, {"k": {A}}, {"k": "new"}, {"k": "old"}) == []


def test_a_section_no_entry_names_produces_nothing():
    """SC-005 - the report is keyed on what a class actually points at."""
    assert eo.named_pairs({B}, {"k": {A}}, {"k": "p"}, {"k": "p"}) == []


def test_a_class_new_in_this_delta_is_never_named():
    """There is no older prose for a section to have drifted from."""
    assert eo.named_pairs({A}, {"k": {A}}, {"k": "p"}, {}) == []


def test_the_prose_key_is_derived_and_ignores_the_data_tags():
    """FR-002. Re-pointing an `Entry:` or fixing a `Sources:` line must NOT silence the check, because
    the words a reader sees have not moved - which is why the key is the prose and not the docstring."""
    sys.path.insert(0, str(SKILL))
    from l7r.diagram.interactive.classes import _base

    def src(why: str, entry: str) -> str:
        return f'class K:\n    """\n    What: a thing.\n    Why: {why}\n    Note: GUESS: a note.\n    Name: k\n    Covers: c\n    Label: guess\n    Sources: s\n    Entry: {entry}\n    """\n\n    key = "k"\n'

    base = eo.classes_in(src("because.", "research/a.html - 'H'"), _base)
    same_prose = eo.classes_in(src("because.", "research/b.html - 'OTHER'"), _base)
    moved_prose = eo.classes_in(src("for another reason.", "research/a.html - 'H'"), _base)
    assert base == same_prose, "a data-tag edit must leave the prose key untouched"
    assert base != moved_prose, "a Why: edit must move it"


def test_the_class_parser_still_finds_the_registry():
    """NON-VACUITY for `_entry_owed.py`'s matching surface (FR-011.1, SC-006). A parser that matched
    nothing would make every "is not named" assertion above pass for the wrong reason."""
    sys.path.insert(0, str(SKILL))
    from l7r.diagram.interactive.classes import CLASSES, _base

    found: dict[str, str] = {}
    for path in sorted((SKILL / "l7r/diagram/interactive/classes").glob("*.py")):
        found |= eo.classes_in(path.read_text(encoding="utf-8"), _base)
    assert set(found) == set(CLASSES), "the ast parser and the engine disagree about what a Kind is"
    assert len(found) > 40, f"only {len(found)} classes parsed - the surface has gone quiet"


def test_every_entry_heading_resolves_today():
    """SC-003's standing half, and the reason FR-009 calls the check prophylactic: 0 of 51 are broken."""
    assert ceh.broken(REPO) == []


def test_a_declared_silence_is_recognized_and_does_not_swallow_a_broken_heading():
    """SC-004. The two must be told apart by the FORM, never by the absence of a match."""
    assert ceh.SILENT.search("research/fields.html (no dedicated entry - recorded as silent)")
    assert not ceh.SILENT.search("research/fields.html - 'A heading that does not exist'")
    assert not ceh.SILENT.search("research/archetypes.html - 'Real heading'")


def test_the_heading_checker_proves_it_still_bites():
    """FR-011.2, SC-006 - the `--selftest` the push runs before the scan, for the same reason its three
    siblings do: on a research-only delta this check is the only thing standing there."""
    assert ceh.selftest() == 0


@pytest.mark.parametrize("token", ["", "x", "ok"])
def test_the_push_escape_demands_a_real_reason(token: str):
    """SC-013's floor: a bare `ENTRY_DRIFT_OK` explains nothing to the person auditing later."""
    p = subprocess.run([sys.executable, str(REPO / "scripts/_hm_escape.py"), "reason-ok"], input=token, capture_output=True, text=True)
    assert p.returncode != 0, f"{token!r} passed the reason floor"


def test_a_real_reason_clears_the_floor():
    p = subprocess.run([sys.executable, str(REPO / "scripts/_hm_escape.py"), "reason-ok"], input="a maintenance sweep moved no finding", capture_output=True, text=True)
    assert p.returncode == 0


def test_the_judgment_agent_is_pre_authorized():
    """SC-009. Without this the mandate loses to the default system prompt's "do not call the Agent tool
    unless the user asked", which sits ABOVE CLAUDE.md - the documented 2026-07-27 failure in which three
    city maps shipped unreviewed. It was held by inspection until this test existed, which is the very
    thing SC-009 forbids."""
    text = (REPO / "container-scripts/append-system-prompt.md").read_text(encoding="utf-8")
    authorized = {m.strip("`") for m in __import__("re").findall(r"`[a-z-]+`", text.split("invoke it with the Agent tool")[0])}
    assert "entry-drift" in authorized, f"entry-drift is not in the pre-authorized list: {sorted(authorized)}"
    assert (REPO / ".claude/agents/entry-drift.md").is_file(), "pre-authorized but the agent file is missing"


def test_the_agent_pins_opus_like_every_subagent_check():
    """GM 2026-09-07 - and `tests/test_agent_models.py` holds the whole tree to it; this asserts the one
    file this feature adds, so a failure here names the feature rather than the roster."""
    text = (REPO / ".claude/agents/entry-drift.md").read_text(encoding="utf-8")
    assert "\nmodel: opus\n" in text, "entry-drift must pin model: opus"
