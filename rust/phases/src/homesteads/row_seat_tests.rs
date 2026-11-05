//! A row village's seating: its unit tests (feature 444 T30).
//!
//! Research:
//!     the row seating's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::bearing::Margin;
use super::bundle::Grove;
use super::dispersed::bundle_turn;
use super::fit_rules::Rules;
use super::fixtures::{Forms, Kind};
use super::ground::Ground;
use super::grove_seat::{Axes, Corridors, GroveSite};
use super::level::Hard;
use super::lots::Lots;
use super::place::Site;
use super::row_seat::{seat_rows, RowSite};
use super::rows::Form;
use super::Counts;
use crate::field::fan::Pt;

#[test]
#[expect(
    clippy::too_many_lines,
    clippy::cast_precision_loss,
    reason = "one fixture and its assertions; a ring of four points"
)]
fn a_row_village_seats_its_farms_along_its_streets_with_their_holdings() {
    let mut t = Counts::default();
    let canvas = (2400.0, 2400.0);
    let field = vec![
        (200.0, 1500.0),
        (2200.0, 1500.0),
        (2200.0, 2300.0),
        (200.0, 2300.0),
    ];
    let mut ground = Ground::new((0.0, 0.0), canvas, &mut t);
    ground.fill_ring(&field, &mut t);
    let reach = ground.reach(&[], &mut t);
    let margin = Margin::new(&field, 0.0, &mut t);
    let lots = Lots::deal(4, 7, 0.0, &[(Kind::Privy, 1.0)]);
    let forms = Forms::default();
    let beyond = |_p: Pt| true;
    assert!(beyond((0.0, 0.0)));
    let rules = Rules {
        chains: vec![vec![((200.0, 1500.0), (2200.0, 1500.0), (0.0, -1.0))]],
        sun: true,
        ..Rules::default()
    };
    let site = Site {
        ground: &ground,
        beyond: &beyond,
        reach: &reach,
        field: &field,
        streams: &[],
        canvas,
        bearing: (&margin, 0.0),
        lots: &lots,
        byre: None,
        forms: &forms,
        shade: 50.0,
        rules: &rules,
    };
    let chains = rules.chains.clone();
    let paddies = vec![field.clone()];
    let corridors = Corridors::default();
    let gs = GroveSite {
        site: &site,
        grove: Grove {
            sides: 2,
            turn: bundle_turn("NW"),
            sun_band: false,
            well: 0.0,
            yard_sun: 22.0,
        },
        paddies: &paddies,
        corridors: &corridors,
        axes: Axes {
            c: (1200.0, 1250.0),
            along: (1.0, 0.0),
            out: (0.0, -1.0),
            anchor: (1200.0, 1500.0),
            lat: 400.0,
        },
        chains: &chains,
        house_max: (62.1, 30.8),
        shape: "elongated",
        alleys: false,
        seed: 7,
        want: 12,
        band: (400.0, 150.0),
        bound: 500.0,
        single_file: false,
        streets: (&[], 0.0),
    };
    let hard = Hard::new(
        &[field.clone()],
        &[((1000.0, 1300.0), (1000.0, 1490.0), 8.0)],
        &mut t,
    );
    let rs = RowSite {
        gs,
        hard: &hard,
        anchor: (1200.0, 1440.0),
        both: true,
        form: Form::Street,
        shelter: (
            true,
            (
                -std::f64::consts::FRAC_1_SQRT_2,
                -std::f64::consts::FRAC_1_SQRT_2,
            ),
        ),
        front: (1.0, 0.0),
        sheet: canvas,
    };
    // seven lots dealt for twelve households: once they are spent a clear seat's offer is refused, and the row goes on to its end
    let rows = seat_rows(&rs);
    let n = rows.seating.seated.len();
    assert_eq!(n, 7);
    assert_eq!(rows.sheltered.len(), n);
    // every far-row farm with its holding, behind it and off every house
    assert!(!rows.holdings.is_empty());
    for (ring, _t, nrm, depth, lot) in &rows.holdings {
        let h = rows.seating.seated[*lot].bundle.house;
        let c = ring.iter().fold((0.0, 0.0), |a, p| {
            (a.0 + p.0 / ring.len() as f64, a.1 + p.1 / ring.len() as f64)
        });
        assert!((c.0 - h.0) * nrm.0 + (c.1 - h.1) * nrm.1 > 0.0 && *depth > 0.0);
    }
    // the streets that seated a farm, each farm's house beside its street
    assert!(
        !rows.streets.is_empty()
            && rows
                .streets
                .iter()
                .all(|(l, f)| l.len() >= 2 && !f.is_empty())
    );
    // one side only on the dry edge, two farms wanted: no holdings, no shelter, the rows stopped once both stand
    let one = seat_rows(&RowSite {
        gs: GroveSite { want: 2, ..rs.gs },
        both: false,
        form: Form::Edge,
        ..rs
    });
    assert!(
        one.holdings.is_empty()
            && one.sheltered.iter().all(|s| !s)
            && one.seating.seated.len() == 2
    );
    // a run of ponds along the row: seated round them, never more farms than wanted
    let ponds = [
        field.clone(),
        vec![
            (400.0, 1100.0),
            (440.0, 1100.0),
            (440.0, 1480.0),
            (400.0, 1480.0),
        ],
        vec![
            (490.0, 1100.0),
            (530.0, 1100.0),
            (530.0, 1480.0),
            (490.0, 1480.0),
        ],
        vec![
            (580.0, 1100.0),
            (620.0, 1100.0),
            (620.0, 1480.0),
            (580.0, 1480.0),
        ],
        vec![
            (670.0, 1100.0),
            (710.0, 1100.0),
            (710.0, 1480.0),
            (670.0, 1480.0),
        ],
        vec![
            (760.0, 1100.0),
            (800.0, 1100.0),
            (800.0, 1480.0),
            (760.0, 1480.0),
        ],
        vec![
            (850.0, 1100.0),
            (890.0, 1100.0),
            (890.0, 1480.0),
            (850.0, 1480.0),
        ],
        vec![
            (940.0, 1100.0),
            (980.0, 1100.0),
            (980.0, 1480.0),
            (940.0, 1480.0),
        ],
        vec![
            (1030.0, 1100.0),
            (1070.0, 1100.0),
            (1070.0, 1480.0),
            (1030.0, 1480.0),
        ],
        vec![
            (1120.0, 1100.0),
            (1160.0, 1100.0),
            (1160.0, 1480.0),
            (1120.0, 1480.0),
        ],
        vec![
            (1210.0, 1100.0),
            (1250.0, 1100.0),
            (1250.0, 1480.0),
            (1210.0, 1480.0),
        ],
        vec![
            (1300.0, 1100.0),
            (1340.0, 1100.0),
            (1340.0, 1480.0),
            (1300.0, 1480.0),
        ],
        vec![
            (1390.0, 1100.0),
            (1430.0, 1100.0),
            (1430.0, 1480.0),
            (1390.0, 1480.0),
        ],
        vec![
            (1480.0, 1100.0),
            (1520.0, 1100.0),
            (1520.0, 1480.0),
            (1480.0, 1480.0),
        ],
        vec![
            (1570.0, 1100.0),
            (1610.0, 1100.0),
            (1610.0, 1480.0),
            (1570.0, 1480.0),
        ],
        vec![
            (1660.0, 1100.0),
            (1700.0, 1100.0),
            (1700.0, 1480.0),
            (1660.0, 1480.0),
        ],
        vec![
            (1750.0, 1100.0),
            (1790.0, 1100.0),
            (1790.0, 1480.0),
            (1750.0, 1480.0),
        ],
        vec![
            (1840.0, 1100.0),
            (1880.0, 1100.0),
            (1880.0, 1480.0),
            (1840.0, 1480.0),
        ],
        vec![
            (1930.0, 1100.0),
            (1970.0, 1100.0),
            (1970.0, 1480.0),
            (1930.0, 1480.0),
        ],
        vec![
            (2020.0, 1100.0),
            (2060.0, 1100.0),
            (2060.0, 1480.0),
            (2020.0, 1480.0),
        ],
    ];
    let brook = Hard::new(&ponds, &[((1000.0, 1300.0), (1000.0, 1490.0), 8.0)], &mut t);
    let crossed = seat_rows(&RowSite { hard: &brook, ..rs });
    assert!(crossed.seating.seated.len() <= n);
    // a dry edge long enough to turn the field's corners: a frame at the bend reaches across its own street and is passed over
    let bent = seat_rows(&RowSite {
        form: Form::Edge,
        ..rs
    });
    assert!(bent.seating.seated.len() <= n);
    // no hard ground: no street, no farm
    let none = seat_rows(&RowSite {
        hard: &Hard::new(&[], &[], &mut t),
        ..rs
    });
    assert!(none.seating.seated.is_empty() && none.streets.is_empty());
}
