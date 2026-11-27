//! The booking's categories (451 T243): the names a wait, an agent's span, a model's turn and a run are booked under, and the make
//! targets each run ran. Split from `book.rs` at the file-size bar (451 T298).

use std::collections::HashMap;

use l7r_shared::guards::event_log_hooks::{agent_category, bucket_of};
use l7r_shared::make::{invoked, DEFAULT_GOAL};

use super::super::super::where_time::columns::{Run, PRECEDENCE};

/// A main session's time with nothing in flight: the prefix of its classes, each named by what came just before and after the gap
/// (the GM 2026-11-25: "as long as that automatically gets broken down in the future"), the rest named unexplained.
pub const NOTHING: &str = "waiting: nothing in flight";
/// A gap while a detached page session ran with no monitor on it: the session was waiting on a queue it did not track.
pub const NOTHING_PAGES: &str =
    "waiting: nothing in flight - a page session running, no monitor on it";
/// A gap after the work its `Stop` named had ended: the wake came after the thing waited on was done.
pub const NOTHING_ENDED: &str =
    "waiting: nothing in flight - after the work its Stop named had ended";
/// A `Stop` naming nothing, then a notification or reminder (a prompt not the GM's) woke the session.
pub const NOTHING_WOKEN: &str =
    "waiting: nothing in flight - until a notification or reminder woke it";
/// A `Stop` naming nothing, then the session started again (a resume, a compaction or a clear).
pub const NOTHING_RESTART: &str = "waiting: nothing in flight - until the session started again";
/// A builder between a stop and its resumption with nothing of its own in flight (451 T345): waiting on whoever resumes it - the
/// session's message, or the notification of work that had already ended.
pub const STOPPED: &str = "builders: stopped, waiting to be resumed";
/// A main session's wait with only a monitor in flight and no page session running.
pub const MONITOR: &str = "waiting: a monitor alone";
/// A detached page session's phases and the research-pass agents.
pub const PAGES: &str = "research and page sessions";
/// The record and pop-up checks' agents.
pub const RECORD: &str = "record and pop-up checks: agents";
/// A builder's time inside its span that no line of its accounts for.
/// Generating maps: a map, sheet or cohort run's remainder, its phases' column, and a builder's scratch sweep (the GM's "generating maps").
pub const MAPS: &str = "map generation";

/// The targets that draw maps or sheets: the guard's table books them tests (`map`, `hamlet`, `compound`, `sheet-render`, the dev
/// loop's own run) or gate (`cohort`, `cohort-landing`, the sweep a landing reads); the breakdown books them all to [`MAPS`].
pub const MAP_TARGETS: [&str; 7] = [
    "map",
    "hamlet",
    "compound",
    "sheet-render",
    "maps-moved",
    "cohort",
    "cohort-landing",
];
pub const UNLINED: &str = "builders: inside its span, no line of its";
/// A command no transcript holds.
pub const UNREAD: &str = "commands no transcript holds";
pub const BOOKED_ELSEWHERE: &str = "Makefile targets the guard's table does not book";
/// The builder pool's own commands: a tree handed out (`make builder-tree`), freed (`make builder-tree-release`) or the trees
/// listed (`make builder-trees`), 451 T298.
pub const POOL: &str = "builder pool (a tree handed out, freed or listed)";
/// A builder's commit carried into the clone (`make carry`): where its task's own table ends (451 T298).
pub const CARRY: &str = "carry into the clone";
/// The targets a main session runs before a push, not for a task: under the mark alone they are the batch's whose span holds them,
/// else the session's own (451 T298: "the session's own make quick before a push is booked to a task").
pub const SESSION_CHECKS: [&str; 2] = ["quick", "done"];

/// The review kind an agent's whole span is booked to, `None` for a builder (451 T243 (f)).
#[must_use]
pub fn review_cat(kind: &str) -> Option<&'static str> {
    Some(match kind {
        "claims-triage" => "claims round: agents",
        "modal-triage" | "source-filter" | "size-exception" => RECORD,
        "escalation-check" => "the GM's filter: agents (escalation-check)",
        "research-pass" => PAGES,
        "work-budget" | "message-check" | "perf-audit" => {
            "other review agents (work-budget, message-check)"
        }
        _ => match agent_category(kind, "") {
            "claims check" => "claims round: agents",
            "record check" => RECORD,
            "review check" => "map and building reviews: agents",
            "spec review" => "plan review: agents",
            "round arbiter" => "arbiter: agents",
            _ => return None,
        },
    })
}

