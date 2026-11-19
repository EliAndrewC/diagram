//! `gate-hooks` (features 152, 162; ported from `scripts/hooks/gate-hooks.sh`, feature 449 T007): a command running both `make quick` and
//! `make done` is rewritten to `done` alone, its superset. `GATE_OK` with a reason stands the guard aside. The refusal's words are the
//! shell's; the reasons behind each rule stand in its comments, kept in git history.
//!
//! Its other half - a `-k` SUBSET of a pytest file (`make test-file K=` or a `::` node id) armed a flag, and a `make done` while it stood
//! was refused once - left with pytest and its targets (feature 449 T213): no command can run a subset any more, so nothing arms it.
//!
//! Plan T007's decisions: (a) `hm_make.py`'s parts it reads are `shared::make`; (b) the command is read as JSON, not the shell's
//! greedy `sed` (constitution XIV).

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::make::combine;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "gate-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

/// What a combined command is told (feature 162).
const COMBINED: &str =
    "`make quick` was dropped from this command and `make done` runs alone: done is a superset \
(the same lint, format and typecheck, and a strict superset of the tests), so nothing you \
asked has gone unasked. Combined rather than refused because a refusal would have cost a \
model round trip to save one warm quick (4.1 s measured).";

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    if event.tool() != "Bash" {
        return Vec::new();
    }
    let ti = event
        .input
        .get("tool_input")
        .cloned()
        .unwrap_or(Value::Null);
    let cmd = field(&ti, "command");
    let log = |kind: &str, detail: &str, rule: &str| {
        fire("gate", kind, detail, rule, &event.input, session);
    };
    let shown: String = cmd.chars().take(200).collect();
    match escape_or_refuse(cmd, "GATE_OK") {
        Escape::Escaped(why) => {
            log("escaped", &why, "gate-ok");
            return Vec::new();
        }
        Escape::Refused(text) => {
            log("blocked", &shown, "GATE_OK-no-reason");
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    if let Some(combined) = combine(cmd) {
        log("rewrote", &shown, "");
        let mut rewritten = ti.clone();
        rewritten["command"] = Value::String(combined);
        return vec![
            Answer::Rewrite(rewritten),
            Answer::Notice(COMBINED.to_owned()),
        ];
    }
    Vec::new()
}

#[cfg(test)]
mod tests;
