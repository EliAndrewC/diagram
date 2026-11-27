# t388: time an Agent call's PreToolUse and PostToolUse hooks in the throwaway world (t388-build.sh), T373's method
# (dev/measurements/2026-11-26/edit-hook/t373-time.py) with three changes the Agent call needs:
#   - the state an Agent hook WRITES (checks-open.json, check-passes.jsonl, the prompt store agent-prefix compares against) is put
#     back from $S/pristine before EVERY run, outside the clock, so no run sees an earlier run's dispatch, hold or prompt;
#   - each run's payload is written fresh: its own tool_use_id and a nonce at the prompt's end, and the PostToolUse carries the
#     background launch's real response shape ({"status": "async_launched", "agentId": ...});
#   - the gate's launcher (pair-hooks and check-bundle-hooks call scripts/gates/l7r-gate.sh) is aimed at a copied gate binary
#     (L7R_GATE_TARGET) and cannot build (L7R_GATE_CARGO=/bin/false).
# Arms are interleaved round-robin after one uncounted warm-up round; wall ms and children's CPU ms are kept. One TSV row an arm.
#   python3 t388-time.py <out.tsv> <rounds> <arm> [<arm> ...]
#     arm = <case>.<Event>:<what>[=<guards>][+<variant>]
#       case    = gp (a builder's brief, general-purpose) | sf (a spec-fidelity plan review) | rf (a record-format check on a bundle)
#       what    = hook (scripts/hooks/l7r-hook, launcher + binary) | bin (the binary, every guard) | ver (--version, the process start)
#                 | only (each guard named, alone: --only <guard>-hooks)
#       variant = fresh (L7R_GATE_FRESH set to the gate binary: its launcher skips the source walk) | small (checks-open.json with its
#                 finished dispatches dropped) | none (checks-open.json absent) | shortlog (the feature's event log cut to its first
#                 2,000 lines: what a log read costs)
import json, os, shutil, statistics, subprocess, sys, time

S = '/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t388'
W = S + '/w/diagram'
C = W + '/.clones/diagram-backlog'
G = C + '/.git'
BIN = S + '/target/l7r-guard.good'
GATE = S + '/gate/tool/l7r-gate'
SID = 't388-sess-0001'
TRANSCRIPT = S + '/home/.claude/projects/-diagram/t388-sess-0001.jsonl'

PRE = ['agent-model', 'agent-prefix', 'builder-brief', 'check-bundle', 'context-cap', 'escalation', 'event-log', 'pair',
       'research-switch', 'review-round']  # every guard taking an Agent PreToolUse (their GUARD constants, mirror 8963f871c4)
POST = ['checks', 'event-log']  # and an Agent PostToolUse

BRIEF = open(os.path.dirname(os.path.abspath(__file__)) + '/t388-brief.txt').read()
PROMPTS = {
    'gp': ('general-purpose', 'Measure: 451 T388 the Agent call hooks', BRIEF),
    'sf': ('spec-fidelity', "451 T384: plan review, 4 changed blocks",
           "MODE 4: PLAN REVIEW of 4 changed block(s) of feature 451-time-retro-and-efficiency's plan (feature 375 FR-043), on their "
           f"bundle: read {S}/bundles/plan-451-blocks/MANIFEST.md and the files beside it, and nothing in the repository. The tree is "
           f"{C}; record your verdict with the command the MANIFEST names."),
    'rf': ('record-format', '451 T384: record-format on 0238, round 2',
           f"Round 2. Run your check on the bundle whose manifest is {S}/bundles/q-record-format/MANIFEST.md (question 0238). The change "
           "since round 1: the visible gloss of one note now reads differently. Round 1 ruled on all 58 prepass words; rule on any new "
           "ones. Read only the bundle. Report verdicts and any EDIT blocks in your usual format."),
}


def payload(case, event, n):
    atype, desc, prompt = PROMPTS[case]
    tid = f'toolu_t388{case}{n:04d}'
    ti = {'description': desc, 'prompt': f'{prompt}\n(run {n})', 'subagent_type': atype, 'run_in_background': True}
    d = {'session_id': SID, 'transcript_path': TRANSCRIPT, 'cwd': C, 'hook_event_name': event, 'tool_name': 'Agent',
         'tool_input': ti, 'tool_use_id': tid, 'permission_mode': 'default'}
    if event == 'PostToolUse':
        d['tool_response'] = {'status': 'async_launched', 'agentId': f'a388{case}{n:012d}', 'description': desc, 'prompt': ti['prompt'],
                              'outputFile': f'/tmp/claude-1000/t388/tasks/a388{case}{n:012d}.output'}
    p = f'{S}/payloads/{case}.{event}.{n}.json'
    with open(p, 'w') as f:
        json.dump(d, f)
    return p


