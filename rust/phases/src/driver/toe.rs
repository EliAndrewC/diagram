//! What the seat is handed that the deleted Python derived (feature 444 T42; `t42-brief.md` section 3, stage 4a): the wet toe
//! below the fields (`toe_band`), and a ring grown outward by the lane's width (`wet_grown_by_the_lane`).
//!
//! Research:
//!     toe band edge - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: 90 ft above the local lowest field between the fields' lower corners, smoothed over three stations
//!     toe band width - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: the paddy fan's foot, corner to corner, plus 90 ft each side
//!     stops at the lower corners - research/questions/0057-marshes-and-wetlands-shitchi.html: a fan's springs come out at its toe and its sides are among the land cleared early, so the wet ground stops at the fields' lower corners and does not climb a side that narrows downhill
//!     flaring flanks - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: part of the straight-band deviation, the band's ends bow outward downhill as seepage spreads

use std::collections::HashMap;

use crate::field::fan::Pt;
use crate::seat::tally;

/// The toe band's pad: its edge above the lowest field, and its margin past the fields each side (ft).
///
/// Research:
///     toe band edge - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: 90 ft above the local lowest field
///     toe band width - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: as wide as the fields' foot plus 90 ft each side
pub const PAD: f64 = 90.0;
/// The bleed past the canvas edge (ft).
///
/// Research:
///     its bleed - CONVENTION: 120 ft past the canvas edge, sizes on the sheet, not in the world
const BLEED: f64 = 120.0;

