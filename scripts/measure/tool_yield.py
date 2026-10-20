#!/usr/bin/env python3
"""`make tool-yield` - every tool of the project, how often it is used and how often it changes the outcome (feature 406 T04).

WHY (the GM 2026-10-19): "Whether or not it's doing something for us should be a measurable question", for "basically ... every
tool" - "how often a tool is used ... Or how often it makes a difference" - and where a tool is "too new to have gathered
measurements, then that's fine". `make fix-yield` (385 T119) read a command rate per hour, which rises when a fix is used.

THE TOOLS, LISTED FROM THE CODE (D163), never from what has fired, so a tool that never fired reads 0:
  guard   - every hook wired in `.claude/settings.json` and every name the guard log carries
  check   - every refusing check: a `.py` with a `__main__` or a `.sh` under `scripts/gates/`, and every `scripts/...` path the
            entry points name (the Makefile recipes of `done`, `quick` and `tick`; `sync-with-main.sh`, `push_checks.py`,
            `preflight.py`), read from them at run time
  target  - every target the Makefile defines
  review  - every `.claude/agents/` type
  step    - every automatic step in `scripts/tool-registry.json`

THE RECORDS: the guard log (`~/.claude/guard-log/*.json`), every clone's event logs (`.git/l7r-events/*.jsonl`) and usage log
(`.git/tool-usage.jsonl`), the review ledger (`dev/review-ledger.md`) and the bypass log (`dev/bypass-log/`). The transcripts
(17 GB) are not read.

PER KIND (FR-001): interventions and likely misfires -
  guard   - blocked, refused, rewrote, reminded, warned / escaped
  check   - refused / "no outcome record" (a check records no escape of its own; its escapes are its caller's)
  target  - runs that failed (a `PostToolUseFailure` line, or before that a PreToolUse with no PostToolUse) / escapes the bypass
            log records for it; a run no session made has no outcome record, counted apart
  review  - passes whose verdict carried a finding / rows declined or MISSED-BY-REVIEWER; a check with no ledger rows reads its
            dispatches and "no outcome record"
  step    - runs that changed something / "no outcome record" (no step records an undo)
A tool first seen under 7 days ago reads "too new"; an older one reports its numbers, however small.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import json
import re
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOO_NEW_DAYS = 7  # the spec's "too new": first seen under 7 days ago (FR-001)
GUARD_HIT = {"blocked", "refused", "rewrote", "reminded", "warned", "blocked-cadence"}
GUARD_MISS = {"escaped"}
#: a pass with a finding: a verdict word, a bare "findings" (not "0 findings"), or a count above 0 of a finding kind (measured
#: 2026-10-19 on the ledger: "findings" is the commonest verdict; "TRUTH 1", "1 FIX, 1 NOTE", "1 VOCABULARY" its counted forms)
FINDING = re.compile(
    r"BLOCK|CHANGES|DRIFT|MISLABEL|NEEDS|TOUCHES|change-route|process-fault|FAIL|CONTRADICT|NOT-FOUND|DIFFERS"
    r"|(?<![0-9] )\bfindings\b|\b[1-9]\d* (?:FIX|VOCABULARY|HISTORY|SESSION|DRIFTED|MISLABELED|findings?|unfootnoted)"
    r"|\b(?:TRUTH|COVERAGE|LINKS) [1-9]",
    re.I,
)
ENTRY_SCRIPTS = ("scripts/sync-with-main.sh", "scripts/gates/push_checks.py", "scripts/gates/preflight.py")
ENTRY_TARGETS = ("done", "quick", "tick")
UNSEEN = (
    "the outcome of a target run no session made (a recipe, a script, the timer) - its run is counted, its outcome is not",
    "an automatic step written later that calls neither the helper nor guard_log - FR-004's check reads files, not steps",
)


def utc(text: str) -> float:
    """Seconds since the epoch of an ISO time (`...Z` or with an offset); 0.0 when unreadable."""
    try:
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError, AttributeError:
        return 0.0


@dataclass
class Tally:
    """One tool's numbers."""

    kind: str
    name: str
    first: float = 0.0
    uses: list[float] = field(default_factory=list)
    hits: int = 0
    misses: int = 0
    unseen: int = 0  # target runs with no outcome record
    outcome_record: bool = True

    def use(self, t: float) -> None:
        self.uses.append(t)
        self.first = min(self.first, t) if self.first else t


