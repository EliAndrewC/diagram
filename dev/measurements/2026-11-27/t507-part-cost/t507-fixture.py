#!/usr/bin/env python3
"""t507: the fixtures and one hook call, shared by t507-time.py and t507-strace.py.

A fixture is a tree `<dir>/fx-<label>/` holding `.git/checks-open.json` (a COPY of the state, never the real one, with the keys named
stripped or replaced) and one running hold on T999 of specs/999-x/plan.md, as 451 T490's `t490-time.py` built it."""
import json, os, shutil, subprocess, time

PLAN = '# plan\n\n### T999 held\n\n- the held text\n\n### T1000 other\n\n- not held\n'


def fixture(base, label, src, strip=(), pad=(), hold=True):
    """A tree at <base>/fx-<label>: `strip` keys dropped; each `pad` key's value replaced by one string of the same byte count
    (the same read and page faults, next to no structure to scan); `hold` False leaves `plan_holds` empty (`{}`), as the key stays
    after every hold."""
    fx = os.path.join(base, f'fx-{label}')
    shutil.rmtree(fx, ignore_errors=True)
    os.makedirs(fx + '/.git')
    os.makedirs(fx + '/specs/999-x')
    with open(fx + '/specs/999-x/plan.md', 'w') as f:
        f.write(PLAN)
    with open(src) as f:
        st = json.load(f)
    for k in strip:
        st.pop(k, None)
    st['plan_holds'] = {'toolu_hold': {'feature': '999-x', 'task': 'T999', 'blocks': [], 't': time.time(), 'state': 'running',
                                       'aid': 'a-hold', 'root': fx}} if hold else {}
    st.pop('plan_snaps', None)
    path = fx + '/.git/checks-open.json'

    def write():
        with open(path, 'w') as f:
            json.dump(st, f, indent=1, sort_keys=True)
    if pad:
        # the padded file is the unpadded one's byte count exactly: the string grown or shrunk by the difference
        write()
        target = os.path.getsize(path)
        for k in pad:
            st[k] = ''
        write()
        st[pad[0]] = 'x' * (target - os.path.getsize(path))
    write()
    return fx


def bash_pre(fx, i):
    return {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': 'true'}, 'cwd': fx,
            'tool_use_id': f'toolu_b{i}', 'session_id': 's'}


def call(argv, fx, payload, env=None):
    """One hook call; returns (CompletedProcess, cpu ms of the child)."""
    import resource
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    p = subprocess.run(argv, input=json.dumps(payload).encode(), capture_output=True,
                       env=dict(os.environ, PWD=fx, **(env or {})), cwd=fx)
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (r1.ru_utime - r0.ru_utime + r1.ru_stime - r0.ru_stime) * 1000
    if p.returncode != 0:
        print('exit', p.returncode, p.stdout[:200], p.stderr[:200])
    return p, cpu
