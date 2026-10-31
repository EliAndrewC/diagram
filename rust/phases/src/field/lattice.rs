//! The comb's lattice (feature 444 T16): the fan cut into rows across the fall and each row into basins along it, every basin a
//! four-cornered ring of the lattice's own crossings. Written from `phases/field_greenfield.derivation.md`'s algorithm and
//! `phases/field.md`'s "The comb's design, next"; the old field code unread.
//!
//! Research:
//!     a basin's size - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal and 26 to 36 ft along it
//!     the bunds converge - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a fan of paddies narrows toward its drain, its bunds converging

use super::fan::{Fan, Pt};
use crate::pyrand::knob_rng;

/// A basin's breadth across its canal: the spacing of the rows down the fall (feet).
///
/// Research:
///     the row spacing - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal
pub const ROW_FT: f64 = 48.0;

/// The rows' spacing by the plan's `plot_size`: the small irregular plots' 34 ft, the page's medium 48, the large block's 70.
///
/// Research:
///     paddy plot size - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a hamlet basin about 48 ft across its canal; the small (34 ft across) and the large block (70 ft) the plan's departures, kept until feature 417 T34
#[must_use]
pub fn row_ft_for(plot_size: &str) -> f64 {
    match plot_size {
        "small_irregular" => 34.0,
        "large_block" => 70.0,
        _ => ROW_FT,
    }
}

/// A basin's length along its canal, the band each one is rolled from (feet).
///
/// Research:
///     the basin's length - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: 26 to 36 ft along it
pub const ALONG_FT: (u32, u32) = (26, 36);

/// One basin: its row (0 at the head), its place in the row (0 at the fan's left looking downhill) and its ring of four corners.
#[derive(Debug, Clone, PartialEq)]
pub struct Basin {
    pub row: usize,
    pub col: usize,
    pub ring: Vec<Pt>,
    /// Whether the basin's right side (its `ring[1]` to `ring[2]`) lies on the drain, and whether its left side (`ring[3]` to
    /// `ring[0]`) does.
    pub on_drain_right: bool,
    pub on_drain_left: bool,
}

impl Basin {
    /// The basin's side on the drain, from its top to its foot, if it has one: the drain's hem.
    ///
    /// Research:
    ///     the hem along the drain - GUESS: the record is silent on a drawn hem; the basins' sides on the drain, the bund it runs in
    #[must_use]
    pub fn drain_side(&self) -> Option<[Pt; 2]> {
        if self.on_drain_right {
            Some([self.ring[1], self.ring[2]])
        } else if self.on_drain_left {
            Some([self.ring[0], self.ring[3]])
        } else {
            None
        }
    }
}

/// The cut positions across one row, as fractions s in [-1, 1], with a cut at 0 where the drain runs down the fan's middle: each
/// half's lengths rolled in `ALONG_FT` from the row's own stream (positional, so a change to one row re-rolls only it), as many as
/// the half's breadth holds at the band's middle, then scaled to fill it.
///
/// Research:
///     the basin's length - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: 26 to 36 ft along it, a knob rolled each basin
///     the drain a bund of its own - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: one drain gathering the water along the lowest line
#[must_use]
pub fn cuts(seed: i64, row: usize, breadth: f64) -> Vec<f64> {
    let middle = f64::from(ALONG_FT.0 + ALONG_FT.1) / 2.0;
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a small positive count of basins"
    )]
    let n = ((breadth / 2.0 / middle).round() as usize).max(1);
    let mut rng = knob_rng(seed, &format!("comb_row:{row}"));
    let span = ALONG_FT.1 - ALONG_FT.0 + 1;
    let mut out = vec![-1.0];
    for from in [-1.0, 0.0] {
        let lengths: Vec<f64> = (0..n)
            .map(|_| f64::from(ALONG_FT.0 + rng.randbelow(span)))
            .collect();
        let total: f64 = lengths.iter().sum();
        let mut s = from;
        for l in &lengths {
            s += l / total;
            out.push(s);
        }
        if let Some(last) = out.last_mut() {
            *last = from + 1.0;
        }
    }
    out
}

