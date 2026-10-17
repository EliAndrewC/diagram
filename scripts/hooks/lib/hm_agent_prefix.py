"""The dispatch guard's decider: a large block an Agent prompt shares with an earlier one, after a part that differs (feature
383 amendment 6, FR-034, plan D37). GUARD_EDIT_OK: feature 383 amendment 6 - a NEW guard, the GM 2026-10-17.

WHY. A prompt is cached as a PREFIX: the cache reads up to the first character that differs from an earlier request and writes
everything after it fresh. The GM, 2026-10-17: *"if I run a subagent and then I am ... giving it ... a unique sentence for its
prompt, and then I put 10 kilobytes of context after that, then none of that gets cached ... even if that same 10 kilobytes
was shared with every other subagent"* - at work that shape cost them an order of magnitude. So a block of SHARED characters
or more that a new prompt has in common with an earlier dispatch of the same type and model (the system prompt before the
prompt differs between types, so nothing is shared across them) is refused when a part that differs comes before it in the
new prompt and that part is not the same in the earlier one. It passes when everything before it is identical in both, or when
it starts the new prompt: the fixed form, which the next dispatch reads from the cache.

The comparison is by lines: the longest run of identical lines both prompts hold, after their common prefix. Prompts are
capped at CAP characters; the session's last KEEP dispatches that passed are kept, by type, in `<git dir>/l7r-agent-prompts/`.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re

#: the block that matters: ~500 tokens, where a cached prefix starts to count against the ~2.5k a dispatch writes regardless
#: (research R13). A convenience number to move, never a target (the GM's case was 10 KB).
SHARED = 2000
CAP = 65536
KEEP = 30
#: the escape, in the prompt, with a reason of two words or more
ESCAPE = re.compile(r"AGENT_PREFIX_OK\s*[=:]\s*[\"']?\S+\s+\S+")


def longest_shared_run(new: str, old: str) -> tuple[int, int]:
    """(characters, start offset in `new`) of the longest run of consecutive identical lines both texts hold."""
    nl, ol = new.splitlines(keepends=True), old.splitlines(keepends=True)
    where: dict[str, list[int]] = {}
    for j, line in enumerate(ol):
        where.setdefault(line, []).append(j)
    best, best_start = 0, 0
    run: dict[int, tuple[int, int]] = {}  # old index ending a run -> (characters, start line in new)
    offsets, pos = [], 0
    for line in nl:
        offsets.append(pos)
        pos += len(line)
    for i, line in enumerate(nl):
        nxt: dict[int, tuple[int, int]] = {}
        for j in where.get(line, ()):
            size, start = run.get(j - 1, (0, i))
            nxt[j] = (size + len(line), start)
            if nxt[j][0] > best:
                best, best_start = nxt[j][0], offsets[start]
        run = nxt
    return best, best_start


def finding(new: str, old: str) -> tuple[int, int]:
    """(characters, offset in `new`) of a shared block that is NOT cacheable as placed - (0, 0) when there is none."""
    new, old = new[:CAP], old[:CAP]
    prefix = len(os.path.commonprefix([new, old]))
    size, start = longest_shared_run(new[prefix:], old[prefix:])
    start += prefix
    if size < SHARED or start == 0:
        return 0, 0
    return size, start


def _store(git_dir: str, session: str) -> pathlib.Path:
    return pathlib.Path(git_dir) / "l7r-agent-prompts" / f"{hashlib.sha256(session.encode()).hexdigest()[:16]}.jsonl"


def earlier(git_dir: str, session: str, key: str) -> list[str]:
    path = _store(git_dir, session)
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError, ValueError:
        return []
    return [r["prompt"] for r in rows if r.get("key") == key]


def remember(git_dir: str, session: str, key: str, prompt: str) -> None:
    path = _store(git_dir, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        rows = []
    rows.append(json.dumps({"key": key, "prompt": prompt[:CAP]}))
    path.write_text("\n".join(rows[-KEEP:]) + "\n", encoding="utf-8")


def verdict(payload: dict, git_dir: str) -> str:
    """ "" to pass (and remember the prompt), else the refusal's first line."""
    ti = payload.get("tool_input") or {}
    if payload.get("tool_name") != "Agent" or not git_dir:
        return ""
    prompt, session = str(ti.get("prompt") or ""), str(payload.get("session_id") or "")
    key = f"{ti.get('subagent_type') or 'general-purpose'}|{ti.get('model') or ''}"
    for old in reversed(earlier(git_dir, session, key)):
        size, start = finding(prompt, old)
        if size and ESCAPE.search(prompt):
            break  # escaped with a reason: the caller says why this shape is right; recorded by the hook
        if size:
            first = prompt[start : start + 70].splitlines()[0] if prompt[start:].strip() else ""
            return f"{size} characters shared with an earlier `{key.split('|')[0]}` dispatch start at character {start} of this prompt, after text that differs: `{first}`"
    remember(git_dir, session, key, prompt)
    return ""


def main() -> int:
    import sys

    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    got = verdict(payload if isinstance(payload, dict) else {}, sys.argv[1] if len(sys.argv) > 1 else "")
    if got:
        print(got)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
