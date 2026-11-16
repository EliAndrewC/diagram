//! What an ABSENCE note says to its reader (`record/absence.py`, feature 292; ported by feature 449 T144): the one place its opening words
//! are kept. A note keeps the short marker every script classifies by; the assembly shows `LEAD` in its place, the marker hidden in a span,
//! and `unrender` gives a reader of the raw markup the note as it was written.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::is_space;

use crate::re;

/// The words every absence note opens with, as its reader sees them (the GM, 2026-09-29).
pub const LEAD: &str =
    "Our research of publicly-available sources couldn't find anything conclusive:";
pub const MARKER: &str = "no publicly readable source";
static RENDERED: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r#"<span class="sep">{MARKER}</span><span class="absence-lead">[^<]*</span>"#
    ))
});

/// A note's body as the page shows it: an absence note's marker hidden and `LEAD` shown; any other note unchanged.
#[must_use]
pub fn render(body: &str) -> String {
    let stripped = body.trim_start_matches(is_space);
    if !stripped.starts_with(MARKER) {
        return body.to_owned();
    }
    let at = body.len() - stripped.len();
    format!(
        r#"{}<span class="sep">{MARKER}</span><span class="absence-lead">{LEAD}</span>{}"#,
        &body[..at],
        &body[at + MARKER.len()..]
    )
}

/// The note as it was written - the marker bare - from a rendered page.
#[must_use]
pub fn unrender(body: &str) -> String {
    RENDERED.replacen(body, 1, MARKER).into_owned()
}

#[cfg(test)]
mod tests;
