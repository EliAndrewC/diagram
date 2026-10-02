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
from l7r.diagram.settlement.rolling.access import ACCESS_HALF_FT  # noqa: E402

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
    # step plate of the hinterland (`IndexError` in the blade flush feature 298 retired). Truncating them by the same watermark
    # is exactly right - a group reserved BEFORE the step still points inside the rewound list; and a cover recorded after the
    # step is not on the plate (`_covers`, whose slots `_header` reserved before any step).
    "_covers",
    "_mark_groups",
    "_pending_stands",
    "_pending_yards",
    "_pending_farmsteads",
    "_captions",
    "_label_queue",
    "_lane_ink",
    "_scatter_frames",
    # ...AND THE DEFERRED WATER (the page audit, 2026-10-02): the brook, the ditches, the drain and the pond's fill are queued
    # in `water` / `late_water` and inked by the finish into a block reserved in `out`, so a step that drew only water counted
    # no ink, got no plate and named none of its features - "a step with no plate drew nothing" was false of `pond`
    "water",
    "late_water",
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
    # The DEFERRED stores are drawn at finish, so their ink sits in slots reserved long before the stage that filled them:
    # the ways (`ground`) and the water carry their class on each entry (`Settlement._tag`), and a tiled cover - the marsh,
    # the scrub - on its `Cover` (feature 298's slots are reserved by `_header`, so the marsh and the scrub were credited
    # to no stage and the closing list named them as features Inashiro does not have)
    for layer in ("ground", "water", "late_water", "_covers"):
        entries = getattr(s, layer, None)
        if isinstance(entries, list):
            for e in entries[lo.get(("attr", layer), 0) : hi.get(("attr", layer), len(entries))]:
                tag = e.get("cls") if isinstance(e, dict) else getattr(e, "cls", None)
                for key in tag_keys(tag):
                    found[key] = found.get(key, 0) + 1
    return sorted(found)


def tag_keys(tag: object) -> list[str]:
    """The classes a reader can click that one deferred entry's tag names: a plain key, both sides of a `Split`, every
    piece of a `Parts` - never `"-"`, the ink ruled NOT highlighted."""
    from l7r.diagram.interactive.tags import Split

    if isinstance(tag, str):
        keys = [tag]
    elif isinstance(tag, Split):
        keys = [tag.fill, tag.stroke]
    elif isinstance(tag, tuple):
        keys = [piece[0] for piece in tag if isinstance(piece, tuple) and piece and isinstance(piece[0], str)]
    else:
        keys = []
    return [k for k in dict.fromkeys(keys) if k and k != "-"]


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

    DERIVED, never listed: a class is present on a map when its MANIFEST counts its ink (`ink_classes`, written by every
    roll). It read the maps' interactive pages until the page audit of 2026-10-02: the gate evicts those pages, so a page
    built after a gate named seventeen classes - Kuwabata's pig sties and fish ponds among them - as drawn by no shipped
    map. A class no shipped map draws is named as such rather than omitted, because a reader can still meet it in the
    vocabulary."""
    import glob
    import json

    where: dict[str, str] = {}
    for manifest in sorted(glob.glob(os.path.join(skill, "pool", "hamlets", "*", "*.json"))):
        try:
            with open(manifest, encoding="utf-8") as fh:
                drawn = json.load(fh).get("ink_classes") or {}
        except OSError, ValueError, AttributeError:  # a manifest that cannot be read names nothing
            continue
        stem = os.path.basename(manifest)[: -len(".json")]
        for key in _hoverable():
            if key not in named and drawn.get(key):
                where.setdefault(key, stem)
    return sorted((k, where.get(k, "")) for k in _hoverable() if k not in named)


def _hoverable() -> list[str]:
    """Every class a reader can hover and click on a map page - the interactive vocabulary's own roster."""
    from l7r.diagram.interactive.classes import CLASSES

    return sorted(CLASSES)


def _ink_total(marks: dict[tuple[str, str], int]) -> int:
    """The ink a watermark stands at - the same five layers `_ink` counts, read off the watermark."""
    return sum(n for (kind, name), n in marks.items() if kind == "attr" and name in _INK_LAYERS)


