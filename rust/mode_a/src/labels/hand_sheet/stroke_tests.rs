//! The hand sheet's leaders held to the ink as SVG draws a stroke (feature 449 T194): a path's curves read as curves, each subpath a
//! stroke of its own and a `Z` closing one, a path's fill read as inherited, a stroke's corners joined as `stroke-linejoin` and
//! `stroke-miterlimit` join them, its dashes drawn and its gaps left bare, and a stroke of no length ending flat drawing nothing. Each
//! sheet is read from its markup, so every one of those is the reader's, and each drawn tip is measured against the test's own drawing
//! of the ink.
//!
//! Research:
//!     its tests - NONE: the placer's leaders measured against the drawn ink, deciding nothing about a building

use super::ink_tests::{led_about, off_box, read};
use super::Shape;
use crate::labels::geom::{dist, inside, rect, seg_closest, Pt};

/// A case: its name, its sheet, its ink's own measure, the point the blocks stand round and how far.
type Case<'a> = (&'a str, String, &'a dyn Fn(Pt) -> f64, Pt, f64);

/// A sheet of one tagged group drawn in dark ink.
fn sheet(g: &str, body: &str) -> String {
    format!(
        r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="-300 -300 800 800"><g data-kind="thing" stroke="#2D2A24" {g}>{body}</g></svg>"##
    )
}

/// How far `p` stands off a set of drawn polygons, 0 inside one: the test's own measure.
fn off_polys(p: Pt, polys: &[Vec<Pt>]) -> f64 {
    polys
        .iter()
        .map(|poly| {
            let edge = (0..poly.len())
                .map(|k| dist(p, seg_closest(p, poly[k], poly[(k + 1) % poly.len()])))
                .fold(f64::INFINITY, f64::min);
            f64::from(u8::from(!inside(p.0, p.1, poly))) * edge
        })
        .fold(f64::INFINITY, f64::min)
}

/// How far `p` stands off a curve sampled at 4,000 points and drawn out round by `half`: the test's own measure of a stroke along it.
fn off_curve(p: Pt, curve: &dyn Fn(f64) -> Pt, half: f64) -> f64 {
    (0..4000)
        .map(|k| {
            let (a, b) = (
                curve(f64::from(k) / 4000.0),
                curve(f64::from(k + 1) / 4000.0),
            );
            dist(p, seg_closest(p, a, b))
        })
        .fold(f64::INFINITY, f64::min)
        .max(half)
        - half
}

/// A segment's band at the half-width `h`, flat at both ends: the test's own drawing.
fn band(a: Pt, b: Pt, h: f64) -> Vec<Pt> {
    let d = dist(a, b);
    let (nx, ny) = (-(b.1 - a.1) / d * h, (b.0 - a.0) / d * h);
    vec![
        (a.0 + nx, a.1 + ny),
        (b.0 + nx, b.1 + ny),
        (b.0 - nx, b.1 - ny),
        (a.0 - nx, a.1 - ny),
    ]
}

/// Each case's blocks whose drawn tip stands on the ink or more than its 1 px trim and a rounding off it, or whose drawn leader is not
/// the one scored: (case, subject, block, how far off).
fn wrong(cases: Vec<Case<'_>>) -> Vec<(&str, usize, i32, f64)> {
    let mut out = Vec::new();
    for (name, src, off, center, r) in cases {
        let shapes = read(&src, false);
        let own: Vec<&Shape> = shapes.iter().collect();
        out.extend(
            led_about(&own, center, r)
                .into_iter()
                .filter_map(|(j, k, scored, drawn)| {
                    let tip = drawn?.1;
                    (scored != drawn || off(tip) == 0.0 || off(tip) > 1.05).then_some((
                        name,
                        j,
                        k,
                        off(tip),
                    ))
                }),
        );
    }
    out
}

