//! The basin's rules, refused where they are decided (feature 444 T16 D7): no corner sharper than 25 degrees, none smaller than a
//! quarter of its cell, none an arrowhead.
//!
//! Research:
//!     the basin's shape - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: no basin tapering to a point sharper than 25 degrees, none smaller than a quarter of its cell, none an arrowhead

use std::fmt;

use super::fan::Pt;
use super::geom::{corner_deg, hull, signed_area};

/// The sharpest corner a basin may have (degrees).
///
/// Research:
///     the basin's corner - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: no basin tapering to a point sharper than 25 degrees
pub const MIN_CORNER_DEG: f64 = 25.0;

/// The smallest basin, as a share of its cell.
///
/// Research:
///     the basin's floor - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: none smaller than a quarter of its cell
pub const MIN_CELL_SHARE: f64 = 0.25;

/// A rule of the field broken where it was decided, named in its message.
///
/// Research:
///     a refusal - NONE: the error's record
#[derive(Debug, Clone, PartialEq)]
pub struct FieldRefused {
    pub rule: &'static str,
    pub detail: String,
}

impl fmt::Display for FieldRefused {
    /// The refusal as its message.
    ///
    /// Research:
    ///     the message - NONE: formatting
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "the field refused, {}: {}", self.rule, self.detail)
    }
}

/// Under this corner a point counts toward an arrowhead (degrees).
///
/// Research:
///     the arrowhead - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a point sharper than 40 degrees and a notch deep enough to bring its solidity under 0.90
pub const ARROW_POINT_DEG: f64 = 40.0;

/// Under this solidity (area over its hull's) a notch counts toward an arrowhead.
///
/// Research:
///     the arrowhead - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a notch deep enough to bring its solidity under 0.90
pub const ARROW_SOLIDITY: f64 = 0.90;

/// Whether a ring is an arrowhead: a point sharper than `ARROW_POINT_DEG` and a notch bringing its solidity under
/// `ARROW_SOLIDITY`, both at once.
///
/// Research:
///     the arrowhead - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: one that does both is an arrowhead, and the maps refuse it
#[must_use]
pub fn arrowhead(ring: &[Pt]) -> bool {
    let point = (0..ring.len()).any(|i| corner_deg(ring, i) < ARROW_POINT_DEG);
    let solidity = signed_area(ring).abs() / signed_area(&hull(ring)).abs().max(1e-12);
    point && solidity < ARROW_SOLIDITY
}

/// A basin held to its rules against its `cell` (square feet), or refused by the rule it breaks.
///
/// # Errors
/// `FieldRefused` naming the first rule the basin breaks.
pub fn held(ring: &[Pt], cell: f64) -> Result<(), FieldRefused> {
    // a triangle at a flank keeps its four corners, two of them one (`lattice::row_basins`, T25): its corners read once each
    let mut once: Vec<Pt> = Vec::with_capacity(ring.len());
    for &p in ring {
        if once
            .last()
            .is_none_or(|q: &Pt| (q.0 - p.0).hypot(q.1 - p.1) > 1e-9)
        {
            once.push(p);
        }
    }
    let ring = once.as_slice();
    let area = signed_area(ring).abs();
    if area < MIN_CELL_SHARE * cell {
        return Err(FieldRefused {
            rule: "a quarter of its cell",
            detail: format!("{area:.0} sq ft against a {cell:.0} sq ft cell"),
        });
    }
    if let Some(i) = (0..ring.len()).find(|&i| corner_deg(ring, i) < MIN_CORNER_DEG) {
        return Err(FieldRefused {
            rule: "25 degrees",
            detail: format!("a corner of {:.1} degrees", corner_deg(ring, i)),
        });
    }
    if arrowhead(ring) {
        return Err(FieldRefused {
            rule: "the arrowhead",
            detail: format!("{ring:?}"),
        });
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{arrowhead, held};

    #[test]
    fn a_basin_is_refused_by_the_rule_it_breaks() {
        let good = [(0.0, 0.0), (31.0, 0.0), (31.0, 48.0), (0.0, 48.0)];
        assert!(held(&good, 1488.0).is_ok());
        let small = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)];
        assert_eq!(
            held(&small, 1488.0).unwrap_err().rule,
            "a quarter of its cell"
        );
        let sharp = [(0.0, 0.0), (200.0, 0.0), (0.0, 40.0)];
        let e = held(&sharp, 1488.0).unwrap_err();
        assert_eq!(e.rule, "25 degrees");
        assert!(e.to_string().contains("25 degrees"));
        // a 30 degree point with a notch in its back: past 25 degrees, but an arrowhead (solidity 0.70)
        let dart = [(100.0, 0.0), (0.0, 27.0), (30.0, 0.0), (0.0, -27.0)];
        assert!(arrowhead(&dart));
        assert_eq!(held(&dart, 1488.0).unwrap_err().rule, "the arrowhead");
        let kite = [(100.0, 0.0), (0.0, 27.0), (-5.0, 0.0), (0.0, -27.0)];
        assert!(!arrowhead(&kite), "a point with no notch is no arrowhead");
        assert!(!arrowhead(&good));
    }
}
