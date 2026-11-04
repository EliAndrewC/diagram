//! The farmhouse's turn (feature 444 T30): the village's common bearing near south, the turn of the lane the house stands on - read
//! from the field margin the lanes are laid along, since no lane stands while the houses are seated - and its own by-eye spread, the
//! two held inside the spread's limit by a soft curve; and the box a part turned by it clears.
//!
//! Research:
//!     farmhouse bearing - research/questions/0029-farmhouses-minka.drawing.html: common bearing plus the lane's turn plus a by-eye spread, held under 30 degrees by a soft limit; no quarter-turned house

use super::layout::{hjit, Rect};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// How far a house may turn from the common bearing (degrees).
///
/// Research:
///     bearing spread - research/questions/0029-farmhouses-minka.html, research/questions/0029-farmhouses-minka.drawing.html: up to about 30 degrees from the common bearing
pub const SPREAD_DEG: f64 = 30.0;

/// The by-eye turn off the lane: a triangular spread of this many degrees each way.
///
/// Research:
///     by-eye turn off the lane - research/questions/0029-farmhouses-minka.drawing.html: triangular, +-12 degrees
pub const JITTER_DEG: f64 = 12.0;

/// The margin a house reads as its lane (feet either side of its nearest margin point), the full turn's reach and the reach the
/// pull fades out at, and the margin's sample step.
///
/// Research:
///     lane bend a house reads - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); 48 px of the margin either side, read as the lane's bend
///     full lane turn within reach - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); the margin's whole turn within 96 px of it
///     lane turn fades out - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); the margin's pull fades to none at 240 px
///     its search steps and tolerances - NONE: a sampling of the margin, deciding nothing about the place - 8 ft
pub const FOLLOW: (f64, f64, f64, f64) = (48.0, 96.0, 240.0, 8.0);

/// The cell a house's draws are keyed on (feet): a seat moved a foot or two keeps the turn it was moved for.
///
/// Research:
///     its salts, guards and sentinels - NONE: a map drawing convention - 4 ft
pub const KEY_CELL: f64 = 4.0;

/// An undirected line's turn as a rectangular house follows it, folded into [-45, 45): a house stands square to its lane with its
/// front or its gable.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 45 (a square's quarter-turn fold (geometry))
#[must_use]
pub fn wrap_square(d: f64) -> f64 {
    (d + 45.0).rem_euclid(90.0) - 45.0
}

/// `d` held inside plus or minus `limit` by a smooth curve: itself near zero, approaching the limit without reaching it.
#[must_use]
pub fn soft_limit(d: f64, limit: f64) -> f64 {
    limit * (d / limit).tanh()
}

/// The field margin's bend, read where a house stands: the margin sampled every few feet once, filed in a grid of cells, and a
/// query the chord across the span either side of its nearest sample, its pull full near the margin and fading past it.
pub struct Margin {
    samples: Vec<Pt>,
    cells: std::collections::HashMap<(i64, i64), Vec<usize>>,
    along: f64,
    span: usize,
}

/// The margin's grid cell (feet).
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 64 (spatial-index cell)
pub const MARGIN_CELL: f64 = 64.0;

