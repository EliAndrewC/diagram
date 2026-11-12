//! Whose time, each task's phases and its decision-log skeleton, for `make feature-report` (feature 385 amendment 4, plan D30-D33; ported
//! from `scripts/measure/task_phases.py` by feature 449 T119, `ask:449-T83-scope`, no door).
//!
//! WHY (the GM, 2026-10-18, asking T03's 2 h 25 min broken down before T04): the report put 64% of T03 under "thinking", but 202 of the 549
//! tool calls in T03's window were its SUBAGENTS' - a subagent's tool calls reach the session's hooks under the session's id with no
//! marker - so it could not say what the session did and what its reviewers did. And T03's decision log was written from memory.
//!
//! WHOSE CALL (D30). A tool event is a subagent's when its `tool_use` id is in a subagent transcript of its session
//! (`<projects>/<project>/<sid>/subagents/agent-<aid>.jsonl`), or when the hook recorded `by`. Where neither can say, a call inside a
//! subagent's start-to-stop window is that subagent's, an ESTIMATE. THE PHASES (D31, D32): a task's segments between decision points, the
//! session's calls, its working, waiting and idle time, and the subagent runs started in each. THE SKELETON (D33): a task's start, every
//! agent returned, every cohort and gate run, every plan heading stamped `part B (<UTC>)` or `Approach (re-answered <UTC>)`, and its tick.

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;
use serde_json::Value;

use super::events::{
    cmp_f, fixed, get, hhmm, is, on, or_s, or_text, py_float_of, re, s, t_of, ts, Event, Raised,
    Tally, IDLE_CAP_S,
};

static TOOL_ID: LazyLock<Regex> = LazyLock::new(|| re(r#""id":\s*"(toolu_[A-Za-z0-9_-]+)""#));
static STAMP: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?m)^#{3,4}\s+(T\d+)\s+(part B|Approach \(re-answered)\s*\(?\s*(\d{4}-\d\d-\d\dT\d\d:\d\d)(?::\d\d)?Z",
    )
});

/// (start, stop, a label) of a run or a span.
pub type Span = (f64, f64, String);

/// A cohort or gate run, the skeleton's (D33): a make target starting `cohort`, one the event log files as a `gate`, or `verify`.
#[must_use]
pub fn measured_run(e: &Event) -> bool {
    let target = or_s(e, "make");
    !target.is_empty()
        && (target.starts_with("cohort") || is(e, "cat", "gate") || target == "verify")
}

/// (`tool_use` id -> the subagent that made it, the subagent runs whose transcripts were found), from each session's subagent transcripts.
/// The sessions and their files are read in sorted order: the Python's set and `glob` gave theirs unordered, which only a tool id in two
/// transcripts could tell apart.
#[must_use]
pub fn subagent_calls(
    sids: &[String],
    projects: &Path,
) -> (HashMap<String, String>, HashSet<String>) {
    let mut out: HashMap<String, String> = HashMap::new();
    let mut found: HashSet<String> = HashSet::new();
    let mut sids: Vec<&str> = sids
        .iter()
        .map(String::as_str)
        .filter(|s| !s.is_empty())
        .collect();
    sids.sort_unstable();
    sids.dedup();
    for sid in sids {
        for project in super::events::names(projects) {
            let dir = projects.join(project).join(sid).join("subagents");
            for name in super::events::names(&dir) {
                let Some(aid) = name
                    .strip_prefix("agent-")
                    .and_then(|n| n.strip_suffix(".jsonl"))
                else {
                    continue;
                };
                found.insert(aid.to_owned());
                let text =
                    String::from_utf8_lossy(&std::fs::read(dir.join(&name)).unwrap_or_default())
                        .into_owned();
                for c in TOOL_ID.captures_iter(&text).filter_map(Result::ok) {
                    out.entry(c[1].to_owned()).or_insert_with(|| aid.to_owned());
                }
            }
        }
    }
    (out, found)
}

/// sid -> (start, stop, aid) of every subagent run logged with both ends, sorted (`_windows`).
fn windows(events: &[Event]) -> Result<HashMap<String, Vec<Span>>, Raised> {
    let mut started: HashMap<String, f64> = HashMap::new();
    let mut out: HashMap<String, Vec<Span>> = HashMap::new();
    for e in events {
        let aid = or_s(e, "aid");
        if aid.is_empty() || on(e, "tool") {
            continue;
        }
        if is(e, "ev", "SubagentStart") {
            let t = t_of(e)?;
            started.entry(aid).or_insert(t);
        } else if is(e, "ev", "SubagentStop") {
            if let Some(a) = started.get(&aid) {
                out.entry(s(e, "sid"))
                    .or_default()
                    .push((*a, t_of(e)?, aid));
            }
        }
    }
    for w in out.values_mut() {
        w.sort_by(|a, b| cmp_f(a.0, b.0).then(cmp_f(a.1, b.1)).then(a.2.cmp(&b.2)));
    }
    Ok(out)
}

