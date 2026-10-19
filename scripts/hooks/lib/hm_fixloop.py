#!/usr/bin/env python3
"""A quote-check fix that keeps failing goes to the round arbiter (feature 399, kind B).

WHY (the GM, 2026-10-19, dictated): *"it sounds like we need a kind-B tweak, where if a fix keeps failed then that should be a
loop the arbitur should judge"* (failing, arbiter). Quote-check ran six passes on question 0251 in feature 390 and the round cap
(`hm_checks.ROUND_CAP`) never fired: the per-question counter leaves a dispatch uncounted when its unread sentences are not the
check's own EDIT text (`first_look` - a hand fix of its own PARTIAL is exactly that) or when `origin/main` moved since the last
counted round (`new_cause` - any landing by any session). Modal checks rely on both (feature 374 batches 9 and 11), so this
sits BESIDE the counter rather than rewriting it, and counts per FOOTNOTE, which neither reset touches.

THE COUNT, `state["flags"]["<stem>#<key>"] = {n, fp, lines}`: at a quote-check reply's return, each footnote of its bundle named
on a line carrying a verdict other than a pass (NOT-READABLE, DIFFERS, NOT-ON-PAGE, PARTIAL, DOES-NOT-SUPPORT) is FLAGGED. A
flag at a fingerprint other than its last flag's is a failed fix (n + 1); at the same fingerprint nothing was tried, and n
stays (a canon note reads NOT-READABLE every round - FR-006). A footnote named on no flagged line passed: its count goes.
Tables are read too (a reply may give its verdicts in one); its counts line and its OUTSIDE THE CHANGE section are not.

THE HOLD: a quote-check bundle carrying a footnote at n >= 2, changed again since its last flag, trips the unit's round
trigger `round:quote-check|q:NNNN@M` (M past every round number the unit's rulings and owed triggers use) and is refused
until the arbiter rules. `continue` lets one more round through, as the cap's own `continue` does (n drops to 1); `accept` and
`process-fault` leave the unit to the closure rule the cap already applies (`hm_arbiter.closed`).
"""

from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from pathlib import Path
from typing import Any

import hm_arbiter

#: a footnote is held at its third round after two failed fixes, as the round cap holds a page at its third round
HOLD_AT = 2
FLAG = re.compile(r"(?<!\d )\b(?:NOT-READABLE|DIFFERS|NOT-ON-PAGE|PARTIAL|DOES-NOT-SUPPORT)\b")
_OUTSIDE = re.compile(r"^#*\s*\**OUTSIDE THE CHANGE\**\s*:?\s*$", re.M)
_NOTE_UNIT = re.compile(r"^unit: quote-check:(\S+#\S+) (\S+)$", re.M)


def notes_of(manifest: str) -> dict[str, str]:
    """{`<stem>#<key>`: fingerprint} of the quote-check footnotes a bundle carries (its `unit:` lines)."""
    return {n: fp for n, fp in _NOTE_UNIT.findall(manifest) if not n.endswith("#unfootnoted")}


def read_reply(reply: str, notes: Collection[str]) -> tuple[dict[str, str], set[str]]:
    """({flagged footnote: its first flagged line}, the footnotes named and never flagged). A key is matched whole, so `deed`
    is not read inside `deed-4`; a line naming no footnote of the bundle flags nothing - the count never guesses."""
    m = _OUTSIDE.search(reply)
    lines = (reply[: m.start()] if m else reply).splitlines()
    start = next((i + 1 for i, ln in enumerate(lines) if ln.strip()), len(lines))  # past the counts line
    keys = {n: re.compile(rf"(?<![\w-]){re.escape(n.partition('#')[2])}(?![\w-])") for n in notes}
    flagged: dict[str, str] = {}
    named: set[str] = set()
    for ln in lines[start:]:
        hits = {n for n, k in keys.items() if k.search(ln)}
        named |= hits
        if hits and FLAG.search(ln):
            for n in hits:
                flagged.setdefault(n, " ".join(ln.split())[:200])
    return flagged, named - set(flagged)


def returned(state: dict[str, Any], d: Mapping[str, Any], reply: str) -> None:
    """Count a returned quote-check reading's flags, once (the caller's `rounded` guard)."""
    notes = d.get("quote_notes") or {}
    if d.get("check") != "quote-check" or not notes or not reply.strip():
        return
    flagged, passed = read_reply(reply, notes)
    fl = state.setdefault("flags", {})
    for n, line in flagged.items():
        prev = fl.get(n) or {}
        if not prev.get("n"):
            fl[n] = {"n": 1, "fp": notes[n], "lines": [line]}
        elif prev.get("fp") != notes[n]:
            fl[n] = {"n": prev["n"] + 1, "fp": notes[n], "lines": [*prev.get("lines", []), line][-2:]}
        else:
            prev["lines"] = [*prev.get("lines", [])[:-1], line]  # flagged again with nothing tried: no failed fix
    for n in passed:
        fl.pop(n, None)


def _next_round(root: Path, unit: str, counted: int) -> int:
    prefix = f"round:{unit}@"
    used = [hm_arbiter._round_no(t) for t in [*hm_arbiter.rulings(root), *hm_arbiter.owed(root)] if t.startswith(prefix)]
    return max([HOLD_AT, counted, *used]) + 1


def hold(state: dict[str, Any], root: Path, check: str, manifest: str, now: float) -> str:
    """The refusal for a quote-check bundle carrying a footnote whose fix keeps failing, or ''."""
    if check != "quote-check":
        return ""
    fl, trips = state.get("flags", {}), state.setdefault("flag_trips", {})
    rul = hm_arbiter.rulings(root)
    for n, fp in sorted(notes_of(manifest).items()):
        f, t = fl.get(n), trips.get(n)
        if t and t in rul:  # ruled: `continue` lets one more round through; accept / process-fault go to the closure rule
            trips.pop(n)
            if f:
                f["n"] = 1 if rul[t].get("ruling") == "continue" else 0
            continue
        if not f or f.get("n", 0) < HOLD_AT or fp == f.get("fp"):
            continue
        if t:
            return hm_arbiter.refusal([t], root)
        unit = f"quote-check|q:{n.split('#', 1)[0].split('.', 1)[0]}"
        trig = f"round:{unit}@{_next_round(root, unit, state.get('rounds', {}).get(unit, 0))}"
        detail = f"footnote {n} flagged by quote-check in {f['n']} rounds in a row, changed between them (feature 399): " + " | ".join(f.get("lines", []))
        hm_arbiter.trip(root, trig, "round", unit, detail, now)
        trips[n] = trig
        return hm_arbiter.refusal([trig], root)
    return ""