# ---- the inventory, from the code -------------------------------------------------------------------------------------------------


def hook_guards(root: Path) -> set[str]:
    """The guard names of the hooks wired in `.claude/settings.json` (`<name>-hooks.sh` -> `<name>`)."""
    settings = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))
    names = set()
    for blocks in settings.get("hooks", {}).values():
        for block in blocks:
            for hook in block.get("hooks", []):
                names |= set(re.findall(r"scripts/hooks/([\w-]+)-hooks\.sh", hook.get("command", "")))
    return names


def targets(root: Path) -> set[str]:
    """Every target the Makefile defines."""
    text = (root / "Makefile").read_text(encoding="utf-8")
    return {m.group(1) for m in re.finditer(r"^([a-z][\w-]*)\s*:(?!=)", text, re.M)}


def recipe(text: str, target: str) -> str:
    """A target's recipe: its rule line and the tab-led lines after it."""
    m = re.search(rf"^{re.escape(target)}\s*:(?!=).*\n((?:\t.*\n|##.*\n)*)", text, re.M)
    return m.group(0) if m else ""


def reached(make: str) -> set[str]:
    """The entry targets and every target their recipes reach - each prerequisite and each `$(MAKE) <target>` followed to its
    own recipe (measured 2026-10-19: done, quick and tick reach 6 targets)."""
    seen: set[str] = set()
    todo = list(ENTRY_TARGETS)
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        text = recipe(make, name)
        head = re.match(rf"^{re.escape(name)}\s*:(?!=)([^\n#]*)", text)
        deps = head.group(1).split() if head else []
        subs = re.findall(r"\$\(MAKE\)[^\n;&|]*?\s([a-z][\w-]+)(?=\s|$|;)", text)
        todo += [d for d in deps + subs if re.fullmatch(r"[a-z][\w-]+", d)]
    return seen


def checks(root: Path) -> set[str]:
    """Every refusing check: the commands under `scripts/gates/`, and every `scripts/` script the entry points name."""
    out = {p.stem for p in (root / "scripts" / "gates").glob("*.py") if '__name__ == "__main__"' in p.read_text(encoding="utf-8")}
    out |= {p.stem for p in (root / "scripts" / "gates").glob("*.sh")}
    make = (root / "Makefile").read_text(encoding="utf-8")
    texts = [recipe(make, t) for t in reached(make)] + [(root / s).read_text(encoding="utf-8") for s in ENTRY_SCRIPTS if (root / s).is_file()]
    for text in texts:
        for path in re.findall(r"scripts/[\w./-]+\.(?:py|sh)", text):
            if "/hooks/" not in path and (root / path).is_file():
                out.add(Path(path).stem)
    return out


def reviews(root: Path) -> set[str]:
    return {p.stem for p in (root / ".claude" / "agents").glob("*.md")}


def registry(root: Path) -> dict[str, dict]:
    path = root / "scripts" / "tool-registry.json"
    return json.loads(path.read_text(encoding="utf-8")).get("tools", {}) if path.is_file() else {}


# ---- the records -------------------------------------------------------------------------------------------------------------------


def git_dirs(root: Path) -> list[Path]:
    """Every clone's git dir beside the mirror's, where the event and usage logs live."""
    base = root if root.parent.name != ".clones" else root.parent.parent
    dirs = [base / ".git"] + [Path(p) for p in glob.glob(str(base / ".clones" / "*" / ".git"))]
    return [d for d in dirs if d.is_dir()]


def jsonl(path: Path) -> Iterable[dict]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            yield row


def guard_rows(guard_log: Path) -> Iterable[dict]:
    for path in guard_log.glob("*.json"):
        try:
            row = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except OSError, ValueError:
            continue
        if isinstance(row, dict):
            yield row


