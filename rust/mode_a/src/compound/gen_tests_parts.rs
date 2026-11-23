//! The compound generator's parts tests (feature 449 T152): each part's rule and each refusal on a small program - the bath, the wells and
//! their rolls, the tubs, the privies, the board, the shrine's tree, the practice ground's gear, the roji, the garden's sun, the size
//! sweep, the knobs and the command (the open ground's void and cart route are `gen_tests_ground.rs`'s).
//!
//! Research: the generator's parts tests - NONE: fixtures and assertions, deciding nothing about a building

use l7r_gate_registry::about::FeatureClass;
use serde_json::Value;

use super::fixtures::{board, garden_sun, practice, privies, roji, tree as shrine_tree};
use super::gen_tests_seat::{b, err, prog, seated, with};
use super::grid::{Ent, What};
use super::layout::{building_rule, Layout};
use super::parts::{bath, tubs, wells, Seated};
use super::spec::Program;
use crate::raster::Host;

fn laid(p: &Program) -> Layout {
    let mut l = seated(p).unwrap();
    l.seat_doors(p).unwrap();
    l
}

fn kitchen(more: &str) -> String {
    b(
        "kitchen",
        "kitchen",
        "service",
        (24.0, 16.0),
        "inner",
        "N",
        more,
    )
}

