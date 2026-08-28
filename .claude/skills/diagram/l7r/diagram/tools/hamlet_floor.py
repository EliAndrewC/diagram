"""THE HAMLET-PATH COVERAGE FLOOR (feature 145, GM 2026-08-28).

    python3 -m l7r.diagram.tools.hamlet_floor           # the check: every hamlet-path module at 100%, or exit 1
    python3 -m l7r.diagram.tools.hamlet_floor --list    # the module set, one path per line

WHAT IT ENFORCES. The GM: *"we will maintain one hundred percent code coverage on the scripted procedure
and anything related to it, and that that will be maintained as we expand it ... I want that threshold
to be automatic rather than something that we just remember to maintain."* Towns, cities and villages
are exempt - nothing exercises them yet and *"they might be deleted entirely"* - and the boundary is
drawn at MODULE level by the GM's ruling (*"I'm okay with it being done at the module level for now.
because eventually, we will just go back to one hundred percent code coverage everywhere"*).

HOW THE SET IS DERIVED, so that no one edits a list. The roll cache records, for every scripted roll,
the engine functions it executed (`gencache.record` - the same trace that keys the cache). The hamlet
path is the union of those records over a FIXED set of subjects - the reference settlement, the three
polder rolls the gate tests use, and the cohort's ratchet seeds 41-44 - mapped to the files they live
in. A module any of those rolls touches owes 100%; a module none of them touches owes nothing here
(the settlement package's ratchet still applies to it - that floor stays, GM's round-1 review). When
the scripted tier grows, the rolls execute more modules and the set grows with them. The subjects are
fixed rather than "whatever is in the cache" so the set is the same on every machine: on a fresh clone
or on CodeBuild the tool rolls them once (`rollcache.report_deps`) - ~1-2 minutes, then cached.

WHY NOT LINES. A line-level floor ("every line a hamlet roll executes is covered") is a tautology when
the suite includes the rolls, and is a different, much larger program when it does not (every line
reached by a NON-rolling test). Module level is what the GM chose, and it means one concrete thing: a
city-only branch inside a module the hamlet path uses is not exempt - it needs a test, or the GM's
decision on the case (spec FR-002; no code is deleted and no `pragma: no cover` is written to make the
floor green).

WHAT A FAILURE LOOKS LIKE. The coverage table names the module and its missing lines; the floor exits
1. With no record and no way to make one (no engine on the path) it exits 2 and says so - a silent
fallback list is exactly the "something we just remember to maintain" this replaces.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import IO, Any

SKILL = Path(__file__).resolve().parents[3]
ENGINE = SKILL / "l7r" / "diagram"
EXCLUDED_PARTS = ("tests", "ci")  # a test file or the CodeBuild dispatcher is never "the hamlet path"


def subjects() -> list[Any]:
    """The fixed specs whose rolls define the path: the reference, the gate's three polders, the cohort's ratchet seeds."""
    from l7r.diagram import hamletgen as hg

    return [
        hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond"),  # `make reference`
        hg.HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0),
        hg.HamletSpec(name="Polder", seed=8, households=16, field_archetype="polder_grid"),
        hg.HamletSpec(name="Polder", seed=19, households=16, field_archetype="polder_grid", down_deg=90),
        *hg.driver.cohort_specs(4, first_seed=41),
    ]


def hamlet_path_files(records: Iterable[dict[str, Any]]) -> list[str]:
    """The engine modules (paths relative to the skill root, sorted) that the recorded rolls executed."""
    out: set[str] = set()
    for deps in records:
        for entry in deps.get("functions", []):
            path = Path(str(entry[0])).resolve()
            try:
                rel = path.relative_to(ENGINE)
            except ValueError:
                continue  # outside the engine (a test helper, a library)
            if any(part in EXCLUDED_PARTS for part in rel.parts[:-1]):
                continue
            out.add(str(path.relative_to(SKILL)))
    return sorted(out)


def module_set(deps_for: Callable[[Any], dict[str, Any]] | None = None) -> list[str]:
    """The hamlet path, derived from the fixed subjects' records (rolled now if not yet recorded)."""
    if deps_for is None:
        from l7r.diagram.pipeline import rollcache

        deps_for = rollcache.report_deps
    return hamlet_path_files(deps_for(spec) for spec in subjects())


def check(files: list[str], data_file: str = ".coverage", out: IO[str] = sys.stdout) -> int:
    """0 when every file is at 100% in the coverage data; 1 otherwise (the table names the misses); 2 when the set is empty."""
    import coverage

    if not files:
        print("hamlet-floor: the hamlet path is EMPTY - no roll record and nothing rolled; `make reference` produces the first record", file=out)
        return 2
    cov = coverage.Coverage(data_file=data_file)
    cov.load()
    print(f"hamlet-floor: {len(files)} modules on the hamlet path (derived from the scripted rolls' records)", file=out)
    total = cov.report(include=[str(SKILL / f) for f in files], show_missing=True, file=out)
    if total < 100.0:
        print(
            f"COVERAGE: a module on the HAMLET PATH is under 100% ({total:.2f}% combined) - the table above names it (feature 145: the path is derived from what the scripted rolls execute; bring it up BY TESTS, spec FR-002)",
            file=out,
        )
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--list", action="store_true", help="print the derived module set and exit")
    ap.add_argument("--data", default=".coverage", help="the coverage data file to judge (default .coverage)")
    args = ap.parse_args(argv)
    os.chdir(SKILL)
    files = module_set()
    if args.list:
        print("\n".join(files))
        return 0 if files else 2
    return check(files, args.data)


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.hamlet_floor")
    sys.exit(main())
