"""`tests/_sweep.py` and `make sweep`: a random-equivalence sweep is widened from the command line, never by editing the test."""

from __future__ import annotations

import pathlib

import pytest

from tests._sweep import seeds


def test_a_sweep_takes_its_default_or_the_widened_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_SWEEP_SEEDS", raising=False)
    assert seeds(30) == range(30)
    monkeypatch.setenv("L7R_SWEEP_SEEDS", "600")
    assert seeds(30) == range(600)


def test_make_sweep_widens_through_the_environment() -> None:
    make = (pathlib.Path(__file__).resolve().parents[1] / "Makefile").read_text()
    assert "\nsweep:" in make and "L7R_SWEEP_SEEDS=$(SEEDS)" in make
