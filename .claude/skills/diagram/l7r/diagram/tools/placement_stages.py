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

It is a by-hand tool (see `pyproject.toml`'s coverage `source` list, which names the measured tools
one by one on purpose). UNDER THE 100% RULE all the same (GM 2026-09-02). Re-run it whenever `STAGES` changes; the
page is generated, never hand-edited.
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import os
import sys
from contextlib import redirect_stdout
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if SKILL not in sys.path:
    sys.path.insert(0, SKILL)

from l7r.diagram.hamletgen import HamletSpec, SitePlan, plan_site  # noqa: E402
from l7r.diagram.hamletgen.driver import STAGES, roll_scope  # noqa: E402
from l7r.diagram.settlement import Settlement  # noqa: E402

# WHAT EACH STAGE IS FOR, AND WHY IT SITS WHERE IT SITS. Keyed by function name so a reordering of
# `STAGES` reorders the page automatically and a RENAMED or NEW stage shows up as missing prose
# rather than silently inheriting its neighbor's - which is the failure mode a hand-kept list has.
# THE NOTES ARE DATA - `placement_stages_notes.json` beside this module (feature 207): prose a reader sees,
# so an edit is not an engine change and re-keys nothing; `tests/tools/test_placement_stages.py` holds the
# roster to `STAGES` both ways, in `make quick`.
with open(os.path.join(HERE, "placement_stages_notes.json"), encoding="utf-8") as _fh:
    NOTES: dict[str, tuple[str, str]] = {name: (title, why) for name, (title, why) in json.load(_fh).items()}


def _ink(s: Settlement) -> int:
    """How many SVG records the settlement has emitted so far, across all four layers.

    This is the test for "did that stage DRAW anything", and it is deliberately a count of records
    rather than a look at the rendered pixels: a stage can legitimately emit ink that happens to be
    invisible at plate scale, and that is not the case being detected here."""
    return sum(len(getattr(s, name, [])) for name in ("out", "top", "walls", "toplabels"))


def _decisions(s: Settlement) -> dict[str, object]:
    """The map's metadata as it stands - what a no-ink stage has to show for itself."""
    return dict(s.M["meta"])


def _plate(snap: Settlement, out_dir: str, stem: str, width: int) -> tuple[str, int, int]:
    """Finish a COPY of the part-built settlement and scale its render down to a page plate."""
    from PIL import Image

    base = os.path.join(out_dir, stem)
    # THE PLATE IS THE PNG, SO ONLY THE PNG IS RENDERED (feature 208, GM 2026-09-07: "a whole lot of rasterizing
    # that is completely pointless"). `finish(render=True)` also made the interactive page's raster picture -
    # resvg at 3 px per map px, PIL, libwebp - for each of the eighteen stage pages, and nothing reads those
    # pages: the walk-through links the plates. So the page is written vector-only (`render=False`) and the PNG
    # is rendered by the same call `finish` would have made. The gate's sampler caught this process at 1.6 GB.
    with redirect_stdout(io.StringIO()):
        snap.finish(base, render=False)
    env_w = os.environ.get("DIAGRAM_PNG_WIDTH")
    snap.render_png(base, int(env_w) if env_w else 2600)
    png = base + ".png"
    with Image.open(png) as im:
        w, h = im.size
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
    return os.path.basename(png), size[0], size[1]


def build_page(out_dir: str, width: int, spec: HamletSpec) -> str:
    """Roll `spec` one stage at a time, writing a plate per stage and an index page. Returns the path."""
    os.makedirs(out_dir, exist_ok=True)
    plan = plan_site(spec)
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    rows = []
    # THE BASELINE IS TAKEN BEFORE STAGE 1, not from an empty dict: `Settlement.__init__` already
    # puts the canvas W/H into `meta`, and starting empty made stage 1's card claim credit for two
    # values the constructor set. A no-ink card must show what THAT stage decided and nothing else.
    known: dict[str, object] = _decisions(s)
    _walk(s, plan, out_dir, width, rows, known)
    return _write_page(out_dir, rows, spec)


def _walk(s: Settlement, plan: SitePlan, out_dir: str, width: int, rows: list[tuple[object, ...]], known: dict[str, object]) -> None:
    """The stage loop of `build_page`, lifted out so the roll scope wraps exactly the loop (feature 210)."""
    # THE WALK-THROUGH IS A ROLL (feature 210): the whole stage loop sits in one `roll_scope`, so the memo
    # is cleared and the heap trimmed when the page is built, as after any roll. Not per stage: the memo
    # serves across stages within a roll, and a plate is a copy finished mid-roll.
    with roll_scope(plan.spec):
        for i, stage in enumerate(STAGES, 1):
            before = _ink(s)
            with redirect_stdout(io.StringIO()):
                stage(s, plan)
            drew = _ink(s) - before
            title, why = NOTES.get(stage.__name__, ("(no note yet)", "This stage has no entry in `NOTES` - add one."))
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
            if drew:
                # A COPY IS FINISHED, NOT THE LIVE SETTLEMENT: `finish` flushes deferred canopies, seats
                # captions and crops, all of which mutate. Snapshotting the real one would change the map
                # the next stage sees, and the page would document a build nobody runs.
                img, iw, ih = _plate(copy.deepcopy(s), out_dir, stem, width)
                decided: list[tuple[str, str]] = []
            else:
                img, iw, ih = None, 0, 0
                decided = [(k, str(v)) for k, v in now.items() if known.get(k) != v]
                stale = os.path.join(out_dir, stem + ".png")
                if os.path.isfile(stale):
                    os.remove(stale)  # a stage that used to draw and no longer does leaves no orphan plate
            known = now
            rows.append((i, stage.__name__, title, why, img, iw, ih, decided))
            print(f"  {i:>2}. {stage.__name__:<22} -> {img or f'(no ink - {len(decided)} values decided)'}")


