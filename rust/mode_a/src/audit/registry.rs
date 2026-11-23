//! The check REGISTRY (feature 449 T175, `pack_audit/registry.py` whole; feature 254, D5): every pass/fail question the audit asks of a
//! Mode A sheet, with the building types it applies to, the red fixture that proves it fires, and the compliant fix its failure names.
//!
//! WHY A REGISTRY. The GM (2026-09-19): "some of those automated checks will likely just be the same for all types of buildings ... and
//! some of them may be specific to individual building types." A check is shared, or the type's own when its declaration
//! (`buildings/types.json`) lists it: no tier is named here. The measured figures that are not pass/fail (the vacant rectangles, the
//! density, the aligned gaps) stay the report's.
//!
//! Research:
//!     the check registry - NONE: the checks listed in order with their fixtures and fixes, deciding nothing about a building

use std::path::Path;
use std::sync::{Mutex, PoisonError};

use l7r_gate_research::Error;

use super::onmap::OnMap;
use super::{
    checks as c, labels as lbl, mapmatch as mm, marks_drawn as md, palette as pal,
    program_rules as pr, roads as rd, shared as s, sun, Sheet,
};
use crate::parse::ParsedPlan;
use crate::py::fixed;
use crate::types::{load_types, BuildingType, Kinds};

/// What a check is handed: the parsed sheet, its source, its declared type, its notes' form and map declaration, the tree its
/// declaration, its kinds' registry and a declared manifest are read from (the Python's package root), and the sheet's name, the seed a
/// rolled site is keyed by (`armory_site`, 449 T303).
pub struct Context<'a> {
    pub plan: &'a ParsedPlan,
    pub svg: Sheet<'a>,
    pub btype: Option<&'a BuildingType>,
    pub form: Option<&'a str>,
    pub on_map: Option<&'a OnMap>,
    pub tree: &'a Path,
    pub sheet: &'a str,
}

impl<'a> Context<'a> {
    #[must_use]
    pub fn new(
        plan: &'a ParsedPlan,
        text: &'a str,
        btype: Option<&'a BuildingType>,
        form: Option<&'a str>,
        on_map: Option<&'a OnMap>,
        tree: &'a Path,
        sheet: &'a str,
    ) -> Self {
        Self {
            plan,
            svg: Sheet::new(text),
            btype,
            form,
            on_map,
            tree,
            sheet,
        }
    }
}

type Run = fn(&Context) -> Result<Vec<String>, Error>;

/// One registered check: its name, what it runs, whether it is the shared layer's (else a declaration lists it), the red fixture under
/// `tests/fixtures/` it FIRES on, the fix a failure prints, and why it did not run on a sheet (the report prints it).
pub struct Check {
    pub name: &'static str,
    pub run: Run,
    pub shared: bool,
    pub fixture: &'static str,
    pub fix: &'static str,
    pub skipped: fn(&Context) -> Option<&'static str>,
}

impl Check {
    /// The tiers this check applies to: None for the shared layer, else derived from the declaration.
    ///
    /// # Errors
    /// The declaration cannot be read.
    pub fn types(&self, tree: &Path) -> Result<Option<Vec<String>>, Error> {
        if self.shared {
            return Ok(None);
        }
        Ok(Some(
            load_types(tree)?
                .into_iter()
                .filter(|t| t.checks.iter().any(|n| n == self.name))
                .map(|t| t.tier)
                .collect(),
        ))
    }

    /// Whether it applies to a sheet of `tier`.
    ///
    /// # Errors
    /// The declaration cannot be read.
    pub fn applies_to(&self, tier: Option<&str>, tree: &Path) -> Result<bool, Error> {
        if self.shared {
            return Ok(true);
        }
        // `tier in (self.types or frozenset())`: the declaration read first, whatever the tier
        let types = self.types(tree)?.unwrap_or_default();
        Ok(tier.is_some_and(|t| types.iter().any(|x| x == t)))
    }
}

fn never(_: &Context) -> Option<&'static str> {
    None
}

