//! `make where-time F=<feature> [SINCE=<ISO>] [UNTIL=<ISO>] [BY=tick]` - where a feature's time went, by task (feature 385 T77, plan D96; ported from
//! `scripts/measure/where_time.py` by feature 449 T119, `ask:449-T83-scope`, no door).
//!
//! WHY. The GM's step-back of 2026-10-18 asked for each task's time by piece; the scratch script that answered it booked T05 224 minutes,
//! about 80 of them the overnight stall: hook events cut the 04:20-09:15 gap into pieces under an hour, each booked "thinking". So from a
//! session's `Stop` to its next `UserPromptSubmit` every gap is BETWEEN TURNS - waiting on background work, on the GM, or the GM away
//! (feature 385 T90, D111). A notification that wakes the session fires the prompt hooks, so a woken turn's work is booked to its task.
//!
//! THE TABLES. Each gap between a session's events goes to the task its tool call NAMES, else the last named, else the one the clone's
//! last `make task-start` made active (T89, D110), in `feature-report`'s categories grouped into buckets; the agents table counts each
//! subagent and its minutes by the task active at its launch. `--by-tick` books each tick-to-tick window instead (T115, D132).

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use fancy_regex::Regex;
use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_gate_core::record::py_lines;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::pyjson::dumps;
use serde_json::Value;

use super::events::{
    cmp_f, event_logs, fixed, get, git, hhmm, is, lines_of, load_all, need, on, py_str, s,
    spec_dir, t_of, ts, turn_lines, with_turns, Event, Raised, Tally, FOREIGN, IDLE_CAP_S,
};
use super::feature_report::tables::tool_cat;
use super::reply;
use super::task_phases::{foreground_spans, in_span};
use crate::Reply;

const WAIT_WORK: &str = "waiting on work";
/// An agent's span's lines, which a wait between turns is booked by (T09: read from every feature's log, `columns::flight`'s doc).
const AGENT_LINES: [&str; 2] = ["SubagentStart", "SubagentStop"];
const WAIT_GM: &str = "the GM";
const GM_AWAY: &str = "the GM away";
// The guard's table's buckets (`event_log_hooks::BUCKETS`, feature 451 D2) are columns of their own since T08: a Bash call with a `make`
// is booked by it through that table (`columns::line_bucket`), so a past log's frozen `cat` re-books; `quick test`, `test file` and `gate`
// are a past log's cats of a line with no `make`. `compile` is the phases a call holds (D4), split out of its gap.
/// The column of the time the session spent in another feature's turn between this one's (T09's plan review, 2026-11-21).
const ANOTHER: &str = "another feature";
const BUCKET: [(&str, &str); 27] = [
    ("tests", "tests"),
    ("compile", "compile"),
    ("land", "land"),
    ("review", "review"),
    ("docs", "docs"),
    ("spec-kit step", "spec-kit step"),
    ("thinking", "model"),
    ("writing the spec", "model"),
    ("waiting: spec-fidelity", "plan review"),
    ("waiting: spec-fidelity-verify", "plan review"),
    ("dispatching: spec review", "plan review"),
    ("waiting: impl-drift", "claims check"),
    ("waiting: claims-triage", "claims check"),
    ("dispatching: claims check", "claims check"),
    ("waiting: glyph-check", "glyph check"),
    ("waiting: round-arbiter", "arbiter"),
    ("dispatching: round arbiter", "arbiter"),
    ("gate", "gate"),
    ("quick test", "tests"),
    ("test file", "tests"),
    ("waiting: a background run", "background run"),
    ("waiting: the GM", "the GM"),
    ("idle (over an hour)", "idle"),
    (ANOTHER, ANOTHER),
    (WAIT_WORK, WAIT_WORK),
    (WAIT_GM, WAIT_GM),
    (GM_AWAY, GM_AWAY),
];
const RECORD: [&str; 9] = [
    "quote-check",
    "record-format",
    "source-reader",
    "source-applicability",
    "translation-check",
    "intro-check",
    "modal-",
    "entry-drift",
    "research-pass",
];
const COLUMNS: [&str; 21] = [
    "model",
    "tests",
    "compile",
    "gate",
    "land",
    "review",
    "docs",
    "spec-kit step",
    "tools",
    "background run",
    "plan review",
    "claims check",
    "record/modal checks",
    "glyph check",
    "arbiter",
    "other subagent",
    WAIT_WORK,
    WAIT_GM,
    GM_AWAY,
    "idle",
    ANOTHER,
];

