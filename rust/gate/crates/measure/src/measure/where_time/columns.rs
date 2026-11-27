//! `make where-time`'s columns (feature 451 T08, plan D2, D4, D7; FR-005): every Bash run of a window booked by its `make` target
//! through the guard's one category table, its compile split from the `Phase` lines it holds, its end read where the session learned it.
//!
//! WHY. The tables booked a tool call by the `cat` the event log froze when it was written, so a past log could never be re-booked, and
//! 846 of a day's 1,323 minutes went to "waiting on work" with every test column near zero: the tests ran in the builders, between the
//! main session's turns (measured 2026-11-21, method: `make where-time F=451 SINCE=2026-11-20T04:33:00Z` before this task). So THE RUNS
//! TABLE books each Bash call of every session and agent - foreground from its `PreToolUse` to its `PostToolUse`, background from its
//! launch to its end - under the task its line names, by [`line_bucket`]. Runs overlap (several builders at once), so its minutes are
//! machine minutes beside the wall clock, never part of it: the critical path (the main session's own, `where_time::tables`) is apart.
//!
//! A BACKGROUND RUN ENDS at the main transcript's `queue-operation` `enqueue` row naming its `<tool-use-id>` - when its notice was queued,
//! seconds after the run ended - never at the `BgEnd` line's `t`, which is when the notice reached the session, minutes late while the
//! session is mid-turn: one enqueued 11:44:08, delivered 11:47:41 (T04's plan review, 2026-11-20). No enqueue row: the `BgEnd`'s `t`; no
//! `BgEnd`: the `TaskStop` call that stopped it ([`stopped`]); none of these: open to the window's end (data-model's edge case: never zero). A subagent's background run ends at its transcript's
//! `queued_command` attachment, T09's.
//!
//! COMPILE (D4) is the union of the `build` and `cover-build` phase spans a run holds; the rest of the run stays its own bucket. D4 says
//! "inside the Bash call or background span that holds them", data-model's row "inside a tests run": a `make land` or `make done`
//! compiles too, and its compile is compile, so every run splits (a deliberate reading of the two, the land and gate columns keeping
//! the rest of their runs). A phase is tied to the run of its session whose span holds it and whose target is the phase's `make` - or,
//! a deviation from D4, whose task is the phase's `task`: a phase's `make` names the outermost make it saw, and of the window's 984
//! compile phases 567 (60.9 min) matched no holding run's target, 170 once the task also ties (measured 2026-11-21, method:
//! `/tmp/t08/loose.py` and `loose2.py` over the 451 log since 2026-11-20T04:33Z, each phase against the Bash spans of its session).
//! Among several, the one of its target, then of its task, then the one started last (D4: a builder waiting on the run lock holds a
//! span another builder's phases fall inside). A phase tied to none is counted, never dropped.
//!
//! A LANDING is booked land however it is launched: a call running several targets (its line's `makes`) is booked by the first of them in
//! [`PRECEDENCE`], and a phase ties to a run that runs its `make` at all - the day's 19 landings were launched `make claims-owed ...; make
//! ledger-owed; make land`, so by their first target they were review, and the runs table showed land 4.2 min and gate 0.0 against 27.4
//! min of their own `gate` phases (T08's final check, 2026-11-21). A landing's `gate` and `cohort` phases (`src: land`; never its `end`,
//! the whole landing) are split out as gate, less the compile inside them, the way compile is.

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::guards::event_log_hooks::bucket_of;
use l7r_shared::make::DEFAULT_GOAL;
use serde_json::Value;

use super::super::events::{
    cmp_f, fixed, get, is, names, or_s, re, t_of, ts, Event, Raised, Tally,
};
use super::task_at;

/// The runs table's buckets, in the guard's table's order, compile after tests, the hook suites and map generation after it (451 T153).
pub const RUN_COLUMNS: [&str; 11] = [
    "tests",
    "compile",
    // a wait on a build slot is split out of its run as compile is (feature 451 T284); until 451 T426 it had no column here, so its
    // seconds were in no column and missing from the table's minutes
    SLOT_WAIT,
    "hook suites",
    "map generation",
    "gate",
    "land",
    "review",
    "docs",
    "spec-kit step",
    "other",
];
/// The runs table's column of the background minutes, already in their buckets.
pub const BACKGROUND: &str = "in the background";

