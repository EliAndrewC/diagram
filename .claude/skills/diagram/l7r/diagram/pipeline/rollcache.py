"""Serve a test's rolled map from cache while nothing it depends on has changed (feature 135, GM 2026-08-27).

WHY. The unlocked `make done` was four to five minutes, and the minutes were the map-rolling tests
re-rolling the same fixed specs on every run - three polder hamlets at ~100 s each, a four-seed cohort,
the reference hamlet - whether or not anything they execute had changed. The GM: *"things like
recomputing things that could be cached, thus wasting millions of operations on every test run"*.

HOW, AND WHY IT IS SAFE. The same argument as the pool cache (`gencache`): a map is a pure function of
its spec and the code + data its roll executes. So a roll is keyed EXACTLY the way a pool gen is -
`gencache.record` captures every engine function the roll executed and every file it read, and
`gencache.key_for` hashes their source plus every module's top level, the interpreter, renderer and
dependency state. A key that matches means the roll would produce the same bytes; the payload the test
asserts on (the plan and the finished manifest, or the gate's report) is served, and the ASSERTIONS
still run on it - only the production is skipped, never the judgment. A key that moved - a function the
roll executed changed - rolls for real, which is exactly when the test has something new to say.

WHAT IT NEVER SERVES. Any doubt at all - a missing or unreadable entry, a payload that will not
unpickle, a vanished data file - regenerates. Under `GATE_NO_CACHE=1` and under the FULL run
(`L7R_TESTS_FULL=1`, where the coverage floors are enforced and a served roll would execute none of the
rolled code) every call produces - EXCEPT a caller that opts into `share=True`, which produces once per
process and re-serves those bytes thereafter (feature 147; see `_SHARED_BYPASS`). Only the spec roll opts in.

PRODUCING AND STORING ARE NOW SEPARATE QUESTIONS (feature 192). The FULL run still produces on every
call - that is what the coverage floors need and it has not changed - but a `roll:` subject under it now
also RECORDS what it executed, because `hamlet_floor` derives the hamlet path from those records and,
finding none, used to re-roll the same maps itself for a measured 401.6 s. `GATE_NO_CACHE=1` is
deliberately excluded and still leaves nothing behind. See `_stores_under_bypass`.

ONE ROLL PER SPEC, IN A CHILD, SHARED BEHIND A LOCK (feature 213, GM 2026-09-07: "never allow the same
hamlet to be rolled twice within the tests"). `hamlet()`, `report()` and `report_deps()` read one
`roll:<spec>` subject - `generate` with its kept manifest - produced once per run in a child process and
handed to every other worker that asks; a worker that asks while the roll is in flight WAITS on its lock
instead of rolling its own (`_share_lock`). The census the gate writes at `driver.roll_scope` proves it on
every run (`_census.py`, `ci/rollverdict.py`, the roster `tests/rolls.py`). Before this, `hamlet()` rolled
`build` alone under one subject and `report()` rolled `generate` under another, and the first wave of
workers each rolled the shared specs at t=0: 37 rolls of 14 specs per gate (specs/213 research R1).

A TEST THAT MONKEYPATCHES THE ENGINE goes through `keyed_to(test, ...)`, never bare `obtain`: a patched
function changes what the roll does without changing any hashed engine source, so the engine key alone
cannot see it. What CAN change the patch is the test's own code - the lambdas live there - so the test
function's source joins the key. The roll is then a function of (the engine functions it executed, the
files it read, the test's source), all three hashed, which is exactly the unpatched argument again.

Excluded from the engine file set (`gencache._NOT_ENGINE`): this module serves rolls and draws nothing.
"""

from __future__ import annotations

import contextlib
import fcntl
import glob
import hashlib
import inspect
import json
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

from l7r.diagram import _census
from l7r.diagram.pipeline import gencache

if TYPE_CHECKING:
    from l7r.diagram.hamletgen import HamletSpec, Report, SitePlan

