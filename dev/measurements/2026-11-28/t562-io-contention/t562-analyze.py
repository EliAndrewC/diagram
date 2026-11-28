#!/usr/bin/env python3
"""t562: analyze t562-sampler.py output. /proc/<pid>/io is INCLUSIVE of reaped children (tested: a shell's
write_bytes grew by a dd child's 20 MiB), so each process's EXCLUSIVE share = its delta minus the deltas of
its children seen to exit in the window. Usage: t562-analyze.py samples.json"""
import json, re, sys, collections

d = json.load(open(sys.argv[1]))
P, S = d['procs'], d['series']
T0, T1 = d['t0'], d['t1']
KEYS = ('write_bytes', 'read_bytes', 'syscw', 'wchar', 'cancelled_write_bytes')


def base(p, k):
    return 0 if p['born_in_window'] else p['first'][k]


def delta(p, k):
    return p['last'][k] - base(p, k)


alive_cut = max(p['last_t'] for p in P.values() if p['last_t']) - 1.0
kids = collections.defaultdict(list)
for key, p in P.items():
    if p['first'] is None:
        continue
    kids[p['ppid']].append(key)

excl = {}
for key, p in P.items():
    if p['first'] is None:
        continue
    e = {k: delta(p, k) for k in KEYS}
    for ck in kids.get(p['pid'], []):
        c = P[ck]
        if c['start'] < p['start'] or c['last_t'] >= alive_cut:
            continue  # not this incarnation's child, or still alive (not folded in)
        if c['last_t'] < p['first_t'] and not p['born_in_window']:
            continue  # reaped before the parent's baseline
        for k in KEYS:
            e[k] -= c['last'][k]  # the reaper's counter takes the child's WHOLE lifetime total at the reap
    excl[key] = e


def tree_of(p):
    for s in [p['cwd'], p['env'].get('CARGO_TARGET_DIR', ''), p['cmd']] + [a[2] for a in p['anc']]:
        m = re.search(r'/diagram/\.clones/([\w.-]+)', s) or re.search(r'l7r-cargo-target/([\w.-]+)', s)
        if m:
            return m.group(1)
    return '-'


def make_target(p):
    chain = [p['cmd']] + [a[2] for a in p['anc']]
    for c in chain:
        if re.match(r'\S*make\b', c):
            toks = [t for t in c.split()[1:] if not t.startswith('-') and '=' not in t]
            return 'make ' + (toks[0] if toks else '?')
    for c in chain:
        if 'l7r-gate lane' in c:
            return 'lane'
        if 'claude' in c.split()[0] if c else False:
            break
    return '(no make)'


def kind(p):
    c, comm = p['cmd'], p['comm']
    td = p['env'].get('CARGO_TARGET_DIR', '')
    cover = '/cover-' in td or '/cover-' in c
    if comm == 'rustc' or c.split()[:1] and c.split()[0].endswith('/rustc'):
        incr = ' -C incremental=' in c
        return 'rustc ' + ('cover' if cover else 'build') + (' incr' if incr else '')
    if '/deps/' in c.split()[0] if c else False:
        return 'test binary' + (' cover' if cover else '')
    if comm in ('ld.lld', 'lld', 'cc', 'ld'):
        return 'linker' + (' cover' if cover else '')
    if comm == 'cargo':
        return 'cargo' + (' cover' if cover else '')
    if comm in ('git', 'git-remote-http'):
        return 'git'
    if comm.startswith('l7r-'):
        return comm
    if comm in ('claude', 'node'):
        return 'claude'
    if comm.startswith('python'):
        return 'python3 ' + ('sampler' if 'sampler' in c else '')
    if 'llvm-profdata' in c or 'llvm-cov' in c:
        return 'llvm-cov/profdata'
    return comm


groups = {name: collections.Counter() for name in ('kind', 'target', 'tree', 'kind_target')}
for key, e in excl.items():
    p = P[key]
    labels = {'kind': kind(p), 'target': make_target(p), 'tree': tree_of(p)}
    labels['kind_target'] = labels['kind'] + ' | ' + labels['target']
    for g, lab in labels.items():
        for k in KEYS:
            groups[g][(lab, k)] += e[k]
        groups[g][(lab, 'n')] += 1

tot = collections.Counter()
for e in excl.values():
    for k in KEYS:
        tot[k] += e[k]

# system deltas
s0, s1 = S[0], S[-1]
def iostat(s):
    m = dict(kv.split('=') for kv in s['cg_io_stat'].split()[1:])
    return int(m['rbytes']), int(m['wbytes']), int(m['rios']), int(m['wios'])
