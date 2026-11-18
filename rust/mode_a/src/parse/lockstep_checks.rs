//! THE CHECKS' LOCKSTEP (`ask:449-engine-order` condition 3, feature 449 T175): the Python audit's checks, registry, report and the engine
//! predicates they call, on the same sheets the parse's lockstep reads and in the same interpreter (`parse/lockstep.rs`), held equal to
//! this port's - every record each check function returns field by field, every check's findings or refusal under the sheet's tier, and
//! the whole report, so an edit of `pack_audit`'s Python (or of `compound_model`'s distances and `compound_parts`' predicates) that the
//! Rust did not follow fails there. A float is compared as its `repr`, bit for bit.
//!
//! What is read where (the Python half's cost kept down, observed 2026-11-17, method: each check timed over the pool and the red
//! fixtures, scratchpad `t175/a/probe`): a pool sheet and a check fixture print the whole report (every check of their tier) and run
//! every other check alone; a red fixture (`tests/fixtures/*-red.svg`, the checks' own) runs its own checks and every check but the
//! three that rasterize or cast shadows. The garden's sun is held by its verdicts - each half hour's lit-or-not, the hours, the
//! shaders - and its unshaded area, the one figure `geo` computes otherwise than GEOS, is measured beside them ([`sun_measure`]).
//!
//! Research:
//!     the checks' lockstep - NONE: the Python and the port compared, deciding nothing about a building

use std::path::Path;

use l7r_guard::shared::pyjson::py_float;
use serde_json::{json, Value};

use crate::audit::checks::{self as c, Gap};
use crate::audit::registry::{checks_for, Context, CHECKS};
use crate::audit::{
    labels as lb, mapmatch as mm, marks_drawn as md, onmap, palette as pl, program_rules as pr,
};
use crate::audit::{report as rp, roads as rd, shared as sh, sun, Sheet};
use crate::parse::{parse_svg, ParsedPlan, Rect};
use crate::py::uncaught;

/// The Python half: `checks_reading(path, text)`, defined for the parse lockstep's script, which calls it for every sheet but the parse's
/// own fixtures.
pub const PYTHON: &str = r#"
from l7r.diagram.tools.pack_audit import checks as C, registry as RG, report as RP, shared as SH, sun as SU, roads as RD
from l7r.diagram.tools.pack_audit import mapmatch as MM, onmap as OM, labels as LB, marks_drawn as MD, palette as PL, program_rules as PR
from l7r.diagram import compound_model as CM, compound_parts as CP
from l7r.diagram.buildings import types as BT
from shapely.ops import unary_union
FIXTURE_TIER = {"ochiba": "magistracies", "hayakawa": "magistracies", "ubame": "magistracies", "hoshigaoka": "country-shrines"}
HEAVY = {"garden_sun", "perimeter_hugging", "coverage_band"}
MAPS_RECORDING = (("hoshigaoka-shrine", "country-shrines"), ("ubame-magistracy", "magistracies"), ("ochiba-magistracy", "magistracies"),
                  ("nowhere-x", "magistracies"), ("ubame-x", "no-such-tier"), ("ubame-x", "country-shrines"),
                  ("hoshigaoka-x", "magistracies"))
SUN_FIXTURE = next(ch.fixture for ch in RG.CHECKS if ch.name == "garden_sun")
def sheet_tier(path):
    t = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(path))))
    return t if t in BT.tiers() else FIXTURE_TIER.get(os.path.basename(path).split("-")[0])
def quiet(fn):
    try:
        return fn()
    except Exception:
        return None
def sun_reading(plan, text):
    out = []
    for r, half in SU.gardens(plan, text):
        bed = SU._rect_poly(r)
        cs = SU.casters(plan, text, bed)
        steps, areas = [], []
        for k in range(int(24 / SU.STEP_H)):
            el, az = SU.sun_at(k * SU.STEP_H)
            if el < SU.MIN_SUN_DEG:
                continue
            shade = [SU.shadow(c, el, az) for c in cs if not (half and c.tree)]
            lit = bed.difference(unary_union(shade)).area if shade else bed.area
            need = SU.LIT_SHARE * bed.area
            steps.append([lit >= need, conv(need)])
            areas.append(conv(lit))
        out.append({"bed": conv(r), "half": half, "steps": steps, "areas": areas, "shaders": SU.shaders(bed, cs, half),
                    "casters": [[c.what, conv(c.height_ft), c.tree, conv(list(c.shape.exterior.coords))] for c in cs]})
    return out
def records(plan, text, btype, on_map, base):
    roads = quiet(lambda: RD.roads(text))
    ends = []
    for road in roads or []:
        others = [o for o in roads if o is not road]
        for end in (road.pts[0], road.pts[-1]):
            ends.append([conv(RD.gates_met(end, road.half, plan)), attempt(lambda: RD.end_meets(end, road, others, text, plan))])
    kinds = sorted(set(plan.label_kinds.values()))
    return {
        "adrift": attempt(lambda: C.fire_water_adrift(plan)), "off_door": attempt(lambda: C.tubs_off_their_doors(plan)),
        "in_building": attempt(lambda: C.tubs_in_buildings(plan)), "on_well": attempt(lambda: C.tubs_on_wells(plan)),
        "occluded": attempt(lambda: C.occluded_foreground(plan)), "openings": attempt(lambda: C.wall_openings(plan)),
        "passage": attempt(lambda: C.passage_blockers(plan)), "board": attempt(lambda: C.notice_board_adrift(plan)),
        "floating": attempt(lambda: C.floating_doors(plan)), "on_walls": attempt(lambda: C.structures_on_walls(plan)),
        "gaps": attempt(lambda: [[g, C.gap_tag(g)] for g in C.aligned_gaps(plan)]),
        "gate_ft": attempt(lambda: C.main_gate_passage_ft(plan)), "gate_mid": attempt(lambda: C._main_gate_passage(plan)),
        "doors_of": attempt(lambda: [C.doors_of(plan, b) for b in plan.buildings]),
        "doors_off": attempt(lambda: MD.doors_off_their_walls(plan)), "steps": attempt(lambda: MD.steps_past_revetment(text)),
        "torii": attempt(lambda: MD.arches_not_in_plan(text)), "roads": conv(roads), "ends": ends,
        "frame": attempt(lambda: RD._frame(text)), "ink": attempt(lambda: SH.ink_bounds(text, plan)),
        "divider_gates": attempt(lambda: SH.divider_gates_ft(plan)),
        "components": attempt(lambda: [[m.pos for m in comp] for comp in PR.components(PR.structure_marks(text))]),
        "entrances": attempt(lambda: PR.entrances(text, plan)),
        "main_fill": attempt(lambda: [[k, PL.main_fill(k, text)] for k in PL.ROLES]),
        "footprints": attempt(lambda: [[k, LB.footprint(plan, k)] for k in kinds]),
        "kinds_of": attempt(lambda: [[i.id, LB.kinds_of(i, plan)] for i in btype.required] if btype else None),
        "site": attempt(lambda: MM.site_classes(plan, text, on_map)), "ways": attempt(lambda: MM.sheet_ways(text)),
        "subject": attempt(lambda: MM.subject_box(plan, on_map.sheet_id) if on_map else None),
    }