/// The reed-marsh toe: the wet band below the fields, laid across the fall, its inner edge `PAD` above the local lowest field
/// point at each cross-slope station (smoothed over three), across the fields' foot from one lower corner to the other plus `PAD`
/// each side, its edge past a corner at that corner's own level, its ends flaring downhill and off the canvas - the deleted
/// `toe_band`, read from the fields' rings. `foot`, the fields' two lower corners (a comb's fan), stops it there: before 449 T432
/// each station past a corner of a fan narrowing downhill found its lowest field up the side, and the band climbed the whole
/// side. With none (a polder's ring) the band spans the rings and reads each station's lowest point, as before.
///
/// Research:
///     toe band edge - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: the inner edge `PAD` above the local lowest field within a pad each way, smoothed over three stations, between the fields' lower corners - where the foot runs slantwise across the fall the edge follows it
///     toe band width - research/questions/0057-marshes-and-wetlands-shitchi.html: the springs at a fan's foot come out along its toe, so the band spans the fields' foot from one lower corner to the other; research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: as wide as the fields' foot, from one lower corner to the other, with the `PAD` of 90 ft more on each side, clipped to the bled canvas - the paddy fan's foot alone, so the dry hem laid beside the fan stays off the band (0 of 35,000 rolls with a dry plot on it, measured 2026-11-25)
///     stops at the lower corners - research/questions/0057-marshes-and-wetlands-shitchi.html: the springs at a fan's foot come out along its toe and its sides are among the ground cleared early; research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: where the fields narrow inward downhill the wet ground does not climb their side but runs between the fields' two lower corners, ATTESTED (a wet side found only on a valley floor against a hill foot, farmed as cold paddy) - so the band stops at the fields' lower corners (449 T432)
///     the shoulder past a corner at the corner's level - UNRESEARCHED: research/questions/0057-marshes-and-wetlands-shitchi.drawing.html sets the edge 90 ft above the foot where that ground is paddy, and beside the fan it is not, so past a lower corner the edge stays at the corner's own level; with it 90 ft higher the dry hem's lowest plots stood on the band (up to 27 percent of a comb's dry plots, measured 2026-11-25)
///     flaring flanks - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: part of the straight-band deviation, the band's ends bow outward downhill to the canvas's far edge
///     flare size - GUESS: each side out to 1.5 pad past the shoulder on a t**1.6 profile
///     its search steps - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N11, 2026-10-25) - a cross-slope station every 24 ft at least, the flank sampled at fifths
#[must_use]
pub(crate) fn toe_band(
    rings: &[&[Pt]],
    foot: Option<[Pt; 2]>,
    down_deg: f64,
    canvas: Pt,
    counts: &mut HashMap<String, u64>,
) -> Vec<Pt> {
    let pts: Vec<Pt> = rings.iter().flat_map(|r| r.iter().copied()).collect();
    if pts.is_empty() {
        return Vec::new();
    }
    let (dx, dy) = (down_deg.to_radians().cos(), down_deg.to_radians().sin());
    let (ux, uy) = (-dy, dx);
    let corners = [
        (-BLEED, -BLEED),
        (canvas.0 + BLEED, -BLEED),
        (canvas.0 + BLEED, canvas.1 + BLEED),
        (-BLEED, canvas.1 + BLEED),
    ];
    let v_out = corners
        .iter()
        .map(|c| c.0 * dx + c.1 * dy)
        .fold(f64::MIN, f64::max);
    let v_in = pts
        .iter()
        .map(|p| p.0 * dx + p.1 * dy)
        .fold(f64::MIN, f64::max)
        - PAD;
    let (corners_uv, u_lo, u_hi) = span(&pts, foot, (dx, dy));
    let cu: Vec<f64> = corners.iter().map(|c| c.0 * ux + c.1 * uy).collect();
    let (u0, u1) = (
        cu.iter().copied().fold(f64::MAX, f64::min).max(u_lo),
        cu.iter().copied().fold(f64::MIN, f64::max).min(u_hi),
    );
    let step = 24.0_f64.max(PAD / 3.0);
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a station count, a few hundred at most"
    )]
    let n = (((u1 - u0) / step) as usize + 1).max(2);
    #[expect(clippy::cast_precision_loss, reason = "a station index")]
    let stations: Vec<f64> = (0..n)
        .map(|k| u0 + (u1 - u0) * k as f64 / (n - 1) as f64)
        .collect();
    let mut by_u: Vec<(f64, f64)> = pts
        .iter()
        .map(|p| (p.0 * ux + p.1 * uy, p.0 * dx + p.1 * dy))
        .collect();
    by_u.sort_by(|a, b| a.0.total_cmp(&b.0));
    let m = by_u.len() as u64;
    let log_m = u64::from(u64::BITS - m.leading_zeros());
    // THE TOE'S COUNTED WORK (feature 443's unit, the deleted `toe_band`'s keys): each field point projected three ways and the
    // sort, then at each station two binary searches and the points in its window, and the edge's three-station smoothing
    tally(counts, "pt_test@toe_band", 3 * m + 3 * n as u64);
    tally(
        counts,
        "index_query@toe_band",
        m * log_m + 2 * n as u64 * log_m,
    );
    let mut examined = 0;
    let local: Vec<f64> = stations
        .iter()
        .map(|&u| {
            // past a lower corner the band's edge stays at that corner's own level: no lowest field read up the side
            match corners_uv {
                Some([l, _]) if u < l.0 => return l.1,
                Some([_, r]) if u > r.0 => return r.1,
                _ => {}
            }
            let lo = by_u.partition_point(|q| q.0 < u - PAD);
            let hi = by_u.partition_point(|q| q.0 <= u + PAD);
            examined += (hi - lo) as u64;
            let near = by_u[lo..hi].iter().map(|q| q.1).fold(f64::MIN, f64::max);
            (if hi > lo { near } else { v_in + PAD }) - PAD
        })
        .collect();
    let edge: Vec<f64> = (0..n)
        .map(|k| {
            local[k.saturating_sub(1)..(k + 2).min(n)]
                .iter()
                .copied()
                .fold(f64::MIN, f64::max)
        })
        .collect();
    tally(counts, "index_examined@toe_band", examined);
    tally(counts, "write@toe_band", n as u64 + 10);
    let at = |u: f64, v: f64| (u * ux + v * dx, u * uy + v * dy);
    let flank = |u_end: f64, v_end: f64, sign: f64| -> Vec<Pt> {
        [0.2, 0.4, 0.6, 0.8, 1.0]
            .iter()
            .map(|&t: &f64| {
                at(
                    u_end + sign * 1.5 * PAD * t.powf(1.6),
                    v_end + (v_out - v_end) * t,
                )
            })
            .collect()
    };
    let mut out: Vec<Pt> = stations
        .iter()
        .zip(&edge)
        .map(|(&u, &v)| at(u, v))
        .collect();
    out.extend(flank(u1, edge[n - 1], 1.0));
    out.extend(flank(u0, edge[0], -1.0).into_iter().rev());
    out
}

