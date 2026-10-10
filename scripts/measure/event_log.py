#!/usr/bin/env python3
"""The feature event log - one line per hook event, so where a feature's time went is counted, not remembered (feature 375).

WHY (the GM, 2026-10-10): *"maybe the actual solution here is that we have hooks built into our tooling which will save off
timestamps that allow us to mechanically and trivially calculate these numbers. Such that the post hoc session review or
analysis of how long a feature took is not actually difficult to do"*. Feature 372's waves 105-111 spent about 120 agent
dispatches on about a dozen rows, and that was measured by reading a transcript by hand. This log is what `make
feature-report` (`feature_report.py`) reads instead.

THE LINE (plan D7). `event-log-hooks.sh` hands every PreToolUse, PostToolUse, SubagentStart, SubagentStop,
UserPromptSubmit and Stop payload here; one JSON line goes to `<git common dir>/l7r-events/<feature dir>.jsonl`, the feature
being the clone's `.specify/feature.json` (`_unassigned.jsonl` without one). Fields: `t` (UTC), `sid`, `ev`, and where they
apply `tool`, `id` (tool_use_id), `cat` (`category`), `make` (a Bash call's make target), `path`, `old`/`new` (digests of an
Edit's strings - the reversal wire), `agent`/`aid`/`manifest` (an agent's type, id and the MANIFEST its prompt names),
`ms` (PostToolUse's duration), `verdict` (a returned agent's verdict word, or `clean` / `findings`). The gap from one PostToolUse to the next PreToolUse is the model's own time. A clone's git dir
outlives its sessions and any compaction, and the report reads every clone's log for the feature.

It never refuses and never prints: a hook that adds a line to every tool call must not be able to stop one.

THE TRANSCRIPT (plan D8). `from-transcript` converts a Claude Code session transcript into the same events, for a feature
built before the hook existed (372, and 375 itself, whose hooks only fire once landed): a tool_use is its PreToolUse, its
tool_result its PostToolUse, an async agent's launch its SubagentStart and the queue's `<task-notification>` enqueue its
SubagentStop, a typed prompt UserPromptSubmit, an end_turn Stop.

    event_log.py hook                           read one hook payload on stdin, append its line
    event_log.py from-transcript <jsonl>        print the transcript's events as lines
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

#: The record checks (the record's own and the modal checks), answered by `make record-checked`
RECORD_CHECKS = frozenset(
    "quote-check record-format source-applicability source-reader entry-drift record-style translation-check intro-check "
    "modal-form modal-research modal-depiction".split()
)
CLAIMS_CHECKS = frozenset({"impl-drift"})
REVIEW_CHECKS = frozenset({"glyph-check", "settlement-review", "fix-check", "building-review", "size-audit"})
SPEC_REVIEWS = frozenset({"spec-fidelity", "spec-fidelity-verify"})
#: make targets by category (plan D9); every other target is `other tool`
MAKE_CATEGORIES = {
    "quick": "quick test",
    "test-file": "test file",
    "done": "gate",
    "tick": "spec-kit step",
    "claim": "spec-kit step",
    "plan-verdict": "spec-kit step",
}
EDIT_TOOLS = frozenset({"Edit", "Write", "NotebookEdit", "MultiEdit"})
_MAKE = re.compile(r"(?:^|[;&|(]\s*|\s)make\s+(?:-[CfIjo]\s+\S+\s+|-{1,2}[\w-]+(?:=\S+)?\s+|[A-Z_]+=\S*\s+)*([a-z][\w-]*)")
_MANIFEST = re.compile(r"(/[^\s`\"'<>)]*MANIFEST\.md)")
_NOTIFICATION = re.compile(r"<task-id>([^<]+)</task-id>")
_RESULT = re.compile(r"<result>(.*?)(?:</result>|$)", re.S)
#: A returned check's verdict word, the first that appears (plan D8: the report counts BLOCKED reviews and clean runs)
_VERDICT = re.compile(r"\b(NOT-REVIEWABLE|NOT FAITHFUL|CHANGES REQUIRED|BLOCKED|FAITHFUL|CLEAR|NEEDS-WORK|PASS|FAIL)\b")


def verdict_of(text: str) -> str:
    """The verdict a returned agent's reply leads with: a verdict word, else `clean` when every count in its first line is
    zero ("COVERAGE 0 findings; TRUTH 0; LINKS 0", "0/0/0"), else `findings` when one is not, else ''."""
    m = _VERDICT.search(text[:600])
    if m:
        return m.group(1)
    first = next((ln for ln in text.strip().splitlines() if ln.strip()), "")
    nums = re.findall(r"\b\d+\b", first)
    if nums:
        return "clean" if all(n == "0" for n in nums) else "findings"
    return ""
EVENTS_DIR = "l7r-events"


def now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def digest(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def make_target(command: str) -> str:
    """The first make target a Bash command runs (`make -C x quick ALL=1` -> `quick`), or ''."""
    m = _MAKE.search(command)
    return m.group(1) if m else ""


def agent_category(agent_type: str, prompt: str = "") -> str:
    """What kind of subagent this is (plan D9): a triage agent is ad hoc, so its MANIFEST says which triage it is."""
    if agent_type in CLAIMS_CHECKS or "claims-triage" in prompt:
        return "claims check"
    if agent_type in RECORD_CHECKS or "modal-triage" in prompt:
        return "record check"
    if agent_type in REVIEW_CHECKS:
        return "review check"
    if agent_type in SPEC_REVIEWS:
        return "spec review"
    if agent_type == "round-arbiter":
        return "round arbiter"
    return "other subagent"


def category(tool: str, tool_input: Mapping[str, Any]) -> str:
    """The category of one tool call, from the call alone (plan D9)."""
    if tool in EDIT_TOOLS:
        return "edit"
    if tool == "Bash":
        return MAKE_CATEGORIES.get(make_target(str(tool_input.get("command") or "")), "other tool")
    if tool == "Agent":
        return agent_category(str(tool_input.get("subagent_type") or ""), str(tool_input.get("prompt") or ""))
    if tool == "Skill" and str(tool_input.get("skill") or "").startswith("speckit-"):
        return "spec-kit step"
    return "other tool"


def line(payload: Mapping[str, Any], t: str | None = None) -> dict[str, Any]:
    """The log line for one hook payload."""
    ev = str(payload.get("hook_event_name") or "")
    out: dict[str, Any] = {"t": t or now(), "sid": payload.get("session_id") or "", "ev": ev}
    tool = payload.get("tool_name")
    if tool:
        ti = payload.get("tool_input") or {}
        ti = ti if isinstance(ti, Mapping) else {}
        out.update(tool=tool, id=payload.get("tool_use_id") or "", cat=category(str(tool), ti))
        if tool == "Bash":
            target = make_target(str(ti.get("command") or ""))
            if target:
                out["make"] = target
        elif tool in EDIT_TOOLS:
            out["path"] = ti.get("file_path") or ti.get("notebook_path") or ""
            if tool == "Edit":
                out.update(old=digest(str(ti.get("old_string") or "")), new=digest(str(ti.get("new_string") or "")))
            elif tool == "Write":
                out["new"] = digest(str(ti.get("content") or ""))
        elif tool == "Agent":
            out["agent"] = ti.get("subagent_type") or "general-purpose"
            m = _MANIFEST.search(str(ti.get("prompt") or ""))
            if m:
                out["manifest"] = m.group(1)
            resp = payload.get("tool_response")
            if isinstance(resp, Mapping) and resp.get("agentId"):
                out["aid"] = resp["agentId"]
        if isinstance(payload.get("duration_ms"), (int, float)):
            out["ms"] = payload["duration_ms"]
    elif ev in ("SubagentStart", "SubagentStop"):
        out.update(agent=payload.get("agent_type") or "", aid=payload.get("agent_id") or "")
        out["cat"] = agent_category(str(out["agent"]))
        verdict = verdict_of(str(payload.get("last_assistant_message") or ""))
        if verdict:
            out["verdict"] = verdict
    return out


def clone_root(cwd: str) -> Path | None:
    """The working tree holding `cwd` - walked up to its `.git`, never by running git (a hook on every call stays cheap)."""
    p = Path(cwd or ".").resolve()
    for d in (p, *p.parents):
        if (d / ".git").exists():
            return d
    return None


def common_git_dir(root: Path) -> Path:
    """The git dir a worktree shares with its clone (`.git` may be a `gitdir:` file in a worktree)."""
    g = root / ".git"
    if g.is_file():
        m = re.match(r"gitdir:\s*(.+)", g.read_text(encoding="utf-8").strip())
        g = (root / m.group(1)).resolve() if m else g
        common = g / "commondir"
        if common.is_file():
            g = (g / common.read_text(encoding="utf-8").strip()).resolve()
    return g


def feature_of(root: Path) -> str:
    """The clone's active feature directory name (`375-enforced-wave-process`), or '' when none is set."""
    try:
        data = json.loads((root / ".specify" / "feature.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    return Path(str(data.get("feature_directory") or "")).name


def log_path(root: Path, feature: str) -> Path:
    base = Path(os.environ["L7R_EVENTS_DIR"]) if os.environ.get("L7R_EVENTS_DIR") else common_git_dir(root) / EVENTS_DIR
    return base / f"{feature or '_unassigned'}.jsonl"


def append(payload: Mapping[str, Any]) -> Path | None:
    """Append the payload's line to its feature's log; None when the call is outside any clone."""
    root = clone_root(str(payload.get("cwd") or os.getcwd()))
    if root is None:
        return None
    path = log_path(root, feature_of(root))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line(payload), ensure_ascii=False, separators=(",", ":")) + "\n")
    return path


