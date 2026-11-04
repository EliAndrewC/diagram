//! The gaps' ways' unit tests (feature 444 T30).
//!
//! Research:
//!     the gaps' ways' tests - NONE: fixtures and assertions, deciding nothing about the place

use super::access::{parts_of, AccessTree};
use super::bundle::Bundle;
use super::gap_ways::{
    gathered_foot, junction_points, lay_the_ways, nearest_foot, GapSite, Household, Judge,
};
use super::ground::Ground;
use super::wood::Shares;
use super::Counts;
use crate::field::fan::Pt;

fn household(x: f64, y: f64) -> Household {
    let r = |dx: f64, dy: f64, w: f64, h: f64| (x + dx, y + dy, w, h);
    let b = Bundle {
        house: r(0.0, 0.0, 40.0, 20.0),
        yard: r(0.0, 25.0, 30.0, 20.0),
        gardens: vec![r(30.0, 25.0, 10.0, 10.0)],
        boxes: vec![
            r(0.0, 0.0, 40.0, 20.0),
            r(0.0, 25.0, 30.0, 20.0),
            r(30.0, 25.0, 10.0, 10.0),
        ],
        bbox: r(0.0, 15.0, 70.0, 50.0),
        ..Bundle::default()
    };
    Household {
        parts: parts_of(&b),
        bbox: b.bbox,
        at: (x, y),
    }
}

struct Open(usize);

impl Judge for Open {
    fn lawful_leg(&mut self, _a: Pt, _b: Pt, _t: &mut Counts) -> bool {
        true
    }
    fn tree_admits(&mut self, _d: &[Pt], k: usize, _t: &mut Counts) -> bool {
        k != self.0
    }
    fn reserve(&mut self, _d: &[Pt], _k: usize) {}
}

struct Shut;

impl Judge for Shut {
    fn lawful_leg(&mut self, _a: Pt, _b: Pt, _t: &mut Counts) -> bool {
        false
    }
    fn tree_admits(&mut self, _d: &[Pt], _k: usize, _t: &mut Counts) -> bool {
        true
    }
    fn reserve(&mut self, _d: &[Pt], _k: usize) {}
}

#[test]
fn each_household_is_laid_a_way_in_the_gaps_to_the_track_or_pinched() {
    let mut t = Counts::default();
    let ground = Ground::new((0.0, 0.0), (3000.0, 3000.0), &mut t);
    let beyond = |_p: Pt| true;
    let mut wood = Shares::default();
    wood.commit(
        &[(700.0, 450.0), (500.0, 530.0)],
        super::wood::keepouts(&[], &[]),
        &mut t,
    );
    let site = GapSite {
        ground: &ground,
        beyond: &beyond,
        wood: &wood,
        canvas: (3000.0, 3000.0),
        lane_gap: 25.0,
    };
    let houses = [
        household(500.0, 500.0),
        household(620.0, 520.0),
        household(560.0, 640.0),
    ];
    let mut tree = AccessTree::new(7.0);
    tree.add((0.0, 800.0), (2900.0, 800.0));
    let ways = lay_the_ways(&site, &houses, &mut tree, &mut Open(usize::MAX), &mut t);
    assert!(ways.drawn.iter().all(Option::is_some));
    assert!(tree.segs.len() > 1);
    // one household the tree refuses: pinched across its nearest reached neighbor's yard
    let mut fresh = AccessTree::new(7.0);
    fresh.add((0.0, 800.0), (2900.0, 800.0));
    let one = lay_the_ways(&site, &houses, &mut fresh, &mut Open(0), &mut t);
    assert!(one.drawn[0].is_none() && one.pinched[0].is_some());
    // nothing on lawful ground: none drawn, none to be pinched across
    let mut shut = AccessTree::new(7.0);
    shut.add((0.0, 800.0), (2900.0, 800.0));
    let none = lay_the_ways(&site, &houses, &mut shut, &mut Shut, &mut t);
    assert!(none.drawn.iter().all(Option::is_none) && none.pinched.iter().all(Option::is_none));
    assert!(Shut.tree_admits(&[], 0, &mut t));
    Shut.reserve(&[], 0);
    // no tree, or no household: nothing
    assert!(lay_the_ways(
        &site,
        &houses,
        &mut AccessTree::new(7.0),
        &mut Open(9),
        &mut t
    )
    .drawn
    .iter()
    .all(Option::is_none));
    assert!(
        lay_the_ways(&site, &[], &mut AccessTree::new(7.0), &mut Open(9), &mut t)
            .drawn
            .is_empty()
    );
}

#[test]
fn the_tree_s_feet_and_junctions() {
    let segs = [
        ((0.0, 0.0), (10.0, 0.0)),
        ((10.0, 0.0), (20.0, 0.0)),
        ((5.0, 0.0), (5.0, 10.0)),
        ((3.0, 3.0), (3.0, 3.0)),
    ];
    assert_eq!(nearest_foot((7.0, 5.0), &segs[..2]), Some((7.0, 0.0)));
    assert_eq!(nearest_foot((3.0, 3.0), &segs[3..]), Some((3.0, 3.0)));
    assert!(nearest_foot((0.0, 0.0), &[]).is_none());
    let j = junction_points(&segs[..3]);
    assert!(j.contains(&(0.0, 0.0)) && j.contains(&(20.0, 0.0)) && !j.contains(&(10.0, 0.0)));
    assert_eq!(gathered_foot((1.0, 0.0), &j, 25.0), Some((0.0, 0.0)));
    assert!(gathered_foot((0.0, 0.0), &[(0.0, 0.0)], 25.0).is_none());
}
