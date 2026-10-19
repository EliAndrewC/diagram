#!/usr/bin/env python3
"""The bundle the round arbiter steps back over at the feature's hourly checkpoint (feature 383, plan D11).

WHY (the GM 2026-10-12: *"convert the hourly check that we are doing here into something that like happens automatically"*).
The hourly check one session ran by hand over another's log found loops, guards misfiring and slow steps the working session
could not see from inside. Its reading is mechanical, so a script does it; the judging is the round arbiter's, from outside,
on what this writes - never the session reading its own log, the author reviewing its own work.

What it writes, under `/tmp/l7r-check/step-back-<feature>-<n>/` (out of the repository, as every check bundle is):

- `time.md` - where the hour went: the window's wall time, the model's time (each reply after a tool result,
  `scripts/measure/turn_time.py`), the tools' time by command (a make target, else the program), and the rest (waiting on
  background work, subagents or the GM);
- `dispatches.md` - each subagent the session dispatched in the hour, its kind, its time and its verdict (the event log);
- `refusals.md` - each guard that refused the session in the hour (the guard log);
- `task.md` - the feature's open tasks;
- `words.md` - the session's own words in the hour: its replies, each command it ran (never their output), each edit's old
  and new text, cut to about 40,000 characters, the newest kept;
- `MANIFEST.md` - the four questions, the two rulings and how to record one.

    stepback_bundle.py <trigger> [--root <clone>] [--transcript <jsonl>] [--since <ISO>] [--until <ISO>] [--out <dir>]

`--transcript`, `--since` and `--until` replay any hour of any session (SC-008); without them the window is the checkpoint's
(its start to now) and the transcript the event log's session.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import re
import sys
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "measure"))
import review_owed as ro  # noqa: E402

OUT = Path("/tmp/l7r-check")
WORDS_CAP = 40_000
PROJECTS = Path.home() / ".claude" / "projects"
GUARD_LOG = Path.home() / ".claude" / "guard-log"


def _ts(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def _iso(t: float) -> str:
    return datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M UTC")


def _lines(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if path.is_file() else []:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict):
            out.append(d)
    return out


def command_key(cmd: str) -> str:
    """A command's name for the tally: `make <targets>`, else its first program (assignments and a leading `cd` dropped)."""
    makes = re.findall(r"\bmake\s+(?:-\S+\s+)*([a-z][\w-]*)", cmd)
    if makes:
        return "make " + "+".join(dict.fromkeys(makes))
    rest = re.sub(r"^(cd \S+ && |[A-Z_]+=\S+ )+", "", cmd.strip())
    return (rest.split() or ["?"])[0]


def tool_time(records: list[dict], since: float, until: float) -> tuple[float, collections.Counter, collections.Counter, dict]:
    """(seconds in tools, seconds per command, calls per command, the longest call per command) of the main session's tool
    calls that started in the window - each tool_use paired with its tool_result."""
    start: dict[str, tuple[float, str, str]] = {}
    spent: collections.Counter = collections.Counter()
    count: collections.Counter = collections.Counter()
    longest: dict[str, tuple[float, str]] = {}
    for d in records:
        if d.get("isSidechain") or "timestamp" not in d:
            continue
        t = _ts(d["timestamp"])
        content = (d.get("message") or {}).get("content")
        for b in content if isinstance(content, list) else ():
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                inp = b.get("input") or {}
                cmd = str(inp.get("command") or "") if b.get("name") == "Bash" else ""
                key = command_key(cmd) + (" [background]" if inp.get("run_in_background") else "") if cmd else str(b.get("name") or "?")
                start[str(b.get("id"))] = (t, key, cmd)
            elif b.get("type") == "tool_result" and str(b.get("tool_use_id")) in start:
                t0, key, cmd = start.pop(str(b.get("tool_use_id")))
                if since <= t0 <= until:
                    spent[key] += t - t0
                    count[key] += 1
                    if t - t0 > longest.get(key, (0.0, ""))[0]:
                        longest[key] = (t - t0, " ".join(cmd.split())[:160])
    return sum(spent.values()), spent, count, longest


