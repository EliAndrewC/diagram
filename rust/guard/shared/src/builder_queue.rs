//! THE BUILDERS' QUEUE, AS A FILE CODE READS (feature 451 T313, with T395 and the first half of T297; the GM, 2026-11-26: "what you
//! are doing sounds like something that we want our tooling to actually enforce. Because otherwise you just have to remember to keep
//! our tasks in flight"). Measured 2026-11-27 (`dev/measurements/2026-11-27/tree-idle/results.md`): the three warm pool trees stood
//! idle 336 of 1,440 tree-minutes (23%) with the queue never short - the queue was prose (`queue.md`), so no code could name the
//! next task. Here: the file's one format ([`parse`]), each entry's state computed and never typed ([`states`]), the overlap of two
//! entries' files ([`overlap`], T297), the next entry to hand out ([`next`]) and the one rule the Stop guard asks ([`idle`]). The
//! gate lists and writes it (`rust/gate/crates/task/src/builder_queue.rs`: `make queue`, `make queue-add`, `make builder-next`,
//! `make builder-done`'s last block); the guard reads it (`rust/guard/src/guards/pool_idle_hooks.rs`).
//!
//! THE FILE is `specs/<feature>/queue.txt`, ONE ENTRY A LINE IN THE ORDER TO HAND OUT, a `#` line a comment:
//!
//! ```text
//! <task[,task]> <kind> [jobs=<1-3>] [measures=<n>] [load=1] crates=<dir,dir|-> files=<path,prefix|-> [waits=<T<n>,GM,alone>] [note=<the rest of the line>]
//! ```
//!
//! WHY THIS FORM AND NOT TAB-SEPARATED COLUMNS OR A FENCED BLOCK OF `queue.md`: a tab is the hand edit's hazard - it cannot be seen,
//! an editor may write spaces for it, and a row of nine columns one cell short reads as another row. Here only the two words every
//! entry has are placed by position (what `make builder-brief` takes as `T=` and `KIND=`); every other field is named, in any order,
//! split on any whitespace, so a missing or misspelled field is refused by its name and line. A file of its own, because a fence in
//! prose can be broken by an edit of the prose, and the prose queue went stale beside its own entries (2026-11-26, 20:10 UTC).
//!
//! AN ENTRY IS ONE DISPATCH, and READY means `make builder-brief` will take it. Its state, the first that holds:
//!
//! 1. `landed` - each of its tasks' boxes is ticked in the clone's `tasks.md` or archived in its `tasks-done.md`;
//! 2. `built` - a `done` line of the pool's log (`make builder-done`) NAMES this entry or a later one of its tasks (`"entry": k`,
//!    the entry's ordinal among its first task's lines, which `make builder-next` prints as `ENTRY=k` and `make builder-brief` logs
//!    beside the take; 451 T313's review, round 1): so two runs for one entry end it once, and a kept tree's one run ends the halves
//!    through the one it names. A done line naming none (written before this, or a tree briefed without `ENTRY=`) counts, as it
//!    did: each task's first entry is ended by its first such line, its second by its second. So a line STAYS IN THE FILE UNTIL ITS
//!    TASK IS LANDED - removing a line renames the entries after it - and a task that needs another builder gets another line;
//! 3. `waiting` on an earlier entry of one of its tasks that is not yet built (a closing half behind its build half);
//! 4. `in flight` - a pool tree is held for one of its tasks;
//! 5. `waiting` on a task its `waits=` names that is neither ticked nor carried, or on the GM (`waits=GM`, ended by editing the
//!    word out) - never on the carry of a done commit of one of its own tasks: `make builder-tree` applies that commit onto the
//!    handout uncommitted and the entry's done supersedes its ref (461 T09, T48; 451 T398 made it wait);
//! 6. `READY`.
//!
//! "Carried" is read from the refs alone: a task's done commit waits while `refs/l7r/done/<feature>-<task>` stands, which `make
//! carry` deletes at its verified end. A carry finished by hand leaves the ref until the next `make builder-done` clears it, so
//! such an entry waits a little longer than `make builder-trees` says it must - the safe side.
//!
//! THE OVERLAP RULE (T297): two entries overlap where a crate or a path of one is a crate or a path of the other, or lies under it
//! by whole path components (`rust/guard` holds `rust/guard/src/lib.rs`, not `rust/guardian`). An entry with no crates and no files
//! (a measurement) overlaps nothing. The next entry is, among the READY ones that overlap no entry in flight, an open performance
//! task's first (FR-013 under SC-006: its `[perf]` tag or its `PERF=1` checklist, [`perf_of`]), then the queue's order; `waits=alone` is
//! skipped while any pool tree is held, and while an `alone` entry is in flight nothing else is offered. A held tree whose task
//! the queue does not list has files nobody wrote down: it is named (`unchecked`) and holds nothing back.
//!
//! FIRST OF ALL (451 T313's round-3 ruling, T421): an open performance task of an active feature that no queue line names
//! ([`unlisted`]) is named before any entry, with the `make queue-add` that writes its line, and across queues [`offer`] takes a READY
//! performance entry of any queue before the preferred queue's pick - the Stop guard's rule and `make builder-done`'s step 1 alike.
// GUARD_EDIT_OK: feature 451 T313 - a new operation, the builders' queue, which the gate lists and the pool-idle guard reads

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::builder_pool::Tree;

