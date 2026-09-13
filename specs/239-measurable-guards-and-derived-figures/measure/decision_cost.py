#!/usr/bin/env python3
"""What a guard decision costs spawned, and what the same decision costs called.

    python3 specs/239-*/measure/decision_cost.py [N] [--record]

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
    code = compile(program, "<house-style>", "exec")
    os.environ["HS_HERE"] = str(ROOT / "scripts")
    sys.path.insert(0, str(ROOT / "scripts"))
    began = time.time()
    for cmd in cmds:
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        stdin, stdout = sys.stdin, sys.stdout
        sys.stdin, sys.stdout = io.StringIO(payload), io.StringIO()
        try:
            exec(code, {"__name__": "__main__"})
        except SystemExit:
            pass
        finally:
            sys.stdin, sys.stdout = stdin, stdout
    return (time.time() - began) / len(cmds)


def bare(argv: list[str]) -> float:
    began = time.time()
    for _ in range(20):
        subprocess.run(argv, capture_output=True)
    return (time.time() - began) / 20


def record(entries: dict[str, dict]) -> None:
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
    n = next((int(a) for a in argv if a.isdigit()), len(window))
    cmds = sorted(window, key=len, reverse=True)[:n]
    program = inline_program(HOOK.read_text())
    spawn_each, call_each = spawned(cmds), in_process(cmds, program)
    py, sh = bare([sys.executable, "-c", "pass"]), bare(["bash", "-c", "true"])
    
    scope = "all" if len(cmds) == len(window) else f"the {len(cmds)} longest of"
    print(f"over {scope} {len(window)} frozen commands ({CORPUS.name}):")
    print(f"  spawned (bash + python3 -c + its imports): {spawn_each*1000:6.0f} ms each")
    print(f"  the same program, compiled once, in process: {call_each*1000:6.1f} ms each")
    print(f"  a bare python3 spawn {py*1000:.0f} ms | a bare bash spawn {sh*1000:.0f} ms")
    print(f"  ratio {spawn_each/call_each:.0f}x; over the whole {len(window)}-command window "
          f"{spawn_each*len(window):.0f} s against {call_each*len(window):.1f} s")
    if "--record" in argv:
        record({
            "decision-spawned-ms": {"value": round(spawn_each * 1000), "unit": "ms", "varies": True,
                                    "note": f"the shipped hook, over {len(cmds)} frozen commands"},
            "decision-in-process-ms": {"value": round(call_each * 1000, 1), "unit": "ms", "varies": True,
                                       "note": "the same program compiled once and executed per command"},
            "decision-spawn-ratio": {"value": round(spawn_each / call_each), "unit": "x", "varies": True},
            "frozen-window-commands": {"value": len(window), "unit": "commands",
                                      "note": f"in {CORPUS.name}, built by measure/freeze_window.py"},
            "window-spawned-s": {"value": round(spawn_each * len(window)), "unit": "s", "varies": True,
                                "note": f"the whole {len(window)}-command window"},
            "window-in-process-s": {"value": round(call_each * len(window), 1), "unit": "s", "varies": True},
            "bare-python-spawn-ms": {"value": round(py * 1000), "unit": "ms", "varies": True},
        })
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
