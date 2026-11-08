//! `source-block-hooks` (constitution V, NON-NEGOTIABLE; ported from the shell of the same name, feature 449 T037): THE GM'S OWN WRITING IS NOT EDITABLE. Text
//! between the SOURCE markers is the GM's original prose. An Edit whose anchor lies inside such a block, or a Write that does not keep every block the file
//! already had, is refused, judged against the file on disk. `SOURCE_EDIT_OK` with the GM's instruction as its reason is the escape, recorded.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{enough, reason};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "source-block-hooks",
    events: &["PreToolUse"],
    matcher: "Edit|Write|NotebookEdit",
    decide,
};

const TOKEN: &str = "SOURCE_EDIT_OK";

static BLOCK: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?si)<!--\s*SOURCE: GM NOTES.*?<!--\s*END SOURCE\s*-->")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// What the call would do to a block, or None.
pub(crate) fn report(path: &str, old: &str, new: &str) -> Option<String> {
    let disk = std::fs::read_to_string(path).ok()?;
    let name = Path::new(path)
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let blocks: Vec<&str> = BLOCK
        .find_iter(&disk)
        .flatten()
        .map(|m| m.as_str())
        .collect();
    let anchor = old.trim();
    if !anchor.is_empty() && blocks.iter().any(|b| b.contains(anchor)) {
        return Some(format!(
            "an Edit whose anchor lies inside a SOURCE block in {name}"
        ));
    }
    let missing = blocks.iter().filter(|b| !new.contains(**b)).count();
    (!new.is_empty() && missing > 0)
        .then(|| format!("a Write that would change or drop {missing} SOURCE block(s) in {name}"))
}

const NO_REASON: &str = "BLOCKED: SOURCE_EDIT_OK with no reason given.

This escape permits an edit to the GM S OWN WRITING (constitution V: only they may change
it). Say what they told you, in the edit, so the record shows it:

    SOURCE_EDIT_OK: <what the GM asked for, in their words>";

fn refusal(what: &str) -> String {
    format!(
        "BLOCKED: {what}

That text is the GM's own writing. Constitution V (NON-NEGOTIABLE): content between
<!-- SOURCE: GM NOTES - DO NOT MODIFY --> and <!-- END SOURCE --> must never be modified, rephrased,
summarized, reworded, or \"improved\". Only the GM edits it.

This includes edits that feel like housekeeping:

  - \"fixing\" a British spelling. Their prose is theirs; house style governs OUR text, not theirs.
  - rewrapping, re-punctuating, or tightening a sentence.
  - updating a SOURCE block to match the current l7r.md. Drift is EXPECTED - a block is a frozen
    point-in-time snapshot, not a live mirror. The canonical for any topic is always l7r.md.

If the GM has actually told you to edit it, put SOURCE_EDIT_OK in the edit with their instruction, so
the reason is in the diff.

(rust/guard/src/guards/source_block_hooks.rs; constitution V)"
    )
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let Some(input) = event.input.get("tool_input") else {
        return Vec::new();
    };
    let (path, old) = (field(input, "file_path"), field(input, "old_string"));
    let new = field(input, "content");
    let shown: String = path.chars().take(200).collect();
    let written = format!("{}{new}", field(input, "new_string"));
    if written.contains(TOKEN) {
        let why = reason(&written, TOKEN);
        if enough(&why) {
            log::fire(
                "source-block",
                "escaped",
                &why,
                "source-edit-ok",
                &event.input,
                session,
            );
            return Vec::new();
        }
        log::fire(
            "source-block",
            "blocked",
            &shown,
            "SOURCE_EDIT_OK-no-reason",
            &event.input,
            session,
        );
        return vec![Answer::Refuse(NO_REASON.to_owned())];
    }
    let Some(what) = report(path, old, new) else {
        return Vec::new();
    };
    log::fire(
        "source-block",
        "blocked",
        &shown,
        "gm-source-block",
        &event.input,
        session,
    );
    vec![Answer::Refuse(refusal(&what))]
}

#[cfg(test)]
mod tests;
