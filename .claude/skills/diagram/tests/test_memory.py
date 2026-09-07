"""`_memory.trim_heap` (feature 210): glibc's freed arenas go back to the kernel when a roll ends."""

from __future__ import annotations

import ctypes

import pytest

from l7r.diagram import _memory


def test_trim_runs_here_and_reports_it() -> None:
    assert _memory.trim_heap() is True


def test_trim_is_a_courtesy_never_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A platform without glibc, or a libc without the symbol, gets False - a roll must never go red over
    a memory courtesy."""

    def no_libc(_name: str) -> object:
        raise OSError("no libc.so.6 here")

    monkeypatch.setattr(ctypes, "CDLL", no_libc)
    assert _memory.trim_heap() is False

    class NoSymbol:
        def __getattr__(self, name: str) -> object:
            raise AttributeError(name)

    monkeypatch.setattr(ctypes, "CDLL", lambda _name: NoSymbol())
    assert _memory.trim_heap() is False