/// The fields' two lower corners, each across and down the slope.
///
/// Research:
///     the corners - NONE: a pair of points across and down the slope
type Corners = Option<[(f64, f64); 2]>;

/// The fields' lower corners across and down the slope (the left one first), and the band's cross-slope span: from one corner to
/// the other and `PAD` past each, or with none the rings' whole span and `PAD` past it.
///
/// Research:
///     toe band width - research/questions/0057-marshes-and-wetlands-shitchi.html: the springs at a fan's foot come out along its toe, so the band spans the foot from corner to corner; research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: as wide as the fields' foot, from one lower corner to the other, with the `PAD` of 90 ft more on each side; with no foot (a polder) the rings' whole span and `PAD` past it
fn span(pts: &[Pt], foot: Option<[Pt; 2]>, (dx, dy): Pt) -> (Corners, f64, f64) {
    let (ux, uy) = (-dy, dx);
    let corners_uv = foot.map(|f| {
        let mut c = f.map(|p| (p.0 * ux + p.1 * uy, p.0 * dx + p.1 * dy));
        if c[0].0 > c[1].0 {
            c.swap(0, 1);
        }
        c
    });
    let us = pts.iter().map(|p| p.0 * ux + p.1 * uy);
    let (u_lo, u_hi) = match corners_uv {
        Some([l, r]) => (l.0, r.0),
        None => us.fold((f64::MAX, f64::MIN), |(a, b), u| (a.min(u), b.max(u))),
    };
    (corners_uv, u_lo - PAD, u_hi + PAD)
}

