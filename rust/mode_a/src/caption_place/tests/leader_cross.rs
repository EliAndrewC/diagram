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

/// The county example's stables' privy (449 T384): a privy at the foot of a 17 px lane between the stables and a lodging, the lane too
/// narrow for its name and a wall below it, is named above the lane, and its leader runs down the lane's middle - where the name's
/// block and the privy share a span, every point of it equally near, the leader ends at that span's middle - not 0.5 px off the
/// stables' 2 px stroke from the privy's corner, read as the stables' own edge (the regenerated sheet's 57.6 px leader down the stables'
/// east wall, observed 2026-11-23).
#[test]
fn a_leader_down_a_lane_runs_its_middle_clear_of_both_walls() {
    let stroked = |kind: &str, (x, y, w, h): (u32, u32, u32, u32)| {
        format!(
            r##"<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#C9A57A" stroke="#6B4F2A" stroke-width="2" data-kind="{kind}"/>"##
        )
    };
    let privy = r##"<g data-kind="latrine"><rect x="247.5" y="121" width="15" height="15" fill="#7E726A" stroke="#4A3318" stroke-width="0.8" data-id="p"/><text font-size="7" data-names="p">latrine</text></g>"##;
    let body = [
        stroked("stables", (192, 64, 54, 72)),
        stroked("retainers' quarters", (264, 64, 66, 72)),
        block_at((100, 137, 300, 163)),
        privy.to_owned(),
    ]
    .concat();
    let all = seats(&sheet(400, 300, &body));
    let s = of(&all, "latrine");
    let (a, b) = s.leader.expect("a leader past twice the gap");
    assert!(matches!(s.how, How::Swept(_, 0)), "{:?}", s.how);
    assert!(
        (a.0 - 255.0).abs() < 1e-6 && (b.0 - 255.0).abs() < 1e-6,
        "{a:?} {b:?}"
    );
}

/// A leader slid along its shared span (449 T384): where a post stands on the line from the span's middle, run through by less than a
/// crossing - as at its middle the Ubame sheet's wood-kami altar's leader ran through the arch's post and 1 px from a fire-water tub's
/// center - the seat the sweep takes on the middle's line keeps its place, and its leader is drawn on the line within the span that meets
/// the least other ink, clear of the post, still upright and ending on the privy's top edge under the name.
#[test]
fn a_leader_slides_along_its_span_past_a_post_on_its_middle() {
    let stroked = |kind: &str, (x, y, w, h): (u32, u32, u32, u32)| {
        format!(
            r##"<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#C9A57A" stroke="#6B4F2A" stroke-width="2" data-kind="{kind}"/>"##
        )
    };
    let privy = r##"<g data-kind="latrine"><rect x="247.5" y="121" width="15" height="15" fill="#7E726A" stroke="#4A3318" stroke-width="0.8" data-id="p"/><text font-size="7" data-names="p">latrine</text></g>"##;
    let post =
        r##"<rect x="253.2" y="93.2" width="3.6" height="3.6" fill="#5A1A10" data-kind="arch"/>"##;
    let body = [
        stroked("stables", (192, 64, 54, 72)),
        stroked("retainers' quarters", (264, 64, 66, 72)),
        block_at((100, 137, 300, 163)),
        privy.to_owned(),
        post.to_owned(),
    ]
    .concat();
    let all = seats(&sheet(400, 300, &body));
    let s = of(&all, "latrine");
    let (a, b) = s.leader.expect("a leader past twice the gap");
    assert!(
        matches!(s.how, How::Swept(_, 0)) && (s.center.0 - 255.0).abs() < 1e-6,
        "{:?} {:?}",
        s.how,
        s.center
    );
    assert!((a.0 - b.0).abs() < 1e-6, "an upright leader {a:?} {b:?}");
    assert!(
        (b.1 - 120.6).abs() < 1e-6 && (247.5..=262.5).contains(&b.0),
        "on the privy's top edge {b:?}"
    );
    assert!(!(252.2..=257.8).contains(&b.0), "clear of the post {b:?}");
}
