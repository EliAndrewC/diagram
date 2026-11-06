//! The appurtenances' seats tested on small hand-laid hamlets.

use super::farm_water::{crosses_other_water, cross_t, dooryard_end, farm_channels, source_points, Farm, Ground};
use super::wells::{cluster_seats, groups, row_well_seats, verge_seats, Cluster, House, RowWells};
use crate::counts::Counts;
use crate::field::geom::dist;

const RUNGS: &[(f64, usize)] = &[(190.0, 5), (300.0, 5), (520.0, 5), (760.0, 5), (520.0, 3), (520.0, 2)];

/// A street of houses 100 ft apart, two rows 120 ft apart, each house 46 by 28 ft.
fn rows(n: usize) -> Vec<House> {
    (0..n).map(|i| ((i / 2) as f64 * 100.0, (i % 2) as f64 * 120.0, 46.0, 28.0, 0.0)).collect()
}

#[test]
fn the_houses_are_halved_along_the_longer_side_at_the_median() {
    let pts: Vec<_> = rows(12).iter().map(|h| (h.0, h.1)).collect();
    let mut t = Counts::default();
    let g = groups(&pts, 2, &mut t);
    assert_eq!(g.len(), 2);
    assert_eq!(g[0].len() + g[1].len(), 12);
    let max0 = g[0].iter().map(|&i| pts[i].0).fold(f64::MIN, f64::max);
    let min1 = g[1].iter().map(|&i| pts[i].0).fold(f64::MAX, f64::min);
    assert!(max0 <= min1, "cut across the street's length: {g:?}");
    assert_eq!(groups(&pts, 1, &mut t).len(), 1);
    assert_eq!(groups(&pts[..1], 3, &mut t).len(), 1, "one house is never halved");
}

#[test]
fn a_cluster_seat_stands_between_houses_within_the_gap_of_a_wall_and_off_every_house() {
    let houses = rows(12);
    let needy = vec![true; 12];
    let c = Cluster { houses: &houses, needy: &needy, want: 2, rungs: RUNGS, gap: 80.0 };
    let mut t = Counts::default();
    let got = cluster_seats(&c, &mut t);
    assert_eq!(got.len(), 2);
    for g in &got {
        assert!(!g.is_empty());
        for &p in g {
            let walls = houses
                .iter()
                .map(|h| {
                    let (dx, dy) = ((p.0 - h.0).abs() - h.2 / 2.0, (p.1 - h.1).abs() - h.3 / 2.0);
                    dx.max(0.0).hypot(dy.max(0.0))
                })
                .fold(f64::INFINITY, f64::min);
            assert!(walls > 0.0 && walls <= 80.0 + 1e-9, "{p:?} is {walls} ft off a wall");
        }
    }
    // ...the first seat of each group nearest its own houses' middle, so the two wells stand apart
    assert!(dist(got[0][0], got[1][0]) > 150.0, "{:?} {:?}", got[0][0], got[1][0]);
    assert!(t.0.contains_key("candidate@cluster_pairs"));
}

#[test]
fn a_household_watered_by_open_water_owes_no_group_and_none_owing_serves_them_all() {
    let houses = rows(6);
    let mut needy = vec![false; 6];
    needy[0] = true;
    let c = Cluster { houses: &houses, needy: &needy, want: 1, rungs: RUNGS, gap: 80.0 };
    let mut t = Counts::default();
    let one = cluster_seats(&c, &mut t);
    assert_eq!(one.len(), 1);
    assert!(!one[0].is_empty(), "a group of one house seats a step off its walls");
    let none = vec![false; 6];
    let all = cluster_seats(&Cluster { needy: &none, ..c }, &mut t);
    assert!(!all[0].is_empty());
}

#[test]
fn a_seat_on_no_rung_is_not_offered() {
    let houses = vec![(0.0, 0.0, 46.0, 28.0, 0.0), (5000.0, 0.0, 46.0, 28.0, 0.0)];
    let needy = vec![true; 2];
    let c = Cluster { houses: &houses, needy: &needy, want: 1, rungs: RUNGS, gap: 80.0 };
    let mut t = Counts::default();
    assert!(cluster_seats(&c, &mut t)[0].is_empty(), "two houses a mile apart share no seat");
}

#[test]
fn the_verge_seats_stand_either_side_of_the_track() {
    let houses = rows(8);
    let needy = vec![true; 8];
    let c = Cluster { houses: &houses, needy: &needy, want: 1, rungs: RUNGS, gap: 80.0 };
    let track = vec![(-50.0, 60.0), (400.0, 60.0)];
    let mut t = Counts::default();
    let got = verge_seats(&c, &track, (10.0, 11.0), &mut t);
    assert_eq!(got.len(), 1);
    assert!(!got[0].is_empty());
    assert!(got[0].iter().all(|p| (p.1 - 60.0).abs() > 9.0 && (p.1 - 60.0).abs() < 11.0));
}