def model_time(records: list[dict], since: float, until: float) -> float:
    """The model's seconds in the window: each reply's gap after the tool result it answers (turn_time's turns)."""
    import turn_time  # noqa: PLC0415

    kept = [json.dumps(d) for d in records if "timestamp" in d and since <= _ts(d["timestamp"]) <= until]
    return sum(s for _ctx, s, _out in turn_time.turns(kept))


def words(records: list[dict], since: float, until: float, cap: int = WORDS_CAP) -> str:
    """The sessions' own words in the window, in order: replies, commands, edits - never a tool's output. The newest kept. A
    record tagged `_sid` (`build`, more than one session in the hour) is labeled with its session's first 8 characters."""
    parts: list[str] = []
    refused = refused_calls(records)
    for d in records:
        if d.get("isSidechain") or "timestamp" not in d or d.get("type") != "assistant":
            continue
        t = _ts(d["timestamp"])
        if not since <= t <= until:
            continue
        stamp = datetime.fromtimestamp(t, UTC).strftime("%H:%M") + (f" {str(d['_sid'])[:8]}" if d.get("_sid") else "")
        for b in (d.get("message") or {}).get("content") or []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and str(b.get("text") or "").strip():
                parts.append(f"[{stamp}] SAID: {str(b['text']).strip()}")
            elif b.get("type") == "tool_use":
                inp = b.get("input") or {}
                name = b.get("name")
                # A CALL A GUARD REFUSED never ran: five refused edits and ten refused dispatches read as an oscillation and as
                # checks that never happened (the round arbiter's tooling fix on hour:397@2)
                verb = "REFUSED " if b.get("id") in refused else ""
                if name == "Bash":
                    parts.append(f"[{stamp}] {verb}RAN: {str(inp.get('command') or '')[:300]}")
                elif name in ("Edit", "Write"):
                    old, new = str(inp.get("old_string") or "")[:200], str(inp.get("new_string") or inp.get("content") or "")[:200]
                    parts.append(f"[{stamp}] {verb}{name.upper()} {inp.get('file_path')}: {old!r} -> {new!r}")
                elif name == "Agent":
                    parts.append(f"[{stamp}] {verb + 'DISPATCH' if verb else 'DISPATCHED'} {inp.get('subagent_type') or 'agent'}: {inp.get('description') or ''}")
    text = "\n".join(parts)
    if len(text) <= cap:
        return text
    # OVER THE CAP, COMMANDS AND EDITS SHRINK FIRST (the round arbiter's tooling fix on hour:383@1): multi-line heredoc bodies
    # filled the cap and the hour's first half - its reviews, its replies - was cut. Each RAN and EDIT keeps its first line,
    # every SAID and DISPATCHED stays whole, and only then are the oldest entries dropped.
    parts = [p if p.split("] ", 1)[-1].startswith(("SAID", "DISPATCHED")) else p.split("\n", 1)[0][:200] for p in parts]
    text = "\n".join(parts)
    return text if len(text) <= cap else "[... the hour's earlier words cut to the cap ...]\n" + text[-cap:]


def refused_calls(records: list[dict]) -> set[str]:
    """The ids of the tool calls a hook refused: their result is an error that opens with the hook's own words."""
    out = set()
    for d in records:
        for b in (d.get("message") or {}).get("content") or [] if d.get("type") == "user" else []:
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                c = b.get("content")
                text = c if isinstance(c, str) else " ".join(str(x.get("text") or "") for x in c or [] if isinstance(x, dict))
                if text.lstrip().startswith(("PreToolUse:", "<tool_use_error>PreToolUse:")) or "hook error:" in text[:200]:
                    out.add(str(b.get("tool_use_id")))
    return out


