#!/usr/bin/env python3
"""t490: the before and after guard binaries' answers on a copy of the clone's checks-open.json, call by call.

usage: t490-diff.py <before bin> <after bin> <state>
Each binary has its own fixture tree (.git/ with the state copy, one running hold on T999 of specs/999-x/plan.md, and one running
quote-check row added on q:0105 so the freeze has a frozen page). The same calls run in the same order in each; after each, the exit
code, stdout, stderr and the state file's bytes are compared, the tree's path written as <root>. A time stamped by the call itself (past the script's start) is written <now>. Reports each call's verdict."""
import json, os, re, shutil, subprocess, sys, time

BINS = {'before': sys.argv[1], 'after': sys.argv[2]}
SRC = sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = '# plan\n\n### T999 held\n\n- the held text\n\n### T1000 other\n\n- not held\n'
T = time.time()


def fixture(label, text=None):
    fx = os.path.join(HERE, f't490-dfx-{label}')
    shutil.rmtree(fx, ignore_errors=True)
    os.makedirs(fx + '/.git')
    os.makedirs(fx + '/specs/999-x')
    os.makedirs(fx + '/.specify')
    with open(fx + '/.specify/feature.json', 'w') as f:
        f.write('{"feature_directory": "specs/999-x"}')
    with open(fx + '/specs/999-x/plan.md', 'w') as f:
        f.write(PLAN)
    with open(fx + '/MANIFEST.md', 'w') as f:
        f.write('unit: quote-check:0105.drawing#bath abc\n')
    if text is None:
        st = json.load(open(SRC))
        st['plan_holds'] = {'toolu_hold': {'feature': '999-x', 'task': 'T999', 'blocks': [], 't': T, 'state': 'running',
                                           'aid': 'a-hold', 'root': fx}}
        st.pop('plan_snaps', None)
        st['dispatches']['toolu_t490run'] = {'check': 'quote-check', 'subjects': ['q:0105'], 'state': 'running', 't': T,
                                             'aid': 'ag-t490', 'manifest': ''}
        text = json.dumps(st, indent=1, sort_keys=True)
    with open(fx + '/.git/checks-open.json', 'w') as f:
        f.write(text)
    return fx