#[test]
fn a_leader_ends_on_a_path_s_curve_as_the_sheet_draws_it() {
    // feature 449 T194, research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a leader "ends at the nearest
    // drawn point - a disc's curve, a stroke's edge" - the reader kept a curve by its end points, so Hoshigaoka's sacred-tree rope, a ring
    // drawn in two arcs, was read as a 10 px line doubled back, and a leader to it ended inside the ring; a cubic's hump and a quadratic's
    // wave, its smooth step reflecting the control point before, were read as the straight line between their ends
    let ring = |p: Pt| (dist(p, (0.0, 0.0)) - 10.0).abs().max(1.0) - 1.0;
    let cubic = |t: f64| {
        let u = 1.0 - t;
        (
            3.0 * u * t * t * 60.0 + t * t * t * 60.0,
            3.0 * u * u * t * -40.0 + 3.0 * u * t * t * -40.0,
        )
    };
    let quadratic = |t: f64| {
        // Q 20 -30 40 0, then T 80 0: its control reflected to (60, 30)
        let (s, c) = if t < 0.5 {
            (t * 2.0, [(0.0, 0.0), (20.0, -30.0), (40.0, 0.0)])
        } else {
            (t * 2.0 - 1.0, [(40.0, 0.0), (60.0, 30.0), (80.0, 0.0)])
        };
        let u = 1.0 - s;
        (
            u * u * c[0].0 + 2.0 * u * s * c[1].0 + s * s * c[2].0,
            u * u * c[0].1 + 2.0 * u * s * c[1].1 + s * s * c[2].1,
        )
    };
    let off_cubic = |p: Pt| off_curve(p, &cubic, 1.0);
    let off_quadratic = |p: Pt| off_curve(p, &quadratic, 1.0);
    let path = |d: &str| format!(r#"<path d="{d}" fill="none" stroke-width="2"/>"#);
    let cases: Vec<Case<'_>> = vec![
        (
            "a ring drawn in two arcs",
            sheet("", &path("M -10 0 a 10 10 0 1 0 20 0 a 10 10 0 1 0 -20 0")),
            &ring,
            (0.0, 0.0),
            50.0,
        ),
        (
            "a cubic's hump",
            sheet("", &path("M 0 0 C 0 -40 60 -40 60 0")),
            &off_cubic,
            (30.0, -15.0),
            60.0,
        ),
        (
            "a quadratic wave, its second half smooth",
            sheet("", &path("M 0 0 Q 20 -30 40 0 T 80 0")),
            &off_quadratic,
            (40.0, 0.0),
            70.0,
        ),
    ];
    assert_eq!(wrong(cases), Vec::new());
}

#[test]
fn a_path_s_subpaths_are_strokes_of_their_own_a_z_closes_one_and_its_fill_is_inherited() {
    // feature 449 T194: the reader joined a path's second move to the first by a segment nobody drew (Ubame's rear-yard fence, Ochiba's
    // steam marks), left a `Z`'s closing side undrawn (the compound sheets' wells, a square of `h v h z`), and read a path's fill on the
    // path alone, so Ubame's dry-garden rakes, stroked under a group's `fill="none"`, were read as boxes; a leader to any of them ended on
    // ink nobody drew, or short of ink drawn
    let two = |p: Pt| {
        off_box(p, (0.0, -2.0, 100.0, 2.0), 0.0).min(off_box(p, (0.0, 38.0, 100.0, 42.0), 0.0))
    };
    // the square stroked all the way round, its corners mitered (every block stands outside it)
    let closed = |p: Pt| off_box(p, (-2.0, -2.0, 62.0, 42.0), 0.0);
    let rake = |t: f64| {
        let u = 1.0 - t;
        (2.0 * u * t * 50.0 + t * t * 100.0, 2.0 * u * t * -30.0)
    };
    let off_rake = |p: Pt| off_curve(p, &rake, 1.0);
    let cases: Vec<Case<'_>> = vec![
        (
            "a path of two subpaths",
            sheet(
                "",
                r#"<path d="M 0 0 H 100 M 0 40 H 100" fill="none" stroke-width="4"/>"#,
            ),
            &two,
            (50.0, 20.0),
            80.0,
        ),
        (
            "a square closed by its Z",
            sheet(
                "",
                r#"<path d="M 0 0 H 60 V 40 H 0 Z" fill="none" stroke-width="4"/>"#,
            ),
            &closed,
            (30.0, 20.0),
            80.0,
        ),
        (
            "a curve under a group's fill of none",
            sheet(
                r#"fill="none" stroke-width="2""#,
                r#"<path d="M 0 0 Q 50 -30 100 0"/>"#,
            ),
            &off_rake,
            (50.0, -7.0),
            70.0,
        ),
    ];
    assert_eq!(wrong(cases), Vec::new());
}

