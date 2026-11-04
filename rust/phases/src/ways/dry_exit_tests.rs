//! The dry exit's unit tests (feature 444 T30).
//!
//! Research:
//!     the dry exit's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::dry_exit::{
    blocked, clear_of_bands, connector_dry_exit, fill, push_out_of, DrySite, Grid, OVERSHOOT_FT,
};
use super::track::{in_poly, seg_dist};
use super::Counts;
use crate::field::fan::Pt;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

fn site<'a>(
    wet: &'a [Vec<Pt>],
    fabric: &'a [(Vec<Pt>, bool)],
    lines: &'a [(Pt, Pt)],
    course: &'a [Pt],
) -> DrySite<'a> {
    DrySite {
        wet,
        fabric,
        avoid: &[],
        pond: None,
        lines,
        course,
        canvas: (1000.0, 1000.0),
    }
}

#[test]
fn the_fill_finds_the_neck_between_two_marshes_and_pulls_it_taut() {
    let mut t = Counts::default();
    // marsh on every side but a neck to the north
    let wet = [
        square(-100.0, 600.0, 1100.0, 1100.0),
        square(-100.0, -100.0, 440.0, 600.0),
        square(560.0, -100.0, 1100.0, 600.0),
    ];
    let s = site(&wet, &[], &[], &[]);
    let path = connector_dry_exit(&s, (500.0, 500.0), &mut t).expect("the neck");
    assert_eq!(path[0], (500.0, 500.0));
    let end = path[path.len() - 1];
    assert!(end.1 < -OVERSHOOT_FT + 50.0);
    // every leg stays off the marsh grown by the lane
    for w in path.windows(2) {
        for k in 0..=50 {
            let f = f64::from(k) / 50.0;
            let p = (
                w[0].0 + (w[1].0 - w[0].0) * f,
                w[0].1 + (w[1].1 - w[0].1) * f,
            );
            assert!(wet.iter().all(|r| !in_poly(p, r)));
        }
    }
    // walled in on every side: no way out
    let shut = [square(-100.0, -100.0, 1100.0, 1100.0)];
    assert!(connector_dry_exit(&site(&shut, &[], &[], &[]), (500.0, 500.0), &mut t).is_none());
    // and walled in with a brook whose crossing places open on more marsh
    let course = [(-50.0, 300.0), (1050.0, 300.0)];
    let brook = [(course[0], course[1])];
    assert!(
        connector_dry_exit(&site(&shut, &[], &brook, &course), (500.0, 500.0), &mut t).is_none()
    );
    assert!(t.total() > 0);
}

#[test]
fn the_brook_is_crossed_at_its_crossing_places_and_a_channel_only_last() {
    let mut t = Counts::default();
    // a brook across the map north of the gateway; the marsh walls the south, east and west
    let course = [(-50.0, 300.0), (1050.0, 300.0)];
    let brook = [(course[0], course[1])];
    let wet = [
        square(-100.0, 700.0, 1100.0, 1100.0),
        square(-100.0, 320.0, 100.0, 700.0),
        square(900.0, 320.0, 1100.0, 700.0),
    ];
    let p = connector_dry_exit(&site(&wet, &[], &brook, &course), (500.0, 500.0), &mut t)
        .expect("over a crossing place");
    let crossing = p
        .windows(2)
        .find(|w| (w[0].1 - 300.0) * (w[1].1 - 300.0) <= 0.0)
        .map(|w| {
            let f = (300.0 - w[0].1) / (w[1].1 - w[0].1);
            w[0].0 + (w[1].0 - w[0].0) * f
        })
        .expect("it crosses the brook");
    // the crossing places stand every 160 ft from 80 ft along the course
    let off = (crossing + 50.0 - 80.0).rem_euclid(160.0);
    assert!(off.min(160.0 - off) <= 30.0 + 20.0);
    // a drawn channel no crossing place opens: crossed on a deck as the last resort
    let channel = [((-50.0, 300.0), (1050.0, 300.0))];
    assert!(connector_dry_exit(&site(&wet, &[], &channel, &[]), (500.0, 500.0), &mut t).is_some());
    // a brook the fill need not cross: kept to its own bank, the pond and crop walled
    let open = DrySite {
        avoid: &[square(0.0, 600.0, 1000.0, 1000.0)],
        pond: Some((800.0, 450.0, 20.0, 10.0)),
        ..site(&[], &[], &brook, &course)
    };
    let own = connector_dry_exit(&open, (500.0, 500.0), &mut t).expect("its own bank");
    assert!(own
        .iter()
        .all(|q| q.1 > 300.0 || q.1 < -300.0 || q.0 < 0.0 || q.0 > 1000.0));
}

#[test]
fn a_gateway_in_a_grove_band_is_walked_out_first_on_the_finer_grid() {
    let mut t = Counts::default();
    let band = square(450.0, 450.0, 550.0, 550.0);
    let fabric = [(band.clone(), true), (square(0.0, 0.0, 10.0, 10.0), false)];
    let p = connector_dry_exit(&site(&[], &fabric, &[], &[]), (500.0, 540.0), &mut t)
        .expect("out of the band");
    assert!(!in_poly(p[0], &band) && seg_dist(p[0], band[2], band[3]) > 12.5);
    // pushed off a band on its nearest edge's normal, away from its centroid; a point clear is left
    let q = push_out_of(&band, (500.0, 545.0), 10.0);
    assert!((q.1 - 560.0).abs() < 1e-9);
    assert_eq!(push_out_of(&band, (500.0, 700.0), 10.0), (500.0, 700.0));
    let mut rev = band.clone();
    rev.reverse();
    assert!((push_out_of(&rev, (500.0, 455.0), 10.0).1 - 440.0).abs() < 1e-9);
    // a ring with a doubled corner: its zero-length edge measured from its end
    let doubled = [
        (450.0, 450.0),
        (550.0, 450.0),
        (550.0, 450.0),
        (550.0, 550.0),
        (450.0, 550.0),
    ];
    assert!((push_out_of(&doubled, (500.0, 545.0), 10.0).1 - 560.0).abs() < 1e-9);
    assert_eq!(
        clear_of_bands((900.0, 900.0), &[band.as_slice()], 5.0),
        (900.0, 900.0)
    );
}

#[test]
fn the_raster_and_the_fill_at_their_edges() {
    let mut t = Counts::default();
    let g = Grid::new(100.0, 100.0, 20.0);
    // a ring of fewer than three corners walls nothing; a horizontal edge and a line block their strips
    let cells = blocked(
        &g,
        &[
            (vec![(0.0, 0.0), (1.0, 1.0)], 0.0),
            (square(40.0, 40.0, 60.0, 60.0), 0.0),
        ],
        &[((0.0, 10.0), (100.0, 10.0))],
        &mut t,
    );
    assert!(cells.iter().filter(|b| **b).count() > 4);
    // a start off the canvas leaves at once, overshooting from its own cell's center
    let none = vec![false; cells.len()];
    let out = fill(&g, (-30.0, 50.0), &none, (100.0, 100.0), &mut t).expect("off already");
    assert_eq!(out.len(), 2);
    // a start whose cell sits exactly on its center: the overshoot keeps its point
    let at = fill(&g, (-30.0, 50.0 - 0.0), &none, (100.0, 100.0), &mut t).expect("off already");
    assert!(at.len() == 2 && t.total() > 0);
}