// GUARD_EDIT_OK: feature 461 T16 - the lane's repair entries, offered before the queue's (D7)
pub mod repairs;
// GUARD_EDIT_OK: feature 461 T81 - the scheduling policy record and its one reader (FR-011)
pub mod policy;

/// The queue's file, in a feature's directory.
pub const FILE: &str = "queue.txt";
/// The pool's log, in the git common directory, where `make builder-done` writes a `done` line.
pub const LOG: &str = "builder-pool.log";
/// Where a done commit is kept until it is carried: `refs/l7r/done/<feature>-<task>`.
pub const DONE_REFS: &str = "refs/l7r/done/";
/// The settled count of builders at once, which the pool is kept at unless `L7R_BUILDERS` says otherwise. GUESS, a knob, an interim
/// 4 (2026-11-28): the four trees the session ran all of 2026-11-27 and 28 by `L7R_BUILDERS=4`, which fit (the night's sampler, 02:00Z
/// to 15:00Z: memory peak 59% of 10 GiB at four against 31% at three, no OOM, CPU stall 1.04 s a sample against 0.69 s) - a reading of
/// resources only, not of throughput, which integration bounded that night; 461 T35 measures 3, 4 and 5 through the lane over like
/// windows and sets it (the GM, 2026-11-27: "do those measurements and then settle on something for now"). Was 3, the warm trees run
/// by hand on 2026-11-26 (451 T313).
pub const BUILDERS: usize = 4;
/// A builder's kinds, as `make builder-brief` takes them.
pub const KINDS: [&str; 4] = ["fix", "measurement", "build-half", "closing-half"];
const SHAPE: &str = "<task[,task]> <kind> [jobs=<1-3>] [measures=<n>] [load=1] crates=<dir,dir|-> files=<path,prefix|-> [waits=<T<n>,GM,alone>] [note=<the rest of the line>]";
const EMPTY: &str = "the queue is empty: each entry is landed, built or in flight";

/// One entry: a dispatch of `tasks` as `kind`.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Entry {
    /// Its line in the file, from 1.
    pub line: usize,
    pub tasks: Vec<String>,
    pub kind: String,
    /// `JOBS=`, `MEASURES=` and `LOAD=1` of its brief; empty and false where the line names none.
    pub jobs: String,
    pub measures: String,
    pub load: bool,
    /// The crate directories and the files or path prefixes it is expected to change, no trailing slash.
    pub crates: Vec<String>,
    pub files: Vec<String>,
    /// The tasks that must be landed or carried first.
    pub waits: Vec<String>,
    /// It waits on a decision of the GM's.
    pub gm: bool,
    /// It runs with no other task in flight.
    pub alone: bool,
    pub note: String,
    /// ITS NAME AMONG ITS FIRST TASK'S LINES, from 1 (451 T313's review, round 1): `make builder-brief ENTRY=` records it and
    /// `make builder-done` writes it on its `done` line, so an entry is built when a done line names it. Stable while lines stay
    /// until their task lands; a bundle is named by its first task, as `make builder-done`'s `T=` names it first.
    pub ordinal: usize,
}

fn is_task(word: &str) -> bool {
    word.strip_prefix('T')
        .is_some_and(|d| !d.is_empty() && d.chars().all(|c| c.is_ascii_digit()))
}

/// A field's comma-separated list, `-` and nothing both none, a path's trailing slash dropped.
fn list(value: &str) -> Vec<String> {
    value
        .split(',')
        .map(|p| p.trim_end_matches('/'))
        .filter(|p| !p.is_empty() && *p != "-")
        .map(str::to_owned)
        .collect()
}

fn or_none(items: &[String]) -> String {
    if items.is_empty() {
        "-".to_owned()
    } else {
        items.join(",")
    }
}

impl Entry {
    /// Its tasks as a command names them: `T313`, a bundle `T313,T395`.
    #[must_use]
    pub fn name(&self) -> String {
        self.tasks.join(",")
    }

    /// The entry as its line of the file.
    #[must_use]
    pub fn text(&self) -> String {
        let mut out = format!("{} {}", self.name(), self.kind);
        for (key, value) in [("jobs", &self.jobs), ("measures", &self.measures)] {
            if !value.is_empty() {
                let _ = write!(out, " {key}={value}");
            }
        }
        if self.load {
            out.push_str(" load=1");
        }
        let _ = write!(
            out,
            " crates={} files={}",
            or_none(&self.crates),
            or_none(&self.files)
        );
        let mut waits = self.waits.clone();
        waits.extend(self.gm.then(|| "GM".to_owned()));
        waits.extend(self.alone.then(|| "alone".to_owned()));
        if !waits.is_empty() {
            let _ = write!(out, " waits={}", waits.join(","));
        }
        if !self.note.is_empty() {
            let _ = write!(out, " note={}", self.note);
        }
        out
    }

