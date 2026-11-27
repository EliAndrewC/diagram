# t386: time `l7r-guard --only clone-sync-hooks PreToolUse` on a clean clone's Edit, the live claim map and sessions directory copied,
# arms interleaved after one warm-up round.
#   python3 t386-time.py <scratch dir> <rounds> <bin> [<bin> ...]
# The scratch dir holds: main/ (a no-checkout clone of /diagram), main/.clones/diagram-backlog (a checked-out clone, clean),
# main/.clones/.session-clones (the live map, 2,868 files, the 130 non-live claims of diagram-backlog rewritten to the scratch clone),
# sess/ (a copy of ~/.claude/sessions), payload.json (the Edit) and the binaries.
import os, subprocess, sys, time
S, rounds, bins = os.path.abspath(sys.argv[1]), int(sys.argv[2]), sys.argv[3:]
ENV = {'PATH': os.environ['PATH'], 'HOME': os.environ['HOME'], 'CLONE_MAIN': S + '/main', 'CLONE_SESSIONS_DIR': S + '/sess',
       'L7R_GUARD_TREE': '/diagram/.clones/diagram-backlog-t270', 'GUARD_LOG_DIR': S + '/gl', 'MEASURE_STATE_DIR': S + '/ms'}
payload = open(S + '/payload.json', 'rb').read()
def q(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(round(p * (len(v) - 1))))]
times = {b: [] for b in bins}; outs = {}
load0 = os.getloadavg()[0]
for r in range(rounds + 1):
    for b in bins:
        t = time.perf_counter()
        done = subprocess.run([S + '/' + b, '--only', 'clone-sync-hooks', 'PreToolUse'], input=payload, capture_output=True, env=ENV)
        dt = (time.perf_counter() - t) * 1e3
        if r: times[b].append(dt)
        outs[b] = (done.returncode, done.stdout[:200], done.stderr[:200])
load1 = os.getloadavg()[0]
for b in bins:
    v = times[b]
    print(f"{b}\tn={len(v)}\tmedian={q(v,.5):.1f}\tp90={q(v,.9):.1f}\tload={load0:.1f}-{load1:.1f}\trc={outs[b][0]}\tout={outs[b][1]!r}\terr={outs[b][2]!r}", flush=True)
