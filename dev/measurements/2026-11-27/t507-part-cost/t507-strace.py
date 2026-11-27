#!/usr/bin/env python3
"""t507: what one bash-pre call (record-edit-hooks PreToolUse, a Bash `true` under a hold) does with the state file, by strace.

usage: t507-strace.py <guard bin> <state copy> <scratch dir>
Prints how often the state is opened and read, the bytes read, and the memory syscalls, from `strace -f`."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
fx_mod = importlib.import_module('t507-fixture')

BIN, SRC, BASE = sys.argv[1:4]
fx = fx_mod.fixture(BASE, 'strace', SRC)
fx_mod.call([BIN, '--only', 'record-edit-hooks', 'PreToolUse'], fx, fx_mod.bash_pre(fx, 'first'))
out = os.path.join(BASE, 't507-strace.log')
fx_mod.call(['strace', '-f', '-yy', '-o', out, BIN, '--only', 'record-edit-hooks', 'PreToolUse'], fx, fx_mod.bash_pre(fx, 2))
lines = open(out).read().splitlines()
opens = [l for l in lines if 'openat' in l and 'checks-open' in l]
reads = [l for l in lines if re.search(r'\bread\(\d+<[^>]*checks-open', l)]
nbytes = sum(int(m.group(1)) for l in reads if (m := re.search(r'= (\d+)$', l)))
kinds = {}
for l in lines:
    m = re.match(r'\d+\s+(\w+)\(', l)
    if m:
        kinds[m.group(1)] = kinds.get(m.group(1), 0) + 1
print(f'syscalls {len(lines)}; state opened {len(opens)}x; read() calls on it {len(reads)}, {nbytes} bytes')
for l in opens:
    print('  ', l[:160])
print('by syscall:', ', '.join(f'{k} {v}' for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])))
big = [l for l in lines if re.search(r'mmap\(NULL, (\d+)', l) and int(re.search(r'mmap\(NULL, (\d+)', l).group(1)) > 1 << 20]
print('mmaps over 1 MiB:')
for l in big:
    print('  ', l[:160])
