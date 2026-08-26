"""How much of a test runs: the QUICK form by default, the EXHAUSTIVE form on request.

GM 2026-08-26 (feature 133 T19): *"I don't think we need to run it with that many random seeds
on literally every invocation unless we have some reason to believe that it is commonly the case
that ... our unit tests pass, but only because a bunch of the tests had a random seed that happened
to pass ... as of now, we really need to prioritize running very quickly."* So a test that sweeps
seeds, cardinals, structure kinds or fixture sizes runs the sweep only in EXHAUSTIVE mode and a
representative subset otherwise. THE GATE IS EXHAUSTIVE (`make done` always sets it; `make quick
EXHAUSTIVE=1` for a one-off): quick runs the unit-test form, the gate runs the integration form -
constitution v2.9.0, GM 2026-08-26: *"quick tests should do a quick version of this check, and then
we punt the more expensive version into the longer tests."* The
docstring of every such test records the date its exhaustive form was last run green, so the
subset is a documented choice, not a silent one. Importable at collection time (parametrize lists
read it), so it is an environment variable rather than a pytest option.
"""

from __future__ import annotations

import os
from collections.abc import Sequence

EXHAUSTIVE = os.environ.get("L7R_TESTS_EXHAUSTIVE") == "1"


def subset[T](items: Sequence[T], quick: int) -> Sequence[T]:
    """`items` in full under EXHAUSTIVE, else its first `quick` entries."""
    return items if EXHAUSTIVE else items[:quick]


def full_or[T](quick: T, full: T) -> T:
    """The quick-form value (a 1-fan comb, a 600 px canvas) in `make quick`; the full one at the gate."""
    return full if EXHAUSTIVE else quick
