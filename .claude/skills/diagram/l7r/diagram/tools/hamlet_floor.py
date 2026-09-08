"""THE HAMLET-PATH COVERAGE FLOOR (feature 145, GM 2026-08-28).

    The CHECK runs as a phase of `make test-full` (and so of `make done`): every hamlet-path module
    at 100%, or exit 1. There is no `make` route to this module on its own any more - `make
    hamlet-floor` was retired 2026-09-06 (feature 198 - claimed as 195, renumbered 2026-09-07 - GM: *"we already use it on `test-full`"*).
    `--list` still exists as a flag and is still tested, but nothing reachable invokes it: asking
    for the module set without running the gate is the capability that retirement gave up.

WHAT IT ENFORCES. The GM: *"we will maintain one hundred percent code coverage on the scripted procedure
and anything related to it, and that that will be maintained as we expand it ... I want that threshold
to be automatic rather than something that we just remember to maintain."* Towns, cities and villages
are exempt - nothing exercises them yet and *"they might be deleted entirely"* - and the boundary is
drawn at MODULE level by the GM's ruling (*"I'm okay with it being done at the module level for now.
because eventually, we will just go back to one hundred percent code coverage everywhere"*).

HOW THE SET IS DERIVED, so that no one edits a list. The roll cache records, for every scripted roll,
the engine functions it executed (`gencache.record` - the same trace that keys the cache). The hamlet
path is the union of those records over a FIXED set of subjects - the reference settlement, the two
polder rolls the gate tests use, and the cohort's ratchet seeds 41-44 - mapped to the files they live
in. A module any of those rolls touches owes 100%; a module none of them touches owes nothing here
(the settlement package's ratchet still applies to it - that floor stays, GM's round-1 review). When
the scripted tier grows, the rolls execute more modules and the set grows with them. The subjects are
fixed rather than "whatever is in the cache" so the set is the same on every machine: on a fresh clone
or on CodeBuild the tool rolls them once (`rollcache.report_deps`) - ~1-2 minutes, then cached. Since
feature 213 the record it reads is the ONE roll the gate's tests made of each subject (`roll:<spec>`, stored
under the full-run bypass), so an incremental gate no longer rolls a subject the tests just rolled (207's D14).

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
    """The fixed specs whose rolls define the path: the reference, the gate's two polders, the cohort's ratchet seeds.

    `Polder seed=8` LEFT THIS LIST on 2026-09-06 (feature 192 FR-007, the GM's ruling). Two facts
    together, because neither is sufficient: nothing in the tree rolled that spec in any form, so its
    roll had no second consumer; and dropping it does not change what this floor measures - the union
    is 88 modules with or without it. Note the second fact is true of EVERY subject here (each one has
    zero modules unique to it), so it is the FIRST that singles seed 8 out. Measured on today's tree:
    if the engine changes such that a `down_deg=None` polder reaches something the others do not, this
    floor will no longer see it."""
    from l7r.diagram import hamletgen as hg

    # THE PLAIN SHARED ROLLS (feature 214): the same specs the ratchet and the lane rules read, so the record each
    # needs is the one the tests just made. Seeds 41, 42 and 44 went with the cohort; 43 stays for its kink. The
    # reference and Kuwabata are the POOL's maps since feature 215 (their record is the gen cache's, `pool_deps`).
    return [
        hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", fixtures_min={"shrine": 1}),  # the pool's brief
        hg.HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"),
        hg.HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0),
    ]  # Polder 19 and seed 43 left at feature 216: no coverage line of their own (215 R1); the seatings' partial roll is keyed to its test, not a subject here


def hamlet_path_files(records: Iterable[dict[str, Any]]) -> list[str]:
    """The engine modules (paths relative to the skill root, sorted) that the recorded rolls executed."""
    out: set[str] = set()
    for deps in records:
        for entry in deps.get("functions", []):
            if entry[1] == "<module>":
                continue  # an IMPORT is not execution: the registry imports every segment file, a star import every waterfields module; only a function that RAN puts its file on the path
            path = Path(str(entry[0])).resolve()
            try:
                rel = path.relative_to(ENGINE)
            except ValueError:
                continue  # outside the engine (a test helper, a library)
            if any(part in EXCLUDED_PARTS for part in rel.parts[:-1]):
                continue
            out.add(str(path.relative_to(SKILL)))
    return sorted(out)


#: The subjects that are SHIPPED maps (feature 215): their record is the gen cache's entry, written by the pool
#: sweep's coverage child - the gate no longer rolls them under a spec of their own.
POOL_GENS: dict[tuple[str, int], str] = {
    ("Inashiro", 4): "pool/hamlets/inashiro/inashiro.gen.py",
    ("Kuwabata", 21): "pool/hamlets/kuwabata/kuwabata.gen.py",
}


def pool_deps(spec: Any) -> dict[str, Any]:
    """The dependency record of a shipped map: the gen cache entry's, obtained (served or rolled) if absent."""
    import json

    from l7r.diagram.pipeline import gencache

    gen = str(SKILL / POOL_GENS[(spec.name, spec.seed)])
    meta = Path(gencache._entry_dir(gen)) / "meta.json"
    if not meta.is_file():
        gencache.gate_obtain(gen)
    record: dict[str, Any] = json.loads(meta.read_text(encoding="utf-8"))["deps"]
    return record


def _deps_for(spec: Any) -> dict[str, Any]:
    if (spec.name, spec.seed) in POOL_GENS:
        return pool_deps(spec)
    from l7r.diagram.pipeline import rollcache

    return rollcache.report_deps(spec)


def module_set(deps_for: Callable[[Any], dict[str, Any]] | None = None) -> list[str]:
    """The hamlet path, derived from the fixed subjects' records (rolled now if not yet recorded)."""
    return hamlet_path_files((deps_for or _deps_for)(spec) for spec in subjects())


# PARKED LINES (feature 147, GM 2026-08-29). A line listed here is KNOWN-uncovered and deliberately does
# NOT fail the floor. It is the equivalent of skipping a flaky test, for a case where there is no test to
# skip: the tests all pass, and what is unreliable is the floor's VERDICT on them.
#
# The GM's ruling, in their words: *"I would like to keep the speed up even with the flaky floor ... once we
# have pushed back to main, I would like to have you work on fixing the flakiness. This gives other sessions
# the benefit of the faster tests while also prioritizing fixing something that we know is wrong. With that
# being said, why don't we mark the flaky tests as skipped so that other sessions don't end up trying to
# duplicate your work and fix them."*
#
# So each entry says what is wrong, who owns the fix, and - the part that stops the duplicated work - what has
# ALREADY been tried. THE LIST MUST SHRINK, which is why it is printed on every run rather than hidden.
PARKED: dict[str, tuple[frozenset[int], str]] = {
    # EMPTY, AND THAT IS THE POINT. Feature 147 parked `hinterland.py` 503-504 here while the floor's verdict
    # on them flickered; feature 149 found the cause - `gencache` let an entry's stored coverage outlive the
    # key it was recorded under, so a hit replayed line numbers from an older source - and the park came off.
    # Whether this mechanism should exist at all is the GM's call and is NOT settled here (149's Decisions
    # Recorded puts both arguments): an unused way to excuse lines from a non-negotiable floor is an
    # invitation, and the alternative is that the next such case gets an ad-hoc pragma with no owner and no
    # announcement, which is what 147 would have had to do. An entry here must name its owner and what has
    # already been tried, so the next session starts from the elimination instead of repeating it.
}


def parked_for(path: str) -> tuple[frozenset[int], str]:
    return PARKED.get(path, (frozenset(), ""))


# In a docstring for the same reason as `_invocation._Ladder` (feature 191): this line names a make
# target, and a target name that cannot be corrected cheaply is one that goes stale. It named
# `make reference` until that rung was retired on 2026-09-06.
class _EmptyPath:
    """hamlet-floor: the hamlet path is EMPTY - no roll record and nothing rolled; `make maps` produces the first record"""


def check(files: list[str], data_file: str = ".coverage", out: IO[str] = sys.stdout) -> int:
    """0 when every file is at 100% in the coverage data; 1 otherwise (the table names the misses); 2 when the set is empty."""
    import coverage

    if not files:
        print(_EmptyPath.__doc__, file=out)
        return 2
    cov = coverage.Coverage(data_file=data_file)
    cov.load()
    print(f"hamlet-floor: {len(files)} modules on the hamlet path (derived from the scripted rolls' records)", file=out)
    total = cov.report(include=[str(SKILL / f) for f in files], show_missing=True, file=out)

    # THE VERDICT IS TAKEN PER LINE, NOT FROM THE PERCENTAGE, so a parked line can be excused without
    # excusing anything else in the same module (feature 147).
    unparked: list[str] = []
    for f in files:
        lines, _reason = parked_for(f)
        # No try/except: every file here came from the derived set and is a real module, so a failure to
        # analyze one is a broken floor rather than a line to skip, and it should raise where it happens.
        missing = set(cov.analysis2(str(SKILL / f))[3])
        if missing - lines:
            unparked.append(f"{f} {sorted(missing - lines)}")

    # ANNOUNCED WHETHER OR NOT THE LINE IS CURRENTLY MISSING. A park that only speaks up when the floor
    # would have failed is silent exactly when someone could act on it, and the point of the list is that it
    # SHRINKS. Printing it every run is the pressure.
    for _f, (_lines, _why) in sorted(PARKED.items()):
        print(f"hamlet-floor: PARKED (feature 147, the GM's ruling - known wrong, owned, NOT to be re-derived): {_f} {sorted(_lines)} - {_why}", file=out)
    if unparked:
        print(
            f"COVERAGE: a module on the HAMLET PATH is under 100% ({total:.2f}% combined) - {'; '.join(unparked)} "
            "(feature 145: the path is derived from what the scripted rolls execute; bring it up BY TESTS, spec FR-002)",
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
