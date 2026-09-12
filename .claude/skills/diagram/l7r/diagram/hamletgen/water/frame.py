"""STAGE 1 - the water frame: the sluice, the fall and the canvas the field is fitted into.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement

from ..plan import SitePlan

# ---- STAGE 1: the water frame -------------------------------------------------------------------


def stage_water_frame(s: Settlement, plan: SitePlan) -> None:
    """Settle the drainage bearing and the land's fall BEFORE anything is placed.

    This is first because the skill says it is first, at every tier: "before a single feature is
    placed, decide the map's drainage bearing and, separately, the land's fall". Everything
    downstream reads them - which end of the fan is the head, which margin the cluster can stand on,
    which way the drain runs, where the marsh is allowed to be."""
    # THE MAP DECLARES THAT A SCRIPT MADE IT (GM 2026-08-13). Rules that the scripted path adopts
    # ahead of the hand-authored pool are gated on this tag, so a legacy map keeps its present
    # packing and starts obeying the new rule the moment it is CONVERTED - the migration enforces
    # itself instead of needing a list of exemptions that someone has to remember to prune.
    s.meta(
        generated_by="hamletgen",
        name=plan.spec.name,
        scale="hamlet",
        ftpx=plan.ftpx,
        toscale=True,
        households=plan.spec.households,
        water_flow=plan.water_flow,
        down_deg=plan.down_deg,
        windward=plan.windward,
        # THE FORM IS ROLLED, NOT ASSUMED (feature 126). This tier hardcoded `nucleated=True` from
        # the day it was written, which meant every hamlet the generator has ever produced was the
        # same KIND of settlement. The research supports three (research/homesteads.html, "Does a
        # hamlet have to be NUCLEATED at all?"), so per Principle XII the form is a seeded knob.
        #
        # `nucleated` is DERIVED from `settlement_form` rather than set beside it. They were two
        # independent facts that happened to agree; making one a function of the other means they
        # cannot drift, and every existing consumer of `nucleated` keeps working unchanged.
        settlement_form=plan.settlement_form,
        settlement_form_asked=plan.settlement_form,
        nucleated=plan.settlement_form == "nucleated",
        field_footbridges=True,
        water_kind="stream",
        # WHAT STANDS AT THE INTAKE, and which flank the brook passes on (feature 230): both rolled, both
        # recorded, so the page and the tests read the map's own answer rather than re-deriving it.
        intake=plan.intake,
        brook_side=plan.brook_side,
        # NO WORK YARDS ON A NO-RICE HAMLET (feature 150, GM 2026-08-28): the threshing yard is a rice
        # feature; the dike-pond archetype sells silk and fish and buys grain in. Declared here so the
        # bundle omits the yard (`_bundle_geom`) and `harvest_yards_present` stands aside.
        work_yards=plan.field_archetype != "mulberry_dike_fishpond",
        manure_form=plan.manure_form,  # the rolled manure form (feature 150 A2), read by farmstead_fixtures
        kosatsuba_siting=plan.kosatsuba_siting,  # frontage | waterside (feature 152 T21), read by place_kosatsuba
        copse_siting=plan.copse_siting,  # among_the_houses | against_the_belt (feature 152 T20)
    )
    s._work_yards = plan.field_archetype != "mulberry_dike_fishpond"
    # `_nucleated` IS NOT THE FORM - it is the engine's flag for a COMPACT BUNDLE (house + lee
    # garden + south yard, no per-house grove; see `_place_bundle`, which branches on it). The two
    # were the same thing only while every hamlet was nucleated.
    #
    # TRUE FOR NUCLEATED ALONE. This flag drives the bundle SHAPE, and the bundle CARRIES the
    # homestead grove, so it also decides whether a farm gets its own yashikirin or shelters behind
    # one village belt. The two cannot be split without splitting `_place_bundle`.
    #
    # It was briefly `!= "dispersed"`, reasoning that a row village's farmsteads front the street
    # adjacent to their neighbors and so stay compact. That is true of the BUNDLE and false of the
    # GROVE, and one flag cannot say both: linear maps drew a single village belt while
    # `meta["nucleated"]` declared them non-nucleated, and `groves_where_possible` correctly
    # reported four farms with clear windward room and no grove. A generator that DECLARES one thing
    # and DRAWS another is the failure this whole feature exists to remove, so the flag follows the
    # declaration and every non-nucleated farm gets its own grove.
    s._nucleated = plan.settlement_form == "nucleated"
    for knob, value in plan.spec.pins.items():
        s.pin_knob(knob, value)
