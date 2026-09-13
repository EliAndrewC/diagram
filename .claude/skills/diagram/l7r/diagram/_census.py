"""The roll census's WRITER (feature 213, GM 2026-09-07: "program our unit tests to never allow the same
hamlet to be rolled twice within the tests and also to have some required process around adding another
hamlet that gets rolled").

One function, `record`, appends one JSON line to the file named by `L7R_ROLL_CENSUS` - and does nothing
when the variable is unset, which is every run that is not a gate. It is called from the CHOKEPOINTS, not
from patched entry points: `hamletgen.driver.roll_scope` (every stage-running loop enters it - feature
210's static AST test proves that), `pipeline.rollcache` (served and rolled verdicts), `settlement.finish`'s
`render_png` and `interactive.raster.picture` (a render). The first census instrument (specs/213 census/)
patched six functions and missed the package's re-exported `build` on its first run; a record written at
the boundary itself cannot be short that way. The gate sets the variable and every child process inherits
it, so a roll in a test worker, in a roll child, in a pool-sweep child or in a cohort pool child is
recorded the same way. Two more variables ride along for attribution and are set by the pytest plugin
(`ci/rollcensus.py`): `L7R_ROLL_CENSUS_TEST`, the requesting test, and `L7R_ROLL_CENSUS_REQUEST`, one id per
test, so a `generate` that re-rolls three times inside one test is one roll with three attempts, and two
tests rolling the same spec are two rolls. The verdict is `ci/rollverdict.py`; the roster is
`tests/rolls.py`.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

ENV = "L7R_ROLL_CENSUS"
TEST_ENV = "L7R_ROLL_CENSUS_TEST"
REQUEST_ENV = "L7R_ROLL_CENSUS_REQUEST"
CONTEXT_ENV = "L7R_COV_CONTEXT"  # the parent's CURRENT coverage context, exported by ci/selection.switch so a coverage child labels its data with it (below)
# WHY A CHILD'S COVERAGE CARRIES ITS REQUESTER'S CONTEXT (feature 213, found on the polder-only run of 2026-09-08).
# Feature 207 selects the tests an engine change can reach from the baseline's per-test and per-fixture coverage
# contexts. A roll made IN a worker recorded the engine's lines under the rolling fixture's context; a roll made in
# a CHILD (210, 213) records them under no context at all - so a polder-only edit selected 46 unit tests and NOT
# ONE of the polder gate tests, and the hamlet floor re-rolled both polder subjects itself (207's D14 back again,
# by a different door). So every coverage child - the roll child, the pool sweep's gate_obtain child - runs
# starts coverage itself (gencache.child_coverage), imports the engine under NO context, and switches to the parent's
# context for the work alone - `coverage run --context=` labeled the imports too, and every roller then "touched" every
# engine file - so the baseline sees the roll where 207 expects it and nothing more.
WORKER_ENV = "L7R_ROLL_CENSUS_WORKER"  # the test worker's pid - a record from another pid came from a child
# THE MECHANISM, NOT THE REQUESTER (feature 217): a shipped generator's cold roll (`gencache.gate_obtain`) is requested by
# WHICHEVER reader of the pool's map comes first under worksteal - the sweep or a gate module - so the verdict cannot tell a
# `PoolGen` roll from a rostered one by the test that asked. The gen child carries its generator's path in this variable and
# the record writes it; the verdict prints such a roll and never judges it (the pool's membership is the GM's decision).
GEN_ENV = "L7R_ROLL_CENSUS_GEN"


def spec_row(spec: Any) -> dict[str, Any] | None:
    """The fields of a `HamletSpec` the roster keys on and the verdict prints; None for no spec."""
    if spec is None:
        return None
    return {k: getattr(spec, k, None) for k in ("name", "seed", "households", "field_archetype", "down_deg", "water_sink", "settlement_form")}


class RenderedInATest(RuntimeError):
    """A test rendered a real image. Raised where the render would happen, not discovered afterwards."""


TEST_RENDER_PX = 1200
"""The widest raster a test may ask for, in output pixels, while `DIAGRAM_SKIP_RENDER` is set.