    /// The command that hands it out, for the feature keyed `key`.
    #[must_use]
    pub fn command(&self, key: &str) -> String {
        let mut out = format!(
            "make builder-brief T={} F={key} KIND={}",
            self.name(),
            self.kind
        );
        for (name, value) in [("JOBS", &self.jobs), ("MEASURES", &self.measures)] {
            if !value.is_empty() {
                let _ = write!(out, " {name}={value}");
            }
        }
        if !self.crates.is_empty() {
            let _ = write!(out, " CRATE=\"{}\"", self.crates.join(" "));
        }
        if self.load {
            out.push_str(" LOAD=1");
        }
        let _ = write!(out, " ENTRY={}", self.ordinal);
        out
    }

    fn paths(&self) -> impl Iterator<Item = &String> {
        self.crates.iter().chain(&self.files)
    }
}

/// One line as an entry, or why it is none.
fn entry(line: usize, raw: &str) -> Result<Entry, String> {
    let flat = raw.replace('\t', " ");
    let (head, note) = flat.split_once(" note=").unwrap_or((&flat, ""));
    let words: Vec<&str> = head.split_whitespace().collect();
    if words.len() < 3 {
        return Err(format!(
            "{} field(s) found, at least 3 expected ({SHAPE})",
            words.len()
        ));
    }
    let tasks = list(words[0]);
    if tasks.is_empty() || !tasks.iter().all(|t| is_task(t)) {
        return Err(format!(
            "`{}` is no task or bundle (T<n>, or T<n>,T<m>)",
            words[0]
        ));
    }
    if !KINDS.contains(&words[1]) {
        return Err(format!("`{}` is no kind ({})", words[1], KINDS.join(", ")));
    }
    let mut e = Entry {
        line,
        tasks,
        kind: words[1].to_owned(),
        note: note.trim().to_owned(),
        ..Entry::default()
    };
    let mut seen = BTreeSet::new();
    for word in &words[2..] {
        let Some((key, value)) = word.split_once('=') else {
            return Err(format!("`{word}` is no key=value field ({SHAPE})"));
        };
        if !seen.insert(key) {
            return Err(format!("`{key}=` is given twice"));
        }
        let waits = list(value);
        match key {
            "jobs" if matches!(value, "1" | "2" | "3") => value.clone_into(&mut e.jobs),
            "measures" if value.parse::<usize>().is_ok() => value.clone_into(&mut e.measures),
            "load" if value == "1" => e.load = true,
            "crates" => e.crates = waits,
            "files" => e.files = waits,
            "waits"
                if waits
                    .iter()
                    .all(|t| is_task(t) || t == "GM" || t == "alone") =>
            {
                e.gm = waits.iter().any(|t| t == "GM");
                e.alone = waits.iter().any(|t| t == "alone");
                e.waits = waits.into_iter().filter(|t| is_task(t)).collect();
            }
            _ => return Err(format!("`{word}` is no field of an entry ({SHAPE})")),
        }
    }
    if !seen.contains("crates") && !seen.contains("files") {
        return Err("it names neither crates= nor files= (`-` says none)".to_owned());
    }
    if e.kind == "measurement" && e.measures.is_empty() {
        return Err("a measurement names measures=<the things measured>, which make builder-brief sizes it by".to_owned());
    }
    Ok(e)
}

/// The queue's entries in order.
///
/// # Errors
/// Every malformed line, one line each: `queue.txt line <n>: <why>: <the line>`.
pub fn parse(text: &str) -> Result<Vec<Entry>, String> {
    let (mut entries, mut errors) = (Vec::new(), Vec::new());
    for (i, raw) in text.lines().enumerate() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        match entry(i + 1, line) {
            Ok(mut e) => {
                let first = &e.tasks[0];
                e.ordinal = 1 + entries
                    .iter()
                    .filter(|o: &&Entry| o.tasks.contains(first))
                    .count();
                entries.push(e);
            }
            Err(why) => errors.push(format!("{FILE} line {}: {why}: {line}", i + 1)),
        }
    }
    if errors.is_empty() {
        Ok(entries)
    } else {
        Err(errors.join("\n"))
    }
}

/// The path two entries share (the module's overlap rule), the shorter of the pair; none where they share none.
#[must_use]
pub fn overlap(a: &Entry, b: &Entry) -> Option<String> {
    let under = |p: &str, q: &str| p == q || q.strip_prefix(p).is_some_and(|r| r.starts_with('/'));
    a.paths().find_map(|p| {
        let q = b.paths().find(|q| under(p, q) || under(q, p))?;
        Some(if q.len() < p.len() { q } else { p }.clone())
    })
}

/// An entry's state (the module's doc).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum State {
    Landed,
    /// Its done commit is made; the words say whether the carry or the landing is owed.
    Built(String),
    /// The pool tree held for it.
    InFlight(PathBuf),
    /// What it waits on.
    Waiting(String),
    Ready,
}

