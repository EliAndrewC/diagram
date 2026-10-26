#!/usr/bin/env python3
"""Does the turn's final message put a question or a decision to the GM, unfiltered? (feature 429 FR-002, D168)

`escalation-hooks.sh` arms on a review dispatch, so a question with no review behind it reached the GM unfiltered:
on 2026-10-25 a feature 417 report asked him whether a finding applied and which of two placements to take, and he
answered "that is the kind of question that our processes are supposed to answer". This decider reads the final
message (the Stop payload's `last_assistant_message`) for an ASK, and the transcript for an `escalation-check`
dispatched since the GM's last message.

The detector was measured on past final messages before it shipped (`specs/429-memory-rules-as-guards/research.md`):
a line outside code, block quotes and quoted text that carries an ask phrase, or ends in "?" with "you"/"your"/"I".

A QUESTION KEPT FOR THE GM IS NAMED THE TURN IT IS KEPT (feature 432, FR-002): `unnamed` reads the clone's kept questions
(`specs/*/gm-review.jsonl`, kind `question`, status `kept`) whose `kept` time is after the GM's last message, and prints each
whose id (`NNN#row`) the final message does not carry - the one door to him ends in front of him, not in a queue.

Usage: hm_gm_question.py unnamed <clone> < stop payload  ->  prints each unnamed kept question and exits 1; exits 0 otherwise.
Usage: hm_gm_question.py judge < stop payload  ->  prints `ask<TAB>line` (a question for the GM) or `offer<TAB>line`
(only offers: the filter's significance test, amendment 1) and exits 1 when the turn owes the filter; exits 0 otherwise.
"""

from __future__ import annotations

import json
import os
import re
import sys

FENCE = re.compile(r"```.*?```", re.S)
CODE = re.compile(r"`[^`\n]*`")
QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”')
ASK = re.compile(
    r"\b(should I|shall I|do you want|would you (like|prefer|rather)|want me to|which (one|of|would|do you)|your call"
    r"|or should (I|we)|do you agree|is that (ok|okay|right|what you)|can you confirm|let me know (whether|which)"
    r"|say (go|the word|yes)|for you to (decide|approve|choose|pick|confirm|rule)|approve or decline|ask (of )?you"
    r"|needs your (words|approval|decision|ruling|go-ahead|call|answer)|waiting (on|for) (you|your)"
    r"|yours to (decide|call|choose))\b",
    re.I,
)
# Amendment 1 (the GM, 2026-10-26): an OFFER - a decision already made, offered back - is not a question. It still owes
# the filter's SIGNIFICANCE test ("that offer should only be made if it crosses a certain threshold of significance").
OFFER = re.compile(
    r"\b(if you('d| would)? (want|like|prefer|rather)|let me know if|happy to|say so and I'll|easy to (revert|reverse|undo)"
    r"|I can (also |easily )?(revert|reverse|undo|switch|change|restore|raise|add|drop|re-?run|put (it|them) back))\b",
    re.I,
)
FILTER = "escalation-check"


def _lines(text: str):
    for line in FENCE.sub("", text or "").splitlines():
        s = line.strip()
        if not s.startswith(">"):
            yield QUOTED.sub("", CODE.sub("", s))


def classify(text: str) -> tuple[list[str], list[str]]:
    """(the lines that ASK the reader, the lines that only OFFER): an ask line wins over an offer on the same line."""
    ask, offer = [], []
    for s in _lines(text):
        if ASK.search(s):
            ask.append(s[:200])
        elif OFFER.search(s):
            offer.append(s[:200])
        elif s.endswith("?") and re.search(r"\b(you|your|I)\b", s):
            ask.append(s[:200])
    return ask, offer


def asks(text: str) -> list[str]:
    """Every line of the message that puts a question or decision to its reader."""
    return classify(text)[0]


