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
process and re-serves those bytes thereafter (feature 147; see `_SHARED_BYPASS`). Only `hamlet()` opts in.

A TEST THAT MONKEYPATCHES THE ENGINE goes through `keyed_to(test, ...)`, never bare `obtain`: a patched
function changes what the roll does without changing any hashed engine source, so the engine key alone
cannot see it. What CAN change the patch is the test's own code - the lambdas live there - so the test
function's source joins the key. The roll is then a function of (the engine functions it executed, the
files it read, the test's source), all three hashed, which is exactly the unpatched argument again.

Excluded from the engine file set (`gencache._NOT_ENGINE`): this module serves rolls and draws nothing.
"""

from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import os
import pickle
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

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


def obtain[T](subject: str, produce: Callable[[], T], share: bool = False) -> tuple[T, str]:
    """`(payload, how)` for `subject` - "HIT" (served), "MISS" (produced, recorded, stored), "BYPASS"
    (produced, nothing stored) or "BYPASS-SHARED" (this process already produced this subject under the
    bypass; a fresh copy of it). `subject` must determine the roll completely (a spec's repr)."""
    if bypassed():
        if not share:
            return produce(), "BYPASS"
        key = _share_key(subject, produce)
        cached = _SHARED_BYPASS.get(key)
        if cached is not None:
            return pickle.loads(cached), "BYPASS-SHARED"  # noqa: S301 - our own bytes, dumped below
        run_path = _run_share_path(key)
        if run_path is not None and os.path.exists(run_path):
            with contextlib.suppress(OSError, EOFError, pickle.UnpicklingError):
                with open(run_path, "rb") as fh:
                    payload_from_run = pickle.load(fh)  # noqa: S301 - written by a sibling worker of this run
                _SHARED_BYPASS[key] = pickle.dumps(payload_from_run)
                return payload_from_run, "BYPASS-SHARED-RUN"
        payload = produce()
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
    holder: list[T] = []
    deps = gencache.record(lambda: holder.append(produce()))
    payload = holder[0]
    os.makedirs(entry, exist_ok=True)
    _place(pickle.dumps(payload), payload_path)
    _place(json.dumps({"key": gencache.key_for(subject.encode(), deps), "deps": deps, "subject": subject}).encode(), meta_path)
    return payload, "MISS"


def keyed_to[T](test: Callable[..., object], produce: Callable[[], T], label: str = "") -> tuple[T, str]:
    """`obtain` for a roll whose behavior depends on the TEST's own code - its monkeypatches - so the
    test function's source joins the key: edit the patch and the roll is re-made; leave it and the
    engine key decides, as for any roll. `produce` must return plain data (what the assertions read),
    never the Settlement itself."""
    src = inspect.getsource(test)
    return obtain(f"test:{test.__module__}.{test.__qualname__}:{label}:{hashlib.sha256(src.encode()).hexdigest()[:16]}", produce)


def hamlet(spec: HamletSpec) -> tuple[SitePlan, dict[str, Any]]:
    """The plan and the FINISHED manifest of a scripted hamlet built from `spec` (no gate, no files)."""
    from l7r.diagram import hamletgen as hg

    def produce() -> tuple[SitePlan, dict[str, Any]]:
        plan = hg.plan_site(spec)
        s = hg.build(plan)
        with tempfile.TemporaryDirectory() as tmp:
            s.finish(os.path.join(tmp, "scratch"), render=False)  # the manifest is not complete until finish() runs
        return plan, s.M

    # SHARED (feature 147): the scripted negative fixtures are the measured case - 31 of them across two
    # specs, each deep-copying the manifest before breaking it, so a shared roll is exactly what they want.
    # Sharing is OPT-IN and stays here for now: turned on for `obtain` generally it made the hamlet-path
    # floor NON-DETERMINISTIC (`hinterland.py` 503-504 flipped between otherwise identical full runs), and a
    # coverage floor that flips is worse than a slow one. What the fixtures need is this call and no other.
    return obtain(f"hamlet:{spec!r}", produce, share=True)[0]


def report(spec: HamletSpec) -> tuple[Report, str]:
    """`hg.generate(spec)` - build, finish, gate, with the re-roll loop - and how it was obtained."""
    from l7r.diagram import hamletgen as hg

    return obtain(f"report:{spec!r}", lambda: hg.generate(spec, out_base=None, render=False))


def report_deps(spec: HamletSpec) -> dict[str, Any]:
    """The DEPENDENCY RECORD of `report(spec)` - every engine function and file the roll executed - from
    the cache when a valid record exists, else by rolling and recording now. Never bypassed: the FULL
    run bypasses SERVING (a served roll executes nothing the coverage floors could see), but the floor
    that derives the hamlet path from these records (feature 145, `tools/hamlet_floor.py`) needs the
    record itself, and on a fresh clone or CodeBuild there is none until something rolls."""
    from l7r.diagram import hamletgen as hg

    subject = f"report:{spec!r}"
    entry = _entry(subject)
    meta_path, payload_path = os.path.join(entry, "meta.json"), os.path.join(entry, "payload.pickle")
    try:
        meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        if meta.get("subject") == subject and gencache.key_for(subject.encode(), meta.get("deps")) == meta.get("key"):
            deps: dict[str, Any] = meta["deps"]
            return deps
    except OSError, ValueError, KeyError:
        pass
    holder: list[Report] = []
    fresh = gencache.record(lambda: holder.append(hg.generate(spec, out_base=None, render=False)))
    os.makedirs(entry, exist_ok=True)
    _place(pickle.dumps(holder[0]), payload_path)
    _place(json.dumps({"key": gencache.key_for(subject.encode(), fresh), "deps": fresh, "subject": subject}).encode(), meta_path)
    return fresh