fn tub_adrift(ctx: &Context) -> Vec<String> {
    c::fire_water_adrift(ctx.plan)
        .iter()
        .map(|t| {
            format!(
                "tub at svg({},{}) is {} ft from the nearest building",
                fixed(t.x, 0),
                fixed(t.y, 0),
                fixed(t.gap_ft, 1)
            )
        })
        .collect()
}

fn tub_off_its_door(ctx: &Context) -> Vec<String> {
    c::tubs_off_their_doors(ctx.plan)
        .iter()
        .map(|t| {
            let how = if t.door_ft == f64::INFINITY {
                "stands at a building that tags no door".to_owned()
            } else {
                format!(
                    "stands {} ft from its building's nearest door",
                    fixed(t.door_ft, 1)
                )
            };
            format!(
                "a fire-water tub at svg({},{}) {how}",
                fixed(t.x, 0),
                fixed(t.y, 0)
            )
        })
        .collect()
}

fn tub_in_building(ctx: &Context) -> Vec<String> {
    c::tubs_in_buildings(ctx.plan, c::TUB_BLDG_MIN_PX)
        .iter()
        .map(|t| {
            format!(
                "a fire-water tub at svg({},{}) reaches {} ft INTO a building",
                fixed(t.x, 0),
                fixed(t.y, 0),
                fixed(t.into_ft, 1)
            )
        })
        .collect()
}

fn tub_on_well(ctx: &Context) -> Vec<String> {
    c::tubs_on_wells(ctx.plan, c::TUB_WELL_MIN_PX)
        .iter()
        .map(|t| {
            format!(
                "a fire-water tub at svg({},{}) overlaps a well",
                fixed(t.x, 0),
                fixed(t.y, 0)
            )
        })
        .collect()
}

fn occluded(ctx: &Context) -> Vec<String> {
    c::occluded_foreground(ctx.plan, c::OCCLUSION_MIN_PX)
        .iter()
        .map(|o| {
            format!(
                "{} at svg({},{}) is under a feature drawn later",
                o.kind,
                fixed(o.x, 0),
                fixed(o.y, 0)
            )
        })
        .collect()
}

fn passage(ctx: &Context) -> Vec<String> {
    c::passage_blockers(ctx.plan)
        .iter()
        .map(|b| {
            format!(
                "a {} x {} ft object at svg({},{}) stands in a {} ft opening",
                fixed(b.w_ft, 1),
                fixed(b.h_ft, 1),
                fixed(b.x, 0),
                fixed(b.y, 0),
                fixed(b.opening_ft, 1)
            )
        })
        .collect()
}

fn board(ctx: &Context) -> Vec<String> {
    c::notice_board_adrift(ctx.plan)
        .iter()
        .map(|b| {
            format!(
                "notice board at svg({},{}) is {} ft from the nearest gate opening",
                fixed(b.x, 0),
                fixed(b.y, 0),
                fixed(b.gap_ft, 1)
            )
        })
        .collect()
}

fn doors(ctx: &Context) -> Vec<String> {
    c::floating_doors(ctx.plan)
        .iter()
        .map(|d| {
            format!(
                "a door at svg({},{}) floats {} ft inside the building",
                fixed(d.x, 0),
                fixed(d.y, 0),
                fixed(d.gap_ft, 1)
            )
        })
        .collect()
}

fn doors_off(ctx: &Context) -> Vec<String> {
    md::doors_off_their_walls(ctx.plan)
        .iter()
        .map(|d| {
            let how = if d.how == "outside" {
                "outside its wall"
            } else {
                "floating inside its building"
            };
            format!(
                "a door at svg({},{}) is {how}",
                fixed(d.x, 0),
                fixed(d.y, 0)
            )
        })
        .collect()
}

fn steps(ctx: &Context) -> Vec<String> {
    md::steps_past_revetment(ctx.svg.text)
        .iter()
        .map(|t| {
            format!(
                "the landing steps at svg({},{}) run {} ft past the revetment's face",
                fixed(t.x, 0),
                fixed(t.y, 0),
                fixed(t.past_ft, 1)
            )
        })
        .collect()
}

fn arches(ctx: &Context) -> Vec<String> {
    md::arches_not_in_plan(ctx.svg.text)
        .iter()
        .map(|n| format!("the torii at line {n} is drawn as a silhouette, not in plan"))
        .collect()
}

