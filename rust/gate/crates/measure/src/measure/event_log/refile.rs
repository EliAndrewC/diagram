//! `l7r-gate measure event-log refile` - `make events-refile` (feature 451 T26): the one-time re-filing of the event-log lines written
//! before T26's writer landed, each moved to the log of the feature of the task it carries. WHY: the writer filed every line under the
//! clone's `.specify/feature.json`, which `make task-start` rewrites to the feature started last, so with 449 and 451 worked in one clone
//! a 451 builder's `T26` sat in 449's log as 449's T26 (observed 2026-11-20, method: `make events-refile DRY=1` on this clone's logs).
//!
//! Two rules, in order, the writer's own chain run backwards (`event_log_hooks/filed.rs`):
//! - BY BRIEF: a subagent's line (`by`; a SubagentStart/Stop's `aid`; an Agent call's own dispatch by `aid` or its tool-use id) whose
//!   dispatch's brief - its meta file's `description`, under `<projects>/*/<sid>/subagents/` - names a feature other than its log's (the writer's `brief_feature`)
//!   moves there, unless the line carries its own `T=` of its log's feature. Its task becomes the brief's `T<n>`; else stays where it is
//!   one of the new feature's; else that feature's task-start in force at the line's time; else none.
//! - BY TASK ID: a line whose `task` is no task of its log's feature (`tasks.md` and `tasks-done.md`) moves to the feature whose
//!   task-start of that id was in force at the line's time (else the latest that started it), when that feature has the id. The ids
//!   collide across features (`T03` is a task of 16 features), so the clone's own starts say which one this line meant. The rule is the
//!   writer's own `started`, called with the starts made by the line's time (451 T56: one reader, not a copy), so a start more than
//!   72 h before the line names none (451 T53's `STALE_START_S`).
//! - BY THE FALLBACK (451 T56): where no start names the task, the writer's next link - feature.json at the line's time, which
//!   `make task-start` rewrites to the feature it starts, so the feature of the clone's last start by then - when that feature has the
//!   id, the line marked `"fallback": true` as the writer marks it. WHY: 451 T47's three spec-fidelity rounds, briefed `T47 plan review`,
//!   sat in 385's log by 385's T47 start of 2026-10-18, 23 lines that the stale rule alone leaves where they are (observed 2026-11-21,
//!   method: `make events-refile DRY=1`, its lines left joined to their meta files and `task-starts.jsonl`). A line nothing places is
//!   left and counted.
//!
//! Idempotent: a moved line is filed where both rules leave it, and a line already in its target is not appended twice. The target is
//! appended to (`O_APPEND`, as the hooks write - both readers sort by `t`, and `reversal` reads a log as a set); the source is rewritten
//! through a temporary file, any line a live hook appended meanwhile carried over before the rename.

use l7r_shared::env::Reader;
use std::collections::{BTreeMap, HashMap};
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};

use fancy_regex::Regex;
use serde_json::{Map, Value};

use l7r_shared::guards::event_log_hooks::{self as writer, brief_feature, Start};

use super::reply;
use crate::measure::events::ts;
use crate::Reply;

const USAGE: &str = "usage: l7r-gate measure event-log refile --root <tree> [--dir <events dir>] [--projects <dir>] [--dry-run]\n";
/// The commands whose `T=` a line carries as its own (`event_log_hooks::tool_fields`).
const CARRYING: [&str; 4] = ["tick", "task-start", "decide", "land"];
/// A task start's own lines come before its row (the `PreToolUse`) or within its call: a start this soon after the line still counts.
/// GUESS knob: 60 s. 322 of 335 `task-start` calls took 60 s or less, p90 9.4 s, measured 2026-11-20 (the `ms` of every log's
/// `task-start` `PostToolUse` line); a longer call's `PreToolUse` finds no start of its own and is left, counted.
const START_SLACK: f64 = 60.0;

fn re(p: &str) -> Regex {
    l7r_shared::regex::build(p).unwrap_or_else(|e| unreachable!("a fixed pattern: {e}"))
}

/// What the run is given.
struct Given {
    root: PathBuf,
    dir: PathBuf,
    projects: PathBuf,
    dry: bool,
}

