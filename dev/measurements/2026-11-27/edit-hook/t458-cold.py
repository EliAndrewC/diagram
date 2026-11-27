# 451 T458: t443-cold.py with TWO binaries as interleaved arms (before: HEAD; after: HEAD + the PreToolUse screen), T373's sandbox.
#   python3 t458-cold.py <t373 sandbox> <dir holding before/ and after/, each with l7r-guard.good> <rounds> <out.tsv>
# Each round, for each arm in alternating order: the index deleted, a COLD call, then a WARM call; round 0 is a warm-up, not counted.
import os, statistics, subprocess, sys, time
S, B, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
W = S + '/w/diagram'; IDX = W + '/.clones/diagram-backlog/.git/l7r-events/reversal/451-time-retro-and-efficiency.idx'
def env(arm):
    return {'PATH': os.environ['PATH'], 'HOME': S + '/home', 'CLAUDE_PROJECT_DIR': W, 'CLONE_MAIN': W, 'L7R_GUARD_TARGET': f'{B}/{arm}',
            'L7R_GATE_TARGET': B + '/gate-target', 'GUARD_LOG_DIR': S + '/gl', 'MEASURE_STATE_DIR': S + '/ms', 'L7R_GUARD_TREE': W}
def run(arm):
    with open(f'{S}/payloads/wt.edit-doc.PreToolUse.json', 'rb') as f:
        t = time.perf_counter(); p = subprocess.run([f'{B}/{arm}/l7r-guard.good', '--only', 'event-log-hooks', 'PreToolUse'], stdin=f, capture_output=True, env=env(arm))
        return (time.perf_counter() - t) * 1e3, p.returncode, len(p.stdout) + len(p.stderr)
res = {(a, k): [] for a in ('before', 'after') for k in ('cold', 'warm')}; rcs, loads = set(), []
for i in range(n + 1):
    loads.append(float(open('/proc/loadavg').read().split()[0]))
    for arm in (('before', 'after') if i % 2 else ('after', 'before')):
        os.remove(IDX) if os.path.exists(IDX) else None
        c = run(arm); w = run(arm)
        if i: res[(arm, 'cold')].append(c[0]); res[(arm, 'warm')].append(w[0]); rcs |= {(c[1], c[2]), (w[1], w[2])}
q = lambda v, p: sorted(v)[min(len(v) - 1, int(round(p * (len(v) - 1))))]
with open(out, 'w') as o:
    o.write('arm\tstate\tn\tmedian_ms\tp90_ms\tmin_ms\tmax_ms\t(rc, output bytes)\tload1\n')
    for (a, k), v in res.items():
        o.write(f'{a}\t{k}\t{len(v)}\t{statistics.median(v):.1f}\t{q(v, .9):.1f}\t{min(v):.1f}\t{max(v):.1f}\t{sorted(rcs)}\t{min(loads):.2f}-{max(loads):.2f}\n')
print(open(out).read())