def sun_wanted(path):
    # the sun's shadows only where a red fixture is the garden's own: the others are the pool's sheets cut, their beds the same; read
    # as a task of its own (`one`), the longest, so a sheet's report and its sun run side by side
    base = os.path.basename(path)
    return not base.startswith("fixture-") and (not base.endswith("-red.svg") or base == SUN_FIXTURE)
def checks_reading(path, text):
    base = os.path.basename(path)
    out = {"form": attempt(lambda: RP.read_form(path)), "on_map": attempt(lambda: OM.read_on_map(path))}
    try:
        plan = P.parse_svg(text)
    except Exception:
        return out
    tier = sheet_tier(path)
    btype = BT.by_tier(tier) if tier else None
    form, on_map = quiet(lambda: RP.read_form(path)), quiet(lambda: OM.read_on_map(path))
    ctx = RG.Context(plan, text, btype, form, on_map)
    red = base.endswith("-red.svg")
    applies = [ch.name for ch in RG.checks_for(tier)]
    run = [ch for ch in RG.CHECKS if ((ch.fixture == base or ch.name not in HEAVY) if red else ch.name not in applies)]
    out.update(tier=tier, applies=applies, checks=[[ch.name, attempt(lambda: ch.run(ctx))] for ch in run],
               records=records(plan, text, btype, on_map, base))
    if not red:
        out["report"] = attempt(lambda: RP.format_report(plan, text=text, tier=tier, btype=btype, form=form, on_map=on_map))
    return out
def labels_reading(path):
    # a declaration's labeled items, which no declared tier carries since feature 262, on a sheet that labels and tags them
    with open(path, encoding="utf-8") as fh:
        given = json.load(fh)
    plan = P.parse_svg(given["svg"])
    out = []
    for t in BT.parse_types(given["types"]):
        for form in (None, "small"):
            for site in (None, {}, {"water": True}):
                out.append(attempt(lambda: LB.check_program(plan, t, form, site)))
            out.append(attempt(lambda: LB.check_bands(plan, t, form)))
        out.append([[i.id, LB.kinds_of(i, plan), [conv(lb) for lb in LB.matches(i, plan.labels)] if i.label else None]
                    for i in t.required])
    return out
def main_reading(argvs):
    # the command as `__main__` runs it: what it printed, what it returned, and the exception that ended it
    import contextlib, io
    out = []
    for argv in argvs:
        buf, err = io.StringIO(), io.StringIO()
        code, exc = None, None
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                code = RP.main(argv)
        except Exception as e:
            exc = traceback.format_exception_only(type(e), e)[-1].rstrip("\n")
        out.append([buf.getvalue(), err.getvalue(), code, exc])
    return out
def check_defaults():
    # every default argument of the checks, which the port holds as constants, and the constants themselves
    import inspect
    out = {}
    for mod in (C, SH, SU, RD, MM, MD, PL, PR, RP, LB, OM):
        for name, fn in vars(mod).items():
            if inspect.isfunction(fn) and fn.__module__ == mod.__name__:
                for p in inspect.signature(fn).parameters.values():
                    if p.default is not inspect.Parameter.empty:
                        out[f"{mod.__name__.rsplit('.', 1)[1]}.{name}.{p.name}"] = conv(p.default)
    for mod, names in ((CM, "TUB_MAX_GAP_FT TUB_DOOR_MAX_FT NOTICE_BOARD_MAX_FT KINDS"),
                       (C, "TUB_WELL_MIN_PX TUB_BLDG_MIN_PX OCCLUSION_MIN_PX PASSAGE_DEPTH_PX PASSAGE_CLEAR_MIN_PX OPENING_MAX_PX "
                           "DOOR_FLUSH_TOL_PX DOOR_NEAR_PX WALL_OVERLAP_MIN_PX DOOR_ON_WALL_PX SHOE_STONE_ID DOORLESS_KINDS WALL_FACE_CLEAR_FT"),
                       (SH, "OVERLAP_SHARE COVERAGE_FLOOR COVERAGE_CEILING COVERAGE_TOL HUGGING_FLOOR CROP_MAX_MARGIN_PX CROP_TOL_PX GATE_MIN_FT "
                            "GATE_MAX_FT PARCHMENT_SHARE COVERAGE_FIX AXIS_TOL_FT EDGE_TOL_FT STALL_FT HALL_MIN_SPAN_FT "
                            "DUPLICATE_TREE_FRACTION APPROACH_FT CLEAR_FT SHRINE_TREE_FT"),
                       (SU, "LAT_DEG DECL_DEG STEP_H LIT_SHARE SUN_BED_H HALF_SHADE_BED_H BUILDING_FT WALL_FT TREE_FT SMALL_BUILDING_FT "
                            "SMALL_BUILDING_SQFT NOT_STANDING MIN_SUN_DEG MIN_BED_PX GARDEN_KIND"),
                       (RD, "ROAD_KINDS ARCH_KINDS DESTINATION_KINDS ROAD_GATE_TOL_FT"),
                       (MM, "MAP_GRAIN_PX SIZE_GRAIN_PX CLASSES POLYLINE_KEYS SHEET_WAY_KINDS SHEET_IDS MAP_TREES TIER_KEYS"),
                       (MD, "DOOR_WALL_TOL_PX"), (PL, "GRANARY_SLATS PRIVY WELL ROLES"),
                       (PR, "LODGING ENTRANCE_KINDS JOIN_PX PRIVY_FILL COURT_KINDS ATTACHED_PX PRIVY_MIN TUB_KINDS KITCHEN_TUBS HIERARCHY "
                            "VERANDA_FT VERANDA_TOL_PX"),
                       (OM, "GRAMMAR OPT_OUT")):
        for n in names.split():
            out[f"{mod.__name__.rsplit('.', 1)[1]}.{n}"] = conv(getattr(mod, n))
    # the skill root a path is read from: the tree the lockstep runs in, however it is spelled
    out["mapmatch.maps_recording.root"] = os.path.samefile(out["mapmatch.maps_recording.root"], sys.argv[1])
    out["maps_recording"] = [MM.maps_recording(s, t) for s, t in MAPS_RECORDING]
    out["registry"] = [[ch.name, ch.shared, ch.fixture, ch.fix, conv(ch.types)] for ch in RG.CHECKS]
    out["sun_at"] = [conv(SU.sun_at(k * SU.STEP_H)) for k in range(48)]
    # `x ** 0.5` is libm's `pow`, which a square root misses about once in a thousand (scratchpad t175/a/pow_half_probe.py)
    out["pow_half"] = [conv(x ** 0.5) for x in (885562.0, 7643.174758627603, 957249.393903807, 2291.0628339599, 0.7831880041381727,
                                                2639154.027777778, 2.0, 0.0)]
    out["predicates"] = [CP.tub_by_its_eaves((1.0, 4.5), (0.0, 0.0, 1.0, 1.0)), CP.tub_by_its_door((0.0, 0.0), [(10.5, 0.0)]),
                         CP.board_by_a_gate((40.0, 0.0, 41.0, 1.0), [(0.0, 0.0)]), conv(CP._gap((0.0, 0.0, 1.0, 1.0), (3.0, 4.0, 5.0, 5.0)))]
    return out
