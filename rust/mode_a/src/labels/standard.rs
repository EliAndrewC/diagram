//! The cartographic standard for placing a caption, as numbers (feature 449 T151, `labels/standard.py` whole; feature 266, GM
//! 2026-09-27: *"adopt this standard into our project, after looking up the details enough to be able to implement it faithfully."*).
//! Every constant is either the standard's own - with the page it is read from - or a calibration this project chose where the standard
//! names a rule and leaves its number to the mapmaker; each says which, its claim the Python's word for word (`ask:449-phase4-slices`
//! Q10: the claims stay keyed to the `.py` units, which stay for their Python importers until step 3b). The finding is
//! research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html; the evidence is specs/266-*/research.md R1.
//!
//! Research: caption block measure - NONE: the text metrics applied

use crate::py::sum;

/// THE RANKED POSITIONS AROUND A POINT FEATURE, best first: the user-tested order of Bobák, Čmolík and Čadík (2024), `PerceptPPO` (the GM,
/// 2026-09-29, feature 290: *"I would like to follow the published standard rather than deviate"*), its eight positions in its order and
/// no others. Each is (name, sx, sy) in the SUBJECT'S OWN frame as the words read: sx -1/0/+1 is left/center/right and sy -1/0/+1 is
/// above/level/below.
///
/// Research: ranked positions around a point - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: above, below, right, upper right, lower right, left, upper left, lower left
pub const POSITIONS: [(&str, f64, f64); 8] = [
    ("above", 0.0, -1.0),
    ("below", 0.0, 1.0),
    ("right", 1.0, 0.0),
    ("upper right", 1.0, -1.0),
    ("lower right", 1.0, 1.0),
    ("left", -1.0, 0.0),
    ("upper left", -1.0, -1.0),
    ("lower left", -1.0, 1.0),
];

/// THE GAP, measured from the subject's drawn edge to the caption's nearest edge; half the caption's font size is this project's
/// calibration (spec D2), the same for every caption of a size.
///
/// Research: the gap from a feature - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: half the caption's letter height, from the drawn edge
pub const PREFERRED_OFFSET_EM: f64 = 0.5;

/// NEARER FIRST (QGIS's default, "Prefer closer labels"): every position at the preferred offset is tried before any seat further out,
/// then ring by ring outward, half an em a ring.
///
/// Research: nearer first - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: further seats a half em a ring outward
pub const RING_STEP_EM: f64 = 0.5;

/// How far the ringed search runs before the leader rings.
///
/// Research: how far the ringed search runs - CONVENTION: eight ems before the outer leader rings; past twice the usual gap (`placer.LEADERLESS_RINGS`) every seat is tied back by a leader, as 0242 has it
pub const REACH_EM: f64 = 8.0;

/// THE HUG: a caption never stands more than this far, box to box, from the feature it names (`label_hugs_its_referent`, the gate's
/// 120 px since feature 133), so it bounds every seat the placer offers.
///
/// Research: the hug - CONVENTION: never more than 120 px box to box from what it names, a calibration from the gate
pub const HUG_PX: f64 = 120.0;

/// THE WEIGHTS, on Esri's scale: free space first; when none is left, the least total weight.
///
/// Research: an obstacle's weight - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption covers nothing while another choice exists
pub const WEIGHT_OBSTACLE: f64 = 1000.0;

/// What a way crossed costs: half an obstacle, so crossing one beats crossing two.
///
/// Research: a way crossed - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: half an obstacle, so crossing one beats crossing two - the figure the page records as our calibration, not a finding; three ways crossed outweigh one building, which the page never covers while another choice exists, and no pool caption meets it: of the 16 captions costing an obstacle or more, none had in any of its searches a seat crossing only ways with a leader crossing nothing (feature 449 T195, observed 2026-11-19, method: every seat of every search of those captions on the four caption-placing sheets, scratchpad t195/ways2.py, ways2-summary.log; Hoshigaoka draws no way, and the compound sheets take free seats alone)
pub const WEIGHT_WAY: f64 = 500.0;

/// What free ground costs.
///
/// Research: free ground - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: fields, scrub, groves and open ground are available space
pub const WEIGHT_FREE: f64 = 0.0;

