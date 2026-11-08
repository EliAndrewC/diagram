//! `record-edit-gate` (feature 449 T053; the round arbiter's ruling `ask:449-hm-checks-route`): THE TEST OF WHETHER A CALL CONCERNS THE RECORD-EDIT GUARD, IN RUST. `record-edit-hooks.sh` and the libraries under it
//! move to phase 3 with their Python callers, so that one implementation writes `checks-open.json`; until then that guard started Python on every Bash call and Edit. This gate answers without a process for a call that
//! cannot concern it - no plan review holding text, a command that names no landing of edits and runs no gate, a file that is no record page - and runs the shell guard, as it stands, for one that can.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "record-edit-gate",
    events: &["PreToolUse"],
    matcher: "Edit|Write|Bash",
    decide,
};

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

/// The common git directory of the clone holding `from` (`hm_checks.state_path`, without a process): a `.git` file (a worktree) through its gitdir and `commondir`.
fn git_dir(from: &Path) -> Option<PathBuf> {
    let (owner, dot) = from
        .ancestors()
        .find_map(|d| Some((d, Some(d.join(".git")).filter(|g| g.exists())?)))?;
    if dot.is_dir() {
        return Some(dot);
    }
    let text = std::fs::read_to_string(&dot).ok()?;
    let gitdir = owner.join(text.trim().strip_prefix("gitdir:")?.trim());
    let common = std::fs::read_to_string(gitdir.join("commondir"))
        .map_or_else(|_| gitdir.clone(), |c| gitdir.join(c.trim()));
    Some(common)
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
    git_dir(from).is_some_and(|dir| {
        std::fs::read_to_string(dir.join("checks-open.json")).is_ok_and(|s| holds_text(&s))
    })
}

/// The mode to run the shell guard in, or None for a call that cannot concern it.
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

/// The shell guard's reply as this binary's answers.
fn answers(code: i32, out: &str, err: &str) -> Vec<Answer> {
    if code == 2 {
        return vec![Answer::Refuse(err.trim_end().to_owned())];
    }
    let parsed: Value = serde_json::from_str(out).unwrap_or_default();
    let Some(said) = parsed.get("hookSpecificOutput") else {
        return Vec::new();
    };
    let rewrite = said.get("updatedInput").map(|v| Answer::Rewrite(v.clone()));
    let notice = said
        .get("additionalContext")
        .and_then(Value::as_str)
        .map(|t| Answer::Notice(t.to_owned()));
    rewrite.into_iter().chain(notice).collect()
}

pub(crate) fn judge(event: &Event, here: &Path, tree: &Path) -> Vec<Answer> {
    let given = field(&event.input, "cwd");
    let from = if given.is_empty() {
        here
    } else {
        Path::new(given)
    };
    let Some(mode) = mode_for(event, from) else {
        return Vec::new();
    };
    let script = tree.join("scripts/hooks/record-edit-hooks.sh");
    let said = ask(
        here,
        "bash",
        &[&script.to_string_lossy(), mode],
        &event.input.to_string(),
    );
    answers(said.code, &said.out, &said.err)
}

fn decide(event: &Event, _session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(event, &here, &tree)
}

#[cfg(test)]
mod tests;
