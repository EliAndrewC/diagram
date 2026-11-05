//! The fit rules a layout is asked past the raster (feature 444 T30): the house's wall off the paddy's facing chords, every bed off
//! the running water, the house out of the ground no way can reach, every part admitted by what the registry holds, and the
//! persimmon out of a yard's or a bed's sun - this household's own tree dropped, never its seat (`rolling/fit.py` `_parts_fit`).
//!
//! Research:
//!     farmhouse wall off the paddy - research/questions/0029-farmhouses-minka.drawing.html: every rotated corner `HOUSE_PADDY_GAP_FT` plus 1 ft of rounding slack off the field
//!     solid parts off running water - research/questions/0035-villages-beside-their-stream-one-bank-or-both.html: a channel ran alongside the house (Harie) and into its grounds (0031) - beds are held off every ditch, a departure the code keeps until feature 417 T33; each garden bed held off every irrigation line at the corridor `_rect_on_water` keeps
//!     a house no way can reach refused - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a way runs within 100 ft of every house, and no way is drawn on the web's hard ground
//!     every part asked of the registry - NONE: the overlap matrix's own verdict, the extents it forbids each part handed over by the door
//!     persimmon out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: `CANOPY_SHADE_FT` and a crown's radius plus 1 ft, both ways
//!     the tree dropped, never the seat - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: the farm keeps no persimmon

use super::bundle::Bundle;
use super::fit::{corners, Standing};
use super::fixtures::Kind;
use super::layout::Rect;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::seg_dist;
use crate::ways::track::{edge_dist, in_poly, poly_box, segments_cross, Box4};

/// A chord of the paddy's edge facing the seat: its ends and its outward normal (the field side negative).
pub type Chord = (Pt, Pt, Pt);

/// The house's wall off the paddy, and the rounding slack past it (feet).
///
/// Research:
///     farmhouse wall off the paddy - research/questions/0029-farmhouses-minka.drawing.html: 6 ft, the gate's figure
///     the rounding - NONE: the recorded footprint's center and rake rounded to 0.1, so a seat held at exactly the gate's figure came out under it - 1
pub const PADDY_GAP_FT: (f64, f64) = (6.0, 1.0);

/// The persimmon's crown and the foot past it the map's check reads, and its shade's reach (feet).
///
/// Research:
///     the crown - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: 11.5 ft, and a foot past it for the drawn quads
///     its shade - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: `CANOPY_SHADE_FT`, 50 ft east, west and south
pub const PERSIMMON_FT: (f64, f64, f64) = (11.5, 1.0, 50.0);

/// A way's reach of a house, the slack past it, and the points on the circle a seat's depth is asked at.
///
/// Research:
///     a way's reach - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 100 ft
///     the slack - NONE: a foot past the reach, so the ground refused can only be less than the rule's - 1
///     the circle's points - NONE: a sampling grain, 64 about the reach
pub const REACH_FT: (f64, f64, usize) = (100.0, 1.0, 64);

/// What the seating's rules read past the raster: the paddy's facing chords, the running water (each line at its half-width and
/// the box round it), the web's hard ground (each ring grown by its own gap), the extents the registry forbids each part's key,
/// and whether the map keeps the sun corridor.
#[derive(Default)]
pub struct Rules {
    /// The paddy's facing chords, chain by chain.
    pub chains: Vec<Vec<Chord>>,
    /// Each irrigation line, its half-width and its box.
    pub waters: Vec<(Vec<Pt>, f64, Box4)>,
    /// The web's hard ground, each ring with its gap and its box.
    pub hard: Vec<(Vec<Pt>, f64, Box4)>,
    /// Each registry key and the rings it may not lie on.
    pub forbidding: Vec<(String, Vec<Vec<Pt>>)>,
    /// Whether the sun corridor is kept.
    pub sun: bool,
    /// The wood's keep-outs reserved before any house (a shared byre's pocket), each a disc.
    pub bars: Vec<(f64, f64, f64)>,
    /// The boxes placed before any house (a shared byre's pocket), which the placer meets as a standing homestead's box.
    pub placed: Vec<Rect>,
    /// The site boundary's facing chains, the growth's tie-break measures to.
    pub site_chains: Vec<Vec<Chord>>,
    /// The gap a way keeps off a reserved wood seat (feet).
    pub lane_gap: f64,
    /// The passages the settlement's rolled share allows (`passage.passage_budget`).
    pub passage_left: usize,
}

impl Rules {
    /// The water lines and hard rings, each boxed once.
    #[must_use]
    pub fn boxed(lines: Vec<(Vec<Pt>, f64)>) -> Vec<(Vec<Pt>, f64, Box4)> {
        lines
            .into_iter()
            .map(|(r, g)| {
                let b = poly_box(&r);
                (r, g, b)
            })
            .collect()
    }
}

