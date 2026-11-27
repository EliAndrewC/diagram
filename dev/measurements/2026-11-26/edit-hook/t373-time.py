# t373: time hook calls in the throwaway world. Arms are interleaved round-robin inside each round, after one uncounted warm-up
# round; each run's wall ms and its children's CPU ms (user+sys, os.wait4) are kept. Output: one TSV row an arm.
#   python3 t373-time.py <out.tsv> <rounds> <state> <session> <case> [<case> ...]
#     state   = dirty | clean   (the sandbox clone has an uncommitted change, or none)
#     session = sess | none     (a session id the claim map resolves to the sandbox clone with a transcript; or T365's form)
#     case    = <tool-case>.<Event>[:full|:guards|:all][@realhome]   e.g. edit-doc.PreToolUse:all
import json, os, statistics, subprocess, sys, time

S = os.path.dirname(os.path.abspath(__file__))
W = S + '/w/diagram'
C = W + '/.clones/diagram-backlog'
BIN = S + '/target/l7r-guard.good'
MAP = W + '/.clones/.session-clones'
DIRTY = C + '/dev/measurements/2026-11-26/tmp-clutter/t365-glob.txt'  # a tracked file the dirty state appends a line to

GUARDS = {  # each guard's events and matcher, from its GUARD constant (rust/guard/src/guards/*.rs, shared/src/guards/*.rs), in the binary's order
    'pair': ('PreToolUse Stop', 'Bash|Agent'), 'gate': ('PreToolUse', 'Bash'), 'measure': ('PreToolUse status', 'Bash|Edit|Write|NotebookEdit'),
    'no-poll': ('PreToolUse', 'Bash'), 'main-tree': ('PreToolUse', 'Bash'),
    'event-log': ('PreToolUse PostToolUse SubagentStart SubagentStop UserPromptSubmit Stop PostToolUseFailure', '*'),
    'context-cap': ('PreToolUse', '*'), 'clone-sync': ('PreToolUse UserPromptSubmit SessionStart', 'Edit|Write|NotebookEdit|Bash'),
    'engine-freeze': ('PreToolUse', 'Edit|Write|NotebookEdit'), 'gm-tree': ('PreToolUse', 'Bash|Edit|Write|NotebookEdit'),
    'batching': ('PreToolUse PostToolUse status', 'Read|Grep|Glob|Bash'), 'no-branch': ('PreToolUse', 'Bash'), 'discard': ('PreToolUse', 'Bash'),
    'builder-pool': ('PreToolUse', 'Bash'), 'conflict-marker': ('PreToolUse', 'Bash'), 'gate-write': ('PreToolUse', 'Bash|Edit|Write|NotebookEdit'),
    'feature-approval': ('PreToolUse', 'Bash'), 'budget-change': ('PreToolUse', 'Bash'), 'ledger': ('PreToolUse', 'Bash'),
    'archive-first': ('PreToolUse', 'WebFetch'), 'claims-file': ('PreToolUse', 'Bash|Read|Edit|Write|NotebookEdit'),
    'readme': ('PreToolUse', 'Bash|Edit|Write|NotebookEdit'), 'download-copy': ('PreToolUse', 'Bash|Edit|Write|NotebookEdit'),
    'phase-source': ('PreToolUse', 'Bash|Read|Grep|Glob|Write|Edit|MultiEdit'), 'new-file': ('PreToolUse', 'Write|Bash'),
    'blocked-fetch': ('PreToolUse', 'WebFetch|Bash'), 'repo-safety': ('PreToolUse', 'Bash'), 'agent-model': ('PreToolUse', 'Agent'),
    'builder-brief': ('PreToolUse', 'Agent'), 'wakeup': ('PreToolUse Stop', 'ScheduleWakeup'), 'agent-prefix': ('PreToolUse', 'Agent'),
    'workflow': ('PreToolUse', 'Workflow'), 'source-block': ('PreToolUse', 'Edit|Write|NotebookEdit'),
    'house-style': ('PreToolUse', 'Bash|Edit|Write|NotebookEdit'), 'escalation': ('PreToolUse SubagentStop Stop', 'Agent'),
    'review-round': ('PreToolUse', 'Agent'), 'make-only': ('PreToolUse', 'Bash'), 'guard-file': ('PreToolUse', 'Read|Edit|Write|NotebookEdit'),
    'record-edit': ('PreToolUse', 'Edit|Write|Bash'), 'check-bundle': ('PreToolUse', 'Agent'),
    'checks': ('PostToolUse PostToolUseFailure SubagentStop', 'Agent|TaskStop|Bash|Write|Edit|MultiEdit'),
    'static-runs': ('PreToolUse', 'Bash'), 'research-switch': ('PreToolUse', 'Agent|Bash'), 'shell-check': ('PreToolUse', 'Bash'),
}