fn given(args: &[String], env: &Reader) -> Option<Given> {
    let mut root = None;
    let mut dir = None;
    let mut projects = None;
    let mut dry = false;
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--root" => root = Some(PathBuf::from(it.next()?)),
            "--dir" => dir = Some(PathBuf::from(it.next()?)),
            "--projects" => projects = Some(PathBuf::from(it.next()?)),
            "--dry-run" => dry = true,
            _ => return None,
        }
    }
    let root = root?;
    let dir = dir.unwrap_or_else(|| {
        l7r_shared::guards::event_log_hooks::log_path_in(&root, "x", env)
            .parent()
            .map_or_else(PathBuf::new, Path::to_path_buf)
    });
    let projects = projects
        .unwrap_or_else(|| PathBuf::from(env("HOME").unwrap_or_default()).join(".claude/projects"));
    Some(Given {
        root,
        dir,
        projects,
        dry,
    })
}

/// What the rules read, each read once.
struct Facts {
    root: PathBuf,
    projects: PathBuf,
    specs: Vec<String>,
    ids: HashMap<String, Vec<String>>,
    /// the writer's reading of `task-starts.jsonl` (`event_log_hooks::starts`)
    starts: Vec<Start>,
    /// a session's briefs: by agent id and by the dispatch's tool-use id
    briefs: HashMap<String, HashMap<String, String>>,
    task_box: Regex,
    task_named: Regex,
}

impl Facts {
    fn new(root: &Path, projects: &Path) -> Self {
        let specs = super::super::events::names(&root.join("specs"))
            .into_iter()
            .filter(|n| root.join("specs").join(n).is_dir())
            .collect();
        Self {
            root: root.to_path_buf(),
            projects: projects.to_path_buf(),
            specs,
            ids: HashMap::new(),
            starts: writer::starts(root),
            briefs: HashMap::new(),
            task_box: re(r"^- \[[ xX]\] (T\d+[a-z]?)\b"),
            task_named: re(r"\b(T\d+[a-z]?)\b"),
        }
    }

    /// The one feature directory a brief's number names, the single `specs/<n>-*` (the writer's `Specs::named`; a brief's word is a
    /// number, never a whole directory name).
    fn named(&self, word: &str) -> Option<String> {
        let prefix = format!("{word}-");
        let mut hits = self.specs.iter().filter(|n| n.starts_with(&prefix));
        match (hits.next(), hits.next()) {
            (Some(one), None) => Some(one.clone()),
            _ => None,
        }
    }

    /// Does `feature` have task `task`, open or archived?
    fn has(&mut self, feature: &str, task: &str) -> bool {
        if !self.ids.contains_key(feature) {
            let d = self.root.join("specs").join(feature);
            let all = l7r_shared::speckit::tasks::all_text(&d).unwrap_or_default();
            let ids = all
                .lines()
                .filter_map(|l| first(&self.task_box, l))
                .collect();
            self.ids.insert(feature.to_owned(), ids);
        }
        self.ids[feature].iter().any(|t| t == task)
    }

    /// The starts at or before `at` (with the slack), in file order: what the writer had read at the line's time. A start whose time
    /// does not parse has no place in time, so none.
    fn before(&self, at: f64) -> Vec<Start> {
        self.starts
            .iter()
            .filter(|(_, _, s)| s.is_some_and(|s| s <= at + START_SLACK))
            .cloned()
            .collect()
    }

    /// The task in force for `feature` at `at` (the writer's `in_force`).
    fn in_force(&self, feature: &str, at: f64) -> Option<String> {
        writer::in_force(&self.before(at), feature)
    }

    /// The feature whose start of `task` was in force at `at`, else the latest that started it by then, a start more than 72 h
    /// before `at` naming none (the writer's `started`, 451 T56).
    fn started(&self, task: &str, at: f64) -> Option<String> {
        writer::started(&self.before(at), task, Some(at))
    }

    /// The writer's fallback at `at`: feature.json then, which `make task-start` rewrites to the feature it starts, so the feature of
    /// the clone's last start by then (451 T56). CONVENTION, a reading, not a record: feature.json keeps no history, and a feature
    /// created between two starts (`make claim`) is not seen; the move it makes is held to a feature that has the line's task.
    fn fallback(&self, at: f64) -> Option<String> {
        self.before(at).pop().map(|(f, _, _)| f)
    }