def ledger_rows(root: Path) -> Iterable[tuple[str, str, str, str, str]]:
    """(date, check, verdict, class/missed cell, acted on) of the ledger's measured table."""
    path = root / "dev" / "review-ledger.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    start = text.find("| date | check | subject | verdict |")
    for line in text[start:].splitlines()[2:] if start >= 0 else []:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 8 and re.match(r"\d{4}-\d\d-\d\d", cells[0]):
            yield cells[0], cells[1], cells[3], cells[5] + " " + cells[6], cells[7]


# ---- the tally ---------------------------------------------------------------------------------------------------------------------


def tally_guards(t: dict[tuple[str, str], Tally], rows: Iterable[dict]) -> None:
    for row in rows:
        g = str(row.get("guard") or "?")
        tool = t.setdefault(("guard", g), Tally("guard", g))
        tool.use(utc(str(row.get("utc") or "")))
        event = str(row.get("event") or "")
        tool.hits += event in GUARD_HIT
        tool.misses += event in GUARD_MISS


def tally_usage(t: dict[tuple[str, str], Tally], rows: Iterable[dict]) -> float:
    """The usage log's runs; returns when it began (the target counts before it come from the event logs)."""
    began = 0.0
    for row in rows:
        when = utc(str(row.get("utc") or ""))
        began = min(began, when) if began else when
        kind = str(row.get("kind") or "step")
        kind = {"hook": "guard"}.get(kind, kind)
        tool = t.setdefault((kind, str(row.get("tool"))), Tally(kind, str(row.get("tool"))))
        tool.use(when)
        tool.hits += row.get("outcome") in ("refused", "changed", "failed")
    return began


def tally_events(t: dict[tuple[str, str], Tally], rows: Iterable[dict], usage_began: float) -> None:
    """Targets: runs before the usage log began, and every session run's outcome; reviews: dispatches."""
    pre: dict[str, tuple[str, float]] = {}
    post: set[str] = set()
    failed: set[str] = set()
    for row in rows:
        ev, when = row.get("ev"), utc(str(row.get("t") or ""))
        if row.get("make"):
            if ev == "PreToolUse":
                pre[str(row.get("id"))] = (str(row["make"]), when)
            elif ev == "PostToolUse":
                post.add(str(row.get("id")))
            elif ev == "PostToolUseFailure":
                failed.add(str(row.get("id")))
        elif ev == "SubagentStart" and row.get("agent"):
            tool = t.setdefault(("review", str(row["agent"])), Tally("review", str(row["agent"])))
            tool.use(when)
    for tid, (name, when) in pre.items():
        tool = t.setdefault(("target", name), Tally("target", name))
        if not usage_began or when < usage_began:
            tool.use(when)
        if tid in failed or (tid not in post and tid not in failed):
            tool.hits += 1
    if usage_began:  # a run the usage log counts that no session's event matches has no outcome record
        seen = collections.Counter(name for name, when in pre.values() if when >= usage_began)
        for (kind, name), tool in t.items():
            if kind == "target":
                tool.unseen = max(0, sum(1 for u in tool.uses if u >= usage_began) - seen[name])


def tally_ledger(t: dict[tuple[str, str], Tally], rows: Iterable[tuple[str, str, str, str, str]]) -> set[str]:
    """Reviews' findings and misfires; returns the checks the ledger holds rows for."""
    held = set()
    for date, check, verdict, missed, acted in rows:
        tool = t.setdefault(("review", check), Tally("review", check))
        held.add(check)
        when = utc(date + "T00:00:00Z")
        if tool.uses and when < tool.first - 86400:
            continue  # before its dispatches are recorded: findings and uses cover the same span
        if not tool.uses:
            tool.first = min(tool.first, when) if tool.first else when
        tool.hits += bool(FINDING.search(verdict))
        tool.misses += "declined" in acted.lower() or "MISSED-BY-REVIEWER" in missed
    return held


