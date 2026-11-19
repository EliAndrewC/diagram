//! A kitchen garden's sun on a hand-drawn sheet (feature 449 T175, `pack_audit/sun.py` whole; feature 283, research homesteads 044).
//!
//! The GM, 2026-09-28: *"a garden needs a certain amount of sunlight per day ... That feels like it should be an automated check that gets
//! run on hand-drawn diagrams that have gardens"*. The record's sun - 38 degrees north in the autumn shoulder month - is walked through
//! the day in half hours; at each step every drawn thing that stands up casts its shadow away from the sun, as far as its height over the
//! tangent of the sun's elevation, and the half hour counts as lit when at least half the bed is out of every shadow. A sun bed needs 6
//! lit hours; a half-shade bed (`data-bed="half-shade"`) 3, a tree's shadow dappled light for it.
//!
//! THE GEOMETRY, FROM SHAPELY TO `geo` (feature 449 T175): every caster is a box or the 64-gon `Point.buffer(r, 16)` makes, so convex,
//! and a convex footprint swept along a line is the convex hull of it and its shifted copy - which is what the Python's union of the
//! footprint, the shifted footprint and that hull comes to. So a shadow is its [`hull`], its `intersects` read exactly on the hull's
//! input points (`geo`'s robust predicates), and a caster's overlap with the bed and the bed's area are the products GEOS's shoelace
//! gives an axis-aligned box, exactly. Only the bed's unshaded area is an overlay - `geo`'s union and difference, over `i_overlay` - and
//! it decides one comparison, at least half the bed lit; the port's lockstep (feature 449 T175, deleted with the Python by T212) held that
//! verdict, every half hour, equal to the Python's, the area's distance from GEOS's under the verdict's least distance from its threshold.
//!
//! Research:
//!     the garden's sun - NONE: the sun walked and the shadows cast by the figures whose claims stand on each, deciding nothing more

use std::sync::LazyLock;

use fancy_regex::Regex;
use geo::{
    coord, Area, BooleanOps, ConvexHull, Intersects, LineString, MultiPoint, Point, Polygon,
};
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use super::Sheet;
use crate::grids::FTPX;
use crate::parse::{ParsedPlan, Rect};
use crate::py::{fixed, fmt_g, max, min, modulo};

