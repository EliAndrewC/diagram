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

/// A rice polder's pocket pond: the comb's own roll over the block's low row, a resting plot never its host (0008) - the host
/// plot's index, the pond's middle and radii.
///
/// Research:
///     the pond's host - NONE: the polder's plots as the comb's basins; the roll and its rules are `features::pocket_pond`'s
///     a four-sided host - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on the host plot's shape; only a four-sided plot, so the pond's fit inside it holds
///     never a resting plot - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on a pond in a plot left to rest; never its host
fn rice_pond(
    plots: &[super::polder::Plot],
    resting: &[usize],
    seed: i64,
    work: &mut u64,
) -> Option<(usize, f64, f64, f64, f64)> {
    let hosts: Vec<(usize, super::lattice::Basin)> = plots
        .iter()
        .enumerate()
        .filter(|(i, x)| !resting.contains(i) && x.ring.len() == 4)
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
///     a rice polder's pocket pond - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a polder may have a pond on a low plot, a little over half the time; the dike-pond ground has none - the comb's own roll (`features::pocket_pond`) over the block's low row, a resting plot never its host
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
        dikepond,
        layout,
        down_deg,
        center,
        aspect,
        seed,
    );
    let dike = super::dike::dike(&p.inner_env, &p.sluices, seed);
    let outfall = super::polder::outfall(p.sluices[1], down_deg, canvas);
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
        let (parcels, crops) = super::landuse::convert(&rings, seed, at, leftover, fry, crop);
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
    use super::polder_stage;

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