"#;

fn f(x: f64) -> Value {
    json!(format!("f:{}", py_float(x)))
}

fn opt_f(x: Option<f64>) -> Value {
    x.map_or(Value::Null, f)
}

fn pt(p: (f64, f64)) -> Value {
    json!([f(p.0), f(p.1)])
}

fn pts(ps: &[(f64, f64)]) -> Value {
    json!(ps.iter().map(|&p| pt(p)).collect::<Vec<_>>())
}

fn err(e: &l7r_gate_research::Error) -> Value {
    json!({"err": uncaught(e).trim_end()})
}

fn attempt<T>(r: Result<T, l7r_gate_research::Error>, show: impl FnOnce(T) -> Value) -> Value {
    match r {
        Ok(v) => json!({"ok": show(v)}),
        Err(e) => err(&e),
    }
}

fn ok(v: Value) -> Value {
    Value::Object([("ok".to_owned(), v)].into_iter().collect())
}

fn strings(v: &[String]) -> Value {
    json!(v)
}

fn rect(r: &Rect) -> Value {
    super::lockstep::rect(r)
}

fn gap(g: &Gap) -> Value {
    json!({"ft": f(g.ft), "orient": g.orient, "mx": f(g.mx), "my": f(g.my), "kura": g.kura})
}

fn opening(o: &c::WallOpening) -> Value {
    json!({"x": f(o.x), "y": f(o.y), "ft": f(o.ft), "horiz": o.horiz, "span1": f(o.span1), "span2": f(o.span2),
           "across1": f(o.across1), "across2": f(o.across2)})
}

fn on_map_value(m: &onmap::OnMap) -> Value {
    json!({"manifest": m.manifest, "key": m.key, "x": f(m.x), "y": f(m.y), "sheet_id": m.sheet_id})
}

fn list<T>(items: &[T], show: impl Fn(&T) -> Value) -> Value {
    json!(items.iter().map(show).collect::<Vec<_>>())
}

/// The garden's sun as the Python half reads it, without the unshaded areas (which [`sun_measure`] measures), the casters' rings bit for
/// bit.
fn sun_reading(plan: &ParsedPlan, svg: &Sheet) -> Result<Value, l7r_gate_research::Error> {
    let mut out = Vec::new();
    for (r, half) in sun::gardens(plan, svg)? {
        let bed = sun::Bed::new(r);
        let cs = sun::casters(plan, svg, &bed)?;
        let steps: Vec<Value> = sun::lit_areas(&bed, &cs, half)
            .iter()
            .map(|&(lit, need)| json!([lit >= need, f(need)]))
            .collect();
        let casters: Vec<Value> = cs
            .iter()
            .map(|c| json!([c.what, f(c.height_ft), c.tree, pts(&c.ring)]))
            .collect();
        out.push(json!({"bed": rect(r), "half": half, "steps": steps, "shaders": sun::shaders(&bed, &cs, half),
                        "casters": casters}));
    }
    Ok(json!(out))
}

/// Each garden's unshaded areas, half hour by half hour, in the order the Python half lists them (none where the sheet does not parse).
pub fn sun_areas(text: &str) -> Vec<f64> {
    let (Ok(plan), svg) = (parse_svg(text), Sheet::new(text)) else {
        return Vec::new();
    };
    let mut out = Vec::new();
    for (r, half) in sun::gardens(&plan, &svg).unwrap_or_default() {
        let bed = sun::Bed::new(r);
        let cs = sun::casters(&plan, &svg, &bed).unwrap_or_default();
        out.extend(
            sun::lit_areas(&bed, &cs, half)
                .into_iter()
                .map(|(lit, _)| lit),
        );
    }
    out
}

/// The area measure: the largest difference between `geo`'s unshaded area and GEOS's, absolute and as a share of the bed's threshold,
/// and the least distance of GEOS's area from its threshold - the verdict holds while the first stays under the second.
#[derive(Debug, Default)]
pub struct SunMeasure {
    pub steps: usize,
    pub max_abs: f64,
    pub max_rel: f64,
    pub min_margin: f64,
}