/// What the states are computed from, for the feature keyed `key`.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Facts {
    pub key: String,
    /// The tasks whose boxes are ticked.
    pub ticked: BTreeSet<String>,
    /// Every held tree of the clone's pool, whatever feature holds it.
    pub held: Vec<Tree>,
    /// The done lines of the pool's log that name no entry (written before entries were named), counted for each task.
    pub dones: BTreeMap<String, usize>,
    /// The done lines that name an entry: their tasks, as `make builder-done`'s `T=` named them, and the entry's ordinal.
    pub named: Vec<(Vec<String>, usize)>,
    /// The tasks with a done commit not yet carried.
    pub uncarried: BTreeSet<String>,
    /// Each open box of `tasks.md`: its id and the rest of its line.
    pub open: BTreeMap<String, String>,
    /// The open tasks of READY entries that are performance work (FR-013), filled by [`board`] before [`next`].
    pub perf: BTreeSet<String>,
}

/// HOW FAR EACH TASK'S ENTRIES ARE ENDED (451 T313's review, round 1, the T416 case): a done line naming its entry ends that
/// entry and every earlier entry of its tasks - the entry's ordinal among each task's lines, the larger of that and the count -
/// so two runs for one entry end it once, and a kept tree's one run ends the halves through the one it names. A done line naming
/// none, or an entry the queue no longer holds, counts one entry, as before. The larger, not the sum: a successor briefed with no
/// `ENTRY=` after one that named it ends no further entry, so the queue offers an entry again (seen) rather than skip one (unseen).
fn through(entries: &[Entry], f: &Facts) -> BTreeMap<String, usize> {
    let mut count = f.dones.clone();
    let mut named: BTreeMap<String, usize> = BTreeMap::new();
    for (tasks, k) in &f.named {
        let first = &tasks[0];
        let found = entries
            .iter()
            .enumerate()
            .filter(|(_, e)| e.tasks.contains(first))
            .nth(k.saturating_sub(1));
        let Some((i, e)) = found else {
            for t in tasks {
                *count.entry(t.clone()).or_default() += 1;
            }
            continue;
        };
        for t in &e.tasks {
            let ord = entries[..=i].iter().filter(|o| o.tasks.contains(t)).count();
            let at = named.entry(t.clone()).or_default();
            *at = (*at).max(ord);
        }
    }
    for (t, k) in named {
        let at = count.entry(t).or_default();
        *at = (*at).max(k);
    }
    count
}

fn state(
    e: &Entry,
    f: &Facts,
    ended: &BTreeMap<String, usize>,
    seen: &BTreeMap<&str, usize>,
    open: &BTreeMap<&str, usize>,
) -> State {
    let done = |t: &String| ended.get(t).copied().unwrap_or(0);
    if e.tasks.iter().all(|t| f.ticked.contains(t)) {
        return State::Landed;
    }
    let owed = e.tasks.iter().find(|t| f.uncarried.contains(*t));
    if e.tasks.iter().all(|t| done(t) >= seen[t.as_str()]) {
        return State::Built(owed.map_or_else(
            || "carried, its landing owed".to_owned(),
            |t| format!("the carry of {t}'s done commit owed"),
        ));
    }
    let earlier = e
        .tasks
        .iter()
        .find_map(|t| Some((t, open.get(t.as_str())?)));
    if let Some((t, line)) = earlier {
        return State::Waiting(format!("{t}'s earlier entry, line {line}"));
    }
    let holds = |h: &&Tree| h.feature == f.key && h.tasks.iter().any(|t| e.tasks.contains(t));
    if let Some(tree) = f.held.iter().find(holds) {
        return State::InFlight(tree.tree.clone());
    }
    // its own tasks' uncarried done commits hold it no longer: its handout builds on them (461 T09, T48); a `waits=` task's do
    let waits = |t: &&String| !f.ticked.contains(*t) && (done(t) == 0 || f.uncarried.contains(*t));
    let mut on: Vec<String> = e.waits.iter().filter(waits).cloned().collect();
    on.extend(e.gm.then(|| "the GM".to_owned()));
    if on.is_empty() {
        State::Ready
    } else {
        State::Waiting(on.join(", "))
    }
}

/// Each entry's state, in the queue's order.
#[must_use]
pub fn states(entries: &[Entry], f: &Facts) -> Vec<State> {
    // how many entries so far name a task, and the line of a task's earlier entry that is not yet built
    let mut seen: BTreeMap<&str, usize> = BTreeMap::new();
    let mut open: BTreeMap<&str, usize> = BTreeMap::new();
    let ended = through(entries, f);
    let mut out = Vec::new();
    for e in entries {
        for t in &e.tasks {
            *seen.entry(t).or_default() += 1;
        }
        let state = state(e, f, &ended, &seen, &open);
        if !matches!(state, State::Landed | State::Built(_)) {
            for t in &e.tasks {
                open.entry(t).or_insert(e.line);
            }
        }
        out.push(state);
    }
    out
}

/// The entry to hand out next.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Next {
    /// The READY entry that overlaps nothing in flight, an open performance task's first (FR-013), by its index.
    pub pick: Option<usize>,
    /// Each READY entry passed over before it, with why.
    pub skipped: Vec<(usize, String)>,
    /// The holders of the trees held for a task the queue does not list: their files are unknown, and they hold nothing back.
    pub unchecked: Vec<String>,
    /// Why there is no pick; empty where there is one.
    pub none: String,
    /// The pick is an open performance task's entry (FR-013).
    pub perf: bool,
    // GUARD_EDIT_OK: feature 461 T81 - every READY entry free to hand out, which the policy's reader ranks (FR-011)
    /// Every READY entry that overlaps nothing in flight (`alone` kept), in the queue's order: what [`policy::ranked`] ranks.
    pub free: Vec<usize>,
}

