//! `checks-hooks` (feature 375 FR-003(b)(c); feature 449 T048, T86): each check's launch and return, recorded in the state the freeze and the round rule read, and a held plan section written back. It never refuses but the
//! write-back: `after` on a `PostToolUse` of a Bash, Write or Edit call, `launched` on one of an Agent or a `TaskStop`, `returned` on a `SubagentStop`.

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::checks;
use crate::shared::checks::handle;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "checks-hooks",
    events: &["PostToolUse", "SubagentStop"],
    matcher: "Agent|TaskStop|Bash|Write|Edit|MultiEdit",
    decide,
};

const AFTER_TOOLS: [&str; 4] = ["Bash", "Write", "Edit", "MultiEdit"];

fn state_holds_snaps(input: &Value) -> bool {
    let cwd = field(input, "cwd");
    checks::state_path(if cwd.is_empty() { "." } else { cwd })
        .and_then(|p| std::fs::read_to_string(p).ok())
        .is_some_and(|s| s.contains("\"plan_snaps\""))
}

fn decide(event: &Event, _session: &Session) -> Vec<Answer> {
    if event.name == "SubagentStop" {
        let _ = handle::handle("returned", &event.input, None);
        return Vec::new();
    }
    if AFTER_TOOLS.contains(&event.tool()) {
        if !state_holds_snaps(&event.input) {
            return Vec::new();
        }
        let msg = handle::handle("after", &event.input, None);
        return if msg.is_empty() {
            Vec::new()
        } else {
            vec![Answer::Refuse(handle::blocked_text(&msg))]
        };
    }
    let _ = handle::handle("launched", &event.input, None);
    Vec::new()
}

#[cfg(test)]
mod tests;
