//! THE BUILDERS' SCHEDULING POLICY AND ITS ONE READER (feature 461 T81, US6, FR-011; the GM, 2026-11-28: "our scheduler probably
//! needs some tool-based enforcement of these kinds of prioritizations so that you don't need to remember to do the correct thing in
//! the future"). The record is [`FILE`] at the clone's top, read by [`read`]; [`ranked`] ranks every piece of work a free builder
//! could take now - each queue's READY entries that overlap nothing in flight, the lane's open repairs, and the open tasks no queue
//! line names that a class or a feature's form puts forward - and every handout path asks it (461 T82 wires them).
//!
//! THE RECORD, one line each, a `#` line a comment; every line carries the GM's words after `note=`, dated, since only his words set
//! it (FR-011: "a change the GM directs changes the record"):
//!
//! ```text
//! class perf note=<his words>        performance work first, of any feature (451 FR-013's membership)
//! class bugfix note=<his words>      a process bugfix - a box tagged [bugfix] (make task-add BUGFIX=1), a defect's fix
//! <key> all note=<his words>         the feature gets every builder it can use; others get what is left
//! <key> floor <n> note=<his words>   the feature always holds <n>; past them it fills only uncontended trees
//! <key> share note=<his words>       the default form of every feature the record does not name
//! ```
//!
//! A record with no class line keeps the default's two (perf, then bugfix): a line giving one feature its form never silently
//! drops the standing performance-first rule. `class none note=<his words>`, alone among class lines, ranks no class.
//!
//! THE RANK, the first difference decides ([`Ranked::key`]):
//! 1. THE CLASS: a class line's work before any other, in the record's order of class lines - "priority over everything else
//!    regardless of what feature they are attached to" (2026-11-28), so a class outranks every feature form;
//! 2. THE FEATURE'S FORM: a floor not yet met (`floor <n>` holding fewer than `<n>` trees), then `all`, then `share`, then a floor met.
//!    A floor below `all` would let an `all` feature starve it, which the GM's "always gets 1 builder" rules out: the floor's guarantee
//!    ranks first, a DECISION of this task (the record is silent where both forms stand at once; the guarantee is the stronger word);
//! 3. THE CALLER'S OWN FEATURE (`prefer`: `make builder-done`'s and `make builder-next`'s tree, 451 T313), within one form;
//! 4. THE FEATURE'S NAME ORDER (the pool-idle guard's walk over `queues()`), within one form;
//! 5. WITHIN ONE FEATURE: its lane repair, then its queue's entries in their own order, then its unlisted tasks in `tasks.md`'s
//!    order. A repair ranks by its own task's class and feature (FR-011: "below the classes"), first within its feature because it
//!    is that feature's oldest built work; `LANE_REPAIR_FIRST` set no rank of the GM's and is not read here. A queue's own order
//!    (462 T549's `#! order=queue`) is this step and no more: it never puts an entry above a class, inside its feature or out.
//!
//! THE DEFAULT, where [`FILE`] is absent: `class perf`, then `class bugfix`, every feature `share` - the GM's standing rules
//! (performance first, 2026-11-20, 451 FR-013; process bugfixes with it, 2026-11-28). It ranks as the tooling did before it but in
//! three ways: the bugfix class; a repair no longer first of all (step 5); and a listed performance entry before an unlisted
//! performance task of its feature, where the Stop block named the unlisted one first. A malformed record reads as the default too, with its errors in [`Read::why`] for every reader
//! to say: a broken record never silently hands out by an order nobody wrote.
// GUARD_EDIT_OK: feature 461 T81 - a new operation, the scheduling policy record and the one reader that ranks the READY work by it

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use super::{Board, Unlisted, DONE_REFS};
use crate::builder_pool::Tree;

/// The record, relative to the clone's top.
pub const FILE: &str = "dev/builder-policy.txt";
/// The bugfix class's tag on a task's box, among the bracketed tags after its id (FR-011).
pub const BUGFIX_TAG: &str = "[bugfix]";

/// A class of task ranked before every feature's other work.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Class {
    Perf,
    Bugfix,
}

impl Class {
    fn word(self) -> &'static str {
        match self {
            Self::Perf => "perf",
            Self::Bugfix => "bugfix",
        }
    }
}

/// A feature's form.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Form {
    All,
    Floor(usize),
    Share,
}

/// The policy as read.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Policy {
    /// The class lines, in the record's order.
    pub classes: Vec<Class>,
    /// Each named feature's form, by its key.
    pub features: BTreeMap<String, Form>,
}