def dispatches(events: list[dict], since: float, until: float) -> list[str]:
    """One line per subagent dispatched in the window: its kind, category, time and verdict (the event log)."""
    started: dict[str, tuple[float, str, str]] = {}
    out = []
    for e in events:
        if "t" not in e:
            continue
        t = _ts(str(e["t"]))
        if e.get("ev") == "SubagentStart" and since <= t <= until:
            started[str(e.get("aid"))] = (t, str(e.get("agent") or "?"), str(e.get("cat") or ""))
        elif e.get("ev") == "SubagentStop" and str(e.get("aid")) in started:
            t0, agent, cat = started.pop(str(e.get("aid")))
            out.append(f"- {datetime.fromtimestamp(t0, UTC).strftime('%H:%M')} {agent} ({cat}): {t - t0:.0f} s, {e.get('verdict') or 'no verdict read'}")
    out += [f"- {datetime.fromtimestamp(t0, UTC).strftime('%H:%M')} {agent} ({cat}): still running" for t0, agent, cat in started.values()]
    return out


def refusals(sids: Sequence[str], since: float, until: float, log: Path = GUARD_LOG) -> list[str]:
    """One line per guard refusal of these sessions in the window (the guard log: a file per firing, named by its UTC time); no
    session named, every refusal."""
    out = []
    lo, hi = time.strftime("%Y%m%dT%H%M%S", time.gmtime(since)), time.strftime("%Y%m%dT%H%M%S", time.gmtime(until + 1))
    for f in sorted(log.glob("*.json")) if log.is_dir() else []:
        if not lo <= f.name[:15] <= hi:
            continue
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except OSError, ValueError:
            continue
        # `refused` too: the pair guard's hour refusal logs so, and the hour-10 step-back's list missed it (the round arbiter's
        # tooling fix on hour:385-approach-checklist@10)
        if isinstance(r, dict) and r.get("event") in ("blocked", "refused") and (not sids or r.get("session") in sids or r.get("sid") in sids):
            out.append(f"- {f.name[9:11]}:{f.name[11:13]} {r.get('guard')}: {r.get('rule') or ''} - {str(r.get('detail') or '')[:200]}")
    return out


def sessions_of(events: list[dict], since: float, until: float) -> list[str]:
    """Every session that worked the feature in the window, busiest first: the `sid`s of its events there.

    EVERY ONE, NOT THE BUSIEST (the round arbiter's tooling fix on hour:385-approach-checklist@16): that hour had three - this
    feature's page session's check run (439 events), the session working the task (322) and the write run (169) - and the
    busiest alone was read, so `words.md` held the page session's words and none of the working session's."""
    sids = collections.Counter(str(e.get("sid")) for e in events if e.get("sid") and "t" in e and since <= _ts(str(e["t"])) <= until)
    return [s for s, _n in sids.most_common()]


def transcript_of(sid: str, projects: Path = PROJECTS) -> Path | None:
    hits = sorted(projects.glob(f"*/{sid}.jsonl"), key=lambda p: p.stat().st_mtime) if sid else []
    return hits[-1] if hits else None


MANIFEST = """# Step-back bundle - {trigger}

The feature's hourly checkpoint (feature 383): you are the round arbiter, stepping back over one hour of a session's work on
feature {feature}, {since} to {until}. Read the files beside this MANIFEST and nothing in the repository.

| file | what it is |
|---|---|
| `time.md` | where the hour went: model, tools by command, the rest |
| `dispatches.md` | the subagents dispatched, their time and verdicts |
| `refusals.md` | the guards that refused the session |
| `task.md` | the feature's open tasks |
| `words.md` | the session's own words: replies, commands, edits (no tool output), the newest kept |
| `fix-yield.md` | each tooling fix of the feature: the rate of what it was meant to cut, before its ruling and since it was made |

Answer four questions:
1. Is the session going in circles, or oscillating between approaches (the same edit made and unmade, a route tried again)?
2. Is it packing features against a number nobody researched - an UNRESEARCHED, GUESS, CONVENTION or convenience size, spacing,
   reach or band - where more room would settle it while the map stays within the research ("Room before packing")? Name the
   number.
3. Is a step slow, or a guard misfiring, enough to be worth a tooling fix? Name the tool and the change. And in `fix-yield.md`,
   does a made fix save nothing? Then retire it (remove or simplify) as this hour's `tooling_fix`, or keep it with the reason
   in `what`.
4. Is anything too big for the session, which the GM should see?

Rule `continue` (nothing to change) or `change-route` (binding: `what` names the loop or the number, and the route to take -
more room first). Add `tooling_fix` for question 3 (it opens an item the session makes, with its test, or declines as an
overhaul) and `for_gm` for question 4. A `continue` with neither adds nothing to the GM's review.

Record it: write the JSON `{{"ruling": ..., "why": ..., "what": ..., "tooling_fix": ..., "fix_measure": ..., "fix_minutes": ...,
"for_gm": ...}}` to a file (a `tooling_fix` carries `fix_measure` - a regex over the session's Bash commands it should cut, or
`agent:<kind>` - and `fix_minutes`, the cost it measured) and run
`make arbiter-ruled TRIGGER={trigger} FILE=<that file> AS=round-arbiter`.
"""


