# t388: what check-bundle-hooks' cascade check spends in git (rust/guard/shared/src/checks/rounds/freeze.rs changed_lines): the
# work-tree diff it runs against the merge base, and the cheaper forms, 20 interleaved runs each, read-only (GIT_OPTIONAL_LOCKS=0).
#   python3 t388-git.py <clone> [<clone> ...]
import os, statistics, subprocess, sys, time
for root in sys.argv[1:]:
    g = lambda *a: subprocess.run(['git', '-C', root, *a], capture_output=True, text=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0')).stdout.strip()
    base = g('merge-base', 'HEAD', 'origin/main') or g('rev-parse', 'HEAD')
    arms = {
        'diff --numstat <base> (work tree, today)': ['-c', 'diff.autoRefreshIndex=false', 'diff', '--numstat', base],
        'diff --numstat <base> HEAD (trees only)': ['diff', '--numstat', base, 'HEAD'],
        'diff --quiet (work tree against index)': ['-c', 'diff.autoRefreshIndex=false', 'diff', '--quiet'],
        'rev-parse --show-toplevel (a process start)': ['rev-parse', '--show-toplevel'],
    }
    res = {k: [] for k in arms}
    for i in range(21):
        for k, a in (arms.items() if i % 2 == 0 else reversed(arms.items())):
            t = time.perf_counter()
            subprocess.run(['git', '-C', root, *a], capture_output=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
            if i:
                res[k].append((time.perf_counter() - t) * 1e3)
    load = open('/proc/loadavg').read().split()[0]
    ahead = g('rev-list', '--count', f'{base}..HEAD')
    lines = sum(int(a) + int(b) for a, b, *_ in (l.split('\t') for l in g('diff', '--numstat', base).splitlines()) if a.isdigit() and b.isdigit())
    print(f'{root}  base {base[:10]}, {ahead} commits ahead, {lines} lines changed, load {load}')
    for k, v in res.items():
        v.sort()
        print(f'  {statistics.median(v):7.1f} / {v[int(0.9 * (len(v) - 1))]:7.1f} ms  {k}')