FULL_ENV = "L7R_TESTS_FULL"  # set by `make test-full`: the full run produces everything


def bypassed() -> bool:
    return os.environ.get(gencache.GATE_BYPASS) == "1" or os.environ.get(FULL_ENV) == "1"


def _entry(subject: str) -> str:
    return os.path.join(gencache.CACHE_DIR, "rolls", hashlib.sha256(subject.encode()).hexdigest()[:24])


def _place(data: bytes, dest: str) -> None:
    """Write-to-temp-then-replace, so a concurrent reader (another xdist worker rolling the same subject) sees
    old bytes or new bytes, never half; meta.json lands LAST, so an entry is valid only once its payload is."""
    tmp = f"{dest}.tmp{os.getpid()}"
    Path(tmp).write_bytes(data)
    os.replace(tmp, dest)


# THE BYPASS USED TO RE-ROLL THE SAME SPEC ONCE PER CALLER (feature 147). The FULL run bypasses SERVING so
# the coverage floors watch the rolled code execute - which is right, and which nobody costed: the 31 scripted
# negative fixtures share just TWO specs between them, so the bypass rolled one of two identical hamlets 31
# times, ~14 s each, ~430 s of CPU to execute a set of lines that one roll executes. Measured 2026-08-29.
#
# So the bypass now produces each distinct subject ONCE per process and shares it. The floors are unaffected
# for the reason the sharing is safe at all: the first call performs a real roll, so every line an identical
# roll would execute is executed and traced; the other thirty would have executed the SAME lines.
#
# WHAT IS SHARED IS THE BYTES, NOT THE OBJECT, and that is the whole of the isolation argument. A served HIT
# unpickles a fresh payload for every caller, so no test has ever been able to affect another's geometry
# through this module; storing the pickle and re-loading it keeps that exactly, at microseconds against the
# 14 s it replaces. Sharing the object itself would let one fixture's deliberate break leak into the next
# and silently disarm it - the one failure this pass must not introduce.
#
# KEYED ON THE PRODUCER AS WELL AS THE SUBJECT. `subject` is contracted to determine the roll completely and
# in the engine it does (a spec's repr), but a TEST may legitimately hand two different `produce` callables
# the same toy subject, and sharing across those would serve one test another's payload - a far worse bug
# than the one this fixes. The producer's code object separates them: every caller inside `hamlet()` shares
# one code object (so the 31 fixtures share, which is the point), while two different call sites do not.
_SHARED_BYPASS: dict[tuple[str, str], bytes] = {}


def _share_key(subject: str, produce: Callable[[], Any]) -> tuple[str, str]:
    """The producer's CALL SITE, not `id(code)`. An id is unique only among LIVE objects, so a code object
    that has been collected can have its id handed to a different one - and the failure mode is serving one
    caller another caller's roll, which is far worse than the re-rolling this whole mechanism removes. The
    file, line and name of the code object are stable for the life of the process and unique per call site.
    """
    code = getattr(produce, "__code__", None)
    site = f"{code.co_filename}:{code.co_firstlineno}:{code.co_name}" if code is not None else repr(type(produce))
    return (subject, site)


#: How long a waiter gives the holder of a share lock before rolling itself - longer than any roll (the slowest
#: cohort seed under coverage was 205 s with its re-rolls), so it fires only for a holder that is wedged.
LOCK_WAIT_S = 600.0


@contextlib.contextmanager
def _share_lock(run_path: str | None) -> Iterator[None]:
    """An exclusive lock beside the run store's payload for one key (feature 213 FR-002) - or nothing when
    there is no run store, which is a single process with nobody to wait for. `flock`, so a holder that dies
    releases it; polled with a bound, so a wedged holder cannot hang the run: past LOCK_WAIT_S the waiter
    proceeds without the lock and rolls, which is today's behavior."""
    if run_path is None:
        yield
        return
    os.makedirs(os.path.dirname(run_path), exist_ok=True)
    fd = os.open(run_path + ".lock", os.O_RDWR | os.O_CREAT, 0o644)
    held = False
    try:
        deadline = time.time() + LOCK_WAIT_S
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                held = True
                break
            except OSError:
                if time.time() >= deadline:
                    break
                time.sleep(0.25)
        yield
    finally:
        if held:
            with contextlib.suppress(OSError):
                fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


