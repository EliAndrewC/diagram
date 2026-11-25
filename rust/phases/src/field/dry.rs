//! The dry plots (feature 444 T16): the hem of small grain plots just upslope of the supply canal, in tracts of strips square to it,
//! as many as the hamlet's coarse grain needs, climbing outward from the canal when one band will not hold it.
//!
//! Research:
//!     the dry hem - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a hem of small rectangular plots just upslope of the supply canal that runs along the paddy's high edge
//!     the need - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: about 0.85 acre a household, a GUESS resting on attested rates

use super::fan::Pt;
use super::geom::{dist, inside, seg_dist, unit};
use super::index::{bbox, Bands, Boxes, Index};
use crate::pyrand::knob_rng;

/// The coarse grain a household needs (acres).
///
/// Research:
///     the need - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: about 0.85 acre a household, beside its 1.3 acres of paddy
pub const GRAIN_ACRES_PER_HOUSEHOLD: f64 = 0.85;
/// A dry plot along the canal and out from it (feet): 0.15 acre on a hamlet map, in the village figure's proportion of 92 by 72.
///
/// Research:
///     the plot - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: roughly 92 ft across and 72 ft down a row on the village map; about 0.15 acre on the hamlet's
pub const PLOT_FT: (f64, f64) = (91.4, 71.5);
/// The bare bank between the canal and the first strip (feet).
///
/// Research:
///     the bank - GUESS: the record silent on its width, 0006 keeps the plots to the dry side behind a bare bank, not how wide; 6 ft
pub const BANK_FT: f64 = 6.0;
/// A tract's strips out from the canal.
///
/// Research:
///     a tract - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a tract is two to four strips of plots running upslope from the canal
pub const TRACT_STRIPS: (u32, u32) = (2, 4);
/// A tract's plots along the canal.
///
/// Research:
///     a tract's length - GUESS: the record silent on it, 0006 gives a tract's strips, not its length; 3 to 5 plots
pub const TRACT_PLOTS: (u32, u32) = (3, 5);
/// The most a tract's rows turn off the canal's line or its square, and a plot's own turn within its tract (degrees).
///
/// Research:
///     the turns - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: turned up to about 17 degrees; within a tract each plot turns about 3 degrees either way
pub const TURN_DEG: (u32, u32) = (17, 3);
/// The least angle between two tracts' rows (degrees).
///
/// Research:
///     tracts apart - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: tracts are set apart by at least 20 degrees, by a drawing convention - their rows' directions, the right angle between contour and down counted, against the tract beside each along its band and those directly downslope; where the turns allowed leave no such direction, the one farthest from them all (the page: two rows within about 6 degrees read as one)
pub const TRACT_APART_DEG: f64 = 20.0;
/// A bound on the bands the hem climbs: the climb itself ends where the grain is held or a whole band finds no ground.
///
/// Research:
///     the bound - NONE: a guard far past any canvas (64 bands, over a mile and a half); research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html has the plots climb out as far from the canal as the ground runs, until they hold the grain
pub const MAX_BANDS: u32 = 64;
/// How far a candidate's corners are pulled toward its middle before the lap test (feet): plots laid side by side share their
/// corners and edges exactly, which is no lap.
///
/// Research:
///     the pull - NONE: a tolerance of the geometry, under any plot's side
pub const LAP_PULL_FT: f64 = 1.0;
/// The least a strip's edge may run along its canal, as a share of a plot's length, before its column's climb ends.
///
/// Research:
///     the pinch - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html draws small rectangular plots of about a sixth of an acre and is silent on how far one may taper where the canal bends; half a plot's length, past which a strip reads as a sliver, not a plot
pub const PINCH_SHARE: f64 = 0.5;
/// The most a strip's edge may run, as a share of a plot's length, before the strip is cut into plots.
///
/// Research:
///     the stretch - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html draws each plot roughly 92 ft across, never dwarfing the rice basins, and is silent on a strip beside a canal bending away from the dry side; past one and a half plots' length a strip is cut into plots, the mirror of `PINCH_SHARE`
pub const STRETCH_SHARE: f64 = 1.5;
/// The dry crops (0006's four), each map drawing its own mix.
///
/// Research:
///     the crops - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: barley, millet, buckwheat and soybean; each map picks its mix of the four crops at random, a GUESS
pub const CROPS: [&str; 4] = ["barley", "millet", "buckwheat", "soy"];

/// One dry plot: its four corners, its crop, its furrows' bearing (radians on the maps' axes) and its tract.
///
/// Research:
///     a dry plot's record - NONE: the record's type, holding what `hem` decides
#[derive(Debug, Clone, PartialEq)]
pub struct DryPlot {
    pub poly: Vec<Pt>,
    pub crop: &'static str,
    pub theta: f64,
    pub tract: usize,
}

