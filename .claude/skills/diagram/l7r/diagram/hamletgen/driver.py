"""The pipeline itself: STAGES, and everything that drives it.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import os
import sys
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

# IMPORTED AT MODULE LEVEL, not inside generate(). A local import would run the guard's own
# module-init on the FIRST generate() of a process and not on later ones, and gencache keys a
# map on which engine functions EXECUTED - so the dependency set became call-order dependent
# and unchanged pool maps stopped hitting the cache. Caught by the pre-push gate, feature 127.
from l7r.diagram._invocation import guard
from l7r.diagram.settlement import Settlement
from l7r.diagram.sitegen.jobs import default_jobs as default_jobs  # noqa: PLC0414 - explicit re-export so `hamletgen.default_jobs` still resolves under --strict

from .burial import stage_burial
from .consts import DIKE_CROPS, FIELD_ARCHETYPES, LEFTOVER_FORMS, REF_HOUSEHOLDS
from .frame import stage_crossings, stage_frame, stage_labels, stage_notice
from .hinterland import stage_bamboo, stage_hinterland, stage_windbreak, stage_woodland
from .homesteads import stage_appurtenances, stage_homesteads
from .plan import HamletSpec, SitePlan, plan_site
from .pondstock import stage_pond_stock
from .sink import stage_sink
from .water import stage_field, stage_water_frame, stage_waterward
from .ways import stage_seat, stage_track, stage_web

# THE PIPELINE. Read top to bottom: this is the generator.
#
# THE ORDER IS THE DESIGN, and this tuple is where it lives (feature 111). Water first, then the
# field the water shapes, then the sink the field drains to, then the ways, then the homesteads
# that front the ways, then their appurtenances, then ground cover, then the woods, then the
# frame. It is the same order a human follows and the same order the skill's DRAW ORDER map
# requires (.claude/skills/diagram/CLAUDE.md) - so a change here is a change to that map, and the
# two must move together.
#
# It stays a LITERAL tuple, deliberately, rather than being derived by scanning the submodules for
# `stage_*` functions. Constitution clause 14 says derive a registry that merely restates what the
# code already declares; this one does not - the SEQUENCE is a decision no amount of introspection
# could recover, which is exactly the ordered-data case the clause carves out. Adding a stage means
# deciding where in this list it goes.
# THE ORDER, IN THE GM'S WORDS (2026-08-24, feature 128): "We are reordering the procedural layout of
# the hamlet generation so that farmhouses are rendered after the fields and water, but before any
# village lanes. That is what the feature is. Full stop."
#
#     water, fields, drainage  ->  FARMHOUSES  ->  every lane, without exception
#
# ANY lane. There is no exogenous class and no connector exception. A lane drawn before the houses
# registers a no-build corridor that `_fits` refuses seats against, so it takes ground the houses
# cannot have - which is the defect, whatever the lane represents. Provenance is not the axis.
#
# WHY THE TRACK SITS BETWEEN THE HOUSES AND THE APPURTENANCES, rather than after both. The GM's rule
# is about FARMHOUSES - "farmhouses are rendered after the fields and water, but before any village
# lanes" - and a well, byre or shed is not a farmhouse. Placed after the appurtenances the track had
# to thread a fabric that already held every wellhead, and on the reference hamlet the connector came
# out 3.6 px from one (`features_do_not_overlap`, wells x lanes). Placed before them, the well is sunk
# where the track already runs - which is also the truer order: a track is worn by people walking, and
# a well is dug where they already walk past it.
#
# The WEB still runs last of everything, for the reason recorded below: it FILLS leftover ground
# rather than reserving any.
#
# `stage_seat` and `stage_track` are the two halves of what used to be `stage_ways`. It did two
# unrelated jobs: it SEATED the cluster (`plan.seat`, a hard dependency of `stage_homesteads`) and it
# DREW the connector and spur. Because of the first, the stage could not simply be moved after the
# houses - which is why feature 126 moved only the skeleton and left the other two where they were.
STAGE_PROFILE_ENV = "L7R_STAGE_PROFILE"  # `make map ... PROFILE=1`: print where the roll spent its time (feature 151)

STAGES = (
    stage_water_frame,
    stage_field,
    stage_sink,
    stage_seat,  # decides WHERE the settlement sits. Draws nothing.
    # A POLDER'S WATERWARD FRINGE (feature 150) - the reed strips outside the dike on the flanks that
    # face the water. It needs the SEAT (which flank is landward is a fact about where the village
    # stands) and it RESERVES ground, so it goes here and not in the hinterland: laid at stage 9 it
    # was drawn over a connector already routed at stage 6 (`roads_clear_of_marsh`, the grid knob
    # map); laid before the houses and the track, both treat it as the wet ground it is. No ink on a
    # valley hamlet.
    stage_waterward,
    stage_homesteads,  # the farmhouses, seated with no lane anywhere on the map
    stage_track,  # the connector and the field spur, derived from the placed houses
    stage_appurtenances,
    stage_pond_stock,  # a dike-pond hamlet's pig sties, on the ponds nearest the houses (feature 150 A3; the duck pen retired, 269 B32)
    stage_burial,  # where the hamlet's dead lie - the village's ground, nothing drawn (feature 273; feature 280 M68): seated against the placed houses and wells, reserving ground the web and the scrub work around
    # THE WEB RUNS LAST OF THE BUILT THINGS, after the byres, sheds and wells - not just after the
    # houses. It FILLS leftover ground, so everything that RESERVES ground has to be seated first;
    # that is the same rule that put it after `stage_homesteads` in the first place, applied
    # consistently. Placed between the two, its corridor reserved courtyard ground before the
    # appurtenances were seated and pushed them out of it: measured on Mizuguchi by a
    # settlement-review, three fixtures sat 2-4 ft inside a new lane's clearance and were exiled up
    # to 210 ft, taking byre service from a mean 109 ft to 146 and worst-walk 165 to 266 - which
    # erased feature 121's borrow-coverage fix outright. A 2-to-4-foot conflict should bend the
    # lane, and after this reorder it does, because the byre is simply part of the fabric the web
    # threads around.
    stage_web,
    stage_hinterland,
    stage_woodland,
    stage_windbreak,
    stage_bamboo,  # the bamboo stands, over the scrub that kept out of them (feature 133 T47)
    stage_crossings,
    stage_frame,
    # THE NOTICE BOARD GOES LAST - AFTER THE FRAME (GM 2026-08-29). It used to sit between the lane
    # web and the hinterland, which made it the one built thing the woods had to work around: its
    # keep-out suppressed grove clumps, and on Kashikawa an `entrance` seat on the windward fringe
    # punched a 40 ft hole in the shelter belt that nothing replanted.
    #
    # The GM's reasoning is about the settlement rather than about the bug: "where you put the notice
    # board on the map does depend on what other features already exist ... the real humans that live
    # in the society that decide where the notice board will go will look around at the things which
    # already exist and then decide where to put the notice board. They may even decide to move a
    # notice board which has already been placed. Therefore ... the notice board should be literally
    # the very last thing that is ever put on the map."
    #
    # Everything else here reserves ground or grows into it. The board does neither: it is a 12 x 5 ft
    # plank a village drives in beside a way once the village is there. Placing it last means it can
    # see the whole map, and - the part that fixes the defect by construction - nothing is placed
    # after it for it to displace. It also runs after `crop_to_content`, so the frame is already
    # decided and the board can simply be kept inside it, instead of being sited blind and re-seated
    # by a frame guard that knew nothing about why it had been put where it was.
    stage_notice,
    # ...AND THE LABELS AFTER EVEN THAT (feature 157, GM 2026-08-29). *"add a phase at the very end of
    # every settlement creation process, which is putting down the labels for things. Thus, after the
    # final map feature is added, which on a hamlet is the notice board, there is a final phase in
    # which we add labels for whatever map features get labels. This is because how we place labels
    # will always depend on what else is on the map."*
    #
    # It draws no feature and reserves no ground, so it can only ever be last: a caption is placed
    # against a map that is finished being built. On a hamlet that is byte-neutral BY CONSTRUCTION -
    # nothing is placed between the board and this stage - which is what makes it possible to attribute
    # any caption that moves in this feature to the seat rules rather than to the reorder.
    stage_labels,
)


# ---- driving it ---------------------------------------------------------------------------------


@dataclass
class Report:
    """What one generated hamlet came out as - the row of the cohort table."""

    plan: SitePlan
    failures: list[str]
    path: str | None = None
    # The gate's own FAIL lines for this map. Carried so a caller wanting the DETAIL does not have to
    # re-gate (or, worse, re-build) to get it - `cohort_audit` did exactly that by calling `build`
    # instead of `generate`, which silently measured a different code path than the one that ships.
    fail_lines: list[str] = field(default_factory=list)
    # ONE ROLL (feature 287, FR-002): the re-roll loop that could ship attempt four with a different connector and web is
    # gone - the reach it bought is guaranteed where the web settles (`ways/settle.py`, the reserved corridors drawn) - so
    # the `attempt` / `rerolled_after` fields and the manifest's `roll_attempt` / `roll_after` that attributed a map to
    # its attempt went with it (feature 133 T33 added them).
    # THE MANIFEST THE REPORT WAS JUDGED ON (feature 213): one roll now serves the cohort test (the
    # verdict), the lane-rule fixtures (the finished manifest) and the hamlet floor (the record), so the
    # report carries the finished manifest instead of finishing it into a scratch directory and throwing
    # it away. None only when a caller built the Report by hand.
    manifest: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return not self.failures

    def line(self) -> str:
        p = self.plan
        return (
            f"{p.spec.name:<18} seed={p.spec.seed:<4} hh={p.placed}/{p.spec.households:<3} "
            f"acres={p.acres:5.1f}/{p.target_acres:5.1f} fall={int(p.down_deg):<4} wind={p.windward:<3} "
            f"sink={p.water_sink:<7} {p.cluster_shape[:9]:<10} {p.lane_skeleton:<6} "
            f"{'OK' if self.ok else 'FAIL: ' + ', '.join(self.failures[:4])}" + self._breach_note()
        )

    def _breach_note(self) -> str:
        """The scatter's predicted frame was too small for this roll (feature 224 FR-002): a strip inside the view may
        hold no scatter. The cohort and the pool test fail on it; a hand roll (`make hamlet`) meets it HERE, on the
        line it prints, or nowhere (settlement-review 2026-09-11)."""
        breach = ((self.manifest or {}).get("meta") or {}).get("scatter_frame_breach")
        return f"  SCATTER FRAME BREACHED by {breach} px (left, top, right, bottom) - see specs/224" if breach else ""


@contextlib.contextmanager
def roll_scope(spec: HamletSpec | None = None) -> Iterator[None]:
    """The boundary every roll crosses (feature 210, GM 2026-09-07: "we should clear the clearance memo
    at the end of a roll and ... do the malloc_trim after a roll"). Every loop that runs the stages sits
    inside one - `build()` and the three tools that iterate `STAGES` themselves (`perf_snapshot`,
    `perf_profile`, `placement_stages`); `tests/hamletgen/test_driver.py` walks the engine's AST and fails
    on a stage-running loop outside it. On exit, success or failure: the clearance memo is cleared
    (nothing in it can serve a later roll - its keys are object identities) and glibc's freed arenas go
    back to the kernel. Measured before: a worker rested at 197-266 MB after its rolls with 46 MB of that
    the memo and 14-68 MB retained by the allocator (specs/210 research.md R1).

    AND IT IS WHERE THE ROLL CENSUS IS WRITTEN (feature 213, GM 2026-09-07: "never allow the same hamlet
    to be rolled twice within the tests"): because every stage-running loop enters this scope, a record
    written here cannot miss a roll - which is what the gate's roster check needs, and what a census that
    patched entry points could not promise (`_census.py`). `spec` is what the roll is of; the callers pass
    it, and a scope entered without one is recorded as such."""
    from l7r.diagram import _census
    from l7r.diagram._memory import trim_heap
    from l7r.diagram.hamletgen import clearance
    from l7r.diagram.hamletgen.ways.geom import reset_grounds

    t0 = time.time()
    ok = False
    try:
        yield
        ok = True
    finally:
        clearance.reset()
        reset_grounds()  # ...and the worked grounds, kept per manifest (`ways.geom.memo_ground`)
        trim_heap()
        _census.record("roll", spec=_census.spec_row(spec), ok=ok, dt=round(time.time() - t0, 1))


def build(plan: SitePlan) -> Settlement:
    """Run every stage, in order, against a fresh `Settlement` - once: a map is never rolled again with ground forbidden
    (feature 287, FR-002; the reach that re-roll bought is the web's to draw, `ways/settle.py`)."""
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    # EVERY FOOTPRINT HELD TO THE OVERLAP MATRIX AT RECORD TIME (feature 287 M8): every hamlet placer asks the registry of what
    # stands before it chooses (`Settlement.admits`), so a record it forbids is an engine defect, raised by name
    s.standing.strict = True
    if plan.spec.byre_form is not None:  # a declared byre form bypasses the settlement engine's roll (feature 261)
        s.pin_knob("byre_form", plan.spec.byre_form)
    # THE SPEC'S PINS REACH THE ENGINE'S CATALOG, as `HamletSpec.pins` has always said they do; nothing passed them on until
    # 269 E4, whose knobs (`paddy_rest`, `fan_middle`) have no field of their own on the spec.
    for knob, value in plan.spec.pins.items():
        s.pin_knob(knob, value)
    _run_stages(s, plan)
    return s


def _run_stages(s: Settlement, plan: SitePlan) -> None:
    """Every stage, in order, inside the roll's scope."""
    if not os.environ.get(STAGE_PROFILE_ENV):
        with roll_scope(plan.spec):
            for stage in STAGES:
                stage(s, plan)
                s.standing.resync()  # a record a stage reshaped in place is recorded again (the registry's backstop, feature 287 M8)
        return
    # WHERE THE TIME WENT, in one roll (feature 151, US4). Finding the slow stage used to mean editing
    # this loop by hand, rolling, reading, and reverting - done twice in one session before this existed,
    # and the second time it found `stage_waterward` at 21.7 s of a 45 s gen. An environment variable is
    # the channel because `make map` reaches the stages through `regen.py` and a frozen pool generator;
    # feature 132 forbids a variable that changes what a map ROLLS, and this changes only what is
    # PRINTED - `tests/hamletgen/test_driver.py` asserts the manifest is identical with it set and unset.
    timings: list[tuple[str, float]] = []
    with roll_scope(plan.spec):
        for stage in STAGES:
            t0 = time.time()
            stage(s, plan)
            s.standing.resync()  # as above
            timings.append((stage.__name__, time.time() - t0))
    total = sum(d for _n, d in timings)
    slowest = max(timings, key=lambda t: t[1])
    print(f"\n\033[1mstage profile\033[0m {plan.spec.name} seed {plan.spec.seed}: {total:.1f}s total, slowest {slowest[0]} {slowest[1]:.1f}s", file=sys.stderr)
    for name, dur in sorted(timings, key=lambda t: -t[1]):
        if dur >= 0.05:
            print(f"  {dur:6.2f}s  {100 * dur / total:4.1f}%  {name}", file=sys.stderr)


def stage_for(out_base: str) -> str:
    """A staging base beside `out_base`, for one roll's files (feature 261). The directory sits next to the map's own
    files, so the promotion is a same-filesystem rename, and it carries a copy of the map's `.notes.md` because the
    page reads the notes from beside its own path."""
    import shutil
    import tempfile

    stage = tempfile.mkdtemp(prefix=".roll-", dir=os.path.dirname(out_base) or ".")
    base = os.path.join(stage, os.path.basename(out_base))
    if os.path.exists(out_base + ".notes.md"):
        shutil.copy2(out_base + ".notes.md", base + ".notes.md")
    return base


def promote(stage_base: str, out_base: str | None) -> None:
    """Move a staged roll's files onto `out_base` (each an atomic rename) and remove the stage; with no `out_base`, only
    remove it. THE POOL NEVER SHOWS A REJECTED ROLL (feature 261): `generate` used to finish every attempt straight
    into the map's own files, so between a stranding roll and its re-roll the disk held the roll about to be thrown
    away - and the gate's census, reading the pool beside its sweep, read Sawada's first attempt (146 belt crowns,
    where the kept map draws 179)."""
    import shutil

    stage = os.path.dirname(stage_base)
    prefix = os.path.basename(stage_base)
    if out_base is not None:
        for name in sorted(os.listdir(stage)):
            if name.startswith(prefix + ".") and not name.endswith(".notes.md"):
                os.replace(os.path.join(stage, name), out_base + name[len(prefix) :])
    shutil.rmtree(stage, ignore_errors=True)


def discard_on_failure(stage_base: str | None, roll: Callable[[], Any]) -> Any:
    """Run one roll into its stage, and remove the stage if the roll raises (settlement-review of Kuwabata, feature 261: two
    interrupted rolls left `.roll-*` directories in the pool folder, one holding a whole rejected roll, and a commit swept
    them in - the pool showed the rejected roll `promote` exists to hide)."""
    import shutil

    try:
        return roll()
    except BaseException:
        if stage_base is not None:
            shutil.rmtree(os.path.dirname(stage_base), ignore_errors=True)
        raise


def generate(spec: HamletSpec, out_base: str | None = None, render: bool = True) -> Report:
    """Build a hamlet, FINISH it, gate it, and report. Writes svg/png/json when `out_base` is given.

    THE MANIFEST IS NOT COMPLETE UNTIL `finish()` RUNS, and that cost an hour of chasing a phantom
    defect. `finish` is not just "write the file": it flushes the deferred tree canopies, seats the
    deferred captions, and splices the shared water block - which is where a pond's fill records the
    draw position `pond_fill_covers_channel_mouths` reads. Gating the in-memory manifest before that
    reported a broken pond on every map with a pond, and the maps were fine. So the finish always
    runs; a cohort member with nowhere to go finishes into a scratch directory and is thrown away.

    The roll no longer reports on itself (feature 166 left it one verdict: whether its ways reach every
    house it seated). Since feature 287 that too is guaranteed where it is decided - the seating reserves
    a corridor from every door to the exit strip, the web draws it where its lanes do not reach the house
    (`ways/settle.py`), and a settle that leaves one unreached is refused (`ways/last_resort.py`) - so a
    produced map has no failure to report, and a map is built ONCE (FR-002): the re-roll that
    rebuilt a stranding map with its ground forbidden (feature 133 T33), its snapshot and resume
    (feature 284) and its choice between attempts (features 226, 278) are gone."""
    # FR-008: an expensive operation refuses IN-PROCESS too, not only at the CLI. Without this,
    # `python3 -c "from ... import generate; generate(...)"` walks past every command-shape guard - a
    # bypass that needs no git diff and reads perfectly as diligence.
    guard("l7r.diagram.hamletgen")

    import copy
    import tempfile

    # A COPY OF THE PLAN IS BUILT ON (feature 137): the stages accumulate onto the plan they are handed
    # (`plan.bamboo_polys += ...`), and the report reads the plan the roll built on.
    plan = copy.deepcopy(plan_site(spec))
    s = build(plan)
    # THE MANIFEST CARRIES WHAT THE ROLL SEATED (feature 215, D3): what it seated and the acreage it reached go into the
    # meta BEFORE the finish writes the file, so a map read back from disk - the pool's, which the gate's ratchet reads
    # instead of rolling the reference again - answers the same questions the Report does. The roll's self-report of an
    # unreached farmhouse (`meta.roll_failures`, `farmhouses_reach_a_way`) is gone: the web refuses a settle that leaves
    # one (`ways/last_resort.py:refuse_unreached`, feature 287), so a produced map has none to report.
    s.M["meta"]["roll_placed"] = int(plan.placed)
    s.M["meta"]["roll_acres"] = float(plan.acres)
    # THE FINISH GOES INTO A STAGE that is then promoted onto `out_base` (`promote`), so a roll that dies mid-finish never
    # touches the map's own files (`discard_on_failure`, feature 261). A cohort member with nowhere to go finishes into a
    # scratch directory; finishing completes the manifest the report carries (feature 213).
    if out_base is not None:
        _stage = stage_for(out_base)
        discard_on_failure(_stage, lambda: s.finish(_stage, render=render))
        promote(_stage, out_base)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            s.finish(os.path.join(tmp, "scratch"), render=False)
    return Report(plan=plan, failures=[], path=out_base, manifest=s.M)


def cohort_specs(count: int, first_seed: int = 1, households: int | None = None) -> list[HamletSpec]:
    """The specs a cohort rolls: consecutive seeds, zero-padded names, the household ladder unless a count
    is given. Public so the gate can roll a cohort member through the roll cache one at a time (feature 135)."""
    return [
        HamletSpec(
            name=f"Cohort-{first_seed + i:02d}",
            seed=first_seed + i,
            households=households if households is not None else 10 + ((first_seed + i) * 7) % 11,
        )
        for i in range(count)
    ]


def cohort(count: int, first_seed: int = 1, households: int | None = None, jobs: int | None = None) -> list[Report]:
    """Roll `count` hamlets from consecutive seeds and gate every one.

    This is the experiment's actual evidence. A generator that produces ONE good map has shown that
    a person can drive it to a good map; a generator that produces a cohort of correct maps from
    seeds nobody looked at has shown that the SCRIPT is doing the work.

    THE ROLLS FAN OUT ACROSS PROCESSES (2026-08-16), because a cohort is the verification step of
    every placement-rule change and it was the single biggest sink in the one measured: the fan-toe
    pond fix spent 17.3 min of its 45.7 on two SERIAL 24-seed rolls, ~11 min of that as critical-path
    idle - 20% of the whole task, for work that is embarrassingly parallel. `regen.py` and
    `cohort_audit.py` were given the same fan-out in the 2026-08-15 timings round and this CLI was
    simply missed. Safe by the same argument they use: a map is a pure function of its spec (the
    seed fixes every draw - see "RANDOMNESS IS POSITIONAL OR SCOPED" in the skill's CLAUDE.md), so
    parallelism can only change the wall clock, never a verdict. `generate` IS the worker - it takes
    one spec, defaults `out_base` to None, and is picklable - so there is no wrapper to keep honest.
    Results come back in seed order, so a fanned-out run reads exactly like a serial one.

    `jobs=1` forces the serial path, which is what the in-gate callers want: a pytest worker that
    spawns its own pool is competing with the other 21 (the "CPU inflates 2-4x inside the gate"
    entry in the skill CLAUDE.md)."""
    specs = cohort_specs(count, first_seed, households)
    return roll_pool(specs, default_jobs(count) if jobs is None else max(1, jobs))


def roll_pool(specs: Sequence[HamletSpec], jobs: int, produce: Callable[[HamletSpec], Report] | None = None) -> list[Report]:
    """Roll `specs` - serially for `jobs == 1`, else across a process pool - and return the reports in order.
    The body `cohort()` always had, taking explicit specs (feature 214). `produce` is `generate` unless a
    caller names a module-level producer of its own (feature 215): the fan-out test proves the pool branch -
    the fan-out, the order, the pickling - on a producer that rolls nothing, since a map being a pure
    function of its spec is the immune test's claim and not this branch's."""
    fn = produce if produce is not None else generate
    if jobs <= 1:
        return [fn(spec) for spec in specs]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as ex:
        return list(ex.map(fn, specs))


# THE FITTED COHORT'S KNOWN FAILURES, pinned. Constitution Principle XIII requires a regression to
# be judged against a MEASURED baseline - and until 2026-08-17 no such baseline existed anywhere in
# the tree, so every session either re-measured it by hand (a detached worktree and a full 24-map
# roll, minutes each time) or carried "22 of 24, seeds 22 and 24" in its head. Worse, the summary
# line reads `22/24 passed` whether the two failures are the expected ones or two brand-new ones, so
# a real regression and the steady state are INDISTINGUISHABLE at a glance. That is the exact shape
# the principle exists to stop, left unenforced in the principle's own test bed.
#
# Keyed by seed, valued by the BASE check names (the `[instance]` suffix varies with the map's own
# feature ids and is not part of the identity). Keep this pinned to the FITTED cohort only - the
# held-out range is measured, never tuned, so pinning it would defeat its purpose.
COHORT_BASELINE: dict[int, frozenset[str]] = {
    # EMPTY SINCE FEATURE 166, AND ITS LAST PIN WAS STALE. A cohort report now carries the
    # generator's own self-report - `farmhouses_reach_a_way` and nothing else - because every other
    # rule the battery measured here is proven at the placer that makes it.
    #
    # THE PIN WAS CHECKED BEFORE IT WAS DELETED, and the check is the finding. This dict held seed 24
    # against `paddy_bunds_clear_the_supply_channels`; rolling that cohort member and putting it
    # through the battery one last time returned an EMPTY verdict. The defect was fixed at some point
    # and the pin went on excusing a seed that no longer needed it - which is precisely the "STALE
    # PIN ... Blocking" case `baseline_verdict` below exists to catch, unnoticed because the 24-seed
    # cohort runs only under FULL and the idle runs, not at the ordinary gate.
    #
    # Seed 22 pinned `field_ringed` (retired, feature 141) until feature 141 retired that check (the GM's cut).
}
COHORT_BASELINE_SIZE = 24  # the pin describes exactly `--batch 24` from seed 1


def baseline_verdict(reports: Sequence[Report], pin: dict[int, frozenset[str]] | None = None) -> tuple[list[str], bool]:
    """Judge a canonical cohort against `COHORT_BASELINE`: `(lines to print, is_clean)`.

    `pin` is injectable so the LOGIC can be tested without pinning the tests to today's baseline -
    otherwise every honest cohort improvement would break this function's own tests, which is how a
    guard ends up loosened to keep the suite quiet.

    Two ways to be dirty, and BOTH are failures, for the same reason `waivers_are_live` fails on a
    waiver whose defect was fixed: a baseline nobody maintains stops being a baseline.

    - A NEW failure (a seed or a check the pin does not cover) is a regression. Blocking.
    - A pinned failure that now PASSES means the pin is stale and is quietly excusing a seed that no
      longer needs it. Blocking too, with the edit to make - otherwise the pin only ever loosens,
      and the next real regression on that seed is invisible."""
    base = COHORT_BASELINE if pin is None else pin
    actual = {r.plan.spec.seed: {f.split("[")[0] for f in r.failures} for r in reports if r.failures}
    new = {seed: sorted(checks - base.get(seed, frozenset())) for seed, checks in actual.items()}
    new = {seed: checks for seed, checks in new.items() if checks}
    gone = {seed: sorted(expected - actual.get(seed, set())) for seed, expected in base.items()}
    gone = {seed: checks for seed, checks in gone.items() if checks}
    if not new and not gone:
        return [f"cohort matches the pinned baseline ({len(base)} expected failures) - NO NEW REGRESSIONS"], True
    lines: list[str] = []
    for seed, checks in sorted(new.items()):
        lines.append(f"REGRESSION seed {seed}: {', '.join(checks)} - not in the pinned baseline")
    for seed, checks in sorted(gone.items()):
        lines.append(f"STALE PIN seed {seed}: {', '.join(checks)} now PASSES - remove it from COHORT_BASELINE in hamletgen/driver.py")
    if new:
        lines.append("A new cohort failure BLOCKS the merge (constitution Principle XIII): fix it, revert, or get an explicit GM waiver.")
    return lines, False


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a Rokugani rice hamlet from a seed, and gate it.")
    ap.add_argument("--name", default="Hamlet")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--households", type=int, default=REF_HOUSEHOLDS)
    ap.add_argument("--down-deg", type=float, default=None)
    ap.add_argument("--sink", choices=("pond", "offmap"), default=None)
    ap.add_argument("--windward", default=None)
    ap.add_argument("--bamboo", choices=("none", "homestead", "thicket", "both"), default=None, help="pin the bamboo knob (feature 133 T47: one map per knob value is owed at unlock)")
    ap.add_argument("--archetype", choices=FIELD_ARCHETYPES, default=None, help="pin the field archetype (feature 150: the dike-pond is opt-in, like the polder)")
    ap.add_argument("--pond-layout", choices=("grid", "mosaic"), default=None, help="pin a dike-pond's arrangement (feature 150: one map per knob value is owed)")
    ap.add_argument("--manure-form", choices=("heap", "pit"), default=None, help="pin the manure fixture's form (feature 150 A2)")
    ap.add_argument("--dike-crop", choices=sorted(set(DIKE_CROPS)), default=None, help="pin a dike-pond's dike planting (feature 150 A6)")
    ap.add_argument("--leftover", choices=LEFTOVER_FORMS, default=None, help="pin a dike-pond's leftover parcels (feature 150 B2)")
    ap.add_argument("--form", choices=("nucleated", "dispersed", "linear"), default=None, help="pin the settlement form (feature 291: the reference hamlet is pinned nucleated)")
    ap.add_argument("--grove-sides", type=int, choices=(2, 3, 4), default=None, help="pin how many sides each farm's grove takes (feature 291)")
    ap.add_argument("--farm-water", choices=("channel", "well"), default=None, help="pin a dispersed farm's own water (feature 291 amendment 5)")
    ap.add_argument("--row-line", choices=("street", "edge"), default=None, help="pin a row village's line (feature 291)")
    ap.add_argument("--row-sides", choices=("one", "both"), default=None, help="pin a row village's sides (feature 291)")
    ap.add_argument("--row-water", choices=("own", "shared"), default=None, help="pin a row village's water (feature 291)")
    ap.add_argument("--out", default=None, help="write <out>.svg/.png/.json")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--batch", type=int, default=0, help="roll N hamlets from consecutive seeds and gate them all")
    ap.add_argument("--jobs", type=int, default=None, help="worker processes for --batch (default: cpus - 2, capped at the cohort size; 1 for serial)")
    args = ap.parse_args(list(argv) if argv is not None else None)

    if args.batch:
        reports = cohort(args.batch, first_seed=args.seed, jobs=args.jobs)
        for r in reports:
            print(r.line())
        good = sum(1 for r in reports if r.ok)
        print(f"\n{good}/{len(reports)} passed the full gate")
        # The RATE is not the verdict - the failing SET is. `22/24` reads identically whether the
        # two are the pinned pre-existing ones or two fresh regressions, which is why the pin exists.
        if args.seed == 1 and args.batch == COHORT_BASELINE_SIZE:
            lines, clean = baseline_verdict(reports)
            for line in lines:
                print(line)
            return 0 if clean else 1
        print(f"(no pinned baseline for this range - it describes --batch {COHORT_BASELINE_SIZE} from seed 1)")
        return 0 if good == len(reports) else 1

    report = generate(
        HamletSpec(
            name=args.name,
            seed=args.seed,
            households=args.households,
            down_deg=args.down_deg,
            water_sink=args.sink,
            windward=args.windward,
            bamboo=args.bamboo,
            field_archetype=args.archetype,
            pond_layout=args.pond_layout,
            manure_form=args.manure_form,
            dike_crop=args.dike_crop,
            leftover=args.leftover,
            settlement_form=args.form,
            grove_sides=args.grove_sides,
            farm_water=args.farm_water,
            row_line=args.row_line,
            row_sides=args.row_sides,
            row_water=args.row_water,
        ),
        out_base=args.out,
        render=not args.no_render,
    )
    print(report.line())
    for f in report.failures:
        print("  FAIL", f)
    return 0 if report.ok else 1
