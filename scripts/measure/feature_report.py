#!/usr/bin/env python3
"""`make feature-report F=NNN` - where a feature's time and dispatches went, as a table, in seconds (feature 375, FR-009).

WHY (the GM, 2026-10-10): *"if at the end of every feature we literally had a table of how was spent running tests and how
much time was spent thinking and how much time was spent implementing and how much time was spent waiting for subagent
reviews and how much time was spent actually making the spec kit feature"* - and the post-mortem should take *"a second
with a make command"*, not a hand reading of a transcript. Every feature gets one, however small (FR-009), and no route
closes a feature without it (`scripts/gates/close_check.py`).

THE SOURCES (plan D8). The event log every clone's hooks write (`event_log.py`, `<git dir>/l7r-events/<feature>.jsonl`, read
from every clone under `/diagram/.clones/` and this one); a session transcript converted to the same events where the hooks
did not run (`TRANSCRIPT=`, for features before 375 and for 375 itself); `dev/run-log/` for the gates; the feature's own
commits (`git log --grep "Feature NNN"`) for its diff, its plan reviews and its spec rounds.

THE TIME (plan D8, D9). Per session, its events in order: from a PreToolUse to its PostToolUse is that tool's category; from a
PostToolUse (or a prompt, or a returned agent) to the next PreToolUse or Stop is THINKING - the model's own reading, judging
and writing - and it is WRITING THE SPEC when the call it leads to edits the feature's spec, plan or tasks; from a Stop to
what wakes the session is WAITING, on the subagent type whose return woke it, on a background run when the next event is a
tool call, and on the GM when it is a prompt. A gap past `IDLE_CAP_S` is the session left idle, counted apart.

    feature_report.py <NNN> [--transcript FILE ...] [--since ISO] [--until ISO] [--write] [--root DIR]
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import event_log as el  # noqa: E402

#: A gap longer than this is the session left alone (the GM away, a night), not work: counted apart, never as thinking.
IDLE_CAP_S = 3600
#: The check categories the cascade ratio counts (plan D8)
CHECK_CATS = ("record check", "claims check", "review check")
CLONES = Path("/diagram/.clones")
_SUBJECT = re.compile(r"/(?:l7r-check|[^/]+)/([^/]+?)(?:-(?:quote-check|record-format|source-reader|source-applicability|"
                      r"intro-check|translation-check|record-style|entry-drift|modal-[a-z]+))?/MANIFEST\.md$")


def parse_t(t: str) -> float:
    return datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()


def spec_dir(root: Path, feature: str) -> Path | None:
    hits = sorted((root / "specs").glob(f"{int(feature):03d}-*"))
    return hits[0] if hits else None


def event_logs(root: Path, name: str, clones: Path = CLONES) -> list[Path]:
    """Every clone's event log for the feature directory `name`, this clone's first."""
    seen: list[Path] = []
    for base in (root, *(sorted(clones.glob("*")) if clones.is_dir() else ())):
        p = el.common_git_dir(base) / el.EVENTS_DIR / f"{name}.jsonl" if (base / ".git").exists() else None
        if p is not None and p.is_file() and p.resolve() not in {q.resolve() for q in seen}:
            seen.append(p)
    return seen


def load_events(logs: Iterable[Path], transcripts: Iterable[Path], since: str = "", until: str = "") -> list[dict[str, Any]]:
    """The events of every source, deduplicated, in time order, inside [since, until]."""
    out: dict[tuple[Any, ...], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for p in logs:
        rows.extend(el.read_jsonl(p))
    for p in transcripts:
        rows.extend(el.from_transcript(el.read_jsonl(p)))
    for e in rows:
        t = str(e.get("t") or "")
        if not t or (since and t < since) or (until and t > until):
            continue
        out.setdefault((e.get("sid"), e.get("ev"), e.get("id"), e.get("aid"), t), e)
    return sorted(out.values(), key=lambda e: e["t"])


def _spec_edit(e: Mapping[str, Any], name: str) -> bool:
    return e.get("cat") == "edit" and f"specs/{name}/" in str(e.get("path") or "")


def split_time(events: Sequence[Mapping[str, Any]], name: str) -> Counter[str]:
    """Seconds per category over every session (module docstring, THE TIME)."""
    out: Counter[str] = Counter()
    by_sid: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for e in events:
        by_sid[str(e.get("sid"))].append(e)
    for evs in by_sid.values():
        open_calls: dict[str, Mapping[str, Any]] = {}
        for a, b in zip(evs, evs[1:], strict=False):
            gap = parse_t(b["t"]) - parse_t(a["t"])
            if gap <= 0:
                continue
            if gap > IDLE_CAP_S:
                out["idle (over an hour)"] += gap
                continue
            if a["ev"] == "PreToolUse":
                open_calls[str(a.get("id"))] = a
            if a["ev"] == "PreToolUse" and b["ev"] == "PostToolUse" and b.get("id") == a.get("id"):
                out[_tool_cat(a)] += gap
            elif a["ev"] == "Stop":
                out[_waiting(b)] += gap
            elif a["ev"] == "PreToolUse":
                out[_tool_cat(a)] += gap  # a tool still running when another event arrives (a hook's own record)
            elif b["ev"] in ("PreToolUse", "Stop"):
                out["writing the spec" if _spec_edit(b, name) else "thinking"] += gap
            else:
                out["thinking"] += gap
    return out


def _tool_cat(e: Mapping[str, Any]) -> str:
    cat = str(e.get("cat") or "other tool")
    return f"dispatching: {cat}" if e.get("tool") == "Agent" else cat


def _waiting(nxt: Mapping[str, Any]) -> str:
    if nxt["ev"] == "SubagentStop":
        return f"waiting: {nxt.get('agent') or 'subagent'}"
    if nxt["ev"] == "UserPromptSubmit":
        return "waiting: the GM"
    return "waiting: a background run"


def tool_detail(events: Sequence[Mapping[str, Any]]) -> Counter[str]:
    """Seconds of each `other tool` call by its make target (`make map`) or tool name - what the coarse category hides."""
    out: Counter[str] = Counter()
    start: dict[str, Mapping[str, Any]] = {}
    for e in events:
        if e["ev"] == "PreToolUse" and e.get("cat") == "other tool":
            start[str(e.get("id"))] = e
        elif e["ev"] == "PostToolUse" and str(e.get("id")) in start:
            a = start.pop(str(e.get("id")))
            gap = parse_t(e["t"]) - parse_t(a["t"])
            if 0 < gap <= IDLE_CAP_S:
                out[f"make {a['make']}" if a.get("make") else str(a.get("tool"))] += gap
    return out


def subject(manifest: str) -> str:
    """The checked thing a MANIFEST path names - `0105` for `/tmp/l7r-check/0105-quote-check/MANIFEST.md`."""
    m = _SUBJECT.search(manifest)
    return m.group(1) if m else Path(manifest).parent.name


def verdicts(events: Sequence[Mapping[str, Any]]) -> dict[str, Counter[str]]:
    """Each agent type's returns by verdict (`event_log.verdict_of`): BLOCKED plan reviews, clean check runs."""
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for e in events:
        if e["ev"] == "SubagentStop" and e.get("verdict"):
            out[str(e.get("agent"))][str(e["verdict"])] += 1
    return out