/// The hem along `line` (the canal's course, the plots' side `out` of it: the unit normal pointing upslope; `down` the fall), as many plots as
/// `need` square feet asks within at most `most_bands` bands, none inside `field`'s ring or within `clear` feet of the water filed in `ix`. Returns the plots, the
/// room the bands held (square feet) and the outline's edges tested against a point of a plot.
///
/// Research:
///     square to the canal - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: plots square to the canal and laid end to end along its curving line
///     rows on the contour or down - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: rows run either along the contour or down to its outfall, the two a right angle apart; even odds a tract between them, a GUESS (the page: the tract's size and the turns are GUESSES) - the contour square to the fall, not the canal's heading
///     not steep ground - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: on steep ground every tract runs the contour - the comb's hem stands on an alluvial fan's gentle fall, the steep ground's terraced form another archetype this stage does not draw, so its tracts take either
///     the hem's figures - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a tract two to four strips of plots running upslope from the canal (`TRACT_STRIPS`), its length along the canal a GUESS (`TRACT_PLOTS`); the plots begin behind the canal's bare bank (`BANK_FT`); each map's mix of the four crops at random (its one hem, on the first field), each plot one of the mix at even odds, a GUESS
///     the plot - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: roughly 92 ft across and 72 ft down a row (`PLOT_FT`), tiled along and up from the canal
///     the tracts apart - CONVENTION: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html sets tracts at least 20 degrees apart by a drawing convention (`apart`)
///     a band's strips - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html silent on whether a band's tracts run alike upslope; the strip count rolled once a band, every tract in it as deep
///     the climb - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the dry plots climb out as far from the canal as the ground runs, until they hold the grain the hamlet needs
///     the last band from the canal's start - GUESS: research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html silent on where along the canal the last of the plots stands; from its start, along it, until the need is met
///     the climb's bound - NONE: `MAX_BANDS`, a guard far past any canvas; the caller's `most_bands` the climb's own bound
///     a plot onto rice dropped - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot that would lap onto another canal's rice is dropped
///     the settlement's ground kept - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the houses between the canal and the dry fields, so a strip still on their ground past the push behind is dropped, not pushed further
///     a column's climb ends - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the dry plots climb from the toe into the middle, plot by plot - so a column's climb ends where its strip pinches under `PINCH_SHARE` of a plot's length, the columns square to a canal bending toward its dry side converging as they climb, and where its strip laps a plot another column laid, never coming out behind that plot; the settlement's ground is stepped over (0006's houses between), and a strip refused for the water or for the rice is passed by without ending the climb, the ground past an intake race still the hem's (a cleared middle's plots on the race's upslope side, 17 of 141 such rolls, measured 2026-11-24 over seeds 1 to 150 at three sizes; ending the climb at the rice as well changed no roll of 3,200, measured 2026-11-24 over seeds 1 to 400 at eight sizes and falls) - before 449 T423 it climbed on, and drew slivers and detached strips turned against the block they had crossed (seed 52 of 15 households falling at 225 degrees; a plot under half the plot's area on 77 of 98 bare-winter wild rolls, measured 2026-11-24 over seeds 1 to 150 at three sizes); where the pinch falls a GUESS (`PINCH_SHARE`)
///     a strip stretched round a bend cut into plots - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html draws each plot roughly 92 ft across, never dwarfing the rice basins, and is silent on a strip beside a canal bending away from the dry side - a strip whose edge runs past `STRETCH_SHARE` of a plot's length is cut across into plots (`cut`), each asked as a plot; before 449 T434 it was drawn whole, up to 15 plots' length, in 15,644 of 35,000 hem rolls (measured 2026-11-25)
#[expect(
    clippy::too_many_arguments,
    reason = "the hem's line, side, need, field, water, clearance, seed and tag"
)]
#[expect(
    clippy::too_many_lines,
    reason = "the climb in its order - band, tract, column, strip - each refusal where it is decided"
)]
#[must_use]
pub fn hem(
    line: &[Pt],
    out: Pt,
    down: Pt,
    (need, most_bands): (f64, u32),
    field: &[Pt],
    ix: &mut Index,
    clear: f64,
    seed: i64,
    tag: &str,
    keep: &[Vec<Pt>],
) -> (Vec<DryPlot>, f64, u64) {
    let mut rng = knob_rng(seed, &format!("{tag}:dry"));
    let mix: Vec<&'static str> = {
        let mask = 1 + rng.randbelow(15);
        CROPS
            .iter()
            .enumerate()
            .filter(|(i, _)| mask & (1 << i) != 0)
            .map(|(_, c)| *c)
            .collect()
    };
    let segs: Vec<(Pt, Pt)> = line.windows(2).map(|w| (w[0], w[1])).collect();
    if segs.is_empty() {
        return (Vec::new(), 0.0, 0);
    }
    let canal = Canal::new(segs, out);
    let len = canal.len();
    let fall = ((-down.1, down.0), down);
    let (mut plots, mut room, mut got, mut depth) = (Vec::new(), 0.0, 0.0, BANK_FT);
    // the plots laid so far, by cell: each candidate asks only the plots near it (the audit's square scan, T16)
    let mut laid = Boxes::default();
    // the field's outline by bands: each point tested against the edges of its own band, not a walk of the ring
    let mut bands = Bands::new(field);
    let mut tract = 0;
    // each band's tracts: their stretch along the canal and their rows' direction (degrees), the band below's kept for the next
    let mut below: Vec<(f64, f64, f64)> = Vec::new();
    let mut climbs = Climbs::default();
    // the strips under this band
    let mut under = 0;
    for _band in 0..most_bands.min(MAX_BANDS) {
        let strips = TRACT_STRIPS.0 + rng.randbelow(TRACT_STRIPS.1 - TRACT_STRIPS.0 + 1);
        let (mut d, mut column) = (0.0, 0_usize);
        let mut band: Vec<(f64, f64, f64)> = Vec::new();
        let placed_before = plots.len();
        'band: while d + PLOT_FT.0 <= len {
            let n = TRACT_PLOTS.0 + rng.randbelow(TRACT_PLOTS.1 - TRACT_PLOTS.0 + 1);
            // the tract's rows: on the contour or down to the outfall, turned up to 17 degrees, at least 20 from its neighbors'
            let rolled = (
                rng.randbelow(2) == 1,
                f64::from(rng.randbelow(2 * TURN_DEG.0 + 1)) - f64::from(TURN_DEG.0),
            );
            let span = (d, d + f64::from(n) * PLOT_FT.0);
            let near = neighbors(&band, &below, span, &mut ix.tests);
            // the grain held, no plot of the band's rest is laid and the climb ends with it: its tracts' rows are not asked
            let (down, turn) = if got >= need {
                rolled
            } else {
                apart(rolled, &near, &mut ix.tests)
            };
            band.push((span.0, span.1, turn + if down { 90.0 } else { 0.0 }));
            // each column's two frames found once, its strips' seats built from them, the next column taking the second
            let mut frames: Option<(Pt, Pt)> = None;
            for k in 0..n {
                let d0 = d + f64::from(k) * PLOT_FT.0;
                if d0 + PLOT_FT.0 > len {
                    break;
                }
                if got >= need {
                    room += room_left(len - d0, strips);
                    break 'band;
                }
                let (a, b) = canal.column(d0, &mut frames, &mut ix.tests);
                // THE SETTLEMENT'S GROUND KEPT: where the column's first strip would stand on the seat's band or its belt, its
                // strips are laid behind it, a strip's depth at a time until clear - the houses between the paddy and the dry
                // fields (0006)
                let behind = past_keep(a, b, depth, keep, &mut ix.tests);
                let (col, first) = (column + k as usize, under + strips_in(behind));
                for j in 0..strips {
                    let (o0, o1) = (
                        depth + behind + f64::from(j) * PLOT_FT.1,
                        depth + behind + f64::from(j + 1) * PLOT_FT.1,
                    );
                    // the grain held, the band's rest is room the hem did not take: no seat built (the audit, T16: each was
                    // built only to be counted as room)
                    room += PLOT_FT.0 * PLOT_FT.1;
                    // A COLUMN'S CLIMB (449 T423): a strip it already climbed is not asked again (a band pushed behind the settlement's
                    // ground lands on the strips the band before it laid there), and an ended column lays nothing more
                    if got >= need || !climbs.takes(col, first + j) {
                        continue;
                    }
                    let poly = Canal::seat(a, b, (o0, o1), &mut ix.tests);
                    // ...ENDED WHERE THE STRIP PINCHES: the column's two sides have run together, and past it they cross
                    if pinched((a.0, b.0), &poly) {
                        climbs.end(col);
                        continue;
                    }
                    // A STRIP STRETCHED ROUND A BEND IS CUT INTO PLOTS (449 T434): beside a canal bending away from the dry
                    // side the columns splay as they climb, and a strip drawn whole ran up to fifteen plots' length (the
                    // ground is kept, each piece asked as a plot)
                    let pieces = cut(&poly, &mut ix.tests);
                    room += PLOT_FT.0
                        * PLOT_FT.1
                        * f64::from(u32::try_from(pieces.len() - 1).unwrap_or(0));
                    for poly in pieces {
                        if got >= need {
                            break;
                        }
                        // EVERY STRIP OFF THE SETTLEMENT'S GROUND (feature 444 T42, the cohort's dry_on_settlement, 8 of 300 seeds):
                        // the push behind clears the column's first strip, and a ground set askew can still stand across a deeper one
                        let middle = (
                            f64::midpoint(poly[0].0, poly[2].0),
                            f64::midpoint(poly[0].1, poly[2].1),
                        );
                        if on_keep(&poly, middle, keep, &mut ix.tests) {
                            continue;
                        }
                        if let Some(why) =
                            refused(&poly, &mut bands, (&plots, &mut laid), ix, clear)
                        {
                            // ...AND WHERE IT MEETS ANOTHER COLUMN'S PLOTS: the ground behind them is not this column's to climb
                            if why == Refusal::Laps {
                                climbs.end(col);
                            }
                            continue;
                        }
                        let own =
                            f64::from(rng.randbelow(2 * TURN_DEG.1 + 1)) - f64::from(TURN_DEG.1);
                        // the rows on the contour, square to the fall (not the canal's heading: canals run diagonally to the fall), or
                        // down the fall to the outfall
                        let base = (if down { fall.1 } else { fall.0 })
                            .1
                            .atan2((if down { fall.1 } else { fall.0 }).0);
                        let crop =
                            mix[rng.randbelow(u32::try_from(mix.len()).unwrap_or(1)) as usize];
                        let (lo, hi) = bbox(&poly);
                        laid.file(lo, hi);
                        plots.push(DryPlot {
                            poly,
                            crop,
                            theta: base + (turn + own).to_radians(),
                            tract,
                        });
                        got += PLOT_FT.0 * PLOT_FT.1;
                    }
                }
            }
            tract += 1;
            d += f64::from(n) * PLOT_FT.0;
            column += n as usize;
        }
        depth += f64::from(strips) * PLOT_FT.1;
        under += strips;
        below = band;
        // the grain held, or a whole band without ground: the climb ends
        if got >= need || plots.len() == placed_before {
            break;
        }
    }
    ix.touched += laid.touched;
    ix.examined += laid.examined;
    (plots, room, bands.tested)
}

