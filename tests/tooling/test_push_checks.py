"""The four checks still in Python keep off a change that holds none of what they read (`ask:449-T065-scope`, condition 2). The push's own runner is
`rust/gate/src/push.rs`."""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_every_makefile_line_starting_a_retained_python_check_asks_first() -> None:
    """The same condition at the Makefile: a recipe line of `make quick` or `make static` naming one of the four is behind `check needs`."""
    text = (REPO / "Makefile").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.startswith("\t") and re.search(r"python3 scripts/gates/check-(duplicate-defs|function-cap|partial-citations)", line)]
    assert len(lines) == 4 and all("check needs " in line for line in lines), lines