# ---- the transcript (plan D8) --------------------------------------------------------------------------------------


def _typed_prompt(content: Any) -> bool:  # noqa: ANN401 - a transcript's content is a string or a list of blocks
    """Whether a user message is a prompt the GM typed (not a tool result, a notification or a system reminder)."""
    if isinstance(content, list):
        texts = [b.get("text", "") for b in content if isinstance(b, Mapping) and b.get("type") == "text"]
        if not texts or any(isinstance(b, Mapping) and b.get("type") == "tool_result" for b in content):
            return False
        content = "\n".join(texts)
    text = str(content).lstrip()
    return bool(text) and not text.startswith(("<task-notification>", "<system-reminder>", "<local-command", "Caveat:"))


def from_transcript(rows: Iterator[Mapping[str, Any]] | list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """The events a session transcript records, in time order, as `line` would have written them."""
    out: list[dict[str, Any]] = []
    calls: dict[str, tuple[str, Mapping[str, Any]]] = {}
    agent_types: dict[str, str] = {}
    for d in rows:
        if d.get("isSidechain"):
            continue
        t, sid, kind = str(d.get("timestamp") or ""), str(d.get("sessionId") or ""), d.get("type")
        if kind == "assistant":
            msg = d.get("message") or {}
            for b in msg.get("content") or []:
                if isinstance(b, Mapping) and b.get("type") == "tool_use":
                    calls[str(b.get("id"))] = (str(b.get("name")), b.get("input") or {})
                    out.append(line({"hook_event_name": "PreToolUse", "session_id": sid, "tool_name": b.get("name"),
                                     "tool_use_id": b.get("id"), "tool_input": b.get("input") or {}}, t))
            if msg.get("stop_reason") == "end_turn":
                out.append(line({"hook_event_name": "Stop", "session_id": sid}, t))
        elif kind == "user" and not d.get("isMeta"):
            content = (d.get("message") or {}).get("content")
            if isinstance(content, list):
                for b in content:
                    if isinstance(b, Mapping) and b.get("type") == "tool_result":
                        name, ti = calls.get(str(b.get("tool_use_id")), ("", {}))
                        resp = d.get("toolUseResult") if isinstance(d.get("toolUseResult"), Mapping) else {}
                        out.append(line({"hook_event_name": "PostToolUse", "session_id": sid, "tool_name": name,
                                         "tool_use_id": b.get("tool_use_id"), "tool_input": ti, "tool_response": resp}, t))
                        if name == "Agent" and resp.get("agentId"):
                            atype = str(ti.get("subagent_type") or "general-purpose")
                            agent_types[str(resp["agentId"])] = atype
                            if resp.get("status") == "async_launched":
                                out.append(line({"hook_event_name": "SubagentStart", "session_id": sid,
                                                 "agent_type": atype, "agent_id": resp["agentId"]}, t))
            if _typed_prompt(content):
                out.append(line({"hook_event_name": "UserPromptSubmit", "session_id": sid}, t))
        elif kind == "queue-operation" and d.get("operation") == "enqueue":
            content = str(d.get("content") or "")
            m = _NOTIFICATION.search(content)
            if m and m.group(1) in agent_types:
                r = _RESULT.search(content)
                out.append(line({"hook_event_name": "SubagentStop", "session_id": sid, "agent_type": agent_types[m.group(1)],
                                 "agent_id": m.group(1), "last_assistant_message": r.group(1) if r else ""}, t))
    out.sort(key=lambda e: e["t"])
    return out


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if raw:
                try:
                    yield json.loads(raw)
                except ValueError:
                    continue


def main(argv: list[str]) -> int:
    if argv[:1] == ["hook"]:
        try:
            append(json.loads(sys.stdin.read() or "{}"))
        except Exception:  # noqa: BLE001 - the log never stops a tool call (module docstring)
            pass
        return 0
    if argv[:1] == ["from-transcript"] and len(argv) >= 2:
        for e in from_transcript(read_jsonl(Path(argv[1]))):
            sys.stdout.write(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n")
        return 0
    sys.stderr.write(__doc__.split("\n\n")[-1] + "\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