def takers(event, tool):
    return [g for g, (ev, m) in GUARDS.items() if event in ev.split() and (m == '*' or tool in m.split('|'))]


def env(home):
    return {'PATH': os.environ['PATH'], 'HOME': home, 'CLAUDE_PROJECT_DIR': W, 'CLONE_MAIN': W, 'L7R_GUARD_TARGET': S + '/target',
            'GUARD_LOG_DIR': S + '/gl', 'MEASURE_STATE_DIR': S + '/ms', 'L7R_GUARD_TREE': W}


def set_state(state):
    subprocess.run(['git', '-C', C, 'checkout', '-q', '--', os.path.relpath(DIRTY, C)], check=True)
    if state == 'dirty':
        open(DIRTY, 'a').write('t373 dirty\n')
    out = subprocess.run(['git', '-C', C, 'status', '--porcelain'], capture_output=True, text=True).stdout
    assert bool(out.strip()) == (state == 'dirty'), out
    return len(out.splitlines())


def run(argv, payload, e):
    with open(payload, 'rb') as f:
        t = time.perf_counter()
        p = subprocess.Popen(argv, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e)
        out, err = p.communicate()
        dt = (time.perf_counter() - t) * 1e3
    return dt, p.returncode, len(out), len(err)


def cpu():
    r = __import__('resource').getrusage(__import__('resource').RUSAGE_CHILDREN)
    return (r.ru_utime + r.ru_stime) * 1e3


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(round(p * (len(v) - 1))))]


def main():
    out, rounds, state, session = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    arms = []
    for spec in sys.argv[5:]:
        spec, _, home = spec.partition('@')
        case, _, what = spec.partition(':')
        what, _, only = (what or 'full').partition('=')  # guards=clone-sync,event-log times those guards alone
        tool_case, event = case.split('.')
        payload = f'{S}/payloads/{session}.{case}.json'
        tool = json.load(open(payload))['tool_name']
        e = env(os.path.expanduser('~') if home == 'realhome' else S + '/home')
        tag = '@realhome' if home else ''
        if what in ('full', 'all'):
            arms.append((f'{case} hook(launcher+binary){tag}', [W + '/scripts/hooks/l7r-hook', event], payload, e))
            arms.append((f'{case} binary, every guard{tag}', [BIN, event], payload, e))
        if what in ('guards', 'all'):
            arms.append((f'{case} binary --version (process start)', [BIN, '--version'], payload, e))
            for g in (only.split(',') if only else takers(event, tool)):
                arms.append((f'{case} --only {g}-hooks', [BIN, '--only', g + '-hooks', event], payload, e))
    n_dirty = set_state(state)
    res = {a[0]: {'ms': [], 'cpu': [], 'rc': set(), 'out': set()} for a in arms}
    loads = []
    for i in range(rounds + 1):
        loads.append(float(open('/proc/loadavg').read().split()[0]))
        order = arms if i % 2 == 0 else arms[::-1]
        for label, argv, payload, e in order:
            if session == 'none' and os.path.exists(MAP + '/t373-none-0000'):
                os.remove(MAP + '/t373-none-0000')  # T365's form stays unresolved: the guard's claim of the last run is taken back
            c0 = cpu()
            dt, rc, no, ne = run(argv, payload, e)
            if i:
                r = res[label]
                r['ms'].append(dt); r['cpu'].append(cpu() - c0); r['rc'].add(rc); r['out'].add((no, ne))
    set_state('clean')
    with open(out, 'a') as f:
        for label, _, _, _ in arms:
            r = res[label]; v = r['ms']
            f.write('\t'.join([state, session, label, str(len(v)), f'{statistics.median(v):.1f}', f'{q(v, 0.9):.1f}', f'{min(v):.1f}', f'{max(v):.1f}',
                               f'{statistics.median(r["cpu"]):.1f}', ','.join(map(str, sorted(r['rc']))), ';'.join(f'{a}/{b}' for a, b in sorted(r['out'])),
                               f'{min(loads):.2f}-{max(loads):.2f}', str(n_dirty)]) + '\n')


main()
