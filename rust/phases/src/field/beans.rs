//! The beans sown on the bunds (feature 444 T16): runs of beads along the bunds between a row's basins, none drawn in the water.
//!
//! Research:
//!     beans on the bunds - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: some bunds carry a row of soybeans, drawn as dark green beads

use super::fan::Pt;
use super::geom::{seg_dist, unit};
use super::index::Index;
use super::lattice::Basin;
use crate::pyrand::knob_rng;

/// Of this many bunds between a row's basins, `BUND_SHARE.0` carry a run of beans.
///
/// Research:
///     which bunds - GUESS: the record silent on how many; 0014 says some bunds carry a row and not how many; three in eight, near the density today's maps draw
pub const BUND_SHARE: (u32, u32) = (3, 8);
/// The beads a run holds, at least two.
///
/// Research:
///     a run - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a stretch of bund that carries them shows at least two beads; the most, four, a GUESS
pub const RUN_BEADS: (u32, u32) = (2, 4);
/// The spacing of a run's beads (feet).
///
/// Research:
///     the beads' spacing - GUESS: the record silent on it; 0014 gives a bead about 3 ft across in a single row, not their spacing; 8 ft, so each reads apart
pub const BEAD_STEP_FT: f64 = 8.0;
/// A bead's radius (feet).
///
/// Research:
///     the bead - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a round bead about 3 ft across
pub const BEAD_R_FT: f64 = 1.5;

/// The runs of beans on `basins`' bunds: a basin's bund with the next in its row (never the flank's, nor the drain's at the fan's
/// middle), chosen at `BUND_SHARE` from the map's seed and the bund's place, its beads `BEAD_STEP_FT` apart about its middle. A
/// bead within a bead's radius of the water filed in `ix` (each segment at its half-width, `widths`) is drowned and dropped; a run
/// left with fewer than two is dropped whole.
///
/// Research:
///     no bead in the water - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: in a single row on the bund
#[must_use]
pub fn bean_runs(
    basins: &[Basin],
    seed: i64,
    tag: &str,
    ix: &mut Index,
    widths: &[f64],
) -> Vec<Vec<Pt>> {
    let mut runs = Vec::new();
    for (i, b) in basins.iter().enumerate() {
        let next = basins.get(i + 1).filter(|n| n.row == b.row);
        if next.is_none() || b.on_drain_right {
            continue;
        }
        let mut rng = knob_rng(seed, &format!("{tag}:beans:{}:{}", b.row, b.col));
        if rng.randbelow(BUND_SHARE.1) >= BUND_SHARE.0 {
            continue;
        }
        let n = RUN_BEADS.0 + rng.randbelow(RUN_BEADS.1 - RUN_BEADS.0 + 1);
        let (top, foot) = (b.ring[1], b.ring[2]);
        let mid = (f64::midpoint(top.0, foot.0), f64::midpoint(top.1, foot.1));
        let along = unit(top, foot);
        let run: Vec<Pt> = (0..n)
            .map(|k| {
                let off = (f64::from(k) - f64::from(n - 1) / 2.0) * BEAD_STEP_FT;
                (mid.0 + along.0 * off, mid.1 + along.1 * off)
            })
            .filter(|p| !drowned(*p, ix, widths))
            .collect();
        if run.len() >= RUN_BEADS.0 as usize {
            runs.push(run);
        }
    }
    runs
}

/// The runs that survive the map's final water (finish's settling, feature 287 W33): each bead within a bead's radius past a
/// segment's half-width of `segs`, or inside one of `ponds` (x, y, rx, ry) grown by a bead's radius, drowned and dropped; a run
/// left with fewer than two dropped whole.
///
/// Research:
///     a run shows at least two - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a stretch of bund that carries them shows at least two beads
#[must_use]
pub fn settle(
    runs: &[Vec<Pt>],
    segs: &[(Pt, Pt, f64)],
    ponds: &[(f64, f64, f64, f64)],
) -> Vec<Vec<Pt>> {
    let mut ix = Index::default();
    for (a, b, w) in segs {
        ix.file_w(*a, *b, *w);
    }
    let widths = ix.widths.clone();
    let in_pond = |p: Pt| {
        ponds.iter().any(|(x, y, rx, ry)| {
            ((p.0 - x) / (rx + BEAD_R_FT)).powi(2) + ((p.1 - y) / (ry + BEAD_R_FT)).powi(2) <= 1.0
        })
    };
    runs.iter()
        .map(|r| {
            r.iter()
                .copied()
                .filter(|p| !in_pond(*p) && !drowned(*p, &mut ix, &widths))
                .collect::<Vec<_>>()
        })
        .filter(|r| r.len() >= RUN_BEADS.0 as usize)
        .collect()
}

/// Whether a bead at `p` lies in the water filed in `ix`.
fn drowned(p: Pt, ix: &mut Index, widths: &[f64]) -> bool {
    let reach = BEAD_R_FT + widths.iter().copied().fold(0.0, f64::max) / 2.0;
    ix.near((p.0 - reach, p.1 - reach), (p.0 + reach, p.1 + reach))
        .into_iter()
        .any(|i| {
            let (a, b) = ix.segs[i];
            seg_dist(p, a, b) < BEAD_R_FT + widths.get(i).copied().unwrap_or(0.0) / 2.0
        })
}

#[cfg(test)]
mod tests {
    use super::{bean_runs, settle, RUN_BEADS};
    use crate::field::fan::fan;
    use crate::field::index::Index;
    use crate::field::lattice::{basins, ROW_FT};

    #[test]
    fn beans_in_runs_of_two_or_more_and_none_in_the_water() {
        let f = fan(26.0 * 43_560.0, 1.0, 90.0, (3200.0, 3200.0), 4);
        let b = basins(&f, 4, ROW_FT);
        let mut ix = Index::default();
        let runs = bean_runs(&b, 4, "f0", &mut ix, &[]);
        assert!(!runs.is_empty());
        assert!(runs
            .iter()
            .all(|r| (RUN_BEADS.0 as usize..=RUN_BEADS.1 as usize).contains(&r.len())));
        #[expect(clippy::cast_precision_loss, reason = "a few hundred basins")]
        let share = runs.len() as f64 / b.len() as f64;
        assert!((0.15..0.5).contains(&share), "{share}");
        // a ditch along every bund drowns every bead
        let mut wet = Index::default();
        let mut widths = Vec::new();
        for x in &b {
            wet.file(x.ring[1], x.ring[2]);
            widths.push(2.5);
        }
        assert!(bean_runs(&b, 4, "f0", &mut wet, &widths).is_empty());
        // finish's settling: a ditch through a run drowns it, a pond on a bead drowns that bead, a dry run stands
        let run = vec![(0.0, 0.0), (8.0, 0.0), (16.0, 0.0)];
        let kept = settle(&[run.clone()], &[], &[(16.0, 0.0, 3.0, 3.0)]);
        assert_eq!(kept, vec![vec![(0.0, 0.0), (8.0, 0.0)]]);
        assert!(settle(
            &[run.clone()],
            &[((8.0, -10.0), (8.0, 10.0), 2.5)],
            &[(0.0, 0.0, 1.0, 1.0)]
        )
        .is_empty());
        assert_eq!(settle(&[run.clone()], &[], &[]), vec![run]);
    }
}