/// Each column's climb, by its place along the canal: the strip it has climbed to, and whether its climb has ended.
///
/// Research:
///     a column's climb - NONE: the record `hem` keeps of each column; what ends a climb is `hem`'s claim
#[derive(Default)]
struct Climbs(Vec<(u32, bool)>);

impl Climbs {
    /// Whether column `col` climbs to strip `slot` now - its climb not ended and the strip not one it already climbed - the
    /// strip then counted as climbed.
    ///
    /// Research:
    ///     a strip asked once - NONE: bookkeeping; a strip a column was already asked for stands or was refused, and neither changes
    fn takes(&mut self, col: usize, slot: u32) -> bool {
        if self.0.len() <= col {
            self.0.resize(col + 1, (0, false));
        }
        let climb = &mut self.0[col];
        if climb.1 || slot < climb.0 {
            return false;
        }
        climb.0 = slot + 1;
        true
    }

    /// Column `col`'s climb ended (it was asked for a strip first, so it is on the record).
    ///
    /// Research:
    ///     the end kept - NONE: bookkeeping of `hem`'s rule
    fn end(&mut self, col: usize) {
        self.0[col].1 = true;
    }
}

/// The whole strips in `ft` feet of depth.
///
/// Research:
///     the strips - NONE: arithmetic over the plot's depth, `PLOT_FT`'s
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "whole strips behind a column, a few dozen at most"
)]
fn strips_in(ft: f64) -> u32 {
    (ft / PLOT_FT.1).round() as u32
}

