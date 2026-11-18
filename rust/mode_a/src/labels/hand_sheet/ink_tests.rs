//! The hand sheet's leaders held to the ink as the sheet draws it (feature 449 T193): a leader past a stroke's end ends on the end its
//! `stroke-linecap` draws, and a leader ends on the nearest drawn edge - a stroke's band, a closed part's outline drawn out by its own
//! stroke - whichever part's line or outline stands nearer. Each sheet is read from its markup, so the cap and the stroke widths are the
//! reader's.
//!
//! Research:
//!     its tests - NONE: the placer's leaders measured against the drawn ink, deciding nothing about a building

use super::seat::subjects;
use super::{leader_to_ink, read_sheet, Shape};
use crate::labels::geom::{dist, rect, seg_closest, Pt};
use crate::labels::placer::{leader_of, Kind, Placement};

/// Sixteen caption blocks `r` px round `center`, at each beside subject's angle, each leader as `leader_of` scores it at ring 9 and as
/// `leader_to_ink` draws it: (subject, block, scored, drawn).
type Led = (usize, i32, Option<(Pt, Pt)>, Option<(Pt, Pt)>);
fn led_about(own: &[&Shape], center: Pt, r: f64) -> Vec<Led> {
    let mut out = Vec::new();
    for (j, sub) in subjects(own, 9.0)
        .iter()
        .enumerate()
        .filter(|(_, s)| s.kind == Kind::Point)
    {
        for k in 0..16 {
            let a = f64::from(k) * std::f64::consts::PI / 8.0;
            let block = rect(
                center.0 + r * a.cos(),
                center.1 + r * a.sin(),
                20.0,
                5.0,
                sub.angle,
            );
            let scored = leader_of(9, &block, sub);
            let p = Placement {
                x: 0.0,
                y: 0.0,
                angle: 0.0,
                lines: vec!["a".to_owned()],
                block,
                ring: 9,
                rank: 0,
                position: "above",
                cost: 0.0,
                leader: scored,
            };
            out.push((j, k, scored, leader_to_ink(p, own).leader));
        }
    }
    out
}

/// How far `p` stands off a level box `(x0, y0, x1, y1)` drawn out by `grow` - its corners round, as the band rounds a bend (the claimed
/// convention, `stroke_band`) - 0 on it: the test's own measure, not the placer's.
fn off_box(p: Pt, (x0, y0, x1, y1): (f64, f64, f64, f64), grow: f64) -> f64 {
    let dx = (x0 - p.0).max(p.0 - x1).max(0.0);
    let dy = (y0 - p.1).max(p.1 - y1).max(0.0);
    (dx.hypot(dy) - grow).max(0.0)
}

/// A case of the cap test: its name, its sheet, its band's own measure and the stroke's end the blocks stand round.
type CapCase<'a> = (&'a str, String, &'a dyn Fn(Pt) -> f64, Pt);

/// A case of the drawn-edge test: its name, its sheet, its ink's own measure by subject, the point the blocks stand round and how far.
type EdgeCase<'a> = (&'a str, &'a String, &'a dyn Fn(usize, Pt) -> f64, Pt, f64);

/// The sheet's line shapes, or its every shape.
fn read(src: &str, lines_only: bool) -> Vec<Shape> {
    read_sheet(src)
        .unwrap()
        .0
        .into_iter()
        .filter(|s| !lines_only || s.line)
        .collect()
}

