"""461 T01 (plan D12, FR-006/FR-007): a window's tokens by actor and kind, per landed task where they book.

Usage: python3 -I night-tokens.py W0 W1 TASK_TIME_OUT [EXTRACT.tsv]
  W0, W1         UTC ISO bounds, e.g. 2026-11-27T04:30:00Z 2026-11-27T14:29:00Z (half-open [W0, W1))
  TASK_TIME_OUT  a `make task-time SINCE=W0 UNTIL=W1` output (or its kept cut, R3's baseline-task-time.txt): its 451 T512
                 table names the window's landed tasks and their test and non-test lines
  EXTRACT.tsv    optional: one row per model call (no content) so the record re-derives after the transcripts are gone

Sources: the coordinator's transcript (TRANSCRIPT below) and every subagent transcript under its directory, workflow agents
included; any other main-session transcript in the project directory with a call in the window is counted as a page session
(or another main session). Each call is ONE message id (a message is written as one record per content block, usage repeated:
checked identical across records, 2026-11-27). The four kinds are the call's top-level usage, which is the sum of its own
`message` iterations; the advisor's calls (`advisor_message` iterations) are summed in their own columns, never in the four.

Actors: coordinator (the main session); builder (a subagent whose first prompt holds a `BUILDER-BRIEF <feature> <task>`
marker, or a general-purpose agent whose description opens `Fix:`/`Build`/`Repair:` with a feature and task); repair builder (a
builder whose description opens `Repair:` or names a `coverage repair` - the description only, since every brief quotes the
repair rule); review agent (any
agent of a project-defined type: spec-fidelity, message-check, round-arbiter, ...); other agent (a built-in type without a
builder's marker: Explore, ad-hoc general-purpose); page session (another main session).
Booking: a builder books to its marker's feature and task (a bundle `T<a>,T<b>` books whole to the bundle, listed as one unit);
an agent a builder dispatched (its parentAgentId chain) books to that builder's task; a coordinator-dispatched agent books only
where its description names exactly one `<feature> T<n>` pair; the coordinator and the rest book to no task (451 T513).
"""
import collections as C
import glob
import json
import os
import re
import statistics
import sys

PROJ = '/home/agent/.claude/projects/-diagram'
SID = 'c6fd72d1-ab6c-4736-b723-0697a1f5ca51'
TRANSCRIPT = f'{PROJ}/{SID}.jsonl'
KINDS = ('output', 'fresh_in', 'cache_read', 'cache_write')
ADV = ('adv_out', 'adv_in', 'adv_cache_read', 'adv_cache_write')
ACTORS = ('builder', 'repair builder', 'review agent', 'other agent', 'coordinator', 'page session')


def iso(s):
    return s.replace('Z', '')[:23]


def calls(path, w0, w1):
    seen = set()
    for line in open(path, errors='replace'):
        if '"assistant"' not in line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get('type') != 'assistant':
            continue
        t = r.get('timestamp', '')
        if not (w0 <= t[:23] < w1):
            continue
        m = r.get('message') or {}
        mid = m.get('id') or r.get('requestId')
        if mid in seen:
            continue
        seen.add(mid)
        u = m.get('usage') or {}
        row = {'t': t, 'model': m.get('model'),
               'output': u.get('output_tokens', 0), 'fresh_in': u.get('input_tokens', 0),
               'cache_read': u.get('cache_read_input_tokens', 0), 'cache_write': u.get('cache_creation_input_tokens', 0)}
        for k in ADV:
            row[k] = 0
        for it in u.get('iterations') or []:
            if it.get('type') == 'advisor_message':
                row['adv_out'] += it.get('output_tokens', 0) or 0
                row['adv_in'] += it.get('input_tokens', 0) or 0
                row['adv_cache_read'] += it.get('cache_read_input_tokens', 0) or 0
                row['adv_cache_write'] += it.get('cache_creation_input_tokens', 0) or 0
        yield row


def first_prompt(path):
    for line in open(path, errors='replace'):
        if '"user"' not in line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get('type') != 'user':
            continue
        c = (r.get('message') or {}).get('content')
        if isinstance(c, str):
            return c
        return ' '.join(b.get('text', '') for b in c or [] if isinstance(b, dict))
    return ''


