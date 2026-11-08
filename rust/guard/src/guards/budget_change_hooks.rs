//! `budget-change-hooks` (feature 443 FR-005; ported from the shell of the same name and `lib/hm_budget.py`, feature 449 T026): A WORK BUDGET
//! CHANGES ONLY WITH THE GM'S OWN WORDS. `make budget-change` and `make budget-program` cannot read the session's transcript; a hook can, so
//! their `WORDS=` is checked here as an approval line is: three words or more, verbatim in a message the GM wrote in this session.

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::guards::feature_approval_hooks::problem;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::make::targets;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "budget-change-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

const GUARDED: [&str; 2] = ["budget-change", "budget-program"];

static WORDS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?<![\w-])WORDS=(?:"([^"]*)"|'([^']*)'|(\S+))"#)
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// Nothing when `cmd` invokes no guarded target or its WORDS are the GM's; else why not.
pub(crate) fn verdict(cmd: &str, messages: &[String]) -> &'static str {
    if !targets(cmd).iter().any(|t| GUARDED.contains(&t.as_str())) {
        return "";
    }
    let found = WORDS.captures(cmd).ok().flatten();
    let words = found
        .as_ref()
        .and_then(|c| c.get(1).or_else(|| c.get(2)).or_else(|| c.get(3)))
        .map_or("", |m| m.as_str());
    if words.trim().is_empty() {
        return "no-words";
    }
    problem(
        &format!("**Approved**: the GM, 2000-01-01, \"{words}\""),
        messages,
    )
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    if !GUARDED.iter().any(|g| cmd.contains(g)) {
        return Vec::new();
    }
    let bad = verdict(cmd, session.gm_messages());
    if bad.is_empty() {
        return Vec::new();
    }
    log::fire(
        "budget-change",
        "blocked",
        "budget",
        bad,
        &event.input,
        session,
    );
    let why = match bad {
        "no-words" => "no WORDS= given",
        "short" => "WORDS is under three words - a bare \"yes\" approves nothing",
        _ => "the WORDS are in no message the GM wrote in this session",
    };
    vec![Answer::Refuse(format!(
        "\n\u{1b}[1mBLOCKED: a work budget changes only with the GM's own words (feature 443, FR-005).\u{1b}[0m\n  {why}\n\n\
Ask the GM (through escalation-check), then quote the words verbatim:\n  \
make budget-change PHASE=<stage> TO=<per thing> [EXPONENT=<e>] WORDS=\"<the GM's words>\"\n  \
make budget-program OPS_AT_40=<ops> EXPONENT=<e> WORDS=\"<the GM's words>\"\n"
    ))]
}

#[cfg(test)]
mod tests;