/// Whether a strip's seat `poly` has pinched: its inner or its outer edge runs under `PINCH_SHARE` of a plot's length along its
/// column's own stretch of the canal (`along`, the column's two points on it) - an edge whose ends have crossed runs backward.
///
/// Research:
///     the pinch - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html silent on how far a plot may taper; `PINCH_SHARE` of the plot's length, each edge measured along the canal where the column stands
fn pinched(along: (Pt, Pt), poly: &[Pt]) -> bool {
    let u = unit(along.0, along.1);
    let run = |p: Pt, q: Pt| (q.0 - p.0) * u.0 + (q.1 - p.1) * u.1;
    run(poly[0], poly[1]).min(run(poly[3], poly[2])) < PINCH_SHARE * PLOT_FT.0
}

/// Why a dry plot is refused: onto the rice, onto a plot laid before it, or in the water.
///
/// Research:
///     the refusal's name - NONE: the record's type; what each refusal ends is `hem`'s
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Refusal {
    Rice,
    Laps,
    Water,
}

/// The strip `poly` (inner edge `poly[0]`-`poly[1]`, outer `poly[3]`-`poly[2]`) as plots: whole where neither edge runs past
/// `STRETCH_SHARE` of a plot's length, else cut across into the whole number of pieces nearest its longer edge's plots, each
/// edge divided evenly - fewer where the shorter edge's pieces would run under `PINCH_SHARE`, that bound kept first. The pieces
/// built counted in `tests`.
///
/// Research:
///     a stretched strip cut - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html draws each plot roughly 92 ft across and is silent on a strip beside a canal bending away from the dry side; cutting it keeps the ground the hem climbs (room before packing), where ending the column's climb would drop the hem along such bends (9 percent of the strips asked beside the canal itself on 4,000 cohort combs, measured 2026-11-25), and the taper's half-plot bound holds before the stretch's
fn cut(poly: &[Pt], tests: &mut u64) -> Vec<Vec<Pt>> {
    let (inner, outer) = (dist(poly[0], poly[1]), dist(poly[3], poly[2]));
    let (longer, shorter) = (inner.max(outer), inner.min(outer));
    if longer <= STRETCH_SHARE * PLOT_FT.0 {
        return vec![poly.to_vec()];
    }
    let mut n = (longer / PLOT_FT.0).round();
    while n > 1.0 && shorter / n < PINCH_SHARE * PLOT_FT.0 {
        n -= 1.0;
    }
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a strip's pieces, a handful"
    )]
    let n = n as u32;
    *tests += u64::from(n);
    let at = |p: Pt, q: Pt, t: f64| (p.0 + (q.0 - p.0) * t, p.1 + (q.1 - p.1) * t);
    (0..n)
        .map(|k| {
            let (t0, t1) = (f64::from(k) / f64::from(n), f64::from(k + 1) / f64::from(n));
            vec![
                at(poly[0], poly[1], t0),
                at(poly[0], poly[1], t1),
                at(poly[3], poly[2], t1),
                at(poly[3], poly[2], t0),
            ]
        })
        .collect()
}