PAIR = re.compile(r'\b(4\d\d)\b[^T\n]{0,40}?\bT(\d+)\b')


def agent_info(path):
    mp = path[:-len('.jsonl')] + '.meta.json'
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    aid = os.path.basename(path)[len('agent-'):-len('.jsonl')]
    p = first_prompt(path)
    desc = meta.get('description') or ''
    at = meta.get('agentType')
    mk = re.search(r'BUILDER-BRIEF (\d{3})\S* (T\d+(?:,T?\d+)*) KIND=(\S+)', p)
    book = kind = None
    if mk:
        book = (mk.group(1), mk.group(2)); kind = mk.group(3)
    elif at in ('general-purpose', 'claude', None) and re.match(r'(Fix|Build|Repair)\b', desc):
        pr = set(PAIR.findall(desc))
        if len(pr) == 1:
            f, t = pr.pop(); book = (f, 'T' + t); kind = 'unmarked'
    if book:
        # by its description only: every brief quotes the rule "a builder whose JOB is a coverage repair of a red batch
        # gate", so the brief's words matched 451 T308's fix builder (checked 2026-11-27)
        repair = bool(re.match(r'Repair\b|.*\bcoverage repair\b', desc))
        actor = 'repair builder' if repair else 'builder'
    elif meta.get('isBuiltIn') is False:
        actor = 'review agent'
    else:
        actor = 'other agent'
    if not book:
        pr = set(PAIR.findall(desc))
        if len(pr) == 1:
            f, t = pr.pop(); book = (f, 'T' + t)
    return {'aid': aid, 'type': at, 'desc': desc, 'parent': meta.get('parentAgentId'), 'actor': actor,
            'book': book, 'kind': kind, 'own_book': book}


def landed_from(task_time_out):
    """The T512 table's rows: {(feature, 'T<n>'): (test lines, non-test lines, shared?)}."""
    out = {}
    head = None
    for line in open(task_time_out):
        if line.startswith('| task | commits | test lines'):
            head = [c.strip() for c in line.strip().strip('|').split('|')]
            continue
        if head and line.startswith('| ') and not line.startswith('|---'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) != len(head):
                head = None
                continue
            m = re.match(r'(\d{3})\S* (T\d+)$', cells[0])
            if not m:
                continue

            def lines(s):
                a = re.match(r'\+(\d+) -(\d+)', s)
                return int(a.group(1)) + int(a.group(2)) if a else 0
            out[(m.group(1), m.group(2))] = {
                'test': lines(cells[head.index('test lines')]), 'nontest': lines(cells[head.index('non-test lines')]),
                'shared': 'shared' in cells[1],
                't512': {k: float(cells[head.index(h)].split('k')[0]) * 1000
                         for k, h in zip(KINDS, ('output', 'fresh input', 'cache read', 'cache write'))}}
        elif head and not line.startswith('|'):
            head = None
    return out


def M(x):
    return f'{x / 1e6:,.2f}M'


def K(x):
    return f'{x / 1e3:,.1f}k'


