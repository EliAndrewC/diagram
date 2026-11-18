//! The off-map rule's readings at their edges (feature 449 T150); part A's page lockstep held them to the Python's (its Python deleted by part B, the cases' answers held by `page/held.rs`) on every form.
//!
//! Research: the off-map rule's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{shape_box, subpath_box};

#[test]
fn a_shape_missing_a_figure_is_not_judged() {
    for (tag, body) in [
        ("ellipse", " cy=\"1\" cx=\"1\""),
        ("line", " y1=\"1\" x1=\"1\""),
        ("rect", " y=\"1\" x=\"1\""),
        ("circle", " r=\"1\""),
    ] {
        assert_eq!(shape_box(tag, body).unwrap(), None, "{tag}");
    }
    assert_eq!(
        shape_box("rect", " y=\"1\" x=\"2\" width=\"3\" height=\"4\"").unwrap(),
        Some((2.0, 5.0, 1.0, 5.0))
    );
    assert_eq!(
        subpath_box("M5,5a2,2 0 1 0 4,0").unwrap(),
        (5.0, 9.0, 3.0, 7.0)
    );
    assert_eq!(subpath_box("M5,5a").unwrap_err().kind, "IndexError");
}
