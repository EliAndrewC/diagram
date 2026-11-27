"""461 T02 (plan D12, FR-006/FR-007/FR-010): D12's figures other than tokens, a window's concurrency, and the likeness test.

Usage (from the clone's root; KEPT is a directory of extracts this script wrote, read in place of the live sources):
  python3 -I night-figures.py figures W0 W1 TASK_TIME_OUT [--kept DIR] [--json OUT.json]
  python3 -I night-figures.py extract W0 W1 DIR      # keep the night's sources (no content) for a rerun once they are gone
  python3 -I night-figures.py like REF.json W0 [W1] [--kept DIR] [--samples FILE ...]

  W0, W1          UTC ISO bounds, e.g. 2026-11-27T04:30:00Z 2026-11-27T14:29:00Z (half-open [W0, W1))
  TASK_TIME_OUT   a `make task-time SINCE=W0 UNTIL=W1` output, or its kept cut: tasks landed, the cross-blocking row and the
                  landings' side are read from its header
  REF.json        `figures --json` of the reference window (the night: ref-0430-1429.json beside this script)

Sources, all under the common git directory (`git rev-parse --git-common-dir`, so a pool worktree reads the clone's):
  builder-pool.log                       replayed from its first line: `take`, `make` and an `adopt` naming a task hold a
                                         tree; `release`, `landed` and an `adopt` of `free` free it
  l7r-events/*.jsonl                     the `make land` Phase rows: each `end` row is one landing attempt; the `gate` row
                                         inside its span says the gate ran, and its code whether it was red
  l7r-events/samples/mem-samples*.jsonl  the memory sampler: `load1` (the median over the window is the machine's load) and
                                         `held` (the trees held at the sample: a cross-check of the pool log's replay)

The likeness test (plan D12; phase 5 reruns it): a window is LIKE the reference when its wall span is at least LIKE_MIN_H hours,
its time-weighted trees held is within LIKE_TREES_BAND of the reference's, and its median load is within LIKE_LOAD_BAND times
the reference's. With W0 only, it scans ends from W0 + LIKE_MIN_H in 10-minute steps to the last sample and reports the
first LIKE window. The three knobs are GUESSes (plan's knob table) and each may be overridden from the environment.
"""
import collections as C
import datetime as D
import glob
import gzip
import json
import os
import re
import statistics
import subprocess
import sys

# The likeness knobs: GUESS, plan D12 and its knob table. "Eight hours or more of builder work" is read as a WALL span of
# eight hours (tree-hours held printed beside it): the plan is silent between the two, and the wall span is the plain reading.
LIKE_MIN_H = float(os.environ.get('LIKE_MIN_H', '8'))
LIKE_TREES_BAND = float(os.environ.get('LIKE_TREES_BAND', '0.5'))
LIKE_LOAD_BAND = tuple(float(x) for x in os.environ.get('LIKE_LOAD_BAND', '0.75,1.25').split(','))
STEP_S = 600


def ts(s):
    return D.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def iso(t):
    return D.datetime.fromtimestamp(t, D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def common_dir():
    return subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True,
                          text=True, check=True).stdout.strip()


def opener(p):
    return gzip.open(p, 'rt') if p.endswith('.gz') else open(p, errors='replace')


# ---- sources: live, or the kept extracts -------------------------------------------------------------------------------

def pool_rows(kept):
    p = f'{kept}/pool.jsonl.gz' if kept else f'{common_dir()}/builder-pool.log'
    return [json.loads(line) for line in opener(p) if line.strip()]


def land_rows(kept, w0, w1):
    if kept:
        rows = (json.loads(line) for line in opener(f'{kept}/land.jsonl.gz') if line.strip())
        return [r for r in rows if w0 <= ts(r['t']) < w1]
    out = []
    for f in sorted(glob.glob(f'{common_dir()}/l7r-events/*.jsonl')):
        for line in opener(f):
            if '"make":"land"' not in line or '"src":"land"' not in line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get('ev') == 'Phase' and w0 <= ts(r['t']) < w1:
                out.append({k: r.get(k) for k in ('step', 't0', 't1', 't', 'code', 'landed', 'sid', 'clone', 'tasks')})
    return out


