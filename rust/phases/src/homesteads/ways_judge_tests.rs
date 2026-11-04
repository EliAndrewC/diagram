//! The households' judge's unit tests (feature 444 T30).
//!
//! Research:
//!     the judge's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::access::{parts_of, AccessTree};
use super::bundle::Bundle;
use super::gap_ways::{lay_the_ways, GapSite, Household, Judge};
use super::ground::Ground;
use super::standing::Standing;
use super::ways_judge::WaysJudge;
use super::wood::Shares;
use super::Counts;
use crate::field::fan::Pt;
use crate::law::ground::{rot_rect, House, LawGround};
use crate::law::meet::Destinations;
use crate::law::tree::Tree;
use crate::law::walk::Steading;

fn bundle(x: f64, y: f64) -> Bundle {
    let r = |dx: f64, dy: f64, w: f64, h: f64| (x + dx, y + dy, w, h);
    Bundle {
        house: r(0.0, 0.0, 40.0, 20.0),
        yard: r(0.0, 25.0, 30.0, 20.0),
        boxes: vec![r(0.0, 0.0, 40.0, 20.0), r(0.0, 25.0, 30.0, 20.0)],
        bbox: r(0.0, 12.5, 40.0, 45.0),
        ..Bundle::default()
    }
}

#[test]
fn each_household_is_laid_a_lawful_way_onto_the_track() {
    let mut t = Counts::default();
    let at = [(500.0, 500.0), (640.0, 500.0)];
    let bundles: Vec<Bundle> = at.iter().map(|&(x, y)| bundle(x, y)).collect();
    let house = |&(x, y): &Pt| House {
        quad: rot_rect(x, y, 40.0, 20.0, 0.0),
        at: (x, y),
        half_diag: 22.4,
    };
    let ground = LawGround {
        houses: at.iter().map(house).collect(),
        ..LawGround::default()
    };
    let d = Destinations {
        centers: at.to_vec(),
        ..Destinations::default()
    };
    let brook = vec![(0.0, 1500.0), (2000.0, 1500.0)];
    let waters = [(brook.clone(), 8.0)];
    let brooks = [brook];
    let root = vec![(0.0, 800.0), (2000.0, 800.0)];
    let mut tree = Tree::new(root.clone(), ground, d, &waters, &brooks);
    tree.steadings = at
        .iter()
        .map(|p| Steading {
            house: house(p),
            parts: vec![],
        })
        .collect();
    let mut free = Ground::new((0.0, 0.0), (2000.0, 2000.0), &mut t);
    free.fill_ring(
        &[
            (0.0, 1490.0),
            (1000.0, 1490.0),
            (1000.0, 1510.0),
            (0.0, 1510.0),
        ],
        &mut t,
    );
    let beyond = |_p: Pt| true;
    let wood = Shares::default();
    let boxes: Vec<_> = bundles.iter().map(|b| b.bbox).collect();
    let mut judge = WaysJudge {
        tree,
        parts: bundles.iter().map(parts_of).collect(),
        centers: at.to_vec(),
        standing: Standing::new(&free, &beyond, &wood, &boxes, (7.0, 25.0)),
    };
    let site = GapSite {
        ground: &free,
        beyond: &beyond,
        wood: &wood,
        canvas: (2000.0, 2000.0),
        lane_gap: 25.0,
    };
    let households: Vec<Household> = bundles
        .iter()
        .zip(&at)
        .map(|(b, &p)| Household {
            parts: parts_of(b),
            bbox: b.bbox,
            at: p,
        })
        .collect();
    let mut access = AccessTree::new(7.0);
    access.add(root[0], root[1]);
    let ways = lay_the_ways(&site, &households, &mut access, &mut judge, &mut t);
    assert!(ways.drawn.iter().all(Option::is_some));
    assert_eq!(judge.tree.lanes().len(), 2);
    // a leg across the brook squared and judged; a way the laying moves onto its own house refused
    assert!(judge.lawful_leg((100.0, 1400.0), (100.0, 1600.0), &mut t));
    // laid square on open ground: the tree's own question decides it
    let open = [(1480.0, 1450.0), (1520.0, 1560.0), (1520.0, 800.0)];
    let asked = judge.tree_admits(&open, 0, &mut t);
    assert_eq!(asked, judge.tree.admits(&open, (500.0, 500.0), &mut t));
    assert!(!judge.tree_admits(
        &[(480.0, 1450.0), (520.0, 1560.0), (520.0, 800.0)],
        0,
        &mut t
    ));
    assert!(!judge.tree_admits(
        &[
            (640.0, 525.0),
            (560.0, 1450.0),
            (600.0, 1600.0),
            (640.0, 800.0)
        ],
        1,
        &mut t
    ));
}