/// How far past `depth` a column's strips stand so their first is clear of the settlement's ground `keep` (feet): 0 where it
/// already is, else whole strips' depths until it is, at most as far as the ground's box reaches.
///
/// Research:
///     the dry fields behind the houses - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the hem drawn behind the settlement where it stands on the paddy's high edge, the houses between the canal and the dry fields; just upslope of the canal along the rest
///     the push behind - GUESS: no page gives the gap between the houses and their dry fields; a strip's depth (71.5 ft) at a time until the strip's corners and middle clear the ground and no corner of the ground stands in the strip, at most the ground's own diagonal and a strip past it
fn past_keep(a: (Pt, Pt), b: (Pt, Pt), depth: f64, keep: &[Vec<Pt>], tests: &mut u64) -> f64 {
    if keep.is_empty() {
        return 0.0;
    }
    let reach = keep
        .iter()
        .map(|k| {
            let (lo, hi) = bbox(k);
            dist(lo, hi)
        })
        .fold(0.0, f64::max);
    let mut behind = 0.0;
    loop {
        let poly = Canal::seat(a, b, (depth + behind, depth + behind + PLOT_FT.1), tests);
        let middle = (
            f64::midpoint(poly[0].0, poly[2].0),
            f64::midpoint(poly[0].1, poly[2].1),
        );
        let on = on_keep(&poly, middle, keep, tests);
        // clear of the ground, or past its own reach: no ground stands farther out than its box's diagonal
        if !on || behind > reach {
            return behind;
        }
        behind += PLOT_FT.1;
    }
}

/// Whether a strip `poly` stands on the settlement's ground `keep`: its middle or a corner inside a ground's ring, or a ground's
/// corner inside the strip (a box set askew pokes its corner into a strip whose own corners clear it); each test counted.
///
/// Research:
///     the overlap - NONE: a test of whether two grounds overlap; its callers decide what stays off the settlement's ground
fn on_keep(poly: &[Pt], middle: Pt, keep: &[Vec<Pt>], tests: &mut u64) -> bool {
    *tests += keep.iter().map(|k| 5 + k.len() as u64).sum::<u64>();
    keep.iter().any(|k| {
        inside(middle, k)
            || poly.iter().any(|c| inside(*c, k))
            || k.iter().any(|c| inside(*c, poly))
    })
}

/// The rows' directions a tract's neighbors run: the tract before it along its band, and those of the band below whose stretch
/// overlaps `span`; each of the band below's read counted in `tests` (the work-budget audit at T16's landing).
///
/// Research:
///     the neighbors - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a tract set apart from the tract beside it along its band and those directly downslope
fn neighbors(
    band: &[(f64, f64, f64)],
    below: &[(f64, f64, f64)],
    span: (f64, f64),
    tests: &mut u64,
) -> Vec<f64> {
    *tests += below.len() as u64;
    band.last()
        .map(|t| t.2)
        .into_iter()
        .chain(
            below
                .iter()
                .filter(|t| t.0 < span.1 && span.0 < t.1)
                .map(|t| t.2),
        )
        .collect()
}

