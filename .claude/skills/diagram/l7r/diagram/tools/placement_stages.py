#!/usr/bin/env python3
"""Render a scripted hamlet ONE STAGE AT A TIME and write an HTML walk-through.

    python3 -m l7r.diagram.tools.placement_stages                 # Inashiro, into dev/placement-stages/
    python3 -m l7r.diagram.tools.placement_stages --width 1400    # bigger plates

WHY THIS EXISTS (GM, 2026-08-20): *"a lot of the bugs that we've been working through feel like they
might have to do with the placement order of things on the map ... I would actually be very curious
to see what the Inashiro map looks like when it is only the water, and then when we have added only
the rice paddy fields, and then at whatever later stage, we have added the houses."*

It is the COMPANION to `dev/placement.md`, not a duplicate of it, and the split is deliberate. That
document is the rulebook a session loads before changing where something is placed - the registries,
the CENTER-vs-FOOTPRINT trap, the reserve/fill rule. This is the picture: what the map actually looks
like after each stage, so the sequence can be SEEN rather than reconstructed from eighteen function
names. A reader who has looked at the plates knows immediately why the web cannot run before the
houses, because the plate before it is visibly empty of the things it has to thread between.

UNDER THE 100% RULE (GM 2026-09-02). Re-run it whenever `STAGES` or a docstring changes - the landing does
(feature 227, `render_cache`); the page is generated, never hand-edited.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import copy
import functools
import importlib
import inspect
import io
import os
import re
import subprocess
import sys
from contextlib import redirect_stdout
from html import escape
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if SKILL not in sys.path:
    sys.path.insert(0, SKILL)

from l7r.diagram.hamletgen import HamletSpec, SitePlan, plan_site  # noqa: E402
from l7r.diagram.hamletgen.driver import STAGES, roll_scope  # noqa: E402
from l7r.diagram.settlement import Settlement  # noqa: E402

# THE PAGE IS WRITTEN FROM THE CODE'S OWN DOCUMENTATION (feature 227, GM 2026-09-12: *"I would like it if this HTML
# page basically was generated based on the documentation, the docstrings, the stages, and such so that I could just
# know that it was always up to date"*). Each stage's DOCSTRING is its explanation - the first paragraph its purpose,
# the rest the algorithm and its order - and a stage declares its STEPS, the functions that are its algorithm in
# the order it calls them, in a `Steps:` section of that docstring, one dotted name per line. The generator imports
# each step and renders its docstring under the stage. The notes file this replaced (`placement_stages_notes.json`,
# feature 207) is retired: its prose moved into the stage docstrings it described, so the one place a stage is
# explained is the stage. A stage or a step without a docstring, a stage with no `Steps:` section, or a name that
# does not resolve FAILS `tests/tools/test_placement_stages.py` at the gate - the page cannot go quietly stale.


def stage_doc(stage: Any) -> tuple[str, list[str], list[str]]:
    """A stage's docstring as the page reads it: `(title, paragraphs, steps)`.

    The title is the docstring's first paragraph; the paragraphs are the rest up to the `Steps:` line; the steps
    are the dotted names listed under it, one per line, in order. A stage with no docstring gets a title that says
    so and no steps - visibly, never silently (the roster test fails the gate on it)."""
    doc = inspect.getdoc(stage) or ""
    if not doc.strip():
        return ("(no docstring - this stage explains nothing)", ["This stage has no docstring. Write one, with a `Steps:` section naming the functions that are its algorithm."], [])
    head, _sep, tail = doc.partition("\nSteps:")
    paras = [" ".join(line.strip() for line in para.split("\n")) for para in head.strip().split("\n\n")]
    steps = [line.strip() for line in tail.split("\n") if line.strip()] if _sep else []
    return (paras[0].rstrip("."), paras[1:], steps)


def resolve_step(path: str) -> Any:
    """The object a `Steps:` name points at: the longest importable prefix is the module, the rest an attribute
    chain (`l7r.diagram.settlement.Settlement.try_place` is the module, the class and the method)."""
    parts = path.split(".")
    for cut in range(len(parts), 0, -1):
        try:
            obj: Any = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue
        for attr in parts[cut:]:
            obj = getattr(obj, attr)
        return obj
    raise ImportError(path)


def step_doc(path: str) -> tuple[str, list[str]]:
    """A step as the page shows it: its short name and its docstring's paragraphs."""
    obj = resolve_step(path)
    doc = inspect.getdoc(obj) or ""
    paras = [" ".join(line.strip() for line in para.split("\n")) for para in doc.strip().split("\n\n")] if doc.strip() else ["(no docstring)"]
    return (path.rsplit(".", 1)[-1], paras)


