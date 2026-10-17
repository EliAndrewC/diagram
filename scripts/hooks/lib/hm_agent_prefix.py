"""The dispatch guard's decider: a large block an Agent prompt repeats from an earlier dispatch of its type (feature 383
amendment 6, FR-034, plans D37 and D41). GUARD_EDIT_OK: feature 383 amendment 6 - a NEW guard, the GM 2026-10-17.

WHY. The GM, 2026-10-17: *"if I run a subagent and then I am ... giving it ... a unique sentence for its prompt, and then I put
10 kilobytes of context after that, then none of that gets cached ... even if that same 10 kilobytes was shared with every other
subagent"* - at work that shape cost them an order of magnitude. A subagent's request has one cache breakpoint across launches,
after its system prompt (the agent file); the first message - the instruction files and the launch prompt - has none, so text
a launch prompt repeats is written fresh on every launch WHEREVER it sits (research R16, a proxy capture). Only the agent file
is reused, so a block of SHARED characters or more that a new prompt repeats from an earlier dispatch of its type and model is
refused, with that fix; a prompt identical to an earlier one as a whole passes (the cache does reuse that, R14). Within a type:
the fix is that type's agent file. NOT "put it first": the guard first landed passing a block that started the prompt, on R14's
wholly identical prompt taken for a rule about a prompt's start (reopened and corrected the same day).

The comparison is by lines: every run of identical lines both prompts hold. Prompts are capped at CAP characters; the
session's last KEEP dispatches that passed are kept, by type, in `<git dir>/l7r-agent-prompts/`.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import time

#: the block that matters: ~500 tokens, where a cached prefix starts to count against the ~2.5k a dispatch writes regardless
#: (research R13). A convenience number to move, never a target (the GM's case was 10 KB).
SHARED = 2000
CAP = 65536
KEEP = 30
#: a WAVE: this many launches of one agent type inside WAVE_S seconds is the most that goes by hand - the next is refused and
#: sent to the `check-wave` workflow, which staggers by itself and wakes the main session once (feature 383 amendment 7, plan
#: D46; research R20: 5,544 wakes a month re-reading a median 405k tokens). Design numbers to move. The fan-out rule this replaced
#: ("the first alone, the rest in the next message", D42) is gone: the extra main-session turn re-read ~92k tokens of context to
#: save ~3.4k a launch (R20).
WAVE_N = 3
WAVE_S = 10
#: the escape, in the prompt, with a reason of two words or more
#: the wave rule's escape: a batch that must stay hand-launched says why
WAVE_ESCAPE = re.compile(r"WAVE_OK\s*[=:]\s*[\"']?\S+\s+\S+")
ESCAPE = re.compile(r"AGENT_PREFIX_OK\s*[=:]\s*[\"']?\S+\s+\S+")


def shared_runs(new: str, old: str, least: int = SHARED) -> list[tuple[int, int]]:
    """(characters, start offset in `new`) of each maximal run of consecutive identical lines both texts hold that reaches
    `least` characters, in the order they start in `new`."""
    nl, ol = new.splitlines(keepends=True), old.splitlines(keepends=True)
    where: dict[str, list[int]] = {}
    for j, line in enumerate(ol):
        where.setdefault(line, []).append(j)
    offsets, pos = [], 0
    for line in nl:
        offsets.append(pos)
        pos += len(line)
    best: dict[int, int] = {}  # start line in new -> the longest run starting there
    run: dict[int, tuple[int, int]] = {}  # old index ending a run -> (characters, start line in new)
    for i, line in enumerate(nl):
        nxt: dict[int, tuple[int, int]] = {}
        for j in where.get(line, ()):
            size, start = run.get(j - 1, (0, i))
            nxt[j] = (size + len(line), start)
            best[start] = max(best.get(start, 0), nxt[j][0])
        run = nxt
    return [(size, offsets[start]) for start, size in sorted(best.items()) if size >= least]


def finding(new: str, old: str) -> tuple[int, int]:
    """(characters, offset in `new`) of the first block of SHARED+ characters `new` repeats from `old`, wherever it sits - (0, 0)
    when there is none, or when the two prompts are identical as a whole (the one case the cache reuses).

    WHERE IT SITS DOES NOT MATTER (feature 383 amendment 6, reopened): a subagent's request has its cache breakpoint after the
    system prompt - the agent file - and none inside the first message, which holds the instruction files and the launch
    prompt; shared text placed first in a launch prompt is written fresh on every launch (research R16, a proxy capture). The
    guard first landed passing a block that started the prompt, on a measurement of a WHOLLY identical prompt (R14)."""
    new, old = new[:CAP], old[:CAP]
    if new == old:
        return 0, 0
    runs = shared_runs(new, old)
    return runs[0] if runs else (0, 0)


def _store(git_dir: str, session: str) -> pathlib.Path:
    return pathlib.Path(git_dir) / "l7r-agent-prompts" / f"{hashlib.sha256(session.encode()).hexdigest()[:16]}.jsonl"


def _rows(git_dir: str, session: str, key: str) -> list[dict]:
    try:
        rows = [json.loads(line) for line in _store(git_dir, session).read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError, ValueError:
        return []
    return [r for r in rows if r.get("key") == key]


def earlier(git_dir: str, session: str, key: str) -> list[str]:
    return [r["prompt"] for r in _rows(git_dir, session, key)]


def waved(rows: list[dict], kind: str, now: float) -> bool:
    """Would a launch of `kind` at `now` be past the hand-launched wave: WAVE_N of its type passed in the WAVE_S before it?"""
    return sum(1 for r in rows if str(r.get("key", "")).split("|")[0] == kind and 0 <= now - float(r.get("t", 0)) < WAVE_S) >= WAVE_N


def remember(git_dir: str, session: str, key: str, prompt: str, now: float | None = None) -> None:
    path = _store(git_dir, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        rows = []
    now = time.time() if now is None else now
    rows.append(json.dumps({"key": key, "prompt": prompt[:CAP], "t": now}))
    path.write_text("\n".join(rows[-KEEP:]) + "\n", encoding="utf-8")


def _all_rows(git_dir: str, session: str) -> list[dict]:
    try:
        return [json.loads(line) for line in _store(git_dir, session).read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError, ValueError:
        return []


def verdict(payload: dict, git_dir: str, now: float | None = None, wave_unit: bool = False) -> str:
    """ "" to pass (and remember the prompt), "ESCAPED" (passed with a reason), "FANOUT ..." or the refusal's first line."""
    ti = payload.get("tool_input") or {}
    if payload.get("tool_name") != "Agent" or not git_dir:
        return ""
    prompt, session = str(ti.get("prompt") or ""), str(payload.get("session_id") or "")
    key = f"{ti.get('subagent_type') or 'general-purpose'}|{ti.get('model') or ''}"
    now = time.time() if now is None else now
    rows = _rows(git_dir, session, key)
    escaped = bool(ESCAPE.search(prompt))
    kind = key.split("|")[0]
    if not wave_unit and not WAVE_ESCAPE.search(prompt) and waved(_all_rows(git_dir, session), kind, now):
        return f"WAVE {kind}"
    for old in reversed([r["prompt"] for r in rows]):
        size, start = finding(prompt, old)
        if size and escaped:
            remember(git_dir, session, key, prompt, now)
            return "ESCAPED"  # with a reason: the caller says why this shape is right; the hook records it
        if size:
            first = prompt[start : start + 70].splitlines()[0] if prompt[start:].strip() else ""
            return f"{size} characters of this prompt repeat an earlier `{key.split('|')[0]}` dispatch's, from character {start}: `{first}`"
    remember(git_dir, session, key, prompt, now)
    return ""


def main() -> int:
    import sys

    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    import os

    clock = os.environ.get("L7R_AGENT_NOW", "")  # a test's clock: the suite's dispatches say when they happen
    got = verdict(payload if isinstance(payload, dict) else {}, sys.argv[1] if len(sys.argv) > 1 else "", float(clock) if clock else None, os.environ.get("L7R_WAVE_UNIT") == "1")
    if got:
        print(got)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
