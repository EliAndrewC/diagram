"""STAGE 2 - the comb field itself: the fitted fan drawn, the head race taken off the brook, the intake set on its bank.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement, point_in_poly
from l7r.diagram.sitegen.geom import net_acres

from ..consts import (
    POLDER_ARCHETYPES,
)
from ..plan import SitePlan
from .brook import draw_intake, feed_brook
from .fit import fit_field, head_sluice
from .polder import stage_polder


def stage_field(s: Settlement, plan: SitePlan) -> None:
    """Lay the irrigation skeleton and carve the paddies between its threads.

    Second, because the water is first and the field is grown AROUND the water (the water-first
    inversion `waterfields.py` exists for). The head sluice comes from `head_sluice`, which puts the
    intake at the field's high head - gravity, not a knob."""
    if plan.field_archetype in POLDER_ARCHETYPES:
        stage_polder(s, plan)
        return
    dx, dy = plan.fall
    sluice, position = head_sluice(plan)
    s.M["meta"]["water_source"] = position
    s.M["meta"]["water_source_position"] = position

    across, step = s.plot_texture(plan.plot_size, "organic")
    net = fit_field(plan, sluice, plan.spec.seed, across, step)
    plan.net = net
    plan.acres = net_acres(net, plan.ftpx)

    # THE DRAIN'S CONTINUATION IS ALWAYS OURS TO DRAW. `build_comb` hands back a `brook` and
    # `draw_comb_field` draws it when it is there - straight downhill, a FIXED 520 px. Both sinks
    # need something else. A hamlet draining into its own tameike must have NO brook at all (the
    # runoff stops at the pond, and `stage_sink` supplies the ditch that reaches it). A hamlet
    # draining OFF the frame needs a brook that actually gets there, and 520 px is a constant tuned
    # against the canvases the authored maps happened to use: on a wider one the brook stops in open
    # ground and fails `stream_runs_off_edge` + `stream_end_anchored`, which is the same
    # pinned-constant failure the pond set-back had. So the brook is cleared here either way, and
    # `stage_sink` draws the off-map one at a length DERIVED from the distance to the canvas edge.
    net["brook"] = []

    plan.envelope = [(round(x, 1), round(y, 1)) for x, y in net["envelope"]]  # routed against BEFORE the field is drawn (see feed_brook)
    s.field_polys.append(list(plan.envelope))
    s.meta(dry_furrows_vary=net["furrows_vary"])
    s.M["meta"]["field_archetype"] = "valley_paddy"
    # The brook that feeds the head, running in from off-map: the visible source. It is drawn as a
    # STREAM ending AT the sluice, where it becomes the head-race - it does not run on over the
    # paddies. `draw_comb_field` then records the hairline topology channel that grounds the field's
    # water source for the gate.
    # EVERY cultivated ring, and the supply canals with them: the brook passes outside all of it, not
    # merely outside the paddy envelope (`brook_skirt`, and the review that measured the hem crossings).
    # EVERY cultivated RING - the paddies and the dry hem alike, the hem being laid outside the envelope the
    # first cut cleared. NOT the supply canals: a canal is one polyline spanning the whole fan, so a profile
    # that asks which rings lie abreast of a station gets the field's widest point at every station from it,
    # and the brook is pushed out to the fan's shoulder for its whole length (measured: offsets of 400-600 ft
    # against a 34 ft skirt). The canals run inside the plots they water, so clearing the plots clears them.
    plan.brook = feed_brook(plan, sluice, [[(float(x), float(y)) for x, y in p["poly"]] for p in net["plots"] + net["dry_plots"]])
    s.draw_comb_field(net, f"{plan.spec.name.lower()}-paddies", {"kind": "stream", "stream": plan.brook})
    draw_intake(s, plan, sluice)
    # THE PARTS OF A DITCH THAT RUN OUTSIDE THE CROP become no-build corridors.
    #
    # `s.field_channel` registers none of its own, and inside the field envelope it does not need
    # to - the crop is blocked ground already. But a delivery ditch's tail and the collector run out
    # past the envelope onto open margin, where the placer is otherwise free to seat a homestead
    # squarely on the water (`no_structure_on_channel`). Only those stretches are reserved:
    # blanketing the whole ditch net costs the field its ring of farmhouses, because a comb's
    # deliveries run right along the margin the front row wants (`field_ringed`, three maps).
    #
    # And it goes AFTER `draw_comb_field`, which is where `M['field_ditches']` is written. Placed
    # before it, the loop had nothing to iterate and reserved nothing at all - silently, since an
    # empty loop looks exactly like a loop with nothing to do.
    for ditch in s.M.get("field_ditches", []):
        run = [(float(v[0]), float(v[1])) for v in ditch["poly"]]
        outside = [(a, b) for a, b in zip(run, run[1:], strict=False) if not point_in_poly((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, plan.envelope)]
        for a, b in outside:
            s.corridors.append(([a, b], 30.0))