/// The bucket a category goes to (`bucket`).
#[must_use]
pub fn bucket(cat: &str) -> &str {
    if let Some((_, b)) = BUCKET.iter().find(|(c, _)| *c == cat) {
        return b;
    }
    if (cat.starts_with("waiting: ") && RECORD.iter().any(|r| cat.contains(r)))
        || cat == "dispatching: record check"
        || cat == "dispatching: review check"
    {
        return "record/modal checks";
    }
    if cat.starts_with("waiting: ") || cat.starts_with("dispatching") {
        return "other subagent";
    }
    "tools"
}

/// The task the last start at or before `t` made active, `-` before any (`task_at`).
#[must_use]
pub fn task_at(starts: &[(f64, String)], t: f64) -> String {
    starts
        .iter()
        .take_while(|(s, _)| *s <= t)
        .last()
        .map_or_else(|| "-".to_owned(), |(_, k)| k.clone())
}

/// The class of the between-turns window that opens at the `Stop` `evs[i]` (D111), by the prompt that ends it (`window_class`).
fn window_class(evs: &[&Event], i: usize) -> Result<&'static str, Raised> {
    for e in evs[i + 1..].iter().filter(|e| !on(e, FOREIGN)) {
        if need(e, "ev")? == "UserPromptSubmit" {
            if !e.get("gm").is_none_or(super::events::truthy) {
                return Ok(WAIT_WORK);
            }
            return Ok(if t_of(e)? - t_of(evs[i])? > IDLE_CAP_S {
                GM_AWAY
            } else {
                WAIT_GM
            });
        }
    }
    // no prompt yet: the window is still open, on work in the background
    Ok(WAIT_WORK)
}

/// The pattern of the one task a tool call's input names - `T=T60`, `TASK=T60`, "task T60", a `385 T60:` commit, a plan bundle's
/// `plan-...-T60`, a `## T60 - ` or `### T60 ` heading (feature 385 T89, plan D110; `named_task`'s).
#[must_use]
pub fn named_pattern(feature_no: &str) -> Regex {
    let lead = if feature_no.is_empty() {
        String::new()
    } else {
        format!(r"\b{feature_no} |")
    };
    super::events::re(&format!(
        r"(?:\bT=|\bTASK=|\btask |{lead}(?<=[a-z])-(?=T\d)|#{{2,3}} )(T\d{{2,}}[a-z]?)\b"
    ))
}

/// The one task `text` names, or "" when it names none or several (`named_task`).
#[must_use]
pub fn named_task(text: &str, pattern: &Regex) -> String {
    let mut ids: Vec<String> = pattern
        .captures_iter(text)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    ids.sort();
    ids.dedup();
    if ids.len() == 1 {
        ids.remove(0)
    } else {
        String::new()
    }
}

