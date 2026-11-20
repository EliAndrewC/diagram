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
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
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
            .map_while(Result::ok)
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
        .map_while(Result::ok)
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

/// An open task of an active feature: its feature's directory name, its id and the rest of its line.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OpenTask {
    /// The feature's directory name under `specs/`.
    pub feature: String,
    /// The task's id.
    pub id: String,
    /// The rest of its line.
    pub title: String,
}

// FR-013's tag: `[perf]` among the bracketed tags right after the id (`- [ ] T28 [P] [perf] ...`), never a `[perf]` the title quotes - T28's
// own line names "a [perf] tag" in its prose.
static PERF_TAG: LazyLock<Regex> = LazyLock::new(|| re(r"^(?:\[[^\]\n]*\] +)*\[perf\](?: |$)"));

/// Is a task performance work (feature 451 FR-013, the GM 2026-11-20: "can we in general priotitize performance improvements going
/// forward?")? Its line carries the `[perf]` tag after its id, or it was filed with `make task-add ... PERF=1`, whose one mark is the
/// checklist heading it writes into the task's plan section (`### T<n> Performance checklist`, the plan crate's `template::PERFORMANCE`;
/// the task crate's test pins the two together). `title` is the line after the id, `plan` the feature's plan.md.
#[must_use]
pub fn performance(id: &str, title: &str, plan: &str) -> bool {
    PERF_TAG.is_match(title).unwrap_or(false)
        || re(&format!(
            r"(?m)^### {} Performance checklist\b",
            fancy_regex::escape(id)
        ))
        .is_match(plan)
        .unwrap_or(false)
}

fn read(path: &Path) -> Result<String, String> {
    std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))
}

/// THE ACTIVE TEST (feature 385 T70; feature 451 FR-013 names it as its own): a feature's open boxes, or none where it is not active -
/// no open box but the GM's, set down at or after `since` (its last task-start), or closed by its spec's status line, asked last. With
/// `starting`, the feature whose task is being started: its set-downs count for nothing, since the start ends them.
fn active(
    root: &Path,
    downs: &[Value],
    feature: &str,
    since: &str,
    starting: bool,
) -> Result<Vec<(String, String)>, String> {
    let spec_dir = root.join("specs").join(feature);
    let tasks = spec_dir.join("tasks.md");
    if feature.is_empty() || !tasks.is_file() {
        return Ok(Vec::new());
    }
    let boxes = open_boxes(&read(&tasks)?);
    let set_down = !starting
        && downs
            .iter()
            .any(|r| field(r, "feature") == feature && field(r, "utc") >= since);
    if boxes.is_empty() || set_down || closed_by_status(&spec_dir) {
        return Ok(Vec::new());
    }
    Ok(boxes)
}

/// The clone's features by their last task-start, the latest first: (feature, its last start).
fn started(git_dir: &Path) -> Result<Vec<(String, String)>, String> {
    let mut last: Vec<(String, String)> = Vec::new();
    for row in rows(&git_dir.join("task-starts.jsonl"))? {
        let (feature, utc) = (field(&row, "feature"), field(&row, "utc"));
        last.retain(|(f, _)| f != feature);
        last.push((feature.to_owned(), utc.to_owned()));
    }
    last.reverse();
    Ok(last)
}

/// The open performance task to start next (feature 451 FR-013): of `prefer` first (the feature whose task is being started, or the
/// one the turn worked), then of each other ACTIVE feature by its last task-start, the latest first; within a feature, the first in its
/// tasks.md. Active is [`active`]'s test over the clone's own start and set-down logs, so a feature never started in this clone is not
/// active unless it is `prefer` (its task being started makes it so). The one picker the Stop hook's "start the next" and `make
/// task-start`'s refusal share, so the hook never names a task the start refuses.
///
/// # Errors
/// A start or set-down log, a tasks.md or a plan.md that cannot be read.
pub fn next_performance(
    root: &Path,
    git_dir: &Path,
    prefer: &str,
) -> Result<Option<OpenTask>, String> {
    let downs = rows(&git_dir.join("set-downs.jsonl"))?;
    let mut order = started(git_dir)?;
    if !prefer.is_empty() {
        order.retain(|(f, _)| f != prefer);
        order.insert(0, (prefer.to_owned(), String::new()));
    }
    for (feature, since) in order {
        let boxes = active(root, &downs, &feature, &since, feature == prefer)?;
        if boxes.is_empty() {
            continue;
        }
        let plan_path = root.join("specs").join(&feature).join("plan.md");
        let plan = if plan_path.is_file() {
            read(&plan_path)?
        } else {
            String::new()
        };
        if let Some((id, title)) = boxes.into_iter().find(|(id, t)| performance(id, t, &plan)) {
            return Ok(Some(OpenTask { feature, id, title }));
        }
    }
    Ok(None)
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
    let downs = rows(&git_dir.join("set-downs.jsonl"))?;
    let boxes = active(root, &downs, feature, since, false)?;
    let Some((tid, title)) = boxes.first() else {
        return Ok(None);
    };
    // the transcript last: the costly read (206 MB on 2026-10-26), where the status line is one small file
    let path = Path::new(transcript);
    if path.is_file() && !running(path).map_err(|e| e.to_string())?.is_empty() {
        return Ok(None);
    }
    let number = |f: &str| f.split('-').next().unwrap_or(f).to_owned();
    // PERFORMANCE WORK FIRST (feature 451 FR-013): the next named is an open performance task where an active feature holds one; a
    // reader's error names the feature's first box, as before, rather than let the refusal go
    let next = match next_performance(root, &git_dir, feature).ok().flatten() {
        Some(p) => {
            let of = if p.feature == feature {
                String::new()
            } else {
                format!(" of {}", p.feature)
            };
            let short: String = p.title.chars().take(80).collect();
            format!(
                "{} {short}{of} - performance work first, FR-013: make task-start F={} T={}",
                p.id,
                number(&p.feature),
                p.id
            )
        }
        None => format!("{tid} {}", title.chars().take(80).collect::<String>()),
    };
    Ok(Some(format!(
        "BLOCKED: feature {feature} has {} open task(s) and nothing is running - start the next ({next}), or set it down: make set-down F={} WHY=\"<why it stops here>\" (feature 385 T70)",
        boxes.len(),
        number(feature)
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
    // `shared::env`: a test reads its own environment, never a session's export (feature 451 T32)
    judge(event, session, crate::shared::env::opt("SET_DOWN_ROOT"))
}

#[cfg(test)]
mod tests;
