"""461 T10: phase 1 (the builder's own hand-in, T05-T08, T43, T44) measured on the real work since it landed.

Usage (from the clone's root, or a pool worktree of it):
  python3 -I phase1.py extract W0 W1 DIR [--transcripts SUBAGENTS_DIR]   # keep the sources (no content) for a rerun
  python3 -I phase1.py figures W0 W1 [--kept DIR]

  W0, W1   UTC ISO bounds, half-open [W0, W1)

Sources (under the common git directory, read-only), or their kept extracts in DIR:
  builder-pool.log      `done` rows (`handed_in: true` from T08 on) are hand-ins; take/release replayed for trees held
  l7r-events/*.jsonl    the PreToolUse/PostToolUse rows of a `make builder-done` call: `by` is the agent that ran it (no `by`:
                        the coordinator), `id` the tool call; the `make land` Phase rows (night-figures.py's landings())
  l7r-events/samples/   the memory sampler's load1 and held
  SUBAGENTS_DIR         (extract only, optional) the session's subagent transcripts: each builder-done call's tool result,
                        found by its `id`, is classified (handed in / conflict / first-pass refusal / other) and the
                        refusal's reason lines kept - one short line each, no other content. The figures name this source
                        apart from the logs: the logs alone cannot say why a hand-in failed, or whether a conflict came first.

A call is a hand-in where a pool `done` row of the same task falls within [Pre - 5 s, Post + 60 s] (the Post row is written when
the call returns; the done row can lag it, T17's by 30 s). A call with no such row handed nothing in: refused or stopped on a
conflict, which the logs cannot tell apart.
"""
import collections as C
import gzip
import importlib.util
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    'nf', os.path.join(HERE, '..', '461-t01-night-tokens', 'night-figures.py'))
nf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nf)
ts, iso, opener = nf.ts, nf.iso, nf.opener

JOIN_BEFORE_S, JOIN_AFTER_S = 5, 60


def task_key(detail):
    """'461 T12' or '451 T528,T529' -> ('461', 'T12'), the first task names the hand-in."""
    f, _, ts_ = (detail or '').partition(' ')
    return f, ts_.replace(' ', ',').split(',')[0]


# ---- sources ---------------------------------------------------------------------------------------------------------------

def live_pool():
    return [json.loads(x) for x in open(f'{nf.common_dir()}/builder-pool.log') if x.strip()]


def live_calls(w0, w1):
    """builder-done tool calls: {id: {pre, post, by, task, feature}} from the event log."""
    calls = {}
    for f in sorted(os.listdir(f'{nf.common_dir()}/l7r-events')):
        if not f.endswith('.jsonl'):
            continue
        feat = f[:3]
        for line in open(f'{nf.common_dir()}/l7r-events/{f}', errors='replace'):
            if '"builder-done"' not in line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            # a command chaining makes logs the first as `make` and all in `makes` (T17's `make ledger-owed ... && make
            # builder-done`, 21:23:00Z): either names a builder-done call
            named = r.get('make') == 'builder-done' or 'builder-done' in (r.get('makes') or [])
            if not named or r.get('ev') not in ('PreToolUse', 'PostToolUse', 'BgEnd'):
                continue
            if not (w0 <= ts(r['t']) < w1) or not r.get('id'):
                continue
            c = calls.setdefault(r['id'], {'id': r['id'], 'feature': feat, 'by': r.get('by'), 'task': r.get('task')})
            c['by'] = c['by'] or r.get('by')
            c['task'] = c['task'] or r.get('task')
            c[{'PreToolUse': 'pre', 'PostToolUse': 'post', 'BgEnd': 'bgend'}[r['ev']]] = r['t']
            if r.get('bg'):
                c['bg'] = r['bg']
            if r['ev'] == 'BgEnd':
                c['exit'] = r.get('exit')
    return list(calls.values())


def classify_result(text):
    if 'handed in to the lane' in text:
        return 'handed in', []
    if 'with a conflict no rule resolves' in text:
        m = re.search(r'with a conflict no rule resolves: (.*?) - resolve by hand', text, re.S)
        parts = re.split(r', (?=[\w./-]+ \()', m.group(1)) if m else []
        by_hand = [p.split(' (')[0] for p in parts if 'its rule would resolve it' not in p]
        by_rule = [p.split(' (')[0] for p in parts if 'its rule would resolve it' in p]
        return 'conflict', [f'by hand: {", ".join(by_hand) or "-"}', f'by rule: {", ".join(by_rule) or "-"}']
    if 'refused by the first pass' in text:
        tail = text.split('):', 1)[-1] if '):' in text else text
        reasons = [x.strip()[:200] for x in tail.splitlines()
                   if x.strip() and not x.startswith('make:') and not x.strip().startswith('A case that is')]
        return 'first-pass refusal', reasons
    last = [x for x in text.strip().splitlines() if x.strip()]
    return 'other', [last[-1][:200]] if last else []


