//! The compound generator's seating tests (feature 449 T152): each rule of the buildings' tiers, the ells, the middle gate, the doors, the
//! parts and the open ground on a small program, each refusal the generator owes, and the two pool sheets composed and held to every check
//! the audit runs on them.
//!
//! Research: the generator's seating tests - NONE: fixtures and assertions, deciding nothing about a building

use std::path::{Path, PathBuf};

use super::gen_tests::small;
use super::grid::What;
use super::layout::{
    band, court_face, door_at, door_specs, ell_box, gate_approach, seat_order, tier, Layout,
};
use super::spec::{read, Face, Program};
use crate::types::Band;

pub fn tree() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

pub fn prog(extra: &str) -> Program {
    read(&small(extra)).unwrap()
}

pub fn b(
    name: &str,
    kind: &str,
    role: &str,
    wh: (f64, f64),
    court: &str,
    wall: &str,
    more: &str,
) -> String {
    format!(
        r#"{{"name": "{name}", "kind": "{kind}", "role": "{role}", "w": {}, "h": {}, "court": "{court}", "wall": "{wall}"{more}}}"#,
        wh.0, wh.1
    )
}

pub fn with(buildings: &[String], more: &str) -> Program {
    prog(&format!(
        r#", "buildings": [{}]{more}"#,
        buildings.join(", ")
    ))
}

pub fn seated(p: &Program) -> Result<Layout, l7r_gate_research::Error> {
    let mut l = Layout::new(p);
    l.seat_all(p, &[])?;
    Ok(l)
}

pub fn err<T>(r: Result<T, l7r_gate_research::Error>) -> String {
    r.err().map(|e| e.message).unwrap_or_default()
}

#[test]
fn each_wall_gives_its_band_and_its_court_face() {
    let p = with(
        &[
            b(
                "n",
                "k",
                "plain",
                (10.0, 5.0),
                "inner",
                "N",
                r#", "inset": 2"#,
            ),
            b("s", "k", "plain", (10.0, 5.0), "outer", "S", ""),
            b("w", "k", "plain", (10.0, 5.0), "inner", "W", ""),
            b("e", "k", "plain", (10.0, 5.0), "outer", "E", ""),
            b("di", "k", "plain", (10.0, 5.0), "inner", "divider", ""),
            b("do", "k", "plain", (10.0, 5.0), "outer", "divider", ""),
        ],
        "",
    );
    let got: Vec<(f64, f64, bool, f64, f64, f64)> = p
        .buildings
        .iter()
        .map(|x| {
            let (s, len) = band(&p, x, x.inset);
            (s.p0, s.p1, s.along_x, s.lo, s.hi, len)
        })
        .collect();
    assert_eq!(got[0], (5.0, 10.0, true, 3.0, 97.0, 10.0));
    assert_eq!(got[1], (92.0, 97.0, true, 3.0, 97.0, 10.0));
    assert_eq!(got[2], (3.0, 13.0, false, 3.0, 47.5, 5.0));
    assert_eq!(got[3], (87.0, 97.0, false, 52.5, 97.0, 5.0));
    assert_eq!(got[4], (42.5, 47.5, true, 3.0, 97.0, 10.0));
    assert_eq!(got[5], (52.5, 57.5, true, 3.0, 97.0, 10.0));
    let faces: Vec<Face> = p.buildings.iter().map(court_face).collect();
    assert_eq!(
        faces,
        [Face::S, Face::N, Face::E, Face::W, Face::N, Face::S]
    );
}

