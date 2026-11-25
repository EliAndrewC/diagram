//! The task time breakdown's booking (451 T243): every actor's time - each main session, each builder, each review agent, each Bash run -
//! as MINUTES (machine time, which overlaps) and BLOCKING minutes (a main session's wall clock, each second once per task it blocks, descended into what
//! it waited on), by (feature, task), category and make target or program.
//!
//! THE RULES, each the GM's words in tasks.md T243's amendments:
//! - A MODEL TURN is the gap from an actor's line to its next call, booked by the tool that call is: Read/Grep/Glob reading code,
//!   Edit/Write writing code, Bash running a command, Agent dispatching; a gap ending at a `Stop` writes its reply. A tool's own run
//!   joins its turn's category (a Read's milliseconds are reading). The main session's and the builders' are apart.
//! - A REVIEW AGENT's whole span is its kind's (plan review, claims round, record and pop-up checks, arbiter, the GM's filter, research
//!   and page sessions, map and building reviews), never pooled with the builders' reading and writing.
//! - A BASH RUN is booked by its make target through the guard's table (`columns::line_bucket`), its phases split out (compile, hook
//!   suites, map generation), the review bucket split by kind; a run with no booked target by its program ([`super::program`]).
//! - BLOCKING walks each main session's own time: its turns and calls are its own; a wait - between turns on work, or a wait loop - is
//!   booked, at each instant, to each task's thing in flight that ends last (that task's critical one), descending into a builder's own
//!   time the same way: its turns, its foreground commands, and its waits on its own background runs and agents. A wait with nothing in
//!   flight is booked as that, named.
//! - BLOCKING IS BY TASK AND DEPENDENCY (the GM 2026-11-25: "a minute should count as blocking. When something else is waiting on it to
//!   be done before it can be started ... that research would be blocking even if there was a different unrelated task happening in a
//!   different subagent at the same time"): each piece is booked to the task whose next step waited on it. A CLUE given with the data
//!   names it - a dispatch's or a page brief's `Blocks: <feature> T<n>` / `Blocks: T<n>` / `Blocks: none` line, a command's
//!   `L7R_BLOCKS=<feature>:T<n>` (the event log's `blocks`). With none, the DEFAULTS, each a GUESS held to the GM's "it doesn't have to
//!   be 100% exact": a main session's own turns and waits block the task its lines carry (its `make task-start` mark); a builder's time
//!   (its turns, foreground commands, the review agents it awaits) blocks the builder's own task, else its waiter's; a run or a review
//!   agent blocks its waiter's task, a background run only from when its waiter waits on it (the walk reaches it no sooner); a page
//!   session or a research pass blocks nothing. EACH task with blocking work in flight gets its own piece of each second (round 5's L4b):
//!   a wait books every task its work in flight blocks, and an actor's own time (a turn or run, and the session's waits on the GM and
//!   idle hours too) books, beside its own task, every other task its background work in flight blocks - so the tasks' blocking sums to a session's clock or past it. Work that blocks no task is the
//!   wait's piece only where nothing in flight blocks one, and is booked apart (`Ledger::free`), never blocking.

use std::collections::{HashMap, HashSet};

use l7r_shared::guards::event_log_hooks::{agent_category, bucket_of};

use super::super::events::{get, is, or_s, t_of, Event, Raised, IDLE_CAP_S};
use l7r_shared::make::{invoked, DEFAULT_GOAL};

use super::super::where_time::columns::{Agent, Run, Runs, PRECEDENCE};
use super::program;

/// (feature, task): task ids collide across features.
pub type Key = (String, String);

/// A main session's time with nothing in flight: the prefix of its classes, each named by what came just before and after the gap
/// (the GM 2026-11-25: "as long as that automatically gets broken down in the future"), the rest named unexplained.
pub const NOTHING: &str = "waiting: nothing in flight";
/// A gap while a detached page session ran with no monitor on it: the session was waiting on a queue it did not track.
pub const NOTHING_PAGES: &str =
    "waiting: nothing in flight - a page session running, no monitor on it";
/// A gap after the work its `Stop` named had ended: the wake came after the thing waited on was done.
pub const NOTHING_ENDED: &str =
    "waiting: nothing in flight - after the work its Stop named had ended";
/// A `Stop` naming nothing, then a notification or reminder (a prompt not the GM's) woke the session.
pub const NOTHING_WOKEN: &str =
    "waiting: nothing in flight - until a notification or reminder woke it";
/// A `Stop` naming nothing, then the session started again (a resume, a compaction or a clear).
pub const NOTHING_RESTART: &str = "waiting: nothing in flight - until the session started again";
/// A main session's wait with only a monitor in flight and no page session running.
pub const MONITOR: &str = "waiting: a monitor alone";
/// A detached page session's phases and the research-pass agents.
pub const PAGES: &str = "research and page sessions";
/// The record and pop-up checks' agents.
const RECORD: &str = "record and pop-up checks: agents";
/// A builder's time inside its span that no line of its accounts for.
/// Generating maps: a map, sheet or cohort run's remainder, its phases' column, and a builder's scratch sweep (the GM's "generating maps").
pub const MAPS: &str = "map generation";