def _records_backward(path: str, chunk: int = 1 << 20):
    """The transcript's JSON records, last first, read from the end (a main transcript runs to hundreds of MB)."""
    with open(path, "rb") as f:
        f.seek(0, 2)
        pos, tail = f.tell(), b""
        while pos > 0:
            step = min(chunk, pos)
            pos -= step
            f.seek(pos)
            lines = (f.read(step) + tail).split(b"\n")
            tail = lines.pop(0)
            for raw in reversed(lines):
                if raw.strip():
                    try:
                        yield json.loads(raw)
                    except Exception:
                        continue
        if tail.strip():
            try:
                yield json.loads(tail)
            except Exception:
                pass


def _is_gm_message(rec: dict) -> bool:
    if rec.get("type") != "user" or rec.get("isMeta"):
        return False
    c = (rec.get("message") or {}).get("content")
    if isinstance(c, str):
        return not c.startswith("<")  # a hook or command echo, not the GM's words
    return isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "text" for x in c)


def filtered_since_gm(path: str) -> bool:
    """Was `escalation-check` dispatched after the GM's last message?"""
    try:
        for rec in _records_backward(path):
            if _is_gm_message(rec):
                return False
            if rec.get("type") == "assistant":
                for x in (rec.get("message") or {}).get("content") or []:
                    if isinstance(x, dict) and x.get("type") == "tool_use" and x.get("name") in ("Agent", "Task"):
                        if (x.get("input") or {}).get("subagent_type") == FILTER:
                            return True
    except OSError:
        return True  # nothing to read: never refuse on a transcript the hook cannot see
    return False


def _gm_last_at(path: str) -> str:
    """The time of the GM's last message (ISO, to the second), '' when the transcript cannot be read."""
    try:
        for rec in _records_backward(path):
            if _is_gm_message(rec):
                return str(rec.get("timestamp") or "")[:19]
    except OSError:
        pass
    return ""


def kept_ids(clone: str) -> set[str]:
    """Every open question escalation-check kept, as `NNN#row` (feature 432)."""
    import glob  # noqa: PLC0415

    out = set()
    for f in glob.glob(f"{clone}/specs/*/gm-review.jsonl"):
        num = int(f.split("/specs/", 1)[1].split("-", 1)[0])
        with open(f, encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("kind") == "question" and r.get("status") == "kept" and "reviewed" not in r:
                    out.add(f"{num}#{i}")
    return out


def unnamed(clone: str, payload: dict) -> list[str]:
    """The kept questions since the GM's last message that the final message does not name (feature 432, FR-002)."""
    import glob  # noqa: PLC0415

    since = _gm_last_at(payload.get("transcript_path") or "")
    if not since:
        return []  # nothing to read: never refuse on a transcript the hook cannot see
    said = payload.get("last_assistant_message") or ""
    out = []
    for f in sorted(glob.glob(f"{clone}/specs/*/gm-review.jsonl")):
        num = int(f.split("/specs/", 1)[1].split("-", 1)[0])
        with open(f, encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                fresh = str(r.get("kept", ""))[:19] >= since
                if r.get("kind") == "question" and r.get("status") == "kept" and "reviewed" not in r and fresh and f"{num}#{i}" not in said:
                    out.append(f"{num}#{i}: {r.get('question', '')}")
    return out


def main() -> int:
    if sys.argv[1:2] == ["unnamed"] and len(sys.argv) == 3:
        try:
            payload = json.load(sys.stdin) or {}
        except Exception:
            return 0
        missing = unnamed(sys.argv[2], payload)
        print("\n".join(missing))
        return 1 if missing else 0
    if sys.argv[1:2] != ["judge"]:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin) or {}
    except Exception:
        return 0
    ask, offer = classify(payload.get("last_assistant_message") or "")
    # ...A QUESTION ESCALATION-CHECK ALREADY KEPT IS FILTERED (feature 432): naming one, as `unnamed` requires, is no new ask -
    # the two checks refused each other's message on the session that built them (2026-10-26)
    kept = kept_ids(payload.get("cwd") or os.getcwd())
    ask = [a for a in ask if not any(k in a for k in kept)]
    if not (ask or offer) or filtered_since_gm(payload.get("transcript_path") or ""):
        return 0
    print(f"ask\t{ask[0]}" if ask else f"offer\t{offer[0]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