# THE PLATE AFTER EVERY STEP, not only after every stage (feature 227, GM 2026-09-12: *"how much work would it
# be to show a new image for literally every stage at which it would be possible to render an image that has actual
# content? ... The very first image that we see has a stream, an irrigated ditch, dry cropfields, earthen bunds, field
# ponds, wet paddies, and a drainage ditch. That's an awful lot. And the algorithm walks us through the step by step
# seven part algorithm. So To what extent could we show what the map looks like after each of those parts?"*).
#
# HOW, AND WHAT IT COSTS TO BE HONEST ABOUT IT. A step is a function the stage calls, often many times, and there is no
# moment the walk can reach between two of them from outside. So each step is WRAPPED for the duration of its stage and
# records a WATERMARK - the length of every append-only record list on the settlement and in its manifest - after each
# call, keeping the last. The plates are then made after the stage, from one copy per plate wound back to that
# watermark: the records a step had not yet appended are deleted, and what is left is the map as it stood when that
# step finished. Drawing here is append-only, which is what makes the rewind exact.
#
# TWO PLACES IT IS AN APPROXIMATION, stated rather than discovered later. A record REWRITTEN in place after its step
# (`reink_lane`, which shortens a lane and redraws its ink) shows its later geometry on the earlier plate; and a
# DEFERRED group - the blade and scatter buckets a ground-cover stage fills and `finish` flushes - is flushed in full,
# so a step plate inside `stage_hinterland` or `stage_windbreak` can carry cover its step had not drawn yet. Both are
# confined to the stage in hand, and neither can show a feature from a LATER stage, which is the property the page is
# read for.
_RECORD_ATTRS = (
    "out",
    "out_cls",
    "top",
    "top_cls",
    "walls",
    "walls_cls",
    "toplabels",
    "toplabels_cls",
    "ground",
    # ...AND THE DEFERRED STORES, because each entry holds the INDEX of the slot it reserved in `out` and `finish`
    # writes through it: a rewind that truncated `out` and kept the groups appended after it crashed on the first
    # step plate of the hinterland (`IndexError` in `flush_blade_groups`). Truncating them by the same watermark is
    # exactly right - a group reserved BEFORE the step still points inside the rewound list.
    "_blade_groups",
    "_mark_groups",
    "_pending_stands",
    "_pending_yards",
    "_pending_farmsteads",
    "_captions",
    "_label_queue",
    "_lane_ink",
    "_scatter_frames",
)


def _watermark(s: Settlement) -> dict[tuple[str, str], int]:
    """Where every append-only record list stands right now - the four ink layers with their class side-lists, the
    deferred ground, and every list in the manifest. The side-lists are in here because they are PARALLEL to their
    layer: winding `out` back without `out_cls` hands the page writer a class list that no longer lines up."""
    marks: dict[tuple[str, str], int] = {("attr", n): len(getattr(s, n)) for n in _RECORD_ATTRS if isinstance(getattr(s, n, None), list)}
    marks.update({("M", k): len(v) for k, v in s.M.items() if isinstance(v, list)})
    return marks


def _rewind(snap: Settlement, marks: dict[tuple[str, str], int]) -> None:
    """Wind a COPY back to a watermark, in place: everything appended after it is deleted."""
    for (kind, name), n in marks.items():
        lst = getattr(snap, name, None) if kind == "attr" else snap.M.get(name)
        if isinstance(lst, list) and len(lst) > n:
            del lst[n:]


_OPEN_G = re.compile(r"<g\b[^>]*(?<!/)>")


def _balance_groups(snap: Settlement) -> None:
    """Close any SVG group the rewind cut OPEN, so the plate is a document resvg will read.

    A stage opens a `<g>` in one record and closes it in another - the deferred scatter buckets and the
    feature groups both do - so a watermark that falls between the two leaves the prefix unbalanced, and
    resvg refuses the file outright (measured on the beads step of the field stage, which is drawn inside
    the paddies' group). Closing the open groups is exact for a well-formed prefix. The class side-list
    gets the same number of entries, tagged as ruled-but-not-highlighted, because it is PARALLEL to the
    layer and the page writer reads them in step."""
    for layer, tags in (("out", "out_cls"), ("top", "top_cls"), ("walls", "walls_cls"), ("toplabels", "toplabels_cls")):
        records = getattr(snap, layer, None)
        if not isinstance(records, list):
            continue
        depth = sum(len(_OPEN_G.findall(r)) - r.count("</g>") for r in records if isinstance(r, str))
        if depth > 0:
            records.extend(["</g>"] * depth)
            side = getattr(snap, tags, None)
            if isinstance(side, list):
                side.extend(["-"] * depth)