/// A model turn's or a tool's category for actor `who` (`main session` or `builders`), by the tool (`""` the reply).
#[must_use]
pub fn tool_cat(who: &str, tool: &str) -> String {
    let what = match tool {
        "Read" | "Grep" | "Glob" => "reading code".to_owned(),
        "Edit" | "Write" | "NotebookEdit" | "MultiEdit" => "writing code".to_owned(),
        "Bash" => "running a command (the model's turn)".to_owned(),
        "Agent" | "Task" => "dispatching an agent".to_owned(),
        "" => "writing its reply".to_owned(),
        other => format!("other tools ({other})"),
    };
    format!("{who}: {what}")
}

/// The review bucket's kind by target (451 T243 (e)).
#[must_use]
pub fn review_kind(target: &str) -> &'static str {
    match target {
        "decide" | "plan-delta" | "plan-verdict" => "plan review: commands",
        t if t.starts_with("claims-") || t == "impl-check" => "claims round: commands",
        t if t.starts_with("arbiter-") => "arbiter: commands",
        "check-bundle" | "modal-bundle" | "record-owed" | "modal-triage" | "modal-triaged"
        | "modal-prepass" | "translation-owed" | "record-checked" | "record-prepass"
        | "style-prepass" | "quote-verbatim" => "record and pop-up checks: commands",
        _ => "review: other commands",
    }
}

/// The targets a run ran: its line's, else (a line that logged none: a past log, a detector since fixed) the targets its command
/// RUNS, never one it mentions.
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the map `read_subagents` makes")]
pub fn ran(r: &Run, commands: &HashMap<String, String>) -> Vec<String> {
    if !r.makes.is_empty() {
        return r.makes.clone();
    }
    commands.get(&r.id).map_or_else(Vec::new, |c| {
        invoked(c)
            .into_iter()
            .filter(|t| t != DEFAULT_GOAL)
            .collect()
    })
}

/// A run's category (its phases apart) and its label in the per-target table.
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the map `read_subagents` makes")]
pub fn run_cat(r: &Run, commands: &HashMap<String, String>) -> (String, String) {
    let found = ran(r, commands);
    let (makes, bucket) = if r.makes.is_empty() {
        let buckets: Vec<&str> = found.iter().map(|m| bucket_of(m)).collect();
        let first = PRECEDENCE.iter().find(|b| buckets.contains(b));
        (&found[..], first.copied().unwrap_or("other"))
    } else {
        (&r.makes[..], r.bucket)
    };
    // a landing is a landing whatever its command line ran first (451 T298: `make format && make land` was booked `make format`,
    // tests; `make task-start && make land` a spec-kit step, measured 2026-11-26)
    if makes.iter().any(|m| m == "land") {
        return ("landing".to_owned(), "make land".to_owned());
    }
    if bucket != "other" {
        let t = makes
            .iter()
            .find(|m| bucket_of(m) == bucket)
            .map_or("", String::as_str);
        let cat = match bucket {
            _ if MAP_TARGETS.contains(&t) => MAPS,
            "review" => review_kind(t),
            "docs" => "record builds and docs",
            "land" => "landing",
            b => b,
        };
        return (cat.to_owned(), format!("make {t}"));
    }
    if let Some(m) = makes.first() {
        let cat = match m.as_str() {
            // the first tier's remainder (its lint and format; its builds and tests are its own Phase lines, split out before it)
            "crate-checks" | "builder-checks" => "tests",
            "builder-tree" | "builder-tree-release" | "builder-trees" => POOL,
            "carry" => CARRY,
            _ => BOOKED_ELSEWHERE,
        };
        return (cat.to_owned(), format!("make {m}"));
    }
    match commands.get(&r.id) {
        Some(c) => {
            let (cat, label) = super::super::program::class(c);
            (cat.to_owned(), label)
        }
        None => (
            UNREAD.to_owned(),
            "a command no transcript holds".to_owned(),
        ),
    }
}

#[must_use]
pub fn phase_cat(col: &str) -> &str {
    match col {
        "docs" => "record builds and docs",
        "review" => PAGES,
        c => c,
    }
}

#[must_use]
pub fn is_wait(cat: &str) -> bool {
    cat == super::super::program::WAIT || cat == super::super::program::PAGE_WAIT
}