#: How many child rolls may run at once across the whole run (feature 213 FR-010): each is ~120-270 MB and
#: 15-70 s, and worksteal starts every gate module at t=0. Measured in specs/213 research R4.
ROLL_SLOTS_ENV = "L7R_ROLL_SLOTS"
ROLL_SLOTS_DEFAULT = 4


@contextlib.contextmanager
def _roll_slot() -> Iterator[None]:
    """One of N slots for a child roll: the first free slot, else a wait on the slot this pid hashes to.
    Slots live in the run share directory (or the temp directory without one, so a plain `make test-file`
    of two rolling files is bounded too)."""
    n = max(1, int(os.environ.get(ROLL_SLOTS_ENV) or ROLL_SLOTS_DEFAULT))
    base = _run_share_dir() or os.path.join(tempfile.gettempdir(), "l7r-roll-slots")
    os.makedirs(base, exist_ok=True)
    fds = [os.open(os.path.join(base, f"slot-{i}.lock"), os.O_RDWR | os.O_CREAT, 0o644) for i in range(n)]
    held = -1
    try:
        for i, fd in enumerate(fds):
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                held = i
                break
            except OSError:
                continue
        if held < 0:
            held = os.getpid() % n
            fcntl.flock(fds[held], fcntl.LOCK_EX)
        yield
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(fds[held], fcntl.LOCK_UN)
        for fd in fds:
            os.close(fd)


def reset_shared() -> None:
    """Forget every shared payload - the process dict AND this run's on-disk store.

    BOTH, and the second half was a real hole rather than tidiness. The run store outlives a single test,
    so a test that expects to PRODUCE would silently be handed a sibling's payload if an earlier test in
    the same run had used the same subject and call site. `tests/pipeline/test_rollcache.py`'s
    parametrized bypass test is exactly that shape and caught it: the first parameter wrote `shared-toy`,
    the second then got `BYPASS-SHARED-RUN` where it asserted `BYPASS`.
    """
    _SHARED_BYPASS.clear()
    run_dir = _run_share_dir()  # ...not `_run_share_path(("", ""))`, whose dummy key is explained there
    if run_dir is not None:
        shutil.rmtree(run_dir, ignore_errors=True)


def _run_share_path(key: tuple[str, str]) -> str | None:
    """Where a shared payload lives for THIS RUN, or None when there is no run to scope it to.

    THE POINT, AND WHY IT IS NOT THE CACHE FULL BYPASSES (GM 2026-08-31): *"what we are essentially doing
    is using a cache, but it's just that we are building the cache as part of the test run in order to
    ensure that the process that builds the cache is part of what's being tested."* A `rollcache` HIT
    serves an entry produced by an EARLIER run, so nothing executes and no coverage is recorded - which is
    exactly why the FULL run bypasses serving. A payload produced by THIS run and reused within it is a
    different thing: the code ran, its lines are recorded, and coverage is combined across xdist workers
    at the end, so one execution covers the lines for every worker.

    `PYTEST_XDIST_TESTRUNUID` is set by xdist in each worker (`xdist/remote.py`) and is shared by every
    worker of one run and by no other run, so the store cannot outlive the run that built it. Without
    xdist there is no id and this returns None: the per-process dict above is then the whole mechanism,
    exactly as before.

    WHY THIS IS SCOPED TO CALLERS THAT ALREADY OPT IN. Feature 147 turned sharing on for `obtain`
    generally and had to turn it back off: the hamlet-path coverage floor went NON-DETERMINISTIC
    (`hinterland.py` 503-504 flipped between otherwise identical runs), because different call sites take
    different branches and which one produced varied with scheduling. Nothing here widens that envelope -
    it makes the EXISTING opt-in (`hamlet()`, whose callers all ask for the identical artifact through the
    identical produce) reach across workers instead of stopping at the process boundary.
    """
    directory = _run_share_dir()
    if directory is None:
        return None
    # `_share_key` returns a TUPLE (subject, producer-identity), not a string - so it is repr'd
    # rather than encoded. Caught by the FULL run, which was the only scope that exercised this.
    return os.path.join(directory, hashlib.sha256(repr(key).encode()).hexdigest()[:24] + ".pickle")


