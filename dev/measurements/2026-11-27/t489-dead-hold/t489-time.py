#!/usr/bin/env python3
"""t489: a Bash call's two plan-hold hooks while a RUNNING hold past HOLD_MAX_S (1800 s) stands, before and after binaries interleaved.

usage: t489-time.py <before bin> <after bin> [runs]
Each binary has its own fixture tree: .git/ with a copy of the clone's checks-open.json and one running hold, taken 4,000 s ago,
on T999 of specs/999-x/plan.md. One first call (the after binary's purge), then <runs> counted rounds of a Bash `true`:
record-edit-hooks PreToolUse and checks-hooks PostToolUse, before then after. Reported: child CPU median ms per hook, the state's
writes (its inode moved) and whether `plan_holds` is empty at the end."""
import json, os, resource, shutil, statistics, subprocess, sys, time

SRC = os.environ.get('T489_SRC', '/diagram/.clones/diagram-backlog/.git/checks-open.json')
HERE = os.path.dirname(os.path.abspath(__file__))
BINS = {'before': sys.argv[1], 'after': sys.argv[2]}
RUNS = int(sys.argv[3]) if len(sys.argv) > 3 else 20
PLAN = '# plan\n\n### T999 held\n\n- the held text\n\n### T1000 other\n\n- not held\n'


def fixture(label):
    fx = os.path.join(HERE, f't489-fx-{label}')
    shutil.rmtree(fx, ignore_errors=True)
    os.makedirs(fx + '/.git')
    os.makedirs(fx + '/specs/999-x')
    open(fx + '/specs/999-x/plan.md', 'w').write(PLAN)
    st = json.load(open(SRC))
    st['plan_holds'] = {'toolu_hold': {'feature': '999-x', 'task': 'T999', 'blocks': [], 't': time.time() - 4000, 'state': 'running',
                                       'aid': 'a-hold', 'root': fx}}
    st.pop('plan_snaps', None)
    json.dump(st, open(fx + '/.git/checks-open.json', 'w'), indent=1, sort_keys=True)
    return fx


def run(label, fx, guard, payload):
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    subprocess.run([BINS[label], '--only', guard, payload['hook_event_name']], input=json.dumps(payload).encode(),
                   capture_output=True, env=dict(os.environ, PWD=fx), cwd=fx)
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (r1.ru_utime - r0.ru_utime + r1.ru_stime - r0.ru_stime) * 1000


def bash(fx, i, ev):
    d = {'hook_event_name': ev, 'tool_name': 'Bash', 'tool_input': {'command': 'true'}, 'cwd': fx, 'tool_use_id': f'toolu_b{i}',
         'session_id': 's'}
    if ev == 'PostToolUse':
        d['tool_response'] = {'stdout': '', 'stderr': ''}
    return d


fx = {k: fixture(k) for k in BINS}
for k in BINS:
    run(k, fx[k], 'record-edit-hooks', bash(fx[k], 0, 'PreToolUse'))
    run(k, fx[k], 'checks-hooks', bash(fx[k], 0, 'PostToolUse'))
ino = {k: os.stat(fx[k] + '/.git/checks-open.json').st_ino for k in BINS}
cpu = {(k, h): [] for k in BINS for h in ('pre', 'post')}
writes = {k: 0 for k in BINS}
for i in range(1, RUNS + 1):
    for k in BINS:
        cpu[(k, 'pre')].append(run(k, fx[k], 'record-edit-hooks', bash(fx[k], i, 'PreToolUse')))
        cpu[(k, 'post')].append(run(k, fx[k], 'checks-hooks', bash(fx[k], i, 'PostToolUse')))
        n = os.stat(fx[k] + '/.git/checks-open.json').st_ino
        writes[k] += n != ino[k]
        ino[k] = n
for k in BINS:
    holds = json.load(open(fx[k] + '/.git/checks-open.json')).get('plan_holds')
    print(f"{k}: pre {statistics.median(cpu[(k, 'pre')]):.1f} ms, post {statistics.median(cpu[(k, 'post')]):.1f} ms CPU median "
          f"of {RUNS}; writes {writes[k]} of {RUNS}; plan_holds at the end {json.dumps(holds)[:60]}")
for k in BINS:
    shutil.rmtree(fx[k], ignore_errors=True)