def _ink(s: Settlement) -> int:
    """How many SVG records the settlement has emitted so far, across the four ink layers and the deferred ground.

    This is the test for "did that stage DRAW anything", and it is deliberately a count of records
    rather than a look at the rendered pixels: a stage can legitimately emit ink that happens to be
    invisible at plate scale, and that is not the case being detected here."""
    # ...and the DEFERRED ground features - the lanes, streets and roads a way stage lays - live in `ground` until the
    # finish inks them (feature 227: the web stage, which draws nothing else, read as "no ink" and got a card, not a plate)
    return sum(len(getattr(s, name, [])) for name in _INK_LAYERS)


_INK_LAYERS = ("out", "top", "walls", "toplabels", "ground", "water", "late_water")
"""The record lists that are ink: the four layers, the deferred ground (the ways) and the deferred water."""


def _decisions(s: Settlement) -> dict[str, object]:
    """The map's metadata as it stands - what a no-ink stage has to show for itself."""
    return dict(s.M["meta"])


def _plate(snap: Settlement, out_dir: str, stem: str, width: int, overlay: dict[str, Any] | None = None, render_w: int = 2600) -> tuple[str, int, int]:
    """Finish a COPY of the part-built settlement and scale its render down to a page plate.

    `overlay` (feature 227): the site boundary the homesteads were seated against - its chords, outline rings and
    corridor segments from the manifest's `site_boundary` - drawn over the plate in three colors, mapped through the
    finished copy's `meta.view`, because that boundary is the thing the GM asked about and no plate showed it."""
    from PIL import Image

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
            x0, y0, vw, _vh = snap.M["meta"].get("view") or (0.0, 0.0, float(snap.W), float(snap.H))  # a mid-roll copy is uncropped: the plate is the whole canvas
            sc = w / float(vw)
            im = draw_boundary(im.convert("RGB"), overlay, x0, y0, sc)
            im = draw_reservations(im, overlay, x0, y0, sc)
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


def homestead_overlay(s: Settlement) -> dict[str, Any]:
    """What the homesteads plate draws over itself (features 227, 287): the site boundary the homesteads were seated
    against, and the ground the seating RESERVED as it seated them - each house's access corridor (`access_corridors`,
    at its half-width), the exit strip the tree starts from (`access_exit`), and every household's wood-share seats
    (each house's `wood_share`, at the crown radius it reserved). A reservation no plate showed was a rule no reader could
    check against the picture."""
    out: dict[str, Any] = dict(s.M.get("site_boundary") or {})
    out["access"] = [rec["pts"] for rec in s.M.get("access_corridors") or [] if len(rec.get("pts") or []) >= 2]
    out["exit"] = s.M.get("access_exit")
    out["access_half"] = s.px(ACCESS_HALF_FT)
    out["wood"] = [[float(p[0]), float(p[1]), float((h.get("wood_share") or {}).get("r") or 0.0)] for h in s.M.get("houses") or [] for p in (h.get("wood_share") or {}).get("seats") or ()]
    return out


BOUNDARY_COLORS = {"chords": (30, 60, 220, 255), "rings": (200, 30, 30, 255), "water": (20, 150, 150, 255), "taken": (215, 40, 40, 70), "veil": (251, 247, 240, 165), "edge": (60, 50, 40, 255)}
"""The boundary's inks on the homesteads plate: the paddy's facing chords blue, the no-build outline red, the water's and the
registered corridors' lines teal, the ground the seating refuses a translucent red, the ground it never asks veiled in the
page's own paper color, and the edge of the seating window a dark rule."""


def window_mask(size: tuple[int, int], overlay: dict[str, Any], x0: float, y0: float, sc: float) -> Any:
    """Where the seating may offer a house, as an 8-bit mask over a plate: within the window's `bound` of the seat AND within
    its `reach` of the paddy's facing chords (`within_field_reach`), the two limits every grown seat is held to
    (`growth.grow_the_margin`). None where the manifest records no window (a form that is not grown)."""
    from PIL import Image, ImageChops, ImageDraw

    win = overlay.get("window")
    if not win:
        return None
    cx, cy, bound, reach = (float(v) for v in win)
    circle = Image.new("L", size, 0)
    px, py, pr = (cx - x0) * sc, (cy - y0) * sc, bound * sc
    ImageDraw.Draw(circle).ellipse((px - pr, py - pr, px + pr, py + pr), fill=255)
    near = Image.new("L", size, 0)
    draw = ImageDraw.Draw(near)
    rr = reach * sc
    for a, b, *_n in overlay.get("chords") or []:
        pa, pb = ((a[0] - x0) * sc, (a[1] - y0) * sc), ((b[0] - x0) * sc, (b[1] - y0) * sc)
        draw.line([pa, pb], fill=255, width=max(1, round(2 * rr)))
        for q in (pa, pb):
            draw.ellipse((q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr), fill=255)
    return ImageChops.multiply(circle, near) if overlay.get("chords") else circle