    /// The brief of the dispatch a line belongs to, "" where none is on disk.
    fn brief(&mut self, e: &Map<String, Value>) -> String {
        let sid = text_m(e, "sid");
        if sid.is_empty() {
            return String::new();
        }
        if !self.briefs.contains_key(&sid) {
            let found = session_briefs(&self.projects, &sid);
            self.briefs.insert(sid.clone(), found);
        }
        let of = &self.briefs[&sid];
        let ev = text_m(e, "ev");
        let mut keys = Vec::new();
        if text_m(e, "tool") == "Agent" {
            keys.push(text_m(e, "aid"));
            keys.push(text_m(e, "id"));
        }
        if ev == "SubagentStart" || ev == "SubagentStop" {
            keys.push(text_m(e, "aid"));
        }
        keys.push(text_m(e, "by"));
        keys.iter()
            .filter(|k| !k.is_empty())
            .find_map(|k| of.get(k).cloned())
            .unwrap_or_default()
    }
}

/// A session's subagent briefs, by agent id and by the dispatching call's tool-use id.
fn session_briefs(projects: &Path, sid: &str) -> HashMap<String, String> {
    let mut out = HashMap::new();
    for p in super::super::events::names(projects) {
        let dir = projects.join(p).join(sid).join("subagents");
        for n in super::super::events::names(&dir) {
            let Some(aid) = n
                .strip_prefix("agent-")
                .and_then(|r| r.strip_suffix(".meta.json"))
            else {
                continue;
            };
            let Some(meta) = std::fs::read_to_string(dir.join(&n))
                .ok()
                .and_then(|t| serde_json::from_str::<Value>(&t).ok())
            else {
                continue;
            };
            let d = text(&meta, "description");
            let tu = text(&meta, "toolUseId");
            if !tu.is_empty() {
                out.insert(tu, d.clone());
            }
            out.insert(aid.to_owned(), d);
        }
    }
    out
}

fn first(p: &Regex, s: &str) -> Option<String> {
    p.captures(s)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
}

fn text(v: &Value, k: &str) -> String {
    v.get(k)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned()
}

fn text_m(e: &Map<String, Value>, k: &str) -> String {
    e.get(k)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned()
}

/// Why a line moves.
#[derive(Clone, Copy)]
enum Rule {
    Brief,
    TaskId,
    Fallback,
}

/// Where one line of `feature`'s log belongs: None to stay, else the feature, the rule and the line as written there.
fn verdict(facts: &mut Facts, feature: &str, raw: &str) -> Option<(String, Rule, String)> {
    let Ok(Value::Object(mut e)) = serde_json::from_str::<Value>(raw) else {
        return None;
    };
    let at = ts(&text_m(&e, "t")).ok()?;
    let task = text_m(&e, "task");
    let carried = CARRYING.contains(&text_m(&e, "make").as_str())
        && !task.is_empty()
        && facts.has(feature, &task);
    let brief = facts.brief(&e);
    let briefed = brief_feature(&brief, &|n| facts.named(n), &|f| {
        facts.starts.iter().any(|(s, _, _)| s == f)
    });
    if let Some(to) = briefed.filter(|g| g != feature && !carried) {
        // a `T=` the line carries is its own task, kept where the new feature has it; then the brief's
        let own = CARRYING.contains(&text_m(&e, "make").as_str())
            && !task.is_empty()
            && facts.has(&to, &task);
        let new_task = Some(task.clone())
            .filter(|_| own)
            .or_else(|| first(&facts.task_named, &brief))
            .or_else(|| Some(task.clone()).filter(|t| !t.is_empty() && facts.has(&to, t)))
            .or_else(|| facts.in_force(&to, at));
        match new_task {
            Some(t) => e.insert("task".into(), Value::from(t)),
            None => e.remove("task"),
        };
        return Some((to, Rule::Brief, Value::Object(e).to_string()));
    }
    if task.is_empty() || facts.has(feature, &task) {
        return None;
    }
    let (to, rule) = match facts.started(&task, at) {
        Some(to) => (to, Rule::TaskId),
        None => (facts.fallback(at)?, Rule::Fallback),
    };
    if to == feature || !facts.has(&to, &task) {
        return None;
    }
    if let Rule::Fallback = rule {
        e.insert("fallback".into(), Value::Bool(true));
        return Some((to, rule, Value::Object(e).to_string()));
    }
    Some((to, rule, raw.to_owned()))
}

/// Counts of one run.
#[derive(Default)]
struct Tally {
    read: usize,
    /// by source and target: the lines moved by brief, by task id, by the fallback
    moved: BTreeMap<(String, String), [usize; 3]>,
    left: usize,
}