def dispatches(events: Sequence[Mapping[str, Any]]) -> tuple[Counter[str], Counter[tuple[str, str]]]:
    """(dispatches per agent type, rounds per (check, subject)) - a dispatch is an Agent call's PreToolUse."""
    by_type: Counter[str] = Counter()
    rounds: Counter[tuple[str, str]] = Counter()
    for e in events:
        if e["ev"] == "PreToolUse" and e.get("tool") == "Agent":
            by_type[str(e.get("agent"))] += 1
            if e.get("manifest"):
                rounds[(str(e.get("agent")), subject(str(e["manifest"])))] += 1
    return by_type, rounds


def reversals(events: Sequence[Mapping[str, Any]]) -> list[tuple[str, str]]:
    """(path, time) of every Edit that put back a passage an earlier Edit of the same file had replaced (A -> B -> A)."""
    out = []
    replaced: dict[str, set[str]] = defaultdict(set)
    for e in events:
        if e["ev"] != "PreToolUse" or e.get("tool") != "Edit" or not e.get("old"):
            continue
        path = str(e.get("path"))
        if e.get("new") in replaced[path]:
            out.append((path, str(e["t"])))
        replaced[path].add(str(e["old"]))
    return out


def _git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else ""


def utc(iso: str) -> str:
    """An ISO time with any offset as UTC `YYYY-MM-DDTHH:MM:SSZ`, comparable with the events' `t`."""
    dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(datetime.UTC)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def commits(root: Path, feature: str, since: str = "", until: str = "") -> list[tuple[str, str, str]]:
    """(sha, UTC time, subject) of every commit whose message names the feature (`Feature 375`, `375 T04`), in [since, until]."""
    fmt = "%H\x1f%aI\x1f%s"
    out = []
    for raw in _git(root, "log", "--all", "-E", f"--grep=(Feature|feature) {int(feature)}\\b|^{int(feature)} ", f"--format={fmt}").splitlines():
        sha, t, subj = raw.split("\x1f", 2)
        t = utc(t)
        if (since and t < since[:19]) or (until and t > until[:19] + "Z"):
            continue
        out.append((sha, t, subj))
    return out