def sample_rows(kept, files=None):
    if kept and not files:
        files = [f'{kept}/samples.tsv.gz']
    if not files:
        files = sorted(glob.glob(f'{common_dir()}/l7r-events/samples/mem-samples*.jsonl'))
    out = []
    for f in files:
        for line in opener(f):
            if f.endswith('.tsv.gz') or f.endswith('.tsv'):
                if line.startswith('utc'):
                    continue
                u, load, cores, held = line.rstrip('\n').split('\t')
                out.append((ts(u), float(load), int(cores), int(held)))
            else:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                out.append((ts(r['utc']), float(r['load1']), int(r['cores']), len(r.get('held') or [])))
    return sorted(set(out))


# ---- the figures ---------------------------------------------------------------------------------------------------------

def held_spans(rows):
    """Replay the pool log from its first line: per tree, the [start, end) spans it was held, and by what."""
    state, spans = {}, C.defaultdict(list)
    for r in rows:
        t, tree, ev, det = ts(r['utc']), r['tree'], r['event'], r.get('detail', '')
        hold = ev in ('take', 'make') or (ev == 'adopt' and det != 'free')
        free = ev in ('release', 'landed') or (ev == 'adopt' and det == 'free')
        if hold:
            if tree in state:                       # a take over a held tree closes the old span
                spans[tree].append((state[tree][0], t, state[tree][1]))
            state[tree] = (t, det)
        elif free and tree in state:
            spans[tree].append((state[tree][0], t, state[tree][1]))
            del state[tree]
    return spans, state


def concurrency(rows, w0, w1):
    spans, open_ = held_spans(rows)
    per = {}
    for tree in set(spans) | set(open_):
        L = list(spans.get(tree, []))
        if tree in open_:
            L.append((open_[tree][0], float('inf'), open_[tree][1]))
        per[tree] = sum(max(0.0, min(e, w1) - max(s, w0)) for s, e, _ in L) / 3600
    tree_h = sum(per.values())
    return tree_h, tree_h / ((w1 - w0) / 3600), per


def load_figures(samples, w0, w1):
    S = [s for s in samples if w0 <= s[0] < w1]
    if not S:
        return None
    gaps = sum(1 for a, b in zip(S, S[1:]) if b[0] - a[0] > 120)
    return {'samples': len(S), 'first': iso(S[0][0]), 'last': iso(S[-1][0]),
            'load_median': statistics.median(s[1] for s in S), 'cores': statistics.median(s[2] for s in S),
            'held_mean': statistics.mean(s[3] for s in S), 'held_median': statistics.median(s[3] for s in S),
            'gaps': gaps}


def landings(rows):
    """Each `end` row is one attempt; the `gate` row in its span (same session and clone) says whether the gate ran."""
    gates = [r for r in rows if r['step'] == 'gate']
    att = C.Counter()
    for e in (r for r in rows if r['step'] == 'end'):
        a, b = ts(e['t0']), ts(e['t1'])
        g = [x for x in gates if x['sid'] == e['sid'] and x['clone'] == e['clone'] and a <= ts(x['t0']) and ts(x['t1']) <= b]
        att['attempts'] += 1
        if e.get('landed'):
            att['landed'] += 1
            att['landed, gate ran' if g else 'landed, no gate (nothing owed one)'] += 1
        elif not g:
            att['refused before a gate'] += 1
        elif any(x['code'] for x in g):
            att['gate red'] += 1
        else:
            att['gate green, refused after it (tick or push)'] += 1
    return att