def _bind_points(path: str) -> tuple[list[tuple[Any, str]], Any]:
    """Everywhere a step's name is BOUND, and the object it is bound to.

    Its defining owner - a module, or a class for a method - and every other engine module that imported it by name,
    because `from .seats import front_row` binds a second reference and patching only the first would watch a
    function nobody calls. Swept over `l7r.diagram` alone: a name bound outside the engine is not a step."""
    parts = path.split(".")
    leaf = parts[-1]
    owner = resolve_step(".".join(parts[:-1]))
    target = getattr(owner, leaf)
    points = [(owner, leaf)]
    points += [(mod, leaf) for name, mod in list(sys.modules.items()) if name.startswith("l7r.diagram") and mod is not owner and getattr(mod, leaf, None) is target]
    return points, target


@contextlib.contextmanager
def _watch_steps(s: Settlement, steps: list[str]) -> Any:
    """Wrap each of a stage's steps for the duration of the stage; yields `name -> watermark after its last call`.

    A step that cannot be resolved or bound is skipped here and reported by the page as having no plate - the roster
    test is what fails the gate on a name that does not resolve, so this does not need to raise as well."""
    marks: dict[str, dict[tuple[str, str], int]] = {}
    restore: list[tuple[Any, str, Any]] = []
    for path in steps:
        try:
            points, target = _bind_points(path)
        except AttributeError, ImportError:  # pragma: no cover - the roster test fails the gate on such a name
            continue

        def wrapper(*a: Any, _path: str = path, _target: Any = target, **k: Any) -> Any:
            out = _target(*a, **k)
            marks[_path] = _watermark(s)
            return out

        functools.update_wrapper(wrapper, target)
        for obj, leaf in points:
            restore.append((obj, leaf, getattr(obj, leaf)))
            setattr(obj, leaf, wrapper)
    try:
        yield marks
    finally:
        for obj, leaf, original in reversed(restore):
            setattr(obj, leaf, original)


_TAGGED = (("out", "out_cls"), ("top", "top_cls"), ("walls", "walls_cls"), ("toplabels", "toplabels_cls"))


def features_between(s: Settlement, lo: dict[tuple[str, str], int], hi: dict[tuple[str, str], int]) -> list[str]:
    """The FEATURE CLASSES whose ink appeared between two watermarks, in the page's own vocabulary.

    THE PAGE MUST NAME EVERYTHING A READER CAN CLICK (GM 2026-09-12): *"anything that I can click on after
    having it highlighted when I move my mouse over it on the HTML version of the map should be mentioned on
    the page ... Otherwise, how can I hit control f and then find out where the privies are being laid out?"*
    Measured when they asked: 29 of the 51 hoverable classes appeared nowhere on the page - privy, woodpile,
    manure heap, persimmon, storage shed, wet paddy, the dike kinds, every crop but one - because the page's
    words all came from stage and step docstrings and a docstring does not enumerate what its code happens to
    draw.

    So this is DERIVED FROM THE INK rather than written down: the class side-lists run parallel to the ink
    layers, `ink_census` already turns a slice of them into counts per class, and the difference between two
    watermarks is exactly what one stage or one step drew. A feature cannot be renamed, added or moved between
    stages without this following it, and nothing has to be remembered."""
    from l7r.diagram.interactive.page import ink_census

    found: dict[str, int] = {}
    for layer, tags in _TAGGED:
        records, side = getattr(s, layer, None), getattr(s, tags, None)
        if not isinstance(records, list) or not isinstance(side, list):
            continue
        a, b = lo.get(("attr", layer), 0), hi.get(("attr", layer), len(records))
        n = min(b, len(records), len(side))
        if n <= a:
            continue
        counts, _unclassed = ink_census(records[a:n], side[a:n])
        for key, c in counts.items():
            if key and key != "-":  # `"-"` is ink ruled NOT highlighted, so a reader cannot click it
                found[key] = found.get(key, 0) + c
    return sorted(found)


def elsewhere_in_the_pool(named: set[str], skill: str) -> list[tuple[str, str]]:
    """Every hoverable class this page has NOT named, paired with a shipped map that does draw it.

    The stage lists are derived from ONE map's ink, so they can only name what that map has - and the pool
    deliberately draws five different kinds of place, so fourteen classes were left unnamed by Inashiro's
    roll: the dike kinds and their ponds belong to the polder, the grave island to Kashikawa, and a few are
    features a given roll did not happen to place. The GM's rule is about what a READER can click
    (2026-09-12): *"anything that I can click on after having it highlighted when I move my mouse over it on
    the HTML version of the map should be mentioned on the page ... Otherwise, how can I hit control f and
    then find out where the privies are being laid out?"* So a class no Inashiro roll draws is still named,
    beside a map that has it, and a search finds it.

    DERIVED, never listed: a class is present on a map when its key appears in that map's own interactive
    page, which is the page that explains only the classes actually on it. Four classes are drawn by no
    shipped map at all (alternate dike crops the polder's roll did not pick, and the field rock); they are
    named as such rather than omitted, because a reader can still meet them in the vocabulary."""
    import glob

    where: dict[str, str] = {}
    for page in sorted(glob.glob(os.path.join(skill, "pool", "hamlets", "*", "*.html"))):
        try:
            with open(page, encoding="utf-8") as fh:
                body = fh.read()
        except OSError:  # pragma: no cover - a page that cannot be read names nothing
            continue
        stem = os.path.basename(page)[: -len(".html")]
        for key in _hoverable():
            if key not in named and f'"{key}"' in body:
                where.setdefault(key, stem)
    return sorted((k, where.get(k, "")) for k in _hoverable() if k not in named)