/// The next entry of `entries`, whose states are `states` (the module's overlap rule).
#[must_use]
pub fn next(entries: &[Entry], states: &[State], f: &Facts) -> Next {
    let flying: Vec<&Entry> = entries
        .iter()
        .zip(states)
        .filter(|(_, s)| matches!(s, State::InFlight(_)))
        .map(|(e, _)| e)
        .collect();
    let listed = |h: &&Tree| {
        let names = |e: &&Entry| h.tasks.iter().any(|t| e.tasks.contains(t));
        h.feature == f.key && flying.iter().any(names)
    };
    let unchecked = f
        .held
        .iter()
        .filter(|h| !listed(h))
        .map(Tree::holder)
        .collect();
    let lone = flying.iter().find(|e| e.alone);
    let (mut free, mut skipped) = (Vec::new(), Vec::new());
    for (i, e) in entries.iter().enumerate() {
        if states[i] != State::Ready {
            continue;
        }
        let why = if let Some(l) = lone {
            Some(format!("{} runs alone", l.name()))
        } else if e.alone && !f.held.is_empty() {
            Some(format!(
                "it runs alone, and {} tree(s) are held",
                f.held.len()
            ))
        } else {
            let clash = |o: &&Entry| {
                Some(format!(
                    "it overlaps {} in flight at {}",
                    o.name(),
                    overlap(e, o)?
                ))
            };
            flying.iter().find_map(clash)
        };
        match why {
            Some(w) => skipped.push((i, w)),
            None => free.push(i),
        }
    }
    // FR-013 under SC-006 (the GM 2026-11-20): an open performance task's entry first, then the queue's order - the GM's of
    // 2026-11-26 within each class
    let is_perf = |i: &&usize| entries[**i].tasks.iter().any(|t| f.perf.contains(t));
    let perf = free.iter().find(is_perf).copied();
    let pick = perf.or_else(|| free.first().copied());
    if let Some(p) = perf {
        let e = &entries[p];
        let why = format!(
            "{} (line {}) is performance work, offered first (FR-013)",
            e.name(),
            e.line
        );
        skipped.extend(
            free.iter()
                .take_while(|i| **i != p)
                .map(|i| (*i, why.clone())),
        );
        skipped.sort_by_key(|(i, _)| *i);
    }
    // what follows the pick is never passed over: it is only later in the queue
    skipped.retain(|(i, _)| pick.is_none_or(|p| *i < p));
    let waiting: Vec<String> = entries
        .iter()
        .zip(states)
        .filter_map(|(e, s)| match s {
            State::Waiting(on) => Some(format!("{} on {on}", e.name())),
            _ => None,
        })
        .collect();
    let none = if pick.is_some() {
        String::new()
    } else if !skipped.is_empty() {
        "every READY entry is held back by a task in flight".to_owned()
    } else if waiting.is_empty() {
        EMPTY.to_owned()
    } else {
        format!("every open entry waits: {}", waiting.join("; "))
    };
    Next {
        pick,
        perf: perf.is_some(),
        skipped,
        unchecked,
        none,
        free, // GUARD_EDIT_OK: feature 461 T81 - the free list the policy's reader ranks
    }
}

/// A feature directory's key: the number its name opens with.
fn key_of(dir: &Path) -> String {
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    name.chars().take_while(char::is_ascii_digit).collect()
}

/// The facts of the feature at `dir` in `clone`, whose git common directory is `common` and whose pool is `trees`.
#[must_use]
pub fn facts(clone: &Path, common: &Path, dir: &Path, trees: &[Tree]) -> Facts {
    let key = key_of(dir);
    // a ticked box is in `tasks.md` until the tick archives it to `tasks-done.md` (449 T142), where nearly every landed task is
    let read = |name: &str| std::fs::read_to_string(dir.join(name)).unwrap_or_default();
    let tasks =
        read("tasks.md") + "\n" + &crate::speckit::tasks::done_text(dir).unwrap_or_default();
    let ticked = tasks
        .lines()
        .map(str::trim_start)
        .filter_map(|l| {
            l.strip_prefix("- [x] ")
                .or_else(|| l.strip_prefix("- [X] "))
        })
        .filter_map(|l| l.split_whitespace().next())
        .map(str::to_owned)
        .collect();
    let open = read("tasks.md")
        .lines()
        .filter_map(|l| l.trim_start().strip_prefix("- [ ] "))
        .filter_map(|l| {
            let (id, rest) = l.split_once(' ').unwrap_or((l, ""));
            is_task(id).then(|| (id.to_owned(), rest.to_owned()))
        })
        .collect();
    let (mut dones, mut named): (BTreeMap<String, usize>, Vec<_>) = (BTreeMap::new(), Vec::new());
    let log = std::fs::read_to_string(common.join(LOG)).unwrap_or_default();
    for row in log
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
    {
        let detail = row["detail"].as_str().unwrap_or_default();
        let (feature, ids) = detail.split_once(' ').unwrap_or_default();
        let tasks = list(ids);
        if row["event"] != "done" || feature != key || tasks.is_empty() {
            continue;
        }
        let entry = row["entry"].as_u64().and_then(|k| usize::try_from(k).ok());
        match entry.filter(|k| *k > 0) {
            Some(k) => named.push((tasks, k)),
            None => {
                for t in tasks {
                    *dones.entry(t).or_default() += 1;
                }
            }
        }
    }
    let refs = std::process::Command::new("git")
        .arg("-C")
        .arg(clone)
        .args(["for-each-ref", "--format=%(refname)", DONE_REFS])
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default();
    let ours = format!("{DONE_REFS}{key}-");
    let uncarried = refs
        .lines()
        .filter_map(|r| r.strip_prefix(&ours))
        .map(str::to_owned)
        .collect();
    Facts {
        key,
        ticked,
        held: trees.iter().filter(|t| !t.free()).cloned().collect(),
        dones,
        named,
        uncarried,
        open,
        perf: BTreeSet::new(),
    }
}