/// The record's latitude for every shadow it casts (research 0038).
///
/// Research:
///     sun latitude - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: shadows are cast at 38 degrees north, the temperate middle of the empire the maps are set in.
pub const LAT_DEG: f64 = 38.0;
/// The shoulder month: at 38N it gives the record's 3pm sun, 27-28 deg high at azimuth ~232 (0038).
///
/// Research:
///     sun declination - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a solar declination of -8.5 degrees gives, at 38 N, the page's 3 pm sun 27 degrees high in the southwest, late in autumn.
pub const DECL_DEG: f64 = -8.5;
/// The day walked in half hours.
///
/// Research:
///     sun step - NONE: the day is walked in half-hour steps, a measuring grain.
pub const STEP_H: f64 = 0.5;
/// A half hour is lit when at least half the bed is out of shadow (homesteads 044, a guess).
///
/// Research:
///     lit share of a bed - GUESS research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: an hour counts as lit when at least half the bed is out of shadow; the page records the counting as a guess.
pub const LIT_SHARE: f64 = 0.5;
/// Sun crops - daikon, eggplant, cucumber, beans - want about 6 hours or more (homesteads 044).
///
/// Research:
///     sun bed hours - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a kitchen bed of sun crops such as daikon must get 6 hours of direct sun in autumn.
pub const SUN_BED_H: f64 = 6.0;
/// Half-shade crops do with 3 to 4 (homesteads 044).
///
/// Research:
///     half-shade bed hours - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a bed of half-shade crops needs 3 hours of direct sun (3 to 4 for such crops).
pub const HALF_SHADE_BED_H: f64 = 3.0;
/// The farmhouse ridge the record casts a building's shadow from (homesteads 043) - a least height.
///
/// Research:
///     building shadow height - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a building casts its shadow from the farmhouse ridge, about 20 ft, the least height the record gives.
pub const BUILDING_FT: f64 = 20.0;
/// The surviving earth wall's 1.6 m (buildings 490).
///
/// Research:
///     wall shadow height - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a compound wall casts its shadow from 1.6 m (~5 ft), the surviving earth wall's height, the least height the record gives.
pub const WALL_FT: f64 = 1.6 / 0.3048;
/// A working, pruned belt's 10 m (0038); an untended stand is 15-28 m.
///
/// Research:
///     tree shadow height - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a tree casts its shadow from 10 m (~33 ft), a working windbreak's height, the least height the record draws a tree at.
pub const TREE_FT: f64 = 10.0 / 0.3048;
/// A roofed thing under [`SMALL_BUILDING_SQFT`] - a privy, a hokora, a covered way - at the least height a person stands under (a guess).
///
/// Research:
///     small roofed thing height - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: every building casts from the farmhouse ridge's 20 ft, with no smaller class - a roofed thing under SMALL_BUILDING_SQFT casts from 6 ft, a departure the code keeps until feature 417 T33; a roofed thing under SMALL_BUILDING_SQFT (a privy, a hokora, a covered way) casts a shadow from 6 ft, the least height a person stands under; no page gives it.
#[expect(
    clippy::doc_markdown,
    reason = "the claim is the Python's, word for word"
)]
pub const SMALL_BUILDING_FT: f64 = 6.0;
/// The small roofed thing's area.
///
/// Research:
///     small roofed thing area - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: every building casts from the farmhouse ridge's 20 ft, with no smaller class - a roofed thing under 100 sq ft counts as small, a departure the code keeps until feature 417 T33; a roofed thing under 100 sq ft counts as small for its shadow height; no page gives the cutoff.
pub const SMALL_BUILDING_SQFT: f64 = 100.0;
/// What a sheet draws that does not stand up to cast a garden's shadow: ground and water features, a building's own parts (under its
/// roof, which casts for them) and furniture below head height. Everything else the parser counts as a structure casts.
///
/// Research:
///     ground features and a building's parts - GUESS: a basin, a tax barge on its water, and a building's door, veranda, hearth, dais, clerks' seats and altars cast no shadow of their own, the ground's being low and the parts standing under the roof that casts for them; no page gives it.
///     upright furniture - UNRESEARCHED: a weapon rack, a stone lantern and a well with its gear cast no shadow on a bed; research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html casts only buildings, walls and trees, and no page gives their heights (research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.drawing.html draws a lantern as one small mark, research/questions/0165-martial-training-grounds-and-dojo.drawing.html gives a rack's footprint alone).
pub const NOT_STANDING: [&str; 12] = [
    "basin",
    "door",
    "engawa",
    "hearth",
    "weapon rack",
    "stone lantern",
    "tax barge",
    "magistrate's dais",
    "clerks' seats",
    "well",
    "shrine altar",
    "wood-kami altar",
];
/// The kind a notice board is drawn under.
pub const NOTICE_BOARD_KIND: &str = "notice board";
/// THE NOTICE BOARD CASTS (feature 449 T177): it stood in [`NOT_STANDING`], casting nothing, though 0190 measures the frame about 10 to
/// 11 ft high; it casts from the least of those, as every height here is the least the record gives, whatever its drawn footprint.
///
/// Research:
///     the notice board's height - research/questions/0190-notice-boards-kosatsuba.html: the board casts its shadow from 10 ft, the least of the 10 to 11 ft the page measures for a post town's frame, drawn as a roofed frame 16 by 6 ft (research/questions/0190-notice-boards-kosatsuba.drawing.html).
pub const NOTICE_BOARD_FT: f64 = 10.0;
/// Below this the sun is on the horizon: its shadows run off the sheet and it grows nothing.
///
/// Research:
///     sun floor - NONE: below 3 degrees the sun is on the horizon and its shadows run off the sheet, a computation cutoff.
pub const MIN_SUN_DEG: f64 = 3.0;
/// A garden element smaller than this (a label box, a border tick) is not a bed.
///
/// Research:
///     bed area floor - NONE: a garden element under 300 px2 is a label box or border tick, not a bed, a parser classification.
pub const MIN_BED_PX: f64 = 300.0;
/// The kind a kitchen bed is drawn under.
pub const GARDEN_KIND: &str = "vegetable garden";
static BED_ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"data-bed="([^"]+)""#));

/// One thing that stands up and casts a shadow: its footprint's ring (as shapely's exterior gives it, closed), its height in ft, what
/// it is, whether it is a tree.
#[derive(Debug, Clone, PartialEq)]
pub struct Caster {
    pub ring: Vec<(f64, f64)>,
    pub height_ft: f64,
    pub what: String,
    pub tree: bool,
}

/// The sun's (elevation, azimuth) in degrees at solar `hour`; azimuth clockwise from north.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 15 (degrees per hour, solar noon); 12 (degrees per hour, solar noon)
#[must_use]
pub fn sun_at(hour: f64, lat_deg: f64, decl_deg: f64) -> (f64, f64) {
    let h = (15.0 * (hour - 12.0)).to_radians();
    let (la, d) = (lat_deg.to_radians(), decl_deg.to_radians());
    let el = (la.sin() * d.sin() + la.cos() * d.cos() * h.cos()).asin();
    let az = h.sin().atan2(h.cos() * la.sin() - d.tan() * la.cos()) + std::f64::consts::PI;
    (el.to_degrees(), modulo(az.to_degrees(), 360.0))
}

/// `shapely.geometry.box(x0, y0, x1, y1)`'s ring: counter-clockwise from the lower x's far corner, closed.
#[must_use]
pub fn box_ring(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<(f64, f64)> {
    vec![(x1, y0), (x1, y1), (x0, y1), (x0, y0), (x1, y0)]
}

fn rect_ring(r: &Rect) -> Vec<(f64, f64)> {
    box_ring(r.x, r.y, r.x + r.w, r.y + r.h)
}

/// `Point(cx, cy).buffer(r, 16)`'s ring: GEOS's circle, 64 points from (cx + r, cy) clockwise (`OffsetSegmentGenerator::createCircle`,
/// each angle `-i * (2 pi / 64)`), closed.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 64 (circle buffer points, 16 a quarter)
#[must_use]
pub fn circle_ring(cx: f64, cy: f64, r: f64) -> Vec<(f64, f64)> {
    let inc = 2.0 * std::f64::consts::PI / 64.0;
    let mut out = vec![(cx + r, cy)];
    for i in 1..64_i32 {
        let angle = f64::from(-i) * inc;
        out.push((cx + r * angle.cos(), cy + r * angle.sin()));
    }
    out.push((cx + r, cy));
    out
}

/// The area GEOS gives an axis-aligned box ([`box_ring`]): its shoelace from the first corner comes to `(x1 - x0) * (y1 - y0)` exactly.
fn box_area(x0: f64, y0: f64, x1: f64, y1: f64) -> f64 {
    ((x1 - x0) * (y1 - y0)).abs()
}

/// The ground a caster darkens with the sun at (el, az): its footprint and the footprint shifted away from the sun by its shadow's length,
/// and the hull of both - on a sheet north is up and a px is 1/FTPX ft, so the shadow runs (-sin az, +cos az) in px.
#[must_use]
pub fn hull(caster: &Caster, el_deg: f64, az_deg: f64) -> Polygon<f64> {
    let length = caster.height_ft / el_deg.to_radians().tan() * FTPX;
    let (dx, dy) = (
        -az_deg.to_radians().sin() * length,
        az_deg.to_radians().cos() * length,
    );
    let points: Vec<Point<f64>> = caster
        .ring
        .iter()
        .map(|&(x, y)| Point::new(x, y))
        .chain(caster.ring.iter().map(|&(x, y)| Point::new(x + dx, y + dy)))
        .collect();
    MultiPoint::new(points).convex_hull()
}

fn polygon(ring: &[(f64, f64)]) -> Polygon<f64> {
    Polygon::new(
        LineString::new(ring.iter().map(|&(x, y)| coord! { x: x, y: y }).collect()),
        Vec::new(),
    )
}

/// One kitchen bed: its rect and its polygon.
pub struct Bed<'r> {
    pub rect: &'r Rect,
    shape: Polygon<f64>,
}

impl<'r> Bed<'r> {
    #[must_use]
    pub fn new(rect: &'r Rect) -> Self {
        Self {
            rect,
            shape: polygon(&rect_ring(rect)),
        }
    }

    /// `bed.area`, GEOS's.
    #[must_use]
    pub fn area(&self) -> f64 {
        let r = self.rect;
        box_area(r.x, r.y, r.x + r.w, r.y + r.h)
    }

    /// The bed's area out of every shadow in `shade`: `bed.difference(unary_union(shade)).area`, `geo`'s overlay.
    #[must_use]
    pub fn unshaded(&self, shade: &[Polygon<f64>]) -> f64 {
        if shade.is_empty() {
            return self.area();
        }
        let union = geo::unary_union(shade);
        self.shape.difference(&union).unsigned_area()
    }
}

/// The half hours of the day the sun stands at least [`MIN_SUN_DEG`] high: each step's (elevation, azimuth).
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 24 (hours in a day)
#[must_use]
pub fn daylight() -> Vec<(f64, f64)> {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "int(24 / 0.5), 48"
    )]
    let steps = (24.0 / STEP_H) as u32;
    (0..steps)
        .map(|k| sun_at(f64::from(k) * STEP_H, LAT_DEG, DECL_DEG))
        .filter(|(el, _)| *el >= MIN_SUN_DEG)
        .collect()
}