def _run_share_dir() -> str | None:
    """The directory holding THIS RUN's shared payloads, or None when there is no run to scope to.

    **LIFTED OUT so that removing the store does not have to invent a key** (2026-08-31). `reset_shared`
    used to ask for `_run_share_path(("", ""))` and take its `dirname` - a dummy key, passed only to get
    at the directory it happens to live in. That couples deletion to the KEY's shape, and the key's
    shape has already broken once here: `_share_key` returns a tuple, an earlier draft called `.encode()`
    on it, and only the FULL run exercised the path at all. Had that draft shipped, `reset_shared` would
    have raised while clearing rather than while storing - the same bug wearing a different hat, in the
    function whose whole job is cleaning up after the other one."""
    uid = os.environ.get("PYTEST_XDIST_TESTRUNUID")
    if not uid:
        return None
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in uid)[:64]
    return os.path.join(tempfile.gettempdir(), f"l7r-runshare-{safe}")


def _produce_and_store[T](subject: str, produce: Callable[[], T], recorded: Callable[[], tuple[T, dict[str, Any]]] | None = None) -> tuple[T, dict[str, Any]]:
    """Roll, RECORD what the roll executed, and store the entry - payload first, meta LAST.

    ONE BODY, deliberately (feature 192): both the ordinary MISS path and the FULL-run bypass store
    through here, so the pair invariant `_place` exists to hold cannot drift apart between two
    copies of these five lines. Writing meta alone - the payload withheld - is what the rejected
    `deps.json` design was avoiding; sharing this function makes that impossible by construction.

    `recorded`, when given, produces the payload AND its dependency record together - a roll made in a
    CHILD process records itself there, where the functions actually ran (feature 210, `hamlet()`)."""
    entry = _entry(subject)
    if recorded is not None:
        payload, deps = recorded()
    else:
        holder: list[T] = []
        deps = gencache.record(lambda: holder.append(produce()))
        payload = holder[0]
    os.makedirs(entry, exist_ok=True)
    _place(pickle.dumps(payload), os.path.join(entry, "payload.pickle"))
    _place(json.dumps({"key": gencache.key_for(subject.encode(), deps), "deps": deps, "subject": subject}).encode(), os.path.join(entry, "meta.json"))
    return payload, deps


