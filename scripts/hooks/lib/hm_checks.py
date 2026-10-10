#!/usr/bin/env python3
"""The state of the record checks in flight - decide, then freeze (feature 375, FR-003(b)(c), FR-010; plan D4, D10).

WHY. Measured on feature 372 (2026-10-10): 0105 went through about four full rounds of five to seven checks in wave 108 and
0100 about three in wave 106, because a page was edited while its checks were running - each edit made the running checks
read stale words and re-owed the whole set. The rule (FR-003): while a check on a page or pop-up is running, the page is
frozen; once every check of the round has returned, the edits those checks proposed go in, in one pass; then the page is
checked once. And a check is not re-dispatched while another check on the same page is outstanding.

THE STATE, `<git common dir>/checks-open.json`:

    {"feature": "<dir>", "dispatches": {tool_use_id: {check, subjects, manifest, t, aid, state}},
     "rounds": {"<check>|<subject>": n}, "edits": {subject: [[path, old, new], ...]}}

A dispatch is RUNNING from its PreToolUse until it RETURNS - SubagentStop for its agent id (paired at PostToolUse through
`tool_response.agentId`; measured: specs/375-enforced-wave-process/measurements.json `subagent-stop-probe`), a foreground
PostToolUse, or its answer (`make record-checked` / `claims-checked` / `modal-triaged`), whichever comes first, so a missing
event never freezes a page for good. At return its reply's EDIT blocks join its subjects' `edits`.

A SUBJECT is what a check reads: a question (`q:0105`, both its pages and its notes) or a pop-up (`modal:sheet/bath`, its
`.md` file), from the bundle MANIFEST's `unit:` lines. impl-drift and the claims triage have none (plan D4): a claim is not a
page, and their counts reach FR-010 alone.

    hm_checks.py dispatch   (PreToolUse Agent payload on stdin)  -> refusal JSON or nothing
    hm_checks.py launched   (PostToolUse Agent)
    hm_checks.py returned   (SubagentStop)
    hm_checks.py edit       (PreToolUse Edit/Write/Bash payload) -> refusal JSON or nothing
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

STATE = "checks-open.json"
#: the checks whose subject is a question page or a pop-up, and so freeze it while they run
PAGE_CHECKS = frozenset(
    "quote-check record-format source-reader intro-check record-style translation-check entry-drift "
    "modal-form modal-research modal-depiction".split()
)
#: rounds a check may have on one subject in one feature before the round arbiter rules (FR-010, as the review checks' cap)
ROUND_CAP = 2
#: a check silent this long is reported stale and may be closed by hand (the no-poll guard's wait ceiling)
STALE_S = 90 * 60
#: a dispatch recorded at PreToolUse and never launched (another guard refused the call) stops counting after this
PENDING_S = 120
_UNIT = re.compile(r"^unit: (\S+?):(\S.*?) \S+$", re.M)
_Q = re.compile(r"\b(\d{4})(?:[.#-]|$)")
_EDIT = re.compile(
    r"^(?P<ind>[ \t]*)EDIT[ \t]+`?(?P<path>[^\n`]+?)`?[ \t]*\n(?P=ind)<<<\n(?P<old>.*?)\n(?P=ind)===\n(?P<new>.*?)\n?(?P=ind)>>>[ \t]*$",
    re.S | re.M,
)
_PAGE = re.compile(r"research/questions/(\d{4})-[^/]*\.html$")
_MODAL = re.compile(r"interactive/assets/modals/((?:sheet|hamlet|choice)/[^/]+)\.md$")


def subject_of_unit(slug_tail: str) -> str:
    """`0105.drawing#note` -> `q:0105`; `sheet/bath` -> `modal:sheet/bath`."""
    if "/" in slug_tail and not _Q.match(slug_tail):
        return f"modal:{slug_tail}"
    m = _Q.match(slug_tail)
    return f"q:{m.group(1)}" if m else ""


def subjects_of_manifest(text: str) -> list[str]:
    return sorted({s for _c, tail in _UNIT.findall(text) if (s := subject_of_unit(tail))})


def subject_of_path(path: str) -> str:
    """The subject a file belongs to: a question's page, drawing page or notes; a pop-up's `.md` file."""
    p = path.replace(os.sep, "/")
    if m := _PAGE.search(p) or re.search(r"research/questions/(\d{4})-[^/]*\.notes\.html$", p):
        return f"q:{m.group(1)}"
    if m := _MODAL.search(p):
        return f"modal:{m.group(1)}"
    return ""


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _live(d: Mapping[str, Any], now: float) -> bool:
    """A dispatch that counts: launched, or recorded so recently that its launch may still come. One recorded at PreToolUse
    and refused by another guard never launches, and must not freeze its page."""
    return d.get("state") != "pending" or now - float(d.get("t", 0)) < PENDING_S


def running(state: Mapping[str, Any], subject: str, now: float | None = None) -> list[dict]:
    now = time.time() if now is None else now
    return [d for d in state.get("dispatches", {}).values()
            if subject in d.get("subjects", []) and d.get("state") in ("running", "pending") and _live(d, now)]


def open_round(state: Mapping[str, Any], subject: str, now: float | None = None) -> list[dict]:
    """The dispatches of the subject's current round: dispatched and not yet answered."""
    now = time.time() if now is None else now
    return [d for d in state.get("dispatches", {}).values()
            if subject in d.get("subjects", []) and d.get("state") != "answered" and _live(d, now)]


