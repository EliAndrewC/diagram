//! `set-down-hooks` (feature 385 T70; ported from the shell of the same name and `lib/hm_setdown.py`, feature 449 T049): A FEATURE IS WORKED UNTIL
//! IT IS SET DOWN (the GM, 2026-10-18: "stopping with tasks partially done is a constant problem with the Opus line of models"). At a turn's end,
//! for the clone's last `make task-start`: an open box, nothing the session started still running, no `make set-down` since - refused. A turn ending
//! on a question is no way out (the plan review, 2026-10-19). A read error lets the turn end, recorded: a Stop guard that fails closed can hold a
//! session.

use std::collections::HashSet;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log::{self, Entry};
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "set-down-hooks",
    events: &["Stop"],
    matcher: "*",
    decide,
};

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static OPEN: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[ \] (T\d+[a-z]?) (.*)$"));
// A launch is the tool's own record, never its text (2026-10-28): the notice's words reach the transcript quoted, and each quote read as a launch
// kept the guard silent. A workflow's launch is its own shape (2026-11-01).
static LAUNCHED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:"(?:backgroundTaskId|agentId)"|"status":\s*"async_launched",\s*"taskId"):\s*"([A-Za-z0-9]+)""#,
    )
});
static NOTIFIED: LazyLock<Regex> = LazyLock::new(|| re(r"<task-id>([A-Za-z0-9]+)</task-id>"));
// A task ended with TaskStop sends no notification, so its stop is its end (2026-10-28).
static STOPPED: LazyLock<Regex> = LazyLock::new(|| {
    re(r#""name":\s*"TaskStop",\s*"input":\s*\{[^}]*?"(?:task_id|shell_id)":\s*"([A-Za-z0-9]+)""#)
});

fn rows(path: &Path) -> Result<Vec<Value>, String> {
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let text = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
    Ok(text
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect())
}

fn ids(pattern: &Regex, line: &str, into: &mut HashSet<String>) {
    into.extend(
        pattern
            .captures_iter(line)
            .flatten()
            .filter_map(|m| Some(m.get(1)?.as_str().to_owned())),
    );
}

/// The ids launched in the background that no notification has reported on, a line at a time: a transcript reached 206 MB on 2026-10-26, and read
/// whole this guard grew past 1.2 GB at each turn's end.
fn running(path: &Path) -> std::io::Result<HashSet<String>> {
    let mut reader = BufReader::new(File::open(path)?);
    let (mut launched, mut notified) = (HashSet::new(), HashSet::new());
    let mut raw = Vec::new();
    while reader.read_until(b'\n', &mut raw)? > 0 {
        let line = String::from_utf8_lossy(&raw);
        ids(&LAUNCHED, &line, &mut launched);
        ids(&NOTIFIED, &line, &mut notified);
        ids(&STOPPED, &line, &mut notified);
        raw.clear();
    }
    Ok(launched.difference(&notified).cloned().collect())
}

/// The feature's open boxes, the GM's review box left out.
fn open_boxes(text: &str) -> Vec<(String, String)> {
    OPEN.captures_iter(text)
        .flatten()
        .filter_map(|m| Some((m.get(1)?.as_str().to_owned(), m.get(2)?.as_str().to_owned())))
        .filter(|(_, title)| !title.starts_with("GM review"))
        .collect()
}

/// Whether the spec's status line closes it, asked last, only when the turn would be refused: the shared `speckit` reading in process
/// since feature 449 T118 (`ask:449-T83-scope`), where T049 decision (b) ran `speckit-todo.py` by path; a spec that cannot be read is
/// not closed, as the Python's failed run answered no `yes`.
fn closed_by_status(spec_dir: &Path) -> bool {
    crate::shared::speckit::closed_by_status(spec_dir).unwrap_or(false)
}

/// None to let the turn end, else the refusal; an Err is a read error, which lets it end too.
pub(crate) fn verdict(root: &Path, transcript: &str) -> Result<Option<String>, String> {
    let at = root.to_string_lossy();
    let said = ask(
        Path::new("/"),
        "git",
        &[
            "-C",
            &at,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        "",
    );
    if !said.ok() {
        return Err(said.err);
    }
    let git_dir = PathBuf::from(said.out.trim());
    let starts = rows(&git_dir.join("task-starts.jsonl"))?;
    let Some(last) = starts.last() else {
        return Ok(None);
    };
    let (feature, since) = (field(last, "feature"), field(last, "utc"));
    let spec_dir = root.join("specs").join(feature);
    let tasks = spec_dir.join("tasks.md");
    if feature.is_empty() || !tasks.is_file() {
        return Ok(None);
    }
    let boxes = open_boxes(&std::fs::read_to_string(&tasks).map_err(|e| e.to_string())?);
    let Some((tid, title)) = boxes.first() else {
        return Ok(None);
    };
    let path = Path::new(transcript);
    if path.is_file() && !running(path).map_err(|e| e.to_string())?.is_empty() {
        return Ok(None);
    }
    let set_down = rows(&git_dir.join("set-downs.jsonl"))?
        .iter()
        .any(|r| field(r, "feature") == feature && field(r, "utc") >= since);
    if set_down || closed_by_status(&spec_dir) {
        return Ok(None);
    }
    let short: String = title.chars().take(80).collect();
    let number = feature.split('-').next().unwrap_or(feature);
    Ok(Some(format!(
        "BLOCKED: feature {feature} has {} open task(s) and nothing is running - start the next ({tid} {short}), or set it down: make set-down F={number} WHY=\"<why it stops here>\" (feature 385 T70)",
        boxes.len()
    )))
}

/// The tree a turn's feature is read in: the seam, else the session's clone, else the work tree `cwd` stands in.
fn root_of(event: &Event, session: &Session, seam: Option<String>) -> Option<PathBuf> {
    let named = seam
        .filter(|s| !s.is_empty())
        .map(PathBuf::from)
        .or_else(|| session.clone_dir().map(Path::to_path_buf));
    if let Some(dir) = named.filter(|d| d.is_dir()) {
        return Some(dir);
    }
    let cwd = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or(".");
    let said = ask(
        Path::new("."),
        "git",
        &["-C", cwd, "rev-parse", "--show-toplevel"],
        "",
    );
    said.ok().then(|| PathBuf::from(said.out.trim()))
}

pub(crate) fn judge(event: &Event, session: &Session, seam: Option<String>) -> Vec<Answer> {
    let Some(root) = root_of(event, session, seam) else {
        return Vec::new();
    };
    match verdict(&root, field(&event.input, "transcript_path")) {
        Ok(None) => Vec::new(),
        Err(why) => {
            let _ = log::write(&Entry {
                guard: "set-down",
                event: "error",
                detail: "stop",
                rule: "read-error",
                context: Some(Value::String(why)),
                input: &event.input,
                session_name: &session.name(),
            });
            Vec::new()
        }
        Ok(Some(text)) => {
            log::fire(
                "set-down",
                "blocked",
                "stop",
                "not-set-down",
                &event.input,
                session,
            );
            vec![Answer::Refuse(text)]
        }
    }
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(event, session, std::env::var("SET_DOWN_ROOT").ok())
}

#[cfg(test)]
mod tests;
