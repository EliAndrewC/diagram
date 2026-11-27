#!/usr/bin/env python3
"""t387: the plan hold's hooks, the before and after binaries INTERLEAVED, on a scratch copy of the clone's checks-open.json.

usage: t387-time.py <before bin> <after bin> [runs]
Each binary has its own fixture tree: .git/ with the state copy and one running hold on T999 of specs/999-x/plan.md. Per case,
2 warm-up rounds then <runs> counted, each round running before then after:
  bash-pre        record-edit-hooks PreToolUse on a Bash `true` (a kept snapshot already taken: the steady state of a hold)
  bash-post       checks-hooks PostToolUse on that call
  agent-post      checks-hooks PostToolUse on a non-check Agent launch
Reported: wall median / p90 / min ms, child CPU median ms (user+sys), and how many calls rewrote the state (its inode moved)."""
import json, os, resource, shutil, statistics, subprocess, sys, time

SRC = os.environ.get('T387_SRC', '/diagram/.clones/diagram-backlog/.git/checks-open.json')
HERE = os.path.dirname(os.path.abspath(__file__))
BINS = {'before': sys.argv[1], 'after': sys.argv[2]}
RUNS = int(sys.argv[3]) if len(sys.argv) > 3 else 20
PLAN = '# plan\n\n### T999 held\n\n- the held text\n\n### T1000 other\n\n- not held\n'


def fixture(label):
    fx = os.path.join(HERE, f't387-fx-{label}')
    shutil.rmtree(fx, ignore_errors=True)
    os.makedirs(fx + '/.git')
    os.makedirs(fx + '/specs/999-x')
    with open(fx + '/specs/999-x/plan.md', 'w') as f:
        f.write(PLAN)
    st = json.load(open(SRC))
    st['plan_holds'] = {'toolu_hold': {'feature': '999-x', 'task': 'T999', 'blocks': [], 't': time.time(), 'state': 'running',
                                       'aid': 'a-hold', 'root': fx}}
    st.pop('plan_snaps', None)
    json.dump(st, open(fx + '/.git/checks-open.json', 'w'), indent=1, sort_keys=True)
    return fx


def run(label, fx, guard, event, payload):
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.perf_counter()
    p = subprocess.run([BINS[label], '--only', guard, event], input=json.dumps(payload).encode(), capture_output=True,
                       env=dict(os.environ, PWD=fx), cwd=fx)
    wall = (time.perf_counter() - t0) * 1000
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (r1.ru_utime - r0.ru_utime + r1.ru_stime - r0.ru_stime) * 1000
    if p.returncode != 0:
        print(label, guard, 'exit', p.returncode, p.stdout[:200], p.stderr[:200])
    return wall, cpu


def bash(fx, i, ev='PreToolUse'):
    d = {'hook_event_name': ev, 'tool_name': 'Bash', 'tool_input': {'command': 'true'}, 'cwd': fx, 'tool_use_id': f'toolu_b{i}',
         'session_id': 's'}
    if ev == 'PostToolUse':
        d['tool_response'] = {'stdout': '', 'stderr': ''}
    return d


def agent(fx, i):
    return {'hook_event_name': 'PostToolUse', 'tool_name': 'Agent', 'cwd': fx, 'tool_use_id': f'toolu_a{i}', 'session_id': 's',
            'tool_input': {'subagent_type': 'Explore', 'prompt': 'x'}, 'tool_response': {'agentId': f'ag{i}', 'status': 'completed'}}


CASES = [
    ('bash-pre', 'record-edit-hooks', 'PreToolUse', lambda fx, i: bash(fx, i)),
    ('bash-post', 'checks-hooks', 'PostToolUse', lambda fx, i: bash(fx, i, 'PostToolUse')),
    ('agent-post', 'checks-hooks', 'PostToolUse', agent),
]
fxs = {l: fixture(l) for l in BINS}
# the hold's first call, so each tree's snapshot is taken (the after build keeps it once; the before build every call)
for l, fx in fxs.items():
    run(l, fx, 'record-edit-hooks', 'PreToolUse', bash(fx, 'first'))
print(f'# load at start {os.getloadavg()[0]:.1f}, state {os.path.getsize(SRC)} bytes, {RUNS} counted runs a case and binary')
for name, guard, event, payload in CASES:
    got = {l: ([], [], 0) for l in BINS}
    for i in range(RUNS + 2):
        for l, fx in fxs.items():
            path = fx + '/.git/checks-open.json'
            ino = os.stat(path).st_ino
            w, c = run(l, fx, guard, event, payload(fx, i))
            walls, cpus, wrote = got[l]
            wrote += os.stat(path).st_ino != ino
            if i >= 2:
                walls.append(w)
                cpus.append(c)
            got[l] = (walls, cpus, wrote)
    for l, (walls, cpus, wrote) in got.items():
        walls.sort()
        print(f'{l}\t{name}\twall median {statistics.median(walls):.1f}\tp90 {walls[int(len(walls) * 0.9) - 1]:.1f}'
              f'\tmin {walls[0]:.1f}\tcpu median {statistics.median(cpus):.1f}\twrites {wrote}/{RUNS + 2}'
              f'\tstate {os.path.getsize(fxs[l] + "/.git/checks-open.json")}')
print(f'# load at end {os.getloadavg()[0]:.1f}')
