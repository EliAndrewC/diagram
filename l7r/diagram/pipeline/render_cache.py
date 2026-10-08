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

Mode A plans (the hand-drawn sheets) are stamped BESIDE the svg, not in it: their svg is tracked
SOURCE (only the png and page are gitignored), so a comment in it would dirty a tracked file. Their
stamp is a gitignored sidecar, `.<stem>.render-cache`, holding the map's input hash with the sheet's
own bytes folded in - for a sheet the svg is the INPUT the gen reads. They were simply always re-run
until 2026-10-02, when four of them cost 17-28 s on every render-sync, and render-sync ran inside the
prompt hook of every session under one lock: three sessions queued past the hook's 60 s and it was
killed. The Mode A/B split is read from git itself (`git check-ignore` on the predicted svg), so it
tracks the .gitignore's source/derived boundary automatically instead of duplicating it here.

A map's PAGE also shows the heading of every research question its classes name (`sources.
research_questions`), so the fingerprint a stamp is taken under covers the questions' headings too
(`record_headings_fingerprint`) - their headings only, so a body edit to the record re-renders nothing.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import os
import re
import subprocess
import sys

from . import pool_index, poolmaps, record_build

SKILL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)  # the skill root; this module lives in l7r/diagram/pipeline/ - FOUR levels up since feature 119, not two

# Bump to force a one-time full refresh after any change to how the stamp is computed: an old
# stamp computed under a different version can never equal a new input_hash, so every map reruns.
STAMP_ALGO_VERSION = b"v2"  # v2 (2026-10-02): the record's headings and the engine's data files joined the fingerprint

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
    for dirpath, dirnames, filenames in os.walk(os.path.join(skill_dir, "l7r")):  # the engine is under l7r/ (feature 329; see gencache.engine_files)
        # PRUNED BY NAME, so a NEW TOP-LEVEL TREE MUST BE ADDED HERE (feature 161). The legacy
        # tree is map sources, not engine sources: if its 18 frozen gens entered this
        # fingerprint, every live map's stamp would go stale at once and any future edit to a
        # frozen exhibit would invalidate the whole live pool - backwards, since the freeze
        # exists so those files cost nothing. Nothing would go red; both outcomes look exactly
        # like a cache working normally. `poolmaps.TREES` is the list, so it cannot drift.
        dirnames[:] = sorted(d for d in dirnames if d not in (*poolmaps.TREES, "wip", "tests", "__pycache__") and not d.startswith(("test_", ".")))
        rel_dir = os.path.relpath(dirpath, skill_dir)
        for name in sorted(filenames):
            # THE PAGE'S ASSETS ARE RENDER-DETERMINING (feature 187, GM 2026-09-05: "I'm looking at
            # [inashiro.html] and still see the dotted lines. Why is the fix not there?"). `page.css` and
            # `page.js` are inlined into every <map>.html at write time, and this walk took `.py` only - so
            # feature 186's stylesheet-only landing left every stamp fresh, render-sync said "cached
            # (fresh)", and the GM opened a page rendered before the change. The gate key learned the same
            # lesson in feature 181. Assets are hashed by their bytes under the same DIRECTORY prunes; the
            # `test_` name filter and this module's self-exclusion apply to `.py` only - neither has an
            # analogue among assets. (The GENERATION cache never had this gap: it traces the `open()` of
            # each asset into the entry's data files and hashes them - spec 187 D3.)
            # EVERY file in interactive/assets/ is an asset (feature 207): the stylesheet and script, and the
            # page's content files (`*.json`) - a glossary edit must regenerate the pages on landing too.
            # THE ENGINE'S DATA FILES TOO (2026-10-02): `buildings/types.json` decides the building kinds a sheet's page
            # writes up (`interactive/compound_kinds`), and nothing hashed it while every sheet re-ran each time anyway.
            # Every `.json`, `.css` and `.js` under `l7r/` - a superset again (the pool index's own files ride along).
            # ...AT ANY DEPTH (feature 319, plan D12): the modals are `assets/modals/<hamlet|sheet>/<kind>.md`, one file each, and
            # a top-level-only test would have left a reworded modal's pages "cached (fresh)" - feature 187's failure again.
            dirs = rel_dir.split(os.sep)
            is_asset = any(dirs[i : i + 2] == ["interactive", "assets"] for i in range(len(dirs) - 1))
            is_asset = is_asset or (rel_dir.split(os.sep)[0] == "l7r" and name.endswith((".json", ".css", ".js")))
            if not is_asset and (not name.endswith(".py") or name.startswith("test_") or name == os.path.basename(__file__)):
                continue
            rel = os.path.normpath(os.path.join(rel_dir, name))
            with open(os.path.join(dirpath, name), "rb") as fh:
                parts.append(rel.encode() + b"\0" + _sha256(fh.read()).encode())
    return _sha256(b"\n".join(parts))


# A question's heading: the first heading tag of its file, comments stripped - what `sources.research_questions` shows.
_HEADING_RE = re.compile(r"<h([1-6])\b[^>]*>.*?</h\1>", re.S)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def record_headings_fingerprint(skill_dir: str = SKILL_DIR) -> str:
    """Hash of every research question's file name and heading (id and text): the part of the record a map's page
    shows. A tree with no record (a test fixture) hashes the empty list."""
    qdir = os.path.join(skill_dir, "research", "questions")
    parts: list[bytes] = []
    for name in sorted(os.listdir(qdir)) if os.path.isdir(qdir) else []:
        if not name.endswith(".html"):
            continue
        with open(os.path.join(qdir, name), "rb") as fh:
            m = _HEADING_RE.search(_COMMENT_RE.sub("", fh.read().decode("utf-8", "replace")))
        parts.append(name.encode() + b"\0" + (m.group(0).encode() if m else b""))
    return _sha256(b"\n".join(parts))


def render_fingerprint(skill_dir: str = SKILL_DIR) -> str:
    """What every map's stamp is taken under: the engine and the record's headings."""
    return _sha256((engine_fingerprint(skill_dir) + record_headings_fingerprint(skill_dir)).encode())


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


def _sidecar(gen_path: str) -> str:
    """A Mode A sheet's stamp file: `.<stem>.render-cache` beside the gen, gitignored."""
    d, base = os.path.split(gen_path[: -len(".gen.py")])
    return os.path.join(d, "." + base + ".render-cache")


def sheet_hash(gen_path: str, fingerprint: str) -> str | None:
    """A Mode A sheet's stamp value: its input hash with the tracked svg's bytes folded in (the svg is what the gen
    reads). None when the svg is not there."""
    try:
        with open(_predicted_svg(gen_path), "rb") as fh:
            svg_h = _sha256(fh.read())
    except FileNotFoundError:
        return None
    return _sha256(input_hash(gen_path, fingerprint).encode() + b"\0" + svg_h.encode())


def _is_fresh_sheet(gen_path: str, fingerprint: str) -> bool:
    base = gen_path[: -len(".gen.py")]
    if not (os.path.exists(base + ".png") and os.path.exists(base + ".html")):
        return False
    try:
        with open(_sidecar(gen_path), encoding="utf-8") as fh:
            stamped = fh.read().strip()
    except FileNotFoundError:
        return False
    return stamped == sheet_hash(gen_path, fingerprint)


#: AT MOST FOUR MAPS REGENERATE AT ONCE (feature 324, GM 2026-10-05). The post-landing render step ran one generator per
#: core (22 here), each a roll and a render that peaks near half a gigabyte; measured over the pool's 11 live maps
#: (specs/324-render-memory/research.md R2): 22 at once peaked at 1,459 MB in 57 s, 4 at once at 1,219 MB in 72 s, its
#: typical (p90) footprint 889 -> 448 MB. It runs detached, so the 15 s is nobody's wait.
RENDER_JOBS = 4


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
    outputs, so the only safe cwd for both is the gen's own. DIAGRAM_ALLOW_MAIN is set for the
    subprocesses (not this process): the generators import the engine, whose main-tree guard must
    stand down for this one sanctioned regen-in-main."""
    fingerprint = render_fingerprint(skill_dir)
    gens = poolmaps.gens(skill_dir=skill_dir)
    to_run: list[tuple[str, bool]] = []
    skipped: list[str] = []
    frozen: list[str] = []
    for gen in gens:
        if poolmaps.classify(gen) == "legacy":
            # The hand-authored pool is FROZEN (GM 2026-08-16; docs/migration-plan.md "The accepted
            # trade"): a legacy gen must never re-run here, however stale its stamp - the engine
            # drifts freely now, so a rerun would silently replace an exhibit's renders (and
            # rewrite its tracked .json) with output nobody reviewed. Whatever renders exist on
            # disk ARE the exhibit; main() warns loudly if one is missing instead of healing it.
            frozen.append(gen)
            continue
        cacheable = is_cacheable(gen, main_repo)
        if _is_fresh(gen, fingerprint) if cacheable else _is_fresh_sheet(gen, fingerprint):
            skipped.append(gen)
        else:
            to_run.append((gen, cacheable))

    env = dict(os.environ)
    if allow_main:
        env["DIAGRAM_ALLOW_MAIN"] = "1"

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
        elif (value := sheet_hash(gen, fingerprint)) is not None:
            with open(_sidecar(gen), "w", encoding="utf-8") as fh:
                fh.write(value + "\n")
        return gen

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs or min(RENDER_JOBS, os.cpu_count() or 4)) as ex:
        ran = sorted(ex.map(_run, to_run))
    return skipped, ran, frozen


PAGE_DIR = os.path.join("dev", "placement-stages")  # the stage-by-stage walk-through, generated and gitignored


def replate_page(skill_dir: str, fingerprint: str, allow_main: bool = True) -> bool:
    """Re-plate the placement walk-through page when the engine moved (feature 227 FR-005, GM 2026-09-12: the page
    "auto updated ... much like the makefile explanation"). The page is written from the stage docstrings and the
    steps they declare, and `engine_fingerprint` hashes every engine source as BYTES, so a docstring edit moves it as
    an engine edit does; the stamp beside the page holds the fingerprint it was plated under, and a matching stamp
    skips the roll. Returns True when the page was re-plated. Runs the tool as a module in a child, as the pool's
    generators run, under the same main-tree allowance."""
    page_dir = os.path.join(skill_dir, PAGE_DIR)
    stamp = os.path.join(page_dir, ".stamp")
    if os.path.isfile(stamp) and os.path.isfile(os.path.join(page_dir, "hamlet-placement.html")):
        with open(stamp, encoding="utf-8") as fh:
            if fh.read().strip() == fingerprint:
                return False
    env = dict(os.environ)
    if allow_main:
        env["DIAGRAM_ALLOW_MAIN"] = "1"
    subprocess.run([sys.executable, "-m", "l7r.diagram.tools.placement_stages", "--out", page_dir], cwd=skill_dir, env=env, check=True, stdout=subprocess.DEVNULL)
    os.makedirs(page_dir, exist_ok=True)
    with open(stamp, "w", encoding="utf-8") as fh:
        fh.write(fingerprint + "\n")
    with open(os.path.join(page_dir, ".classes"), "w", encoding="utf-8") as fh:
        fh.write(classes_fingerprint() + "\n")
    return True


def classes_fingerprint() -> str:
    """A hash of the class names a reader can click - what `test_every_clickable_class_is_named_somewhere_on_the_committed_page`
    reads the page against (feature 278)."""
    import hashlib

    from l7r.diagram.interactive.classes import CLASSES

    return hashlib.sha256("\n".join(sorted(CLASSES)).encode()).hexdigest()


def replate_if_classes_moved(skill_dir: str, allow_main: bool = False) -> bool:
    """Re-plate the placement page when the class registry has changed since it was plated (feature 278, FR-013).

    The page is gitignored and re-plated at landing, on main; a clone that merged a new class kept the page it had, and
    the test that reads it went red in that clone until someone re-plated by hand - a red only a landing cleared. The
    sync-in that brings the class runs this: the page's `.classes` stamp holds the registry it was plated from, and a
    mismatch - or a page plated before the stamp existed - re-plates it. A clone with no page yet is left alone (the test
    skips it). The engine-fingerprint re-plate is `replate_page`'s, which render-sync runs on main."""
    page_dir = os.path.join(skill_dir, PAGE_DIR)
    if not os.path.isfile(os.path.join(page_dir, "hamlet-placement.html")):
        return False
    stamp = os.path.join(page_dir, ".classes")
    if os.path.isfile(stamp):
        with open(stamp, encoding="utf-8") as fh:
            if fh.read().strip() == classes_fingerprint():
                return False
    return replate_page(skill_dir, engine_fingerprint(skill_dir), allow_main=allow_main)


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
    ap.add_argument("--jobs", type=int, default=None, help="parallelism (default: RENDER_JOBS, at most the cpu count)")
    ap.add_argument("--no-allow-main", action="store_true", help="do not set DIAGRAM_ALLOW_MAIN for the generators")
    ap.add_argument("--page-if-classes", action="store_true", help="only re-plate the placement page if the class registry moved (sync-in; feature 278)")
    args = ap.parse_args(argv)
    if args.page_if_classes:
        replated = replate_if_classes_moved(args.skill_dir, allow_main=not args.no_allow_main)
        print(f"render-cache: placement page {'re-plated (the class registry moved)' if replated else 'current'} ({PAGE_DIR}/hamlet-placement.html)")
        return 0
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
                f"a frozen exhibit's renders are NOT in git - they were removed and archived (.gitignore note 1), so restore from /host-l7r-repo/diagram-render-archive/ (MANIFEST.json carries a sha256 per file) rather than re-running the gen or reaching for git checkout"
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
    if os.path.isfile(os.path.join(args.skill_dir, "l7r", "diagram", "tools", "placement_stages.py")):  # a tree with the page tool (a test fixture has none)
        replated = replate_page(args.skill_dir, engine_fingerprint(args.skill_dir), allow_main=not args.no_allow_main)
        print(f"render-cache: placement page {'re-plated' if replated else 'fresh'} ({PAGE_DIR}/hamlet-placement.html)")
    # THE RECORD'S SITE (feature 301, spec FR-010): built here on the main checkout, never committed, and only when a
    # fragment, an asset or the build's own code moved - the map renders' model, with its own stamp.
    if os.path.isfile(os.path.join(args.skill_dir, "research", "sources", "_front.html")):  # a tree with a record (a test fixture has none)
        built = record_build.rebuild_if_stale(args.skill_dir)
        print(f"render-cache: the record's site {'rebuilt' if built else 'fresh'} (research/site/index.html)")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.pipeline.render_cache")
    raise SystemExit(main())
