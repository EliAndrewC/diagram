//! The router's unit tests (feature 444 T30).
//!
//! Research:
//!     the router's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::route::{
    clear_link, clear_runs, clip_to_clear, crosses_the_crop, ease_corner, length, link_survives,
    route, turn_deg, unjog, Ask, Crossing, Fouling, Ground, Grounds,
};
use crate::field::fan::Pt;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

const NONE: Grounds<'static> = Grounds {
    hard: &[],
    walls: &[],
    water: &[],
};

#[test]
fn the_index_fouls_inside_a_ring_within_its_margin_or_near_a_line() {
    let mut t = 0;
    let hard = [
        Ground::plain(square(0.0, 0.0, 10.0, 10.0)),
        Ground {
            ring: square(100.0, 0.0, 110.0, 10.0),
            gap: Some(1.0),
        },
        Ground::plain(Vec::new()),
        Ground::plain(square(-5000.0, 3000.0, 5000.0, 9000.0)),
    ];
    let idx = Fouling::new(
        &hard,
        5.0,
        &[square(50.0, 50.0, 60.0, 60.0)],
        2.0,
        &[((0.0, 200.0), (100.0, 200.0))],
        3.0,
    );
    assert!(idx.fouled((5.0, 5.0), &mut t) && idx.fouled((13.0, 5.0), &mut t));
    assert!(!idx.fouled((16.0, 5.0), &mut t));
    assert!(idx.fouled((110.5, 5.0), &mut t) && !idx.fouled((111.5, 5.0), &mut t));
    assert!(idx.fouled((61.0, 55.0), &mut t) && !idx.fouled((63.0, 55.0), &mut t));
    assert!(idx.fouled((50.0, 202.0), &mut t) && !idx.fouled((50.0, 204.0), &mut t));
    assert!(idx.fouled((0.0, 5000.0), &mut t));
    assert!(!Fouling::new(&[], 1.0, &[], 1.0, &[], 1.0).fouled((0.0, 0.0), &mut t));
    // a link clears where a run along it is long enough, decided early either way
    let wall = Fouling::new(
        &[Ground::plain(square(40.0, -5.0, 60.0, 5.0))],
        0.0,
        &[],
        0.0,
        &[],
        0.0,
    );
    assert!(link_survives((0.0, 0.0), (100.0, 0.0), &wall, 30.0, &mut t));
    assert!(!link_survives(
        (0.0, 0.0),
        (100.0, 0.0),
        &wall,
        60.0,
        &mut t
    ));
    assert!(link_survives((0.0, 0.0), (35.0, 0.0), &wall, 30.0, &mut t));
    assert!(link_survives(
        (55.0, 0.0),
        (100.0, 0.0),
        &wall,
        30.0,
        &mut t
    ));
    assert!(!link_survives((45.0, 0.0), (50.0, 0.0), &wall, 1.0, &mut t));
    assert!(!link_survives(
        (0.0, 0.0),
        (30.0, 0.0),
        &wall,
        100.0,
        &mut t
    ));
    assert!(!link_survives(
        (10.0, 0.0),
        (41.0, 0.0),
        &wall,
        50.0,
        &mut t
    ));
}

