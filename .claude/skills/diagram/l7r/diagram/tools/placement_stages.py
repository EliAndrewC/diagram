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
import os
import sys
from contextlib import redirect_stdout
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if SKILL not in sys.path:
    sys.path.insert(0, SKILL)

from l7r.diagram.hamletgen import HamletSpec, plan_site  # noqa: E402
from l7r.diagram.hamletgen.driver import STAGES  # noqa: E402
from l7r.diagram.settlement import Settlement  # noqa: E402

# WHAT EACH STAGE IS FOR, AND WHY IT SITS WHERE IT SITS. Keyed by function name so a reordering of
# `STAGES` reorders the page automatically and a RENAMED or NEW stage shows up as missing prose
# rather than silently inheriting its neighbor's - which is the failure mode a hand-kept list has.
NOTES: dict[str, tuple[str, str]] = {
    "stage_water_frame": (
        "The bearing and the fall",
        "THIS STAGE DRAWS NOTHING, and that is the whole point of it. The generator's first act is to "
        "settle two numbers - which way the water runs, and which way the land falls - and write them "
        "into the map's metadata. Which end of the fan is the head, which margin the cluster may stand "
        "on, which way the drain runs, where the marsh is allowed to be: every one of those is decided "
        "downstream of these values, and none of it is ink yet. The water SKELETON is drawn in the next "
        "stage, by the same call that lays the paddy.",
    ),
    "stage_field": (
        "The water skeleton and the paddy",
        "The field is SOLVED for a real acreage rather than drawn to a pixel size, and it is laid before "
        "any built thing exists. That is the ordering decision with the longest reach on the whole map: "
        "the settlement afterwards takes whatever margin the field leaves it. Where that margin curves, "
        "the cluster has to curve with it. This is also where WATER first becomes ink - the intake, the "
        "head race and the field ditches arrive in the same call that lays the plots (`build_comb` returns "
        "the canals and the plots together), which is why there is no plate showing water alone: "
        "splitting the stage to manufacture one was priced and declined, because STAGES is the "
        "generator's design and a page does not get to reorder it.",
    ),
    "stage_sink": (
        "Where the runoff goes",
        "The tail drain and its pond or off-map outfall. It runs with the water rather than with the "
        "ground cover because the pond is a HARD feature - houses, lanes and trees all have to avoid it, "
        "so it must exist before any of them are seated.",
    ),
    "stage_seat": (
        "Where the settlement will sit",
        "The seat band: which stretch of the field margin the cluster will occupy, with its back to the "
        "high ground and its face to the water. NOTHING IS DRAWN HERE - this stage decides a place and "
        "reserves no ground at all, which is why it can run before the houses without constraining them. "
        "It used to be the front half of a stage that also drew the connector and the field spur, and "
        "separating the two is what let every lane move after the farmhouses.",
    ),
    "stage_track": (
        "The connector and the field spur",
        "The track out to the off-map road, and the path to the fields - drawn NOW, after the farmhouses, "
        "because a lane drawn earlier takes ground the houses then cannot have. That is true whatever the "
        "lane represents: a road may well predate a settlement in the world, but this generator does not "
        "inherit a road, it DRAWS one, and drawing it first reserves a no-build corridor the placer then "
        "refuses seats against. Both tracks now start from the settlement as it actually stands rather "
        "than from where it was predicted to go.",
    ),
    "stage_homesteads": (
        "The farmhouses",
        "Each bundle is seated against the field edge and packed toward its neighbors - and at this "
        "moment there is NOT ONE LANE ANYWHERE ON THE MAP. That is the whole feature: the houses answer "
        "to the field, the water and each other, and nothing else has taken ground before them. Every "
        "way on the finished map - the connector, the field spur, the cluster's spine and the alleys - "
        "is laid after this plate and positioned from where these houses actually landed.",
    ),
    "stage_appurtenances": (
        "Yards, gardens, byres, wells, sheds",
        "The rest of each steading, plus the shared fixtures. Kept as its own stage after the houses "
        "because several of them are sited RELATIVE to a house that must already exist - a threshing "
        "yard south of its own farmhouse, a byre off the frontage, a well between steadings.",
    ),
    "stage_web": (
        "The lanes the settlement wore",
        "Every ENDOGENOUS way - the cluster's spine and the web of alleys off it - drawn now because only "
        "now is there a settlement to derive them from. Both are fitted to where the houses actually "
        "landed rather than to where the seat band predicted they would land, which is the distinction "
        "that matters: the spine used to be sized on the band while the houses spread wider than it, so "
        "it could not be guaranteed to reach them. Laid first, these lanes competed for ground with the "
        "very houses they exist to serve - measured, the four pool clusters' long axes grew 15-97%, sprawl "
        "no check measures. They also run after the byres and wells, not merely after the houses; between "
        "the two, their corridors reserved courtyard ground and exiled fixtures up to 210 ft. A DISPERSED "
        "hamlet draws nothing here at all, because it has no internal network - its farmsteads stand in "
        "their own holdings and the connector is the only way on the map. The web is then READ AS "
        "SHAPES before the stage ends (feature 133 T31/T32): every near-junction is closed so the "
        "lanes are one network in ink rather than by tolerance, each junction is made once, ends "
        "within a few paces meet at one node, and every lane is string-pulled and cleared of hairpins "
        "and zigzags - a worn path minimizes its turns, and a bend sits at a plot corner.",
    ),
    "stage_notice": (
        "The notice board - the last FEATURE placed",
        "The kosatsuba is deliberately the last map feature, after even the crop and the title - only the "
        "label phase follows it, and that phase places captions, not features - and the reason is about the "
        "settlement rather than about the drawing (GM 2026-08-29): \u201cwhere you put the notice board on the "
        "map does depend on what other features already exist ... the real humans that live in the society "
        "that decide where the notice board will go will look around at the things which already exist and "
        "then decide where to put the notice board. They may even decide to move a notice board which has "
        "already been placed.\u201d Every other stage either reserves ground or grows into it; the board does "
        "neither. It is a 12 x 5 ft plank a village drives in beside a way once the village is there, so it "
        "is the one feature that should see the whole map before it chooses. "
        "It stands ON a way - on the verge, a few feet off the tread (feature 133 T13), because a kosatsu is "
        "read where people pass - and WHICH way, and where along it, is a per-settlement knob rolled from the "
        "map\u2019s own seed over the placements the record attests and the map can site (feature 154). "
        "Placing it last also fixed a defect by construction: sited among the trees it used to claim a ~55 ft "
        "cleared disc, and an entrance seat on a windward fringe punched a 40 ft hole in the shelter belt that "
        "nothing replanted. No feature is placed after the board now, so it displaces nothing - and the GM\u2019s "
        "ruling is that it never should have: \u201chumans would not need to clear any amount of space in order "
        "to put up a notice board at the side of a path.\u201d It may stand under a canopy at the wood\u2019s edge.",
    ),
    "stage_labels": (
        "The labels - the final phase, after the last feature",
        "Every caption on the map is placed here, against the finished sheet, and nothing comes after it "
        "(feature 157, GM 2026-08-29): \u201cadd a phase at the very end of every settlement creation process, "
        "which is putting down the labels for things. Thus, after the final map feature is added, which on a "
        "hamlet is the notice board, there is a final phase in which we add labels for whatever map features "
        "get labels. This is because how we place labels will always depend on what else is on the map.\u201d "
        "No feature draws its own caption any more: a stage that wants one queues it (`label()`), and this "
        "stage drains the queue (`Settlement.place_labels`) once every feature a caption might have to avoid "
        "exists. It draws no feature and reserves no ground, so it can only ever be last - the same argument "
        "that put the notice board after the frame, taken one step further. The plate is the previous one "
        "with its captions on, which on a hamlet is exactly what the stage is.",
    ),
    "stage_waterward": (
        "A polder\u2019s waterward fringe",
        "The reed strips outside the dike, on the flanks that face the water (feature 150). It needs the "
        "SEAT - which flank is landward is a fact about where the village stands - and it RESERVES ground, "
        "so it runs here rather than in the hinterland with the rest of the wild cover: laid there, it was "
        "drawn over a connector that had already been routed through it; laid before the houses and the "
        "track, both treat it as the wet ground it is. A valley hamlet such as this one draws nothing here, "
        "which is why the plate is a card: the stage decides for a polder and is silent everywhere else.",
    ),
    "stage_pond_stock": (
        "Pig sties and duck pens on the ponds",
        "A dike-pond hamlet\u2019s livestock fixtures (feature 150 A3/A4): duck pens at the corners of the "
        "grow-out ponds nearest the houses, pig sties on the dikes of the next nearest - pens first, because "
        "ducks are driven out to the water and penned back every day while pigs are fed where they stand, "
        "so the pens take the shortest walk. It runs after the appurtenances because each fixture is sited "
        "relative to the houses as placed, and before the lane web because it reserves ground the web must "
        "thread around, like the byres and wells before it. Nothing on a valley hamlet, hence the card.",
    ),
    "stage_hinterland": (
        "The marsh, then scrub and rough grazing",
        "Ground cover fills what is left, so it runs after everything it must avoid; it reads the drawn "
        "features as obstacles rather than reserving anything from them. Three moves, in order: the reed "
        "marsh at the wet toe, its inner edge following the fan's foot along the collector (T30); then the "
        "coppice patches are SCANNED (not yet drawn) and the shelter belt is computed, both from the "
        "houses as they stand; then the scrub is scattered with every wood as a soft keep-out - brush and "
        "pine stop at a wood's line and at the marsh, grass grades into them over one shared feather "
        "(T12, T34, T35). The floor of a worked village wood was kept clear, so no scrub stands under "
        "its crowns.",
    ),
    "stage_woodland": (
        "The woodland commons",
        "Managed coppice on ground nothing else wanted, drawn on the parcels the previous stage scanned - "
        "so the scrub has already kept out of them. Each parcel is an irregular ring inside the reach its "
        "keep-outs were tested at, never a rectangle (T36): an iriai wood was bounded by ridge, stream and "
        "path, and governed by rules rather than parcel lines.",
    ),
    "stage_windbreak": (
        "The shelter belt",
        "Sited from the wind and the cluster it shelters, so it needs the cluster finished. Its canopy is "
        "deferred to the flush at the end - drawn here it would be painted over by nothing, but its "
        "crowns must be filtered against every structure, and not all of them exist yet.",
    ),
    "stage_bamboo": (
        "The bamboo stands",
        "A take-yabu is a clonal thicket with a hard edge - a stand, not a seasoning - and a culm is inches "
        "across, so at this scale bamboo is drawn as a STAND-LEVEL glyph: the stand's position and extent to "
        "scale, the marks inside symbolic (the convention of Japan's own topographic legend, which gives bamboo "
        "its own symbol beside broadleaf and conifer). Seated by the previous stage on the cluster's shady side "
        "or at the field margin's shady end, per the `bamboo` knob; drawn here, after the belt, over scrub that "
        "already kept out of it. Before this stage existed bamboo was 20% of the belt's crowns, one six-foot "
        "culm at a time, and invisible.",
    ),
    "stage_crossings": (
        "Planks and decks",
        "Every way that crosses water gets its deck HERE, which is why the earlier way stages are free to cross a ditch: the crossing is legal because this stage will deck it.",
    ),
    "stage_frame": (
        "Crop, title, scalebar",
        "The canvas is deliberately generous and is cropped to content only now. Erring large is cheap - unused canvas is thrown away - while erring small silently mis-shapes the field.",
    ),
}


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
    with redirect_stdout(io.StringIO()):
        snap.finish(base, render=True)
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
