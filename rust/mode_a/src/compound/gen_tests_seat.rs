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

/// The gatehouse beside the main gate; a building's own start along its wall; the middle gate beside the office hall.
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
    assert_eq!(l.seats[0], Some((55.0, 91.0, 75.0, 97.0)));
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