def _stores_under_bypass(subject: str) -> bool:
    """Does this bypassed roll still leave its record behind? (feature 192, and the WHOLE of the why.)

    THE GATE USED TO ROLL THE SAME MAPS TWICE. `obtain` bypasses SERVING under the FULL run because a
    served roll executes nothing the coverage floors could see - correct, and unchanged. But the
    bypass also stored NOTHING, so `hamlet_floor`, which derives the hamlet path from exactly these
    records, found none and re-rolled its subjects itself: a measured 401.6 s phase against ~1 s when
    the records exist. The suite had already rolled four of them moments earlier.

    TWO CONDITIONS, and each is load-bearing:
      - `L7R_TESTS_FULL` only. `bypassed()` is ALSO true for `GATE_NO_CACHE=1`, which is the
        documented "regenerate everything, leave nothing behind" escape - folding the two together
        would silently change a contract nobody asked to change.
      - `roll:` subjects only (the one subject per spec since feature 213; `report:` before it), because that is what the floor consumes. `test:` rolls are the
        shared fixture path and `test:` rolls are monkeypatched; neither feeds the floor.

    WHY STORING A FULL-RUN PAYLOAD IS SAFE, which is the part that deserved measuring rather than
    asserting: a later non-FULL run can now HIT on an entry this run wrote. That is only legitimate
    if FULL-run bytes equal MISS-run bytes, so the environment axes the gate sets were checked -
    `L7R_TESTS_FULL` is read only here and in `tests/_scope.py` (which selects WHICH tests and specs
    run, never engine behavior inside a roll), and no engine module reads `L7R_TESTS_EXHAUSTIVE` or
    `L7R_COV_FLOORS` at all. The roll is the same program either way."""
    # `roll:` since feature 213 - the ONE subject per spec that hamlet(), report() and report_deps() all read
    return os.environ.get(FULL_ENV) == "1" and os.environ.get(gencache.GATE_BYPASS) != "1" and subject.startswith("roll:")


def obtain[T](subject: str, produce: Callable[[], T], share: bool = False, recorded: Callable[[], tuple[T, dict[str, Any]]] | None = None) -> tuple[T, str]:
    """`(payload, how)` for `subject` - "HIT" (served), "MISS" (produced, recorded, stored),
    "BYPASS-STORED" (produced and recorded, never served - the FULL run's `roll:` subjects, feature
    192), "BYPASS" (produced, nothing stored) or "BYPASS-SHARED" (this process already produced this
    subject under the bypass; a fresh copy of it). `subject` must determine the roll completely (a
    spec's repr). `recorded` (feature 210) is `produce` with its own dependency record, for a roll that
    runs in a child process; the storing paths use it and every serving path is unchanged."""
    if bypassed():
        if not share:
            if _stores_under_bypass(subject):
                return _produce_and_store(subject, produce, recorded)[0], "BYPASS-STORED"
            return produce(), "BYPASS"
        key = _share_key(subject, produce)
        cached = _SHARED_BYPASS.get(key)
        if cached is not None:
            _census.record("served", subject=subject[:80], how="BYPASS-SHARED")
            return pickle.loads(cached), "BYPASS-SHARED"  # noqa: S301 - our own bytes, dumped below
        run_path = _run_share_path(key)
        # THE FIRST WAVE WAITS (feature 213 FR-002, GM 2026-09-07). The run store served a worker that
        # started AFTER another had finished the roll; under worksteal every gate module starts at t=0, and
        # the census found Inashiro rolled by four workers at once, Kuwabata by three, the polder by two - 9
        # rolls and ~230 s of CPU per gate for payloads the share existed to hand out. So the store is now
        # guarded by a lock per key: the first worker takes it and rolls; a worker that finds it held waits
        # for the payload the holder writes, then reads it. A holder that dies releases the lock with no
        # payload, and the next waiter rolls; the wait is bounded so a wedged holder cannot hang the run.
        with _share_lock(run_path):
            if run_path is not None and os.path.exists(run_path):
                with contextlib.suppress(OSError, EOFError, pickle.UnpicklingError):
                    with open(run_path, "rb") as fh:
                        payload_from_run = pickle.load(fh)  # noqa: S301 - written by a sibling worker of this run
                    _SHARED_BYPASS[key] = pickle.dumps(payload_from_run)
                    _census.record("served", subject=subject[:80], how="BYPASS-SHARED-RUN")
                    return payload_from_run, "BYPASS-SHARED-RUN"
            # ...AND THE ONE ROLL IS STORED WHEN THE FLOOR READS IT (feature 213 FR-001, 207's D14): a `roll:` subject's
            # record goes to the on-disk entry too, so `report_deps` (the hamlet floor) reads the roll the tests made
            # instead of rolling the spec a second time.
            payload = _produce_and_store(subject, produce, recorded)[0] if recorded is not None and _stores_under_bypass(subject) else produce()
            # an unpicklable payload shares nothing rather than sharing wrongly - the next caller rolls
            with contextlib.suppress(pickle.PicklingError, TypeError, RecursionError):
                blob = pickle.dumps(payload)
                _SHARED_BYPASS[key] = blob
                if run_path is not None:
                    os.makedirs(os.path.dirname(run_path), exist_ok=True)
                    _place(blob, run_path)
        return payload, "BYPASS"
    entry = _entry(subject)
    meta_path, payload_path = os.path.join(entry, "meta.json"), os.path.join(entry, "payload.pickle")
    try:
        meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        if meta.get("subject") == subject and gencache.key_for(subject.encode(), meta.get("deps")) == meta.get("key"):
            with open(payload_path, "rb") as fh:
                served: T = pickle.load(fh)  # noqa: S301 - our own entry, written below
            return served, "HIT"
    except OSError, ValueError, KeyError, EOFError, AttributeError, pickle.UnpicklingError:
        pass  # an unreadable or half-written entry is DOUBT, and doubt produces - the pool cache's rule
    return _produce_and_store(subject, produce, recorded)[0], "MISS"


