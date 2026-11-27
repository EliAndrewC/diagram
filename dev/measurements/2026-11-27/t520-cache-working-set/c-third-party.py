#!/usr/bin/env python3
"""T520 (c): how much of each tree's build cache is third-party crates, and how much of that is the same file in several trees.

Run: python3 -I c-third-party.py ROOT WORKSPACE_CRATES_FILE [SAMPLE]
  ROOT: ~/.cache/l7r-cargo-target; WORKSPACE_CRATES_FILE: one workspace crate name a line (underscored).
Read-only: stat for every file; the contents (sha256) only of SAMPLE third-party files present in 2+ trees (default 60),
read with O_NOATIME so no atime moves (the sweep reads atimes, 451 T515).

A file under <tree>/<profile>/{deps,build,.fingerprint} is THIRD-PARTY when its crate name (the part before the last
'-<hash>', 'lib' prefix dropped) is no workspace crate's; under incremental/ it is always the workspace's (cargo builds
registry crates non-incrementally). The key across trees is (profile, relative path): cargo's -C metadata hash is in the
file name, so the same name is the same unit of the same version, features, profile and flags.
"""
import collections
import hashlib
import os
import random
import re
import sys

root, wsfile = sys.argv[1], sys.argv[2]
sample = int(sys.argv[3]) if len(sys.argv) > 3 else 60
ws = {l.strip() for l in open(wsfile) if l.strip()}
ws |= {"build_script_build", "build_script_main"}  # a workspace crate's build script names; registry ones are under build/
TREES = ["diagram-backlog", "diagram-backlog-t269", "diagram-backlog-t270", "diagram-backlog-t271", "diagram-backlog-b1",
         "diagram-backlog-land", "diagram"]
hash_re = re.compile(r"^(?:lib)?(.+?)-[0-9a-f]{16}")


def crate_of(name):
    m = hash_re.match(name)
    return m.group(1).replace("-", "_") if m else None


per_tree = collections.defaultdict(lambda: collections.Counter())
where = collections.defaultdict(dict)  # (profile, rel) -> {tree: size}
for t in TREES:
    tdir = os.path.join(root, t)
    if not os.path.isdir(tdir):
        continue
    for prof in sorted(os.listdir(tdir)):
        pdir = os.path.join(tdir, prof)
        if not os.path.isdir(pdir):
            continue
        # a coverage family's cargo target is nested one level (cover-*/target/debug)
        bases = [pdir]
        if prof.startswith("cover-") and os.path.isdir(os.path.join(pdir, "target", "debug")):
            bases = [os.path.join(pdir, "target", "debug")]
        for base in bases:
            for dp, dns, fns in os.walk(base):
                rel_dir = os.path.relpath(dp, base)
                top = rel_dir.split(os.sep)[0]
                for fn in fns:
                    p = os.path.join(dp, fn)
                    try:
                        st = os.lstat(p)
                    except OSError:
                        continue
                    if not os.path.isfile(p) or os.path.islink(p):
                        continue
                    size = st.st_blocks * 512
                    if top == "incremental":
                        kind = "workspace"
                    elif top in ("deps", "build", ".fingerprint"):
                        seg = fn if top == "deps" else rel_dir.split(os.sep)[1] if len(rel_dir.split(os.sep)) > 1 else fn
                        c = crate_of(seg)
                        kind = "other" if c is None else ("workspace" if c in ws else "third")
                    else:
                        kind = "other"
                    per_tree[t][(prof, kind)] += size
                    if kind == "third":
                        where[(prof, os.path.join(rel_dir, fn))][t] = (size, p)

print("GB per tree, profile and kind (allocated blocks)")
for t in TREES:
    tot = collections.Counter()
    for (prof, kind), v in sorted(per_tree[t].items()):
        tot[kind] += v
    line = " ".join("%s=%.2f" % (k, v / 1e9) for k, v in sorted(tot.items()))
    print("%-22s %s" % (t, line))
    for (prof, kind), v in sorted(per_tree[t].items()):
        if v > 50e6:
            print("    %-14s %-9s %6.2f" % (prof, kind, v / 1e9))

# the same third-party unit across trees
dup_bytes = 0
saved = 0
multi = []
by_count = collections.Counter()
for key, trees in where.items():
    by_count[len(trees)] += 1
    if len(trees) > 1:
        sizes = [s for s, _ in trees.values()]
        dup_bytes += sum(sizes)
        saved += sum(sizes) - max(sizes)
        multi.append(key)
third_total = sum(v for t in TREES for (p, k), v in per_tree[t].items() if k == "third")
print("\nthird-party total %.2f GB; units by number of trees holding them: %s" % (third_total / 1e9, dict(sorted(by_count.items()))))
print("third-party bytes in units held by 2+ trees %.2f GB; one copy each would free %.2f GB" % (dup_bytes / 1e9, saved / 1e9))

# same profile name only (debug vs tool vs cover-* differ in flags, so their names differ anyway)
random.seed(520)
pick = random.sample(multi, min(sample, len(multi)))
# and the artifacts that hold the bytes: the 30 largest multi-tree .rlib/.rmeta/.so/.a units and 30 more at random
arts = [k for k in multi if k[1].endswith((".rlib", ".rmeta", ".so", ".a"))]
arts.sort(key=lambda k: -max(s for s, _ in where[k].values()))
rest = arts[30:]
pick += arts[:30] + random.sample(rest, min(30, len(rest)))
art_bytes = sum(sum(s for s, _ in where[k].values()) for k in arts)
print("of which .rlib/.rmeta/.so/.a artifacts: %d units, %.2f GB" % (len(arts), art_bytes / 1e9))
same = diff = 0
bytes_checked = 0
bytes_same = bytes_diff = 0
for key in pick:
    digests = set()
    for t, (size, p) in where[key].items():
        h = hashlib.sha256()
        fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
        with os.fdopen(fd, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        digests.add(h.hexdigest())
        bytes_checked += size
    kb = sum(sz for sz, _ in where[key].values())
    if len(digests) == 1:
        same += 1
        bytes_same += kb
    else:
        diff += 1
        bytes_diff += kb
        print("  DIFFERS:", key, sorted(where[key]))
print("sample of %d multi-tree third-party files (%.2f GB read): identical bytes in every tree %d, differing %d"
      % (len(pick), bytes_checked / 1e9, same, diff))
print("by bytes: identical %.2f GB, differing %.2f GB (differing = same size, a few bytes apart: rustc output not reproducible across trees)"
      % (bytes_same / 1e9, bytes_diff / 1e9))
