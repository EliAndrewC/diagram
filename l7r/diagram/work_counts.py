"""The counted work of a roll: basic operations by kind and by function, per stage (feature 443, D1-D3).

WHY (the GM, 2026-10-27, `specs/443-work-budget-tooling/request.md`): the conversion is judged on "an algorithmically sensible
number of computations", so the work a roll does is counted in units that survive a port to Rust - a point or segment test, a
distance, an index query and the entries it examined, a candidate tried, a thing placed, dropped or moved - and read against
each phase's budget (`make work-budget`, `dev/work-budget.md`).

A COUNTING SITE IS ONE LINE, NEVER A CALL: `if __debug__: OPS["<kind>@<function>"] += <n>`. A dict subscript and an add are C
operations, so the push's call guard (`sys.monitoring` PY_START, feature 427 T03) does not move; `defaultdict`'s `__missing__`
is C too. `python -O` drops every `if __debug__:` block when it compiles, so a deployed run counts nothing (`make
counters-inert` holds that the manifests are identical either way). This module imports nothing of the engine.

Research: plumbing - NONE: it counts, and decides nothing about the place
"""

from collections import defaultdict

#: every counted operation of the roll so far, keyed `<kind>@<function>`
OPS: defaultdict[str, int] = defaultdict(int)
#: each stage's share of OPS, by the stage's name - filled by `hamletgen/driver._run_stages`
BY_STAGE: dict[str, dict[str, int]] = {}
#: the kinds a key may open with
KINDS = ("pt_test", "seg_test", "dist", "index_query", "index_examined", "candidate", "placed", "dropped", "moved")


def reset() -> None:
    """Clear the counts at the start of a roll."""
    OPS.clear()
    BY_STAGE.clear()


def by_kind(counts: dict[str, int]) -> dict[str, int]:
    """`counts` summed over functions, by kind."""
    out: dict[str, int] = {}
    for key, n in counts.items():
        kind = key.split("@", 1)[0]
        out[kind] = out.get(kind, 0) + n
    return out
