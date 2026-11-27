# t383: T373's timer (t373-time.py) with TWO binaries, before and after, as interleaved arms of one run, in T373's throwaway world.
#   python3 t383-time.py <out.tsv> <rounds> <session: sess|wt> <t373 sandbox> <dir holding before/ and after/, each with l7r-guard.good>
# Every call: env -i plus PATH, HOME (the sandbox's scratch home), CLAUDE_PROJECT_DIR and CLONE_MAIN (the sandbox mirror),
# L7R_GUARD_TARGET (that arm's binary), L7R_GATE_TARGET, GUARD_LOG_DIR, MEASURE_STATE_DIR, and L7R_GUARD_TREE for a direct binary call.
# The sandbox clone is DIRTY for the run (T373's first table's state) and put back clean after.
import os, statistics, subprocess, sys, time

out, rounds, session, S, B = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
W = S + '/w/diagram'
C = W + '/.clones/diagram-backlog'
DIRTY = C + '/dev/measurements/2026-11-26/tmp-clutter/t365-glob.txt'
PAYLOAD = f'{S}/payloads/{session}.edit-doc.PreToolUse.json'


def env(arm):
    return {'PATH': os.environ['PATH'], 'HOME': S + '/home', 'CLAUDE_PROJECT_DIR': W, 'CLONE_MAIN': W, 'L7R_GUARD_TARGET': f'{B}/{arm}',
            'L7R_GATE_TARGET': B + '/gate-target', 'GUARD_LOG_DIR': S + '/gl', 'MEASURE_STATE_DIR': S + '/ms', 'L7R_GUARD_TREE': W}


def set_state(dirty):
    subprocess.run(['git', '-C', C, 'checkout', '-q', '--', os.path.relpath(DIRTY, C)], check=True)
    if dirty:
        open(DIRTY, 'a').write('t383 dirty\n')
    return subprocess.run(['git', '-C', C, 'status', '--porcelain'], capture_output=True, text=True).stdout


def run(argv, e):
    with open(PAYLOAD, 'rb') as f:
        t = time.perf_counter()
        p = subprocess.Popen(argv, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e)
        o, err = p.communicate()
        return (time.perf_counter() - t) * 1e3, p.returncode, len(o), len(err)


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(round(p * (len(v) - 1))))]


arms = []
for arm in ('before', 'after'):
    b = f'{B}/{arm}/l7r-guard.good'
    arms.append((f'{arm}: hook (launcher + binary)', [W + '/scripts/hooks/l7r-hook', 'PreToolUse'], env(arm)))
    arms.append((f'{arm}: binary, every guard', [b, 'PreToolUse'], env(arm)))
    arms.append((f'{arm}: --only event-log-hooks', [b, '--only', 'event-log-hooks', 'PreToolUse'], env(arm)))
    arms.append((f'{arm}: --only clone-sync-hooks', [b, '--only', 'clone-sync-hooks', 'PreToolUse'], env(arm)))
assert set_state(True).strip()
res = {a[0]: {'ms': [], 'rc': set(), 'out': set()} for a in arms}
loads = []
for i in range(rounds + 1):  # round 0 is the warm-up, not counted
    loads.append(float(open('/proc/loadavg').read().split()[0]))
    for label, argv, e in (arms if i % 2 == 0 else arms[::-1]):
        dt, rc, no, ne = run(argv, e)
        if i:
            r = res[label]
            r['ms'].append(dt); r['rc'].add(rc); r['out'].add((no, ne))
assert not set_state(False).strip()
with open(out, 'a') as f:
    for label, _, _ in arms:
        r = res[label]; v = r['ms']
        f.write('\t'.join([session, label, str(len(v)), f'{statistics.median(v):.1f}', f'{q(v, 0.9):.1f}', f'{min(v):.1f}', f'{max(v):.1f}',
                           ','.join(map(str, sorted(r['rc']))), ';'.join(f'{a}/{b}' for a, b in sorted(r['out'])), f'{min(loads):.2f}-{max(loads):.2f}']) + '\n')
