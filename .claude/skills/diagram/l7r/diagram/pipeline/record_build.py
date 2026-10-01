"""The record's site, built on the main checkout when - and only when - something it is built from changed (feature 301).

The GM, 2026-10-01: *"I do want these files to end up on main. Like on the main checkout, I mean, just not checked into
main ... that's the same thing that we are doing with our generated map files ... when something lands on the main, then
we regenerate ... if they would change, but we do not regenerate them otherwise."* So render-sync calls this after the
map renders (`render_cache.main`), on the map renders' model: a STAMP of every input, written beside the site, and a
build only when the stamp differs (spec FR-010).

The inputs are what the build actually reads (plan review item 3, 2026-10-01): every file under `research/` that is not
itself built and is not prose about the record - the fragments, the hand-written assets, `confusables.json` - the
glossary's JSON the derived script is written from, and every module of the engine the build has imported, taken from
`sys.modules` after the build's own imports rather than listed, so a module the build comes to depend on is in the stamp
the day it is imported. A change to anything else - a map's generator, a placer, a doc - leaves the site alone.
"""

from __future__ import annotations

import hashlib
import os
import sys
from collections.abc import Callable, Iterable

#: Where the stamp lives: inside the site, so a site deleted by hand takes its stamp with it and is rebuilt.
STAMP = ".stamp"
SITE = "site"
_GLOSSARY = os.path.join("l7r", "diagram", "interactive", "assets", "glossary.json")


def is_input(rel: str) -> bool:
    """Is this file under `research/` something the build reads? Not the site, not a page or citations page or glossary
    script the assembly wrote before 301 (ignored, and perhaps still on disk in an old checkout), not prose. Since
    feature 303 every page the old assembly wrote sat at the record's root, so a root `.html` is never an input."""
    top, _, _rest = rel.partition("/")
    if top in (SITE, "citations") or top.startswith(".site-") or rel == "assets/glossary.js" or rel.endswith(".md"):
        return False
    directory, name = os.path.split(rel)
    return not (name.endswith(".html") and directory == "")


def record_files(research_dir: str) -> list[str]:
    """Every file under `research/` the build reads, as paths relative to it, sorted."""
    out: list[str] = []
    for base, dirs, names in os.walk(research_dir):
        dirs[:] = [d for d in dirs if d not in (SITE, "citations") and not d.startswith(".site-")]
        for name in names:
            rel = os.path.relpath(os.path.join(base, name), research_dir).replace(os.sep, "/")
            if is_input(rel):
                out.append(rel)
    return sorted(out)


def engine_modules(skill_dir: str) -> list[str]:
    """The engine's modules this process has imported - after `site` is, every module the build runs."""
    from l7r.diagram.interactive.record import site  # noqa: F401, PLC0415 - imported for what it imports

    root = os.path.join(os.path.abspath(skill_dir), "l7r") + os.sep
    files = {getattr(m, "__file__", None) or "" for m in list(sys.modules.values())}
    return sorted(f for f in files if f.startswith(root) and f.endswith(".py"))


def fingerprint(skill_dir: str, modules: Iterable[str] | None = None) -> str:
    """One hash over every input of the build: the record's files, the glossary's JSON, the engine modules."""
    research = os.path.join(skill_dir, "research")
    paths = [os.path.join(research, r) for r in record_files(research)]
    paths.append(os.path.join(skill_dir, _GLOSSARY))
    paths += list(engine_modules(skill_dir) if modules is None else modules)
    h = hashlib.sha256()
    for path in paths:
        h.update(os.path.relpath(path, skill_dir).replace(os.sep, "/").encode("utf-8") + b"\0")
        try:
            with open(path, "rb") as fh:
                h.update(hashlib.sha256(fh.read()).digest())
        except OSError:
            h.update(b"-")
    return h.hexdigest()


def read_stamp(site_dir: str) -> str:
    try:
        with open(os.path.join(site_dir, STAMP), encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return ""


def rebuild_if_stale(
    skill_dir: str,
    build: Callable[[str], dict[str, str]] | None = None,
    write: Callable[[dict[str, str], str], None] | None = None,
    modules: Iterable[str] | None = None,
) -> bool:
    """Build the site when its stamp differs from its inputs; True when it built. `build`, `write` and `modules` are the
    real ones unless a test hands its own."""
    from l7r.diagram.interactive.record import site  # noqa: PLC0415 - the build is imported only where it may run

    research = os.path.join(skill_dir, "research")
    out = os.path.join(research, SITE)
    want = fingerprint(skill_dir, modules)
    if read_stamp(out) == want:
        return False
    files = (build or site.build)(research)
    files[STAMP] = want + "\n"
    (write or site.write)(files, out)
    return True
