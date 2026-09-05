"""Feature 188: `make page-check` and the two success exits of `make done` (spec FR-004 to FR-006).

Reads the real Makefile's recipe text, in `test_coverage_floor.py`'s style: the wiring is what is proved -
that the page check runs the two test surfaces with no coverage and writes the `page` stamp and nothing
else, and that of `make done`'s two success exits only the one that RAN the phases writes `page`. The
already-verified short-circuit is blind to the assets since this feature, so a page stamp written there
would vouch for a stylesheet by running nothing - the hole the spec review found in the first draft."""

from __future__ import annotations

import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[2]
MAKEFILE = (SKILL / "Makefile").read_text(encoding="utf-8")


def _recipe(target: str) -> str:
    # the RECIPE line, not a target-specific variable line such as `tick: export TICK_NOTE = $(NOTE)`
    start = re.search(rf"^{re.escape(target)}:(?!\s*export\b)", MAKEFILE, re.M)
    assert start, f"the Makefile has a `{target}` target"
    rest = MAKEFILE[start.end() :]
    nxt = re.search(r"^[a-zA-Z][\w-]*:", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def test_page_check_runs_the_two_page_surfaces_without_coverage_and_stamps_page_only() -> None:
    body = _recipe("page-check")
    assert "tests/interactive tests/full/interactive/test_page_browser.py" in body
    assert "--no-cov" in body, "a CSS or JS change cannot move Python coverage - no floor"
    assert "gate-stamp.py\" --write page" in body
    assert "green-local" not in body and "$(STATE)" not in body, "no verification-state record (ci/decision.py reads the event, not the target)"


def test_only_the_phases_run_exit_of_make_done_stamps_page() -> None:
    body = _recipe("done")
    short = re.search(r"verified-done; then(.*?)exit 0;", body, re.S)
    assert short, "the already-verified short-circuit"
    assert "--write diagram" in short.group(1) and "--write page" not in short.group(1), "the short-circuit ran nothing: diagram only"
    after = body[short.end() :]
    assert "--write diagram && python3" in after and "--write page" in after, "the phases-run exit stamps both"


def test_tick_is_wired_to_the_script() -> None:
    body = _recipe("tick")
    assert 'scripts/tick-task.py" "$(F)" "$(T)" --note-from-env' in body and "$(if $(BOXES),--boxes,)" in body
    assert "tick: export TICK_NOTE = $(NOTE)" in MAKEFILE, "the note travels in the environment, never through the shell"
