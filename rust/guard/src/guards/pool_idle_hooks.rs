//! `pool-idle-hooks` (feature 451 T313; the GM, 2026-11-26: "what you are doing sounds like something that we want our tooling to
//! actually enforce. Because otherwise you just have to remember to keep our tasks in flight"): THE COORDINATING SESSION DOES NOT END
//! A TURN OVER A FREE POOL TREE AND A READY TASK. WHY: measured 2026-11-27 (`dev/measurements/2026-11-27/tree-idle/results.md`), the
//! three warm pool trees stood idle 336 of 1,440 tree-minutes (23%) of an eight-hour window with the queue never short - 46 of them
//! with the session stopped, its turn ended.
//!
//! A THIN RULE OVER THE QUEUE: everything it judges is `shared::builder_queue::idle`, which `make builder-next` and `make
//! builder-done` read too - a pool tree of the session's clone stands free, fewer than the settled count of trees are held
//! (`L7R_BUILDERS`, 3, a GUESS knob), and a queue of the clone (`specs/<feature>/queue.txt`) holds a READY entry that overlaps no
//! task in flight. Then the `Stop` is answered `decision: block`, naming the tree, the task and the one command. Where the
//! coordination moves (the GM is weighing a primary session that only orchestrates), the rule moves with the queue: this module
//! holds no state and no reading of its own.
//!
//! IT DOES NOT FIRE: in a builder or any subagent (the event is `Stop`, and a payload with an `agent_id` passes); in a session
//! whose clone has no pool, which is not a feature's coordinator; with every tree held or the count reached; when the queue's open
//! entries wait (on a task, a carry, the GM), or the only READY ones are `waits=alone` while a tree is held; on a queue that cannot
//! be read - a malformed line is `make queue`'s error, recorded here and never a held session.
//!
//! THE ESCAPE, checked first: a line of the session's final message that STARTS `POOL_IDLE_OK: <reason of two words or more>` (the
//! queue's next entries wait on a decision of the GM's; the count is held for a measurement), recorded. A line of its own, as
//! `BUILDER_BRIEF_OK` is: a message that mentions the token in a sentence, after a bullet or in backticks has not taken it, and
//! the block says "start a line".
//!
//! THIS REVERSES A RETIREMENT: 451 T88's rolling-dispatch Stop block and its `L7R_BUILDERS` were retired by 451 T183 (D10) on the
//! GM's "does nothing and adds nothing to the context if we are still active". T313's words are later and ask for the refusal; it
//! is narrower than T88's - it reads a written queue and the pool's registry, never a transcript, and says one command.
// GUARD_EDIT_OK: feature 451 T313 - adding a guard, the pool-idle Stop check over the builders' queue

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::builder_queue::{self, Idle, Verdict};
use crate::shared::escape::enough;
use crate::shared::log::fire;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "pool-idle-hooks",
    events: &["Stop"],
    matcher: "*",
    decide,
};

const TOKEN: &str = "POOL_IDLE_OK";

// GUARD_EDIT_OK: feature 451 T313 - adding a guard, the pool-idle Stop check: its pattern's builder on one line, as builder_brief_hooks' is
fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// The escape, which STARTS its line (only blanks before it), its reason captured.
static ESCAPE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^[ \t]*POOL_IDLE_OK[ \t]*[=:][ \t]*(.*)$"));

/// What the guard says of one stop.
#[derive(Debug, PartialEq, Eq)]
pub(crate) enum Said {
    /// Not held, nothing recorded.
    Quiet,
    /// Not held, recorded: the escape's reason.
    Escaped(String),
    /// The escape with no reason: held.
    NoReason,
    /// Not held, recorded: a queue that cannot be read.
    Unread(String),
    /// Held: the free tree and the entry that would fill it.
    Held(Idle),
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    // a suite names its clone; a session's is the one it resolves to
    let root = crate::shared::env::opt("POOL_IDLE_ROOT").map(std::path::PathBuf::from);
    // (said eagerly: the suites always name their clone, so a closure here is a line no test reaches)
    let clone = root.as_deref().or(session.clone_dir());
    let said = judge(&event.input, clone, builder_queue::builders());
    let log = |kind: &str, detail: &str, rule: &str| {
        fire("pool-idle", kind, detail, rule, &event.input, session);
    };
    match &said {
        Said::Quiet => {}
        Said::Escaped(why) => log("escaped", why, TOKEN),
        Said::NoReason => log(
            "blocked",
            "POOL_IDLE_OK with no reason",
            "POOL_IDLE_OK-no-reason",
        ),
        Said::Unread(why) => log("passed", why, "queue-unread"),
        Said::Held(i) => log(
            "blocked",
            &format!("{} free, {} READY", i.tree.display(), i.tasks),
            "tree-idle",
        ),
    }
    refusal(&said).map(Answer::StopBlock).into_iter().collect()
}

/// The verdict on one stop of the session whose clone is `clone`, the settled count `builders`.
pub(crate) fn judge(input: &Value, clone: Option<&Path>, builders: usize) -> Said {
    // a builder or any subagent is not the coordinator
    if !field(input, "agent_id").is_empty() {
        return Said::Quiet;
    }
    let Some(clone) = clone else {
        return Said::Quiet;
    };
    let message = field(input, "last_assistant_message");
    if let Ok(Some(m)) = ESCAPE.captures(message) {
        let why = m
            .get(1)
            .map_or("", |g| g.as_str())
            .trim()
            .trim_matches(['"', '\'']);
        return if enough(why) {
            Said::Escaped(why.to_owned())
        } else {
            Said::NoReason
        };
    }
    match builder_queue::idle(clone, builders) {
        Verdict::Quiet => Said::Quiet,
        Verdict::Unread(why) => Said::Unread(why),
        Verdict::Idle(i) => Said::Held(i),
    }
}

/// The block a held stop reads; none where the stop passes.
pub(crate) fn refusal(said: &Said) -> Option<String> {
    match said {
        Said::Quiet | Said::Escaped(_) | Said::Unread(_) => None,
        Said::NoReason => Some(format!(
            "pool-idle: {TOKEN} with no reason. Start a line with: {TOKEN}: <why the free tree stays free, two words or more>\n"
        )),
        Said::Held(i) => Some(held(i)),
    }
}

/// A held stop's block: an open performance task no queue line names FIRST, with the command that writes its line (451 T313's
/// round-3 ruling), then the READY entry and its one command.
fn held(i: &Idle) -> String {
    let tree = i.tree.display();
    let mut out = match i.unlisted.first() {
        None => format!("pool-idle: {tree} is free and "),
        Some(u) => {
            let more = match i.unlisted.len() - 1 {
                0 => String::new(),
                n => format!(" ({n} more: make builder-next names them)"),
            };
            format!("pool-idle: {tree} is free. FIRST, {} is open performance work with no queue line{more}. Write its line - CRATE= and FILES= as its task line names them, WAITS= where it waits, which quiets it:\n  {}\n", u.tasks, u.command)
        }
    };
    if !i.command.is_empty() {
        let then = if i.unlisted.is_empty() { "" } else { "Then " };
        let _ = write!(out, "{then}{} is READY, overlapping no task in flight. Hand it out before this turn ends:\n  {}\n", i.tasks, i.command);
        // GUARD_EDIT_OK: feature 451 T481 - a fix command make builder-brief refuses is said with make queue's flag under it
        out.push_str(&i.flag);
    }
    out + &format!(
        "Or start a line of your final message with: {TOKEN}: <why not, two words or more>\n"
    )
}

#[cfg(test)]
mod tests;
