//! The report's tables over the events (`feature_report.py`'s `split_time`, `tool_detail`, `tripwires`, `verdicts`, `dispatches`,
//! `task_rows` and `check_rows`, feature 449 T119): where the time went, what was dispatched and how often, what fired, each task's
//! decision points and what each check cost per changed line.

use std::collections::HashSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::event_log_hooks::read::reversals;
use l7r_guard::guards::event_log_hooks::round_capped;
use serde_json::{Map, Value};

use super::super::events::{
    cmp_f, fixed, get, hm, is, need, on, or_s, or_text, re, s, t_of, t_text, ts, Event, Raised,
    Tally, IDLE_CAP_S,
};
use super::super::task_phases::{by_sid, foreground_spans, in_span};

/// The check categories the cascade ratio counts (plan D8).
pub const CHECK_CATS: [&str; 3] = ["record check", "claims check", "review check"];
/// The returns that are a task's decision points: a ruling on its plan, or the round arbiter's on its process.
pub const DECISION_AGENTS: [&str; 3] = ["spec-fidelity", "spec-fidelity-verify", "round-arbiter"];

static SUBJECT: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"/(?:l7r-check|[^/]+)/([^/]+?)(?:-(?:quote-check|record-format|source-reader|source-applicability|intro-check|translation-check|record-style|entry-drift|modal-[a-z]+))?/MANIFEST\.md$",
    )
});
static TOKENS: LazyLock<Regex> =
    LazyLock::new(|| re(r"([\d.]+)([kM]?) in .*?/ ([\d.]+)([kM]?) out"));
static WALL: LazyLock<Regex> = LazyLock::new(|| re(r"^([\d.]+)\s*s"));

/// A tool call's category, an Agent call's as `dispatching: <category>` (`_tool_cat`).
#[must_use]
pub fn tool_cat(e: &Event) -> String {
    let cat = or_text(get(e, "cat"), "other tool");
    if is(e, "tool", "Agent") {
        format!("dispatching: {cat}")
    } else {
        cat
    }
}

fn waiting(nxt: &Event) -> String {
    if is(nxt, "ev", "SubagentStop") {
        format!("waiting: {}", or_text(get(nxt, "agent"), "subagent"))
    } else if is(nxt, "ev", "UserPromptSubmit")
        && nxt.get("gm").is_none_or(super::super::events::truthy)
    {
        // ...a notification is no wait on the GM (feature 385)
        "waiting: the GM".to_owned()
    } else {
        "waiting: a background run".to_owned()
    }
}

fn spec_edit(e: &Event, name: &str) -> bool {
    is(e, "cat", "edit") && or_s(e, "path").contains(&format!("specs/{name}/"))
}

/// Seconds per category over every session (`split_time`): a tool's call its category, a Stop to what wakes it WAITING, the rest
/// THINKING, or WRITING THE SPEC when the call it leads to edits the feature's spec; past the hour cap the session left idle.
///
/// # Errors
///
/// An event time the Python could not read.
pub fn split_time(events: &[Event], name: &str) -> Result<Tally<String>, Raised> {
    let mut out = Tally::default();
    let fg = foreground_spans(events)?;
    for evs in by_sid(events) {
        for pair in evs.windows(2) {
            let (a, b) = (pair[0], pair[1]);
            let ta = t_of(a)?;
            let gap = t_of(b)? - ta;
            if gap <= 0.0 {
                continue;
            }
            if gap > IDLE_CAP_S {
                out.add(&"idle (over an hour)".to_owned(), gap);
                continue;
            }
            let run = in_span(ta, &fg);
            let cat = if !run.is_empty() {
                format!("waiting: {run}")
            } else if is(a, "ev", "PreToolUse")
                && is(b, "ev", "PostToolUse")
                && get(b, "id") == get(a, "id")
            {
                tool_cat(a)
            } else if is(a, "ev", "Stop") {
                waiting(b)
            } else if is(a, "ev", "PreToolUse") {
                // a tool still running when another event arrives (a hook's own record)
                tool_cat(a)
            } else if (is(b, "ev", "PreToolUse") || is(b, "ev", "Stop")) && spec_edit(b, name) {
                "writing the spec".to_owned()
            } else {
                "thinking".to_owned()
            };
            out.add(&cat, gap);
        }
    }
    Ok(out)
}

/// Seconds of each `other tool` call by its make target or tool name - what the coarse category hides (`tool_detail`).
///
/// # Errors
///
/// An event time the Python could not read.
pub fn tool_detail(events: &[Event]) -> Result<Tally<String>, Raised> {
    let mut out = Tally::default();
    let mut start: std::collections::HashMap<String, &Event> = std::collections::HashMap::new();
    for e in events {
        if is(e, "ev", "PreToolUse") && is(e, "cat", "other tool") {
            start.insert(s(e, "id"), e);
        } else if is(e, "ev", "PostToolUse") {
            if let Some(a) = start.remove(&s(e, "id")) {
                let gap = t_of(e)? - t_of(a)?;
                if 0.0 < gap && gap <= IDLE_CAP_S {
                    let key = if on(a, "make") {
                        format!("make {}", s(a, "make"))
                    } else {
                        s(a, "tool")
                    };
                    out.add(&key, gap);
                }
            }
        }
    }
    Ok(out)
}