/// Folds one sheet's Python areas and thresholds (`steps`, `areas`) and this port's areas into the measure.
pub fn sun_measure(m: &mut SunMeasure, python: &Value, rust_areas: &[f64]) {
    let mut i = 0;
    for bed in python.as_array().into_iter().flatten() {
        let needs = bed["steps"].as_array().cloned().unwrap_or_default();
        for (area, step) in bed["areas"].as_array().into_iter().flatten().zip(needs) {
            let read = |v: &Value| {
                v.as_str()
                    .and_then(|s| s.strip_prefix("f:"))
                    .and_then(|s| s.parse::<f64>().ok())
                    .unwrap_or(f64::NAN)
            };
            let (geos, need) = (read(area), read(&step[1]));
            let ours = rust_areas.get(i).copied().unwrap_or(f64::NAN);
            let diff = (ours - geos).abs();
            m.steps += 1;
            m.max_abs = m.max_abs.max(diff);
            m.max_rel = m.max_rel.max(if need > 0.0 { diff / need } else { 0.0 });
            let margin = (geos - need).abs();
            m.min_margin = if m.steps == 1 {
                margin
            } else {
                m.min_margin.min(margin)
            };
            i += 1;
        }
    }
}

/// The garden check's own red fixture.
fn sun_fixture() -> &'static str {
    CHECKS
        .iter()
        .find(|ch| ch.name == "garden_sun")
        .map_or("", |ch| ch.fixture)
}

/// A record of a point, `x` and `y` first, as a dataclass with them first converts.
fn at(x: f64, y: f64, rest: Value) -> Value {
    let mut v = json!({"x": f(x), "y": f(y)});
    if let (Value::Object(m), Value::Object(l)) = (&mut v, rest) {
        m.extend(l);
    }
    v
}

/// The records of the checks' own functions (`checks.py`), as `records()` lists them.
fn check_records(plan: &ParsedPlan) -> Value {
    json!({
        "adrift": ok(list(&c::fire_water_adrift(plan), |t| at(t.x, t.y, json!({"gap_ft": f(t.gap_ft)})))),
        "off_door": ok(list(&c::tubs_off_their_doors(plan), |t| at(t.x, t.y, json!({"door_ft": f(t.door_ft)})))),
        "in_building": ok(list(&c::tubs_in_buildings(plan, c::TUB_BLDG_MIN_PX), |t| at(t.x, t.y, json!({"into_ft": f(t.into_ft)})))),
        "on_well": ok(list(&c::tubs_on_wells(plan, c::TUB_WELL_MIN_PX), |t| at(t.x, t.y, json!({})))),
        "occluded": ok(list(&c::occluded_foreground(plan, c::OCCLUSION_MIN_PX), |o| at(o.x, o.y, json!({"kind": o.kind})))),
        "openings": ok(list(&c::wall_openings(plan), opening)),
        "passage": ok(list(&c::passage_blockers(plan), |b| at(b.x, b.y, json!({"w_ft": f(b.w_ft), "h_ft": f(b.h_ft),
                                                                                "opening_ft": f(b.opening_ft)})))),
        "board": ok(list(&c::notice_board_adrift(plan), |b| at(b.x, b.y, json!({"gap_ft": f(b.gap_ft)})))),
        "floating": ok(list(&c::floating_doors(plan), |d| at(d.x, d.y, json!({"gap_ft": f(d.gap_ft)})))),
        "on_walls": ok(list(&c::structures_on_walls(plan, c::WALL_OVERLAP_MIN_PX), |w| at(w.x, w.y, json!({
            "w_ft": f(w.w_ft), "h_ft": f(w.h_ft), "into_ft": f(w.into_ft), "wall": w.wall})))),
        "gaps": ok(list(&c::aligned_gaps(plan), |g| json!([gap(g), c::gap_tag(g)]))),
        "gate_ft": ok(opt_f(c::main_gate_passage_ft(plan))),
        "gate_mid": ok(list(&c::main_gate_passage(plan), |&p| pt(p))),
        "doors_of": ok(list(&plan.buildings, |b| pts(&c::doors_of(plan, b)))),
        "doors_off": ok(list(&md::doors_off_their_walls(plan), |d| at(d.x, d.y, json!({"how": d.how})))),
    })
}

/// Each road's two ends: the gates each meets and what it meets, as `records()` lists them.
fn road_ends(plan: &ParsedPlan, svg: &Sheet, roads: &[rd::Road]) -> Vec<Value> {
    let mut ends = Vec::new();
    for (i, road) in roads.iter().enumerate() {
        let others: Vec<&rd::Road> = roads
            .iter()
            .enumerate()
            .filter(|(j, _)| *j != i)
            .map(|(_, o)| o)
            .collect();
        for end in [road.pts[0], road.pts[road.pts.len() - 1]] {
            let met: Vec<Value> = rd::gates_met(end, road.half(), plan)
                .into_iter()
                .map(f)
                .collect();
            ends.push(json!([
                met,
                attempt(rd::end_meets(end, road, &others, svg, plan), |m| json!(m))
            ]));
        }
    }
    ends
}

/// The records of the sheet's other modules, as `records()` lists them.
fn sheet_records(
    plan: &ParsedPlan,
    svg: &Sheet,
    btype: Option<&crate::types::BuildingType>,
    on_map: Option<&onmap::OnMap>,
    tree: &Path,
) -> Value {
    let roads = rd::roads(svg);
    let ends = roads
        .as_ref()
        .map(|rs| road_ends(plan, svg, rs))
        .unwrap_or_default();
    let mut kinds: Vec<&String> = plan.label_kinds.values().collect();
    kinds.sort();
    kinds.dedup();
    let bounds = |fr: Option<(f64, f64, f64, f64)>| {
        fr.map_or(Value::Null, |(a, b, c2, d)| {
            json!([f(a), f(b), f(c2), f(d)])
        })
    };
    json!({
        "steps": ok(list(&md::steps_past_revetment(svg.text), |s| at(s.x, s.y, json!({"past_ft": f(s.past_ft)})))),
        "torii": ok(json!(md::arches_not_in_plan(svg.text))),
        "roads": roads.as_ref().map_or(Value::Null, |rs| list(rs, |r| json!({"pts": pts(&r.pts), "width": f(r.width)}))),
        "ends": ends,
        "frame": attempt(rd::frame(svg.text), bounds),
        "ink": attempt(sh::ink_bounds(svg.text, plan, 0.0), bounds),
        "divider_gates": attempt(sh::divider_gates_ft(plan), |g| json!(g.into_iter().map(f).collect::<Vec<_>>())),
        "components": attempt(pr::structure_marks(svg), |ms| json!(pr::components(&ms, pr::JOIN_PX).iter()
            .map(|comp| comp.iter().map(|m| m.pos).collect::<Vec<_>>()).collect::<Vec<_>>())),
        "entrances": attempt(pr::entrances(svg, plan), |es| list(&es, super::lockstep::mark)),
        "main_fill": attempt(
            pl::roles().iter().map(|(k, _)| pl::main_fill(k, svg).map(|m| json!([k, m.map_or(Value::Null, super::lockstep::mark)])))
                .collect::<Result<Vec<_>, _>>(),
            |v| json!(v)),
        "footprints": ok(json!(kinds.iter().map(|k| json!([k, lb::footprint(plan, k).map_or(Value::Null, rect)])).collect::<Vec<_>>())),
        "kinds_of": ok(btype.map_or(Value::Null, |b| list(&b.required, |i| json!([i.id, lb::kinds_of(i, plan)])))),
        "site": attempt(mm::site_classes(plan, svg, on_map, tree), |s| s.map_or(Value::Null, |mut s| {
            s.sort();
            json!(s.into_iter().map(|(k, v)| json!([k, v])).collect::<Vec<_>>())
        })),
        "ways": attempt(mm::sheet_ways(svg), |ws| list(&ws, |w| pts(w))),
        "subject": ok(on_map.and_then(|m| mm::subject_box(plan, &m.sheet_id)).as_ref().map_or(Value::Null, rect)),
    })
}

