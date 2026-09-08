"""`_census.record` (feature 213): a no-op with no census open, one JSON line per call with one, never an error."""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram import _census
from l7r.diagram.hamletgen import HamletSpec


def test_no_census_no_record(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    monkeypatch.delenv(_census.ENV, raising=False)
    _census.record("roll", spec=None)
    assert list(tmp_path.iterdir()) == []


def test_a_record_carries_the_spec_the_test_and_the_request(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    path = tmp_path / "census.jsonl"
    monkeypatch.setenv(_census.ENV, str(path))
    monkeypatch.setenv(_census.TEST_ENV, "tests/x.py::test_y")
    monkeypatch.setenv(_census.REQUEST_ENV, "abc123")
    monkeypatch.setenv(_census.WORKER_ENV, "42")
    monkeypatch.setenv(_census.CONTEXT_ENV, "fixture:tests/gate/a.py::polder")  # feature 217: the roll's coverage context
    monkeypatch.setenv(_census.GEN_ENV, "pool/hamlets/x/x.gen.py")  # feature 217: a gen child's roll, whoever requested it
    spec = HamletSpec(name="X", seed=7, households=12)
    _census.record("roll", spec=_census.spec_row(spec), ok=True, dt=1.5)
    _census.record("served", subject="roll:X")
    rows = [json.loads(ln) for ln in path.read_text().splitlines()]
    assert [r["kind"] for r in rows] == ["roll", "served"]
    assert rows[0]["spec"]["name"] == "X" and rows[0]["spec"]["seed"] == 7 and rows[0]["spec"]["households"] == 12
    assert rows[0]["test"] == "tests/x.py::test_y" and rows[0]["request"] == "abc123" and rows[0]["worker"] == "42" and rows[0]["ok"] is True
    assert rows[0]["context"] == "fixture:tests/gate/a.py::polder", "the verdict maps the roll to the lines it earned by this (feature 217)"
    assert rows[0]["gen"] == "pool/hamlets/x/x.gen.py", "the verdict prints a shipped generator's roll and never judges it (feature 217)"
    assert _census.spec_row(None) is None


def test_an_unwritable_census_never_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    monkeypatch.setenv(_census.ENV, str(tmp_path / "no-such-dir" / "census.jsonl"))
    _census.record("roll", spec=None)  # the directory does not exist; a roll must not go red over its census
