"""A plan section or block is held while its review runs (feature 385 T85, plan D106; the GM's approved proposal B).

WHY. On the evening of 2026-10-18 two of 42 plan reviews came back unrecorded - `make plan-verdict` refused them, "it changed
while it was being reviewed" - after the session edited T76's and T77's sections under them. So every running `spec-fidelity`
plan review HOLDS what its bundle names - a task preflight (`plan-<feature>-<T>`) that task's section, a block review
(`plan-<feature>-blocks-...`) each block its `blocks.md` names - and a write that would change held text is refused, naming the
running review. `PLAN_EDIT_OK="<reason>"` passes a hold only when its dispatch is dead (never launched past `PENDING_S`, or no
return past `HOLD_MAX_S`); a live review's held text has no escape - it returns in minutes.

A Bash write is found by its text: it names the plan and carries a write (`open(..., "w")`, `write_text`, `sed -i`, a redirect,
`tee`) - wider than `hm_house.write_targets`, which does not see a Python heredoc's write, the session's usual route - and it is
refused when its text holds a held heading or a held line.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

HOLD_MAX_S = 1800  # a plan review returns in about 1-4 minutes (the evening's 42); past half an hour its hold is dead
PENDING_S = 60
_BUNDLE = re.compile(r"(\S*/plan-(\d{3}-[a-z0-9-]+?)-(?:(T\d+[a-z]?)|blocks-[\w-]+))/MANIFEST\.md")
_WRITE = re.compile(r"""open\([^)]*['"][wa]['"]|write_text|\bsed\s+(?:-\S+\s+)*-i|>\s*['"]?\S*plan\.md|\btee\b""")


def hold(state: dict[str, Any], tid: str, prompt: str, now: float) -> None:
    """Record the hold a plan review's dispatch takes (at its PreToolUse)."""
    m = _BUNDLE.search(prompt)
    if not m:
        return
    bundle = Path(m.group(1))
    keys: list[str] = []
    if not m.group(3):
        try:
            keys = re.findall(r'^<!-- block "((?:[^"\\]|\\.)*)" sha256', (bundle / "blocks.md").read_text(encoding="utf-8"), re.M)
        except OSError:
            keys = []
        keys = [k.encode().decode("unicode_escape") for k in keys]
    state.setdefault("plan_holds", {})[tid] = {"feature": m.group(2), "task": m.group(3) or "", "blocks": keys, "t": now, "state": "pending"}


def launched(state: dict[str, Any], tid: str, agent_id: str) -> None:
    h = (state.get("plan_holds") or {}).get(tid)
    if h is not None:
        h.update(state="running", aid=agent_id)


def returned(state: dict[str, Any], agent_id: str) -> None:
    holds = state.get("plan_holds") or {}
    for tid in [t for t, h in holds.items() if h.get("aid") == agent_id]:
        del holds[tid]


def dead(h: Mapping[str, Any], now: float) -> bool:
    return (h.get("state") == "pending" and now - float(h.get("t", 0)) > PENDING_S) or now - float(h.get("t", 0)) > HOLD_MAX_S


def held(root: Path, h: Mapping[str, Any]) -> list[str]:
    """The texts a hold holds, read from the plan as it stands: the task's section, or each named block."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gates"))
    import plan_gate  # noqa: PLC0415

    plan = root / "specs" / str(h.get("feature")) / "plan.md"
    try:
        text = plan.read_text(encoding="utf-8")
    except OSError:
        return []
    if h.get("task"):
        sec = plan_gate.task_sections(text).get(str(h["task"]))
        return [sec] if sec else []
    want = set(h.get("blocks") or [])
    return [body for key, body, _at in plan_gate.blocks(text) if key in want]


def refusal(state: Mapping[str, Any], root: Path | None, tool: str, ti: Mapping[str, Any], now: float, escaped: bool) -> str:
    """Why this write is refused while a plan review holds what it would change, or ''."""
    if root is None:
        return ""
    for h in (state.get("plan_holds") or {}).values():
        plan = root / "specs" / str(h.get("feature")) / "plan.md"
        texts = held(root, h)
        # A DISPATCH THAT NEVER LAUNCHED HOLDS NOTHING (feature 385 T104, D121): refused by another guard, it reads no text - T98's
        # refused review left a hold that refused its section's amendment an hour after the re-sent review had returned
        never = h.get("state") == "pending" and now - float(h.get("t", 0)) > PENDING_S
        if not texts or never or (escaped and dead(h, now)):
            continue
        hit = False
        if tool in ("Edit", "Write", "MultiEdit") and Path(str(ti.get("file_path") or "")).resolve() == plan.resolve():
            current = plan.read_text(encoding="utf-8")
            if tool == "Write":
                hit = any(t not in str(ti.get("content") or "") for t in texts)
            else:
                old = str(ti.get("old_string") or "")
                at = current.find(old) if old else -1
                hit = any((t in current) and current.find(t) <= at <= current.find(t) + len(t) for t in texts) or any(old and old in t for t in texts)
        elif tool == "Bash":
            cmd = str(ti.get("command") or "")
            if "plan.md" in cmd and str(h.get("feature")) in cmd and _WRITE.search(cmd):
                lines = {ln.strip() for t in texts for ln in t.splitlines() if len(ln.strip()) >= 16}
                # ...or a quoted fragment of held text - the old side of a replace, the session's usual edit (12+ characters)
                quoted = [q for q in re.findall(r'"((?:[^"\\\n]|\\.){12,})"|\'([^\'\n]{12,})\'', cmd) for q in q if q]
                heads = {t.splitlines()[0].strip() for t in texts if t.strip()}
                hit = any(hd in cmd for hd in heads) or any(ln in cmd for ln in lines) or any(q in t for q in quoted for t in texts)
        if hit:
            what = f"{h.get('task')}'s section" if h.get("task") else f"{len(h.get('blocks') or [])} block(s)"
            who = f"agent {h.get('aid')}" if h.get("aid") else "a dispatch not yet launched"
            return (f"the plan review of {what} in specs/{h.get('feature')}/plan.md is running ({who}) - an edit now voids its verdict; "
                    "wait for it to return (feature 385 T85)" + ("" if not dead(h, now) else "; its dispatch looks dead: PLAN_EDIT_OK=\"<reason>\" passes it"))
    return ""