impl Default for Policy {
    fn default() -> Self {
        Self {
            classes: vec![Class::Perf, Class::Bugfix],
            features: BTreeMap::new(),
        }
    }
}

impl Policy {
    /// The form of the feature keyed `key`.
    #[must_use]
    pub fn form(&self, key: &str) -> Form {
        self.features.get(key).copied().unwrap_or(Form::Share)
    }
}

// GUARD_EDIT_OK: feature 461 T81 - a record with no class line keeps the default classes; `class none` drops them
/// One line as a class or a feature's form, or why it is neither; `classed` says a class line came before (`class none` one too).
fn line(p: &mut Policy, raw: &str, classed: &mut bool) -> Result<(), String> {
    let (head, note) = raw.split_once(" note=").unwrap_or((raw, ""));
    if note.trim().is_empty() {
        return Err(
            "it carries no note=<the GM's words, dated>: only his words set the policy".to_owned(),
        );
    }
    let words: Vec<&str> = head.split_whitespace().collect();
    match words[..] {
        ["class", c] => {
            let class = match c {
                "perf" => Some(Class::Perf),
                "bugfix" => Some(Class::Bugfix),
                "none" => None,
                _ => return Err(format!("`{c}` is no class (perf, bugfix, none)")),
            };
            if *classed && (class.is_none() || p.classes.is_empty()) {
                return Err("class none stands alone: no other class line beside it".to_owned());
            }
            if class.is_some_and(|k| p.classes.contains(&k)) {
                return Err(format!("class {c} is given twice"));
            }
            *classed = true;
            p.classes.extend(class);
        }
        [key, ref rest @ ..] if !key.is_empty() && key.chars().all(|c| c.is_ascii_digit()) => {
            let form = match rest {
                ["all"] => Form::All,
                ["share"] => Form::Share,
                ["floor", n] => Form::Floor(n.parse().ok().filter(|n| *n > 0).ok_or(format!(
                    "`floor {n}`: a floor is a count of builders, 1 or more"
                ))?),
                _ => {
                    return Err(format!(
                        "`{}` is no form (all, floor <n>, share)",
                        rest.join(" ")
                    ))
                }
            };
            if p.features.insert(key.to_owned(), form).is_some() {
                return Err(format!("feature {key} is given twice"));
            }
        }
        _ => {
            return Err(
                "no line of the policy (class <perf|bugfix>, or <feature key> all|floor <n>|share)"
                    .to_owned(),
            )
        }
    }
    Ok(())
}

/// The record's text as a policy.
///
/// # Errors
/// Every malformed line, one each: `dev/builder-policy.txt line <n>: <why>: <the line>`.
pub fn parse(text: &str) -> Result<Policy, String> {
    let mut p = Policy {
        classes: Vec::new(),
        features: BTreeMap::new(),
    };
    let (mut errors, mut classed) = (Vec::new(), false);
    for (i, raw) in text.lines().enumerate() {
        let l = raw.trim();
        if l.is_empty() || l.starts_with('#') {
            continue;
        }
        if let Err(why) = line(&mut p, l, &mut classed) {
            errors.push(format!("{FILE} line {}: {why}: {l}", i + 1));
        }
    }
    if !classed {
        p.classes = Policy::default().classes;
    }
    if errors.is_empty() {
        Ok(p) // GUARD_EDIT_OK: feature 461 T81 - the default classes where no class line is given
    } else {
        Err(errors.join("\n"))
    }
}

/// The policy a reader ranks by, and why it is the default where it is.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Read {
    pub policy: Policy,
    /// Empty where the record was read; else the record's errors (the default ranks meanwhile).
    pub why: String,
    /// The record is absent: the default ranks.
    pub absent: bool,
}

/// The record of the clone at `clone` ([`FILE`]), the default where it is absent or malformed (the module's doc).
#[must_use]
pub fn read(clone: &Path) -> Read {
    let Ok(text) = std::fs::read_to_string(clone.join(FILE)) else {
        return Read {
            absent: true,
            ..Read::default()
        };
    };
    match parse(&text) {
        Ok(policy) => Read {
            policy,
            ..Read::default()
        },
        Err(why) => Read {
            why: format!("{why}\nthe default policy ranks until it is mended (class perf, class bugfix, every feature share)"),
            ..Read::default()
        },
    }
}

