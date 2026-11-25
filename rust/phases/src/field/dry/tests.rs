//! The dry hem's unit tests (feature 444 T16; moved beside `dry.rs` by feature 449 T423, the file past its 1,000 lines).
//!
//! Research:
//!     the dry hem's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::{
    apart, hem, past_keep, refused, DryPlot, Refusal, BANK_FT, GRAIN_ACRES_PER_HOUSEHOLD,
    MAX_BANDS, PLOT_FT, TRACT_APART_DEG, TRACT_STRIPS,
};
use crate::field::geom::inside;
use crate::field::index::Index;
use crate::field::index::{Bands, Boxes};

#[test]
fn a_later_plot_over_a_laid_slivers_corners_is_refused() {
    // the pair `make seeds` found on fresh comb seed 549270514 (feature 444 T36): two of the laid sliver's corners stood inside
    // the later plot, neither middle in the other, none of the later plot's corners in the sliver
    let sliver = vec![
        (2912.502, 4129.410),
        (2895.458, 4126.519),
        (2903.240, 4197.594),
        (2912.110, 4200.909),
    ];
    let later = vec![
        (2895.743, 4135.169),
        (2790.850, 4178.074),
        (2815.571, 4245.165),
        (2922.717, 4201.386),
    ];
    let plots = vec![DryPlot {
        poly: sliver.clone(),
        crop: "millet",
        theta: 0.0,
        tract: 7,
    }];
    let mut laid = Boxes::default();
    laid.file((2895.0, 4126.0), (2913.0, 4201.0));
    let (mut bands, mut ix) = (Bands::new(&[]), Index::default());
    assert_eq!(
        refused(&later, &mut bands, (&plots, &mut laid), &mut ix, 1.0),
        Some(Refusal::Laps)
    );
    // ...and a plot beside the sliver, sharing no ground, is not
    let beside: Vec<_> = sliver.iter().map(|p| (p.0 + 40.0, p.1)).collect();
    assert_eq!(
        refused(&beside, &mut bands, (&plots, &mut laid), &mut ix, 1.0),
        None
    );
}
#[test]
fn a_plot_onto_the_rice_is_refused_by_that_name() {
    let plot = vec![(0.0, 0.0), (91.4, 0.0), (91.4, 71.5), (0.0, 71.5)];
    let field = [
        (-10.0, -10.0),
        (200.0, -10.0),
        (200.0, 200.0),
        (-10.0, 200.0),
    ];
    let (mut bands, mut ix, mut laid) = (Bands::new(&field), Index::default(), Boxes::default());
    assert_eq!(
        refused(&plot, &mut bands, (&[], &mut laid), &mut ix, 1.0),
        Some(Refusal::Rice)
    );
}
#[test]
fn a_cleared_middles_hem_is_one_band_along_the_whole_canal() {
    let line = [(0.0, 0.0), (0.0, 1200.0)];
    let field = [(1.0, -10.0), (900.0, -10.0), (900.0, 1300.0), (1.0, 1300.0)];
    let mut ix = Index::default();
    let (plots, _, _) = hem(
        &line,
        (-1.0, 0.0),
        (1.0, 0.0),
        (f64::INFINITY, 1),
        &field,
        &mut ix,
        4.0,
        4,
        "f0",
        &[],
    );
    // the whole canal, end to end, and no deeper than one band's strips
    let deepest = BANK_FT + f64::from(TRACT_STRIPS.1) * PLOT_FT.1 + 1.0;
    assert!(plots.iter().all(|p| p.poly.iter().all(|c| -c.0 <= deepest)));
    assert!(plots.iter().any(|p| p.poly.iter().any(|c| c.1 < 1.0)));
    assert!(plots
        .iter()
        .any(|p| p.poly.iter().any(|c| c.1 > 1200.0 - PLOT_FT.0 - 1.0)));
}

