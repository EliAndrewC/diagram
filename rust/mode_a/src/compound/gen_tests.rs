//! The compound generator's unit tests (feature 449 T152): the spec read, the rolls, the grid, the span search and the writer - each a rule of
//! its module, on small programs built here.
//!
//! Research: the generator's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::emit::{esc, n, paint, px, Svg};
use super::grid::{overlaps, Grid, What};
use super::roll::{chance, choice, crc32, Rng};
use super::span::{centered, insert, nearest, walk, Ask, Strip};
use super::spec::{read, Court, Face, Wall};

/// A small program: a 100 x 100 ft compound, its divider at 50, its main gate in the south wall; `extra` adds fields.
pub fn small(extra: &str) -> String {
    format!(
        r#"{{"name": "t", "title": "T", "envelope": {{"w": 100, "h": 100, "divider": 50}},
        "gates": [{{"kind": "main gate", "wall": "S", "at": 50, "width": 6}}]{extra}}}"#
    )
}

#[test]
fn a_spec_reads_its_program_and_its_defaults() {
    let p = read(&small(
        r#", "subtitle": "s", "middle_gate": 5,
        "zones": [{"kind": "garden", "caption": "g", "x": 1, "y": 2, "w": 3, "h": 4}],
        "buildings": [{"name": "a", "kind": "kitchen", "role": "service", "w": 10, "h": 8, "court": "inner", "wall": "N",
          "order": 3, "rank": 2, "inset": 1, "joins": "b", "end": "W", "beside": "main gate", "near": 7, "bays": [5],
          "doors": [{"face": "E", "at": 0.5}], "interior": "cell",
          "rooms": [{"kind": "r", "x": 0, "y": 0, "w": 1, "h": 1}, {"kind": "q", "caption": "c", "x": 0, "y": 0, "w": 1, "h": 1, "style": "dais"}]},
          {"name": "b", "kind": "k", "caption": "B", "role": "lord", "w": 1, "h": 1, "court": "outer", "wall": "divider"}],
        "parts": {"bath": {"w": 10, "h": 8}, "wells": ["kitchen"], "privies": ["b"], "rack_by": "b", "posts": 2, "roji": true, "board": true,
          "landform": "upland"},
        "knobs": [{"key": "k", "options": ["x", "y"], "value": "x"}]"#,
    ))
    .unwrap();
    assert_eq!(
        (p.subtitle.as_str(), p.middle_gate, p.zones[0].bx),
        ("s", 5.0, (1.0, 2.0, 4.0, 6.0))
    );
    let a = &p.buildings[0];
    assert_eq!(
        (
            a.caption.as_str(),
            a.rank,
            a.inset,
            a.end,
            a.beside_gate,
            a.near
        ),
        ("a", 2, 1.0, Some(Face::W), true, Some(7.0))
    );
    assert_eq!(
        (a.court, a.wall, a.bays.clone(), a.doors[0].face),
        (Court::Inner, Wall::Side(Face::N), vec![5.0], Face::E)
    );
    assert_eq!(
        (a.rooms[0].style.as_str(), a.rooms[1].style.as_str()),
        ("room", "dais")
    );
    let b = &p.buildings[1];
    assert_eq!(
        (b.caption.as_str(), b.rank, b.order, b.wall, b.court),
        ("B", 1, 0, Wall::Divider, Court::Outer)
    );
    assert_eq!(
        (
            p.parts.bath,
            p.parts.posts,
            p.parts.roji,
            p.knobs[0].value.as_str()
        ),
        (Some((10.0, 8.0)), 2, true, "x")
    );
    let bare = read(&small("")).unwrap();
    assert_eq!(
        (bare.middle_gate, bare.parts.posts, bare.subtitle.as_str()),
        (6.0, 0, "")
    );
}