def keyed_to[T](test: Callable[..., object], produce: Callable[[], T], label: str = "", child: str | None = None) -> tuple[T, str]:
    """`obtain` for a roll whose behavior depends on the TEST's own code - its monkeypatches - so the
    test function's source joins the key: edit the patch and the roll is re-made; leave it and the
    engine key decides, as for any roll. `produce` must return plain data (what the assertions read),
    never the Settlement itself."""
    src = inspect.getsource(test)
    subject = f"test:{test.__module__}.{test.__qualname__}:{label}:{hashlib.sha256(src.encode()).hexdigest()[:16]}"
    if child is None:
        return obtain(subject, produce)
    # THE ROLL RUNS IN A CHILD (feature 213 FR-007): `child` names a module-level function (`module:function`,
    # the test's produce closure lifted out - the feature-146 doctrine) that the child imports and calls with
    # no argument; `produce` is kept only as the in-process fallback signature `obtain` expects.

    def recorded() -> tuple[T, dict[str, Any]]:
        return _in_child(child, None)

    return obtain(subject, lambda: recorded()[0], recorded=recorded)


def _roll_payload(spec: HamletSpec) -> tuple[SitePlan, dict[str, Any], Report]:
    """THE ONE ROLL of a spec (feature 213 FR-001): `generate()` - the re-roll loop, the finish, the
    reachability verdict - and what every reader needs of it: the plan, the finished manifest of the kept
    attempt, and the Report. `hamlet()` reads the first two, `report()` the third, `report_deps()` (the
    hamlet floor) the dependency record taken around it. Before this, `hamlet()` rolled `build` alone and
    `report()` rolled `generate` under a different cache subject, so the cohort seeds were rolled twice
    per gate and the lane-rule tests read a map `generate` might have re-rolled. Module-level so the child
    driver calls it by name and a test can compare the child's result with the same code run in-process."""
    from l7r.diagram import hamletgen as hg

    rep = hg.generate(spec, out_base=None, render=False)
    assert rep.manifest is not None, "generate() carries the kept attempt's manifest (feature 213)"
    return rep.plan, rep.manifest, rep