/// The targets that draw maps or sheets: the guard's table books them tests (`map`, `hamlet`, `compound`, `sheet-render`, the dev
/// loop's own run) or gate (`cohort`, `cohort-landing`, the sweep a landing reads); the breakdown books them all to [`MAPS`].
const MAP_TARGETS: [&str; 7] = [
    "map",
    "hamlet",
    "compound",
    "sheet-render",
    "maps-moved",
    "cohort",
    "cohort-landing",
];
pub const UNLINED: &str = "builders: inside its span, no line of its";
/// A command no transcript holds.
pub const UNREAD: &str = "commands no transcript holds";
const BOOKED_ELSEWHERE: &str = "Makefile targets the guard's table does not book";

/// One (key, category, target) cell.
#[derive(Debug, Default, Clone, Copy, PartialEq)]
pub struct Cell {
    /// Machine seconds.
    pub min: f64,
    /// Blocking seconds.
    pub block: f64,
    /// The blocking seconds booked from a foreground run in its actor.
    pub fg: f64,
}

/// What the booking found.
#[derive(Debug, Default)]
pub struct Ledger {
    /// (key, category, target or "") -> its cell.
    pub cells: HashMap<(Key, String, String), Cell>,
    /// (key, target) -> runs.
    pub runs: HashMap<(Key, String), usize>,
    /// target -> the category its runs book to, their phases apart.
    pub books_to: HashMap<String, String>,
    /// Seconds a wait was held by work that blocked no task (a page session or research pass whose brief names none, a `Blocks: none`
    /// clue), by the category the work is: waited on, never blocking.
    pub free: HashMap<String, f64>,
    /// Seconds of the window with 0, 1, 2 and 3 or more actors working at once (a main session's own turns and runs, each agent's
    /// span, each page-session phase): the overlap the minutes hide.
    pub at_once: [f64; 4],
}

impl Ledger {
    fn add(&mut self, key: &Key, cat: &str, target: &str, c: Cell) {
        let e = self
            .cells
            .entry((key.clone(), cat.to_owned(), target.to_owned()))
            .or_default();
        e.min += c.min;
        e.block += c.block;
        e.fg += c.fg;
    }
}

/// A page session's phase: a detached runner's, held by no Bash run.
#[derive(Debug, Clone, PartialEq)]
pub struct Page {
    /// Its span.
    pub t0: f64,
    /// Its end.
    pub t1: f64,
    /// Its feature and task.
    pub key: Key,
    /// The session the runner started (the phase's `name`): its own lines are the page session's, never a main session's.
    pub sid: String,
    /// Its brief's `Blocks:` clue, "" where it gave none (it then blocks nothing).
    pub blocks: String,
}

/// What the booking reads.
pub struct World<'a> {
    /// Every log's lines in the window, each tagged with its log's `feature`, in time order.
    pub stream: &'a [Event],
    /// Every Bash run ([`super::super::where_time::columns::runs`]).
    pub runs: &'a Runs,
    /// tool-use id -> its command.
    pub commands: &'a HashMap<String, String>,
    /// Every agent with its spans.
    pub agents: &'a [Agent],
    /// The page sessions' phases.
    pub pages: &'a [Page],
    /// The window, `[lo, hi]` in UTC seconds.
    pub window: (f64, f64),
}

#[derive(Debug, Clone, Copy, PartialEq)]
enum Cand {
    Run(usize),
    Agent(usize),
    Pages,
}

#[derive(Debug, Clone, PartialEq)]
enum What {
    Own(String),
    Run(usize),
    Wait(Vec<Cand>, String),
}

/// How a run's piece is booked: as minutes under its own task, or as blocking the task given (none: waited on, blocking nothing).
#[derive(Debug, Clone, Copy)]
enum As<'k> {
    Minutes,
    Blocking(Option<&'k Key>),
}

#[derive(Debug, Clone, PartialEq)]
struct Seg {
    t0: f64,
    t1: f64,
    key: Key,
    /// The actor whose time it is (its owned background work is in flight beside it).
    who: String,
    what: What,
}

/// An event's (feature, task).
fn key_of(e: &Event) -> Key {
    let task = or_s(e, "task");
    (
        or_s(e, "feature"),
        if task.is_empty() {
            "-".to_owned()
        } else {
            task
        },
    )
}

