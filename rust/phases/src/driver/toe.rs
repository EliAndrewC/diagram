//! What the seat is handed that the deleted Python derived (feature 444 T42; `t42-brief.md` section 3, stage 4a): the wet toe
//! below the fields (`toe_band`), and a ring grown outward by the lane's width (`wet_grown_by_the_lane`).
//!
//! Research:
//!     toe band edge - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: 90 ft above the local lowest field, smoothed over three stations
//!     toe band width - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: as wide as the fields plus 90 ft each side
//!     flaring flanks - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: part of the straight-band deviation, the band's ends bow outward downhill as seepage spreads

use std::collections::HashMap;

use crate::field::fan::Pt;
use crate::seat::tally;

/// The toe band's pad above the lowest field, and the bleed past the canvas (ft).
///
/// Research:
///     toe band edge - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: 90 ft above the local lowest field
///     its bleed - CONVENTION: 120 ft past the canvas edge, sizes on the sheet, not in the world
pub const PAD: f64 = 90.0;
const BLEED: f64 = 120.0;

/// The reed-marsh toe: the wet band below the fields, laid across the fall, its inner edge `PAD` above the local lowest field
/// point at each cross-slope station (smoothed over three), as wide as the fields plus `PAD`, its ends flaring downhill and off
/// the canvas - the deleted `toe_band`, read from the fields' rings.
///
/// Research:
///     flare size - GUESS: each side out to 1.5 pad past the shoulder on a t**1.6 profile
///     its search steps - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N11, 2026-10-25) - a cross-slope station every 24 ft at least, the flank sampled at fifths
#[must_use]
pub(crate) fn toe_band(
    rings: &[&[Pt]],
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
    let us: Vec<f64> = pts.iter().map(|p| p.0 * ux + p.1 * uy).collect();
    let (u_lo, u_hi) = (
        us.iter().copied().fold(f64::MAX, f64::min) - PAD,
        us.iter().copied().fold(f64::MIN, f64::max) + PAD,
    );
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

/// `ring` grown outward by `d` (ft): each vertex moved along the mean of its two edges' outward normals - the deleted
/// `ring_offset`'s round-joined offset, kept to a vertex a corner.
///
/// Research:
///     the lane's width round wet ground - GUESS: the deleted `wet_grown_by_the_lane`, 8 ft, the way out keeping its own width off the wet
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
        let toe = toe_band(&[&field], 90.0, (1000.0, 1000.0), &mut HashMap::new());
        assert!(toe.len() > 10);
        let lowest_inner = toe.iter().take(5).map(|p| p.1).fold(f64::MAX, f64::min);
        assert!((lowest_inner - (600.0 - PAD)).abs() < 1e-6);
        assert!(toe.iter().any(|p| p.1 > 1000.0));
        assert!(toe_band(&[], 90.0, (10.0, 10.0), &mut HashMap::new()).is_empty());
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