/// The room a band's rest holds once the grain is held (square feet): its whole columns over the course still ahead, `ahead`
/// feet, each `strips` plots deep - counted at once, not walked (the work-budget audit at T16's landing: every column and strip
/// was visited only to add to the room).
///
/// Research:
///     the room - NONE: arithmetic over the plot's size, `PLOT_FT`'s
fn room_left(ahead: f64, strips: u32) -> f64 {
    (ahead / PLOT_FT.0).floor() * f64::from(strips) * PLOT_FT.0 * PLOT_FT.1
}

/// The rows' direction for a tract rolled `rolled` (down to the outfall, and its turn in degrees) whose neighbors' rows run `near`
/// (degrees, the right angle counted): the rolled one if it stands `TRACT_APART_DEG` from each, else the nearest to it that does
/// (keeping the rolled side first), else the one farthest from them all.
///
/// Research:
///     tracts apart - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: tracts are set apart by at least 20 degrees, turned up to about 17 degrees, the two directions a right angle apart
///     where none stands apart - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html silent on a tract whose neighbors leave no turn 20 degrees from them on either side; the turn farthest from them all, of the range's ends and the turns midway between them, though under 20 degrees
fn apart(rolled: (bool, f64), near: &[f64], tests: &mut u64) -> (bool, f64) {
    let mut gap = |a: f64| {
        *tests += near.len() as u64;
        near.iter()
            .map(|b| {
                let s = (a - b).rem_euclid(180.0);
                s.min(180.0 - s)
            })
            .fold(f64::INFINITY, f64::min)
    };
    let most = f64::from(TURN_DEG.0);
    let sides = [rolled.0, !rolled.0];
    // CONSTRUCTED, NOT SEARCHED (the round arbiter on ask:444-T16-field-budget-cheaper; MODE BUDGET's ninth verdict): on a side,
    // the turns that stand apart are the range less each neighbor's window `TRACT_APART_DEG` either side of it, so the nearest to
    // the roll is the roll itself or a window's edge - those few asked, not every turn in cost order (about 38 tests a tract
    // where the neighbors share the roll's side, the record's measure of the scan; about 4 now)
    if gap(rolled.1 + if rolled.0 { 90.0 } else { 0.0 }) >= TRACT_APART_DEG {
        return rolled; // the roll itself stands apart: nothing else asked
    }
    for down in sides {
        let base = if down { 90.0 } else { 0.0 };
        let mut cands = if down == rolled.0 {
            Vec::new()
        } else {
            vec![rolled.1]
        };
        for b in near {
            let c = (b - base + 90.0).rem_euclid(180.0) - 90.0;
            cands.extend(
                [c - TRACT_APART_DEG, c + TRACT_APART_DEG]
                    .into_iter()
                    .filter(|e| (-most..=most).contains(e)),
            );
        }
        let best = cands
            .into_iter()
            .filter(|t| gap(t + base) >= TRACT_APART_DEG)
            .min_by(|a, b| {
                ((a - rolled.1).abs(), *a)
                    .partial_cmp(&((b - rolled.1).abs(), *b))
                    .unwrap_or(std::cmp::Ordering::Equal)
            });
        if let Some(t) = best {
            return (down, t);
        }
    }
    // ...else the one farthest from them all: on each side the range's ends and the turns midway between neighbors' windows
    let mut best = (rolled, f64::NEG_INFINITY);
    for down in sides {
        let base = if down { 90.0 } else { 0.0 };
        let mut cs: Vec<f64> = near
            .iter()
            .map(|b| (b - base + 90.0).rem_euclid(180.0) - 90.0)
            .collect();
        cs.sort_by(f64::total_cmp);
        let mids = cs.windows(2).map(|w| f64::midpoint(w[0], w[1]).floor());
        for t in [-most, most].into_iter().chain(mids) {
            if (-most..=most).contains(&t) {
                let g = gap(t + base);
                if g > best.1 {
                    best = ((down, t), g);
                }
            }
        }
    }
    best.0
}

/// The canal's course as the hem lays along it: its segments, the distance along it at each segment's start, and the one side
/// the plots stand (`side`: +1 to the left of the course's direction, -1 to the right), fixed once for the whole course from its
/// first segment against `out`, so the plots stand on the same side of every leg - along the head, where the course runs square
/// to `out`, the side read a segment at a time flipped at random and folded plots back onto the rice (the audit, T16).
///
/// Research:
///     the canal's course - NONE: geometry, the line the hem follows and the side it stands
struct Canal {
    segs: Vec<(Pt, Pt)>,
    starts: Vec<f64>,
    side: f64,
    /// The segment the last lookup found: the hem asks the course in order along it, so each lookup steps from here
    cursor: std::cell::Cell<usize>,
}

