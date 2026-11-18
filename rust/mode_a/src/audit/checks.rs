//! The audit's geometric checks (feature 449 T175, `pack_audit/checks.py` whole): one function per question asked of a parsed plan,
//! each with its own result record - the fire-water tubs ([`fire_water_adrift`], [`tubs_off_their_doors`], [`tubs_in_buildings`],
//! [`tubs_on_wells`]), a buried foreground ([`occluded_foreground`]), the notice board ([`notice_board_adrift`]) and the doors
//! ([`floating_doors`]); the wall's openings, its passages, a structure on its ink and the aligned gaps are [`walls`]'.
//!
//! The tub's and the board's rules are the engine's (`crate::compound`): the draft seats by the same predicates, so a generated sheet
//! cannot seat what this audit would flag (feature 287, homes H29b).
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3): `checks.py` stays for the generators' Python until step 3; an edit of it makes the same
//! change here in the same commit, and `parse/lockstep_checks.rs` holds every record of every function equal on every sheet it reads.
//!
//! Research:
//!     the audit's checks - NONE: result records, lookups, geometry and checks applying thresholds whose claims stand on each; a check that decides a rule of its own carries its own claim

use crate::compound::{board_by_a_gate, tub_by_its_door, tub_by_its_eaves, FtBox};
use crate::grids::FTPX;
use crate::parse::{ParsedPlan, Rect};
use crate::py::{hypot, max, min};

pub mod walls;

pub use walls::{
    aligned_gaps, gap_tag, passage_blockers, structures_on_walls, wall_openings, Gap,
    PassageBlocker, StructureOnWall, WallOpening, OPENING_MAX_PX, PASSAGE_CLEAR_MIN_PX,
    PASSAGE_DEPTH_PX, WALL_FACE_CLEAR_FT, WALL_OVERLAP_MIN_PX,
};

/// A fire-water tub overlapping a well glyph by more than this sits ON it.
///
/// Research:
///     tub-on-well overlap - NONE: a fire-water tub overlapping a well glyph by more than 1 px sits on it, an audit pixel tolerance.
pub const TUB_WELL_MIN_PX: f64 = 1.0;
/// ...and reaching this far past a building's edge, it is drawn INTO the building.
///
/// Research:
///     tub-in-building overlap - NONE: a tub reaching 0.5 px past a building's edge is drawn into it, an audit pixel tolerance.
pub const TUB_BLDG_MIN_PX: f64 = 0.5;
/// A later feature must cover at least this much of a foreground item to count.
///
/// Research:
///     occlusion size - NONE: a later feature must cover 3 px of a foreground item to count as occluding it, an audit pixel tolerance.
pub const OCCLUSION_MIN_PX: f64 = 3.0;
/// A door within this of a building edge reads as ON the wall.
///
/// Research:
///     door flush tolerance - NONE: a door within 1.5 px of a building edge reads as on the wall, an audit pixel tolerance.
pub const DOOR_FLUSH_TOL_PX: f64 = 1.5;
/// A door candidate this close to an edge is TRYING to be in the wall (vs a deep interior marker).
///
/// Research:
///     door near-edge reach - NONE: a door candidate within 12 px of an edge is trying to be in the wall, an audit pixel tolerance.
pub const DOOR_NEAR_PX: f64 = 12.0;
/// A door glyph is drawn inside its wall's line or just outside it - a step or a porch board (Hayakawa's kitchen door stands 6 px out,
/// its guest house's entrance 8 px: plan review of wave 106).
pub const DOOR_ON_WALL_PX: f64 = 4.0 * FTPX;
/// The reception's way in: a stone the sheet DECLARES (`id="shoe-stone"`) is that building's entrance (R07, research 0104, wave 106).
pub const SHOE_STONE_ID: &str = "shoe-stone";
/// A bath is entered from the house it abuts (no outside door): its tub stands on its yard side, judged by no door.
///
/// Research:
///     a bath's tub judged by no door - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html, research/questions/0105-baths-furo.drawing.html: the bath our plans attach to the kitchen is entered from the house, so its fire-water tub stands on its yard side and is not held to stand beside a door.
pub const DOORLESS_KINDS: [&str; 1] = ["bath"];

