#!/usr/bin/env python3
"""451 T536: bytes of feature 451's records returned to each builder's context by its own tool calls (read-only).

Adapted from ../plan-reads/plan-reads.py (451 T499). Builders = subagent transcripts under /home/agent/.claude/projects/-diagram*/
whose first user prompt carries a BUILDER-BRIEF line, first timestamp on DAY (UTC, default 2026-11-27; FROM=HH:MM narrows it, the
seventeenth message's table counted from 02:00Z). A call counts for a record when it is a Read, Grep or Bash whose path or command
names a path UNDER the feature directory `specs/451-time-retro-and-efficiency/` (the record is the first path part after it, so a
record split into a directory by T537 is still counted under its name) or under `l7r-events/451` (the event log, any part). A call
naming several records counts once in the total and once under each record named (an upper bound per record). Bytes are UTF-8 bytes
of the tool result text; tokens are an ESTIMATE at about 4 bytes a token.
Run: python3 -I t536-builder-reads.py > t536-builder-reads.txt   (env DAY=YYYY-MM-DD FROM=HH:MM)
ALL=1 counts EVERY transcript of the day instead (the plan review of T536, round 1: "which agents" is every agent): each subagent
grouped by its type (`agent-<id>.meta.json`'s agentType; a builder is any whose first prompt has a BUILDER-BRIEF line), and the
top-level sessions (the coordinating ones) as `session`, with each group's largest single call naming one of the four large records.
"""
import collections, glob, json, os, re, statistics, sys

DAY = os.environ.get("DAY", "2026-11-27")
FROM = os.environ.get("FROM", "00:00")
FEAT = re.compile(r'specs/451-time-retro-and-efficiency/([A-Za-z0-9_.-]+)')
EVENTS = re.compile(r'l7r-events/451[A-Za-z0-9_.-]*')
SELF = "T536"


def text_of(c):
    if isinstance(c, str):
        return c
    return ''.join(b.get('text', '') for b in c if isinstance(b, dict) and b.get('type') == 'text')


def named(name, inp):
    s = ' '.join(str(inp.get(k, '')) for k in ('file_path', 'path', 'command', 'pattern', 'glob'))
    keys = set(m.group(1) for m in FEAT.finditer(s))
    if EVENTS.search(s):
        keys.add('event log')
    return keys


ALL = os.environ.get("ALL") == "1"
LARGE = {"plan-review.json", "plan-done.md", "tasks-done.md", "event log"}


def kind_of(p, first):
    if '/subagents/' not in p:
        return 'session'
    if re.search(r'^BUILDER-BRIEF \S+ T\d+', first or '', re.M):
        return 'builder'
    try:
        return json.load(open(p[:-len('.jsonl')] + '.meta.json')).get('agentType') or '?'
    except Exception:
        return '?'