def _hoverable() -> list[str]:
    """Every class a reader can hover and click on a map page - the interactive vocabulary's own roster."""
    from l7r.diagram.interactive.classes import CLASSES

    return sorted(CLASSES)


def _ink_total(marks: dict[tuple[str, str], int]) -> int:
    """The ink a watermark stands at - the same five layers `_ink` counts, read off the watermark."""
    return sum(n for (kind, name), n in marks.items() if kind == "attr" and name in ("out", "top", "walls", "toplabels", "ground"))


def _ink(s: Settlement) -> int:
    """How many SVG records the settlement has emitted so far, across the four ink layers and the deferred ground.

    This is the test for "did that stage DRAW anything", and it is deliberately a count of records
    rather than a look at the rendered pixels: a stage can legitimately emit ink that happens to be
    invisible at plate scale, and that is not the case being detected here."""
    # ...and the DEFERRED ground features - the lanes, streets and roads a way stage lays - live in `ground` until the
    # finish inks them (feature 227: the web stage, which draws nothing else, read as "no ink" and got a card, not a plate)
    return sum(len(getattr(s, name, [])) for name in ("out", "top", "walls", "toplabels", "ground"))


def _decisions(s: Settlement) -> dict[str, object]:
    """The map's metadata as it stands - what a no-ink stage has to show for itself."""
    return dict(s.M["meta"])


def _plate(snap: Settlement, out_dir: str, stem: str, width: int, overlay: dict[str, Any] | None = None, render_w: int = 2600) -> tuple[str, int, int]:
    """Finish a COPY of the part-built settlement and scale its render down to a page plate.

    `overlay` (feature 227): the site boundary the homesteads were seated against - its chords, outline rings and
    corridor segments from the manifest's `site_boundary` - drawn over the plate in three colors, mapped through the
    finished copy's `meta.view`, because that boundary is the thing the GM asked about and no plate showed it."""
    from PIL import Image, ImageDraw

    base = os.path.join(out_dir, stem)
    # THE PLATE IS THE PNG, SO ONLY THE PNG IS RENDERED (feature 208, GM 2026-09-07: "a whole lot of rasterizing
    # that is completely pointless"). `finish(render=True)` also made the interactive page's raster picture -
    # resvg at 3 px per map px, PIL, the picture's encoder - for each of the eighteen stage pages, and nothing reads those
    # pages: the walk-through links the plates. So the page is written vector-only (`render=False`) and the PNG
    # is rendered by the same call `finish` would have made. The gate's sampler caught this process at 1.6 GB.
    with redirect_stdout(io.StringIO()):
        snap.finish(base, render=False)
    env_w = os.environ.get("DIAGRAM_PNG_WIDTH")
    snap.render_png(base, int(env_w) if env_w else render_w)
    png = base + ".png"
    with Image.open(png) as im:
        w, h = im.size
        if overlay:
            im = im.convert("RGB")
            x0, y0, vw, _vh = snap.M["meta"].get("view") or (0.0, 0.0, float(snap.W), float(snap.H))  # a mid-roll copy is uncropped: the plate is the whole canvas
            sc = w / float(vw)
            draw = ImageDraw.Draw(im)
            for ring in overlay.get("rings", []) + overlay.get("holes", []):
                pts = [((x - x0) * sc, (y - y0) * sc) for x, y in ring]
                draw.line([*pts, pts[0]], fill=(200, 30, 30), width=max(2, round(sc * 3)))
            for a, b, *_rest in overlay.get("chords", []):
                draw.line([((a[0] - x0) * sc, (a[1] - y0) * sc), ((b[0] - x0) * sc, (b[1] - y0) * sc)], fill=(30, 60, 220), width=max(2, round(sc * 4)))
            for a, b, *_rest in overlay.get("water", []) + overlay.get("corridors", []):
                draw.line([((a[0] - x0) * sc, (a[1] - y0) * sc), ((b[0] - x0) * sc, (b[1] - y0) * sc)], fill=(20, 150, 150), width=max(2, round(sc * 3)))
        if w > width:
            im = im.resize((width, max(1, round(h * width / w))), Image.LANCZOS)
        # PALETTISED, because these are flat-color maps and this page is COMMITTED. At full render
        # size the plates came to 96 MB (thirteen of them then, eighteen now), which is not a documentation asset, it is a liability -
        # and the whole point is that the page lives in the repo and is re-run when `STAGES` changes.
        # An adaptive 128-color palette is visually indistinguishable on flat fills and hard strokes
        # while cutting each plate by roughly an order of magnitude.
        im = im.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        im.save(png, optimize=True)
        size = im.size
    # The SVG was only ever a means to the plate; keeping it doubles the directory for nothing.
    if os.path.isfile(base + ".svg"):
        os.remove(base + ".svg")
    if os.path.isfile(base + ".json"):
        os.remove(base + ".json")
    if os.path.isfile(base + ".html"):
        os.remove(base + ".html")  # the interactive page of a half-built map: 700 KB apiece that nothing links (feature 227)
    return os.path.basename(png), size[0], size[1]


