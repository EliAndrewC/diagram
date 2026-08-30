"""The verdict journal (feature 163): the gate records which checks it made FAIL or WAIVE.

WHY IT LIVES IN `check()` AND NOT IN A GREP. The census this feature is built for asks which checks
anything the engine can produce TODAY still makes fail. A grep over `tests/` answers a different
question and answers it wrong in both directions: 140 of the 152 live check names appear somewhere
under `tests/`, while only about 95 have a negative fixture of any kind. `check()` is the single
point where every verdict is emitted, so it is the only honest observation post.

WHAT THE FEATURE-132 GUARD IS FOR. The journal is switched by an environment variable, and this
project forbids a variable that changes what a map ROLLS. `test_the_journal_changes_no_verdict`
below is the proof that this one changes only what is RECORDED - the same guard
`tests/hamletgen/test_driver.py` holds over `STAGE_PROFILE_ENV`.
"""

from __future__ import annotations

import atexit
import json

import pytest

from l7r.diagram.check_village import driver

# A garden sitting squarely on a drain ditch - the smallest manifest that reliably fails one named
# check. Borrowed from test_segments_04_homesteads.py so the fixture and the check stay in step.
_GARDEN_ON_A_DITCH = {
    "meta": {"scale": "village", "name": "Journal-test"},
    "houses": [{"x": 500, "y": 500, "w": 44, "h": 29, "kind": "plain", "rot": 0}],
    "gardens": [{"x": 540, "y": 500, "w": 24, "h": 16, "rot": 0, "of": [500, 500]}],
    "field_ditches": [{"poly": [[540, 480], [540, 520]], "role": "drain", "w": 6, "field": "f"}],
}
_CHECK = "gardens_clear_of_channels"
# 60+ characters of real reason, which is what `waivers_are_documented` demands of a live waiver.
_REASON = "The ditch here is a covered culvert under the raised bed, laid when the lane was cut."


@pytest.fixture(autouse=True)
def _clean_journal_state():
    """The journal is module state, so a test that records must not leak into the next one."""
    driver._VERDICTS.clear()
    driver._FLUSH_REGISTERED = False
    yield
    atexit.unregister(driver.flush_verdicts)
    driver._VERDICTS.clear()
    driver._FLUSH_REGISTERED = False


def _gate(M):
    return set(driver.gate({**M}, verbose=False, only={_CHECK}))


# ---- record_verdict: off by default, on when the directory is set ------------------------------


def test_record_verdict_is_a_no_op_when_the_journal_directory_is_unset(monkeypatch):
    monkeypatch.delenv(driver.VERDICT_JOURNAL_ENV, raising=False)
    assert driver.record_verdict("x", "FAIL", "somewhere") is False
    assert driver._VERDICTS == set()


def test_record_verdict_records_when_the_journal_directory_is_set(monkeypatch, tmp_path):
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    assert driver.record_verdict("x", "FAIL", "somewhere") is True
    assert driver._VERDICTS == {("x", "FAIL", "somewhere")}


def test_record_verdict_registers_the_flush_exactly_once(monkeypatch, tmp_path):
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    driver.record_verdict("x", "FAIL", "a")
    assert driver._FLUSH_REGISTERED is True
    driver.record_verdict("y", "FAIL", "b")  # the second record must not register a second handler
    assert driver._FLUSH_REGISTERED is True
    assert len(driver._VERDICTS) == 2


# ---- flush_verdicts -----------------------------------------------------------------------------


def test_flush_verdicts_writes_one_file_per_process(monkeypatch, tmp_path):
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    driver.record_verdict("b_check", "WAIVE", "Kuwabata")
    driver.record_verdict("a_check", "FAIL", "Inashiro")
    path = driver.flush_verdicts()
    assert path is not None
    assert json.loads(open(path, encoding="utf-8").read()) == [["a_check", "FAIL", "Inashiro"], ["b_check", "WAIVE", "Kuwabata"]]


def test_flush_verdicts_creates_the_directory_it_was_given(tmp_path):
    driver._VERDICTS.add(("x", "FAIL", "a"))
    target = tmp_path / "not" / "yet" / "there"
    path = driver.flush_verdicts(str(target))
    assert path is not None and target.is_dir()


def test_flush_verdicts_returns_none_with_no_directory(monkeypatch):
    monkeypatch.delenv(driver.VERDICT_JOURNAL_ENV, raising=False)
    driver._VERDICTS.add(("x", "FAIL", "a"))
    assert driver.flush_verdicts() is None


def test_flush_verdicts_returns_none_with_nothing_recorded(tmp_path):
    assert driver.flush_verdicts(str(tmp_path)) is None


# ---- what the gate actually journals -------------------------------------------------------------


def test_a_failing_check_is_journaled_as_fail_against_the_map_that_failed_it(monkeypatch, tmp_path):
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    assert _CHECK in _gate(_GARDEN_ON_A_DITCH)
    assert (_CHECK, "FAIL", "Journal-test") in driver._VERDICTS


def test_a_waived_check_is_journaled_as_waive_because_a_waive_is_a_suppressed_fail(monkeypatch, tmp_path):
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    waived = {**_GARDEN_ON_A_DITCH, "meta": {**_GARDEN_ON_A_DITCH["meta"], "waivers": {_CHECK: _REASON}}}
    assert _CHECK not in _gate(waived)  # a waiver keeps it out of the failure list...
    assert (_CHECK, "WAIVE", "Journal-test") in driver._VERDICTS  # ...and the journal still sees it fire


def test_a_passing_check_is_never_journaled(monkeypatch, tmp_path):
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    clean = {**_GARDEN_ON_A_DITCH, "field_ditches": []}
    assert _CHECK not in _gate(clean)
    assert driver._VERDICTS == set()


def test_a_map_with_no_name_journals_a_placeholder_rather_than_crashing(monkeypatch, tmp_path):
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    unnamed = {**_GARDEN_ON_A_DITCH, "meta": {"scale": "village"}}
    _gate(unnamed)
    assert (_CHECK, "FAIL", "<unnamed>") in driver._VERDICTS


# ---- the feature-132 guard: the switch changes what is RECORDED, never what is DECIDED -----------


def test_the_journal_changes_no_verdict(monkeypatch, tmp_path):
    """Feature 132 forbids an environment variable that changes what a map rolls. This one may exist
    because it changes only what is recorded - so the verdicts must be identical with it set and unset."""
    monkeypatch.delenv(driver.VERDICT_JOURNAL_ENV, raising=False)
    off = _gate(_GARDEN_ON_A_DITCH)
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    on = _gate(_GARDEN_ON_A_DITCH)
    assert off == on == {_CHECK}


def test_the_journal_leaves_the_manifest_untouched(monkeypatch, tmp_path):
    """gate() mutates the manifest it is handed (DEFAULT_MANIFEST merge, theater_stage normalization);
    what it must NOT do is mutate it DIFFERENTLY because the journal is on."""
    monkeypatch.delenv(driver.VERDICT_JOURNAL_ENV, raising=False)
    a = {**_GARDEN_ON_A_DITCH}
    driver.gate(a, verbose=False, only={_CHECK})
    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    b = {**_GARDEN_ON_A_DITCH}
    driver.gate(b, verbose=False, only={_CHECK})
    assert a == b
