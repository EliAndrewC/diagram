//! What counts as a DWELLING (`l7r/diagram/dwellings.py`, feature 156; ported by feature 449 T150, the engine port's step 2, the
//! Python deleted by its part B): one leaf with no imports of its own, so the place card (`place.rs`) and any other
//! reader share one definition of a dwelling.
//!
//! Research: what counts as a dwelling - NONE: the leaf's plumbing, each kind set and the household claimed beside it

/// A building's role for the population and frontage maths: a DWELLING houses one ~5-person household; the merchant's house and shop is
/// both a dwelling and a business. Adept-monk households by the temple precincts count as housing (GM 2026-07-24) and are absent from
/// the caste bands; `samurai_large` is a dwelling like every other `_large` variant.
///
/// Research: which buildings are homes - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html: ten kinds, monk houses among them
pub const DWELLING_KINDS: [&str; 10] = [
    "laborer",
    "laborer_large",
    "servant",
    "burakumin",
    "samurai",
    "samurai_large",
    "merchant",
    "merchant_house",
    "merchant_large",
    "monk_house",
];

/// A commercial frontage.
///
/// Research: commercial frontages - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html: a shop, and the merchant's house-over-shop counted as house and shop
pub const BUSINESS_KINDS: [&str; 2] = ["shop", "merchant"];

/// Inhabitants to a dwelling.
///
/// Research: inhabitants to a dwelling - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html: five, the setting's household
pub const HOUSEHOLD: i64 = 5;

/// Whether a building kind is a dwelling (`kind in DWELLING_KINDS`).
///
/// Research: plumbing - NONE: membership of the dwelling kinds, whose own claim says which they are
#[must_use]
pub fn is_dwelling(kind: &str) -> bool {
    DWELLING_KINDS.contains(&kind)
}

#[cfg(test)]
mod tests {
    #[test]
    fn a_dwelling_is_one_of_the_ten() {
        assert!(super::is_dwelling("monk_house") && !super::is_dwelling("shop"));
        assert!(super::BUSINESS_KINDS.contains(&"merchant"));
        assert_eq!(super::HOUSEHOLD, 5);
    }
}
