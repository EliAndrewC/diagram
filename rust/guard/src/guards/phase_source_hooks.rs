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

use crate::guards::feature_approval_hooks::problem;
use crate::guards::finished_run_hooks::runs::realpath;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::{self, civil};
use crate::shared::make::targets;
use crate::shared::parked;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "phase-source-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Read|Grep|Glob|Write|Edit|MultiEdit",
    decide,
};

const DEFAULT_GLOB: &str =
    "/diagram/.git/phase-sources.json /diagram/.clones/*/.git/phase-sources.json";

// a read verb by its name however spelled - past a `\`, and by its quotes or its path at a command position, where such a word is a
// program and not an argument (451 T453: `\cat <held>` and `/usr/bin/git show` passed; `ls rust/cat <held>` stays a mention)
const VERBS: &str = r"cat|sed|head|tail|less|more|grep|rg|ugrep|awk|nl|bat|python3?";
static VERB: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(&format!(
        r#"(?:(?:^|[\s;&|(`$])\\?|(?:^|[;&|(`]|\$\()\s*(?:{}|\w+=\S*\s+)*{})(?:{VERBS}|git["']?\s+(?:show|diff|log|blame))\b"#,
        crate::shared::spelled::WRAPPER_WORDS,
        crate::shared::spelled::before(&format!("(?:{VERBS}|git)"))
    ))
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

/// What a call writes that resumes a parked stage ([`parked::shell_hits`], [`parked::write_hits`]): a Bash command from `base`, a
/// Write's content against the file it replaces, an Edit's or a `MultiEdit`'s new text against its old.
fn parked_hits(event: &Event, base: &str) -> Vec<parked::Hit> {
    let Some(input) = event.input.get("tool_input") else {
        return Vec::new();
    };
    let path = field(input, "file_path");
    match event.tool() {
        "Bash" => {
            let home = crate::shared::env::opt("HOME").unwrap_or_default();
            parked::shell_hits(field(input, "command"), base, &home)
        }
        "Write" => {
            let old = std::fs::read_to_string(path).unwrap_or_default();
            parked::write_hits(path, field(input, "content"), &old)
        }
        "Edit" => parked::write_hits(path, field(input, "new_string"), field(input, "old_string")),
        "MultiEdit" => {
            let edits = input
                .get("edits")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            let joined = |key: &str| {
                edits
                    .iter()
                    .map(|e| field(e, key))
                    .collect::<Vec<_>>()
                    .join("\n")
            };
            parked::write_hits(path, &joined("new_string"), &joined("old_string"))
        }
        _ => Vec::new(),
    }
}

/// THE PARKED STAGES WAIT FOR THE GM (feature 449 T244; the GM 2026-11-21, `docs/gm-rulings.md`, "Stop before homesteads, and talk
/// first"): a write moving a parked stage into `rust/phases/src/` or declaring it in its `lib.rs` is refused, naming the ruling, unless
/// `parked-resumed.jsonl` names the stage (a `make task-start` resumed it) or the command carries `GM_RESUMED="<the GM's words>"`. Those
/// words, on a move or on a `make task-start`, must stand in a message the GM wrote this session (three words or more, the approval
/// line's test): a session cannot resume a stage on words of its own. A move resumed so is recorded in the guard log and in
/// `parked-resumed.jsonl`. None lets the call go on to the read hold.
fn parked_verdict(event: &Event, session: &Session, base: &str) -> Option<Vec<Answer>> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    let given = (event.tool() == "Bash")
        .then(|| parked::words(cmd))
        .flatten();
    let starting = given.is_some() && targets(cmd).iter().any(|t| t == "task-start");
    let hits: Vec<parked::Hit> = parked_hits(event, base)
        .into_iter()
        .filter(|h| !parked::resumed(&parked::common_of(Path::new(&h.root)), &h.stage))
        .collect();
    if hits.is_empty() && !starting {
        return None;
    }
    let shown: String = cmd.chars().take(200).collect();
    let stages: Vec<&str> = hits.iter().map(|h| h.stage.as_str()).collect();
    if let Some(words) = given {
        let bad = problem(
            &format!("**Approved**: the GM, 2000-01-01, \"{words}\""),
            session.gm_messages(),
        );
        if bad.is_empty() {
            log::fire(
                "parked-stage",
                "escaped",
                &format!("{}: {words}", stages.join(", ")),
                "gm-resumed",
                &event.input,
                session,
            );
            for hit in &hits {
                let row = serde_json::json!({"stage": hit.stage, "words": words, "utc": stamp(), "by": "a move"});
                let _ = parked::record(&parked::common_of(Path::new(&hit.root)), &row);
            }
            return None;
        }
        log::fire(
            "parked-stage",
            "blocked",
            &shown,
            &format!("GM_RESUMED-{bad}"),
            &event.input,
            session,
        );
        let why = if bad == "short" {
            "GM_RESUMED is under three words - a bare \"yes\" resumes nothing"
        } else {
            "GM_RESUMED's words are in no message the GM wrote in this session"
        };
        return Some(vec![Answer::Refuse(format!(
            "BLOCKED: {why}. A parked stage is resumed only with the GM's own words, quoted verbatim (feature 449 T244).\n\n{}\n",
            parked::RULING
        ))]);
    }
    let what = hits
        .iter()
        .map(|h| {
            if h.declares {
                format!("a write declaring `{}` in rust/phases/src/lib.rs", h.stage)
            } else {
                format!("a write moving `{}` into rust/phases/src/", h.stage)
            }
        })
        .collect::<Vec<_>>()
        .join("; ");
    let path = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "file_path"));
    let detail = if shown.is_empty() {
        path.to_owned()
    } else {
        shown
    };
    log::fire(
        "parked-stage",
        "blocked",
        &detail,
        &stages.join(","),
        &event.input,
        session,
    );
    Some(vec![Answer::Refuse(parked::refusal(&what))])
}

pub(crate) fn judge(
    event: &Event,
    session: &Session,
    here: &str,
    glob: &str,
    now: &str,
) -> Vec<Answer> {
    let base = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or(here);
    if let Some(answers) = parked_verdict(event, session, base) {
        return answers;
    }
    if !matches!(event.tool(), "Bash" | "Read" | "Grep" | "Glob") {
        return Vec::new();
    }
    if !any_match(glob) {
        return Vec::new();
    }
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
