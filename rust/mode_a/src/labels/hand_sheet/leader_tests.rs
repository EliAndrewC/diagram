//! The hand sheet's leaders held to where they end (feature 449 T191, T192): a leader to a lone L-shaped house on the house, not its box's
//! corner; a leader to a disc on its drawn curve, not its box; a leader to several parts drawn as the placer scored it; and a part's drawn
//! ink - a disc's sampled curve, a stroke's edge, any other outline. Split from `tests.rs` at the 1,000-line bar (constitution X clause 13).
//!
//! Research:
//!     its tests - NONE: the placer's leaders measured against the drawn ink, deciding nothing about a building

use super::seat::subjects;
use super::tests::{at30, drawn};
use crate::labels::placer::{Kind, Placement};
use crate::py::half_sum;

#[test]
fn a_leader_to_a_lone_l_shaped_outline_ends_on_the_l_not_its_box() {
    // feature 449 T191, research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption more than twice the
    // usual gap from its feature "is tied to it by a thin leader line" - a lone L-shaped house is seated off its box (turned with it, or
    // upright where it is level), and its leader ended at that box's nearest point, on the empty ground of the L's notch (T190's probe:
    // 42 to 80 of 256 ring-9 seats more than 1.5 px off the L's ink)
    use crate::labels::geom::{dist, nearest_points, rect};
    use crate::labels::placer::leader_of;
    let corners = [
        (0.0, 0.0),
        (60.0, 0.0),
        (60.0, 20.0),
        (20.0, 20.0),
        (20.0, 50.0),
        (0.0, 50.0),
    ];
    // turned 30 degrees, level, and turned with a closing point repeating the first
    for (turn, closing) in [
        (at30 as fn(f64, f64) -> (f64, f64), false),
        (|u, v| (u, v), false),
        (at30, true),
    ] {
        let ell: Vec<(f64, f64)> = corners.iter().map(|&(u, v)| turn(u, v)).collect();
        let mut drawn_poly = ell.clone();
        drawn_poly.extend(closing.then_some(ell[0]));
        let shape = drawn("polygon", drawn_poly);
        let beside = subjects(&[&shape], 9.0).remove(1);
        assert_eq!(beside.kind, Kind::Point);
        // sixteen caption blocks round the L, 70 px from its box's middle, each tied back by a leader that runs from the block's nearest
        // point to the L to the L's own outline, short of each by its trim of at most 1 px: the blocks whose leader does not
        let mut off = Vec::new();
        for k in 0..16 {
            let a = f64::from(k) * std::f64::consts::PI / 8.0;
            let (mx, my) = turn(30.0, 25.0);
            let block = rect(
                mx + 70.0 * a.cos(),
                my + 70.0 * a.sin(),
                20.0,
                5.0,
                beside.angle,
            );
            let (start, end) =
                leader_of(9, &block, &beside).expect("a ring-9 seat clear of the L draws a leader");
            let (from, to) = nearest_points(&block, &ell, true);
            let on_ink = nearest_points(&[end], &ell, true);
            let tied = dist(on_ink.0, on_ink.1) <= 1.0 + 1e-9
                && dist(start, from) <= 1.0 + 1e-9
                && dist(end, to) <= 1.0 + 1e-9;
            off.extend((!tied).then_some(k));
        }
        assert_eq!(off, Vec::<i32>::new());
    }
}

/// A disc's outline as the reader keeps it, its drawn box: `(cx, cy)`, half-sides `rx` and `ry`, turned by `turn` about the origin.
fn disc_box(
    turn: fn(f64, f64) -> (f64, f64),
    cx: f64,
    cy: f64,
    rx: f64,
    ry: f64,
) -> Vec<(f64, f64)> {
    [
        (cx - rx, cy - ry),
        (cx + rx, cy - ry),
        (cx + rx, cy + ry),
        (cx - rx, cy + ry),
    ]
    .iter()
    .map(|&(u, v)| turn(u, v))
    .collect()
}