def dispatch(state: dict[str, Any], tid: str, check: str, manifest: str, text: str, now: float) -> str:
    """Record a check's dispatch, or say why it is refused (FR-003(c) apply once, FR-010 the round cap)."""
    subjects = subjects_of_manifest(text) if check in PAGE_CHECKS else []
    for s in subjects:
        same = [d for d in open_round(state, s, now) if d["check"] == check]
        if same and running(state, s, now):
            return (f"`{check}` is already in {s}'s round and that round has a check still running - all of a round's checks "
                    "return, their edits go in in one pass, then the page is checked once (feature 375 FR-003c)")
        n = state.setdefault("rounds", {}).get(f"{check}|{s}", 0)
        if n >= ROUND_CAP and not state.get("arbiter", {}).get(f"{check}|{s}") == "continue":
            return (f"round {n + 1} of `{check}` on {s} in this feature - the cap is {ROUND_CAP} (feature 375 FR-010). "
                    f"The round arbiter rules first: make arbiter-bundle TRIGGER=\"{check}|{s}\", dispatch `round-arbiter` on its "
                    "MANIFEST, then make arbiter-ruled")
    for s in subjects:
        if not open_round(state, s, now):
            state.setdefault("edits", {})[s] = []  # a new round: the last round's proposals are spent
        state["rounds"][f"{check}|{s}"] = state["rounds"].get(f"{check}|{s}", 0) + 1  # every dispatch let through is a round
    state.setdefault("dispatches", {})[tid] = {"check": check, "subjects": subjects, "manifest": manifest, "t": now, "state": "pending"}
    return ""


def launched(state: dict[str, Any], tid: str, agent_id: str, background: bool) -> None:
    d = state.get("dispatches", {}).get(tid)
    if d is None:
        return
    d["aid"] = agent_id
    d["state"] = "running" if background else "returned"


def returned(state: dict[str, Any], agent_id: str, reply: str) -> None:
    for d in state.get("dispatches", {}).values():
        if d.get("aid") == agent_id and d.get("state") == "running":
            d["state"] = "returned"
            for path, old, new in _blocks(reply):
                for s in d["subjects"]:
                    state.setdefault("edits", {}).setdefault(s, []).append([path, old, new])


def answered(state: dict[str, Any], check: str, subjects: list[str]) -> int:
    """Close the dispatches of `check` on any of `subjects` - its answer is recorded (`make record-checked`), or `make
    check-closed` closed a silent one (check `*`)."""
    n = 0
    for d in state.get("dispatches", {}).values():
        if d["check"] in (check, "*") or check == "*":
            if set(d["subjects"]) & set(subjects) and d.get("state") != "answered":
                d["state"] = "answered"
                n += 1
    return n