/// Is `p` on the field side of a chord it projects onto, or nearer than `gap` to one (past a chord's ends, its end)?
#[must_use]
pub fn chain_violated(p: Pt, chains: &[Vec<Chord>], gap: f64, tests: &mut Counts) -> bool {
    chains.iter().flatten().any(|&(a, b, n)| {
        tests.add("seg_test@chain_violated", 1);
        let (ex, ey) = (b.0 - a.0, b.1 - a.1);
        let el2 = ex * ex + ey * ey;
        if el2 <= 1e-12 {
            return false;
        }
        let t = ((p.0 - a.0) * ex + (p.1 - a.1) * ey) / el2;
        if (0.0..=1.0).contains(&t) {
            (p.0 - a.0) * n.0 + (p.1 - a.1) * n.1 < gap
        } else {
            let q = if t < 0.0 { a } else { b };
            (p.0 - q.0).hypot(p.1 - q.1) < gap
        }
    })
}

/// Would any corner of the house as turned stand on the paddy's side or nearer its chords than the wall's gap?
#[must_use]
pub fn wall_on_the_bund(b: &Bundle, rules: &Rules, tests: &mut Counts) -> bool {
    let gap = PADDY_GAP_FT.0 + PADDY_GAP_FT.1;
    corners(b.house, b.turn)
        .iter()
        .any(|&c| chain_violated(c, &rules.chains, gap, tests))
}

/// Does a box (center, width, height) land on a running line - a corner or its center within the line's half-width, or an edge
/// crossing it?
#[must_use]
pub fn on_water(r: Rect, waters: &[(Vec<Pt>, f64, Box4)], tests: &mut Counts) -> bool {
    let gc = corners(r, 0.0);
    let (x0, y0, x1, y1) = (
        r.0 - r.2 / 2.0,
        r.1 - r.3 / 2.0,
        r.0 + r.2 / 2.0,
        r.1 + r.3 / 2.0,
    );
    waters.iter().any(|(line, hw, bx)| {
        if bx.2 + hw < x0 || bx.0 - hw > x1 || bx.3 + hw < y0 || bx.1 - hw > y1 {
            return false;
        }
        line.windows(2).any(|w| {
            let (a, b) = (w[0], w[1]);
            if a.0.min(b.0) - hw > x1
                || a.0.max(b.0) + hw < x0
                || a.1.min(b.1) - hw > y1
                || a.1.max(b.1) + hw < y0
            {
                return false;
            }
            tests.add("seg_test@on_water", 9);
            gc.iter()
                .chain(std::iter::once(&(r.0, r.1)))
                .any(|&p| seg_dist(p, a, b) < *hw)
                || (0..4).any(|e| segments_cross(a, b, gc[e], gc[(e + 1) % 4]))
        })
    })
}

/// Does any bed of `b` land on running water?
#[must_use]
pub fn beds_on_water(b: &Bundle, rules: &Rules, tests: &mut Counts) -> bool {
    b.boxes[2..2 + b.gardens.len()]
        .iter()
        .any(|&g| on_water(g, &rules.waters, tests))
}

/// Is `p` on the web's hard ground, each ring grown by its gap?
fn on_hard(p: Pt, hard: &[(Vec<Pt>, f64, Box4)], tests: &mut Counts) -> bool {
    hard.iter().any(|(ring, gap, b)| {
        p.0 >= b.0 - gap && p.0 <= b.2 + gap && p.1 >= b.1 - gap && p.1 <= b.3 + gap && {
            tests.add("pt_test@on_hard", 1);
            in_poly(p, ring) || edge_dist(p, ring) <= *gap
        }
    })
}

/// Would a house at `p` stand deeper in the web's hard ground than a way's reach - its center and every point of the circle the
/// reach and its slack draw about it on that ground? A ring of points can find the disc covered where a hole the size of a
/// point's spacing is not, so it refuses at most a few seats the rule would keep (`boundary.py` `UnreachableGround`, shapely's
/// erosion, refuses fewer).
#[must_use]
pub fn unreachable(p: Pt, rules: &Rules, tests: &mut Counts) -> bool {
    let (reach, slack, n) = REACH_FT;
    let r = reach + slack;
    on_hard(p, &rules.hard, tests)
        && (0..n).all(|k| {
            #[expect(clippy::cast_precision_loss, reason = "a circle's few dozen points")]
            let a = std::f64::consts::TAU * k as f64 / n as f64;
            on_hard((p.0 + r * a.cos(), p.1 + r * a.sin()), &rules.hard, tests)
        })
}

/// The key the registry files a fixture under, where it holds the fixture while the seating lasts.
fn held_key(k: Kind) -> Option<&'static str> {
    match k {
        Kind::Persimmon => None,
        Kind::Retirement => Some("retirement_houses"),
        _ => Some("farm_fixtures"),
    }
}

/// Do two rings meet - an edge of one crossing an edge of the other, or one standing inside the other?
fn rings_meet(a: &[Pt], b: &[Pt]) -> bool {
    let edges = |r: &[Pt]| {
        (0..r.len())
            .map(move |i| (r[i], r[(i + 1) % r.len()]))
            .collect::<Vec<_>>()
    };
    let (ea, eb) = (edges(a), edges(b));
    ea.iter()
        .any(|&(p, q)| eb.iter().any(|&(r, s)| segments_cross(p, q, r, s)))
        || a.first().is_some_and(|&p| in_poly(p, b))
        || b.first().is_some_and(|&p| in_poly(p, a))
}

