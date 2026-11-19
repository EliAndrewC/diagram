//! The sheet reader's own tests (feature 449 T202: its old tests went with the placer they tested): transforms, path steps and curves,
//! dash patterns, paint inherited, and the shapes each drawn element is read as.
//!
//! Research: the sheet reader's tests - NONE: the reader's reading pinned, deciding nothing about where a caption stands

use super::super::{char_w_of, render, Attrs, Cap, Join, Shape, CAPS_W_EM, CHAR_W_EM};
use super::{apply, parse_transform, path_points, read_sheet, Pt};

fn sheet(body: &str) -> Vec<Shape> {
    let src =
        format!(r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{body}</svg>"#);
    read_sheet(&src).unwrap().0
}

fn near(a: Pt, b: Pt) -> bool {
    (a.0 - b.0).abs() < 1e-9 && (a.1 - b.1).abs() < 1e-9
}

/// Translate, scale (one value and two), rotate about a point and matrix multiply out in order; a transform SVG has that the reader does
/// not is passed over.
#[test]
fn a_transform_list_multiplies_out_in_order() {
    let m = parse_transform(Some("translate(10) scale(2) matrix(1 0 0 1 3 4) skewX(5)")).unwrap();
    assert!(near(apply(m, (0.0, 0.0)), (16.0, 8.0)));
    let s = parse_transform(Some("scale(2 3)")).unwrap();
    assert!(near(apply(s, (1.0, 1.0)), (2.0, 3.0)));
    let r = parse_transform(Some("rotate(90 1 1)")).unwrap();
    assert!(near(apply(r, (2.0, 1.0)), (1.0, 2.0)));
    assert!(near(
        apply(parse_transform(None).unwrap(), (5.0, 6.0)),
        (5.0, 6.0)
    ));
}

/// A transform short of its values is Python's `IndexError`; a value that is no number its `ValueError`.
#[test]
fn a_transform_short_of_its_values_or_no_number_is_refused() {
    assert_eq!(
        parse_transform(Some("scale()")).unwrap_err().kind,
        "IndexError"
    );
    assert_eq!(
        parse_transform(Some("matrix(1 2)")).unwrap_err().kind,
        "IndexError"
    );
    assert_eq!(
        parse_transform(Some("translate(x)")).unwrap_err().kind,
        "ValueError"
    );
}

/// Horizontal and vertical steps, a `Z` closing the subpath, and a step after it starting a new one at the closed one's start; a path
/// starting with no move starts at the origin.
#[test]
fn a_step_after_a_close_starts_a_new_subpath() {
    let subs = path_points("M0 0 H10 V10 Z L5 5", 0.05).unwrap();
    assert_eq!(
        subs,
        vec![
            (vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], true),
            (vec![(0.0, 0.0), (5.0, 5.0)], false)
        ]
    );
    assert_eq!(
        path_points("L5 5", 0.05).unwrap(),
        vec![(vec![(0.0, 0.0), (5.0, 5.0)], false)]
    );
    // relative steps from the current point
    assert_eq!(
        path_points("m1 1 l2 0 h1 v1", 0.05).unwrap(),
        vec![(vec![(1.0, 1.0), (3.0, 1.0), (4.0, 1.0), (4.0, 2.0)], false)]
    );
}

/// The Beziers flattened, each ending on its end point; `S` reflects the cubic's second control point and `T` the quadratic's control
/// point, so the smooth halves bow the other way; a smooth step with no curve before it takes its start as its control point.
#[test]
fn the_beziers_flatten_and_the_smooth_forms_reflect() {
    let subs = path_points("M0 0 C0 10 10 10 10 0 S20 -10 20 0 Q25 10 30 0 T40 0", 0.1).unwrap();
    let pts = &subs[0].0;
    assert_eq!(pts.last(), Some(&(40.0, 0.0)));
    assert!(pts.len() > 8);
    let bows = |lo: f64, hi: f64| {
        pts.iter()
            .filter(|p| p.0 > lo && p.0 < hi)
            .map(|p| p.1)
            .sum::<f64>()
    };
    assert!(bows(0.5, 9.5) > 0.0 && bows(10.5, 19.5) < 0.0);
    assert!(bows(20.5, 29.5) > 0.0 && bows(30.5, 39.5) < 0.0);
    // with nothing to reflect, the control point is the start: a smooth cubic from (0,0) bows only toward its second control point
    let lone = path_points("M0 0 S10 10 20 0 q5 5 10 0 S40 -10 40 0", 0.1).unwrap();
    assert_eq!(lone[0].0.last(), Some(&(40.0, 0.0)));
    let relative = path_points("m0 0 c0 10 10 10 10 0", 0.1).unwrap();
    assert_eq!(relative[0].0.last(), Some(&(10.0, 0.0)));
}

