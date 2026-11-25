//! The feeder and the outfall's run drawn no narrower than a dike-pond block's ring canal (449 T431), apart from `tests.rs`,
//! which stands at the file-size bar.
//!
//! Research:
//!     the crossings' tests - NONE: fixtures and assertions; the rule's claim is at `sluice_channels`

use crate::driver::{roll, spec::parse};

/// The stroke width the map draws the line through `pts` at, read off the SVG by the line's own path.
fn drawn_width(svg: &str, pts: &[(f64, f64)]) -> f64 {
    let f = |v: f64| {
        let s = format!("{v:.1}");
        s.strip_suffix(".0").map_or(s.clone(), str::to_owned)
    };
    let d: Vec<String> = pts
        .iter()
        .map(|p| format!("{},{}", f(p.0), f(p.1)))
        .collect();
    let key = format!(r#"<path d="M{}" fill="none""#, d.join(" L"));
    let at = svg.find(&key).expect("the line is drawn");
    let rest = &svg[at..];
    let w = rest.find("stroke-width=\"").unwrap() + 14;
    rest[w..w + rest[w..].find('"').unwrap()].parse().unwrap()
}

/// NO STEP DOWN UNDER A SLUICE ON A DIKE-POND BLOCK (449 T431): the feeder into the inlet and the outfall's run out of it are
/// drawn no narrower than the ring canal they join through the sluices, the block's creek width; a rice polder's keep 3 and
/// 5.5 ft. Red before T431: on Kuwabata the feeder was drawn 3 ft against a 6.2 ft ring and the run 5.5 ft.
#[test]
fn a_dike_ponds_feeder_and_outfall_run_are_no_narrower_than_its_ring_canal() {
    let (mut got, mut want) = (Vec::new(), Vec::new());
    for spec in [
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
        r#"{"name": "P35", "seed": 35, "households": 15, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond"}"#,
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let join = |seg: &str| s.polder.ditches.iter().find(|d| d.seg == seg).unwrap().w;
        let dikepond = s.converted.is_some();
        for (name, course, ring, rice) in [
            (
                "feeder",
                s.polder.feeder.as_slice(),
                join("inlet_join"),
                3.0,
            ),
            (
                "outfall run",
                s.outfall.as_slice(),
                join("outfall_join"),
                5.5,
            ),
        ] {
            let w = drawn_width(&r.svg, course);
            let ok = if dikepond {
                // the SVG writes a tenth of a foot
                w >= ring - 0.05
            } else {
                (w - rice).abs() < 1e-9
            };
            got.push(format!(
                "{} {name}: drawn {w} ft, ring {ring:.2} ft, as owed {ok}",
                r.plan.name
            ));
            want.push(format!(
                "{} {name}: drawn {w} ft, ring {ring:.2} ft, as owed true",
                r.plan.name
            ));
        }
    }
    assert_eq!(got, want);
}
