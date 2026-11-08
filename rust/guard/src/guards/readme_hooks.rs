//! `readme-hooks` (constitution XVII; ported from the shell of the same name, feature 449 T032): A SESSION DOES NOT WRITE A README. A README is
//! not loaded into a session's context; a directory `CLAUDE.md` is, automatically, whenever work happens in that directory, so anything a README
//! holds is invisible to the next session unless it happens to look. `README_OK` with a reason that quotes the GM's authorization is the escape.

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "readme-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FILE: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)(^|/)README(\.[A-Za-z0-9]+)?$"));
static WRITES: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)(?:>>?\s*|sed\s+-i\b[^;|&]*?|tee\s+(?:-a\s+)?|cp\s+\S+\s+|mv\s+\S+\s+)[\w./-]*README(?:\.[A-Za-z0-9]+)?(?=\s|$)",
    )
});
static PY_WRITE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?i)README(?:\.[A-Za-z0-9]+)?['"]\s*\)?\s*\)?\s*\.write_text"#));

/// What would write a README, or None.
pub(crate) fn hit(event: &Event) -> Option<String> {
    let input = event.input.get("tool_input")?;
    if ["Write", "Edit", "NotebookEdit"].contains(&event.tool()) {
        let path = field(input, "file_path");
        return FILE
            .is_match(path)
            .unwrap_or(false)
            .then(|| path.to_owned());
    }
    let cmd = field(input, "command");
    [&*WRITES, &*PY_WRITE]
        .iter()
        .find_map(|r| r.find(cmd).ok().flatten().map(|m| m.as_str().to_owned()))
}

fn shown(event: &Event) -> String {
    let input = event.input.get("tool_input");
    let text = input.map_or("", |t| {
        Some(field(t, "command"))
            .filter(|c| !c.is_empty())
            .unwrap_or(field(t, "file_path"))
    });
    text.chars().take(200).collect()
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    match escape_or_refuse(cmd, "README_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "readme",
                "escaped",
                &why,
                "gm-authorized",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "readme",
                "blocked",
                &shown(event),
                "README_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    let Some(found) = hit(event) else {
        return Vec::new();
    };
    log::fire(
        "readme",
        "blocked",
        &shown(event),
        "readme-is-the-gm-s",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "BLOCKED: writing a README ({found}).\n\n\
A README is not loaded into a session's context. A directory CLAUDE.md is - automatically, whenever\n\
work happens in that directory. So anything you would put in a README is invisible to the next\n\
session unless it happens to look, which is to say by luck.\n\n\
Put it where it will actually be read:\n\n  \
- a CLAUDE.md in the directory it governs, for a rule that must be known while working there\n  \
- a topic doc referenced from a CLAUDE.md, when it is long enough that always loading it is waste\n\n\
WHAT THIS COST, once: dev/perf-log/README.md carried \"an append-only shared log must be a DIRECTORY,\n\
because concurrent clones conflict on every push\". A session read that file, quoted it, and hours\n\
later created a single-file run-log.jsonl. Had it been a CLAUDE.md the rule would have been in\n\
context when it mattered. It is one now.\n\n\
A README is written by a human for a human; if the GM wants one, the GM writes it. The one escape is\n\
the GM delegating an edit in their own words: README_OK in the command, with a reason that quotes the\n\
authorization (GM 2026-09-06, the research/ link table) - it is recorded, and `make audit` shows it.\n\n\
(rust/guard/src/guards/readme_hooks.rs; constitution XVII, GM 2026-08-24)"
    ))]
}

#[cfg(test)]
mod tests;
