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
///     the least pond - GUESS: research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html silent on a parcel too small for the village's bank; the water a tenth of the parcel across
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
    (kept * turn > 0.0 && kept.abs() < super::geom::signed_area(ring).abs()).then_some(out)
}

/// The pond (or bank) on `ring`'s four corners: pushed in `inset` feet on every side (`pushed_in`; where the bank asks more than the
/// parcel holds, the parcel shrunk about its middle to `LEAST_SHARE`), each corner then rounded by a quadratic curve with its
/// control at the corner, cut back `reach` times a factor rolled within `CUT_STRAY` from `draw`. Returns the SVG path and the 13
/// points that sample it.
///
/// Research:
///     the bank's inset - GUESS: research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html records that one inset serves every parcel as this project's GUESS - the same bank's width on every side of every pond
///     rounded corners - GUESS: research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html silent on a pond's corners, giving ponds of uneven shape; each corner rounded on a quadratic curve
#[must_use]
pub fn rounded(ring: &[Pt], inset: f64, reach: f64, draw: u32) -> (String, Vec<Pt>) {
    let corners = ring.len();
    let at = pushed_in(ring, inset).unwrap_or_else(|| {
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
    }
}