def build_page(out_dir: str, width: int, spec: HamletSpec, steps_too: bool = True) -> str:
    """Roll `spec` one stage at a time, writing a plate per stage and an index page. Returns the path."""
    os.makedirs(out_dir, exist_ok=True)
    plan = plan_site(spec)
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    rows: list[dict[str, Any]] = []
    # THE BASELINE IS TAKEN BEFORE STAGE 1, not from an empty dict: `Settlement.__init__` already
    # puts the canvas W/H into `meta`, and starting empty made stage 1's card claim credit for two
    # values the constructor set. A no-ink card must show what THAT stage decided and nothing else.
    known: dict[str, object] = _decisions(s)
    _walk(s, plan, out_dir, width, rows, known, steps_too)
    return _write_page(out_dir, rows, spec)


def _walk(s: Settlement, plan: SitePlan, out_dir: str, width: int, rows: list[dict[str, Any]], known: dict[str, object], steps_too: bool = True) -> None:
    """The stage loop of `build_page`, lifted out so the roll scope wraps exactly the loop (feature 210)."""
    # THE WALK-THROUGH IS A ROLL (feature 210): the whole stage loop sits in one `roll_scope`, so the memo
    # is cleared and the heap trimmed when the page is built, as after any roll. Not per stage: the memo
    # serves across stages within a roll, and a plate is a copy finished mid-roll.
    with roll_scope(plan.spec):
        for i, stage in enumerate(STAGES, 1):
            before = _ink(s)
            had_boundary = "site_boundary" in s.M
            title, paras, step_names = stage_doc(stage)
            start = _watermark(s)
            # THE STEPS ARE WATCHED WHILE THE STAGE RUNS, and only while it runs: the patches are undone on the way
            # out, so nothing the next stage calls is wrapped and no map is ever rolled through a patched engine.
            with redirect_stdout(io.StringIO()), _watch_steps(s, step_names) as step_marks:
                stage(s, plan)
            drew = _ink(s) - before
            stem = f"{i:02d}-{stage.__name__}"
            now = _decisions(s)
            # A STAGE THAT LAYS NO INK GETS A CARD, NOT A PLATE (GM, 2026-08-23: *"the water skeleton,
            # which is the first picture, appears to be blank"*). `stage_water_frame` emits zero SVG
            # records - it settles the drainage bearing and the land's fall and writes them to `meta` -
            # so its plate was a plain cream square, which is indistinguishable from a broken render and
            # was reasonably read as one. The honest page shows what such a stage DECIDED instead. This
            # is generic rather than a special case for stage 1: any future metadata-only stage gets the
            # same treatment automatically, and a stage that stops drawing announces itself here rather
            # than turning quietly blank.
            row: dict[str, Any] = {
                "i": i,
                "fn": stage.__name__,
                "title": title,
                "paras": paras,
                "steps": [],
                "img": None,
                "iw": 0,
                "ih": 0,
                "decided": [],
                "features": features_between(s, start, _watermark(s)),
            }
            rows.append(row)
            # A COPY IS FINISHED, NOT THE LIVE SETTLEMENT: `finish` flushes deferred canopies, seats captions and
            # crops, all of which mutate. Snapshotting the real one would change the map the next stage sees, and the
            # page would document a build nobody runs. The copy is taken INSIDE the worker (feature 227), because
            # holding one per plate until the end of the walk is how this process reached 1.6 GB with fourteen plates
            # and would have been sixty: at most `max_workers` copies are alive at once now.
            jobs: list[tuple[Any, dict[tuple[str, str], int] | None, str, dict[str, Any] | None, int]] = []
            if drew:
                overlay = dict(s.M["site_boundary"]) if not had_boundary and "site_boundary" in s.M else None
                jobs.append((row, None, stem, overlay, 2600))
            else:
                row["decided"] = [(k, str(v)) for k, v in now.items() if known.get(k) != v]
                stale = os.path.join(out_dir, stem + ".png")
                if os.path.isfile(stale):
                    os.remove(stale)  # a stage that used to draw and no longer does leaves no orphan plate
            # ...AND A PLATE AFTER EVERY STEP THAT ADDED INK (the GM's refinement). In the docstring's order, skipping
            # a step that was never called and one whose ink total has not moved past the last plate - a scan, a
            # predicate or a pre-test has nothing to show, and the page says so in words instead.
            # WHICH STEPS GET A PLATE IS DECIDED IN THE ORDER THE INK LANDED, not in the order the steps are
            # declared. A step that CONTAINS others finishes after them - `draw_comb_field` returns once the hem,
            # the paddies, the beads, the source and the ditches are all drawn - so walking the declared order
            # plated the parent and then skipped all five of its parts as "no new ink", which is the opposite of
            # the progression the GM asked to see. Sorted by where each step's ink ended, the parts plate in turn
            # and the parent, which adds nothing after its last part, does not.
            at = _ink_total(start)
            plate_at: dict[str, dict[tuple[str, str], int]] = {}
            _from: dict[str, dict[tuple[str, str], int]] = {}
            _prev = start
            for path, mark in sorted(((p, m) for p, m in step_marks.items() if p in step_names), key=lambda kv: _ink_total(kv[1])):
                if _ink_total(mark) > at:
                    at, plate_at[path], _from[path] = _ink_total(mark), mark, _prev
                    _prev = mark
            for k, path in enumerate(step_names, 1):
                name, sparas = step_doc(path)
                entry: dict[str, Any] = {"name": name, "path": path, "paras": sparas, "img": None, "iw": 0, "ih": 0, "unrenderable": False, "features": []}
                row["steps"].append(entry)
                if path in plate_at:
                    entry["features"] = features_between(s, _from[path], plate_at[path])
                if steps_too and path in plate_at:
                    jobs.append((entry, plate_at.pop(path), f"{i:02d}-{k:02d}-{name.strip('_')}", None, 1500))
            _make_plates(s, jobs, out_dir, width)
            known = now
    for row in rows:
        shown = sum(1 for e in row["steps"] if e["img"])
        print(f"  {row['i']:>2}. {row['fn']:<22} -> {row['img'] or f'(no ink - {len(row['decided'])} values decided)'}" + (f"  + {shown} step plate(s)" if shown else ""))