/// The tiers: the north and south rows, then the east and west columns, then the divider; highest order, then largest first; an ell
/// straight after its host.
#[test]
fn the_tiers_seat_rows_then_columns_then_the_divider() {
    let p = with(
        &[
            b(
                "hall",
                "k",
                "plain",
                (10.0, 5.0),
                "outer",
                "divider",
                r#", "order": 9"#,
            ),
            b("col", "k", "plain", (10.0, 5.0), "inner", "W", ""),
            b(
                "small",
                "k",
                "plain",
                (10.0, 5.0),
                "inner",
                "N",
                r#", "order": 2"#,
            ),
            b(
                "big",
                "k",
                "plain",
                (20.0, 5.0),
                "inner",
                "N",
                r#", "order": 2"#,
            ),
            b(
                "ell",
                "k",
                "plain",
                (5.0, 5.0),
                "inner",
                "N",
                r#", "joins": "small""#,
            ),
            b(
                "first",
                "k",
                "plain",
                (5.0, 5.0),
                "outer",
                "S",
                r#", "order": 5"#,
            ),
        ],
        "",
    );
    assert_eq!(seat_order(&p), [5, 3, 2, 4, 1, 0]);
    assert_eq!(tier(&p.buildings[0]), (2, 1));
    let l = seated(&p).unwrap();
    assert_eq!(l.seats[3], Some((3.0, 3.0, 23.0, 8.0)));
    assert_eq!(l.seats[2], Some((29.0, 3.0, 39.0, 8.0)));
    // the ell at the end of its host toward the wall's middle
    assert_eq!(l.seats[4], Some((39.0, 3.0, 44.0, 8.0)));
    // the column flows below the north row
    assert_eq!(l.seats[1], Some((3.0, 14.0, 13.0, 19.0)));
    // the divider's first building centered in the free ground holding the middle
    assert_eq!(l.seats[0], Some((45.0, 52.5, 55.0, 57.5)));
    assert!(l.middle.is_none());
}

#[test]
fn a_building_with_no_room_is_reported_never_squeezed() {
    let p = with(
        &[b("long", "k", "plain", (95.0, 5.0), "inner", "N", "")],
        "",
    );
    assert!(err(seated(&p)).contains("no room on its wall for the long"));
    let p = with(
        &[b(
            "deep",
            "k",
            "plain",
            (5.0, 5.0),
            "inner",
            "divider",
            r#", "inset": 60"#,
        )],
        "",
    );
    assert!(err(seated(&p)).contains("outside its court"));
    let bands = [(
        "k".to_owned(),
        Band {
            w: Some((1.0, 2.0)),
            h: Some((1.0, 2.0)),
            area: None,
        },
    )];
    let p = with(&[b("a", "k", "plain", (5.0, 5.0), "inner", "N", "")], "");
    let mut l = Layout::new(&p);
    assert!(err(l.seat_all(&p, &bands)).contains("outside the k band"));
    let presence = [(
        "k".to_owned(),
        Band {
            w: None,
            h: None,
            area: None,
        },
    )];
    assert!(Layout::new(&p).seat_all(&p, &presence).is_ok());
}

/// The second rank holds stores alone, behind the wall's rank-1 row.
#[test]
fn the_second_rank_holds_stores_behind_the_row() {
    let p = with(
        &[
            b("row", "k", "plain", (40.0, 10.0), "inner", "N", ""),
            b(
                "store",
                "storehouse",
                "kura",
                (10.0, 5.0),
                "inner",
                "N",
                r#", "rank": 2"#,
            ),
        ],
        "",
    );
    let l = seated(&p).unwrap();
    assert_eq!(l.seats[1], Some((3.0, 19.0, 13.0, 24.0)));
    let p = with(
        &[b(
            "servants",
            "k",
            "service",
            (10.0, 5.0),
            "inner",
            "N",
            r#", "rank": 2"#,
        )],
        "",
    );
    assert!(err(seated(&p)).contains("holds stores only"));
}