/// Is a task a process bugfix (FR-011)? Its line carries [`BUGFIX_TAG`] among the bracketed tags right after its id (`- [ ] T85
/// [P] [bugfix] ...`), never one its title only quotes. `title` is the line after the id. By the tag alone: a task building a
/// mechanism is never in the class by its subject. The tags are read as `set_down_hooks`' `PERF_TAG` reads them: each `[...]`,
/// a space inside one too, followed by one or more spaces or the line's end.
// GUARD_EDIT_OK: feature 461 T81 - a tag holding a space before [bugfix] no longer ends the scan
#[must_use]
pub fn bugfix(title: &str) -> bool {
    let mut rest = title;
    while let Some((tag, after)) = rest.strip_prefix('[').and_then(|r| r.split_once(']')) {
        if !(after.is_empty() || after.starts_with(' ')) {
            return false;
        }
        if BUGFIX_TAG.get(1..BUGFIX_TAG.len() - 1) == Some(tag) {
            return true;
        }
        rest = after.trim_start_matches(' ');
    }
    false
}

/// Where a piece of work comes from, in its rank within one feature (the module's step 5).
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub enum Source {
    /// The lane's repair entry `r<n>`.
    Repair(String),
    /// A queue entry, by its line.
    Entry(usize),
    /// An open task no queue line names, by its place among the feature's boxes: named with the `make queue-add` that writes its line.
    Unlisted(usize),
}

/// A piece of work a free builder could take now.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Work {
    /// The feature's key, which orders features as their directories' names do (`45-` before `451-`, `451-` before `9-`).
    pub key: String,
    pub tasks: Vec<String>,
    pub source: Source,
    /// The command that hands it out (`make builder-brief ...`), or for an unlisted task the `make queue-add` that lists it.
    pub command: String,
    /// The classes its tasks are in.
    pub perf: bool,
    pub bugfix: bool,
}

impl Work {
    /// As a reader names it: `461 T81`.
    #[must_use]
    pub fn name(&self) -> String {
        format!("{} {}", self.key, self.tasks.join(","))
    }
}

/// A piece of work with its rank and why.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Ranked {
    pub work: Work,
    /// The class that ranks it, if any.
    pub class: Option<Class>,
    pub form: Form,
    /// The rank, smallest first (the module's steps 1-5).
    pub key: (usize, usize, bool, String, Source),
    /// Why it stands where it does, for a refusal or a list.
    pub why: String,
}

/// The rank of `w` under `p`, with `held` the trees each feature holds and `prefer` the caller's feature key.
fn rank_of(p: &Policy, w: Work, held: &BTreeMap<String, usize>, prefer: &str) -> Ranked {
    let class = p
        .classes
        .iter()
        .position(|c| match c {
            Class::Perf => w.perf,
            Class::Bugfix => w.bugfix,
        })
        .map(|i| (i, p.classes[i]));
    let form = p.form(&w.key);
    let holds = held.get(&w.key).copied().unwrap_or(0);
    let (tier, said) = match form {
        Form::Floor(n) if holds < n => (0, format!("floor {n}, {holds} held: its guarantee")),
        Form::All => (1, "all: every builder it can use".to_owned()),
        Form::Share => (2, "share".to_owned()),
        Form::Floor(n) => (
            3,
            format!("floor {n}, {holds} held: only an uncontended tree"),
        ),
    };
    let why = match class {
        Some((_, c)) => format!("class {} first, then feature {} ({said})", c.word(), w.key),
        None => format!("feature {} ({said})", w.key),
    };
    Ranked {
        class: class.map(|(_, c)| c),
        form,
        key: (
            class.map_or(p.classes.len(), |(i, _)| i),
            tier,
            prefer.is_empty() || w.key != prefer,
            w.key.clone(),
            w.source.clone(),
        ),
        why,
        work: w,
    }
}

/// THE RANKING, pure: `work` under `p`, the trees `held` counted for each feature, `prefer` the caller's feature key - best first.
#[must_use]
pub fn rank(p: &Policy, work: Vec<Work>, held: &[Tree], prefer: &str) -> Vec<Ranked> {
    let mut count: BTreeMap<String, usize> = BTreeMap::new();
    for t in held.iter().filter(|t| !t.free()) {
        *count.entry(t.feature.clone()).or_default() += 1;
    }
    let mut out: Vec<Ranked> = work
        .into_iter()
        .map(|w| rank_of(p, w, &count, prefer))
        .collect();
    out.sort_by(|a, b| a.key.cmp(&b.key));
    out
}

/// A feature directory's name for its key, under `clone/specs`.
fn dir_of(clone: &Path, key: &str) -> Option<PathBuf> {
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(clone.join("specs"))
        .ok()?
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|d| super::key_of(d) == key && d.join("tasks.md").is_file())
        .collect();
    dirs.sort();
    dirs.into_iter().next()
}