def main():
    if ALL:
        return main_all()
    builders, seen = [], set()
    for p in glob.glob('/home/agent/.claude/projects/-diagram*/**/*.jsonl', recursive=True):
        if '/subagents/' not in p or os.path.basename(p) in seen:
            continue
        seen.add(os.path.basename(p))
        first = ts0 = None
        uses, per, calls, total, task = {}, collections.Counter(), collections.Counter(), 0, '?'
        any_b = any_c = 0
        for line in open(p, errors='replace'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts0 = ts0 or d.get('timestamp')
            m = d.get('message')
            if not isinstance(m, dict):
                continue
            c = m.get('content')
            if first is None and d.get('type') == 'user':
                first = text_of(c)
                mm = re.search(r'^BUILDER-BRIEF (\S+) (\S+)', first, re.M)
                if not mm:
                    break
                task = ' '.join(mm.groups())
            if not isinstance(c, list):
                continue
            for b in c:
                if b.get('type') == 'tool_use':
                    uses[b['id']] = (b['name'], b.get('input', {}))
                elif b.get('type') == 'tool_result':
                    sz = len(text_of(b.get('content', '')).encode())
                    total += sz
                    nm, inp = uses.get(b.get('tool_use_id'), (None, {}))
                    keys = named(nm, inp) if nm in ('Read', 'Bash', 'Grep') else set()
                    if keys:
                        any_b += sz
                        any_c += 1
                    for k in keys:
                        per[k] += sz
                        calls[k] += 1
        if task == '?' or not ts0 or ts0[:10] != DAY or ts0[11:16] < FROM:
            continue
        if task.endswith(SELF):
            continue  # this measurement's own builder
        builders.append(dict(task=task, ts=ts0, total=total, per=per, calls=calls, any=any_b, anyc=any_c))
    n = len(builders)
    print(f"builders: {n} (first timestamp {DAY} from {FROM}Z, BUILDER-BRIEF first prompt, this task's own left out)")
    T = sum(b['total'] for b in builders)
    A = sum(b['any'] for b in builders)
    print(f"tool-result bytes, all builders: {T:,}; naming any 451 record: {A:,} in {sum(b['anyc'] for b in builders):,} calls "
          f"({100 * A / max(T, 1):.1f}%), {A / max(n, 1):,.0f} a builder, about {A / 4 / max(n, 1):,.0f} tokens a builder (ESTIMATE)")
    agg, aggc = collections.Counter(), collections.Counter()
    for b in builders:
        agg.update(b['per'])
        aggc.update(b['calls'])
    print("\n| record (path under the feature dir, or the event log) | calls | bytes returned | bytes a call |\n|---|---|---|---|")
    for k, z in agg.most_common(25):
        print(f"| {k} | {aggc[k]:,} | {z:,} | {z / aggc[k]:,.0f} |")
    pb = sorted(b['any'] for b in builders)
    if pb:
        print(f"\nper builder, bytes naming any 451 record: median {statistics.median(pb):,.0f}, max {pb[-1]:,}")


def main_all():
    groups = collections.defaultdict(lambda: dict(n=0, total=0, any=0, anyc=0, large=0, largec=0, top=(0, ''),
                                                  per=collections.Counter()))
    seen = set()
    for p in glob.glob('/home/agent/.claude/projects/-diagram*/**/*.jsonl', recursive=True):
        if os.path.basename(p) in seen or '/tool-results/' in p:
            continue
        seen.add(os.path.basename(p))
        first = ts0 = None
        uses, rows = {}, []
        for line in open(p, errors='replace'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = d.get('timestamp')
            m = d.get('message')
            if not isinstance(m, dict):
                continue
            c = m.get('content')
            if first is None and d.get('type') == 'user':
                first = text_of(c)
            if not isinstance(c, list):
                continue
            for b in c:
                if b.get('type') == 'tool_use':
                    uses[b['id']] = (b['name'], b.get('input', {}))
                elif b.get('type') == 'tool_result' and ts and ts[:10] == DAY and ts[11:16] >= FROM:
                    ts0 = ts0 or ts
                    sz = len(text_of(b.get('content', '')).encode())
                    nm, inp = uses.get(b.get('tool_use_id'), (None, {}))
                    keys = named(nm, inp) if nm in ('Read', 'Bash', 'Grep') else set()
                    rows.append((sz, keys, (inp.get('file_path') or inp.get('command') or inp.get('pattern') or '')[:140]))
        if not rows:
            continue  # nothing returned on the day (a session's results are counted by their own timestamps)
        if first and SELF in first and 'BUILDER-BRIEF 451 T536' in first:
            continue  # this measurement's own builder
        g = groups[kind_of(p, first)]
        g['n'] += 1
        for sz, keys, what in rows:
            g['total'] += sz
            if keys:
                g['any'] += sz
                g['anyc'] += 1
                g['per'].update({k: sz for k in keys})
            if keys & LARGE:
                g['large'] += sz
                g['largec'] += 1
                if sz > g['top'][0]:
                    g['top'] = (sz, f"{sorted(keys & LARGE)}: {what}")
    print(f"every transcript with a tool result on {DAY} from {FROM}Z (UTC), by kind; this task's own builder left out")
    print("\n| kind | transcripts | tool-result bytes | naming any 451 record | calls | naming one of the four large | calls | largest such call |")
    print("|---|---|---|---|---|---|---|---|")
    for k, g in sorted(groups.items(), key=lambda kv: -kv[1]['any']):
        print(f"| {k} | {g['n']} | {g['total']:,} | {g['any']:,} | {g['anyc']:,} | {g['large']:,} | {g['largec']:,} | "
              f"{g['top'][0]:,} {g['top'][1]} |")
    print("\nthe four large records, by kind (bytes):")
    for k, g in sorted(groups.items(), key=lambda kv: -kv[1]['large']):
        if g['large']:
            print(f"  {k}: " + ", ".join(f"{r} {g['per'][r]:,}" for r in sorted(LARGE) if g['per'][r]))


main()