/// The review kind an agent's whole span is booked to, `None` for a builder (451 T243 (f)).
#[must_use]
pub fn review_cat(kind: &str) -> Option<&'static str> {
    Some(match kind {
        "claims-triage" => "claims round: agents",
        "modal-triage" | "source-filter" | "size-exception" => RECORD,
        "escalation-check" => "the GM's filter: agents (escalation-check)",
        "research-pass" => PAGES,
        "work-budget" | "message-check" | "perf-audit" => {
            "other review agents (work-budget, message-check)"
        }
        _ => match agent_category(kind, "") {
            "claims check" => "claims round: agents",
            "record check" => RECORD,
            "review check" => "map and building reviews: agents",
            "spec review" => "plan review: agents",
            "round arbiter" => "arbiter: agents",
            _ => return None,
        },
    })
}

/// A model turn's or a tool's category for actor `who` (`main session` or `builders`), by the tool (`""` the reply).
#[must_use]
pub fn tool_cat(who: &str, tool: &str) -> String {
    let what = match tool {
        "Read" | "Grep" | "Glob" => "reading code".to_owned(),
        "Edit" | "Write" | "NotebookEdit" | "MultiEdit" => "writing code".to_owned(),
        "Bash" => "running a command (the model's turn)".to_owned(),
        "Agent" | "Task" => "dispatching an agent".to_owned(),
        "" => "writing its reply".to_owned(),
        other => format!("other tools ({other})"),
    };
    format!("{who}: {what}")
}

/// The review bucket's kind by target (451 T243 (e)).
fn review_kind(target: &str) -> &'static str {
    match target {
        "decide" | "plan-delta" | "plan-verdict" => "plan review: commands",
        t if t.starts_with("claims-") || t == "impl-check" => "claims round: commands",
        t if t.starts_with("arbiter-") => "arbiter: commands",
        "check-bundle" | "modal-bundle" | "record-owed" | "modal-triage" | "modal-triaged"
        | "modal-prepass" | "translation-owed" | "record-checked" | "record-prepass"
        | "style-prepass" | "quote-verbatim" => "record and pop-up checks: commands",
        _ => "review: other commands",
    }
}

/// A run's category (its phases apart) and its label in the per-target table.
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the map `read_subagents` makes")]
pub fn run_cat(r: &Run, commands: &HashMap<String, String>) -> (String, String) {
    // a line that logged no target (a past log, a detector since fixed): the targets its command RUNS, never one it mentions
    let found: Vec<String>;
    let (makes, bucket) = if r.makes.is_empty() {
        found = commands.get(&r.id).map_or_else(Vec::new, |c| {
            invoked(c)
                .into_iter()
                .filter(|t| t != DEFAULT_GOAL)
                .collect()
        });
        let buckets: Vec<&str> = found.iter().map(|m| bucket_of(m)).collect();
        let first = PRECEDENCE.iter().find(|b| buckets.contains(b));
        (&found[..], first.copied().unwrap_or("other"))
    } else {
        (&r.makes[..], r.bucket)
    };
    if bucket != "other" {
        let t = makes
            .iter()
            .find(|m| bucket_of(m) == bucket)
            .map_or("", String::as_str);
        let cat = match bucket {
            _ if MAP_TARGETS.contains(&t) => MAPS,
            "review" => review_kind(t),
            "docs" => "record builds and docs",
            "land" => "landing",
            b => b,
        };
        return (cat.to_owned(), format!("make {t}"));
    }
    if let Some(m) = makes.first() {
        let cat = match m.as_str() {
            "crate-checks" => "tests",
            _ => BOOKED_ELSEWHERE,
        };
        return (cat.to_owned(), format!("make {m}"));
    }
    match commands.get(&r.id) {
        Some(c) => {
            let (cat, label) = program::class(c);
            (cat.to_owned(), label)
        }
        None => (
            UNREAD.to_owned(),
            "a command no transcript holds".to_owned(),
        ),
    }
}

fn phase_cat(col: &str) -> &str {
    match col {
        "docs" => "record builds and docs",
        "review" => PAGES,
        c => c,
    }
}

fn is_wait(cat: &str) -> bool {
    cat == program::WAIT || cat == program::PAGE_WAIT
}

/// The booking's indexes over the world.
struct Ix<'a> {
    w: &'a World<'a>,
    run_of: HashMap<&'a str, usize>,
    run_key: Vec<Key>,
    run_cats: Vec<(String, String)>,
    agent_of: HashMap<&'a str, usize>,
    agent_key: Vec<Key>,
    /// Each run's and each agent's `Blocks:` clue, "" where none was given.
    run_clue: Vec<String>,
    agent_clue: Vec<String>,
    /// The features the lines name, a clue's `451` read as the one it opens.
    features: Vec<String>,
    /// actor -> its own background runs and the agents it dispatched.
    owned: HashMap<String, Vec<Cand>>,
    segs: HashMap<String, Vec<Seg>>,
}

