//! A dike-pond's pond and bank rounded from its parcel (feature 444 T16 D8): the parcel's four-sided ring shrunk about its middle by
//! the bank's inset, each corner rounded on a curve whose cut-back is rolled about the reach, so no two ponds are alike and every
//! one stays four-sided. Written new from the shape's contract (measured by calling the old `_rounded_pond`, its body unread) and
//! the record.
//!
//! Research:
//!     ponds of uneven shape - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: ponds of uneven shape, each ringed by a bank of its own mud
//!     every pond four-sided - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the mosaic bends the lattice but keeps every pond four-sided

use std::fmt::Write;

use super::fan::Pt;
use crate::pyrand::PyRandom;

/// How far a corner's cut-back strays from the reach, either way (a share of it).
///
/// Research:
///     the corner's stray - GUESS: the record gives ponds of uneven shape, not a figure; 15% of the reach either way
pub const CUT_STRAY: f64 = 0.15;
/// The least a pond keeps of its parcel's span where the bank asks more than the parcel holds (a share about its middle).
///
/// Research:
///     the least pond - GUESS research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#least-pond: a parcel too small for its bank still gets a pond, the water drawn a tenth of the parcel across
pub const LEAST_SHARE: f64 = 0.1;

/// `ring` pushed in `by` feet on every side: each side's line moved inward along its normal, the corners where neighboring lines
/// meet. `None` where the bank asks more than the ring holds (the result turned inside out or a corner run off).
///
/// Research:
///     the offset - NONE: geometry
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn pushed_in(ring: &[Pt], by: f64) -> Option<Vec<Pt>> {
    let n = ring.len();
    let turn = if super::geom::signed_area(ring) >= 0.0 {
        1.0
    } else {
        -1.0
    };
    // each side's line moved inward: a point on it and its direction
    let lines: Vec<(Pt, Pt)> = (0..n)
        .map(|i| {
            let (a, b) = (ring[i], ring[(i + 1) % n]);
            let u = super::geom::unit(a, b);
            let inward = (-u.1 * turn, u.0 * turn);
            ((a.0 + inward.0 * by, a.1 + inward.1 * by), u)
        })
        .collect();
    let mut out = Vec::with_capacity(n);
    for i in 0..n {
        let ((p, u), (q, v)) = (lines[(i + n - 1) % n], lines[i]);
        let cross = u.0 * v.1 - u.1 * v.0;
        if cross.abs() < 1e-9 {
            out.push(q);
            continue;
        }
        let t = ((q.0 - p.0) * v.1 - (q.1 - p.1) * v.0) / cross;
        out.push((p.0 + u.0 * t, p.1 + u.1 * t));
    }
    let kept = super::geom::signed_area(&out);
    // ...NEVER GROWN, and kept whole at no inset (the glyph check of Kuwabata's fish ponds, feature 444 T16): a strict `<` refused
    // the ring itself at `by` 0, so the bank fell back to a speck a tenth across, under the water
    (kept * turn > 0.0 && kept.abs() <= super::geom::signed_area(ring).abs() * (1.0 + 1e-9))
        .then_some(out)
}

/// The pond (or bank) on `ring`'s four corners: pushed in `inset` feet on every side (`pushed_in`; where the bank asks more than the
/// parcel holds, or leaves water a side of which is shorter than the least pond's, the parcel shrunk about its middle to `LEAST_SHARE`), each corner then rounded by a quadratic curve with its
/// control at the corner, cut back `reach` times a factor rolled within `CUT_STRAY` from `draw`. Returns the SVG path and the 13
/// points that sample it.
///
/// Research:
///     the bank's inset - GUESS research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#pond-set-parcel-s: one inset holds for the whole village, measured on its parcel of median area - the same bank's width on every side of every pond whose parcel holds its bank, a parcel drawing the least pond excepted
///     rounded corners - GUESS research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#pond-corners-rounded: a pond's corners are drawn rounded, no page giving the shape of a pond's corner - each corner rounded on a quadratic curve, its cut-back rolled about the reach
///     the least pond - GUESS research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#least-pond: where the bank the village's split asks for is more than a parcel holds, the water is still drawn - the parcel shrunk about its middle to `LEAST_SHARE`; and that least pond is the floor, so a parcel that holds its bank with water any side of which is shorter than a tenth of the parcel's same side draws the least pond too, never a sliver thinner than a tenth of the parcel across (feature 449 T420, its plan section's D8 holds the measurement)
#[must_use]
pub fn rounded(ring: &[Pt], inset: f64, reach: f64, draw: u32) -> (String, Vec<Pt>) {
    let corners = ring.len();
    // the least pond is a floor: water the bank leaves with a side shorter than the least pond's same side is a sliver, and
    // the least pond is drawn in its place
    let side = |r: &[Pt], i: usize| super::geom::dist(r[i], r[(i + 1) % r.len()]);
    let at = pushed_in(ring, inset)
        .filter(|water| {
            water.len() == corners
                && (0..corners).all(|i| side(water, i) >= side(ring, i) * LEAST_SHARE)
        })
        .unwrap_or_else(|| {
            #[expect(clippy::cast_precision_loss, reason = "a parcel's four corners")]
            let count = corners as f64;
            let middle = (
                ring.iter().map(|p| p.0).sum::<f64>() / count,
                ring.iter().map(|p| p.1).sum::<f64>() / count,
            );
            ring.iter()
                .map(|p| {
                    (
                        middle.0 + (p.0 - middle.0) * LEAST_SHARE,
                        middle.1 + (p.1 - middle.1) * LEAST_SHARE,
                    )
                })
                .collect()
        });
    let mut rolls = PyRandom::new(u64::from(draw));
    let cuts: Vec<f64> = (0..corners)
        .map(|_| reach * (1.0 - CUT_STRAY + 2.0 * CUT_STRAY * rolls.random()))
        .collect();
    let toward = |from: Pt, to: Pt, by: f64| {
        let u = super::geom::unit(from, to);
        let by = by.min(super::geom::dist(from, to) / 2.0);
        (from.0 + u.0 * by, from.1 + u.1 * by)
    };
    let mut path = String::new();
    let mut pts = Vec::new();
    for i in 0..corners {
        let (prev, c, next) = (
            at[(i + corners - 1) % corners],
            at[i],
            at[(i + 1) % corners],
        );
        let (a, b) = (toward(c, prev, cuts[i]), toward(c, next, cuts[i]));
        let bend = (
            0.25 * a.0 + 0.5 * c.0 + 0.25 * b.0,
            0.25 * a.1 + 0.5 * c.1 + 0.25 * b.1,
        );
        let lead = if i == 0 { "M" } else { "L" };
        let _ = write!(
            path,
            "{lead} {:.1} {:.1} Q {:.1} {:.1} {:.1} {:.1} ",
            a.0, a.1, c.0, c.1, b.0, b.1
        );
        pts.extend([a, bend, b]);
    }
    path.push('Z');
    pts.push(pts[0]);
    (path, pts)
}

