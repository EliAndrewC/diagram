#!/usr/bin/env python3
"""What a guard decision costs spawned, and what the same decision costs called.

    python3 specs/239-*/measure/decision_cost.py [N] [--record] [--repeat K]

The house-style decision is a Python program inside a shell string, so it cannot be imported and a
measurement has to spawn it. This harness measures that, and then measures the SAME program compiled
once and executed in process with its stdin and stdout redirected per command - which is what FR-001
makes permanent, and which is why the figure can be taken before the extraction exists.

The commands are the FROZEN corpus under `scripts/fixtures/`, built by `freeze_window.py`, so a
re-run on a clean tree reproduces the figures instead of crashing on a path under `/tmp`.
"""

from __future__ import annotations

import datetime
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[3]
HOOK = ROOT / "scripts" / "house-style-hooks.sh"
CORPUS = max(ROOT.glob("scripts/fixtures/command-window-*.json"), default=None)   # the frozen window
MEASUREMENTS = HERE.parent.parent / "measurements.json"


def inline_program(text: str) -> str:
    """The hook's own Python program, lifted out of the shell string it lives in."""
    start = text.index("python3 -c '") + len("python3 -c '")
    return text[start:text.index("\n')", start)]


def spawned(cmds: list[str]) -> float:
    began = time.time()
    for cmd in cmds:
        subprocess.run([str(HOOK), "pretool"], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
                       capture_output=True, text=True,
                       env=dict(os.environ, GUARD_LOG_DIR="/tmp/claude-1000/measure-guard-log"))
    return (time.time() - began) / len(cmds)


def in_process(cmds: list[str], program: str) -> float:
    """Seconds per command with the program compiled once and executed per command.

    THE PATH IS RESTORED AFTER EVERY EXECUTION. The program inserts its own directory into `sys.path`
    each time it runs - free in a process that runs it once, and unbounded in a bench that runs it 560
    times (the path reached 331 entries). A module with a function, which FR-001 makes of it, carries
    no such per-process setup at all. What this restoration did NOT fix, because it was never the
    cause: a seventeen-fold rise in the in-process figure that was first blamed on it. That was the
    argument parse in `main` sampling three commands instead of the whole window - see the comment
    there - while the container's load, which was also real, moved only the spawned figure.
    """
    code = compile(program, "<house-style>", "exec")
    os.environ["HS_HERE"] = str(ROOT / "scripts")
    began = time.time()
    for cmd in cmds:
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        stdin, stdout, path = sys.stdin, sys.stdout, list(sys.path)
        sys.stdin, sys.stdout = io.StringIO(payload), io.StringIO()
        try:
            exec(code, {"__name__": "__main__"})
        except SystemExit:
            pass
        finally:
            sys.stdin, sys.stdout, sys.path[:] = stdin, stdout, path
    return (time.time() - began) / len(cmds)


def drift(values: list[float]) -> float:
    """The spread of K measurements as a percentage of the smallest - what `varies: true` must tolerate.

    A timing does not repeat exactly, and FR-011a needs the band to be a MEASURED number rather than a
    sentence: this is the figure it rests on, recorded as a key like any other.
    """
    return (max(values) - min(values)) / min(values) * 100


def bare(argv: list[str]) -> float:
    began = time.time()
    for _ in range(20):
        subprocess.run(argv, capture_output=True)
    return (time.time() - began) / 20


QUIET = 2.0   # the 1-minute load average above which a timing on this container is not its own


def record(entries: dict[str, dict], load_start: float | None = None) -> None:
    """Write the figures, refusing a TIMING measured while the container was busy.

    A shared container measures itself: the same command gave 145 ms and 303 ms per spawn on the same
    tree an hour apart, the second while another session rolled a map at 152% CPU. A number taken then
    is not the guard's cost, and this project has already recorded one such figure as fact (feature
    236's `2.2 s`). So the load average goes into the entry, and `--anyway` is the only way past.
    """
    load = os.getloadavg()[0]
    timings = [k for k, e in entries.items() if e.get("varies")]
    if timings and load > QUIET and "--anyway" not in sys.argv:
        raise SystemExit(f"decision_cost: load average {load:.1f} is above {QUIET} - a timing measured "
                         f"now is the container's, not the guard's. Wait, or pass --anyway to record it "
                         f"with the load on the entry.")
    # THE LOAD IS A SPAN, NOT A POINT: a five-minute run began at 1.9 and ended at 2.1, so a single
    # reading at record time either passed a contended run or refused a quiet one. Both ends go on the
    # entry, and the refusal above keeps judging the end, the stricter of the two for a run that ran long.
    entries = {k: ({**e, "load": round(load, 2),
                    **({"load_start": round(load_start, 2)} if load_start is not None else {})}
                   if e.get("varies") else e) for k, e in entries.items()}
    now = datetime.date.today().isoformat()
    have = json.loads(MEASUREMENTS.read_text()) if MEASUREMENTS.is_file() else {}
    for key, entry in entries.items():
        have[key] = {**entry, "taken": now,
                     "command": "python3 specs/239-measurable-guards-and-derived-figures/measure/decision_cost.py --record"}
    MEASUREMENTS.write_text(json.dumps(have, indent=1, sort_keys=True) + "\n")
    print(f"recorded {len(entries)} figures in {MEASUREMENTS.name}")