#[test]
fn a_row_shares_a_well_at_each_stretch_off_its_bends() {
    let street = vec![(0.0, 0.0), (2000.0, 0.0)];
    let farms: Vec<_> = (0..20).map(|i| (f64::from(i) * 100.0, 40.0)).collect();
    let r = RowWells { streets: &[street], farms: &farms, frame: 240.0, reach: 760.0, off: 20.0, bend: (40.0, 30.0) };
    let mut t = Counts::default();
    let marks = row_well_seats(&r, &mut t);
    assert_eq!(marks.len(), 2, "1,900 ft of row at 1.6 reaches a stretch: two");
    assert_eq!(marks[0].len(), 10, "five marks, either side");
    assert!((marks[0][0].1 - 20.0).abs() < 1e-9 && (marks[0][1].1 + 20.0).abs() < 1e-9);
    let bent = vec![(0.0, 0.0), (950.0, 0.0), (950.0, 1000.0)];
    let farms2: Vec<_> = [(500.0, 30.0), (940.0, 30.0), (960.0, 500.0)].to_vec();
    let r2 = RowWells { streets: &[bent], farms: &farms2, ..r };
    let m2 = row_well_seats(&r2, &mut t);
    assert!(m2.iter().all(|m| m.len() <= 10));
}

#[test]
fn the_sources_are_nearest_first_and_include_each_course_s_nearest_point() {
    let mut t = Counts::default();
    let pts = source_points(&[vec![(0.0, 0.0), (100.0, 0.0)]], (37.0, 30.0), 20.0, 3, 0.0, &mut t);
    assert_eq!(pts[0], (37.0, 0.0), "the course's own nearest point comes first");
    assert!(pts.len() == 3 && (0..2).all(|i| dist(pts[i], (37.0, 30.0)) <= dist(pts[i + 1], (37.0, 30.0))));
}

#[test]
fn the_dooryard_end_is_a_step_off_the_yard_toward_the_water() {
    let yard = [(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0)];
    let e = dooryard_end(&yard, (20.0, 200.0), 6.0);
    assert!(e.1 > 30.0 && (e.1 - 36.0).abs() < 1.0 && (e.0 - 20.0).abs() < 1.0, "{e:?}");
}

#[test]
fn a_channel_crosses_no_water_but_at_its_own_mouth() {
    let mut t = Counts::default();
    let water = [((-10.0, 0.0), (10.0, 0.0))];
    assert!(!crosses_other_water(&[(0.0, -2.0), (0.0, 100.0)], &water, 6.0, &mut t), "2 ft from the start is its mouth");
    assert!(crosses_other_water(&[(0.0, -50.0), (0.0, 100.0)], &water, 6.0, &mut t), "50 ft along is another water");
    assert!((cross_t((0.0, 0.0), (1.0, 0.0), (0.5, -1.0), (0.5, 1.0)) - 0.5).abs() < 1e-12);
    assert!(cross_t((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)).abs() < 1e-12, "parallel lines meet nowhere");
}

#[test]
fn a_farm_takes_a_channel_off_the_nearest_ditch_and_a_later_one_may_take_it_off_the_first() {
    let yard = |x: f64, y: f64| vec![(x - 20.0, y - 10.0), (x + 20.0, y - 10.0), (x + 20.0, y + 10.0), (x - 20.0, y + 10.0)];
    let farms = [
        Farm { at: (400.0, 300.0), yard: yard(400.0, 350.0), own: vec![] },
        Farm { at: (600.0, 300.0), yard: yard(600.0, 350.0), own: vec![] },
        Farm { at: (900.0, 900.0), yard: vec![], own: vec![] },
    ];
    let courses = [vec![(100.0, 500.0), (500.0, 500.0)]];
    let g = Ground { hard: &[], walls: &[], courses: &courses, water: &[] };
    let mut t = Counts::default();
    let got = farm_channels(&farms, &g, &mut t);
    assert!(got[0].len() >= 2 && (got[0][0].1 - 500.0).abs() < 1.0, "led off the ditch: {:?}", got[0]);
    assert!(got[0][got[0].len() - 1].1 > 360.0 && got[0][got[0].len() - 1].1 < 375.0, "a step off the yard");
    assert!(got[1].len() >= 2, "the second farm reached too");
    assert!(got[2].is_empty(), "a farm with no yard is left to its well");
    let none = Ground { courses: &[], ..g };
    assert!(farm_channels(&farms, &none, &mut t).iter().all(Vec::is_empty), "no water to lead it off");
}