#: What a session does not write by hand - a regenerated sheet, an index, a ledger, a ranking rebuilt by a script - and the
#: specs' own bookkeeping are not "the feature's own diff" (FR-009's cascade ratio): measured on 372's waves 106-111, 4,252
#: lines of `dev/claims-index.json` and 5,057 of a regenerated `ranking.md` would have made 96 dispatches look like 0.02 a line.
GENERATED = re.compile(r"\.(svg|json|jsonl|png|webp)$|^specs/|^dev/(run-log|perf-log|bypass-log|idle-log)/|^pool/.*\.notes\.md$")


def diff_lines(root: Path, shas: Iterable[str]) -> int:
    """Lines added and removed by the feature's commits in hand-written files outside `specs/` (the cascade ratio's base,
    plan D8)."""
    total = 0
    for sha in shas:
        for raw in _git(root, "show", "--numstat", "--format=", sha).splitlines():
            parts = raw.split("\t")
            if len(parts) == 3 and parts[0].isdigit() and not GENERATED.search(parts[2]):
                total += int(parts[0]) + int(parts[1])
    return total


def gates(root: Path, shas: set[str], since: str, until: str) -> Counter[str]:
    """Gate runs at one of the feature's commits, inside its window, by result (`dev/run-log/`)."""
    out: Counter[str] = Counter()
    for p in sorted((root / "dev" / "run-log").rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        utc = str(d.get("utc") or "")
        if d.get("target") != "done" or (since and utc < since[:19]) or (until and utc > until[:19] + "Z"):
            continue
        if any(s.startswith(str(d.get("commit") or "-")) for s in shas):
            res = str(d.get("result") or "")
            out["red" if res.startswith("failed") else res] += 1
    return out


def spec_rounds(text: str) -> Counter[str]:
    """The spec's Review history, by verdict."""
    out: Counter[str] = Counter()
    for line in text.splitlines():
        m = re.match(r"\s*-\s*Round \d+ \(.*?\):\s*([A-Z][A-Z -]+?)\s+-", line)
        if m:
            out[m.group(1).strip()] += 1
    return out


def plan_blocks(root: Path, name: str, shas: set[str]) -> int:
    """How many recorded plan reviews were BLOCKED - every version of `plan-review.json` the feature's commits wrote."""
    n = 0
    for sha in [s for s in _git(root, "log", "--format=%H", "--", f"specs/{name}/plan-review.json").split() if s in shas]:
        if '"verdict": "BLOCKED"' in _git(root, "show", f"{sha}:specs/{name}/plan-review.json"):
            n += 1
    return n


def tasks_done(d: Path) -> tuple[int, int]:
    text = (d / "tasks.md").read_text(encoding="utf-8") if (d / "tasks.md").is_file() else ""
    return len(re.findall(r"^- \[[xX]\]", text, re.M)), len(re.findall(r"^- \[[ xX]\]", text, re.M))


def _hm(s: float) -> str:
    m = round(s / 60)
    return f"{m // 60} h {m % 60:02d} min" if m >= 60 else f"{m} min"


def report(root: Path, feature: str, transcripts: Sequence[Path] = (), since: str = "", until: str = "",
           clones: Path = CLONES) -> str:
    t0 = time.monotonic()
    d = spec_dir(root, feature)
    if d is None:
        raise SystemExit(f"feature-report: no specs/{feature}-* directory")
    name = d.name
    events = load_events(event_logs(root, name, clones), transcripts, since, until)
    span = (events[0]["t"], events[-1]["t"]) if events else ("", "")
    cs = commits(root, feature, since, until)
    shas = {c[0] for c in cs}
    split = split_time(events, name)
    by_type, rounds = dispatches(events)
    checks = sum(n for e_type, n in by_type.items() if el.agent_category(e_type) in CHECK_CATS)
    lines = diff_lines(root, shas)
    g = gates(root, shas, since or span[0], until or span[1])
    done, total = tasks_done(d)
    spec_text = (d / "spec.md").read_text(encoding="utf-8") if (d / "spec.md").is_file() else ""
    out = [f"# Feature report - {name}", "",
           f"Written by `make feature-report F={feature}` from {len(events)} events"
           + (f" ({span[0][:16]} to {span[1][:16]} UTC)" if events else " (no event log and no transcript: the time table is empty)")
           + f", {len(cs)} commits, the run log and the spec.", ""]
    out += ["## Where the time went", "", "| category | time | share |", "|---|---|---|"]
    whole = sum(v for k, v in split.items() if not k.startswith("idle")) or 1
    for k, v in sorted(split.items(), key=lambda kv: -kv[1]):
        share = "-" if k.startswith("idle") else f"{100 * v / whole:.0f}%"
        out.append(f"| {k} | {_hm(v)} | {share} |")
    detail = tool_detail(events)
    if detail:
        out += ["", "## Inside `other tool` (the five largest)", "", "| tool or make target | time |", "|---|---|"]
        out += [f"| {k} | {_hm(v)} |" for k, v in detail.most_common(5)]
    vs = verdicts(events)
    out += ["", "## Dispatches", "", "| agent | dispatches | returned, by verdict |", "|---|---|---|"]
    out += [f"| {k} | {v} | {', '.join(f'{w} {n}' for w, n in sorted(vs.get(k, {}).items())) or '-'} |"
            for k, v in sorted(by_type.items(), key=lambda kv: (-kv[1], kv[0]))]
    out += ["", "## Rounds per checked thing (two or more)", "", "| check | subject | rounds |", "|---|---|---|"]
    out += [f"| {c} | {s} | {n} |" for (c, s), n in sorted(rounds.items(), key=lambda kv: (-kv[1], kv[0])) if n >= 2] or ["| - | - | - |"]
    rv = reversals(events)
    out += ["", "## Process signals", "",
            f"- gates: {', '.join(f'{k} {v}' for k, v in sorted(g.items())) or 'none recorded'}",
            f"- spec rounds: {', '.join(f'{k} {v}' for k, v in sorted(spec_rounds(spec_text).items())) or 'none recorded'}",
            f"- plan reviews BLOCKED: {plan_blocks(root, name, shas)} recorded in commits, {vs.get('spec-fidelity', {}).get('BLOCKED', 0)} returned",
            f"- reversals (A -> B -> A): {len(rv)}" + (" - " + "; ".join(f"{Path(p).name} {t[11:16]}" for p, t in rv[:8]) if rv else ""),
            f"- check dispatches {checks} over {lines} changed lines: cascade ratio {checks / lines if lines else 0:.2f}",
            f"- tasks ticked: {done} of {total}", ""]
    out += [f"This report took {time.monotonic() - t0:.1f} s to build; its own runs are the `make feature-report` rows of the "
            "event log (category `other tool`).", ""]
    return "\n".join(out)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("feature")
    ap.add_argument("--transcript", action="append", default=[])
    ap.add_argument("--since", default="")
    ap.add_argument("--until", default="")
    ap.add_argument("--write", action="store_true", help="write specs/NNN-*/report.md as well as printing it")
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    text = report(root, a.feature, [Path(p) for p in a.transcript], a.since, a.until)
    sys.stdout.write(text)
    if a.write:
        d = spec_dir(root, a.feature)
        assert d is not None
        (d / "report.md").write_text(text, encoding="utf-8")
        sys.stdout.write(f"\nfeature-report: written to {d.relative_to(root)}/report.md\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
