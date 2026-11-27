//! `builder-brief-hooks` (feature 451 T334; the GM, 2026-11-26: "is this also part of our checklist-based process for kicking off
//! and managing builders? Or do we not have such a checklist? ... I just want to make sure that we're putting the instructions in the
//! right place"): A BUILDER IS DISPATCHED WITH THE BLOCK THE TOOLING MADE. The rules for sizing a builder's brief lived in
//! `scripts/container/builder-brief.md`, a file the coordinating session was to load and remember; on 2026-11-26 it broke them five
//! times with nothing refusing (T285, T298, T316, T308: several jobs, or a measurement and a build, in one brief, each reaching the
//! 300k cap; T315: "one job" that was seven crates and eight levers, ended at 308k). `make builder-brief`
//! (`rust/gate/crates/task/src/builder_brief.rs`) now sizes the brief, takes the pool tree and prints the standing block, whose first
//! line is the marker (`shared::builder_brief`); this guard holds a dispatch to it.
//!
//! A BUILDER DISPATCH: an `Agent` call of an ad-hoc type that can build (`BUILDERS`: none named, `general-purpose`, `claude`) whose
//! prompt names a pool tree - a path some clone's registry holds (`shared::builder_pool`), never a name's shape - or carries a marker
//! line, or holds a line opening `STOP POINT` (`shared::builder_brief::stop_point`; 451 T353: a builder briefed by hand into the
//! session clone names no pool tree - over 2026-11-20..27, 23 dispatches carried the line and named none, every one an Edit/Write
//! into the clone, and none of the 107 that wrote nothing carried it; the 334 in-clone builders before the line existed, 2026-11-25,
//! carried neither and would not be seen). A defined agent (a check) is never one, and neither is the claims round's own dispatch (its prompt opens `Run the claims
//! round`, as `context_cap_hooks/split.rs` reads it), which names the builder's tree to read it.
//!
//! Refused, each printing the command that makes the brief:
//! - no `BUILDER-BRIEF` line of its own (a sentence that mentions the marker is no marker);
//! - a marker whose kind is not one of the four, or whose jobs are past three (a marker edited by hand);
//! - a marker whose tree the pool does not hold for its task - for every task of a bundle (`T=a,b`: one builder, one tree, the
//!   marker naming both);
//! - a `KIND=measurement` brief with a line that orders a source edit. This one is NARROW (`EDITS`): a line opening `Job <n>`,
//!   `Part <n>` or `Step <n>` that holds `fix`, `fixes`, `implement`, `patch`, `build it` or `red-first`. It does NOT catch an edit
//!   ordered in a sentence with no such opening ("then fix what you find"), in a numbered list (`(2) ...`), or in other words
//!   ("change", "add a test"); it would wrongly catch a measurement job whose line uses one of those words of the thing measured.
//!
//! NOT caught at all: a marker typed by hand with a true tree and task (the sizing refusals are the command's); a brief whose jobs
//! outnumber the `JOBS=` its caller stated; a builder briefed with no pool tree named, no marker and no STOP POINT line; a mechanism briefed as one
//! `fix` (the command refuses it from the task's line, which this guard does not read).
//!
//! The escape, checked before any refusal: a prompt line `BUILDER_BRIEF_OK: <reason of two words or more>` (or `="..."`), recorded.
//! A line of its own, as `SESSION_MODEL` is: a brief that quotes the escape in a sentence has not taken it.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::builder_brief::{self, Marker, JOBS_MAX, KINDS};
use crate::shared::builder_pool::{self, Tree};
use crate::shared::escape::enough;
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "builder-brief-hooks",
    events: &["PreToolUse"],
    matcher: "Agent",
    decide,
};

/// The ad-hoc types a builder is dispatched as: the ones that can edit and run. `Explore` and `Plan` cannot edit, and a defined
/// agent's file says what it is.
const BUILDERS: [&str; 3] = ["", "general-purpose", "claude"];

/// The escape's token.
const TOKEN: &str = "BUILDER_BRIEF_OK";

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// The escape on a line of its own, its reason captured.
static ESCAPE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^[ \t]*BUILDER_BRIEF_OK[ \t]*[=:][ \t]*(.*)$"));
/// A line of a measurement brief that orders a source edit (the module's NARROW rule).
static EDITS: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?im)^[ \t]*(?:job|part|step)[ \t]*\d+\b[^\n]*\b(?:fix|fixes|implement|patch|build it|red-first)\b[^\n]*",
    )
});