/// How far `p` stands off the curve a disc's drawn box holds (the image of the unit circle in the box, center plus cos t of one half-side
/// plus sin t of the other), the curve walked in 100,000 steps: the test's own measure, not the placer's.
#[expect(
    clippy::many_single_char_names,
    reason = "the curve's own names: center, half-sides, angle"
)]
fn off_curve(p: (f64, f64), b: &[(f64, f64)]) -> f64 {
    let c = (half_sum(b[0].0, b[2].0), half_sum(b[0].1, b[2].1));
    let u = ((b[1].0 - b[0].0) / 2.0, (b[1].1 - b[0].1) / 2.0);
    let v = ((b[3].0 - b[0].0) / 2.0, (b[3].1 - b[0].1) / 2.0);
    (0..100_000)
        .map(|k| {
            let t = f64::from(k) * std::f64::consts::TAU / 100_000.0;
            let q = (
                c.0 + t.cos() * u.0 + t.sin() * v.0,
                c.1 + t.cos() * u.1 + t.sin() * v.1,
            );
            crate::labels::geom::dist(p, q)
        })
        .fold(f64::INFINITY, f64::min)
}

/// Sixteen caption blocks round `own`'s box middle, 70 px out at each beside subject's angle, each leader as `leader_of` scores it at ring 9
/// and as `leader_to_ink` draws it: (subject, block, scored, drawn).
type Led = (
    usize,
    i32,
    Option<((f64, f64), (f64, f64))>,
    Option<((f64, f64), (f64, f64))>,
);
fn led_round(own: &[&super::Shape]) -> Vec<Led> {
    use crate::labels::geom::{bbox, rect};
    use crate::labels::placer::leader_of;
    let pts: Vec<(f64, f64)> = own.iter().flat_map(|s| s.poly.iter().copied()).collect();
    let (x0, y0, x1, y1) = bbox(&pts);
    let mut out = Vec::new();
    for (j, sub) in subjects(own, 9.0)
        .iter()
        .enumerate()
        .filter(|(_, s)| s.kind == Kind::Point)
    {
        for k in 0..16 {
            let a = f64::from(k) * std::f64::consts::PI / 8.0;
            let block = rect(
                half_sum(x0, x1) + 70.0 * a.cos(),
                half_sum(y0, y1) + 70.0 * a.sin(),
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
            out.push((j, k, scored, super::leader_to_ink(p, own).leader));
        }
    }
    out
}

#[test]
fn a_leader_to_a_disc_ends_on_its_drawn_curve() {
    // feature 449 T192, research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption more than twice the
    // usual gap from its feature "is tied to it by a thin leader line" - the reader keeps a disc's outline as its drawn box, and a leader to
    // a lone disc, or to a scatter of them, ended on that box, at its corner over the empty ground beside the curve (T191's leftover: three
    // pool leaders 1.75 to 4.45 px off the curve, Hayakawa's old pines and striking posts, Ubame's fire-water tubs)
    let level = |u: f64, v: f64| (u, v);
    let well = drawn("circle", disc_box(level, 0.0, 0.0, 20.0, 20.0));
    let pond = drawn("ellipse", disc_box(at30, 0.0, 0.0, 30.0, 12.0));
    let (post_a, post_b) = (
        drawn("circle", disc_box(level, 0.0, 0.0, 6.0, 6.0)),
        drawn("circle", disc_box(level, 30.0, 10.0, 6.0, 6.0)),
    );
    for (name, own) in [
        ("a lone circle", vec![&well]),
        ("a lone turned ellipse", vec![&pond]),
        ("two posts", vec![&post_a, &post_b]),
    ] {
        // each drawn leader's tip within its trim of at most 1 px of the curve, and the curve's sampling: the blocks whose tip is not
        let off: Vec<(usize, i32)> = led_round(&own)
            .into_iter()
            .filter_map(|(j, k, _, drawn)| {
                let (_, tip) = drawn?;
                let gap = own
                    .iter()
                    .map(|s| off_curve(tip, &s.poly))
                    .fold(f64::INFINITY, f64::min);
                (gap > 1.05).then_some((j, k))
            })
            .collect();
        assert_eq!(off, Vec::<(usize, i32)>::new(), "{name}");
    }
}

#[test]
fn a_leader_to_several_parts_is_drawn_as_it_was_scored() {
    // feature 449 T192: a subject of several parts scored its leader to its box, while the hand sheet drew it to the parts' ink
    // (`leader_to_ink`), so the placer weighed a leader it never drew (T191's leftover: Hayakawa's striking posts and weapon rack, the drawn
    // tips 3.85 and 1.36 px from the scored ones) - a weapon rack of three rails, two striking posts, and a barge with its mooring line
    let level = |u: f64, v: f64| (u, v);
    let rails: Vec<super::Shape> = [(0.0, 0.0), (0.0, 14.0), (16.0, 28.0)]
        .iter()
        .map(|&(x, y)| {
            drawn(
                "rect",
                vec![(x, y), (x + 24.0, y), (x + 24.0, y + 4.0), (x, y + 4.0)],
            )
        })
        .collect();
    let (post_a, post_b) = (
        drawn("circle", disc_box(level, 0.0, 0.0, 6.0, 6.0)),
        drawn("circle", disc_box(level, 30.0, 10.0, 6.0, 6.0)),
    );
    let hull = drawn(
        "rect",
        vec![(0.0, 0.0), (20.0, 0.0), (20.0, 8.0), (0.0, 8.0)],
    );
    let rope = super::Shape {
        tag: "line".to_owned(),
        poly: vec![(20.0, 4.0), (44.0, 30.0)],
        half: 0.75,
        line: true,
        ..super::Shape::default()
    };
    for (name, own) in [
        ("a weapon rack", rails.iter().collect::<Vec<_>>()),
        ("two posts", vec![&post_a, &post_b]),
        ("a moored barge", vec![&hull, &rope]),
    ] {
        // the blocks whose drawn leader is not the one scored
        let moved: Vec<(usize, i32)> = led_round(&own)
            .into_iter()
            .filter_map(|(j, k, scored, drawn)| (scored != drawn).then_some((j, k)))
            .collect();
        assert_eq!(moved, Vec::<(usize, i32)>::new(), "{name}");
    }
}

#[test]
fn a_drawn_part_s_ink_is_its_curve_its_stroke_or_its_outline() {
    // feature 449 T192: a disc's drawn curve sampled with no chord more than DISC_SAG_PX inside it - 80 points at the pool's largest disc
    // (a 45 px circle, its half-sides bounding R at 45 * sqrt 2), 8 for a disc under the sag - a stroke its line at its half-width (at least
    // half a pixel), any other shape, or a disc drawn with other than its four box corners, its outline as read
    use super::classify::{disc_samples, drawn_ink};
    use crate::labels::placer::{leader_of, Cap, InkPart, Subject};
    assert_eq!(
        (
            disc_samples(45.0 * 2.0_f64.sqrt()),
            disc_samples(0.01),
            disc_samples(0.5)
        ),
        (80, 8, 8)
    );
    let well = drawn(
        "circle",
        vec![(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)],
    );
    let ink = drawn_ink(&well);
    assert_eq!(
        (ink.pts.len(), ink.line, ink.pts[0]),
        (12, false, (1.0, 0.0))
    );
    let grain = drawn(
        "circle",
        vec![(-0.01, -0.01), (0.01, -0.01), (0.01, 0.01), (-0.01, 0.01)],
    );
    assert_eq!(drawn_ink(&grain).pts.len(), 8);
    let odd = drawn("circle", vec![(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]);
    assert_eq!(drawn_ink(&odd).pts, odd.poly);
    let rope = super::Shape {
        tag: "line".to_owned(),
        poly: vec![(0.0, 0.0), (0.0, 100.0)],
        half: 0.25,
        line: true,
        ..super::Shape::default()
    };
    assert_eq!(
        drawn_ink(&rope),
        InkPart {
            pts: rope.poly.clone(),
            line: true,
            half: 0.5,
            cap: Cap::Butt,
        }
    );
    // a drawn leader ending within a stroke's band is left as it is: the placer's own leader to a stroke ends at its edge, short by its trim
    let led = Placement {
        x: 0.0,
        y: 0.0,
        angle: 0.0,
        lines: vec!["a".to_owned()],
        block: Vec::new(),
        ring: 9,
        rank: 0,
        position: "above",
        cost: 0.0,
        leader: Some(((20.0, 5.0), (0.5, 5.0))),
    };
    assert_eq!(
        super::leader_to_ink(led.clone(), &[&rope]).leader,
        led.leader
    );
    // a block reaching a stroke's edge touches what it names: no leader; one clear of it ends at the stroke's edge, short by its trim
    let border = Subject {
        ink: vec![InkPart {
            pts: vec![(0.0, 0.0), (0.0, 100.0)],
            line: true,
            half: 4.5,
            cap: Cap::Butt,
        }],
        ..Subject::new(
            Kind::Point,
            vec![(-4.5, 0.0), (4.5, 0.0), (4.5, 100.0), (-4.5, 100.0)],
            0.0,
        )
    };
    let near = crate::labels::geom::rect(24.0, 50.0, 20.0, 5.0, 0.0);
    assert_eq!(leader_of(9, &near, &border), None);
    let far = crate::labels::geom::rect(40.0, 50.0, 20.0, 5.0, 0.0);
    assert_eq!(
        leader_of(9, &far, &border).map(|(a, b)| (to_billionth(a), to_billionth(b))),
        Some(((19.0, 45.0), (5.5, 45.0)))
    );
}

/// A point to a billionth: the band's corners are its line's points plus and less its half-width, a rounding off the drawn figure.
fn to_billionth(p: (f64, f64)) -> (f64, f64) {
    ((p.0 * 1e9).round() / 1e9, (p.1 * 1e9).round() / 1e9)
}

#[test]
fn a_leader_ends_on_the_nearest_drawn_edge_an_exact_tie_on_the_outline_then_the_wider_stroke() {
    // feature 449 T192, T193: a part is chosen by its drawn edge - a stroke's band, an outline drawn out by its own stroke - so a stroke
    // drawn along a bare building's edge takes the leader by its half-width and a stroked outline takes it back (Ochiba's SERVANTS'
    // QUARTERS); on an exact tie, a closed outline before a stroke, and the wider of two strokes, whatever their order
    use crate::labels::placer::{leader_of, Cap, InkPart, Subject};
    let far = crate::labels::geom::rect(40.0, 50.0, 20.0, 5.0, 0.0);
    let stroke = |x: f64, y0: f64, y1: f64, half: f64| InkPart {
        pts: vec![(x, y0), (x, y1)],
        line: true,
        half,
        cap: Cap::Butt,
    };
    let house = |half: f64| InkPart {
        pts: vec![(-10.0, 45.0), (0.0, 45.0), (0.0, 55.0), (-10.0, 55.0)],
        line: false,
        half,
        cap: Cap::Butt,
    };
    let led_to = |ink: Vec<InkPart>| {
        let sub = Subject {
            ink,
            ..Subject::new(
                Kind::Point,
                vec![(-10.0, 0.0), (0.0, 0.0), (0.0, 100.0), (-10.0, 100.0)],
                0.0,
            )
        };
        leader_of(9, &far, &sub).map(|l| to_billionth(l.1))
    };
    // the nearer drawn edge: a 1 px stroke on a bare outline's edge, then the outline's own 1.5 px stroke over it
    let edge = stroke(0.0, 0.0, 100.0, 0.5);
    assert_eq!(led_to(vec![house(0.0), edge.clone()]), Some((1.5, 45.0)));
    assert_eq!(led_to(vec![edge.clone(), house(0.75)]), Some((1.75, 45.0)));
    // exact ties 20 px off, ending apart: the outline's (0, 45) before a stroke's (0, 47), the 9 px stroke's (0, 51) before the 2.5 px one's (0, 47)
    let (thin, wide) = (stroke(-0.5, 47.0, 53.0, 0.5), stroke(-4.5, 49.0, 51.0, 4.5));
    assert_eq!(led_to(vec![thin.clone(), house(0.0)]), Some((1.0, 45.0)));
    assert_eq!(led_to(vec![house(0.0), thin]), Some((1.0, 45.0)));
    let mid = stroke(-1.25, 47.0, 53.0, 1.25);
    assert_eq!(led_to(vec![mid.clone(), wide.clone()]), Some((1.0, 51.0)));
    assert_eq!(led_to(vec![wide, mid]), Some((1.0, 51.0)));
}

#[test]
fn a_stroke_s_band_and_a_part_s_drawn_edge() {
    // feature 449 T193: a stroke of no length is one disc; a bend is a disc and each end its cap; a leader's start within a part's own
    // stroke lies on its ink, and draws no leader
    use super::classify::drawn_ink;
    use crate::labels::placer::{band_nearest, stroke_band, Cap, InkPart};
    let part = |pts: Vec<(f64, f64)>, cap: Cap| InkPart {
        pts,
        line: true,
        half: 1.0,
        cap,
    };
    assert_eq!(
        stroke_band(&part(vec![(5.0, 5.0), (5.0, 5.0)], Cap::Butt)),
        (Vec::new(), vec![(5.0, 5.0)])
    );
    let (rects, discs) = stroke_band(&part(
        vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)],
        Cap::Round,
    ));
    assert_eq!(rects.len(), 2);
    assert_eq!(discs, vec![(10.0, 0.0), (0.0, 0.0), (10.0, 10.0)]);
    // a block reaching a round end past the stroke's rectangle touches it: the block's own point twice
    let (a, b) = band_nearest(
        &crate::labels::geom::rect(11.5, 0.0, 1.0, 0.2, 0.0),
        &part(vec![(0.0, 0.0), (10.0, 0.0)], Cap::Round),
    );
    assert_eq!(a, b);
    let (square, _) = stroke_band(&part(vec![(0.0, 0.0), (10.0, 0.0)], Cap::Square));
    assert_eq!(
        square,
        vec![vec![(-1.0, 1.0), (11.0, 1.0), (11.0, -1.0), (-1.0, -1.0)]]
    );
    assert_eq!(
        (
            Cap::of("square"),
            Cap::of("round"),
            Cap::of("butt"),
            Cap::of("inherit")
        ),
        (Cap::Square, Cap::Round, Cap::Butt, Cap::Butt)
    );
    let shed = super::Shape {
        edge: 2.0,
        ..drawn(
            "rect",
            vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],
        )
    };
    assert_eq!(drawn_ink(&shed).half.to_bits(), 2.0_f64.to_bits());
    let led = |start: (f64, f64)| Placement {
        x: 0.0,
        y: 0.0,
        angle: 0.0,
        lines: vec!["a".to_owned()],
        block: Vec::new(),
        ring: 9,
        rank: 0,
        position: "above",
        cost: 0.0,
        leader: Some((start, (30.0, 30.0))),
    };
    // from 1 px off the outline, inside its 2 px stroke: on the ink; from 20 px off, to the stroke's edge 2 px out, short by its trim
    assert_eq!(
        super::leader_to_ink(led((11.0, 5.0)), &[&shed]).leader,
        None
    );
    assert_eq!(
        super::leader_to_ink(led((30.0, 5.0)), &[&shed]).leader,
        Some(((30.0, 5.0), (13.0, 5.0)))
    );
}