static TOOL_USE: LazyLock<Regex> =
    LazyLock::new(|| re(r"<tool-use-id>(toolu_[A-Za-z0-9_-]+)</tool-use-id>"));

/// A line's frozen `cat` read as a table bucket, for a line with no `make`: a past log's `quick test` and `test file` are tests.
#[must_use]
pub fn cat_bucket(cat: &str) -> &'static str {
    match cat {
        "tests" | "quick test" | "test file" => "tests",
        "gate" => "gate",
        "land" => "land",
        "review" => "review",
        "docs" => "docs",
        "spec-kit step" => "spec-kit step",
        _ => "other",
    }
}

/// A line's make target, a goal-less make (`shared::make::invoked`'s `.DEFAULT_GOAL`, since T15) read as the Makefile's default goal.
#[must_use]
pub fn target<'a>(make: &'a str, goal: &'a str) -> &'a str {
    if make == DEFAULT_GOAL && !goal.is_empty() {
        goal
    } else {
        make
    }
}

/// Which bucket a call running several targets is booked by, first first: a landing launched `make claims-owed ...; make ledger-owed; make
/// land` is a landing, and a `make decide ... && make quick` is its tests.
pub const PRECEDENCE: [&str; 7] = [
    "land",
    "gate",
    "tests",
    "review",
    "docs",
    "spec-kit step",
    "other",
];

/// A line's make targets: its `makes` (every target, since T14) when it runs several, else its `make`; each [`target`]ed.
fn targets_of(e: &Event, goal: &str) -> Vec<String> {
    let all: Vec<String> = match get(e, "makes") {
        Value::Array(list) => list
            .iter()
            .filter_map(Value::as_str)
            .map(str::to_owned)
            .collect(),
        _ => vec![or_s(e, "make")],
    };
    all.iter()
        .filter(|m| !m.is_empty())
        .map(|m| target(m, goal).to_owned())
        .collect()
}

/// The bucket of a tool line (D2): its make targets through the guard's table, the first in [`PRECEDENCE`], so a past log re-books and a
/// landing launched behind a review target is a landing (the T08 final check: the day's 19 landings, so launched, were booked review);
/// else its frozen `cat`.
#[must_use]
pub fn line_bucket(e: &Event, goal: &str) -> &'static str {
    let buckets: Vec<&str> = targets_of(e, goal).iter().map(|m| bucket_of(m)).collect();
    if buckets.is_empty() {
        return cat_bucket(&or_s(e, "cat"));
    }
    PRECEDENCE
        .iter()
        .find(|b| buckets.contains(b))
        .copied()
        .unwrap_or("other")
}

/// The Makefile's default goal as GNU make finds it: a `.DEFAULT_GOAL` it sets, else the first target of its first rule that does not
/// start with a dot. A recipe or continuation line (leading whitespace), a comment, an assignment and a line naming a variable are no rule.
#[must_use]
pub fn default_goal(makefile: &str) -> String {
    let mut first = String::new();
    for line in makefile.lines() {
        if let Some(rest) = line.strip_prefix(".DEFAULT_GOAL") {
            let value = rest.trim_start().trim_start_matches([':', '?', '=']).trim();
            if !value.is_empty() {
                return value.to_owned();
            }
        }
        if !first.is_empty() || line.starts_with(char::is_whitespace) || line.starts_with('#') {
            continue;
        }
        let Some((head, tail)) = line.split_once(':') else {
            continue;
        };
        if head.contains(['=', '$']) || tail.starts_with('=') {
            continue;
        }
        if let Some(t) = head.split_whitespace().find(|t| !t.starts_with('.')) {
            t.clone_into(&mut first);
        }
    }
    first
}