/// tool-use id -> its input as `json.dumps` writes it, from each session's transcript (`<projects>/*/<sid>.jsonl`, `transcript_inputs`).
///
/// # Errors
///
/// A transcript line holding a tool use that is no object, or whose content is not iterable: the Python's raise.
pub fn transcript_inputs(
    sids: &[String],
    projects: &Path,
) -> Result<HashMap<String, String>, Raised> {
    let mut out = HashMap::new();
    for sid in sids {
        for project in super::events::names(projects) {
            let path = projects.join(project).join(format!("{sid}.jsonl"));
            let Ok(bytes) = std::fs::read(&path) else {
                continue;
            };
            let text = l7r_guard::guards::event_log_hooks::read::universal(
                &String::from_utf8_lossy(&bytes),
            );
            for line in text
                .split_inclusive('\n')
                .filter(|l| l.contains("\"tool_use\""))
            {
                let Ok(rec) = serde_json::from_str::<Value>(line) else {
                    continue;
                };
                let Some(rec) = rec.as_object() else {
                    return Err("AttributeError: a transcript line is no object".to_owned());
                };
                let msg = get(rec, "message");
                let content = if super::events::truthy(msg) {
                    msg.as_object()
                        .ok_or_else(|| {
                            "AttributeError: a transcript message is no object".to_owned()
                        })?
                        .get("content")
                        .unwrap_or(&Value::Null)
                } else {
                    &Value::Null
                };
                let blocks: &[Value] = match content {
                    Value::Array(items) => items,
                    Value::Number(_) if super::events::truthy(content) => {
                        return Err("TypeError: a transcript's content is not iterable".to_owned())
                    }
                    Value::Bool(true) => {
                        return Err("TypeError: a transcript's content is not iterable".to_owned())
                    }
                    _ => &[],
                };
                for c in blocks.iter().filter_map(Value::as_object) {
                    if is(c, "type", "tool_use") {
                        out.insert(s(c, "id"), dumps(get(c, "input"), None, true));
                    }
                }
            }
        }
    }
    Ok(out)
}

/// Minutes by task and bucket, agents by task and kind, agent seconds by task and kind.
pub struct Tables {
    /// Seconds by task and bucket, tasks in the order first booked.
    pub time: Vec<(String, Tally<String>)>,
    /// Agents by task and kind.
    pub agents: Vec<(String, Tally<String>)>,
    /// Agent seconds by task and kind.
    pub secs: Vec<(String, Tally<String>)>,
    /// Which rule booked each gap's seconds: `named`, `carried`, `the mark`.
    pub rules: Tally<String>,
    /// The seconds of the waits between turns on work by what held them (T09): `shell`, `agent`, `monitor`, or `none`.
    pub waits: Tally<String>,
}

fn add(rows: &mut Vec<(String, Tally<String>)>, task: &str, key: &str, by: f64) {
    let i = rows.iter().position(|(k, _)| k == task).unwrap_or_else(|| {
        rows.push((task.to_owned(), Tally::default()));
        rows.len() - 1
    });
    rows[i].1.add(&key.to_owned(), by);
}

fn row<'a>(rows: &'a [(String, Tally<String>)], task: &str) -> Option<&'a Tally<String>> {
    rows.iter().find(|(k, _)| k == task).map(|(_, t)| t)
}

/// The events in time order, the Python's `sorted(events, key=lambda e: parse_t(e["t"]))`.
fn by_time(events: &[Event]) -> Result<Vec<&Event>, Raised> {
    let mut keyed = Vec::with_capacity(events.len());
    for e in events {
        keyed.push((t_of(e)?, e));
    }
    keyed.sort_by(|a, b| cmp_f(a.0, b.0));
    Ok(keyed.into_iter().map(|(_, e)| e).collect())
}

