#!/usr/bin/env python3
"""When a gate's failures happened, and what the machine was doing around it - for the run log.

    _runstats.py start <dir>          snapshot the host at the gate's start; clear the failure marks
    _runstats.py fail <dir> <phase>   mark a phase that failed, at the moment it finished
    _runstats.py end <dir>            print the run-log fields as JSON (empty object on no start)

`<dir>` is the clone's git directory. `make done` calls all three; `tests/_gate_failures.py` appends
one `<epoch> test` mark per failed test as pytest reports it, so `first_failure_s` is when the first
test failed, not when the phase holding it ended.

WHY (GM 2026-10-03): whether streaming a gate's failures as they occur would let a session start
fixing early depends on how long a failed gate runs after its first failure, which nothing recorded.
The host figures come with them so an outlier (a 436 s gate against a 151 s idle run) can be told
from a real slowdown: load and available memory at both ends, the kernel's pressure-stall totals over
the run (`stall_s`: seconds some task waited for CPU, for the disk, for memory), the CPU package
temperature at both ends and the thermal-throttle time over the run. Every figure is one read of a
small /proc or /sys file - the GM's condition was "only if those things are extremely cheap" - and a
figure the host does not expose (CodeBuild, a laptop without coretemp) is left out, never guessed.
No sampling during the run: a peak temperature would need a sampler, and the throttle time already
says whether heat cost the run anything.
"""

from __future__ import annotations

import glob
import json
import os
import sys
import time

START = "gate-stats-start.json"
FAILURES = "gate-failures"
PROC = "/proc"
SYS = "/sys"


def _read(path: str) -> str | None:
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return None


def _load(proc: str) -> float | None:
    text = _read(f"{proc}/loadavg")
    return float(text.split()[0]) if text else None


def _mem_avail_mb(proc: str) -> int | None:
    for line in (_read(f"{proc}/meminfo") or "").splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    return None


def _stall_us(proc: str) -> dict[str, int]:
    """The `some` total (microseconds) of each pressure-stall file, plus io's `full`."""
    out: dict[str, int] = {}
    for kind in ("cpu", "io", "memory"):
        for line in (_read(f"{proc}/pressure/{kind}") or "").splitlines():
            head, _, rest = line.partition(" ")
            fields = dict(f.split("=", 1) for f in rest.split())
            if "total" in fields and (head == "some" or (kind == "io" and head == "full")):
                out[kind if head == "some" else "io_full"] = int(fields["total"])
    return out


def _cpu_temp_c(sys_root: str) -> float | None:
    """The coretemp package sensor, or the hottest coretemp sensor when none is labeled package."""
    for hw in sorted(glob.glob(f"{sys_root}/class/hwmon/hwmon*")):
        if (_read(f"{hw}/name") or "").strip() != "coretemp":
            continue
        temps = {}
        for inp in sorted(glob.glob(f"{hw}/temp*_input")):
            raw = _read(inp)
            if raw and raw.strip().lstrip("-").isdigit():
                temps[(_read(inp.replace("_input", "_label")) or "").strip()] = int(raw) / 1000
        package = [v for k, v in temps.items() if k.startswith("Package")]
        if package or temps:
            return max(package or temps.values())
    return None


def _throttle_ms(sys_root: str) -> dict[str, int]:
    """Thermal-throttle time so far: core time summed over CPUs, package time from its busiest CPU
    (every CPU of a package reports the same package counter, so a sum would multiply it)."""
    core, package, seen = 0, 0, False
    for cpu in glob.glob(f"{sys_root}/devices/system/cpu/cpu[0-9]*/thermal_throttle"):
        c, p = _read(f"{cpu}/core_throttle_total_time_ms"), _read(f"{cpu}/package_throttle_total_time_ms")
        if c is not None:
            core, seen = core + int(c), True
        if p is not None:
            package, seen = max(package, int(p)), True
    return {"core": core, "package": package} if seen else {}


def snapshot(proc: str = PROC, sys_root: str = SYS) -> dict:
    return {
        "t": time.time(),
        "load": _load(proc),
        "mem_avail_mb": _mem_avail_mb(proc),
        "stall_us": _stall_us(proc),
        "cpu_temp_c": _cpu_temp_c(sys_root),
        "throttle_ms": _throttle_ms(sys_root),
    }


def start(gitdir: str, proc: str = PROC, sys_root: str = SYS) -> None:
    with open(os.path.join(gitdir, START), "w") as f:
        json.dump(snapshot(proc, sys_root), f)
    try:
        os.remove(os.path.join(gitdir, FAILURES))
    except FileNotFoundError:
        pass


def fail(gitdir: str, phase: str) -> None:
    with open(os.path.join(gitdir, FAILURES), "a") as f:
        f.write(f"{time.time():.3f} phase:{phase}\n")


def _failure_marks(gitdir: str) -> tuple[list[float], int]:
    """Every failure moment, and how many tests failed. A test phase's own end mark is dropped when its
    tests left marks: it would make `last_failure_s` the phase's end. With no test marks (a coverage
    floor, the roll census) the phase end is the only moment there is, and it stands."""
    tests, phases = [], []
    for line in (_read(os.path.join(gitdir, FAILURES)) or "").splitlines():
        stamp, _, kind = line.partition(" ")
        try:
            moment = float(stamp)
        except ValueError:
            continue
        if kind == "test":
            tests.append(moment)
        else:
            phases.append((moment, kind))
    kept = [m for m, kind in phases if not (tests and kind in ("phase:test-full", "phase:test"))]
    return tests + kept, len(tests)


def _delta(before: dict, after: dict, scale: float = 1.0) -> dict:
    return {k: round((after[k] - before[k]) / scale, 1) for k in before if k in after}


def end(gitdir: str, proc: str = PROC, sys_root: str = SYS) -> dict:
    raw = _read(os.path.join(gitdir, START))
    if not raw:
        return {}
    s, e = json.loads(raw), snapshot(proc, sys_root)
    out: dict = {}
    moments, failed_tests = _failure_marks(gitdir)
    if moments:
        out["first_failure_s"] = round(min(moments) - s["t"], 1)
        out["last_failure_s"] = round(max(moments) - s["t"], 1)
    if failed_tests:
        out["failed_tests"] = failed_tests
    host: dict = {}
    for key in ("load", "mem_avail_mb", "cpu_temp_c"):
        if s[key] is not None and e[key] is not None:
            host[key] = [s[key], e[key]]
    if stall := _delta(s["stall_us"], e["stall_us"], 1e6):
        host["stall_s"] = stall
    if throttle := _delta(s["throttle_ms"], e["throttle_ms"]):
        host["throttle_ms"] = {k: int(v) for k, v in throttle.items()}
    if host:
        out["host"] = host
    return out


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "start":
        start(argv[1])
    elif len(argv) >= 3 and argv[0] == "fail":
        fail(argv[1], argv[2])
    elif len(argv) >= 2 and argv[0] == "end":
        print(json.dumps(end(argv[1])))
    else:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