/// tool-use id -> when the main transcript queued its run's notice: each session's `<projects>/*/<sid>.jsonl` `queue-operation` `enqueue`
/// rows naming a `<tool-use-id>`, the first kept. A row that is no JSON, or names no time, is skipped: a transcript the session is still
/// writing can end on half a row.
#[must_use]
pub fn enqueued(sids: &[String], projects: &Path) -> HashMap<String, f64> {
    let mut out = HashMap::new();
    for sid in sids {
        for project in names(projects) {
            let path = projects.join(project).join(format!("{sid}.jsonl"));
            let Ok(text) = std::fs::read_to_string(&path) else {
                continue;
            };
            for line in text.lines().filter(|l| l.contains("\"enqueue\"")) {
                let Ok(Value::Object(row)) = serde_json::from_str::<Value>(line) else {
                    continue;
                };
                let (Some(content), Some(at)) = (
                    get(&row, "content").as_str(),
                    get(&row, "timestamp").as_str().and_then(|t| ts(t).ok()),
                ) else {
                    continue;
                };
                if !is(&row, "type", "queue-operation") {
                    continue;
                }
                if let Ok(Some(c)) = TOOL_USE.captures(content) {
                    out.entry(c[1].to_owned()).or_insert(at);
                }
            }
        }
    }
    out
}

/// `TaskStop` call id -> the background task it stopped, from each session's transcript and its subagents'
/// (`<projects>/*/<sid>.jsonl`, `<projects>/*/<sid>/subagents/*.jsonl`): a stopped run sends no notice, so without it a run a builder
/// stopped was booked open to the window's end - ten such on 2026-11-20 booked 6,070 machine minutes "other" (measured 2026-11-21,
/// method: this reader over `make where-time F=451 SINCE=2026-11-20T04:33:00Z`, each open run's bg id found in a `TaskStop` input).
/// `KillShell` is the tool's earlier name.
#[must_use]
pub fn stopped(sids: &[String], projects: &Path) -> HashMap<String, String> {
    read_subagents(sids, projects, (f64::MIN, f64::MAX)).stopped
}

/// What [`read_subagents`] reads of the transcripts.
#[derive(Debug, Default)]
pub struct Subagents {
    /// [`stopped`]'s map.
    pub stopped: HashMap<String, String>,
    /// tool-use id -> when a subagent's background run's notice was queued.
    pub queued: HashMap<String, f64>,
    /// agent id -> its tokens inside the window (T10, `spent::tokens`).
    pub tokens: HashMap<String, spent::Tok>,
    /// agent id -> its model calls inside the window, each message id once (451 T512).
    pub calls: HashMap<String, usize>,
    /// session id -> its own model calls inside the window, each its time, tokens and tool calls, in time order (451 T512, T513).
    pub session: HashMap<String, Vec<spent::Call>>,
    /// agent id -> its model calls and their tokens by model (451 T532).
    pub models: HashMap<String, spent::Models>,
    /// tool-use id -> a Bash call's command, the session's and its subagents': the program a call running no make target is listed by
    /// (451 T243, the task time breakdown - the event log keeps no command).
    pub commands: HashMap<String, String>,
}