/// A fire-water tub sitting too far from any building to be gutter-fed: its center (px) and its distance to the nearest building (ft).
#[derive(Debug, Clone, PartialEq)]
pub struct TubAdrift {
    pub x: f64,
    pub y: f64,
    pub gap_ft: f64,
}

/// A fire-water tub at its building's eaves but away from every door of it; `door_ft` infinite where none draws a door.
#[derive(Debug, Clone, PartialEq)]
pub struct TubOffItsDoor {
    pub x: f64,
    pub y: f64,
    pub door_ft: f64,
}

/// A fire-water tub whose glyph reaches `into_ft` into a building instead of standing clear of it.
#[derive(Debug, Clone, PartialEq)]
pub struct TubInBuilding {
    pub x: f64,
    pub y: f64,
    pub into_ft: f64,
}

/// A fire-water tub glyph overlapping a well glyph.
#[derive(Debug, Clone, PartialEq)]
pub struct TubOnWell {
    pub x: f64,
    pub y: f64,
}

/// A foreground item painted over by anything drawn later: `kind` is "tub", "well" or "feature".
#[derive(Debug, Clone, PartialEq)]
pub struct Occluded {
    pub kind: &'static str,
    pub x: f64,
    pub y: f64,
}

/// A notice board too far from any gate opening to be seen by passers-through.
#[derive(Debug, Clone, PartialEq)]
pub struct MisplacedBoard {
    pub x: f64,
    pub y: f64,
    pub gap_ft: f64,
}

/// A door glyph floating INSIDE a building, `gap_ft` from the wall it should sit on.
#[derive(Debug, Clone, PartialEq)]
pub struct FloatingDoor {
    pub x: f64,
    pub y: f64,
    pub gap_ft: f64,
}

/// Python's `max(a, b, c)`: the first strictly greater kept.
fn max3(a: f64, b: f64, c: f64) -> f64 {
    max(max(a, b), c)
}

/// The first value `pick` keeps against each later one, `default` where there is none: the one loop under Python's `min()` and `max()`
/// (non-generic, so every caller's shape of list runs the same lines, feature 449 T175).
fn fold(values: &[f64], default: f64, pick: fn(f64, f64) -> f64) -> f64 {
    let Some((&first, rest)) = values.split_first() else {
        return default;
    };
    rest.iter().fold(first, |m, &x| pick(m, x))
}

/// Python's `min()` of what is given, `default` where nothing is.
pub(crate) fn min_of(values: impl IntoIterator<Item = f64>, default: f64) -> f64 {
    fold(&values.into_iter().collect::<Vec<_>>(), default, min)
}

/// Python's `max()` of what is given, `default` where nothing is.
pub(crate) fn max_of(values: impl IntoIterator<Item = f64>, default: f64) -> f64 {
    fold(&values.into_iter().collect::<Vec<_>>(), default, max)
}

/// A stable sort, largest first, as Python's `sort(key=..., reverse=True)` keeps equal keys in their order.
pub(crate) fn sort_desc<T>(items: &mut [T], key: impl Fn(&T) -> f64) {
    items.sort_by(|a, b| {
        key(b)
            .partial_cmp(&key(a))
            .unwrap_or(std::cmp::Ordering::Equal)
    });
}

/// The index of the first key no later key beats, as Python's `min(..., key=)` and `max(..., key=)` keep the first.
fn first_index(keys: &[f64], beats: fn(f64, f64) -> bool) -> Option<usize> {
    let mut best: Option<usize> = None;
    for (i, &k) in keys.iter().enumerate() {
        if best.is_none_or(|b| beats(k, keys[b])) {
            best = Some(i);
        }
    }
    best
}

