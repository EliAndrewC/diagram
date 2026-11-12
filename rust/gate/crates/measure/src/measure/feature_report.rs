//! `make feature-report F=NNN` - where a feature's time and dispatches went, as a table (feature 375, FR-009; ported from
//! `scripts/measure/feature_report.py` by feature 449 T119, `ask:449-T83-scope`, no door).
//!
//! WHY (the GM, 2026-10-10): *"if at the end of every feature we literally had a table of how was spent running tests and how much time
//! was spent thinking and how much time was spent implementing and how much time was spent waiting for subagent reviews and how much time
//! was spent actually making the spec kit feature"* - and the post-mortem should take *"a second with a make command"*, not a hand reading
//! of a transcript. Every feature gets one, however small (FR-009), and no route closes a feature without it.
//!
//! THE SOURCES (plan D8). The event log every clone's hooks write (`<git dir>/l7r-events/<feature>.jsonl`, read from every clone under
//! `/diagram/.clones/` and this one, through the guard's one reader); a session transcript converted to the same events where the hooks did
//! not run (`--transcript`); `dev/run-log/` for the gates; the feature's own commits for its diff, its plan reviews and its spec rounds; the
//! review passes, costed as `make ledger-owed` costs them (`reviews::ledger_passes::passes`, in process since T119, where the Python ran
//! `l7r-gate reviews ledger-passes`).
//!
//! THE TIME (plan D8, D9). Per session, its events in order: a `PreToolUse` to its `PostToolUse` is that tool's category; from a `PostToolUse`
//! to the next `PreToolUse` or Stop is THINKING, or WRITING THE SPEC when the call it leads to edits the feature's spec; from a Stop to what
//! wakes the session is WAITING. A gap past an hour is the session left idle, counted apart.
//!
//! ```text
//! l7r-gate measure feature-report <NNN> [--transcript FILE ...] [--since ISO] [--until ISO] [--write] [--root DIR]
//! ```

pub mod sources;
pub mod tables;

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::time::Instant;

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_gate_core::record::bundle::resolve;
use l7r_gate_reviews::reviews::ledger_passes::{passes, Env};
use l7r_guard::guards::event_log_hooks::agent_category;
use l7r_guard::guards::event_log_hooks::read::reversals;

use super::events::{
    event_logs, fixed, head, hm, load_events, or_s, spec_dir, t_text, Event, Raised, Tally,
};
use super::reply;
use super::task_phases::{
    attribute, attribution, call_counts, session_events, subagent_calls, subagent_runs, Phases,
};
use crate::Reply;
use sources::{
    commits, diff_lines, gate_sequence, gates, plan_blocks, spec_rounds, task_starts, task_ticks,
    tasks_done,
};
use tables::{
    check_rows, dispatches, path_name, sorted_starts, split_time, task_rows, tool_detail,
    tripwires, under, verdicts, CHECK_CATS, DECISION_AGENTS,
};

/// A report's inputs.
pub struct Ask<'a> {
    /// The tree read (`--root`, resolved).
    pub root: &'a Path,
    /// The feature as given.
    pub feature: &'a str,
    /// Transcripts to convert.
    pub transcripts: &'a [PathBuf],
    /// The ISO bounds on the events read.
    pub since: &'a str,
    /// The ISO bounds on the events read.
    pub until: &'a str,
    /// Every clone's checkout (`/diagram/.clones`).
    pub clones: &'a Path,
    /// What the review passes are costed from: the working directory, `$HOME` and the cache switch.
    pub env: &'a Env,
}

/// A `SystemExit` the report raised, or a raise it did not catch.
pub enum Stop {
    /// `raise SystemExit(msg)`: the message, exit 1.
    Exit(String),
    /// An uncaught raise: a traceback, exit 1.
    Raised(Raised),
}

impl From<Raised> for Stop {
    fn from(why: Raised) -> Self {
        Self::Raised(why)
    }
}

fn joined(t: &Tally<String>) -> String {
    let mut items = t.items().to_vec();
    items.sort_by(|a, b| a.0.cmp(&b.0));
    items
        .iter()
        .map(|(k, v)| format!("{k} {v}"))
        .collect::<Vec<_>>()
        .join(", ")
}