#[test]
fn the_bath_stands_on_the_kitchens_service_side_or_is_refused() {
    let p = prog("");
    let (mut l, mut s) = (laid(&p), Seated::default());
    bath(&p, &mut l, &mut s).unwrap();
    assert!(s.bath.is_none());
    let p = with(&[], r#", "parts": {"bath": {"w": 10, "h": 8}}"#);
    assert!(err(bath(&p, &mut laid(&p), &mut s)).contains("a bath with no kitchen"));
    let p = with(
        &[b(
            "kitchen",
            "kitchen",
            "service",
            (10.0, 8.0),
            "inner",
            "N",
            "",
        )],
        r#", "parts": {"bath": {"w": 10, "h": 8}}"#,
    );
    assert!(err(bath(&p, &mut laid(&p), &mut s)).contains("no room for the bath"));
    let p = with(
        &[kitchen(r#", "doors": [{"face": "E", "at": 0.5}]"#)],
        r#", "parts": {"bath": {"w": 10, "h": 8}}"#,
    );
    bath(&p, &mut laid(&p), &mut s).unwrap();
    assert_eq!(s.bath, Some((3.0, 19.0, 13.0, 27.0)));
}

#[test]
fn each_well_by_its_use_and_its_gear_rolled() {
    let garden = r#"{"kind": "garden", "x": 40, "y": 20, "w": 40, "h": 20}"#;
    for (land, water) in [("valley floor", "shallow"), ("upland", "deep")] {
        let p = with(
            &[],
            &format!(
                r#", "zones": [{garden}], "parts": {{"wells": ["garden"], "landform": "{land}"}}"#
            ),
        );
        let (mut l, mut s) = (laid(&p), Seated::default());
        wells(&p, &mut l, &mut s).unwrap();
        assert_eq!(s.rolls[0], ("water depth".to_owned(), water.to_owned()));
        // the well's ground at the garden's far end, along its north edge: the curb centered in it
        let w = s.wells[0].bx;
        let mid = (f64::midpoint(w.0, w.2), f64::midpoint(w.1, w.3));
        assert!((mid.0 - 74.0).abs() < 1e-9 && (mid.1 - 26.0).abs() < 1e-9);
    }
    let p = prog("");
    let mut s = Seated::default();
    wells(&p, &mut laid(&p), &mut s).unwrap();
    assert!(s.wells.is_empty() && s.rolls.is_empty());
    for (use_, said) in [
        ("kitchen", "no kitchen"),
        ("garden", "no garden"),
        ("stables", "no stables"),
    ] {
        let p = with(&[], &format!(r#", "parts": {{"wells": ["{use_}"]}}"#));
        assert!(err(wells(&p, &mut laid(&p), &mut Seated::default())).contains(said));
    }
    let closed = r#", "zones": [{"kind": "practice ground", "x": 0, "y": 19, "w": 100, "h": 30}]"#;
    let p = with(
        &[kitchen(r#", "doors": [{"face": "E", "at": 0.5}]"#)],
        &format!(r#"{closed}, "parts": {{"wells": ["kitchen"]}}"#),
    );
    assert!(err(wells(&p, &mut laid(&p), &mut Seated::default()))
        .contains("no room for the kitchen's well"));
    let p = with(
        &[b(
            "kitchen",
            "kitchen",
            "service",
            (24.0, 8.0),
            "inner",
            "N",
            r#", "doors": [{"face": "E", "at": 0.5}]"#,
        )],
        r#", "parts": {"bath": {"w": 10, "h": 25}, "wells": ["kitchen"]}"#,
    );
    let (mut l, mut s) = (laid(&p), Seated::default());
    bath(&p, &mut l, &mut s).unwrap();
    assert!(err(wells(&p, &mut l, &mut s)).contains("past 20 ft"));
    let p = with(
        &[],
        r#", "zones": [{"kind": "garden", "x": 40, "y": 20, "w": 5, "h": 5}], "parts": {"wells": ["garden"]}"#,
    );
    assert!(err(wells(&p, &mut laid(&p), &mut Seated::default()))
        .contains("no room for the garden's well"));
    let stables = b(
        "stables",
        "stables",
        "service",
        (18.0, 24.0),
        "outer",
        "S",
        "",
    );
    let p = with(
        &[stables],
        r#", "zones": [{"kind": "practice ground", "x": 0, "y": 52, "w": 100, "h": 20.5}], "parts": {"wells": ["stables"]}"#,
    );
    assert!(err(wells(&p, &mut laid(&p), &mut Seated::default()))
        .contains("no room for the stables' well"));
}

#[test]
fn a_tub_stands_beside_a_door_or_round_the_nearer_corner() {
    let closed = r#", "zones": [{"kind": "practice ground", "x": 0, "y": 13, "w": 100, "h": 30}]"#;
    for (kind, at) in [("office hall", 0.5), ("k", 0.5), ("k", 0.9)] {
        let p = with(
            &[b(
                "hall",
                kind,
                "lord",
                (30.0, 10.0),
                "inner",
                "N",
                &format!(r#", "doors": [{{"face": "S", "at": {at}}}]"#),
            )],
            closed,
        );
        let (mut l, mut s) = (laid(&p), Seated::default());
        let r = tubs(&p, &mut l, &mut s);
        if kind == "k" {
            // at the face's middle no seat and the corner out of reach: reported; near its end, round the corner
            let owed = if at > 0.5 { (0, 1) } else { (1, 0) };
            assert_eq!((s.notes.len(), s.tubs.len()), owed);
        } else {
            assert!(err(r).contains("no seat for the hall's fire-water tub"));
        }
    }
    // an 8 ft face: no seat beside its door, so the tub stands round the corner within reach
    let p = with(
        &[b(
            "shed",
            "k",
            "plain",
            (8.0, 8.0),
            "inner",
            "W",
            r#", "doors": [{"face": "E", "at": 0.9}]"#,
        )],
        "",
    );
    let (mut l, mut s) = (laid(&p), Seated::default());
    tubs(&p, &mut l, &mut s).unwrap();
    assert_eq!(s.tubs.len(), 1);
    assert!(s.tubs[0].1 > 11.0, "{:?}", s.tubs);
    // the kura none, the kitchen two
    let p = with(
        &[
            b("k", "kitchen", "service", (24.0, 18.0), "inner", "N", ""),
            b(
                "store",
                "storehouse",
                "kura",
                (12.0, 10.0),
                "inner",
                "E",
                "",
            ),
        ],
        "",
    );
    let (mut l, mut s) = (laid(&p), Seated::default());
    tubs(&p, &mut l, &mut s).unwrap();
    assert_eq!(s.tubs.len(), 2);
}

#[test]
fn the_baths_tub_takes_its_yard_side_or_an_end() {
    let k = kitchen(r#", "doors": [{"face": "E", "at": 0.5}]"#);
    let p = with(&[k.clone()], r#", "parts": {"bath": {"w": 10, "h": 8}}"#);
    let (mut l, mut s) = (laid(&p), Seated::default());
    bath(&p, &mut l, &mut s).unwrap();
    tubs(&p, &mut l, &mut s).unwrap();
    assert_eq!(s.tubs.len(), 3);
    let closed = r#", "zones": [{"kind": "practice ground", "x": 13.1, "y": 19, "w": 80, "h": 30}, {"kind": "practice ground", "x": 0, "y": 27.1, "w": 13, "h": 30}]"#;
    let p = with(
        &[k],
        &format!(r#"{closed}, "parts": {{"bath": {{"w": 10, "h": 8}}}}"#),
    );
    let (mut l, mut s) = (laid(&p), Seated::default());
    bath(&p, &mut l, &mut s).unwrap();
    tubs(&p, &mut l, &mut s).unwrap();
    assert!(s
        .notes
        .iter()
        .any(|n| n.starts_with("the bath takes no tub")));
}

fn house(wall: &str, rooms: &str) -> String {
    b(
        "house",
        "residence",
        "lord",
        (40.0, 20.0),
        "inner",
        wall,
        &format!(r#", "inset": 6{rooms}"#),
    )
}

#[test]
fn the_house_keeps_two_privies_and_each_outer_one_stands_against_its_wall() {
    let rooms = r#", "rooms": [{"kind": "family quarters", "x": 30, "y": 0, "w": 10, "h": 10}, {"kind": "reception room", "x": 0, "y": 0, "w": 10, "h": 20}]"#;
    let p = with(&[house("N", rooms)], "");
    let (mut l, mut s) = (laid(&p), Seated::default());
    privies(&p, &mut l, &mut s).unwrap();
    assert_eq!(
        (s.privies[0].bx, s.privies[1].bx),
        ((5.5, 4.0, 10.5, 9.0), (38.0, 4.0, 43.0, 9.0))
    );
    let p = with(
        &[b(
            "house",
            "residence",
            "lord",
            (20.0, 40.0),
            "inner",
            "W",
            r#", "inset": 6, "rooms": [{"kind": "reception room", "x": 0, "y": 0, "w": 20, "h": 10}]"#,
        )],
        "",
    );
    let (mut l, mut s) = (laid(&p), Seated::default());
    privies(&p, &mut l, &mut s).unwrap();
    assert_eq!(s.privies.len(), 2);
    let p = with(
        &[b(
            "house",
            "residence",
            "lord",
            (40.0, 20.0),
            "inner",
            "N",
            "",
        )],
        "",
    );
    assert!(err(privies(&p, &mut laid(&p), &mut Seated::default()))
        .contains("no room for the house's privy"));
    for (wall, court) in [
        ("N", "inner"),
        ("W", "outer"),
        ("E", "outer"),
        ("S", "outer"),
    ] {
        let p = with(
            &[b("row", "k", "plain", (10.0, 10.0), court, wall, "")],
            r#", "parts": {"privies": ["row"]}"#,
        );
        let (mut l, mut s) = (laid(&p), Seated::default());
        privies(&p, &mut l, &mut s).unwrap();
        assert!(s.privies[0].hatch.is_some(), "{wall}");
    }
    let p = with(&[], r#", "parts": {"privies": ["nobody"]}"#);
    assert!(err(privies(&p, &mut laid(&p), &mut Seated::default())).contains("which is not seated"));
    let p = with(
        &[b(
            "hall",
            "k",
            "plain",
            (10.0, 10.0),
            "outer",
            "divider",
            "",
        )],
        r#", "parts": {"privies": ["hall"]}"#,
    );
    assert!(err(privies(&p, &mut laid(&p), &mut Seated::default())).contains("not the divider"));
    let full = r#", "zones": [{"kind": "practice ground", "x": 0, "y": 0, "w": 100, "h": 48}], "parts": {"privies": ["row"]}"#;
    let p = with(
        &[b("row", "k", "plain", (94.0, 5.0), "inner", "N", "")],
        full,
    );
    let mut l = Layout::new(&p);
    l.seats[0] = Some((3.0, 3.0, 97.0, 8.0));
    assert!(err(privies(&p, &mut l, &mut Seated::default()))
        .contains("no room for the privy by the row"));
}

#[test]
fn the_board_stands_outside_the_main_gate_beside_its_passage() {
    let p = prog("");
    let (mut l, mut s) = (laid(&p), Seated::default());
    board(&p, &mut l, &mut s);
    assert!(s.board.is_none());
    let p = with(&[], r#", "parts": {"board": true}"#);
    board(&p, &mut l, &mut s);
    assert_eq!(s.board, Some((37.0, 103.0, 43.0, 103.0 + 5.0 / 3.0)));
}

#[test]
fn the_shrines_tree_takes_the_first_face_with_room() {
    let shrine = |wall: &str, more: &str| {
        b(
            "shrine",
            "compound shrine",
            "shrine",
            (18.0, 14.0),
            "inner",
            wall,
            more,
        )
    };
    let p = prog("");
    let mut s = Seated::default();
    shrine_tree(&p, &mut laid(&p), &mut s).unwrap();
    assert!(s.tree.is_none());
    for (wall, more) in [
        ("N", ""),
        ("N", r#", "near": 79"#),
        ("E", ""),
        ("W", r#", "order": 1"#),
    ] {
        let p = with(&[shrine(wall, more)], "");
        let (mut l, mut s) = (laid(&p), Seated::default());
        shrine_tree(&p, &mut l, &mut s).unwrap();
        assert!(s.tree.is_some(), "{wall}{more}");
    }
    let p = with(&[shrine("W", r#", "near": 30"#)], "");
    let (mut l, mut s) = (laid(&p), Seated::default());
    shrine_tree(&p, &mut l, &mut s).unwrap();
    let closed = r#", "zones": [{"kind": "practice ground", "x": 22, "y": 0, "w": 78, "h": 50}, {"kind": "practice ground", "x": 0, "y": 18, "w": 22, "h": 32}]"#;
    let p = with(&[shrine("W", r#", "near": 3"#)], closed);
    assert!(err(shrine_tree(&p, &mut laid(&p), &mut s)).contains("no face of the compound shrine"));
}

#[test]
fn the_practice_grounds_rack_faces_the_watch_and_its_posts_stand_inside() {
    let p = prog("");
    let mut s = Seated::default();
    practice(&p, &mut laid(&p), &mut s).unwrap();
    let ground = r#"{"kind": "practice ground", "x": 30, "y": 65, "w": 40, "h": 20}"#;
    for (wall, court, face) in [
        ("E", "outer", 'E'),
        ("W", "outer", 'W'),
        ("divider", "outer", 'N'),
        ("S", "outer", 'S'),
    ] {
        let more = if face == 'S' { r#", "near": 50"# } else { "" };
        let p = with(
            &[b(
                "watch",
                "barracks",
                "service",
                (10.0, 10.0),
                court,
                wall,
                more,
            )],
            &format!(r#", "zones": [{ground}], "parts": {{"rack_by": "watch", "posts": 2}}"#),
        );
        let (mut l, mut s) = (laid(&p), Seated::default());
        practice(&p, &mut l, &mut s).unwrap();
        let r = s.rack.unwrap();
        let (edge, want) = match face {
            'E' => (r.2, 70.0),
            'W' => (r.0, 30.0),
            'N' => (r.1, 65.0),
            _ => (r.3, 85.0),
        };
        let at = (edge - want).abs() < 1e-9;
        assert!(at && s.posts.len() == 2, "{face} {r:?}");
    }
    let p = with(
        &[],
        &format!(r#", "zones": [{ground}], "parts": {{"rack_by": "nobody"}}"#),
    );
    assert!(
        err(practice(&p, &mut laid(&p), &mut Seated::default())).contains("which is not seated")
    );
    let tiny = r#"{"kind": "practice ground", "x": 40, "y": 60, "w": 5, "h": 5}"#;
    let p = with(
        &[b(
            "watch",
            "barracks",
            "service",
            (10.0, 10.0),
            "outer",
            "E",
            "",
        )],
        &format!(r#", "zones": [{tiny}], "parts": {{"rack_by": "watch"}}"#),
    );
    assert!(err(practice(&p, &mut laid(&p), &mut Seated::default()))
        .contains("no room for the weapon rack"));
}

#[test]
fn the_roji_runs_from_the_middle_gate_to_the_shoe_stone_clear_or_is_refused() {
    let hall = b(
        "hall",
        "office hall",
        "lord",
        (30.0, 10.0),
        "outer",
        "divider",
        "",
    );
    let reception = r#", "rooms": [{"kind": "reception room", "x": 30, "y": 0, "w": 10, "h": 20}]"#;
    let p = with(
        &[house("N", reception), hall.clone()],
        r#", "parts": {"roji": true}"#,
    );
    let (mut l, mut s) = (laid(&p), Seated::default());
    roji(&p, &mut l, &mut s).unwrap();
    assert_eq!(
        (s.roji.len(), s.shoe),
        (11, Some((36.0, 29.0, 40.0, 29.0 + 5.0 / 3.0)))
    );
    let p = with(&[house("N", "")], r#", "parts": {"roji": true}"#);
    assert!(err(roji(&p, &mut laid(&p), &mut Seated::default())).contains("no middle gate"));
    let p = with(&[hall.clone()], r#", "parts": {"roji": true}"#);
    assert!(err(roji(&p, &mut laid(&p), &mut Seated::default())).contains("no house"));
    let p = with(
        &[
            house("N", ""),
            hall,
            b(
                "pavilion",
                "k",
                "plain",
                (10.0, 6.0),
                "inner",
                "divider",
                r#", "near": 30"#,
            ),
        ],
        r#", "zones": [{"kind": "vegetable garden", "x": 40, "y": 40, "w": 5, "h": 5}], "parts": {"roji": true}"#,
    );
    assert!(
        err(roji(&p, &mut laid(&p), &mut Seated::default())).contains("stands on the roji's line")
    );
    let p = prog("");
    roji(&p, &mut laid(&p), &mut Seated::default()).unwrap();
}

#[test]
fn a_kitchen_garden_wants_its_sun() {
    let bed = r#", "zones": [{"kind": "vegetable garden", "x": 40, "y": 5, "w": 20, "h": 10}]"#;
    // in the open, nothing standing south of it: six hours and more
    garden_sun(&prog(bed), &laid(&prog(bed)), &Seated::default()).unwrap();
    // a 20 x 10 ft building 22.5 ft south of the bed: its 20 ft ridge throws 21 ft at noon and its longer morning and afternoon shadows
    // fall aside, so the bed keeps more than half its ground lit for six hours - counted, not ruled by a strip (0109's six hours)
    let p = with(
        &[b(
            "shade",
            "k",
            "plain",
            (20.0, 10.0),
            "inner",
            "divider",
            r#", "near": 40"#,
        )],
        bed,
    );
    garden_sun(&p, &laid(&p), &Seated::default()).unwrap();
    // a bed against the divider's north face: the wall's 5 ft shadow takes it (0038's six-hour check casts a wall)
    let walled = r#", "zones": [{"kind": "vegetable garden", "x": 40, "y": 45, "w": 20, "h": 3}]"#;
    assert!(err(garden_sun(
        &prog(walled),
        &laid(&prog(walled)),
        &Seated::default()
    ))
    .contains("six hours"));
    let p = with(
        &[b(
            "shade",
            "k",
            "plain",
            (30.0, 20.0),
            "inner",
            "W",
            r#", "inset": 34"#,
        )],
        bed,
    );
    assert!(err(garden_sun(&p, &laid(&p), &Seated::default())).contains("six hours"));
}

#[test]
fn the_knobs_and_the_size_sweep_hold_or_refuse_the_program() {
    let p = with(
        &[],
        r#", "knobs": [{"key": "main gate form", "options": ["a", "b"], "value": "c"}]"#,
    );
    assert!(err(super::knobs(&p)).contains("the sheet's seed rolls"));
    let ranked = with(
        &[
            b("house", "residence", "lord", (10.0, 10.0), "inner", "N", ""),
            b(
                "kitchen",
                "kitchen",
                "service",
                (20.0, 10.0),
                "inner",
                "N",
                r#", "near": 50"#,
            ),
        ],
        "",
    );
    let rl = laid(&ranked);
    assert!(err(super::composition(&ranked, &rl, &Seated::default()))
        .contains("is not smaller than the residence"));
    let l = laid(&prog(""));
    let s = Seated {
        privies: vec![super::parts::Privy {
            bx: (10.0, 10.0, 15.0, 15.0),
            house: true,
            hatch: None,
        }],
        ..Seated::default()
    };
    assert!(err(super::composition(&prog(""), &l, &s)).contains("a court with no privy"));
    assert!(super::composition(&prog(""), &l, &Seated::default()).is_ok());
    let e = |what: What| {
        building_rule(&Ent {
            bx: (0.0, 0.0, 1.0, 1.0),
            what,
        })
    };
    assert_eq!(
        (e(What::Part("tub", None)), e(What::Wall), e(What::Held(0))),
        (None, None, Some((1.5, 0.0)))
    );
}

/// Every kind the small sheet draws, known to the registry handed in; and one that knows none of them.
#[expect(
    clippy::unnecessary_wraps,
    reason = "the registry reader's signature, which the command takes"
)]
fn known(_: &std::path::Path) -> Result<Vec<FeatureClass>, l7r_gate_research::Error> {
    let kinds = [
        "k",
        "inner court",
        "outer court",
        "kitchen",
        "door",
        "compound wall",
        "court divider",
        "main gate",
        "fire-water tubs",
    ];
    Ok(kinds
        .iter()
        .map(|k| FeatureClass {
            key: (*k).into(),
            name: (*k).into(),
            ..Default::default()
        })
        .collect())
}

#[expect(
    clippy::unnecessary_wraps,
    reason = "the registry reader's signature, which the command takes"
)]
fn none(_: &std::path::Path) -> Result<Vec<FeatureClass>, l7r_gate_research::Error> {
    Ok(Vec::new())
}

#[test]
fn the_command_draws_a_spec_whole_or_refuses_it() {
    let _log = crate::reads::taker();
    let tree = super::gen_tests_seat::tree();
    let dir = l7r_shared::tempdir::TempDir::new("compound-cli");
    let spec = dir.path().join("t.compound.json");
    let named = r#", "zones": [{"kind": "inner court", "x": 3, "y": 30, "w": 94, "h": 17}, {"kind": "outer court", "x": 3, "y": 53, "w": 94, "h": 30}]"#;
    let shed = b(
        "shed",
        "k",
        "plain",
        (8.0, 8.0),
        "inner",
        "E",
        r#", "doors": [{"face": "W", "at": 0.5}]"#,
    );
    let src = super::gen_tests::small(&format!(
        r#"{named}, "buildings": [{}, {shed}]"#,
        kitchen("")
    ));
    std::fs::write(&spec, &src).unwrap();
    let at = spec.to_string_lossy().into_owned();
    let skip = Host {
        vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
        ..Host::default()
    };
    let r = super::cli::run(std::slice::from_ref(&at), &tree, &skip, &known);
    assert_eq!(r.code, 0, "{}", r.stderr);
    let v: Value = serde_json::from_str(&r.stdout).unwrap();
    assert!(v["reads"]
        .as_array()
        .unwrap()
        .iter()
        .any(|p| p.as_str() == Some(at.as_str())));
    assert!(
        dir.path().join("t.svg").exists()
            && dir.path().join("t.html").exists()
            && !dir.path().join("t.png").exists()
    );
    let r = super::cli::run(std::slice::from_ref(&at), &tree, &Host::default(), &none);
    assert!(
        r.code == 1
            && r.stderr.contains(
                "t.compound.json: untagged ink [] ; unknown kinds"
                    .replace(" ;", ";")
                    .as_str()
            )
    );
    assert!(dir.path().join("t.png").exists());
    // `--out DIR` (feature 449 T221): the sheet and its page drawn there, the spec's folder left as it was
    let staged = dir.path().join("staged");
    std::fs::create_dir(&staged).unwrap();
    let to = staged.to_string_lossy().into_owned();
    let r = super::cli::run(
        &[to.clone(), "--out".into(), at.clone()][1..],
        &tree,
        &skip,
        &known,
    );
    assert_eq!(r.code, 2);
    let r = super::cli::run(&[at.clone(), "--out".into(), to], &tree, &skip, &known);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(staged.join("t.svg").is_file() && staged.join("t.html").is_file());
    let bad = dir.path().join("t.json").to_string_lossy().into_owned();
    let r = super::cli::run(&[bad], &tree, &skip, &known);
    assert!(r.code == 1 && r.stdout.contains("is named <map>.compound.json"));
    let gone = dir
        .path()
        .join("gone.compound.json")
        .to_string_lossy()
        .into_owned();
    let r = super::cli::run(&[gone], &tree, &skip, &known);
    assert!(r.code == 1 && r.stderr.starts_with("FileNotFoundError"));
    assert_eq!(super::cli::run(&[], &tree, &skip, &known).code, 2);
}

/// The rest of each rule's branches: a sheet with no parts written; the divider's first building beside a blocked middle; an ell toward
/// the middle from either side; a gate's approach and another door's step in the way; the bath's tub on a column kitchen; the rack's
/// ground without its rack; and a sheet the command cannot write.
#[test]
fn each_rules_other_branches_hold() {
    let p = prog("");
    let text = super::sheet(&p, &Layout::new(&p), &Seated::default());
    assert!(text.contains(r#"data-kind="court divider""#) && !text.contains("fire-water tubs"));
    let blocked = r#", "zones": [{"kind": "garden", "x": 45, "y": 52, "w": 10, "h": 5}]"#;
    let p = with(
        &[b("hall", "k", "plain", (20.0, 5.0), "outer", "divider", "")],
        blocked,
    );
    assert_eq!(seated(&p).unwrap().seats[0], Some((55.0, 52.5, 75.0, 57.5)));
    let p = with(
        &[
            b(
                "house",
                "k",
                "plain",
                (20.0, 10.0),
                "inner",
                "N",
                r#", "near": 70"#,
            ),
            b(
                "k",
                "k",
                "plain",
                (6.0, 6.0),
                "inner",
                "N",
                r#", "joins": "house""#,
            ),
            b(
                "tower",
                "k",
                "plain",
                (10.0, 20.0),
                "inner",
                "E",
                r#", "near": 25"#,
            ),
            b(
                "t",
                "k",
                "plain",
                (6.0, 6.0),
                "inner",
                "E",
                r#", "joins": "tower""#,
            ),
        ],
        "",
    );
    let l = seated(&p).unwrap();
    assert_eq!(
        (l.seats[1], l.seats[3]),
        (Some((64.0, 3.0, 70.0, 9.0)), Some((91.0, 19.0, 97.0, 25.0)))
    );
}

#[test]
fn a_gate_or_a_door_in_the_way_is_refused() {
    let gate = r#", "gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}, {"kind": "side gate", "wall": "W", "at": 46, "width": 6}]"#;
    let src = super::gen_tests::small(&format!(
        r#", "buildings": [{}]"#,
        b(
            "hall",
            "office hall",
            "lord",
            (60.0, 5.0),
            "outer",
            "divider",
            ""
        )
    ));
    let p = super::spec::read(&src.replacen(
        r#""gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}]"#,
        &gate[2..],
        1,
    ))
    .unwrap();
    // the west stretch beside the hall is the side gate's approach: the middle gate opens on the east
    assert_eq!(seated(&p).unwrap().middle, Some((83.5, 89.5)));
    let facing = with(
        &[
            b("a", "k", "plain", (20.0, 20.0), "inner", "N", ""),
            b(
                "b",
                "k",
                "plain",
                (20.0, 20.5),
                "inner",
                "divider",
                r#", "near": 3, "doors": [{"face": "N", "at": 0.5}]"#,
            ),
        ],
        "",
    );
    let mut l = seated(&facing).unwrap();
    assert!(err(l.seat_doors(&facing)).contains("the b's door"));
}

#[test]
fn the_column_kitchens_bath_and_a_bare_practice_ground() {
    let k = b(
        "k",
        "kitchen",
        "service",
        (16.0, 24.0),
        "inner",
        "W",
        r#", "doors": [{"face": "S", "at": 0.5}]"#,
    );
    let p = with(&[k], r#", "parts": {"bath": {"w": 8, "h": 10}}"#);
    let (mut l, mut s) = (laid(&p), Seated::default());
    bath(&p, &mut l, &mut s).unwrap();
    tubs(&p, &mut l, &mut s).unwrap();
    assert_eq!(s.tubs.len(), 3);
    let ground = r#", "zones": [{"kind": "practice ground", "x": 30, "y": 65, "w": 40, "h": 20}], "parts": {"posts": 1}"#;
    let p = with(&[], ground);
    let (mut l, mut s) = (laid(&p), Seated::default());
    practice(&p, &mut l, &mut s).unwrap();
    assert_eq!((s.rack, s.posts.len()), (None, 1));
}

#[test]
fn the_centered_search_reads_past_its_reach_and_a_sheet_unwritable_is_refused() {
    let mut g = super::grid::Grid::new(200.0, 20.0);
    g.file((150.0, 0.0, 160.0, 10.0), What::Zone(0));
    let rule = |_: &Ent| Some((0.0, 0.0));
    let strip = super::span::Strip {
        along_x: true,
        p0: 0.0,
        p1: 10.0,
        lo: 0.0,
        hi: 200.0,
    };
    let ask = super::span::Ask {
        strip,
        len: 40.0,
        rule: &rule,
        reach: 15.0,
        f: "t",
    };
    assert_eq!(super::span::centered(&mut g, &ask, 100.0), Some(55.0));
    let _log = crate::reads::taker();
    let dir = l7r_shared::tempdir::TempDir::new("compound-cli-write");
    let spec = dir.path().join("w.compound.json");
    let named = r#", "zones": [{"kind": "inner court", "x": 3, "y": 3, "w": 94, "h": 44}, {"kind": "outer court", "x": 3, "y": 53, "w": 94, "h": 30}]"#;
    std::fs::write(&spec, super::gen_tests::small(named)).unwrap();
    std::fs::create_dir(dir.path().join("w.svg")).unwrap();
    let skip = Host {
        vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
        ..Host::default()
    };
    let r = super::cli::run(
        &[spec.to_string_lossy().into_owned()],
        &super::gen_tests_seat::tree(),
        &skip,
        &known,
    );
    assert_eq!(r.code, 1);
}

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