impl Margin {
    /// The margin `ring` sampled and filed, its bends read against the settlement's axis at `along` degrees.
    #[must_use]
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        clippy::cast_precision_loss,
        reason = "sample counts of a few thousand and cell indices of a few hundred"
    )]
    pub fn new(ring: &[Pt], along: f64, tests: &mut Counts) -> Self {
        let step = FOLLOW.3;
        let mut samples = Vec::new();
        for i in 0..ring.len() {
            let (a, b) = (ring[i], ring[(i + 1) % ring.len()]);
            let k = ((dist(a, b) / step) as usize).max(1);
            for t in 0..k {
                let f = t as f64 / k as f64;
                samples.push((a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f));
            }
        }
        let mut cells: std::collections::HashMap<(i64, i64), Vec<usize>> =
            std::collections::HashMap::new();
        for (i, p) in samples.iter().enumerate() {
            cells
                .entry((
                    (p.0 / MARGIN_CELL).floor() as i64,
                    (p.1 / MARGIN_CELL).floor() as i64,
                ))
                .or_default()
                .push(i);
        }
        tests.add("write@new", 2 * samples.len() as u64);
        Self {
            samples,
            cells,
            along,
            span: ((FOLLOW.0 / step) as usize).max(1),
        }
    }

    /// The nearest sample within the pull's reach: the cells round the point, the search widened while it finds none.
    #[expect(
        clippy::cast_possible_truncation,
        reason = "cell indices of a few hundred"
    )]
    fn nearest(&self, p: Pt, tests: &mut Counts) -> Option<usize> {
        let reach = FOLLOW.2;
        let mut pad = MARGIN_CELL;
        while pad <= reach * 2.0 {
            let mut best: Option<(f64, usize)> = None;
            let (i0, i1) = (
                ((p.0 - pad) / MARGIN_CELL).floor() as i64,
                ((p.0 + pad) / MARGIN_CELL).floor() as i64,
            );
            let (j0, j1) = (
                ((p.1 - pad) / MARGIN_CELL).floor() as i64,
                ((p.1 + pad) / MARGIN_CELL).floor() as i64,
            );
            for i in i0..=i1 {
                for j in j0..=j1 {
                    for &k in self.cells.get(&(i, j)).map_or(&[][..], Vec::as_slice) {
                        tests.add("index_query@nearest", 1);
                        let d = dist(p, self.samples[k]);
                        if d <= pad && best.is_none_or(|(bd, bk)| (d, k) < (bd, bk)) {
                            best = Some((d, k));
                        }
                    }
                }
            }
            if let Some((d, k)) = best {
                return (d <= reach).then_some(k);
            }
            pad *= 2.0;
        }
        None
    }

    /// The turn the margin gives a house at `p` (degrees): its chord's bend against the axis, folded square, full within the full
    /// reach and fading to none at the pull's reach.
    #[must_use]
    #[expect(
        clippy::many_single_char_names,
        reason = "the plane geometry's own names"
    )]
    pub fn follow(&self, p: Pt, tests: &mut Counts) -> f64 {
        let n = self.samples.len();
        let Some(k) = self.nearest(p, tests).filter(|_| n >= 3) else {
            return 0.0;
        };
        let (a, b) = (
            self.samples[(k + n - self.span % n) % n],
            self.samples[(k + self.span) % n],
        );
        let turn = wrap_square((b.1 - a.1).atan2(b.0 - a.0).to_degrees() - self.along);
        let (_, full, reach, _) = FOLLOW;
        turn * ((reach - dist(p, self.samples[k])) / (reach - full)).clamp(0.0, 1.0)
    }
}

/// The turn a farmhouse seated at `p` is drawn at (degrees): the common bearing, the lane's turn and the house's own triangular
/// spread keyed on its seat, the two held under the spread's limit.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 11 (jitter salts (triangular spread)); 14 (jitter salts (triangular spread))
#[must_use]
pub fn house_rot(p: Pt, common: f64, lane: f64) -> f64 {
    let (kx, ky) = (
        (p.0 / KEY_CELL).round() * KEY_CELL,
        (p.1 / KEY_CELL).round() * KEY_CELL,
    );
    let spread = (hjit(kx, ky, 11.0) + hjit(kx, ky, 14.0) - 1.0) * JITTER_DEG;
    common + soft_limit(lane + spread, SPREAD_DEG)
}

/// The axis-aligned box of `r` as drawn, turned by `rot` degrees about its own center.
#[must_use]
pub fn turned_box(r: Rect, rot: f64) -> Rect {
    let th = rot.to_radians();
    let (c, s) = (th.cos().abs(), th.sin().abs());
    (r.0, r.1, r.2 * c + r.3 * s, r.2 * s + r.3 * c)
}