#[test]
fn a_leader_past_a_stroke_s_end_ends_on_the_end_its_cap_draws() {
    // feature 449 T193, research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a leader "ends at the nearest
    // drawn point - ... a stroke's edge" - the reader kept no `stroke-linecap`, so a leader led past a stroke's end ended on a round cap,
    // where SVG's default butt end draws nothing: past a 9 px wall's end it stopped up to 4.5 px short of the ink (T192's finding), and a
    // block within the half-width of a butt end, clear of the ink, read as touching it and drew no leader
    let sheet = |g: &str, body: &str| {
        format!(
            r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="-200 -200 400 400"><g stroke="#2D2A24" {g}>{body}</g></svg>"##
        )
    };
    let wall = r#"<line x1="0" y1="0" x2="100" y2="0" data-kind="wall"/>"#;
    // each wall's drawn band as SVG draws it, its own measure: butt flat at x 0 and 100, square drawn on to -4.5 and 104.5, round a capsule
    let flat = |p: Pt| off_box(p, (0.0, -4.5, 100.0, 4.5), 0.0);
    let square = |p: Pt| off_box(p, (-4.5, -4.5, 104.5, 4.5), 0.0);
    let round = |p: Pt| (dist(p, seg_closest(p, (0.0, 0.0), (100.0, 0.0))) - 4.5).max(0.0);
    // two flat-ended runs and the bend drawn round between them
    let bent = |p: Pt| {
        off_box(p, (0.0, -3.0, 100.0, 3.0), 0.0)
            .min(off_box(p, (97.0, 0.0, 103.0, 60.0), 0.0))
            .min((dist(p, (100.0, 0.0)) - 3.0).max(0.0))
    };
    let cases: [CapCase<'_>; 6] = [
        (
            "a butt wall, its cap unsaid",
            sheet(r#"stroke-width="9""#, wall),
            &flat,
            (100.0, 0.0),
        ),
        (
            "a butt wall",
            sheet(r#"stroke-width="9" stroke-linecap="butt""#, wall),
            &flat,
            (100.0, 0.0),
        ),
        (
            "a square wall, its cap on its group",
            sheet(r#"stroke-width="9" stroke-linecap="square""#, wall),
            &square,
            (100.0, 0.0),
        ),
        (
            "a round wall, its own cap over its group's",
            sheet(
                r#"stroke-width="9" stroke-linecap="square""#,
                &wall.replace("/>", r#" stroke-linecap="round"/>"#),
            ),
            &round,
            (100.0, 0.0),
        ),
        (
            "a wall of a cap SVG does not know, drawn butt",
            sheet(
                r#"stroke-width="9" stroke-linecap="square""#,
                &wall.replace("/>", r#" stroke-linecap="bevel"/>"#),
            ),
            &flat,
            (100.0, 0.0),
        ),
        (
            "a butt fence bent square",
            sheet(
                r#"stroke-width="6""#,
                r#"<polyline points="0,0 100,0 100,60" fill="none" data-kind="fence"/>"#,
            ),
            &bent,
            (100.0, 60.0),
        ),
    ];
    let mut wrong = Vec::new();
    for (name, src, off, end) in cases {
        let shapes = read(&src, true);
        let own: Vec<&Shape> = shapes.iter().collect();
        // each drawn tip off the ink and within its trim of at most 1 px of it, and each drawn leader the one scored: the blocks that are not
        let blocks: Vec<(usize, i32)> = led_about(&own, end, 30.0)
            .into_iter()
            .filter_map(|(j, k, scored, drawn)| {
                (scored != drawn
                    || drawn.is_some_and(|(_, tip)| off(tip) == 0.0 || off(tip) > 1.05))
                .then_some((j, k))
            })
            .collect();
        wrong.extend((!blocks.is_empty()).then_some((name, blocks)));
    }
    // a block 2 px past a butt end, inside the half-width of the end point, is clear of the ink: it draws a leader to the flat end
    let shapes = read(&sheet(r#"stroke-width="9""#, wall), true);
    let own: Vec<&Shape> = shapes.iter().collect();
    let sub = subjects(&own, 9.0)
        .into_iter()
        .find(|s| s.kind == Kind::Point)
        .unwrap();
    let past = leader_of(9, &rect(122.0, 0.0, 20.0, 5.0, 0.0), &sub);
    assert_eq!(
        (wrong, past),
        (Vec::new(), Some(((101.5, 4.5), (100.5, 4.5))))
    );
}

#[test]
fn a_leader_ends_on_the_nearest_drawn_edge() {
    // feature 449 T193, research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a leader "ends at the nearest
    // drawn point - ... a stroke's edge" - the part was chosen by its stroke's line, and a closed part read bare of its own stroke, so a
    // leader to a house with a 9 px wall drawn along its edge ended on the house's outline under the wall's ink, and one to a heavily
    // outlined house inside its outline's stroke; and Ochiba's servants' range, whose 1 px partitions end flat on its 1.5 px outline and
    // whose 0.8 px dashed roof edge crosses its passage, keeps its leaders on the outline's stroke (T192's two forms priced and not kept);
    // a stepped house whose blocks are each a fill and an outline stroked over it as two elements (Hayakawa's RESIDENCE): a block's leader,
    // read off its fill alone, ended inside the outline's stroke
    let svg = |body: &str| {
        format!(
            r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="-200 -200 600 600"><g data-kind="house">{body}</g></svg>"#
        )
    };
    let walled = svg(
        r##"<rect x="0" y="0" width="60" height="40" fill="#DDB87A"/><line x1="-20" y1="1" x2="80" y2="1" stroke="#2D2A24" stroke-width="9"/>"##,
    );
    let outlined = svg(
        r##"<rect x="0" y="0" width="60" height="40" fill="#DDB87A" stroke="#5A3F1E" stroke-width="4"/>"##,
    );
    let range = svg(concat!(
        r##"<rect x="0" y="0" width="48" height="45" fill="#C9A57A" stroke="#6B4F2A" stroke-width="1.5"/>"##,
        r##"<rect x="68" y="0" width="144" height="45" fill="#C9A57A" stroke="#6B4F2A" stroke-width="1.5"/>"##,
        r##"<line x1="116" y1="0" x2="116" y2="45" stroke="#6B4F2A" stroke-width="1"/>"##,
        r##"<line x1="164" y1="0" x2="164" y2="45" stroke="#6B4F2A" stroke-width="1"/>"##,
        r##"<line x1="48" y1="0" x2="68" y2="0" stroke="#4A3318" stroke-width="0.8" stroke-dasharray="4 3"/>"##,
    ));
    // each sheet's drawn ink, the test's own measure: the walled house's wall band and bare house, the outlined house drawn out by 2, the
    // range's two blocks drawn out by 0.75, its partitions and its dashed edge as flat-ended bands
    let off_walled = |_: usize, p: Pt| {
        off_box(p, (0.0, 0.0, 60.0, 40.0), 0.0).min(off_box(p, (-20.0, -3.5, 80.0, 5.5), 0.0))
    };
    let off_outlined = |_: usize, p: Pt| off_box(p, (0.0, 0.0, 60.0, 40.0), 2.0);
    let off_range = |_: usize, p: Pt| {
        [
            off_box(p, (0.0, 0.0, 48.0, 45.0), 0.75),
            off_box(p, (68.0, 0.0, 212.0, 45.0), 0.75),
            off_box(p, (115.5, 0.0, 116.5, 45.0), 0.0),
            off_box(p, (163.5, 0.0, 164.5, 45.0), 0.0),
            off_box(p, (48.0, -0.4, 68.0, 0.4), 0.0),
        ]
        .into_iter()
        .fold(f64::INFINITY, f64::min)
    };
    let stepped = svg(concat!(
        r##"<rect x="0" y="0" width="60" height="40" fill="#DDB87A"/>"##,
        r##"<rect x="0" y="0" width="60" height="40" fill="none" stroke="#5A3F1E" stroke-width="2.5"/>"##,
        r##"<rect x="40" y="40" width="50" height="40" fill="#DDB87A"/>"##,
        r##"<rect x="40" y="40" width="50" height="40" fill="none" stroke="#5A3F1E" stroke-width="2.5"/>"##,
    ));
    // a block's leader measured to its own block: the subjects beside are the west block's fill and outline (4, 5), then the east's
    let off_stepped = |j: usize, p: Pt| {
        if j <= 5 {
            off_box(p, (0.0, 0.0, 60.0, 40.0), 1.25)
        } else {
            off_box(p, (40.0, 40.0, 90.0, 80.0), 1.25)
        }
    };
    let cases: [EdgeCase<'_>; 4] = [
        (
            "a house with a wall along its edge",
            &walled,
            &off_walled,
            (30.0, 20.0),
            70.0,
        ),
        (
            "a heavily outlined house",
            &outlined,
            &off_outlined,
            (30.0, 20.0),
            70.0,
        ),
        (
            "a range of two stroked blocks",
            &range,
            &off_range,
            (106.0, 22.5),
            100.0,
        ),
        (
            "a stepped house, each block a fill and an outline stroked over it",
            &stepped,
            &off_stepped,
            (45.0, 40.0),
            80.0,
        ),
    ];
    let mut wrong = Vec::new();
    for (name, src, off, center, r) in cases {
        let shapes = read(src, false);
        let own: Vec<&Shape> = shapes.iter().collect();
        let blocks: Vec<(usize, i32, f64)> = led_about(&own, center, r)
            .into_iter()
            .filter_map(|(j, k, scored, drawn)| {
                let tip = drawn?.1;
                (scored != drawn || off(j, tip) == 0.0 || off(j, tip) > 1.05).then_some((
                    j,
                    k,
                    off(j, tip),
                ))
            })
            .collect();
        wrong.extend((!blocks.is_empty()).then_some((name, blocks)));
    }
    assert_eq!(wrong, Vec::<(&str, Vec<(usize, i32, f64)>)>::new());
}
