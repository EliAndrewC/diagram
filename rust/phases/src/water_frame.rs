//! The water frame: the map's plan rolled before anything is placed (feature 444 T19), written from
//! `specs/444-work-budget-program/phases/water_frame_greenfield.derivation.md` alone.
//!
//! Research:
//!     fall and drainage declared first - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the bearing and the fall rolled before any feature is placed
//!     knobs rolled from the seed - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each knob's form rolled per hamlet, never chosen

use std::collections::HashMap;

use pyo3::prelude::*;

use crate::pyrand::knob_rng;

/// One knob of the plan as Python gathered it: its name, how many forms its table holds, whether the spec pins it, and the
/// branch it applies on.
type KnobIn = (String, u32, bool, String);

/// The derivation's count, kept by `<kind>@<function>` as the Python counters keep theirs - `candidate@roll_plan` for a draw here,
/// `write@_rust_rolls` for a field Python writes back (D9) - compiled out of a build
/// without the `counters` feature (FR-012).
///
/// Research:
///     the counts - NONE: the work-budget's own bookkeeping
#[derive(Default)]
struct Counts(HashMap<String, u64>);

impl Counts {
    #[cfg_attr(
        not(feature = "counters"),
        expect(clippy::unused_self, reason = "the counters compile out (FR-012)")
    )]
    fn add(&mut self, key: &str, n: u64) {
        #[cfg(feature = "counters")]
        {
            *self.0.entry(key.to_owned()).or_insert(0) += n;
        }
        #[cfg(not(feature = "counters"))]
        let _ = (key, n);
    }
}

/// The bearing of a wind quarter, in compass degrees (north 0, clockwise).
fn quarter_deg(windward: &str) -> f64 {
    match windward {
        "NE" => 45.0,
        "E" => 90.0,
        "SE" => 135.0,
        "S" => 180.0,
        "SW" => 225.0,
        "W" => 270.0,
        "NW" => 315.0,
        _ => 0.0,
    }
}

/// THE FALLS THAT BACK THE WIND (feature 444 T19; the round arbiter's ruling on ask:444-T19-outside-charges): the bearings - the
/// eight compass points, or the four cardinals a polder's survey grid is laid to - from the wind's own quarter clockwise round to
/// its opposite, both ends in, so the settlement's high side is its windward side and its back is to the wind. A table read once,
/// in place of a test of each fall (measured 2026-10-30: the same admitted set as `plan.fall_backs_the_wind` on every quarter).
///
/// Research:
///     high side and windward side as one - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the high windward margin, the wind read before the fall
#[must_use]
pub fn admitted(windward: &str, cardinal: bool) -> Vec<f64> {
    let w = quarter_deg(windward);
    let (n, step) = if cardinal { (4, 90.0) } else { (8, 45.0) };
    (0..n)
        .map(|i| f64::from(i) * step)
        .filter(|f| (f - w).rem_euclid(360.0) <= 180.0 + 1e-9)
        .collect()
}

/// The admitted falls, for Python's test against the rule it replaces.
#[pyfunction]
#[expect(clippy::needless_pass_by_value, reason = "PyO3 hands a String")]
#[must_use]
pub fn admitted_falls(windward: String, cardinal: bool) -> Vec<f64> {
    admitted(&windward, cardinal)
}

/// Whether a knob on `branch` applies to a map of settlement form `form`: the derivation's knob row - `all`, the nucleated
/// form's own, every form but nucleated (the farm's grove), the dispersed farm's, a row's, or `off` (Python found its branch
/// absent: no brook, a fixed row on flood ground).
fn applies(branch: &str, form: &str) -> bool {
    match branch {
        "all" => true,
        "nucleated" => form == "nucleated",
        "not_nucleated" => form != "nucleated",
        "dispersed" => form == "dispersed",
        "linear" => form == "linear",
        _ => false,
    }
}

/// The plan's rolls, as the derivation counts them: the fall from `n_falls` admitted bearings (unless pinned), and for each
/// knob in order - the settlement form first, named by `forms` - its allowed forms read, one rolled or the pin taken, and
/// written (3); a knob with one form left read and written (2); a knob off its branch written alone (1). Returns the fall's
/// index (`None` where pinned), each knob's index (`None` where pinned or off its branch), and the counts.
#[must_use]
pub fn roll_plan(
    seed: i64,
    falls: &[f64],
    fall_pinned: bool,
    forms: &[String],
    knobs: &[KnobIn],
) -> (Option<f64>, Vec<Option<u32>>, HashMap<String, u64>) {
    let mut counts = Counts::default();
    counts.add("write@_rust_rolls", 3);
    let fall = if fall_pinned || falls.is_empty() {
        None
    } else {
        let n = u32::try_from(falls.len()).unwrap_or(u32::MAX);
        falls
            .get(knob_rng(seed, "down_deg").randbelow(n) as usize)
            .copied()
    };
    counts.add("candidate@roll_plan", 6);
    let mut form = String::new();
    let mut out = Vec::with_capacity(knobs.len());
    for (i, (name, n, pinned, branch)) in knobs.iter().enumerate() {
        let on = i == 0 || applies(branch, &form);
        let chosen = if !on {
            counts.add("write@_rust_rolls", 1);
            None
        } else if *n <= 1 && !*pinned {
            counts.add("write@_rust_rolls", 2);
            Some(0)
        } else {
            counts.add("candidate@roll_plan", 3);
            if *pinned {
                None
            } else {
                Some(knob_rng(seed, name).randbelow(*n))
            }
        };
        if i == 0 {
            form = chosen
                .and_then(|k| forms.get(k as usize).cloned())
                .unwrap_or_else(|| forms.first().cloned().unwrap_or_default());
        }
        out.push(chosen);
    }
    (fall, out, counts.0)
}