def tally_arbiter(t: dict[tuple[str, str], Tally], root: Path) -> bool:
    """The round arbiter's outcomes, from every feature's `arbiter.jsonl` (it keeps no ledger rows): a ruling that changed the
    route, found a process fault or named a tooling fix is its intervention. Returns whether any ruling was read."""
    tool = t.setdefault(("review", "round-arbiter"), Tally("review", "round-arbiter"))
    read = False
    for path in (root / "specs").glob("*/arbiter.jsonl"):
        for row in jsonl(path):
            if row.get("ruling"):
                read = True
                if tool.uses and utc(str(row.get("utc") or "")) < tool.first - 86400:
                    continue
                tool.hits += row.get("ruling") in ("change-route", "process-fault") or bool(row.get("tooling_fix"))
    return read


def tally_bypass(t: dict[tuple[str, str], Tally], root: Path) -> None:
    """A target's rule escaped through its bypass route (the bypass log) - counted only from when its use record begins, so
    the misfires and the uses cover the same span (the bypass log reaches back before the event log)."""
    for path in (root / "dev" / "bypass-log").glob("*/*.json"):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            name = str(row.get("target") or "").split()[0]
        except OSError, ValueError, IndexError:
            continue
        tool = t.get(("target", name))
        if tool is not None and tool.first and utc(str(row.get("utc") or "")) >= tool.first:
            tool.misses += 1


def collect(root: Path = ROOT, guard_log: Path | None = None) -> dict[tuple[str, str], Tally]:
    """Every tool, listed from the code, with its numbers from the records."""
    t: dict[tuple[str, str], Tally] = {}
    for name in hook_guards(root):
        t[("guard", name)] = Tally("guard", name)
    for name in checks(root):
        t[("check", name)] = Tally("check", name)
    for name in targets(root):
        t[("target", name)] = Tally("target", name)
    for name in reviews(root):
        t[("review", name)] = Tally("review", name)
    for name, entry in registry(root).items():
        kind = {"hook": "guard"}.get(entry.get("kind", "step"), entry.get("kind", "step"))
        t.setdefault((kind, name), Tally(kind, name))
    tally_guards(t, guard_rows(guard_log or Path.home() / ".claude" / "guard-log"))
    dirs = git_dirs(root)
    began = tally_usage(t, (row for d in dirs for row in jsonl(d / "tool-usage.jsonl")))
    tally_events(t, (row for d in dirs for p in sorted((d / "l7r-events").glob("*.jsonl")) for row in jsonl(p)), began)
    held = tally_ledger(t, ledger_rows(root))
    if tally_arbiter(t, root):
        held.add("round-arbiter")
    tally_bypass(t, root)
    for (kind, name), tool in t.items():
        if kind in ("check", "step") and not tool.hits and not tool.uses:
            tool.outcome_record = False
        if kind == "review" and name not in held:
            tool.outcome_record = False
    return t


# ---- the report --------------------------------------------------------------------------------------------------------------------


def row(tool: Tally, now: float) -> list[str]:
    week = sum(1 for u in tool.uses if u >= now - 7 * 86400)
    first = dt.datetime.fromtimestamp(tool.first, dt.UTC).strftime("%Y-%m-%d") if tool.first else "-"
    if tool.first and now - tool.first < TOO_NEW_DAYS * 86400:
        note = "too new"
    elif not tool.outcome_record:
        note = "no outcome record"
    else:
        note = f"{tool.unseen} run(s) with no outcome record" if tool.unseen else ""
    misses = "no outcome record" if tool.kind in ("check", "step") else str(tool.misses)
    return [tool.kind, tool.name, first, str(week), str(len(tool.uses)), str(tool.hits), misses, note]


def table(t: Mapping[tuple[str, str], Tally], kind: str = "", now: float | None = None) -> str:
    now = now if now is not None else dt.datetime.now(dt.UTC).timestamp()
    lines = ["| kind | tool | first seen | uses (7 d) | uses (all) | interventions | likely misfires | note |", "|---|---|---|---|---|---|---|---|"]
    for key in sorted(t, key=lambda k: (k[0], -len(t[k].uses), k[1])):
        if not kind or key[0] == kind:
            lines.append("| " + " | ".join(row(t[key], now)) + " |")
    lines += ["", "What this report still cannot see:"] + [f"- {u}" for u in UNSEEN]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--kind", default="", choices=("", "guard", "check", "target", "review", "step"))
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    print(table(collect(Path(a.root)), a.kind), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