def _write_page(out_dir: str, rows: list[tuple[object, ...]], spec: HamletSpec) -> str:
    """The tail of `build_page`: prune the orphan plates, write the index page, return its path."""
    # PRUNE EVERY PLATE THIS RUN DID NOT WRITE. The per-stage removal above only catches a stage that
    # kept its index and stopped drawing; it cannot see a RENAME or a RENUMBER, which is what actually
    # happens when `STAGES` is reordered. Feature 128 split `stage_ways` into `stage_seat` and
    # `stage_track` and moved the houses ahead of both, and every plate from 06 down shifted by one -
    # leaving seven orphans in a COMMITTED directory, `04-stage_ways.png` among them. An orphan here is
    # worse than clutter: the page is how the GM reads the build order, and a leftover plate showing
    # lanes before houses is a picture of the very thing the feature removed.
    keep = {r[4] for r in rows if r[4]} | {"hamlet-placement.html"}
    for name in sorted(os.listdir(out_dir)):
        if name not in keep and name.endswith(".png"):
            os.remove(os.path.join(out_dir, name))
            print(f"  pruned stale plate {name}")

    parts = [
        "<title>Hamlet placement order</title>",
        "<style>",
        ":root{--ink:#241c14;--dim:#6b5d4d;--rule:#d9cdbb;--bg:#fbf7f0;--card:#fff}",
        ':root:not([data-theme="light"]){}',
        "@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){--ink:#ece3d6;--dim:#a2957f;--rule:#3b332a;--bg:#171310;--card:#201a15}}",
        ':root[data-theme="dark"]{--ink:#ece3d6;--dim:#a2957f;--rule:#3b332a;--bg:#171310;--card:#201a15}',
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
        "img{display:block;width:100%;height:auto;border:1px solid var(--rule);border-radius:3px;background:#fff}",
        ".noink{border:1px dashed var(--rule);border-radius:3px;padding:1rem 1.15rem;background:transparent}",
        ".noink .cap{font:700 .8rem/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.06em;",
        "text-transform:uppercase;color:var(--dim);margin-bottom:.7rem}",
        ".kv{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.3rem 1.5rem;margin:0}",
        ".kv div{display:flex;gap:.6rem;justify-content:space-between;border-bottom:1px dotted var(--rule);",
        "padding:.15rem 0;font:.87rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}",
        ".kv .k{color:var(--dim)}.kv .v{color:var(--ink);font-weight:700;text-align:right}",
        "</style>",
        '<div class="wrap">',
        "<h1>Hamlet placement order</h1>",
        f'<p class="lede">{escape(spec.name)}, rolled one stage at a time. Each plate is the map as it stands '
        f"after that stage and nothing later - the same build (the driver's first roll), snapshotted {len(STAGES)} times. Read "
        "<code>dev/placement.md</code> for the rules; this is what they look like. Generated by "
        "<code>python3 -m l7r.diagram.tools.placement_stages</code> - re-run it when <code>STAGES</code> changes.</p>",
    ]
    for i, fn, title, why, img, iw, ih, decided in rows:
        parts += [
            '<section class="stage">',
            f'<div class="hd"><span class="n">{i:02d}</span><span class="t">{escape(title)}</span><span class="fn">{escape(fn)}</span></div>',
            f'<p class="why">{escape(why)}</p>',
        ]
        if img:
            parts.append(f'<img src="{escape(img)}" width="{iw}" height="{ih}" alt="{escape(title)}" loading="lazy">')
        else:
            parts += [
                '<div class="noink">',
                '<div class="cap">This stage places no ink - it decides these</div>',
                '<div class="kv">',
                *(f'<div><span class="k">{escape(k)}</span><span class="v">{escape(v)}</span></div>' for k, v in decided),
                "</div></div>",
            ]
        parts.append("</section>")
    # The "why there is no water-only plate" closing note was folded into stage 02's own prose
    # (GM 2026-08-27, feature 133 T37: the page ends with its last plate).
    parts.append("</div>")
    page = os.path.join(out_dir, "hamlet-placement.html")
    with open(page, "w") as fh:
        fh.write("\n".join(parts) + "\n")
    return page


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(SKILL, "dev", "placement-stages"))
    ap.add_argument("--width", type=int, default=1100, help="plate width in px (default 1100)")
    a = ap.parse_args(argv)
    spec = HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")
    page = build_page(a.out, a.width, spec)
    print(f"\nwrote {page}")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.tools.placement_stages")
    raise SystemExit(main())