r0, w0, ri0, wi0 = iostat(s0); r1, w1, ri1, wi1 = iostat(s1)
dk0, dk1 = s0['disk'], s1['disk']
dur = s1['t'] - s0['t']
def jb(s):
    t = s['jbd2']
    n = int(re.search(r'(\d+) transactions \(', t).group(1))
    commit = int(re.search(r'(\d+)us average transaction commit', t).group(1))
    run = int(re.search(r'(\d+)ms running transaction', t).group(1))
    blocks = int(re.search(r'(\d+) blocks per transaction', t).group(1))
    handles = int(re.search(r'(\d+) handles per transaction', t).group(1))
    req = int(re.search(r'\((\d+) requested\)', t).group(1))
    return n, req, commit, run, blocks, handles
def psi(text, which):
    for line in text.splitlines():
        if line.startswith(which):
            return dict(kv.split('=') for kv in line.split()[1:])
out = {}
out['window'] = dict(t0=T0, t1=T1, seconds=round(dur))
out['cgroup_io'] = dict(read_GB=(r1-r0)/1e9, write_GB=(w1-w0)/1e9, read_ios=ri1-ri0, write_ios=wi1-wi0)
out['disk'] = dict(read_GB=(dk1[2]-dk0[2])*512/1e9, write_GB=(dk1[6]-dk0[6])*512/1e9,
                   read_ms=dk1[3]-dk0[3], write_ms=dk1[7]-dk0[7], io_ticks_ms=dk1[9]-dk0[9],
                   weighted_ms=dk1[10]-dk0[10], flush_ios=(dk1[15]-dk0[15]) if len(dk1) > 15 else None,
                   flush_ms=(dk1[16]-dk0[16]) if len(dk1) > 16 else None)
out['ext4_lifetime_write_GB'] = (s1['ext4_lw_kb']-s0['ext4_lw_kb'])*1024/1e9
out['refault_file_GB'] = (s1['cg_mem']['workingset_refault_file']-s0['cg_mem']['workingset_refault_file'])*4096/1e9
out['pgscan_direct_GB'] = (s1['cg_mem']['pgscan_direct']-s0['cg_mem']['pgscan_direct'])*4096/1e9
out['cg_io_psi_full_s'] = (int(psi(s1['cg_io_psi'],'full')['total'])-int(psi(s0['cg_io_psi'],'full')['total']))/1e6
out['cg_io_psi_some_s'] = (int(psi(s1['cg_io_psi'],'some')['total'])-int(psi(s0['cg_io_psi'],'some')['total']))/1e6
out['host_io_psi_full_s'] = (int(psi(s1['psi_io'],'full')['total'])-int(psi(s0['psi_io'],'full')['total']))/1e6
out['host_io_psi_some_s'] = (int(psi(s1['psi_io'],'some')['total'])-int(psi(s0['psi_io'],'some')['total']))/1e6
out['cg_mem_psi_full_s'] = (int(psi(s1['cg_mem_psi'],'full')['total'])-int(psi(s0['cg_mem_psi'],'full')['total']))/1e6
out['cg_mem_psi_some_s'] = (int(psi(s1['cg_mem_psi'],'some')['total'])-int(psi(s0['cg_mem_psi'],'some')['total']))/1e6
j0, j1 = jb(s0), jb(s1)
out['jbd2'] = dict(transactions=j1[0]-j0[0], requested=j1[1]-j0[1],
                   commit_us_series=[jb(s)[2] for s in S], running_ms_series=[jb(s)[3] for s in S],
                   blocks_series=[jb(s)[4] for s in S], handles_series=[jb(s)[5] for s in S])
c0, c1 = s0['cpu'], s1['cpu']
out['cpu_iowait_pct'] = 100*(c1[4]-c0[4])/max(1, sum(c1)-sum(c0))
out['blocked_series'] = [s.get('procs_blocked') for s in S]
out['dirty_MB_series'] = [round(s['cg_mem']['file_dirty']/1e6) for s in S]
out['memcur_GB_series'] = [round(s['cg_mem_cur']/1e9, 2) for s in S]
out['psi_full_avg10_series'] = [float(psi(s['psi_io'],'full')['avg10']) for s in S]
out['proc_sum'] = {k: tot[k] for k in KEYS}
out['nprocs'] = len(excl)

def table(g, sortkey='write_bytes', n=30):
    labs = {lab for (lab, k) in groups[g]}
    rows = sorted(labs, key=lambda l: -groups[g][(l, sortkey)])[:n]
    return [[l, groups[g][(l, 'n')], round(groups[g][(l, 'write_bytes')]/1e9, 3), round(groups[g][(l, 'read_bytes')]/1e9, 3),
             groups[g][(l, 'syscw')], round(groups[g][(l, 'cancelled_write_bytes')]/1e9, 3)] for l in rows]
for g in groups:
    out['by_' + g] = table(g)
    out['by_' + g + '_reads'] = table(g, 'read_bytes', 15)
json.dump(out, sys.stdout, indent=1)