/// Every record `records()` lists: the checks', the other modules', and the sun's where it is read.
fn records(
    plan: &ParsedPlan,
    svg: &Sheet,
    btype: Option<&crate::types::BuildingType>,
    on_map: Option<&onmap::OnMap>,
    tree: &Path,
    base: &str,
) -> Value {
    let mut out = check_records(plan);
    if let (Value::Object(out), Value::Object(more)) =
        (&mut out, sheet_records(plan, svg, btype, on_map, tree))
    {
        out.extend(more);
    }
    let wanted =
        !base.starts_with("fixture-") && (!base.ends_with("-red.svg") || base == sun_fixture());
    out["sun"] = if wanted {
        attempt(sun_reading(plan, svg), |v| v)
    } else {
        Value::Null
    };
    out
}

/// This port's reading of one sheet, as `checks_reading(path, text)` reads it; `tree` is the skill root.
pub fn reading(path: &Path, text: &str, tree: &Path) -> Value {
    let name = path.to_string_lossy();
    let base = path
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let form = rp::read_form(&name);
    let on_map = onmap::read_on_map(&name);
    let mut out = json!({
        "form": attempt(form.clone(), |v| json!(v)),
        "on_map": attempt(on_map.clone(), |m| m.as_ref().map_or(Value::Null, on_map_value)),
    });
    let Ok(plan) = parse_svg(text) else {
        return out;
    };
    let tier = sheet_tier(path, tree);
    let btype = tier
        .as_deref()
        .and_then(|t| crate::types::by_tier(t, tree).ok().flatten());
    let (form, on_map) = (form.ok().flatten(), on_map.ok().flatten());
    let ctx = Context::new(
        &plan,
        text,
        btype.as_ref(),
        form.as_deref(),
        on_map.as_ref(),
        tree,
    );
    let red = base.ends_with("-red.svg");
    let applies: Vec<&str> = checks_for(tier.as_deref(), tree)
        .unwrap_or_default()
        .iter()
        .map(|ch| ch.name)
        .collect();
    let heavy = ["garden_sun", "perimeter_hugging", "coverage_band"];
    let run = CHECKS.iter().filter(|ch| {
        if red {
            ch.fixture == base || !heavy.contains(&ch.name)
        } else {
            !applies.contains(&ch.name)
        }
    });
    let checks: Vec<Value> = run
        .map(|ch| json!([ch.name, attempt((ch.run)(&ctx), |v| strings(&v))]))
        .collect();
    out["tier"] = json!(tier);
    out["applies"] = json!(applies);
    out["checks"] = json!(checks);
    out["records"] = records(
        &plan,
        &ctx.svg,
        btype.as_ref(),
        on_map.as_ref(),
        tree,
        &base,
    );
    if !red {
        out["report"] = attempt(
            rp::format_report(
                &plan,
                crate::grids::CELL,
                text,
                tier.as_deref(),
                btype.as_ref(),
                form.as_deref(),
                on_map.as_ref(),
                tree,
            ),
            |r| json!(r),
        );
    }
    out
}

/// The fixtures' tiers by the sheet they were cut from (the registry's fixture test's, `tests/tools/test_registry.py` before feature 449
/// FR-001b deleted it).
const FIXTURE_TIER: [(&str, &str); 4] = [
    ("ochiba", "magistracies"),
    ("hayakawa", "magistracies"),
    ("ubame", "magistracies"),
    ("hoshigaoka", "country-shrines"),
];

fn sheet_tier(path: &Path, tree: &Path) -> Option<String> {
    // every sheet the lockstep names is absolute, and its tier is the name two folders up whether or not `..` is folded first
    let t = path
        .parent()
        .and_then(Path::parent)
        .and_then(Path::file_name)
        .map(|n| n.to_string_lossy().into_owned());
    let declared = crate::types::tiers(tree).unwrap_or_default();
    if let Some(t) = t.filter(|t| declared.contains(t)) {
        return Some(t);
    }
    let base = path
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let place = base.split('-').next().unwrap_or_default();
    FIXTURE_TIER
        .iter()
        .find(|(k, _)| *k == place)
        .map(|(_, t)| (*t).to_owned())
}