def main(argv: list[str]) -> int:
    if CORPUS is None:
        raise SystemExit("no frozen corpus in scripts/fixtures/ - run measure/freeze_window.py first")
    window = json.loads(CORPUS.read_text())["commands"]
    # THE WHOLE WINDOW by default, because the ratio depends on the command MIX: measured over the 60
    # longest it is 4x (a long heredoc costs the decision real work and the spawn a constant), and over
    # a sample of the ones the guard ACTS on it was 37x. A bench replays everything, so that is what is
    # measured and recorded; `N` takes the longest N for a quick run and says so.
    # N is a POSITIONAL digit that is not the value of `--repeat`. The first version took the first digit
    # anywhere in argv, so `--repeat 3` sampled THREE commands - the three longest heredocs in the window -
    # and recorded a 2x ratio and 121 ms in process that were a property of that sample, not of the
    # guard. That misreading, not container load and not path growth, was most of the 2x a review round
    # found in measurements.json; the load was real, and explains the spawned figure moving, but not this.
    skip = {argv.index("--repeat") + 1} if "--repeat" in argv else set()
    n = next((int(a) for i, a in enumerate(argv) if a.isdigit() and i not in skip), len(window))
    cmds = sorted(window, key=len, reverse=True)[:n]
    program = inline_program(HOOK.read_text())
    load_start = os.getloadavg()[0]
    repeat = int(argv[argv.index("--repeat") + 1]) if "--repeat" in argv else 1
    runs = [(spawned(cmds), in_process(cmds, program)) for _ in range(repeat)]
    spawn_each, call_each = runs[-1]
    spread = max(drift([r[0] for r in runs]), drift([r[1] for r in runs])) if repeat > 1 else None
    py, sh = bare([sys.executable, "-c", "pass"]), bare(["bash", "-c", "true"])
    
    scope = "all" if len(cmds) == len(window) else f"the {len(cmds)} longest of"
    print(f"over {scope} {len(window)} frozen commands ({CORPUS.name}):")
    print(f"  spawned (bash + python3 -c + its imports): {spawn_each*1000:6.0f} ms each")
    print(f"  the same program, compiled once, in process: {call_each*1000:6.1f} ms each")
    print(f"  a bare python3 spawn {py*1000:.0f} ms | a bare bash spawn {sh*1000:.0f} ms")
    print(f"  ratio {spawn_each/call_each:.0f}x; over the whole {len(window)}-command window "
          f"{spawn_each*len(window):.0f} s against {call_each*len(window):.1f} s")
    if spread is not None:
        print(f"  over {repeat} runs on an unchanged tree the timings spread by {spread:.1f}%")
    if "--record" in argv:
        # FR-011e: the SAMPLE goes on every timing entry, so an entry can never again say it covered the
        # window while it measured three commands.
        sample = (f"{len(cmds)} of the {len(window)} commands in {CORPUS.name}"
                  + ("" if len(cmds) == len(window) else " (the longest)") + f", {repeat} run(s), the last recorded")
        record({
            **({"timing-run-to-run-drift-pct": {"value": round(spread, 1), "unit": "%", "varies": True,
                                               "quantity": f"widest spread across {repeat} runs as a percentage of the smallest; {sample}"}}
               if spread is not None else {}),
            "decision-spawned-ms": {"value": round(spawn_each * 1000), "unit": "ms", "varies": True,
                                    "quantity": f"wall time per command of the shipped hook, spawned; {sample}"},
            "decision-in-process-ms": {"value": round(call_each * 1000, 1), "unit": "ms", "varies": True,
                                       "quantity": f"wall time per command of the same program compiled once, in process; {sample}"},
            "decision-spawn-ratio": {"value": round(spawn_each / call_each), "unit": "x", "varies": True,
                                     "quantity": f"spawned over in-process wall time; {sample}"},
            "frozen-window-commands": {"value": len(window), "unit": "commands",
                                      "note": f"in {CORPUS.name}, built by measure/freeze_window.py"},
            "window-spawned-s": {"value": round(spawn_each * len(window)), "unit": "s", "varies": True,
                                "quantity": f"spawned per-command time times the window size; {sample}"},
            "window-in-process-s": {"value": round(call_each * len(window), 1), "unit": "s", "varies": True,
                                    "quantity": f"in-process per-command time times the window size; {sample}"},
            "bare-python-spawn-ms": {"value": round(py * 1000), "unit": "ms", "varies": True,
                                     "quantity": "wall time of `python3 -c pass`, mean of 20 spawns"},
        }, load_start)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