#[test]
fn an_ell_takes_a_free_end_of_its_host_or_is_refused() {
    let host = |wall: &str, court: &str| b("house", "k", "plain", (20.0, 10.0), court, wall, "");
    let p = with(
        &[
            host("N", "inner"),
            b(
                "k",
                "k",
                "plain",
                (8.0, 6.0),
                "inner",
                "N",
                r#", "joins": "house", "end": "W""#,
            ),
        ],
        "",
    );
    // the west end is the corner: refused there, it takes the east end
    assert_eq!(seated(&p).unwrap().seats[1], Some((23.0, 3.0, 31.0, 9.0)));
    let p = with(
        &[
            b(
                "house",
                "k",
                "plain",
                (20.0, 10.0),
                "inner",
                "W",
                r#", "order": 1"#,
            ),
            b(
                "k",
                "k",
                "plain",
                (6.0, 8.0),
                "inner",
                "W",
                r#", "joins": "house""#,
            ),
        ],
        "",
    );
    assert_eq!(seated(&p).unwrap().seats[1], Some((3.0, 13.0, 9.0, 21.0)));
    let p = with(
        &[
            b("house", "k", "plain", (90.0, 10.0), "inner", "N", ""),
            b(
                "k",
                "k",
                "plain",
                (8.0, 6.0),
                "inner",
                "N",
                r#", "joins": "house""#,
            ),
        ],
        "",
    );
    assert!(err(seated(&p)).contains("no free end of the house"));
    let p = with(
        &[b(
            "k",
            "k",
            "plain",
            (8.0, 6.0),
            "inner",
            "N",
            r#", "joins": "nobody""#,
        )],
        "",
    );
    assert!(seat_order(&p).is_empty());
    let mut l = Layout::new(&p);
    assert!(err(l.seat_all(&p, &[])).is_empty());
    let hb = (10.0, 10.0, 20.0, 20.0);
    for (back, end, want) in [
        (Face::N, Face::W, (8.0, 10.0, 10.0, 13.0)),
        (Face::N, Face::E, (20.0, 10.0, 22.0, 13.0)),
        (Face::S, Face::W, (8.0, 17.0, 10.0, 20.0)),
        (Face::S, Face::E, (20.0, 17.0, 22.0, 20.0)),
        (Face::W, Face::N, (10.0, 7.0, 12.0, 10.0)),
        (Face::W, Face::S, (10.0, 20.0, 12.0, 23.0)),
        (Face::E, Face::N, (18.0, 7.0, 20.0, 10.0)),
        (Face::E, Face::S, (18.0, 20.0, 20.0, 23.0)),
    ] {
        assert_eq!(ell_box(hb, back, end, 2.0, 3.0), want, "{back:?} {end:?}");
    }
}

/// The gatehouse by the main gate; a building's own start along its wall; the middle gate beside the office hall.
#[test]
fn a_building_may_start_beside_the_gate_or_at_its_own_point() {
    let p = with(
        &[
            b(
                "gatehouse",
                "gatehouse",
                "dark",
                (20.0, 6.0),
                "outer",
                "S",
                r#", "beside": "main gate""#,
            ),
            b(
                "house",
                "k",
                "plain",
                (10.0, 6.0),
                "inner",
                "N",
                r#", "near": 60"#,
            ),
            b(
                "hall",
                "office hall",
                "lord",
                (40.0, 10.0),
                "outer",
                "divider",
                "",
            ),
        ],
        "",
    );
    let l = seated(&p).unwrap();
    // the fixture's sheet "t" rolls its gatehouse behind the gate (449 T398): past the gate's east post, set back past its approach
    assert_eq!(l.seats[0], Some((55.0, 79.0, 75.0, 85.0)));
    assert_eq!(l.seats[1], Some((60.0, 3.0, 70.0, 9.0)));
    assert_eq!(l.middle, Some((73.5, 79.5)));
    let p = with(
        &[
            b("w", "k", "plain", (45.0, 44.5), "inner", "W", ""),
            b("e", "k", "plain", (45.0, 44.5), "inner", "E", ""),
            b(
                "hall",
                "office hall",
                "lord",
                (10.0, 10.0),
                "outer",
                "divider",
                "",
            ),
        ],
        "",
    );
    assert!(err(seated(&p)).contains("no stretch of the divider"));
}

#[test]
fn every_door_opens_on_its_face_and_a_blocked_one_is_refused() {
    let p = with(
        &[
            b(
                "row",
                "barracks",
                "service",
                (40.0, 10.0),
                "outer",
                "S",
                r#", "bays": [10, 25]"#,
            ),
            b("plain", "k", "plain", (10.0, 10.0), "inner", "W", ""),
            b(
                "own",
                "k",
                "plain",
                (10.0, 10.0),
                "inner",
                "E",
                r#", "doors": [{"face": "N", "at": 0}]"#,
            ),
        ],
        "",
    );
    let mut l = seated(&p).unwrap();
    l.seat_doors(&p).unwrap();
    let faces: Vec<(usize, Face)> = l.doors.iter().map(|d| (d.b, d.face)).collect();
    assert_eq!(
        faces,
        [
            (0, Face::N),
            (0, Face::N),
            (0, Face::N),
            (1, Face::E),
            (2, Face::N)
        ]
    );
    let mids: Vec<f64> = l.doors.iter().take(3).map(|d| d.mid().0).collect();
    assert_eq!(mids, [8.0, 20.5, 35.5]);
    assert!((door_specs(&p.buildings[1])[0].at - 0.5).abs() < 1e-12);
    let blocked = with(
        &[
            b("a", "k", "plain", (20.0, 20.0), "inner", "N", ""),
            b(
                "b",
                "k",
                "plain",
                (20.0, 23.0),
                "inner",
                "divider",
                r#", "near": 3"#,
            ),
        ],
        "",
    );
    let mut l = seated(&blocked).unwrap();
    assert!(err(l.seat_doors(&blocked)).contains("the a's door on its S face"));
    let bx = (0.0, 0.0, 12.0, 12.0);
    for (f, block, step) in [
        (Face::N, (3.0, 0.0, 9.0, 4.0 / 3.0), (3.0, -3.0, 9.0, 0.0)),
        (
            Face::S,
            (3.0, 12.0 - 4.0 / 3.0, 9.0, 12.0),
            (3.0, 12.0, 9.0, 15.0),
        ),
        (Face::W, (0.0, 3.0, 4.0 / 3.0, 9.0), (-3.0, 3.0, 0.0, 9.0)),
        (
            Face::E,
            (12.0 - 4.0 / 3.0, 3.0, 12.0, 9.0),
            (12.0, 3.0, 15.0, 9.0),
        ),
    ] {
        let d = door_at(0, bx, f, 0.5);
        assert_eq!((d.bx, d.step), (block, step), "{f:?}");
    }
}