def _make_plates(s: Settlement, jobs: list[Any], out_dir: str, width: int) -> None:
    """Render one stage's plates - its own and its steps' - and hang each result on the row that asked for it.

    The copy and the rewind happen in the worker, so the peak is `max_workers` settlements rather than all of them.
    A step plate is rendered at a smaller size than a stage plate: it answers "what appeared", not "read the map"."""
    if not jobs:
        return

    def one(job: Any) -> tuple[Any, tuple[str, int, int]]:
        target, mark, stem, overlay, render_w = job
        snap = copy.deepcopy(s)
        if mark is not None:
            _rewind(snap, mark)
            _balance_groups(snap)
        return target, _plate(snap, out_dir, stem, width if render_w > 2000 else max(520, width // 2), overlay, render_w)

    # A STEP PLATE THAT WILL NOT RENDER IS REPORTED AND DROPPED; A STAGE PLATE IS NOT. The rewind is exact for a
    # well-formed prefix and `_balance_groups` closes the one way it is not, but it reconstructs a moment inside a
    # stage rather than a moment the engine ever finished at, so a future stage could hand it something resvg
    # refuses - and the page, which is documentation, should then lose one picture and say so rather than fail. A
    # STAGE plate is a moment the engine really passes through: if that will not render, something is broken and
    # the run must stop.
    def guarded(job: Any) -> tuple[Any, tuple[str, int, int] | None]:
        try:
            return one(job)
        except (subprocess.CalledProcessError, ValueError, IndexError, KeyError) as exc:
            if job[1] is None:
                raise
            print(f"  NO PLATE for step {job[2]} - the part-built map would not render ({type(exc).__name__})")
            job[0]["unrenderable"] = True
            return job[0], None

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(jobs))) as ex:
        for target, made in ex.map(guarded, jobs):
            if made is not None:
                img, iw, ih = made
                target.update(img=img, iw=iw, ih=ih)