#[test]
fn runs_clips_links_and_touches_measure_what_the_ground_allows() {
    let mut t = 0;
    let wall = square(40.0, -5.0, 60.0, 5.0);
    let hard = [Ground::plain(wall.clone())];
    let idx = Fouling::new(&hard, 0.0, &[], 0.0, &[], 0.0);
    let runs = clear_runs(&[(0.0, 0.0), (100.0, 0.0)], &idx, 3.0, 10.0, &mut t);
    assert_eq!(runs.len(), 2);
    assert!(clear_runs(&[(45.0, 0.0), (55.0, 0.0)], &idx, 3.0, 1.0, &mut t).is_empty());
    // a clip stops before the wall, keeps the whole where it clears, and drops a stub
    assert_eq!(
        clip_to_clear(&[(0.0, 0.0), (10.0, 0.0)], &[], 1.0, &[], &mut t).len(),
        2
    );
    let far = clip_to_clear(
        &[(-100.0, 0.0), (0.0, 0.0), (100.0, 0.0)],
        &[wall.clone()],
        2.0,
        &[],
        &mut t,
    );
    assert!(far.last().is_some_and(|p| p.0 < 38.0) && length(&far) >= 70.0);
    assert!(clip_to_clear(
        &[(0.0, 0.0), (100.0, 0.0)],
        &[wall.clone()],
        2.0,
        &[],
        &mut t
    )
    .is_empty());
    assert_eq!(
        clip_to_clear(
            &[(0.0, 100.0), (100.0, 100.0)],
            &[],
            1.0,
            &[((50.0, 0.0), (50.0, 10.0))],
            &mut t
        )
        .len(),
        2
    );
    let g = Grounds {
        hard: &hard,
        walls: &[],
        water: &[],
    };
    assert!(g.clear_touch((0.0, 0.0), (0.5, 0.0), 7.0, &mut t));
    assert!(!g.clear_touch((0.0, 0.0), (100.0, 0.0), 7.0, &mut t));
    assert!(g.clear_touch((0.0, 50.0), (100.0, 50.0), 7.0, &mut t));
    let links = g.link_index(7.0);
    assert!(clear_link((0.0, 0.0), (0.5, 0.0), &links, &mut t));
    assert!(!clear_link((0.0, 0.0), (100.0, 0.0), &links, &mut t));
    assert!((turn_deg((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)) - 90.0).abs() < 1e-9);
    assert!(turn_deg((0.0, 0.0), (0.0, 0.0), (1.0, 1.0)).abs() < 1e-12);
    assert!(crosses_the_crop(
        (0.0, 0.0),
        (20.0, 0.0),
        &[Ground {
            ring: square(5.0, -5.0, 10.0, 5.0),
            gap: Some(1.0)
        }]
    ));
    assert!(!crosses_the_crop((0.0, 0.0), (20.0, 0.0), &hard));
}

#[test]
fn the_route_threads_round_a_wall_and_refuses_where_there_is_no_way() {
    let mut t = 0;
    let walls = [square(40.0, -60.0, 60.0, 60.0)];
    let g = Grounds {
        hard: &[],
        walls: &walls,
        water: &[],
    };
    let r = route((0.0, 0.0), (100.0, 0.0), &g, None, Ask::default(), &mut t);
    assert!(r.len() >= 3 && r[0] == (0.0, 0.0) && r[r.len() - 1] == (100.0, 0.0));
    let walled = g.link_index(7.0);
    assert!(r
        .windows(2)
        .all(|w| clear_link(w[0], w[1], &walled, &mut t)));
    // straight where nothing stands; a span under a foot as it is; a box past the budget, or a goal walled in, no route
    assert_eq!(
        route(
            (0.0, 0.0),
            (100.0, 0.0),
            &NONE,
            None,
            Ask::default(),
            &mut t
        ),
        vec![(0.0, 0.0), (100.0, 0.0)]
    );
    assert_eq!(
        route((0.0, 0.0), (0.5, 0.0), &NONE, None, Ask::default(), &mut t).len(),
        2
    );
    assert_eq!(
        route((0.0, 0.0), (3.0, 0.0), &NONE, None, Ask::default(), &mut t).len(),
        2
    );
    assert!(route(
        (0.0, 0.0),
        (5000.0, 0.0),
        &NONE,
        None,
        Ask::default(),
        &mut t
    )
    .is_empty());
    let pen = [
        square(70.0, -40.0, 130.0, -30.0),
        square(70.0, 30.0, 130.0, 40.0),
        square(70.0, -40.0, 80.0, 40.0),
        square(120.0, -40.0, 130.0, 40.0),
    ];
    let shut = Grounds {
        hard: &[],
        walls: &pen,
        water: &[],
    };
    assert!(route(
        (0.0, 0.0),
        (100.0, 0.0),
        &shut,
        None,
        Ask::default(),
        &mut t
    )
    .is_empty());
    // a crop the lattice would cut a corner of: no route
    let crop = [Ground {
        ring: vec![(30.0, -200.0), (70.0, -200.0), (70.0, 200.0), (30.0, 200.0)],
        gap: Some(0.0),
    }];
    let cropped = Grounds {
        hard: &crop,
        walls: &[],
        water: &[],
    };
    assert!(route(
        (0.0, 0.0),
        (100.0, 0.0),
        &cropped,
        None,
        Ask::default(),
        &mut t
    )
    .is_empty());
}

