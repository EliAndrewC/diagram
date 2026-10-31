//! The water frame: the map's plan rolled before anything is placed (feature 444 T19), written from
//! `specs/444-work-budget-program/phases/water_frame_greenfield.derivation.md` alone.
//!
//! Research:
//!     fall and drainage declared first - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the bearing and the fall rolled before any feature is placed
//!     knobs rolled from the seed - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each knob's form rolled per hamlet, never chosen

use std::collections::HashMap;

use pyo3::prelude::*;

/// One knob of the plan as Python gathered it: its name, how many forms its table holds, whether the spec pins it, and the
/// branch it applies on.
type KnobIn = (String, u32, bool, String);

/// A seeded `SplitMix64` (D7): the same draws on every platform, no dependency, one stream per knob name so adding a knob
/// re-rolls no other.
///
/// Research:
///     the rolls' generator - NONE: a deterministic generator, the plan's draws its own (D7)
struct SplitMix(u64);

impl SplitMix {
    /// The stream of `knob` under the map's `seed`: the seed mixed with the name's FNV-1a hash.
    fn for_knob(seed: u64, knob: &str) -> Self {
        let mut h: u64 = 0xcbf2_9ce4_8422_2325;
        for b in knob.bytes() {
            h ^= u64::from(b);
            h = h.wrapping_mul(0x0100_0000_01b3);
        }
        Self(seed ^ h)
    }

    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        z ^ (z >> 31)
    }

    /// An index below `n`, by the high bits (Lemire's multiply), so every form of a table is as likely as its repeats make it.
    fn below(&mut self, n: u32) -> u32 {
        u32::try_from((u128::from(self.next()) * u128::from(n)) >> 64).unwrap_or(0)
    }
}

/// The derivation's count, kept by `<kind>@<function>` as the Python counters keep theirs (D9), compiled out of a build
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
pub fn roll(
    seed: u64,
    n_falls: u32,
    fall_pinned: bool,
    forms: &[String],
    knobs: &[KnobIn],
) -> (Option<u32>, Vec<Option<u32>>, HashMap<String, u64>) {
    let mut counts = Counts::default();
    counts.add("write@water_frame_identity", 3);
    let fall = if fall_pinned {
        None
    } else {
        Some(SplitMix::for_knob(seed, "down_deg").below(n_falls))
    };
    counts.add("candidate@water_frame_bearing", 6);
    let mut form = String::new();
    let mut out = Vec::with_capacity(knobs.len());
    for (i, (name, n, pinned, branch)) in knobs.iter().enumerate() {
        let on = i == 0 || applies(branch, &form);
        let chosen = if !on {
            counts.add("write@water_frame_knob", 1);
            None
        } else if *n <= 1 && !*pinned {
            counts.add("write@water_frame_knob", 2);
            Some(0)
        } else {
            counts.add("candidate@water_frame_knob", 3);
            if *pinned {
                None
            } else {
                Some(SplitMix::for_knob(seed, name).below(*n))
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
pub fn water_frame(
    seed: u64,
    n_falls: u32,
    fall_pinned: bool,
    forms: Vec<String>,
    knobs: Vec<KnobIn>,
) -> (Option<u32>, Vec<Option<u32>>, HashMap<String, u64>) {
    roll(seed, n_falls, fall_pinned, &forms, &knobs)
}

#[cfg(test)]
mod tests {
    use super::{applies, roll, SplitMix};

    fn knob(name: &str, n: u32, branch: &str) -> (String, u32, bool, String) {
        (name.to_owned(), n, false, branch.to_owned())
    }

    #[test]
    fn a_draw_is_the_same_each_time_and_differs_by_knob() {
        assert_eq!(
            SplitMix::for_knob(7, "bamboo").below(4),
            SplitMix::for_knob(7, "bamboo").below(4)
        );
        let spread: std::collections::HashSet<u32> = (0..64)
            .map(|s| SplitMix::for_knob(s, "bamboo").below(4))
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
        let (fall, got, _counts) = roll(3, 8, false, &forms, &knobs);
        assert!(fall.is_some_and(|f| f < 8));
        assert_eq!(got[0], Some(0), "one form: taken");
        assert!(got[1].is_some(), "on its branch: rolled");
        assert_eq!(got[2], None, "off its branch: written alone");
        assert_eq!(got[3], Some(0));
        let pinned = vec![("settlement_form".to_owned(), 3, true, "all".to_owned())];
        let (fall, got, _counts) = roll(3, 8, true, &forms, &pinned);
        assert_eq!(
            (fall, got),
            (None, vec![None]),
            "a pin is taken, never drawn"
        );
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
        let (_f, got, counts) = roll(1, 8, false, &forms, &knobs);
        let on = if got[0] == Some(0) { (3, 1) } else { (1, 3) };
        let total: u64 = counts.values().sum();
        assert_eq!(
            total,
            3 + 6 + 3 + on.0 + on.1 + 2,
            "identity, bearings, the form, its two branch knobs, a one-form knob"
        );
    }
}
