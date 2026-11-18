//! What the audit reads of the compound engine (feature 449 T175, `ask:449-engine-order` condition 2): `compound_model`'s three distances
//! and its palette (`KINDS`), and `compound_parts`' three predicates with the box gap they measure by - the ONE rule the draft seats a
//! fire-water tub and a notice board by and the audit holds every sheet to (feature 287, homes H29b). Nothing more of either module:
//! the rest is the drafting engine, the plan's step 3.
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3): `compound_model.py` and `compound_parts.py` stay for the generators until step 3; an edit
//! of what is here makes the same change here in the same commit, and `parse/lockstep_checks.rs` holds the two equal (each constant, and
//! each predicate on every tub, board and opening of every sheet the lockstep reads). The claims stay keyed to the `.py` units
//! (`ask:449-phase4-slices` Q10); each copy here carries the same claim.
//!
//! Research:
//!     the compound engine's audit rules - NONE: the engine's distances and predicates held as the audit reads them, deciding nothing here that the claims on each do not

use crate::py::pow_half;

/// A box in feet: `(x, y, x2, y2)`, the engine's `Box`.
pub type FtBox = (f64, f64, f64, f64);

/// How far from its building a fire-water tub may stand (feature 287, homes H29b): the number the audit's `fire_water_adrift` registers
/// - a gutter-fed tub hugs its eaves.
///
/// Research:
///     fire-water tub reach from its building - GUESS: a gutter-fed tub stands within 3.5 ft of its building's eaves; 0100 puts tubs beside a building's door and is silent on the distance.
pub const TUB_MAX_GAP_FT: f64 = 3.5;

/// How far a fire-water tub's center may stand from a door of the building it serves (feature 372 wave 106): research 0100 keeps
/// standing water at a wooden building's ENTRANCE, so a tub stands beside a door. A CONVENTION of this project, the number the audit's
/// `tubs_off_their_doors` registers.
///
/// Research:
///     fire-water tub reach from a door - GUESS: a tub's center stands within 10.5 ft of a door of its building, a figure fixed by the kitchen's two tubs beside a 6 ft door; 0100 puts tubs beside a door and is silent on the distance.
pub const TUB_DOOR_MAX_FT: f64 = 10.5;

/// How far from the main gate's opening the compound's notice board may stand (feature 287, homes H29b): the number the audit's
/// `notice_board_adrift` registers. 40 ft since feature 372 wave 104 (it was 20, set while boards stood against the wall).
///
/// Research:
///     board by the gate - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: the notice board stands within about 15 ft of a gate in the wall - it is allowed 40 ft, a departure the code keeps until feature 417 T33; within 40 ft of the opening, this project's figure, so a board beside the road (0190) can face its gate across the Imperial road's 30 ft (0088)
pub const NOTICE_BOARD_MAX_FT: f64 = 40.0;

/// The Mode A palette: a role, and its (fill, stroke), in the declaration's order (`compound_model.KINDS`; SKILL.md's Palette table).
pub const KINDS: [(&str, (&str, &str)); 8] = [
    ("lord", ("#DDB87A", "#5A3F1E")),
    ("service", ("#C9A57A", "#6B4F2A")),
    ("plain", ("#E8D2A8", "#6B4F2A")),
    ("kura", ("#F2EFE4", "#4A3318")),
    // 0098's raised timber storehouse (takakura): slatted walls on posts, the hand sheets' form (feature 374 wave 128)
    ("takakura", ("url(#granary-slats)", "#5A3F1E")),
    ("shrine", ("#C9876C", "#6B2A18")),
    ("cell", ("#B89868", "#5C4318")),
    ("dark", ("#8C6F3E", "#4A3318")),
];

/// The fill of a palette role (`KINDS[role][0]`); a role the palette does not name is the Python's `KeyError`, which no caller asks.
#[must_use]
pub fn fill(role: &str) -> &'static str {
    KINDS
        .iter()
        .find(|(k, _)| *k == role)
        .map_or("", |(_, (f, _))| f)
}

/// The clear distance between two boxes (0 where they touch or overlap), as the engine's `_gap` takes it: `(dx * dx + dy * dy) ** 0.5`,
/// libm's `pow` and not a square root ([`pow_half`]).
#[must_use]
pub fn gap(a: FtBox, b: FtBox) -> f64 {
    let dx = crate::py::max(crate::py::max(b.0 - a.2, a.0 - b.2), 0.0);
    let dy = crate::py::max(crate::py::max(b.1 - a.3, a.1 - b.3), 0.0);
    pow_half(dx * dx + dy * dy)
}

/// THE ONE PREDICATE of `fire_water_adrift` (feature 287, homes H29b), in feet: a fire-water tub's CENTER stands within [`TUB_MAX_GAP_FT`]
/// of the building whose gutter feeds it.
#[must_use]
pub fn tub_by_its_eaves(tub: (f64, f64), host: FtBox) -> bool {
    gap((tub.0, tub.1, tub.0, tub.1), host) <= TUB_MAX_GAP_FT
}

/// THE ONE PREDICATE of `tubs_off_their_doors` (feature 372 wave 106), in feet: a fire-water tub's CENTER stands within [`TUB_DOOR_MAX_FT`]
/// of the center of one of its building's doors - research 0100's water kept at the entrance.
#[must_use]
pub fn tub_by_its_door(tub: (f64, f64), doors: &[(f64, f64)]) -> bool {
    doors
        .iter()
        .any(|&(dx, dy)| crate::py::hypot(tub.0 - dx, tub.1 - dy) <= TUB_DOOR_MAX_FT)
}

/// THE ONE PREDICATE of `notice_board_adrift` (feature 287, homes H29b), in feet: the nearest edge of the board's box stands within
/// [`NOTICE_BOARD_MAX_FT`] of the middle of a gate opening.
#[must_use]
pub fn board_by_a_gate(board: FtBox, openings: &[(f64, f64)]) -> bool {
    openings
        .iter()
        .any(|&(ox, oy)| gap((ox, oy, ox, oy), board) <= NOTICE_BOARD_MAX_FT)
}

#[cfg(test)]
mod tests {
    use super::{board_by_a_gate, fill, gap, tub_by_its_door, tub_by_its_eaves};

    #[test]
    #[expect(clippy::float_cmp, reason = "each figure is the Python's to the bit")]
    fn the_predicates_measure_as_the_engine_s() {
        assert_eq!(gap((0.0, 0.0, 1.0, 1.0), (4.0, 5.0, 6.0, 6.0)), 5.0);
        assert_eq!(gap((0.0, 0.0, 1.0, 1.0), (0.5, 0.5, 2.0, 2.0)), 0.0);
        assert!(tub_by_its_eaves((0.0, 3.5), (0.0, 0.0, 0.0, 0.0)));
        assert!(!tub_by_its_eaves((0.0, 3.6), (0.0, 0.0, 0.0, 0.0)));
        assert!(tub_by_its_door((0.0, 0.0), &[(30.0, 0.0), (10.5, 0.0)]));
        assert!(!tub_by_its_door((0.0, 0.0), &[]));
        assert!(board_by_a_gate((40.0, 0.0, 41.0, 1.0), &[(0.0, 0.0)]));
        assert!(!board_by_a_gate((40.1, 0.0, 41.0, 1.0), &[(0.0, 0.0)]));
        assert_eq!((fill("kura"), fill("nothing")), ("#F2EFE4", ""));
    }
}
