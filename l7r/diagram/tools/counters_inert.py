"""The work counters change no map: one seed rolled with them and under `python -O`, the manifests compared (feature 443 T02, D5).

    make counters-inert [SEED=25] [HOUSEHOLDS=15]

WHY (the design's section 1, approved by the GM 2026-10-28): every counter sits in an `if __debug__:` block, which `python -O`
drops, so a deployed run counts nothing. That holds only if no counter touches what the roll decides; this proves it on a real
roll - the reference spec at one seed and size, built once in each mode by `hamletgen.driver.generate`, each manifest written to a
temporary file - and refuses unless the two are byte-identical, naming the first key that differs. `make done` runs it.

Research: plumbing - NONE: it compares two rolls, and decides nothing about the place
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
#: the child each mode runs: the reference rolled and its manifest written, the counters' own state left out of it
CHILD = (
    "import json, sys\n"
    "from l7r.diagram.hamletgen import HamletSpec\n"
    "from l7r.diagram.hamletgen.driver import generate\n"
    "from l7r.diagram.hamletgen.plan import beyond_the_band\n"
    "from l7r.diagram.tools.perf_snapshot import REFERENCE\n"
    "try:\n"
    "    with beyond_the_band():\n"
    "        out = generate(HamletSpec(seed=int(sys.argv[1]), **{**REFERENCE, 'households': int(sys.argv[2])}), None, render=False).manifest\n"
    "except (ValueError, RuntimeError) as e:  # a refusal is the roll's outcome too: it must be the same refusal in both modes\n"
    "    out = {'refused': f'{type(e).__name__}: {e}'}\n"
    "open(sys.argv[3], 'w').write(json.dumps(out, sort_keys=True, default=str))\n"
)


def first_difference(a: Any, b: Any, path: str = "") -> str | None:
    """The first key path at which `a` and `b` differ, or None where they are equal."""
    if type(a) is not type(b):
        return path or "(the top)"
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                return f"{path}.{k}" if path else str(k)
            d = first_difference(a[k], b[k], f"{path}.{k}" if path else str(k))
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path} (length {len(a)} against {len(b)})"
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            d = first_difference(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else (path or "(the top)")


def roll(seed: int, households: int, optimize: bool, out: str, runner: Any = subprocess.run) -> None:
    """Roll the reference in a fresh interpreter (`-O` when `optimize`), its manifest written to `out`."""
    env = {**os.environ, "PYTHONPATH": SKILL + os.pathsep + os.environ.get("PYTHONPATH", "")}
    cmd = [sys.executable, *(["-O"] if optimize else []), "-c", CHILD, str(seed), str(households), out]
    runner(cmd, cwd=SKILL, env=env, check=True)


def compare(seed: int, households: int, runner: Any = subprocess.run) -> str | None:
    """None when the two rolls' manifests are byte-identical; else the first key that differs."""
    with tempfile.TemporaryDirectory() as tmp:
        on, off = os.path.join(tmp, "counted.json"), os.path.join(tmp, "optimized.json")
        roll(seed, households, False, on, runner)
        roll(seed, households, True, off, runner)
        with open(on, encoding="utf-8") as fa, open(off, encoding="utf-8") as fb:
            ta, tb = fa.read(), fb.read()
        if ta == tb:
            return None
        return first_difference(json.loads(ta), json.loads(tb)) or "(the bytes differ, the values do not)"


def main(argv: list[str] | None = None, runner: Any = subprocess.run) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--seed", type=int, default=25)
    ap.add_argument("--households", type=int, default=15)  # the reference size (`perf_snapshot.REFERENCE`)
    a = ap.parse_args(argv)
    diff = compare(a.seed, a.households, runner)
    if diff is None:
        print(f"counters-inert: seed {a.seed} at {a.households} households - the manifests with the counters and under python -O are identical")
        return 0
    print(
        f"counters-inert: REFUSED - seed {a.seed} at {a.households} households, the manifest with the counters differs from the one under"
        f" python -O first at {diff}: a counter changes what the roll decides. Find the `if __debug__:` block that writes beyond"
        " `work_counts.OPS` (grep -n '__debug__' in the changed engine files) and keep it to the counter alone.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.counters_inert")
    raise SystemExit(main())