#[test]
fn a_stroke_s_corners_are_joined_as_svg_joins_them() {
    // feature 449 T194, research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a leader "ends at the nearest
    // drawn point" - `stroke-linejoin` was unread and every corner measured round, where SVG's default miter draws it square (1.86 px past
    // the round at a 9 px wall's right angle, T193's finding), a sharp corner past the miter limit beveled, and a miter limit raised draws
    // it out to its point; the join and the limit are inherited, a join SVG does not know leaving the one inherited
    let wall = |g: &str| {
        sheet(
            g,
            r#"<polyline points="0,0 100,0 100,60" fill="none" stroke-width="9"/>"#,
        )
    };
    let mitered = |p: Pt| {
        off_box(p, (0.0, -4.5, 104.5, 4.5), 0.0).min(off_box(p, (95.5, -4.5, 104.5, 60.0), 0.0))
    };
    let rounded = |p: Pt| {
        off_box(p, (0.0, -4.5, 100.0, 4.5), 0.0)
            .min(off_box(p, (95.5, 0.0, 104.5, 60.0), 0.0))
            .min((dist(p, (100.0, 0.0)) - 4.5).max(0.0))
    };
    let house = sheet(
        "",
        r##"<rect x="0" y="0" width="60" height="40" fill="#DDB87A" stroke-width="4"/>"##,
    );
    let squared = |p: Pt| off_box(p, (-2.0, -2.0, 62.0, 42.0), 0.0);
    // a V of 20 degrees: its miter would stand h / sin(10 degrees), 5.76 half-widths, past its corner
    let (a, v, b) = (
        (0.0, 0.0),
        (100.0, 100.0 * 10_f64.to_radians().tan()),
        (0.0, 200.0 * 10_f64.to_radians().tan()),
    );
    let vee = |g: &str| {
        sheet(
            g,
            &format!(
                r#"<polyline points="{},{} {},{} {},{}" fill="none" stroke-width="9"/>"#,
                a.0, a.1, v.0, v.1, b.0, b.1
            ),
        )
    };
    // the corner's outer side, away from the turn: each arm's band corner at the V's point on the side the V does not open to
    let (o1, o2) = (band(a, v, 4.5)[2], band(v, b, 4.5)[3]);
    let beveled = |p: Pt| off_polys(p, &[band(a, v, 4.5), band(v, b, 4.5), vec![v, o1, o2]]);
    let tip = (v.0 + 4.5 / 10_f64.to_radians().sin(), v.1);
    let pointed = |p: Pt| off_polys(p, &[band(a, v, 4.5), band(v, b, 4.5), vec![v, o1, tip, o2]]);
    let round_vee =
        |p: Pt| off_polys(p, &[band(a, v, 4.5), band(v, b, 4.5)]).min((dist(p, v) - 4.5).max(0.0));
    let cases: Vec<Case<'_>> = vec![
        (
            "a wall bent square, mitered",
            wall(""),
            &mitered,
            (100.0, 0.0),
            30.0,
        ),
        (
            "a wall bent square, its round join on its group",
            wall(r#"stroke-linejoin="round""#),
            &rounded,
            (100.0, 0.0),
            30.0,
        ),
        (
            "a wall bent square, a join SVG does not know over its group's round",
            wall(r#"stroke-linejoin="round""#)
                .replace("<polyline", r#"<polyline stroke-linejoin="pointy""#),
            &rounded,
            (100.0, 0.0),
            30.0,
        ),
        (
            "a house outlined in a 4 px stroke, its corners mitered",
            house,
            &squared,
            (30.0, 20.0),
            70.0,
        ),
        (
            "a sharp corner past the miter limit, beveled",
            vee(""),
            &beveled,
            v,
            40.0,
        ),
        (
            "a sharp corner within its group's miter limit of 10, mitered",
            vee(r#"stroke-miterlimit="10""#),
            &pointed,
            v,
            60.0,
        ),
        (
            "a sharp corner, its round join on its group",
            vee(r#"stroke-linejoin="round""#),
            &round_vee,
            v,
            40.0,
        ),
    ];
    assert_eq!(wrong(cases), Vec::new());
}

#[test]
fn a_dash_gap_is_not_ink() {
    // feature 449 T194, research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a leader "ends at the nearest
    // drawn point" - a dashed stroke's `stroke-dasharray` was unread, so a leader to it could end in a gap, on nothing; each dash is a
    // stroke of its own with the stroke's caps, laid from the stroke's start and `stroke-dashoffset` into the pattern
    let line = |g: &str| {
        sheet(
            &format!(r#"stroke-width="6" {g}"#),
            r#"<line x1="0" y1="0" x2="200" y2="0"/>"#,
        )
    };
    let dashes = |from: f64, cap: f64| {
        move |p: Pt| {
            (0..6)
                .map(|k| {
                    let x0 = (from + 40.0 * f64::from(k)).max(0.0);
                    let x1 = (from + 40.0 * f64::from(k) + 20.0).min(200.0);
                    if x1 <= x0 {
                        return f64::INFINITY;
                    }
                    off_box(p, (x0 - cap, -3.0, x1 + cap, 3.0), 0.0)
                })
                .fold(f64::INFINITY, f64::min)
        }
    };
    let (plain, offset, square) = (dashes(0.0, 0.0), dashes(-10.0, 0.0), dashes(0.0, 3.0));
    let cases: Vec<Case<'_>> = vec![
        (
            "a dashed wall",
            line(r#"stroke-dasharray="20 20""#),
            &plain,
            (100.0, 0.0),
            40.0,
        ),
        (
            "a dashed wall, one value repeated",
            line(r#"stroke-dasharray="20""#),
            &plain,
            (100.0, 0.0),
            40.0,
        ),
        (
            "a dashed wall, 10 px into its pattern",
            line(r#"stroke-dasharray="20, 20" stroke-dashoffset="10""#),
            &offset,
            (100.0, 0.0),
            40.0,
        ),
        (
            "a dashed wall, each dash square-capped",
            line(r#"stroke-dasharray="20 20" stroke-linecap="square""#),
            &square,
            (100.0, 0.0),
            40.0,
        ),
    ];
    assert_eq!(wrong(cases), Vec::new());
}

#[test]
fn a_stroke_of_no_length_ending_flat_draws_nothing() {
    // feature 449 T194 (T193's impl-drift): a stroke of no length was one disc of its half-width whatever its cap, but SVG draws nothing
    // for a butt one; a leader to a dot that draws no ink is led to where it stands, its outline
    let dot = sheet(
        r#"stroke-width="6""#,
        r#"<line x1="50" y1="50" x2="50" y2="50"/>"#,
    );
    let at = |p: Pt| dist(p, (50.0, 50.0));
    let round = |p: Pt| (dist(p, (50.0, 50.0)) - 3.0).max(0.0);
    let cases: Vec<Case<'_>> = vec![
        ("a butt dot", dot.clone(), &at, (50.0, 50.0), 40.0),
        (
            "a round dot",
            dot.replace(
                r#"stroke-width="6""#,
                r#"stroke-width="6" stroke-linecap="round""#,
            ),
            &round,
            (50.0, 50.0),
            40.0,
        ),
    ];
    assert_eq!(wrong(cases), Vec::new());
}

#[test]
fn the_reader_s_and_the_band_s_edge_cases() {
    // feature 449 T194: a path with no move starts at the origin, and a step after a `Z` at the closed subpath's start; a smooth step with
    // no curve of its kind before reflects nothing; an arc to its own start draws nothing, one of no radius is a straight step, one too
    // small for its end is scaled up to a half circle, and the large arc swept the other way round; a subpath of one point is no shape; a dash
    // pattern of `none`, of no number or of a negative one leaves none or the one inherited
    use super::read::path_points;
    use crate::labels::placer::{
        band_nearest, dashes, join, outline_corners, part_nearest, InkPart, Join,
    };
    let subs = path_points(
        "L 5 0 Z l 0 5 M 0 10 S 5 15 10 10 T 20 10 A 3 3 0 0 1 20 10 A 0 2 0 0 1 30 10 A 1 1 0 0 1 40 10 A 10 10 0 0 0 50 20 A 10 10 0 1 1 60 20",
        0.05,
    )
    .unwrap();
    assert_eq!(
        subs[..2],
        [
            (vec![(0.0, 0.0), (5.0, 0.0)], true),
            (vec![(0.0, 0.0), (0.0, 5.0)], false)
        ]
    );
    let arcs = &subs[2].0;
    let at = |x: f64| arcs.iter().position(|p| *p == (x, 10.0)).unwrap();
    // the arc to its own start adds nothing, the radius-0 arc its end alone, the scaled arc a half circle of radius 5 reaching y 5
    assert_eq!((at(30.0) - at(20.0), arcs.last()), (1, Some(&(60.0, 20.0))));
    let low = arcs[at(30.0)..=at(40.0)]
        .iter()
        .map(|p| p.1)
        .fold(f64::INFINITY, f64::min);
    assert!((low - 5.0).abs() < 1e-9, "{low}");
    let sheet = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 99 99"><g stroke="#000" fill="none" stroke-dasharray="4 2">
        <path d="M 1 1 M 2 2 L 3 3"/><line x1="0" y1="0" x2="9" y2="0" stroke-dasharray="none"/>
        <line x1="0" y1="0" x2="9" y2="0" stroke-dasharray="4 x"/><line x1="0" y1="0" x2="9" y2="0" stroke-dasharray="-1 2"/></g></svg>"##;
    let shapes = super::read_sheet(sheet).unwrap().0;
    let dash: Vec<Vec<f64>> = shapes.iter().map(|s| s.dash.clone()).collect();
    assert_eq!(
        dash,
        [vec![4.0, 2.0], vec![], vec![4.0, 2.0], vec![4.0, 2.0]]
    );
    // the band's corners: a straight-on vertex joins nothing; an exact reversal bevels; an outline with a corner past the miter limit is
    // measured as its whole band; a block on a miter's point past the round corner touches the outline
    let straight = InkPart {
        pts: vec![
            (0.0, 0.0),
            (5.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ],
        half: 2.0,
        ..InkPart::default()
    };
    let (beveled, corners) = outline_corners(&straight);
    assert_eq!((beveled, corners.len()), (false, 4));
    assert_eq!(
        join((0.0, 0.0), (1.0, 0.0), (1.0, 0.0), 1.0, Join::Miter, 4.0),
        (None, None)
    );
    assert_eq!(
        join((0.0, 0.0), (1.0, 0.0), (-1.0, 0.0), 1.0, Join::Miter, 4.0)
            .0
            .map(|p| p.len()),
        Some(3)
    );
    let touched = part_nearest(&rect(11.8, -1.8, 0.1, 0.1, 0.0), &straight).unwrap();
    assert_eq!(touched.0, touched.1);
    let sharp = InkPart {
        pts: vec![(0.0, 0.0), (100.0, 10.0), (0.0, 20.0)],
        half: 2.0,
        ..InkPart::default()
    };
    let block = rect(120.0, 10.0, 2.0, 2.0, 0.0);
    assert_eq!(part_nearest(&block, &sharp), band_nearest(&block, &sharp));
    // a dash pattern laid from 5 px into it: past the first dash, into the gap after it
    let dashed = InkPart {
        pts: vec![(0.0, 0.0), (10.0, 0.0)],
        line: true,
        half: 1.0,
        dash: vec![4.0, 3.0],
        offset: 5.0,
        ..InkPart::default()
    };
    assert_eq!(
        dashes(&dashed),
        [vec![(2.0, 0.0), (6.0, 0.0)], vec![(9.0, 0.0), (10.0, 0.0)]]
    );
}