def _write_page(out_dir: str, rows: list[dict[str, Any]], spec: HamletSpec) -> str:
    """The tail of `build_page`: prune the orphan plates, write the index page, return its path."""
    # PRUNE EVERY PLATE THIS RUN DID NOT WRITE. The per-stage removal above only catches a stage that
    # kept its index and stopped drawing; it cannot see a RENAME or a RENUMBER, which is what actually
    # happens when `STAGES` is reordered. Feature 128 split `stage_ways` into `stage_seat` and
    # `stage_track` and moved the houses ahead of both, and every plate from 06 down shifted by one -
    # leaving seven orphans in a COMMITTED directory, `04-stage_ways.png` among them. An orphan here is
    # worse than clutter: the page is how the GM reads the build order, and a leftover plate showing
    # lanes before houses is a picture of the very thing the feature removed.
    # ...AND THE STEP PLATES THIS RUN WROTE (feature 227): the sweep keeps what the page REFERENCES, so a set
    # built from the stage rows alone deleted every per-step plate the moment after it was rendered.
    keep = {r["img"] for r in rows if r["img"]} | {e["img"] for r in rows for e in r["steps"] if e["img"]} | {"hamlet-placement.html"}
    for name in sorted(os.listdir(out_dir)):
        if name not in keep and name.endswith(".png"):
            os.remove(os.path.join(out_dir, name))
            print(f"  pruned stale plate {name}")
    parts = [
        "<title>Hamlet placement order</title>",
        "<style>",
        ":root{--ink:#241c14;--dim:#6b5d4d;--rule:#d9cdbb;--bg:#fbf7f0;--card:#fff;--step:#f4ede1}",
        ':root:not([data-theme="light"]){}',
        "@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){--ink:#ece3d6;--dim:#a2957f;--rule:#3b332a;--bg:#171310;--card:#201a15;--step:#2a231c}}",
        ':root[data-theme="dark"]{--ink:#ece3d6;--dim:#a2957f;--rule:#3b332a;--bg:#171310;--card:#201a15;--step:#2a231c}',
        "body{margin:0;padding:2.5rem 1.25rem 4rem;background:var(--bg);color:var(--ink);",
        "font:16px/1.6 Georgia,'Times New Roman',serif}",
        ".wrap{max-width:1180px;margin:0 auto}",
        "h1{font-size:1.9rem;margin:0 0 .3rem}",
        ".lede{color:var(--dim);margin:0 0 2rem}",
        ".stage{background:var(--card);border:1px solid var(--rule);border-radius:6px;",
        "padding:1.1rem 1.25rem 1.4rem;margin:0 0 1.6rem}",
        ".hd{display:flex;gap:.7rem;align-items:baseline;flex-wrap:wrap;margin-bottom:.35rem}",
        ".n{font:700 .95rem/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim)}",
        ".t{font-size:1.15rem;font-weight:700}",
        ".fn{font:.85rem/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim)}",
        ".why{color:var(--ink);margin:.2rem 0 .9rem}",
        ".steps{margin:.6rem 0 1rem;border-left:3px solid var(--rule);padding-left:1rem}",
        ".steps summary{cursor:pointer;font:700 .8rem/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--dim)}",
        ".step{background:var(--step);border-radius:4px;padding:.6rem .9rem;margin:.6rem 0}",
        ".step .sn{font:700 .95rem/1.3 ui-monospace,SFMono-Regular,Menlo,monospace}",
        ".step .sp{font:.85rem/1.3 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim);margin-left:.5rem}",
        ".step p{margin:.35rem 0 0;font-size:.95rem}",
        ".step img{margin:.7rem 0 .2rem}",
        ".after{font:.8rem/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim)}",
        ".feats{margin:.5rem 0 .2rem;font-size:.92rem}",
        ".fl{font:700 .72rem/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);display:block}",
        "img{display:block;width:100%;height:auto;border:1px solid var(--rule);border-radius:3px;background:#fff}",
        ".noink{border:1px dashed var(--rule);border-radius:3px;padding:1rem 1.15rem;background:transparent}",
        ".noink .cap{font:700 .8rem/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.06em;",
        "text-transform:uppercase;color:var(--dim);margin-bottom:.7rem}",
        ".kv{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.3rem 1.5rem;margin:0}",
        ".kv div{display:flex;gap:.6rem;justify-content:space-between;border-bottom:1px dotted var(--rule);",
        "padding:.15rem 0;font:.87rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}",
        ".kv .k{color:var(--dim)}.kv .v{color:var(--ink);font-weight:700;text-align:right}",
        ".legend{font-size:.85rem;color:var(--dim);margin:.4rem 0 0}",
        "</style>",
        '<div class="wrap">',
        "<h1>Hamlet placement order</h1>",
        f'<p class="lede">{escape(spec.name)}, rolled one stage at a time. Each plate is the map as it stands '
        f"after that stage and nothing later - the same build (the driver's first roll), snapshotted {len(STAGES)} times. "
        "Every word on this page is read from the code: a stage's explanation is its docstring, and the steps under it "
        "are the functions the docstring names as its algorithm, each shown in its own words, with its OWN plate wherever "
        "that step put something on the map - so a stage is not one picture of fifteen decisions. A step with no plate "
        "drew nothing: it measured, scanned or decided. The page is as current "
        "as the code, and the gate fails a stage that explains nothing. Read <code>dev/placement.md</code> for the rules "
        "across stages. Regenerated by <code>make placement-stages</code>, and by every landing that changes the engine.</p>",
    ]
    for r in rows:
        parts += [
            '<section class="stage">',
            f'<div class="hd"><span class="n">{r["i"]:02d}</span><span class="t">{escape(r["title"])}</span><span class="fn">{escape(r["fn"])}</span></div>',
            *(f'<p class="why">{escape(p)}</p>' for p in r["paras"]),
        ]
        if r["features"]:
            parts.append('<p class="feats"><span class="fl">Features this stage puts on the map</span> ' + escape(", ".join(r["features"])) + "</p>")
        if r["steps"]:
            parts.append(f'<details class="steps" open><summary>The algorithm, step by step ({len(r["steps"])})</summary>')
            for e in r["steps"]:
                parts.append(f'<div class="step"><span class="sn">{escape(e["name"])}</span>' + "".join(f"<p>{escape(p)}</p>" for p in e["paras"]))
                if e["features"]:
                    parts.append('<p class="feats"><span class="fl">Draws</span> ' + escape(", ".join(e["features"])) + "</p>")
                if e["img"]:
                    parts.append(f'<img src="{escape(e["img"])}" width="{e["iw"]}" height="{e["ih"]}" alt="after {escape(e["name"])}" loading="lazy">')
                    parts.append('<p class="after">the map after this step, and nothing later in the stage</p>')
                elif e["unrenderable"]:
                    # HONEST ABOUT THE ONE PLATE IT CANNOT MAKE, so "no plate" keeps meaning "drew nothing".
                    parts.append('<p class="after">no plate: this step draws INTO what the step before it left, so the map part-way through it is not a document the renderer will read</p>')
                parts.append("</div>")
            parts.append("</details>")
        if r["img"]:
            parts.append(f'<img src="{escape(r["img"])}" width="{r["iw"]}" height="{r["ih"]}" alt="{escape(r["title"])}" loading="lazy">')
            if r["fn"] == "stage_homesteads":
                parts.append(
                    '<p class="legend">Drawn over this plate: the site boundary the homesteads were seated against - the paddy\'s facing chords in blue, the outline of everything else (the hem, the marshes, the ponds, the reed toe) in red, the water and corridor segments in teal.</p>'
                )
        else:
            parts += [
                '<div class="noink">',
                '<div class="cap">This stage places no ink - it decides these</div>',
                '<div class="kv">',
                *(f'<div><span class="k">{escape(k)}</span><span class="v">{escape(v)}</span></div>' for k, v in r["decided"]),
                "</div></div>",
            ]
        parts.append("</section>")
    # EVERY CLICKABLE THING IS NAMED SOMEWHERE ON THIS PAGE (GM 2026-09-12). The stage lists above name what
    # this map draws; this names the rest, so a reader searching for any feature they can click finds it.
    _named = {k for r in rows for k in r["features"]} | {k for r in rows for e in r["steps"] for k in e["features"]}
    _rest = elsewhere_in_the_pool(_named, SKILL)
    if _rest:
        parts += [
            '<section class="stage">',
            '<div class="hd"><span class="t">Features this map does not have</span></div>',
            f'<p class="why">The {len(_named)} features listed under the stages above are the ones {escape(spec.name)} actually draws, read from the ink '
            "itself rather than from any list. The interactive map's vocabulary covers other kinds of place too, and those features are named here with a "
            "shipped map that has them - so searching this page for anything you can click on a map will find it.</p>",
            '<div class="kv">',
            *(f'<div><span class="k">{escape(k)}</span><span class="v">{escape(m or "no shipped map draws it today")}</span></div>' for k, m in _rest),
            "</div></section>",
        ]
    parts.append("</div>")
    page = os.path.join(out_dir, "hamlet-placement.html")
    with open(page, "w") as fh:
        fh.write("\n".join(parts) + "\n")
    return page


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(SKILL, "dev", "placement-stages"))
    ap.add_argument("--width", type=int, default=1100, help="plate width in px (default 1100)")
    # THE STEP PLATES ARE THE PAGE'S POINT AND ITS COST, so they can be turned off for a run that only wants the
    # stage walk (a landing's re-plate passes nothing, so it gets them: the GM reads this page, and a page that is
    # cheap to make and does not show what was asked for is not cheaper, it is useless).
    ap.add_argument("--no-steps", dest="steps", action="store_false", help="stage plates only - skip the per-step plates")
    a = ap.parse_args(argv)
    spec = HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")
    page = build_page(a.out, a.width, spec, a.steps)
    print(f"\nwrote {page}")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.tools.placement_stages")
    raise SystemExit(main())