/// THE OPEN PERFORMANCE TASKS OF THE READY ENTRIES (FR-013): a task whose open box carries the `[perf]` tag after its id, or whose
/// plan section opens with the checklist `make task-add PERF=1` writes - `set_down_hooks::performance`, the one test `make
/// task-start` and the Stop hook's next task already ask. FR-013's measurement clause (work that measures where the time goes)
/// is read through that tag, which such tasks carry (T08-T11, T22, T53), never from an entry's kind: a `measurement` entry may
/// measure a correctness question. Asked of READY entries only, the plan read once, so a Stop pays for no other box.
fn perf_of(dir: &Path, entries: &[Entry], states: &[State], f: &Facts) -> BTreeSet<String> {
    let ready = entries
        .iter()
        .zip(states)
        .filter(|(_, s)| **s == State::Ready);
    let tasks: BTreeSet<&String> = ready.flat_map(|(e, _)| &e.tasks).collect();
    let mut plan = None;
    let mut out = BTreeSet::new();
    for t in tasks {
        let Some(title) = f.open.get(t) else {
            continue;
        };
        let text = plan.get_or_insert_with(|| {
            std::fs::read_to_string(dir.join("plan.md")).unwrap_or_default()
        });
        if crate::guards::set_down_hooks::performance(t, title, text) {
            out.insert(t.clone());
        }
    }
    out
}

/// The feature directories of `clone` that hold a queue, in name order.
#[must_use]
pub fn queues(clone: &Path) -> Vec<PathBuf> {
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(clone.join("specs"))
        .map(|d| d.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default();
    dirs.retain(|d| d.join(FILE).is_file());
    dirs.sort();
    dirs
}

/// A feature's queue as it stands: its entries, each one's state, the facts they were computed from and the next entry.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Board {
    pub key: String,
    pub entries: Vec<Entry>,
    pub states: Vec<State>,
    pub facts: Facts,
    pub next: Next,
}

/// The queue of the feature at `dir`, read and computed.
///
/// # Errors
/// The file cannot be read, or holds a malformed line ([`parse`]'s error, each line under the file's path).
pub fn board(clone: &Path, common: &Path, dir: &Path, trees: &[Tree]) -> Result<Board, String> {
    let path = dir.join(FILE);
    let at = path
        .strip_prefix(clone)
        .unwrap_or(&path)
        .display()
        .to_string();
    let text = std::fs::read_to_string(&path).map_err(|e| format!("{at}: {e}"))?;
    let entries =
        parse(&text).map_err(|e| e.replace(&format!("{FILE} line "), &format!("{at} line ")))?;
    let mut facts = facts(clone, common, dir, trees);
    let states = states(&entries, &facts);
    facts.perf = perf_of(dir, &entries, &states, &facts);
    let next = next(&entries, &states, &facts);
    Ok(Board {
        key: facts.key.clone(),
        entries,
        states,
        facts,
        next,
    })
}

/// AN OPEN PERFORMANCE TASK NO QUEUE LINE NAMES (451 T313's round-3 ruling, `ask:451-T313-plan-round3`; built here as T421): named
/// FIRST by the Stop block, `make builder-done`'s step 1, `make builder-next` and `make queue`, with the command that writes its line,
/// rather than a non-performance entry offered silently - an entry needs its crates and files, which only its author can write, so the
/// tooling names the line owed instead of guessing one.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Unlisted {
    /// The task as a reader names it: `451 T341`.
    pub tasks: String,
    /// The kind its line is written with: `build-half` where [`crate::builder_brief::mechanism`] reads a new command or guard in its
    /// task line - the test by which `make builder-brief` refuses `KIND=fix` - and `fix` otherwise; the author changes it where the
    /// line is a measurement.
    pub kind: String,
    /// `make queue-add F=<key> T=<task> KIND=<kind>`, which runs as printed (crates=- files=-); CRATE=, FILES= and WAITS= are added
    /// where the task line names them, and a line with `waits=` is what quiets a task that waits.
    pub command: String,
}