#[test]
fn a_gate_holds_its_passage_and_approach_on_any_wall() {
    let p = prog("");
    assert_eq!(
        gate_approach(&p, Face::S, 50.0, 6.0),
        (45.0, 86.5, 55.0, 101.5)
    );
    assert_eq!(
        gate_approach(&p, Face::N, 50.0, 6.0),
        (45.0, -1.5, 55.0, 13.5)
    );
    assert_eq!(
        gate_approach(&p, Face::W, 50.0, 6.0),
        (-1.5, 45.0, 13.5, 55.0)
    );
    assert_eq!(
        gate_approach(&p, Face::E, 50.0, 6.0),
        (86.5, 45.0, 101.5, 55.0)
    );
    let l = Layout::new(&p);
    assert!(matches!(l.grid.ents[0].what, What::Gate));
}

/// The pool's two generated sheets compose from their specs, each building in its declared court with the water and privies the program
/// owes. Their checks are the pool sweep's (`crate::pool_sweep`, feature 449 T211): this test's report ran on a copy outside the pool,
/// which the report read as a sheet of no tier, so it held them to the shared layer alone.
#[test]
fn the_pool_sheets_compose_in_their_courts() {
    let tree = tree();
    for name in ["ochiba-roundtrip-test", "county-magistracy-example"] {
        let spec = tree.join(format!("pool/magistracies/{name}/{name}.compound.json"));
        let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
        let (l, s) = super::generate(&p, &bands).unwrap();
        // office front, residence rear: each building in its declared court
        for (i, x) in p.buildings.iter().enumerate() {
            let at = l.seats[i].unwrap();
            let (inner, owed) = (at.3 <= p.divider, x.court == super::spec::Court::Inner);
            assert_eq!(inner, owed, "{}", x.name);
        }
        let owed = (
            l.middle.is_some(),
            s.tubs.len() >= 12,
            s.privies.len(),
            s.wells.len(),
        );
        assert_eq!(owed, (true, true, 5, 3), "{name}");
    }
}

/// The official study stands at the household's end of the office hall (449 T392): the Edo North and South Town Magistracies' plans of
/// 1841 and 1842 put the magistrate's own working room, the yobeya, at the join of office and residence, the inner entrance one corridor
/// away or adjoining (research pass t381-study-seat, on research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.html),
/// so on each generated pool sheet no room of the hall stands between the study and the hall's end nearest the middle gate save the
/// armory (its end bay rolled, 0123) or the genkan, and the magistrate's way from the house to the study runs through no working room.
#[test]
fn the_official_study_stands_at_the_households_end_of_the_office_hall() {
    let tree = tree();
    for name in ["ochiba-roundtrip-test", "county-magistracy-example"] {
        let spec = tree.join(format!("pool/magistracies/{name}/{name}.compound.json"));
        let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
        let (l, _) = super::generate(&p, &bands).unwrap();
        let i = p
            .buildings
            .iter()
            .position(|b| b.kind == "office hall")
            .unwrap();
        let (hall, (g0, g1)) = (l.seats[i].unwrap(), l.middle.unwrap());
        let toward = (f64::midpoint(g0, g1) - f64::midpoint(hall.0, hall.2)).signum();
        let rooms = &p.buildings[i].rooms;
        let study = rooms
            .iter()
            .find(|r| r.kind == "official study")
            .unwrap()
            .bx;
        let between: Vec<&str> = rooms
            .iter()
            .filter(|r| r.style == "room")
            .filter(|r| {
                (f64::midpoint(r.bx.0, r.bx.2) - f64::midpoint(study.0, study.2)) * toward > 0.0
            })
            .map(|r| r.kind.as_str())
            .filter(|k| !["armory", "genkan"].contains(k))
            .collect();
        assert_eq!(between, Vec::<&str>::new(), "{name}");
    }
}

