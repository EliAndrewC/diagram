//! A leader kept off other features (feature 449 T209): a swept seat whose leader would cross another feature's building is refused
//! while a seat whose leader crosses none is within reach - the placer's CONVENTION, 0330 being silent on what a leader crosses.
//!
//! Research: the leader-crossing tests - NONE: tests of the leader rule claimed where the placer decides it, deciding nothing themselves

use super::super::geom::{segments_cross, Pt};
use super::super::search::How;
use super::{block_at, of, seats, sheet, well};

/// Does the segment `a`-`b` cross the box `(x0, y0, x1, y1)`'s edges or lie inside it?
fn crosses_box((a, b): (Pt, Pt), (x0, y0, x1, y1): (f64, f64, f64, f64)) -> bool {
    let c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)];
    let inside = |p: Pt| x0 < p.0 && p.0 < x1 && y0 < p.1 && p.1 < y1;
    (0..4).any(|i| segments_cross(a, b, c[i], c[(i + 1) % 4])) || inside(a) || inside(b)
}

/// A well hemmed in on every side: the nearest free seat, 35 px out to its right, would be tied back by a leader across the building
/// on that side; 45 px straight up, past a slot too narrow for the name, the leader runs down the slot and crosses nothing - and that
/// seat is taken.
#[test]
fn a_swept_seat_whose_leader_crosses_a_building_is_refused() {
    let right = (207, 100, 33, 100);
    let walls = [
        block_at(right),
        block_at((150, 100, 47, 44)),
        block_at((203, 100, 4, 44)),
        block_at((150, 156, 57, 44)),
        block_at((150, 144, 44, 12)),
    ]
    .concat();
    let all = seats(&sheet(
        400,
        300,
        &format!("{walls}{}", well(200, 150, "well")),
    ));
    let s = of(&all, "well");
    let leader = s.leader.expect("a leader past twice the gap");
    assert!(
        !crosses_box(leader, (207.0, 100.0, 240.0, 200.0)),
        "{:?} {leader:?}",
        s.how
    );
    assert!(
        matches!(s.how, How::Swept(d, 0) if (d - 45.0).abs() < 1e-3),
        "{:?}",
        s.how
    );
}

/// Every swept seat's leader crossing a building, a place at the usual gap covering only a road is taken: a leader across a building
/// weighs as a building covered, and a road crossed weighs half one.
#[test]
fn a_leader_across_a_building_weighs_more_than_a_road_covered() {
    let walls = [
        block_at((150, 90, 100, 41)),
        block_at((150, 156, 100, 60)),
        block_at((120, 90, 69, 126)),
        block_at((211, 90, 69, 126)),
    ]
    .concat();
    let road = r##"<path d="M 100 136 L 300 136" stroke="#B89060" stroke-width="6" fill="none" data-kind="road"/>"##;
    let all = seats(&sheet(
        400,
        300,
        &format!("{walls}{road}{}", well(200, 150, "well")),
    ));
    let s = of(&all, "well");
    assert!(
        matches!(s.how, How::CoverLeast(c) if (c - 0.5).abs() < 1e-9),
        "{:?}",
        s.how
    );
    assert!(s.leader.is_none());
    assert!((s.center.0 - 200.0).abs() < 1e-9);
}