#[test]
#[expect(clippy::too_many_lines, reason = "the hem's cases, one scenario each")]
fn the_hem_holds_the_need_outside_the_field() {
    let line = [(0.0, 0.0), (0.0, 1200.0)];
    let field = [(1.0, -10.0), (900.0, -10.0), (900.0, 1300.0), (1.0, 1300.0)];
    let need = 15.0 * GRAIN_ACRES_PER_HOUSEHOLD * 43_560.0;
    let mut ix = Index::default();
    let (plots, room, _) = hem(
        &line,
        (-1.0, 0.0),
        (1.0, 0.0),
        (need, MAX_BANDS),
        &field,
        &mut ix,
        4.0,
        4,
        "f0",
        &[],
    );
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
    // a brook through a plot's middle, its ends outside it, refuses it
    let mut through = Index::default();
    through.file_w((-50.0, -100.0), (-50.0, 2000.0), 7.0);
    let (crossed, _, _) = hem(
        &line,
        (-1.0, 0.0),
        (1.0, 0.0),
        (need, MAX_BANDS),
        &field,
        &mut through,
        1.0,
        4,
        "f0",
        &[],
    );
    assert!(crossed
        .iter()
        .all(|p| p.poly.iter().all(|c| c.0 > -46.0) || p.poly.iter().all(|c| c.0 < -54.0)));
    let (dry, _, _) = hem(
        &line,
        (-1.0, 0.0),
        (1.0, 0.0),
        (need, MAX_BANDS),
        &field,
        &mut wet,
        5000.0,
        4,
        "f0",
        &[],
    );
    assert!(dry.is_empty());
    let (none, _, _) = hem(
        &line,
        (-1.0, 0.0),
        (1.0, 0.0),
        (0.0, MAX_BANDS),
        &field,
        &mut Index::default(),
        4.0,
        4,
        "f0",
        &[],
    );
    assert!(none.is_empty(), "no need, no plots");
    let (short, _, _) = hem(
        &[(0.0, 0.0), (0.0, 10.0)],
        (-1.0, 0.0),
        (1.0, 0.0),
        (need, MAX_BANDS),
        &field,
        &mut Index::default(),
        4.0,
        4,
        "f0",
        &[],
    );
    let (dot, _, _) = hem(
        &[(0.0, 0.0)],
        (-1.0, 0.0),
        (1.0, 0.0),
        (need, MAX_BANDS),
        &field,
        &mut Index::default(),
        4.0,
        4,
        "f0",
        &[],
    );
    assert!(dot.is_empty());
    // the other side of the canal: the normal turned to it
    let (east, _, _) = hem(
        &line,
        (1.0, 0.0),
        (-1.0, 0.0),
        (need, MAX_BANDS),
        &[],
        &mut Index::default(),
        4.0,
        4,
        "f0",
        &[],
    );
    assert!(east.iter().all(|p| p.poly.iter().all(|c| c.0 >= -1e-9)));
    assert!(short.is_empty());
}

/// The plots of a hem that taper under half a plot's length along `line`'s own heading where they stand, and those standing
/// on nothing: an inner edge neither on the canal's bank nor on the outer edge of the plot before it in its column.
fn loose(plots: &[DryPlot], line: &[(f64, f64)]) -> (usize, usize) {
    let off = |p: (f64, f64)| {
        line.windows(2)
            .map(|w| crate::field::geom::seg_dist(p, w[0], w[1]))
            .fold(f64::INFINITY, f64::min)
    };
    let same = |a: (f64, f64), b: (f64, f64)| (a.0 - b.0).abs() + (a.1 - b.1).abs() < 1e-6;
    let side = |a: (f64, f64), b: (f64, f64)| (a.0 - b.0).hypot(a.1 - b.1);
    let tapered = plots
        .iter()
        .filter(|p| side(p.poly[2], p.poly[3]) < 0.5 * PLOT_FT.0)
        .count();
    let unstacked = plots
        .iter()
        .filter(|p| {
            off(p.poly[0]) > BANK_FT + 0.01
                && !plots
                    .iter()
                    .any(|q| same(q.poly[3], p.poly[0]) && same(q.poly[2], p.poly[1]))
        })
        .count();
    (tapered, unstacked)
}

