#!/usr/bin/env python3
"""t562: per-process IO sampler + system IO series. Reads /proc only; writes one JSON at the end
(and a checkpoint every 30 s) into the output directory. Usage: t562-sampler.py OUTDIR SECONDS"""
import json, os, sys, time

OUT, DUR = sys.argv[1], float(sys.argv[2])
FAST, SLOW = 0.5, 5.0
os.makedirs(OUT, exist_ok=True)
CLK = os.sysconf('SC_CLK_TCK')
BOOT = time.time() - float(open('/proc/uptime').read().split()[0])
SELF = os.getpid()


def rd(p):
    try:
        with open(p, 'rb') as f:
            return f.read()
    except OSError:
        return None


def stat(pid):
    s = rd(f'/proc/{pid}/stat')
    if not s:
        return None
    s = s.decode(errors='replace')
    r = s.rfind(')')
    comm = s[s.find('(') + 1:r]
    f = s[r + 2:].split()
    return comm, int(f[1]), BOOT + int(f[19]) / CLK  # comm, ppid, starttime(epoch)


def pio(pid):
    s = rd(f'/proc/{pid}/io')
    if not s:
        return None
    d = {}
    for line in s.decode().splitlines():
        k, v = line.split(':')
        d[k] = int(v)
    return d


procs = {}  # key "pid:start" -> info
T0 = time.time()


def ident(pid):
    st = stat(pid)
    if not st:
        return None
    comm, ppid, start = st
    key = f'{pid}:{int(start*100)}'
    if key not in procs:
        cmd = (rd(f'/proc/{pid}/cmdline') or b'').replace(b'\0', b' ').decode(errors='replace')[:400]
        try:
            cwd = os.readlink(f'/proc/{pid}/cwd')
        except OSError:
            cwd = ''
        env = rd(f'/proc/{pid}/environ') or b''
        envd = {}
        for kv in env.split(b'\0'):
            for want in (b'CARGO_TARGET_DIR=', b'TMPDIR=', b'CARGO_INCREMENTAL=', b'L7R_', b'MAKELEVEL='):
                if kv.startswith(want):
                    k, _, v = kv.decode(errors='replace').partition('=')
                    envd[k] = v[:200]
        # ancestry at first sight
        anc = []
        p = ppid
        for _ in range(12):
            if p <= 1:
                break
            a = stat(p)
            if not a:
                break
            c = (rd(f'/proc/{p}/cmdline') or b'').replace(b'\0', b' ').decode(errors='replace')[:300]
            anc.append([p, a[0], c])
            p = a[1]
        procs[key] = dict(pid=pid, comm=comm, ppid=ppid, start=start, cmd=cmd, cwd=cwd, env=envd,
                          anc=anc, born_in_window=start > T0, first=None, last=None,
                          first_t=None, last_t=None)
    return key


series = []


def sysread():
    d = {'t': time.time()}
    d['psi_io'] = (rd('/proc/pressure/io') or b'').decode()
    d['cg_io_psi'] = (rd('/sys/fs/cgroup/io.pressure') or b'').decode()
    d['cg_mem_psi'] = (rd('/sys/fs/cgroup/memory.pressure') or b'').decode()
    d['cg_io_stat'] = (rd('/sys/fs/cgroup/io.stat') or b'').decode()
    ms = {}
    for line in (rd('/sys/fs/cgroup/memory.stat') or b'').decode().splitlines():
        k, v = line.split()
        if k in ('file', 'anon', 'file_dirty', 'file_writeback', 'workingset_refault_file', 'pgscan_direct',
                 'pgscan_kswapd', 'pgsteal_direct', 'slab_reclaimable', 'active_file', 'inactive_file'):
            ms[k] = int(v)
    d['cg_mem'] = ms
    d['cg_mem_cur'] = int((rd('/sys/fs/cgroup/memory.current') or b'0').strip())
    d['jbd2'] = (rd('/proc/fs/jbd2/nvme0n1p3-8/info') or b'').decode()
    for line in (rd('/proc/diskstats') or b'').decode().splitlines():
        f = line.split()
        if f[2] == 'nvme0n1':
            d['disk'] = [int(x) for x in f[3:]]
    vm = {}
    for line in (rd('/proc/vmstat') or b'').decode().splitlines():
        k, v = line.split()
        if k in ('nr_dirty', 'nr_writeback', 'pgpgin', 'pgpgout', 'workingset_refault_file', 'pgmajfault',
                 'nr_dirtied', 'nr_written'):
            vm[k] = int(v)
    d['vm'] = vm
    for line in (rd('/proc/stat') or b'').decode().splitlines():
        if line.startswith('procs_blocked') or line.startswith('procs_running'):
            k, v = line.split()
            d[k] = int(v)
        elif line.startswith('cpu '):
            d['cpu'] = [int(x) for x in line.split()[1:]]
    d['load'] = (rd('/proc/loadavg') or b'').decode().strip()
    d['ext4_lw_kb'] = int((rd('/sys/fs/ext4/nvme0n1p3/lifetime_write_kbytes') or b'0').strip())
    # who is running: make targets / cargo with cwd
    return d


def checkpoint(final=False):
    tmp = os.path.join(OUT, 'samples.json.tmp')
    with open(tmp, 'w') as f:
        json.dump({'t0': T0, 't1': time.time(), 'final': final, 'procs': procs, 'series': series}, f)
    os.replace(tmp, os.path.join(OUT, 'samples.json'))


last_slow = 0
last_ck = time.time()
while time.time() - T0 < DUR:
    now = time.time()
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid == SELF:
            continue
        key = ident(pid)
        if not key:
            continue
        io = pio(pid)
        if not io:
            continue
        p = procs[key]
        if p['first'] is None:
            p['first'], p['first_t'] = io, now
        p['last'], p['last_t'] = io, now
    if now - last_slow >= SLOW:
        series.append(sysread())
        last_slow = now
    if now - last_ck >= 30:
        checkpoint()
        last_ck = now
    time.sleep(max(0, FAST - (time.time() - now)))
series.append(sysread())
checkpoint(final=True)
