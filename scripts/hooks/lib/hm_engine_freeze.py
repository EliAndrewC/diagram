#!/usr/bin/env python3
"""Is an engine edit about to invalidate a map review still running? The engine-freeze guard's verdict (feature 429 D167).

A map review's verdict is recorded against the engine it reviewed. Feature 261 (2026-09-27) edited engine code while
reviews were still running, twice, and every one of them recorded NOT-REVIEWABLE - a whole extra round; feature 317
did it with a docstring. So an Edit/Write/NotebookEdit of an ENGINE path (`l7r/diagram/ci/delta.py` `is_engine`, the
one list) in a diagram clone is refused while a map-review agent (`pair-hooks.sh` `REVIEW_AGENTS_RE`, the one list)
that this session launched has not FINISHED - unless the edit changes only docstrings and comments outside the
interactive page's classes (`docstring_only`: the engine key a review is recorded against strips them; the GM, 2026-10-27).

FINISHED, read from the agent's own files: its `meta.json` says `"finished": true`, or its transcript's last record is
an assistant message that ended its turn (`stop_reason: end_turn`; older harnesses write no `finished`), or the session
acked it after a TaskStop (`agent-stall-hooks.sh ack`, `<subagents>/../stall-ack/<id>`). Anything else is live -
stalled or not, however old (spec-fidelity round 1 and the plan review: a slow review looks exactly like a dead one, and
TaskStop then ack is the route).

Usage: hm_engine_freeze.py judge < payload  ->  prints one line per live review (`<id> <type> live|stalled <age>s`)
and exits 1 when the edit must wait; exits 0 otherwise.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FILE_TOOLS = ("Edit", "Write", "NotebookEdit")
STALE = int(os.environ.get("AGENT_STALE_S", "300"))


def review_types() -> set[str]:
    """`pair-hooks.sh`'s REVIEW_AGENTS_RE, read from its one copy."""
    text = open(os.path.join(HERE, "..", "pair-hooks.sh"), encoding="utf-8").read()
    m = re.search(r'^REVIEW_AGENTS_RE="([^"]+)"', text, re.M)
    return set(m.group(1).split("|")) if m else set()


def _is_engine(root: str, rel: str) -> bool:
    path = os.path.join(root, "l7r", "diagram", "ci", "delta.py")
    if not os.path.isfile(path):
        return False  # not a diagram tree
    spec = importlib.util.spec_from_file_location("_l7r_delta", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # a dataclass resolves its module by name
    spec.loader.exec_module(mod)
    return bool(mod.is_engine(rel))


def engine_edit(payload: dict) -> bool:
    if (payload.get("tool_name") or "") not in FILE_TOOLS:
        return False
    ti = payload.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    if not path.startswith("/"):
        return False
    d = os.path.dirname(path)
    while d and not os.path.isdir(d):
        d = os.path.dirname(d)
    top = subprocess.run(["git", "-C", d or "/", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    root = top.stdout.strip()
    if top.returncode or not root:
        return False
    rel = os.path.relpath(os.path.realpath(path), os.path.realpath(root))
    return not rel.startswith("..") and _is_engine(root, rel) and not docstring_only(rel, path, ti, payload.get("tool_name") or "")


def docstring_only(rel: str, path: str, ti: dict, tool: str) -> bool:
    """Does the edit change only docstrings and comments of a `.py` file - its semantic id, the AST with docstrings stripped
    (`gate-stamp.py` `semantic_bytes`, what the engine key a review is recorded against hashes since feature 426), the same?
    Then no review's verdict can move, and the edit passes (the GM, 2026-10-27: "We should change the rule to allow docstring
    edits during a run, since those don't affect things"). Never in the byte-hashed areas (`RAW_AREAS`: the interactive page's
    class docstrings ARE the modal text a review reads), and never for a NotebookEdit or a file that cannot be read."""
    if not rel.endswith(".py") or tool not in ("Edit", "Write"):
        return False
    try:
        with open(path, "rb") as f:
            old = f.read()
    except OSError:
        return False
    if tool == "Write":
        new = str(ti.get("content") or "")
    else:
        cur, o, n = old.decode("utf-8", "replace"), str(ti.get("old_string") or ""), str(ti.get("new_string") or "")
        if o not in cur:
            return False
        new = cur.replace(o, n) if ti.get("replace_all") else cur.replace(o, n, 1)
    spec = importlib.util.spec_from_file_location("gate_stamp", os.path.join(HERE, "..", "..", "gates", "gate-stamp.py"))
    if spec is None or spec.loader is None:
        return False
    gs = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(gs)
        if any(gs._matches(rel, *gs.AREAS[a]) for a in gs.RAW_AREAS if a in gs.AREAS):  # noqa: SLF001
            return False
        return bool(gs.semantic_bytes(old, rel) == gs.semantic_bytes(new.encode("utf-8"), rel))
    except Exception:  # noqa: BLE001 - a guard that cannot judge refuses as before
        return False


def _last_record(path: str) -> dict:
    with open(path, "rb") as f:
        f.seek(0, 2)
        pos = f.tell()
        buf = b""
        while pos > 0:
            step = min(65536, pos)
            pos -= step
            f.seek(pos)
            buf = f.read(step) + buf
            if buf.rstrip(b"\n").count(b"\n"):
                break
    try:
        return json.loads(buf.rstrip(b"\n").rsplit(b"\n", 1)[-1]) or {}
    except Exception:
        return {}


def live_reviews(subagents: str, types: set[str], now: float | None = None) -> list[tuple[str, str, str, int]]:
    """(id, type, 'live'|'stalled', age in seconds) for every unfinished map-review agent in this session."""
    now = time.time() if now is None else now
    out = []
    if not os.path.isdir(subagents):
        return out
    for name in sorted(os.listdir(subagents)):
        if not (name.startswith("agent-") and name.endswith(".jsonl")):
            continue
        aid = name[len("agent-") : -len(".jsonl")]
        tpath = os.path.join(subagents, name)
        try:
            meta = json.load(open(os.path.join(subagents, f"agent-{aid}.meta.json")))
        except Exception:
            continue
        if meta.get("agentType") not in types or meta.get("finished") is True:
            continue
        if os.path.exists(os.path.join(subagents, "..", "stall-ack", aid)):
            continue
        age = int(now - os.stat(tpath).st_mtime)
        last = _last_record(tpath)
        if last.get("type") == "assistant" and (last.get("message") or {}).get("stop_reason") == "end_turn":
            continue
        stalled = age >= STALE and last.get("type") == "user"
        out.append((aid, meta["agentType"], "stalled" if stalled else "live", age))
    return out


def main() -> int:
    if sys.argv[1:2] != ["judge"]:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin) or {}
    except Exception:
        return 0
    if not engine_edit(payload):
        return 0
    tp = payload.get("transcript_path") or ""
    if not tp.endswith(".jsonl"):
        return 0
    found = live_reviews(tp[: -len(".jsonl")] + "/subagents", review_types())
    for aid, atype, state, age in found:
        print(f"{aid} {atype} {state} {age}s")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
