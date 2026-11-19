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
    let pts =
        path_points("M 1 2 L 3 4 5 6 H 7 V 8 C 0 0 0 0 9 9 A 1 1 0 0 1 10 11 m 5 5 H V Z").unwrap();
    assert_eq!(
        pts[..5],
        [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (7.0, 6.0), (7.0, 8.0)]
    );
    // the cubic's and the arc's drawn points (T195), each ending on its end, then the move
    assert!(pts.contains(&(9.0, 9.0)));
    assert_eq!(pts[pts.len() - 2..], [(10.0, 11.0), (15.0, 16.0)]);
    assert!(path_points("C 1").unwrap().is_empty());
}

/// T182: a relative command's pairs are offsets from the segment's start (they were skipped), a `Z` returns to the subpath's start, a
/// repeated curve visits each segment's end, and a number with an exponent or a leading point is one number.
#[test]
fn a_relative_step_is_read_from_where_the_path_stands() {
    let pts = path_points(
        "M 10 10 l 5 0 0 5 h -2 v 3 c 1 1 2 2 3 3 4 4 5 5 6 6 z q 1 0 2 2 t 3 3 s 0 1 2 2 a 1 1 0 0 1 4 0 M1e1 .5",
    )
    .unwrap();
    assert_eq!(
        pts[..5],
        [
            (10.0, 10.0),
            (15.0, 10.0),
            (15.0, 15.0),
            (13.0, 15.0),
            (13.0, 18.0)
        ]
    );
    // each curve's end, read from where the path stands, after the `z` from the subpath's start
    for end in [
        (16.0, 21.0),
        (22.0, 27.0),
        (12.0, 12.0),
        (15.0, 15.0),
        (17.0, 17.0),
    ] {
        assert!(pts.contains(&end), "{end:?} in {pts:?}");
    }
    // the relative arc's drawn half circle over its 4 px chord, from where the path stands (T195), then the move
    let arc_at = pts.iter().position(|p| *p == (17.0, 17.0)).unwrap();
    assert!(pts[arc_at..pts.len() - 1]
        .iter()
        .all(|p| ((p.0 - 19.0).hypot(p.1 - 17.0) - 2.0).abs() < 1e-9 && p.1 < 17.0 + 1e-9));
    assert_eq!(pts[pts.len() - 2..], [(21.0, 17.0), (10.0, 0.5)]);
    // the crop's ink reaches the curve's bow, not its control point at -10 (T195)
    let (xs, ys) = crate::audit::shared::ink::path_points("M 10 10 c 1 -20 2 2 3 3");
    assert_eq!((xs.first(), xs.last()), (Some(&10.0), Some(&13.0)));
    let top = ys.iter().copied().fold(f64::INFINITY, f64::min);
    assert!(top > 1.6 && top < 1.7, "{top}");
}

/// T195: a Bezier is read by its drawn bow, not its ends - Ubame's raked curves, bowed 1 ft, read 0 ft high in the size table.
#[test]
fn a_curve_is_read_by_its_drawn_points() {
    let rake = path_points("M 756 384 q 34 -6 68 0").unwrap();
    let top = rake.iter().map(|p| p.1).fold(f64::INFINITY, f64::min);
    assert!((top - 381.0).abs() < 0.06, "{top}");
    assert_eq!(
        (rake.first(), rake.last()),
        (Some(&(756.0, 384.0)), Some(&(824.0, 384.0)))
    );
    // a smooth curve reflects the control point before it, or stands on its start where the curve before is of another kind
    let s = path_points("M 0 0 Q 5 10 10 0 T 20 0").unwrap();
    assert!(s.iter().any(|p| p.0 > 10.0 && p.1 < -4.9), "{s:?}");
    let flat = path_points("M 0 0 L 10 0 T 20 0").unwrap();
    assert!(flat.iter().all(|p| p.1 == 0.0), "{flat:?}");
}

/// T195: an arc is read by its drawn curve, not its end point alone - Hoshigaoka's sacred-tree rope, a ring of 5 px radius drawn in two
/// arcs, was a 10 by 0 px mark in the size table (3.3 by 0.0 ft, a run of 6.7 ft for its 10.5) and stood no farther than its two ends in
/// the viewBox crop's ink.
#[test]
fn an_arc_is_read_by_its_drawn_curve() {
    let rope = "M581.0,800.0 a5,5 0 1,0 10,0 a5,5 0 1,0 -10,0";
    let pts = path_points(rope).unwrap();
    assert!(pts.len() > 8, "{pts:?}");
    assert_eq!(
        (pts.first(), pts.contains(&(591.0, 800.0)), pts.last()),
        (Some(&(581.0, 800.0)), true, Some(&(581.0, 800.0)))
    );
    // every point on the ring, within the reader's sag
    assert!(pts
        .iter()
        .all(|p| ((p.0 - 586.0).hypot(p.1 - 800.0) - 5.0).abs() < 0.06));
    let ms = marks(&format!(
        r#"<svg><g data-kind="sacred tree"><path d="{rope}" fill="none"/></g></svg>"#
    ))
    .unwrap();
    assert_eq!(
        ((ms[0].w * 10.0).round(), (ms[0].h * 10.0).round()),
        (100.0, 100.0)
    );
    let (xs, ys) = crate::audit::shared::ink::path_points(rope);
    let (lo, hi) = ys
        .iter()
        .fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), &y| {
            (lo.min(y), hi.max(y))
        });
    assert_eq!(((lo * 10.0).round(), (hi * 10.0).round()), (7950.0, 8050.0));
    assert!(xs.iter().all(|&x| (581.0..=591.0).contains(&x)));
    // an arc of a zero radius is a straight step, and one ending where it starts draws nothing: it visits its end alone
    assert_eq!(
        path_points("M 0 0 A 0 5 0 0 1 4 0").unwrap(),
        [(0.0, 0.0), (4.0, 0.0)]
    );
    assert_eq!(
        path_points("M 0 0 A 5 5 0 0 1 0 0").unwrap(),
        [(0.0, 0.0), (0.0, 0.0)]
    );
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

/// T182: an attribute in single quotes, or spaced about its `=`, is read (it read as absent: a single-quoted `data-kind` untagged, its
/// box at the origin).
#[test]
fn an_attribute_in_either_quote_is_read() {
    let ms =
        marks(r#"<svg><rect x='1' y = "2" width='3' height='4' data-kind='hut'/></svg>"#).unwrap();
    assert_eq!(
        (ms[0].x, ms[0].y, ms[0].w, ms[0].h, ms[0].kind.as_deref()),
        (1.0, 2.0, 3.0, 4.0, Some("hut"))
    );
}