impl Canal {
    /// The canal's segments with their running starts, its side fixed once from the first segment against `out`.
    ///
    /// Research:
    ///     the canal's measure - NONE: geometry, the line the hem follows
    fn new(segs: Vec<(Pt, Pt)>, out: Pt) -> Self {
        let mut starts = Vec::with_capacity(segs.len() + 1);
        let mut d = 0.0;
        for (a, b) in &segs {
            starts.push(d);
            d += dist(*a, *b);
        }
        starts.push(d);
        let u = unit(segs[0].0, segs[0].1);
        let side = if -u.1 * out.0 + u.0 * out.1 >= 0.0 {
            1.0
        } else {
            -1.0
        };
        Self {
            segs,
            starts,
            side,
            cursor: std::cell::Cell::new(0),
        }
    }

    /// The canal's whole length.
    ///
    /// Research:
    ///     the canal's measure - NONE: geometry, the line the hem follows
    fn len(&self) -> f64 {
        self.starts[self.segs.len()]
    }

    /// The point `d` feet along the course, and its heading there (past the end, the last segment's end): the segment found by
    /// a binary search of the distances, not a walk from the start.
    #[expect(
        clippy::many_single_char_names,
        reason = "the plane geometry's own names"
    )]
    /// The point at `d` along the canal and its heading there.
    ///
    /// Research:
    ///     the canal's measure - NONE: geometry, the line the hem follows
    fn along(&self, d: f64) -> (Pt, Pt) {
        // the last segment starting at or before `d` (the first, before the start): stepped to from the last lookup's, the hem's
        // lookups moving forward along the course (the work-budget audit, T16: a binary search a lookup)
        let n = self.segs.len();
        let mut k = self.cursor.get().min(n - 1);
        while k + 1 < n && self.starts[k + 1] <= d {
            k += 1;
        }
        while k > 0 && self.starts[k] > d {
            k -= 1;
        }
        self.cursor.set(k);
        let (a, b) = self.segs[k];
        let u = unit(a, b);
        let t = (d - self.starts[k]).clamp(0.0, dist(a, b));
        ((a.0 + u.0 * t, a.1 + u.1 * t), u)
    }

    /// A plot's seat between the frames `a` and `b` (`frame` at its two ends along the course), `o.0` to `o.1` feet out: the
    /// canal's own course pushed out along its smoothed normal, so neighbors share their sides and the bands nest and the hem
    /// follows the canal as a hem does - four offsets, counted in `work` with the hem's tests.
    ///
    /// Research:
    ///     the seat - NONE: geometry of the canal's course; the plot's size and where the hem stands are `PLOT_FT`'s and `hem`'s
    fn seat(a: (Pt, Pt), b: (Pt, Pt), (o0, o1): (f64, f64), work: &mut u64) -> Vec<Pt> {
        *work += 4;
        let at = |f: (Pt, Pt), o: f64| (f.0 .0 + f.1 .0 * o, f.0 .1 + f.1 .1 * o);
        vec![at(a, o0), at(b, o0), at(b, o1), at(a, o1)]
    }

    /// A column's two frames at `d` and a plot's length past it, the first the last column's second where there is one (`frames`
    /// keeps it).
    ///
    /// Research:
    ///     the column's frames - NONE: plumbing of the canal's course; the need is `hem`'s caller's
    fn column(
        &self,
        d: f64,
        frames: &mut Option<(Pt, Pt)>,
        work: &mut u64,
    ) -> ((Pt, Pt), (Pt, Pt)) {
        let a = frames.unwrap_or_else(|| self.frame(d, work));
        let b = self.frame(d + PLOT_FT.0, work);
        *frames = Some(b);
        (a, b)
    }

    /// The point `d` feet along the course and its normal to the hem's side, smoothed over a plot's length either way: three
    /// lookups, counted in `work`; a column of seats shares its two frames, the next column the second.
    ///
    /// Research:
    ///     square to the canal - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: each plot a rectangle square to the canal where it stands, the project's choice - the normal to the course's local line, taken over a plot's length either way, not to the paddy's slope
    fn frame(&self, d: f64, work: &mut u64) -> (Pt, Pt) {
        *work += 3;
        let (p, _) = self.along(d);
        let u = unit(
            self.along((d - PLOT_FT.0).max(0.0)).0,
            self.along(d + PLOT_FT.0).0,
        );
        (p, (-u.1 * self.side, u.0 * self.side))
    }
}