# THE ROLL LEAVES THE WORKER (feature 210, GM 2026-09-07: "we should also roll in a forked child ... test out by
# trying it in one place"). This is the one place: `hamlet()` produces the gate fixtures' rolls, the bulk of a
# gate's rolls, and its payload is already the picklable pair the FULL run shares between workers. The child is
# a SUBPROCESS rather than `os.fork()` - a forked copy of a coverage-traced xdist worker carries the parent's
# `sys.monitoring` tool, its execnet channel and pytest-cov's hooks ("two recorders fight over the sys.monitoring
# tool id", gate_obtain) - and it is the pool sweep's proven shape (`gencache.gate_obtain`, feature 026): under a
# coverage-recording parent it runs `coverage run --parallel-mode` with the parent's hooks stripped and publishes
# its data file into the skill directory's `.coverage.*` glob for the Makefile's `combine --append`; plain
# otherwise. The dependency record the cache keys on is taken IN the child, where the functions ran. What it
# saves: the roll's whole working set - the 121 MB a roll ends at, the memo, the retained arenas, the pymalloc
# fragmentation - never enters the worker (specs/210 research.md R1, R3). The roll-out list is the spec's FR-004.
_CHILD_DRIVER = (
    "import importlib, pickle, sys\n"
    "sys.path.insert(0, {here!r})\n"
    "from l7r.diagram.pipeline import gencache\n"
    "with open({spec_path!r}, 'rb') as fh:\n"
    "    arg = pickle.load(fh)\n"
    "mod, fn = {target!r}.rsplit(':', 1)\n"
    "produce = getattr(importlib.import_module(mod), fn)\n"
    "holder = []\n"
    "deps = gencache.record(lambda: holder.append(produce(arg) if arg is not None else produce()))\n"
    "with open({out_path!r}, 'wb') as fh:\n"
    "    pickle.dump((holder[0], deps), fh)\n"
)

#: The child's target for THE roll of a spec: `module:function`, called with the spec.
ROLL_TARGET = "l7r.diagram.pipeline.rollcache:_roll_payload"


def _parent_is_covered() -> bool:
    """Is THIS process recording coverage - so the child must record its own, or the roll's lines vanish
    from the floor. Two signals, either suffices: pytest-cov's subprocess environment (`COV_CORE_SOURCE`),
    and a live `coverage.Coverage` in this process (what pytest-cov actually runs in an xdist worker; the
    landing gate of feature 210 lost three lines of `water.py` to the environment signal alone)."""
    if os.environ.get("COV_CORE_SOURCE"):
        return True
    cov = sys.modules.get("coverage")
    current = getattr(getattr(cov, "Coverage", None), "current", None)
    return current is not None and current() is not None


def _hamlet_in_child(spec: HamletSpec) -> tuple[tuple[SitePlan, dict[str, Any], Report], dict[str, Any]]:
    """`(_roll_payload(spec), its dependency record)`, produced in a child process - see `_CHILD_DRIVER`."""
    return _in_child(ROLL_TARGET, spec)


def _in_child(target: str, arg: Any) -> tuple[Any, dict[str, Any]]:
    """`(target(arg), its dependency record)` from a child Python. `target` is `module:function`: feature 213
    FR-007 generalizes feature 210's child so a test's lifted produce function runs here by name, with its
    patches applied inside the function; `arg` is pickled in, and None means call with no argument."""
    here = gencache.HERE
    workdir = tempfile.mkdtemp(prefix="rollchild-")
    try:
        spec_path, out_path, driver = (os.path.join(workdir, n) for n in ("spec.pickle", "out.pickle", "driver.py"))
        with open(spec_path, "wb") as fh:
            pickle.dump(arg, fh)
        Path(driver).write_text(_CHILD_DRIVER.format(here=here, spec_path=spec_path, out_path=out_path, target=target), encoding="utf-8")
        # the child must be the ONLY coverage recorder in its process (gate_obtain's rule): the parent's
        # pytest-cov hooks are stripped, and when the parent IS under coverage the child records its own
        under_coverage = _parent_is_covered()
        env = {k: v for k, v in os.environ.items() if not k.startswith(("COV_CORE_", "COVERAGE_"))}
        covbase = os.path.join(workdir, "cov")
        if under_coverage:
            env["COVERAGE_FILE"] = covbase
            cmd = [sys.executable, "-m", "coverage", "run", "--parallel-mode", driver]
        else:
            cmd = [sys.executable, driver]
        with _roll_slot():  # at most N child rolls at once across the run (FR-010)
            proc = subprocess.run(cmd, cwd=here, env=env, capture_output=True, text=True, check=False)
        if proc.returncode or not os.path.isfile(out_path):
            raise RuntimeError(f"the roll child failed for {target} {arg!r} (exit {proc.returncode}):\n{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}")
        with open(out_path, "rb") as fh:
            payload, deps = pickle.load(fh)  # noqa: S301 - our own child's bytes, written above
        for i, covfile in enumerate(sorted(glob.glob(covbase + ".*"))):
            # published onto the session's data-file glob that `coverage combine --append` sweeps -
            # copy-then-replace, as gate_obtain: the scratch dir may be on another filesystem. UNIQUE PER
            # CHILD, not per worker: a worker rolls several hamlets, and a name keyed on the worker's pid
            # alone had each child overwrite the last - the landing gate lost one line of water.py to it.
            dest = os.path.join(here, f".coverage.rollchild-{os.getpid()}-{os.path.basename(workdir)[len('rollchild-') :]}-{i}")
            shutil.copyfile(covfile, dest + ".tmp")
            os.replace(dest + ".tmp", dest)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return payload, deps


