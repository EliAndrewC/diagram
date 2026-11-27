//! A plan section's "Performance work?" line that answers no of a measurement, refused at `make decide` (feature 451 T410).
//!
//! WHY: FR-013 counts work that measures where the time goes as performance work for the ordering, though it speeds nothing itself
//! (the GM 2026-11-20), and the section template's prompt defined a `[perf]` task only as one that makes something faster. On
//! 2026-11-26/27 five plan reviews blocked a round on a section answering "no: a measurement" - T315, T274, T301 and two the
//! coordinating session headed off by brief - each a round of minutes a script can see coming. The template now names the clause
//! (`template.rs`); this is the refusal for a section that answers no all the same.

/// What opens the line.
const PROMPT: &str = "**Performance work?**";

/// The sentence the refusal prints to write in the line's place.
pub(super) const WRITE: &str = "**Performance work?** yes - a `[perf]` task under 451 FR-013's measurement clause: it measures where time goes and speeds nothing itself.";

/// Each line of `section` that opens with the prompt (after its indent and a list dash), answers no and holds the word `measurement` (or its plural; a path such as `dev/measurements/` is no word): its offset and its text. The
/// answer's first word decides it (`no`, whatever its case, and no longer word such as `none` or `not`), so the template's own
/// unfilled prompt (`<no - or yes ...`) is no answer and a `yes` that names a measurement passes.
pub(super) fn measured_no(section: &str) -> Vec<(usize, String)> {
    let mut at = 0;
    let mut out = Vec::new();
    for line in section.split('\n') {
        let lower = line.to_lowercase();
        let opens = lower.trim_start().trim_start_matches("- ");
        let answer = opens
            .strip_prefix(&PROMPT.to_lowercase())
            .map(str::trim_start);
        let no = answer
            .and_then(|a| a.strip_prefix("no"))
            .is_some_and(|rest| !rest.starts_with(char::is_alphanumeric));
        // the word, never a path that holds it (`dev/measurements/...`)
        let word = |c: char| c.is_alphanumeric() || "/-_".contains(c);
        let named = lower
            .split(|c| !word(c))
            .any(|w| w == "measurement" || w == "measurements");
        if no && named {
            out.push((at, line.chars().take(160).collect()));
        }
        at += line.len() + 1;
    }
    out
}