/// The tables (`tables`). With `inputs` (tool-use id -> its input), a gap goes to the task its tool call NAMES, else the last named,
/// else the mark (T89, D110).
///
/// # Errors
///
/// An event with no kind or a time the Python could not read.
#[expect(clippy::implicit_hasher, reason = "the map `transcript_inputs` makes")]
pub fn tables(
    events: &[Event],
    starts: &[(f64, String)],
    inputs: Option<&HashMap<String, String>>,
    feature_no: &str,
    booking: &Booking,
) -> Result<Tables, Raised> {
    let mut t = Tables {
        time: Vec::new(),
        agents: Vec::new(),
        secs: Vec::new(),
        rules: Tally::default(),
        waits: Tally::default(),
    };
    let sorted = by_time(events)?;
    let mut order: Vec<String> = Vec::new();
    let mut groups: HashMap<String, Vec<&Event>> = HashMap::new();
    for e in &sorted {
        let k = s(e, "sid");
        if !groups.contains_key(&k) {
            order.push(k.clone());
        }
        groups.entry(k).or_default().push(e);
    }
    let fg = foreground_spans(events)?;
    let pattern = named_pattern(feature_no);
    let inputs = inputs.filter(|i| !i.is_empty());
    for k in &order {
        let evs = &groups[k];
        // `opener`: the `Stop` that opened the wait between turns, whose `inflight` runs the wait is booked to (T09)
        // `away`: inside another feature's turn
        let (mut between, mut window, mut last, mut opener, mut away) =
            (false, "", String::new(), None::<&Event>, false);
        // the main session's call or state a subagent's line falls inside (`booking`'s doc)
        let mut held: (String, Option<&columns::Split>) = ("thinking".to_owned(), None);
        for i in 0..evs.len().saturating_sub(1) {
            let (a, b) = (evs[i], evs[i + 1]);
            let ev = need(a, "ev")?;
            // a subagent's own call, or a subagent's start or stop: the session goes on with what it was doing (T08's model check)
            // a line of another feature's turn (`with_turns`) moves no state of this one's: it only opens or closes that turn (T09)
            let foreign = on(a, FOREIGN);
            let theirs = (on(a, "tool") && on(a, "by"))
                || ev == "SubagentStart"
                || ev == "SubagentStop"
                || foreign;
            if foreign {
                // away from its prompt to the session's next line of this feature's: the waits between that feature's turns are its own
                away = away || ev == "UserPromptSubmit";
            } else if ev == "Stop" && !between {
                (window, opener) = (window_class(evs, i)?, Some(a));
            }
            between = foreign && between
                || !foreign && (between || ev == "Stop") && ev != "UserPromptSubmit";
            if !theirs {
                away = false;
                // the session's own line moves its state on even across a zero gap: a background agent's `PostToolUse` and its
                // `SubagentStart` share a millisecond, and skipping first left the launch's category held for the thinking after it
                held = if ev == "PreToolUse" {
                    (pre_cat(a, &booking.goal), booking.splits.get(&s(a, "id")))
                } else {
                    ("thinking".to_owned(), None)
                };
            }
            let t0 = t_of(a)?;
            let gap = t_of(b)? - t0;
            if gap <= 0.0 {
                continue;
            }
            let run = in_span(t0, &fg);
            let mut spans = None;
            let cat = if away {
                ANOTHER.to_owned()
            } else if between {
                window.to_owned()
            } else if gap > IDLE_CAP_S {
                "idle (over an hour)".to_owned()
            } else if !run.is_empty() {
                format!("waiting: {run}")
            } else {
                spans = held.1;
                held.0.clone()
            };
            let named = match inputs {
                Some(inputs) if ev == "PreToolUse" => {
                    named_task(inputs.get(&s(a, "id")).map_or("", String::as_str), &pattern)
                }
                _ => String::new(),
            };
            let (rule, task) = carry(&named, &mut last, starts, t0);
            t.rules.add(&rule.to_owned(), gap);
            let (compile, gate) = spans.map_or((0.0, 0.0), |c| {
                (
                    columns::overlap(&c.compile, t0, t0 + gap),
                    columns::overlap(&c.gate, t0, t0 + gap),
                )
            });
            for (col, x) in [("compile", compile), ("gate", gate)] {
                if x > 0.0 {
                    add(&mut t.time, &task, col, x);
                }
            }
            if between && window == WAIT_WORK && !away {
                wait(&mut t, &task, booking.flight.book(k, opener, t0, t0 + gap));
                continue;
            }
            add(&mut t.time, &task, bucket(&cat), gap - compile - gate);
        }
    }
    agents(&sorted, starts, &mut t)?;
    Ok(t)
}

/// The rule a gap's task is found by and the task: the one its call names, else the last named, else the mark at `t0` (T89, D110).
fn carry(
    named: &str,
    last: &mut String,
    starts: &[(f64, String)],
    t0: f64,
) -> (&'static str, String) {
    if !named.is_empty() {
        named.clone_into(last);
        return ("named", last.clone());
    }
    if last.is_empty() {
        ("the mark", task_at(starts, t0))
    } else {
        ("carried", last.clone())
    }
}