/// Each daylight half hour's unshaded area of the bed, with the threshold it is held to (`LIT_SHARE * bed.area`): what
/// [`lit_hours`] counts.
///
/// Research:
///     a tree's dappled light - GUESS research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: for a half-shade bed a tree's shadow is not counted, the bed needing hours in which nothing but a tree's leaves stands between it and the sun, the page's guess at how to count dappled light.
#[must_use]
pub fn lit_areas(bed: &Bed, casters: &[Caster], half_shade: bool) -> Vec<(f64, f64)> {
    daylight()
        .into_iter()
        .map(|(el, az)| {
            let shade: Vec<Polygon<f64>> = casters
                .iter()
                .filter(|c| !(half_shade && c.tree))
                .map(|c| hull(c, el, az))
                .collect();
            (bed.unshaded(&shade), LIT_SHARE * bed.area())
        })
        .collect()
}

/// Hours of the day at least [`LIT_SHARE`] of the bed is in direct sun (for a half-shade bed a tree's shadow is dappled light).
///
/// Research:
///     its lit hours - NONE: the half hours [`daylight`] walks counted where the bed's unshaded area reaches its threshold, deciding nothing the claims on those figures do not
#[must_use]
pub fn lit_hours(bed: &Bed, casters: &[Caster], half_shade: bool) -> f64 {
    let lit = lit_areas(bed, casters, half_shade)
        .into_iter()
        .filter(|(lit, need)| lit >= need)
        .count();
    #[expect(clippy::cast_precision_loss, reason = "at most 48 half hours")]
    let n = lit as f64;
    n * STEP_H
}

