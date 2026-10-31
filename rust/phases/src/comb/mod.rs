//! The comb field, rebuilt (feature 444 T16): its area, its single-field cap, and how many fields a settlement draws. Written from
//! `specs/444-work-budget-program/phases/field_greenfield.derivation.md` and T16's Decisions alone; the old field code unread.
//!
//! Research:
//!     the field's area - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: 1.3 acres gross a household

use crate::pyrand::knob_rng;

/// Square feet in an acre.
const SQ_FT_PER_ACRE: f64 = 43_560.0;
/// Square feet in a hectare (10,000 m2 at 0.3048 m a foot).
const SQ_FT_PER_HA: f64 = 107_639.104;

/// The paddy a household works, gross (acres).
///
/// Research:
///     paddy per household - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: 1.3 acres gross
pub const ACRES_PER_HOUSEHOLD: f64 = 1.3;

/// The single-field cap's band (hectares), rolled per settlement.
///
/// Research:
///     the single-field cap - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: the cap rolled per settlement between about 45 and 60 ha
pub const CAP_HA: (f64, f64) = (45.0, 60.0);

/// The settlement's paddy in square feet: its households times what each works.
///
/// Research:
///     the field's area - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: 1.3 acres gross a household
#[must_use]
pub fn paddy_sq_ft(households: u32) -> f64 {
    f64::from(households) * ACRES_PER_HOUSEHOLD * SQ_FT_PER_ACRE
}

/// The settlement's single-field cap in square feet: uniform in `CAP_HA`, drawn from the seed's `field_cap` stream (T16 D2).
///
/// Research:
///     the single-field cap - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: a knob between about 45 and 60 ha
#[must_use]
pub fn cap_sq_ft(seed: i64) -> f64 {
    // a draw in [0, 1) at the stream's resolution: 2^32 steps is finer than any area the map can show
    let u = f64::from(knob_rng(seed, "field_cap").randbelow(u32::MAX)) / f64::from(u32::MAX);
    (CAP_HA.0 + u * (CAP_HA.1 - CAP_HA.0)) * SQ_FT_PER_HA
}

/// How many fields the paddy is drawn as: one, or as many as keep each at most the cap, the paddy shared evenly (T16 D2).
///
/// Research:
///     several fields past the cap - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html: a settlement with more farmland had several tracts
#[must_use]
pub fn fields_for(paddy: f64, cap: f64) -> u32 {
    if paddy <= cap || cap <= 0.0 {
        return 1;
    }
    // paddy / cap is finite and positive here; a settlement's tracts number in the tens at most
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a small positive count"
    )]
    let n = (paddy / cap).ceil() as u32;
    n
}

#[cfg(test)]
mod tests {
    use super::{cap_sq_ft, fields_for, paddy_sq_ft, CAP_HA, SQ_FT_PER_HA};

    #[test]
    fn the_paddy_and_the_cap() {
        assert!(
            (paddy_sq_ft(20) / 43_560.0 - 26.0).abs() < 1e-9,
            "20 households farm 26 acres"
        );
        for seed in 0..64 {
            let ha = cap_sq_ft(seed) / SQ_FT_PER_HA;
            assert!((CAP_HA.0..=CAP_HA.1).contains(&ha), "{ha}");
        }
        assert_eq!(cap_sq_ft(7), cap_sq_ft(7), "the seed fixes the cap");
    }

    #[test]
    fn one_field_until_the_cap_then_several_each_at_most_it() {
        let cap = 45.0 * SQ_FT_PER_HA;
        assert_eq!(
            fields_for(paddy_sq_ft(80), cap),
            1,
            "80 households, 42 ha, under the floor"
        );
        let big = paddy_sq_ft(200); // about 105 ha
        let n = fields_for(big, cap);
        assert_eq!(n, 3);
        assert!(big / f64::from(n) <= cap);
        assert_eq!(fields_for(1.0, 0.0), 1);
    }
}
