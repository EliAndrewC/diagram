//! The fan's envelope (feature 444 T16): the comb field's outline before the comb is cut, its fork at the upslope head and its
//! drain at the downslope foot, narrowing toward the drain, its area the settlement's paddy.
//!
//! Research:
//!     the fan narrows toward its drain - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a fan of paddies narrows toward its drain, its bunds converging

use crate::pyrand::knob_rng;

/// A point on the map, in feet (x east, y south: the map's own axes).
pub type Pt = (f64, f64);

/// How much wider the fan is at its head than on the mean, and narrower at its foot (a GUESS: the record says the fan narrows
/// toward its drain, not by how much - a knob's middle, held here until the knob is rolled).
///
/// Research:
///     the fan's taper - GUESS: 0005 says a fan narrows toward its drain, not how much; a fifth either way of its mean breadth
pub const TAPER: f64 = 0.2;

/// How far a flank wanders off its line, as a share of the half-breadth, in each of its two waves (a GUESS: the record gives no
/// figure; enough that no flank reads as a ruled line, the GM's 2026-08-26 complaint of a brook "exactly east to west").
///
/// Research:
///     the flank's wander - GUESS: the record silent; 4% and 2% of the half-breadth, waves of the fan's whole length and its half
pub const WAVES: [(f64, f64); 2] = [(0.04, 1.0), (0.02, 2.0)];

/// The spacing of the envelope's points along its edge: one a water-index cell (a CONVENTION of the drawing - an edge drawn
/// gently wavering needs a point no oftener than the cell it is filed in).
///
/// Research:
///     the edge's point spacing - CONVENTION: one point a 64 ft index cell
pub const EDGE_STEP_FT: f64 = 64.0;

/// The unit vector a bearing points along, on the map's axes: the maps' angles turn clockwise from east (0 east, 90 south; y grows
/// southward).
///
/// Research:
///     bearings - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the maps' angles turn clockwise from east, so 90 is south
#[must_use]
pub fn heading(deg: f64) -> Pt {
    let r = deg.to_radians();
    (r.cos(), r.sin())
}

/// The fan: its fork (the head's middle), its foot (the drain's outfall) and its envelope, a closed ring of points.
#[derive(Debug, Clone, PartialEq)]
pub struct Fan {
    pub fork: Pt,
    pub foot: Pt,
    pub ring: Vec<Pt>,
    /// The unit vector down the fall, and the one across it to the fan's right looking downhill.
    pub down: Pt,
    pub across: Pt,
    /// The fan's length down the fall, and its half-breadths at the head and the foot (feet).
    pub length: f64,
    pub half_head: f64,
    pub half_foot: f64,
    /// Each flank's two waves' phases (radians), the left flank's first: rolled from the seed's `fan_wave` stream.
    pub phases: [[f64; 2]; 2],
}

impl Fan {
    /// The point `u` feet down the fall from the fork and `s` of the half-breadth there across it (s in [-1, 1]).
    ///
    /// Research:
    ///     the fan's coordinates - NONE: geometry; the half-breadth narrows evenly from head to foot (`TAPER`)
    #[must_use]
    pub fn at(&self, u: f64, s: f64) -> Pt {
        let h = self.half_side(u, s);
        (
            self.fork.0 + self.down.0 * u + self.across.0 * s * h,
            self.fork.1 + self.down.1 * u + self.across.1 * s * h,
        )
    }

    /// The half-breadth `u` feet down the fall on the flank `s` lies toward, its waves applied (the drain's middle, s = 0, none).
    ///
    /// Research:
    ///     the flank's wander - GUESS: `WAVES`, so no flank reads as a ruled line
    #[must_use]
    pub fn half_side(&self, u: f64, s: f64) -> f64 {
        let side = usize::from(s > 0.0);
        let t = u / self.length.max(f64::MIN_POSITIVE) * std::f64::consts::TAU;
        let wave: f64 = WAVES
            .iter()
            .zip(self.phases[side])
            .map(|((a, n), ph)| a * (t * n + ph).sin())
            .sum();
        self.half_at(u) * (1.0 + wave)
    }

    /// The half-breadth `u` feet down the fall.
    ///
    /// Research:
    ///     the fan narrows toward its drain - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: its bunds converging
    #[must_use]
    pub fn half_at(&self, u: f64) -> f64 {
        let t = u / self.length.max(f64::MIN_POSITIVE);
        self.half_head + (self.half_foot - self.half_head) * t
    }
}

