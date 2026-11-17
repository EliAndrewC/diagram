//! The parse (feature 449 T170): what the lockstep's fixtures do not name - the marks a caller read first, a room folded into its
//! building, a path's rings; the lockstep (`lockstep.rs`) holds every field against the Python's.
//!
//! Research:
//!     the parse's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{parse_marked, parse_svg, path_rings, rooms_folded, Rect};
use crate::tagged::marks;

#[test]
fn the_marks_a_caller_read_give_the_same_parse() {
    let svg = r##"<svg><rect id="precinct" x="0" y="0" width="9" height="9" fill="#fff"/><rect data-kind="hearth" x="1" y="1" width="2" height="2" fill="#2D2A24"/><rect x="4" y="1" width="2" height="2" fill="#2D2A24"/></svg>"##;
    let plan = parse_svg(svg).unwrap();
    assert_eq!(plan, parse_marked(svg, &marks(svg).unwrap()).unwrap());
    assert_eq!(plan.door_rects.len(), 1, "the tagged hearth is no door");
    assert!(parse_marked("<svg/>", &[]).is_err());
}

#[test]
fn a_room_drawn_inside_its_building_is_folded_into_it() {
    let r = |x, fill: &str| Rect::new(x, 0.0, 10.0, 10.0, fill, 0);
    let inner = Rect::new(2.0, 2.0, 3.0, 3.0, "#DDB87A", 1);
    let folded = rooms_folded(vec![
        r(0.0, "#DDB87A"),
        inner.clone(),
        r(20.0, "#DDB87A"),
        Rect {
            fill: "#C9A57A".into(),
            ..inner
        },
    ]);
    assert_eq!(folded.len(), 3);
}

#[test]
fn a_path_s_rings_are_read_only_when_rectilinear() {
    assert_eq!(
        path_rings("M 0 0 H 4 V 4 H 0 Z").unwrap(),
        Some(vec![vec![(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]])
    );
    assert_eq!(path_rings("M 0 0 L 4 4 L 0 4 L 0 1").unwrap(), None);
    assert_eq!(path_rings("M 0 0 H 4 Z").unwrap(), None);
    assert_eq!(path_rings("c 1 1").unwrap(), None);
    assert_eq!(path_rings("1 2").unwrap(), None, "a point before any move");
    assert!(path_rings("M 1").is_err());
}