/// A wait on work booked, each second to the run in flight that held it (T09, D3; `columns::flight`'s doc), and counted by what held it.
fn wait(t: &mut Tables, task: &str, booked: Vec<(String, &'static str, f64)>) {
    for (col, held, secs) in booked {
        add(&mut t.time, task, &col, secs);
        let held = if held.is_empty() { "none" } else { held };
        t.waits.add(&held.to_owned(), secs);
    }
}

/// Each subagent counted, with its minutes, by the task active at its launch.
fn agents(sorted: &[&Event], starts: &[(f64, String)], t: &mut Tables) -> Result<(), Raised> {
    let mut open: HashMap<String, (f64, String, String)> = HashMap::new();
    for e in sorted.iter().copied() {
        if is(e, "ev", "SubagentStart") {
            let at = t_of(e)?;
            open.insert(
                s(e, "aid"),
                (
                    at,
                    super::events::or_text(get(e, "agent"), "?"),
                    task_at(starts, at),
                ),
            );
        } else if is(e, "ev", "SubagentStop") {
            if let Some((t0, kind, task)) = open.remove(&s(e, "aid")) {
                add(&mut t.agents, &task, &kind, 1.0);
                add(&mut t.secs, &task, &kind, t_of(e)? - t0);
            }
        }
    }
    Ok(())
}

/// What a call's gap is booked by beyond its line (feature 451 T08): the compile and landing-gate spans of each call ([`columns::splits_by_id`]) and the
/// Makefile's default goal. A subagent's call (`by`) inside the main session's turn is booked as what the session was doing - the call it
/// was waiting on, or the model - so a builder's line no longer cuts the session's `make static` in two; between turns it keeps the wait.
#[derive(Default)]
pub struct Booking {
    /// tool-use id -> its run's compile and landing-gate spans.
    pub splits: HashMap<String, columns::Split>,
    /// The Makefile's default goal.
    pub goal: String,
    /// The window's background runs and agents, which a wait between turns is booked to (T09).
    pub flight: columns::Flight,
}

/// A `PreToolUse` line's category: a Bash call with a `make` by the guard's table (`other` the line's `other tool`), else its `cat`.
fn pre_cat(e: &Event, goal: &str) -> String {
    if is(e, "tool", "Bash") && super::events::on(e, "make") {
        match columns::line_bucket(e, goal) {
            "other" => "other tool".to_owned(),
            b => b.to_owned(),
        }
    } else {
        tool_cat(e)
    }
}

/// `sum(values)` from Python's `0`, never Rust's `-0.0`.
fn total(t: &Tally<String>) -> f64 {
    t.items().iter().fold(0.0, |a, (_, v)| a + v)
}

/// The two tables as Markdown (`render`).
#[must_use]
pub fn render(t: &Tables, order: &[String]) -> String {
    let order: Vec<&String> = order
        .iter()
        .filter(|k| row(&t.time, k).is_some() || row(&t.agents, k).is_some())
        .collect();
    let mut lines = vec![
        format!("| task | total | {} |", COLUMNS.join(" | ")),
        format!("|---|---|{}", "---|".repeat(COLUMNS.len())),
    ];
    let mut tot: Tally<String> = Tally::default();
    let empty = Tally::default();
    let cells = |c: &Tally<String>| {
        COLUMNS
            .map(|x| fixed(c.get(&x.to_owned()) / 60.0, 0))
            .join(" | ")
    };
    for k in &order {
        let c = row(&t.time, k).unwrap_or(&empty);
        for (key, v) in c.items() {
            tot.add(key, *v);
        }
        lines.push(format!(
            "| {k} | {} | {} |",
            fixed(total(c) / 60.0, 0),
            cells(c)
        ));
    }
    lines.push(format!(
        "| all | {} | {} |",
        fixed(total(&tot) / 60.0, 0),
        cells(&tot)
    ));
    lines.extend(
        [
            "",
            "| task | agents | agent minutes | by kind (count) |",
            "|---|---|---|---|",
        ]
        .map(String::from),
    );
    for k in &order {
        let Some(a) = row(&t.agents, k).filter(|a| !a.is_empty()) else {
            continue;
        };
        let secs = row(&t.secs, k).map_or(0.0, total);
        let kinds = a
            .most_common()
            .iter()
            .map(|(n, c)| format!("{n} {c}"))
            .collect::<Vec<_>>()
            .join(", ");
        lines.push(format!(
            "| {k} | {} | {} | {kinds} |",
            total(a),
            fixed(secs / 60.0, 0)
        ));
    }
    lines.join("\n")
}

/// (UTC seconds, task) of each task's tick: the first commit in `git log --reverse --format=@@%cI -p -- tasks.md` that turned its box
/// `[x]` (feature 385 T115, D132; `parse_ticks`).
///
/// # Errors
///
/// A commit time `fromisoformat` refuses.
pub fn parse_ticks(log_p: &str) -> Result<Vec<(f64, String)>, Raised> {
    static TICK: std::sync::LazyLock<Regex> =
        std::sync::LazyLock::new(|| super::events::re(r"^\+- \[x\] (T\d+[a-z]?)\b"));
    let mut out: Vec<(f64, String)> = Vec::new();
    let mut cur: Option<f64> = None;
    for line in py_lines(log_p) {
        let lead = line.get(2..).unwrap_or("");
        if line.starts_with("@@") && lead.chars().next().is_some_and(|c| c.is_ascii_digit()) {
            cur = Some(ts(strip(lead))?);
        } else if let (Ok(Some(m)), Some(at)) = (TICK.captures(line), cur) {
            if !out.iter().any(|(_, k)| *k == m[1]) {
                out.push((at, m[1].to_owned()));
            }
        }
    }
    Ok(out)
}

/// (start, end, label) of each tick's window - from the tick before it (or `since`) to it - the tasks ticked in one commit sharing a
/// window, "T96+T98" (D132; `tick_windows`).
#[must_use]
pub fn tick_windows(ticks: &[(f64, String)], since: f64) -> Vec<(f64, f64, String)> {
    let mut by_t: Vec<(f64, Vec<&str>)> = Vec::new();
    for (t, k) in ticks.iter().filter(|(t, _)| *t >= since) {
        // a dict keyed by the tick's time: one commit's ticks share it exactly
        #[expect(clippy::float_cmp, reason = "the Python's dict keys, equal floats")]
        let same = |at: &f64| at == t;
        match by_t.iter_mut().find(|(at, _)| same(at)) {
            Some((_, ks)) => ks.push(k),
            None => by_t.push((*t, vec![k])),
        }
    }
    by_t.sort_by(|a, b| cmp_f(a.0, b.0));
    let mut prev = since;
    by_t.into_iter()
        .map(|(t, ks)| {
            let w = (prev, t, ks.join("+"));
            prev = t;
            w
        })
        .collect()
}

/// The task starts of the feature (`<git common dir>/task-starts.jsonl`), in time order: those at or after `since`, and the last one
/// before it - the task at hand when the window opens (T207: cutting it booked the window's first stretch to `-`).
fn starts(root: &Path, name: &str, since: &str) -> Result<Vec<(f64, String)>, Raised> {
    let common = git(
        root,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    )?;
    let common = strip(&common);
    let path = Path::new(if common.is_empty() { "." } else { common }).join("task-starts.jsonl");
    let text = super::events::text_if_file(&path)?;
    let mut out: Vec<(f64, String)> = Vec::new();
    let mut last_before: Option<(f64, String)> = None;
    for x in py_lines(&text).into_iter().filter(|x| !strip(x).is_empty()) {
        let r: Value = serde_json::from_str(x).map_err(|e| format!("JSONDecodeError: {e}"))?;
        let r = r
            .as_object()
            .ok_or_else(|| "AttributeError: a task start is no object".to_owned())?;
        if get(r, "feature").as_str() != Some(name) {
            continue;
        }
        let utc = || match need(r, "utc")? {
            Value::String(u) => Ok(u.as_str()),
            _ => Err("TypeError: a task start's time is no text".to_owned()),
        };
        let start = (ts(utc()?)?, py_str(need(r, "task")?));
        // before SINCE by the same text comparison the events are cut by (`load_events`), so the window opens on one instant
        if !since.is_empty() && utc()? < since {
            if last_before
                .as_ref()
                .is_none_or(|b| cmp_f(start.0, b.0).is_ge())
            {
                last_before = Some(start);
            }
            continue;
        }
        out.push(start);
    }
    out.extend(last_before);
    out.sort_by(|a, b| cmp_f(a.0, b.0).then(a.1.cmp(&b.1)));
    Ok(out)
}

/// `where_time.py`'s command line.
#[must_use]
pub fn cli(args: &[String], projects: &Path, clones: &Path) -> Reply {
    let specs = [
        Spec::value("--since"),
        Spec::value("--until"),
        Spec::value("--root"),
        Spec::flag("--by-tick"),
    ];
    let p = match parse_with(args, &specs, 1) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => return usage("the following arguments are required: feature"),
        Err(why) => return usage(&why),
    };
    match run(
        &p.positional[0],
        p.text("--since", ""),
        p.text("--until", ""),
        p.text("--root", "."),
        p.on("--by-tick"),
        projects,
        clones,
    ) {
        Ok(Ok(text)) => reply(text, String::new(), 0),
        Ok(Err(missing)) => reply(String::new(), format!("{missing}\n"), 2),
        Err(why) => reply(
            String::new(),
            format!("Traceback (most recent call last):\n  l7r-gate measure where-time\n{why}\n"),
            1,
        ),
    }
}

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!("usage: l7r-gate measure where-time [--since SINCE] [--until UNTIL] [--root ROOT] [--by-tick] feature\nl7r-gate measure where-time: error: {why}\n"),
        2,
    )
}