/// The labeled items' declaration and sheet `labels_reading(path)` reads: two tiers, one ending on a kind no registry knows.
pub const LABELS: &str = r##"{"types": [
 {"tier": "labeled", "title": "L", "program": "P", "hand_drawn": true, "checks": [], "required": [
  {"id": "kitchen", "label": "kitch\\w+", "band_ft": {"w": [5, 10], "h": [5, 10]}, "class": "guess", "why": "a test's"},
  {"id": "hall", "label": "great\\s+hall", "band_ft": {"area": [10, 20]}, "class": "accurate", "why": "a test's",
   "forms": {"small": null}},
  {"id": "pond", "label": "pond", "band_ft": {}, "class": "convention", "why": "a test's", "site": "water"},
  {"id": "well", "label": "well", "band_ft": {}, "class": "convention", "why": "a test's", "site": "water_point"},
  {"id": "gate", "label": "gate", "band_ft": {}, "class": "guess", "why": "a test's", "optional": true},
  {"id": "porch", "label": "porch", "band_ft": {"w": [1, 2]}, "class": "guess", "why": "a test's"},
  {"id": "shed", "label": "shed", "band_ft": {"w": [1, 2], "h": [1, 2]}, "class": "guess", "why": "a test's"},
  {"id": "byre", "label": "byre", "band_ft": {}, "class": "guess", "why": "a test's"},
  {"id": "hearth", "kind": "hearth", "band_ft": {}}]},
 {"tier": "unknown", "title": "U", "program": "P", "hand_drawn": true, "checks": [], "required": [
  {"id": "store", "kind": "no such kind", "band_ft": {"w": [1, 2], "h": [1, 2]}}]}],
 "svg": "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"300\" height=\"200\" fill=\"url(#court-earth)\"/><g data-kind=\"kitchen\"><rect x=\"10\" y=\"10\" width=\"60\" height=\"45\" fill=\"#C9A57A\"/><text x=\"20\" y=\"30\">Kitchen  yard</text></g><g data-kind=\"hall\"><rect x=\"100\" y=\"10\" width=\"90\" height=\"60\" fill=\"#DDB87A\"/><text x=\"110\" y=\"30\">GREAT   Hall</text></g><g data-kind=\"porch\"><rect x=\"100\" y=\"100\" width=\"9\" height=\"9\" fill=\"#DDB87A\"/><text x=\"100\" y=\"100\">porch</text></g><text x=\"200\" y=\"150\">shed</text><g data-kind=\"ground\"><text x=\"10\" y=\"180\">byre</text></g><rect id=\"gate\" x=\"1\" y=\"1\" width=\"2\" height=\"2\" fill=\"#000\"/><g data-kind=\"no such kind\"><rect x=\"200\" y=\"100\" width=\"30\" height=\"30\" fill=\"#C9A57A\"/></g><text x=\"10\" y=\"150\">Pond</text></svg>"
}"##;

/// This port's reading of [`LABELS`], as `labels_reading(path)` reads it.
pub fn labels_reading(tree: &Path) -> Value {
    let given: Value = serde_json::from_str(LABELS).unwrap();
    let plan = parse_svg(given["svg"].as_str().unwrap()).unwrap();
    let mut kinds = crate::types::Kinds::new(tree);
    let mut out = Vec::new();
    for t in crate::types::parse_types(&given["types"]).unwrap() {
        for form in [None, Some("small")] {
            let water = [("water".to_owned(), true)];
            for site in [None, Some(&[][..]), Some(&water[..])] {
                out.push(ok(json!(lb::check_program(&plan, &t, form, site))));
            }
            out.push(attempt(lb::check_bands(&plan, &t, form, &mut kinds), |v| {
                json!(v)
            }));
        }
        out.push(list(&t.required, |i| {
            let found = i
                .label
                .as_ref()
                .map(|_| list(&lb::matches(i, &plan.labels), |l| super::lockstep::label(l)));
            json!([i.id, lb::kinds_of(i, &plan), found])
        }));
    }
    json!(out)
}

/// This port's run of the command for each argument list, as `main_reading(argvs)` reads it.
pub fn main_reading(runs: &Value, tree: &Path) -> Value {
    let mut out = Vec::new();
    for given in runs.as_array().into_iter().flatten() {
        let args: Vec<String> = given
            .as_array()
            .into_iter()
            .flatten()
            .map(|a| a.as_str().unwrap_or_default().to_owned())
            .collect();
        let reply = rp::main(&args, tree);
        // the Python's `main` returned its code, or raised: the traceback's last line is what the port writes to stderr
        let (code, exc) = if reply.code == 1 {
            (Value::Null, json!(reply.stderr.trim_end()))
        } else {
            (json!(reply.code), Value::Null)
        };
        let err = if reply.code == 2 {
            reply.stderr.clone()
        } else {
            String::new()
        };
        out.push(json!([reply.stdout, err, code, exc]));
    }
    json!(out)
}

