# t388: one call under T373's LD_PRELOAD shim (dev/measurements/2026-11-26/edit-hook/t373-shim.c; strace is refused here); prints the
# call's output, each process with its duration, every write, and the reads counted by directory (the big files named).
#   python3 t388-probe.py <case> <Event> [<guard>] [+<variant>]
import collections, importlib.util, os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
src = open(H + '/t388-time.py').read().replace('\nmain()\n', '\n')
t = {'__file__': H + '/t388-time.py'}
exec(compile(src, 't388-time.py', 'exec'), t)
S = t['S']
args = [a for a in sys.argv[1:] if not a.startswith('+')]
variant = next((a[1:] for a in sys.argv[1:] if a.startswith('+')), '')
case, event = args[0], args[1]
only = args[2] if len(args) > 2 else None
log = f'{S}/probe.{case}.{event}{"." + only if only else ""}{"+" + variant if variant else ""}.log'
if os.path.exists(log):
    os.remove(log)
t['restore'](variant)
e = t['env'](variant)
if event == 'PostToolUse':
    subprocess.run([t['BIN'], 'PreToolUse'], stdin=open(t['payload'](case, 'PreToolUse', 1), 'rb'), capture_output=True, env=e, cwd=t['C'])
p = t['payload'](case, event, 1)
e2 = dict(e, T373_OUT=log, LD_PRELOAD=S + '/t373-shim.so')
argv = [t['BIN'], '--only', only + '-hooks', event] if only else [t['W'] + '/scripts/hooks/l7r-hook', event]
r = subprocess.run(argv, stdin=open(p, 'rb'), capture_output=True, env=e2, text=True, cwd=t['C'])
t['restore']('')
print('exit', r.returncode, 'stdout', r.stdout[:400].replace('\n', ' '), 'stderr', r.stderr[:400].replace('\n', ' '))
start = {}; reads = collections.Counter(); spawns = 0
for line in open(log, errors='replace'):
    ms, pid, ppid, kind, *rest = line.rstrip('\n').split(' ', 4)
    rest = rest[0] if rest else ''
    if kind == 'START':
        start[pid] = (float(ms), rest)
    elif kind == 'END':
        s = start.get(pid, (float(ms), '?'))
        print(f'{float(ms) - s[0]:8.1f} ms  pid {pid} ppid {ppid}  {s[1][:200].replace(S, "$S")}  [{rest}]')
    elif kind == 'SPAWN':
        spawns += 1
    elif kind in ('OPENW', 'MKDIR', 'RENAME', 'UNLINK'):
        if not rest.startswith('/dev/'):
            print(f'   {kind} {rest.replace(S, "$S")}')
    elif kind == 'OPENR':
        r2 = rest.replace(S, '$S')
        big = r2.endswith(('.json', '.jsonl')) and os.path.exists(rest) and os.path.getsize(rest) > 100_000
        reads[r2 if big else ('/'.join(r2.split('/')[:-1]) if len(r2.split('/')) > 2 else r2)] += 1
print('spawn calls', spawns, '; reads by directory (files over 100 KB by name):')
for d, n in reads.most_common(14):
    print(f'   {n:6d} {d}')
