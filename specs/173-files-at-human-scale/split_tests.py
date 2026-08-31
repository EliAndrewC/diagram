#!/usr/bin/env python3
"""Feature 173's mover for an oversize TEST file: it mirrors the package its subject became.

Lineage: `025-human-scale-splits/split_tests.py`. The difference is that this one does not need a
cut table - once `hamletgen/ways.py` is `hamletgen/ways/`, every test already declares its own
destination by which names it exercises, so the split is DERIVED:

    test_route_goes_around_an_obstacle_rather_than_through_it   -> ways/route.py    -> test_route.py
    test_touch_junctions_does_not_close_a_short_lane_onto_...   -> ways/touch.py    -> test_touch.py

A test that names nothing from the package follows the test above it, which keeps a banner's run of
tests together. Shared fixtures and stub classes go to `_builders.py`, beside the existing
`tests/hamletgen/_builders.py` this file already imports from.

    python3 split_tests.py <test file> <subject package>
"""

from __future__ import annotations

import ast
import collections
import os
import subprocess
import sys

import split_module as sm


def submodule_names(pkg: str) -> dict[str, str]:
    """name -> the submodule of `pkg` that defines it."""
    home: dict[str, str] = {}
    for fn in sorted(os.listdir(pkg)):
        if not fn.endswith(".py") or fn == "__init__.py":
            continue
        tree = ast.parse(open(os.path.join(pkg, fn)).read())
        for node in tree.body:
            for name in sm.toplevel_names(node):
                home.setdefault(name, fn[:-3])
    return home


def main(argv: list[str]) -> int:
    path, pkg = argv[0], argv[1]
    src = sm.Source(path)
    home = submodule_names(pkg)
    nodes = src.body_nodes()
    entries = src.contiguous(nodes, src.header_end)

    tests = [i for i, n in enumerate(nodes) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    helpers = [i for i in range(len(nodes)) if i not in set(tests)]

    owner: dict[int, str] = {}
    last = ""
    for i in tests:
        seg = ast.get_source_segment(src.text, nodes[i]) or ""
        # ATTRIBUTE ACCESS IS HOW A TEST NAMES ITS SUBJECT HERE. Most of this file reaches the
        # engine as `hg.ways._touch_junctions(...)`, which is an ast.Attribute and not a free Name,
        # so a vote counted from free reads alone sees only the eight names the header imports
        # directly - and puts 92 of 103 tests in the two modules those eight happen to live in.
        used = set(sm.reads_of(seg))
        used |= {n.attr for n in ast.walk(ast.parse(seg)) if isinstance(n, ast.Attribute)}
        votes = collections.Counter(home[nm] for nm in used if nm in home)
        last = votes.most_common(1)[0][0] if votes else (last or sorted(set(home.values()))[0])
        owner[i] = last

    out = path[:-3].replace("test_", "", 1)
    os.makedirs(out, exist_ok=True)
    helper_names = {nm for i in helpers for nm in sm.toplevel_names(nodes[i])}
    hdr = f'"""Split from {os.path.basename(path)} by feature 173 - see this directory\'s CLAUDE.md."""\n\n'

    body = sm._deepen("".join(entries[i][1] for i in helpers))
    with open(os.path.join(out, "_builders.py"), "w") as fh:
        fh.write(hdr + sm._synth_imports(body, src, helper_names, {}, False, None) + "\n\n" + body.lstrip("\n"))

    groups: dict[str, list[int]] = collections.defaultdict(list)
    for i in tests:
        groups[owner[i]].append(i)
    written = []
    for mod, idxs in sorted(groups.items()):
        body = sm._deepen("".join(entries[i][1] for i in idxs))
        imports = sm._synth_imports(body, src, set(), dict.fromkeys(helper_names, "_builders"), False, None)
        text = hdr + imports + "\n\n" + body.lstrip("\n")
        name = f"test_{mod}.py"
        with open(os.path.join(out, name), "w") as fh:
            fh.write(text)
        written.append((text.count("\n"), name, len(idxs)))
    open(os.path.join(out, "__init__.py"), "w").close()
    os.remove(path)
    subprocess.run([sys.executable, "-m", "ruff", "check", "--fix", "-q", os.path.abspath(out)], check=False)
    subprocess.run([sys.executable, "-m", "ruff", "format", "-q", os.path.abspath(out)], check=False)
    for n, name, count in sorted(written, reverse=True):
        print(f"{n:6d}  {os.path.basename(out)}/{name}  ({count} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
