#!/usr/bin/env python3
"""t508: a state that is not UTF-8 (one bad byte in `dispatches`, before the key), under a hold with its snapshot: each build's
PreToolUse (record-edit-hooks) and PostToolUse (checks-hooks) on a Bash `true`, their exit and output, and whether the file's bytes moved.
usage: t508-nonutf8.py <scratch dir> <state copy> <t507 dir>"""
import hashlib, importlib, sys
BASE, SRC, T507 = sys.argv[1:4]
sys.path.insert(0, T507)
fx_mod = importlib.import_module('t507-fixture')
for b in ('clean', 'B'):
    fx = fx_mod.fixture(BASE, f'nonutf8-{b}', SRC, hold=True)
    binp = f'{BASE}/b/bin/l7r-guard-{b}'
    fx_mod.call([binp, '--only', 'record-edit-hooks', 'PreToolUse'], fx, fx_mod.bash_pre(fx, 'first'))
    path = fx + '/.git/checks-open.json'
    data = open(path, 'rb').read()
    i = data.index(b'"dispatches"') + 40
    data = data[:i] + b'\xff' + data[i + 1:]
    open(path, 'wb').write(data)
    for case, guard, ev in (('pre', 'record-edit-hooks', 'PreToolUse'), ('post', 'checks-hooks', 'PostToolUse')):
        before = hashlib.sha1(open(path, 'rb').read()).hexdigest()
        payload = fx_mod.bash_pre(fx, 'n')
        if case == 'post':
            payload = dict(payload, hook_event_name='PostToolUse', tool_response={'stdout': '', 'stderr': ''})
        p, _ = fx_mod.call([binp, '--only', guard, ev], fx, payload)
        after = hashlib.sha1(open(path, 'rb').read()).hexdigest()
        print(f'{b}\t{case}\texit {p.returncode}\tstdout {p.stdout[:120]!r}\tfile {"unchanged" if before == after else "CHANGED"}')
