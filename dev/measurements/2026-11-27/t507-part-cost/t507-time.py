#!/usr/bin/env python3
"""t507: where a bash-pre call's CPU goes (record-edit-hooks PreToolUse on a Bash `true` under a plan hold, the steady state of a
hold: its snapshot already kept), split by the stamps build's in-process stamps, over copies of the state.

usage: t507-time.py <scratch dir> <state copy> [runs] [out dir] [case]   (binaries from t507-build.sh under <scratch dir>/b/bin/)
case: bash-pre (record-edit-hooks PreToolUse, the default) or bash-post (checks-hooks PostToolUse on the same call)
arms: a comma list (default: full,full-reread,padded,nodisp,floor); `nohold` and `nohold-nodisp` are full and nodisp with no hold
(`plan_holds` empty): any Bash call outside a plan hold, which pays the guard's prefilter alone
Arms, each its own fixture tree (`full-reread` shares `full`'s), run INTERLEAVED (2 warm-up rounds, then <runs> counted, every arm
once a round):
  full         the state copy as it is
  full-reread  the same, the stamps build reading the file a second time into the buffer the first read faulted in (T507_REREAD)
  padded       `dispatches` replaced by one string, the file the same byte count as full's: the same read and faults, little to scan
  nodisp       `dispatches` dropped (451 T490's 10.9 ms arm)
  floor        `dispatches`, `versions` and `seen` dropped: only what the partial read keeps as values
and full and nodisp on the clean build (HEAD, no stamps), to price the stamps.
Reported: per arm and build, the CPU median ms from RUSAGE_CHILDREN (the process, its `flock` child, its exit); per stamp interval,
the median over runs of that interval's process CPU (clock_gettime, ms), wall (ms) and minor faults, each interval SUMMED within a run
where its label pair repeats; the full - nodisp gap per interval. The first run's raw stamps of each arm go to t507-raw-<arm>.tsv."""
import collections, importlib, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
fx_mod = importlib.import_module('t507-fixture')

BASE, SRC = sys.argv[1], sys.argv[2]
RUNS = int(sys.argv[3]) if len(sys.argv) > 3 else 20
OUT = sys.argv[4] if len(sys.argv) > 4 else BASE
CASE = sys.argv[5] if len(sys.argv) > 5 else 'bash-pre'
GUARD, EVENT = {'bash-pre': ('record-edit-hooks', 'PreToolUse'), 'bash-post': ('checks-hooks', 'PostToolUse')}[CASE]
BIN = {'stamps': f'{BASE}/b/bin/l7r-guard-stamps', 'clean': f'{BASE}/b/bin/l7r-guard-clean'}
TREES = {
    'full': {},
    'padded': {'pad': ['dispatches']},
    'nodisp': {'strip': ['dispatches']},
    'floor': {'strip': ['dispatches', 'versions', 'seen']},
    'nohold': {'hold': False},
    'nohold-nodisp': {'strip': ['dispatches'], 'hold': False},
}
ALL = {'full': 'full', 'full-reread': 'full', 'padded': 'padded', 'nodisp': 'nodisp', 'floor': 'floor', 'nohold': 'nohold',
       'nohold-nodisp': 'nohold-nodisp'}
PICK = (sys.argv[6] if len(sys.argv) > 6 else 'full,full-reread,padded,nodisp,floor').split(',')
ARMS = {a: ALL[a] for a in PICK}
RUNS_OF = [(a, 'stamps') for a in ARMS] + [(a, 'clean') for a in ('full', 'nodisp', 'nohold', 'nohold-nodisp') if a in ARMS]
fxs = {t: fx_mod.fixture(BASE, t, SRC, **kw) for t, kw in TREES.items() if t in ARMS.values()}
STAMPS = os.path.join(BASE, 't507-stamps.tsv')


