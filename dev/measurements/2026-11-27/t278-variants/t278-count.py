#!/usr/bin/env python3
"""451/462 T278 thing 1: the variants a crate in every cover-<family> build directory, read by lstat alone (no file opened, so no
atime moves). For each store (`deps`, `incremental`, `.fingerprint`, `build`) the entries are grouped as the sweep groups them
(`variant_of` in rust/guard/src/guards/scratch_sweep_hooks/sweep/cargo.rs), each entry's age its newest mtime (`newest`), and the
script prints per directory: groups, entries, the largest group, entries built since T325 landed, and the bytes the variants rule
would take at keep K and idle cutoff H for each K in KEEPS and H in HOURS (H=0: no idle wait).

usage: t278-count.py [ROOT ...]   (default: every ~/.cache/l7r-cargo-target/*/cover-*)
"""
import glob
import os
import sys
import time

STORES = {"deps", "incremental", ".fingerprint", "build"}
KEEPS = [16, 8, 4, 2, 1]
HOURS = [12, 6, 1, 0]
T325 = 1795740133  # 2026-11-26 19:42:13 -0500, `make land` of T325 (49d0f3c96d)


def variant_of(name):
    stem, ext = name, ""
    if "." in name:
        s, e = name.rsplit(".", 1)
        if s and "-" not in e:
            stem, ext = s, e
    base = stem.rsplit("-", 1)[0] if "-" in stem else stem
    return f"{base}.{ext}"


def walk(path):
    """(newest mtime, bytes on disk) of a path and everything under it, by lstat."""
    st = os.lstat(path)
    newest, size = st.st_mtime, st.st_blocks * 512
    if os.path.isdir(path) and not os.path.islink(path):
        for e in os.scandir(path):
            n, s = walk(e.path)
            newest, size = max(newest, n), size + s
    return newest, size


def stores(root, depth=5):
    for e in os.scandir(root):
        if e.is_dir(follow_symlinks=False):
            if e.name in STORES:
                yield e.path
            elif depth > 1:
                yield from stores(e.path, depth - 1)


def main(roots):
    now = time.time()
    print("dir\tgroups\tentries\tmax_group\tgroups_over_16\tgroups_over_4\tgroups_over_2\tentries_since_T325\tGB\t"
          + "\t".join(f"take_k{k}_h{h}_GB" for k in KEEPS for h in HOURS))
    for root in roots:
        groups = {}
        total = 0
        since = 0
        for store in stores(root):
            for e in os.scandir(store):
                t, b = walk(e.path)
                total += b
                since += t >= T325
                groups.setdefault((store, variant_of(e.name)), []).append((t, b))
        take = {}
        for k in KEEPS:
            for h in HOURS:
                cut = now - h * 3600
                take[k, h] = sum(b for v in groups.values()
                                 for t, b in sorted(v, reverse=True)[k:] if t < cut)
        sizes = [len(v) for v in groups.values()]
        print("\t".join(str(x) for x in [
            root.replace(os.path.expanduser("~/.cache/l7r-cargo-target/"), ""), len(groups), sum(sizes), max(sizes, default=0),
            sum(s > 16 for s in sizes), sum(s > 4 for s in sizes), sum(s > 2 for s in sizes), since, f"{total / 1e9:.2f}"]
            + [f"{take[k, h] / 1e9:.2f}" for k in KEEPS for h in HOURS]))


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(glob.glob(os.path.expanduser("~/.cache/l7r-cargo-target/*/cover-*"))))
