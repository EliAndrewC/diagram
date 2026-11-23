//! The compound generator's open-ground tests (feature 449 T152; split from `gen_tests_parts.rs` at the 1,000-line bar by 449 T265): the
//! open ground's unnamed void and the cart route from a gate to the granary's and the stables' doors, in either court.
//!
//! Research: the generator's open-ground tests - NONE: fixtures and assertions, deciding nothing about a building

use super::gen_tests_seat::{b, err, prog, seated, with};
use super::layout::Layout;
use super::spec::Program;

fn laid(p: &Program) -> Layout {
    let mut l = seated(p).unwrap();
    l.seat_doors(p).unwrap();
    l
}

#[test]
fn the_open_ground_holds_no_unnamed_void_and_a_cart_reaches_the_granary_and_stables() {
    // a court with nothing in its center: void; the same center named, or a compound too small to have a center past its perimeter
    let big = r#"{"name": "t", "title": "T", "envelope": {"w": 200, "h": 200, "divider": 100}, "gates": [{"kind": "main gate", "wall": "S", "at": 100, "width": 6}]}"#;
    let p = super::spec::read(big).unwrap();
    assert!(err(super::ground::open_ground(&p, &laid(&p))).contains("unnamed open void"));
    let p = prog("");
    super::ground::open_ground(&p, &laid(&p)).unwrap();
    let named = r#", "zones": [{"kind": "inner court", "x": 3, "y": 3, "w": 94, "h": 44}, {"kind": "outer court", "x": 30, "y": 53, "w": 40, "h": 30}]"#;
    let gates = r#""gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}, {"kind": "side gate", "wall": "N", "at": 50, "width": 6}, {"kind": "side gate", "wall": "E", "at": 80, "width": 6}]"#;
    let src = super::gen_tests::small(&format!(
        r#"{named}, "buildings": [{}, {}]"#,
        b("granary", "granary", "kura", (20.0, 10.0), "outer", "W", ""),
        b(
            "stables",
            "stables",
            "service",
            (10.0, 10.0),
            "outer",
            "N",
            r#", "inset": 0"#
        )
    ))
    .replacen(
        r#""gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}]"#,
        gates,
        1,
    );
    let p =
        super::spec::read(&src.replace(r#""wall": "N", "inset": 0"#, r#""wall": "E""#)).unwrap();
    super::ground::open_ground(&p, &laid(&p)).unwrap();
    let walled = with(
        &[
            b(
                "granary",
                "granary",
                "kura",
                (20.0, 10.0),
                "outer",
                "W",
                r#", "doors": [{"face": "N", "at": 0.5}]"#,
            ),
            b(
                "ring",
                "k",
                "plain",
                (40.0, 10.0),
                "outer",
                "divider",
                r#", "near": 3"#,
            ),
            b(
                "post",
                "k",
                "plain",
                (6.0, 20.0),
                "outer",
                "W",
                r#", "order": 2"#,
            ),
        ],
        named,
    );
    let mut l = Layout::new(&walled);
    l.seats = vec![
        Some((3.0, 64.0, 23.0, 74.0)),
        Some((3.0, 52.5, 43.0, 62.5)),
        Some((23.0, 60.0, 29.0, 80.0)),
    ];
    l.doors = vec![super::layout::door_at(
        0,
        (3.0, 64.0, 23.0, 74.0),
        super::spec::Face::N,
        0.5,
    )];
    assert!(err(super::ground::open_ground(&walled, &l)).contains("no cart route"));
    assert!(!super::ground::reaches(
        &super::ground::sweep(&[], (0.0, 0.0, 10.0, 10.0)),
        &[],
        (1.0, 1.0)
    ));
}

/// A granary stands on the office's side of the divider (0123: Pingyao built its granary north of the official quarters behind the war,
/// justice and works offices, not in the residence's court; building-review 2026-11-22 E1): one seated in the household's court is
/// refused whatever gate its court has (449 T274, which undid T265's walk from the inner court's own gate); one in the office court,
/// between the divider and the office hall, is reached by cart from an outer gate round the hall's end.
#[test]
fn a_granary_stands_on_the_offices_side_of_the_divider() {
    let granary = |court: &str, wall: &str| {
        b(
            "granary",
            "granary",
            "kura",
            (20.0, 10.0),
            court,
            wall,
            r#", "doors": [{"face": "E", "at": 0.5}]"#,
        )
    };
    let hall = b(
        "office hall",
        "office hall",
        "lord",
        (40.0, 10.0),
        "outer",
        "divider",
        r#", "order": 10, "inset": 16"#,
    );
    let gates = r#""gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}, {"kind": "side gate", "wall": "E", "at": 42, "width": 6}]"#;
    let laid_out = |buildings: &[String]| {
        let src = super::gen_tests::small(&format!(
            r#", "zones": [{{"kind": "inner court", "x": 3, "y": 3, "w": 94, "h": 20}}], "buildings": [{}]"#,
            buildings.join(", ")
        ))
        .replacen(
            r#""gates": [{"kind": "main gate", "wall": "S", "at": 50, "width": 6}]"#,
            gates,
            1,
        );
        let p = super::spec::read(&src).unwrap();
        super::ground::open_ground(&p, &laid(&p))
    };
    let household = err(laid_out(&[granary("inner", "E")]));
    let office = err(laid_out(&[hall, granary("outer", "divider")]));
    assert!(household.contains("household's court"), "{household}");
    // the fix the refusal names is 0123's drawing page's seat, an office-court flanking column beside the hall, never behind the
    // office hall, where the household's court lies (449 T366)
    let flank = "one of the office court's flank columns beside the office hall";
    assert!(household.contains(flank), "{household}");
    assert!(!household.contains("behind the office hall"), "{household}");
    assert!(office.is_empty(), "{office}");
}

/// A granary's or stable's door on an end along its row opens on a lane a cart passes beside the door's tub (449 T388: the county example's
/// stables, entered at the west gable, put their tub in the 6 ft fire gap and left a cart 2.7 ft): on each pool sheet the program draws,
/// the ground between the tub and the nearest building across the lane is at least `CART_FT`.
#[test]
fn a_cart_route_door_on_an_end_keeps_a_carts_width_past_its_tub() {
    use super::ground::{CART_FT, CART_KINDS};
    use super::parts::TUB_R;
    use super::spec::Face;
    let tree = super::gen_tests_seat::tree();
    let mut lanes = 0;
    for name in ["county-magistracy-example", "ochiba-roundtrip-test"] {
        let spec = tree.join(format!("pool/magistracies/{name}/{name}.compound.json"));
        let (p, bands) = super::cli::load(&tree, &spec.to_string_lossy()).unwrap();
        let (l, s) = super::generate(&p, &bands).unwrap();
        for d in &l.doors {
            let b = &p.buildings[d.b];
            let along_x = matches!(
                b.wall,
                super::spec::Wall::Side(Face::N | Face::S) | super::spec::Wall::Divider
            );
            let on_end = matches!(
                (along_x, d.face),
                (true, Face::W | Face::E) | (false, Face::N | Face::S)
            );
            if !CART_KINDS.contains(&b.kind.as_str()) || !on_end {
                continue;
            }
            let (dx, dy) = d.mid();
            let tub = s
                .tubs
                .iter()
                .copied()
                .min_by(|a, c| {
                    (a.0 - dx)
                        .hypot(a.1 - dy)
                        .total_cmp(&(c.0 - dx).hypot(c.1 - dy))
                })
                .unwrap();
            // the tub's far edge from the door's face, and the nearest building across the lane over the tub's own span
            // read in the lane's own frame: `a` across the lane (outward from the door's face, `out`), `c` along it
            let x_lane = matches!(d.face, Face::W | Face::E);
            let sw = |p: (f64, f64)| if x_lane { p } else { (p.1, p.0) };
            let (ta, tc) = sw(tub);
            let out = if matches!(d.face, Face::W | Face::N) {
                -1.0
            } else {
                1.0
            };
            let (far, lo, hi) = (ta + out * TUB_R, tc - TUB_R, tc + TUB_R);
            let clear = l
                .seats
                .iter()
                .enumerate()
                .filter_map(|(j, a)| a.filter(|_| j != d.b))
                .filter_map(|a| {
                    let ((a0, c0), (a1, c1)) = (sw((a.0, a.1)), sw((a.2, a.3)));
                    let across = c0 < hi && c1 > lo;
                    match d.face {
                        Face::W | Face::N => (across && a1 <= far).then_some(far - a1),
                        Face::E | Face::S => (across && a0 >= far).then_some(a0 - far),
                    }
                })
                .fold(f64::INFINITY, f64::min);
            lanes += 1;
            let (fits, at) = (clear >= CART_FT - 1e-9, &b.name);
            assert!(fits, "{name}: {at} tub leaves a cart {clear:.2} ft");
        }
    }
    assert_eq!(lanes, 2, "the county's and the round trip's stables");
}

/// 0082 (449 T397): a stables with a door on each end along its row holds a cart's lane at both ends, so seated at either end of its
/// row the wall past that door stands a whole lane off, not at the first door's end alone.
#[test]
fn a_door_on_each_end_keeps_a_carts_lane_at_both() {
    use super::layout::{CART_LANE, WALL_HALF};
    let doors =
        r#""interior": "stables", "doors": [{"face": "W", "at": 0.5}, {"face": "E", "at": 0.5}]"#;
    for near in [0, 200] {
        let extra = format!(r#", "near": {near}, {doors}"#);
        let spec = b(
            "stables",
            "stables",
            "service",
            (18.0, 24.0),
            "outer",
            "S",
            &extra,
        );
        let p = with(&[spec], "");
        let l = seated(&p).unwrap();
        let (x0, _, x1, _) = l.seats[0].unwrap();
        let (west, east) = (x0 - WALL_HALF, p.w - WALL_HALF - x1);
        let lane = west.min(east);
        assert!(lane >= CART_LANE - 1e-9, "near {near}: {lane:.2} ft");
    }
    // mid-row on the 100 ft fixture (its gate's approach at 45..55), a smaller neighbor seated after it nearest the second door's end
    // stands a whole lane off that door: the high end's held ground as well as the low's
    let stables = b(
        "stables",
        "stables",
        "service",
        (18.0, 24.0),
        "outer",
        "S",
        &format!(r#", "near": 60, {doors}"#),
    );
    let shed = b(
        "shed",
        "shed",
        "plain",
        (5.0, 5.0),
        "outer",
        "S",
        r#", "near": 85"#,
    );
    let l = seated(&with(&[stables, shed], "")).unwrap();
    let ((_, _, s1, _), (n0, _, _, _)) = (l.seats[0].unwrap(), l.seats[1].unwrap());
    let lane = n0 - s1;
    assert!(lane >= CART_LANE - 1e-9, "{lane:.2} ft past the east door");
}

#[test]
fn a_cart_route_door_at_its_rows_end_keeps_a_carts_lane_to_the_wall() {
    use super::layout::{court_range, CART_LANE, CLEAR, WALL_HALF};
    // a stables alone on its row, seated at the end its door is on: the S wall's west end (its default west gable), the same stables
    // near the east end with its door declared east, and one on the W wall at the divider's end (its default north gable)
    let gable = r#", "interior": "stables""#;
    let east = r#", "interior": "stables", "near": 100, "doors": [{"face": "E", "at": 0.5}]"#;
    let cases = [
        (
            b(
                "stables",
                "stables",
                "service",
                (18.0, 24.0),
                "outer",
                "S",
                gable,
            ),
            'W',
        ),
        (
            b(
                "stables",
                "stables",
                "service",
                (18.0, 24.0),
                "outer",
                "S",
                east,
            ),
            'E',
        ),
        (
            b(
                "stables",
                "stables",
                "service",
                (24.0, 18.0),
                "outer",
                "W",
                gable,
            ),
            'N',
        ),
    ];
    for (spec, face) in cases {
        let p = with(&[spec], "");
        let l = seated(&p).unwrap();
        let (x0, y0, x1, _) = l.seats[0].unwrap();
        let lo = court_range(&p, super::spec::Court::Outer).0;
        let lane = match face {
            'W' => x0 - WALL_HALF,
            'E' => p.w - WALL_HALF - x1,
            _ => y0 - (lo - CLEAR),
        };
        let fits = lane >= CART_LANE - 1e-9;
        assert!(fits, "{face}: {lane:.2} ft to the row's end");
    }
}