/// What the guard says of one call.
#[derive(Debug, PartialEq, Eq)]
pub(crate) enum Said {
    /// No builder's dispatch, or one whose marker holds.
    Pass,
    /// Escaped, with its reason.
    Escaped(String),
    /// The escape's line with no reason.
    NoReason,
    /// A builder with no marker: the task and feature its named tree is held for, where one is.
    NoMarker(String, String),
    /// A builder's brief written by hand - a STOP POINT line, no marker, no pool tree named - so it builds in the clone (451 T353).
    Unbriefed,
    /// A marker of no known kind.
    Kind(Marker),
    /// A marker of more jobs than a brief holds.
    Jobs(Marker),
    /// A marker whose tree the pool does not hold for its task: who holds it (`not a pool tree` where none does).
    Tree(Marker, String),
    /// A measurement brief that orders a source edit: the line.
    Edits(Marker, String),
}

/// Does `prompt` name `tree` - its path, ended there?
fn names(prompt: &str, tree: &Path) -> bool {
    let path = tree.to_string_lossy();
    let more = |c: char| c.is_ascii_alphanumeric() || c == '-' || c == '_';
    !path.is_empty()
        && prompt
            .match_indices(path.as_ref())
            .any(|(at, _)| !prompt[at + path.len()..].starts_with(more))
}

/// The reason on the prompt's escape line, quotes dropped; none where no line of its own holds the token.
fn escape(prompt: &str) -> Option<String> {
    let found = ESCAPE.captures(prompt).ok().flatten()?;
    let why = found.get(1).map_or("", |g| g.as_str());
    Some(why.trim().trim_matches(['"', '\'']).trim().to_owned())
}

/// Who holds the marker's tree where it is not the marker's task: none where the pool holds it for that task.
fn not_held(m: &Marker, pool: &[Tree]) -> Option<String> {
    let Some(tree) = pool.iter().find(|t| t.tree == m.tree) else {
        return Some("not a pool tree".to_owned());
    };
    // a bundle's marker names its tasks joined by commas: the tree is held for every one
    let all = m.task.split(',').all(|t| tree.tasks.iter().any(|h| h == t));
    let holds = all && (tree.feature.is_empty() || tree.feature == m.feature);
    (!holds).then(|| format!("held by {}", tree.holder()))
}

pub(crate) fn verdict(input: &Value, pool: &[Tree]) -> Said {
    let null = Value::Null;
    let ti = input.get("tool_input").unwrap_or(&null);
    let prompt = field(ti, "prompt");
    if !matches!(field(input, "tool_name"), "Agent" | "Task")
        || !BUILDERS.contains(&field(ti, "subagent_type"))
        || prompt.trim_start().starts_with("Run the claims round")
    {
        return Said::Pass;
    }
    let marker = builder_brief::parse(prompt);
    let named: Vec<&Tree> = pool.iter().filter(|t| names(prompt, &t.tree)).collect();
    if marker.is_none() && named.is_empty() && !builder_brief::stop_point(prompt) {
        return Said::Pass;
    }
    match escape(prompt) {
        // the refusal's own `<reason ...>` pasted back decides nothing
        Some(why) if enough(&why) && !why.starts_with('<') => return Said::Escaped(why),
        Some(_) => return Said::NoReason,
        None => {}
    }
    let Some(m) = marker else {
        if named.is_empty() {
            return Said::Unbriefed;
        }
        // the tree a task holds, before a neighbor's free one the brief also names
        let held = named.iter().find(|t| !t.free()).unwrap_or(&named[0]);
        return Said::NoMarker(held.tasks.join(","), held.feature.clone());
    };
    if !KINDS.contains(&m.kind.as_str()) {
        return Said::Kind(m);
    }
    if m.jobs > JOBS_MAX {
        return Said::Jobs(m);
    }
    if let Some(holder) = not_held(&m, pool) {
        return Said::Tree(m, holder);
    }
    let edit = EDITS.find(prompt).ok().flatten();
    match edit {
        Some(line) if m.kind == "measurement" => {
            Said::Edits(m, line.as_str().trim().chars().take(120).collect())
        }
        _ => Said::Pass,
    }
}

