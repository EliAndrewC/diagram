//! `phase-source-hooks` (feature 444; ported from the shell of the same name and `lib/hm_phase_source.py`, feature 449 T046): A STAGE BEING REBUILT
//! IS WRITTEN FROM ITS DERIVATION, NEVER READ FROM ITS OLD CODE (the GM, 2026-10-30: "we are not trying to re-implement the same algorithms, because
//! the old algorithms were computationally inefficient"). While `make task-start` holds a phase task's old modules, a read of one is refused: a Read,
//! a Glob aimed at it or its directory, a shell command naming it with a read verb, and (T204) a search - the Grep tool, a shell grep, rg, ag, git
//! grep or a find running one - whose path reaches it and whose flags do not leave it out (`search.rs`). A mention is not a read, nor is `make
//! phase-read` or a git listing of names and counts (T204). The refusal names the derivation the task recorded (its block's `derivation:` line, or
//! the derivation its prose cites), only where that file is in the checkout, never an invented path (T204). `PHASE_SOURCE_OK` with a reason is the
//! escape.

mod search;

use std::path::Path;
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::Value;

use crate::guards::finished_run_hooks::runs::realpath;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::{self, civil};
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "phase-source-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Read|Grep|Glob",
    decide,
};

const DEFAULT_GLOB: &str =
    "/diagram/.git/phase-sources.json /diagram/.clones/*/.git/phase-sources.json";

static VERB: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r"(?:^|[\s;&|(`$])(?:cat|sed|head|tail|less|more|grep|rg|ugrep|awk|nl|bat|python3?|git\s+(?:show|diff|log|blame))\b")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// Whether a pattern with at most one `*` path component matches a file (`compgen -G`, for the shapes this guard is given).
fn any_match(patterns: &str) -> bool {
    patterns
        .split_whitespace()
        .any(|pattern| match pattern.split_once('*') {
            None => Path::new(pattern).exists(),
            Some((head, tail)) => std::fs::read_dir(head).is_ok_and(|d| {
                d.filter_map(Result::ok)
                    .any(|e| Path::new(&format!("{}{tail}", e.path().display())).exists())
            }),
        })
}