/// The comb's basins: the fan's length cut into rows of about `row_ft` (`ROW_FT` on the plan's medium plot size), each row cut across by `cuts` at fixed s, so the bunds of a
/// row converge with the fan; a row's cuts are its own, meeting the next row's bund in a T as a fan's paddies do.
///
/// Research:
///     the comb - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal and 26 to 36 ft along it, the bunds converging toward the drain
#[must_use]
pub fn basins(fan: &Fan, seed: i64, row_ft: f64) -> Vec<Basin> {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a small positive count of rows"
    )]
    let rows = ((fan.length / row_ft).round() as usize).max(1);
    #[expect(clippy::cast_precision_loss, reason = "a small row count")]
    let step = fan.length / rows as f64;
    let mut out = Vec::new();
    for row in 0..rows {
        #[expect(clippy::cast_precision_loss, reason = "a small row count")]
        let (u0, u1) = (row as f64 * step, (row + 1) as f64 * step);
        let breadth = fan.half_at(u0) + fan.half_at(u1);
        let s = cuts(seed, row, breadth);
        for (col, pair) in s.windows(2).enumerate() {
            let ring = vec![
                fan.at(u0, pair[0]),
                fan.at(u0, pair[1]),
                fan.at(u1, pair[1]),
                fan.at(u1, pair[0]),
            ];
            out.push(Basin {
                row,
                col,
                ring,
                on_drain_right: pair[1].abs() < 1e-12,
                on_drain_left: pair[0].abs() < 1e-12,
            });
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{basins, cuts, row_ft_for, ALONG_FT, ROW_FT};
    use crate::field::fan::fan;
    use crate::field::geom::signed_area;

    #[test]
    fn the_basins_fill_the_fan_at_the_researched_size() {
        let area = 26.0 * 43_560.0;
        let f = fan(area, 1.0, 315.0, (3200.0, 3200.0));
        let b = basins(&f, 4, ROW_FT);
        let total: f64 = b.iter().map(|x| signed_area(&x.ring).abs()).sum();
        assert!((total / area - 1.0).abs() < 1e-6, "the basins tile the fan");
        #[expect(clippy::cast_precision_loss, reason = "a few hundred basins")]
        let mean = total / b.len() as f64;
        assert!((1_200.0..1_800.0).contains(&mean));
        assert!(b.iter().all(|x| x.ring.len() == 4));
        let hem: Vec<_> = b.iter().filter_map(super::Basin::drain_side).collect();
        let rows = b.iter().map(|x| x.row).max().unwrap() + 1;
        assert_eq!(hem.len(), 2 * rows, "both sides of the drain, every row");
        assert_eq!(b, basins(&f, 4, ROW_FT), "the seed fixes the comb");
        assert_ne!(b, basins(&f, 5, ROW_FT));
    }

    #[test]
    fn a_row_cuts_at_the_researched_lengths_and_converges() {
        assert!(
            (row_ft_for("large_block") - 70.0).abs() < 1e-9
                && row_ft_for("small_irregular") < row_ft_for("medium")
        );
        let s = cuts(9, 3, 900.0);
        assert!(s.iter().any(|x| x.abs() < 1e-12), "a cut on the drain");
        assert!((s[0] + 1.0).abs() < 1e-12);
        assert!((s.last().unwrap() - 1.0).abs() < 1e-12);
        for w in s.windows(2) {
            let ft = (w[1] - w[0]) / 2.0 * 900.0;
            assert!((f64::from(ALONG_FT.0) * 0.9..=f64::from(ALONG_FT.1) * 1.1).contains(&ft));
        }
        let f = fan(26.0 * 43_560.0, 1.0, 0.0, (0.0, 0.0));
        let b = basins(&f, 4, ROW_FT);
        let first = b.iter().filter(|x| x.row == 0).count();
        let last_row = b.iter().map(|x| x.row).max().unwrap();
        let last = b.iter().filter(|x| x.row == last_row).count();
        assert!(last < first, "fewer basins a row toward the drain");
    }
}