/// The window's events (cut at UNTIL), its sessions, its runs and what the tables book a call's gap by (feature 451 T08). The logs are read
/// to their end, so a run still going at UNTIL is found and clipped there, not dropped.
type Booked = (Vec<Event>, Vec<String>, columns::Runs, Booking);

fn booked(
    root: &Path,
    name: &str,
    (since, until): (&str, &str),
    starts: &[(f64, String)],
    projects: &Path,
    clones: &Path,
) -> Result<Booked, Raised> {
    let loaded = load_all(&event_logs(root, name, clones), &[], since, "")?;
    let mut sids: Vec<String> = loaded
        .stream
        .iter()
        .filter(|e| until.is_empty() || s(e, "t").as_str() <= until)
        .map(|e| s(e, "sid"))
        .collect();
    sids.sort();
    sids.dedup();
    // the sessions' turn lines from every feature's log, since they are filed in whichever was active (T09, `turn_lines`' doc)
    let turns = turn_lines(root, clones, &sids, (since, until));
    let events: Vec<Event> = with_turns(&loaded.stream, turns)
        .into_iter()
        .filter(|e| until.is_empty() || s(e, "t").as_str() <= until)
        .collect();
    let end = if until.is_empty() {
        let mut last = 0.0_f64;
        for e in loaded.stream.iter().chain(&loaded.aside) {
            last = last.max(t_of(e)?);
        }
        last
    } else {
        ts(until)?
    };
    let makefile = std::fs::read_to_string(root.join("Makefile")).unwrap_or_default();
    let goal = columns::default_goal(&makefile);
    let queued = columns::enqueued(&sids, projects);
    let (stops, sub_queued) = columns::read_subagents(&sids, projects);
    let window = columns::Window {
        end,
        enqueued: &queued,
        stopped: &stops,
        queued: &sub_queued,
        goal: &goal,
    };
    let runs = columns::runs(&loaded.stream, &loaded.aside, starts, &window)?;
    let booking = Booking {
        splits: columns::splits_by_id(&runs),
        goal: goal.clone(),
        flight: columns::flight(
            &runs,
            &lines_of(root, clones, &sids, &AGENT_LINES),
            &loaded.stream,
            end,
        )?,
    };
    Ok((events, sids, runs, booking))
}