/// [`stopped`]'s map, and tool-use id -> when a SUBAGENT's background run's notice was queued (feature 451 T09, plan D3): the
/// `queued_command` attachment of its transcript (`<projects>/*/<sid>/subagents/*.jsonl`) naming its `<tool-use-id>`, the first kept.
/// A subagent has no prompt line and its session's transcript no enqueue row for it, so without this a builder's background run was
/// open to the window's end. The attachment's time is the run's end: it fell within 30 ms of the run's output file's last write on
/// each of eight runs, measured 2026-11-21 (the session's subagent transcripts against `/tmp/claude-1000/.../tasks/*.output` mtimes).
/// One pass reads both, since the subagent transcripts are the most of what the command reads (1,311 for the main session), and with
/// them each agent's tokens inside `window` ([`spent::tokens`], T10).
#[must_use]
pub fn read_subagents(sids: &[String], projects: &Path, window: (f64, f64)) -> Subagents {
    let (mut out, mut queued, mut commands) = (HashMap::new(), HashMap::new(), HashMap::new());
    let mut tokens = spent::Tokens::default();
    for sid in sids {
        for project in names(projects) {
            let dir = projects.join(&project);
            let subs = dir.join(sid).join("subagents");
            let mut files = vec![dir.join(format!("{sid}.jsonl"))];
            files.extend(names(&subs).into_iter().map(|n| subs.join(n)));
            for path in files {
                let Ok(text) = std::fs::read_to_string(&path) else {
                    continue;
                };
                tokens.read(&path, &text, window);
                for line in text.lines().filter(|l| {
                    l.contains("\"TaskStop\"")
                        || l.contains("\"KillShell\"")
                        || l.contains("\"queued_command\"")
                        || l.contains("\"Bash\"")
                }) {
                    let Ok(row) = serde_json::from_str::<Value>(line) else {
                        continue;
                    };
                    let note = |k: &str| {
                        row.pointer(&format!("/attachment/{k}"))
                            .and_then(Value::as_str)
                    };
                    if let (Some("queued_command"), Some(prompt), Some(Ok(at))) =
                        (note("type"), note("prompt"), note("timestamp").map(ts))
                    {
                        if let Ok(Some(c)) = TOOL_USE.captures(prompt) {
                            queued.entry(c[1].to_owned()).or_insert(at);
                        }
                    }
                    let blocks = row.pointer("/message/content").and_then(Value::as_array);
                    for b in blocks.into_iter().flatten() {
                        if let (Some("Bash"), Some(id), Some(cmd)) = (
                            b.get("name").and_then(Value::as_str),
                            b.get("id").and_then(Value::as_str),
                            b.pointer("/input/command").and_then(Value::as_str),
                        ) {
                            commands.insert(id.to_owned(), cmd.to_owned());
                            continue;
                        }
                        let input =
                            |k: &str| b.pointer(&format!("/input/{k}")).and_then(Value::as_str);
                        if let (Some(id), Some(task)) = (
                            b.get("id").and_then(Value::as_str),
                            input("task_id").or_else(|| input("shell_id")),
                        ) {
                            out.insert(id.to_owned(), task.to_owned());
                        }
                    }
                }
            }
        }
    }
    Subagents {
        stopped: out,
        queued,
        calls: tokens.calls(),
        session: tokens.session(),
        models: tokens.models(),
        tokens: tokens.sums(),
        commands,
    }
}

/// One Bash run.
#[derive(Debug, Clone, PartialEq)]
pub struct Run {
    /// Its tool-use id.
    pub id: String,
    /// Its start: the `PreToolUse` line's time.
    pub t0: f64,
    /// Its end: its `PostToolUse`, or a background run's enqueue row, `BgEnd`, or the window's end.
    pub t1: f64,
    /// Its session.
    pub sid: String,
    /// The subagent whose call it is, empty for the session's own.
    pub by: String,
    /// Its background task id, empty for a foreground run.
    pub bg_id: String,
    /// Its make targets, every one it runs ([`targets_of`]), the default goal for a goal-less make.
    pub makes: Vec<String>,
    /// Its bucket ([`line_bucket`]).
    pub bucket: &'static str,
    /// The task its line names, else the mark at its start.
    pub task: String,
    /// Whether it ran in the background.
    pub bg: bool,
    /// Whether no end was found: booked open to the window's end.
    pub open: bool,
    /// The phases it holds, by category ([`Split`]).
    pub split: Split,
}

impl Run {
    /// Its seconds compiling.
    #[must_use]
    pub fn compile_s(&self) -> f64 {
        overlap(self.split.spans("compile"), self.t0, self.t1)
    }

    /// Its seconds in a landing's gate, its compile apart.
    #[must_use]
    pub fn gate_s(&self) -> f64 {
        overlap(self.split.spans("gate"), self.t0, self.t1)
    }
}

/// The time a compiling cargo call waited for one of the machine's build slots (feature 451 T284): a category of its own, so `make
/// task-time` shows what the slot costs beside the compile it spreads out.
pub const SLOT_WAIT: &str = "waiting on a build slot";

/// THE UNMARKED SCRATCH HOLDS the record names (feature 451 T426): before the writer marked a wait on a scratch slot directory, its
/// lines read like a real one. 451 T420's record (`dev/measurements/2026-11-27/slot-waits/results.md`) names the one known run - T355's
/// `lint-wait.sh`, in the pool tree `diagram-backlog-t270`, 01:48:50 to 02:01:30Z on 2026-11-27 - whose four waits (221.9 s) are the
/// only `slot-wait` lines of that tree and span. (the tree's name, the first and last start, UTC)
const KNOWN_SCRATCH: [(&str, &str, &str); 1] = [(
    "diagram-backlog-t270",
    "2026-11-27T01:48:50Z",
    "2026-11-27T02:01:30Z",
)];

