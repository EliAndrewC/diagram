//! The tagged marks (feature 449 T170): what a mark belongs to, a path's points, a translate and the refusals; the lockstep
//! (`parse/lockstep.rs`) holds every mark of every pool sheet against the Python's.
//!
//! Research:
//!     the tagged marks' tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{marks, path_points};
use crate::py::uncaught;

#[test]
fn a_mark_belongs_to_its_kind_and_its_lineage() {
    let svg = r##"<svg><g data-kind="latrine" fill="#7E726A"><rect x="1" y="2" width="3" height="4"/></g><rect data-part-of="well" data-kind="curb" fill="#9C8C70"/></svg>"##;
    let ms = marks(svg).unwrap();
    assert_eq!(
        (
            ms[0].fill(),
            ms[0].belongs_to("latrine"),
            ms[0].belongs_to("well")
        ),
        ("#7E726A", true, false)
    );
    assert_eq!(
        (
            ms[1].belongs_to("well"),
            ms[1].belongs_to("curb"),
            ms[1].fill()
        ),
        (true, true, "#9C8C70")
    );
    assert_eq!(marks("<svg><rect/></svg>").unwrap()[0].fill(), "");
    // a sheet the reader refuses has no marks
    assert!(marks("<g>").unwrap().is_empty());
}

#[test]
fn a_path_visits_its_absolute_points() {
    assert_eq!(
        path_points("M 1 2 L 3 4 5 6 H 7 V 8 C 0 0 0 0 9 9 A 1 1 0 0 1 10 11 m 5 5 H V Z").unwrap(),
        [
            (1.0, 2.0),
            (3.0, 4.0),
            (5.0, 6.0),
            (7.0, 6.0),
            (7.0, 8.0),
            (9.0, 9.0),
            (10.0, 11.0)
        ]
    );
    assert!(path_points("C 1").unwrap().is_empty());
}

#[test]
fn a_translate_moves_the_ink_and_a_bad_one_is_refused() {
    let ms = marks(r#"<svg><g transform="translate(10 -2)"><circle cx="1" cy="1" r="1"/><g transform="translate(1)"><text x="0" y="0">a <tspan>b</tspan></text></g></g></svg>"#).unwrap();
    assert_eq!((ms[0].x, ms[0].y, ms[0].w), (10.0, -2.0, 2.0));
    assert_eq!(
        (ms[1].x, ms[1].text.as_str(), ms[1].placed),
        (11.0, "a b", true)
    );
    let bad = marks(r#"<svg><g transform="translate(1.2.3)"><rect/></g></svg>"#).unwrap_err();
    assert_eq!(
        uncaught(&bad),
        "ValueError: could not convert string to float: '1.2.3'\n"
    );
}