/// Does the registry admit every part `b` lays - its house, yard, beds, annexes as turned and its held fixtures as drawn - none on
/// an extent the matrix forbids its key?
#[must_use]
pub fn admitted(b: &Bundle, rules: &Rules, tests: &mut Counts) -> bool {
    let turned = |r: Rect| corners(r, b.turn).to_vec();
    let mut parts: Vec<(&str, Vec<Pt>)> = vec![
        ("houses", turned(b.house)),
        ("threshing_yards", turned(b.yard)),
    ];
    parts.extend(b.gardens.iter().map(|&g| ("gardens", turned(g))));
    parts.extend(b.kura.map(|k| ("farm_sheds", turned(k))));
    parts.extend(b.byre.map(|(r, _)| ("byres", turned(r))));
    let first = 2 + b.gardens.len() + usize::from(b.kura.is_some()) + usize::from(b.byre.is_some());
    parts.extend(
        b.fixtures
            .iter()
            .zip(&b.boxes[first..])
            .filter_map(|(&(k, _), &bx)| held_key(k).map(|key| (key, corners(bx, 0.0).to_vec()))),
    );
    parts.iter().all(|(key, quad)| {
        let qb = poly_box(quad);
        rules
            .forbidding
            .iter()
            .filter(|(k, _)| k == key)
            .flat_map(|(_, rings)| rings)
            .all(|ring| {
                let rb = poly_box(ring);
                rb.2 < qb.0 || rb.0 > qb.2 || rb.3 < qb.1 || rb.1 > qb.3 || {
                    tests.add("seg_test@admitted", (quad.len() * ring.len()) as u64);
                    !rings_meet(quad, ring)
                }
            })
    })
}

/// Does a crown of radius `r` at `c` meet the plot's sun ground - the plot widened by `reach` east and west and deepened by it to
/// the south, from its north edge?
#[must_use]
pub fn crown_shades(c: Pt, r: f64, plot: Rect, reach: f64) -> bool {
    let (x0, x1) = (plot.0 - plot.2 / 2.0 - reach, plot.0 + plot.2 / 2.0 + reach);
    let (y0, y1) = (plot.1 - plot.3 / 2.0, plot.1 + plot.3 / 2.0 + reach);
    let (dx, dy) = (c.0 - c.0.clamp(x0, x1), c.1 - c.1.clamp(y0, y1));
    dx * dx + dy * dy < r * r
}

/// The persimmon of `b`, by its center, where it keeps one.
#[must_use]
pub fn persimmon_of(b: &Bundle) -> Option<Pt> {
    b.fixtures
        .iter()
        .find(|(k, _)| *k == Kind::Persimmon)
        .map(|&(_, r)| (r.0, r.1))
}

/// The persimmon's sun, both ways: this household's tree dropped where it shades its own plots or a standing neighbor's (its box
/// taken out with it); the seat refused where a standing neighbor's tree shades this household's plots. True where the seat is
/// refused. Asked only on a map that keeps the sun corridor.
pub fn persimmon_conflict(
    b: &mut Bundle,
    standing: &Standing,
    rules: &Rules,
    tests: &mut Counts,
) -> bool {
    if !rules.sun {
        return false;
    }
    let (crown, past, reach) = PERSIMMON_FT;
    let r = crown + past;
    let plots: Vec<Rect> = b.boxes[1..2 + b.gardens.len()].to_vec();
    let near = |lo: Pt, hi: Pt, tests: &mut Counts| standing.meeting(lo, hi, tests);
    if let Some(t) = persimmon_of(b) {
        let theirs = near(
            (t.0 - r - reach, t.1 - r - reach),
            (t.0 + r + reach, t.1 + r),
            tests,
        );
        let shades_own = plots.iter().any(|&p| crown_shades(t, r, p, reach));
        let shades_theirs = theirs.iter().any(|&k| {
            let p = &standing.all[k];
            std::iter::once(&p.yard)
                .chain(&p.beds)
                .any(|&q| crown_shades(t, r, q, reach))
        });
        if shades_own || shades_theirs {
            let k = b
                .fixtures
                .iter()
                .position(|(k, _)| *k == Kind::Persimmon)
                .unwrap_or(0);
            let at = 2
                + b.gardens.len()
                + usize::from(b.kura.is_some())
                + usize::from(b.byre.is_some())
                + k;
            b.fixtures.remove(k);
            b.boxes.remove(at);
        }
    }
    plots.iter().any(|&p| {
        let lo = (p.0 - p.2 / 2.0 - reach - r, p.1 - p.3 / 2.0 - r);
        let hi = (p.0 + p.2 / 2.0 + reach + r, p.1 + p.3 / 2.0 + reach + r);
        near(lo, hi, tests).iter().any(|&k| {
            tests.add("pt_test@persimmon_conflict", 1);
            standing.all[k]
                .persimmon
                .is_some_and(|t| crown_shades(t, r, p, reach))
        })
    })
}
