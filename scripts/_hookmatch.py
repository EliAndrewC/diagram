#!/usr/bin/env python3
"""The shared decisions every guard makes - now an UMBRELLA over three leaves (feature 172).

WHAT MOVED, AND WHY. This file was 574 lines holding three unrelated families, and every guard suite
was declared to depend on all of it. A one-line change to the make/rewrite family re-ran all 21 guard
suites. The families now live apart:

    _hm_shape.py    what a command literally IS - heredocs, quotes, the bracket form, a file-watching
                    wait. The BASE: the other two stand on it, so a change here is felt everywhere.
    _hm_escape.py   did a session escape a guard, and did it say WHY (features 169 and 170). Nearly
                    every guard reaches this through `_guardlog.sh`, so ~20 of 21 suites depend on it.
    _hm_make.py     which make target a command invokes, and the compliant form (features 162, 164).
                    Only `gate`, `make-only` and `pair` use it - three suites instead of twenty-one.

**GUARDS CALL THE LEAF, NOT THIS FILE.** A split behind an umbrella that imports everything changes no
dependency set at all: the closure is what matters, not the file count. This file exists for two
narrower reasons - anything that imports `_hookmatch` by name keeps working, and a session reading the
tree for the first time finds the map here rather than having to guess which leaf holds what.

The GM's question that led to it (2026-08-30): *"am I correct in thinking that we would also be able to
potentially break up those two files? ... I'm not saying that we should go so far as to put every
single function or bit of functionality which we define into its own separate file."* The answer, and
why the split stops at three, is in `specs/172-hooks-test-deps/`: past cohesion the closure through the
shape primitives dominates, so finer files shrink no blast radius. `_guardlog.sh` is not split at all -
98 lines, one cohesive thing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hm_escape import escape_reason, escape_used, reason_is_enough  # noqa: E402
from _hm_make import as_make_target, as_paired, classify, combine, targets  # noqa: E402
from _hm_shape import _strip_heredocs, _strip_quotes, bracket_pattern, file_watching_wait  # noqa: E402

__all__ = [
    "as_make_target", "as_paired", "bracket_pattern", "classify", "combine", "escape_reason",
    "escape_used", "file_watching_wait", "reason_is_enough", "targets",
]


if __name__ == "__main__":
    # The umbrella CLI still answers every mode, so a caller this feature missed keeps working. It is
    # the SLOW path for dependencies - invoking it means depending on all three leaves - which is why
    # each guard was pointed at the leaf it uses.
    RAW = sys.stdin.read()
    try:
        _ti = json.loads(RAW).get("tool_input", {}) or {}
    except Exception:
        _ti = {}
    CMD = _ti.get("command", "") or ""
    CONTENT = (_ti.get("new_string") or "") + (_ti.get("content") or "")
    TEXT = CMD or CONTENT
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    token = sys.argv[2] if len(sys.argv) > 2 else ""

    if mode == "targets":
        print("\n".join(sorted(targets(CMD))))
    elif mode in ("combine", "as-make-target", "as-paired", "bracket"):
        fn = {"combine": combine, "as-make-target": as_make_target,
              "as-paired": as_paired, "bracket": bracket_pattern}[mode]
        out = fn(CMD)
        if out:
            print(out)
    elif mode == "file-wait":
        try:
            whole = json.loads(RAW)
        except Exception:
            whole = {}
        if file_watching_wait(whole):
            print("yes")
    elif mode == "sanitize":
        print(_strip_quotes(_strip_heredocs(CMD)))
    elif mode == "reason-ok":
        sys.exit(0 if reason_is_enough(RAW.strip()) else 1)
    elif mode == "escape" and token:
        if escape_used(CMD, token):
            print("yes")
    elif mode == "escape-reason" and token:
        _r = escape_reason(TEXT, token)
        if (escape_used(TEXT, token) or (CONTENT and token in CONTENT)) and reason_is_enough(_r):
            print(_r)
    else:
        print(classify(CMD))
