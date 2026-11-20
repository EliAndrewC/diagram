//! The waterward fringe's unit tests (feature 444 T29).
//!
//! Research:
//!     the fringe's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::{face, flanks, fringe};

fn ring(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<(f64, f64)> {
    let mut out = Vec::new();
    for k in 0..=20 {
        let t = f64::from(k) / 20.0;
        out.push((x0 + (x1 - x0) * t, y0));
        out.push((x1, y0 + (y1 - y0) * t));
        out.push((x1 - (x1 - x0) * t, y1));
        out.push((x0, y1 - (y1 - y0) * t));
    }
    out
}

#[test]
fn the_foot_and_the_cross_flanks_the_village_does_not_stand_on() {
    // the land falls south: the head north, the foot south, the cross flanks west and east
    assert_eq!(flanks((0.0, 1.0), None), vec!['W', 'E', 'S']);
    // the village on the east flank
    assert_eq!(flanks((0.0, 1.0), Some((1.0, 0.0))), vec!['W', 'S']);
    // falling west, the village on the north
    assert_eq!(flanks((-1.0, 0.0), Some((0.0, -1.0))), vec!['S', 'W']);
}

#[test]
fn the_strip_follows_the_dike_s_outer_face_and_steps_in_at_a_notch() {
    let dike = ring(1000.0, 1000.0, 2000.0, 2000.0);
    let mut t = 0;
    // the outermost face of the west half, a run at one face its ends only
    let west = face(&dike, 'W', 970.0, 2020.0, 0.0, &[], 15.0, &mut t);
    assert!(west.iter().all(|p| (p.0 - 1000.0).abs() < 1e-9) && west.len() < 32);
    // stepped in through the notch, toward the field, on either side
    let notched = face(
        &dike,
        'W',
        970.0,
        2020.0,
        20.0,
        &[(1000.0, 1500.0)],
        15.0,
        &mut t,
    );
    assert!(notched.iter().any(|p| (p.0 - 1020.0).abs() < 1e-9));
    let east = face(
        &dike,
        'E',
        970.0,
        2020.0,
        20.0,
        &[(2000.0, 1500.0)],
        15.0,
        &mut t,
    );
    assert!(east.iter().any(|p| (p.0 - 1980.0).abs() < 1e-9));
    let north = face(&dike, 'N', 970.0, 2020.0, 0.0, &[], 15.0, &mut t);
    let south = face(&dike, 'S', 970.0, 2020.0, 0.0, &[], 15.0, &mut t);
    assert!(
        north.iter().all(|p| (p.1 - 1000.0).abs() < 1e-9)
            && south.iter().all(|p| (p.1 - 2000.0).abs() < 1e-9)
    );
    // a span past the ring keeps the extreme in the bins the ring does not reach
    let wide = face(&dike, 'W', 0.0, 3000.0, 0.0, &[], 15.0, &mut t);
    assert!(wide.iter().all(|p| (p.0 - 1000.0).abs() < 1e-9));
}

#[test]
fn a_polder_s_strips_run_off_toward_the_frame_and_none_without_a_dike() {
    let dike = (
        ring(1000.0, 1000.0, 2000.0, 2000.0),
        vec![(1000.0, 1500.0), (1500.0, 2000.0)],
    );
    let f = fringe(
        &[dike],
        20.0,
        15.0,
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    assert_eq!(f.flanks, vec!['W', 'S']);
    // each strip 280 ft deep off its face
    assert!(
        f.strips.len() == 2
            && (f.strips[0][0].0 - 720.0).abs() < 1e-9
            && (f.strips[1][0].1 - 2280.0).abs() < 1e-9
    );
    #[cfg(feature = "counters")] // a count, kept by the counting build alone (FR-012)
    assert!(f.counts["write@strip"] > 0);
    // EVERY LOOP COUNTED (feature 449 T226, rubric S5): the ring's 84 points, a notch on each of the two flanks. Each face reads the
    // ring three times (its coordinates, their extremes, its bins: 3 x 84) and asks its one notch of each of the 32 bins (32), folds
    // the 43 points on its own half for each bin's outermost, and walks its 32 bins three times more (the filled bins, the values,
    // the runs); the fringe boxes the ring (84) and files each notch against the four flanks (2 x 4); the three flanks asked of the
    // seat's side. Before T226 the folds, the bins' walks, the box, the filing and the flanks went uncounted: test@face read 568.
    #[cfg(feature = "counters")]
    assert_eq!(
        (
            f.counts.get("test@face"),
            f.counts.get("test@fringe"),
            f.counts.get("test@flanks")
        ),
        (
            Some(&(2 * (3 * 84 + 32 + 43 + 3 * 32))),
            Some(&(84 + 2 * 4)),
            Some(&3)
        )
    );
    // held to 20 ft off the frame
    let tight = fringe(
        &[(
            ring(100.0, 100.0, 2900.0, 2900.0),
            vec![(2900.0, 500.0), (500.0, 100.0)],
        )],
        20.0,
        15.0,
        280.0,
        (3000.0, 3000.0),
        (0.0, -1.0),
        None,
    );
    assert!(tight
        .strips
        .iter()
        .flatten()
        .all(|p| p.0 >= -20.0 && p.0 <= 3020.0 && p.1 >= -20.0 && p.1 <= 3020.0));
    assert!(
        fringe(&[], 20.0, 15.0, 280.0, (3000.0, 3000.0), (0.0, 1.0), None)
            .strips
            .is_empty()
    );
}
