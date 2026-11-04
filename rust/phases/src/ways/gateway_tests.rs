//! The gateway's unit tests (feature 444 T30).
//!
//! Research:
//!     the gateway's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::dry_exit::DrySite;
use super::gateway::{
    choose_track_out, cluster_gateway, gate_out_of_the_field, gateway_track, Axes, Choice,
};
use super::through::{Fabric, Law};
use super::track::{poly_box, TrackSite};
use super::Counts;
use crate::field::fan::Pt;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

const NORTH: Axes = Axes {
    along: (1.0, 0.0),
    out: (0.0, -1.0),
};

#[test]
fn the_gateway_stands_on_the_clouds_downslope_edge_clear_of_what_stands() {
    let mut t = Counts::default();
    let houses = [(400.0, 500.0), (600.0, 480.0)];
    let s = square(380.0, 470.0, 420.0, 520.0);
    let fab = [(s.clone(), poly_box(&s))];
    let g = cluster_gateway(&houses, NORTH, (0.0, 0.0), 0.0, &fab, &mut t);
    assert!((g.0 - 500.0).abs() < 1e-9 && (g.1 - 465.0).abs() < 1e-9);
    // turned a quarter: out along the margin
    let e = cluster_gateway(&houses, NORTH, (0.0, 0.0), 90.0, &fab, &mut t);
    assert!(e.0 > 600.0);
    assert_eq!(
        cluster_gateway(&[], NORTH, (7.0, 7.0), 0.0, &fab, &mut t),
        (7.0, 7.0)
    );
    // pushed out of the field
    let field = square(0.0, 600.0, 1000.0, 1000.0);
    assert!((gate_out_of_the_field(&field, (500.0, 610.0)).1 - 583.0).abs() < 1e-9);
}

#[test]
fn the_track_out_is_swept_from_the_gateway_turned_where_walled_and_threaded() {
    let mut t = Counts::default();
    let field = vec![square(0.0, 600.0, 1000.0, 1000.0)];
    let houses = [(500.0, 500.0)];
    let st = square(480.0, 480.0, 520.0, 520.0);
    let steadings = [(st.clone(), false)];
    let standing = [(st.clone(), poly_box(&st))];
    let sweep = TrackSite {
        lean: ((0.0, -1.0), (0.0, -1.0)),
        seat: (500.0, 500.0),
        avoid: &field,
        wet: &[],
        fabric: std::slice::from_ref(&st),
        water: (None, &[], &[]),
        canvas: (1000.0, 1000.0),
    };
    let dry = DrySite {
        wet: &[],
        fabric: &[],
        avoid: &field,
        pond: None,
        lines: &[],
        course: &[],
        canvas: (1000.0, 1000.0),
    };
    let fabric = Fabric {
        steadings: &steadings,
        envelope: &field[0],
        crops: &[],
        wet: &[],
        paddy: &[],
        lines: &[],
        houses: &houses,
        crossing: None,
    };
    let well = square(5000.0, 5000.0, 5010.0, 5010.0);
    let forbidding = [(well.clone(), poly_box(&well))];
    let law = Law {
        solid: &[],
        forbidding: &forbidding,
        seats: &[],
        brooks: &[],
        waters: &[],
    };
    let c = Choice {
        sweep: &sweep,
        dry: &dry,
        fabric: &fabric,
        law: &law,
        standing: &standing,
        axes: NORTH,
        fallback: (0.0, 0.0),
    };
    let (run, _) = choose_track_out(&c, &mut t).expect("north");
    assert!(run[run.len() - 1].1 < 0.0);
    // the downslope walled by marsh: a turned gateway's sweep, or its dry exit
    let marsh = [square(-100.0, -100.0, 1100.0, 440.0)];
    let wet_sweep = TrackSite {
        wet: &marsh,
        ..sweep
    };
    let wet_dry = DrySite { wet: &marsh, ..dry };
    let turned = Choice {
        sweep: &wet_sweep,
        dry: &wet_dry,
        ..c
    };
    let r = gateway_track(&turned, (500.0, 450.0), &mut t).expect("east or west");
    assert!(r[r.len() - 1].0 < 0.0 || r[r.len() - 1].0 > 1000.0);
    // walled on every side: none
    let shut = [square(-100.0, -100.0, 1100.0, 1100.0)];
    let s2 = TrackSite {
        wet: &shut,
        ..sweep
    };
    let d2 = DrySite { wet: &shut, ..dry };
    let closed = Choice {
        sweep: &s2,
        dry: &d2,
        ..c
    };
    assert!(choose_track_out(&closed, &mut t).is_none());
}