/// A COLUMN'S CLIMB ENDS WHERE IT PINCHES (449 T423): along a canal bending toward its dry side the columns square to it
/// converge as they climb, and past half a plot's length a strip is a sliver, not a plot - before T423 the climb ran on
/// through the bend's middle, each strip narrower than the last, then out the far side.
#[test]
fn a_column_that_pinches_as_it_climbs_ends_there() {
    // an arc of 500 ft radius, 120 degrees of it, its middle on the dry side: the columns meet 500 ft out
    let line: Vec<(f64, f64)> = (0..=24)
        .map(|k| {
            let a = (-60.0 + 5.0 * f64::from(k)).to_radians();
            (-500.0 + 500.0 * a.cos(), 600.0 + 500.0 * a.sin())
        })
        .collect();
    let field = [
        (10.0, -100.0),
        (900.0, -100.0),
        (900.0, 1300.0),
        (10.0, 1300.0),
    ];
    let (plots, _, _) = hem(
        &line,
        (-1.0, 0.0),
        (1.0, 0.0),
        (60.0 * PLOT_FT.0 * PLOT_FT.1, MAX_BANDS),
        &field,
        &mut Index::default(),
        1.0,
        4,
        "f0",
        &[],
    );
    // three strips a column before the fourth's outer edge is under half a plot's length
    assert_eq!((plots.len() >= 30, loose(&plots, &line)), (true, (0, 0)));
}

/// A COLUMN'S CLIMB ENDS WHERE IT MEETS ANOTHER'S PLOTS (449 T423, seed 52 of 15 households falling at 225 degrees): past a
/// corner turned toward the dry side the columns of the long leg run into the short leg's block, and before T423 came out
/// behind it as detached strips turned against it, bare ground between.
#[test]
fn a_column_that_meets_another_columns_plots_ends_there() {
    // three plots' length of canal, then a corner of 30 degrees toward the dry side and six plots' length on
    let (c, s) = (30f64.to_radians().cos(), 30f64.to_radians().sin());
    let mut line: Vec<(f64, f64)> = (0..=6).map(|k| (0.0, 45.7 * f64::from(k))).collect();
    line.extend((1..=12).map(|k| (-s * 45.7 * f64::from(k), 274.2 + c * 45.7 * f64::from(k))));
    let field = [
        (10.0, -100.0),
        (900.0, -100.0),
        (900.0, 1300.0),
        (10.0, 1300.0),
    ];
    let (plots, _, _) = hem(
        &line,
        (-1.0, 0.0),
        (1.0, 0.0),
        (126.0 * PLOT_FT.0 * PLOT_FT.1, MAX_BANDS),
        &field,
        &mut Index::default(),
        1.0,
        4,
        "f0",
        &[],
    );
    assert_eq!((plots.len() >= 40, loose(&plots, &line)), (true, (0, 0)));
}

#[test]
fn a_tract_s_turn_stands_apart_from_its_neighbors_nearest_the_roll() {
    let mut t = 0;
    // the roll 15 on the contour between neighbors at 30 and -30: too near the first; on its side the windows' edges 10 and
    // -10 both stand apart, and the one nearer the roll is taken
    assert_eq!(apart((false, 15.0), &[30.0, -30.0], &mut t), (false, 10.0));
}

#[test]
fn a_column_on_ground_no_strip_clears_is_pushed_past_its_reach() {
    let mut t = 0;
    let frames = (((0.0, 0.0), (-1.0, 0.0)), ((0.0, 91.4), (-1.0, 0.0)));
    let ground = vec![vec![
        (-1000.0, -10.0),
        (-1.0, -10.0),
        (-1.0, 100.0),
        (-1000.0, 100.0),
    ]];
    let behind = past_keep(frames.0, frames.1, 6.0, &ground, &mut t);
    assert!(behind > 900.0, "{behind}");
    assert!(past_keep(frames.0, frames.1, 6.0, &[], &mut t) == 0.0);
}

