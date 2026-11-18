//! Its unit tests (feature 449 T174).
//!
//! Research:
//!     its tests - NONE: tests, deciding nothing about a building

use super::{mark_rows, render, untabled_kinds, MarkRow};

/// Every figure below is `CPython` 3.14.4's on the same sheet.
const SHEET: &str = r#"<svg><g data-kind="road" stroke-width="4.5px"><path d="M 10 10 L 40 50 L 41 52"/></g><circle cx="50" cy="50" r="7.3" data-kind="tree"/><circle cx="1" cy="1" r="1" data-kind="-"/><circle cx="2" cy="2" r="1"/><rect x="1" y="1" width="0" height="4" data-kind="flat"/><rect x="1" y="1" width="3" height="4" data-kind="box"/><g data-kind="landing"><rect x="1" y="1" width="3" height="3" data-kind="steps"/></g><text x="1" y="1" data-kind="alcove">a</text><rect x="1" y="1" width="2" height="2" data-kind="-"/></svg>"#;

#[test]
fn the_sized_marks_are_the_python_s() {
    let rows = mark_rows(SHEET).unwrap();
    let row = |tag: &str, kind: &str, at: f64, w: f64, len: f64, ink: f64| MarkRow {
        tag: tag.to_owned(),
        kind: kind.to_owned(),
        x_px: at,
        y_px: at,
        w_ft: w,
        h_ft: if tag == "path" { 14.0 } else { w },
        length_ft: len,
        stroke_ft: ink,
    };
    assert_eq!(
        rows,
        [
            row("path", "road", 10.0, 10.3, 17.4, 1.5),
            row("circle", "tree", 42.7, 4.9, 0.0, 0.0)
        ]
    );
    assert_eq!(untabled_kinds(SHEET).unwrap(), ["flat"]);
    assert_eq!(
        render(&rows),
        "marks (circles, ellipses, paths, lines, polygons): 2\n   w ft   h ft  run ft  ink ft  tag      at px         kind (data-kind)\n   10.3   14.0    17.4     1.5  path     10,10         road\n    4.9    4.9     0.0     0.0  circle   42.7,42.7     tree"
    );
}

#[test]
fn a_mark_the_reader_refuses_refuses_both_lists() {
    let bad = r#"<svg><g transform="translate(.)"><circle r="1" data-kind="x"/></g></svg>"#;
    assert_eq!(mark_rows(bad).unwrap_err().kind, "ValueError");
    assert_eq!(untabled_kinds(bad).unwrap_err().kind, "ValueError");
}
