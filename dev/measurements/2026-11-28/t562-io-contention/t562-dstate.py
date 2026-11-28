#!/usr/bin/env python3
"""t562: every 0.2 s, count each process's state; for D (uninterruptible, mostly IO) record its wchan.
Output counters as JSON at the end. Usage: t562-dstate.py OUT.json SECONDS"""
import json, os, sys, time, collections
OUT, DUR = sys.argv[1], float(sys.argv[2])
SELF = os.getpid()
T0 = time.time()
n = 0
states = collections.Counter()          # (comm, state)
dw = collections.Counter()              # (comm, wchan)
dtree = collections.Counter()           # (tree, comm, wchan)
per_sample_D = []
cwdcache = {}
while time.time() - T0 < DUR:
    t = time.time()
    nd = 0
    for name in os.listdir('/proc'):
        if not name.isdigit() or int(name) == SELF:
            continue
        try:
            s = open(f'/proc/{name}/stat').read()
        except OSError:
            continue
        r = s.rfind(')')
        comm = s[s.find('(') + 1:r]
        st = s[r + 2]
        states[(comm, st)] += 1
        if st == 'D':
            nd += 1
            try:
                w = open(f'/proc/{name}/wchan').read().strip()
            except OSError:
                w = '?'
            dw[(comm, w)] += 1
            if name not in cwdcache:
                try:
                    c = os.readlink(f'/proc/{name}/cwd')
                except OSError:
                    c = ''
                cwdcache[name] = c.split('/diagram/.clones/')[-1].split('/')[0] if '/diagram/.clones/' in c else c[:40]
            dtree[(cwdcache[name], comm, w)] += 1
    per_sample_D.append(nd)
    n += 1
    time.sleep(max(0, 0.2 - (time.time() - t)))
json.dump({'t0': T0, 't1': time.time(), 'samples': n, 'period_s': 0.2,
           'states': [[a, b, c] for (a, b), c in states.most_common()],
           'dwchan': [[a, b, c] for (a, b), c in dw.most_common()],
           'dtree': [[a, b, c, k] for (a, b, c), k in dtree.most_common(200)],
           'per_sample_D': per_sample_D}, open(OUT, 'w'))
