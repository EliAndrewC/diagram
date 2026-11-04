//! The hem stage's unit tests (feature 444 T28).

use super::lay;
use crate::field::build::HemIn;
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
    assert!(kept.counts["write@dry_plot"] > 0);
    // water filed at its width keeps the plots off it
    let wet = lay(&h, &field, &[((-40.0, 0.0), (-40.0, 1200.0), 4.0)], &[]);
    assert!(wet.plots.len() < open.plots.len());
}