/// The events, each subagent's tool event marked `by` its subagent and `how` it was told (D30): `transcript`, `hook`, or - inside the
/// window of a run whose own transcript was not `found` - `window`, the estimate.
///
/// # Errors
///
/// An event time the Python could not read.
#[expect(clippy::implicit_hasher, reason = "the maps `subagent_calls` makes")]
pub fn attribute(
    events: Vec<Event>,
    calls: &HashMap<String, String>,
    found: &HashSet<String>,
) -> Result<Vec<Event>, Raised> {
    let wins = windows(&events)?;
    let mut out = Vec::with_capacity(events.len());
    for mut e in events {
        if on(&e, "tool") {
            if on(&e, "by") {
                e.entry("how").or_insert_with(|| Value::from("hook"));
            } else if let Some(aid) = calls.get(&s(&e, "id")).filter(|a| !a.is_empty()) {
                e.insert("by".into(), Value::from(aid.clone()));
                e.insert("how".into(), Value::from("transcript"));
            } else if !is(&e, "tool", "Agent") {
                let t = t_of(&e)?;
                let hit = wins.get(&s(&e, "sid")).and_then(|w| {
                    w.iter()
                        .find(|(a, b, aid)| *a <= t && t <= *b && !found.contains(aid))
                });
                if let Some((_, _, aid)) = hit {
                    e.insert("by".into(), Value::from(aid.clone()));
                    e.insert("how".into(), Value::from("window"));
                }
            }
        }
        out.push(e);
    }
    Ok(out)
}

/// How each subagent tool call was told from the session's (`attribution`).
#[must_use]
pub fn attribution(events: &[Event]) -> Tally<String> {
    let mut out = Tally::default();
    for e in events
        .iter()
        .filter(|e| is(e, "ev", "PreToolUse") && on(e, "by"))
    {
        out.add(&s(e, "how"), 1.0);
    }
    out
}

/// The session's own events: every event but a subagent's tool call.
#[must_use]
pub fn session_events(events: &[Event]) -> Vec<Event> {
    events
        .iter()
        .filter(|e| !(on(e, "tool") && on(e, "by")))
        .cloned()
        .collect()
}

/// (the session's tool calls, its subagents' tool calls).
#[must_use]
pub fn call_counts(events: &[Event]) -> (usize, usize) {
    let pre = events.iter().filter(|e| is(e, "ev", "PreToolUse"));
    let sub = pre.clone().filter(|e| on(e, "by")).count();
    (pre.count() - sub, sub)
}

/// (start, stop, type, verdict) of every subagent run with both ends logged.
pub type Run = (f64, f64, String, String);

/// Every subagent run with both ends logged (`subagent_runs`).
///
/// # Errors
///
/// An event time the Python could not read.
pub fn subagent_runs(events: &[Event]) -> Result<Vec<Run>, Raised> {
    let mut started: HashMap<String, (f64, String)> = HashMap::new();
    let mut out = Vec::new();
    for e in events {
        let aid = or_s(e, "aid");
        if aid.is_empty() || on(e, "tool") {
            continue;
        }
        if is(e, "ev", "SubagentStart") {
            let first = (t_of(e)?, or_s(e, "agent"));
            started.entry(aid).or_insert(first);
        } else if is(e, "ev", "SubagentStop") && on(e, "agent") {
            if let Some((t0, _)) = started.remove(&aid) {
                out.push((t0, t_of(e)?, s(e, "agent"), or_s(e, "verdict")));
            }
        }
    }
    Ok(out)
}

