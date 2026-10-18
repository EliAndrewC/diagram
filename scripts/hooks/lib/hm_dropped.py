#!/usr/bin/env python3
"""A dispatch a guard refused is sent again or recorded dropped before a turn ends (feature 385 T22, plan D44).

WHY. Measured on feature 385 T05 (2026-10-18, the session transcript): of seven agents sent at 03:57, the decide-first guard
refused four with identical lines that named no check. The session re-sent three at 04:02; the fourth, impl-drift round 2,
was never re-sent, and the session ended its turn "waiting on" it - about 5 h idle until the GM came back. The round arbiter's
fix on hour:385-approach-checklist@11: the turn's end is refused while a refused dispatch is neither re-sent nor recorded.

WHAT IS READ. The Stop payload's `transcript_path`, from its last TURN END - a `system` entry of subtype `turn_duration`,
which the harness writes only for a turn that ended (a turn end this guard blocks writes none, so a refusal stays in the
window until answered) - or from the session's start when there is none. Never from the GM's last prompt: measured, the
incident's refusals (03:57:57-03:58:06) came after a prompt queued at 03:57:47 and taken into the running turn, so that
window would have missed them (spec-fidelity, T22 round 2). A REFUSAL is an Agent call whose result is an error a PreToolUse hook
wrote (`PreToolUse:Agent hook error`). It is ANSWERED by a later Agent call of the same `subagent_type` and the same KEY
that was not refused, or by `make dispatch-dropped TYPE= BUNDLE= WHY=`, which appends to `<gitdir>/dropped-dispatches.jsonl`.
The KEY is the first bundle the prompt names (a `.../MANIFEST.md`, else a `/tmp/l7r-check/...` path), else the call's
description.

    hm_dropped.py stop --root <clone>          (Stop payload on stdin) -> the refusal text on stderr, exit 2; or nothing
    hm_dropped.py drop --root <clone> --type <t> --bundle <key> --why "<reason>"
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

BUNDLE = re.compile(r"[^\s`'\"]*/MANIFEST\.md|/tmp/l7r-check/[^\s`'\")]+")
REFUSED = "PreToolUse:Agent hook error"
DROPPED = "dropped-dispatches.jsonl"


def gitdir(root: Path) -> Path:
    out = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--git-common-dir"], capture_output=True, text=True
    ).stdout.strip()
    p = Path(out or ".git")
    return p if p.is_absolute() else root / p


def key_of(tool_input: dict) -> str:
    m = BUNDLE.search(str(tool_input.get("prompt") or ""))
    return m.group(0) if m else str(tool_input.get("description") or "")


def entries(transcript: Path):
    try:
        fh = transcript.open()
    except OSError:
        return
    with fh:
        for line in fh:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def _content(entry: dict) -> list:
    c = (entry.get("message") or {}).get("content")
    return c if isinstance(c, list) else []


def last_turn_end(rows: list[dict]) -> str:
    """The timestamp of the transcript's last ended turn, or "" (the session's start) when none has ended."""
    stamps = [r.get("timestamp", "") for r in rows if r.get("type") == "system" and r.get("subtype") == "turn_duration"]
    return stamps[-1] if stamps else ""


def calls(rows: list[dict]) -> list[dict]:
    """Every Agent call in order: {t, id, type, key, refused}."""
    out: dict[str, dict] = {}
    for r in rows:
        for b in _content(r):
            if b.get("type") == "tool_use" and b.get("name") == "Agent":
                ti = b.get("input") or {}
                out[b["id"]] = {"t": r.get("timestamp", ""), "type": ti.get("subagent_type") or "", "key": key_of(ti),
                                "refused": False, "why": ""}
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in out and b.get("is_error"):
                text = str(b.get("content") or "")
                if REFUSED in text:
                    out[b["tool_use_id"]]["refused"] = True
                    m = re.search(r"BLOCKED: ([^\n]*)", text)
                    out[b["tool_use_id"]]["why"] = (m.group(1) if m else "")[:160]
    return list(out.values())


def dropped(root: Path) -> set[tuple[str, str]]:
    got = set()
    try:
        lines = (gitdir(root) / DROPPED).read_text().splitlines()
    except OSError:
        return got
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        got.add((d.get("type", ""), d.get("bundle", "")))
    return got


def unanswered(rows: list[dict], since: str, gone: set[tuple[str, str]]) -> list[dict]:
    seq = calls(rows)
    left = []
    for i, c in enumerate(seq):
        if not c["refused"] or c["t"] <= since or (c["type"], c["key"]) in gone:
            continue
        if any(not d["refused"] and (d["type"], d["key"]) == (c["type"], c["key"]) for d in seq[i + 1:]):
            continue
        if any((d["type"], d["key"]) == (c["type"], c["key"]) for d in left):
            continue
        left.append(c)
    return left


def refusal(left: list[dict]) -> str:
    lines = [f"BLOCKED: {len(left)} dispatch(es) a guard refused this turn were neither sent again nor recorded dropped:"]
    for c in left:
        lines.append(f"    {c['type']} on {c['key']}" + (f" - refused: {c['why']}" if c["why"] else ""))
    lines.append("Send each again once its refusal is met, or, if it is no longer wanted:")
    for c in left:
        lines.append(f'    make dispatch-dropped TYPE={c["type"]} BUNDLE="{c["key"]}" WHY="<why it is not owed>"')
    lines.append("(feature 385 T22: a refused impl-drift was never re-sent and the session idled 5 h waiting on it)")
    return "\n".join(lines)


def stop(root: Path, payload: dict) -> int:
    transcript = Path(str(payload.get("transcript_path") or ""))
    if not transcript.is_file():
        return 0
    rows = list(entries(transcript))
    left = unanswered(rows, last_turn_end(rows), dropped(root))
    if left:
        print(refusal(left), file=sys.stderr)
        return 2
    return 0


def drop(root: Path, atype: str, bundle: str, why: str) -> int:
    if len(why.split()) < 2 or len(why) < 8:
        print('dispatch-dropped: WHY="<reason>" needs two words and eight characters, so the audit says why', file=sys.stderr)
        return 2
    row = {"type": atype, "bundle": bundle, "why": why, "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with (gitdir(root) / DROPPED).open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(f"dispatch-dropped: {atype} on {bundle} recorded - {why}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=("stop", "drop"))
    ap.add_argument("--root", default=".")
    ap.add_argument("--type", default="")
    ap.add_argument("--bundle", default="")
    ap.add_argument("--why", default="")
    a = ap.parse_args(argv)
    root = Path(a.root)
    if a.verb == "drop":
        return drop(root, a.type, a.bundle, a.why)
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    return stop(root, payload)


if __name__ == "__main__":
    sys.exit(main())