def transcript_outcomes(subdir, ids):
    """{tool_use_id: (outcome, reason lines)} for the calls named, read from the subagent transcripts."""
    out = {}
    for f in os.listdir(subdir):
        if not f.endswith('.jsonl'):
            continue
        for line in open(os.path.join(subdir, f), errors='replace'):
            if '"tool_result"' not in line or not any(i in line for i in ids):
                continue
            d = json.loads(line)
            for b in d.get('message', {}).get('content') or []:
                if isinstance(b, dict) and b.get('type') == 'tool_result' and b.get('tool_use_id') in ids:
                    t = b.get('content')
                    t = t if isinstance(t, str) else ' '.join(x.get('text', '') for x in t if isinstance(x, dict))
                    out[b['tool_use_id']] = classify_result(t)
    return out


def extract(w0s, w1s, d, subdir=None):
    w0, w1 = ts(w0s), ts(w1s)
    os.makedirs(d, exist_ok=True)
    with gzip.open(f'{d}/pool.jsonl.gz', 'wt') as f:
        for r in live_pool():
            if ts(r['utc']) < w1:
                f.write(json.dumps(r) + '\n')
    calls = live_calls(w0, w1)
    if subdir:
        oc = transcript_outcomes(subdir, {c['id'] for c in calls if c.get('by')})
        for c in calls:
            if c['id'] in oc:
                c['outcome'], c['reasons'] = oc[c['id']]
    with gzip.open(f'{d}/calls.jsonl.gz', 'wt') as f:
        for c in sorted(calls, key=lambda c: c.get('pre') or c.get('post')):
            f.write(json.dumps(c) + '\n')
    phases = C.Counter()
    for f in sorted(os.listdir(f'{nf.common_dir()}/l7r-events')):
        if f.endswith('.jsonl'):
            for line in open(f'{nf.common_dir()}/l7r-events/{f}', errors='replace'):
                if '"make":"builder-done"' in line and '"ev":"Phase"' in line:
                    r = json.loads(line)
                    if w0 <= ts(r['t']) < w1:
                        phases[f"{r['t'][:19]}Z {r.get('src')} {r.get('step')}"] += 1
    with gzip.open(f'{d}/phases.jsonl.gz', 'wt') as f:   # what a hand-in ran: one row per (second, src, step)
        for k, v in sorted(phases.items()):
            f.write(json.dumps({'t': k.split()[0], 'src': k.split()[1], 'step': k.split()[2], 'n': v}) + '\n')
    with gzip.open(f'{d}/land.jsonl.gz', 'wt') as f:
        for r in nf.land_rows(None, w0, w1):
            f.write(json.dumps(r) + '\n')
    with gzip.open(f'{d}/samples.tsv.gz', 'wt') as f:
        f.write('utc\tload1\tcores\theld\n')
        for t, load, cores, held in nf.sample_rows(None):
            if w0 <= t < w1:
                f.write(f'{iso(t)}\t{load}\t{cores}\t{held}\n')
    print(f'kept: {d}/pool.jsonl.gz, calls.jsonl.gz ({len(calls)} calls'
          f'{", outcomes from " + subdir if subdir else ""}), land.jsonl.gz, samples.tsv.gz')


# ---- figures ---------------------------------------------------------------------------------------------------------------