/// `ring` grown outward by `d` (ft): each vertex moved along the mean of its two edges' outward normals - the deleted
/// `ring_offset`'s round-joined offset, kept to a vertex a corner.
///
/// Research:
///     the ring's offset - NONE: geometry, the ring grown by the width its caller hands it (the lane's 8 ft is `driver::LANE_FT`'s claim)
#[must_use]
pub(crate) fn grow(ring: &[Pt], by: f64, counts: &mut HashMap<String, u64>) -> Vec<Pt> {
    let len = ring.len();
    if len < 3 {
        return ring.to_vec();
    }
    let twice_area: f64 = (0..len)
        .map(|i| ring[i].0 * ring[(i + 1) % len].1 - ring[(i + 1) % len].0 * ring[i].1)
        .sum();
    // each corner's two edge normals read and its offset written, and the winding's pass (the deleted `exit_walls`' key)
    tally(counts, "write@exit_walls", 4 * len as u64);
    let side = if twice_area > 0.0 { 1.0 } else { -1.0 };
    let normal = |from: Pt, to: Pt| {
        let (ex, ey) = (to.0 - from.0, to.1 - from.1);
        let length = ex.hypot(ey).max(1e-9);
        (side * ey / length, -side * ex / length)
    };
    (0..len)
        .map(|i| {
            let here = ring[i];
            let before = normal(ring[(i + len - 1) % len], here);
            let after = normal(here, ring[(i + 1) % len]);
            let (mx, my) = (before.0 + after.0, before.1 + after.1);
            let length = mx.hypot(my).max(1e-9);
            (here.0 + by * mx / length, here.1 + by * my / length)
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::{grow, toe_band, PAD};
    use std::collections::HashMap;

    #[test]
    fn the_toe_lies_below_the_field_and_flares_off_the_canvas() {
        let field: Vec<(f64, f64)> = vec![
            (400.0, 300.0),
            (600.0, 300.0),
            (620.0, 600.0),
            (380.0, 600.0),
        ];
        let toe = toe_band(&[&field], None, 90.0, (1000.0, 1000.0), &mut HashMap::new());
        assert!(toe.len() > 10);
        let lowest_inner = toe.iter().take(5).map(|p| p.1).fold(f64::MAX, f64::min);
        assert!((lowest_inner - (600.0 - PAD)).abs() < 1e-6);
        assert!(toe.iter().any(|p| p.1 > 1000.0));
        assert!(toe_band(&[], None, 90.0, (10.0, 10.0), &mut HashMap::new()).is_empty());
    }

    /// THE WET GROUND STOPS AT THE FIELDS' LOWER CORNERS (449 T432): a fan whose head is wider than its foot, falling south;
    /// before T432 each station past a lower corner found its lowest field up the narrowing side, so the band's inner edge
    /// climbed both sides to the head (0057.drawing's DEVIATION `toe-on-tapering-flank`).
    #[test]
    fn the_toe_stops_at_a_narrowing_fans_lower_corners() {
        let fan: Vec<(f64, f64)> = vec![(300.0, 0.0), (700.0, 0.0), (560.0, 800.0), (440.0, 800.0)];
        let foot = [(440.0, 800.0), (560.0, 800.0)];
        let toe = toe_band(
            &[&fan],
            Some(foot),
            90.0,
            (2000.0, 2000.0),
            &mut HashMap::new(),
        );
        // no point of the band above the corners' level, nor across the slope past a corner and its 90 ft shoulder before it
        // flares downhill
        assert!(toe.iter().all(|p| p.1 >= 800.0 - PAD - 1e-6), "{toe:?}");
        let inner: Vec<_> = toe.iter().filter(|p| p.1 < 1000.0).collect();
        let (lo, hi) = (440.0 - 2.5 * PAD, 560.0 + 2.5 * PAD);
        let strays: Vec<_> = inner.iter().filter(|p| p.0 < lo || p.0 > hi).collect();
        assert_eq!(strays, Vec::<&&(f64, f64)>::new());
        // a polder's ring hands no corners: its band as before, across the ring's whole span
        let open = toe_band(&[&fan], None, 90.0, (2000.0, 2000.0), &mut HashMap::new());
        assert!(open.iter().any(|p| p.1 < 400.0));
    }

    /// ...BUT ALONG A SLANTED FOOT THE EDGE STILL FOLLOWS THE FIELDS POINT BY POINT (0057.drawing, the GM on Inashiro 2026-08-26).
    #[test]
    fn between_the_corners_the_edge_follows_a_slanted_foot() {
        let fan: Vec<(f64, f64)> =
            vec![(200.0, 0.0), (1000.0, 0.0), (800.0, 900.0), (400.0, 600.0)];
        let toe = toe_band(
            &[&fan],
            Some([(400.0, 600.0), (800.0, 900.0)]),
            90.0,
            (2000.0, 2000.0),
            &mut HashMap::new(),
        );
        let at = |x: f64| {
            toe.iter()
                .filter(|p| (p.0 - x).abs() < 20.0 && p.1 < 1000.0)
                .map(|p| p.1)
                .fold(f64::MAX, f64::min)
        };
        let (west, east) = (at(450.0), at(750.0));
        assert!(west < 700.0, "{west}");
        assert!(east > 750.0, "{east}");
    }

    #[test]
    fn a_ring_grows_outward_whichever_way_it_winds() {
        let sq = vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)];
        for ring in [sq.clone(), sq.iter().rev().copied().collect()] {
            let g = grow(&ring, 2.0, &mut HashMap::new());
            assert!(g
                .iter()
                .all(|p| p.0 < 0.0 || p.0 > 10.0 || p.1 < 0.0 || p.1 > 10.0));
        }
        assert_eq!(grow(&sq[..2], 2.0, &mut HashMap::new()).len(), 2);
    }
}
