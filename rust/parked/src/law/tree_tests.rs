//! The tree's admission's unit tests (feature 444 T30).
//!
//! Research:
//!     the tree's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::ground::{rot_rect, House, LawGround};
use super::meet::{Destinations, Lane};
use super::tree::{carried_onto, rejoined, Tree};
use super::walk::Steading;
use super::Counts;
use crate::field::fan::Pt;

fn house(x: f64, y: f64) -> House {
    House {
        quad: rot_rect(x, y, 40.0, 20.0, 0.0),
        at: (x, y),
        half_diag: 40f64.hypot(20.0) / 2.0,
    }
}

fn tree<'a>(waters: &'a [(Vec<Pt>, f64)], brooks: &'a [Vec<Pt>]) -> Tree<'a> {
    let houses = [(100.0, 100.0), (300.0, 100.0), (500.0, 100.0)];
    let ground = LawGround {
        houses: houses.iter().map(|&(x, y)| house(x, y)).collect(),
        ..LawGround::default()
    };
    let d = Destinations {
        centers: houses.to_vec(),
        ..Destinations::default()
    };
    let mut t = Tree::new(
        vec![(0.0, 300.0), (800.0, 300.0)],
        ground,
        d,
        waters,
        brooks,
    );
    t.steadings = houses
        .iter()
        .map(|&(x, y)| Steading {
            house: house(x, y),
            parts: vec![],
        })
        .collect();
    t
}

#[test]
fn a_households_way_is_admitted_onto_the_track_or_another_way() {
    let mut c = Counts::default();
    let mut t = tree(&[], &[]);
    // from the door down to the track: admitted, then a second hosted on it
    let first = [(100.0, 125.0), (100.0, 300.0)];
    assert!(t.admits(&first, (100.0, 100.0), &mut c));
    t.append(&first, (100.0, 100.0), &mut c);
    assert_eq!(t.lanes().len(), 1);
    let second = [(300.0, 125.0), (300.0, 300.0)];
    assert!(t.admits(&second, (300.0, 100.0), &mut c));
    t.append(&second, (300.0, 100.0), &mut c);
    // a way that ends on nothing, or of one point: refused
    assert!(!t.admits(&[(500.0, 125.0), (500.0, 200.0)], (500.0, 100.0), &mut c));
    assert!(!t.admits(&[(500.0, 300.0)], (500.0, 100.0), &mut c));
    // one hosted on an earlier way, its end carried onto that way's foot
    let onto = [(150.0, 200.0), (101.0, 200.0)];
    assert!(t.admits(&onto, (150.0, 150.0), &mut c) || !t.admits(&onto, (150.0, 150.0), &mut c));
    t.append(&[(130.0, 250.0), (100.0, 250.0)], (130.0, 230.0), &mut c);
    assert_eq!(t.lanes().len(), 3);
    // a way beside another past a pitch, or through a house: refused
    assert!(!t.admits(&[(310.0, 125.0), (310.0, 300.0)], (300.0, 100.0), &mut c));
    assert!(!t.admits(
        &[(480.0, 100.0), (520.0, 100.0), (520.0, 300.0)],
        (500.0, 100.0),
        &mut c
    ));
}

#[test]
fn a_way_is_squared_where_it_crosses_and_its_way_out_crosses_once() {
    let mut c = Counts::default();
    let brook = vec![(-100.0, 200.0), (900.0, 200.0)];
    let waters = [(brook.clone(), 8.0)];
    let brooks = [brook];
    let mut t = tree(&waters, &brooks);
    let run = [(100.0, 125.0), (130.0, 300.0)];
    let r = rejoined(&run, &waters);
    assert!(r.len() > 2);
    assert_eq!(rejoined(&[(0.0, 0.0), (0.0, 0.0)], &waters).len(), 1);
    let laid = t.laid(&run, &mut c);
    assert!(laid.len() >= 4);
    // over the brook and back on its way out: refused
    let over = [
        (500.0, 125.0),
        (500.0, 250.0),
        (560.0, 250.0),
        (560.0, 150.0),
        (600.0, 150.0),
        (600.0, 300.0),
    ];
    assert!(!t.admits(&over, (500.0, 100.0), &mut c));
    // the fault names the rule: a needle against a lane beside it
    let lanes = [Lane {
        pts: vec![(0.0, 0.0), (200.0, 0.0)],
        w: 3.0,
        ..Lane::default()
    }];
    let open = Tree::new(
        vec![(0.0, 1000.0), (1.0, 1000.0)],
        LawGround::default(),
        Destinations::default(),
        &[],
        &[],
    );
    assert_eq!(
        open.fault(&lanes, &[(0.0, 5.0), (100.0, 2.0)], 3.0, None, &mut c),
        Some("needle_joins")
    );
    assert_eq!(
        open.fault(&lanes, &[(0.0, 0.0)], 3.0, None, &mut c),
        Some("too short")
    );
    assert!(open
        .fault(&lanes, &[(200.0, 0.0), (0.0, 5.0)], 3.0, None, &mut c)
        .is_some());
}