def figures(w0s, w1s, kept=None):
    w0, w1 = ts(w0s), ts(w1s)
    if kept:
        pool = [json.loads(x) for x in opener(f'{kept}/pool.jsonl.gz') if x.strip()]
        calls = [json.loads(x) for x in opener(f'{kept}/calls.jsonl.gz') if x.strip()]
        calls = [c for c in calls if w0 <= ts(c.get('pre') or c['post']) < w1]
    else:
        pool, calls = live_pool(), live_calls(w0, w1)
    print(f'# 461 T10: phase 1 on real work, {w0s} to {w1s} ({(w1 - w0) / 3600:.2f} h wall)')
    print(f'source: {"the kept extracts in " + kept if kept else "the live sources under " + nf.common_dir()}')

    # -- hand-ins: the pool's done rows, joined to the calls that wrote them
    dones = [r for r in pool if r['event'] == 'done' and w0 <= ts(r['utc']) < w1]
    calls = [c for c in calls if c.get('task') or c.get('post')]
    for c in calls:
        c['done'] = None
    # each done row goes to the LATEST call of its task whose span holds it: a refused call and its rerun can both span one
    # done row (T17: refused 21:22:24-21:22:51Z, rerun 21:23:00-21:23:21Z, done 21:23:21Z)
    used = set()
    for i, r in enumerate(dones):
        t, task = ts(r['utc']), task_key(r['detail'])[1]
        cands = [c for c in calls if not c['done'] and (not c.get('task') or c['task'] == task)
                 and ts(c.get('pre') or c['post']) - JOIN_BEFORE_S <= t
                 <= ts(c.get('post') or c.get('bgend') or c['pre']) + JOIN_AFTER_S]
        if cands:
            max(cands, key=lambda c: ts(c.get('pre') or c['post']))['done'] = r
            used.add(i)
    print('\n## Hand-ins (the pool log\'s `done` rows; who ran each from the event log\'s builder-done call)')
    hi = [r for r in dones if r.get('handed_in')]
    print(f'pool done rows: {len(dones)}, of them `"handed_in": true`: {len(hi)}')
    by_builder = [c for c in calls if c['done'] and c.get('by')]
    by_coord = [c for c in calls if c['done'] and not c.get('by')]
    print(f'  run by a builder: {len(by_builder)}; run by the coordinator: {len(by_coord)}; '
          f'done rows no call explains: {len(dones) - len(used)}')
    for i, r in enumerate(dones):
        if i not in used:
            print(f'    unexplained done row: {r["utc"]} {r["detail"]} handed_in={r.get("handed_in")}')
    tasks = C.Counter(r['detail'] for r in hi)
    print(f'  distinct tasks (or bundles) handed in: {len(tasks)}; handed in more than once: '
          + (', '.join(f'{k} x{v}' for k, v in sorted(tasks.items()) if v > 1) or 'none'))

    # -- calls that handed nothing in
    print('\n## builder-done calls that handed nothing in (a call with no `done` row of its task in its span)')
    bcalls = [c for c in calls if c.get('by')]
    failed = [c for c in bcalls if not c['done']]
    print(f'builder calls: {len(bcalls)}; handed in: {len(bcalls) - len(failed)}; handed nothing in: {len(failed)} '
          f'({len(failed) / len(bcalls):.0%} of calls)' if bcalls else 'builder calls: 0')
    ftasks = {(c['feature'], c['task']) for c in failed}
    btasks = {(c['feature'], c['task']) for c in bcalls}
    print(f'  tasks whose builder ran it: {len(btasks)}; of them with at least one call that handed nothing in: {len(ftasks)}')
    outcomes = C.Counter()
    for c in sorted(failed, key=lambda c: c['pre']):
        later = [x for x in bcalls if x['done'] and x['task'] == c['task'] and x['feature'] == c['feature']
                 and ts(x['pre']) > ts(c['pre'])]
        nxt = later[0] if later else None
        then = ('then handed in ' + nxt['done']['utc'][11:19] + (' by the same builder' if nxt['by'] == c['by']
                                                               else ' by another agent')) if nxt else 'not handed in since'
        oc = c.get('outcome', '(no transcript outcome kept)')
        outcomes[oc] += 1
        print(f'  {c["pre"][11:19]} {c["feature"]} {c["task"]} by {c["by"][:8]}: {oc}; {then}')
        for x in c.get('reasons', []):
            print(f'      {x}')
    print('  outcomes (the transcripts, a second source): ' + ', '.join(f'{k} {v}' for k, v in sorted(outcomes.items())))
    conflicts = [c for c in failed if c.get('outcome') == 'conflict']
    same = [c for c in conflicts if any(x['done'] and x['by'] == c['by'] and x['task'] == c['task']
                                        and ts(x['pre']) > ts(c['pre']) for x in bcalls)]
    print(f'  conflicts: {len(conflicts)}; resolved and handed in by the same builder: {len(same)}')
    oc_in = C.Counter(c.get('outcome', '(none)') for c in bcalls if c['done'])
    print('  the handed-in calls\' own outcome, cross-check: ' + ', '.join(f'{k} {v}' for k, v in sorted(oc_in.items())))

    if kept and os.path.exists(f'{kept}/phases.jsonl.gz'):
        ph = C.Counter()
        for x in opener(f'{kept}/phases.jsonl.gz'):
            r = json.loads(x)
            if w0 <= ts(r['t']) < w1:
                ph[f"{r['src']} {r['step']}"] += r['n']
        print('  what the hand-ins ran (the event log\'s Phase rows written under make builder-done): '
              + ', '.join(f'{k} {v}' for k, v in sorted(ph.items())) + '; a coverage step (rust cover-build or cover-run): '
              + str(sum(v for k, v in ph.items() if k.startswith('rust cover'))))

    # -- landings
    att = nf.landings(nf.land_rows(kept, w0, w1))
    print('\n## Landing attempts (the event log\'s `make land` rows; night-figures.py landings())')
    for k in ('attempts', 'landed', 'landed, gate ran', 'landed, no gate (nothing owed one)', 'refused before a gate',
              'gate red', 'gate green, refused after it (tick or push)'):
        print(f'{k}: {att[k]}')
    lr = nf.land_rows(kept, w0, w1)
    for e in (r for r in lr if r['step'] == 'end'):
        g = [x for x in lr if x['step'] == 'gate' and x['sid'] == e['sid'] and x['clone'] == e['clone']
             and ts(e['t0']) <= ts(x['t0']) and ts(x['t1']) <= ts(e['t1'])]
        print(f'  {e["t1"][11:19]} {os.path.basename(e["clone"])} landed={e.get("landed")} gate='
              f'{",".join(str(x["code"]) for x in g) or "none"} ({sum(ts(x["t1"]) - ts(x["t0"]) for x in g):.0f} s) '
              f'tasks={" ".join(e.get("tasks") or [])}')
    landed_tasks = sum(len(e.get('tasks') or []) for e in lr if e['step'] == 'end' and e.get('landed'))
    print(f'tasks landed by those attempts: {landed_tasks}')

    # -- concurrency (FR-010)
    # the lane's own tree (adopted `lane` 21:08:09Z) is no builder's: night-figures.py leaves it out since 461 T59
    tree_h, held, per = nf.concurrency(pool, w0, w1)
    _, held_all, _ = nf.concurrency(pool, w0, w1, lane=True)
    print('\n## Concurrency (FR-010)')
    print(f'trees held, time-weighted (pool log, the lane tree left out): {held:.2f}; with it: {held_all:.2f}')
    print(f'tree-hours held: {tree_h:.2f} - ' + ', '.join(
        f'{os.path.basename(t)} {h:.2f} h ({h / ((w1 - w0) / 3600):.0%})' for t, h in sorted(per.items()) if h))
    lf = nf.load_figures(nf.sample_rows(kept), w0, w1)
    if lf:
        print(f'sampler: {lf["samples"]} samples, {lf["first"]} to {lf["last"]}, {lf["gaps"]} gap(s) over 120 s')
        print(f'median load: {lf["load_median"]:.1f} on {lf["cores"]:.0f} cores ({lf["load_median"] / lf["cores"]:.2f}x)')
        print(f'cross-check, the sampler\'s held: mean {lf["held_mean"]:.2f}, median {lf["held_median"]:.0f}')
    print(f'LIKE the night (night-figures.py\'s rule: >= {nf.LIKE_MIN_H} h wall, trees held 3.19 +- {nf.LIKE_TREES_BAND}, '
          f'load 14.1 x {nf.LIKE_LOAD_BAND}): ' + ('yes' if (w1 - w0) / 3600 >= nf.LIKE_MIN_H and abs(held - 3.19)
                                                   <= nf.LIKE_TREES_BAND and lf and nf.LIKE_LOAD_BAND[0] * 14.1 <=
                                                   lf['load_median'] <= nf.LIKE_LOAD_BAND[1] * 14.1 else 'no'))


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'extract':
        sub = args[args.index('--transcripts') + 1] if '--transcripts' in args else None
        extract(args[0], args[1], args[2], sub)
    elif cmd == 'figures':
        figures(args[0], args[1], args[args.index('--kept') + 1] if '--kept' in args else None)
    else:
        sys.exit(__doc__)