def _records(sids: list[str], transcript: Path | None, projects: Path) -> tuple[list[dict], list[str], list[str]]:
    """(the records, merged by time, the sessions read, the sessions whose transcript was not found). A replay's `transcript` is
    read alone, as before (SC-008); else every session's, each record tagged `_sid` when there is more than one."""
    if transcript is not None:
        return _lines(transcript), [transcript.stem], []
    read, missing, records = [], [], []
    for sid in sids:
        path = transcript_of(sid, projects)
        if path is None:
            missing.append(sid)
            continue
        read.append(sid)
        records += [{**d, "_sid": sid} if len(sids) > 1 else d for d in _lines(path)]
    records.sort(key=lambda d: _ts(d["timestamp"]) if "timestamp" in d else 0.0)
    return records, read, missing


def silent_minutes(records: list[dict], since: float, until: float, gap: float = 300.0) -> list[str]:
    """The stretches of the window, five minutes or longer, in which no record read has a timestamp - named in `words.md`
    so the arbiter does not judge an hour it saw only part of (the round arbiter's tooling fix on hour:395@2)."""
    ts = sorted(t for d in records if "timestamp" in d and since <= (t := _ts(d["timestamp"])) <= until)
    marks, out = [since, *ts, until], []
    for a, b in itertools.pairwise(marks):
        if b - a >= gap:
            out.append(f"{_iso(a)[11:16]}-{_iso(b)[11:16]}")
    return out


