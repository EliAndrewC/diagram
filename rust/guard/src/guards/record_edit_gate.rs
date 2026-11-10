//! The record-edit guard's prefilter (feature 449 T053, T86): whether a call can concern the guard at all - no plan review holding text, a command that names no landing of edits and runs no gate, a file that is no
//! record page - answered without a process. `record_edit_hooks` runs the rest in Rust.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::Event;
use crate::shared::checks;
use crate::shared::state::field;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

// `hm_checks._handle`'s `make done` test, verbatim: the arbiter's holds refuse the gate.
static MAKE_DONE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)(?:^|[;&|(]\s*)(?:[A-Z_]+=\S*\s+)*make\s+(?:-\S+\s+)*done\b"));
// The files `hm_checks.subject_of_path` freezes and `hm_record.page_dir_for` re-aims.
static RECORD_FILE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?:^|/)research/.*\.html$|interactive/assets/modals/.*\.md$|interactive/assets/glossary\.json$",
    )
});

// While a plan review holds text, the file an Edit could change it through.
static PLAN_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"(?:^|/)specs/[^/]+/plan\.md$"));

fn found(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// `plan_holds` non-empty, as `hm_checks._handle` asks (the key stays, empty, after every hold; a snapshot's copy of this text is escaped, so it does not match). A scan, not a
/// pattern: the state file can be large, and this runs on every Bash call.
fn holds_text(state: &str) -> bool {
    state
        .split_once("\"plan_holds\":")
        .is_some_and(|(_, rest)| {
            rest.trim_start()
                .strip_prefix('{')
                .is_some_and(|inner| !inner.trim_start().starts_with('}'))
        })
}

/// Whether a plan review holds text now (`checks-hooks.sh after` asks the same of the same file); with no repository there is no state, so no hold.
fn holding(from: &Path) -> bool {
    checks::state_path(&from.to_string_lossy())
        .is_some_and(|p| std::fs::read_to_string(p).is_ok_and(|s| holds_text(&s)))
}

/// `pretool-bash` or `pretool`, or None for a call that cannot concern the guard.
pub(crate) fn mode_for(event: &Event, from: &Path) -> Option<&'static str> {
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    if event.tool() == "Bash" {
        let cmd = field(input, "command");
        return (holding(from)
            || cmd.contains("apply-edits")
            || (cmd.contains("done") && found(&MAKE_DONE, cmd)))
        .then_some("pretool-bash");
    }
    let file = field(input, "file_path");
    (found(&RECORD_FILE, file) || (found(&PLAN_FILE, file) && holding(from))).then_some("pretool")
}

#[cfg(test)]
mod tests;