/// The checked thing a MANIFEST path names - `0105` for `/tmp/l7r-check/0105-quote-check/MANIFEST.md` (`subject`).
#[must_use]
pub fn subject(manifest: &str) -> String {
    if let Ok(Some(c)) = SUBJECT.captures(manifest) {
        return c[1].to_owned();
    }
    let p = super::super::events::py_path_parts(manifest);
    if p.len() >= 2 {
        p[p.len() - 2].clone()
    } else {
        String::new()
    }
}

/// (time, what fired) for every tripwire the events would have tripped (FR-010, replayed): a check's third and later round on one
/// subject, an Edit putting back replaced text, a round run on the GM's waiver, and a second red gate in a row (`tripwires`).
#[must_use]
pub fn tripwires(events: &[Event], gate_results: &[(String, String)]) -> Vec<(String, String)> {
    let mut out: Vec<(String, String)> = Vec::new();
    let mut count: Tally<(String, String)> = Tally::default();
    // a ROUND is a check that ran: a dispatch the hooks refused has no PostToolUse, and an ad-hoc agent has no round cap
    let ran: HashSet<String> = events
        .iter()
        .filter(|e| is(e, "ev", "PostToolUse") && is(e, "tool", "Agent"))
        .map(|e| s(e, "id"))
        .collect();
    for e in events {
        let capped = get(e, "agent").as_str().is_some_and(round_capped);
        let cat = get(e, "cat").as_str().unwrap_or_default();
        if !(is(e, "ev", "PreToolUse")
            && is(e, "tool", "Agent")
            && CHECK_CATS.contains(&cat)
            && capped)
        {
            continue;
        }
        if on(e, "id") && !ran.contains(&s(e, "id")) {
            continue;
        }
        let unit = if on(e, "manifest") {
            subject(&s(e, "manifest"))
        } else {
            or_s(e, "unit").trim_end_matches([',', ';', '.']).to_owned()
        };
        if unit.is_empty() {
            continue;
        }
        let k = (s(e, "agent"), unit.clone());
        count.add(&k, 1.0);
        let n = count.get(&k);
        if n > 2.0 {
            let waiver = if on(e, "waiver") {
                " (ran on the GM's waiver)"
            } else {
                ""
            };
            out.push((
                t_text(e).to_owned(),
                format!("round:{}|{unit}@{n}{waiver}", s(e, "agent")),
            ));
        }
    }
    let refs: Vec<&Map<String, Value>> = events.iter().collect();
    out.extend(
        reversals(&refs)
            .into_iter()
            .map(|(p, t)| (t, format!("reversal:{p}"))),
    );
    let mut prev = "";
    for (t, result) in gate_results {
        if result == "red" && prev == "red" {
            out.push((t.clone(), "red-gate".to_owned()));
        }
        prev = result;
    }
    out.sort();
    out
}

/// Each agent type's returns by verdict (`verdicts`).
#[must_use]
pub fn verdicts(events: &[Event]) -> Vec<(String, Tally<String>)> {
    let mut out: Vec<(String, Tally<String>)> = Vec::new();
    for e in events
        .iter()
        .filter(|e| is(e, "ev", "SubagentStop") && on(e, "verdict"))
    {
        let agent = s(e, "agent");
        let i = out
            .iter()
            .position(|(k, _)| *k == agent)
            .unwrap_or_else(|| {
                out.push((agent, Tally::default()));
                out.len() - 1
            });
        out[i].1.add(&s(e, "verdict"), 1.0);
    }
    out
}

/// Dispatches per agent type, rounds per (check, subject).
pub type Dispatches = (Tally<String>, Tally<(String, String)>);

/// (dispatches per agent type, rounds per (check, subject)) - a dispatch is an Agent call's `PreToolUse` (`dispatches`).
///
/// # Errors
///
/// An event with no `ev`: the Python's `KeyError`, which every report met here.
pub fn dispatches(events: &[Event]) -> Result<Dispatches, Raised> {
    let mut by_type = Tally::default();
    let mut rounds = Tally::default();
    for e in events {
        if need(e, "ev")? == "PreToolUse" && is(e, "tool", "Agent") {
            by_type.add(&s(e, "agent"), 1.0);
            if on(e, "manifest") {
                rounds.add(&(s(e, "agent"), subject(&s(e, "manifest"))), 1.0);
            }
        }
    }
    Ok((by_type, rounds))
}

