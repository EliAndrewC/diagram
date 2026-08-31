"""Content-hash short-circuit for regenerating the diagram pool renders in main.

WHY (GM 2026-07-22): the stop-work procedure used to BUILD the map renders in a session clone and
COPY them into main (rsync + byte-verify). That was fragile: whether a clone had touched a given
render was situational, so a stale copy could linger in main. The new rule is simpler and cannot
go stale - after the push, main REGENERATES its own renders from its own tip. Renders become a
pure function of main's committed code; nothing is copied, so nothing can be copied stale.

"Always regenerate after every push" is self-healing (main re-derives correct renders from its
tip regardless of history), but a full pool regen is ~30s parallel / ~2min serial - wasteful on a
push that changed nothing a map depends on. So each derived (Mode B, gitignored) svg carries a
stamp of everything that determines its output: `<!-- render-cache: <sha256> -->`, where the hash
covers the map's own generator source AND the shared engine sources. Regeneration skips any map
whose stamp still matches and whose png is present; a stale stamp or a missing png forces a rerun.
The upshot: change one map's gen.py and only that map regenerates; change the engine and every
map's stamp goes stale, forcing the full refresh the doctrine already required. No stale render can
survive, because the stamp is a pure function of the source that produced it.

The png is deliberately NOT separately hashed. Every generator writes its svg and png together in
one run (settlement.finish -> render_png), so an up-to-date stamped svg with its png present proves
the pair is current; the only extra guard needed is "png exists", which catches a manual `rm`. A
present-but-corrupted png is the one thing caching cannot heal - an accepted tradeoff for the
short-circuit (a hand-deleted png still self-heals; delete it to force a rerun). (GM 2026-07-22.)

Mode A magistracy plans are exempt: their svg is tracked SOURCE (only the png is gitignored), so
regenerating must reproduce it byte-for-byte and it is never stamped (a comment would dirty a
tracked file). They are simply always re-run - there are few, and the point is the gitignored png.
The Mode A/B split is read from git itself (`git check-ignore` on the predicted svg), so it tracks
the .gitignore's source/derived boundary automatically instead of duplicating it here.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import os
import re
import subprocess
import sys

from . import pool_index, poolmaps

SKILL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)  # the skill root; this module lives in l7r/diagram/pipeline/ - FOUR levels up since feature 119, not two

# Bump to force a one-time full refresh after any change to how the stamp is computed: an old
# stamp computed under a different version can never equal a new input_hash, so every map reruns.
STAMP_ALGO_VERSION = b"v1"

# The stamp sits right after the "<svg ...>" opening tag; optional leading newline so a re-stamp
# strips the whole line cleanly rather than leaving a blank one.
_STAMP_RE = re.compile(rb"\n?<!-- render-cache: ([0-9a-f]{64}) -->")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _predicted_svg(gen_path: str) -> str:
    """Mode B generators all write <dir>/<stem>.svg (+ .png + .json) via settlement.finish() -
    a convention every settlement gen follows, so the output path is knowable without running."""
    return gen_path[: -len(".gen.py")] + ".svg"


def engine_fingerprint(skill_dir: str = SKILL_DIR) -> str:
    """Hash of every render-determining engine source: all *.py under the skill dir AT ANY DEPTH
    (feature 025 made settlement/ a package, so root-only listing would silently DROP the main
    engine from the fingerprint), excluding test files and test packages, pool/ and wip/ trees,
    and this module. Any engine edit changes this -> every map's input_hash goes stale -> full
    refresh.

    Deliberately a SAFE SUPERSET: including a non-rendering module (an audit tool, the validator
    package) costs at most one needless full regen, whereas UNDER-including a module that does
    affect pixels would silently serve stale renders - the exact outcome this whole mechanism
    exists to prevent. This module is excluded because a change to the cache logic already
    invalidates old stamps by value (an old stamp cannot match a new hash), so it need not also
    be in the fingerprint; test files are excluded because they never determine a render."""
    parts: list[bytes] = []
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        # PRUNED BY NAME, so a NEW TOP-LEVEL TREE MUST BE ADDED HERE (feature 161). The legacy
        # tree is map sources, not engine sources: if its 18 frozen gens entered this
        # fingerprint, every live map's stamp would go stale at once and any future edit to a
        # frozen exhibit would invalidate the whole live pool - backwards, since the freeze
        # exists so those files cost nothing. Nothing would go red; both outcomes look exactly
        # like a cache working normally. `poolmaps.TREES` is the list, so it cannot drift.
        dirnames[:] = sorted(d for d in dirnames if d not in (*poolmaps.TREES, "wip", "tests", "__pycache__") and not d.startswith(("test_", ".")))
        rel_dir = os.path.relpath(dirpath, skill_dir)
        for name in sorted(filenames):
            if not name.endswith(".py") or name.startswith("test_") or name == os.path.basename(__file__):
                continue
            rel = os.path.normpath(os.path.join(rel_dir, name))
            with open(os.path.join(dirpath, name), "rb") as fh:
                parts.append(rel.encode() + b"\0" + _sha256(fh.read()).encode())
    return _sha256(b"\n".join(parts))


def input_hash(gen_path: str, fingerprint: str) -> str:
    """The stamp value: everything that determines a map's render - its own generator source plus
    the shared engine fingerprint. `fingerprint` is passed in so it is computed once per run."""
    with open(gen_path, "rb") as fh:
        gen_h = _sha256(fh.read())
    return _sha256(STAMP_ALGO_VERSION + b"\0" + fingerprint.encode() + b"\0" + gen_h.encode())


def read_stamp(svg_path: str) -> str | None:
    """Return the stamped hash of a Mode B svg, or None if the file is missing or unstamped. Only
    the head is read - the stamp is always right after the opening tag, and these svgs run to tens
    of megabytes."""
    try:
        with open(svg_path, "rb") as fh:
            head = fh.read(1024)
    except FileNotFoundError:
        return None
    m = _STAMP_RE.search(head)
    return m.group(1).decode() if m else None


def stamp_svg(svg_path: str, value: str) -> None:
    """Insert (or replace) the render-cache stamp right after the '<svg ...>' opening tag. The
    stamp is an XML comment - invisible to resvg and every browser - and Mode B svgs are gitignored,
    so stamping never dirties a tracked file. Idempotent: any prior stamp is stripped first."""
    with open(svg_path, "rb") as fh:
        data = fh.read()
    data = _STAMP_RE.sub(b"", data, count=1)
    open_end = data.index(b">", data.index(b"<svg")) + 1
    stamp = b"\n<!-- render-cache: " + value.encode() + b" -->"
    with open(svg_path, "wb") as fh:
        fh.write(data[:open_end] + stamp + data[open_end:])


def is_cacheable(gen_path: str, main_repo: str) -> bool:
    """A generator's svg is cache-managed iff it is gitignored (a derived Mode B render). Mode A
    magistracy svgs are tracked source - never stamped, always regenerated. Read from git so the
    boundary tracks the .gitignore instead of being duplicated here."""
    svg = _predicted_svg(gen_path)
    r = subprocess.run(["git", "-C", main_repo, "check-ignore", "-q", svg], check=False)
    return r.returncode == 0


def _is_fresh(gen_path: str, fingerprint: str) -> bool:
    svg = _predicted_svg(gen_path)
    png = svg[: -len(".svg")] + ".png"
    page = svg[: -len(".svg")] + ".html"  # the interactive page is a derived render like the png (feature 134)
    if not (os.path.exists(svg) and os.path.exists(png) and os.path.exists(page)):
        return False
    return read_stamp(svg) == input_hash(gen_path, fingerprint)


def regen_pool(
    skill_dir: str,
    main_repo: str,
    jobs: int | None = None,
    allow_main: bool = True,
) -> tuple[list[str], list[str], list[str]]:
    """Regenerate the pool's derived renders in place, skipping any Mode B map whose stamp is fresh
    and never touching a FROZEN legacy map.

    Walks BOTH trees (feature 161). The live tree is what actually regenerates; the legacy tree is
    here because the missing-exhibit WARNING below is about frozen maps, and that job followed the
    exhibits when they moved out of `pool/`.

    Returns (skipped, regenerated, frozen) as sorted lists of generator paths. Each generator runs
    from its OWN directory - Mode B gens are cwd-independent, Mode A gens write cwd-relative
    outputs, so the only safe cwd for both is the gen's own. GM_ASSISTANT_ALLOW_MAIN is set for the
    subprocesses (not this process): the generators import the engine, whose main-tree guard must
    stand down for this one sanctioned regen-in-main."""
    fingerprint = engine_fingerprint(skill_dir)
    gens = poolmaps.gens(skill_dir=skill_dir)
    to_run: list[tuple[str, bool]] = []
    skipped: list[str] = []
    frozen: list[str] = []
    for gen in gens:
        if poolmaps.classify(gen) == "legacy":
            # The hand-authored pool is FROZEN (GM 2026-08-16; migration-plan.md "The accepted
            # trade"): a legacy gen must never re-run here, however stale its stamp - the engine
            # drifts freely now, so a rerun would silently replace an exhibit's renders (and
            # rewrite its tracked .json) with output nobody reviewed. Whatever renders exist on
            # disk ARE the exhibit; main() warns loudly if one is missing instead of healing it.
            frozen.append(gen)
            continue
        cacheable = is_cacheable(gen, main_repo)
        if cacheable and _is_fresh(gen, fingerprint):
            skipped.append(gen)
        else:
            to_run.append((gen, cacheable))

    env = dict(os.environ)
    if allow_main:
        env["GM_ASSISTANT_ALLOW_MAIN"] = "1"

    def _run(item: tuple[str, bool]) -> str:
        gen, cacheable = item
        subprocess.run(
            [sys.executable, os.path.basename(gen)],
            cwd=os.path.dirname(gen),
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        if cacheable:
            stamp_svg(_predicted_svg(gen), input_hash(gen, fingerprint))
        return gen

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs or (os.cpu_count() or 4)) as ex:
        ran = sorted(ex.map(_run, to_run))
    return skipped, ran, frozen


def stale_flat_renders(skill_dir: str) -> list[str]:
    """Derived renders left at the PRE-FEATURE-161 flat path, `<tree>/<tier>/<map>.<ext>`.

    WHY THIS REPORTS RATHER THAN DELETES. When every map gained its own folder, a tracked file moved
    with the commit - but a live map's `.svg`/`.png`/`.html` are GITIGNORED, so they were never in
    the commit and simply stayed where they were. Any tree that had rendered a map before the move
    (main, the GM's own checkout, every other session's clone) therefore pulls the new folders and
    keeps the old files sitting beside them - which is the exact flat clutter the reorganization
    existed to remove, reappearing right after it was removed. They are no longer ignored either,
    since the ignore rules moved a level deeper, so they show up as untracked noise in `git status`.

    Deleting files is not render-sync's job - it regenerates, it does not tidy - and a session
    reading its own `git status` is owed the explanation rather than a silent removal. So this names
    them and says they are safe to go.

    Only a file whose map ALSO exists in the new layout counts: a loose render with no map folder is
    something else entirely (a draft, a hand copy) and is left alone and unmentioned.
    """
    out: list[str] = []
    known = {(b.tree, b.tier, b.stem) for b in poolmaps.bundles(skill_dir=skill_dir)}
    for tree, tier, stem in sorted(known):
        for ext in (".svg", ".png", ".html"):
            flat = os.path.join(skill_dir, tree, tier, stem + ext)
            if os.path.isfile(flat):
                out.append(flat)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Regenerate the diagram pool renders, cache-short-circuited.")
    ap.add_argument("--main-repo", default=None, help="git repo whose .gitignore decides Mode A vs B (default: the checkout this file is in)")
    ap.add_argument("--skill-dir", default=SKILL_DIR, help="skill dir holding BOTH pool trees and the engine sources")
    ap.add_argument("--jobs", type=int, default=None, help="parallelism (default: cpu count)")
    ap.add_argument("--no-allow-main", action="store_true", help="do not set GM_ASSISTANT_ALLOW_MAIN for the generators")
    args = ap.parse_args(argv)
    if args.main_repo is None:  # feature 131: no hardcoded /gm-assistant - the checkout this file lives in
        here = os.path.dirname(os.path.abspath(__file__))
        args.main_repo = subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
    skipped, ran, frozen = regen_pool(
        args.skill_dir,
        args.main_repo,
        jobs=args.jobs,
        allow_main=not args.no_allow_main,
    )
    print(f"render-cache: {len(ran)} regenerated, {len(skipped)} cached (fresh), {len(frozen)} frozen (legacy, never re-run)")
    for gen in ran:
        print(f"  regen  {os.path.relpath(gen, args.skill_dir)}")
    for gen in frozen:
        svg = _predicted_svg(gen)
        missing = [p for p in (svg, svg[: -len(".svg")] + ".png") if not os.path.exists(p)]  # frozen exhibits predate the .html and never owe one
        if missing:
            print(
                f"  WARNING: frozen map {os.path.relpath(gen, args.skill_dir)} is MISSING {', '.join(os.path.basename(p) for p in missing)} - "
                f"a frozen exhibit's render cannot be faithfully regenerated once the engine has drifted, so it is NOT healed here; "
                f"the frozen renders are committed (GM 2026-08-16), so restore the file with git checkout rather than re-running the gen"
            )
    for orphan in stale_flat_renders(args.skill_dir):
        print(
            f"  ORPHAN {os.path.relpath(orphan, args.skill_dir)} - a render at the PRE-161 flat path, beside the map's own "
            f"folder. Nothing writes it any more and nothing ignores it; it is safe to delete."
        )
    # The pool index is derived from the same tree the renders live in, so refresh it whenever the
    # renders are refreshed - this is what keeps main's index.html current (GM 2026-08-15).
    index_path = pool_index.write_index(args.skill_dir)
    print(f"render-cache: index refreshed ({os.path.relpath(index_path, args.skill_dir)})")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.pipeline.render_cache")
    raise SystemExit(main())