/// An actor's name: a main session's `s:<sid>`, an agent's id.
fn actor(e: &Event) -> String {
    let by = or_s(e, "by");
    if by.is_empty() {
        format!("s:{}", or_s(e, "sid"))
    } else {
        by
    }
}

impl<'a> Ix<'a> {
    fn new(w: &'a World<'a>) -> Self {
        let mut pre_key: HashMap<&str, Key> = HashMap::new();
        let mut clue: HashMap<String, String> = HashMap::new();
        let mut features: Vec<String> = Vec::new();
        let mut agent_feature: HashMap<String, String> = HashMap::new();
        let mut owned: HashMap<String, Vec<Cand>> = HashMap::new();
        let agent_of: HashMap<&str, usize> = w
            .agents
            .iter()
            .enumerate()
            .map(|(i, a)| (a.aid.as_str(), i))
            .collect();
        for e in w.stream {
            if let Some(id) = get(e, "id").as_str() {
                if is(e, "ev", "PreToolUse") {
                    pre_key.insert(id, key_of(e));
                }
            }
            let (f, blocks) = (or_s(e, "feature"), or_s(e, "blocks"));
            if !features.contains(&f) {
                features.push(f);
            }
            let aid = or_s(e, "aid");
            // a call's clue under its id, an Agent call's under its agent's too (its end's line names the agent)
            for id in [or_s(e, "id"), aid.clone()] {
                if !blocks.is_empty() && !id.is_empty() {
                    clue.insert(id, blocks.clone());
                }
            }
            if !aid.is_empty() {
                agent_feature
                    .entry(aid.clone())
                    .or_insert_with(|| or_s(e, "feature"));
                if is(e, "ev", "PostToolUse") && is(e, "tool", "Agent") {
                    if let Some(&i) = agent_of.get(aid.as_str()) {
                        owned.entry(actor(e)).or_default().push(Cand::Agent(i));
                    }
                }
            }
        }
        for p in w.pages {
            if !features.contains(&p.key.0) {
                features.push(p.key.0.clone());
            }
        }
        let run_key: Vec<Key> = w
            .runs
            .runs
            .iter()
            .map(|r| {
                let k = pre_key.get(r.id.as_str()).cloned().unwrap_or_default();
                (k.0, r.task.clone())
            })
            .collect();
        for (i, r) in w.runs.runs.iter().enumerate().filter(|(_, r)| r.bg) {
            let who = if r.by.is_empty() {
                format!("s:{}", r.sid)
            } else {
                r.by.clone()
            };
            owned.entry(who).or_default().push(Cand::Run(i));
        }
        let agent_key = w
            .agents
            .iter()
            .map(|a| {
                let task = if a.task.is_empty() { "-" } else { &a.task };
                (
                    agent_feature.get(&a.aid).cloned().unwrap_or_default(),
                    task.to_owned(),
                )
            })
            .collect();
        Ix {
            w,
            run_clue: w
                .runs
                .runs
                .iter()
                .map(|r| clue.get(&r.id).cloned().unwrap_or_default())
                .collect(),
            agent_clue: w
                .agents
                .iter()
                .map(|a| clue.get(&a.aid).cloned().unwrap_or_default())
                .collect(),
            features,
            run_of: w
                .runs
                .runs
                .iter()
                .enumerate()
                .map(|(i, r)| (r.id.as_str(), i))
                .collect(),
            run_cats: w.runs.runs.iter().map(|r| run_cat(r, w.commands)).collect(),
            run_key,
            agent_of,
            agent_key,
            owned,
            segs: HashMap::new(),
        }
    }

    fn span(&self, c: Cand) -> (f64, f64) {
        match c {
            Cand::Run(i) => (self.w.runs.runs[i].t0, self.w.runs.runs[i].t1),
            Cand::Agent(i) => {
                let s = &self.w.agents[i].spans;
                (
                    s.first().map_or(0.0, |x| x.0),
                    s.last().map_or(0.0, |x| x.1),
                )
            }
            Cand::Pages => self
                .w
                .pages
                .iter()
                .fold((f64::MAX, f64::MIN), |(a, b), p| (a.min(p.t0), b.max(p.t1))),
        }
    }

