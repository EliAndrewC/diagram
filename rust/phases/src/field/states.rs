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
/// Of this many maps, one draws the seasonal plots (the flooded and the gold) at all.
///
/// Research:
///     on some maps - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: on some maps about one rice plot in sixteen is drawn still flooded and one in twenty gold - the maps that do rolled at even odds, a GUESS of "some"
pub const SEASONAL_IN: u32 = 2;

/// What a basin is drawn as.
///
/// Research:
///     a basin's state - NONE: the record's type, holding what `states` decides
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum State {
    Green,
    Wet,
    Flooded,
    Gold,
    Rest,
}

/// A draw in [0, n) for one plot, keyed by the map's seed, the field's tag, the draw's name and the plot's place.
///
/// Research:
///     the draw - NONE: a seeded draw, positional; what it decides is `states`'s
fn plot_draw(seed: i64, tag: &str, what: &str, b: &Basin, n: u32) -> u32 {
    knob_rng(seed, &format!("{tag}:{what}:{}:{}", b.row, b.col)).randbelow(n)
}

/// Whether two basins share a bund: neighbors in a row, or in neighboring rows the upper's foot and the lower's top overlapping
/// along the row's line (each ring top-left, top-right, foot-right, foot-left).
///
/// Research:
///     a shared bund - NONE: geometry; the rule it serves is `states`'
fn shares_bund(a: &Basin, b: &Basin) -> bool {
    if a.row == b.row {
        return a.col.abs_diff(b.col) == 1;
    }
    if a.row.abs_diff(b.row) != 1 {
        return false;
    }
    let (up, lo) = if a.row < b.row { (a, b) } else { (b, a) };
    let d = super::geom::unit(up.ring[3], up.ring[2]);
    let at = |p: super::fan::Pt| (p.0 - up.ring[3].0) * d.0 + (p.1 - up.ring[3].1) * d.1;
    let (u0, u1) = (at(up.ring[3]), at(up.ring[2]));
    let (l0, l1) = (
        at(lo.ring[0]).min(at(lo.ring[1])),
        at(lo.ring[0]).max(at(lo.ring[1])),
    );
    u0.max(l0) + 1e-6 < u1.min(l1)
}

