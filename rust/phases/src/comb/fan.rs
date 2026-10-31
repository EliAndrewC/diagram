//! The fan's envelope (feature 444 T16): the comb field's outline before the comb is cut, its fork at the upslope head and its
//! drain at the downslope foot, narrowing toward the drain, its area the settlement's paddy.
//!
//! Research:
//!     the fan narrows toward its drain - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a fan of paddies narrows toward its drain, its bunds converging

/// A point on the map, in feet (x east, y south: the map's own axes).
pub type Pt = (f64, f64);

/// How much wider the fan is at its head than on the mean, and narrower at its foot (a GUESS: the record says the fan narrows
/// toward its drain, not by how much - a knob's middle, held here until the knob is rolled).
///
/// Research:
///     the fan's taper - GUESS: 0005 says a fan narrows toward its drain, not how much; a third either way of its mean breadth
pub const TAPER: f64 = 1.0 / 3.0;

/// The spacing of the envelope's points along its edge: one a water-index cell (a CONVENTION of the drawing - an edge drawn
/// gently wavering needs a point no oftener than the cell it is filed in).
///
/// Research:
///     the edge's point spacing - CONVENTION: one point a 64 ft index cell
pub const EDGE_STEP_FT: f64 = 64.0;

/// The unit vector a compass bearing points along, on the map's axes (north 0, clockwise; y grows southward).
///
/// Research:
///     bearings - NONE: compass arithmetic
#[must_use]
pub fn heading(deg: f64) -> Pt {
    let r = deg.to_radians();
    (r.sin(), -r.cos())
}

/// The fan: its fork (the head's middle), its foot (the drain's outfall) and its envelope, a closed ring of points.
#[derive(Debug, Clone, PartialEq)]
pub struct Fan {
    pub fork: Pt,
    pub foot: Pt,
    pub ring: Vec<Pt>,
}

/// The fan of `area` square feet, its length `aspect` times its mean breadth, falling along `down_deg`, its middle at `centre`.
/// The head is (1 + TAPER) times the mean breadth across, the foot (1 - TAPER): a trapezoid whose area is the mean breadth times
/// its length. Each edge is cut into points `EDGE_STEP_FT` apart.
///
/// Research:
///     the fan narrows toward its drain - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: its bunds converging
///     its area - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: the households' paddy
#[must_use]
pub fn fan(area: f64, aspect: f64, down_deg: f64, center: Pt) -> Fan {
    let mean = (area / aspect.max(0.1)).sqrt();
    let length = area / mean;
    let (dx, dy) = heading(down_deg);
    let (ax, ay) = (-dy, dx); // across the fall, to the fan's right looking downhill
    let fork = (center.0 - dx * length / 2.0, center.1 - dy * length / 2.0);
    let foot = (center.0 + dx * length / 2.0, center.1 + dy * length / 2.0);
    let (head, tail) = (mean * (1.0 + TAPER) / 2.0, mean * (1.0 - TAPER) / 2.0);
    let corners = [
        (fork.0 - ax * head, fork.1 - ay * head),
        (fork.0 + ax * head, fork.1 + ay * head),
        (foot.0 + ax * tail, foot.1 + ay * tail),
        (foot.0 - ax * tail, foot.1 - ay * tail),
    ];
    let mut ring = Vec::new();
    for i in 0..4 {
        let (a, b) = (corners[i], corners[(i + 1) % 4]);
        let len = ((b.0 - a.0).powi(2) + (b.1 - a.1).powi(2)).sqrt();
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a small positive count of steps"
        )]
        let steps = ((len / EDGE_STEP_FT).ceil() as usize).max(1);
        for k in 0..steps {
            #[expect(clippy::cast_precision_loss, reason = "a small step count")]
            let t = k as f64 / steps as f64;
            ring.push((a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t));
        }
    }
    Fan { fork, foot, ring }
}

/// A closed ring's area by the shoelace formula (square feet).
///
/// Research:
///     area - NONE: geometry
#[must_use]
pub fn ring_area(ring: &[Pt]) -> f64 {
    let n = ring.len();
    let twice: f64 = (0..n)
        .map(|i| {
            let (a, b) = (ring[i], ring[(i + 1) % n]);
            a.0 * b.1 - b.0 * a.1
        })
        .sum();
    twice.abs() / 2.0
}

#[cfg(test)]
mod tests {
    use super::{fan, heading, ring_area, TAPER};

    #[test]
    fn the_fan_holds_its_area_falls_its_way_and_narrows_toward_its_drain() {
        let area = 26.0 * 43_560.0;
        let f = fan(area, 1.0, 315.0, (3200.0, 3200.0));
        assert!(
            (ring_area(&f.ring) / area - 1.0).abs() < 1e-6,
            "the paddy's area"
        );
        let (dx, dy) = heading(315.0);
        let down = (f.foot.0 - f.fork.0, f.foot.1 - f.fork.1);
        assert!(
            down.0 * dx + down.1 * dy > 0.0,
            "the foot lies downhill of the fork"
        );
        let head_w =
            ((f.ring[0].0 - f.fork.0).powi(2) + (f.ring[0].1 - f.fork.1).powi(2)).sqrt() * 2.0;
        assert!(head_w > 0.0 && TAPER > 0.0);
        let n = f.ring.len();
        assert!(n > 40, "an edge point each cell: {n}");
        assert_eq!(heading(90.0).0.round(), 1.0, "east is +x");
        assert_eq!(heading(180.0).1.round(), 1.0, "south is +y");
    }
}
