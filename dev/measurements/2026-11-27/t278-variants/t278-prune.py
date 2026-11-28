#!/usr/bin/env python3
"""T278: the sweep's variants rule (rust/guard/src/guards/scratch_sweep_hooks/sweep/cargo.rs, `stale_variants`: each store's
entries grouped by `variant_of`, ranked by newest mtime, those past the newest KEEP and idle past HOURS taken) applied to a COPY of
a build directory, with KEEP and HOURS as arguments - the levers priced. With LIVE (a build's JSON messages), it first says which
entries that build used would go: the hashes in every compiler-artifact's filenames and every build-script-executed out_dir.

usage: t278-prune.py DIR KEEP HOURS [--live MESSAGES.json] [--apply]
Refuses a DIR under ~/.cache/l7r-cargo-target: it never touches a live cache."""
import importlib.util
import json
import os
import re
import shutil
import sys
import time

spec = importlib.util.spec_from_file_location("c", os.path.join(os.path.dirname(os.path.abspath(__file__)), "t278-count.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def live_hashes(path):
    out = set()
    for line in open(path):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        paths = m.get("filenames", []) + ([m["out_dir"]] if m.get("out_dir") else []) + ([m["executable"]] if m.get("executable") else [])
        for p in paths:
            for h in re.findall(r"-([0-9a-f]{16})(?:[./]|$)", p):
                out.add(h)
    return out


def main():
    args = sys.argv[1:]
    root, keep, hours = os.path.abspath(args[0]), int(args[1]), float(args[2])
    if root.startswith(os.path.expanduser("~/.cache/l7r-cargo-target")):
        sys.exit("t278-prune: refusing a live cache; give it a copy")
    live = live_hashes(args[args.index("--live") + 1]) if "--live" in args else set()
    apply = "--apply" in args
    cut = time.time() - hours * 3600
    groups = {}
    for store in c.stores(root):
        for e in os.scandir(store):
            t, b = c.walk(e.path)
            groups.setdefault((store, c.variant_of(e.name)), []).append((t, b, e.path))
    taken, nbytes, live_taken, ties = [], 0, [], 0
    for v in groups.values():
        v.sort(key=lambda x: x[0], reverse=True)
        if len(v) > keep and v[keep - 1][0] == v[keep][0]:
            ties += 1
        for t, b, p in v[keep:]:
            if t < cut:
                taken.append(p)
                nbytes += b
                m = re.search(r"-([0-9a-f]{16})(?:\.|$)", os.path.basename(p))
                if m and m.group(1) in live:
                    live_taken.append(os.path.relpath(p, root))
    print(f"keep={keep} hours={hours}: {len(taken)} entries, {nbytes / 1e9:.2f} GB; groups tied at the cut {ties}; "
          f"live hashes {len(live)}; live entries taken {len(live_taken)}")
    for p in sorted(live_taken):
        print("  LIVE TAKEN", p)
    if apply:
        for p in taken:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
        print("applied")


if __name__ == "__main__":
    main()