def one(arm, b, i):
    fx = fxs[ARMS[arm]]
    try:
        os.remove(STAMPS)
    except FileNotFoundError:
        pass
    env = None
    if b == 'stamps':
        env = {'T507_STAMPS': STAMPS}
        if arm == 'full-reread':
            env['T507_REREAD'] = '1'
    payload = fx_mod.bash_pre(fx, i)
    if CASE == 'bash-post':
        payload = dict(payload, hook_event_name='PostToolUse', tool_response={'stdout': '', 'stderr': ''})
    _, cpu = fx_mod.call([BIN[b], '--only', GUARD, EVENT], fx, payload, env=env)
    rows, raw = [], ''
    if b == 'stamps':
        raw = open(STAMPS).read().split('\n--')[0].strip()
        for line in raw.splitlines():
            label, wall, c, mi, ma = line.split('\t')
            rows.append((label, int(wall) / 1e6, int(c) / 1e6, int(mi), int(ma)))
    return cpu, rows, raw


for t in fxs:  # the hold's first call takes its snapshot (a bash-pre call, whatever the case)
    fx_mod.call([BIN['stamps'], '--only', 'record-edit-hooks', 'PreToolUse'], fxs[t], fx_mod.bash_pre(fxs[t], 'first'))
print(f'# case {CASE} ({GUARD} {EVENT}); load at start {os.getloadavg()[0]:.1f}, state copy {os.path.getsize(SRC)} bytes, {RUNS} counted runs an arm')
for t in fxs:
    print(f'# tree {t}: {os.path.getsize(fxs[t] + "/.git/checks-open.json")} bytes')
cpus = collections.defaultdict(list)
ivals = collections.defaultdict(lambda: collections.defaultdict(lambda: ([], [], [], [])))
keys = {}
for i in range(RUNS + 2):
    for arm, b in RUNS_OF:
        cpu, rows, raw = one(arm, b, i)
        if i < 2:
            continue
        cpus[(arm, b)].append(cpu)
        if not rows:
            continue
        if i == 2:
            with open(os.path.join(OUT, f't507-raw-{CASE}-{arm}.tsv'), 'w') as f:
                f.write('label\twall_ns\tcpu_ns\tminflt\tmajflt\n' + raw + '\n')
        run = collections.OrderedDict()
        prev = ('start', 0.0, 0.0, 0, 0)  # the first stamp, `main`: everything before main (exec, the loader, the runtime)
        for r in rows:
            k = f'{prev[0]}->{r[0]}'
            c, w, f, m = run.get(k, (0.0, 0.0, 0, 0))
            run[k] = (c + r[2] - prev[2], w + r[1] - prev[1], f + r[3] - prev[3], m + r[4] - prev[4])
            prev = r
        run['exit->reaped (rusage - last stamp)'] = (cpu - rows[-1][2], 0.0, 0, 0)
        run['TOTAL (rusage)'] = (cpu, 0.0, 0, 0)
        for k, vals in run.items():
            keys.setdefault(k, None)
            for lst, v in zip(ivals[arm][k], vals):
                lst.append(v)
print(f'# load at end {os.getloadavg()[0]:.1f}')
med = statistics.median
for (arm, b), v in cpus.items():
    print(f'{arm}\t{b}\tcpu median {med(v):.2f}\tmin {min(v):.2f}\tp90 {sorted(v)[int(len(v) * 0.9) - 1]:.2f}')
print()
print('interval\t' + '\t'.join(f'{a} cpu / wall / minflt' for a in ARMS) + '\tfull - nodisp cpu (or nohold - nohold-nodisp)')
for k in keys:
    cells = []
    for a in ARMS:
        c, w, f, m = ivals[a].get(k, ([], [], [], []))
        cells.append((f'{med(c):.2f} / {med(w):.2f} / {med(f):.0f}' + (f' maj{sum(m)}' if any(m) else '')) if c else '-')
    gap = ''
    if ivals['full'].get(k) and ivals['nodisp'].get(k):
        gap = f'{med(ivals["full"][k][0]) - med(ivals["nodisp"][k][0]):+.2f}'
    elif ivals['nohold'].get(k) and ivals['nohold-nodisp'].get(k):
        gap = f'{med(ivals["nohold"][k][0]) - med(ivals["nohold-nodisp"][k][0]):+.2f} (nohold - nohold-nodisp)'
    print(f'{k}\t' + '\t'.join(cells) + f'\t{gap}')