/// A `slot-wait` line that a measurement's own scripted hold wrote (feature 451 T426): marked `"scratch": true` by the writer
/// (`rustc/slot.rs`), or one of [`KNOWN_SCRATCH`]. Such a wait is booked to no category: neither waiting nor the compile whose span
/// holds it, so its seconds are its run's own; the runs table's note and the task time breakdown's footnote count it.
#[must_use]
pub fn scratch_wait(p: &Event) -> bool {
    if !(is(p, "src", "rust") && is(p, "step", "slot-wait")) {
        return false;
    }
    if matches!(get(p, "scratch"), Value::Bool(true)) {
        return true;
    }
    let (tree, t0) = (or_s(p, "clone"), or_s(p, "t0"));
    let name = Path::new(&tree).file_name().unwrap_or_default();
    KNOWN_SCRATCH.iter().any(|(n, lo, hi)| {
        name == *n
            && ts(&t0).is_ok_and(|t| ts(lo).is_ok_and(|a| a <= t) && ts(hi).is_ok_and(|b| t <= b))
    })
}

/// The spans of a run's scratch waits, which [`Split::of`] takes out before every category.
const SCRATCH: &str = "a measurement's scratch slot hold";

/// THE CATEGORIES A PHASE IS BOOKED TO (feature 451 T153; the GM 2026-11-22: "we want everything measured so we know where our time goes,
/// especially for compiling, running tests, and generating maps"), first first: a second two phases hold goes to the first - compile
/// before all (D4: a hook suite or a map run that compiles is compiling), the hook suites and map generation before the tests that hold
/// them (`make done`'s hooks-test), and a landing's gate last, less all of them (T08's rule).
///
/// A WAIT ON A BUILD SLOT is before compile (feature 451 T284, `rustc/slot.rs`): a cargo call that waited for one of the machine's
/// slots writes its wait as a `slot-wait` line, and the step it was part of (a lint, a test build) spans it, so the wait is taken out
/// first and the step's own category holds only what ran.
pub const PHASE_COLUMNS: [&str; 8] = [
    SLOT_WAIT,
    "compile",
    "hook suites",
    "map generation",
    "tests",
    "gate",
    "docs",
    "review",
];

/// A `Phase` line's category, or None for a step that holds others and is booked by its run (a landing's `end`, `make done`'s
/// `static` or `hooks-test`, a lint): the checks' `build` and `cover-build` compile (D4) and their `test` and `cover-run` tests; a
/// hook suite (`src: hooks`); a map's `generate`, `render`, `page` and `cached` (`src: map`), a cohort, the gate's seeds and its
/// reference map (each rolls maps); `make quick`, `make preflight` and the gate's `counters-inert` and preflight tests; a landing's
/// `gate` and `cohort` gate; `make record` docs; a page session's write docs and its check review.
#[must_use]
pub fn category(p: &Event) -> Option<&'static str> {
    let (src, step) = (or_s(p, "src"), or_s(p, "step"));
    Some(match (src.as_str(), step.as_str()) {
        ("rust", "slot-wait") => SLOT_WAIT,
        (_, "build" | "cover-build") => "compile",
        ("rust", "test" | "cover-run")
        | ("quick" | "preflight", _)
        | ("gate", "counters-inert" | "preflight") => "tests",
        ("hooks", _) => "hook suites",
        ("map" | "cohort", _) | ("gate", "seeds" | "reference") => "map generation",
        ("land", "gate" | "cohort") => "gate",
        ("record", _) | ("page-session", "write") => "docs",
        ("page-session", _) => "review",
        // A POOL TREE'S PRE-WARM IS NO CALL'S COMPILE (feature 451 T316, `rustc/prewarm.rs`): its step is `prewarm`, never `build`, so
        // a pre-warm whose span falls inside a builder's own call is not booked to that call. Its seconds are the `Phase` lines' own
        // until a category shows them (T317).
        _ => return None,
    })
}