    /// Whether `c` is in flight over all of `[x, y]`.
    #[expect(
        clippy::many_single_char_names,
        reason = "an interval's ends `x`/`y` beside its run, agent or segment, as the module's doc names them"
    )]
    fn active(&self, c: Cand, x: f64, y: f64) -> bool {
        match c {
            Cand::Run(i) => {
                let r = &self.w.runs.runs[i];
                r.t0 <= x && y <= r.t1
            }
            Cand::Agent(i) => self.w.agents[i].spans.iter().any(|s| s.0 <= x && y <= s.1),
            Cand::Pages => self.w.pages.iter().any(|p| p.t0 <= x && y <= p.t1),
        }
    }

    /// The candidates a `Stop` names in flight; with no list, every one the actor owns.
    fn named(&self, who: &str, stop: &Event) -> Vec<Cand> {
        let Some(list) = get(stop, "inflight").as_array() else {
            return self.owned.get(who).cloned().unwrap_or_default();
        };
        let mut out = Vec::new();
        for x in list {
            let id = x
                .get("id")
                .and_then(serde_json::Value::as_str)
                .unwrap_or("");
            if let Some(&i) = self.agent_of.get(id) {
                out.push(Cand::Agent(i));
            } else if let Some(i) = self.w.runs.runs.iter().position(|r| r.bg && r.bg_id == id) {
                out.push(Cand::Run(i));
            } else if x.get("type").and_then(serde_json::Value::as_str) == Some("monitor") {
                out.push(Cand::Pages);
            }
        }
        out
    }

    /// A main session's time from its `Stop` to the next line `next`, `gap` seconds: the GM's when he speaks, else a wait.
    fn after_stop(&self, who: &str, stop: &Event, next: &Event, gap: f64) -> What {
        if is(next, "ev", "UserPromptSubmit") && get(next, "gm").as_bool() != Some(false) {
            let cat = if gap > IDLE_CAP_S {
                "the GM away"
            } else {
                "the GM"
            };
            return What::Own(cat.to_owned());
        }
        let monitor = get(stop, "inflight").as_array().is_some_and(|l| {
            l.iter()
                .any(|x| x.get("type").and_then(serde_json::Value::as_str) == Some("monitor"))
        });
        let fallback = if monitor {
            MONITOR.to_owned()
        } else {
            match or_s(next, "ev").as_str() {
                "UserPromptSubmit" => NOTHING_WOKEN.to_owned(),
                "SessionStart" => NOTHING_RESTART.to_owned(),
                ev => format!("{NOTHING} - unexplained, then a {ev} line"),
            }
        };
        What::Wait(self.named(who, stop), fallback)
    }

    /// An actor's segments from its lines in time order (the module's doc).
    fn segments(&self, who: &str, lines: &[&Event], builder: bool) -> Result<Vec<Seg>, Raised> {
        let posted: HashSet<String> = lines
            .iter()
            .filter(|e| is(e, "ev", "PostToolUse") || is(e, "ev", "PostToolUseFailure"))
            .map(|e| or_s(e, "id"))
            .collect();
        let prefix = if builder { "builders" } else { "main session" };
        let mut open: Vec<&Event> = Vec::new();
        let mut out = Vec::new();
        let mut between: Option<&Event> = None;
        for (i, a) in lines.iter().enumerate() {
            let ev = or_s(a, "ev");
            match ev.as_str() {
                "PreToolUse" if posted.contains(&or_s(a, "id")) => open.push(a),
                "PostToolUse" | "PostToolUseFailure" => {
                    open.retain(|o| or_s(o, "id") != or_s(a, "id"));
                }
                "Stop" if !builder => between = Some(a),
                "UserPromptSubmit" => between = None,
                _ => {}
            }
            let Some(b) = lines.get(i + 1) else { break };
            let (x, y) = (t_of(a)?, t_of(b)?);
            if y <= x {
                continue;
            }
            let key = key_of(a);
            let what = if let Some(stop) = between {
                self.after_stop(who, stop, b, y - x)
            } else if let Some(o) = open.last() {
                let tool = or_s(o, "tool");
                match self.run_of.get(or_s(o, "id").as_str()) {
                    Some(&r) if tool == "Bash" && is_wait(&self.run_cats[r].0) => What::Wait(
                        self.owned.get(who).cloned().unwrap_or_default(),
                        program::WAIT.to_owned(),
                    ),
                    Some(&r) if tool == "Bash" => What::Run(r),
                    _ => What::Own(tool_cat(prefix, &tool)),
                }
            } else if y - x > IDLE_CAP_S {
                What::Own("idle (over an hour)".to_owned())
            } else {
                let tool = if is(b, "ev", "PreToolUse") {
                    or_s(b, "tool")
                } else {
                    String::new()
                };
                // a builder's turn that ends after its own background work did is a wait on it up to that end (the module's doc)
                let held: Vec<Cand> = if builder {
                    self.owned
                        .get(who)
                        .into_iter()
                        .flatten()
                        .copied()
                        .filter(|c| {
                            let (s0, s1) = self.span(*c);
                            s0 <= x && x < s1 && s1 <= y
                        })
                        .collect()
                } else {
                    Vec::new()
                };
                let w_end = held.iter().map(|c| self.span(*c).1).fold(x, f64::max);
                if w_end > x {
                    out.push(Seg {
                        t0: x,
                        t1: w_end,
                        key: key.clone(),
                        who: who.to_owned(),
                        what: What::Wait(
                            held,
                            "builders: waiting on its background work".to_owned(),
                        ),
                    });
                }
                if y > w_end {
                    out.push(Seg {
                        t0: w_end,
                        t1: y,
                        key,
                        who: who.to_owned(),
                        what: What::Own(tool_cat(prefix, &tool)),
                    });
                }
                continue;
            };
            out.push(Seg {
                t0: x,
                t1: y,
                key,
                who: who.to_owned(),
                what,
            });
        }
        Ok(out)
    }

    /// A run's piece `[x, y]` booked: its phases, the rest its category - as minutes under its own task, or as blocking `blocked`.
    #[expect(
        clippy::many_single_char_names,
        reason = "an interval's ends `x`/`y` beside its run, agent or segment, as the module's doc names them"
    )]
    fn book_run(&self, l: &mut Ledger, i: usize, (x, y): (f64, f64), how: As, fg: bool) {
        let r = &self.w.runs.runs[i];
        let (cat, target) = &self.run_cats[i];
        let mut split = 0.0;
        let mut put = |col: &str, s: f64| match how {
            As::Blocking(b) => block(l, b, (col, target), s, fg),
            As::Minutes => l.add(
                &self.run_key[i],
                col,
                target,
                Cell {
                    min: s,
                    ..Cell::default()
                },
            ),
        };
        for (col, s) in r.split.booked(x, y) {
            put(phase_cat(col), s);
            split += s;
        }
        put(cat, y - x - split);
    }

    /// The blocking of `[x, y]`, a wait on `cands` by a waiter blocking `blocked`: each instant, for each task, to its work in flight that blocks it
    /// and ends last (the critical one); with none blocking a task, the one ending last, as waited-on time; with none, `fallback`.
    #[expect(
        clippy::many_single_char_names,
        reason = "an interval's ends `x`/`y` beside its run, agent or segment, as the module's doc names them"
    )]
    fn descend(
        &self,
        l: &mut Ledger,
        cands: &[Cand],
        (x, y): (f64, f64),
        blocked: Option<&Key>,
        fallback: &str,
        depth: usize,
    ) {
        let mut cuts = vec![x, y];
        // a gap with nothing in flight is split where a page session starts or ends, so its piece under one is named so
        let nothing = fallback.starts_with(NOTHING);
        for c in cands {
            let (a, b) = self.span(*c);
            cuts.extend([a, b].into_iter().filter(|t| x < *t && *t < y));
        }
        if nothing || cands.contains(&Cand::Pages) {
            for p in self.w.pages {
                cuts.extend([p.t0, p.t1].into_iter().filter(|t| x < *t && *t < y));
            }
        }
        cuts.sort_by(f64::total_cmp);
        cuts.dedup();
        for w in cuts.windows(2) {
            let (px, py) = (w[0], w[1]);
            // blocking is by dependency (the GM 2026-11-25: "a minute should count as blocking. When something else is waiting on it to
            // be done before it can be started ... even if there was a different unrelated task happening in a different subagent at
            // the same time"): EACH task with blocking work in flight gets its own piece, the one of its work that ends last (the
            // others ending sooner would not have shortened its wait) - so the tasks' blocking may sum past the clock (round 5's L4b)
            if self.each_task(l, cands, (px, py), blocked, None, depth) {
                continue;
            }
            // nothing in flight blocks a task: the one ending last, waited on and blocking none
            let best = cands
                .iter()
                .copied()
                .filter(|c| self.active(*c, px, py))
                .map(|c| (self.target(c, (px, py), blocked), c))
                .max_by(|a, b| self.span(a.1).1.total_cmp(&self.span(b.1).1));
            let class = if !nothing {
                fallback
            } else if self.w.pages.iter().any(|p| p.t0 <= px && py <= p.t1) {
                NOTHING_PAGES
            } else if cands.is_empty() {
                fallback
            } else {
                NOTHING_ENDED
            };
            match best {
                // a wait on a page session nothing tracked blocks what the page session blocks: its brief's task, else nothing
                None if class == NOTHING_PAGES => {
                    let to = self.target(Cand::Pages, (px, py), blocked);
                    block(l, to.as_ref(), (class, ""), py - px, false);
                }
                None => block(l, blocked, (class, ""), py - px, false),
                Some((to, c)) => self.book_cand(l, c, (px, py), to.as_ref(), depth),
            }
        }
    }

    /// Books, over `[x, y]` (no candidate starting or ending inside it), each task that work in `cands` blocks - but the task `skip` -
    /// its own piece: that task's work in flight that ends last. Whether any was booked.
    #[expect(
        clippy::many_single_char_names,
        reason = "an interval's ends `x`/`y` beside its run, agent or segment, as the module's doc names them"
    )]
    fn each_task(
        &self,
        l: &mut Ledger,
        cands: &[Cand],
        (x, y): (f64, f64),
        blocked: Option<&Key>,
        skip: Option<&Key>,
        depth: usize,
    ) -> bool {
        let mut by_task: Vec<(Key, Cand)> = Vec::new();
        for c in cands.iter().copied().filter(|c| self.active(*c, x, y)) {
            let Some(k) = self.target(c, (x, y), blocked) else {
                continue;
            };
            if skip == Some(&k) {
                continue;
            }
            match by_task.iter_mut().find(|(t, _)| *t == k) {
                Some(e) if self.span(c).1 > self.span(e.1).1 => e.1 = c,
                Some(_) => {}
                None => by_task.push((k, c)),
            }
        }
        for (k, c) in &by_task {
            self.book_cand(l, *c, (x, y), Some(k), depth);
        }
        !by_task.is_empty()
    }

    /// A candidate's piece `[x, y]` booked as blocking `to`.
    #[expect(
        clippy::many_single_char_names,
        reason = "an interval's ends `x`/`y` beside its run, agent or segment, as the module's doc names them"
    )]
    fn book_cand(
        &self,
        l: &mut Ledger,
        c: Cand,
        (x, y): (f64, f64),
        to: Option<&Key>,
        depth: usize,
    ) {
        match c {
            Cand::Pages => block(l, to, (PAGES, ""), y - x, false),
            Cand::Run(i) if is_wait(&self.run_cats[i].0) => {
                let next: &[Cand] = if self.run_cats[i].0 == program::PAGE_WAIT {
                    &[Cand::Pages]
                } else {
                    &[]
                };
                self.descend(l, next, (x, y), to, program::WAIT, depth + 1);
            }
            Cand::Run(i) => self.book_run(l, i, (x, y), As::Blocking(to), false),
            Cand::Agent(i) => self.agent_piece(l, i, (x, y), to, depth + 1),
        }
    }

    /// While an actor's own turn or run blocks `blocked`, its background work in flight that blocks ANOTHER task blocks that task
    /// beside it (round 5's L4b: a research pass `Blocks: T4` keeps blocking T4 while the session works its own T5 turn).
    #[expect(
        clippy::many_single_char_names,
        reason = "an interval's ends `x`/`y` beside its run, agent or segment, as the module's doc names them"
    )]
    fn beside(
        &self,
        l: &mut Ledger,
        who: &str,
        (x, y): (f64, f64),
        blocked: Option<&Key>,
        depth: usize,
    ) {
        let owned: Vec<Cand> = self
            .owned
            .get(who)
            .into_iter()
            .flatten()
            .copied()
            .filter(|c| {
                let (a, b) = self.span(*c);
                a < y && x < b
            })
            .collect();
        if owned.is_empty() || depth >= 8 {
            return;
        }
        let mut cuts = vec![x, y];
        for c in &owned {
            let (a, b) = self.span(*c);
            cuts.extend([a, b].into_iter().filter(|t| x < *t && *t < y));
        }
        cuts.sort_by(f64::total_cmp);
        cuts.dedup();
        for w in cuts.windows(2) {
            self.each_task(l, &owned, (w[0], w[1]), blocked, blocked, depth);
        }
    }

    /// An agent's time `[x, y]` booked as blocking `blocked`: a review agent's to its kind, a builder's by its own segments.
    #[expect(
        clippy::many_single_char_names,
        reason = "an interval's ends `x`/`y` beside its run, agent or segment, as the module's doc names them"
    )]
    fn agent_piece(
        &self,
        l: &mut Ledger,
        i: usize,
        (x, y): (f64, f64),
        blocked: Option<&Key>,
        depth: usize,
    ) {
        let a = &self.w.agents[i];
        if let Some(cat) = review_cat(&a.kind) {
            block(l, blocked, (cat, ""), y - x, false);
            return;
        }
        let mut covered = 0.0;
        for s in self.segs.get(&a.aid).into_iter().flatten() {
            let (sx, sy) = (s.t0.max(x), s.t1.min(y));
            if sy <= sx {
                continue;
            }
            covered += sy - sx;
            self.book_seg(l, s, (sx, sy), blocked, depth);
        }
        if y - x - covered > 0.0 {
            block(l, blocked, (UNLINED, ""), y - x - covered, false);
        }
    }

    /// A segment's piece booked as blocking `blocked`.
    fn book_seg(
        &self,
        l: &mut Ledger,
        s: &Seg,
        piece: (f64, f64),
        blocked: Option<&Key>,
        depth: usize,
    ) {
        match &s.what {
            What::Own(cat) => {
                block(l, blocked, (cat, ""), piece.1 - piece.0, false);
                self.beside(l, &s.who, piece, blocked, depth);
            }
            What::Run(i) => {
                self.book_run(l, *i, piece, As::Blocking(blocked), true);
                self.beside(l, &s.who, piece, blocked, depth);
            }
            // a cycle cannot form (an agent waits only on what it started), but the depth bounds the walk all the same
            What::Wait(c, fb) if depth < 8 => self.descend(l, c, piece, blocked, fb, depth),
            What::Wait(_, fb) => block(l, blocked, (fb, ""), piece.1 - piece.0, false),
        }
    }
}

