"""The iteration switches (feature 132): remote off, scope locked.

Two committed, repository-wide switches in ONE tracked file, `dev/switches.json`:

    remote   on (default) | off        nothing is dispatched to AWS CodeBuild; the merge gate is
                                       satisfied by a green LOCAL `make done` on the merged engine
                                       content instead (the ci dispatcher's LOCAL-GATED verdict)
    scope    unlocked (default) | reference
                                       no invocation may roll a map other than the tier's reference
                                       settlement, and no invocation may roll more than one map

WHY (GM 2026-08-25): *"I want to make sure that as we iterate, not only do we not run the full test
suite, but we literally cannot because just telling you, please make sure not to run the full
tests. In the past has frequently resulted in the full tests getting run, and that costs both time
and actual money now that we are running on AWS."* and *"can we perhaps have the first thing that we
do to update the tooling to essentially disable AWS? That seems like something that would be good as
a reusable setting anyway. such that if it is disabled, then we do not use it as a gate. and we do
not dispatch to it while we are doing iteration."*

THE RULES THIS MODULE IS BUILT ON, each with its reason:

- ONE TRACKED FILE, NOT AN ENVIRONMENT VARIABLE. An environment variable is a forgery vector (feature
  130 refused the FULL door through one for the same reason) and does not travel: a setting the GM
  throws once must reach every clone through the normal sync, which only a committed file does.
  It is a SETTING with a current value, not an append-only log, so the per-entry directory that
  `perf-log/` and `bypass-log/` needed against concurrent pushes does not apply - two sessions
  flipping the same switch at once is a real conflict that SHOULD be seen.
- WRITTEN ONLY BY THE FOUR MAKE TARGETS, WHICH COMMIT. `ci-off` / `ci-on` / `scope-lock` /
  `scope-unlock`, each demanding a reason. The history of throws and releases is the file's git
  log; no second reporting surface (the fidelity review of round 1 removed one as unrequested).
- NO OVERRIDE EXISTS. Not an environment variable, not a make variable, not a flag. The release
  target is the only way back, and it commits. This is the GM's "literally cannot".
- A MALFORMED FILE FAILS CLOSED - remote off, scope locked. A corrupt switch must not silently
  become "everything is allowed".
- ABSENT MEANS DEFAULTS. A checkout older than this feature, or a fixture, has remote on and scope
  unlocked. Absence is never "off".
- ONE MAP PER INVOCATION is the whole carve-out under the lock (spec FR-012). The GM's own
  definition of the suite is *"forty eight different maps ... some number of different maps with
  some number of different seeds per map"* - a sweep. One map is iteration, and refusing it would
  make the lock refuse the work the lock exists to protect. Enforced in the Makefile AND in every
  Python entry point that can roll more than one map (`pipeline.regen`, `tools.cohort_audit`,
  `tools.mapcheck`, `tools.cache_audit`, `tools.make_regressions`, `tools.perf_snapshot`, the ci
  dispatcher) - the Makefile's own record says a guard on one door is not a guard.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

FILE = Path("dev") / "switches.json"  # relative to the skill directory

REMOTE_STATES = ("on", "off")
DEFAULT_REMOTE = "on"


@dataclass(frozen=True)
class Axis:
    state: str
    why: str = ""
    who: str = ""
    utc: str = ""


@dataclass(frozen=True)
class Switches:
    remote: Axis
    error: str = ""  # non-empty when the file was malformed - the axis is then CLOSED

    @property
    def remote_off(self) -> bool:
        return self.remote.state == "off"


DEFAULTS = Switches(Axis(DEFAULT_REMOTE))


def _closed(error: str) -> Switches:
    why = f"switches.json is MALFORMED ({error}) - failing closed"
    return Switches(Axis("off", why), error=error)


def _axis(raw: object, name: str, allowed: tuple[str, ...]) -> Axis:
    if not isinstance(raw, dict):
        raise ValueError(f"{name!r} is not an object")
    state = raw.get("state")
    if state not in allowed:
        raise ValueError(f"{name}.state is {state!r}, not one of {allowed}")
    return Axis(str(state), str(raw.get("why", "")), str(raw.get("who", "")), str(raw.get("utc", "")))


def read(skill: Path) -> Switches:
    """Absent -> defaults. Malformed -> CLOSED (remote off) with `error` set.

    UNKNOWN KEYS ARE IGNORED, and that is load-bearing (feature 185, FR-007a). Only `remote` is read,
    through `data.get`, with no key iteration and no schema validation - so a leftover `scope` block
    from before the lock was retired is simply not looked at. Making this strict would fail closed on
    such a file, and failing closed means REMOTE OFF in every clone that still carries one.
    `_closed()` has exactly three entrances: a JSON parse failure, a non-dict top level, or `_axis`
    rejecting a NAMED key. Never an unrecognized one.

    THE IDLE RELAXATION IS GONE WITH THE SCOPE LOCK (feature 185), but `idle_context` BELOW IS NOT.
    It has a second consumer that has nothing to do with the lock: the Makefile's `DONE_NAME` picks
    `idle-done` over `done` from it, and `ci/state.py`'s `GREEN_TARGETS` deliberately omits
    `idle-done` - which is the whole mechanism by which an unattended idle gate neither grants nor
    revokes a push (feature 136 D1/FR-006b). Removing it would make a detached timer write a record
    the push honors, and nothing would catch it: the code still runs, only the recorded NAME changes,
    so coverage stays full and every test passes."""
    path = skill / FILE
    if not path.is_file():
        sw = DEFAULTS
    else:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("top level is not an object")
            sw = Switches(_axis(data.get("remote", {"state": DEFAULT_REMOTE}), "remote", REMOTE_STATES))
        except (ValueError, OSError) as e:
            return _closed(str(e))
    return sw


IDLE_TIMER_MARK = "idle-tests-hooks.sh"


def _proc_status(pid: int) -> str:
    """`/proc/<pid>/status`, or "" when it cannot be read (the process exited under us)."""
    try:
        return Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return ""


def _ancestors(pid: int, status_of: Callable[[int], str] = _proc_status) -> list[int]:
    """The pid chain from `pid` up to init.

    `status_of` is injected for the same reason `idle_context` injects this function: the walk's two
    EXITS depend on the shape of the live process tree, so which of them a test reaches is decided by
    the machine rather than by the test. Feature 174 measured that directly - the `ppid <= 0` exit was
    covered by one `make test-full` and missed by the very next `make done` on identical code, because
    a reparented process came and went between them. Injected, both exits are three lines of dict."""
    out: list[int] = []
    while pid > 1 and len(out) < 64:
        status = status_of(pid)
        if not status:
            break  # the process is gone; the chain ends where we can still read it
        ppid = next((int(line.split()[1]) for line in status.splitlines() if line.startswith("PPid:")), 0)
        if ppid <= 0:
            break  # a process reporting no parent - init, or one whose parent went away
        out.append(ppid)
        pid = ppid
    return out


def _cmdline(pid: int) -> str:
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return ""


def idle_context(skill: Path, ancestors: Callable[[int], list[int]] = _ancestors, cmdline: Callable[[int], str] = _cmdline, pid: int | None = None) -> bool:
    """True iff this process descends from the idle timer that wrote `.git/idle-tests.running`."""
    top = subprocess.run(["git", "-C", str(skill), "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not top:
        return False
    marker = Path(top) / ".git" / "idle-tests.running"
    try:
        timer = int(marker.read_text().strip())
    except OSError, ValueError:
        return False
    me = os.getpid() if pid is None else pid
    return timer in ancestors(me) and IDLE_TIMER_MARK in cmdline(timer) and " timer " in cmdline(timer)


def _who(skill: Path) -> str:
    p = subprocess.run(["git", "-C", str(skill), "config", "user.name"], capture_output=True, text=True)
    return p.stdout.strip() or "unknown"


def write(skill: Path, axis: str, state: str, why: str, who: str | None = None) -> Switches:
    """Set one axis. Refuses an empty reason and an unknown state; keeps the other axis as is.

    Only the make targets call this (they commit the result). A malformed file is REPLACED here -
    the throw or release is the repair, and it is a diff someone reads."""
    if not why.strip():
        raise ValueError("a reason is required (REASON=...) - a reason someone will READ is a decision you have to defend")
    allowed = {"remote": REMOTE_STATES}.get(axis)
    if allowed is None or state not in allowed:
        raise ValueError(f"unknown switch {axis}={state}")
    cur = read(skill)
    if cur.error:
        cur = DEFAULTS
    new = Axis(state, why.strip(), who if who is not None else _who(skill), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    out = Switches(new)
    path = skill / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"remote": asdict(out.remote)}, indent=2) + "\n", encoding="utf-8")
    return out


def describe(sw: Switches) -> str:
    def line(name: str, a: Axis, default: str) -> str:
        if a.state == default and not a.why:
            return f"  {name:<7} {a.state:<10} (default)"
        return f"  {name:<7} {a.state:<10} since {a.utc} by {a.who or '?'}: {a.why}"

    head = "switches (dev/switches.json):"
    if sw.error:
        head += f"\n  MALFORMED - {sw.error} - remote CLOSED until `make ci-on REASON=...` rewrites it"
    return "\n".join([head, line("remote", sw.remote, DEFAULT_REMOTE)])


def refusal(sw: Switches, axis: str, what: str) -> str | None:
    """None if `what` may run; otherwise the full refusal text - reason, date, the release target,
    and the local route that DOES the job (a guard that blocks a legitimate question without giving
    the route is a guard that gets worked around - CLAUDE.md, feature 127)."""
    if axis == "remote":
        if not sw.remote_off:
            return None
        a, release, route = sw.remote, "make ci-on REASON=...", "a green local `make done`, then `scripts/sync-with-main.sh done` (the gated route pushes on the local verdict while remote is off)"
        head = f"REFUSED: `{what}` would run on AWS CodeBuild, and remote is OFF"
    else:
        raise ValueError(f"unknown axis {axis!r}")
    return "\n".join(
        [
            f"\n\033[1m{head}.\033[0m",
            f"  since {a.utc} by {a.who or '?'}: {a.why}",
            "",
            f"  What runs instead:  {route}",
            f"  To release it:      \033[1m{release}\033[0m  (commits the change; there is no flag or variable that skips this)",
            "",
        ]
    )


def check(skill: Path, axis: str, what: str) -> bool:
    """Print the refusal and return False, or return True. The one call every guarded entry makes."""
    text = refusal(read(skill), axis, what)
    if text is None:
        return True
    print(text, file=sys.stderr)
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="l7r.diagram.switches", description="the iteration switches (feature 132)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    s = sub.add_parser("set")
    s.add_argument("axis", choices=("remote",))
    s.add_argument("state")
    s.add_argument("--why", default="")
    c = sub.add_parser("check")
    c.add_argument("axis", choices=("remote",))
    c.add_argument("what")
    q = sub.add_parser("state", help="print one axis's bare state - what the Makefile reads to shape a target")
    q.add_argument("axis", choices=("remote",))
    sub.add_parser("idle", help="print 1 when this process descends from the idle timer (feature 136), else 0")
    a = ap.parse_args(argv)
    skill = Path.cwd()
    if a.cmd == "show":
        print(describe(read(skill)))
        return 0
    if a.cmd == "state":
        print(getattr(read(skill), a.axis).state)
        return 0
    if a.cmd == "idle":
        print("1" if idle_context(skill) else "0")
        return 0
    if a.cmd == "set":
        try:
            sw = write(skill, a.axis, a.state, a.why)
        except ValueError as e:
            print(f"switches: REFUSED - {e}", file=sys.stderr)
            return 1
        print(describe(sw))
        return 0
    return 0 if check(skill, a.axis, a.what) else 1


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.switches")
    sys.exit(main())