def build(trigger: str, root: Path, out: Path, since: float, until: float, transcript: Path | None, sids: Sequence[str] = (), projects: Path = PROJECTS) -> Path:
    feature = trigger.split(":", 1)[-1].rsplit("@", 1)[0]
    g = ro._gitdir(root)  # noqa: SLF001
    events = _lines(g / "l7r-events" / f"{feature}.jsonl") if g is not None else []
    # EVERY SESSION OF THE CLONE IN THE WINDOW (the round arbiter's tooling fix on hour:395-shrine-building-costs@2): the main
    # session's events went to 397's log while `.specify/feature.json` named 397, so its 16 minutes of 395's work (four tooling
    # fixes landed, round-3 bundles built) were in no session this read. Sessions come from every feature's log in the clone.
    clone_events = [e for f in sorted((g / "l7r-events").glob("*.jsonl")) for e in _lines(f)] if g is not None and (g / "l7r-events").is_dir() else events
    sids = list(sids) or sessions_of(clone_events, since, until)
    records, read, missing = _records(sids, transcript, projects)
    out.mkdir(parents=True, exist_ok=True)
    tools, spent, count, longest = tool_time(records, since, until)
    model = model_time(records, since, until)
    wall = until - since
    rows = [f"- {spent[k] / 60:5.1f} min x{count[k]:<3} {k} (longest {longest[k][0]:.0f} s: `{longest[k][1]}`)" for k, _ in spent.most_common(15)]
    (out / "time.md").write_text(
        f"# Where the hour went ({_iso(since)} to {_iso(until)})\n\n"
        + (f"summed over {len(read)} sessions, which may run side by side and so sum past the hour\n\n" if len(read) > 1 else "")
        + f"wall {wall / 60:.0f} min; the model {model / 60:.1f} min; tools "
        f"{tools / 60:.1f} min; the rest (waiting on background work, subagents or the GM) {max(wall - model - tools, 0) / 60:.1f} min\n\n"
        "## Tools by command\n\n" + ("\n".join(rows) or "(no tool call in the window)") + "\n",
        encoding="utf-8",
    )
    (out / "dispatches.md").write_text("# Subagents dispatched\n\n" + ("\n".join(dispatches(events, since, until)) or "(none)") + "\n", encoding="utf-8")
    (out / "refusals.md").write_text("# Guard refusals\n\n" + ("\n".join(refusals(sids, since, until)) or "(none)") + "\n", encoding="utf-8")
    tasks = root / "specs" / feature / "tasks.md"
    open_boxes = [ln for ln in tasks.read_text(encoding="utf-8").splitlines() if ln.startswith("- [ ]")] if tasks.is_file() else []
    (out / "task.md").write_text(f"# Open tasks of {feature}\n\n" + ("\n".join(open_boxes[:30]) or "(none)") + "\n", encoding="utf-8")
    said = words(records, since, until)
    head = f"sessions read: {', '.join(s[:8] for s in read) or 'none'}" + (f"; left out (no transcript found): {', '.join(s[:8] for s in missing)}" if missing else "")
    if said.startswith("[... the hour's earlier words cut"):
        head += "; cut to the cap: the hour's earliest words"
    if gaps := silent_minutes(records, since, until):
        head += f"; NO WORDS FOUND for {', '.join(gaps)} of the window - judge those minutes as unseen, not as idle"
    (out / "words.md").write_text("# The sessions' own words\n\n" + head + "\n\n" + (said or "(no transcript found)") + "\n", encoding="utf-8")
    # EACH FIX'S YIELD (feature 385 T119, D141; the GM's change 3 of 2026-10-19): a fix that saves nothing is retired. Read over
    # every session of the clone, never this hour's alone: a fix's before and after span many hours (`make fix-yield` reads the same)
    import fix_yield  # noqa: PLC0415 - scripts/measure, on the path above

    (out / "fix-yield.md").write_text("# Each tooling fix's yield\n\n" + fix_yield.report(root, root / "specs" / feature, None, projects), encoding="utf-8")
    (out / "MANIFEST.md").write_text(MANIFEST.format(trigger=trigger, feature=feature, since=_iso(since), until=_iso(until)), encoding="utf-8")
    return out / "MANIFEST.md"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("trigger", help="hour:<feature>@<n> (make step-back prints it)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--transcript", default="", help="replay: the session transcript to read")
    ap.add_argument("--since", default="", help="replay: the window's start (ISO, UTC)")
    ap.add_argument("--until", default="", help="replay: the window's end (ISO, UTC)")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    if not args.trigger.startswith("hour:") or "@" not in args.trigger:
        print("stepback-bundle: the trigger is hour:<feature>@<n>", file=sys.stderr)
        return 2
    root = Path(ro._git(Path(args.root), "rev-parse", "--show-toplevel") or args.root)  # noqa: SLF001
    if args.since:
        since = _ts(args.since if args.since.endswith("Z") or "+" in args.since else args.since + "Z")
    else:
        sys.path.insert(0, str(HERE))
        import checkpoint  # noqa: PLC0415

        since = float(checkpoint.state(root).get("since") or time.time() - 3600)
    until = _ts(args.until if args.until.endswith("Z") or "+" in args.until else args.until + "Z") if args.until else time.time()
    name = args.trigger.split(":", 1)[1].replace("@", "-")
    out = Path(args.out) if args.out else OUT / f"step-back-{name}"
    manifest = build(args.trigger, root, out, since, until, Path(args.transcript) if args.transcript else None)
    print(f"step-back: {args.trigger} - dispatch `round-arbiter` on {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