#[test]
fn a_spec_refuses_what_is_not_a_program() {
    for (src, said) in [
        ("{", "JSONDecodeError"),
        ("[]", "program is no object"),
        (r#"{"name": "t"}"#, "envelope is no object"),
        (
            r#"{"name": "t", "envelope": {"w": 1, "h": 1, "divider": 1}, "gates": []}"#,
            "first gate",
        ),
        (
            &small(r#", "buildings": [{"name": "a"}]"#),
            "\"kind\" is no string",
        ),
        (
            &small(r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": "x"}]"#),
            "\"w\" is no number",
        ),
        (
            &small(
                r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": 1, "h": 1, "court": "mid", "wall": "N"}]"#,
            ),
            "inner or outer",
        ),
        (
            &small(
                r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": 1, "h": 1, "court": "inner", "wall": "Q"}]"#,
            ),
            "N, S, E or W",
        ),
        (
            &small(
                r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": 1, "h": 1, "court": "inner", "wall": "N", "bays": ["x"]}]"#,
            ),
            "a bay",
        ),
        (
            &small(
                r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": 1, "h": 1, "court": "inner", "wall": "N", "inset": "x"}]"#,
            ),
            "\"inset\"",
        ),
        (
            &small(
                r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": 1, "h": 1, "court": "inner", "wall": "N", "end": "Q"}]"#,
            ),
            "N, S, E or W",
        ),
        (
            &small(
                r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": 1, "h": 1, "court": "inner", "wall": "N", "doors": [1]}]"#,
            ),
            "door is no object",
        ),
        (
            &small(
                r#", "buildings": [{"name": "a", "kind": "k", "role": "r", "w": 1, "h": 1, "court": "inner", "wall": "N", "rooms": [1]}]"#,
            ),
            "room is no object",
        ),
        (&small(r#", "buildings": [1]"#), "building is no object"),
        (&small(r#", "zones": [1]"#), "zone is no object"),
        (&small(r#", "parts": 1"#), "parts is no object"),
        (&small(r#", "parts": {"bath": 1}"#), "bath is no object"),
        (&small(r#", "knobs": [1]"#), "knob is no object"),
        (
            r#"{"name": "t", "envelope": {"w": 1, "h": 1, "divider": 1}, "gates": [1]}"#,
            "gate is no object",
        ),
    ] {
        let e = read(src).unwrap_err();
        let said_all = format!("{}: {}", e.kind, e.message);
        assert!(said_all.contains(said), "{said_all}");
    }
}

#[test]
fn a_face_knows_its_opposite_and_its_axis() {
    for (f, o, x) in [
        (Face::N, Face::S, true),
        (Face::S, Face::N, true),
        (Face::E, Face::W, false),
        (Face::W, Face::E, false),
    ] {
        assert_eq!((f.opposite(), f.along_x()), (o, x));
    }
}

/// The rolls are Python's: zlib's CRC-32 and `random.Random(seed)` (values from `CPython` 3.14, `zlib.crc32` and `random.Random`).
#[test]
fn the_rolls_are_the_docs_formula_as_python_draws_it() {
    assert_eq!(
        crc32(b"The quick brown fox jumps over the lazy dog"),
        0x414f_a339
    );
    assert!((Rng::new(0).random() - 0.844_421_851_525_048_1).abs() < 1e-15);
    assert_eq!(Rng::new(12345).below(1000), 426);
    assert_eq!(Rng::keyed("x:y").below(7), 4);
    assert!(
        (Rng::keyed("ochiba-roundtrip-test:well gear 1").random() - 0.321_045_650_762_320_06).abs()
            < 1e-15
    );
    let forms = ["one-bay gate".to_owned(), "gate range".to_owned()];
    assert_eq!(
        choice("county-magistracy-example", "main gate form", &forms).map(String::as_str),
        Some("one-bay gate")
    );
    assert_eq!(choice("t", "k", &[]), None);
    assert!(chance("ochiba-roundtrip-test", "well gear 1", 0.75));
    assert!(!chance("ochiba-roundtrip-test", "well gear 1", 0.3));
    let mut r = Rng::new(7);
    let draws: Vec<u32> = (0..700).map(|_| r.below(3)).collect();
    assert!(draws.iter().all(|d| *d < 3));
}

#[test]
fn the_grid_reads_each_entry_once_and_overlap_needs_area() {
    let mut g = Grid::new(100.0, 90.0);
    let a = g.file((10.0, 10.0, 90.0, 20.0), What::Gate);
    let _ = g.file((200.0, 200.0, 210.0, 210.0), What::Zone(0));
    assert_eq!(g.query((0.0, 0.0, 100.0, 100.0), "t"), vec![a]);
    assert!(g.query((90.0, 10.0, 95.0, 20.0), "t").is_empty());
    assert!(!overlaps((0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 2.0, 1.0)));
    assert!(overlaps((0.0, 0.0, 1.0, 1.0), (0.5, 0.5, 2.0, 2.0)));
    assert_eq!(
        Grid::new(0.0, 0.0).query((0.0, 0.0, 1.0, 1.0), "t"),
        Vec::<usize>::new()
    );
}

fn rule_all(e: &super::grid::Ent) -> Option<(f64, f64)> {
    match e.what {
        What::Gate => None,
        What::Building(_) => Some((2.0, 0.0)),
        _ => Some((0.0, 0.0)),
    }
}

fn strip() -> Strip {
    Strip {
        along_x: true,
        p0: 0.0,
        p1: 10.0,
        lo: 0.0,
        hi: 200.0,
    }
}

#[test]
fn a_span_search_reads_off_the_first_free_span_each_way() {
    let mut g = Grid::new(200.0, 20.0);
    g.file((20.0, 0.0, 30.0, 10.0), What::Building(0));
    g.file((60.0, 0.0, 70.0, 10.0), What::Zone(0));
    g.file((0.0, 0.0, 200.0, 10.0), What::Gate);
    g.file((100.0, 12.0, 110.0, 20.0), What::Zone(1));
    let ask = Ask {
        strip: strip(),
        len: 15.0,
        rule: &rule_all,
        reach: 2.0,
        f: "t",
    };
    assert_eq!(walk(&mut g, &ask, &[], 0.0, 1.0), Some(0.0));
    assert_eq!(walk(&mut g, &ask, &[], 10.0, 1.0), Some(32.0));
    assert_eq!(walk(&mut g, &ask, &[(0.0, 45.0)], 0.0, 1.0), Some(45.0));
    assert_eq!(walk(&mut g, &ask, &[], 70.0, -1.0), Some(45.0));
    assert_eq!(walk(&mut g, &ask, &[], 60.0, -1.0), Some(45.0));
    let long = Ask { len: 300.0, ..ask };
    assert_eq!(walk(&mut g, &long, &[], 0.0, 1.0), None);
    assert_eq!(nearest(&mut g, &ask, 40.0), Some(40.0));
    assert_eq!(nearest(&mut g, &ask, 52.0), Some(45.0));
    assert_eq!(nearest(&mut g, &ask, 62.0), Some(70.0));
    assert_eq!(nearest(&mut g, &long, 36.0), None);
    let tight = Ask { len: 199.0, ..ask };
    let mut empty = Grid::new(200.0, 20.0);
    assert_eq!(nearest(&mut empty, &tight, 50.0), Some(1.0));
}

#[test]
fn a_centered_span_sits_in_the_middle_of_the_free_ground_holding_its_point() {
    let mut g = Grid::new(200.0, 20.0);
    g.file((20.0, 0.0, 30.0, 10.0), What::Zone(0));
    g.file((150.0, 0.0, 160.0, 10.0), What::Zone(0));
    let ask = Ask {
        strip: strip(),
        len: 40.0,
        rule: &rule_all,
        reach: 0.0,
        f: "t",
    };
    assert_eq!(centered(&mut g, &ask, 100.0), Some(70.0));
    assert_eq!(centered(&mut g, &ask, 25.0), None);
    let mut empty = Grid::new(200.0, 20.0);
    assert_eq!(centered(&mut empty, &ask, 10.0), Some(80.0));
    let wide = Ask { len: 400.0, ..ask };
    assert_eq!(centered(&mut empty, &wide, 10.0), None);
}

#[test]
fn a_strip_runs_either_way_and_its_intervals_merge() {
    let s = Strip {
        along_x: false,
        p0: 1.0,
        p1: 2.0,
        lo: 0.0,
        hi: 9.0,
    };
    assert_eq!(s.bx(3.0, 4.0, 0.5), (0.5, 3.0, 2.5, 4.0));
    assert_eq!(s.split((1.0, 2.0, 3.0, 4.0)), ((2.0, 4.0), (1.0, 3.0)));
    let mut l = vec![(0.0, 2.0), (5.0, 6.0)];
    insert(&mut l, (1.0, 5.5), "t");
    assert_eq!(l, vec![(0.0, 6.0)]);
}

#[test]
fn the_writer_writes_feet_as_pixels_and_escapes_its_text() {
    assert_eq!(
        (n(1.0), n(1.006), n(-0.001), n(2.5)),
        (
            "1".to_owned(),
            "1.01".to_owned(),
            "0".to_owned(),
            "2.5".to_owned()
        )
    );
    assert_eq!(px(1.0, 2.0), (24.0, 51.0));
    assert_eq!(esc("a<b>&"), "a&lt;b&gt;&amp;");
    assert_eq!(
        (paint("kura").0, paint("unknown")),
        ("#F2EFE4", ("#E8D2A8", "#6B4F2A"))
    );
    let mut s = Svg::default();
    let id = s.id();
    s.caption("x", "k", "", &[id]);
    s.line((0.0, 0.0), (1.0, 1.0), "");
    let text = s.finish();
    assert!(text.contains(r#"data-names="d0">x</text>"#), "{text}");
    assert!(text.ends_with("</svg>\n"), "{text}");
}

/// A corridor in pieces is one passage: its pieces' union traced as one ring, straight runs merged; apart, a ring each.
#[test]
fn a_union_of_boxes_is_traced_as_its_rings() {
    let corridor = [
        (0.0, 26.0, 36.0, 32.0),
        (36.0, 26.0, 65.0, 32.0),
        (62.0, 29.0, 90.0, 35.0),
    ];
    let rings = super::emit::union_rings(&corridor);
    assert_eq!(rings.len(), 1);
    let mut got = rings[0].clone();
    got.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.total_cmp(&b.1)));
    let want = [
        (0.0, 26.0),
        (0.0, 32.0),
        (62.0, 32.0),
        (62.0, 35.0),
        (65.0, 26.0),
        (65.0, 29.0),
        (90.0, 29.0),
        (90.0, 35.0),
    ];
    assert_eq!(got, want);
    assert_eq!(
        super::emit::union_rings(&[(0.0, 0.0, 1.0, 1.0), (2.0, 0.0, 3.0, 1.0)]).len(),
        2
    );
    assert!(super::emit::union_rings(&[]).is_empty());
}

/// The hearing court's floor is a knob each plan takes (0099's drawing page): white gravel or river cobbles, drawn as the program says;
/// a hearing court whose program names no floor is refused.
#[test]
fn the_hearing_courts_floor_is_the_programs() {
    let court = |floor: &str| {
        small(&format!(
            r#", "zones": [{{"kind": "hearing court", "x": 20, "y": 60, "w": 40, "h": 15{floor}}}]"#
        ))
    };
    for (floor, fill) in [
        ("white gravel", "url(#oshirasu-sand)"),
        ("river cobbles", "url(#court-cobbles)"),
    ] {
        let p = read(&court(&format!(r#", "floor": "{floor}""#))).unwrap();
        let l = super::layout::Layout::new(&p);
        let text = super::sheet(&p, &l, &super::parts::Seated::default());
        let drawn = format!(r##"fill="{fill}" stroke="#5A3F1E""##);
        assert!(text.contains(&drawn));
    }
    assert!(read(&court(r#", "floor": "marble""#))
        .unwrap_err()
        .message
        .contains("white gravel or river cobbles"));
    assert!(read(&court(""))
        .unwrap_err()
        .message
        .contains("white gravel or river cobbles"));
}

/// A gate's posts stand past the wall's ink, so they read as posts (0092's drawing page draws them 2 ft square at the opening): a post
/// drawn within the wall's 3 ft stroke, in the wall's own color, could not be seen.
#[test]
fn a_gates_posts_stand_past_the_walls_ink() {
    let p = read(&small("")).unwrap();
    let text = super::sheet(
        &p,
        &super::layout::Layout::new(&p),
        &super::parts::Seated::default(),
    );
    let at = text.find(r#"data-kind="main gate">"#).unwrap();
    let post = &text[at..text[at..].find("</g>").unwrap() + at];
    let h: f64 = post
        .split(r#"height=""#)
        .nth(1)
        .unwrap()
        .split('"')
        .next()
        .unwrap()
        .parse()
        .unwrap();
    assert!(h > 9.0, "{post}");
}

/// The small glyphs are drawn after the walls (0090's drawing page: small glyphs drawn last), so a privy's collection hatch through the
/// wall is seen over the wall's ink.
#[test]
fn the_small_glyphs_are_drawn_over_the_walls() {
    let p = read(&small("")).unwrap();
    let hatch = (40.0, -1.5, 42.0, 1.5);
    let s = super::parts::Seated {
        privies: vec![super::parts::Privy {
            bx: (38.5, 3.0, 43.5, 8.0),
            house: false,
            hatch: Some(hatch),
        }],
        ..super::parts::Seated::default()
    };
    let text = super::sheet(&p, &super::layout::Layout::new(&p), &s);
    let wall = text.find(r#"data-kind="compound wall""#).unwrap();
    let latrine = text.find(r#"data-kind="latrine""#).unwrap();
    assert!(latrine > wall);
}