/// The county example keeps an armory at an ordinary seat and its granary on the offices' side (449 T265, 417 T33; T274): Kaibara's
/// ordinary gate range held a gun store (0093) and Pingyao, with no standing barracks, kept its armory in the great hall's west end bay
/// (0123), so the quiet county's office hall holds an armory; Pingyao built "north of them the county granary" (0123) on the office
/// side, behind the war, justice and works offices, not in the residence's court (building-review 2026-11-22 E1), so the granary stands
/// in the office court at the head of its column, its north face no further south than the office hall's (the two-court plan's nearest
/// seat to Pingyao's, a DEVIATION), and a cart still reaches its door.
#[test]
fn the_county_example_keeps_an_armory_and_its_granary_on_the_offices_side() {
    let tree = tree();
    let spec = tree.join(
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
    );
    let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
    let (l, _) = super::generate(&p, &bands).unwrap();
    let at = |kind: &str| {
        let i = p.buildings.iter().position(|b| b.kind == kind).unwrap();
        l.seats[i].unwrap()
    };
    let hall = p
        .buildings
        .iter()
        .find(|b| b.kind == "office hall")
        .unwrap();
    let armory = hall.rooms.iter().any(|r| r.kind == "armory");
    let (granary, office) = (at("granary"), at("office hall"));
    let behind = p.divider <= granary.1 && granary.1 <= office.1;
    assert!(armory, "no armory in the office hall");
    let why = format!(
        "granary {granary:?}, office hall {office:?}, divider {}",
        p.divider
    );
    assert!(behind, "{why}");
}

/// The county example's long-house doors each front open court (449 T280, T288; building-review 2026-11-22 E1: T274's recentred hall
/// pushed the tax archive to 7.5 ft off the senior retainers' long-house, so the karo's door and his neighbor's faced its blank wall down a
/// dead-end lane): no other building stands within `APPROACH` (12 ft) before any of its doors, across the door's width.
///
/// Research: a dwelling door's frontage - GUESS: 12 ft, the gate approach's held depth reused (`layout::APPROACH`); no page states the
/// ground before a compound rowhouse's doors (449 T280's research pass, 2026-11-22: the sources say only that the rows along a compound's
/// edge were entered from inside it)
#[test]
fn the_county_examples_long_house_doors_front_open_court() {
    let tree = tree();
    let spec = tree.join(
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
    );
    let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
    let (l, _) = super::generate(&p, &bands).unwrap();
    let i = p
        .buildings
        .iter()
        .position(|b| b.kind == "retainers' quarters")
        .unwrap();
    let depth = super::layout::APPROACH;
    let fronts: Vec<super::spec::Bx> = l
        .doors
        .iter()
        .filter(|d| d.b == i)
        .map(|d| frontage(d.step, d.face, depth))
        .collect();
    let blocked: Vec<(&str, super::spec::Bx)> = fronts
        .iter()
        .flat_map(|&f| l.seats.iter().enumerate().map(move |(j, at)| (j, at, f)))
        .filter_map(|(j, at, f)| {
            let hit = j != i && at.is_some_and(|a| super::grid::overlaps(a, f));
            hit.then_some((p.buildings[j].name.as_str(), f))
        })
        .collect();
    assert!(!fronts.is_empty(), "the retainers' quarters have no door");
    assert_eq!(blocked, Vec::new());
}

/// The ground a door's step fronts, `depth` deep, on the side its face opens to (the long-house test's frontage).
fn frontage(s: super::spec::Bx, face: Face, depth: f64) -> super::spec::Bx {
    match face {
        Face::N => (s.0, s.3 - depth, s.2, s.3),
        Face::S => (s.0, s.1, s.2, s.1 + depth),
        Face::W => (s.2 - depth, s.1, s.2, s.3),
        Face::E => (s.0, s.1, s.0 + depth, s.3),
    }
}