fn less(k: f64, best: f64) -> bool {
    k < best
}

fn greater(k: f64, best: f64) -> bool {
    k > best
}

/// The item at the first key no later one beats.
fn first_by<T>(
    items: impl IntoIterator<Item = T>,
    key: impl Fn(&T) -> f64,
    beats: fn(f64, f64) -> bool,
) -> Option<T> {
    let items: Vec<T> = items.into_iter().collect();
    let keys: Vec<f64> = items.iter().map(key).collect();
    let at = first_index(&keys, beats)?;
    items.into_iter().nth(at)
}

/// The first item with the least key, as Python's `min(..., key=)`.
pub(crate) fn first_min<T>(
    items: impl IntoIterator<Item = T>,
    key: impl Fn(&T) -> f64,
) -> Option<T> {
    first_by(items, key, less)
}

/// The first item with the greatest key, as Python's `max(..., key=)` (Rust's `max_by` keeps the last).
pub(crate) fn first_max<T>(
    items: impl IntoIterator<Item = T>,
    key: impl Fn(&T) -> f64,
) -> Option<T> {
    first_by(items, key, greater)
}

/// Euclidean distance from a point to a rectangle (0 if the point is inside).
#[must_use]
pub fn point_rect_dist(px: f64, py: f64, r: &Rect) -> f64 {
    let dx = max3(r.x - px, 0.0, px - r.x2());
    let dy = max3(r.y - py, 0.0, py - r.y2());
    hypot(dx, dy)
}

/// A sheet rect as the engine's feet box - what the H29b predicates measure.
#[must_use]
pub fn ft_box(r: &Rect) -> FtBox {
    (r.x / FTPX, r.y / FTPX, r.x2() / FTPX, r.y2() / FTPX)
}

/// Fire-water tubs sitting farther than the engine's reach from any building - a tub no building's eaves hold by
/// [`tub_by_its_eaves`], the one predicate the compound draft seats its tubs by. A tensuioke is fed by roof runoff, so every tub must
/// sit against a building. Worst (farthest) first.
#[must_use]
pub fn fire_water_adrift(plan: &ParsedPlan) -> Vec<TubAdrift> {
    let mut out = Vec::new();
    for t in &plan.tubs {
        let (cx, cy) = (t.x + t.w / 2.0, t.y + t.h / 2.0);
        if plan
            .buildings
            .iter()
            .any(|b| tub_by_its_eaves((cx / FTPX, cy / FTPX), ft_box(b)))
        {
            continue;
        }
        let gap = min_of(
            plan.buildings.iter().map(|b| point_rect_dist(cx, cy, b)),
            f64::INFINITY,
        );
        out.push(TubAdrift {
            x: cx,
            y: cy,
            gap_ft: gap / FTPX,
        });
    }
    sort_desc(&mut out, |t| t.gap_ft);
    out
}

/// The centers (px) of the doors on building `b`: each rect the sheet tags `door` or the shoe stone it declares, within
/// [`DOOR_ON_WALL_PX`] of the footprint and of one of its edges (an inner room's door, deep inside, is no entrance).
///
/// Research:
///     a stepping stone counts as a door - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: a reception our plans enter by a stepping stone at its veranda has its tub beside that stone, so the shoe stone a sheet declares is that building's door for its tubs.
#[must_use]
pub fn doors_of(plan: &ParsedPlan, b: &Rect) -> Vec<(f64, f64)> {
    let m = DOOR_ON_WALL_PX;
    plan.fills
        .iter()
        .filter(|d| {
            (plan.label_kinds.get(&d.pos).map(String::as_str) == Some("door")
                || d.ident == SHOE_STONE_ID)
                && d.x >= b.x - m
                && d.x2() <= b.x2() + m
                && d.y >= b.y - m
                && d.y2() <= b.y2() + m
                && min(
                    min(
                        min((d.x - b.x).abs(), (d.x2() - b.x2()).abs()),
                        (d.y - b.y).abs(),
                    ),
                    (d.y2() - b.y2()).abs(),
                ) <= m
        })
        .map(|d| (d.x + d.w / 2.0, d.y + d.h / 2.0))
        .collect()
}

