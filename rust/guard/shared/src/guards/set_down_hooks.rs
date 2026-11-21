//! `set-down-hooks` (feature 385 T70; ported from the shell of the same name and `lib/hm_setdown.py`, feature 449 T049): A FEATURE IS WORKED UNTIL
//! IT IS SET DOWN (the GM, 2026-10-18: "stopping with tasks partially done is a constant problem with the Opus line of models"). At a turn's end,
//! for the clone's last `make task-start`: an open box, nothing the session started still running, no `make set-down` since - refused. A turn ending
//! on a question is no way out (the plan review, 2026-10-19). A read error lets the turn end, recorded: a Stop guard that fails closed can hold a
//! session.

use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::log::{self, Entry};
use crate::protocol::{Answer, Event, Guard};
use crate::session::Session;
use crate::state::field;
use crate::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "set-down-hooks",
    events: &["Stop"],
    matcher: "*",
    decide,
};

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static OPEN: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[ \] (T\d+[a-z]?) (.*)$"));
// A launch is the tool's own record, never its text (2026-10-28): the notice's words reach the transcript quoted, and each quote read as a launch
// kept the guard silent. A workflow's launch is its own shape (2026-11-01). A SendMessage resume is a launch (451 T65: a resumed builder
// read as finished, its turn refused as "nothing is running"): its result's `resumedAgentId`, unescaped in the tool's own record alone.
static LAUNCHED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:"(?:backgroundTaskId|agentId|resumedAgentId)"|"status":\s*"async_launched",\s*"taskId"):\s*"([A-Za-z0-9]+)""#,
    )
});
static NOTIFIED: LazyLock<Regex> = LazyLock::new(|| re(r"<task-id>([A-Za-z0-9]+)</task-id>"));
// A task ended with TaskStop sends no notification, so its stop is its end (2026-10-28).
static STOPPED: LazyLock<Regex> = LazyLock::new(|| {
    re(r#""name":\s*"TaskStop",\s*"input":\s*\{[^}]*?"(?:task_id|shell_id)":\s*"([A-Za-z0-9]+)""#)
});
// A turn's end in an agent's own transcript (451 T65): the record's own key, unescaped, on its text block's record - each block of a
// message is a record of its own, its thinking's carrying `end_turn` too, written first (an agent's at 21:27:45 and its text 19 s later,
// measured 2026-11-21 in `agent-a4e93c6a157b06302.jsonl`).
static TURN_END: LazyLock<Regex> = LazyLock::new(|| re(r#""stop_reason":\s*"end_turn""#));
static TEXT_BLOCK: LazyLock<Regex> = LazyLock::new(|| re(r#""type":\s*"text""#));
/// An interim notice's summary ends so (451 T65; read 2026-11-21 from a session's transcript, its note "the same task-id notifies again
/// if it does; the result below may be interim"): the agent stopped with background work of its own running, so the notice ends nothing.
const INTERIM: &str = "is waiting on its own background work";
/// A request blob re-emits the history sent to the model (451 T65), so its copy of an old notice would end an agent resumed since; no
/// task-id of 6,636 in 12 transcripts is named in a blob alone (measured 2026-11-21), so a blob's line is not read.
const BLOB: &[u8] = br#"{"type":"api-request-blob""#;

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

/// What a record says of an id.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Said {
    /// Launched or resumed.
    Launched,
    /// An interim notice: the agent waits on its own background work.
    Interim,
    /// A final notice, or a stop.
    Ended,
}

fn put<'a>(pattern: &Regex, said: Said, line: &'a str, into: &mut Vec<(usize, Said, &'a str)>) {
    into.extend(
        pattern
            .captures_iter(line)
            .map_while(Result::ok)
            .filter_map(|m| m.get(1))
            .map(|g| (g.start(), said, g.as_str())),
    );
}

/// Whether a notice's own text - from its id to the next notice or its close - holds an interim summary.
fn interim(body: &str) -> bool {
    body.split_once("<summary>")
        .and_then(|(_, rest)| rest.split_once("</summary>"))
        .is_some_and(|(summary, _)| summary.ends_with(INTERIM))
}

/// A line's events in their order: a record can hold several notices, an interim one and its final one together.
fn events(line: &str) -> Vec<(usize, Said, &str)> {
    let mut out = Vec::new();
    put(&LAUNCHED, Said::Launched, line, &mut out);
    put(&STOPPED, Said::Ended, line, &mut out);
    let notices: Vec<_> = NOTIFIED
        .captures_iter(line)
        .map_while(Result::ok)
        .filter_map(|m| Some((m.get(0)?.start(), m.get(1)?)))
        .collect();
    for (k, (_, id)) in notices.iter().enumerate() {
        let to = notices.get(k + 1).map_or(line.len(), |next| next.0);
        let body = &line[id.end()..to];
        let body = body
            .split_once("</task-notification>")
            .map_or(body, |(own, _)| own);
        let said = if interim(body) {
            Said::Interim
        } else {
            Said::Ended
        };
        out.push((id.start(), said, id.as_str()));
    }
    out.sort_by_key(|e| e.0);
    out
}

/// A transcript read in order (451 T65): each id's last word, launched (or resumed) or interim, an id a final notice or a stop ended
/// dropped. `me` is the agent whose own transcript it is, its every line naming it; `woken`, whether an end of its own work came after
/// its last turn's end (read for an agent's own transcript alone).
#[derive(Default)]
struct Read {
    ids: HashMap<String, Said>,
    woken: bool,
}

fn read_in_order(path: &Path, me: &str) -> std::io::Result<Read> {
    let mut reader = BufReader::new(File::open(path)?);
    let mut read = Read::default();
    let mut raw = Vec::new();
    while reader.read_until(b'\n', &mut raw)? > 0 {
        if !raw.starts_with(BLOB) {
            let line = String::from_utf8_lossy(&raw);
            if !me.is_empty()
                && TURN_END.is_match(&line).unwrap_or(false)
                && TEXT_BLOCK.is_match(&line).unwrap_or(false)
            {
                read.woken = false;
            }
            for (_, said, id) in events(&line) {
                if id == me {
                    continue;
                }
                if said == Said::Ended {
                    read.ids.remove(id);
                    read.woken = true;
                } else {
                    read.ids.insert(id.to_owned(), said);
                }
            }
        }
        raw.clear();
    }
    Ok(read)
}

/// Whether an agent whose last word is an interim notice still runs (451 T65): its own transcript (`<dir>/agent-<id>.jsonl`, the
/// session's `subagents` directory) holds work of its own running - or an interim sub-agent that does - or it was woken since its last
/// turn's end. No transcript, not running, as before T65. `known` holds each agent's answer, one on the way reading as not running, so a
/// cycle ends.
fn awake(dir: &Path, id: &str, known: &mut HashMap<String, bool>) -> std::io::Result<bool> {
    if let Some(&is) = known.get(id) {
        return Ok(is);
    }
    known.insert(id.to_owned(), false);
    let file = dir.join(format!("agent-{id}.jsonl"));
    if !file.is_file() {
        return Ok(false);
    }
    let read = read_in_order(&file, id)?;
    let mut is = read.woken || read.ids.values().any(|s| *s == Said::Launched);
    for (sub, _) in read.ids.iter().filter(|(_, s)| **s == Said::Interim) {
        is = is || awake(dir, sub, known)?;
    }
    known.insert(id.to_owned(), is);
    Ok(is)
}

/// The ids still running, a line at a time: a transcript reached 206 MB on 2026-10-26, and read whole this guard grew past 1.2 GB at each
/// turn's end. Read in order (451 T65): an id launched or resumed after its last final notice runs; one whose last word is an interim
/// notice runs while its own transcript says so ([`awake`]), read only when nothing else plainly runs. Taken literally, an interim
/// notice never ending anything kept 8 of a session's 58 interim agents running for good - they never notified again - and the guard
/// silent from its line 2,132 of 50,891 on (measured 2026-11-21, a replay of `c6fd72d1-...jsonl`).
fn running(path: &Path) -> std::io::Result<HashSet<String>> {
    let read = read_in_order(path, "")?;
    let (live, waiting): (Vec<_>, Vec<_>) = read
        .ids
        .into_iter()
        .partition(|(_, said)| *said == Said::Launched);
    if !live.is_empty() {
        return Ok(live.into_iter().map(|(id, _)| id).collect());
    }
    let dir = path.with_extension("").join("subagents");
    let mut known = HashMap::new();
    let mut out = HashSet::new();
    for (id, _) in waiting {
        if awake(&dir, &id, &mut known)? {
            out.insert(id);
        }
    }
    Ok(out)
}

/// Whether one agent still runs by [`running`]'s reading of the session's transcript, for `finished_run_hooks` (451 T85: a run a
/// still-running builder started is the builder's to wait on): launched or resumed since its last final notice, or its last word an
/// interim notice and its own transcript [`awake`]. An id the transcript never names is not running.
///
/// # Errors
/// The transcript, or the agent's own, cannot be read.
pub fn still_running(path: &Path, id: &str) -> std::io::Result<bool> {
    match read_in_order(path, "")?.ids.get(id) {
        Some(Said::Launched) => Ok(true),
        Some(Said::Interim) => awake(
            &path.with_extension("").join("subagents"),
            id,
            &mut HashMap::new(),
        ),
        _ => Ok(false),
    }
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
    crate::speckit::closed_by_status(spec_dir).unwrap_or(false)
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
    judge(event, session, crate::env::opt("SET_DOWN_ROOT"))
}

#[cfg(test)]
mod tests;
