#!/usr/bin/env python3
"""T278: a smaller keep's take NET of T515's prune. T515 (sweep/prune.rs) already takes an entry unread in L7R_CACHE_STALE_HOURS (48)
before its profile's own last use; "last use" the newest mtime in it and the newest atime of any file in it but a `.json`. This prints,
per cover-<family> directory, the variants rule's take at keep K (idle cutoff 12 h) and the part of it T515 would NOT take - the
lever's own gain. An approximation of T515: a profile is the directory's `target/debug`, and "not the newest of its kind" is not
applied (it only keeps more, so the net is an upper bound). lstat only.

usage: t278-net.py [DIR ...]"""
import glob
import importlib.util
import os
import sys
import time

spec = importlib.util.spec_from_file_location("c", os.path.join(os.path.dirname(os.path.abspath(__file__)), "t278-count.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
STALE = 48 * 3600
KEEPS = [8, 4, 2]


def use(path):
    st = os.lstat(path)
    m, a, b = st.st_mtime, (0 if path.endswith(".json") else st.st_atime), st.st_blocks * 512
    if os.path.isdir(path) and not os.path.islink(path):
        a = 0
        for e in os.scandir(path):
            m2, a2, b2 = use(e.path)
            m, a, b = max(m, m2), max(a, a2), b + b2
    return m, a, b


def main(roots):
    now = time.time()
    print("dir\tGB\t" + "\t".join(f"k{k}_take_GB\tk{k}_net_of_T515_GB" for k in KEEPS))
    for root in roots:
        groups, total, last = {}, 0, 0
        for store in c.stores(root):
            for e in os.scandir(store):
                m, a, b = use(e.path)
                total += b
                last = max(last, m, a)
                groups.setdefault((store, c.variant_of(e.name)), []).append((m, max(m, a), b))
        cells = []
        for k in KEEPS:
            take = net = 0
            for v in groups.values():
                for m, u, b in sorted(v, reverse=True)[k:]:
                    if m < now - 12 * 3600:
                        take += b
                        net += b if u >= last - STALE else 0
            cells += [f"{take / 1e9:.2f}", f"{net / 1e9:.2f}"]
        print("\t".join([root.replace(os.path.expanduser("~/.cache/l7r-cargo-target/"), ""), f"{total / 1e9:.2f}"] + cells))


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(glob.glob(os.path.expanduser("~/.cache/l7r-cargo-target/*/cover-*"))))
