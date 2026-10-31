//! The dry plots (feature 444 T16): the hem of small grain plots just upslope of the supply canal, in tracts of strips square to it,
//! as many as the hamlet's coarse grain needs, climbing outward from the canal when one band will not hold it.
//!
//! Research:
//!     the dry hem - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a hem of small rectangular plots just upslope of the supply canal that runs along the paddy's high edge
//!     the need - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: about 0.85 acre a household, a GUESS resting on attested rates

use super::fan::Pt;
use super::geom::{dist, inside, seg_dist, unit};
use super::index::Index;
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
///     the bank - GUESS: the record silent on its width; 0006 keeps the plots to the dry side behind a bare bank, not how wide; 6 ft
pub const BANK_FT: f64 = 6.0;
/// A tract's strips out from the canal.
///
/// Research:
///     a tract - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a tract is two to four strips of plots running upslope from the canal
pub const TRACT_STRIPS: (u32, u32) = (2, 4);
/// A tract's plots along the canal.
///
/// Research:
///     a tract's length - GUESS: the record silent on it; 0006 gives a tract's strips, not its length; 3 to 5 plots
pub const TRACT_PLOTS: (u32, u32) = (3, 5);
/// The most a tract's rows turn off the canal's line or its square, and a plot's own turn within its tract (degrees).
///
/// Research:
///     the turns - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: turned up to about 17 degrees; within a tract each plot turns about 3 degrees either way
pub const TURN_DEG: (u32, u32) = (17, 3);
/// The least angle between two tracts' rows (degrees).
///
/// Research:
///     tracts apart - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: tracts are set apart by at least 20 degrees, by a drawing convention
pub const TRACT_APART_DEG: f64 = 20.0;
/// The bands of tracts the hem may climb to (a bound on the room: past it the need is left unmet and the meta says so).
///
/// Research:
///     the room - GUESS: the record sets no limit; eight bands of tracts, about a quarter mile of dry ground
pub const MAX_BANDS: u32 = 8;
/// The dry crops (0006's four), each map drawing its own mix.
///
/// Research:
///     the crops - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: barley, millet, buckwheat and soybean; each map picks its mix of the four crops at random, a GUESS
pub const CROPS: [&str; 4] = ["barley", "millet", "buckwheat", "soy"];

/// One dry plot: its four corners, its crop, its furrows' bearing (radians on the maps' axes) and its tract.
#[derive(Debug, Clone, PartialEq)]
pub struct DryPlot {
    pub poly: Vec<Pt>,
    pub crop: &'static str,
    pub theta: f64,
    pub tract: usize,
}