/// A STRIP STRETCHED ROUND A BEND AWAY FROM THE DRY SIDE IS CUT INTO PLOTS (449 T434): the columns square to such a bend splay
/// as they climb, and a strip's edges grow with its depth; 0006 draws a plot roughly 92 ft across that never dwarfs the rice
/// basins. Red before T434: the hem drew each strip as one plot, stretched past three plots' length along a bend of 250 ft
/// radius; now each is cut into plots of about a plot's length, no edge past one and a half, the pieces standing on the bank
/// or on the plots below them.
#[test]
fn a_strip_stretched_round_a_bend_is_cut_into_plots() {
    // an arc of 250 ft radius, 120 degrees of it, the dry side outside it: the columns splay as they climb
    let line: Vec<(f64, f64)> = (0..=24)
        .map(|k| {
            let a = (-60.0 + 5.0 * f64::from(k)).to_radians();
            (-250.0 + 250.0 * a.cos(), 600.0 + 250.0 * a.sin())
        })
        .collect();
    let field = [
        (-260.0, 590.0),
        (-250.0, 590.0),
        (-250.0, 610.0),
        (-260.0, 610.0),
    ];
    let (plots, _, _) = hem(
        &line,
        (1.0, 0.0),
        (-1.0, 0.0),
        (60.0 * PLOT_FT.0 * PLOT_FT.1, MAX_BANDS),
        &field,
        &mut Index::default(),
        1.0,
        4,
        "f0",
        &[],
    );
    let side = |a: (f64, f64), b: (f64, f64)| (a.0 - b.0).hypot(a.1 - b.1);
    let longest = plots
        .iter()
        .map(|p| side(p.poly[0], p.poly[1]).max(side(p.poly[2], p.poly[3])))
        .fold(0.0, f64::max);
    let (n, most) = (plots.len(), 1.5 * PLOT_FT.0);
    assert!(n >= 60 && longest < most, "{n}: {longest:.1}");
    // each piece's inner corners stand on the canal's bank or on the outer edge of a plot below it
    let bank = |p: (f64, f64)| {
        line.windows(2)
            .map(|w| crate::field::geom::seg_dist(p, w[0], w[1]))
            .fold(f64::INFINITY, f64::min)
            <= BANK_FT + 0.01
    };
    let on = |c: (f64, f64)| {
        bank(c)
            || plots
                .iter()
                .any(|q| crate::field::geom::seg_dist(c, q.poly[3], q.poly[2]) < 1e-6)
    };
    let stands = |p: &DryPlot| on(p.poly[0]) && on(p.poly[1]);
    assert_eq!(plots.iter().filter(|p| !stands(p)).count(), 0);
}

/// A STRIP CUT, ITS TAPER KEPT FIRST (449 T434): a strip whose outer edge runs four plots' length is cut in four; one whose inner
/// edge is a plot's length and outer three is cut in two, not three, so no piece's inner edge runs under half a plot's length;
/// one no longer than one and a half plots is whole.
#[test]
fn a_stretched_strip_is_cut_its_taper_kept_first() {
    let l = PLOT_FT.0;
    let pieces = |inner: f64, outer: f64| {
        let mut tests = 0;
        super::cut(
            &[(0.0, 0.0), (inner, 0.0), (outer, 71.5), (0.0, 71.5)],
            &mut tests,
        )
        .len()
    };
    assert_eq!(
        (
            pieces(4.0 * l, 4.0 * l),
            pieces(l, 3.0 * l),
            pieces(l, 1.4 * l)
        ),
        (4, 2, 1)
    );
}
