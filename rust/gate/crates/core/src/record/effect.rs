//! The effect an outside-the-change note must name before it is filed (feature 451 T219).
//!
//! A check's note on something its change did not touch was filed whatever it said: 52 of feature 449's 176 tasks of 2026-11-20 to
//! 11-23 came that way, 22 of them naming nothing wrong (the task audit, 2026-11-24), and its found row 178 says `effect: none on the
//! map` in its own text. A note is filed only when it names a wrong outcome a reader of the map, the sheet or the page would meet,
//! or the user of a tool - a command or check that crashes, hangs, refuses valid input or answers wrongly (constitution XIV: a
//! defect is a wrong outcome, never a difference); the rest are listed and dropped.

use std::sync::LazyLock;

use fancy_regex::Regex;

use super::units::re;

/// The form a filed note ends in, as a refusal prints it.
pub const FORM: &str =
    "effect: <map|sheet|page|tool> - <the wrong outcome its reader or user meets>";

static EFFECT: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?is)\A(.*?)[\s|;.,]*\beffect:\s*((?:map|sheet|page|tool)\s+-\s+\S.*)\z")
});

/// (the note without its effect, the effect) where `note` ends by naming one in [`FORM`]; None where it names none, `effect: none`
/// among them.
#[must_use]
pub fn named(note: &str) -> Option<(String, String)> {
    let m = EFFECT.captures(note.trim()).ok().flatten()?;
    Some((m[1].to_owned(), m[2].trim_end().to_owned()))
}

#[cfg(test)]
mod tests {
    use super::named;

    #[test]
    fn a_note_names_its_effect_or_none() {
        assert_eq!(
            named("the card contradicts itself | effect: map - the place card reads two winds "),
            Some((
                "the card contradicts itself".to_owned(),
                "map - the place card reads two winds".to_owned()
            ))
        );
        assert_eq!(
            named("laps the paddy; Effect: sheet - a belt on the field")
                .unwrap()
                .1,
            "sheet - a belt on the field"
        );
        // constitution XIV's other defect: a tool or check that crashes, hangs, refuses valid input or answers wrongly
        assert_eq!(
            named("the walk skips it | effect: tool - make claims-owed names no claim after a unit is renamed")
                .unwrap()
                .1,
            "tool - make claims-owed names no claim after a unit is renamed"
        );
        for none in [
            "names only the drawn size; effect: none on the map, but the why does not cover the band",
            "the page is silent on the fringe's width",
            "wording | effect: the claim reads loosely",
            "x | effect: page -",
        ] {
            assert_eq!(named(none), None, "{none}");
        }
    }
}