/// Each face's frontage keeps the step's span along the wall and runs `depth` across it.
#[test]
fn a_doors_frontage_runs_depth_from_its_step_on_each_face() {
    let s = (10.0, 20.0, 14.0, 30.0);
    let got: Vec<super::spec::Bx> = [Face::N, Face::S, Face::W, Face::E]
        .iter()
        .map(|&f| frontage(s, f, 2.0))
        .collect();
    assert_eq!(
        got,
        [
            (10.0, 28.0, 14.0, 30.0),
            (10.0, 20.0, 14.0, 22.0),
            (12.0, 20.0, 14.0, 30.0),
            (10.0, 20.0, 12.0, 30.0)
        ]
    );
}

/// No court of a generated sheet leaves a corner bare (449 T274, building-review 2026-11-22 E2: the county example's barracks slid north
/// and left a 31 x 31 ft corner of the office court holding nothing): each court's four corners, a perimeter band's square
/// (`PERIMETER_FT`) inside its walls, each touch a building or a named ground.
#[test]
fn no_court_of_a_pool_sheet_leaves_a_corner_bare() {
    let tree = tree();
    for name in ["ochiba-roundtrip-test", "county-magistracy-example"] {
        let spec = tree.join(format!("pool/magistracies/{name}/{name}.compound.json"));
        let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
        let (l, _) = super::generate(&p, &bands).unwrap();
        let bare = bare_corners(&p, &l.seats);
        let none: Vec<super::spec::Bx> = Vec::new();
        assert_eq!(bare, none, "{name}");
    }
    // T265's drawing: the barracks at the divider end of the east wall - the office court's south-east corner bare
    let spec = tree.join(
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
    );
    let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
    let (mut l, _) = super::generate(&p, &bands).unwrap();
    let i = p
        .buildings
        .iter()
        .position(|b| b.kind == "barracks")
        .unwrap();
    l.seats[i] = Some((244.0, 92.5, 267.0, 162.5));
    let bare = bare_corners(&p, &l.seats);
    let cb = super::ground::court_box(&p, super::spec::Court::Outer);
    let band = super::ground::PERIMETER_FT;
    let south_east = vec![(cb.2 - band, cb.3 - band, cb.2, cb.3)];
    assert_eq!(bare, south_east);
}

/// Each court's corners, a perimeter band's square inside its walls, that touch no building and no named ground.
fn bare_corners(
    p: &super::spec::Program,
    seats: &[Option<super::spec::Bx>],
) -> Vec<super::spec::Bx> {
    let band = super::ground::PERIMETER_FT;
    let held: Vec<super::spec::Bx> = seats
        .iter()
        .flatten()
        .copied()
        .chain(p.zones.iter().map(|z| z.bx))
        .collect();
    let mut bare = Vec::new();
    for court in [super::spec::Court::Inner, super::spec::Court::Outer] {
        let cb = super::ground::court_box(p, court);
        let corners = [
            (cb.0, cb.1, cb.0 + band, cb.1 + band),
            (cb.2 - band, cb.1, cb.2, cb.1 + band),
            (cb.0, cb.3 - band, cb.0 + band, cb.3),
            (cb.2 - band, cb.3 - band, cb.2, cb.3),
        ];
        bare.extend(
            corners
                .into_iter()
                .filter(|c| !held.iter().any(|h| super::grid::overlaps(*h, *c))),
        );
    }
    bare
}

/// The generator's counted work on each pool sheet within twice its budget (`dev/work-budget.json`'s `compound` stage, the derivation's
/// Totals line on each sheet; 444 FR-022's leeway): the counting build alone. `L7R_COMPOUND_COUNTS_OUT=<file>` writes each sheet's counts
/// there, the figures `make budget-sheets PHASE=compound COUNTS=...` reads.
#[cfg(feature = "counters")]
#[test]
fn the_pool_sheets_count_within_twice_their_budget() {
    let tree = tree();
    let budget: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(tree.join("dev/work-budget.json")).unwrap())
            .unwrap();
    let mut out = serde_json::Map::new();
    for name in ["ochiba-roundtrip-test", "county-magistracy-example"] {
        let spec = tree.join(format!("pool/magistracies/{name}/{name}.compound.json"));
        let got: serde_json::Value =
            serde_json::from_str(&super::cli::counts(&tree, &spec.to_string_lossy()).unwrap())
                .unwrap();
        let total = got["total"].as_f64().unwrap();
        let figure = budget["sheet_stages"]["compound"]["sheets"][name]["budget"]
            .as_f64()
            .unwrap();
        assert!(
            total > 0.0 && total <= 2.0 * figure,
            "{name}: {total} against {figure}: {}",
            got["by_kind"]
        );
        out.insert(name.to_owned(), got);
    }
    if let Ok(path) = std::env::var("L7R_COMPOUND_COUNTS_OUT") {
        std::fs::write(path, serde_json::Value::Object(out).to_string()).unwrap();
    }
}