/// The held state, and the checkout it is for: `make task-start` wrote it and the task's box is still open.
fn state_for(cwd: &str) -> Option<(String, Value)> {
    let said = ask(
        Path::new("/"),
        "git",
        &[
            "-C",
            cwd,
            "rev-parse",
            "--show-toplevel",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        "",
    );
    let mut lines = said.out.lines();
    let (top, common) = (lines.next()?.to_owned(), lines.next()?.to_owned());
    let state: Value = serde_json::from_str(
        &std::fs::read_to_string(Path::new(&common).join("phase-sources.json")).ok()?,
    )
    .ok()?;
    let tasks = std::fs::read_to_string(
        Path::new(&top)
            .join("specs")
            .join(field(&state, "feature"))
            .join("tasks.md"),
    )
    .ok()?;
    let open = format!("- [ ] {}", field(&state, "task"));
    let boxed = tasks.lines().any(|l| {
        l.strip_prefix(&open)
            .is_some_and(|rest| !rest.starts_with(|c: char| c.is_alphanumeric() || c == '_'))
    });
    boxed.then_some((top, state))
}

/// The time now, as `make phase-read`'s `until` writes it.
fn stamp() -> String {
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn allowed(state: &Value, rel: &str, now: &str) -> bool {
    state
        .get("allow")
        .and_then(Value::as_array)
        .is_some_and(|a| {
            a.iter()
                .any(|x| field(x, "file") == rel && field(x, "until") > now)
        })
}

fn parent_of(file: &str) -> &str {
    file.rsplit_once('/').map_or(".", |(p, _)| p)
}

/// The held file `path` names - itself, or with `dirs` the directory holding it.
fn held_path(top: &str, path: &str, cwd: &str, files: &[&str], dirs: bool) -> Option<String> {
    let full = realpath(&Path::new(cwd).join(path));
    let rel = full
        .strip_prefix(realpath(Path::new(top)))
        .ok()?
        .to_string_lossy()
        .into_owned();
    files
        .iter()
        .find(|f| rel == **f || (dirs && !rel.is_empty() && parent_of(f) == rel))
        .map(|f| (*f).to_owned())
}

/// The held file a shell command reads.
fn held_in_command(cmd: &str, files: &[&str]) -> Option<String> {
    if !VERB.is_match(cmd).unwrap_or(false) {
        return None;
    }
    files
        .iter()
        .find(|f| {
            let named =
                crate::shared::regex::build(&format!(r"(?<![\w.-]){}\b", fancy_regex::escape(f)))
                    .unwrap_or_else(|e| unreachable!("{e}"));
            let dir = crate::shared::regex::build(&format!(
                r#"(?<![\w.-]){}/?(?=[\s'"]|$)"#,
                fancy_regex::escape(parent_of(f))
            ))
            .unwrap_or_else(|e| unreachable!("{e}"));
            named.is_match(cmd).unwrap_or(false) || dir.is_match(cmd).unwrap_or(false)
        })
        .map(|f| (*f).to_owned())
}

/// What this call reads of the held code: one file, or the files a search reaches.
#[derive(Debug)]
enum Hit {
    Read(String),
    Search(search::Found),
}

/// What this call reads of the held code, with the state and the checkout, or None. A file `make phase-read` let through is not held.
fn verdict(event: &Event, cwd: &str, now: &str) -> Option<(Hit, Value, String)> {
    let (top, state) = state_for(cwd)?;
    let input = event.input.get("tool_input")?;
    let files: Vec<&str> = state
        .get("files")?
        .as_array()?
        .iter()
        .filter_map(Value::as_str)
        .filter(|f| !allowed(&state, f, now))
        .collect();
    let hit = match event.tool() {
        "Read" => held_path(&top, field(input, "file_path"), cwd, &files, false).map(Hit::Read),
        "Glob" => Some(field(input, "path"))
            .filter(|p| !p.is_empty())
            .and_then(|p| held_path(&top, p, cwd, &files, true))
            .map(Hit::Read),
        "Grep" => search::grep_tool(input, cwd, &top, &files).map(Hit::Search),
        _ => match search::shell(field(input, "command"), cwd, &top, &files) {
            Err(found) => Some(Hit::Search(found)),
            Ok(rest) => held_in_command(&rest, &files).map(Hit::Read),
        },
    }?;
    Some((hit, state, top))
}

/// Where to write the stage from: the derivation the task recorded, or feature 444's `phases/<stage>_greenfield.derivation.md`, only
/// where the file is in the checkout - otherwise where to look, never an invented path (T204: T202's refusal named a `phases/` file
/// that never existed, where its derivation was `derivations/T198-placer.md`).
fn derivation_line(top: &str, state: &Value) -> String {
    let (phase, feature, task) = (
        field(state, "phase"),
        field(state, "feature"),
        field(state, "task"),
    );
    let named = field(state, "derivation");
    let greenfield = format!("specs/{feature}/phases/{phase}_greenfield.derivation.md");
    if let Some(path) = [named, greenfield.as_str()]
        .into_iter()
        .find(|p| !p.is_empty() && Path::new(top).join(p).is_file())
    {
        return format!("Write it from:  {path}  (its Contract and Minimal algorithm)");
    }
    let missing = if named.is_empty() {
        String::new()
    } else {
        format!(" ({named}, which is not in the checkout)")
    };
    format!(
        "Write it from its derivation - {task}'s block names no derivation in the checkout{missing}: look in its block in\n\
specs/{feature}/tasks.md and its section of specs/{feature}/plan.md (a `derivation: <path>` line on the block is what\n\
`make task-start` records for this message)"
    )
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let glob = std::env::var("PHASE_SOURCE_GLOB").unwrap_or_else(|_| DEFAULT_GLOB.to_owned());
    judge(event, session, &here.to_string_lossy(), &glob, &stamp())
}

pub(crate) fn judge(
    event: &Event,
    session: &Session,
    here: &str,
    glob: &str,
    now: &str,
) -> Vec<Answer> {
    if !any_match(glob) {
        return Vec::new();
    }
    let base = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or(here);
    let Some((hit, state, top)) = verdict(event, base, now) else {
        return Vec::new();
    };
    let (phase, feature, task) = (
        field(&state, "phase"),
        field(&state, "feature"),
        field(&state, "task"),
    );
    let input = event.input.get("tool_input");
    let cmd = input.map_or("", |t| field(t, "command"));
    let shown: String = input
        .map_or("", |t| {
            Some(field(t, "command"))
                .filter(|c| !c.is_empty())
                .unwrap_or(field(t, "file_path"))
        })
        .chars()
        .take(200)
        .collect();
    match escape_or_refuse(cmd, "PHASE_SOURCE_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "phase-source",
                "escaped",
                &why,
                phase,
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "phase-source",
                "blocked",
                &shown,
                "PHASE_SOURCE_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    log::fire(
        "phase-source",
        "blocked",
        &shown,
        phase,
        &event.input,
        session,
    );
    let write_from = derivation_line(&top, &state);
    let (head, file) = match &hit {
        Hit::Read(file) => (
            format!("BLOCKED: {file} is the old code of `{phase}`, and {feature} {task} rebuilds that stage from its derivation, not from today's code."),
            file.clone(),
        ),
        Hit::Search(found) => {
            let shown = found.files.iter().take(6).cloned().collect::<Vec<_>>().join(", ");
            let more = found.files.len().saturating_sub(6);
            let more = if more > 0 { format!(" and {more} more") } else { String::new() };
            (
                format!(
                    "BLOCKED: this search over {} prints lines of {shown}{more} - the old code of `{phase}`, which {feature} {task} rebuilds\n\
from its derivation, not from today's code.\n\n\
Search without them:  {}\n\
   (or a narrower path that holds none of them)",
                    found.root, found.fix
                ),
                found.files[0].clone(),
            )
        }
    };
    vec![Answer::Refuse(format!(
        "{head}\n\n{write_from}\n\n\
The GM, 2026-10-30: \"we are not trying to re-implement the same algorithms, because the old algorithms were\n\
computationally inefficient.\" To replace the stage's thin Python function or delete the old module, open that one\n\
file for ten minutes:  make phase-read FILE={file} WHY=\"<why>\"   (a shell read: PHASE_SOURCE_OK=\"<why>\")"
    ))]
}

#[cfg(test)]
mod tests;