def calls(fx, st):
    live = [(k, d) for k, d in st['dispatches'].items() if d['state'] in ('pending', 'running')]
    pending = next(k for k, d in live if d['state'] == 'pending')
    running_aid = next(d['aid'] for k, d in live if d['state'] == 'running' and d.get('aid'))
    bash = lambda cmd, tid, ev='PreToolUse': {'hook_event_name': ev, 'tool_name': 'Bash', 'tool_input': {'command': cmd},
                                               'cwd': fx, 'tool_use_id': tid, 'session_id': 's'}
    agent = lambda sub, prompt, tid: {'hook_event_name': 'PreToolUse', 'tool_name': 'Agent', 'cwd': fx, 'tool_use_id': tid,
                                      'session_id': 's', 'tool_input': {'subagent_type': sub, 'prompt': prompt}}
    post_agent = lambda tid, aid: {'hook_event_name': 'PostToolUse', 'tool_name': 'Agent', 'cwd': fx, 'tool_use_id': tid,
                                   'session_id': 's', 'tool_input': {'subagent_type': 'Explore', 'prompt': 'x'},
                                   'tool_response': {'agentId': aid, 'status': 'async_launched'}}
    stop = lambda aid: {'hook_event_name': 'SubagentStop', 'cwd': fx, 'agent_id': aid, 'session_id': 's',
                        'last_assistant_message': 'q: 1\n'}
    page = {'hook_event_name': 'PreToolUse', 'tool_name': 'Edit', 'cwd': fx, 'session_id': 's', 'tool_use_id': 'e1',
            'tool_input': {'file_path': fx + '/research/questions/0105-x.html', 'old_string': 'a', 'new_string': 'b'}}
    plan = dict(page, tool_input={'file_path': fx + '/specs/999-x/plan.md', 'old_string': 'the held', 'new_string': 'x'})
    return [
        ('bash under the hold, first (its save)', 'record-edit-hooks', 'PreToolUse', bash('true', 'b1')),
        ('its end', 'checks-hooks', 'PostToolUse', bash('true', 'b1', 'PostToolUse')),
        ('bash under the hold, steady', 'record-edit-hooks', 'PreToolUse', bash('true', 'b2')),
        ('its end', 'checks-hooks', 'PostToolUse', bash('true', 'b2', 'PostToolUse')),
        ('Edit of a frozen page', 'record-edit-hooks', 'PreToolUse', page),
        ('Edit of the held plan', 'record-edit-hooks', 'PreToolUse', plan),
        ('apply-edits on a reply', 'record-edit-hooks', 'PreToolUse', bash('make apply-edits FROM=/nonexistent/r.md', 'b3')),
        ('Explore dispatch', 'check-bundle-hooks', 'PreToolUse', agent('Explore', 'look around', 'x1')),
        ('Explore launch', 'checks-hooks', 'PostToolUse', post_agent('x1', 'ag-x1')),
        ('Explore return', 'checks-hooks', 'SubagentStop', stop('ag-x1')),
        ('a pending dispatch launched', 'checks-hooks', 'PostToolUse', post_agent(pending, 'ag-pend')),
        ('a running check returns', 'checks-hooks', 'SubagentStop', stop(running_aid)),
        ('the hold\'s review returns', 'checks-hooks', 'SubagentStop', stop('a-hold')),
        ('TaskStop', 'checks-hooks', 'PostToolUse', {'hook_event_name': 'PostToolUse', 'tool_name': 'TaskStop', 'cwd': fx,
                                                     'session_id': 's', 'tool_input': {'task_id': 'ag-pend'},
                                                     'tool_response': {}}),
        ('quote-check dispatch', 'check-bundle-hooks', 'PreToolUse', agent('quote-check', f'Read {fx}/MANIFEST.md', 'qc1')),
    ]


def run(binary, fx, guard, event, payload):
    p = subprocess.run([binary, '--only', guard, event], input=json.dumps(payload).encode(), capture_output=True,
                       env=dict(os.environ, PWD=fx), cwd=fx)
    try:
        state = open(fx + '/.git/checks-open.json').read()
    except OSError:
        state = ''
    return [str(p.returncode), p.stdout.decode(), p.stderr.decode(), state]


def stamp(text):
    # a time the call itself stamps (the binary's clock, after this script began) is written <now>: the arms run apart in time
    return re.sub(r'(\d{10}\.\d+)', lambda m: '<now>' if float(m.group(1)) > T + 1 else m.group(1), text)


def arm_pair(text=None, title='the clone\'s state'):
    fxs = {l: fixture(l, text) for l in BINS}
    st = json.load(open(fxs['before'] + '/.git/checks-open.json')) if text is None else json.load(open(SRC))
    same = 0
    rows = [calls(fxs[l], st) for l in BINS]
    for (name, guard, event, pb), (_, _, _, pa) in zip(*rows):
        got = {l: [stamp(x.replace(fxs[l], '<root>')) for x in run(BINS[l], fxs[l], guard, event, p)]
               for l, p in (('before', pb), ('after', pa))}
        ok = got['before'] == got['after']
        same += ok
        print(f'{title}\t{name}\t{"SAME" if ok else "DIFFERENT"}\texit {got["after"][0]}\tstdout {len(got["after"][1])} B'
              f'\tstderr {len(got["after"][2])} B\tstate {len(got["after"][3])} B')
        if not ok:
            for i, part in enumerate(('exit', 'stdout', 'stderr', 'state')):
                if got['before'][i] != got['after'][i]:
                    print('   differs in', part, got['before'][i][:300], '|', got['after'][i][:300])
    print(f'# {title}: {same} of {len(rows[0])} calls the same')


arm_pair()
arm_pair('not json', 'a state that is not JSON')