def main():
    w0, w1, ttout = iso(sys.argv[1]), iso(sys.argv[2]), sys.argv[3]
    extract = sys.argv[4] if len(sys.argv) > 4 else None
    landed = landed_from(ttout)
    subs = sorted(glob.glob(f'{PROJ}/{SID}/subagents/**/*.jsonl', recursive=True))
    info = {}
    rows = []
    for p in subs:
        cs = list(calls(p, w0, w1))
        if not cs:
            continue
        a = agent_info(p)
        info[a['aid']] = a
        for c in cs:
            c['aid'] = a['aid']; rows.append(c)
    for c in calls(TRANSCRIPT, w0, w1):
        c['aid'] = 'coordinator'; rows.append(c)
    others = []
    for p in sorted(glob.glob(f'{PROJ}/*.jsonl')):
        if p == TRANSCRIPT:
            continue
        cs = list(calls(p, w0, w1))
        if cs:
            others.append(p)
            for c in cs:
                c['aid'] = 'page:' + os.path.basename(p)[:8]; rows.append(c)
    # a dispatched agent's booking follows its parent chain up to a builder (depth 2 and deeper)
    allmeta = {}
    for p in subs:
        mp = p[:-len('.jsonl')] + '.meta.json'
        if os.path.exists(mp):
            allmeta[os.path.basename(p)[len('agent-'):-len('.jsonl')]] = json.load(open(mp)).get('parentAgentId')
    builders = {}
    for p in subs:
        aid = os.path.basename(p)[len('agent-'):-len('.jsonl')]
        if aid in info and info[aid]['actor'] in ('builder', 'repair builder'):
            builders[aid] = info[aid]['book']
    # builders active only outside the window still own their children: read their markers too
    for aid, a in info.items():
        par = a['parent']; hops = 0
        while par and hops < 5:
            if par not in builders and par not in info:
                p = glob.glob(f'{PROJ}/{SID}/subagents/**/agent-{par}.jsonl', recursive=True)
                if p:
                    b = agent_info(p[0])
                    if b['actor'] in ('builder', 'repair builder'):
                        builders[par] = b['book']
            if par in builders:
                a['book'] = builders[par]; a['via'] = par; break
            par = allmeta.get(par); hops += 1

    def actor_of(c):
        if c['aid'] == 'coordinator':
            return 'coordinator'
        if c['aid'].startswith('page:'):
            return 'page session'
        return info[c['aid']]['actor']

    def book_of(c):
        if c['aid'] in info:
            return info[c['aid']]['book']
        return None

    def is_landed(b):
        if not b:
            return False
        f, ts = b
        return all((f, t if t.startswith('T') else 'T' + t) in landed for t in ts.split(','))

    tot = C.defaultdict(lambda: C.Counter())
    rec = C.defaultdict(lambda: C.Counter())
    per = C.defaultdict(lambda: C.Counter())
    ncalls = C.Counter(); nagents = C.defaultdict(set); models = C.defaultdict(C.Counter)
    for c in rows:
        a = actor_of(c); b = book_of(c)
        ncalls[a] += 1; nagents[a].add(c['aid']); models[a][c['model']] += 1
        for k in KINDS + ADV:
            tot[a][k] += c[k]
        where = 'landed' if is_landed(b) else ('booked, not landed' if b else 'unbooked')
        for k in KINDS:
            rec[(a, where)][k] += c[k]
        if is_landed(b):
            for k in KINDS + ADV:
                per[b][k] += c[k]
            per[b]['builder_side' if a in ('builder', 'repair builder') else 'review_side'] += sum(c[k] for k in KINDS)
    n = len(landed)
    print(f'# night-tokens.py {sys.argv[1]} {sys.argv[2]} {os.path.basename(ttout)}')
    print(f'window [{w0}Z, {w1}Z): {len(rows)} model calls (each message id once), {sum(len(v) for v in nagents.values())} '
          f'transcripts with a call; tasks landed (the T512 table of {os.path.basename(ttout)}): {n}')
    print(f'other main sessions in {PROJ} with a call in the window (page sessions): {len(others)} {others}')
    print()
    print('## Tokens by actor and kind (window totals; advisor calls apart)')
    print()
    print('| actor | transcripts | calls | output | fresh input | cache read | cache write | per landed task: output / cache read'
          ' | advisor out / in |')
    print('|---|---|---|---|---|---|---|---|---|')
    G = C.Counter()
    for a in ACTORS:
        t = tot[a]; G.update(t)
        print(f'| {a} | {len(nagents[a])} | {ncalls[a]} | {M(t["output"])} | {M(t["fresh_in"])} | {M(t["cache_read"])} | '
              f'{M(t["cache_write"])} | {K(t["output"] / n) if n else "-"} / {M(t["cache_read"] / n) if n else "-"} | '
              f'{M(t["adv_out"])} / {M(t["adv_in"])} |')
    print(f'| all | {sum(len(v) for v in nagents.values())} | {sum(ncalls.values())} | {M(G["output"])} | {M(G["fresh_in"])} | '
          f'{M(G["cache_read"])} | {M(G["cache_write"])} | {K(G["output"] / n) if n else "-"} / '
          f'{M(G["cache_read"] / n) if n else "-"} | {M(G["adv_out"])} / {M(G["adv_in"])} |')
    print()
    print('model mix (calls):', {a: dict(models[a]) for a in ACTORS if models[a]})
    print()
    print('## Reconciliation: each actor\'s total = booked to a landed task + booked to a task not landed + unbooked (output / cache read)')
    print()
    for a in ACTORS:
        parts = [(w, rec[(a, w)]) for w in ('landed', 'booked, not landed', 'unbooked')]
        s = C.Counter()
        for _, v in parts:
            s.update(v)
        ok = all(s[k] == tot[a][k] for k in KINDS)
        print(f'- {a}: ' + '; '.join(f'{w} {M(v["output"])} / {M(v["cache_read"])}' for w, v in parts) + f' (sums to total: {ok})')
    print()
    print('## Per landed task (booked: its builder(s) and the agents they and the session dispatched for it)')
    print()
    booked = [b for b in per]
    print(f'tasks landed with tokens booked: {len(booked)} of {n} (a bundle is one unit)')
    lines = [(landed[k]['test'], landed[k]['nontest']) for k in landed]
    if lines:
        print(f'task size (T512, added+deleted, a shared commit counted whole under each task it names, so totals double-count '
              f'{sum(1 for k in landed if landed[k]["shared"])} shared rows): test lines median {statistics.median(x for x, _ in lines)} '
              f'total {sum(x for x, _ in lines)}; non-test lines median {statistics.median(y for _, y in lines)} total '
              f'{sum(y for _, y in lines)}')
    for k in KINDS:
        v = [per[b][k] for b in booked]
        if v:
            print(f'- {k}: median {K(statistics.median(v))}, total {M(sum(v))} over the booked tasks')
    print()
    print('| task | test lines | non-test lines | output | fresh input | cache read | cache write | builder / review share |')
    print('|---|---|---|---|---|---|---|---|')
    for b in sorted(booked, key=lambda b: -per[b]['cache_read']):
        f, ts = b
        t0 = ts.split(',')[0]
        sz = landed.get((f, t0 if t0.startswith('T') else 'T' + t0), {})
        s = per[b]['builder_side'] + per[b]['review_side']
        print(f'| {f} {ts} | {sz.get("test", "-")} | {sz.get("nontest", "-")} | {per[b]["output"] / 1e3:,.1f}k | '
              f'{per[b]["fresh_in"] / 1e3:,.1f}k | {per[b]["cache_read"] / 1e3:,.1f}k | {per[b]["cache_write"] / 1e3:,.1f}k | '
              f'{100 * per[b]["builder_side"] / s if s else 0:.0f}% / {100 * per[b]["review_side"] / s if s else 0:.0f}% |')
    print()
    print('## Cross-check: the T512 table\'s own per-task booking, summed over its rows (builders + review agents + session)')
    T = C.Counter()
    for k in landed:
        T.update(landed[k]['t512'])
    B = C.Counter()
    for b in booked:
        B.update({k: per[b][k] for k in KINDS})
    print('- T512 rows: ' + ', '.join(f'{k} {M(T[k])}' for k in KINDS))
    print('- this script, booked to landed tasks (no session share): ' + ', '.join(f'{k} {M(B[k])}' for k in KINDS))
    print()
    print('## Audit: builders and repair builders matched, and agents booked through a parent or a description')
    for aid, a in sorted(info.items(), key=lambda x: (x[1]['actor'], str(x[1]['book']))):
        if a['actor'] in ('builder', 'repair builder'):
            print(f'- {a["actor"]} {aid[:10]} {a["book"]} KIND={a["kind"]} landed={is_landed(a["book"])}: {a["desc"]}')
    nb = C.Counter((a['actor'], 'via builder' if a.get('via') else ('by description' if a['book'] else 'unbooked'))
                   for a in info.values() if a['actor'] not in ('builder', 'repair builder'))
    print('- other agents\' booking:', dict(nb))
    if extract:
        with open(extract, 'w') as fh:
            fh.write('t\tagent\tactor\tagent_type\tbook\tlanded\tmodel\t' + '\t'.join(KINDS + ADV) + '\n')
            for c in sorted(rows, key=lambda c: c['t']):
                b = book_of(c)
                fh.write('\t'.join([c['t'], c['aid'], actor_of(c), str((info.get(c['aid']) or {}).get('type')),
                                    ' '.join(b) if b else '-', str(is_landed(b)), str(c['model'])]
                                   + [str(c[k]) for k in KINDS + ADV]) + '\n')


if __name__ == '__main__':
    main()