def refused_ground(overlay: dict[str, Any]) -> Any:
    """The ground the seating refuses a homestead without asking the fit test, rebuilt from the recorded boundary exactly as
    the seating built it (`boundary.FreeGround` over the window's box): its surely-taken cells. None without a window."""
    from l7r.diagram.hamletgen.homesteads.boundary import FreeGround

    win = overlay.get("window")
    if not win:
        return None
    cx, cy, bound, _reach = (float(v) for v in win)
    chains = [[((a[0], a[1]), (b[0], b[1]), (n[0], n[1])) for a, b, n in overlay.get("chords") or []]]
    corridors = ([((a[0], a[1]), (b[0], b[1]), c) for a, b, c in overlay.get("water") or []], [((a[0], a[1]), (b[0], b[1]), c) for a, b, c in overlay.get("corridors") or []])
    outline = ([[(x, y) for x, y in r] for r in overlay.get("rings") or []], [[(x, y) for x, y in h] for h in overlay.get("holes") or []])
    return FreeGround(chains, corridors, outline, (cx - bound, cy - bound, cx + bound, cy + bound))


def draw_boundary(im: Any, overlay: dict[str, Any], x0: float, y0: float, sc: float) -> Any:
    """Draw the ground the homesteads were seated against over a plate (features 227, 308). Where the seating recorded its
    window, only what it asks is shown: outside the window is veiled; inside, the ground it refuses is tinted and the
    boundary's lines are drawn, clipped to the window, and the window's edge is ruled. Without a window, every line of the
    boundary is drawn, as recorded."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter

    lines = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(lines)
    refused = Image.new("L", im.size, 0)  # the refused cells as a mask, so the rule can go round the ground a house may take
    fg = refused_ground(overlay)
    if fg is not None:
        c = fg.cell * sc
        for i, j in fg.taken:
            x, y = (fg.x0 + i * fg.cell - x0) * sc, (fg.y0 + j * fg.cell - y0) * sc
            draw.rectangle((x, y, x + c, y + c), fill=BOUNDARY_COLORS["taken"])
            ImageDraw.Draw(refused).rectangle((x, y, x + c, y + c), fill=255)
    for ring in (overlay.get("rings") or []) + (overlay.get("holes") or []):
        pts = [((x - x0) * sc, (y - y0) * sc) for x, y in ring]
        draw.line([*pts, pts[0]], fill=BOUNDARY_COLORS["rings"], width=max(2, round(sc * 3)))
    for a, b, *_rest in overlay.get("chords") or []:
        draw.line([((a[0] - x0) * sc, (a[1] - y0) * sc), ((b[0] - x0) * sc, (b[1] - y0) * sc)], fill=BOUNDARY_COLORS["chords"], width=max(2, round(sc * 4)))
    for a, b, *_rest in (overlay.get("water") or []) + (overlay.get("corridors") or []):
        draw.line([((a[0] - x0) * sc, (a[1] - y0) * sc), ((b[0] - x0) * sc, (b[1] - y0) * sc)], fill=BOUNDARY_COLORS["water"], width=max(2, round(sc * 3)))
    mask = window_mask(im.size, overlay, x0, y0, sc)
    base = im.convert("RGBA")
    if mask is None:
        return Image.alpha_composite(base, lines).convert("RGB")
    veil = Image.new("RGBA", im.size, BOUNDARY_COLORS["veil"])
    base = Image.composite(base, Image.alpha_composite(base, veil), mask)
    lines.putalpha(ImageChops.multiply(lines.getchannel("A"), mask))  # the lines and the tint clipped to the window
    base = Image.alpha_composite(base, lines)
    # THE RULE GOES ROUND THE GROUND A HOUSE MAY TAKE, not round the window's two limits (the GM, 2026-10-02: the shape "extends
    # into the rice paddy fields where certainly none of that could go"): the window less its refused cells, so the paddy
    # inside the limits lies outside the rule, tinted, and only seatable ground is enclosed
    open_ground = ImageChops.subtract(mask, refused)
    edge = open_ground.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0)
    base.paste(Image.new("RGBA", im.size, BOUNDARY_COLORS["edge"]), (0, 0), edge)
    return base.convert("RGB")


RESERVATION_COLORS = {"access": (235, 135, 20, 110), "exit": (45, 45, 55, 170), "wood": (25, 110, 35, 255)}
"""The reservations' inks on the homesteads plate: the access corridors a translucent orange band, the exit strip a
dark gray band (it was magenta, and the GM read it as the boundary's red, 2026-10-02), the wood-share seats a dark green ring - none of them a color the map itself uses for ground."""


def draw_reservations(im: Any, overlay: dict[str, Any], x0: float, y0: float, sc: float) -> Any:
    """Draw `homestead_overlay`'s reservations over a plate at scale `sc` from the view's corner (x0, y0): the corridor
    and exit bands at their true width, composited translucent so the map shows through, then the wood seats' rings."""
    from PIL import Image, ImageDraw

    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    band = max(2, round(2 * float(overlay.get("access_half") or 0.0) * sc))
    for key, segs in (("access", overlay.get("access") or []), ("exit", [overlay["exit"]] if overlay.get("exit") else [])):
        for pts in segs:
            draw.line([((p[0] - x0) * sc, (p[1] - y0) * sc) for p in pts], fill=RESERVATION_COLORS[key], width=band, joint="curve")
    for x, y, r in overlay.get("wood") or []:
        cx, cy, rr = (x - x0) * sc, (y - y0) * sc, max(2.0, r * sc)
        draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=RESERVATION_COLORS["wood"], width=max(2, round(sc * 2)))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


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
                overlay = homestead_overlay(s) if not had_boundary and "site_boundary" in s.M else None
                if overlay and overlay.get("window"):  # the window's two limits, in feet, for the plate's legend
                    row["window_ft"] = (float(overlay["window"][2]) / s.px(1.0), float(overlay["window"][3]) / s.px(1.0))
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