def record_answer(root: Path, check: str, slugs: list[str]) -> None:
    """Called by `record_owed.answer`: the units it answered close their subjects' dispatches of that check."""
    path = state_path(str(root))
    if path is None or not path.is_file():
        return
    state = load(path)
    if answered(state, check, sorted({s for slug in slugs if (s := subject_of_unit(slug.split(":", 1)[-1]))})):
        save(path, state)


def proposed(state: Mapping[str, Any], subject: str, old: str, new: str) -> bool:
    """An edit the round's checks proposed, or part of one applied in place: its old text inside a block's old text, and the
    block's new text reading the same up to it and then `new` (a different replacement at a proposed place is not one)."""
    for _p, b_old, b_new in state.get("edits", {}).get(subject, []):
        i = b_old.find(old)
        if old and i >= 0 and b_new.startswith(b_old[:i] + new):
            return True
    return False


def edit_refusal(state: Mapping[str, Any], path: str, old: str, new: str, now: float) -> str:
    """Why an Edit to `path` is refused now (FR-003(b)), or ''."""
    s = subject_of_path(path)
    if not s or not open_round(state, s, now):
        return ""
    live = running(state, s, now)
    if live:
        names = ", ".join(sorted({d["check"] for d in live}))
        stale = [d for d in live if now - d["t"] > STALE_S]
        tail = (f" ({len(stale)} silent past 90 minutes: `make check-closed SUBJECT={s} REASON=...` closes it)" if stale else "")
        return f"{s} is frozen while its checks run ({names}) - edit it once every check of the round has returned{tail} (feature 375 FR-003b)"
    if proposed(state, s, old, new):
        return ""
    blocks = state.get("edits", {}).get(s, [])
    return (f"{s}'s checks have returned, and this edit is none of the {len(blocks)} edit(s) they proposed - apply those (`make "
            "apply-edits REPLY=<the reply>`, or by hand), answer the checks, and make any other change after (FR-003b)"
            if blocks else f"{s}'s checks returned no edit to apply; answer them (`make record-checked`) before editing it (FR-003b)")


def state_path(cwd: str) -> Path | None:
    """`<git common dir>/checks-open.json` of the clone holding `cwd`, found without running git (a hook on every call)."""
    p = Path(cwd or ".").resolve()
    for d in (p, *p.parents):
        g = d / ".git"
        if g.is_dir():
            return g / STATE
        if g.is_file():
            m = re.match(r"gitdir:\s*(.+)", g.read_text(encoding="utf-8").strip())
            if m:
                gd = (d / m.group(1)).resolve()
                common = gd / "commondir"
                return ((gd / common.read_text(encoding="utf-8").strip()).resolve() if common.is_file() else gd) / STATE
    return None


def _manifest_of(prompt: str) -> tuple[str, str]:
    m = re.search(r"(/[^\s`\"'<>)]*MANIFEST\.md)", prompt)
    if not m:
        return "", ""
    try:
        return m.group(1), Path(m.group(1)).read_text(encoding="utf-8")
    except OSError:
        return m.group(1), ""