/// The tasks some line of the queue at `dir` names, any state; none where it holds no file, and `None` where its file cannot be
/// parsed (another feature's file of that name - a page session's - says nothing of the tasks it lists, so its tasks are not named).
fn listed_in(dir: &Path) -> Option<BTreeSet<String>> {
    let Ok(text) = std::fs::read_to_string(dir.join(FILE)) else {
        return Some(BTreeSet::new());
    };
    let entries = parse(&text).ok()?;
    Some(entries.into_iter().flat_map(|e| e.tasks).collect())
}

/// Every open performance task of every active feature ([`crate::guards::set_down_hooks::open_performance`], FR-013's own test and
/// walk, the feature keyed `prefer` first) that no line of its feature's queue names. A log that cannot be read names none: the
/// Stop guard is never held on it.
#[must_use]
pub fn unlisted(clone: &Path, common: &Path, prefer: &str) -> Vec<Unlisted> {
    let specs = clone.join("specs");
    let mut dirs: Vec<String> = std::fs::read_dir(&specs)
        .map(|d| {
            d.filter_map(Result::ok)
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        })
        .unwrap_or_default();
    dirs.sort();
    let first = dirs
        .into_iter()
        .find(|d| !prefer.is_empty() && key_of(Path::new(d)) == prefer);
    let open =
        crate::guards::set_down_hooks::open_performance(clone, common, &first.unwrap_or_default());
    let known = crate::builder_brief::targets(
        &std::fs::read_to_string(clone.join("Makefile")).unwrap_or_default(),
    );
    let mut lines: BTreeMap<String, Option<BTreeSet<String>>> = BTreeMap::new();
    let mut out = Vec::new();
    for t in open.unwrap_or_default() {
        let listed = lines
            .entry(t.feature.clone())
            .or_insert_with(|| listed_in(&specs.join(&t.feature)));
        if listed.as_ref().is_none_or(|l| l.contains(&t.id)) {
            continue;
        }
        let key = key_of(Path::new(&t.feature));
        let line = format!("- [ ] {} {}", t.id, t.title);
        let kind = if crate::builder_brief::mechanism(&line, &known).is_some() {
            "build-half"
        } else {
            "fix"
        };
        out.push(Unlisted {
            tasks: format!("{key} {}", t.id),
            kind: kind.to_owned(),
            command: format!("make queue-add F={key} T={} KIND={kind}", t.id),
        });
    }
    out
}

/// THE ENTRY TO OFFER ACROSS THE CLONE'S QUEUES (FR-013, "in any active feature"; 451 T313's round-3 ruling): a READY performance
/// entry of any queue first ([`Next::perf`]), then the pick of the queue keyed `prefer`, then the first queue's - `idle`'s rule, which
/// `make builder-done`'s step 1 now takes too. The board and the entry's index; none where no queue has an entry to hand out.
#[must_use]
pub fn offer<'a>(boards: &'a [Board], prefer: &str) -> Option<(&'a Board, usize)> {
    let first = |keep: &dyn Fn(&Board) -> bool| {
        boards
            .iter()
            .filter(|b| keep(b))
            .find_map(|b| Some((b, b.next.pick?)))
    };
    first(&|b| b.next.perf)
        .or_else(|| first(&|b| b.key == prefer))
        .or_else(|| first(&|_| true))
}

/// THE FLAG ON A FIX ENTRY ITS BRIEF WOULD REFUSE (451 T412): `make builder-brief` refuses `KIND=fix` for a task whose line names a
/// new mechanism, so such an entry read READY and the commands named a brief that is refused (T302 and T296, found by hand). Each
/// of `e`'s tasks' lines (`line_of`: its open box, whole) is asked the brief's own test, [`crate::builder_brief::mechanism`], and
/// the first that names one is said, `pad` before each line: what the test read, the `KIND=build-half` command for the feature keyed
/// `key`, and the route a misread line takes. Nothing for another kind, or where no line names one. Here, not in the gate, so the
/// pool-idle Stop block says the same flag under the command it names (451 T481).
///
/// WHY A NOTICE AND NEVER A SKIP: the test misfires (it took T437, T412 and T431 on 2026-11-27 for a quoted refusal phrase and a
/// `make -C`; 451 T431 mends the `make -` half). A flag that hid or retyped the entry would hold back a task the brief takes with
/// `SIZING_OK=`; this one leaves the state and the pick alone and quotes what it read, so a misread is told at a glance and costs a
/// line, and a true one names the command that runs. It goes quiet for a misread when T431's fix lands, since it asks the one test.
#[must_use]
pub fn flag(
    e: &Entry,
    key: &str,
    line_of: &dyn Fn(&String) -> Option<String>,
    known: &BTreeSet<String>,
    pad: &str,
) -> String {
    let read = |t: &String| {
        Some((
            t.clone(),
            crate::builder_brief::mechanism(&line_of(t)?, known)?,
        ))
    };
    let Some((t, what)) = e.tasks.iter().find_map(read).filter(|_| e.kind == "fix") else {
        return String::new();
    };
    let half = Entry {
        kind: "build-half".to_owned(),
        ..e.clone()
    };
    format!("{pad}FLAG: {} (line {}) is typed fix, but {t}'s line names a new mechanism ({what}), which make builder-brief refuses KIND=fix for: retype the line build-half and add its closing-half line after it, then\n{pad}  {}\n{pad}  or, where the test misreads the line (a quoted refusal phrase, `make -C`), the fix command as printed with SIZING_OK=\"<reason>\"\n", e.name(), e.line, half.command(key))
}