def snapshot(s: Settlement) -> Settlement:
    """A copy of the part-built settlement to finish into a plate, its MEMOS left behind (feature 287): a memo is a roll's
    cache of questions asked of the standing ground (`rolling/access.py`'s `_corridor_memo` holds lazy answers a copy
    cannot take), not the map, and the reader of each rebuilds it when it finds none. Each is copied as None."""
    return copy.deepcopy(s, {id(v): None for k, v in vars(s).items() if k.endswith("_memo")})


def _make_plates(s: Settlement, jobs: list[Any], out_dir: str, width: int) -> None:
    """Render one stage's plates - its own and its steps' - and hang each result on the row that asked for it.

    The copy and the rewind happen in the worker, so the peak is `max_workers` settlements rather than all of them.
    A step plate is rendered at a smaller size than a stage plate: it answers "what appeared", not "read the map"."""
    if not jobs:
        return

    def one(job: Any) -> tuple[Any, tuple[str, int, int]]:
        target, mark, stem, overlay, render_w = job
        snap = snapshot(s)
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


def homestead_legend(window_ft: tuple[float, float] | None) -> str:
    """The homesteads plate's legend: what `draw_boundary` and `draw_reservations` drew over it, and - where the seating
    recorded its window - the window's two limits in feet."""
    reserved = (
        "Over that, the ground the seating reserved as it seated them: each house's access corridor in orange (bending where it was "
        "routed round what stands), the exit strip in dark gray - the start of the hamlet's way out, reserved before any house so "
        "every house's path can join it - and each household's wood-share seats as "
        "dark green rings."
    )
    if window_ft is None:
        return (
            "Drawn over this plate: the site boundary the homesteads were seated against - the paddy's facing chords in blue, the "
            "outline of the no-build ground in red, the water and corridor segments in teal. " + reserved
        )
    bound, reach = window_ft
    return (
        f"Drawn over this plate: what the seating asked of the ground. The dark rule encloses the ground a house may be offered: "
        f"within {bound:,.0f} ft of the margin's seat (the cluster's limit, which keeps a nucleated hamlet together) and "
        f"{reach:,.0f} ft of the paddy, less the ground refused outright. Beyond those two limits the plate is veiled, because no "
        "seat there is ever asked. Within them, the red tint is the refused ground, rasterized once and looked up per seat: the "
        "paddy's side of its facing chords (blue), the no-build ground's outline (red: the hem, the marshes, the ponds, the dry "
        "plots, the reed toe) and the water's clearance (teal). " + reserved
    )


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
        if name not in keep and name.endswith((".png", ".svg", ".json", ".html")):  # ...and what a plate left half-made
            os.remove(os.path.join(out_dir, name))
            print(f"  pruned stale plate {name}")
    parts = [
        "<title>Hamlet placement order</title>",
        "<style>",
        ":root{--ink:#241c14;--dim:#6b5d4d;--rule:#d9cdbb;--bg:#fbf7f0;--card:#fff;--step:#f4ede1}",
        ':root:not([data-theme="light"]){}',
        "@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){--ink:#ece3d6;--dim:#a2957f;--rule:#3b332a;--bg:#171310;--card:#201a15;--step:#2a231c}}",
        ':root[data-theme="dark"]{--ink:#ece3d6;--dim:#a2957f;--rule:#3b332a;--bg:#171310;--card:#201a15;--step:#2a231c}',
        "body{margin:0;padding:1.25rem;background:var(--bg);color:var(--ink);",
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
        ".toc{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:.9rem 1.25rem;margin:0 0 1.6rem}",
        ".toc .cap{font:700 .8rem/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);margin-bottom:.4rem}",
        ".toc ol{list-style:none;margin:0;padding:0;columns:2 22rem;column-gap:2rem}",
        ".toc li{break-inside:avoid;margin:.15rem 0}",
        ".toc a{color:var(--ink);text-decoration:none}.toc a:hover{text-decoration:underline}",
        ".toc .n{margin-right:.55rem}",
        "</style>",
        '<div class="wrap">',
        "<h1>Hamlet placement order</h1>",
        f'<p class="lede">{escape(spec.name)}, rolled one stage at a time. Each plate is the map as it stands '
        f"after that stage and nothing later - the one build the driver makes (nothing is re-rolled), snapshotted {len(STAGES)} times. "
        "Every word on this page is read from the code: a stage's explanation is its docstring, and the steps under it "
        "are the functions the docstring names as its algorithm, each shown in its own words, with its OWN plate wherever "
        "that step put something on the map - so a stage is not one picture of fifteen decisions. A step with no plate "
        "drew nothing: it measured, scanned or decided. The page is as current "
        "as the code, and the gate fails a stage that explains nothing. Read <code>dev/placement.md</code> for the rules "
        "across stages. Regenerated by <code>make placement-stages</code>, and by every landing that changes the engine.</p>",
    ]
    # THE CONTENTS (GM 2026-10-02: "it would be really helpful for me to be able to start at the top and then jump to the part
    # that I care about"): every stage, and the closing list, linked by its anchor
    _named = {k for r in rows for k in r["features"]} | {k for r in rows for e in r["steps"] for k in e["features"]}
    _rest = elsewhere_in_the_pool(_named, SKILL)
    parts += [
        '<nav class="toc"><div class="cap">Contents</div><ol>',
        *(f'<li><a href="#s{r["i"]:02d}"><span class="n">{r["i"]:02d}</span>{escape(r["title"])}</a></li>' for r in rows),
        *(['<li><a href="#missing">Features this map does not have</a></li>'] if _rest else []),
        "</ol></nav>",
    ]
    for r in rows:
        parts += [
            f'<section class="stage" id="s{r["i"]:02d}">',
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
                parts.append(f'<p class="legend">{escape(homestead_legend(r.get("window_ft")))}</p>')
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
    if _rest:
        parts += [
            '<section class="stage" id="missing">',
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
    # THE POOL'S OWN SPEC (pool/hamlets/inashiro/inashiro.gen.py), its fixture floor included: the page says it is Inashiro
    spec = HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", settlement_form="nucleated", fixtures_min={"shrine": 1})
    page = build_page(a.out, a.width, spec, a.steps)
    print(f"\nwrote {page}")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.tools.placement_stages")
    raise SystemExit(main())