/// (launch, return, type) of every session `Agent` call that ran in the foreground - its run's `SubagentStop` before the call returned
/// (D31): the session waits through it, no `Stop` marking the wait.
///
/// # Errors
///
/// An event time the Python could not read.
pub fn foreground_spans(events: &[Event]) -> Result<Vec<Span>, Raised> {
    let pre: HashMap<String, &Event> = events
        .iter()
        .filter(|e| is(e, "ev", "PreToolUse") && is(e, "tool", "Agent"))
        .map(|e| (s(e, "id"), e))
        .collect();
    let mut stops: HashMap<String, Vec<f64>> = HashMap::new();
    for e in events {
        if is(e, "ev", "SubagentStop") && on(e, "aid") && !on(e, "tool") {
            stops.entry(s(e, "aid")).or_default().push(t_of(e)?);
        }
    }
    let mut out = Vec::new();
    for e in events {
        if !(is(e, "ev", "PostToolUse") && is(e, "tool", "Agent")) {
            continue;
        }
        if let Some(a) = pre.get(&s(e, "id")) {
            let (t0, t1) = (t_of(a)?, t_of(e)?);
            let hit = stops
                .get(&or_s(e, "aid"))
                .is_some_and(|st| st.iter().any(|s| t0 <= *s && *s <= t1));
            if hit {
                out.push((t0, t1, or_text(get(a, "agent"), "subagent")));
            }
        }
    }
    Ok(out)
}

/// The type of the foreground run whose span holds `t`, or "".
#[must_use]
pub fn in_span(t: f64, spans: &[Span]) -> &str {
    spans
        .iter()
        .find(|(a, b, _)| *a <= t && t < *b)
        .map_or("", |(_, _, k)| k.as_str())
}

/// The events of each session, in the order the sessions first appear.
#[must_use]
pub fn by_sid(events: &[Event]) -> Vec<Vec<&Event>> {
    let mut order: Vec<String> = Vec::new();
    let mut groups: HashMap<String, Vec<&Event>> = HashMap::new();
    for e in events {
        let k = s(e, "sid");
        if !groups.contains_key(&k) {
            order.push(k.clone());
        }
        groups.entry(k).or_default().push(e);
    }
    order
        .iter()
        .map(|k| groups.remove(k).unwrap_or_default())
        .collect()
}

/// (start, end, `work` | `wait` | `idle`) of every gap between two of the session's events, per session (D31, `_gaps`).
///
/// # Errors
///
/// An event time the Python could not read.
pub fn gaps(events: &[Event]) -> Result<Vec<Span>, Raised> {
    let fg = foreground_spans(events)?;
    let own = session_events(events);
    let mut out = Vec::new();
    for evs in by_sid(&own) {
        for pair in evs.windows(2) {
            let (t0, t1) = (t_of(pair[0])?, t_of(pair[1])?);
            if t1 > t0 {
                let waits = is(pair[0], "ev", "Stop") || !in_span(t0, &fg).is_empty();
                let kind = if t1 - t0 > IDLE_CAP_S {
                    "idle"
                } else if waits {
                    "wait"
                } else {
                    "work"
                };
                out.push((t0, t1, kind.to_owned()));
            }
        }
    }
    Ok(out)
}

fn clip(spans: &[Span], lo: f64, hi: f64) -> Tally<String> {
    let mut out = Tally::default();
    for (t0, t1, kind) in spans {
        out.add(kind, 0f64.max(t1.min(hi) - t0.max(lo)));
    }
    out
}

/// The task's decision points as (time, what): the plan and arbiter rulings returned between `start` and `end` (`_cuts`).
fn cuts(
    events: &[Event],
    start: f64,
    end: f64,
    decision: &[&str],
) -> Result<Vec<(f64, String)>, Raised> {
    let mut out = Vec::new();
    for e in events {
        if is(e, "ev", "SubagentStop")
            && get(e, "agent")
                .as_str()
                .is_some_and(|a| decision.contains(&a))
        {
            let t = t_of(e)?;
            if start <= t && t <= end {
                out.push((
                    t,
                    strip(&format!("{} {}", s(e, "agent"), or_s(e, "verdict"))).to_owned(),
                ));
            }
        }
    }
    out.sort_by(|a, b| cmp_f(a.0, b.0).then(a.1.cmp(&b.1)));
    Ok(out)
}

/// What the phases read once a report: the gaps and the runs (`phase_rows` computed both again for each task, the same each time).
pub struct Phases<'a> {
    /// The events.
    pub events: &'a [Event],
    /// [`gaps`].
    pub gaps: Vec<Span>,
    /// [`subagent_runs`].
    pub runs: Vec<Run>,
    /// The session's own `PreToolUse` events.
    pub own: Vec<&'a Event>,
}

impl<'a> Phases<'a> {
    /// Read once.
    ///
    /// # Errors
    ///
    /// An event time the Python could not read.
    pub fn new(events: &'a [Event]) -> Result<Self, Raised> {
        Ok(Self {
            events,
            gaps: gaps(events)?,
            runs: subagent_runs(events)?,
            own: events
                .iter()
                .filter(|e| !(on(e, "tool") && on(e, "by")) && is(e, "ev", "PreToolUse"))
                .collect(),
        })
    }

