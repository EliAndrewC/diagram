#!/usr/bin/env python3
"""Where one session's tokens went, per piece of work: the main session, each named agent, the ad-hoc ones.

WHY THIS EXISTS. The GM asked on 2026-09-21, before feature 250's pipeline runs at scale, whether
splitting the record into per-entry files (features 258, 259) made the research checks cheap enough:
"how many tokens are eaten up by the main session, how many by each named subagent, how many by the
ad hoc subagents". `scripts/_agent_census.py` answers per agent type over EVERY session and never
counts the main session; this reads ONE session and cuts it into the windows `mark` opened, so a
task's cost is the main session's turns inside its window plus the agents that started inside it.

It also lists what each agent READ, largest first, because the hypothesis under test is structural:
a check that opens a small fragment is cheap, and one that still opens an assembled page is not.

Usage is folded per message id as the per-field maximum, for the reason `_agent_census.py` records
(one transcript record per content block, each repeating the message's usage as it then stood).

    tokens.py mark "T03 sizing source-reader"     open a window (closes the one before it)
    tokens.py report [--json out.json]            the table
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from _agent_census import BUILTIN, FIELDS, usage_of  # noqa: E402

MARKS = HERE / "marks.json"
SESSION = pathlib.Path.home() / ".claude/projects/-diagram/e34913cb-bb99-485e-9f5d-ecbd754898cd.jsonl"


def records(path: pathlib.Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def messages(recs: list[dict]) -> list[dict]:
    """One row per assistant message: its first timestamp, its model, its usage folded as the maximum."""
    per: dict[str, dict] = {}
    for rec in recs:
        got = usage_of(rec)
        if got is None:
            continue
        mid, model, use = got
        row = per.setdefault(mid, {"ts": str(rec.get("timestamp") or ""), "model": model, **dict.fromkeys(FIELDS, 0)})
        for f in FIELDS:
            row[f] = max(row[f], use[f])
    return list(per.values())


def reads(recs: list[dict]) -> list[tuple[int, str]]:
    """(characters returned, what was asked for) of every tool call in a transcript, largest first."""
    asked: dict[str, str] = {}
    sized: list[tuple[int, str]] = []
    for rec in recs:
        content = (rec.get("message") or {}).get("content")
        for block in content if isinstance(content, list) else []:
            if block.get("type") == "tool_use":
                inp = block.get("input") or {}
                what = inp.get("file_path") or inp.get("url") or inp.get("pattern") or inp.get("command") or inp.get("query") or ""
                asked[block.get("id", "")] = f"{block.get('name')} {' '.join(str(what).split())[:110]}"
            elif block.get("type") == "tool_result":
                body = block.get("content")
                text = body if isinstance(body, str) else "".join(str(p.get("text", "")) for p in body or [] if isinstance(p, dict))
                sized.append((len(text), asked.get(block.get("tool_use_id", ""), "?")))
    return sorted(sized, reverse=True)


def window_of(ts: str, marks: list[dict]) -> str:
    label = "(before the first mark)"
    for m in marks:
        if ts >= m["ts"]:
            label = m["label"]
    return label


def total(rows: list[dict]) -> dict:
    out = {f: sum(r[f] for r in rows) for f in FIELDS}
    out["turns"] = len(rows)
    return out


def build(session: pathlib.Path, marks: list[dict]) -> list[dict]:
    """One entry per window: the main session's usage, then one row per agent run that started in it."""
    windows: dict[str, dict] = {}

    def win(label: str) -> dict:
        return windows.setdefault(label, {"window": label, "main": [], "agents": []})

    for msg in messages([r for r in records(session) if not r.get("isSidechain")]):
        win(window_of(msg["ts"], marks))["main"].append(msg)
    for path in sorted(session.with_suffix("").glob("subagents/agent-*.jsonl")):
        recs = records(path)
        msgs = messages(recs)
        if not msgs:
            continue
        try:
            meta = json.loads(path.with_suffix("").with_suffix(".meta.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            meta = {}
        kind = str(meta.get("agentType") or "unknown")
        started = min(m["ts"] for m in msgs)
        win(window_of(started, marks))["agents"].append(
            {
                "agent": kind,
                "class": "ad-hoc" if kind in BUILTIN else "named",
                "model": msgs[0]["model"],
                "description": str(meta.get("description") or "")[:60],
                **total(msgs),
                "peak_context": max(m["fresh"] + m["cached"] for m in msgs),
                # what the agent holds BEFORE it has read anything: the harness's system prompt and tool
                # schemas, the agent's contract, and the dispatch prompt - the floor no file split moves
                "first_turn": min(msgs, key=lambda m: m["ts"])["fresh"] + min(msgs, key=lambda m: m["ts"])["cached"],
                "read_chars": sum(size for size, _what in reads(recs)),
                # CLAUDE.md files the harness attached when the agent first read under their directory -
                # `omitClaudeMd` drops the launch copy, not these (measured on this slice: three per check)
                "nested_chars": sum(len(str((r.get("attachment") or {}).get("content") or r.get("attachment"))) for r in recs if r.get("type") == "attachment" and (r.get("attachment") or {}).get("type") == "nested_memory"),
                "nested_files": sum(1 for r in recs if r.get("type") == "attachment" and (r.get("attachment") or {}).get("type") == "nested_memory"),
                "reads": reads(recs)[:6],
            }
        )
    out = []
    # several sessions may open windows of the same label (one marks file per page, a session per group)
    for label in dict.fromkeys(["(before the first mark)"] + [m["label"] for m in marks]):
        if label in windows:
            w = windows[label]
            mains = w["main"]
            out.append({"window": label, "main": {**total(mains), "peak_context": max((m["fresh"] + m["cached"] for m in mains), default=0)}, "agents": w["agents"]})
    return out


def _n(v: int) -> str:
    return f"{v:,}"


def render(report: list[dict]) -> str:
    head = f"{'who':<34}{'model':<22}{'turns':>6}{'fresh in':>12}{'cached in':>13}{'output':>10}{'peak ctx':>11}"
    lines = []
    grand = {"main": dict.fromkeys(FIELDS, 0), "named": dict.fromkeys(FIELDS, 0), "ad-hoc": dict.fromkeys(FIELDS, 0)}
    for w in report:
        lines += ["", f"== {w['window']}", head, "-" * len(head)]
        m = w["main"]
        lines.append(f"{'main session':<34}{'':<22}{m['turns']:>6}{_n(m['fresh']):>12}{_n(m['cached']):>13}{_n(m['output']):>10}{_n(m['peak_context']):>11}")
        for f in FIELDS:
            grand["main"][f] += m[f]
        for a in w["agents"]:
            who = f"{a['agent']} [{a['class']}]"
            lines.append(f"{who:<34}{a['model']:<22}{a['turns']:>6}{_n(a['fresh']):>12}{_n(a['cached']):>13}{_n(a['output']):>10}{_n(a['peak_context']):>11}")
            lines.append(f"      first turn {_n(a['first_turn'])} tokens before anything was read; everything it then read: {_n(a['read_chars'])} chars (~{_n(a['read_chars'] // 4)} tokens); nested CLAUDE.md attached: {a['nested_files']} file(s), {_n(a['nested_chars'])} chars (~{_n(a['nested_chars'] // 4)} tokens)")
            for size, what in a["reads"]:
                lines.append(f"      {_n(size):>10} chars  {what}")
            for f in FIELDS:
                grand[a["class"]][f] += a[f]
    lines += ["", "== the whole session, by who spent it", f"{'':<14}{'fresh in':>12}{'cached in':>14}{'output':>10}"]
    for who, g in grand.items():
        lines.append(f"{who:<14}{_n(g['fresh']):>12}{_n(g['cached']):>14}{_n(g['output']):>10}")
    return "\n".join(lines)


def summary(files: list[pathlib.Path], questions: int, items: int, modals: int = 0, keys: int = 0) -> dict:
    """One page's figures from its sessions' `--json` records - the row R6 and later compare (feature 250 D15).

    PER QUESTION CHECKED is the headline (R6, recommendation 4): the check work scales with the questions a page's
    check sessions take, not with its items - three items on `cities/government` were four questions checked.
    Totals are fresh + cached + output, main and agents, summed over every window of every session."""
    main_t = turns = peak = 0
    agents: dict[str, list[int]] = {}
    for f in files:
        for w in json.loads(f.read_text(encoding="utf-8")):
            m = w["main"]
            main_t += m["fresh"] + m["cached"] + m["output"]
            turns += m["turns"]
            peak = max(peak, m["peak_context"])
            for a in w["agents"]:
                k = agents.setdefault(a["agent"], [0, 0, 0])
                k[0] += 1
                k[1] += a["fresh"] + a["cached"] + a["output"]
                k[2] += a["read_chars"]
    runs = sum(k[0] for k in agents.values())
    agent_t = sum(k[1] for k in agents.values())
    total = main_t + agent_t
    return {"sessions": len(files), "main": main_t, "turns": turns, "mean_turn": main_t // max(turns, 1), "peak": peak,
            "agent_runs": runs, "agents": agent_t, "mean_agent": agent_t // max(runs, 1), "total": total,
            "per_question": total // max(questions, 1), "per_item": total // max(items, 1),
            # D17 (R8 rec. 3): per THING checked - a question, an owed modal or a registry key - since `fields` checked
            # three questions but also seven modals and four sources, and per question read that as the dearest page
            "things": questions + modals + keys, "per_thing": total // max(questions + modals + keys, 1),
            "by_kind": {k: {"runs": v[0], "tokens": v[1], "mean_read_chars": v[2] // v[0]} for k, v in sorted(agents.items())}}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("verb", choices=("mark", "report", "summary"))
    ap.add_argument("label", nargs="?", default="")
    ap.add_argument("--session", default=str(SESSION))
    ap.add_argument("--json", default="")
    ap.add_argument("--marks", default=str(MARKS), help="the windows file - a page session keeps its own")
    ap.add_argument("--files", nargs="*", default=[], help="summary: the page's sessions' --json records")
    ap.add_argument("--questions", type=int, default=0, help="summary: the questions the check sessions took")
    ap.add_argument("--items", type=int, default=0, help="summary: the page's FR-002 and FR-006 items")
    ap.add_argument("--modals", type=int, default=0, help="summary: the modals owed an entry-drift the check sessions took")
    ap.add_argument("--keys", type=int, default=0, help="summary: the registry keys the check sessions took")
    args = ap.parse_args(argv)
    if args.verb == "summary":
        print(json.dumps(summary([pathlib.Path(f) for f in args.files], args.questions, args.items, args.modals, args.keys), indent=1))
        return 0
    marks_file = pathlib.Path(args.marks)
    marks = json.loads(marks_file.read_text(encoding="utf-8")) if marks_file.is_file() else []
    if args.verb == "mark":
        if not args.label:
            ap.error("mark needs a label")
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        marks.append({"label": args.label, "ts": now})
        marks_file.write_text(json.dumps(marks, indent=1) + "\n", encoding="utf-8")
        print(f"mark: {args.label} at {now}")
        return 0
    report = build(pathlib.Path(args.session), marks)
    print(render(report))
    # What made the MAIN session's context grow: a tool result stays in context for every later turn, so
    # one 40,000-character result at turn 20 of 90 is paid for seventy times over, as cached input.
    main_reads = reads([r for r in records(pathlib.Path(args.session)) if not r.get("isSidechain")])
    print("\n== the main session: the largest tool results that entered its context (each is re-read every later turn)")
    for size, what in main_reads[:14]:
        print(f"  {_n(size):>10} chars  {what}")
    print(f"  {_n(sum(s for s, _w in main_reads)):>10} chars in all, over {len(main_reads)} tool results")
    if args.json:
        # the record keeps each read's SIZE, not the command that made it: a command quotes whatever it grepped
        # for, a source's own spelling among it, and the figures are what the record is for
        for w in report:
            for a in w["agents"]:
                a["reads"] = [size for size, _what in a["reads"]]
        pathlib.Path(args.json).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
