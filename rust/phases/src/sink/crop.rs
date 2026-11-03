//! The field's outline as the sink reads it (feature 444 T26 D4, D5): read once, its area summed and the segments below the
//! outfall kept - the only ones a pond seated below the outfall can meet.
//!
//! Research:
//!     the outline as read - NONE: its reading and geometry; each rule's claim is at the unit that keeps it

use std::collections::HashMap;

use super::brook::proper_cross;
use super::tally;
use crate::field::fan::Pt;
use crate::field::geom::{inside, seg_dist};

/// The outline read once.
pub struct Crop {
    /// The ring as read.
    pub ring: Vec<Pt>,
    /// Its area (square feet).
    pub area: f64,
    /// The segments reaching below the outfall's line across the fall.
    pub low: Vec<(Pt, Pt)>,
    fall: Pt,
}

impl Crop {
    /// Read `outline` once: its area, and its segments reaching below `out` along `fall`.
    pub fn read(outline: &[Pt], out: Pt, fall: Pt, counts: &mut HashMap<String, u64>) -> Self {
        let n = outline.len();
        let u = |p: Pt| p.0 * fall.0 + p.1 * fall.1;
        let floor = u(out) - 1.0;
        let mut twice = 0.0;
        let mut low = Vec::new();
        for i in 0..n {
            let (a, b) = (outline[i], outline[(i + 1) % n]);
            twice += a.0 * b.1 - b.0 * a.1;
            if u(a).max(u(b)) >= floor {
                low.push((a, b));
            }
        }
        tally(counts, "read@outline", n as u64);
        Crop {
            ring: outline.to_vec(),
            area: twice.abs() / 2.0,
            low,
            fall,
        }
    }

    /// Whether the pond centered at `c` with radii `rx`, `ry` lies clear of the crop: no low segment meets its ellipse, and its
    /// center is outside the outline (a ray cast down the fall crosses the outline an even number of times - every segment it can
    /// cross reaches below the center, so below the outfall, so is low).
    ///
    /// Research:
    ///     the pond clear of the crop - research/questions/0060-field-drains-akusuiro.drawing.html: the pond at the field's foot
    pub fn pond_clear(&self, c: Pt, rx: f64, ry: f64, tests: &mut u64) -> bool {
        let mut odd = false;
        let cu = c.0 * self.fall.0 + c.1 * self.fall.1;
        let ray = (c.0 + self.fall.0 * 1e6, c.1 + self.fall.1 * 1e6);
        for &(a, b) in &self.low {
            *tests += 1;
            if a.0.max(b.0) >= c.0 - rx
                && a.0.min(b.0) <= c.0 + rx
                && a.1.max(b.1) >= c.1 - ry
                && a.1.min(b.1) <= c.1 + ry
                && meets_ellipse(a, b, c, rx, ry)
            {
                return false;
            }
            let reaches = (a.0 * self.fall.0 + a.1 * self.fall.1)
                .max(b.0 * self.fall.0 + b.1 * self.fall.1)
                >= cu;
            if reaches && proper_cross(c, ray, a, b) {
                odd = !odd;
            }
        }
        !odd
    }

    /// Whether the run's legs keep out of the rice: no leg crossing the outline and no interior vertex inside it - the first leg
    /// exempt where `anchored`, the run starting inside the field at the collector's own outfall. `tests` counts the work.
    ///
    /// Research:
    ///     not through the rice - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); no interior vertex or leg of a run in the field
    pub fn run_clear(&self, run: &[Pt], anchored: bool, tests: &mut u64) -> bool {
        let n = self.ring.len();
        for (k, leg) in run.windows(2).enumerate() {
            if k == 0 && anchored {
                continue;
            }
            *tests += n as u64;
            if (0..n).any(|i| proper_cross(leg[0], leg[1], self.ring[i], self.ring[(i + 1) % n])) {
                return false;
            }
        }
        for &p in &run[1..run.len().saturating_sub(1)] {
            *tests += n as u64;
            if inside(p, &self.ring) {
                return false;
            }
        }
        true
    }

    /// Whether `p` lies inside the outline (a whole-ring test, counted).
    pub fn holds(&self, p: Pt, tests: &mut u64) -> bool {
        *tests += self.ring.len() as u64;
        inside(p, &self.ring)
    }
}

/// Whether segment `a-b` meets the axis-aligned ellipse centered at `c` with radii `rx`, `ry`: in the ellipse's own frame,
/// scaled to a unit circle, the segment comes within 1 of the center.
#[must_use]
pub fn meets_ellipse(a: Pt, b: Pt, c: Pt, rx: f64, ry: f64) -> bool {
    let s = |p: Pt| ((p.0 - c.0) / rx, (p.1 - c.1) / ry);
    seg_dist((0.0, 0.0), s(a), s(b)) <= 1.0
}

/// How far past its drawn half-width a run keeps off a resting basin's edge (feet): the 0.2 the registry asks a stroked candidate
/// past its width, as a placer stricter by a hair.
///
/// Research:
///     a placer stricter by a hair - NONE: the registry's rounding margin, 0.2 ft
pub const RUN_MARGIN: f64 = 0.2;

/// The distance between segments `a0-a1` and `b0-b1` (0 where they cross).
fn seg_seg(a0: Pt, a1: Pt, b0: Pt, b1: Pt) -> f64 {
    if proper_cross(a0, a1, b0, b1) {
        return 0.0;
    }
    seg_dist(a0, b0, b1)
        .min(seg_dist(a1, b0, b1))
        .min(seg_dist(b0, a0, a1))
        .min(seg_dist(b1, a0, a1))
}

/// Whether a run's legs keep off every resting basin: no leg within its drawn half-width (`run_w`) and `RUN_MARGIN` of a basin's ring, no point of the run past its
/// first inside one (the overlap matrix: a drain never runs across a resting basin) - the first leg exempt where `anchored`, the
/// run starting inside the field: that leg is the collector's own continuation through its field, a sibling of the field's own
/// plots as the collector is (its record names the field).
///
/// Research:
///     no drain across a resting basin - GUESS: no source could speak to it, a value of ours; a resting basin is one of its field's plots (research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: resting plots scattered through the fields), kept clear by the run's drawn half-width and a margin, its first leg exempt as the collector's own
#[must_use]
pub fn off_resting(
    run: &[Pt],
    resting: &[Vec<Pt>],
    run_w: f64,
    anchored: bool,
    tests: &mut u64,
) -> bool {
    let skip = usize::from(anchored);
    let clear = run_w / 2.0 + RUN_MARGIN;
    resting.iter().all(|ring| {
        let n = ring.len();
        *tests += (n * run.len()) as u64;
        !run.windows(2)
            .skip(skip)
            .any(|leg| (0..n).any(|i| seg_seg(leg[0], leg[1], ring[i], ring[(i + 1) % n]) < clear))
            && !run.iter().skip(1 + skip).any(|&p| inside(p, ring))
    })
}

/// The point of segment `a-b` nearest `p`.
#[must_use]
pub fn nearest_on(p: Pt, a: Pt, b: Pt) -> Pt {
    let (vx, vy) = (b.0 - a.0, b.1 - a.1);
    let l2 = (vx * vx + vy * vy).max(1e-12);
    let t = (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / l2).clamp(0.0, 1.0);
    (a.0 + vx * t, a.1 + vy * t)
}
