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
///     the bank - GUESS: 0006 keeps the plots to the dry side behind a bare bank, not how wide; 6 ft
pub const BANK_FT: f64 = 6.0;
/// A tract's strips out from the canal.
///
/// Research:
///     a tract - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a tract is two to four strips of plots running upslope from the canal
pub const TRACT_STRIPS: (u32, u32) = (2, 4);
/// A tract's plots along the canal.
///
/// Research:
///     a tract's length - GUESS: 0006 gives a tract's strips, not its length; 3 to 5 plots
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
            for k in 0..n {
                let d0 = d + f64::from(k) * PLOT_FT.0;
                if d0 + PLOT_FT.0 > len {
                    break;
                }
                let ((p0, u), (p1, _)) = (along_at(d0), along_at(d0 + PLOT_FT.0));
                // square to the canal where it runs: its own normal, turned to the upslope side
                let n = if -u.1 * out.0 + u.0 * out.1 >= 0.0 {
                    (-u.1, u.0)
                } else {
                    (u.1, -u.0)
                };
                for j in 0..strips {
                    let (o0, o1) = (
                        depth + f64::from(j) * PLOT_FT.1,
                        depth + f64::from(j + 1) * PLOT_FT.1,
                    );
                    let poly = vec![
                        (p0.0 + n.0 * o0, p0.1 + n.1 * o0),
                        (p1.0 + n.0 * o0, p1.1 + n.1 * o0),
                        (p1.0 + n.0 * o1, p1.1 + n.1 * o1),
                        (p0.0 + n.0 * o1, p0.1 + n.1 * o1),
                    ];
                    room += PLOT_FT.0 * PLOT_FT.1;
                    // a plot onto the rice is dropped: its middle or its outer corners in the field (its inner edge may lie on the canal's bank)
                    let middle = (
                        f64::midpoint(poly[0].0, poly[2].0),
                        f64::midpoint(poly[0].1, poly[2].1),
                    );
                    let onto = [middle, poly[2], poly[3]].iter().any(|p| inside(*p, field));
                    if got >= need || onto || poly.iter().any(|p| wet(*p, ix, clear)) {
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

/// Whether `p` lies within `clear` feet of the water filed in `ix`.
fn wet(p: Pt, ix: &mut Index, clear: f64) -> bool {
    ix.near((p.0 - clear, p.1 - clear), (p.0 + clear, p.1 + clear))
        .into_iter()
        .any(|i| {
            let (a, b) = ix.segs[i];
            seg_dist(p, a, b) < clear
        })
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