/// The hem along `line` (the canal's course, the plots' side `out` of it: the unit normal pointing upslope), as many plots as
/// `need` square feet asks, none inside `field`'s ring or within `clear` feet of the water filed in `ix`. Returns the plots and the
/// room the bands held (square feet).
///
/// Research:
///     square to the canal - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: plots square to the canal and laid end to end along its curving line
///     rows on the contour or down - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: rows run either along the contour or down to its outfall, the two a right angle apart
///     a plot onto rice dropped - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot that would lap onto another canal's rice is dropped
#[expect(
    clippy::too_many_arguments,
    reason = "the hem's line, side, need, field, water, clearance, seed and tag"
)]
#[must_use]
pub fn hem(
    line: &[Pt],
    out: Pt,
    need: f64,
    field: &[Pt],
    ix: &mut Index,
    clear: f64,
    seed: i64,
    tag: &str,
) -> (Vec<DryPlot>, f64) {
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
    let len: f64 = line.windows(2).map(|w| dist(w[0], w[1])).sum();
    let segs: Vec<(Pt, Pt)> = line.windows(2).map(|w| (w[0], w[1])).collect();
    if segs.is_empty() {
        return (Vec::new(), 0.0);
    }
    let along_at = |d: f64| along(&segs, d);
    let (mut plots, mut room, mut got, mut depth) = (Vec::new(), 0.0, 0.0, BANK_FT);
    let mut last_turn: Option<f64> = None;
    let mut tract = 0;
    for _band in 0..MAX_BANDS {
        let strips = TRACT_STRIPS.0 + rng.randbelow(TRACT_STRIPS.1 - TRACT_STRIPS.0 + 1);
        let mut d = 0.0;
        while d + PLOT_FT.0 <= len {
            let n = TRACT_PLOTS.0 + rng.randbelow(TRACT_PLOTS.1 - TRACT_PLOTS.0 + 1);
            // the tract's rows: on the contour or down to the outfall, turned up to 17 degrees, at least 20 from the last tract's
            let down = rng.randbelow(2) == 1;
            let mut turn = f64::from(rng.randbelow(2 * TURN_DEG.0 + 1)) - f64::from(TURN_DEG.0);
            if let Some(prev) = last_turn {
                if (turn - prev).abs() < TRACT_APART_DEG {
                    turn = if prev >= 0.0 {
                        prev - TRACT_APART_DEG
                    } else {
                        prev + TRACT_APART_DEG
                    };
                }
            }
            last_turn = Some(turn);
            // the tract's heading, for its furrows: its stretch of the canal's
            let u = unit(along_at(d).0, along_at(d + f64::from(n) * PLOT_FT.0).0);
            for k in 0..n {
                let d0 = d + f64::from(k) * PLOT_FT.0;
                if d0 + PLOT_FT.0 > len {
                    break;
                }
                for j in 0..strips {
                    let (o0, o1) = (
                        depth + f64::from(j) * PLOT_FT.1,
                        depth + f64::from(j + 1) * PLOT_FT.1,
                    );
                    // the canal's own course pushed out along its smoothed normal: neighbors share their sides and the bands
                    // nest, so the hem follows the canal as a hem does
                    let poly = vec![
                        offset(&segs, out, d0, o0),
                        offset(&segs, out, d0 + PLOT_FT.0, o0),
                        offset(&segs, out, d0 + PLOT_FT.0, o1),
                        offset(&segs, out, d0, o1),
                    ];
                    room += PLOT_FT.0 * PLOT_FT.1;
                    if got >= need || refused(&poly, field, &plots, ix, clear) {
                        continue;
                    }
                    let own = f64::from(rng.randbelow(2 * TURN_DEG.1 + 1)) - f64::from(TURN_DEG.1);
                    let base = u.1.atan2(u.0)
                        + if down {
                            std::f64::consts::FRAC_PI_2
                        } else {
                            0.0
                        };
                    let crop = mix[rng.randbelow(u32::try_from(mix.len()).unwrap_or(1)) as usize];
                    plots.push(DryPlot {
                        poly,
                        crop,
                        theta: base + (turn + own).to_radians(),
                        tract,
                    });
                    got += PLOT_FT.0 * PLOT_FT.1;
                }
            }
            tract += 1;
            d += f64::from(n) * PLOT_FT.0;
        }
        depth += f64::from(strips) * PLOT_FT.1;
        if got >= need {
            break;
        }
    }
    (plots, room)
}

/// The point `d` feet along the segments pushed `o` feet out along their normal there, the normal smoothed over a plot's length
/// either way and turned to `out`'s side.
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn offset(segs: &[(Pt, Pt)], out: Pt, d: f64, o: f64) -> Pt {
    let (p, _) = along(segs, d);
    let u = unit(
        along(segs, (d - PLOT_FT.0).max(0.0)).0,
        along(segs, d + PLOT_FT.0).0,
    );
    let n = if -u.1 * out.0 + u.0 * out.1 >= 0.0 {
        (-u.1, u.0)
    } else {
        (u.1, -u.0)
    };
    (p.0 + n.0 * o, p.1 + n.1 * o)
}

/// The point `d` feet along the segments, and their heading there (past the end, the last segment's end).
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn along(segs: &[(Pt, Pt)], d: f64) -> (Pt, Pt) {
    let mut left = d;
    let mut k = 0;
    while k + 1 < segs.len() && left > dist(segs[k].0, segs[k].1) {
        left -= dist(segs[k].0, segs[k].1);
        k += 1;
    }
    let (a, b) = segs[k];
    let u = unit(a, b);
    let t = left.min(dist(a, b));
    ((a.0 + u.0 * t, a.1 + u.1 * t), u)
}

/// Whether a dry plot is refused: onto the rice (its middle or its outer corners in the field - its inner edge may lie on the
/// canal's bank), onto a plot an earlier tract laid, or in the water along its inner edge, where a bend of the canal may meet it,
/// or at its outer corners.
///
/// Research:
///     a plot onto rice dropped - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot that would lap onto another canal's rice is dropped
fn refused(poly: &[Pt], field: &[Pt], plots: &[DryPlot], ix: &mut Index, clear: f64) -> bool {
    let middle = (
        f64::midpoint(poly[0].0, poly[2].0),
        f64::midpoint(poly[0].1, poly[2].1),
    );
    let onto = [middle, poly[2], poly[3]].iter().any(|p| inside(*p, field));
    let laps = plots
        .iter()
        .any(|q| inside(middle, &q.poly) || poly.iter().any(|c| inside(*c, &q.poly)));
    onto || laps || wet(poly, ix, clear)
}