/// The report's text and the spec directory it was built from (`report`).
///
/// # Errors
///
/// No spec directory (`Stop::Exit`), or what the Python raised reading its sources (`Stop::Raised`).
#[expect(
    clippy::too_many_lines,
    reason = "the Python's one `report`, its sections in its order, kept together to read beside it"
)]
pub fn report(ask: &Ask) -> Result<(String, PathBuf), Stop> {
    let t0 = Instant::now();
    let root = ask.root;
    let Some(d) = spec_dir(root, ask.feature)? else {
        return Err(Stop::Exit(format!(
            "feature-report: no specs/{}-* directory",
            ask.feature
        )));
    };
    let name = d
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    let events = load_events(
        &event_logs(root, &name, ask.clones),
        ask.transcripts,
        ask.since,
        ask.until,
    )?;
    // WHOSE CALL (feature 385 amendment 4, plan D30): a subagent's tool calls reach the session's hooks under its id, so each is marked
    // from the subagent transcripts before any table reads the session's time
    let projects = Path::new(&ask.env.home).join(".claude").join("projects");
    let (calls, found) = subagent_calls(
        &events.iter().map(|e| or_s(e, "sid")).collect::<Vec<_>>(),
        &projects,
    );
    let events = attribute(events, &calls, &found)?;
    let how = attribution(&events);
    let (own_calls, sub_calls) = call_counts(&events);
    let span = match (events.first(), events.last()) {
        (Some(a), Some(b)) => (t_text(a).to_owned(), t_text(b).to_owned()),
        _ => (String::new(), String::new()),
    };
    let cs = commits(root, ask.feature, ask.since, ask.until)?;
    let shas: std::collections::HashSet<&str> = cs.iter().map(|c| c.0.as_str()).collect();
    let mine = session_events(&events);
    let split = split_time(&mine, &name)?;
    let (by_type, rounds) = dispatches(&events)?;
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a count of dispatches"
    )]
    let checks = by_type
        .items()
        .iter()
        .filter(|(k, _)| CHECK_CATS.contains(&agent_category(k, "")))
        .map(|(_, n)| *n)
        .sum::<f64>() as u64;
    let mut sha_list: Vec<&str> = shas.iter().copied().collect();
    sha_list.sort_unstable();
    let lines = diff_lines(root, &sha_list)?;
    let since = if ask.since.is_empty() {
        span.0.as_str()
    } else {
        ask.since
    };
    let until = if ask.until.is_empty() {
        span.1.as_str()
    } else {
        ask.until
    };
    let g = gates(root, &shas, since, until)?;
    let (done, total) = tasks_done(&d)?;
    let spec_text = super::events::text_if_file(&d.join("spec.md"))?;
    let mut out = vec![format!("# Feature report - {name}"), String::new()];
    let window = if events.is_empty() {
        " (no event log and no transcript: the time table is empty)".to_owned()
    } else {
        format!(" ({} to {} UTC)", head(&span.0, 16), head(&span.1, 16))
    };
    out.push(format!(
        "Written by `make feature-report F={}` from {} events{window}, {} commits, the run log and the spec.",
        ask.feature,
        events.len(),
        cs.len()
    ));
    out.extend(
        [
            "",
            "## Where the time went",
            "",
            "| category | time | share |",
            "|---|---|---|",
        ]
        .map(String::from),
    );
    let whole: f64 = split
        .items()
        .iter()
        .filter(|(k, _)| !k.starts_with("idle"))
        .map(|(_, v)| *v)
        .sum();
    let whole = if whole == 0.0 { 1.0 } else { whole };
    for (k, v) in split.most_common() {
        let share = if k.starts_with("idle") {
            "-".to_owned()
        } else {
            format!("{}%", fixed(100.0 * v / whole, 0))
        };
        out.push(format!("| {k} | {} | {share} |", hm(v)));
    }
    let runs = subagent_runs(&events)?;
    let n = |k: &str| how.get(&k.to_owned());
    out.push(String::new());
    out.push(format!(
        "The session's own time above; its {sub_calls} subagent tool call(s) (of {}) are counted apart ({} by the subagent transcripts, {} by the hook's `by`, {} by the agents' windows - an estimate; plan D30). The subagents' own work: {} run(s), {} in all, much of it while the session waited or worked on.",
        own_calls + sub_calls,
        n("transcript"),
        n("hook"),
        n("window"),
        runs.len(),
        hm(runs.iter().map(|(a, b, _, _)| b - a).sum())
    ));
    let detail = tool_detail(&mine)?;
    if !detail.is_empty() {
        out.extend(
            [
                "",
                "## Inside `other tool` (the five largest)",
                "",
                "| tool or make target | time |",
                "|---|---|",
            ]
            .map(String::from),
        );
        out.extend(
            detail
                .most_common()
                .iter()
                .take(5)
                .map(|(k, v)| format!("| {k} | {} |", hm(*v))),
        );
    }
    let vs = verdicts(&events);
    let verdicts_of = |k: &str| vs.iter().find(|(a, _)| a == k).map(|(_, t)| t);
    out.extend(
        [
            "",
            "## Dispatches",
            "",
            "| agent | dispatches | returned, by verdict |",
            "|---|---|---|",
        ]
        .map(String::from),
    );
    let mut types = by_type.items().to_vec();
    types.sort_by(|a, b| super::events::cmp_f(b.1, a.1).then(a.0.cmp(&b.0)));
    for (k, v) in types {
        let returned = verdicts_of(&k)
            .map(joined)
            .filter(|t| !t.is_empty())
            .unwrap_or_else(|| "-".to_owned());
        out.push(format!("| {k} | {v} | {returned} |"));
    }
    out.extend(
        [
            "",
            "## Rounds per checked thing (two or more)",
            "",
            "| check | subject | rounds |",
            "|---|---|---|",
        ]
        .map(String::from),
    );
    let mut rs = rounds.items().to_vec();
    rs.sort_by(|a, b| super::events::cmp_f(b.1, a.1).then(a.0.cmp(&b.0)));
    let rs: Vec<String> = rs
        .iter()
        .filter(|(_, n)| *n >= 2.0)
        .map(|((c, s), n)| format!("| {c} | {s} | {n} |"))
        .collect();
    out.extend(if rs.is_empty() {
        vec!["| - | - | - |".to_owned()]
    } else {
        rs
    });
    let refs: Vec<&Event> = events.iter().collect();
    let rv = reversals(&refs);
    let wires = tripwires(&events, &gate_sequence(root, &shas, since, until)?);
    let none = |t: String| {
        if t.is_empty() {
            "none recorded".to_owned()
        } else {
            t
        }
    };
    let blocked = verdicts_of("spec-fidelity").map_or(0.0, |t| t.get(&"BLOCKED".to_owned()));
    let mut reversed = format!("- reversals (A -> B -> A): {}", rv.len());
    if !rv.is_empty() {
        let listed: Vec<String> = rv
            .iter()
            .take(8)
            .map(|(p, t)| format!("{} {}", path_name(p), slice(t, 11, 16)))
            .collect();
        let _ = write!(reversed, " - {}", listed.join("; "));
    }
    #[expect(clippy::cast_precision_loss, reason = "counts of dispatches and lines")]
    let ratio = if lines == 0 {
        0.0
    } else {
        checks as f64 / lines as f64
    };
    out.extend([
        String::new(),
        "## Process signals".to_owned(),
        String::new(),
        format!("- gates: {}", none(joined(&g))),
        format!("- spec rounds: {}", none(joined(&spec_rounds(&spec_text)))),
        format!(
            "- plan reviews BLOCKED: {} recorded in commits, {blocked} returned",
            plan_blocks(root, &name, &shas)?
        ),
        reversed,
        format!(
            "- check dispatches {checks} over {lines} changed lines: cascade ratio {}",
            fixed(ratio, 2)
        ),
        format!("- tasks ticked: {done} of {total}"),
        String::new(),
        "## Tripwires (FR-010) - what fired, or would have".to_owned(),
        String::new(),
    ]);
    if wires.is_empty() {
        out.push("- none".to_owned());
    }
    out.extend(
        wires
            .iter()
            .map(|(t, w)| format!("- {} {w}", slice(t, 11, 16))),
    );
    tasks(&mut out, root, &name, &d, &events)?;
    let costs = check_rows(&events, &passes(ask.env)?, lines).unwrap_or_default();
    if !costs.is_empty() {
        out.extend([
            String::new(),
            format!("## What each check cost, per changed line ({lines} lines)"),
            String::new(),
            "| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |".to_owned(),
            "|---|---|---|---|---|---|---|".to_owned(),
        ]);
        out.extend(costs);
    }
    out.push(String::new());
    out.push(format!(
        "This report took {} s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).",
        fixed(t0.elapsed().as_secs_f64(), 1)
    ));
    out.push(String::new());
    Ok((out.join("\n"), d))
}