#[test]
fn a_brook_crossing_is_tolled_and_the_pull_takes_back_none() {
    let mut t = 0;
    let brook = [(-200.0, 50.0), (400.0, 50.0)];
    let x = Crossing::new(&brook, 10.0, 150.0, &mut t);
    assert!(x.in_band((0.0, 55.0), &mut t) && !x.in_band((0.0, 70.0), &mut t));
    assert!(!x.in_band((5000.0, 5000.0), &mut t));
    assert!(x.new_crossing(&[(0.0, 0.0), (0.0, 100.0)], 0, 1, &mut t));
    assert!(!x.new_crossing(&[(0.0, 0.0), (0.0, 55.0), (0.0, 100.0)], 0, 2, &mut t));
    assert!(!x.new_crossing(&[(0.0, 0.0), (100.0, 0.0)], 0, 1, &mut t));
    assert!(Crossing::new(&[], 10.0, 150.0, &mut t).cost == 0.0);
    // a way along the near bank stays there; one that must cross does
    let walls = [square(40.0, -60.0, 60.0, 30.0)];
    let g = Grounds {
        hard: &[],
        walls: &walls,
        water: &[],
    };
    let r = route(
        (0.0, 0.0),
        (100.0, 0.0),
        &g,
        Some(&x),
        Ask::default(),
        &mut t,
    );
    assert!(r.len() >= 3);
    let over = route(
        (0.0, 0.0),
        (0.0, 100.0),
        &NONE,
        Some(&x),
        Ask::default(),
        &mut t,
    );
    assert_eq!(over.len(), 2);
}

#[test]
fn the_jogs_are_chorded_kneed_or_eased_where_the_chord_is_blocked() {
    let mut t = 0;
    // a hairpin on open ground: chorded
    let hp = unjog(vec![(0.0, 0.0), (50.0, 0.0), (0.0, 5.0)], &NONE, &mut t);
    assert_eq!(hp, vec![(0.0, 0.0), (0.0, 5.0)]);
    // a zigzag on open ground: chorded
    let zz = unjog(
        vec![(0.0, 0.0), (50.0, 0.0), (50.0, 20.0), (100.0, 20.0)],
        &NONE,
        &mut t,
    );
    assert_eq!(zz, vec![(0.0, 0.0), (100.0, 20.0)]);
    // a zigzag whose chord is blocked but its knee clears
    let block = [square(45.0, 4.0, 55.0, 12.0)];
    let g = Grounds {
        hard: &[],
        walls: &block,
        water: &[],
    };
    let kneed = unjog(
        vec![(0.0, -30.0), (50.0, -30.0), (50.0, -10.0), (100.0, -10.0)],
        &g,
        &mut t,
    );
    assert!(kneed.len() <= 4);
    let knee = [square(20.0, 0.0, 80.0, 6.0)];
    let gk = Grounds {
        hard: &[],
        walls: &knee,
        water: &[],
    };
    let k2 = unjog(
        vec![(0.0, -20.0), (50.0, -20.0), (50.0, 20.0), (100.0, 20.0)],
        &gk,
        &mut t,
    );
    assert!(k2.len() >= 2);
    let z3 = unjog(
        vec![(0.0, -12.0), (60.0, -12.0), (40.0, 30.0), (100.0, 30.0)],
        &gk,
        &mut t,
    );
    assert!(z3.len() >= 2);
    // a hairpin round a wall: its corner eased off the apex, or left
    let hw = [square(-5.0, 2.0, 60.0, 4.0)];
    let gh = Grounds {
        hard: &[],
        walls: &hw,
        water: &[],
    };
    let eased = unjog(vec![(0.0, 0.0), (80.0, 3.0), (0.0, 6.0)], &gh, &mut t);
    assert!(eased.len() == 3);
    let box_in = [
        square(-200.0, -200.0, 200.0, -1.0),
        square(-200.0, 7.0, 200.0, 200.0),
        square(-5.0, 2.0, 60.0, 4.0),
    ];
    let gb = Grounds {
        hard: &[],
        walls: &box_in,
        water: &[],
    };
    let left = unjog(vec![(0.0, 0.0), (80.0, 3.0), (0.0, 6.0)], &gb, &mut t);
    assert_eq!(left.len(), 3);
    assert!(ease_corner((0.0, 0.0), (5.0, 5.0), (0.5, 0.0), &NONE, &mut t).is_none());
    assert!(ease_corner((0.0, 0.0), (5.0, -5.0), (10.0, 0.0), &NONE, &mut t).is_some());
    assert!(ease_corner((0.0, 0.0), (1.0, 50.0), (2.0, 0.0), &NONE, &mut t).is_none());
}