/// The open boxes of `dir`'s tasks.md, in order: id and the rest of the line; and its plan's checklist headings, which
/// `set_down_hooks::performance` reads.
fn boxes(dir: &Path) -> (Vec<(String, String)>, String) {
    let read = |n: &str| std::fs::read_to_string(dir.join(n)).unwrap_or_default();
    let open = read("tasks.md")
        .lines()
        .filter_map(|l| l.trim_start().strip_prefix("- [ ] "))
        .filter_map(|l| {
            let (id, rest) = l.split_once(' ').unwrap_or((l, ""));
            super::is_task(id).then(|| (id.to_owned(), rest.to_owned()))
        })
        .collect();
    (open, read("plan.md"))
}

/// Each board's READY entries that overlap nothing in flight ([`super::Next::free`]) as work.
fn entries(boards: &[Board]) -> Vec<Work> {
    let mut out = Vec::new();
    for b in boards {
        for &i in &b.next.free {
            let e = &b.entries[i];
            let title = |t: &String| b.facts.open.get(t).map_or("", String::as_str);
            out.push(Work {
                key: b.key.clone(),
                tasks: e.tasks.clone(),
                source: Source::Entry(e.line),
                command: e.command(&b.key),
                perf: e.tasks.iter().any(|t| b.facts.perf.contains(t)),
                bugfix: e.tasks.iter().any(|t| bugfix(title(t))),
            });
        }
    }
    out
}

/// The tasks each feature's queue names, any state, by key.
fn listed(boards: &[Board]) -> BTreeMap<&str, BTreeSet<&String>> {
    boards
        .iter()
        .map(|b| {
            (
                b.key.as_str(),
                b.entries.iter().flat_map(|e| &e.tasks).collect(),
            )
        })
        .collect()
}

/// The facts [`gather`] reads besides the boards: the clone, its pool's held trees, its done refs and its lane's ready repairs.
pub struct Ground<'a> {
    pub clone: &'a Path,
    pub held: &'a [Tree],
    /// The done refs' names after [`DONE_REFS`]: `<key>-<task>`.
    pub uncarried: BTreeSet<String>,
    pub repairs: Vec<super::repairs::Repair>,
    /// The open performance tasks no queue line names ([`super::unlisted`]).
    pub unlisted: Vec<Unlisted>,
    /// The open process bugfixes of every active feature, `<key> <task>` ([`crate::guards::set_down_hooks::open_bugfix`]): the
    /// class ranks across every feature, so one no queue line names is named as T313 names performance work.
    pub bugfixes: BTreeSet<String>,
    /// The Makefile's targets, by which an unlisted task's kind is read ([`crate::builder_brief::mechanism`]).
    pub known: BTreeSet<String>,
}

/// The unlisted open tasks of a feature the policy puts forward (an `all` feature or a floor not met), and a class's unlisted ones:
/// open boxes no queue line names, no tree holds and no done ref keeps, each named by the `make queue-add` that lists it.
fn unlisted_of(p: &Policy, g: &Ground, boards: &[Board]) -> Vec<Work> {
    let names = listed(boards);
    let mut count: BTreeMap<&str, usize> = BTreeMap::new();
    for t in g.held.iter().filter(|t| !t.free()) {
        *count.entry(t.feature.as_str()).or_default() += 1;
    }
    let forward = |key: &str| match p.form(key) {
        Form::All => true,
        Form::Floor(n) => count.get(key).copied().unwrap_or(0) < n,
        Form::Share => false,
    };
    let perf: BTreeSet<String> = g.unlisted.iter().map(|u| u.tasks.clone()).collect();
    let mut keys: BTreeSet<String> = p.features.keys().filter(|k| forward(k)).cloned().collect();
    // GUARD_EDIT_OK: feature 461 T81 - an unlisted bugfix of any active feature named with its class, as performance's is
    let classed = |t: &String| perf.contains(t) || g.bugfixes.contains(t);
    keys.extend(
        perf.iter()
            .chain(&g.bugfixes)
            .filter_map(|t| t.split(' ').next().map(str::to_owned)),
    );
    let mut out = Vec::new();
    for key in keys {
        let Some(dir) = dir_of(g.clone, &key) else {
            continue;
        };
        let (open, plan) = boxes(&dir);
        for (k, (id, title)) in open.iter().enumerate() {
            let is_perf = perf.contains(&format!("{key} {id}"))
                || crate::guards::set_down_hooks::performance(id, title, &plan);
            let quiet = names.get(key.as_str()).is_some_and(|l| l.contains(id))
                || g.held
                    .iter()
                    .any(|t| t.feature == key && t.tasks.contains(id))
                || g.uncarried.contains(&format!("{key}-{id}"));
            if quiet || !(forward(&key) || classed(&format!("{key} {id}"))) {
                continue;
            }
            let line = format!("- [ ] {id} {title}");
            let kind = if crate::builder_brief::mechanism(&line, &g.known).is_some() {
                "build-half"
            } else {
                "fix"
            };
            out.push(Work {
                key: key.clone(),
                tasks: vec![id.clone()],
                source: Source::Unlisted(k),
                command: format!("make queue-add F={key} T={id} KIND={kind}"),
                perf: is_perf,
                bugfix: bugfix(title),
            });
        }
    }
    out
}

