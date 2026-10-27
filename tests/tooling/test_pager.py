"""scripts/record/pager.py: a long report goes through a pager on a terminal, whole everywhere else (the GM 2026-10-27:
`make claims-report`'s 128 KB burst dropped his `podman exec -it` tab)."""

from __future__ import annotations

import importlib.util
import io
import os
import shutil
import sys

import pytest

from tests._scripts import script

spec = importlib.util.spec_from_file_location("pager", script("pager"))
assert spec and spec.loader
pg = importlib.util.module_from_spec(spec)
sys.modules["pager"] = pg
spec.loader.exec_module(pg)

LONG = "\n".join(f"line {i}" for i in range(500))


class _Tty(io.StringIO):
    def isatty(self) -> bool:
        return True


@pytest.fixture
def ran(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(pg.subprocess, "run", lambda cmd, **kw: calls.append((cmd, kw["input"])))
    monkeypatch.setattr(pg.shutil, "get_terminal_size", lambda: os.terminal_size((80, 40)))
    monkeypatch.setattr(pg.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.delenv("PAGER", raising=False)
    monkeypatch.delenv("NO_PAGER", raising=False)
    return calls


def test_a_long_report_on_a_terminal_is_paged(ran: list[tuple[str, str]]) -> None:
    out = _Tty()
    pg.page(LONG, out)
    assert ran == [("less -FRSX", LONG + "\n")] and out.getvalue() == ""


def test_a_pipe_a_short_report_no_pager_and_no_less_print_it_whole(ran: list[tuple[str, str]], monkeypatch: pytest.MonkeyPatch) -> None:
    piped = io.StringIO()
    pg.page(LONG, piped)
    short = _Tty()
    pg.page("one\ntwo", short)
    monkeypatch.setenv("NO_PAGER", "1")
    off = _Tty()
    pg.page(LONG, off)
    monkeypatch.delenv("NO_PAGER")
    monkeypatch.setattr(pg.shutil, "which", lambda name: None)
    missing = _Tty()
    pg.page(LONG, missing)
    assert ran == [] and piped.getvalue() == off.getvalue() == missing.getvalue() == LONG + "\n" and short.getvalue() == "one\ntwo\n"


def test_pager_env_is_honored(ran: list[tuple[str, str]], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAGER", "more")
    pg.page(LONG, _Tty())
    assert ran[0][0] == "more" and shutil.which is not None
