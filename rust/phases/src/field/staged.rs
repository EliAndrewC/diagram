//! The polder stage's work (feature 444 T16 D8), apart from its door so the Rust driver asks it too (T42): the block, its dike,
//! outfall, resting plots, pocket pond and drawn states, and on a dike-pond block its conversion - the records out.
//!
//! Research:
//!     the polder's seam - NONE: the records out; each placement is claimed at the Rust that makes it

use super::dike::Dike;
use super::fan::Pt;
use super::landuse::{Crops, Parcel};
use super::polder::Polder;
use super::states::State;
use crate::counts::Counts;

/// What the polder stage laid.
///
/// Research:
///     the polder stage's record - NONE: the record's type
#[derive(Debug)]
pub struct PolderStage {
    pub polder: Polder,
    pub dike: Dike,
    pub outfall: Vec<Pt>,
    pub resting: Vec<usize>,
    pub pocket: Option<(usize, f64, f64, f64, f64)>,
    pub states: Vec<State>,
    /// A dike-pond block's parcels, its banks' crops and the ponds' inset (ft).
    pub converted: Option<(Vec<Parcel>, Crops, f64)>,
    pub counts: Counts,
}

/// A rice polder's pocket pond: the comb's own roll over the block's low plots of four ring points, a resting plot never its
/// host, and no pond where none is left (0008; 449 T429) - the host plot's index, the pond's middle and radii.
///
/// Research:
///     the pond's host - NONE: the polder's plots as the comb's basins; the roll and its rules are `features::pocket_pond`'s
///     only a low plot - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: "Our maps sink each pond wholly inside one low plot" - only the block's low plots are hosts, so where none of them is left the block draws no pond (449 T429: seed 183 at ten households laid every low plot a merged pair, and the pond fell to a top-row plot)
///     a four-sided host - GUESS research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html#pond-host-four-sided: "On a polder's rice, the pond takes only a four-sided plot", a fallback of the drawing - a plot of four ring points; a merged pair, which carries two mid-side points, is passed over
///     never a resting plot - GUESS research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html#pond-never-resting-plot: "A plot left to rest never holds the pond", a fallback of the drawing - held already by `polder::rest`, which never rests a low plot (0007), and repeated here
fn rice_pond(
    plots: &[super::polder::Plot],
    resting: &[usize],
    seed: i64,
    work: &mut u64,
) -> Option<(usize, f64, f64, f64, f64)> {
    let hosts: Vec<(usize, super::lattice::Basin)> = plots
        .iter()
        .enumerate()
        .filter(|(i, x)| x.low && !resting.contains(i) && x.ring.len() == 4)
        .map(|(i, x)| {
            (
                i,
                super::lattice::Basin {
                    row: usize::from(x.low),
                    col: x.col,
                    ring: x.ring.clone(),
                    on_drain_right: false,
                    on_drain_left: false,
                },
            )
        })
        .collect();
    let basins: Vec<super::lattice::Basin> = hosts.iter().map(|(_, b)| b.clone()).collect();
    *work += plots.len() as u64;
    super::features::pocket_pond(&basins, None, seed, "polder", work)
        .map(|(k, q)| (hosts[k].0, q.x, q.y, q.rx, q.ry))
}

/// The polder's plots drawn apart (`states::polder_states`), each low plot wet and the rest green on a dike-pond block, whose
/// parcels `_dikeponds` draws.
///
/// Research:
///     the polder's plots drawn apart - NONE: the rolls are `states::polder_states`'s; a dike-pond block's states set here draw nothing, every parcel of it converted and drawn by its ponds (`field_stage._dikeponds`)
fn polder_drawn(
    plots: &[super::polder::Plot],
    resting: &[usize],
    seed: i64,
    dikepond: bool,
    counts: &mut crate::counts::Counts,
) -> Vec<State> {
    let drawn: Vec<(usize, usize, bool)> = plots.iter().map(|x| (x.row, x.col, x.low)).collect();
    if dikepond {
        return drawn
            .iter()
            .map(|x| if x.2 { State::Wet } else { State::Green })
            .collect();
    }
    let mut work = 0;
    let out = super::states::polder_states(&drawn, resting, seed, &mut work);
    counts.add("candidate@polder_states", work);
    out
}