/// The spine's grounds abut and never overlap: an overlap refuses the program before any building is seated.
#[test]
fn the_spines_grounds_never_overlap() {
    let zones = r#", "zones": [{"kind": "garden", "x": 10, "y": 10, "w": 20, "h": 20}, {"kind": "rear yard", "x": 30, "y": 10, "w": 5, "h": 5}]"#;
    assert!(seated(&prog(zones)).is_ok());
    let zones = r#", "zones": [{"kind": "garden", "x": 10, "y": 10, "w": 20, "h": 20}, {"kind": "rear yard", "x": 29, "y": 10, "w": 5, "h": 5}]"#;
    assert!(err(seated(&prog(zones))).contains("the garden and the rear yard overlap"));
}

/// The county example without the ground it names `outer court` - the open ground between the office hall's hearing court and the practice
/// ground, walled by buildings and named grounds, touching no wall - is refused: an UNNAMED central void (docs/buildings.md, Composition).
#[test]
fn an_unnamed_central_void_is_refused() {
    let tree = tree();
    let spec = tree.join(
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
    );
    let mut v: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(spec).unwrap()).unwrap();
    v["zones"]
        .as_array_mut()
        .unwrap()
        .retain(|z| z["caption"] != "outer court");
    let p = read(&v.to_string()).unwrap();
    assert!(err(super::generate(&p, &[])).contains("unnamed open void"));
}

/// A formal entrance's porch stands out from any face by the one shikidai measured (0104: about 12 by 9 ft), its door on the porch's
/// outer edge and its step before that (449 T291).
#[test]
fn a_genkan_is_built_out_from_its_face() {
    let bx = (0.0, 0.0, 40.0, 20.0);
    for (f, porch) in [
        (Face::N, (14.0, -9.0, 26.0, 0.0)),
        (Face::S, (14.0, 20.0, 26.0, 29.0)),
        (Face::W, (-9.0, 4.0, 0.0, 16.0)),
        (Face::E, (40.0, 4.0, 49.0, 16.0)),
    ] {
        let d = super::layout::genkan_at(0, bx, f, 0.5);
        let plain = door_at(0, porch, f, 0.5);
        let got = (d.porch, d.bx, d.step);
        assert_eq!(got, (Some(porch), plain.bx, plain.step), "{f:?}");
    }
}