/// The byte offset of code point `cp` (a parsed rect's `pos`, always inside the text), or the text's end.
fn byte_of(text: &str, cp: i64) -> usize {
    let n = usize::try_from(cp).unwrap_or(usize::MAX);
    text.char_indices().nth(n).map_or(text.len(), |(b, _)| b)
}

/// Every drawn kitchen bed - a rect of the `vegetable garden` kind, at least [`MIN_BED_PX`] - and whether it is declared a half-shade
/// bed; a sheet that tags no bed is not read for kinds.
///
/// # Errors
/// The sheet's reader refused it.
pub fn gardens<'p>(plan: &'p ParsedPlan, svg: &Sheet) -> Result<Vec<(&'p Rect, bool)>, Error> {
    let text = svg.text;
    if !text.contains(&format!("data-kind=\"{GARDEN_KIND}\"")) {
        return Ok(Vec::new());
    }
    let kinds = svg.kinds()?;
    let mut out = Vec::new();
    for r in &plan.fills {
        if kinds.get(&r.pos).map(String::as_str) == Some(GARDEN_KIND) && r.w * r.h >= MIN_BED_PX {
            // `text[r.pos : text.find(">", r.pos)]`, a find that fails being -1: the text up to its last character
            let start = byte_of(text, r.pos);
            let last = text.char_indices().last().map_or(0, |(b, _)| b);
            let end = text[start..].find('>').map_or(last, |i| start + i);
            let tag = text.get(start..end.max(start)).unwrap_or_default();
            let half = BED_ATTR
                .captures(tag)
                .ok()
                .flatten()
                .is_some_and(|m| &m[1] == "half-shade");
            out.push((r, half));
        }
    }
    Ok(out)
}

