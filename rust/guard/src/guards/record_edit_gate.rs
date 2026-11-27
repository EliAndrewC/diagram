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
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

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

/// Whether a plan review holds text now: `plan_holds` non-empty, as `hm_checks._handle` asks (a snapshot's copy of the key is escaped, so
/// it does not match); with no repository there is no state, so no hold. The state streamed to its key, not read whole: this runs on
/// every Bash call (451 T508, `checks::scan`).
fn holding(from: &Path) -> bool {
    checks::state_path(&from.to_string_lossy()).is_some_and(|p| checks::scan::holds(&p))
}

/// `pretool-bash` or `pretool`, or None for a call that cannot concern the guard.
pub(crate) fn mode_for(event: &Event, from: &Path) -> Option<&'static str> {
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    if event.tool() == "Bash" {
        let cmd = field(input, "command");
        return (holding(from)
            || cmd.contains("apply-edits")
            // the gate as `checks::handle` reads it, through the one make detector (feature 451 D1): the arbiter's holds refuse it
            || (cmd.contains("done") && crate::shared::make::invoked(cmd).iter().any(|t| t == "done")))
        .then_some("pretool-bash");
    }
    let file = field(input, "file_path");
    (found(&RECORD_FILE, file) || (found(&PLAN_FILE, file) && holding(from))).then_some("pretool")
}

#[cfg(test)]
mod tests;
