//! The polder's tests: the block's shape and plots, a dike-pond's creeks (their width, their place between the banks, the drift
//! eased to give them room), the resting plots and the outfall.
//!
//! Research:
//!     the polder's tests - NONE: fixtures and assertions; each rule's claim is at the unit it tests

use super::{outfall, polder, rest, shape, MODULE_FT};
use crate::field::geom::{inside, seg_dist, signed_area};

#[test]
fn the_shape_wastes_least() {
    assert_eq!(shape(24, 1.0), (6, 4));
    let (r, c) = shape(34, 0.5);
    assert!(r * c >= 34 && r * c - 34 < c);
    assert_eq!(shape(1, 0.0), (1, 1));
}

#[test]
fn a_rice_polder_and_a_dike_pond_block() {
    let paddy = 15.0 * 1.3 * 43_560.0;
    for (dikepond, layout) in [(false, "mosaic"), (true, "mosaic"), (true, "chessboard")] {
        let p = polder(paddy, dikepond, layout, 90.0, (3200.0, 3200.0), 1.0, 4);
        let area: f64 = p.plots.iter().map(|x| signed_area(&x.ring).abs()).sum();
        assert!(area >= paddy * 0.8, "{area} for {paddy}");
        assert!(p
            .plots
            .iter()
            .all(|x| x.ring.len() == 4 || x.ring.len() == 6));
        assert!(p.plots.iter().any(|x| x.low));
        #[expect(clippy::cast_precision_loss, reason = "a parcel's few corners")]
        let center = |r: &[(f64, f64)]| {
            (
                r.iter().map(|q| q.0).sum::<f64>() / r.len() as f64,
                r.iter().map(|q| q.1).sum::<f64>() / r.len() as f64,
            )
        };
        assert!(p
            .plots
            .iter()
            .all(|x| inside(center(&x.ring), &p.inner_env)));
        assert!(!inside(p.pond.0, &p.inner_env));
        assert!(
            p.fringe.len() == 16
                && p.fringe
                    .iter()
                    .all(|q| (q.0 - p.pond.0 .0).abs() <= 82.0 + 40.0 + 1e-9)
        );
        assert!(p.ditches.len() >= 4 && p.feeder.len() == 3);
        if dikepond {
            let paired = p
                .plots
                .iter()
                .filter(|x| signed_area(&x.ring).abs() > MODULE_FT.1 * MODULE_FT.1 * 1.5)
                .count();
            if layout == "mosaic" {
                assert!(paired * 2 > p.plots.len());
            } else {
                // the chessboard's ponds are its squares, never paired
                assert_eq!(paired, 0);
            }
        } else {
            assert!(p.plots.len() > p.shape.0 * p.shape.1);
        }
    }
    let p = polder(paddy, false, "mosaic", 90.0, (3200.0, 3200.0), 1.0, 4);
    assert!(rest(&p.plots, 4, false).is_empty() && rest(&[], 4, true).is_empty());
    for seed in 0..10 {
        let r = rest(&p.plots, seed, true);
        assert!((1..=4).contains(&r.len()));
        for (k, &i) in r.iter().enumerate() {
            for &j in &r[k + 1..] {
                let (a, b) = (&p.plots[i], &p.plots[j]);
                assert!(a.col != b.col || a.row > b.row + b.span || b.row > a.row + a.span);
            }
        }
    }
    // the outfall runs down the fall off the canvas, whichever way the fall
    for (deg, canvas) in [
        (90.0, (6400.0, 6400.0)),
        (0.0, (6400.0, 6400.0)),
        (180.0, (6400.0, 6400.0)),
        (270.0, (6400.0, 6400.0)),
        (45.0, (6400.0, 6400.0)),
    ] {
        let run = outfall((3200.0, 3300.0), deg, canvas);
        let end = run[run.len() - 1];
        assert_eq!(run.len(), 3, "two turns of 45 degrees onto the fall");
        assert!(end.0 < 0.0 || end.1 < 0.0 || end.0 > canvas.0 || end.1 > canvas.1);
    }
    let flat = polder(paddy, true, "chessboard", 90.0, (0.0, 0.0), 1.0, 4);
    let warped = polder(paddy, true, "mosaic", 90.0, (0.0, 0.0), 1.0, 4);
    assert_ne!(flat.plots, warped.plots, "the mosaic bends the lattice");
}

