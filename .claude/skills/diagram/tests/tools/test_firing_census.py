"""The firing census (feature 163) - and the guards that stop it lying quietly.

WHY THIS FILE EXISTS AT ALL. `dev/gate.md` records the failure mode in one line: *"a census that
silently returns nothing is indistinguishable from a clean bill of health"*. This feature's whole
first task is a census whose output DELETES code, so the instrument is proved before its number is
believed (FR-005, and `dev/gate.md`'s "before a number decides anything, spend one run proving the
instrument"). Three things are asserted, each of which has to be able to go red:

  1. it names a check independently known to fire,
  2. it fails loudly rather than returning an empty or partial classification,
  3. a check a frozen fixture pins is never in the NEVER-FIRES set.

The census tool itself is a by-hand diagnostic outside the 100% coverage floor; these are guards on
its VERDICTS, not coverage of its lines.
"""

from __future__ import annotations

import json

import pytest

from l7r.diagram.tools import firing_census as fc

# A check the repository independently knows fires: `pool/regressions/` carries a frozen manifest
# named for it, and that manifest was rolled by the scripted generator (feature 134 SC-006).
KNOWN_FIRING = "all_ink_is_ruled_on"


# ---- the pure classifiers, on plain dicts ------------------------------------------------------


def test_a_live_pool_map_is_classified_live():
    assert fc.classify_manifest({"meta": {"generated_by": "hamletgen"}}, frozen=False) == fc.LIVE_MAP


def test_a_frozen_fixture_from_a_scripted_roll_is_current_era():
    assert fc.classify_manifest({"meta": {"generated_by": "hamletgen"}}, frozen=True) == fc.SCRIPTED_FIXTURE


def test_a_frozen_fixture_with_no_generator_stamp_is_hand_era():
    assert fc.classify_manifest({"meta": {"scale": "hamlet"}}, frozen=True) == fc.HAND_FIXTURE
    assert fc.classify_manifest({}, frozen=True) == fc.HAND_FIXTURE


@pytest.mark.parametrize(
    ("rows", "expect"),
    [
        (set(), fc.NEVER_FIRES),
        ({(fc.LIVE_MAP, "a")}, fc.FIRES),
        ({(fc.SCRIPTED_FIXTURE, "a")}, fc.FIRES),
        ({(fc.HAND_FIXTURE, "a")}, fc.FIRES_HAND_ONLY),
        ({(fc.TEST, "a")}, fc.FIRES_HAND_ONLY),
        ({(fc.HAND_FIXTURE, "a"), (fc.SCRIPTED_FIXTURE, "b")}, fc.FIRES),
    ],
)
def test_the_verdict_follows_the_evidence_class_not_the_evidence_count(rows, expect):
    """FR-001: what counts is whether the CURRENT implementation makes it fail, not how much
    hand-era evidence has piled up. A hundred hand fixtures are still FIRES-HAND-ONLY; one scripted
    fixture is FIRES."""
    assert fc.verdict_for(rows) == expect


def test_a_test_journal_row_is_never_counted_as_the_current_implementation():
    """A unit test's inline manifest is a dict a person typed, not a shape a generator produces -
    so it proves the check has TEETH and not that the engine still trips it. The distinction is the
    whole of FR-001, and collapsing it is what would delete a working check."""
    assert fc.TEST not in fc.CURRENT


# ---- the merge and the journal reader ------------------------------------------------------------


def test_journals_from_several_workers_are_unioned(tmp_path):
    (tmp_path / "verdicts-1.json").write_text(json.dumps([["a", "FAIL", "M1"]]))
    (tmp_path / "verdicts-2.json").write_text(json.dumps([["a", "WAIVE", "M2"], ["b", "FAIL", "M1"]]))
    ev = fc.evidence_from_journals(str(tmp_path))
    assert ev["a"] == {(fc.TEST, "suite:M1"), (fc.TEST, "suite:M2")}
    assert ev["b"] == {(fc.TEST, "suite:M1")}


def test_an_absent_journal_directory_contributes_nothing(tmp_path):
    assert fc.evidence_from_journals(str(tmp_path / "nope")) == {}


def test_merge_unions_rather_than_overwrites():
    a = {"x": {(fc.LIVE_MAP, "1")}}
    b = {"x": {(fc.HAND_FIXTURE, "2")}, "y": {(fc.TEST, "3")}}
    assert fc.merge(a, b) == {"x": {(fc.LIVE_MAP, "1"), (fc.HAND_FIXTURE, "2")}, "y": {(fc.TEST, "3")}}


# ---- guards that read no fixture ---------------------------------------------------------------


def test_the_check_roster_is_read_and_is_not_empty():
    """Guard 2, first half: the census classifies against the live pin, and a pin that came back
    empty would classify nothing while reporting a clean bill of health."""
    names = fc.live_check_names()
    assert len(names) > 100
    assert KNOWN_FIRING in names
    assert names == sorted(set(names))


def test_a_gate_error_is_recorded_rather_than_swallowed():
    """A fixture built for one check can raise from an unrelated one. That must not read as 'no
    verdicts', which is what a bare try/except pass would make it look like."""
    out = fc.verdicts_for({"houses": object()})  # not a list - something downstream will raise
    assert out and all(name == "<error>" for name, _v in out)


# ---- the emitted name is not always the pinned name ---------------------------------------------


def test_an_indexed_check_name_is_normalized_to_the_pinned_name():
    """`check(f"stream_source_anchored[{idx}]")` emits a name the pin does not carry. Comparing the
    two literally reported both stream anchors as NEVER-FIRES while the gate fires them on every map
    with a stream - and the census was about to hand them to a deletion task."""
    assert fc.base_name("stream_source_anchored[0]") == "stream_source_anchored"
    assert fc.base_name("stream_end_anchored[12]") == "stream_end_anchored"


def test_an_ordinary_check_name_passes_through_unchanged():
    assert fc.base_name("all_ink_is_ruled_on") == "all_ink_is_ruled_on"


def test_every_dynamically_named_check_still_resolves_to_a_pinned_name():
    """The guard on the fix rather than on the symptom: whatever the segments emit dynamically must
    normalize to a name the pin carries, or the census is silently mis-classifying again. Three
    segments build a name at runtime today; if a fourth appears with a shape `base_name` cannot
    handle, this goes red."""
    import re

    names = set(fc.live_check_names())
    src = ""
    for p in sorted(__import__("glob").glob(f"{fc.HERE}/l7r/diagram/check_village/segments_*.py")):
        with open(p, encoding="utf-8") as fh:
            src += fh.read()
    dynamic = re.findall(r'check\(\s*f"([^"]*)"', src)
    assert dynamic, "no dynamically-named checks found - the census guard is testing nothing"
    for pattern in dynamic:
        # substitute a plausible value for each {placeholder}, then normalize
        concrete = re.sub(r"\{scale\}", "hamlet", re.sub(r"\{idx\}", "0", pattern))
        assert "{" not in concrete, f"unhandled placeholder in {pattern!r} - teach base_name about it"
        assert fc.base_name(concrete) in names, f"{pattern!r} normalizes to a name the pin does not carry"