fn on_wall(ctx: &Context) -> Vec<String> {
    c::structures_on_walls(ctx.plan, c::WALL_OVERLAP_MIN_PX)
        .iter()
        .map(|w| {
            format!(
                "a {} x {} ft structure at svg({},{}) reaches {} ft into the {} or the foot clear of its face",
                fixed(w.w_ft, 0),
                fixed(w.h_ft, 0),
                fixed(w.x, 0),
                fixed(w.y, 0),
                fixed(w.into_ft, 1),
                w.wall
            )
        })
        .collect()
}

fn program_complete(ctx: &Context) -> Result<Vec<String>, Error> {
    let Some(btype) = ctx.btype else {
        return Ok(Vec::new());
    };
    let site = mm::site_classes(ctx.plan, &ctx.svg, ctx.on_map, ctx.tree)?;
    Ok(lbl::check_program(
        ctx.plan,
        btype,
        ctx.form,
        site.as_deref(),
    ))
}

fn size_bands(ctx: &Context) -> Result<Vec<String>, Error> {
    let Some(btype) = ctx.btype else {
        return Ok(Vec::new());
    };
    with_kinds(ctx.tree, |kinds| {
        lbl::check_bands(ctx.plan, btype, ctx.form, kinds)
    })
}

/// The Mode A kinds' registry of `tree`, read once for the process as the Python's import of `compound_kinds` read it (feature 449 T175:
/// read once a sheet, it cost the lockstep 3.7 s over the red fixtures, observed 2026-11-17, method: each check timed in the test).
fn with_kinds<T>(tree: &Path, f: impl FnOnce(&mut Kinds<'static>) -> T) -> T {
    static CACHE: Mutex<Vec<Kinds<'static>>> = Mutex::new(Vec::new());
    let mut cache = CACHE.lock().unwrap_or_else(PoisonError::into_inner);
    let i = if let Some(i) = cache.iter().position(|k| k.tree() == tree) {
        i
    } else {
        // one path a tree, kept for the process as the registry it names is
        let kept: &'static Path = Box::leak(tree.to_path_buf().into_boxed_path());
        cache.push(Kinds::new(kept));
        cache.len() - 1
    };
    f(&mut cache[i])
}

/// A check's further red fixtures, beside the one its registry row names: each a failure mode that row's fixture does not draw, found
/// unnamed by T211 and wired by T212 (feature 449) to the check each was cut for - its git history and the Python test that read it.
/// The pool sweep (`crate::pool_sweep`) holds each check to firing on each, under the tier of the sheet it was cut from.
#[cfg(test)]
pub(crate) const MORE_FIXTURES: &[(&str, &str)] = &[
    // the second Ubame tub fix (the GM, 2026-07-26): one tub of 19 hanging 0.8 px into the house across a 9 px alley, its center
    // outside - the residue a center test left once the gross case (`ubame-tubs-inside-red.svg`) was fixed
    ("tubs_in_buildings", "ubame-tub-straddle-red.svg"),
    // Hayakawa's frozen layout round (2026-07): its notice board far from every gate and its kura door 2 px inside its wall, the
    // second sheet beside `ochiba-layout-red.svg` that the Python test held both checks to
    ("notice_board_adrift", "hayakawa-layout-red.svg"),
    ("floating_doors", "hayakawa-layout-red.svg"),
    // the country shrine's precinct ringed by a compound wall (feature 254's fixture for `fence_not_wall`, which feature 268 replaced in
    // its registry row by this check, a fence refused as well as a wall): the wall, beside `hoshigaoka-fenced-precinct-red.svg`'s fence
    ("no_precinct_enclosure", "hoshigaoka-walled-red.svg"),
];

/// Every registered check, in the order the report prints them.
pub const CHECKS: [Check; 44] = [
    // --- the shared layer: pure geometry, every sheet ---
    Check {
        name: "structures_overlap",
        run: |ctx| Ok(s::structures_overlap(ctx.plan, s::OVERLAP_SHARE)),
        shared: true,
        fixture: "ochiba-overlap-red.svg",
        fix: "move one footprint clear of the other, or draw a contained part (an engawa, a porch) fully inside its building",
        skipped: never,
    },
    Check {
        name: "structures_on_walls",
        run: |ctx| Ok(on_wall(ctx)),
        shared: true,
        fixture: "ubame-privy-in-wall-red.svg",
        fix: "set the structure a foot or two clear of the wall's inner face, or break the wall around it if it IS part of the wall",
        skipped: never,
    },
    // NO CHECK OF WHERE A CAPTION STANDS (feature 286): captions are placed by the one placer in the render pipeline
    Check {
        name: "occluded_foreground",
        run: |ctx| Ok(occluded(ctx)),
        shared: true,
        fixture: "ubame-occlusion-red.svg",
        fix: "move the buried glyph or feature to the top layer",
        skipped: never,
    },
    Check {
        name: "floating_doors",
        run: |ctx| Ok(doors(ctx)),
        shared: true,
        fixture: "ochiba-layout-red.svg",
        fix: "set the door glyph on the wall it opens through",
        skipped: never,
    },
    // feature 335: the door convention by TAG (light-filled doors included), the stepped landing, the plan arch
    Check {
        name: "doors_off_their_walls",
        run: |ctx| Ok(doors_off(ctx)),
        shared: true,
        fixture: "hayakawa-steps-and-doors-red.svg",
        fix: "set the door wholly inside its building, its outer edge on the wall it opens through (research 0117's drawing page)",
        skipped: never,
    },
    Check {
        name: "steps_past_revetment",
        run: |ctx| Ok(steps(ctx)),
        shared: true,
        fixture: "hayakawa-steps-and-doors-red.svg",
        fix: "notch the flight into the revetment: no tread past its water-side face (research 0176)",
        skipped: never,
    },
    Check {
        name: "arch_in_plan",
        run: |ctx| Ok(arches(ctx)),
        shared: true,
        fixture: "ubame-torii-silhouette-red.svg",
        fix: "draw the torii in plan - the beam across the approach, the two post squares and the id=\"arch\" rect (docs/buildings.md)",
        skipped: never,
    },
    Check {
        name: "passage_blockers",
        run: |ctx| Ok(passage(ctx)),
        shared: true,
        fixture: "ochiba-stones-in-passage-red.svg",
        fix: "move the object clear of the track - stones and posts FLANK a passage",
        skipped: never,
    },
    Check {
        name: "gate_widths",
        run: |ctx| Ok(s::gate_widths(ctx.plan, s::GATE_MIN_FT, s::GATE_MAX_FT)),
        shared: true,
        fixture: "ochiba-capped-gates-red.svg",
        fix: "draw the opening at passage width from the INK (pull each flanking endpoint back by half a stroke)",
        skipped: never,
    },
    Check {
        name: "scale_bar_present",
        run: |ctx| Ok(s::scale_bar_present(ctx.plan)),
        shared: true,
        fixture: "ochiba-no-scale-red.svg",
        fix: "add the 90 px scale bar with its `30 ft` and `(3 px = 1 ft)` labels",
        skipped: never,
    },
    // every sheet, on a map or not (feature 268, the GM 2026-09-27): a sheet on a map is cropped to its ink like any other
    Check {
        name: "viewbox_cropped",
        run: |ctx| s::viewbox_cropped(ctx.svg.text, ctx.plan, s::CROP_MAX_MARGIN_PX, s::CROP_TOL_PX),
        shared: true,
        fixture: "ochiba-wide-viewbox-red.svg",
        fix: "crop the viewBox to ~15-25 px of parchment around the ink",
        skipped: never,
    },
    Check {
        name: "trees_overlap",
        run: |ctx| Ok(s::trees_overlap(ctx.plan, c::WALL_OVERLAP_MIN_PX)),
        shared: true,
        fixture: "hoshigaoka-tree-on-fence-red.svg",
        fix: "move the tree onto open ground - off the building, the fence and the well; crowns may overlap each other, but a tree is not drawn on top of another",
        skipped: never,
    },
    Check {
        name: "matches_map",
        run: |ctx| mm::matches_map(ctx.plan, &ctx.svg, ctx.on_map, mm::MAP_GRAIN_PX, ctx.tree),
        shared: true,
        fixture: "hoshigaoka-off-map-red.svg",
        fix: "draw what the map shows at the subject and nothing it does not - move, add or remove the feature, or size the subject to the map's footprint (the map is the canon for the site)",
        skipped: |ctx| mm::skipped(ctx.on_map),
    },
    // a kitchen bed gets its sun (feature 283, the GM 2026-09-28): every sheet, since both programs draw one
    Check {
        name: "garden_sun",
        run: |ctx| sun::garden_sun(ctx.plan, &ctx.svg),
        shared: true,
        fixture: "hoshigaoka-garden-shaded-red.svg",
        fix: "move the bed to open ground where it gets its hours - clear of the shadows the report names, never by declaring a sun bed half-shade",
        skipped: never,
    },
    // --- the program itself, generic over the declaration: every type's required items and their bands (D7) ---
    Check {
        name: "program_complete",
        run: program_complete,
        shared: true,
        fixture: "ochiba-no-cell-red.svg",
        fix: "draw and label the missing program item, or record in the notes why this instance lacks it",
        skipped: never,
    },
    Check {
        name: "size_bands",
        run: size_bands,
        shared: true,
        fixture: "ochiba-big-bath-red.svg",
        fix: "redraw the footprint inside its band, or record the instance particular that justifies it and re-derive the band",
        skipped: never,
    },
    // --- the building-review's sweep, moved into the registry (feature 294, plan B16 and B19-B23): every sheet ---
    Check {
        name: "lodging_entrances",
        run: |ctx| pr::lodging_entrances(&ctx.svg, ctx.plan, c::DOOR_FLUSH_TOL_PX),
        shared: true,
        fixture: "ochiba-lodging-no-door-red.svg",
        fix: "draw a door (data-kind=\"door\") or a genkan on the lodging block's outer wall, flush in it; divide a barracks or a retainers' long-house into dwellings by solid walls, a door to each",
        skipped: never,
    },
    Check {
        name: "size_hierarchy",
        run: |ctx| Ok(pr::size_hierarchy(ctx.plan, &pr::HIERARCHY)),
        shared: true,
        fixture: "ochiba-stables-outsize-red.svg",
        fix: "resize the pair so the compound ranks as the record reads it - the house out-measures its kitchen, the barracks its stables",
        skipped: never,
    },
    Check {
        name: "sheet_furniture",
        run: |ctx| pr::sheet_furniture(&ctx.svg),
        shared: true,
        fixture: "ochiba-no-title-red.svg",
        fix: "draw the title (bold, the sheet's largest text) just above the compound, and no compass rose or key box",
        skipped: never,
    },
    Check {
        name: "roads_leave_the_frame",
        run: |ctx| rd::roads_leave_the_frame(&ctx.svg, ctx.plan),
        shared: true,
        fixture: "ochiba-road-stub-red.svg",
        fix: "run the road off the viewBox edge, or end it at the gate, door, arch or road it serves - never a stub stopping short",
        skipped: never,
    },
    Check {
        name: "palette_roles",
        run: |ctx| pal::palette_roles(&ctx.svg, &pal::roles()),
        shared: true,
        fixture: "ochiba-stables-painted-red.svg",
        fix: "paint the building in its palette role's fill (SKILL.md, Palette)",
        skipped: never,
    },
    Check {
        name: "gate_feeds_its_road",
        run: |ctx| rd::gate_feeds_its_road(&ctx.svg, ctx.plan, rd::ROAD_GATE_TOL_FT),
        shared: true,
        fixture: "ochiba-road-wider-than-gate-red.svg",
        fix: "narrow the lane to the side gate's passage (a foot of grain at most), or widen the gate if the record calls for a wider one",
        skipped: never,
    },
    Check {
        name: "veranda_depths",
        run: |ctx| pr::veranda_depths(&ctx.svg, pr::VERANDA_FT),
        shared: true,
        fixture: "ochiba-veranda-narrow-red.svg",
        fix: "draw the veranda 3 to 6 ft deep (9-18 px), half a ken to one ken (research 0102's drawing page)",
        skipped: never,
    },
    // --- fire-water: required by BOTH programs, so both declarations list it (spec 254 FR-003, round-1 item 2) ---
    Check {
        name: "fire_water_adrift",
        run: |ctx| Ok(tub_adrift(ctx)),
        shared: false,
        fixture: "ochiba-tub-adrift-red.svg",
        fix: "move the tub to a wall or eaves corner - a tensuioke is gutter-fed",
        skipped: never,
    },
    Check {
        name: "tubs_off_their_doors",
        run: |ctx| Ok(tub_off_its_door(ctx)),
        shared: false,
        fixture: "ochiba-tub-off-door-red.svg",
        fix: "move the tub beside a door of its building - research 0100 keeps the water at the entrance",
        skipped: never,
    },
    Check {
        name: "fire_water_distribution",
        run: |ctx| pr::fire_water_distribution(&ctx.svg, ctx.plan),
        shared: false,
        fixture: "ubame-kitchen-one-tub-red.svg",
        fix: "seat a tub by the eaves of the listed wooden building (two at the kitchen), and none by a plaster kura alone",
        skipped: never,
    },
    Check {
        name: "tubs_in_buildings",
        run: |ctx| Ok(tub_in_building(ctx)),
        shared: false,
        fixture: "ubame-tubs-inside-red.svg",
        fix: "move the tub OUT, clear of the wall",
        skipped: never,
    },
    Check {
        name: "tubs_on_wells",
        run: |ctx| Ok(tub_on_well(ctx)),
        shared: false,
        fixture: "ochiba-tub-on-well-red.svg",
        fix: "move the tub to a different eaves corner",
        skipped: never,
    },
    // --- the magistracy's own ---
    Check {
        name: "notice_board_adrift",
        run: |ctx| Ok(board(ctx)),
        shared: false,
        fixture: "ochiba-layout-red.svg",
        fix: "move the notice board to within 40 ft of a gate opening",
        skipped: never,
    },
    Check {
        name: "privies_by_zone",
        run: |ctx| pr::privies_by_zone(&ctx.svg, pr::PRIVY_MIN),
        shared: false,
        fixture: "ochiba-privy-detached-red.svg",
        fix: "attach the family's and the guests' privies to the residence (data-part-of=\"residence\"), and stand one in each court - at least three in all",
        skipped: never,
    },
    Check {
        name: "coverage_band",
        run: |ctx| s::coverage_band(ctx.plan, s::COVERAGE_FLOOR, s::COVERAGE_CEILING, s::COVERAGE_TOL),
        shared: false,
        fixture: "ochiba-coverage-red.svg",
        fix: s::COVERAGE_FIX,
        skipped: never,
    },
    Check {
        name: "perimeter_hugging",
        run: |ctx| s::perimeter_hugging(ctx.plan, s::HUGGING_FLOOR),
        shared: false,
        fixture: "ochiba-hugging-red.svg",
        fix: "move the building against its wall - the center of each court stays open",
        skipped: never,
    },
    Check {
        name: "two_court_zoning",
        run: |ctx| s::two_court_zoning(ctx.plan),
        shared: false,
        fixture: "ochiba-zoning-red.svg",
        fix: "put the hearing court on the gate's side of the divider and the residence behind it",
        skipped: never,
    },
    Check {
        name: "armory_site",
        run: |ctx| Ok(super::armory::armory_site(ctx.plan, ctx.sheet, ctx.form)),
        shared: false,
        fixture: "hayakawa-armory-misplaced-red.svg",
        fix: "draw the armory where `<sheet>:armory site` rolls it among the sites the sheet offers - a room of the gate range, an end bay of the office hall (the west or east one `<sheet>:armory end bay` rolls, the back row drawn from that end), or a store of its own in the outer court - and declare its form (`**Form**: armory in the gate range` or `armory as a store of its own`; none for the hall's bay)",
        skipped: never,
    },
    Check {
        name: "stall_width",
        run: |ctx| s::stall_width(&ctx.svg),
        shared: false,
        fixture: "hayakawa-wide-stalls-red.svg",
        fix: "draw the stable's stalls one ken (~6 ft) wide, the earth passage before them and the grooms' room in it (0108)",
        skipped: never,
    },
    Check {
        name: "postern_approach",
        run: |ctx| Ok(s::postern_approach(ctx.plan)),
        shared: false,
        fixture: "county-sealed-postern-red.svg",
        fix: "keep a way of at least 3 ft clear before each gate and postern, on both faces of its wall",
        skipped: never,
    },
    Check {
        name: "shrine_tree",
        run: |ctx| s::shrine_tree(&ctx.svg),
        shared: false,
        fixture: "county-shrine-without-tree-red.svg",
        fix: "stand a tree beside the compound shrine: a crown tagged sacred tree, data-part-of the compound shrine, its trunk within 15 ft of the hall",
        skipped: never,
    },
    Check {
        name: "well_gear",
        run: |ctx| s::well_gear(&ctx.svg),
        shared: true,
        fixture: "ochiba-well-without-gear-red.svg",
        fix: "draw the well's lifting gear over the curb as the compound generator draws it (rust/mode_a/src/compound/emit_parts.rs) - an open-air well its rolled sweep or pulley frame and any roof as an unfilled outline on four posts, an indoor well the beam pulley and no roof (<g data-kind=\"well\" data-gear=... data-at=\"cx,cy\">)",
        skipped: never,
    },
    Check {
        name: "one_compound_shrine",
        run: |ctx| Ok(s::one_compound_shrine(ctx.svg.text)),
        shared: false,
        fixture: "hayakawa-two-shrines-red.svg",
        fix: "draw one compound shrine and enshrine the second god in its hall",
        skipped: never,
    },
    // --- the country shrine's own, each fixture cut from the Hoshigaoka exemplar ---
    Check {
        name: "sanctuary_on_axis",
        run: |ctx| Ok(s::sanctuary_on_axis(ctx.plan, s::AXIS_TOL_FT)),
        shared: false,
        fixture: "hoshigaoka-sanctuary-off-axis-red.svg",
        fix: "set the sanctuary on the approach axis behind the hall",
        skipped: never,
    },
    Check {
        name: "arch_on_approach",
        run: |ctx| s::arch_on_approach(ctx.plan, s::EDGE_TOL_FT),
        shared: false,
        fixture: "hoshigaoka-arch-adrift-red.svg",
        fix: "stand the arch over the approach where it crosses the fence",
        skipped: never,
    },
    Check {
        name: "well_clear_of_arch",
        run: |ctx| Ok(s::well_clear_of_arch(ctx.plan)),
        shared: false,
        fixture: "hoshigaoka-well-on-approach-red.svg",
        fix: "draw the stone basin beside the approach, and keep it and any well clear of the way and the arches",
        skipped: never,
    },
    Check {
        name: "no_precinct_enclosure",
        run: |ctx| s::no_precinct_enclosure(ctx.plan),
        shared: false,
        fixture: "hoshigaoka-fenced-precinct-red.svg",
        fix: "take the fence or wall off the precinct and the sanctuary: its arch and its wood mark it, however rich the parish",
        skipped: never,
    },
    Check {
        name: "hall_at_an_end",
        run: |ctx| s::hall_at_an_end(&ctx.svg, ctx.plan),
        shared: false,
        fixture: "hoshigaoka-hall-in-the-middle-red.svg",
        fix: "under one roof put the hall at one end of the building, on the approach, and the dwelling (kitchen and monk's rooms) at the other",
        skipped: never,
    },
];

/// The registered checks that apply to a sheet of `tier` (None: the shared layer only).
///
/// # Errors
/// The declaration cannot be read.
pub fn checks_for(tier: Option<&str>, tree: &Path) -> Result<Vec<&'static Check>, Error> {
    let mut out = Vec::new();
    for ch in &CHECKS {
        if ch.applies_to(tier, tree)? {
            out.push(ch);
        }
    }
    Ok(out)
}

/// Every applicable check with its findings, in registry order (an empty list = it passed); the first check that raises ends the run,
/// as the Python's did.
///
/// # Errors
/// The declaration cannot be read, or a check raised.
pub fn run_checks(
    ctx: &Context,
    tier: Option<&str>,
) -> Result<Vec<(&'static Check, Vec<String>)>, Error> {
    let mut out = Vec::new();
    for ch in checks_for(tier, ctx.tree)? {
        out.push((ch, (ch.run)(ctx)?));
    }
    Ok(out)
}