/// A CREEK HAS ROOM BETWEEN ITS BANKS (449 T420): over forty rolled blocks, mosaic and chessboard, no creek's water reaches
/// more than the page's foot and a half or so over a parcel's edge (0018's drawing page: a canal may graze the edge of a
/// bank) - each creek midway between the sides it runs between, and a mosaic whose drift would pinch a corridor under its
/// creek's width eased until none is, the others and every chessboard keeping the whole; each creek's rounded end stops at
/// the ring canal's middle line, inside the dike's foot.
#[test]
fn a_creek_stands_midway_between_its_banks_and_a_pinched_mosaic_is_eased() {
    let paddy = 15.0 * 1.3 * 43_560.0;
    let (mut eased, mut whole) = (0, 0);
    for seed in 1..=40 {
        for layout in ["mosaic", "chessboard"] {
            let p = polder(paddy, true, layout, 90.0, (3200.0, 3200.0), 1.0, seed);
            assert!(p.ease > 0.0 && p.ease <= 1.0 && p.corridor_tests > 0);
            if layout == "chessboard" {
                assert!((p.ease - 1.0).abs() < 1e-12, "a chessboard keeps the whole");
            } else if p.ease < 1.0 {
                eased += 1;
            } else {
                whole += 1;
            }
            for d in p
                .ditches
                .iter()
                .filter(|d| d.seg == "column" || d.seg == "row")
            {
                for &q in &d.pts {
                    let near = p
                        .plots
                        .iter()
                        .flat_map(|x| {
                            (0..x.ring.len()).map(move |i| {
                                seg_dist(q, x.ring[i], x.ring[(i + 1) % x.ring.len()])
                            })
                        })
                        .fold(f64::INFINITY, f64::min);
                    let (kind, w) = (d.seg, d.w);
                    let said = format!("{layout} seed {seed}: a {kind} creek {w:.1} ft wide stands {near:.2} ft off a parcel's edge");
                    assert!(near >= w / 2.0 - 1.5, "{said}");
                    assert!(p.plots.iter().all(|x| !inside(q, &x.ring)));
                    assert!(inside(q, &p.inner_env), "inside the dike's foot");
                }
                let (head, tail) = (d.pts[0], d.pts[d.pts.len() - 1]);
                let ring = &p.ditches[..4];
                let to_ring = |q: (f64, f64)| {
                    ring.iter()
                        .map(|t| seg_dist(q, t.pts[0], t.pts[1]))
                        .fold(f64::INFINITY, f64::min)
                };
                if d.seg == "column" {
                    // the rounded end, half the width long, reaches the ring canal's middle line and no farther
                    assert!((to_ring(head) - d.w / 2.0).abs() < 1.5);
                    assert!((to_ring(tail) - d.w / 2.0).abs() < 1.5);
                }
            }
        }
    }
    assert!(eased > 0 && whole > eased, "{eased} eased, {whole} whole");
}