def task_time_header(path):
    txt = ''.join(open(path).readlines()[:12])
    num = r'([\d.]+)'
    out = {'tasks_landed': int(re.search(r'\((\d+) tasks landed\)', txt).group(1))}
    m = re.search(rf"the tasks' side {num} min, {num} min blocking \({num} of it a task waiting on a landing\)", txt)
    out['tasks_side_min'], out['tasks_side_blocking'], out['cross_blocking'] = map(float, m.groups())
    m = re.search(rf"the landings' side \(every batch landing and every carry\) {num} min, {num} min blocking", txt)
    out['landings_side_min'], out['landings_side_blocking'] = map(float, m.groups())
    return out


def figures(w0s, w1s, tt, kept=None, jout=None):
    w0, w1 = ts(w0s), ts(w1s)
    hdr = task_time_header(tt)
    tree_h, held, per = concurrency(pool_rows(kept), w0, w1)
    lf = load_figures(sample_rows(kept), w0, w1)
    att = landings(land_rows(kept, w0, w1))
    print(f'# 461 T02: D12 figures, {w0s} to {w1s} ({(w1 - w0) / 3600:.2f} h wall)')
    print(f'source: {"the kept extracts in " + kept if kept else "the live sources under " + common_dir()}; task-time: {tt}')
    print('\n## Throughput (task-time header; the pool log replayed from its first line)')
    print(f'tasks landed: {hdr["tasks_landed"]}')
    print(f'tree-hours held (builder hours): {tree_h:.2f} - ' +
          ', '.join(f'{os.path.basename(t)} {h:.2f} h ({h / ((w1 - w0) / 3600):.0%})' for t, h in sorted(per.items()) if h))
    print(f'landed per tree-hour held: {hdr["tasks_landed"] / tree_h:.2f}')
    print('\n## Blocking (task-time header)')
    print(f'cross-blocking (a task waited on a landing): {hdr["cross_blocking"]} min of the tasks\' side\'s '
          f'{hdr["tasks_side_blocking"]} blocking ({hdr["tasks_side_min"]} min working)')
    print(f'landings\' side: {hdr["landings_side_blocking"]} blocking of {hdr["landings_side_min"]} min')
    print('\n## Landing attempts (the event log\'s `make land` rows)')
    for k in ('attempts', 'landed', 'landed, gate ran', 'landed, no gate (nothing owed one)', 'refused before a gate',
              'gate red', 'gate green, refused after it (tick or push)'):
        print(f'{k}: {att[k]}')
    print('\n## Concurrency (FR-010)')
    print(f'trees held, time-weighted (pool log): {held:.2f}')
    if lf:
        print(f'sampler: {lf["samples"]} samples, {lf["first"]} to {lf["last"]}, {lf["gaps"]} gap(s) over 120 s')
        print(f'median load: {lf["load_median"]:.1f} on {lf["cores"]:.0f} cores ({lf["load_median"] / lf["cores"]:.2f}x)')
        print(f'cross-check, the sampler\'s held: mean {lf["held_mean"]:.2f}, median {lf["held_median"]:.0f}')
    else:
        print('sampler: no samples in the window')
    if jout:
        ref = {'w0': w0s, 'w1': w1s, 'trees_held': round(held, 3), 'tree_hours': round(tree_h, 2),
               'load_median': lf and lf['load_median'], 'cores': lf and lf['cores'], **hdr, 'landings': dict(att)}
        json.dump(ref, open(jout, 'w'), indent=1)
        print(f'\nreference written: {jout}')


def extract(w0s, w1s, d):
    w0, w1 = ts(w0s), ts(w1s)
    os.makedirs(d, exist_ok=True)
    with gzip.open(f'{d}/pool.jsonl.gz', 'wt') as f:
        for r in pool_rows(None):
            if ts(r['utc']) < w1:
                f.write(json.dumps(r) + '\n')
    with gzip.open(f'{d}/land.jsonl.gz', 'wt') as f:
        for r in land_rows(None, w0, w1):
            f.write(json.dumps(r) + '\n')
    with gzip.open(f'{d}/samples.tsv.gz', 'wt') as f:
        f.write('utc\tload1\tcores\theld\n')
        for t, load, cores, held in sample_rows(None):
            if w0 <= t < w1:
                f.write(f'{iso(t)}\t{load}\t{cores}\t{held}\n')
    print(f'kept: {d}/pool.jsonl.gz, land.jsonl.gz, samples.tsv.gz')