/// One source log re-filed: its moves appended to their targets, its kept lines written back.
fn refile_log(
    facts: &mut Facts,
    g: &Given,
    feature: &str,
    tally: &mut Tally,
) -> Result<(), String> {
    let path = g.dir.join(format!("{feature}.jsonl"));
    let bytes = std::fs::read(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    let body = String::from_utf8_lossy(&bytes);
    let mut kept = String::new();
    let mut out: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for raw in body.split_inclusive('\n') {
        let line = raw.trim_end_matches('\n');
        tally.read += 1;
        if let Some((to, rule, written)) = verdict(facts, feature, line) {
            let c = tally
                .moved
                .entry((feature.to_owned(), to.clone()))
                .or_default();
            c[rule as usize] += 1;
            out.entry(to).or_default().push(written);
        } else {
            let task = serde_json::from_str::<Value>(line)
                .ok()
                .map(|e| text(&e, "task"))
                .unwrap_or_default();
            if !task.is_empty() && !facts.has(feature, &task) {
                tally.left += 1;
            }
            kept.push_str(raw);
        }
    }
    if g.dry || out.is_empty() {
        return Ok(());
    }
    for (to, lines) in &out {
        let target = g.dir.join(format!("{to}.jsonl"));
        let there = std::fs::read_to_string(&target).unwrap_or_default();
        let have: std::collections::HashSet<&str> = there.lines().collect();
        let mut add = String::new();
        for l in lines.iter().filter(|l| !have.contains(l.as_str())) {
            add.push_str(l);
            add.push('\n');
        }
        std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&target)
            .and_then(|mut f| f.write_all(add.as_bytes()))
            .map_err(|e| format!("{}: {e}", target.display()))?;
    }
    write_back(&path, kept.into_bytes(), bytes.len())
}

/// The kept lines written over `path` through a temporary file, any bytes appended since `read` carried over first.
fn write_back(path: &Path, mut kept: Vec<u8>, mut read: usize) -> Result<(), String> {
    let tmp = path.with_extension("jsonl.refile");
    let fail = |e: std::io::Error| format!("{}: {e}", path.display());
    loop {
        std::fs::write(&tmp, &kept).map_err(fail)?;
        let now = std::fs::read(path).map_err(fail)?;
        if now.len() <= read {
            break;
        }
        kept.extend_from_slice(&now[read..]);
        read = now.len();
    }
    std::fs::rename(&tmp, path).map_err(fail)
}

/// The command: every log in the directory re-filed (or, `--dry-run`, only counted), the counts printed.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    cli_in(args, &l7r_shared::env::opt)
}

/// [`cli`] reading the environment `env` (feature 451 T38: a test's own, never a session's exports).
#[must_use]
pub fn cli_in(args: &[String], env: &Reader) -> Reply {
    let Some(g) = given(args, env) else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let mut facts = Facts::new(&g.root, &g.projects);
    let mut tally = Tally::default();
    let logs: Vec<String> = super::super::events::names(&g.dir)
        .into_iter()
        .filter_map(|n| n.strip_suffix(".jsonl").map(str::to_owned))
        .collect();
    for feature in &logs {
        if let Err(why) = refile_log(&mut facts, &g, feature, &mut tally) {
            return reply(String::new(), format!("refile: {why}\n"), 1);
        }
    }
    let mut out = String::new();
    let _ = writeln!(
        out,
        "refile: {} lines read in {} logs under {}",
        tally.read,
        logs.len(),
        g.dir.display()
    );
    let mut all = 0;
    for ((from, to), [brief, id, fallback]) in &tally.moved {
        all += brief + id + fallback;
        // the fallback's count only where it moved a line, so a run with none reads as it did before 451 T56
        let fell = if *fallback > 0 {
            format!(", {fallback} by the fallback")
        } else {
            String::new()
        };
        let _ = writeln!(
            out,
            "refile: {from} -> {to}: {} lines ({brief} by brief, {id} by task id{fell})",
            brief + id + fallback
        );
    }
    let _ = writeln!(
        out,
        "refile: {all} lines moved{}",
        if g.dry {
            " (dry run: nothing written)"
        } else {
            ""
        }
    );
    let _ = writeln!(
        out,
        "refile: {} lines left whose task is no task of their log's feature and no rule places",
        tally.left
    );
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
