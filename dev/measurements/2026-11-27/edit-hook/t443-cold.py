# 451 T443: the after binary's event-log-hooks on a COLD index (deleted before each call) against WARM calls, interleaved, T373's sandbox.
import os, statistics, subprocess, sys, time
S, B, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
W = S + '/w/diagram'; IDX = W + '/.clones/diagram-backlog/.git/l7r-events/reversal/451-time-retro-and-efficiency.idx'
env = {'PATH': os.environ['PATH'], 'HOME': S + '/home', 'CLAUDE_PROJECT_DIR': W, 'CLONE_MAIN': W, 'L7R_GUARD_TARGET': B + '/after',
       'L7R_GATE_TARGET': B + '/gate-target', 'GUARD_LOG_DIR': S + '/gl', 'MEASURE_STATE_DIR': S + '/ms', 'L7R_GUARD_TREE': W}
def run():
    with open(f'{S}/payloads/wt.edit-doc.PreToolUse.json', 'rb') as f:
        t = time.perf_counter(); p = subprocess.run([B + '/after/l7r-guard.good', '--only', 'event-log-hooks', 'PreToolUse'], stdin=f, capture_output=True, env=env)
        return (time.perf_counter() - t) * 1e3, p.returncode, len(p.stdout) + len(p.stderr)
cold, warm, rcs, loads = [], [], set(), []
for i in range(n + 1):
    loads.append(float(open('/proc/loadavg').read().split()[0]))
    os.remove(IDX) if os.path.exists(IDX) else None
    c = run(); w = run()
    if i: cold.append(c[0]); warm.append(w[0]); rcs |= {(c[1], c[2]), (w[1], w[2])}
q = lambda v, p: sorted(v)[min(len(v) - 1, int(round(p * (len(v) - 1))))]
for k, v in (('cold (index deleted first)', cold), ('warm (the next call)', warm)):
    print(f'wt\tafter: --only event-log-hooks, {k}\t{len(v)}\t{statistics.median(v):.1f}\t{q(v, .9):.1f}\t{min(v):.1f}\t{max(v):.1f}\t{sorted(rcs)}\t{min(loads):.2f}-{max(loads):.2f}')