/// An arc ends on its end point; its two flags choose which of the four arcs it is, the large ones reaching far past the small ones and
/// the two sweeps bowing to opposite sides; radii too small to reach are scaled up; an arc of no radius is a straight step, and one ending
/// where it starts draws nothing.
#[test]
fn an_arc_is_the_one_its_flags_name() {
    let reach = |large: u8, sweep: u8| {
        let d = format!("M0 0 A10 10 0 {large} {sweep} 10 0");
        let pts = path_points(&d, 0.05).unwrap().remove(0).0;
        assert_eq!(pts.last(), Some(&(10.0, 0.0)));
        pts.iter()
            .map(|p| p.1)
            .fold(0.0, |m: f64, y| if y.abs() > m.abs() { y } else { m })
    };
    let (small0, small1, large0, large1) = (reach(0, 0), reach(0, 1), reach(1, 0), reach(1, 1));
    assert!(small0.abs() < 2.0 && small1.abs() < 2.0);
    assert!(large0.abs() > 18.0 && large1.abs() > 18.0);
    assert!(small0 * small1 < 0.0 && large0 * large1 < 0.0);
    // radii of 1 cannot span 10: scaled to a half circle of radius 5
    let half = path_points("M0 0 A1 1 0 0 1 10 0", 0.05)
        .unwrap()
        .remove(0)
        .0;
    let deepest = half.iter().map(|p| p.1.abs()).fold(0.0, f64::max);
    assert!((deepest - 5.0).abs() < 0.1, "{deepest}");
    assert_eq!(
        path_points("M0 0 A0 5 0 0 1 50 0 A5 5 0 0 1 50 0", 0.05).unwrap(),
        vec![(vec![(0.0, 0.0), (50.0, 0.0)], false)]
    );
}

/// A dash pattern as SVG reads it, inherited from the group: `none` and lengths of no sum solid, an odd count doubled, and a value SVG
/// does not read - a negative, no number, nothing - ignored, so the group's pattern stands.
#[test]
fn a_dash_pattern_is_read_as_svg_reads_it() {
    let dash = |v: &str| {
        let shapes = sheet(&format!(
            r##"<g stroke="#000" stroke-dasharray="5 1"><line x1="0" y1="0" x2="10" y2="0" stroke-dasharray="{v}"/></g>"##
        ));
        shapes[0].dash.clone()
    };
    assert_eq!(dash("none"), Vec::<f64>::new());
    assert_eq!(dash("0 0"), Vec::<f64>::new());
    assert_eq!(dash("4 2"), vec![4.0, 2.0]);
    assert_eq!(dash("3"), vec![3.0, 3.0]);
    for ignored in ["-1 2", "a b", ""] {
        assert_eq!(dash(ignored), vec![5.0, 1.0], "{ignored:?}");
    }
}

/// A stroke's join and miter limit inherited, a join SVG does not know and a limit under 1 ignored so the inherited one stands; a closed
/// stroke drawn back to its start; a fill set on a polyline making it an outline.
#[test]
fn a_stroke_s_paint_is_inherited_as_svg_inherits_it() {
    let shapes = sheet(concat!(
        r##"<g stroke="#000" fill="none" stroke-linejoin="round" stroke-miterlimit="10" stroke-linecap="square">"##,
        r#"<path d="M0 0 L10 0 L10 10 Z" stroke-linejoin="zzz" stroke-miterlimit="0.5" stroke-linecap="zzz"/>"#,
        r#"<polyline points="0 0 5 5 9 0" stroke-linejoin="bevel"/>"#,
        r##"<polyline points="0 0 5 5 9 0" fill="#fff"/>"##,
        "</g>"
    ));
    let (closed, bevel, filled) = (&shapes[0], &shapes[1], &shapes[2]);
    assert!(closed.line && closed.closed);
    assert_eq!(closed.poly.first(), closed.poly.last());
    assert_eq!(
        (closed.join, closed.miter, closed.cap),
        (Join::Round, 10.0, Cap::Square)
    );
    assert_eq!(bevel.join, Join::Bevel);
    assert!(!filled.line && filled.filled);
}