/// Fire-water tubs that stand at a building's wall but not at its entrance (feature 372 wave 106): a tub's center stands within the
/// engine's reach of a door of a building whose eaves hold it ([`tub_by_its_door`]). A tub whose buildings tag no door fails too; a
/// tub at a bath (its NEAREST host, or one of the hosts tied for nearest, [`DOORLESS_KINDS`]) is not judged by a door; one adrift of
/// every building is [`fire_water_adrift`]'s. Worst first.
///
/// Research:
///     a bath's tub on its yard side - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: the bath our plans attach to the kitchen, entered from the house, has its tub on its yard side, so a tub whose nearest host is a bath - or a bath tied for nearest - is not judged by a door
///     each tub beside a door - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: each tub stands beside a door of its building, within the convention's reach, so every other tub stands by a door of a building whose eaves hold it
#[must_use]
pub fn tubs_off_their_doors(plan: &ParsedPlan) -> Vec<TubOffItsDoor> {
    let mut out = Vec::new();
    for t in &plan.tubs {
        let (cx, cy) = (t.x + t.w / 2.0, t.y + t.h / 2.0);
        let hosts: Vec<&Rect> = plan
            .buildings
            .iter()
            .filter(|b| tub_by_its_eaves((cx / FTPX, cy / FTPX), ft_box(b)))
            .collect();
        let doors: Vec<(f64, f64)> = hosts
            .iter()
            .flat_map(|b| doors_of(plan, b))
            .map(|(dx, dy)| (dx / FTPX, dy / FTPX))
            .collect();
        // T182: every host tied for nearest is asked, never the first in plan order - the round-trip's bath tub stood 8 px from the bath
        // and 8 px from the house, and was judged by the house's door 52 ft away
        let Some(nearest) = first_min(hosts.iter().copied(), |b| point_rect_dist(cx, cy, b)) else {
            continue;
        };
        let near = point_rect_dist(cx, cy, nearest);
        if hosts.iter().any(|b| {
            // an exact tie, as the Python's `==` asks it
            point_rect_dist(cx, cy, b).total_cmp(&near).is_eq()
                && plan
                    .label_kinds
                    .get(&b.pos)
                    .is_some_and(|k| DOORLESS_KINDS.contains(&k.as_str()))
        }) {
            continue;
        }
        if !doors.is_empty() && tub_by_its_door((cx / FTPX, cy / FTPX), &doors) {
            continue;
        }
        let door_ft = min_of(
            doors
                .iter()
                .map(|&(dx, dy)| hypot(cx / FTPX - dx, cy / FTPX - dy)),
            f64::INFINITY,
        );
        out.push(TubOffItsDoor {
            x: cx,
            y: cy,
            door_ft,
        });
    }
    sort_desc(&mut out, |t| t.door_ft);
    out
}

/// Fire-water tubs whose glyph overlaps a building footprint (or a ROOFED court, feature 267 pass 3) instead of standing clear of it.
/// The measure is the DRAWN DISC's penetration past the nearest footprint edge, not its center's position (GM catch 2026-07-26): it
/// rises smoothly from the first pixel of contact. Worst (deepest in) first.
///
/// Research:
///     no tub inside a building - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: no tub stands inside a building's outline on our plans, so a tub's disc reaching into a footprint is refused.
///     no tub under a roofed court - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: no tub stands inside a building's outline, and a roofed court is under a roof as a building is, so a tub's disc reaching into one is refused (feature 267 pass 3).
#[must_use]
pub fn tubs_in_buildings(plan: &ParsedPlan, min_px: f64) -> Vec<TubInBuilding> {
    let mut out = Vec::new();
    for t in &plan.tubs {
        let (cx, cy, rad) = (t.x + t.w / 2.0, t.y + t.h / 2.0, t.w / 2.0);
        let mut into = 0.0;
        for b in plan.buildings.iter().chain(&plan.roofed_courts) {
            let gap = point_rect_dist(cx, cy, b);
            // center outside: the disc reaches (rad - gap) past the edge; center inside: its radius PLUS the center's depth
            let inside = if gap == 0.0 {
                min(min(min(cx - b.x, b.x2() - cx), cy - b.y), b.y2() - cy)
            } else {
                -gap
            };
            into = max(into, rad + inside);
        }
        if into >= min_px {
            out.push(TubInBuilding {
                x: cx,
                y: cy,
                into_ft: into / FTPX,
            });
        }
    }
    sort_desc(&mut out, |t| t.into_ft);
    out
}

