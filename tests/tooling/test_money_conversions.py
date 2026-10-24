"""`scripts/record/money_conversions.py` - the record's copy of gm-assistant's money conversion table (feature 413, FR-001).

A fresh copy checks clean; a stale one fails the check naming the command and is refreshed by the copy; a container without
gm-assistant mounted checks nothing and passes."""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

from tests._scripts import script


def _mod():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("money_conversions", script("money_conversions"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _root(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    source = tmp_path / "conversions.json"
    source.write_text('{"eras": {}}\n', encoding="utf-8")
    (tmp_path / "repo" / "research" / "assets").mkdir(parents=True)
    return source, tmp_path / "repo"


def test_stale_fails_the_check_then_the_copy_refreshes_it(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    mc = _mod()
    source, root = _root(tmp_path)
    assert mc.main(["--check"], str(source), str(root)) == 1
    assert "make money-conversions" in capsys.readouterr().err
    assert mc.main([], str(source), str(root)) == 0
    assert (root / mc.COPY).read_bytes() == source.read_bytes()
    assert mc.main(["--check"], str(source), str(root)) == 0
    assert "is current" in capsys.readouterr().out


def test_no_mount_checks_nothing(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _mod().main(["--check"], str(tmp_path / "absent.json"), str(tmp_path)) == 0
    assert "nothing to compare" in capsys.readouterr().out