/// The lane's ready repairs as work, each classed by its own tasks' boxes (FR-011: a repair ranks by its task's class and feature).
fn repairs_of(g: &Ground) -> Vec<Work> {
    let mut out = Vec::new();
    for r in &g.repairs {
        let dir = dir_of(g.clone, &r.key);
        let (open, plan) = dir.as_deref().map(boxes).unwrap_or_default();
        let title = |t: &String| {
            open.iter()
                .find(|(id, _)| id == t)
                .map(|(_, title)| title.as_str())
        };
        let ours = |f: &dyn Fn(&String, &str) -> bool| {
            r.tasks.iter().any(|t| title(t).is_some_and(|x| f(t, x)))
        };
        out.push(Work {
            key: r.key.clone(),
            tasks: r.tasks.clone(),
            source: Source::Repair(r.id.clone()),
            command: r.command(),
            perf: ours(&|t, x| crate::guards::set_down_hooks::performance(t, x, &plan)),
            bugfix: ours(&|_, x| bugfix(x)),
        });
    }
    out
}

/// Every piece of work a free builder could take now, unranked (the module's doc): the boards' free READY entries, the ground's
/// repairs, and the unlisted tasks the policy or a class puts forward.
#[must_use]
pub fn gather(p: &Policy, g: &Ground, boards: &[Board]) -> Vec<Work> {
    let mut out = repairs_of(g);
    out.extend(entries(boards));
    out.extend(unlisted_of(p, g, boards));
    out
}

/// What [`ranked`] finds.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Ranking {
    /// The record as read.
    pub read: Read,
    /// Every piece of work a free builder could take now, best first: the policy's pick is the first.
    pub work: Vec<Ranked>,
    /// A queue that could not be read, each.
    pub unread: Vec<String>,
}

/// THE ONE READER every handout path asks (FR-011): the clone at `clone`'s record, queues, pool, done refs, lane repairs and
/// unlisted performance tasks, ranked by the policy, `prefer` the caller's feature key (empty for none).
#[must_use]
pub fn ranked(clone: &Path, prefer: &str) -> Ranking {
    let common = clone.join(".git");
    let trees = crate::builder_pool::read(&common);
    let held: Vec<Tree> = trees.iter().filter(|t| !t.free()).cloned().collect();
    let (mut boards, mut unread) = (Vec::new(), Vec::new());
    for dir in super::queues(clone) {
        match super::board(clone, &common, &dir, &trees) {
            Ok(b) => boards.push(b),
            Err(why) => unread.push(why),
        }
    }
    let read = read(clone);
    // the caller's feature's directory, which the active walk counts active whether started or not (as T313's `unlisted` does)
    let prefer_dir = dir_of(clone, prefer)
        .filter(|_| !prefer.is_empty())
        .and_then(|d| d.file_name().map(|n| n.to_string_lossy().into_owned()))
        .unwrap_or_default();
    let refs = std::process::Command::new("git")
        .arg("-C")
        .arg(clone)
        .args(["for-each-ref", "--format=%(refname)", DONE_REFS])
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default();
    let ground = Ground {
        clone,
        held: &held,
        uncarried: refs
            .lines()
            .filter_map(|r| r.strip_prefix(DONE_REFS))
            .map(str::to_owned)
            .collect(),
        repairs: super::repairs::offer(&common, &held).ready,
        unlisted: super::unlisted(clone, &common, prefer),
        bugfixes: crate::guards::set_down_hooks::open_bugfix(clone, &common, &prefer_dir)
            .unwrap_or_default()
            .into_iter()
            .map(|t| format!("{} {}", super::key_of(Path::new(&t.feature)), t.id))
            .collect(),
        known: crate::builder_brief::targets(
            &std::fs::read_to_string(clone.join("Makefile")).unwrap_or_default(),
        ),
    };
    let work = gather(&read.policy, &ground, &boards);
    Ranking {
        work: rank(&read.policy, work, &held, prefer),
        read,
        unread,
    }
}

#[cfg(test)]
mod tests;