/// Smaller of the x/y overlaps between a box and rect `b` (>0 only on a real 2-D overlap).
#[must_use]
pub fn overlap_px(left: f64, top: f64, right: f64, bottom: f64, b: &Rect) -> f64 {
    min(
        min(right, b.x2()) - max(left, b.x),
        min(bottom, b.y2()) - max(top, b.y),
    )
}

/// Fire-water tubs sitting ON a well: overlapping point glyphs read as one object (a rain-fed fire tub is not the drawing well).
///
/// Research:
///     a tub off a well - CONVENTION: a fire-water tub's glyph never overlaps a well's, two point glyphs that would read as one object; no page gives it.
#[must_use]
pub fn tubs_on_wells(plan: &ParsedPlan, min_px: f64) -> Vec<TubOnWell> {
    plan.tubs
        .iter()
        .filter(|t| {
            plan.wells
                .iter()
                .any(|w| overlap_px(t.x, t.y, t.x2(), t.y2(), w) >= min_px)
        })
        .map(|t| TubOnWell {
            x: t.x + t.w / 2.0,
            y: t.y + t.h / 2.0,
        })
        .collect()
}

/// Foreground items (tubs, wells, every sub-building rect) painted OVER by any rect or glyph drawn LATER in the SVG; a later shape
/// wholly inside the item is its own detailing. Captions are not checked (feature 286: the placer seats them).
///
/// Research:
///     the foreground drawn last - CONVENTION: tubs, wells and every sub-building rect are drawn above the fills, so a later shape covering one is a defect, the draw order research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html records for labels and small glyphs; the covered area carries a claim of its own.
#[must_use]
pub fn occluded_foreground(plan: &ParsedPlan, min_px: f64) -> Vec<Occluded> {
    let occluders: Vec<&Rect> = plan.fills.iter().chain(&plan.glyphs).collect();
    let buried = |r: &Rect| {
        occluders.iter().any(|f| {
            f.pos > r.pos
                && overlap_px(r.x, r.y, r.x2(), r.y2(), f) >= min_px
                && !(f.x >= r.x && f.y >= r.y && f.x2() <= r.x2() && f.y2() <= r.y2())
        })
    };
    let mut out = Vec::new();
    for (kind, rects) in [
        ("tub", &plan.tubs),
        ("well", &plan.wells),
        ("feature", &plan.furniture),
    ] {
        for r in rects.iter().filter(|r| buried(r)) {
            out.push(Occluded {
                kind,
                x: r.x + r.w / 2.0,
                y: r.y + r.h / 2.0,
            });
        }
    }
    out
}

/// Midpoints of gaps in the compound wall - the gate and postern openings.
#[must_use]
pub fn gate_openings(plan: &ParsedPlan) -> Vec<(f64, f64)> {
    wall_openings(plan).iter().map(|o| (o.x, o.y)).collect()
}