/// ASSOCIATION: a block nearer than the preferred offset to any obstacle but its subject counts as covering it (plan P1).
///
/// Research: association - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption as near a neighbor as its subject counts as covering it
pub const CLEAR_EM: f64 = PREFERRED_OFFSET_EM;

/// A way is crossed when the block comes within its drawn half-width plus this notch: a halo on a tread reads as a bite out of the path.
/// The figure is in sheet units: 2 ft where a unit is a foot, 2/3 ft on a hand sheet drawn at 3 px to the foot (feature 449 T188).
///
/// Research: way notch - CONVENTION: 2 sheet units past a way's half-width, where a halo would bite the tread - 2 ft where a unit is a foot (the gate's `NOTCH_CLEARANCE`), 2/3 ft on a hand sheet at 3 px to the foot
pub const WAY_NOTCH: f64 = 2.0;

/// Research: character width - CONVENTION: 0.55 em
pub const CHAR_W_EM: f64 = 0.55;
/// Research: line height - CONVENTION: 1.05 em
pub const LINE_H_EM: f64 = 1.05;
/// Research: line pitch - CONVENTION: 1.15 em
pub const PITCH_EM: f64 = 1.15;
/// Research: block center above the baseline - CONVENTION: 0.275 em
pub const CENTER_ABOVE_BASELINE_EM: f64 = 0.275;

/// An angle in degrees turned into (-90, 90], so the words never read upside down (psu-geog486-point-labels: "don't write upside
/// down"). `math.fmod` is C's `fmod`, Rust's `%` on floats.
///
/// Research: never upside down - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a half turn where the angle would invert the words
#[must_use]
pub fn upright(angle: f64) -> f64 {
    let a = angle % 180.0;
    if a <= -90.0 {
        a + 180.0
    } else if a > 90.0 {
        a - 180.0
    } else {
        a
    }
}

/// `len(line)`: a line's length in code points, as Python counts it.
#[must_use]
#[expect(clippy::cast_precision_loss, reason = "Python's `len()` as a float")]
pub fn chars(line: &str) -> f64 {
    line.chars().count() as f64
}

/// The half-width and half-height of a caption set on `lines` at `size` - the block `label()` records. `char_w` is the width per character
/// in ems, the standard's unless a caller measured its text as wider.
///
/// Research: caption block size - NONE: the text metrics applied, the widest line by its characters and the lines by their pitch
#[must_use]
#[expect(clippy::cast_precision_loss, reason = "Python's `len()` as a float")]
pub fn block_half(lines: &[String], size: f64, char_w: f64) -> (f64, f64) {
    // the lengths are whole numbers, so the largest is the largest whichever comes first
    let widest = lines.iter().map(|l| chars(l)).fold(0.0, f64::max);
    let w = widest * size * char_w;
    let h = size * LINE_H_EM + (lines.len() as f64 - 1.0) * size * PITCH_EM;
    (w / 2.0, h / 2.0)
}

/// The sum of the per-line heights (`sum(PITCH_EM * s for s in sizes)`), Python's compensated `sum()`.
#[must_use]
pub fn pitch_sum(sizes: &[f64]) -> f64 {
    sum(sizes.iter().map(|s| PITCH_EM * s))
}

#[cfg(test)]
mod tests {
    use super::{block_half, chars, pitch_sum, upright, POSITIONS, WEIGHT_FREE};

    #[test]
    #[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
    fn an_angle_is_turned_to_read_upright() {
        assert_eq!(upright(126.0), -54.0);
        assert_eq!(upright(-54.0), -54.0);
        assert_eq!(upright(-90.0), 90.0);
        assert_eq!(upright(90.0), 90.0);
        assert_eq!(upright(-270.0), 90.0);
        assert_eq!(upright(450.0), 90.0);
    }

    #[test]
    #[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
    fn a_block_is_its_widest_line_by_its_lines() {
        let lines = ["Shrine of".to_owned(), "Benten".to_owned()];
        // Python: block_half(["Shrine of", "Benten"], 10, 0.55) == (24.750000000000004, 11.0)
        assert_eq!(
            block_half(&lines, 10.0, 0.55),
            (24.750_000_000_000_004, 11.0)
        );
        assert_eq!(chars("\u{6c34}a"), 2.0);
        assert_eq!(pitch_sum(&[12.0, 8.0]), 23.0);
        assert_eq!((POSITIONS[0].0, WEIGHT_FREE), ("above", 0.0));
    }
}
