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
    assert!(office.is_empty(), "{office}");
}