/// The fan of `area` square feet, its length `aspect` times its mean breadth, falling along `down_deg`, its middle at `center`,
/// its flanks' waves rolled from `seed`. The head is (1 + TAPER) times the mean breadth across, the foot (1 - TAPER); each flank
/// wanders by `WAVES`. The ring runs down the left flank, across the foot, up the right flank and back across the head, a point
/// every `EDGE_STEP_FT`.
///
/// Research:
///     the fan narrows toward its drain - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: its bunds converging
///     its area - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: the households' paddy
#[must_use]
pub fn fan(area: f64, aspect: f64, down_deg: f64, center: Pt, seed: i64) -> Fan {
    // the waves move the ring's area a little off the paddy: one rescale by what they left puts it back
    let first = traced(area, aspect, down_deg, center, seed);
    let held = super::geom::signed_area(&first.ring).abs();
    traced(area * area / held.max(1.0), aspect, down_deg, center, seed)
}

/// The fan traced at `area` before the waves' rescale.
fn traced(area: f64, aspect: f64, down_deg: f64, center: Pt, seed: i64) -> Fan {
    let mean = (area / aspect.max(0.1)).sqrt();
    let length = area / mean;
    let (dx, dy) = heading(down_deg);
    let (ax, ay) = (-dy, dx); // across the fall, to the fan's right looking downhill
    let fork = (center.0 - dx * length / 2.0, center.1 - dy * length / 2.0);
    let foot = (center.0 + dx * length / 2.0, center.1 + dy * length / 2.0);
    let (head, tail) = (mean * (1.0 + TAPER) / 2.0, mean * (1.0 - TAPER) / 2.0);
    let mut waves = knob_rng(seed, "fan_wave");
    let mut draw = || f64::from(waves.randbelow(360)).to_radians();
    let phases = [[draw(), draw()], [draw(), draw()]];
    let mut f = Fan {
        fork,
        foot,
        ring: Vec::new(),
        down: (dx, dy),
        across: (ax, ay),
        length,
        half_head: head,
        half_foot: tail,
        phases,
    };
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a small positive count of steps"
    )]
    let (along, across) = (
        ((length / EDGE_STEP_FT).ceil() as usize).max(1),
        ((2.0 * tail / EDGE_STEP_FT).ceil() as usize).max(1),
    );
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a small positive count of steps"
    )]
    let across_head = ((2.0 * head / EDGE_STEP_FT).ceil() as usize).max(1);
    #[expect(clippy::cast_precision_loss, reason = "small step counts")]
    let frac = |k: usize, n: usize| k as f64 / n as f64;
    let mut ring = Vec::new();
    ring.extend((0..along).map(|k| f.at(length * frac(k, along), -1.0)));
    ring.extend((0..across).map(|k| f.at(length, -1.0 + 2.0 * frac(k, across))));
    ring.extend((0..along).map(|k| f.at(length * (1.0 - frac(k, along)), 1.0)));
    ring.extend((0..across_head).map(|k| f.at(0.0, 1.0 - 2.0 * frac(k, across_head))));
    f.ring = ring;
    f
}

#[cfg(test)]
mod tests {
    use super::{fan, heading, TAPER};
    use crate::field::geom::signed_area;

    #[test]
    fn the_fan_holds_its_area_falls_its_way_and_narrows_toward_its_drain() {
        let area = 26.0 * 43_560.0;
        let f = fan(area, 1.0, 315.0, (3200.0, 3200.0), 4);
        assert!((signed_area(&f.ring).abs() / area - 1.0).abs() < 0.002);
        let (dx, dy) = heading(315.0);
        let down = (f.foot.0 - f.fork.0, f.foot.1 - f.fork.1);
        assert!(down.0 * dx + down.1 * dy > 0.0);
        let head_w =
            ((f.ring[0].0 - f.fork.0).powi(2) + (f.ring[0].1 - f.fork.1).powi(2)).sqrt() * 2.0;
        assert!(head_w > 0.0 && TAPER > 0.0);
        let n = f.ring.len();
        assert!(n > 40, "an edge point each cell: {n}");
        assert!((heading(0.0).0 - 1.0).abs() < 1e-12, "0 is east, +x");
        assert!((heading(90.0).1 - 1.0).abs() < 1e-12, "90 is south, +y");
    }
}
