"""A Python entry started under the Rust gate still passes `guard()` (feature 449 T064, the round arbiter's `ask:449-T064-slices`): retiring
`ci/__main__.py` puts `l7r-gate` between make and such a process, and the check walks every ancestor, so what stands between them changes nothing."""

from __future__ import annotations

import pytest

from l7r.diagram import _invocation as inv


def test_a_python_entry_under_the_rust_gate_is_under_make(monkeypatch: pytest.MonkeyPatch) -> None:
    table = {30: "python3", 20: "l7r-gate", 10: "make"}
    monkeypatch.setattr(inv, "_ancestry", lambda: [30, 20, 10])
    monkeypatch.setattr(inv, "_comm", lambda pid: table[pid])
    monkeypatch.setattr(inv, "_cwd", lambda pid: inv._REPO)  # noqa: ARG005, SLF001 - the module's own constant
    monkeypatch.setattr(inv, "_cmdline", lambda pid: ["make", "ci-status"])  # noqa: ARG005
    assert inv._compute() == (True, "")  # noqa: SLF001 - the check itself, no cached verdict