/// The county example's formal entrance (449 T291): its formal entrance form's knob rolls a genkan on the office hall (0104's drawing
/// page: where office and residence share a compound the genkan is drawn on the office), so the hall draws one porch, built out from its
/// south face, clear of the hearing court and of every other building.
#[test]
fn the_county_examples_office_hall_has_its_genkan() {
    let tree = tree();
    let spec = tree.join(
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
    );
    let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
    let (l, _) = super::generate(&p, &bands).unwrap();
    let i = p
        .buildings
        .iter()
        .position(|b| b.kind == "office hall")
        .unwrap();
    let porches: Vec<(Face, super::spec::Bx)> = l
        .doors
        .iter()
        .filter(|d| d.b == i)
        .filter_map(|d| d.porch.map(|b| (d.face, b)))
        .collect();
    let faces: Vec<Face> = porches.iter().map(|(f, _)| *f).collect();
    assert_eq!(faces, vec![Face::S]);
    let porch = porches[0].1;
    let hall = l.seats[i].unwrap();
    let built_out = (porch.1, porch.0 >= hall.0, porch.2 <= hall.2);
    assert_eq!(built_out, (hall.3, true, true));
    let court = p
        .zones
        .iter()
        .find(|z| z.kind == "hearing court")
        .unwrap()
        .bx;
    let on_court = super::grid::overlaps(porch, court);
    assert!(!on_court, "the genkan stands on the hearing court");
    let hit = (0..p.buildings.len())
        .filter(|&j| j != i && l.seats[j].is_some_and(|a| super::grid::overlaps(a, porch)))
        .count();
    assert_eq!(hit, 0, "a building stands on the genkan");
    let (text, _) = super::cli::compose(&p, &bands).unwrap();
    let drawn = text.matches(r#"data-kind="genkan""#).count();
    let want = 5; // the porch, its door and its caption; the genkan room behind it and its caption (449 T314 Q4)
    assert_eq!(drawn, want, "porch, door, caption; genkan room, caption");
}

#[test]
fn the_county_example_without_its_genkan_lays_a_roji_to_the_shoe_stone() {
    let tree = tree();
    let spec = tree.join(
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
    );
    let (mut p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
    for b in &mut p.buildings {
        for d in &mut b.doors {
            d.genkan = false;
        }
    }
    p.parts.roji = true;
    let (text, _) = super::cli::compose(&p, &bands).unwrap();
    let stones = (
        text.contains(r#"id="shoe-stone""#),
        text.matches("<ellipse").count() > 0,
    );
    assert_eq!(stones, (true, true));
}

/// 0093 (449 T398): a gatekeepers' house of its own stands against its wall beside the gate or inside behind it, as the sheet's seed
/// rolls its `gatehouse site` - behind, it stands past the gate's held approach, to the side of the way in and never across it.
#[test]
fn a_gatehouse_stands_beside_or_behind_its_gate_as_the_seed_rolls() {
    use super::layout::{gatehouse_site, APPROACH, GATEHOUSE_SITES};
    let gatehouse = |more: &str| {
        b(
            "gatehouse",
            "gatehouse",
            "dark",
            (20.0, 6.0),
            "outer",
            "S",
            &format!(r#", "beside": "main gate"{more}"#),
        )
    };
    // sheet "t" rolls behind and "w" beside (zlib.crc32 of "<sheet>:gatehouse site" seeding Python's choice)
    let behind = with(&[gatehouse("")], "");
    let mut beside = behind.clone();
    beside.name = "w".to_owned();
    assert_eq!(
        (gatehouse_site(&behind), gatehouse_site(&beside)),
        (GATEHOUSE_SITES[1], GATEHOUSE_SITES[0])
    );
    let (inside, against) = (
        seated(&behind).unwrap().seats[0].unwrap(),
        seated(&beside).unwrap().seats[0].unwrap(),
    );
    // against the wall beside the gate, and set back past the approach behind it
    assert_eq!(against, (55.0, 91.0, 75.0, 97.0));
    let back = against.1 - inside.1;
    assert!((back - APPROACH).abs() < 1e-9, "{inside:?}");
    // the gate's passage (47..53) and posts (45..55) stay clear of it either side: with a garden taking the ground just east of the
    // way in, the nearer free span is west of it, ending at the west post
    let zone =
        r#", "zones": [{"kind": "garden", "caption": "g", "x": 56, "y": 70, "w": 20, "h": 20}]"#;
    let west = seated(&with(&[gatehouse("")], zone)).unwrap().seats[0].unwrap();
    assert_eq!((west.0, west.2), (25.0, 45.0), "west of the way in");
    // a gatehouse too long for the ground left east of the garden has the west side alone
    let mut long = with(&[gatehouse("")], zone);
    long.buildings[0].w = 40.0;
    let west = seated(&long).unwrap().seats[0].unwrap();
    assert_eq!((west.0, west.2), (5.0, 45.0), "the west side alone");
}

/// 0093 (449 T398): the county example's program under a sheet whose seed rolls its gatehouse behind the gate is refused aloud - the
/// set-back gatehouse takes the ground its deep south-row neighbor's span needs - never drawn squeezed (room first: the envelope is the
/// program's to move); the county's own seed rolls it beside the gate.
#[test]
fn the_county_program_rolled_behind_the_gate_is_refused_aloud() {
    use super::layout::{gatehouse_site, GATEHOUSE_SITES};
    let tree = tree();
    let spec = tree.join(
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
    );
    let (mut p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
    assert_eq!(gatehouse_site(&p), GATEHOUSE_SITES[0]);
    p.name = "county-magistracy-behind".to_owned();
    p.knobs.clear();
    assert_eq!(gatehouse_site(&p), GATEHOUSE_SITES[1]);
    let why = err(super::generate(&p, &bands));
    let room = "no room on its wall for the junior retainers' quarters";
    assert!(why.starts_with(room), "{why}");
}
