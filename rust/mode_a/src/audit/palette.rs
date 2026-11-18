//! A kind is painted in its palette role (feature 449 T175, `pack_audit/palette.py` whole; feature 294, plan B22): the building a sheet
//! tags `stables` is filled with the service buildings' color, a kura with the sealed storehouse's, and so on.
//!
//! THE TABLE IS A MAP DRAWING CONVENTION (plan D11): SKILL.md's Palette table names a role per element, its machine form the engine's
//! palette ([`crate::compound::KINDS`]); a kind the palette does not name is assigned the role every sheet that draws it already paints it
//! in, labeled GUESS beside its row. A kind's color is the fill of its largest rect that is NOT a room (a rect wholly inside a structure
//! of another kind is the building it stands in).
//!
//! Research:
//!     the palette's roles - NONE: a map drawing convention's table, each GUESS row labeled beside it, deciding nothing about a building

use l7r_gate_research::Error;

use super::checks::first_max;
use super::Sheet;
use crate::compound::fill;
use crate::parse::is_structure;
use crate::py::fixed;
use crate::tagged::Mark;

/// The slatted granary's pattern.
///
/// Research:
///     the slatted granary's fill - CONVENTION: the raised timber granary, the takakura that research/questions/0098-storehouses-for-the-tax-rice.drawing.html draws as one of a granary's two forms, is filled with a slat pattern so it reads apart from the plastered kura; no page gives a granary's drawn fill.
pub const GRANARY_SLATS: &str = "url(#granary-slats)";
/// SKILL.md: Latrines / utility.
///
/// Research:
///     the privy's gray - CONVENTION: a privy is filled gray, #7E726A, so it reads apart from the tan buildings where the household lives and works, the map drawing convention research/questions/0101-privies-setchin.drawing.html records; no source gives a privy's color.
pub const PRIVY: &str = "#7E726A";
/// SKILL.md: Well stone curb.
///
/// Research:
///     the well curb's color - CONVENTION: a well's stone curb is filled #9C8C70, the palette's stone; no page gives a curb's drawn color.
pub const WELL: &str = "#9C8C70";

/// kind -> the roles (palette keys, or a fill) it may be painted in, in the table's order; rows with no comment are the SKILL.md
/// palette's own words.
///
/// Research:
///     the palette's table - CONVENTION: the palette role each building kind is painted in, the Mode A palette's own rows, a kind the palette does not name assigned a role labeled GUESS beside its row; a fill says nothing of a building's real color.
///     the tax archive drawn as a kura - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: an office's records storehouse is drawn as one of the earth-walled storehouses (dozo), so the tax archive's role is the kura's.
///     a storehouse drawn as a kura - GUESS: a compound's storehouse is drawn as a sealed kura, as its records storehouse is; no page gives a general storehouse's form.
///     the granary's two forms - research/questions/0098-storehouses-for-the-tax-rice.drawing.html: the granary is either a timber storehouse raised on posts or an earth-walled kura, each map taking one, so the slatted fill and the kura's are both its role.
const ROLE_NAMES: [(&str, &[&str]); 25] = [
    ("residence", &["lord"]),
    ("lord's quarters", &["lord"]),
    ("family quarters", &["lord"]),
    // GUESS: the palette names "residence, audience pavilion"; every sheet's office hall is the lord's
    ("office hall", &["lord"]),
    // GUESS: the lord's own rooms (a room of the residence on the hand sheets)
    ("guest quarters", &["lord"]),
    // GUESS: the house elder's house, painted as the lord's on every sheet
    ("karo's house", &["lord"]),
    // GUESS: the shrine's hall-and-dwelling in the lord's-building color
    ("hall and dwelling", &["lord"]),
    ("kitchen", &["service"]),
    ("stables", &["service"]),
    ("barracks", &["service"]),
    // GUESS: a service building (the servants' row)
    ("servants' quarters", &["service"]),
    // GUESS: a service building (the retainers' row)
    ("retainers' quarters", &["service"]),
    // GUESS: a service building (a small addition to the kitchen)
    ("bath", &["service"]),
    ("gatehouse", &["dark"]),
    ("magistrate's dais", &["dark"]),
    ("clerks' room", &["plain"]),
    ("tally office", &["plain"]),
    ("tax archive", &["kura"]),
    // GUESS: a sealed kura, as the tax archive
    ("storehouse", &["kura"]),
    // the granary has TWO attested forms (docs/building-programs.md; Ochiba notes R18): the raised slatted granary, and the earthen
    // kura - a knob, so both fills are its role
    ("granary", &[GRANARY_SLATS, "kura"]),
    ("cell", &["cell"]),
    ("compound shrine", &["shrine"]),
    ("sanctuary", &["shrine"]),
    ("latrine", &[PRIVY]),
    // the curb; a roof over it is an unfilled outline on posts (feature 374 wave 135, 0196)
    ("well", &[WELL]),
];

/// The table: kind -> the fills it may be painted in (`ROLES`).
#[must_use]
pub fn roles() -> Vec<(&'static str, Vec<&'static str>)> {
    ROLE_NAMES
        .iter()
        .map(|(k, rs)| {
            let fills = rs
                .iter()
                .map(|r| {
                    if r.starts_with('#') || r.starts_with("url(") {
                        *r
                    } else {
                        fill(r)
                    }
                })
                .collect();
            (*k, fills)
        })
        .collect()
}

/// `r` stands wholly inside a built structure of another kind: a room, not a building.
fn room(r: &Mark, structures: &[&Mark]) -> bool {
    structures.iter().any(|s| {
        !std::ptr::eq(*s, r)
            && s.kind != r.kind
            && s.x <= r.x
            && s.y <= r.y
            && r.x2() <= s.x2()
            && r.y2() <= s.y2()
    })
}

/// The kind's largest filled rect that is not a room, or None where it draws none.
///
/// # Errors
/// The sheet's marks refused.
pub fn main_fill<'s>(kind: &str, svg: &'s Sheet) -> Result<Option<&'s Mark>, Error> {
    let rects: Vec<&Mark> = svg
        .marks()?
        .iter()
        .filter(|m| m.tag == "rect" && !matches!(m.fill(), "" | "none") && m.w > 0.0 && m.h > 0.0)
        .collect();
    let structures: Vec<&Mark> = rects
        .iter()
        .copied()
        .filter(|m| is_structure(m.fill()))
        .collect();
    Ok(first_max(
        rects
            .iter()
            .copied()
            .filter(|r| r.kind.as_deref() == Some(kind) && !room(r, &structures)),
        |r| r.w * r.h,
    ))
}

/// Every tabled kind's main fill is one of its role's fills.
///
/// # Errors
/// The sheet's marks refused.
pub fn palette_roles(svg: &Sheet, roles: &[(&str, Vec<&str>)]) -> Result<Vec<String>, Error> {
    let mut out = Vec::new();
    for (kind, allowed) in roles {
        let Some(r) = main_fill(kind, svg)? else {
            continue;
        };
        if !allowed.contains(&r.fill()) {
            let mut sorted = allowed.clone();
            sorted.sort_unstable();
            out.push(format!(
                "the {kind} at svg({},{}) is painted {} - its palette role is {}",
                fixed(r.x, 0),
                fixed(r.y, 0),
                r.fill(),
                sorted.join(" or ")
            ));
        }
    }
    Ok(out)
}