/// One row per started task: start to tick (or to the last event, while open), its decision points, the time to the last and after it,
/// and each segment between two (`task_rows`).
///
/// # Errors
///
/// An event time the Python could not read.
pub fn task_rows(
    events: &[Event],
    starts: &[(String, f64)],
    ticks: &[(String, f64)],
) -> Result<Vec<String>, Raised> {
    let last_t = match events.last() {
        Some(e) => ts(&super::super::events::py_str(need(e, "t")?))?,
        None => 0.0,
    };
    let mut rows = Vec::new();
    for (task, start) in sorted_starts(starts) {
        let tick = ticks.iter().find(|(k, _)| k == task).map(|(_, t)| *t);
        let end = tick.filter(|t| *t != 0.0).unwrap_or(last_t);
        let mut points = Vec::new();
        for e in events {
            if is(e, "ev", "SubagentStop")
                && get(e, "agent")
                    .as_str()
                    .is_some_and(|a| DECISION_AGENTS.contains(&a))
            {
                let t = ts(&super::super::events::py_str(need(e, "t")?))?;
                if start <= t && t <= end {
                    points.push(t);
                }
            }
        }
        points.sort_by(|a, b| cmp_f(*a, *b));
        let mut cuts = vec![start];
        cuts.extend(&points);
        cuts.push(end);
        let segs = cuts
            .windows(2)
            .map(|w| fixed((w[1] - w[0]) / 60.0, 0))
            .collect::<Vec<_>>()
            .join(", ");
        let to_last = points.last().copied().unwrap_or(start) - start;
        let open = if tick.is_some() { "" } else { " (open)" };
        rows.push(format!(
            "| {task} | {}{open} | {} | {} | {} | {segs} |",
            hm(end - start),
            hm(to_last),
            hm(end - start - to_last),
            points.len()
        ));
    }
    Ok(rows)
}

/// `sorted(starts.items(), key=lambda kv: kv[1])`: by time, ties in the order first seen.
#[must_use]
pub fn sorted_starts(starts: &[(String, f64)]) -> Vec<(&str, f64)> {
    let mut out: Vec<(&str, f64)> = starts.iter().map(|(k, t)| (k.as_str(), *t)).collect();
    out.sort_by(|a, b| cmp_f(a.1, b.1));
    out
}

/// `float(text)` of a figure `[\d.]+` matched, none where it is no number (the Python's `ValueError`, which the report caught).
fn figure(text: &str) -> Option<f64> {
    super::super::events::py_float_text(text)
}

/// (tokens in, tokens out) of a ledger cell, none where a figure is no number (`_tokens`).
fn tokens(cell: &str) -> Option<(f64, f64)> {
    let Ok(Some(m)) = TOKENS.captures(cell) else {
        return Some((0.0, 0.0));
    };
    let scale = |unit: &str| match unit {
        "k" => 1e3,
        "M" => 1e6,
        _ => 1.0,
    };
    Some((figure(&m[1])? * scale(&m[2]), figure(&m[3])? * scale(&m[4])))
}

/// One row per check kind: the feature's own passes (matched to its event log by agent id), their wall time and tokens, and each per
/// changed line (FR-011, `check_rows`); none where a figure is no number, the `ValueError` the report caught.
#[must_use]
pub fn check_rows(
    events: &[Event],
    passes: &[Map<String, Value>],
    lines: u64,
) -> Option<Vec<String>> {
    let aids: HashSet<String> = events
        .iter()
        .filter(|e| on(e, "aid"))
        .map(|e| s(e, "aid"))
        .collect();
    let mut agg: Vec<(String, [f64; 4])> = Vec::new();
    for p in passes {
        let text = |k: &str| {
            p.get(k)
                .map_or_else(String::new, super::super::events::py_str)
        };
        if !aids.contains(&text("agent")) {
            continue;
        }
        let check = or_text(p.get("check").unwrap_or(&Value::Null), "?");
        let i = agg
            .iter()
            .position(|(k, _)| *k == check)
            .unwrap_or_else(|| {
                agg.push((check, [0.0; 4]));
                agg.len() - 1
            });
        let wall = match WALL.captures(&text("wall")) {
            Ok(Some(m)) => figure(&m[1])?,
            _ => 0.0,
        };
        let (tin, tout) = tokens(&text("tokens"))?;
        let a = &mut agg[i].1;
        a[0] += 1.0;
        a[1] += wall;
        a[2] += tin;
        a[3] += tout;
    }
    #[expect(clippy::cast_precision_loss, reason = "a count of changed lines")]
    let per = lines.max(1) as f64;
    agg.sort_by(|a, b| cmp_f(b.1[2], a.1[2]));
    Some(
        agg.iter()
            .map(|(k, v)| {
                format!(
                    "| {k} | {} | {} | {}k | {}k | {} | {}k |",
                    v[0],
                    hm(v[1]),
                    fixed(v[2] / 1e3, 0),
                    fixed(v[3] / 1e3, 1),
                    fixed(v[0] / per, 3),
                    fixed(v[2] / per / 1e3, 1)
                )
            })
            .collect(),
    )
}

/// `Path(text).name`.
#[must_use]
pub fn path_name(text: &str) -> String {
    super::super::events::py_path_parts(text)
        .last()
        .cloned()
        .unwrap_or_default()
}

/// The feature's directory, for the tests that read a report's paths.
#[must_use]
pub fn under(root: &Path, d: &Path) -> String {
    d.strip_prefix(root).unwrap_or(d).display().to_string()
}

#[cfg(test)]
mod tests;
