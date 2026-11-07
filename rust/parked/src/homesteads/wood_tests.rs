//! The wood share's unit tests (feature 444 T30).
//!
//! Research:
//!     the wood's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::ground::Ground;
use super::wood::{crown_cells, in_keepouts, keepouts, Shares, WoodSite, CANOPY, WOOD};
use super::Counts;
use std::collections::HashSet;

#[test]
fn a_homestead_reserves_its_floor_behind_its_house_and_none_twice() {
    let mut t = Counts::default();
    let ground = Ground::new((0.0, 0.0), (1000.0, 1000.0), &mut t);
    let site = WoodSite {
        ground: &ground,
        streams: &[],
        canvas: (1000.0, 1000.0),
    };
    let house = (0.0 + 500.0, 500.0, 46.0, 28.0);
    let yard = (500.0, 531.0, 30.0, 20.0);
    let own = keepouts(&[house], &[yard]);
    let mut shares = Shares::default();
    let seats = shares
        .share((500.0, 500.0), 0.0, &own, &site, &mut t)
        .expect("room for the wood");
    // the floor covered by the kept seats' crowns, within the reach, none on a part's keep-out, behind the house first
    let held: HashSet<(i64, i64)> = seats
        .iter()
        .flat_map(|&p| crown_cells(p, CANOPY.1, CANOPY.0))
        .collect();
    assert!(f64::from(u32::try_from(held.len()).unwrap_or(0)) * CANOPY.0 * CANOPY.0 >= WOOD.0);
    // the lattice anchored on the house: a seat a whole number of pitches off it, to a tenth
    assert!(seats.iter().any(|p| (p.0 - 500.0).abs() < 1e-9));
    assert!(seats
        .iter()
        .all(|p| (p.0 - 500.0).hypot(p.1 - 500.0) <= WOOD.1 && !in_keepouts(*p, &own)));
    let behind = seats.iter().filter(|p| p.1 < 500.0).count();
    assert!(behind * 2 > seats.len());
    // a neighbor beside it may not cover those seats with its keep-outs, nor seat a crown on their cells alone
    shares.commit(&seats, own, &mut t);
    let close = keepouts(&[(560.0, 470.0, 46.0, 28.0)], &[]);
    assert!(shares.covers_a_seat(&close, &mut t));
    let far = keepouts(&[(900.0, 900.0, 46.0, 28.0)], &[]);
    assert!(!shares.covers_a_seat(&far, &mut t));
    let next = shares
        .share(
            (500.0, 380.0),
            0.0,
            &keepouts(&[(500.0, 380.0, 46.0, 28.0)], &[]),
            &site,
            &mut t,
        )
        .unwrap_or_default();
    assert!(next.iter().all(|p| !seats.contains(p)));
}

#[test]
fn a_seat_is_barred_off_the_sheet_on_taken_ground_or_across_a_stream_and_a_crowded_house_is_refused(
) {
    let mut t = Counts::default();
    let mut ground = Ground::new((0.0, 0.0), (400.0, 400.0), &mut t);
    let none = keepouts(&[], &[]);
    // near the sheet's corner, the seats past the edge are barred, the rest enough
    let site = WoodSite {
        ground: &ground,
        streams: &[],
        canvas: (400.0, 400.0),
    };
    let shares = Shares::default();
    let corner = shares.share((30.0, 30.0), 0.0, &none, &site, &mut t);
    assert!(corner.is_none_or(|s| s.iter().all(|p| p.0 >= 6.0 && p.1 >= 6.0)));
    // a neighbor's keep-outs bar the seats on them
    let mut barred = Shares::default();
    barred.commit(&[], keepouts(&[(200.0, 120.0, 46.0, 28.0)], &[]), &mut t);
    let beside = barred
        .share((200.0, 200.0), 0.0, &none, &site, &mut t)
        .unwrap_or_default();
    assert!(beside
        .iter()
        .all(|p| (p.0 - 200.0).hypot(p.1 - 120.0) >= 0.5 * 46f64.hypot(28.0) + 11.0 + 2.0));
    // a stream across the lot bars the far bank; taken ground bars every seat on it
    let streams = [((0.0, 200.0), (400.0, 200.0))];
    let banked = WoodSite {
        ground: &ground,
        streams: &streams,
        canvas: (400.0, 400.0),
    };
    let s = shares
        .share((200.0, 180.0), 0.0, &none, &banked, &mut t)
        .unwrap_or_default();
    assert!(s.iter().all(|p| p.1 < 200.0));
    ground.fill_ring(
        &[(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)],
        &mut t,
    );
    let full = WoodSite {
        ground: &ground,
        streams: &[],
        canvas: (400.0, 400.0),
    };
    assert!(shares
        .share((200.0, 200.0), 0.0, &none, &full, &mut t)
        .is_none());
    // a seat past the raster's window is barred too: the window holds the house's three by three seats, too few for the floor
    let small = Ground::new((180.0, 180.0), (220.0, 220.0), &mut t);
    let window = WoodSite {
        ground: &small,
        streams: &[],
        canvas: (400.0, 400.0),
    };
    assert!(shares
        .share((200.0, 200.0), 0.0, &none, &window, &mut t)
        .is_none());
}

#[test]
fn a_crowns_cells_are_those_whose_centers_it_holds() {
    let got: HashSet<(i64, i64)> = crown_cells((10.3, -4.7), 11.0, 2.0).into_iter().collect();
    let mut want = HashSet::new();
    for i in -10..15 {
        for j in -15..10 {
            let (x, y) = ((f64::from(i) + 0.5) * 2.0, (f64::from(j) + 0.5) * 2.0);
            if (x - 10.3).powi(2) + (y + 4.7).powi(2) <= 121.0 {
                want.insert((i64::from(i), i64::from(j)));
            }
        }
    }
    assert_eq!(got, want);
}