#[cfg(test)]
mod tests {
    use super::rounded;
    use crate::field::geom::signed_area;

    #[test]
    fn a_pond_rounded_inside_its_parcel() {
        let sq = [(0.0, 0.0), (200.0, 0.0), (200.0, 100.0), (0.0, 100.0)];
        let (d, pts) = rounded(&sq, 16.0, 16.0, 7);
        assert_eq!(pts.len(), 13);
        assert!(d.starts_with('M') && d.ends_with('Z') && d.matches('Q').count() == 4);
        let xs: Vec<f64> = pts.iter().map(|p| p.0).collect();
        assert!(xs.iter().all(|x| (16.0 - 1e-9..=184.0 + 1e-9).contains(x)));
        assert!(signed_area(&pts).abs() < 200.0 * 100.0);
        assert_ne!(rounded(&sq, 16.0, 16.0, 8).0, d, "each pond its own");
        let (_, bare) = rounded(&sq, 0.0, 8.0, 7);
        assert!(bare
            .iter()
            .all(|p| (0.0..=200.0).contains(&p.0) && (0.0..=100.0).contains(&p.1)));
        let (_, tiny) = rounded(
            &[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
            5.0,
            8.0,
            1,
        );
        assert_eq!(tiny.len(), 13, "a cut never past a side's middle");
        // a bank wider than the parcel: the least pond
        assert!(tiny.iter().all(|p| (0.4..=0.6).contains(&p.0)));
        // one bank's width on every side, the long sides and the short alike
        let pushed = super::pushed_in(&sq, 16.0).unwrap();
        assert!((pushed[0].0 - 16.0).abs() < 1e-9 && (pushed[0].1 - 16.0).abs() < 1e-9);
        assert!((pushed[2].0 - 184.0).abs() < 1e-9 && (pushed[2].1 - 84.0).abs() < 1e-9);
        let back: Vec<_> = sq.iter().rev().copied().collect();
        // either way round
        assert!((super::pushed_in(&back, 16.0).unwrap()[0].0 - 16.0).abs() < 1e-9);
        assert!(super::pushed_in(&sq, 60.0).is_none());
        let flat = [
            (0.0, 0.0),
            (100.0, 0.0),
            (200.0, 0.0),
            (200.0, 100.0),
            (0.0, 100.0),
        ];
        // a straight corner kept
        assert_eq!(super::pushed_in(&flat, 10.0).unwrap().len(), 5);
        // no inset is the ring itself, never the fallback speck (the bank, feature 444 T16's glyph check)
        assert_eq!(super::pushed_in(&sq, 0.0).unwrap(), sq.to_vec());
    }

    /// THE LEAST POND IS A FLOOR (449 T420): a parcel that holds its bank with a sliver to spare draws the least pond, a tenth of
    /// the parcel across, never water thinner than it (a rolled mosaic drew a pond 5.6 ft wide in a parcel 127 ft across).
    #[test]
    fn a_parcel_that_barely_holds_its_bank_draws_the_least_pond_not_a_sliver() {
        let sq = [(0.0, 0.0), (200.0, 0.0), (200.0, 100.0), (0.0, 100.0)];
        // the bank leaves 101 ft by 1 ft of water: less than the least pond's 20 ft by 10 ft
        let (_, sliver) = rounded(&sq, 49.5, 16.0, 7);
        let ys: Vec<f64> = sliver.iter().map(|p| p.1).collect();
        let across = ys.iter().copied().fold(f64::MIN, f64::max)
            - ys.iter().copied().fold(f64::MAX, f64::min);
        // a tenth of the parcel's 100 ft across, where the bank alone left 1 ft
        assert!((across - 10.0).abs() < 1e-9);
        // a pond larger than the least keeps its bank's full width
        // a long parcel: 164 ft by 4 ft of water is more area than the least pond's, and still a sliver
        let long = [(0.0, 0.0), (320.0, 0.0), (320.0, 160.0), (0.0, 160.0)];
        let (_, thin) = rounded(&long, 78.0, 16.0, 7);
        let ys: Vec<f64> = thin.iter().map(|p| p.1).collect();
        let across = ys.iter().copied().fold(f64::MIN, f64::max)
            - ys.iter().copied().fold(f64::MAX, f64::min);
        assert!((across - 16.0).abs() < 1e-9);
        let (_, wide) = rounded(&sq, 40.0, 16.0, 7);
        assert!(wide
            .iter()
            .all(|p| (40.0 - 1e-9..=60.0 + 1e-9).contains(&p.1)));
    }
}