/// The constants and the default arguments, named as `check_defaults()` names them.
#[expect(
    clippy::too_many_lines,
    reason = "one key a constant, every constant the Python half lists"
)]
pub fn defaults(tree: &Path) -> Value {
    use crate::compound::{KINDS, NOTICE_BOARD_MAX_FT, TUB_DOOR_MAX_FT, TUB_MAX_GAP_FT};
    let fs = |v: &[&str]| json!(v);
    let sorted = |v: &[&str]| {
        let mut v = v.to_vec();
        v.sort_unstable();
        json!(v)
    };
    let pair = |p: (f64, f64)| json!([f(p.0), f(p.1)]);
    let mut kinds: Vec<Value> = KINDS.iter().map(|(k, (a, b))| json!([k, [a, b]])).collect();
    kinds.sort_by_key(|v| v[0].as_str().unwrap_or_default().to_owned());
    let mut roles: Vec<Value> = pl::roles()
        .iter()
        .map(|(k, v)| json!([k, sorted(v)]))
        .collect();
    roles.sort_by_key(|v| v[0].as_str().unwrap_or_default().to_owned());
    let mut classes: Vec<Value> = mm::CLASSES.iter().map(|(k, v)| json!([k, v])).collect();
    classes.sort_by_key(|v| v[0].as_str().unwrap_or_default().to_owned());
    let mut ids: Vec<Value> = mm::SHEET_IDS.iter().map(|(k, v)| json!([k, v])).collect();
    ids.sort_by_key(|v| v[0].as_str().unwrap_or_default().to_owned());
    let types = crate::types::load_types(tree).unwrap_or_default();
    let mut tier_keys: Vec<Value> = types.iter().map(|t| json!([t.tier, t.map_keys])).collect();
    tier_keys.sort_by_key(|v| v[0].as_str().unwrap_or_default().to_owned());
    let registry: Vec<Value> = CHECKS
        .iter()
        .map(|ch| {
            let types = ch.types(tree).ok().flatten().map(|mut t| {
                t.sort();
                json!(t)
            });
            json!([ch.name, ch.shared, ch.fixture, ch.fix, types])
        })
        .collect();
    let hierarchy: Vec<Value> = pr::HIERARCHY.iter().map(|(a, b)| json!([a, b])).collect();
    // in parts: one `json!` of every key passes the macro's recursion limit
    let mut out = serde_json::Map::new();
    if let Value::Object(part) = json!({
        "compound_model.TUB_MAX_GAP_FT": f(TUB_MAX_GAP_FT), "compound_model.TUB_DOOR_MAX_FT": f(TUB_DOOR_MAX_FT),
        "compound_model.NOTICE_BOARD_MAX_FT": f(NOTICE_BOARD_MAX_FT), "compound_model.KINDS": kinds,
        "checks.TUB_WELL_MIN_PX": f(c::TUB_WELL_MIN_PX), "checks.TUB_BLDG_MIN_PX": f(c::TUB_BLDG_MIN_PX),
        "checks.OCCLUSION_MIN_PX": f(c::OCCLUSION_MIN_PX), "checks.PASSAGE_DEPTH_PX": f(c::PASSAGE_DEPTH_PX),
        "checks.PASSAGE_CLEAR_MIN_PX": f(c::PASSAGE_CLEAR_MIN_PX), "checks.OPENING_MAX_PX": f(c::OPENING_MAX_PX),
        "checks.DOOR_FLUSH_TOL_PX": f(c::DOOR_FLUSH_TOL_PX), "checks.DOOR_NEAR_PX": f(c::DOOR_NEAR_PX),
        "checks.WALL_OVERLAP_MIN_PX": f(c::WALL_OVERLAP_MIN_PX), "checks.DOOR_ON_WALL_PX": f(c::DOOR_ON_WALL_PX),
        "checks.SHOE_STONE_ID": c::SHOE_STONE_ID, "checks.DOORLESS_KINDS": sorted(&c::DOORLESS_KINDS)
    }) {
        out.extend(part);
    }
    if let Value::Object(part) = json!({
        "checks.WALL_FACE_CLEAR_FT": f(c::WALL_FACE_CLEAR_FT),
        "checks.tubs_in_buildings.min_px": f(c::TUB_BLDG_MIN_PX), "checks.tubs_on_wells.min_px": f(c::TUB_WELL_MIN_PX),
        "checks.occluded_foreground.min_px": f(c::OCCLUSION_MIN_PX), "checks.structures_on_walls.min_px": f(c::WALL_OVERLAP_MIN_PX),
        "shared.OVERLAP_SHARE": f(sh::OVERLAP_SHARE), "shared.COVERAGE_FLOOR": f(sh::COVERAGE_FLOOR),
        "shared.COVERAGE_CEILING": f(sh::COVERAGE_CEILING), "shared.COVERAGE_TOL": f(sh::COVERAGE_TOL),
        "shared.HUGGING_FLOOR": f(sh::HUGGING_FLOOR), "shared.CROP_MAX_MARGIN_PX": f(sh::CROP_MAX_MARGIN_PX),
        "shared.CROP_TOL_PX": f(sh::CROP_TOL_PX), "shared.GATE_MIN_FT": f(sh::GATE_MIN_FT), "shared.GATE_MAX_FT": f(sh::GATE_MAX_FT),
        "shared.PARCHMENT_SHARE": f(sh::PARCHMENT_SHARE), "shared.COVERAGE_FIX": sh::COVERAGE_FIX
    }) {
        out.extend(part);
    }
    if let Value::Object(part) = json!({
        "shared.AXIS_TOL_FT": f(sh::AXIS_TOL_FT), "shared.EDGE_TOL_FT": f(sh::EDGE_TOL_FT), "shared.STALL_FT": pair(sh::STALL_FT),
        "shared.HALL_MIN_SPAN_FT": f(sh::HALL_MIN_SPAN_FT), "shared.DUPLICATE_TREE_FRACTION": f(sh::DUPLICATE_TREE_FRACTION),
        "shared.APPROACH_FT": f(sh::APPROACH_FT), "shared.CLEAR_FT": f(sh::CLEAR_FT), "shared.SHRINE_TREE_FT": f(sh::SHRINE_TREE_FT),
        "shared.structures_overlap.share": f(sh::OVERLAP_SHARE), "shared.viewbox_cropped.max_margin_px": f(sh::CROP_MAX_MARGIN_PX),
        "shared.viewbox_cropped.tol_px": f(sh::CROP_TOL_PX), "shared.coverage_band.floor": f(sh::COVERAGE_FLOOR),
        "shared.coverage_band.ceiling": f(sh::COVERAGE_CEILING), "shared.coverage_band.tol": f(sh::COVERAGE_TOL),
        "shared.perimeter_hugging.floor": f(sh::HUGGING_FLOOR), "shared.gate_widths.lo_ft": f(sh::GATE_MIN_FT),
        "shared.gate_widths.hi_ft": f(sh::GATE_MAX_FT), "shared.sanctuary_on_axis.tol_ft": f(sh::AXIS_TOL_FT)
    }) {
        out.extend(part);
    }
    if let Value::Object(part) = json!({
        "shared.arch_on_approach.edge_tol_ft": f(sh::EDGE_TOL_FT), "shared.trees_overlap.tol": f(c::WALL_OVERLAP_MIN_PX),
        "shared.ink_bounds.canvas_area": f(0.0),
        "sun.LAT_DEG": f(sun::LAT_DEG), "sun.DECL_DEG": f(sun::DECL_DEG), "sun.STEP_H": f(sun::STEP_H), "sun.LIT_SHARE": f(sun::LIT_SHARE),
        "sun.SUN_BED_H": f(sun::SUN_BED_H), "sun.HALF_SHADE_BED_H": f(sun::HALF_SHADE_BED_H), "sun.BUILDING_FT": f(sun::BUILDING_FT),
        "sun.WALL_FT": f(sun::WALL_FT), "sun.TREE_FT": f(sun::TREE_FT), "sun.SMALL_BUILDING_FT": f(sun::SMALL_BUILDING_FT),
        "sun.SMALL_BUILDING_SQFT": f(sun::SMALL_BUILDING_SQFT), "sun.NOT_STANDING": sorted(&sun::NOT_STANDING),
        "sun.MIN_SUN_DEG": f(sun::MIN_SUN_DEG), "sun.MIN_BED_PX": f(sun::MIN_BED_PX), "sun.GARDEN_KIND": sun::GARDEN_KIND,
        "sun.sun_at.lat_deg": f(sun::LAT_DEG), "sun.sun_at.decl_deg": f(sun::DECL_DEG), "sun.lit_hours.half_shade": false
    }) {
        out.extend(part);
    }
    if let Value::Object(part) = json!({
        "sun.shaders.half_shade": false,
        "roads.ROAD_KINDS": sorted(&rd::ROAD_KINDS), "roads.ARCH_KINDS": sorted(&rd::ARCH_KINDS),
        "roads.DESTINATION_KINDS": sorted(&rd::DESTINATION_KINDS), "roads.ROAD_GATE_TOL_FT": f(rd::ROAD_GATE_TOL_FT),
        "roads.gate_feeds_its_road.tol_ft": f(rd::ROAD_GATE_TOL_FT),
        "mapmatch.MAP_GRAIN_PX": f(mm::MAP_GRAIN_PX), "mapmatch.SIZE_GRAIN_PX": f(mm::SIZE_GRAIN_PX), "mapmatch.CLASSES": classes,
        "mapmatch.POLYLINE_KEYS": sorted(&mm::POLYLINE_KEYS), "mapmatch.SHEET_WAY_KINDS": sorted(&mm::SHEET_WAY_KINDS),
        "mapmatch.SHEET_IDS": ids, "mapmatch.MAP_TREES": fs(&mm::MAP_TREES), "mapmatch.TIER_KEYS": tier_keys,
        "mapmatch.matches_map.grain": f(mm::MAP_GRAIN_PX), "mapmatch.maps_recording.root": true
    }) {
        out.extend(part);
    }
    if let Value::Object(part) = json!({
        "marks_drawn.DOOR_WALL_TOL_PX": f(md::DOOR_WALL_TOL_PX),
        "palette.GRANARY_SLATS": pl::GRANARY_SLATS, "palette.PRIVY": pl::PRIVY, "palette.WELL": pl::WELL, "palette.ROLES": roles,
        "palette.palette_roles.roles": roles_value(),
        "program_rules.LODGING": sorted(&pr::LODGING), "program_rules.ENTRANCE_KINDS": sorted(&pr::ENTRANCE_KINDS),
        "program_rules.JOIN_PX": f(pr::JOIN_PX), "program_rules.PRIVY_FILL": pr::PRIVY_FILL, "program_rules.COURT_KINDS": fs(&pr::COURT_KINDS),
        "program_rules.ATTACHED_PX": f(pr::ATTACHED_PX), "program_rules.PRIVY_MIN": pr::PRIVY_MIN, "program_rules.TUB_KINDS": fs(&pr::TUB_KINDS),
        "program_rules.KITCHEN_TUBS": pr::KITCHEN_TUBS, "program_rules.HIERARCHY": hierarchy.clone(),
        "program_rules.VERANDA_FT": pair(pr::VERANDA_FT), "program_rules.VERANDA_TOL_PX": f(pr::VERANDA_TOL_PX)
    }) {
        out.extend(part);
    }
    if let Value::Object(part) = json!({
        "program_rules.components.join_px": f(pr::JOIN_PX), "program_rules.lodging_entrances.tol": f(c::DOOR_FLUSH_TOL_PX),
        "program_rules.privies_by_zone.minimum": pr::PRIVY_MIN, "program_rules.size_hierarchy.pairs": hierarchy,
        "program_rules.veranda_depths.band": pair(pr::VERANDA_FT),
        "report.format_report.cell": crate::grids::CELL, "report.format_report.text": "", "report.format_report.tier": null,
        "report.format_report.btype": null, "report.format_report.form": null, "report.format_report.on_map": null,
        "report.main.argv": null, "labels.check_program.site": null,
        "onmap.GRAMMAR": onmap::GRAMMAR, "onmap.OPT_OUT": onmap::OPT_OUT,
        "registry": registry, "maps_recording": maps_recording(tree)
    }) {
        out.extend(part);
    }
    if let Value::Object(part) = json!({
        "sun_at": (0..48).map(|k| { let (a, b) = sun::sun_at(f64::from(k) * sun::STEP_H, sun::LAT_DEG, sun::DECL_DEG); json!([f(a), f(b)]) })
            .collect::<Vec<_>>(),
        "pow_half": POW_HALF.map(|x| f(crate::py::pow_half(x))),
        "predicates": [json!(crate::compound::tub_by_its_eaves((1.0, 4.5), (0.0, 0.0, 1.0, 1.0))),
                       json!(crate::compound::tub_by_its_door((0.0, 0.0), &[(10.5, 0.0)])),
                       json!(crate::compound::board_by_a_gate((40.0, 0.0, 41.0, 1.0), &[(0.0, 0.0)])),
                       f(crate::compound::gap((0.0, 0.0, 1.0, 1.0), (3.0, 4.0, 5.0, 5.0)))]
    }) {
        out.extend(part);
    }
    Value::Object(out)
}