#[test]
fn the_rarer_turns_of_the_search_the_pull_and_the_jogs() {
    let mut t = 0;
    // a run that meets the wall exactly at its need
    let wall = Fouling::new(
        &[Ground::plain(square(40.5, -5.0, 60.0, 5.0))],
        0.0,
        &[],
        0.0,
        &[],
        0.0,
    );
    assert!(link_survives((0.0, 0.0), (99.0, 0.0), &wall, 39.0, &mut t));
    // a start in the brook's band, the goal along it: a cell first reached over the toll is reached again cheaper
    let x = Crossing::new(&[(-200.0, 50.0), (600.0, 50.0)], 10.0, 150.0, &mut t);
    assert!(
        route(
            (0.0, 50.0),
            (300.0, 50.0),
            &NONE,
            Some(&x),
            Ask::default(),
            &mut t
        )
        .len()
            >= 2
    );
    // pegs at four lattice points: a cell reached once is reached again cheaper, and its first entry is passed over
    let pegs: Vec<Ground> = [(0.0, -20.0), (10.0, 0.0), (40.0, -40.0), (40.0, -10.0)]
        .iter()
        .map(|&(x, y)| Ground {
            ring: square(x - 1.0, y - 1.0, x + 1.0, y + 1.0),
            gap: Some(0.0),
        })
        .collect();
    let pegged = Grounds {
        hard: &pegs,
        walls: &[],
        water: &[],
    };
    let _ = route(
        (0.0, 0.0),
        (60.0, 0.0),
        &pegged,
        None,
        Ask::default(),
        &mut t,
    );
    // a crop strip thinner than the lattice: every long link fails on it and the one step left crosses it
    let strip = [Ground {
        ring: square(-1000.0, 2.5, 1000.0, 3.5),
        gap: Some(0.0),
    }];
    let thin = Grounds {
        hard: &strip,
        walls: &[],
        water: &[],
    };
    assert!(route(
        (0.0, 0.0),
        (0.0, 100.0),
        &thin,
        None,
        Ask::default(),
        &mut t
    )
    .is_empty());
    // a hairpin whose chord a small wall blocks: its corner eased
    let peg = [square(-1.0, 9.0, 1.0, 11.0)];
    let gp = Grounds {
        hard: &[],
        walls: &peg,
        water: &[],
    };
    let eased = unjog(vec![(0.0, 0.0), (200.0, 10.0), (0.0, 20.0)], &gp, &mut t);
    assert!(eased.len() == 3 && eased[1].0 < 30.0 && eased[1].0 > 0.0);
    // a zigzag whose chord is blocked and its knee clear: kneed
    let low = [square(40.5, 7.4, 41.5, 8.4)];
    let gl = Grounds {
        hard: &[],
        walls: &low,
        water: &[],
    };
    let kneed = unjog(
        vec![(0.0, 0.0), (50.0, 0.0), (32.0, 34.0), (100.0, 34.0)],
        &gl,
        &mut t,
    );
    assert_eq!(kneed, vec![(0.0, 0.0), (41.0, 17.0), (100.0, 34.0)]);
    // and with the knee blocked too: eased
    let mid = [square(38.0, 10.0, 46.0, 18.0)];
    let gm = Grounds {
        hard: &[],
        walls: &mid,
        water: &[],
    };
    let z = unjog(
        vec![(0.0, 0.0), (50.0, 0.0), (32.0, 34.0), (100.0, 34.0)],
        &gm,
        &mut t,
    );
    assert_eq!(z.len(), 3);
    assert!(z[1].1 < 17.0);
}