    /// One row per phase of `task` (D32): span, what ended it, the session's calls, working, waiting and idle minutes, the subagents
    /// that started in it (`phase_rows`).
    ///
    /// # Errors
    ///
    /// An event time the Python could not read.
    pub fn rows(
        &self,
        task: &str,
        start: f64,
        end: f64,
        decision: &[&str],
    ) -> Result<Vec<String>, Raised> {
        let mut bounds = vec![(start, String::new())];
        bounds.extend(cuts(self.events, start, end, decision)?);
        bounds.push((end, "the tick or the last event".to_owned()));
        let mut rows = Vec::new();
        for w in bounds.windows(2) {
            let (a, b, what) = (w[0].0, w[1].0, &w[1].1);
            let c = clip(&self.gaps, a, b);
            let mut calls = 0;
            for e in &self.own {
                let t = t_of(e)?;
                calls += usize::from(a <= t && t < b);
            }
            let mut kinds: Tally<String> = Tally::default();
            let mut mins = 0.0;
            for (t0, t1, k, _) in &self.runs {
                if a <= *t0 && *t0 < b {
                    kinds.add(k, 1.0);
                    mins += t1 - t0;
                }
            }
            let mut sorted = kinds.items().to_vec();
            sorted.sort_by(|x, y| x.0.cmp(&y.0));
            let mut subs = sorted
                .iter()
                .map(|(k, n)| format!("{k} x{n}"))
                .collect::<Vec<_>>()
                .join(", ");
            if !kinds.is_empty() {
                let _ = write!(subs, " ({} min)", fixed(mins / 60.0, 0));
            }
            if subs.is_empty() {
                "-".clone_into(&mut subs);
            }
            rows.push(format!(
                "| {task} | {}-{} | {what} | {calls} | {} | {} | {} | {subs} |",
                hhmm(a),
                hhmm(b),
                fixed(c.get(&"work".to_owned()) / 60.0, 0),
                fixed(c.get(&"wait".to_owned()) / 60.0, 0),
                fixed(c.get(&"idle".to_owned()) / 60.0, 0),
            ));
        }
        Ok(rows)
    }

    /// `task`'s decision-log skeleton (D33), in time order, each with an empty cell for what decided it (`skeleton_rows`).
    ///
    /// # Errors
    ///
    /// An event time, a plan stamp or a duration the Python could not read.
    pub fn skeleton(
        &self,
        task: &str,
        start: f64,
        end: f64,
        plan_text: &str,
        ticked: bool,
    ) -> Result<Vec<String>, Raised> {
        let mut items: Vec<(f64, String)> = vec![(start, "started (`make task-start`)".to_owned())];
        for (t0, t1, kind, verdict) in &self.runs {
            if start <= *t1 && *t1 <= end {
                let v = if verdict.is_empty() {
                    String::new()
                } else {
                    format!(" {verdict}")
                };
                items.push((
                    *t1,
                    format!("{kind} returned{v} ({} min)", fixed((t1 - t0) / 60.0, 0)),
                ));
            }
        }
        for e in self.events {
            if (on(e, "tool") && on(e, "by")) || !is(e, "ev", "PostToolUse") || !measured_run(e) {
                continue;
            }
            let t = t_of(e)?;
            if start <= t && t <= end {
                let ms = if on(e, "ms") {
                    py_float_of(get(e, "ms"))?
                } else {
                    0.0
                };
                items.push((
                    t,
                    format!("`make {}` ({} min)", s(e, "make"), fixed(ms / 60000.0, 0)),
                ));
            }
        }
        for c in STAMP.captures_iter(plan_text).filter_map(Result::ok) {
            let when = ts(&format!("{}:00Z", &c[3]))?;
            if &c[1] == task && start <= when && when <= end {
                let what = if &c[2] == "part B" {
                    "part B written"
                } else {
                    "Approach re-answered"
                };
                items.push((when, what.to_owned()));
            }
        }
        if ticked {
            items.push((end, "ticked".to_owned()));
        }
        items.sort_by(|a, b| cmp_f(a.0, b.0).then(a.1.cmp(&b.1)));
        Ok(items
            .into_iter()
            .map(|(t, what)| format!("| {task} | {} | {what} | |", hhmm(t)))
            .collect())
    }
}

#[cfg(test)]
mod tests;