/// The middle of the passage between the `main gate`'s posts (feature 267: a nagaya-mon's passage runs THROUGH its gate range, which
/// stands in a wall break wider than any gap the wall-opening scan counts as a gate).
#[must_use]
pub fn main_gate_passage(plan: &ParsedPlan) -> Vec<(f64, f64)> {
    let posts = &plan.gate_posts;
    if posts.is_empty() {
        return Vec::new();
    }
    #[expect(
        clippy::cast_precision_loss,
        reason = "a sheet's post count, far inside f64's integers"
    )]
    let n = posts.len() as f64;
    vec![(
        crate::py::sum(posts.iter().map(|r| r.x + r.w / 2.0)) / n,
        crate::py::sum(posts.iter().map(|r| r.y + r.h / 2.0)) / n,
    )]
}

/// The clear width between the `main gate`'s two posts, in feet - the group's two SMALLEST rects (a gate drawn through a range tags
/// its passage floor too, Hayakawa); None without two.
#[must_use]
pub fn main_gate_passage_ft(plan: &ParsedPlan) -> Option<f64> {
    if plan.gate_posts.len() < 2 {
        return None;
    }
    let mut by_area: Vec<&Rect> = plan.gate_posts.iter().collect();
    by_area.sort_by(|a, b| {
        (a.w * a.h)
            .partial_cmp(&(b.w * b.h))
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    let mut posts: Vec<&Rect> = by_area.into_iter().take(2).collect();
    posts.sort_by(|a, b| {
        a.x.partial_cmp(&b.x)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal))
    });
    let (a, b) = (posts[0], posts[1]);
    let across = if (a.y - b.y).abs() < max(a.h, b.h) {
        b.x - (a.x + a.w)
    } else {
        b.y - (a.y + a.h)
    };
    Some(across / FTPX)
}

/// A notice board (kosatsu) is read where people pass: every board the sheet TAGS (feature 266: the board, not its caption) farther
/// than the engine's reach from every wall gate opening and the main gate's passage ([`board_by_a_gate`]).
#[must_use]
pub fn notice_board_adrift(plan: &ParsedPlan) -> Vec<MisplacedBoard> {
    let mut ops = gate_openings(plan);
    ops.extend(main_gate_passage(plan));
    if ops.is_empty() {
        return Vec::new();
    }
    let feet: Vec<(f64, f64)> = ops.iter().map(|&(x, y)| (x / FTPX, y / FTPX)).collect();
    let mut out = Vec::new();
    for r in &plan.fills {
        if plan.label_kinds.get(&r.pos).map(String::as_str) != Some("notice board") {
            continue;
        }
        if board_by_a_gate(ft_box(r), &feet) {
            continue;
        }
        let gap = min_of(
            ops.iter().map(|&(ox, oy)| point_rect_dist(ox, oy, r)),
            f64::INFINITY,
        );
        out.push(MisplacedBoard {
            x: r.x + r.w / 2.0,
            y: r.y + r.h / 2.0,
            gap_ft: gap / FTPX,
        });
    }
    out
}

/// A small dark door-rect fully inside a building whose nearest edge is close (it is meant to be that wall's door) but not flush; the
/// first building that holds it is the one judged.
///
/// Research:
///     a door flush to its wall - CONVENTION: a door glyph sits flush to the wall it opens through and never floats just inside the building, the map drawing convention research/questions/0117-doorways-and-doors-to.drawing.html records and research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html checks; the two pixel reaches carry claims of their own.
#[must_use]
pub fn floating_doors(plan: &ParsedPlan) -> Vec<FloatingDoor> {
    let mut out = Vec::new();
    for d in &plan.door_rects {
        for b in &plan.buildings {
            let gaps = [d.x - b.x, b.x2() - d.x2(), d.y - b.y, b.y2() - d.y2()];
            if gaps.iter().all(|g| *g >= 0.0) {
                let gap = min(min(min(gaps[0], gaps[1]), gaps[2]), gaps[3]);
                if DOOR_FLUSH_TOL_PX < gap && gap <= DOOR_NEAR_PX {
                    out.push(FloatingDoor {
                        x: d.x + d.w / 2.0,
                        y: d.y + d.h / 2.0,
                        gap_ft: gap / FTPX,
                    });
                }
                break;
            }
        }
    }
    out
}