/// [`flag`] for entry `i` of `b`, read from its open boxes; only an entry not yet in flight, built or landed is flagged.
#[must_use]
pub fn flagged(b: &Board, i: usize, known: &BTreeSet<String>, pad: &str) -> String {
    let line_of = |t: &String| Some(format!("- [ ] {t} {}", b.facts.open.get(t)?));
    let open = matches!(b.states[i], State::Ready | State::Waiting(_));
    if open {
        flag(&b.entries[i], &b.key, &line_of, known, pad)
    } else {
        String::new()
    }
}

/// The settled builder count: `L7R_BUILDERS`, else [`BUILDERS`].
#[must_use]
pub fn builders() -> usize {
    crate::env::var("L7R_BUILDERS").parse().unwrap_or(BUILDERS)
}

/// A pool tree standing idle: the free tree, the entry that would fill it and its command (both empty where no queue has one), and
/// the open performance tasks no queue line names, which the block names first (451 T313's round 3).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Idle {
    pub tree: PathBuf,
    /// The entry as a reader names it: `451 T313`.
    pub tasks: String,
    pub command: String,
    /// [`flagged`]'s lines under the command, two spaces before each: the command is a fix `make builder-brief` refuses (451 T481);
    /// empty where it is not.
    pub flag: String,
    pub unlisted: Vec<Unlisted>,
}

/// What [`idle`] finds.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Verdict {
    Quiet,
    /// A queue that cannot be read: said, never held.
    Unread(String),
    Idle(Idle),
}

/// THE RULE THE STOP GUARD ASKS, whole: in the pool of the clone at `clone` a tree stands free (and on disk), fewer than `builders`
/// trees are held, and a queue of the clone holds a next entry ([`next`]: READY, overlapping nothing in flight, `alone` kept). "No
/// handout followed the tree's release" is the state itself: a handout of that entry would make it `in flight`, and one of any
/// other raises the held count. A free tree belongs to no feature, so it is judged against every queue the clone holds, in
/// directory order. A clone with no pool has no free tree: quiet. A `queue.txt` that cannot be read hides no other: another
/// feature may hold a file of that name in another form (a page session's, as features 269 and 280 do), so the walk goes on
/// past it, and the first unread one is the verdict only where no queue has an entry to hand out.
#[must_use]
pub fn idle(clone: &Path, builders: usize) -> Verdict {
    let common = clone.join(".git");
    let trees = crate::builder_pool::read(&common);
    let held = trees.iter().filter(|t| !t.free()).count();
    let Some(free) = trees.iter().find(|t| t.free() && t.tree.is_dir()) else {
        return Verdict::Quiet;
    };
    if held >= builders {
        return Verdict::Quiet;
    }
    // GUARD_EDIT_OK: feature 451 T313 - a queue.txt that cannot be read (features 269 and 280 hold a page session's file of that
    // name) no longer hides a readable queue behind it: the first unread one is said only when no queue has an entry to hand out
    // and an open performance task's entry of any queue is named before another queue's first pick (FR-013, "in any active feature")
    // GUARD_EDIT_OK: feature 451 T313's round-3 ruling - an open performance task no queue line names is named first, with its
    // make queue-add command, by the one walk builder-done and builder-next share ([`unlisted`], [`offer`])
    let (mut unread, mut boards) = (None, Vec::new());
    for dir in queues(clone) {
        match board(clone, &common, &dir, &trees) {
            Err(why) => {
                unread.get_or_insert(why);
            }
            Ok(b) => boards.push(b),
        }
    }
    let unlisted = unlisted(clone, &common, "");
    // GUARD_EDIT_OK: feature 451 T481 - the entry's fix flag, as make queue and make builder-next say it, so the block never names a
    // command make builder-brief refuses without saying so
    let known = crate::builder_brief::targets(
        &std::fs::read_to_string(clone.join("Makefile")).unwrap_or_default(),
    );
    let queued = offer(&boards, "").map(|(b, i)| {
        (
            format!("{} {}", b.key, b.entries[i].name()),
            b.entries[i].command(&b.key),
            flagged(b, i, &known, "  "),
        )
    });
    // GUARD_EDIT_OK: feature 461 T16 - an open repair entry of the lane is offered before the queue's pick (D7, LANE_REPAIR_FIRST)
    let held: Vec<Tree> = trees.iter().filter(|t| !t.free()).cloned().collect();
    let repair = repairs::offer(&common, &held)
        .ready
        .into_iter()
        .next()
        .map(|r| {
            (
                format!("{}, a FRESH builder", r.name()),
                r.command(),
                String::new(),
            )
        });
    let pick = if repairs::first() {
        repair.or(queued)
    } else {
        queued.or(repair)
    };
    if pick.is_none() && unlisted.is_empty() {
        return unread.map_or(Verdict::Quiet, Verdict::Unread);
    }
    let (tasks, command, flag) = pick.unwrap_or_default();
    Verdict::Idle(Idle {
        tree: free.tree.clone(),
        tasks,
        command,
        flag,
        unlisted,
    })
}

#[cfg(test)]
mod tests;
