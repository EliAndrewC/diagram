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
rolled code) every DISTINCT subject produces - once per process, shared as bytes thereafter (feature 147;
see `_SHARED_BYPASS`), so the floors still watch a real roll while thirty identical re-rolls do not happen.

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
_SHARED_BYPASS: dict[tuple[str, int], bytes] = {}


def _share_key(subject: str, produce: Callable[[], Any]) -> tuple[str, int]:
    code = getattr(produce, "__code__", None)
    return (subject, id(code) if code is not None else 0)


def reset_shared() -> None:
    """Forget every shared bypass payload. For a test that means to watch a roll happen again."""
    _SHARED_BYPASS.clear()


def obtain[T](subject: str, produce: Callable[[], T]) -> tuple[T, str]:
    """`(payload, how)` for `subject` - "HIT" (served), "MISS" (produced, recorded, stored), "BYPASS"
    (produced, nothing stored) or "BYPASS-SHARED" (this process already produced this subject under the
    bypass; a fresh copy of it). `subject` must determine the roll completely (a spec's repr)."""
    if bypassed():
        share = _share_key(subject, produce)
        cached = _SHARED_BYPASS.get(share)
        if cached is not None:
            return pickle.loads(cached), "BYPASS-SHARED"  # noqa: S301 - our own bytes, dumped below
        payload = produce()
        # an unpicklable payload shares nothing rather than sharing wrongly - the next caller rolls
        with contextlib.suppress(pickle.PicklingError, TypeError, RecursionError):
            _SHARED_BYPASS[share] = pickle.dumps(payload)
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

    return obtain(f"hamlet:{spec!r}", produce)[0]


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