/// Floats whose `x ** 0.5` differs from their square root in `CPython` 3.14.4 (observed 2026-11-17, scratchpad `t175/a/pow_half_probe.py`), and two that do not.
const POW_HALF: [f64; 8] = [
    885_562.0,
    7_643.174_758_627_603,
    957_249.393_903_807,
    2_291.062_833_959_9,
    0.783_188_004_138_172_7,
    2_639_154.027_777_778,
    2.0,
    0.0,
];

/// The manifests that record a subject at each sheet's place, as `MAPS_RECORDING` asks.
fn maps_recording(tree: &Path) -> Value {
    let asked: [(&str, &str); 7] = [
        ("hoshigaoka-shrine", "country-shrines"),
        ("ubame-magistracy", "magistracies"),
        ("ochiba-magistracy", "magistracies"),
        ("nowhere-x", "magistracies"),
        ("ubame-x", "no-such-tier"),
        ("ubame-x", "country-shrines"),
        ("hoshigaoka-x", "magistracies"),
    ];
    json!(asked.map(|(stem, tier)| json!(mm::maps_recording(stem, tier, tree).unwrap())))
}

/// `palette_roles`' default argument: the table itself, conv'd as a dict of sets.
fn roles_value() -> Value {
    let mut roles: Vec<Value> = pl::roles()
        .iter()
        .map(|(k, v)| {
            let mut v = v.clone();
            v.sort_unstable();
            json!([k, v])
        })
        .collect();
    roles.sort_by_key(|v| v[0].as_str().unwrap_or_default().to_owned());
    json!(roles)
}
