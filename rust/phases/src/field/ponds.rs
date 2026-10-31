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

/// The pond (or bank) on `ring`'s four corners: shrunk about its middle so each side comes in by `inset` in proportion to its
/// length against the mean side, each corner then rounded by a quadratic curve with its control at the corner, cut back
/// `reach` times a factor rolled within `CUT_STRAY` from `draw`. Returns the SVG path and the 13 points that sample it.
///
/// Research:
///     the bank's inset - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: one inset holds for the whole village, measured on its parcel of median area
///     rounded corners - CONVENTION: a pond dug and banked has no sharp corner; a quadratic curve a corner
#[must_use]
pub fn rounded(ring: &[Pt], inset: f64, reach: f64, draw: u32) -> (String, Vec<Pt>) {
    let corners = ring.len();
    #[expect(clippy::cast_precision_loss, reason = "a parcel's four corners")]
    let count = corners as f64;
    let middle = (
        ring.iter().map(|p| p.0).sum::<f64>() / count,
        ring.iter().map(|p| p.1).sum::<f64>() / count,
    );
    let mean = (0..corners)
        .map(|i| super::geom::dist(ring[i], ring[(i + 1) % corners]))
        .sum::<f64>()
        / count;
    let shrink = (1.0 - 2.0 * inset / mean.max(1.0)).max(0.1);
    let at: Vec<Pt> = ring
        .iter()
        .map(|p| {
            (
                middle.0 + (p.0 - middle.0) * shrink,
                middle.1 + (p.1 - middle.1) * shrink,
            )
        })
        .collect();
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
        assert!(xs.iter().all(|x| (21.0..=179.0).contains(x)));
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
    }
}
