"""`tests/_heap.py`: the trim after a test that grew the worker (2026-10-04)."""

from __future__ import annotations

import os

import pytest

from l7r.diagram import _memory
from tests import _heap


def test_rss_is_read_from_proc() -> None:
    assert _heap.rss_kb() > 1024 if os.path.exists("/proc/self/statm") else _heap.rss_kb() == 0


def test_rss_survives_a_stubbed_builtin_open(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_open(*_a: object, **_k: object) -> None:
        raise OSError("stubbed")

    monkeypatch.setattr("builtins.open", no_open)
    assert _heap.rss_kb() >= 0


def test_no_proc_reads_as_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_proc(*_a: object) -> int:
        raise OSError("no /proc")

    monkeypatch.setattr(_heap, "_os_open", no_proc)
    assert _heap.rss_kb() == 0


def test_only_growth_past_the_bar_trims(monkeypatch: pytest.MonkeyPatch) -> None:
    trims: list[int] = []
    monkeypatch.setattr(_memory, "trim_heap", lambda: trims.append(1) or True)
    assert not _heap.trim_if_grown(100_000, 100_000 + _heap.GROWTH_KB)
    assert _heap.trim_if_grown(100_000, 100_001 + _heap.GROWTH_KB)
    assert trims == [1]