/// `text[a:b]` by characters.
fn slice(text: &str, a: usize, b: usize) -> String {
    text.chars().skip(a).take(b.saturating_sub(a)).collect()
}

/// Each task split at its decision points, its phases and its decision-log skeleton (feature 385 T02, plan D10, D32, D33).
fn tasks(
    out: &mut Vec<String>,
    root: &Path,
    name: &str,
    d: &Path,
    events: &[Event],
) -> Result<(), Raised> {
    let starts = task_starts(root, name)?;
    if starts.is_empty() {
        return Ok(());
    }
    out.extend(
        [
            "",
            "## Each task, split at its decision points",
            "",
            "| task | start to tick | to its last decision | after it | decisions | segments (min) |",
            "|---|---|---|---|---|---|",
        ]
        .map(String::from),
    );
    let ticks = task_ticks(root, name)?;
    out.extend(task_rows(events, &starts, &ticks)?);
    let last_t = match events.last() {
        Some(e) => super::events::ts(t_text(e))?,
        None => 0.0,
    };
    let tick = |task: &str| ticks.iter().find(|(k, _)| k == task).map(|(_, t)| *t);
    // a task wholly outside SINCE/UNTIL has no phases there
    let spans: Vec<(&str, f64, f64)> = sorted_starts(&starts)
        .into_iter()
        .map(|(task, start)| {
            (
                task,
                start,
                tick(task).filter(|t| *t != 0.0).unwrap_or(last_t),
            )
        })
        .filter(|s| s.2 > s.1)
        .collect();
    out.extend(
        [
            "",
            "## Each task's phases (plan D32)",
            "",
            "| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |",
            "|---|---|---|---|---|---|---|---|",
        ]
        .map(String::from),
    );
    let phases = if spans.is_empty() {
        None
    } else {
        Some(Phases::new(events)?)
    };
    if let Some(p) = &phases {
        for (task, start, end) in &spans {
            out.extend(p.rows(task, *start, *end, &DECISION_AGENTS)?);
        }
    }
    let plan_text = super::events::text_if_file(&d.join("plan.md"))?;
    out.extend(
        [
            "",
            "## Each task's decision-log skeleton (plan D33) - fill the last column in the retro",
            "",
            "| task | UTC | point | what decided it |",
            "|---|---|---|---|",
        ]
        .map(String::from),
    );
    if let Some(p) = &phases {
        for (task, start, end) in &spans {
            out.extend(p.skeleton(task, *start, *end, &plan_text, tick(task).is_some())?);
        }
    }
    Ok(())
}