/// Whether a dry plot is refused, and why: onto the rice (its middle or its outer corners in the field - its inner edge may lie on the
/// canal's bank), onto a plot an earlier tract laid (either's middle in the other, or its corners in the laid one), or in the water along its inner edge, where a bend of the canal may meet it,
/// or at its outer corners.
///
/// Research:
///     a plot onto rice dropped - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot that would lap onto another canal's rice is dropped
///     off the water - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html silent on how near the water a dry plot may come; a plot any of whose edges comes within `clear` past a filed water's half-width, or that holds a water's end, dropped - a bend of the canal meeting it
fn refused(
    poly: &[Pt],
    field: &mut Bands,
    (plots, laid): (&[DryPlot], &mut Boxes),
    ix: &mut Index,
    clear: f64,
) -> Option<Refusal> {
    let middle = (
        f64::midpoint(poly[0].0, poly[2].0),
        f64::midpoint(poly[0].1, poly[2].1),
    );
    // each test asked only if the one before it passed, the cheapest first (the audit, T16)
    let mut onto = || [middle, poly[2], poly[3]].iter().any(|p| field.inside(*p));
    let mut laps = || {
        let (lo, hi) = bbox(poly);
        // each corner pulled a foot toward the middle: a neighbor's shared corner and edge are not a lap (the corners exactly
        // on a laid plot's edge read inside it, and refused about a plot a candidate - the audit, T16)
        let pulled: Vec<Pt> = poly
            .iter()
            .map(|c| {
                let u = unit(*c, middle);
                (c.0 + u.0 * LAP_PULL_FT, c.1 + u.1 * LAP_PULL_FT)
            })
            .collect();
        let mut tests = 0_u64;
        let hit = laid.near(lo, hi).into_iter().any(|i| {
            let q = &plots[i].poly;
            tests += 2;
            // ...AND THE LAID PLOT'S MIDDLE IN THE CANDIDATE (feature 444 T42's map checks, cohort seeds 320 and 994): a sliver laid at a
            // bend lay wholly inside a later, larger plot, none of whose corners stood in the sliver
            let q_middle = (f64::midpoint(q[0].0, q[2].0), f64::midpoint(q[0].1, q[2].1));
            inside(middle, q)
                || inside(q_middle, poly)
                || pulled.iter().any(|c| {
                    tests += 1;
                    inside(*c, q)
                })
                // ...AND THE LAID PLOT'S CORNERS IN THE CANDIDATE (feature 444 T36, `make seeds`' fresh comb seed 549270514): two
                // slanted plots crossed with two of the laid sliver's corners inside the later plot, though neither middle stood in
                // the other and none of the later plot's corners stood in the sliver - each pulled a foot toward its own middle, as
                // the candidate's are, so a shared corner or edge is still no lap
                || q.iter().any(|c| {
                    tests += 1;
                    let u = unit(*c, q_middle);
                    inside((c.0 + u.0 * LAP_PULL_FT, c.1 + u.1 * LAP_PULL_FT), poly)
                })
        });
        (hit, tests)
    };
    if onto() {
        return Some(Refusal::Rice);
    }
    let (lapped, tests) = laps();
    ix.tests += tests;
    if lapped {
        return Some(Refusal::Laps);
    }
    wet(poly, ix, clear).then_some(Refusal::Water)
}

/// Whether the plot `poly` meets the water filed in `ix`: a segment near it crossing its sides, ending inside it, or within `clear`
/// feet past its own half-width of a side.
///
/// Research:
///     the water test - NONE: geometry against the filed water; what it keeps a plot off is `hem`'s and `refused`'s
fn wet(poly: &[Pt], ix: &mut Index, clear: f64) -> bool {
    let reach = clear + ix.widest / 2.0;
    let (lo, hi) = bbox(poly);
    ix.near((lo.0 - reach, lo.1 - reach), (hi.0 + reach, hi.1 + reach))
        .into_iter()
        .collect::<Vec<_>>()
        .into_iter()
        .any(|i| {
            let (a, b) = ix.segs[i];
            let near = clear + ix.widths[i] / 2.0;
            ix.tests += 2;
            inside(a, poly)
                || inside(b, poly)
                || (0..poly.len()).any(|k| {
                    ix.tests += 1;
                    seg_seg_dist(a, b, poly[k], poly[(k + 1) % poly.len()]) < near
                })
        })
}

/// The least distance between two segments: zero where they cross.
///
/// Research:
///     the distance - NONE: geometry
pub(crate) fn seg_seg_dist(a: Pt, b: Pt, c: Pt, d: Pt) -> f64 {
    let side = |p: Pt, q: Pt, r: Pt| (q.0 - p.0) * (r.1 - p.1) - (q.1 - p.1) * (r.0 - p.0);
    let (d1, d2, d3, d4) = (side(c, d, a), side(c, d, b), side(a, b, c), side(a, b, d));
    if d1 * d2 < 0.0 && d3 * d4 < 0.0 {
        return 0.0;
    }
    seg_dist(a, c, d)
        .min(seg_dist(b, c, d))
        .min(seg_dist(c, a, b))
        .min(seg_dist(d, a, b))
}

#[cfg(test)]
mod tests;