def _roll(spec: HamletSpec) -> tuple[tuple[SitePlan, dict[str, Any], Report], str]:
    """THE ONE ROLL a gate makes of `spec` (feature 213 FR-001): `(plan, manifest, report)` under the one
    subject `roll:<spec>`, produced in a child (feature 210), shared across the run's workers behind the
    first-wave lock (FR-002), and STORED under the full-run bypass so the hamlet floor's `report_deps` reads
    the same roll (207's D14). `hamlet()` and `report()` are its two views."""

    def recorded() -> tuple[tuple[SitePlan, dict[str, Any], Report], dict[str, Any]]:
        return _hamlet_in_child(spec)

    def produce() -> tuple[SitePlan, dict[str, Any], Report]:
        return recorded()[0]

    return obtain(f"roll:{spec!r}", produce, share=True, recorded=recorded)


def hamlet(spec: HamletSpec) -> tuple[SitePlan, dict[str, Any]]:
    """The plan and the FINISHED manifest of a scripted hamlet built from `spec` (no files) - the roll
    `generate()` kept, since feature 213 (before it, a `build`-only roll under a subject of its own)."""
    (plan, manifest, _rep), _how = _roll(spec)
    return plan, manifest


def report(spec: HamletSpec) -> tuple[Report, str]:
    """`hg.generate(spec)` - build, finish, gate, with the re-roll loop - and how it was obtained."""
    (_plan, _manifest, rep), how = _roll(spec)
    return rep, how


def report_deps(spec: HamletSpec) -> dict[str, Any]:
    """The DEPENDENCY RECORD of `report(spec)` - every engine function and file the roll executed - from
    the cache when a valid record exists, else by rolling and recording now. Never bypassed: the FULL
    run bypasses SERVING (a served roll executes nothing the coverage floors could see), but the floor
    that derives the hamlet path from these records (feature 145, `tools/hamlet_floor.py`) needs the
    record itself, and on a fresh clone or CodeBuild there is none until something rolls."""

    subject = f"roll:{spec!r}"  # the ONE subject per spec (feature 213); the tests' roll IS this record
    # only the META is read here - the payload path went with the store body this now delegates to
    meta_path = os.path.join(_entry(subject), "meta.json")
    try:
        meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        if meta.get("subject") == subject and gencache.key_for(subject.encode(), meta.get("deps")) == meta.get("key"):
            deps: dict[str, Any] = meta["deps"]
            return deps
    except OSError, ValueError, KeyError:
        pass
    # DELEGATES rather than repeating the store (feature 192 FR-008). `_produce_and_store`'s docstring
    # claims the pair invariant is held by ONE body; a second copy of these lines here made that untrue.
    return _produce_and_store(subject, lambda: _hamlet_in_child(spec)[0], lambda: _hamlet_in_child(spec))[1]