/// `word`, or `placeholder` where it is empty.
fn or<'a>(word: &'a str, placeholder: &'a str) -> &'a str {
    if word.is_empty() {
        placeholder
    } else {
        word
    }
}

const OUT: &str = "Not a builder, or the block cannot fit this case? A prompt line: BUILDER_BRIEF_OK: <reason, two words or more>";
const ALL: &str = "fix|measurement|build-half|closing-half";

/// The command that makes the brief.
fn made(task: &str, feature: &str, kind: &str) -> String {
    format!(
        "make builder-brief T={} F={} KIND={kind}",
        or(task, "<task>"),
        or(feature, "<feature>")
    )
}

/// The refusal a verdict earns and the rule it is logged under; none for a pass or an escape.
pub(crate) fn refusal(said: &Said) -> Option<(String, &'static str)> {
    Some(match said {
        Said::Pass | Said::Escaped(_) => return None,
        Said::NoReason => (
            format!("BLOCKED (builder-brief): {TOKEN} with no reason. Give one on its line: {TOKEN}: <why this dispatch needs no builder's block, two words or more>"),
            "BUILDER_BRIEF_OK-no-reason",
        ),
        Said::NoMarker(task, feature) => (
            format!("BLOCKED (builder-brief): this dispatch works in a pool tree and its prompt has no BUILDER-BRIEF line.\n\nRun: {} [JOBS=<n>] [MEASURES=<n>] [CRATE=\"<crates>\"]\nand paste what it prints at the head of the brief.\n{OUT}", made(task, feature, ALL)),
            "no-marker",
        ),
        Said::Unbriefed => (
            format!("BLOCKED (builder-brief): this dispatch has a STOP POINT line and no BUILDER-BRIEF line: a builder briefed by hand, to build\nin the session clone with no pool tree and no sizing.\n\nRun: {} [JOBS=<n>] [MEASURES=<n>] [CRATE=\"<crates>\"]\nand paste what it prints at the head of the brief: it takes the task's tree from the pool.\n{OUT}", made("", "", ALL)),
            "stop-point-no-marker",
        ),
        Said::Kind(m) => (
            format!("BLOCKED (builder-brief): KIND={} is no builder's kind.\n\nRun: {}\nand paste what it prints in place of the marker's block.\n{OUT}", m.kind, made(&m.task, &m.feature, ALL)),
            "unknown-kind",
        ),
        Said::Jobs(m) => (
            format!("BLOCKED (builder-brief): JOBS={} - a brief holds at most {JOBS_MAX} jobs.\n\nSplit it, a brief each: {} JOBS=<1-{JOBS_MAX}>\n{OUT}", m.jobs, made(&m.task, &m.feature, &m.kind)),
            "too-many-jobs",
        ),
        Said::Tree(m, holder) => (
            format!("BLOCKED (builder-brief): the marker's tree {} is not held by {} {} in the pool ({holder}).\n\nRun: {}\nIt takes the task's tree from the pool and prints the block with it (make builder-trees lists who holds each).\n{OUT}", m.tree.display(), m.feature, m.task, made(&m.task, &m.feature, &m.kind)),
            "tree-not-held",
        ),
        Said::Edits(m, line) => (
            format!("BLOCKED (builder-brief): a KIND=measurement brief orders a source edit: `{line}`. A measurement changes no source; its report is the next builder's brief.\n\nSend the measurement alone, then: {}\n{OUT}", made(&m.task, &m.feature, "fix")),
            "measurement-edits",
        ),
    })
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let prompt = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "prompt"));
    // no read of any registry for a dispatch that names no clone's tree and no marker
    if !prompt.contains(".clones/")
        && !prompt.contains(builder_brief::MARKER)
        && !prompt.contains(builder_brief::STOP)
    {
        return Vec::new();
    }
    let pool = builder_pool::pools(&session.main().join(".clones"));
    let said = verdict(&event.input, &pool);
    if let Said::Escaped(why) = &said {
        log::fire(
            "builder-brief",
            "escaped",
            why,
            "builder-brief-ok",
            &event.input,
            session,
        );
    }
    let Some((text, rule)) = refusal(&said) else {
        return Vec::new();
    };
    let shown: String = prompt.chars().take(200).collect();
    log::fire(
        "builder-brief",
        "blocked",
        &shown,
        rule,
        &event.input,
        session,
    );
    vec![Answer::Refuse(text)]
}

#[cfg(test)]
mod tests;