/// The stage's entry from Python (`plan_site`, D6): the settlement form's pin, where the spec gives one, stands in `forms` as
/// its only entry.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 hands Vecs from Python lists"
)]
#[must_use]
pub fn stage_water_frame(
    seed: i64,
    windward: String,
    cardinal: bool,
    fall_pinned: bool,
    forms: Vec<String>,
    knobs: Vec<KnobIn>,
) -> (Option<f64>, Vec<Option<u32>>, HashMap<String, u64>) {
    roll_plan(
        seed,
        &admitted(&windward, cardinal),
        fall_pinned,
        &forms,
        &knobs,
    )
}

#[cfg(test)]
mod tests {
    use super::{applies, knob_rng, roll_plan};

    fn knob(name: &str, n: u32, branch: &str) -> (String, u32, bool, String) {
        (name.to_owned(), n, false, branch.to_owned())
    }

    #[test]
    fn the_falls_that_back_the_wind_run_clockwise_from_its_quarter_to_its_opposite() {
        assert_eq!(
            super::admitted("N", false),
            vec![0.0, 45.0, 90.0, 135.0, 180.0]
        );
        assert_eq!(
            super::admitted("SW", false),
            vec![0.0, 45.0, 225.0, 270.0, 315.0]
        );
        assert_eq!(super::admitted("NE", true), vec![90.0, 180.0]);
        assert!(roll_plan(1, &[], false, &[], &[]).0.is_none());
    }

    #[test]
    fn a_draw_is_the_same_each_time_and_differs_by_knob() {
        assert_eq!(
            knob_rng(7, "bamboo").randbelow(4),
            knob_rng(7, "bamboo").randbelow(4)
        );
        let spread: std::collections::HashSet<u32> = (0..64)
            .map(|s| knob_rng(s, "bamboo").randbelow(4))
            .collect();
        assert_eq!(spread.len(), 4, "every form drawn across seeds");
    }

    #[test]
    fn the_settlement_form_decides_each_knob_s_branch() {
        assert!(
            applies("nucleated", "nucleated")
                && !applies("nucleated", "linear")
                && applies("not_nucleated", "linear")
        );
        assert!(
            applies("dispersed", "dispersed")
                && applies("linear", "linear")
                && applies("all", "x")
                && !applies("off", "x")
        );
        let forms = vec!["nucleated".to_owned()];
        let knobs = vec![
            knob("settlement_form", 1, "all"),
            knob("well_siting", 2, "nucleated"),
            knob("row_line", 2, "linear"),
            knob("copse", 1, "all"),
        ];
        let (fall, got, _counts) =
            roll_plan(3, &super::admitted("NW", false), false, &forms, &knobs);
        assert!(fall.is_some_and(|f| [0.0, 45.0, 90.0, 135.0, 315.0].contains(&f)));
        assert_eq!(got[0], Some(0), "one form: taken");
        assert!(got[1].is_some(), "on its branch: rolled");
        assert_eq!(got[2], None, "off its branch: written alone");
        assert_eq!(got[3], Some(0));
        let pinned = vec![("settlement_form".to_owned(), 3, true, "all".to_owned())];
        let (fall, got, _counts) = roll_plan(3, &[0.0], true, &forms, &pinned);
        assert_eq!((fall, got), (None, vec![None])); // a pin is taken, never drawn
    }

    #[cfg(feature = "counters")]
    #[test]
    fn the_counts_are_the_derivation_s() {
        let forms = vec!["nucleated".to_owned(), "linear".to_owned()];
        let knobs = vec![
            knob("settlement_form", 2, "all"),
            knob("well_siting", 2, "nucleated"),
            knob("row_line", 2, "linear"),
            knob("one", 1, "all"),
        ];
        let (_f, got, counts) = roll_plan(1, &[0.0, 90.0], false, &forms, &knobs);
        let on = if got[0] == Some(0) { (3, 1) } else { (1, 3) };
        let total: u64 = counts.values().sum();
        assert_eq!(total, 3 + 6 + 3 + on.0 + on.1 + 2); // identity, bearings, the form, its two branch knobs, a one-form knob
    }
}