# ---- the likeness test ---------------------------------------------------------------------------------------------------

def like_one(ref, rows, samples, w0, w1):
    tree_h, held, _ = concurrency(rows, w0, w1)
    lf = load_figures(samples, w0, w1)
    span = (w1 - w0) / 3600
    miss = []
    if span < LIKE_MIN_H:
        miss.append(f'span {span:.2f} h < {LIKE_MIN_H:g} h')
    if abs(held - ref['trees_held']) > LIKE_TREES_BAND:
        miss.append(f'trees held {held:.2f} not within {LIKE_TREES_BAND:g} of {ref["trees_held"]:.2f}')
    load = lf['load_median'] if lf else None
    lo, hi = LIKE_LOAD_BAND[0] * ref['load_median'], LIKE_LOAD_BAND[1] * ref['load_median']
    if load is None:
        miss.append('no sampler samples in the window')
    elif not lo <= load <= hi:
        miss.append(f'median load {load:.1f} outside {lo:.1f} to {hi:.1f}')
    return {'w0': iso(w0), 'w1': iso(w1), 'span_h': span, 'tree_hours': tree_h, 'trees_held': held, 'load': load,
            'like': not miss, 'miss': miss}


def show(r, ref):
    load = 'none' if r['load'] is None else f'{r["load"]:.1f}'
    print(f'{"LIKE" if r["like"] else "NOT LIKE"}: {r["w0"]} to {r["w1"]} - span {r["span_h"]:.2f} h, '
          f'tree-hours held {r["tree_hours"]:.2f}, trees held {r["trees_held"]:.2f} (reference {ref["trees_held"]:.2f}), '
          f'median load {load} (reference {ref["load_median"]:.1f})' + ('' if r['like'] else ' - missed: ' + '; '.join(r['miss'])))


def like(argv):
    kept, files, pos = None, [], []
    i = 0
    while i < len(argv):
        if argv[i] == '--kept':
            kept = argv[i + 1]; i += 2
        elif argv[i] == '--samples':
            i += 1
            while i < len(argv) and not argv[i].startswith('--'):
                files.append(argv[i]); i += 1
        else:
            pos.append(argv[i]); i += 1
    ref = json.load(open(pos[0]))
    rows, samples = pool_rows(kept), sample_rows(kept, files or None)
    print(f'knobs (GUESS, plan D12): LIKE_MIN_H={LIKE_MIN_H:g} (wall hours), LIKE_TREES_BAND={LIKE_TREES_BAND:g}, '
          f'LIKE_LOAD_BAND={LIKE_LOAD_BAND[0]:g},{LIKE_LOAD_BAND[1]:g}; reference {ref["w0"]} to {ref["w1"]}')
    w0 = ts(pos[1])
    if len(pos) > 2:
        r = like_one(ref, rows, samples, w0, ts(pos[2]))
        show(r, ref)
        return 0 if r['like'] else 1
    last = samples[-1][0] if samples else w0
    e = w0 + LIKE_MIN_H * 3600
    tried = 0
    while e <= last:
        r = like_one(ref, rows, samples, w0, e)
        tried += 1
        if r['like']:
            show(r, ref)
            print(f'the first like window from {iso(w0)} ({tried} ends tried, {STEP_S // 60}-minute steps)')
            return 0
        e += STEP_S
    print(f'NOT LIKE: no window from {iso(w0)} to the last sample {iso(last)} passes ({tried} ends tried)')
    if tried:
        show(like_one(ref, rows, samples, w0, last), ref)
    return 1


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'figures':
        kept = args[args.index('--kept') + 1] if '--kept' in args else None
        jout = args[args.index('--json') + 1] if '--json' in args else None
        figures(args[0], args[1], args[2], kept, jout)
    elif cmd == 'extract':
        extract(*args[:3])
    elif cmd == 'like':
        sys.exit(like(args))
    else:
        sys.exit(__doc__)
