//! The usual gap off a feature's drawn edge (feature 449 T209): research/questions/0242's drawing page, "The gap is measured from the
//! edge of the feature as it is drawn" - a stroked building's drawn edge is its stroke's outer edge, and the nearness test and the seat
//! both measure from it, so the place directly above a stroked building is not refused by the building's own stroke.
//!
//! Research: the drawn-edge tests - NONE: tests of the gap rule claimed where the placer decides it, deciding nothing themselves

use super::super::geom::{turn, Pt};
use super::super::search::How;
use super::{block_box, of, seats, sheet};

/// A small storehouse at `x, y`, `w` x `h`, filled and stroked `sw` px wide, turned `deg` about its middle, its name too wide for it.
fn storehouse((x, y, w, h): (u32, u32, u32, u32), sw: f64, deg: i32) -> String {
    let (cx, cy) = (
        f64::from(x) + f64::from(w) / 2.0,
        f64::from(y) + f64::from(h) / 2.0,
    );
    format!(
        r##"<g data-kind="storehouse" transform="rotate({deg} {cx} {cy})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#C9A57A" stroke="#5A3F1E" stroke-width="{sw}"/><text font-size="8">storehouse</text></g>"##
    )
}

/// 0242: a stroked building too small for its name is named directly above it, the first ranked place, half the letter height off
/// its stroke's outer edge - not refused by its own stroke and sent to a diagonal.
#[test]
fn a_stroked_building_is_named_above_it_off_its_drawn_edge() {
    for sw in [1.0, 1.5, 3.0] {
        let all = seats(&sheet(400, 300, &storehouse((190, 140, 20, 20), sw, 0)));
        let s = of(&all, "storehouse");
        assert_eq!(s.how, How::Gap(0), "stroke {sw}: {:?}", s.how);
        // the block's foot 4 px (half the 8 px lettering) above the stroke's outer edge, 140 - sw / 2
        let foot = block_box(s).3;
        assert!(
            (140.0 - sw / 2.0 - 4.0 - foot).abs() < 1e-9,
            "stroke {sw}: foot {foot}"
        );
        assert!((s.center.0 - 200.0).abs() < 1e-9);
    }
}

/// 0242: a turned stroked building is named directly above it as the words read, the gap measured off its turned stroke's outer edge.
#[test]
fn a_turned_stroked_building_is_named_above_it_off_its_drawn_edge() {
    let all = seats(&sheet(400, 300, &storehouse((190, 140, 20, 20), 2.0, 30)));
    let s = of(&all, "storehouse");
    assert_eq!(s.how, How::Gap(0), "{:?}", s.how);
    assert!((s.angle - 30.0).abs() < 1e-6);
    // in the building's own frame, the block's foot stands 4 px above the stroke's outer edge (the rect's top less 1 px)
    let back = |p: Pt| turn(p, -s.angle);
    let top = back((200.0, 150.0)).1 - 10.0 - 1.0;
    let foot = back(s.center).1 + s.h / 2.0;
    assert!((top - 4.0 - foot).abs() < 1e-6, "foot {foot}, top {top}");
}

/// 0242: a road's name stands the usual gap off the road's drawn edge - its stroke's outer edge, not its center line - directly above
/// it as the words read.
#[test]
fn a_roads_name_stands_off_its_drawn_edge() {
    let all = seats(&sheet(
        400,
        300,
        r##"<g data-kind="road"><path d="M 50 150 L 350 150" stroke="#B89060" stroke-width="10" fill="none"/><text font-size="8">the road</text></g>"##,
    ));
    let s = of(&all, "the road");
    assert_eq!(s.how, How::Gap(0), "{:?}", s.how);
    // the block's foot 4 px (half the 8 px lettering) above the stroke's outer edge, 150 - 5
    let foot = block_box(s).3;
    assert!((150.0 - 5.0 - 4.0 - foot).abs() < 1e-9, "foot {foot}");
}