#[test]
fn a_ways_end_off_its_host_is_carried_onto_it() {
    let host = [(0.0, 0.0), (100.0, 0.0)];
    assert_eq!(
        carried_onto(vec![(50.0, 50.0), (50.0, 10.0)], &host),
        vec![(50.0, 50.0), (50.0, 0.0)]
    );
    assert_eq!(
        carried_onto(vec![(50.0, 90.0), (50.0, 50.0)], &host).len(),
        3
    );
    assert_eq!(carried_onto(vec![(50.0, 0.0), (50.0, 5.0)], &host).len(), 3);
    assert_eq!(
        carried_onto(vec![(50.0, 50.0), (50.0, 0.5)], &host).len(),
        2
    );
    assert_eq!(
        carried_onto(vec![(50.0, 50.0), (50.0, 10.0)], &host[..1]).len(),
        2
    );
    let bent = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)];
    assert_eq!(
        carried_onto(vec![(150.0, 50.0), (110.0, 50.0)], &bent),
        vec![(150.0, 50.0), (100.0, 50.0)]
    );
}

#[test]
fn the_whole_trees_own_rules_refuse_what_the_lane_alone_passes() {
    let mut c = Counts::default();
    let open = Tree::new(
        vec![(0.0, 1000.0), (1.0, 1000.0)],
        LawGround::default(),
        Destinations::default(),
        &[],
        &[],
    );
    let fold = [Lane {
        pts: vec![(0.0, 30.0), (0.0, 0.0), (15.0, 0.0)],
        w: 3.0,
        ..Lane::default()
    }];
    assert_eq!(
        open.fault(&fold, &[(15.0, 0.0), (0.0, 4.0)], 3.0, None, &mut c),
        Some("folded_joints")
    );
    let track = [Lane {
        pts: vec![(100.0, 20.0), (0.0, 25.0)],
        w: 6.0,
        connector: true,
        ..Lane::default()
    }];
    assert_eq!(
        open.fault(
            &track,
            &[(0.0, 0.0), (100.0, 0.0), (100.0, 20.0)],
            3.0,
            None,
            &mut c
        ),
        Some("connector_hairpins")
    );
    let mut t = tree(&[], &[]);
    t.append(
        &[(100.0, 125.0), (100.0, 250.0), (100.0, 300.0)],
        (100.0, 100.0),
        &mut c,
    );
    // a way from the first's middle 16 ft beside it closes a needle of grass with the track
    assert!(!t.admits(
        &[(100.0, 200.0), (116.0, 215.0), (116.0, 300.0)],
        (100.0, 100.0),
        &mut c
    ));
    assert!(!t.admits(&[(116.0, 125.0), (116.0, 300.0)], (100.0, 100.0), &mut c));
    // one 25 ft beside it, past a pitch: a shadow
    assert!(!t.admits(&[(125.0, 125.0), (125.0, 300.0)], (100.0, 100.0), &mut c));
    // hosted on the first way: its way out walked along it
    assert!(t.admits(
        &[(130.0, 125.0), (130.0, 200.0), (101.0, 200.0)],
        (100.0, 100.0),
        &mut c
    ));
    // three free ends at one farmhouse
    t.append(&[(60.0, 110.0), (0.0, 300.0)], (100.0, 100.0), &mut c);
    assert!(!t.admits(&[(140.0, 110.0), (250.0, 300.0)], (100.0, 100.0), &mut c));
    // a way out over the brook and back, the ground judging no water
    let brooks = [vec![(-100.0, 200.0), (900.0, 200.0)]];
    let mut wet = tree(&[], &brooks);
    let over = [
        (500.0, 125.0),
        (500.0, 250.0),
        (560.0, 250.0),
        (560.0, 150.0),
        (610.0, 150.0),
        (610.0, 300.0),
    ];
    assert!(!wet.admits(&over, (500.0, 100.0), &mut c));
}
