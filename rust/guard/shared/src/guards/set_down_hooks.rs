//! `set-down-hooks` (feature 385 T70; ported from the shell of the same name and `lib/hm_setdown.py`, feature 449 T049): A FEATURE IS WORKED UNTIL
//! IT IS SET DOWN (the GM, 2026-10-18: "stopping with tasks partially done is a constant problem with the Opus line of models"). At a turn's end,
//! for the clone's last `make task-start`: an open box, nothing the session started still running, no `make set-down` since - refused. A turn ending
//! on a question is no way out (the plan review, 2026-10-19). A read error lets the turn end, recorded: a Stop guard that fails closed can hold a
//! session. Since 451 T183 the block is said by the background idle check (`idle.rs`), never a Stop that waits on running work, nor
//! for a feature or a task a ruling holds (`holds.rs`); nothing names a free builder slot while builders run (T183's MODE 4, D10).

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
    // SessionStart: a compaction forgets what was said in one line (451 T171, `once::forget`). A Stop is no longer decided here: its
    // block is the idle check's (451 T183), and nothing names a free builder slot while a builder runs (T183's MODE 4, D10)
    events: &["SessionStart"],
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
// A Monitor's launch is its result opening `{"taskId": ..., "timeoutMs": ...}` (451 T193: T184's builder's watch `bx5gtybg3` read as no
// work; the only result opening `taskId` in the transcripts of 2026-11-22 and 23, 214 of them, measured 2026-11-23).
static LAUNCHED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:"(?:backgroundTaskId|agentId|resumedAgentId)"|"status":\s*"async_launched",\s*"taskId"|"toolUseResult":\s*\{\s*"taskId"):\s*"([A-Za-z0-9]+)""#,
    )
});
// A FOREGROUND AGENT'S RESULT IS ITS END (449 T268): a synchronous Agent call's `toolUseResult` opens `"status":"completed"` and carries
// the finished agent's `agentId` after its prompt, and no notice ever follows it, so read as a launch it ran for good - the Stop hook of
// T197 G2's check session read 28 ids running where 1 was (27 foreground results, 2 notices, measured 2026-11-22 over its transcript
// `e4a31b0e-...jsonl`); over 12 of the clone's transcripts the result's status was `async_launched` 3,387 times and `completed` 89.
// Each tool result's opening is matched, and an id inside one that opens `completed` is an end.
static RESULT: LazyLock<Regex> =
    LazyLock::new(|| re(r#""toolUseResult":\s*\{(\s*"status":\s*"completed")?"#));
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
    // the start log's rows, a start and its `make task-unstart` read as no start (451 T359); no other log holds an `unstart` row
    Ok(crate::speckit::marks::live_starts(&text)
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
    if !out.is_empty() {
        let results: Vec<(usize, bool)> = RESULT
            .captures_iter(line)
            .map_while(Result::ok)
            .filter_map(|c| Some((c.get(0)?.start(), c.get(1).is_some())))
            .collect();
        for event in &mut out {
            let done = results
                .iter()
                .rev()
                .find(|(at, _)| *at < event.0)
                .is_some_and(|(_, done)| *done);
            if done {
                event.1 = Said::Ended;
            }
        }
    }
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
/// interim notice and its own transcript [`awake`]. An id the transcript never names runs by its dispatcher's reading ([`alive`]).
///
/// # Errors
/// The transcript, or an agent's own, cannot be read.
pub fn still_running(path: &Path, id: &str) -> std::io::Result<bool> {
    let read = read_in_order(path, "")?;
    alive(&read, &subagents(path), id, &mut HashMap::new(), HOPS)
}

/// How far up its dispatchers an agent is followed (a CONVENTION: the session's builders dispatch checks, which dispatch none, so
/// two hops is every agent seen; four leaves room).
const HOPS: usize = 4;

/// A BUILDER'S OWN SUB-AGENT RUNS WHILE ITS DISPATCHER DOES (451 T171): an id the session's transcript never names - it was launched
/// from an agent's own transcript - runs while the agent that dispatched it (its meta's `parentAgentId`) runs and that agent's own
/// transcript reads it as running, by [`runs`]' rule. WHY: a run a builder's sub-agent started was read as a stopped builder's and the
/// coordinator's turn refused over it (T85's rule asked the session's transcript alone, which names no sub-agent's launch).
fn alive(
    read: &Read,
    dir: &Path,
    id: &str,
    known: &mut HashMap<String, bool>,
    hops: usize,
) -> std::io::Result<bool> {
    if read.ids.contains_key(id) {
        return runs(read, dir, id, known);
    }
    let Some(parent) = builders::parent_of(dir, id) else {
        return Ok(false);
    };
    let own = dir.join(format!("agent-{parent}.jsonl"));
    if hops == 0 || !own.is_file() || !alive(read, dir, &parent, known, hops - 1)? {
        return Ok(false);
    }
    runs(&read_in_order(&own, &parent)?, dir, id, known)
}

/// [`still_running`]'s rule for one id over a reading already made: launched or resumed, or interim and [`awake`].
fn runs(
    read: &Read,
    dir: &Path,
    id: &str,
    known: &mut HashMap<String, bool>,
) -> std::io::Result<bool> {
    match read.ids.get(id) {
        Some(Said::Launched) => Ok(true),
        Some(Said::Interim) => awake(dir, id, known),
        _ => Ok(false),
    }
}

/// The session's `subagents` directory, beside its transcript.
fn subagents(path: &Path) -> PathBuf {
    path.with_extension("").join("subagents")
}

/// A builder's brief: the description of an agent the session dispatched (its meta's `spawnDepth` 1) opening with its feature number
/// ([`builder_brief`]; 449 T268 dropped the `T<n>` it had to follow, so a bundle's brief is one).
static BRIEF: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*(\d{3})\b"));
/// A task id in a brief, or a range of them (`T289-T300`, 451 T156): the first id's number and letter, the last's.
static TASK_ID: LazyLock<Regex> = LazyLock::new(|| re(r"\bT(\d+)([a-z]?)(?:-T(\d+)([a-z]?))?\b"));
/// A task its line says it comes after (`after T86`).
static AFTER: LazyLock<Regex> = LazyLock::new(|| re(r"\bafter (T\d+[a-z]?)\b"));
/// A WAIT THE HOOK READS (451 T102): a task line's `(waits: <when>)`, right after its id's bracketed tags as FR-013's `[perf]` is, so a
/// line that only quotes the clause in its prose (T102's own) waits on nothing. `<when>` is a landing, `T88 lands` (no task it names
/// still open), or a day after one, `a full day after T02-T21 land` (24 hours past the latest landing of the tasks it names, a
/// CONVENTION: the plain reading of T22's "first full day of work after T02-T21 land"). Anything else in the parentheses is no wait:
/// it fails toward a start the session sees named, never a task hidden for good. A bare date is deliberately not a form (T102's plan
/// review, D7e): the clock against a typed date, with no landing behind it, would take a performance task out of FR-013's refusal
/// with no reason recorded.
static WAITS: LazyLock<Regex> = LazyLock::new(|| re(r"^(?:\[[^\]\n]*\] +)*\(waits: ([^)\n]+)\)"));
/// A `<when>` that is a landing: one task (`T88`) or a range of them (`T02-T21`, every task numbered in it), a day after it or not.
static LANDS: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(a full day after )?T(\d{1,9})([a-z]?)(?:-T(\d{1,9}))? lands?$"));
/// An open task's line saying it lands before another (`lands before T22`): that other waits on its landing.
static BEFORE: LazyLock<Regex> = LazyLock::new(|| re(r"\blands before (T\d+[a-z]?)\b"));
/// A task's number and letter (`T11a`).
static ID: LazyLock<Regex> = LazyLock::new(|| re(r"^T(\d{1,9})([a-z]?)$"));
/// A full day in microseconds.
const DAY_MICROS: i64 = 86_400 * 1_000_000;

/// Each feature's landings, read once a Stop (451 T102): the feature, then each task's latest landing in microseconds past the epoch.
type Lands = HashMap<String, HashMap<String, i64>>;

/// An ISO time in microseconds past the epoch, UTC: a time without a zone read as UTC (a land line's `t1` carries its `Z`).
fn instant(text: &str) -> Option<i64> {
    crate::iso::moment(text).map(|(at, zone)| at - zone.unwrap_or(0))
}

/// Now, in microseconds past the epoch: `L7R_WAITS_NOW` (an ISO time, the tests' seam, as `L7R_PERMIT_NOW` is the permit's), else the
/// clock.
fn now() -> i64 {
    crate::env::opt("L7R_WAITS_NOW")
        .and_then(|n| instant(&n))
        .unwrap_or_else(|| {
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map_or(0, |d| i64::try_from(d.as_micros()).unwrap_or(i64::MAX))
        })
}

/// Each task's latest landing in a feature's event log (451 T102): each land `end` line that landed (`landed` true, as T06 writes one),
/// at its `t1`, for every task in its `tasks` (a batch lands several), else its `task`. A task ticked before the log carried these
/// lines (451 T02-T05) has none, and reads as landed long ago.
fn landings(root: &Path, feature: &str) -> Result<HashMap<String, i64>, String> {
    let log = super::event_log_hooks::log_path(root, feature);
    let mut out = HashMap::new();
    if !log.is_file() {
        return Ok(out);
    }
    let text = read(&log)?;
    for row in text
        .lines()
        .filter(|l| l.contains(r#""src":"land""#) && l.contains(r#""step":"end""#))
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(|r| r.get("landed").and_then(Value::as_bool) == Some(true))
    {
        let Some(at) = instant(field(&row, "t1")) else {
            continue;
        };
        let tasks: Vec<&str> = row.get("tasks").and_then(Value::as_array).map_or_else(
            || vec![field(&row, "task")],
            |list| list.iter().filter_map(Value::as_str).collect(),
        );
        for task in tasks {
            let last = out.entry(task.to_owned()).or_insert(at);
            *last = (*last).max(at);
        }
    }
    Ok(out)
}

/// Can a task not start yet (451 T102)? Its `(waits: ...)` clause is unmet ([`WAITS`]), it comes `after T<n>` an open task (451 T88's
/// rule), or an open task's line says it `lands before` it. The one reading the nothing-running refusal and `make
/// task-start`'s performance-first picker ([`next_performance`]) share - FR-013's "a performance task waiting on another task's
/// landing", read rather than escaped. `boxes` are the feature's open boxes; the log is read only for a day after a landing.
fn waits(
    root: &Path,
    feature: &str,
    boxes: &[(String, String)],
    (id, title): (&str, &str),
    lands: &mut Lands,
) -> Result<bool, String> {
    let open = |t: &str| boxes.iter().any(|(o, _)| o == t);
    let after = AFTER
        .captures_iter(title)
        .map_while(Result::ok)
        .any(|c| open(&c[1]));
    let before = boxes.iter().any(|(o, t)| {
        o != id
            && BEFORE
                .captures_iter(t)
                .map_while(Result::ok)
                .any(|c| &c[1] == id)
    });
    if after || before || asks_the_gm(root, feature, id)? {
        return Ok(true);
    }
    let Some(when) = WAITS
        .captures(title)
        .ok()
        .flatten()
        .map(|c| c[1].trim().to_owned())
    else {
        return Ok(false);
    };
    let Some(c) = LANDS.captures(&when).ok().flatten() else {
        return Ok(false);
    };
    let num = |s: &str| s.parse::<u64>().unwrap_or_default();
    let (lo, letter, hi) = (num(&c[2]), &c[3], c.get(4).map(|m| num(m.as_str())));
    // one task by its id, a range by every number in it, whatever its letter
    let named = |t: &str| {
        ID.captures(t).ok().flatten().is_some_and(|i| {
            let n = num(&i[1]);
            hi.map_or(n == lo && &i[2] == letter, |hi| (lo..=hi).contains(&n))
        })
    };
    if boxes.iter().any(|(o, _)| named(o)) {
        return Ok(true);
    }
    if c.get(1).is_none() {
        return Ok(false);
    }
    if !lands.contains_key(feature) {
        lands.insert(feature.to_owned(), landings(root, feature)?);
    }
    let last = lands[feature]
        .iter()
        .filter(|(t, _)| named(t))
        .map(|(_, at)| *at)
        .max();
    let now = now();
    Ok(last.is_some_and(|at| now < at + DAY_MICROS))
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
    // the heading as text first (451 T102): a pattern built and run over the whole plan for every box cost the Stop hook 0.1 s of CPU
    // once its picker walked past a waiting T22, measured 2026-11-21 (a fixture copy of 451, the plan emptied: 0.01 s)
    let heading = format!("### {id} Performance checklist");
    PERF_TAG.is_match(title).unwrap_or(false)
        || (plan.contains(&heading)
            && re(&format!(r"(?m)^{}\b", fancy_regex::escape(&heading)))
                .is_match(plan)
                .unwrap_or(false))
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
/// task-start`'s refusal share, so the hook never names a task the start refuses. A task that waits ([`waits`], 451 T102) is skipped,
/// so other work starts with no `PERF_LATER_OK` for it.
///
/// # Errors
/// A start or set-down log, a tasks.md, a plan.md or an event log a wait reads that cannot be read.
pub fn next_performance(
    root: &Path,
    git_dir: &Path,
    prefer: &str,
) -> Result<Option<OpenTask>, String> {
    next_performance_in(root, git_dir, prefer, false, &mut Lands::new())
}

/// [`next_performance`] with the landings already read this Stop; `idle`, the idle check's reading, skips a task a ruling holds by name
/// ([`holds::named`], T183's MODE 4, D6), which `make task-start`'s does not.
fn next_performance_in(
    root: &Path,
    git_dir: &Path,
    prefer: &str,
    idle: bool,
    lands: &mut Lands,
) -> Result<Option<OpenTask>, String> {
    let downs = rows(&git_dir.join("set-downs.jsonl"))?;
    let mut order = started(git_dir)?;
    if !prefer.is_empty() {
        order.retain(|(f, _)| f != prefer);
        order.insert(0, (prefer.to_owned(), String::new()));
    }
    for (feature, since) in order {
        // another feature a ruling holds offers no performance work to start (451 T183); the feature being started is never skipped,
        // so a start the GM approved under a hold is refused only as it was before
        if feature != prefer && holds::held(root, &feature).is_some() {
            continue;
        }
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
        let named = if idle {
            holds::named(root, &feature)
        } else {
            Vec::new()
        };
        for (id, title) in &boxes {
            if performance(id, title, &plan)
                && !named.contains(id)
                && crate::parked::held_task(root, git_dir, title).is_none()
                && !waits(root, &feature, &boxes, (id, title), lands)?
            {
                return Ok(Some(OpenTask {
                    feature,
                    id: id.clone(),
                    title: title.clone(),
                }));
            }
        }
    }
    Ok(None)
}

/// EVERY OPEN PERFORMANCE TASK OF EVERY ACTIVE FEATURE (451 T313's round-3 ruling, `ask:451-T313-plan-round3`; T421): the walk of
/// [`next_performance`] - `prefer` first, then each active feature by its last task-start, a held feature (not `prefer`) and a parked
/// stage's task skipped - collecting every [`performance`] box, and WITHOUT its wait skip: the builders' queue names one with no
/// `queue.txt` line until its line is written, and a line with `waits=` is what quiets a task that waits. The plan is cut once to its
/// checklist headings, the only lines [`performance`] reads of it, so an open box does not search the whole plan (451's: 140 open boxes, 679,113 bytes, measured 2026-11-27).
///
/// # Errors
/// A start or set-down log, a tasks.md or a plan.md that cannot be read.
pub fn open_performance(
    root: &Path,
    git_dir: &Path,
    prefer: &str,
) -> Result<Vec<OpenTask>, String> {
    let downs = rows(&git_dir.join("set-downs.jsonl"))?;
    let mut order = started(git_dir)?;
    if !prefer.is_empty() {
        order.retain(|(f, _)| f != prefer);
        order.insert(0, (prefer.to_owned(), String::new()));
    }
    let mut out = Vec::new();
    for (feature, since) in order {
        if feature != prefer && holds::held(root, &feature).is_some() {
            continue;
        }
        let boxes = active(root, &downs, &feature, &since, feature == prefer)?;
        let plan_path = root.join("specs").join(&feature).join("plan.md");
        let plan = if boxes.is_empty() || !plan_path.is_file() {
            String::new()
        } else {
            read(&plan_path)?
        };
        let headings: String = plan
            .lines()
            .filter(|l| l.starts_with("### ") && l.contains(" Performance checklist"))
            .flat_map(|l| [l, "\n"])
            .collect();
        for (id, title) in boxes {
            if performance(&id, &title, &headings)
                && crate::parked::held_task(root, git_dir, &title).is_none()
            {
                out.push(OpenTask {
                    feature: feature.clone(),
                    id,
                    title,
                });
            }
        }
    }
    Ok(out)
}

/// None to let the turn end, else the refusal; an Err is a read error, which lets it end too.
/// `listed_idle`: the Stop's own `background_tasks` (the harness's list of what it runs, 451 T183) was given and empty, so the
/// transcript's reading of what runs is not asked.
pub(crate) fn verdict(
    root: &Path,
    transcript: &str,
    listed_idle: bool,
) -> Result<Option<String>, String> {
    let Some((git_dir, feature, since)) = idle::last_start(root)? else {
        return Ok(None);
    };
    let (feature, since) = (feature.as_str(), since.as_str());
    let downs = rows(&git_dir.join("set-downs.jsonl"))?;
    let boxes = active(root, &downs, feature, since, false)?;
    // A RULING THAT HOLDS NEW WORK lets the session wait (451 T183, `holds`), and so does one that holds every open task by name
    // (T183's MODE 4, D6): a held task is never named, though a wait still reads it as open
    let named = holds::named(root, feature);
    let free: Vec<&(String, String)> = boxes.iter().filter(|(id, _)| !named.contains(id)).collect();
    if free.is_empty() || holds::held(root, feature).is_some() {
        return Ok(None);
    }
    // the transcript last: the costly read (206 MB on 2026-10-26), where the status line is one small file. Something running is
    // waited on, its end waking the session (451 T183); the harness's own empty list of what runs is taken at its word
    let path = Path::new(transcript);
    if !listed_idle && path.is_file() && !running(path).map_err(|e| e.to_string())?.is_empty() {
        return Ok(None);
    }
    let number = |f: &str| f.split('-').next().unwrap_or(f).to_owned();
    // ONLY PARKED STAGES LEFT (449 T244): the stop the GM asked for, which `make set-down` takes; never one of them named as the next
    if free
        .iter()
        .all(|(_, t)| crate::parked::held_task(root, &git_dir, t).is_some())
    {
        return Ok(Some(format!(
            "BLOCKED: feature {feature} has {} open task(s), every one a parked hamlet stage the GM stops before (feature 449 T244) - do not start one; stop and set it down, which this ruling lets through: make set-down F={} WHY=\"the parked stages wait for the GM, 2026-11-21\"\n\n{}",
            boxes.len(),
            number(feature),
            crate::parked::RULING
        )));
    }
    // PERFORMANCE WORK FIRST (feature 451 FR-013): the next named is an open performance task where an active feature holds one; a
    // reader's error names the feature's first box, as before, rather than let the refusal go
    let mut lands = Lands::new();
    let next = match next_performance_in(root, &git_dir, feature, true, &mut lands)
        .ok()
        .flatten()
    {
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
        // the first task that can start (451 T102), a wait's read error counted as none, a parked stage's never (449 T244)
        None => free
            .iter()
            .filter(|(_, t)| crate::parked::held_task(root, &git_dir, t).is_none())
            .find(|(id, t)| !waits(root, feature, &boxes, (id, t), &mut lands).unwrap_or(false))
            .map_or_else(
                || "none can start yet: each waits on a day or a landing, 451 T102".to_owned(),
                |(id, t)| format!("{id} {}", t.chars().take(80).collect::<String>()),
            ),
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
    // AN UNCHANGED REFUSAL IS SAID ONCE (451 T171): in full, then in one line until it changes or a Stop passes without it
    let said = crate::once::file(&super::event_log_hooks::common_git_dir(&root), &event.input);
    // A COMPACTION FORGETS WHAT WAS SAID (451 T171): a SessionStart refuses nothing; after a compaction, a clear or a resume, the next
    // Stop says the block in full
    if event.name == "SessionStart" {
        crate::once::forget(said.as_deref(), field(&event.input, "source"));
        return Vec::new();
    }
    let transcript = field(&event.input, "transcript_path");
    let read_error = |why: String, detail: &str| {
        let _ = log::write(&Entry {
            guard: "set-down",
            event: "error",
            detail,
            rule: "read-error",
            context: Some(Value::String(why)),
            input: &event.input,
            session_name: &session.name(),
        });
        Vec::new()
    };
    // THE IDLE CHECK (451 T183, [`idle_check`]): the open-task block, said once while its text is unchanged - a repeat would only wake
    // a session that already heard it and chose to wait
    let listed_idle = event
        .input
        .get("background_tasks")
        .and_then(Value::as_array)
        .is_some_and(Vec::is_empty);
    let got = verdict(&root, transcript, listed_idle);
    if !matches!(got, Ok(Some(_))) {
        crate::once::clear(said.as_deref(), "set-down");
    }
    match got {
        Ok(None) => Vec::new(),
        Err(why) => read_error(why, "stop"),
        Ok(Some(text)) => {
            if crate::once::repeat(said.as_deref(), "set-down", &text, now() / 1_000_000).is_some()
            {
                log::fire(
                    "set-down",
                    "permitted",
                    "idle, unchanged: said before",
                    "said-once",
                    &event.input,
                    session,
                );
                return Vec::new();
            }
            log::fire(
                "set-down",
                "blocked",
                "idle",
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

mod builders;
pub mod holds;
mod idle;
mod stalls;
use builders::asks_the_gm;
pub use builders::{
    agent_builder, builder_brief, page_session_brief, page_session_listed, session_dispatched,
};
pub use idle::{idle_check, idle_check_with, status, Procs};

#[cfg(test)]
mod tests;