def _reply_of(transcript: str, last: str) -> str:
    """A returned agent's reply: SubagentStop's `last_assistant_message`, else the last text of its own transcript."""
    if last:
        return last
    try:
        lines = Path(transcript).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    for raw in reversed(lines):
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        for b in (d.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text"):
                return b["text"]
    return ""


def _blocks(reply: str) -> list[tuple[str, str, str]]:
    out = []
    for m in _EDIT.finditer(reply):
        ind = m.group("ind")
        undent = lambda t: "\n".join(line[len(ind):] if line.startswith(ind) else line for line in t.split("\n"))  # noqa: E731
        out.append((m.group("path").strip(), undent(m.group("old")), undent(m.group("new"))))
    return out


def _reply_file(path: str) -> str:
    """The reply `make apply-edits FROM=` reads: an agent's transcript (`.jsonl` / `.output`, its last text) or a saved reply."""
    if path.endswith((".jsonl", ".output")):
        return _reply_of(path, "")
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def apply_refusal(state: Mapping[str, Any], command: str, now: float) -> str:
    """Why `make apply-edits FROM=<reply>` is refused now: a subject it edits has a check still running, or a block in it is
    none of that subject's round's returned blocks (FR-003b). Outside any open round it is not this guard's business."""
    m = re.search(r"\bmake\b[^;&|]*\bapply-edits\b[^;&|]*\bFROM=(\"[^\"]+\"|'[^']+'|\S+)", command)
    if not m:
        return ""
    for path, old, new in _blocks(_reply_file(m.group(1).strip("'\""))):
        s = subject_of_path(path)
        if not s or not open_round(state, s, now):
            continue
        if running(state, s, now):
            return edit_refusal(state, path, old, new, now)
        if [path, old, new] not in [list(e) for e in state.get("edits", {}).get(s, [])] and not proposed(state, s, old, new):
            return f"a block of this reply for {s} is not one its round's checks returned - apply only this round's replies (FR-003b)"
    return ""


def _feature(root: Path) -> str:
    try:
        return Path(str(json.loads((root / ".specify" / "feature.json").read_text(encoding="utf-8")).get("feature_directory", ""))).name
    except (OSError, ValueError):
        return ""


def handle(mode: str, payload: Mapping[str, Any], now: float | None = None) -> str:
    """One hook event. Returns a refusal message (the hook exits 2 with it) or ''."""
    now = time.time() if now is None else now
    path = state_path(str(payload.get("cwd") or os.getcwd()))
    if path is None:
        return ""
    state = load(path)
    feature = _feature(path.parent.parent if path.parent.name == ".git" else Path(str(payload.get("cwd") or ".")))
    if state.get("feature") != feature:  # the round cap counts per feature (FR-010): a new feature starts its own count
        state = {"feature": feature, "dispatches": state.get("dispatches", {})}
    ti = payload.get("tool_input") or {}
    ti = ti if isinstance(ti, Mapping) else {}
    out = ""
    if mode == "dispatch" and payload.get("tool_name") == "Agent":
        check = str(ti.get("subagent_type") or "")
        if check not in PAGE_CHECKS or re.search(r'FREEZE_OK="[^"]{8,}"', str(ti.get("prompt") or "")):
            return ""
        manifest, text = _manifest_of(str(ti.get("prompt") or ""))
        out = dispatch(state, str(payload.get("tool_use_id") or now), check, manifest, text, now)
    elif mode == "launched" and payload.get("tool_name") == "Agent":
        resp = payload.get("tool_response") if isinstance(payload.get("tool_response"), Mapping) else {}
        launched(state, str(payload.get("tool_use_id") or ""), str(resp.get("agentId") or ""), resp.get("status") == "async_launched")
    elif mode == "returned":
        returned(state, str(payload.get("agent_id") or ""), _reply_of(str(payload.get("agent_transcript_path") or ""),
                                                                       str(payload.get("last_assistant_message") or "")))
    elif mode == "edit" and payload.get("tool_name") == "Bash":
        command = str(ti.get("command") or "")
        return "" if re.search(r'FREEZE_OK="[^"]{8,}"', command) else apply_refusal(state, command, now)
    elif mode == "edit" and payload.get("tool_name") in ("Edit", "Write", "MultiEdit"):
        if re.search(r'FREEZE_OK="[^"]{8,}"', " ".join(str(v) for v in ti.values())):
            return ""
        old = str(ti.get("old_string") or "") if payload.get("tool_name") == "Edit" else ""
        return edit_refusal(state, str(ti.get("file_path") or ""), old, str(ti.get("new_string") or ti.get("content") or ""), now)
    else:
        return ""
    if not out:
        save(path, state)
    return out


def main(argv: list[str]) -> int:
    mode = argv[0] if argv else ""
    if mode == "close" and len(argv) == 3:  # make check-closed SUBJECT= REASON=
        path = state_path(os.getcwd())
        state = load(path) if path else {}
        if len(argv[2].split()) < 2:
            print("check-closed: REASON needs two words or more - it is what a later audit reads", file=sys.stderr)
            return 2
        n = answered(state, "*", [argv[1]])
        if path and n:
            save(path, state)
        print(f"check-closed: {n} dispatch(es) on {argv[1]} closed - {argv[2]}")
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    msg = handle(mode, payload)
    if msg:
        print(f"BLOCKED: {msg}\n(scripts/hooks/lib/hm_checks.py; escape FREEZE_OK=\"<reason>\" in the prompt or the edit)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
