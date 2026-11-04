//! The standing ground's unit tests (feature 444 T30).
//!
//! Research:
//!     the standing ground's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::ground::Ground;
use super::standing::Standing;
use super::wood::{keepouts, lane_gap, Shares};
use super::Counts;

#[test]
fn a_way_keeps_to_the_sites_ground_off_the_seats_and_the_other_homesteads() {
    let mut t = Counts::default();
    let mut ground = Ground::new((0.0, 0.0), (1000.0, 1000.0), &mut t);
    ground.fill_ring(
        &[(600.0, 0.0), (700.0, 0.0), (700.0, 1000.0), (600.0, 1000.0)],
        &mut t,
    );
    let beyond = |p: (f64, f64)| p.0 > 1500.0;
    let mut wood = Shares::default();
    wood.commit(&[(300.0, 800.0)], keepouts(&[], &[]), &mut t);
    let placed = [(300.0, 300.0, 40.0, 40.0), (100.0, 100.0, 20.0, 20.0)];
    let gap = lane_gap(7.0, 1.0);
    assert!(gap > 20.0);
    let mut st = Standing::new(&ground, &beyond, &wood, &placed, (7.0, gap));
    // open ground: clear, and remembered
    assert!(st.clear((0.0, 500.0), (500.0, 500.0), None, &mut t));
    assert!(st.clear((0.0, 500.0), (500.0, 500.0), None, &mut t));
    // across taken ground, beyond the window where the site says so, by a seat, by a homestead but its own
    assert!(!st.clear((500.0, 500.0), (800.0, 500.0), None, &mut t));
    assert!(!st.clear((1100.0, 500.0), (1600.0, 500.0), None, &mut t));
    assert!(st.clear((1100.0, 500.0), (1200.0, 500.0), None, &mut t));
    assert!(!st.clear((200.0, 810.0), (400.0, 810.0), None, &mut t));
    assert!(st.clear((200.0, 900.0), (400.0, 900.0), None, &mut t));
    assert!(!st.clear((200.0, 300.0), (400.0, 300.0), None, &mut t));
    assert!(st.clear((200.0, 300.0), (400.0, 300.0), Some(0), &mut t));
    // a homestead met in two of the line's cells is asked once
    assert!(st.clear((200.0, 250.0), (400.0, 250.0), None, &mut t));
}
