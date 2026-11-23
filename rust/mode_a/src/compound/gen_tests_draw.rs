//! The compound generator's drawing tests (feature 449 T152; split from `gen_tests_parts.rs` at the 1,000-line bar by 449 T354's bundle):
//! the interiors and the gate posts on any wall, the open shed on its posts, the hearing court's mats on the dais's axis and the dais's
//! caption.
//!
//! Research: the generator's drawing tests - NONE: fixtures and assertions, deciding nothing about a building

use super::gen_tests_seat::{b, seated, with};
use super::parts::Seated;

/// The interiors drawn on any wall - a stable's stalls and a cell's bars measured from their court face - and gate posts on every wall.
#[test]
fn the_interiors_and_the_gate_posts_draw_on_any_wall() {
    let gates = r#""gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}, {"kind": "side gate", "wall": "N", "at": 50, "width": 6}, {"kind": "side gate", "wall": "E", "at": 25, "width": 6}]"#;
    let src = super::gen_tests::small(&format!(
        r#", "buildings": [{}, {}, {}]"#,
        b(
            "stables",
            "stables",
            "service",
            (24.0, 18.0),
            "inner",
            "N",
            r#", "interior": "stables""#
        ),
        b(
            "cell",
            "cell",
            "cell",
            (10.0, 12.0),
            "inner",
            "W",
            r#", "interior": "cell""#
        ),
        b(
            "stable2",
            "stables",
            "service",
            (18.0, 24.0),
            "outer",
            "W",
            r#", "interior": "stables""#
        )
    ));
    let p = super::spec::read(&src.replacen(
        r#""gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}]"#,
        gates,
        1,
    ))
    .unwrap();
    let l = seated(&p).unwrap();
    let text = super::sheet(&p, &l, &Seated::default());
    assert_eq!(text.matches(r#"data-kind="side gate""#).count(), 2);
    assert_eq!(text.matches("stroke-dasharray=\"3 2\"").count(), 2);
}

/// An open-sided workshop is drawn as the hand sheet draws it: a hatched roof over open sides on six posts, with no door and not the
/// shrine's solid mark (449 T359: the round trip's cinnabar workshop was the shrine's exact fill with a door, where its legend, docs/buildings.md's
/// colonnade-hatch and ochiba-magistracy.svg draw an open shed on six posts).
#[test]
fn an_open_shed_is_a_hatched_roof_on_six_posts_with_no_door() {
    let shed = |name: &str, wh: (f64, f64), wall: &str| {
        b(
            name,
            "cinnabar workshop",
            "shrine",
            wh,
            "inner",
            wall,
            r#", "interior": "open shed""#,
        )
    };
    // one shed wider than deep, its posts in two rows along x; one deeper than wide, in two columns along y
    let p = with(
        &[
            shed("wide", (30.0, 24.0), "E"),
            shed("deep", (12.0, 20.0), "W"),
        ],
        "",
    );
    let mut l = seated(&p).unwrap();
    l.seat_doors(&p).unwrap();
    assert!(l.doors.is_empty(), "{:?}", l.doors.len());
    let text = super::sheet(&p, &l, &Seated::default());
    let at = text.find(r#"<g data-kind="cinnabar workshop">"#).unwrap();
    let body = &text[at..at + text[at..].find("</g>").unwrap()];
    assert!(body.contains(r#"fill="url(#colonnade-hatch)""#), "{body}");
    assert!(!body.contains("#C9876C"), "{body}");
    assert_eq!(body.matches("<circle").count(), 6, "{body}");
    let drawn = &text[text.find("</defs>").unwrap()..];
    assert_eq!(drawn.matches("<circle").count(), 12, "{drawn}");
    let deep = l.seats[1].unwrap();
    let column = super::emit::n(super::emit::px(deep.0 + 10.0 / 3.0, 0.0).0);
    let on_column = text.matches(&format!(r#"<circle cx="{column}""#)).count();
    assert_eq!(on_column, 3, "{text}");
    assert!(text.contains(r#"<pattern id="colonnade-hatch""#));
}

/// A cell's lattice shows beside its door: on a 10 ft court face the 6 ft door covered every bar at 2 ft spacing, so the county's cell
/// read as an end bay of the rowhouse it is joined to (449 T351, glyph-check 2026-11-23 F1; the round arbiter's
/// ask:cell-lattice-hidden-449-T351): at least two bars stand clear of every door's span.
#[test]
fn a_cells_bars_show_beside_its_door() {
    let p = with(
        &[b(
            "cell",
            "cell",
            "cell",
            (10.0, 12.0),
            "outer",
            "S",
            r#", "interior": "cell""#,
        )],
        "",
    );
    let mut l = seated(&p).unwrap();
    l.seat_doors(&p).unwrap();
    let text = super::sheet(&p, &l, &Seated::default());
    let attr = |e: &str, k: &str| -> f64 {
        let at = e.find(&format!(r#" {k}=""#)).unwrap() + k.len() + 3;
        e[at..at + e[at..].find('"').unwrap()].parse().unwrap()
    };
    let door_mark = r#"data-kind="door" data-part-of="cell""#;
    let door_at = text.find(door_mark).unwrap();
    let door = &text[text[..door_at].rfind("<rect").unwrap()..door_at];
    let (d0, d1) = (attr(door, "x"), attr(door, "x") + attr(door, "width"));
    let at = text.find(r#"<g data-kind="cell">"#).unwrap();
    let body = &text[at..at + text[at..].find("</g>").unwrap()];
    let clear = body
        .split("<line")
        .skip(1)
        .map(|e| attr(e, "x1"))
        .filter(|&x| x < d0 - 0.5 || x > d1 + 0.5)
        .count();
    let door_span = (d0, d1);
    assert!(clear >= 2, "{clear} clear of {door_span:?}: {body}");
}

/// The accused's mat kneels on the dais's axis, not at the court's middle, where the two differ: a court cut short of the hall's door
/// keeps its mats before the magistrate's seat (449 T354: the round trip's mats, re-centered on its shortened court, knelt 8 ft west of
/// the dais); a court with no dais over it keeps them at its middle.
#[test]
fn the_accused_kneels_on_the_dais_axis() {
    let dais = r#", "rooms": [{"kind": "magistrate's dais", "caption": "dais", "x": 11, "y": 10, "w": 18, "h": 10, "style": "dais"}]"#;
    let court = r#", "zones": [{"kind": "hearing court", "x": 4, "y": 75, "w": 60, "h": 15, "floor": "white gravel"}]"#;
    let mat = |text: &str| -> String {
        let at = text.find(r#"data-kind="kneeling positions""#).unwrap();
        let x = at + text[at..].find(r#"<rect x=""#).unwrap() + 9;
        text[x..x + text[x..].find('"').unwrap()].to_owned()
    };
    let p = with(
        &[b(
            "hall",
            "office hall",
            "lord",
            (40.0, 20.0),
            "outer",
            "divider",
            dais,
        )],
        court,
    );
    let l = seated(&p).unwrap();
    let axis = l.seats[0].unwrap().0 + 20.0;
    let off = (axis - 34.0).abs();
    assert!(off > 3.0, "the dais at {axis} must be off the middle");
    let text = super::sheet(&p, &l, &Seated::default());
    assert_eq!(
        mat(&text),
        super::emit::n(super::emit::px(axis - 3.0, 0.0).0)
    );
    let bare = with(
        &[b(
            "hall",
            "office hall",
            "lord",
            (40.0, 20.0),
            "outer",
            "divider",
            "",
        )],
        court,
    );
    let text = super::sheet(&bare, &seated(&bare).unwrap(), &Seated::default());
    assert_eq!(mat(&text), super::emit::n(super::emit::px(31.0, 0.0).0));
}

/// A dais's caption reads wherever the placer seats it: the hand sheets' dark ink at 7 px, never the light ink that read only on the
/// dais (449 T338: the county example's white caption sat wholly off its 18 ft dais on the hall's light floor, about 1.8:1).
#[test]
fn a_dais_caption_is_dark_ink_that_reads_on_or_off_the_dais() {
    let dais = r#", "rooms": [{"kind": "q", "caption": "dais", "x": 11, "y": 10, "w": 18, "h": 10, "style": "dais"}]"#;
    let p = with(
        &[b(
            "hall",
            "k",
            "lord",
            (40.0, 20.0),
            "outer",
            "divider",
            dais,
        )],
        "",
    );
    let text = super::sheet(&p, &seated(&p).unwrap(), &Seated::default());
    assert!(text.contains(
        r##"<text font-size="7" font-weight="bold" fill="#3A2E1C" data-kind="q" data-names="##
    ));
    assert!(!text.contains("#FFFAE6"));
}