/// Each drawn element read as its shape: an ellipse by its two radii, a polygon of two points as its box, a path of one point not at all,
/// an element of another namespace drawing nothing while what it holds is read.
#[test]
fn each_element_is_read_as_its_shape() {
    let shapes = sheet(concat!(
        r#"<ellipse cx="10" cy="10" rx="4" ry="2"/>"#,
        r#"<polygon points="0 0 10 5"/>"#,
        r#"<path d="M5 5"/>"#,
        r#"<o:wrap xmlns:o="urn:other"><rect x="1" y="1" width="2" height="2"/></o:wrap>"#
    ));
    assert_eq!(shapes.len(), 3);
    assert_eq!(
        shapes[0].poly,
        vec![(6.0, 8.0), (14.0, 8.0), (14.0, 12.0), (6.0, 12.0)]
    );
    assert_eq!(
        shapes[1].poly,
        vec![(0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0)]
    );
    assert_eq!(shapes[2].tag, "rect");
}

/// A caption's lines are its `<tspan>`s', its block measured at its face and set by its anchor.
#[test]
fn a_caption_reads_its_tspans_and_its_anchor() {
    let shapes = sheet(concat!(
        r#"<text x="50" y="20" font-size="10" text-anchor="end"><tspan>AB</tspan><tspan>cd</tspan></text>"#,
        r#"<text x="50" y="40" font-size="10">ab</text>"#
    ));
    assert_eq!(shapes[0].lines, vec!["AB".to_owned(), "cd".to_owned()]);
    assert_eq!(shapes[0].text, "AB cd");
    let right = shapes[0].poly.iter().map(|p| p.0).fold(f64::MIN, f64::max);
    assert!((right - 50.0).abs() < 1e-9, "{right}");
    let left = shapes[1].poly.iter().map(|p| p.0).fold(f64::MAX, f64::min);
    assert!((left - 50.0).abs() < 1e-9, "{left}");
}

/// A view box short of its four numbers is Python's `IndexError`; a coordinate that is no finite number is refused.
#[test]
fn a_sheet_with_no_view_or_an_infinite_coordinate_is_refused() {
    let short = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10"/>"#;
    assert_eq!(read_sheet(short).unwrap_err().kind, "IndexError");
    let infinite = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect x="1e999" width="1" height="1"/></svg>"#;
    assert_eq!(read_sheet(infinite).unwrap_err().kind, "ValueError");
}

/// The stroke values SVG knows, and none for one it does not.
#[test]
fn a_cap_and_a_join_are_read_from_their_svg_words() {
    assert_eq!(
        ["butt", "square", "round", "zzz"].map(Cap::of),
        [Some(Cap::Butt), Some(Cap::Square), Some(Cap::Round), None]
    );
    assert_eq!(
        ["miter", "miter-clip", "arcs", "round", "bevel", "zzz"].map(Join::of),
        [
            Some(Join::Miter),
            Some(Join::Miter),
            Some(Join::Miter),
            Some(Join::Round),
            Some(Join::Bevel),
            None
        ]
    );
}

/// A face's letter-spacing is a share of its size, so a text of no size takes the plain width; a text with no attributes takes its letters'.
#[test]
fn a_text_of_no_size_takes_no_letter_spacing() {
    let attrs: Attrs = [("letter-spacing".to_owned(), "2".to_owned())].into();
    assert!((char_w_of(Some(&attrs), "ab", 0.0) - CHAR_W_EM).abs() < 1e-12);
    assert!((char_w_of(Some(&attrs), "ab", 10.0) - (CHAR_W_EM + 0.2)).abs() < 1e-12);
    // a text with no face of its own: all-caps run wider, nothing added
    assert!((char_w_of(None, "AB", 10.0) - CAPS_W_EM).abs() < 1e-12);
}

/// A picture that cannot be written is refused with the reason.
#[test]
fn a_picture_that_cannot_be_written_is_refused() {
    let src = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>"#;
    let at = std::path::Path::new("/no-such-directory-t202/sheet.png");
    assert!(render(src, at).is_err());
}
