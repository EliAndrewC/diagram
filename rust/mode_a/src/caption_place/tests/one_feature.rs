//! A feature covered counts once (feature 449 T209): research/questions/0242's drawing page weighs what a caption covers by the features
//! it covers - a road crossed half a building, "crossing one is better than crossing two" - so a road drawn as its bed and a dashed
//! texture over it, or a board drawn as its footing, frame and rail, is one feature covered, not one per drawn element.
//!
//! Research: the one-feature tests - NONE: tests of the cover rule claimed where the placer decides it, deciding nothing themselves

use super::super::search::How;
use super::{block_at, of, seats, sheet, well};

/// A well with no free place on a small sheet: its best place, directly above, lies on one road drawn as two paths (its bed and a dashed
/// texture), and covers half a building - not one.
#[test]
fn a_road_drawn_as_two_paths_is_crossed_once() {
    let walls = [
        block_at((0, 22, 22, 16)),
        block_at((38, 22, 22, 16)),
        block_at((0, 38, 60, 22)),
    ]
    .concat();
    let road = r##"<g data-kind="road"><path d="M 0 12 L 60 12" stroke="#B89060" stroke-width="20" fill="none"/><path d="M 0 12 L 60 12" stroke="#9C7448" stroke-width="20" stroke-dasharray="14 12" fill="none"/></g>"##;
    let all = seats(&sheet(
        60,
        60,
        &format!("{walls}{road}{}", well(30, 30, "well")),
    ));
    let s = of(&all, "well");
    assert!(
        matches!(s.how, How::CoverLeast(c) if (c - 0.5).abs() < 1e-9),
        "{:?}",
        s.how
    );
    assert!((s.center.0 - 30.0).abs() < 1e-9);
}