/// The polder (T16 D8): the households' paddy as a rice polder or a dike-pond block - its block, dike, outfall, resting plots and,
/// on a dike-pond, its conversion.
///
/// Research:
///     a rice polder's pocket pond - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a polder may have a pond on a low plot, a little over half the time; the dike-pond ground has none - the comb's own roll (`features::pocket_pond`) over the block's low plots of four ring points, a resting plot never its host, and no pond where no such plot is left (`rice_pond`)
///     resting only when unsettled - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: an unsettled settlement rests two to four whole plots (`polder::rest`), a settled one none
///     no resting plot on a dike-pond block - GUESS: research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html silent on a converted block; its parcels are ponds, their banks and a few in standing rice, and none is rested
#[must_use]
#[expect(
    clippy::too_many_arguments,
    reason = "the polder's inputs, each a plan field (D1)"
)]
pub fn polder_stage(
    seed: i64,
    households: u32,
    dikepond: bool,
    layout: &str,
    down_deg: f64,
    center: Pt,
    aspect: f64,
    canvas: Pt,
    unsettled: bool,
    pond: (f64, &str, &str, &str),
) -> PolderStage {
    let p = super::polder::polder(
        super::paddy_sq_ft(households),
        dikepond.then_some((pond.0, pond.1)),
        layout,
        down_deg,
        center,
        aspect,
        seed,
    );
    let outfall = super::polder::outfall(p.sluices[1], down_deg, canvas);
    let dike = super::dike::dike(&p.inner_env, &p.sluices, &[&p.feeder, &outfall], seed);
    let resting = super::polder::rest(&p.plots, seed, unsettled && !dikepond);
    let mut pond_work = 0_u64;
    let pocket = if dikepond {
        None
    } else {
        rice_pond(&p.plots, &resting, seed, &mut pond_work)
    };
    let mut counts = Counts::default();
    counts.add("candidate@polder_pond", pond_work);
    let states = polder_drawn(&p.plots, &resting, seed, dikepond, &mut counts);
    counts.add("candidate@polder_shape", 4);
    counts.add("write@polder_plot", 5 * p.plots.len() as u64);
    counts.add(
        "write@polder_ditch",
        2 * p.ditches.iter().map(|d| d.pts.len() as u64).sum::<u64>(),
    );
    counts.add("candidate@polder_corridor", p.corridor_tests);
    counts.add("write@polder_pond", 6);
    counts.add("write@dike_crest", 2 * dike.crest.len() as u64);
    counts.add("write@dike_face", 2 * dike.outer.len() as u64);
    counts.add(
        "write@dike_tree",
        2 * dike.trees.iter().map(|(_, r)| r.len() as u64).sum::<u64>(),
    );
    let converted = dikepond.then(|| {
        let (share, leftover, fry, crop) = pond;
        let rings: Vec<Vec<Pt>> = p.plots.iter().map(|x| x.ring.clone()).collect();
        let at = super::landuse::inset(&rings, share);
        let (parcels, mut crops) = super::landuse::convert(&rings, seed, at, leftover, fry, crop);
        // no bush in a creek's water (0018; 449 T420): a creek may graze a bank's foot where the mosaic pinches a gap
        let channels: Vec<(&[Pt], f64)> = p
            .ditches
            .iter()
            .map(|d| (d.pts.as_slice(), d.w.max(d.w_tail)))
            .collect();
        counts.add(
            "candidate@bank_crop_water",
            super::landuse::off_the_water(&mut crops, &channels),
        );
        counts.add("write@dikepond", 13 * parcels.len() as u64);
        counts.add(
            "write@bank_crop",
            2 * (crops.crowns.len() + crops.hedges.len()) as u64,
        );
        (parcels, crops, at)
    });
    PolderStage {
        polder: p,
        dike,
        outfall,
        resting,
        pocket,
        states,
        converted,
        counts,
    }
}

#[cfg(test)]
mod tests {
    use super::{polder_stage, rice_pond};
    use crate::field::polder::Plot;

    /// A plot of the block: its row, span and column, a square ring at `(x, y)` (a merged pair's two mid-side points added when
    /// `pair`), low when it reaches the last row.
    fn plot(row: usize, col: usize, pair: bool, low: bool) -> Plot {
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let (x, y) = (col as f64 * 100.0, row as f64 * 100.0);
        let h = if pair { 190.0 } else { 90.0 };
        let ring = if pair {
            vec![
                (x, y),
                (x + 90.0, y),
                (x + 90.0, y + 95.0),
                (x + 90.0, y + h),
                (x, y + h),
                (x, y + 95.0),
            ]
        } else {
            vec![(x, y), (x + 90.0, y), (x + 90.0, y + h), (x, y + h)]
        };
        Plot {
            row,
            span: if pair { 2 } else { 1 },
            col,
            ring,
            low,
        }
    }

    #[test]
    fn a_rice_polder_whose_low_plots_are_all_merged_pairs_draws_no_pond() {
        // 449 T429: seed 183 at ten households laid every last-row plot a merged pair, and the pond fell to a top-row plot
        // (0008: "Our maps sink each pond wholly inside one low plot"; a low plot of any other shape passed over)
        let plots = vec![
            plot(0, 0, false, false),
            plot(0, 1, false, false),
            plot(1, 0, true, true),
            plot(1, 1, true, true),
        ];
        for seed in [183, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] {
            let mut work = 0;
            let drawn = rice_pond(&plots, &[], seed, &mut work).is_some();
            assert!(!drawn, "seed {seed}: a pond in a plot not low");
        }
        // with a four-sided low plot left, the pond still takes it, and only it
        let mixed = vec![
            plot(0, 0, false, false),
            plot(1, 0, true, true),
            plot(2, 1, false, true),
        ];
        let mut drawn = 0;
        for seed in 1..=40 {
            let mut work = 0;
            if let Some((k, ..)) = rice_pond(&mixed, &[], seed, &mut work) {
                assert_eq!(k, 2, "seed {seed}");
                drawn += 1;
            }
        }
        assert!(drawn > 0);
    }

    #[test]
    fn a_rice_polder_and_a_dike_pond_block_are_laid() {
        let rice = polder_stage(
            21,
            16,
            false,
            "grid",
            90.0,
            (2000.0, 2000.0),
            1.0,
            (4000.0, 4000.0),
            true,
            (0.6, "rice", "none", "mulberry"),
        );
        assert!(!rice.polder.plots.is_empty() && rice.converted.is_none());
        assert_eq!(rice.states.len(), rice.polder.plots.len());
        assert!(!rice.resting.is_empty());
        let dike = polder_stage(
            21,
            16,
            true,
            "mosaic",
            90.0,
            (2000.0, 2000.0),
            1.0,
            (4000.0, 4000.0),
            true,
            (0.6, "rice", "fry_village", "mulberry"),
        );
        assert!(dike.pocket.is_none() && dike.resting.is_empty());
        assert!(dike
            .converted
            .as_ref()
            .is_some_and(|(parcels, _, at)| !parcels.is_empty() && *at > 0.0));
        assert!(!dike.outfall.is_empty() && !dike.dike.crest.is_empty());
    }
}