/// Each basin's state. The lowest row is wet at `WET_PCT` unless it tapers to a point; of the rest, one in `FLOODED_IN` floods and
/// one in `GOLD_IN` is gold; on an `unsettled` field 2 to 4 plots rest, chosen down the slope (a plot's weight its row, so the far
/// end of the water's run is likeliest), never two sharing a bund (adjacent in a row or across one).
///
/// Research:
///     a pointed plot stays green - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: leaves green any plot of that row that tapers to a point
///     resting down the slope - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: a plot's chance of resting grows the farther down the field's slope it lies, a GUESS
///     no two share a bund - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: no two share a bund, a drawing convention
///     a resting plot from the green - GUESS: research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html silent on whether a wet plot rests; a plot already drawn wet, flooded or gold is not taken, so each plot wears one state
///     one state a plot - CONVENTION: each plot drawn as one - wet first, then flooded, then gold, so the wet tint on the drain's row is never covered by a seasonal one
///     a field short of its rest - GUESS: research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html silent on a field too small or crowded for its two to four whole plots; tried a bounded number of times, a small or crowded field may rest fewer
///     the comb's wet row - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a comb field gives each plot of its lowest row a 45% chance of the tint; a polder tints every low plot, at its own stage (`field_stage._polder`)
///     on some maps - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: the flooded and the gold drawn on some maps (`SEASONAL_IN`), not every map
#[must_use]
pub fn states(
    basins: &[Basin],
    seed: i64,
    tag: &str,
    unsettled: bool,
    work: &mut u64,
) -> Vec<State> {
    let last = basins.iter().map(|b| b.row).max().unwrap_or(0);
    let seasonal = knob_rng(seed, &format!("{tag}:seasonal")).randbelow(SEASONAL_IN) == 0;
    let mut out: Vec<State> = basins
        .iter()
        .map(|b| {
            // each test asked only where it can decide: the point only of the low row, the seasonal draws only on a map that
            // draws them (the audit, T16), each counted as asked
            let mut draw = |what: &str, n: u32| {
                *work += 1;
                plot_draw(seed, tag, what, b, n)
            };
            let wet = b.row == last
                && draw("wet", 100) < WET_PCT
                && !(0..b.ring.len()).any(|i| corner_deg(&b.ring, i) < ARROW_POINT_DEG);
            let corners = if b.row == last {
                b.ring.len() as u64
            } else {
                0
            };
            let state = if wet {
                State::Wet
            } else if seasonal && draw("flooded", FLOODED_IN) == 0 {
                State::Flooded
            } else if seasonal && draw("gold", GOLD_IN) == 0 {
                State::Gold
            } else {
                State::Green
            };
            *work += corners;
            state
        })
        .collect();
    if unsettled && !basins.is_empty() {
        let mut rng = knob_rng(seed, &format!("{tag}:rest"));
        let want = REST_PLOTS.0 + rng.randbelow(REST_PLOTS.1 - REST_PLOTS.0 + 1);
        let mut chosen: Vec<usize> = Vec::new();
        // a draw over the plots' own weights (each its row from the head, counted from one), so a plot lower down is likelier
        // whatever its row holds; a refused pick (a shared bund, a plot drawn otherwise) tries again, a bounded number of times
        let weights: Vec<u32> = basins
            .iter()
            .map(|b| u32::try_from(b.row + 1).unwrap_or(u32::MAX))
            .collect();
        // each plot's weight summed down the list, so a pick is a binary search, not a walk of the plots before it (the audit)
        let ends: Vec<u32> = weights
            .iter()
            .scan(0_u32, |s, w| {
                *s += w;
                Some(*s)
            })
            .collect();
        let weight: u32 = ends.last().copied().unwrap_or(0);
        for _ in 0..want * 8 {
            if chosen.len() >= want as usize {
                break;
            }
            let pick = rng.randbelow(weight.max(1));
            let i = ends.partition_point(|e| *e <= pick).min(basins.len() - 1);
            *work += 1 + chosen.len() as u64;
            let touches = |j: usize| shares_bund(&basins[i], &basins[j]);
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
    use crate::field::lattice::{basins, ROW_FT};

    #[test]
    fn the_plots_drawn_apart() {
        let f = fan(26.0 * 43_560.0, 1.0, 90.0, (3200.0, 3200.0), 4);
        let b = basins(&f, 4, ROW_FT);
        let last = b.iter().map(|x| x.row).max().unwrap();
        let s = states(&b, 4, "f0", false, &mut 0);
        let wet: Vec<_> = (0..b.len()).filter(|&i| s[i] == State::Wet).collect();
        assert!(!wet.is_empty() && wet.iter().all(|&i| b[i].row == last));
        // the flooded and the gold on some maps, not every one
        let maps: Vec<_> = (0..16)
            .map(|seed| states(&b, seed, "f0", false, &mut 0))
            .collect();
        let seasonal = |m: &Vec<State>| m.contains(&State::Flooded) || m.contains(&State::Gold);
        let some = maps.iter().filter(|m| seasonal(m)).count();
        assert!(some > 0 && some < maps.len(), "{some} of {}", maps.len());
        let with = maps.iter().find(|m| m.contains(&State::Flooded)).unwrap();
        let flooded = with.iter().filter(|x| **x == State::Flooded).count();
        assert!((b.len() / 40..b.len() / 8).contains(&flooded));
        assert!(maps.iter().any(|m| m.contains(&State::Gold)));
        assert!(!s.contains(&State::Rest), "a settled field rests none");
        assert_eq!(s, states(&b, 4, "f0", false, &mut 0), "positional");
        for seed in 0..12 {
            let r = states(&b, seed, "f0", true, &mut 0);
            let rest: Vec<_> = (0..b.len()).filter(|&i| r[i] == State::Rest).collect();
            assert!(rest.len() <= REST_PLOTS.1 as usize && !rest.is_empty());
            for (k, &i) in rest.iter().enumerate() {
                for &j in &rest[k + 1..] {
                    // no two resting plots share a bund
                    assert!(!super::shares_bund(&b[i], &b[j]));
                }
            }
        }
        assert!(states(&[], 1, "f0", true, &mut 0).is_empty());
    }
}
