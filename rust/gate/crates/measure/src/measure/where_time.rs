//! `make where-time F=<feature> [SINCE=<ISO>] [BY=tick]` - where a feature's time went, by task (feature 385 T77, plan D96; ported from
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
    cmp_f, event_logs, fixed, get, git, hhmm, is, load_events, need, py_str, s, spec_dir, t_of, ts,
    Event, Raised, Tally, IDLE_CAP_S,
};
use super::feature_report::tables::tool_cat;
use super::reply;
use super::task_phases::{foreground_spans, in_span};
use crate::Reply;

const WAIT_WORK: &str = "waiting on work";
const WAIT_GM: &str = "the GM";
const GM_AWAY: &str = "the GM away";
const BUCKET: [(&str, &str); 20] = [
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
    ("gate", "gate/tests"),
    ("quick test", "gate/tests"),
    ("test file", "gate/tests"),
    ("waiting: a background run", "background run"),
    ("waiting: the GM", "the GM"),
    ("idle (over an hour)", "idle"),
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
const COLUMNS: [&str; 14] = [
    "model",
    "tools",
    "gate/tests",
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
    for e in &evs[i + 1..] {
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
        .filter_map(Result::ok)
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
) -> Result<Tables, Raised> {
    let mut t = Tables {
        time: Vec::new(),
        agents: Vec::new(),
        secs: Vec::new(),
        rules: Tally::default(),
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
        let (mut between, mut window, mut last) = (false, "", String::new());
        for i in 0..evs.len().saturating_sub(1) {
            let (a, b) = (evs[i], evs[i + 1]);
            let ev = need(a, "ev")?;
            if ev == "Stop" && !between {
                window = window_class(evs, i)?;
            }
            between = (between || ev == "Stop") && ev != "UserPromptSubmit";
            let t0 = t_of(a)?;
            let gap = t_of(b)? - t0;
            if gap <= 0.0 {
                continue;
            }
            let run = in_span(t0, &fg);
            let cat = if between {
                window.to_owned()
            } else if gap > IDLE_CAP_S {
                "idle (over an hour)".to_owned()
            } else if !run.is_empty() {
                format!("waiting: {run}")
            } else if ev == "PreToolUse" {
                tool_cat(a)
            } else {
                "thinking".to_owned()
            };
            let named = match inputs {
                Some(inputs) if ev == "PreToolUse" => {
                    named_task(inputs.get(&s(a, "id")).map_or("", String::as_str), &pattern)
                }
                _ => String::new(),
            };
            if !named.is_empty() {
                last.clone_from(&named);
            }
            let rule = if !named.is_empty() {
                "named"
            } else if !last.is_empty() {
                "carried"
            } else {
                "the mark"
            };
            t.rules.add(&rule.to_owned(), gap);
            let task = if last.is_empty() {
                task_at(starts, t0)
            } else {
                last.clone()
            };
            add(&mut t.time, &task, bucket(&cat), gap);
        }
    }
    let mut open: HashMap<String, (f64, String, String)> = HashMap::new();
    for e in sorted {
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
    Ok(t)
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

/// The task starts of the feature (`<git common dir>/task-starts.jsonl`), at or after `since`, in time order.
fn starts(root: &Path, name: &str, since: &str) -> Result<Vec<(f64, String)>, Raised> {
    let common = git(
        root,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    )?;
    let common = strip(&common);
    let path = Path::new(if common.is_empty() { "." } else { common }).join("task-starts.jsonl");
    let text = super::events::text_if_file(&path)?;
    let mut out = Vec::new();
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
        if !since.is_empty() && utc()? < since {
            continue;
        }
        out.push((ts(utc()?)?, py_str(need(r, "task")?)));
    }
    out.sort_by(|a, b| cmp_f(a.0, b.0).then(a.1.cmp(&b.1)));
    Ok(out)
}

/// `where_time.py`'s command line.
#[must_use]
pub fn cli(args: &[String], projects: &Path, clones: &Path) -> Reply {
    let specs = [
        Spec::value("--since"),
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
        format!("usage: l7r-gate measure where-time [--since SINCE] [--root ROOT] [--by-tick] feature\nl7r-gate measure where-time: error: {why}\n"),
        2,
    )
}

/// `main` after its arguments: the tables' text, or the missing directory's message (exit 2).
fn run(
    feature: &str,
    since: &str,
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
    let events = load_events(&event_logs(&root, &name, clones), &[], since, "")?;
    let feature_no = name.split('-').next().unwrap_or_default();
    if by_tick {
        // ...EACH TASK'S TICK WINDOW (feature 385 T115, D132): what the GM's speed question was answered with by hand
        let rel = format!("specs/{name}/tasks.md");
        let log_p = git(
            &root,
            &["log", "--reverse", "--format=@@%cI", "-p", "--", &rel],
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
        let t = tables(&events, &marks, None, feature_no)?;
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
    let mut sids: Vec<String> = events.iter().map(|e| s(e, "sid")).collect();
    sids.sort();
    sids.dedup();
    let inputs = transcript_inputs(&sids, projects)?;
    let t = tables(&events, &starts, Some(&inputs), feature_no)?;
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
    Ok(Ok(format!(
        "{}\n\nbooked by: {rules} (feature 385 T89: the task a call names, else the last named, else the mark)\n",
        render(&t, &order)
    )))
}

#[cfg(test)]
mod tests;