IT IS THE SIZE THAT COSTS, WHICH IS WHY THE BAR IS A SIZE (GM 2026-09-12: *"if we ever start rendering real
images during unit tests again, then it fails with an exception"* - real images). A map's PNG is 2,600 px wide
over a multi-megabyte document and costs resvg ~420 MB; the page's raster is the view at 2-3 px per map px and
costs a PIL child ~444 MB. A test that genuinely exercises the renderer does it on a 40x40 document, and 34
such tests exist (`tests/interactive/test_raster.py`, `test_page.py`, `tools/test_picture_diff.py`,
`test_page_lit.py`) - they are the reason the first cut of this guard was wrong: it refused ANY resvg call and
so refused every deliberate probe along with the real renders.

1,200 px is chosen from the two endpoints, both measured on 2026-09-12 rather than guessed. BELOW it: the
raster module's own probes at 40 to 100 px, and the synthetic pages the interactive and browser tests render -
a 300x300 document at `RASTER_R` = 2 px per map px, so 600 px, which is the largest honest render in the suite.
ABOVE it: a map's PNG at 2,600 px, and a real page's raster at the view's 1,400x3,000 times the same 2 - 2,800
px and up. Nothing in the tree sits between 600 and 2,600, so the bar is not a judgment call about a borderline
case; it separates two populations that are four times apart.

A test that needs a genuinely large render clears the switch (`monkeypatch.delenv`) and marks itself `renders`,
which is the contract feature 213 already set."""


def refuse_render_in_a_test(what: str, px: float, detail: str = "") -> None:
    """Raise when a test asks for a raster wider than `TEST_RENDER_PX` while `DIAGRAM_SKIP_RENDER` is set.

    THE POLICY EXISTED AND KEPT BEING BROKEN, WHICH IS WHY IT IS AN EXCEPTION NOW (GM 2026-09-12: *"we already
    put in a lot of work to stop rendering these things during tests, but then they keep getting added back in
    because we just forget and then don't notice."*).

    What was there before: `tests/conftest.py` sets `DIAGRAM_SKIP_RENDER=1` for every test (feature 213),
    `finish()` consults it and skips both the PNG and the page's raster, and the roll census fails the gate on a
    render from a test not marked `renders`. All of that is real, and a full-size render still got back in -
    because `render_png` and `resvg_png` spawn the renderer THEMSELVES and neither consulted the switch. The
    placement-page tests reached them directly and rendered at full size with the switch set, at 55 and 23 MiB
    a test, found in the memory audit of 2026-09-12 rather than by any check. The guard then found three more
    in the same file that the audit had missed.

    So the refusal lives at the two places that actually spawn the renderer, which is where it cannot be walked
    around, and it is judged on the SIZE asked for rather than on the call happening at all."""
    import os

    if not os.environ.get("DIAGRAM_SKIP_RENDER") or px <= TEST_RENDER_PX:
        return
    raise RenderedInATest(
        f"a test asked to render {what} at {px:.0f} px wide" + (f" ({detail})" if detail else "") + f", over the {TEST_RENDER_PX} px a test may ask for.\n"
        "Tests do not render real images - a map's PNG is resvg at ~420 MB and the page's picture a PIL child at\n"
        "~444 MB, and the suite's memory is the sum of its workers. MOCK IT: patch the plate or the render helper,\n"
        "or assert on the SVG or the manifest the renderer would have read. A small probe is fine and needs nothing:\n"
        f"the deliberate render tests work on a 40x40 document, well under {TEST_RENDER_PX} px.\n"
        "A test that genuinely needs a large render marks itself `@pytest.mark.renders` and clears the switch with\n"
        "`monkeypatch.delenv(\"DIAGRAM_SKIP_RENDER\", raising=False)` - the contract feature 213 set, now enforced\n"
        "where the renderer is spawned rather than only where `finish()` consults the switch (GM 2026-09-12)."
    )


def record(kind: str, **fields: Any) -> None:
    """Append one record - `kind` is `roll`, `served`, `rolled` or `render` - when a census is open. Never
    raises: a census that cannot be written must not turn a roll red; the verdict notices a short census
    because the roster's specs went unrolled."""
    path = os.environ.get(ENV)
    if not path:
        return
    row = {
        "kind": kind,
        "t": round(time.time(), 3),
        "pid": os.getpid(),
        "test": os.environ.get(TEST_ENV),
        "request": os.environ.get(REQUEST_ENV),
        "worker": os.environ.get(WORKER_ENV),
        "context": os.environ.get(CONTEXT_ENV),
        "gen": os.environ.get(GEN_ENV),
        **fields,
    }  # context: feature 217, the verdict maps a roll to the lines it earned
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, default=str) + "\n")
    except OSError:
        pass
