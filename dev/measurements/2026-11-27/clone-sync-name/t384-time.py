# t384: time `l7r-guard --only clone-sync-hooks PreToolUse` on an Edit of a file in a scratch clone, arms interleaved, one warm-up round.
#   python3 t384-time.py <rounds> <bin> [<bin> ...]
import json, os, subprocess, sys, time
S = os.path.dirname(os.path.abspath(__file__))
M = S + '/main'; C = M + '/.clones/diagram-backlog'; DIRTY = C + '/docs/usage.md'
def payload(tr):
    return json.dumps({"session_id": "t384-sid", "transcript_path": S + '/' + tr, "cwd": C, "hook_event_name": "PreToolUse",
                       "tool_name": "Edit", "tool_input": {"file_path": C + "/docs/usage.md", "old_string": "a", "new_string": "b"}}).encode()
ENV = {'PATH': os.environ['PATH'], 'HOME': os.environ['HOME'], 'CLONE_MAIN': M, 'CLONE_SESSIONS_DIR': S + '/sess',
       'L7R_GUARD_TREE': '/diagram/.clones/diagram-backlog-b1', 'GUARD_LOG_DIR': S + '/gl', 'MEASURE_STATE_DIR': S + '/ms'}
def state(s):
    subprocess.run(['git', '-C', C, 'checkout', '-q', '--', 'docs/usage.md'], check=True)
    if s == 'dirty': open(DIRTY, 'a').write('t384 dirty\n')
    out = subprocess.run(['git', '-C', C, 'status', '--porcelain'], capture_output=True, text=True).stdout
    assert bool(out.strip()) == (s == 'dirty'), out
def q(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(round(p * (len(v) - 1))))]
rounds, bins = int(sys.argv[1]), sys.argv[2:]
for st in ('dirty', 'clean'):
    state(st)
    for tr in ('t384-transcript.jsonl', 't384-untitled.jsonl'):
        arms = [(b, payload(tr)) for b in bins]; times = {b: [] for b in bins}; outs = {}
        for r in range(rounds + 1):
            for b, p in arms:
                t = time.perf_counter()
                done = subprocess.run([S + '/' + b, '--only', 'clone-sync-hooks', 'PreToolUse'], input=p, capture_output=True, env=ENV)
                dt = (time.perf_counter() - t) * 1e3
                if r: times[b].append(dt)
                outs[b] = (done.returncode, done.stdout[:200], done.stderr[:300])
        load = os.getloadavg()[0]
        for b in bins:
            v = times[b]
            print(f"{st}\t{tr}\t{b}\tn={len(v)}\tmedian={q(v,.5):.1f}\tp90={q(v,.9):.1f}\tload={load:.1f}\trc={outs[b][0]}\tout={outs[b][1]!r}\terr={outs[b][2]!r}", flush=True)
state('clean')