/// A DIKE-POND'S CHANNELS ARE CREEKS, A RICE POLDER'S DITCHES (449 T420): the channels between a dike-pond block's ponds, down
/// its columns and across its rows, are each 6 to 8 ft wide (0018's drawing page), one width the block over, where they took
/// the rice polder's delivery rung, 1.2 to 2.5 ft down a column and 0.75 of it across a row; a rice polder's column ditches
/// keep that rung and it has no row channels; the ring canal's four trunks are 0068's on the rice polder, and on a dike-pond block
/// each reach is the larger of its rung and the creek's width (449 T427: the next test).
#[test]
fn a_dike_ponds_channels_are_creeks_and_a_rice_polders_stay_ditches() {
    let paddy = 15.0 * 1.3 * 43_560.0;
    let trunks = |p: &super::Polder| -> Vec<(f64, f64)> {
        p.ditches[..4].iter().map(|d| (d.w, d.w_tail)).collect()
    };
    let ladder: Vec<(f64, f64)> = vec![(4.5, 1.5), (1.5, 1.5), (4.0, 1.5), (1.2, 5.5)];
    let mut widths = Vec::new();
    for (layout, seed) in [
        ("mosaic", 4),
        ("chessboard", 4),
        ("mosaic", 21),
        ("mosaic", 7),
    ] {
        let p = polder(paddy, true, layout, 90.0, (3200.0, 3200.0), 1.0, seed);
        let between: Vec<_> = p
            .ditches
            .iter()
            .filter(|d| d.seg == "column" || d.seg == "row")
            .collect();
        assert!(between.iter().any(|d| d.seg == "column"));
        assert!(between.iter().any(|d| d.seg == "row"));
        let found: Vec<(f64, f64)> = between.iter().map(|d| (d.w, d.w_tail)).collect();
        let creeks = found
            .iter()
            .all(|&(w, tail)| (6.0..=8.0).contains(&w) && (w - tail).abs() < 1e-9);
        let said =
            format!("{layout} seed {seed}: a creek 6 to 8 ft wide, head to tail - found {found:?}");
        assert!(creeks, "{said}");
        let one = found.iter().all(|&x| (x.0 - found[0].0).abs() < 1e-12);
        assert!(one, "one width a block");
        let wider: Vec<(f64, f64)> = ladder
            .iter()
            .map(|&(w, t)| (w.max(found[0].0), t.max(found[0].0)))
            .collect();
        assert_eq!(trunks(&p), wider);
        widths.push(found[0].0);
    }
    let same = (widths[0] - widths[1]).abs() < 1e-12;
    assert!(same, "the width is the seed's, not the layout's");
    let rolled = widths.iter().any(|&w| (w - widths[0]).abs() > 1e-9);
    assert!(rolled, "rolled block by block");
    let rice = polder(paddy, false, "mosaic", 90.0, (3200.0, 3200.0), 1.0, 4);
    assert!((rice.ease - 1.0).abs() < 1e-12 && rice.corridor_tests == 0);
    assert_eq!(trunks(&rice), ladder);
    assert!(rice.ditches.iter().all(|d| d.seg != "row"));
    let columns: Vec<_> = rice.ditches.iter().filter(|d| d.seg == "column").collect();
    assert!(!columns.is_empty());
    assert!(columns
        .iter()
        .all(|d| d.w <= 2.5 && d.w_tail <= 1.2 && d.w >= d.w_tail));
}

#[test]
fn a_dike_pond_ring_canal_is_no_narrower_than_its_creeks_and_a_rice_polders_keeps_its_rungs() {
    let paddy = 15.0 * 1.3 * 43_560.0;
    let trunks = ["feeder", "w_toe", "e_toe", "drain"];
    for seed in 1..=12 {
        for (dikepond, layout) in [(false, "mosaic"), (true, "mosaic"), (true, "chessboard")] {
            let p = polder(paddy, dikepond, layout, 90.0, (3200.0, 3200.0), 1.0, seed);
            let ring: Vec<_> = p
                .ditches
                .iter()
                .filter(|d| trunks.contains(&d.seg))
                .collect();
            assert_eq!(ring.len(), 4);
            let widths: Vec<(f64, f64)> = ring.iter().map(|d| (d.w, d.w_tail)).collect();
            if !dikepond {
                // 0068's ladder, untouched: the supply's two arms, the far flank's lateral, the drain
                assert_eq!(widths, [(4.5, 1.5), (1.5, 1.5), (4.0, 1.5), (1.2, 5.5)]);
                continue;
            }
            let creek = p.ditches.iter().find(|d| d.seg == "column").unwrap().w;
            assert!((6.0..=8.0).contains(&creek));
            for (d, &(w, tail)) in ring.iter().zip(&widths) {
                // every reach of the ring at least the creek's width, never below its rice rung
                let seg = d.seg;
                let said = format!("{layout} seed {seed}: the ring's {seg} drawn {w:.2} to {tail:.2} ft against a {creek:.2} ft creek");
                assert!(w.min(tail) >= creek - 1e-9, "{said}");
            }
            // the joins through the sluices carry their trunk's width at the corner
            let join = |seg: &str| p.ditches.iter().find(|d| d.seg == seg).unwrap().w;
            assert!(join("inlet_join") >= creek - 1e-9 && join("outfall_join") >= creek - 1e-9);
            // a creek's rounded mouth on the ring's middle line stays inside the ring's water
            for c in p.ditches.iter().filter(|d| d.seg == "column") {
                for end in [c.pts[0], c.pts[c.pts.len() - 1]] {
                    let (near, tw) = ring
                        .iter()
                        .map(|t| (seg_dist(end, t.pts[0], t.pts[1]), t.w.max(t.w_tail)))
                        .fold((f64::INFINITY, 0.0), |a, b| if b.0 < a.0 { b } else { a });
                    assert!(c.w / 2.0 - near <= tw / 2.0 + 1e-6);
                }
            }
        }
    }
}