/// `secs` of `cat` (its make target `target`) booked as blocking `blocked`, or, blocking no task, as waited-on time.
fn block(l: &mut Ledger, blocked: Option<&Key>, (cat, target): (&str, &str), secs: f64, fg: bool) {
    match blocked {
        Some(k) => l.add(
            k,
            cat,
            target,
            Cell {
                block: secs,
                fg: if fg { secs } else { 0.0 },
                ..Cell::default()
            },
        ),
        None => *l.free.entry(cat.to_owned()).or_default() += secs,
    }
}

/// The ledger of the world (the module's doc).
///
/// # Errors
///
/// A line's time the reader cannot read.
pub fn book(w: &World) -> Result<Ledger, Raised> {
    let mut ix = Ix::new(w);
    let mut lines: HashMap<String, Vec<&Event>> = HashMap::new();
    let mut order: Vec<String> = Vec::new();
    for e in w.stream {
        let ev = or_s(e, "ev");
        let who = match ev.as_str() {
            "PreToolUse" | "PostToolUse" | "PostToolUseFailure" => actor(e),
            "Stop" | "UserPromptSubmit" => format!("s:{}", or_s(e, "sid")),
            "SubagentStart" | "SubagentStop" => or_s(e, "aid"),
            _ => continue,
        };
        if !lines.contains_key(&who) {
            order.push(who.clone());
        }
        lines.entry(who).or_default().push(e);
    }
    for who in &order {
        let builder = !who.starts_with("s:");
        let segs = ix.segments(who, &lines[who], builder)?;
        ix.segs.insert(who.clone(), segs);
    }
    let mut l = Ledger::default();
    let (lo, hi) = w.window;
    // a page session is a detached `claude` session that logs as one: its phases are its minutes, and nobody's clock is its own (on
    // 2026-11-25 its sessions' turns booked 393 min of "main session" blocking before this, measured by `make task-time SINCE=24h`)
    let paged: HashSet<String> = w.pages.iter().map(|p| format!("s:{}", p.sid)).collect();
    // MINUTES: every run but a review agent's foreground one (its agent's span holds it), every builder's and main session's own
    // segment, every review agent's span, every page-session phase
    for (i, r) in w.runs.runs.iter().enumerate() {
        let review_fg = (!r.bg
            && ix
                .agent_of
                .get(r.by.as_str())
                .is_some_and(|&a| review_cat(&w.agents[a].kind).is_some()))
            || (r.by.is_empty() && paged.contains(&format!("s:{}", r.sid)));
        let (x, y) = (r.t0.max(lo), r.t1.min(hi));
        // a run counts where it ran: one read back before the window is a landed task's, never the window's
        if r.t1 >= lo && r.t0 <= hi {
            *l.runs
                .entry((ix.run_key[i].clone(), ix.run_cats[i].1.clone()))
                .or_default() += 1;
        }
        l.books_to
            .insert(ix.run_cats[i].1.clone(), ix.run_cats[i].0.clone());
        if !review_fg && y > x {
            ix.book_run(&mut l, i, (x, y), As::Minutes, false);
        }
    }
    for who in order.iter().filter(|w| !paged.contains(*w)) {
        let review = ix
            .agent_of
            .get(who.as_str())
            .is_some_and(|&a| review_cat(&w.agents[a].kind).is_some());
        for s in ix.segs[who].iter().filter(|_| !review) {
            if let What::Own(cat) = &s.what {
                let (x, y) = (s.t0.max(lo), s.t1.min(hi));
                if y > x && !cat.starts_with("the GM") && !cat.starts_with("idle") {
                    l.add(
                        &s.key,
                        cat,
                        "",
                        Cell {
                            min: y - x,
                            ..Cell::default()
                        },
                    );
                }
            }
        }
    }
    span_minutes(w, &ix, &mut l);
    l.at_once = at_once(w, &ix, &order, &paged);
    // BLOCKING: each main session's own time, descended
    for who in order
        .iter()
        .filter(|w| w.starts_with("s:") && !paged.contains(*w))
    {
        for s in &ix.segs[who] {
            let (x, y) = (s.t0.max(lo), s.t1.min(hi));
            if y > x {
                ix.book_seg(&mut l, s, (x, y), Some(&s.key), 0);
            }
        }
    }
    Ok(l)
}

mod clue;
mod window;
use window::{at_once, span_minutes};

#[cfg(test)]
pub mod tests;