/// Whether the plot `poly` meets the water filed in `ix`: a segment near it crossing its sides, ending inside it, or within `clear`
/// feet past its own half-width of a side.
fn wet(poly: &[Pt], ix: &mut Index, clear: f64) -> bool {
    let reach = clear + ix.widths.iter().copied().fold(0.0, f64::max) / 2.0;
    let (lo, hi) = poly.iter().fold(
        (
            (f64::INFINITY, f64::INFINITY),
            (f64::NEG_INFINITY, f64::NEG_INFINITY),
        ),
        |(l, h), p| ((l.0.min(p.0), l.1.min(p.1)), (h.0.max(p.0), h.1.max(p.1))),
    );
    ix.near((lo.0 - reach, lo.1 - reach), (hi.0 + reach, hi.1 + reach))
        .into_iter()
        .any(|i| {
            let (a, b) = ix.segs[i];
            let near = clear + ix.widths[i] / 2.0;
            inside(a, poly)
                || inside(b, poly)
                || (0..poly.len())
                    .any(|k| seg_seg_dist(a, b, poly[k], poly[(k + 1) % poly.len()]) < near)
        })
}

/// The least distance between two segments: zero where they cross.
fn seg_seg_dist(a: Pt, b: Pt, c: Pt, d: Pt) -> f64 {
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
mod tests {
    use super::{hem, GRAIN_ACRES_PER_HOUSEHOLD, PLOT_FT, TRACT_APART_DEG};
    use crate::field::geom::inside;
    use crate::field::index::Index;

    #[test]
    fn the_hem_holds_the_need_outside_the_field() {
        let line = [(0.0, 0.0), (0.0, 1200.0)];
        let field = [(1.0, -10.0), (900.0, -10.0), (900.0, 1300.0), (1.0, 1300.0)];
        let need = 15.0 * GRAIN_ACRES_PER_HOUSEHOLD * 43_560.0;
        let mut ix = Index::default();
        let (plots, room) = hem(&line, (-1.0, 0.0), need, &field, &mut ix, 4.0, 4, "f0");
        #[expect(clippy::cast_precision_loss, reason = "a hundred plots")]
        let got = plots.len() as f64 * PLOT_FT.0 * PLOT_FT.1;
        assert!(got >= need && got < need + 2.0 * PLOT_FT.0 * PLOT_FT.1 * 4.0);
        assert!(room >= got);
        assert!(plots
            .iter()
            .all(|p| p.poly.iter().all(|c| !inside(*c, &field) && c.0 < 0.0)));
        let mut tracts: Vec<_> = plots.iter().map(|p| p.tract).collect();
        tracts.dedup();
        assert!(tracts.len() > 2);
        let _ = TRACT_APART_DEG;
        // none where the water is
        let mut wet = Index::default();
        wet.file((-200.0, 0.0), (-200.0, 1200.0));
        // a brook through a plot's middle, its ends outside it, refuses it
        let mut through = Index::default();
        through.file_w((-50.0, -100.0), (-50.0, 2000.0), 7.0);
        let (crossed, _) = hem(&line, (-1.0, 0.0), need, &field, &mut through, 1.0, 4, "f0");
        assert!(crossed
            .iter()
            .all(|p| p.poly.iter().all(|c| c.0 > -46.0) || p.poly.iter().all(|c| c.0 < -54.0)));
        let (dry, _) = hem(&line, (-1.0, 0.0), need, &field, &mut wet, 5000.0, 4, "f0");
        assert!(dry.is_empty());
        let (none, _) = hem(
            &line,
            (-1.0, 0.0),
            0.0,
            &field,
            &mut Index::default(),
            4.0,
            4,
            "f0",
        );
        assert!(none.is_empty(), "no need, no plots");
        let (short, _) = hem(
            &[(0.0, 0.0), (0.0, 10.0)],
            (-1.0, 0.0),
            need,
            &field,
            &mut Index::default(),
            4.0,
            4,
            "f0",
        );
        let (dot, _) = hem(
            &[(0.0, 0.0)],
            (-1.0, 0.0),
            need,
            &field,
            &mut Index::default(),
            4.0,
            4,
            "f0",
        );
        assert!(dot.is_empty());
        // the other side of the canal: the normal turned to it
        let (east, _) = hem(
            &line,
            (1.0, 0.0),
            need,
            &[],
            &mut Index::default(),
            4.0,
            4,
            "f0",
        );
        assert!(east.iter().all(|p| p.poly.iter().all(|c| c.0 >= -1e-9)));
        assert!(short.is_empty());
    }
}
