//! A placement written as the Python wrote it (feature 449 T151; each line printed by `labels/svg.py` under `CPython` 3.14.4,
//! 2026-11-18).
//!
//! Research:
//!     its tests - NONE: the port held to the Python's answers, deciding nothing about a building

use super::{caption_svg, leader_svg};
use crate::labels::placer::Placement;

fn placement(angle: f64, lines: &[&str], leader: Option<((f64, f64), (f64, f64))>) -> Placement {
    Placement {
        x: 100.0,
        y: 50.0,
        angle,
        lines: lines.iter().map(|l| (*l).to_owned()).collect(),
        block: Vec::new(),
        ring: 0,
        rank: 0,
        position: "above",
        cost: 0.0,
        leader,
    }
}

#[test]
fn a_caption_and_its_leader_are_written_as_the_python_wrote_them() {
    let p = placement(30.0, &["A & B", "<c>"], Some(((1.0, 2.0), (3.05, 4.0))));
    assert_eq!(
        caption_svg(&p, 12.0, " font-style=\"italic\"", "#3A2E1C", "well", "w1 w2"),
        "<text x=\"100.0\" y=\"43.1\" text-anchor=\"middle\" font-size=\"12\" font-style=\"italic\" fill=\"#3A2E1C\" transform=\"rotate(30.0 100.0 46.7)\" data-kind=\"well\" data-names=\"w1 w2\"><tspan x=\"100.0\" dy=\"0.0\">A &amp; B</tspan><tspan x=\"100.0\" dy=\"13.8\">&lt;c&gt;</tspan></text>"
    );
    // an angle that rounds to none turns nothing
    let q = placement(0.04, &["one"], None);
    assert_eq!(caption_svg(&q, 8.5, "", "#000", "", ""), "<text x=\"100.0\" y=\"50.0\" text-anchor=\"middle\" font-size=\"8.5\" fill=\"#000\">one</text>");
    assert_eq!(leader_svg(&q, 8.0, "#000", "", false), "");
    // 3.05 is printed 3.0, the float below it; the thinnest stroke 0.60
    assert_eq!(
        leader_svg(&p, 5.0, "#111", "well", true),
        "<line x1=\"1.0\" y1=\"2.0\" x2=\"3.0\" y2=\"4.0\" stroke=\"#111\" stroke-width=\"0.60\" stroke-linecap=\"round\" data-kind=\"well\" data-leader=\"1\"/>"
    );
    assert_eq!(
        leader_svg(&p, 12.0, "#111", "", false),
        "<line x1=\"1.0\" y1=\"2.0\" x2=\"3.0\" y2=\"4.0\" stroke=\"#111\" stroke-width=\"0.96\" stroke-linecap=\"round\"/>"
    );
}
