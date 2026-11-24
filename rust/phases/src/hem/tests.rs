//! The hem stage's unit tests (feature 444 T28).
//!
//! Research:
//!     the hem's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::lay;
use crate::field::build::HemIn;
use crate::field::dry::{BANK_FT, PLOT_FT};
use crate::field::geom::inside;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<(f64, f64)> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

#[test]
fn the_hem_keeps_off_the_settlement_s_ground_and_stands_behind_it() {
    // a canal along a field's west edge, the hem climbing west from it, one band of it on a cleared middle
    let line: Vec<(f64, f64)> = (0..=24).map(|k| (0.0, 50.0 * f64::from(k))).collect();
    let h = HemIn {
        line,
        out: (-1.0, 0.0),
        down: (0.0, 1.0),
        bounds: (f64::INFINITY, 1),
        seed: 4,
    };
    let field = square(1.0, -10.0, 900.0, 1300.0);
    let open = lay(&h, &field, &[], &[]);
    assert!(!open.plots.is_empty() && open.grain.0 > 0.0);
    // the settlement on the canal's west side from y 300 to 700, 300 ft deep: no plot on it, the column's plots laid behind it
    let ground = square(-300.0, 300.0, -1.0, 700.0);
    let kept = lay(&h, &field, &[], &[ground.clone()]);
    assert!(kept
        .plots
        .iter()
        .all(|p| !p.poly.iter().any(|c| inside(*c, &ground))));
    // behind it: a plot beside the settlement's band, further from the canal than the settlement's depth
    assert!(kept.plots.iter().any(|p| p
        .poly
        .iter()
        .all(|c| c.0 < -300.0 && c.1 > 300.0 && c.1 < 700.0)));
    #[cfg(feature = "counters")] // a count, kept by the counting build alone (FR-012)
    assert!(kept.counts["write@dry_plot"] > 0);
    // water filed at its width keeps the plots off it
    let wet = lay(&h, &field, &[((-40.0, 0.0), (-40.0, 1200.0), 4.0)], &[]);
    assert!(wet.plots.len() < open.plots.len());
}

#[test]
fn a_ground_no_strip_clears_pushes_its_columns_past_its_reach() {
    let line: Vec<(f64, f64)> = (0..=8).map(|k| (0.0, 50.0 * f64::from(k))).collect();
    let h = HemIn {
        line,
        out: (-1.0, 0.0),
        down: (0.0, 1.0),
        bounds: (f64::INFINITY, 1),
        seed: 4,
    };
    // a ground reaching far past its own box's diagonal on the hem's side: no column clears it within its reach
    let ground = vec![
        (-100_000.0, -1000.0),
        (-1.0, -1000.0),
        (-1.0, 2000.0),
        (-100_000.0, 2000.0),
    ];
    let laid = lay(
        &h,
        &square(1.0, -10.0, 900.0, 1300.0),
        &[],
        &[ground.clone()],
    );
    assert!(laid
        .plots
        .iter()
        .all(|p| !p.poly.iter().any(|c| inside(*c, &ground))));
}

/// THE BANDS BEHIND THE SETTLEMENT STACK UNBROKEN (449 T421, on 444's found row 388): on a straight canal with the settlement's
/// ground on it and grain enough for several bands, every plot's inner edge stands on the bank, on the outer edge of the plot
/// before it in its column, or within a strip's depth behind the ground - a band laid after a pushed column leaves no gap in it.
#[test]
fn the_bands_behind_a_pushed_column_stack_with_no_gap() {
    let line: Vec<(f64, f64)> = (0..=24).map(|k| (0.0, 50.0 * f64::from(k))).collect();
    let plot = PLOT_FT.0 * PLOT_FT.1;
    let h = HemIn {
        line,
        out: (-1.0, 0.0),
        down: (0.0, 1.0),
        bounds: (150.0 * plot, 64),
        seed: 4,
    };
    let ground = square(-300.0, 300.0, -1.0, 700.0);
    let laid = lay(&h, &square(1.0, -10.0, 900.0, 1300.0), &[], &[ground]);
    // each plot's span along the canal and its inner and outer edges out from it (feet)
    let spans: Vec<(f64, f64, f64, f64)> = laid
        .plots
        .iter()
        .map(|p| {
            let on = |f: fn(f64, f64) -> f64, k: usize| {
                let v = |c: &(f64, f64)| if k == 0 { c.1 } else { -c.0 };
                p.poly.iter().map(v).reduce(f).unwrap()
            };
            (
                on(f64::min, 0),
                on(f64::max, 0),
                on(f64::min, 1),
                on(f64::max, 1),
            )
        })
        .collect();
    let deepest = spans.iter().map(|s| s.3).fold(0.0, f64::max);
    let loose = spans
        .iter()
        .filter(|s| {
            let stacked = spans
                .iter()
                .any(|t| (t.3 - s.2).abs() < 0.5 && t.0 < s.1 - 1.0 && s.0 < t.1 - 1.0);
            let behind = s.2 >= 300.0 && s.2 < 300.0 + PLOT_FT.1 && s.1 > 300.0 && s.0 < 700.0;
            !((s.2 - BANK_FT).abs() < 0.5 || stacked || behind)
        })
        .count();
    let got = (laid.plots.len() >= 150, loose, deepest > 9.0 * PLOT_FT.1);
    assert_eq!(got, (true, 0, true));
}
