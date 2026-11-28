#!/usr/bin/env python3
"""t562: attribution robust to /proc/<pid>/io being inclusive of reaped children.
ROOTS: the children of claude (pid 31: each Bash tool call or hook) and of tini (pid 1: detached runners) - each root's
inclusive delta covers its subtree; claude's own threads write ~0 (measured: 45 kB in 20 s). LEAVES: processes with no child
seen - their delta is their own. Residual = the cgroup's io.stat total minus the roots: subtrees that lived under 0.5 s."""
import json, re, sys, collections
exec(open(sys.argv[0].replace('t562-roots.py', 't562-analyze.py')).read().split('groups = {')[0].replace("d = json.load(open(sys.argv[1]))", "d = json.load(open(sys.argv[1]))"))
roots = collections.Counter(); rootn = collections.Counter(); rootx = collections.defaultdict(list)
def label(p, desc):
    cmds = [p['cmd']] + [P[k]['cmd'] for k in desc]
    for c in cmds:
        m = re.search(r'\bmake\s+(?:-\S+\s+)*([a-z][\w-]*)', c)
        if m: return 'make ' + m.group(1)
    for c in cmds:
        if 'lane --work' in c: return 'lane runner'
        if 'sampler' in c and 'python' in c: return 't562 sampler'
        if 'mem-samples' in c or 'sampler' in c: return 'clone sampler'
    for c in cmds:
        if 'l7r-guard' in c: return 'hook (l7r-guard)'
        if c.startswith('git ') or '/git ' in c: return 'git (direct)'
    return 'other: ' + (p['comm'])
children = collections.defaultdict(list)
for k, p in P.items(): children[p['ppid']].append(k)
def descendants(pid, start):
    out = []; stack = [pid]
    while stack:
        q = stack.pop()
        for ck in children.get(q, []):
            if P[ck]['start'] >= start and ck not in out:
                out.append(ck); stack.append(P[ck]['pid'])
    return out
for k, p in P.items():
    if p['first'] is None or p['ppid'] not in (1, 31) or p['comm'] in ('claude', 'tini'): continue
    desc = descendants(p['pid'], p['start'])
    lab = label(p, desc)
    for kk in ('write_bytes', 'read_bytes', 'syscw', 'cancelled_write_bytes'):
        roots[(lab, kk)] += delta(p, kk)
    rootn[lab] += 1
tot_w = sum(v for (l, k), v in roots.items() if k == 'write_bytes')
tot_r = sum(v for (l, k), v in roots.items() if k == 'read_bytes')
labs = sorted(rootn, key=lambda l: -roots[(l, 'write_bytes')])
print('ROOTS: write GB, read GB, syscw, cancelled GB, n')
for l in labs[:30]:
    print(f"{l:40s} {roots[(l,'write_bytes')]/1e9:8.3f} {roots[(l,'read_bytes')]/1e9:8.3f} {roots[(l,'syscw')]:9d} {roots[(l,'cancelled_write_bytes')]/1e9:7.3f} {rootn[l]}")
print('roots total write GB', tot_w/1e9, 'read GB', tot_r/1e9)
leaf = collections.Counter(); leafn = collections.Counter()
for k, p in P.items():
    if p['first'] is None: continue
    if any(P[c]['start'] >= p['start'] for c in children.get(p['pid'], [])): continue
    kd = kind(p)
    for kk in ('write_bytes', 'read_bytes', 'syscw', 'cancelled_write_bytes'):
        leaf[(kd, kk)] += delta(p, kk)
    leafn[kd] += 1
print('LEAVES (no child seen): write GB, read GB, syscw, cancelled GB, n')
for l in sorted(leafn, key=lambda l: -leaf[(l, 'write_bytes')])[:25]:
    print(f"{l:40s} {leaf[(l,'write_bytes')]/1e9:8.3f} {leaf[(l,'read_bytes')]/1e9:8.3f} {leaf[(l,'syscw')]:9d} {leaf[(l,'cancelled_write_bytes')]/1e9:7.3f} {leafn[l]}")
print('leaves total write GB', sum(v for (l,k),v in leaf.items() if k=='write_bytes')/1e9)
