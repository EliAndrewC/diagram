//! The plots drawn apart (feature 444 T16): the wet low row, the flooded and the early-gold basins, and the plots left to rest.
//! Each is rolled positionally - the map's seed and the plot's own row and place - so a change elsewhere re-rolls only what moved.
//!
//! Research:
//!     wet plots - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: each plot of its lowest row, the ones whose foot lies on the drain, a 45% chance of the tint
//!     flooded and gold - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: about one rice plot in sixteen drawn still flooded and one in twenty gold
//!     resting plots - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: an unsettled settlement rests two to four whole plots, no two sharing a bund

use super::geom::corner_deg;
use super::lattice::Basin;
use super::rules::ARROW_POINT_DEG;
use crate::pyrand::knob_rng;

/// The share of the lowest row tinted wet, in hundredths.
///
/// Research:
///     wet plots - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a 45% chance of the tint
pub const WET_PCT: u32 = 45;
/// One rice plot in this many drawn still flooded.
///
/// Research:
///     flooded - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: about one rice plot in sixteen drawn still flooded
pub const FLOODED_IN: u32 = 16;
/// One rice plot in this many drawn gold, ripening early.
///
/// Research:
///     gold - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: one in twenty gold, ripening early
pub const GOLD_IN: u32 = 20;
/// How many plots an unsettled settlement rests in a field.
///
/// Research:
///     resting plots - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: two to four whole plots in each field, a GUESS
pub const REST_PLOTS: (u32, u32) = (2, 4);

/// What a basin is drawn as.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum State {
    Green,
    Wet,
    Flooded,
    Gold,
    Rest,
}

/// A draw in [0, n) for one plot, keyed by the map's seed, the field's tag, the draw's name and the plot's place.
fn plot_draw(seed: i64, tag: &str, what: &str, b: &Basin, n: u32) -> u32 {
    knob_rng(seed, &format!("{tag}:{what}:{}:{}", b.row, b.col)).randbelow(n)
}

/// Each basin's state. The lowest row is wet at `WET_PCT` unless it tapers to a point; of the rest, one in `FLOODED_IN` floods and
/// one in `GOLD_IN` is gold; on an `unsettled` field 2 to 4 plots rest, chosen down the slope (a plot's weight its row, so the far
/// end of the water's run is likeliest), never two sharing a bund (adjacent in a row or across one).
///
/// Research:
///     a pointed plot stays green - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: leaves green any plot of that row that tapers to a point
///     resting down the slope - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: a plot's chance of resting grows the farther down the field's slope it lies, a GUESS
///     no two share a bund - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: no two share a bund, a drawing convention
#[must_use]
pub fn states(basins: &[Basin], seed: i64, tag: &str, unsettled: bool) -> Vec<State> {
    let last = basins.iter().map(|b| b.row).max().unwrap_or(0);
    let mut out: Vec<State> = basins
        .iter()
        .map(|b| {
            let pointed = (0..b.ring.len()).any(|i| corner_deg(&b.ring, i) < ARROW_POINT_DEG);
            if b.row == last && !pointed && plot_draw(seed, tag, "wet", b, 100) < WET_PCT {
                State::Wet
            } else if plot_draw(seed, tag, "flooded", b, FLOODED_IN) == 0 {
                State::Flooded
            } else if plot_draw(seed, tag, "gold", b, GOLD_IN) == 0 {
                State::Gold
            } else {
                State::Green
            }
        })
        .collect();
    if unsettled {
        let mut rng = knob_rng(seed, &format!("{tag}:rest"));
        let want = REST_PLOTS.0 + rng.randbelow(REST_PLOTS.1 - REST_PLOTS.0 + 1);
        let mut chosen: Vec<usize> = Vec::new();
        // a draw over the rows' weights, the plot then drawn within its row; a refused pick (a shared bund, a wet plot) tries again,
        // a bounded number of times
        let weight: u32 = (0..=last)
            .map(|r| u32::try_from(r + 1).unwrap_or(u32::MAX))
            .sum();
        for _ in 0..want * 8 {
            if chosen.len() >= want as usize {
                break;
            }
            let mut pick = rng.randbelow(weight.max(1));
            let mut row = 0;
            while pick > u32::try_from(row).unwrap_or(u32::MAX) {
                pick -= u32::try_from(row + 1).unwrap_or(u32::MAX);
                row += 1;
            }
            let in_row: Vec<usize> = (0..basins.len())
                .filter(|&i| basins[i].row == row)
                .collect();
            if in_row.is_empty() {
                continue;
            }
            let i = in_row[rng.randbelow(u32::try_from(in_row.len()).unwrap_or(1)) as usize];
            let touches = |j: usize| {
                let (a, b) = (&basins[i], &basins[j]);
                a.row.abs_diff(b.row) <= 1 && (a.row != b.row || a.col.abs_diff(b.col) <= 1)
            };
            if out[i] == State::Green && !chosen.iter().any(|&j| touches(j)) {
                chosen.push(i);
                out[i] = State::Rest;
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{states, State, REST_PLOTS};
    use crate::field::fan::fan;
    use crate::field::lattice::basins;

    #[test]
    fn the_plots_drawn_apart() {
        let f = fan(26.0 * 43_560.0, 1.0, 90.0, (3200.0, 3200.0));
        let b = basins(&f, 4);
        let last = b.iter().map(|x| x.row).max().unwrap();
        let s = states(&b, 4, "f0", false);
        let wet: Vec<_> = (0..b.len()).filter(|&i| s[i] == State::Wet).collect();
        assert!(!wet.is_empty() && wet.iter().all(|&i| b[i].row == last));
        let flooded = s.iter().filter(|x| **x == State::Flooded).count();
        assert!((b.len() / 40..b.len() / 8).contains(&flooded));
        assert!(s.contains(&State::Gold));
        assert!(!s.contains(&State::Rest), "a settled field rests none");
        assert_eq!(s, states(&b, 4, "f0", false), "positional");
        for seed in 0..12 {
            let r = states(&b, seed, "f0", true);
            let rest: Vec<_> = (0..b.len()).filter(|&i| r[i] == State::Rest).collect();
            assert!(rest.len() <= REST_PLOTS.1 as usize && !rest.is_empty());
            for (k, &i) in rest.iter().enumerate() {
                for &j in &rest[k + 1..] {
                    let near = b[i].row.abs_diff(b[j].row) <= 1
                        && (b[i].row != b[j].row || b[i].col.abs_diff(b[j].col) <= 1);
                    assert!(!near, "no two resting plots share a bund");
                }
            }
        }
        assert!(states(&[], 1, "f0", true).is_empty());
    }
}