def env(variant):
    e = {'PATH': os.environ['PATH'], 'HOME': S + '/home', 'CLAUDE_PROJECT_DIR': W, 'CLONE_MAIN': W, 'L7R_GUARD_TARGET': S + '/target',
         'L7R_GATE_TARGET': S + '/gate', 'L7R_GATE_CARGO': '/bin/false', 'GUARD_LOG_DIR': S + '/gl', 'MEASURE_STATE_DIR': S + '/ms',
         'L7R_GUARD_TREE': W}
    if variant == 'fresh':
        e['L7R_GATE_FRESH'] = GATE
    return e


EVLOG = G + '/l7r-events/451-time-retro-and-efficiency.jsonl'
SHORT = {'last': ''}


def restore(variant):
    if variant == 'shortlog' or SHORT['last'] == 'shortlog':
        if not os.path.exists(S + '/pristine/events.jsonl'):
            shutil.copyfile(EVLOG, S + '/pristine/events.jsonl')
        if variant == 'shortlog':
            with open(S + '/pristine/events.jsonl') as src, open(EVLOG, 'w') as dst:
                for k, line in enumerate(src):
                    if k >= 2000:
                        break
                    dst.write(line)
        else:
            shutil.copyfile(S + '/pristine/events.jsonl', EVLOG)
    SHORT['last'] = variant
    shutil.copyfile(S + '/pristine/checks-open.json', G + '/checks-open.json')
    shutil.copyfile(S + '/pristine/check-passes.jsonl', G + '/check-passes.jsonl')
    shutil.rmtree(G + '/l7r-agent-prompts', ignore_errors=True)
    shutil.copytree(S + '/pristine/l7r-agent-prompts', G + '/l7r-agent-prompts')
    if variant == 'small':
        shutil.copyfile(S + '/pristine/checks-open.small.json', G + '/checks-open.json')
    elif variant == 'none':
        os.remove(G + '/checks-open.json')


def run(argv, payload_path, e):
    with open(payload_path, 'rb') as f:
        t = time.perf_counter()
        p = subprocess.Popen(argv, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e, cwd=C)
        out, err = p.communicate()
        dt = (time.perf_counter() - t) * 1e3
    return dt, p.returncode, out + err


def cpu():
    import resource
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (r.ru_utime + r.ru_stime) * 1e3


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(round(p * (len(v) - 1))))]


def arms_of(spec):
    spec, _, variant = spec.partition('+')
    case_ev, _, what = spec.partition(':')
    what, _, only = what.partition('=')
    case, event = case_ev.split('.')
    tag = f'+{variant}' if variant else ''
    if what == 'hook':
        return [(f'{case_ev} hook{tag}', [W + '/scripts/hooks/l7r-hook', event], case, event, variant)]
    if what == 'bin':
        return [(f'{case_ev} binary{tag}', [BIN, event], case, event, variant)]
    if what == 'ver':
        return [(f'{case_ev} --version', [BIN, '--version'], case, event, variant)]
    names = only.split(',') if only else (PRE if event == 'PreToolUse' else POST)
    return [(f'{case_ev} --only {g}-hooks{tag}', [BIN, '--only', g + '-hooks', event], case, event, variant) for g in names]


def main():
    out, rounds = sys.argv[1], int(sys.argv[2])
    arms = [a for spec in sys.argv[3:] for a in arms_of(spec)]
    res = {a[0]: {'ms': [], 'cpu': [], 'rc': {}} for a in arms}
    loads = []
    n = 0
    for i in range(rounds + 1):
        loads.append(float(open('/proc/loadavg').read().split()[0]))
        for label, argv, case, event, variant in (arms if i % 2 == 0 else arms[::-1]):
            n += 1
            restore(variant)
            if event == 'PostToolUse':  # its PreToolUse first, outside the clock, so the dispatch row a launch books exists
                subprocess.run([BIN, 'PreToolUse'], stdin=open(payload(case, 'PreToolUse', n), 'rb'), capture_output=True, env=env(variant), cwd=C)
            p = payload(case, event, n)
            c0 = cpu()
            dt, rc, said = run(argv, p, env(variant))
            if i:
                r = res[label]
                r['ms'].append(dt); r['cpu'].append(cpu() - c0)
                r['rc'][rc] = r['rc'].get(rc, 0) + 1
                if rc and 'said' not in r:
                    r['said'] = said[:300].decode(errors='replace').replace('\n', ' ').replace('\t', ' ')
            os.remove(p)
    restore('')
    with open(out, 'a') as f:
        for label, *_ in arms:
            r = res[label]; v = r['ms']
            f.write('\t'.join([label, str(len(v)), f'{statistics.median(v):.1f}', f'{q(v, 0.9):.1f}', f'{min(v):.1f}', f'{max(v):.1f}',
                               f'{statistics.median(r["cpu"]):.1f}', ','.join(f'{k}x{c}' for k, c in sorted(r['rc'].items())),
                               f'{min(loads):.2f}-{max(loads):.2f}', r.get('said', '')]) + '\n')


main()
