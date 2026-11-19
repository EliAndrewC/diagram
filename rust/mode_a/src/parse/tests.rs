//! The parse (feature 449 T170): the marks a caller read first, a room folded into its building, a path's rings, and each form of
//! `fixtures.rs` (the lockstep that held every field against the Python's deleted with it, T212).
//!
//! Research:
//!     the parse's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{parse_labels, parse_marked, parse_svg, path_rings, rooms_folded, Rect};
use crate::tagged::marks;

#[test]
fn the_marks_a_caller_read_give_the_same_parse() {
    let svg = r##"<svg><rect id="precinct" x="0" y="0" width="9" height="9" fill="#fff"/><rect data-kind="hearth" x="1" y="1" width="2" height="2" fill="#2D2A24"/><rect x="4" y="1" width="2" height="2" fill="#2D2A24"/></svg>"##;
    let plan = parse_svg(svg).unwrap();
    assert_eq!(plan, parse_marked(svg, &marks(svg).unwrap()).unwrap());
    assert_eq!(plan.door_rects.len(), 1, "the tagged hearth is no door");
    assert!(parse_marked("<svg/>", &[]).is_err());
}

#[test]
fn a_room_drawn_inside_its_building_is_folded_into_it() {
    let r = |x, fill: &str| Rect::new(x, 0.0, 10.0, 10.0, fill, 0);
    let inner = Rect::new(2.0, 2.0, 3.0, 3.0, "#DDB87A", 1);
    let folded = rooms_folded(vec![
        r(0.0, "#DDB87A"),
        inner.clone(),
        r(20.0, "#DDB87A"),
        Rect {
            fill: "#C9A57A".into(),
            ..inner
        },
    ]);
    assert_eq!(folded.len(), 3);
}

#[test]
fn a_path_s_rings_are_read_only_when_rectilinear() {
    assert_eq!(
        path_rings("M 0 0 H 4 V 4 H 0 Z").unwrap(),
        Some(vec![vec![(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]])
    );
    assert_eq!(path_rings("M 0 0 L 4 4 L 0 4 L 0 1").unwrap(), None);
    assert_eq!(path_rings("M 0 0 H 4 Z").unwrap(), None);
    assert_eq!(path_rings("c 1 1").unwrap(), None);
    assert_eq!(path_rings("1 2").unwrap(), None, "a point before any move");
    assert!(path_rings("M 1").is_err());
}

#[test]
fn a_rect_whose_size_is_no_number_is_skipped() {
    let sheet = |rect: &str| {
        format!(
            r##"<svg><rect id="precinct" x="0" y="0" width="900" height="900" fill="#fff"/>{rect}</svg>"##
        )
    };
    let bare = parse_svg(&sheet("")).unwrap();
    let wide = r##"<rect x="1" y="1" width="wide" height="200" fill="#DDB87A"/>"##;
    assert_eq!(parse_svg(&sheet(wide)).unwrap().buildings, bare.buildings);
    let drawn = r##"<rect x="1" y="1" width="200" height="200" fill="#DDB87A"/>"##;
    assert_ne!(parse_svg(&sheet(drawn)).unwrap().buildings, bare.buildings);
}

#[test]
fn a_roofed_court_with_no_position_is_refused_as_the_python_refused_it() {
    let svg = r##"<svg><rect id="precinct" x="0" y="0" width="900" height="900" fill="#fff"/><rect y="1" width="90" height="90" fill="url(#court-cobbles)" stroke="#5A3F1E"/></svg>"##;
    let err = parse_svg(svg).unwrap_err();
    assert_eq!((err.kind, err.message.as_str()), ("KeyError", "x"));
}

#[test]
fn a_caption_with_no_place_or_no_words_is_no_label_and_bold_figures_run_narrow() {
    let svg = r#"<svg><text y="3">no x</text><text x="5" y="5">  </text><text x="1" y="2" font-weight="bold">100</text><text x="1" y="9" font-weight="bold">HALL</text></svg>"#;
    let labels = parse_labels(svg).unwrap();
    let texts: Vec<&str> = labels.iter().map(|l| l.text.as_str()).collect();
    assert_eq!(texts, ["100", "HALL"]);
    // a run with no letter is measured as mixed case, the narrower advance, and caps at the wider
    assert!(labels[0].w / 3.0 < labels[1].w / 4.0);
}
