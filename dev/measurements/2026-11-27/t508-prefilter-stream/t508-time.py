#!/usr/bin/env python3
"""t508: the routes priced on the same arms - one Bash `true` call's hook CPU (RUSAGE_CHILDREN) for each scratch build of
t508-build.sh, over T507's fixtures (a COPY of the clone's state), interleaved, 2 warm-up rounds and <runs> counted.
usage: t508-time.py <scratch dir> <state copy> <t507 dir> [runs] [bins]
cases: bash-pre (record-edit-hooks PreToolUse) and bash-post (checks-hooks PostToolUse), each under a hold and with none.
Each build has its own fixture tree per arm (a hold's call may write its state). Every call's exit and stdout is compared across builds."""
import collections, importlib, os, statistics, sys
BASE, SRC, T507 = sys.argv[1], sys.argv[2], sys.argv[3]
RUNS = int(sys.argv[4]) if len(sys.argv) > 4 else 20
BINS = (sys.argv[5] if len(sys.argv) > 5 else 'clean,A,B,C').split(',')
sys.path.insert(0, T507)
fx_mod = importlib.import_module('t507-fixture')
CASES = {'bash-pre': ('record-edit-hooks', 'PreToolUse'), 'bash-post': ('checks-hooks', 'PostToolUse')}
fxs = {}
for b in BINS:
    for hold in (True, False):
        fx = fx_mod.fixture(BASE, f'{b}-{"hold" if hold else "nohold"}', SRC, hold=hold)
        fx_mod.call([f'{BASE}/b/bin/l7r-guard-{b}', '--only', 'record-edit-hooks', 'PreToolUse'], fx, fx_mod.bash_pre(fx, 'first'))
        fxs[(b, hold)] = fx
print(f'# load at start {os.getloadavg()[0]:.1f}, state copy {os.path.getsize(SRC)} bytes, {RUNS} counted runs, builds {BINS}')
cpu = collections.defaultdict(list)
outs = collections.defaultdict(set)
for i in range(RUNS + 2):
    for case, (guard, event) in CASES.items():
        for hold in (True, False):
            for b in BINS:
                fx = fxs[(b, hold)]
                payload = fx_mod.bash_pre(fx, i)
                if case == 'bash-post':
                    payload = dict(payload, hook_event_name='PostToolUse', tool_response={'stdout': '', 'stderr': ''})
                p, c = fx_mod.call([f'{BASE}/b/bin/l7r-guard-{b}', '--only', guard, event], fx, payload)
                outs[(case, hold)].add((p.returncode, p.stdout.replace(fx.encode(), b'FX')))
                if i >= 2:
                    cpu[(case, hold, b)].append(c)
print(f'# load at end {os.getloadavg()[0]:.1f}')
med = statistics.median
for case in CASES:
    for hold in (True, False):
        row = '\t'.join(f'{b} {med(cpu[(case, hold, b)]):.2f}' for b in BINS)
        base = med(cpu[(case, hold, 'clean')])
        save = '\t'.join(f'{b} {base - med(cpu[(case, hold, b)]):+.2f}' for b in BINS if b != 'clean')
        print(f'{case}\t{"hold" if hold else "nohold"}\tcpu median ms: {row}\tsaved vs clean: {save}\toutputs {len(outs[(case, hold)])} distinct')