/// `main` after its arguments: the tables' text, or the missing directory's message (exit 2).
fn run(
    feature: &str,
    since: &str,
    until: &str,
    root_arg: &str,
    by_tick: bool,
    projects: &Path,
    clones: &Path,
) -> Result<Result<String, String>, Raised> {
    let top = git(Path::new(root_arg), &["rev-parse", "--show-toplevel"])?;
    let top = strip(&top);
    let root = PathBuf::from(if top.is_empty() { root_arg } else { top });
    let Some(d) = spec_dir(&root, feature)? else {
        return Ok(Err(format!("where-time: no specs/{feature}-* directory")));
    };
    let name = d
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    let starts = starts(&root, &name, since)?;
    let (events, sids, runs, booking) =
        booked(&root, &name, (since, until), &starts, projects, clones)?;
    let feature_no = name.split('-').next().unwrap_or_default();

    if by_tick {
        // ...EACH TASK'S TICK WINDOW (feature 385 T115, D132): what the GM's speed question was answered with by hand
        // ...a tick the tick archived in the same write is in tasks-done.md's history (feature 449 T142)
        let rel = format!("specs/{name}/tasks.md");
        let done = format!("specs/{name}/tasks-done.md");
        let log_p = git(
            &root,
            &[
                "log",
                "--reverse",
                "--format=@@%cI",
                "-p",
                "--",
                &rel,
                &done,
            ],
        )?;
        let t0 = if since.is_empty() {
            let mut first: Option<f64> = None;
            for e in &events {
                let t = t_of(e)?;
                first = Some(first.map_or(t, |f| f.min(t)));
            }
            first.unwrap_or(0.0)
        } else {
            ts(since)?
        };
        let wins = tick_windows(&parse_ticks(&log_p)?, t0);
        let marks: Vec<(f64, String)> = wins.iter().map(|(s, _, k)| (*s, k.clone())).collect();
        let t = tables(&events, &marks, None, feature_no, &booking)?;
        let labels: Vec<String> = wins.iter().map(|(_, _, k)| k.clone()).collect();
        let mut text = render(&t, &labels);
        text += "\n\n| window | from (UTC) | to (UTC) | wall minutes |\n|---|---|---|---|\n";
        for (s, e, k) in &wins {
            let _ = writeln!(
                text,
                "| {k} | {} | {} | {} |",
                hhmm(*s),
                hhmm(*e),
                fixed((e - s) / 60.0, 0)
            );
        }
        return Ok(Ok(text));
    }
    let inputs = transcript_inputs(&sids, projects)?;
    let t = tables(&events, &starts, Some(&inputs), feature_no, &booking)?;
    // the tasks in the order of their first start, a task never started first: the Python sorted a set, so among those its order was its
    // string hash's; here it is the order first booked
    let first = |k: &str| starts.iter().find(|(_, t)| t == k).map_or(0.0, |(s, _)| *s);
    let mut order: Vec<String> = t.time.iter().map(|(k, _)| k.clone()).collect();
    for (k, _) in &t.agents {
        if !order.contains(k) {
            order.push(k.clone());
        }
    }
    order.sort_by(|a, b| cmp_f(first(a), first(b)));
    let rules = t
        .rules
        .most_common()
        .iter()
        .map(|(r, v)| format!("{r} {} min", fixed(v / 60.0, 0)))
        .collect::<Vec<_>>()
        .join(", ");
    let w = |k: &str| fixed(t.waits.get(&k.to_owned()) / 60.0, 0);
    Ok(Ok(format!(
        "{}\n\nbooked by: {rules} (feature 385 T89: the task a call names, else the last named, else the mark)\n\nthe waits between turns on \
         work, by what held them: a background shell {} min, an agent {} min, a monitor alone {} min, none {} min (feature 451 T09)\n\n{}",
        render(&t, &order),
        w("shell"),
        w("agent"),
        w("monitor"),
        w("none"),
        columns::render(&runs, &order)
    )))
}

pub mod columns;

#[cfg(test)]
mod tests;