/// Everything the sheet draws that stands up: its buildings (a small one at its own height), its walls (the compound's and its court
/// dividers) and its trees - never the bed itself (a structure more than half over it), nor what [`NOT_STANDING`] names.
///
/// Research:
///     its casters - NONE: the sheet's structures, walls and trees standing at the heights whose claims stand on them, deciding nothing more
///     the bed's own ink - GUESS: a structure covering more than half the bed is read as the bed's own drawing, not as a caster, a classification of ours; no page gives it.
///     a court divider casts at the wall's height - GUESS: a court divider casts its shadow from the compound wall's 1.6 m, the divider being a wall of the compound; no page gives a divider's height.
///
/// # Errors
/// The sheet's reader refused it.
pub fn casters(plan: &ParsedPlan, svg: &Sheet, bed: &Bed) -> Result<Vec<Caster>, Error> {
    let kinds = svg.kinds()?;
    let b = bed.rect;
    let mut out = Vec::new();
    for r in &plan.structures {
        let kind = kinds.get(&r.pos).map(String::as_str);
        // a box's intersection with the bed is a box, its area GEOS's product
        let (x0, y0) = (max(r.x, b.x), max(r.y, b.y));
        let (x1, y1) = (min(r.x + r.w, b.x + b.w), min(r.y + r.h, b.y + b.h));
        let over = if x1 > x0 && y1 > y0 {
            box_area(x0, y0, x1, y1)
        } else {
            0.0
        };
        if kind == Some(GARDEN_KIND)
            || kind.is_some_and(|k| NOT_STANDING.contains(&k))
            || over > 0.5 * bed.area()
        {
            continue;
        }
        let small = r.w * r.h / (FTPX * FTPX) < SMALL_BUILDING_SQFT;
        out.push(Caster {
            ring: rect_ring(r),
            height_ft: if kind == Some(NOTICE_BOARD_KIND) {
                NOTICE_BOARD_FT
            } else if small {
                SMALL_BUILDING_FT
            } else {
                BUILDING_FT
            },
            what: kind
                .filter(|k| !k.is_empty())
                .unwrap_or("building")
                .to_owned(),
            tree: false,
        });
    }
    for w in plan.wall_segs.iter().chain(&plan.dividers) {
        out.push(Caster {
            ring: rect_ring(w),
            height_ft: WALL_FT,
            what: "wall".to_owned(),
            tree: false,
        });
    }
    for t in &plan.trees {
        out.push(Caster {
            ring: circle_ring(t.x + t.w / 2.0, t.y + t.h / 2.0, t.w / 2.0),
            height_ft: TREE_FT,
            what: "trees".to_owned(),
            tree: true,
        });
    }
    Ok(out)
}

/// What takes the bed's sun: the casters whose shadow reaches it in some daylight half hour, by what they are, most first.
///
/// Research:
///     its shaders - NONE: the casters whose shadow meets the bed in a half hour [`daylight`] walks, named, deciding nothing about the place
#[must_use]
pub fn shaders(bed: &Bed, cs: &[Caster], half_shade: bool) -> Vec<String> {
    let mut hit: Vec<(String, usize)> = Vec::new();
    let day = daylight();
    for c in cs {
        if half_shade && c.tree {
            continue;
        }
        if day
            .iter()
            .any(|&(el, az)| hull(c, el, az).intersects(&bed.shape))
        {
            match hit.iter_mut().find(|(w, _)| *w == c.what) {
                Some((_, n)) => *n += 1,
                None => hit.push((c.what.clone(), 1)),
            }
        }
    }
    hit.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
    hit.into_iter()
        .map(|(what, n)| if n > 1 { format!("{what} ({n})") } else { what })
        .collect()
}

/// Each kitchen bed that gets too little sun, with its hours, the hours it needs and what shades it.
///
/// # Errors
/// The sheet's reader refused it.
pub fn garden_sun(plan: &ParsedPlan, svg: &Sheet) -> Result<Vec<String>, Error> {
    let mut out = Vec::new();
    for (r, half) in gardens(plan, svg)? {
        let bed = Bed::new(r);
        let cs = casters(plan, svg, &bed)?;
        let got = lit_hours(&bed, &cs, half);
        let need = if half { HALF_SHADE_BED_H } else { SUN_BED_H };
        if got < need {
            // a bed short of its hours has a shader, so the list is never empty (feature 449 T182: its "nothing drawn" could not show)
            let what = shaders(&bed, &cs, half).join(", ");
            out.push(format!(
                "the {}kitchen bed at ({},{}), {} by {} ft, has {} h of sun in the shoulder month and needs {} (research homesteads 044) - shaded by {what}",
                if half { "half-shade " } else { "" },
                fixed(r.x, 0),
                fixed(r.y, 0),
                fixed(r.w / FTPX, 0),
                fixed(r.h / FTPX, 0),
                fmt_g(got),
                fmt_g(need)
            ));
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::{rect_ring, shaders, Bed, Caster};
    use crate::parse::Rect;

    /// A half-shade bed is shaded by what stands, never by a tree (feature 283: a bed sown for half shade wants the trees' shade).
    #[test]
    fn a_tree_shades_a_sun_bed_and_not_a_half_shade_one() {
        let r = Rect::new(0.0, 0.0, 30.0, 30.0, "", 0);
        let bed = Bed::new(&r);
        let caster = |what: &str, tree| Caster {
            ring: rect_ring(&r),
            height_ft: 20.0,
            what: what.to_owned(),
            tree,
        };
        let cs = [
            caster("tree", true),
            caster("hall", false),
            caster("hall", false),
        ];
        assert_eq!(shaders(&bed, &cs, false), ["hall (2)", "tree"]);
        assert_eq!(shaders(&bed, &cs, true), ["hall (2)"]);
    }
}
