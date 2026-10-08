"""STAGE 1 - the water frame: the sluice, the fall and the canvas the field is fitted into.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement

from ..consts import POLDER_ARCHETYPES
from ..plan import SitePlan

def grows_grain(plan: SitePlan) -> bool:
    """Does the hamlet grow a grain its farms thresh? Every archetype does but the mulberry dike-fishpond, whose
    leftover parcels are standing rice (grain) or ponds (none).

    Research: grain to thresh - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: every rice and dry-field farm keeps a yard
    """
    return plan.field_archetype != "mulberry_dike_fishpond" or plan.leftover == "rice"


# ---- STAGE 1: the water frame -------------------------------------------------------------------


def stage_water_frame(s: Settlement, plan: SitePlan) -> None:
    """Record the drainage bearing and the land's fall BEFORE anything is placed.

    This is first because the skill says it is first, at every tier: "before a single feature is
    placed, decide the map's drainage bearing and, separately, the land's fall". Everything
    downstream reads them - which end of the fan is the head, which margin the cluster can stand on,
    which way the drain runs, where the marsh is allowed to be. They were settled by `plan_site`, which
    `generate` runs before the first stage; this stage writes them to the manifest and pins the knobs the
    plan resolved.

    Steps:
        l7r.diagram.settlement.Settlement.pin_knob

    Research:
        fall and drainage declared first - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the bearing and the fall recorded before anything is placed
        no work yards where no grain grows - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: every rice and dry-field farm keeps a yard; `work_yards` false only on a dike-pond hamlet whose leftover parcels are ponds (`grows_grain`; the GM's no-rice ruling, 2026-08-28)
        field footbridges on every hamlet - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: `field_footbridges` true, a crossing where a bund path meets a ditch
        house racks - research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: a rack by every house where the harvest weather is changeable
        compact bundle for the clustered form only - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a non-nucleated farm takes its own grove
        manifest record - NONE: the rolled plan written to the manifest
    """
    # WHICH MAPS HAVE A BROOK AT ALL: the comb archetypes tap a stream (`stage_field` -> `feed_brook`), the polders
    # take their water from a reservoir at the high corner (`stage_polder`). `water_kind` stays "stream" on both and
    # that is DELIBERATE rather than missed: it is the knob-resolution CONTEXT (`settlement/_knobs.py`), so changing
    # it on the polder would change which knob values are admissible and re-roll a shipped map, to fix a field whose
    # honest sibling `water_source` ("reservoir") is already recorded beside it. The cost of leaving it: `water_kind`
    # reads as the engine's rolling context and not as a claim about the sheet.
    _brook_fed = plan.field_archetype not in POLDER_ARCHETYPES
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
        # WHETHER THE WIND IS THE REGION'S OR THE MAP'S OWN (feature 261): the windbreak's pop-up says which.
        wind_source="declared" if plan.spec.windward else "regional",
        # THE FORM IS ROLLED, NOT ASSUMED (feature 126). This tier hardcoded `nucleated=True` from
        # the day it was written, which meant every hamlet the generator has ever produced was the
        # same KIND of settlement. The research supports three (research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html), so per Principle XII the form is a seeded knob.
        #
        # `nucleated` is DERIVED from `settlement_form` rather than set beside it. They were two
        # independent facts that happened to agree; making one a function of the other means they
        # cannot drift, and every existing consumer of `nucleated` keeps working unchanged.
        settlement_form=plan.settlement_form,
        settlement_form_asked=plan.settlement_form,
        nucleated=plan.settlement_form == "nucleated",
        # THE GROVE'S SIDES AND THE GROUND THAT CHOSE THEIR TABLE (feature 291), recorded on every hamlet; the engine's
        # dispersed bundle reads `grove_sides` and `grove_flank` (`homestead_parts/groves.py` `grove_faces`).
        grove_sides=plan.grove_sides,
        grove_flank=plan.grove_flank,
        flood_ground=plan.flood_ground,
        row_line=plan.row_line,
        row_sides=plan.row_sides,
        row_water=plan.row_water,
        farm_water=plan.farm_water,
        field_footbridges=True,
        water_kind="stream",
        # WHAT STANDS AT THE INTAKE, and which flank the brook passes on (feature 230): both rolled, both
        # recorded, so the page and the tests read the map's own answer rather than re-deriving it.
        # ...AND A MAP WITH NO BROOK RECORDS NEITHER (settlement-review, feature 230 pass 12). A polder is fed from a
        # reservoir at its high corner and draws no stream at all, so these two named works that are nowhere on the
        # sheet: Kuwabata shipped `intake: weir` and `brook_side: -1` beside `streams: []`, and anything reading the
        # field - a later check, the page, a person - was told about water the map does not have. The knob rolled and
        # had nothing to govern. It is still ROLLED on every map, because the roll is part of the seed stream and
        # skipping it would move every archetype's downstream draws; what changes is only what gets written down.
        intake=plan.intake if _brook_fed else None,
        brook_side=plan.brook_side if _brook_fed else None,
        # NO WORK YARDS WHERE NO GRAIN GROWS (feature 150, GM 2026-08-28: the threshing yard is a rice feature; feature
        # 328: 0037 keeps a yard on every rice and dry-field farm). A dike-pond hamlet sells silk and fish and buys grain
        # in - unless its leftover parcels stand in rice, which is threshed. Declared here so the bundle omits the yard
        # (`_bundle_geom`) and `harvest_yards_present` stands aside.
        work_yards=grows_grain(plan),
        manure_form=plan.manure_form,  # the rolled manure form (feature 150 A2), read by farmstead_fixtures
        harvest_weather=plan.harvest_weather,  # the declared harvest weather (feature 282), recorded for the page and the tests
        kosatsuba_siting=plan.kosatsuba_siting,  # frontage (feature 328: the drawing-water form retired)
        copse_siting=plan.copse_siting,  # among_the_houses (feature 328: the belt-side form retired)
    )
    s._work_yards = grows_grain(plan)
    s._house_racks = plan.harvest_weather == "changeable"  # a rack by every house's yard (feature 282, `HARVEST_WEATHERS`)
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