/// `feature_report.py`'s command line: the report on stdout, and with `--write` in `specs/NNN-*/report.md` too.
#[must_use]
pub fn cli(args: &[String], env: &Env, clones: &Path) -> Reply {
    let specs = [
        Spec::value("--transcript"),
        Spec::value("--since"),
        Spec::value("--until"),
        Spec::flag("--write"),
        Spec::value("--root"),
    ];
    let p = match parse_with(args, &specs, 1) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => return usage("the following arguments are required: feature"),
        Err(why) => return usage(&why),
    };
    let root = resolve(p.text("--root", "."));
    let transcripts: Vec<PathBuf> = p
        .all("--transcript")
        .into_iter()
        .map(PathBuf::from)
        .collect();
    let feature = p.positional[0].as_str();
    let ask = Ask {
        root: &root,
        feature,
        transcripts: &transcripts,
        since: p.text("--since", ""),
        until: p.text("--until", ""),
        clones,
        env,
    };
    let (text, d) = match report(&ask) {
        Ok(done) => done,
        Err(Stop::Exit(msg)) => return reply(String::new(), format!("{msg}\n"), 1),
        Err(Stop::Raised(why)) => return raised(String::new(), &why),
    };
    if !p.on("--write") {
        return reply(text, String::new(), 0);
    }
    match std::fs::write(d.join("report.md"), &text) {
        Ok(()) => reply(
            format!(
                "{text}\nfeature-report: written to {}/report.md\n",
                under(&root, &d)
            ),
            String::new(),
            0,
        ),
        Err(e) => raised(
            text,
            &format!("OSError: {}: {e}", d.join("report.md").display()),
        ),
    }
}

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!(
            "usage: l7r-gate measure feature-report [--transcript FILE] [--since ISO] [--until ISO] [--write] [--root DIR] feature\nl7r-gate measure feature-report: error: {why}\n"
        ),
        2,
    )
}

/// What the Python's uncaught raise gave: exit 1, what it had printed, and its message after a `Traceback` line.
fn raised(printed: String, why: &str) -> Reply {
    reply(
        printed,
        format!("Traceback (most recent call last):\n  l7r-gate measure feature-report\n{why}\n"),
        1,
    )
}

#[cfg(test)]
pub mod tests;