/// (category, its spans) - one call's phases of one category, the form [`Split`] holds and is built from.
pub type Parts = Vec<(&'static str, Vec<(f64, f64)>)>;

/// A call's spans split out of its gap, by category: each category's spans in [`PHASE_COLUMNS`]' order, disjoint from every earlier
/// one's and in order.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct Split {
    /// (category, its spans), first first.
    pub parts: Parts,
    /// Its counted lines ([`ran::kind`]: every compile, unit-test run and coverage run), a `make task-time` count and listing
    /// beside its minutes (451 T512, T522).
    pub ran: Vec<Ran>,
}

impl Split {
    /// Each category's phases, each made disjoint from those of every category before it.
    #[must_use]
    pub fn of(held: &[(&'static str, Vec<(f64, f64)>)]) -> Self {
        // a scratch wait (feature 451 T426) is taken out first and booked to none: its seconds stay the run's own
        let mut taken = union(
            held.iter()
                .filter(|(c, _)| *c == SCRATCH)
                .flat_map(|(_, s)| s.iter().copied())
                .collect(),
        );
        let mut parts = Vec::new();
        for col in PHASE_COLUMNS {
            let spans: Vec<(f64, f64)> = held
                .iter()
                .filter(|(c, _)| *c == col)
                .flat_map(|(_, s)| s.iter().copied())
                .collect();
            let own = minus(&union(spans), &taken);
            if own.is_empty() {
                continue;
            }
            taken = union(taken.into_iter().chain(own.iter().copied()).collect());
            parts.push((col, own));
        }
        Self {
            parts,
            ran: Vec::new(),
        }
    }

    /// One category's spans, none where it holds none.
    #[must_use]
    pub fn spans(&self, col: &str) -> &[(f64, f64)] {
        self.parts
            .iter()
            .find(|(c, _)| *c == col)
            .map_or(&[], |(_, s)| s.as_slice())
    }

    /// Each category's seconds inside `[lo, hi]`, a category with none left out.
    #[must_use]
    pub fn booked(&self, lo: f64, hi: f64) -> Vec<(&'static str, f64)> {
        self.parts
            .iter()
            .map(|(c, s)| (*c, overlap(s, lo, hi)))
            .filter(|(_, x)| *x > 0.0)
            .collect()
    }
}

/// The window's runs and what could not be tied to one.
#[derive(Debug, Default)]
pub struct Runs {
    /// Every run, in start order.
    pub runs: Vec<Run>,
    /// `PreToolUse` Bash lines with no `PostToolUse`: refused by a guard before they ran, so no run.
    pub refused: usize,
    /// Phases tied to no run, and their seconds.
    pub loose: (usize, f64),
    /// The page sessions' phases (task, category, seconds): a detached runner's, held by no Bash run by construction, so booked under
    /// their task directly (451 T153), never counted loose.
    pub detached: Vec<(String, &'static str, f64)>,
    /// The scratch waits' spans ([`scratch_wait`], feature 451 T426), every one read, the reports counting their window's.
    pub scratch: Vec<(f64, f64)>,
    /// The pool trees' pre-warm builds ([`ran::PREWARM`], 451 T522): held by no run, each counted under its line's own task.
    pub prewarm: Vec<Ran>,
}

/// What the runs are cut and ended by.
pub struct Window<'a> {
    /// The window's end (UTC seconds): `UNTIL=`, else the last line's time.
    pub end: f64,
    /// [`enqueued`]'s map.
    pub enqueued: &'a HashMap<String, f64>,
    /// [`stopped`]'s map.
    pub stopped: &'a HashMap<String, String>,
    /// [`read_subagents`]' queued map: a subagent's background run's end.
    pub queued: &'a HashMap<String, f64>,
    /// The Makefile's [`default_goal`].
    pub goal: &'a str,
}

/// The summed length of `spans` (disjoint) inside `[lo, hi]`.
#[must_use]
pub fn overlap(spans: &[(f64, f64)], lo: f64, hi: f64) -> f64 {
    spans
        .iter()
        .fold(0.0, |n, (a, b)| n + (b.min(hi) - a.max(lo)).max(0.0))
}

fn union(mut spans: Vec<(f64, f64)>) -> Vec<(f64, f64)> {
    spans.sort_by(|a, b| cmp_f(a.0, b.0));
    let mut out: Vec<(f64, f64)> = Vec::new();
    for (a, b) in spans {
        match out.last_mut() {
            Some(last) if a <= last.1 => last.1 = last.1.max(b),
            _ => out.push((a, b)),
        }
    }
    out
}

/// Every Bash run of `stream` (each session's and agent's) started by the window's end, its end found and clipped there, and the
/// compile phases of `aside` (`load_all`'s set-aside lines) tied to it.
///
/// # Errors
///
/// A line's time, or a `Phase` line's `t0`/`t1`, the reader cannot read.
pub fn runs(
    stream: &[Event],
    aside: &[Event],
    starts: &[(f64, String)],
    w: &Window,
) -> Result<Runs, Raised> {
    let mut ends: HashMap<String, (f64, String)> = HashMap::new();
    for e in stream {
        if (is(e, "ev", "PostToolUse") || is(e, "ev", "PostToolUseFailure"))
            && is(e, "tool", "Bash")
        {
            ends.entry(or_s(e, "id"))
                .or_insert((t_of(e)?, or_s(e, "bg")));
        }
    }
    let mut bg_ends: HashMap<String, f64> = HashMap::new();
    for e in aside.iter().filter(|e| is(e, "ev", "BgEnd")) {
        bg_ends.entry(or_s(e, "id")).or_insert(t_of(e)?);
    }
    // background task id -> when a `TaskStop` call stopped it
    let mut stops: HashMap<&str, f64> = HashMap::new();
    for e in stream.iter().filter(|e| is(e, "ev", "PreToolUse")) {
        if let Some(task) = w.stopped.get(&or_s(e, "id")) {
            stops.entry(task.as_str()).or_insert(t_of(e)?);
        }
    }
    let mut out = Runs::default();
    for e in stream {
        if !(is(e, "ev", "PreToolUse") && is(e, "tool", "Bash")) {
            continue;
        }
        let (id, t0) = (or_s(e, "id"), t_of(e)?);
        if t0 > w.end {
            continue;
        }
        let Some((post, bg_id)) = ends.get(&id) else {
            out.refused += 1;
            continue;
        };
        let bg = !bg_id.is_empty();
        let found = if bg {
            w.enqueued
                .get(&id)
                .or_else(|| bg_ends.get(&id))
                .or_else(|| w.queued.get(&id))
                .or_else(|| stops.get(bg_id.as_str()))
                .copied()
        } else {
            Some(*post)
        };
        let task = or_s(e, "task");
        out.runs.push(Run {
            t0,
            t1: found.unwrap_or(w.end).min(w.end).max(t0),
            sid: or_s(e, "sid"),
            by: or_s(e, "by"),
            bg_id: bg_id.clone(),
            makes: targets_of(e, w.goal),
            bucket: line_bucket(e, w.goal),
            task: if task.is_empty() {
                task_at(starts, t0)
            } else {
                task
            },
            bg,
            open: found.is_none(),
            split: Split::default(),
            id,
        });
    }
    tie(&mut out, aside, starts, w.end)?;
    Ok(out)
}

/// `spans` less `cut`, both disjoint and in order.
fn minus(spans: &[(f64, f64)], cut: &[(f64, f64)]) -> Vec<(f64, f64)> {
    let mut out = Vec::new();
    for &(mut a, b) in spans {
        for &(c, d) in cut {
            if d <= a || c >= b {
                continue;
            }
            if c > a {
                out.push((a, c));
            }
            a = d;
        }
        if a < b {
            out.push((a, b));
        }
    }
    out
}

/// Seconds by task and [`RUN_COLUMNS`] (and [`BACKGROUND`], `runs` the count), tasks in the order first booked.
#[must_use]
pub fn by_task(runs: &Runs) -> Vec<(String, Tally<String>)> {
    let mut rows: Vec<(String, Tally<String>)> = Vec::new();
    for r in &runs.runs {
        let i = rows
            .iter()
            .position(|(k, _)| *k == r.task)
            .unwrap_or_else(|| {
                rows.push((r.task.clone(), Tally::default()));
                rows.len() - 1
            });
        let row = &mut rows[i].1;
        row.add(&"runs".to_owned(), 1.0);
        let mut split = 0.0;
        for (col, x) in r.split.booked(r.t0, r.t1) {
            row.add(&col.to_owned(), x);
            split += x;
        }
        row.add(&r.bucket.to_owned(), r.t1 - r.t0 - split);
        if r.bg {
            row.add(&BACKGROUND.to_owned(), r.t1 - r.t0);
        }
    }
    for (task, col, secs) in &runs.detached {
        let i = rows.iter().position(|(k, _)| k == task).unwrap_or_else(|| {
            rows.push((task.clone(), Tally::default()));
            rows.len() - 1
        });
        rows[i].1.add(&(*col).to_owned(), *secs);
    }
    rows
}

/// tool-use id -> its run's [`Split`]: what the critical path splits a call's gap by.
#[must_use]
pub fn splits_by_id(runs: &Runs) -> HashMap<String, Split> {
    runs.runs
        .iter()
        .filter(|r| !r.split.parts.is_empty())
        .map(|r| (r.id.clone(), r.split.clone()))
        .collect()
}

/// The runs table as Markdown, its rows in `order` and then any task `order` lacks, with its footnote.
#[must_use]
pub fn render(runs: &Runs, order: &[String]) -> String {
    let rows = by_task(runs);
    let mut ordered: Vec<&(String, Tally<String>)> = order
        .iter()
        .filter_map(|k| rows.iter().find(|(r, _)| r == k))
        .collect();
    ordered.extend(rows.iter().filter(|(k, _)| !order.contains(k)));
    let cols: Vec<&str> = RUN_COLUMNS.iter().copied().chain([BACKGROUND]).collect();
    let mut text = format!(
        "| task | runs | minutes | {} |\n|---|---|---|{}\n",
        cols.join(" | "),
        "---|".repeat(cols.len())
    );
    let mut all: Tally<String> = Tally::default();
    let mut line = |k: &str, t: &Tally<String>| {
        let minutes = RUN_COLUMNS
            .iter()
            .fold(0.0, |n, c| n + t.get(&(*c).to_owned()));
        let cells: Vec<String> = cols
            .iter()
            .map(|c| fixed(t.get(&(*c).to_owned()) / 60.0, 1))
            .collect();
        let _ = writeln!(
            text,
            "| {k} | {} | {} | {} |",
            t.get(&"runs".to_owned()),
            fixed(minutes / 60.0, 1),
            cells.join(" | ")
        );
    };
    for (k, t) in ordered {
        for (c, v) in t.items() {
            all.add(c, *v);
        }
        line(k, t);
    }
    line("all", &all);
    let bg = runs.runs.iter().filter(|r| r.bg).count();
    let open = runs.runs.iter().filter(|r| r.open).count();
    let _ = write!(
        text,
        "\nruns: {} Bash calls of every session and agent ({bg} in the background, {open} open at the window's end), booked by their `make` \
         target through the guard's table (feature 451 T08); machine minutes, which overlap, never the wall clock; {} refused before \
         running; phases tied to no run: {} ({} min){}\n",
        runs.runs.len(),
        runs.refused,
        runs.loose.0,
        fixed(runs.loose.1 / 60.0, 1),
        scratch_note(&runs.scratch, f64::NEG_INFINITY)
    );
    text
}

/// The note on the scratch waits from `from` on (feature 451 T426), as a clause to append: how many and their minutes, and where
/// they went; nothing where there were none, so a report with none reads as it did.
#[must_use]
pub fn scratch_note(spans: &[(f64, f64)], from: f64) -> String {
    let inside: Vec<&(f64, f64)> = spans.iter().filter(|(a, _)| *a >= from).collect();
    if inside.is_empty() {
        return String::new();
    }
    let secs = inside.iter().fold(0.0, |n, (a, b)| n + (b - a));
    let what = if from.is_finite() {
        " in the window"
    } else {
        ""
    };
    format!(
        "; waits on a scratch slot directory (451 T426): {}{what} ({} min), booked to no category - a measurement's own scripted holds \
         (`L7R_BUILD_SLOT_DIR` away from the default), their seconds their run's own, never `{SLOT_WAIT}`",
        inside.len(),
        fixed(secs / 60.0, 1)
    )
}

mod flight;
pub mod ran;
pub mod spent;
pub use flight::{flight, Agent, Flight};
use ran::tie;
pub use ran::Ran;

#[cfg(test)]
mod tests;

#[cfg(test)]
mod waits_tests;

#[cfg(test)]
mod scratch_tests;

#[cfg(test)]
mod spent_tests;
