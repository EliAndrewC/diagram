#!/usr/bin/env python3
"""t562: the LEAVES (processes with no child seen: their /proc io is their own) by make target, by tree, and by
kind within target - the lane's work marked by an ancestor `l7r-gate lane --work`. Usage: t562-leaves.py samples.json"""
import json, re, sys, collections
src = open(sys.argv[0].replace('t562-leaves.py', 't562-analyze.py')).read().split('groups = {')[0]
exec(src)
children = collections.defaultdict(list)
for k, p in P.items(): children[p['ppid']].append(k)
def target(p):
    chain = [p['cmd']] + [a[2] for a in p['anc']]
    lane = any('lane --work' in c for c in chain)
    t = make_target(p)
    if t == '(no make)':
        for c in chain:
            m = re.search(r'l7r-gate(?:\.sh)? (rust \w+|\w+)', c)
            if m: t = 'l7r-gate ' + m.group(1); break
    return ('lane: ' if lane else '') + t
G = {g: collections.Counter() for g in ('target', 'tree', 'kind in target')}
N = {g: collections.Counter() for g in G}
tot = 0
for k, p in P.items():
    if p['first'] is None: continue
    if any(P[c]['start'] >= p['start'] for c in children.get(p['pid'], [])): continue
    w = delta(p, 'write_bytes'); tot += w
    labs = {'target': target(p), 'tree': tree_of(p)}
    labs['kind in target'] = kind(p) + ' | ' + labs['target']
    for g, l in labs.items(): G[g][l] += w; N[g][l] += 1
print(f'leaves wrote {tot/1e9:.2f} GB of the cgroup\'s 29.57 GB; the rest is unlabeled (short-lived, ended threads, deleted files)')
for g in G:
    print(f'\n## by {g}: GB written, processes')
    for l, v in G[g].most_common(16): print(f'{l:60s} {v/1e9:7.3f} {N[g][l]}')
