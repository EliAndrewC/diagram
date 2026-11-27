//! WHERE A LINE IS FILED (feature 451 T26): the feature of the task the line carries, never the clone's `.specify/feature.json` alone.
//! WHY: `make task-start` rewrites feature.json to the feature whose task started last, so with two features worked in one clone (449
//! and 451 on 2026-11-20) every line landed in that one feature's log - a 451 builder's `T26` was booked in 449's log as 449's T26, 45
//! lines of it and 5 of 451's T03 (observed 2026-11-20, method: the 449 log's lines whose `task` is no 449 task, matched to the clone's
//! `task-starts.jsonl`), and `make where-time` read both features wrong.
//!
//! THE CHAIN (first that says wins, each read cheap - no `tasks.md` is read on a hook):
//! - the FEATURE: a make command's `F=` (read outside its heredocs, 451 T53) where the command carries its own `T=` or no brief names a
//!   feature; else the dispatch's brief - the Agent call's own `description`, or a subagent's meta file's, or for a first start, whose meta
//!   file is not written yet, its dispatch's (`dispatches.rs`, 451 T53) - the feature it names ([`brief_feature`]); else the feature whose
//!   task-start names the line's task, a start older than [`STALE_START_S`] naming none (451 T53); else the feature the builder pool
//!   says holds the line's tree ([`pool_feature`], 451 T529); else the
//!   FALLBACK, `feature_of` (the session's environment, then feature.json), and the line is marked `"fallback": true` unless the session's environment declared that feature;
//! - the TASK: a `tick`, `task-start`, `decide` or `land` command's `T=` (`line`), or a `closing-checks` one's (451 T106); else, for an
//!   Agent call, the `T<n>` its own description names; else the agent's CORRECTION (451 T106, [`renumbered`]); else the `T<n>` the
//!   brief names; else, for an Agent call, its prompt's first line's (451 T07); else, for an agent's line, its builder's reading - its
//!   description's head, else its own prompt's first line, else its dispatching builder's (451 T161, `set_down_hooks::agent_builder`);
//!   else a page session's brief's (`L7R_PAGE_SESSION`, else the line's `session_id` listed in `page-sessions/index.txt`, 451 T167;
//!   `set_down_hooks::page_session_brief`); else, for the main session's own line
//!   alone - a gate tool's own row among them, a check's `Phase` line - the task the builder pool says holds the line's tree
//!   ([`pool_task`], 451 T332), else the task-start in force for the line's feature (D2's last entry, now of the line's own feature,
//!   not of feature.json's) - an agent's or page session's line naming no task carries none, never the clone's mark (451 T161).
//!
//! THE CORRECTION (451 T106): a builder the coordinator re-numbers keeps the task the correction names on every later line, its feature
//! still the brief's. What says it, earliest first - the night's 136 builders, measured 2026-11-21 (a Python read of the session
//! transcript, its subagents' transcripts and meta files, and the 451 log):
//! - the coordinator's `SendMessage` to the agent: T101's, "Your task is T101, not T100", came 20 s into its run, before every one of its
//!   writes (8 of its 230 lines, all reads, before it); a message NAMING another task is no correction - 40 of 108 messages to a briefed
//!   agent named one and one was - so only `T<new>, not T<old>` counts, `T<old>` the task the agent is filed under now ([`CORRECTION`]);
//! - the builder's own `make closing-checks`, `make decide` or `make task-start` `T=`: 1,113 of 1,695 Write and Edit lines came before
//!   a builder's first such call, and no builder ran `task-start`, so it files the lines after it - the backstop where a correction is
//!   worded otherwise.
//!
//! Earlier lines stay as filed: T101's 8 were reads, which neither land-alone's list nor the closing checks' split reads. Its handoff
//! file's name is no signal: `context_cap_hooks` names it from [`filed_at`](super::filed_at)'s task, the brief's until now.
//!
//! A fallback line's task is a guess when two features are worked at once (the coordinator's own calls), so it says so: a reader of the
//! task field (T07, T08, T14) can keep that time apart rather than book it to the task feature.json happened to name. The session's
//! environment (`L7R_FEATURE_DIRECTORY`, `SPECIFY_FEATURE` in the hook's own process) is the fallback's, not first: the hook's
//! environment is the whole Claude Code session's, shared by the main session and every builder it dispatches, so it cannot tell two
//! builders apart; a line's own word can.

use std::cell::OnceCell;
use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{
    common_git_dir, dispatches, feature_of, first_group, log_path_in, make_target, re, text_of,
    TASK, TASK_NAMED,
};
use crate::guards::set_down_hooks::{agent_builder, page_session_brief, page_session_listed};
use crate::shape::strip_heredocs;

/// How old a task start may be and still name a brief's bare task's feature (451 T53). WHY: `T47 plan review`, from a 451 T47 builder
/// in a clone that never started 451's T47, was filed by 385's T47 start of 2026-10-18 - 23 lines, three spec-fidelity rounds, in
/// 385's log on 2026-11-21 (observed 2026-11-21, method: `make events-refile DRY=1`'s lines left, joined to their meta files). GUESS knob:
/// 72 h. Of 571 task-only briefs in the clone's logs, the start their log's feature made of that task was p50 0.3 h, p90 1.8 h old,
/// 14 past 24 h, the longest of them 34.1 h (444's T16), and then 313, 618 and 799 h (7 agents), measured 2026-11-21 (each such
/// subagent's first line against the clone's `task-starts.jsonl`); the bound keeps the 34 h one and drops the three weeks-old ones.
pub(super) const STALE_START_S: f64 = 72.0 * 3600.0;

pattern!(FEATURE_ARG, r#"(?:^|\s)F=["']?([A-Za-z0-9][\w.-]*)"#);
// a brief's feature: the number before its task (`451 T26: ...`, `spec-fidelity on 451 T03's section`) ...
pattern!(FEATURE_BEFORE_TASK, r"\b(\d+)\s+T\d+[a-z]?\b");
// ... else a number standing alone - never one inside a hyphenated word (`FR-008`, `qingshigao-122`, `375-a1`)
pattern!(BARE_NUMBER, r"(?<![\w-])(\d+)(?![\w-])");
// a coordinator's correction (451 T106): `T101, not T100` - GUESS knob, one case fitted: the night's one correction read "Your task is
// T101, not T100" (its summary; the message said "is T101 in tasks.md, not T100"), and of its 117 SendMessages the one other `T<n>, not
// T<m>`, "filed as T43, not T42" to T40's builder, named no task of its own, measured 2026-11-21 (the session transcript's SendMessage
// inputs). Its open side: a correction worded otherwise is filed by the builder's own closing step, from that call on
pattern!(CORRECTION, r"\b(T\d+[a-z]?),?\s+\(?not\s+(T\d+[a-z]?)\b");

/// The closing-step targets whose `T=` names the task a builder works on (451 T106): `make closing-checks`, `make decide`, `make
/// task-start`.
const OWN_STEPS: [&str; 3] = ["closing-checks", "decide", "task-start"];

/// The feature a dispatch's brief names (451 T26): the number before a task id, naming one feature directory; else a number standing
/// alone that names one feature directory this clone has started a task of. WHY the second is held to started features: a brief's
/// numbers are mostly counts and source ids - "Triage T09's 108 moved claims", "source-reader Qingshigao 122", "impl-drift on 154 owed
/// claims" - and every one of those named an old feature's directory (observed 2026-11-20, method: the numbers of every subagent
/// meta file's `description` under `~/.claude/projects` matched to `specs/<n>-*`; `make events-refile DRY=1` moved 545 lines to 008
/// on "FR-008" before this rule).
pub fn brief_feature(
    brief: &str,
    named: &dyn Fn(&str) -> Option<String>,
    worked: &dyn Fn(&str) -> bool,
) -> Option<String> {
    let numbers = |p: &Regex| -> Vec<String> {
        p.captures_iter(brief)
            .map_while(Result::ok)
            .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
            .collect()
    };
    numbers(&FEATURE_BEFORE_TASK)
        .iter()
        .find_map(|n| named(n))
        .or_else(|| {
            numbers(&BARE_NUMBER)
                .iter()
                .find_map(|n| named(n).filter(|f| worked(f)))
        })
}

/// Where a line goes: its feature (the log), its task, and whether the feature was only the fallback's.
pub(super) struct Filed {
    pub feature: String,
    pub task: Option<String>,
    pub fallback: bool,
}

/// The `specs/` directory names, read at most once a line, and only when a word asks.
struct Specs<'a> {
    root: &'a Path,
    names: OnceCell<Vec<String>>,
}

impl Specs<'_> {
    /// The one feature directory `word` names: `specs/<word>` itself, else the single `specs/<word>-*`; None for none or several.
    fn named(&self, word: &str) -> Option<String> {
        let specs = self.root.join("specs");
        if specs.join(word).is_dir() {
            return Some(word.to_owned());
        }
        let names = self.names.get_or_init(|| {
            std::fs::read_dir(&specs)
                .into_iter()
                .flatten()
                .filter_map(Result::ok)
                .filter(|e| e.path().is_dir())
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        });
        let prefix = format!("{word}-");
        let mut hits = names.iter().filter(|n| n.starts_with(&prefix));
        match (hits.next(), hits.next()) {
            (Some(one), None) => Some(one.clone()),
            _ => None,
        }
    }
}

/// The dispatch's briefs: an Agent call's own `description`; else, for a subagent's line, its meta file's `description`
/// (`<transcript_path without .jsonl>/subagents/agent-<agent_id>.meta.json`, research R2; one read a line); else, for a first start,
/// whose meta file is not written yet, the dispatches it may have come from (`dispatches.rs`, 451 T53). None where nothing is readable;
/// several only for a start, which the caller takes where they agree.
fn briefs(payload: &Value, events: &Path, now: &str) -> Vec<String> {
    if text_of(payload.get("tool_name")) == "Agent" {
        let own = text_of(payload.get("tool_input").and_then(|t| t.get("description")));
        if !own.is_empty() {
            return vec![own];
        }
    }
    let aid = text_of(payload.get("agent_id"));
    if aid.is_empty() || text_of(payload.get("transcript_path")).is_empty() {
        return Vec::new();
    }
    if let Some(own) = meta_brief(payload, &aid) {
        return vec![own];
    }
    if text_of(payload.get("hook_event_name")) == "SubagentStart" {
        return dispatches::briefs_at_start(events, payload, now);
    }
    Vec::new()
}

/// Agent `aid`'s meta file's `description`, in the session the payload's `transcript_path` names (research R2); None where none is
/// readable.
fn meta_brief(payload: &Value, aid: &str) -> Option<String> {
    let transcript = Some(text_of(payload.get("transcript_path"))).filter(|t| !t.is_empty())?;
    let session = transcript.strip_suffix(".jsonl").unwrap_or(&transcript);
    std::fs::read_to_string(Path::new(session).join(format!("subagents/agent-{aid}.meta.json")))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .map(|m| text_of(m.get("description")))
}

/// The (feature number, tasks) agent `aid` builds by its builder's reading - its description's head, else its own prompt's first line,
/// else the builder that dispatched it (`set_down_hooks::agent_builder`, 449 T268's and 451 T157's reading) - in the session the
/// payload's `transcript_path` names; None where none is readable (451 T161).
fn builder_named(payload: &Value, aid: &str) -> Option<(String, Vec<String>)> {
    let transcript = Some(text_of(payload.get("transcript_path"))).filter(|t| !t.is_empty())?;
    let session = transcript.strip_suffix(".jsonl").unwrap_or(&transcript);
    agent_builder(&Path::new(session).join("subagents"), aid)
}

/// Whether `word` is a task id: `T`, digits, at most one lowercase letter (`T07`, `T7a`).
pub(super) fn is_task(word: &str) -> bool {
    let Some(rest) = word.strip_prefix('T') else {
        return false;
    };
    let digits = rest.trim_end_matches(|c: char| c.is_ascii_lowercase());
    rest.len() - digits.len() <= 1
        && !digits.is_empty()
        && digits.bytes().all(|b| b.is_ascii_digit())
}

/// The task a command's own closing step names: the `T=` of a command that runs [`OWN_STEPS`]' target, read outside its heredocs (451
/// T106); None for any other command.
fn own_step(command: &str) -> Option<String> {
    let steps = crate::make::invoked(command);
    if !steps.iter().any(|t| OWN_STEPS.contains(&t.as_str())) {
        return None;
    }
    first_group(&TASK, &strip_heredocs(command))
}

/// The task agent `aid`'s lines are filed under now, this line's own word aside: its correction, else its meta file's brief's `T<n>`.
fn current(events: &Path, payload: &Value, sid: &str, aid: &str) -> Option<String> {
    dispatches::corrected(events, sid, aid)
        .or_else(|| meta_brief(payload, aid).and_then(|b| first_group(&TASK_NAMED, &b)))
        .or_else(|| builder_named(payload, aid).and_then(|(_, tasks)| tasks.into_iter().next()))
}

/// The agent a payload re-numbers and its new task, which `dispatches::record` keeps for the agent's later lines (451 T106): the main
/// session's delivered `SendMessage` to an agent whose summary or message reads `T<new>, not T<old>`, `T<old>` the agent's task now
/// ([`CORRECTION`]); or a builder's own [`OWN_STEPS`] call naming a task neither its brief names nor it is filed under now. None for
/// any other payload.
pub(super) fn renumbered(payload: &Value, events: &Path) -> Option<(String, String)> {
    let field = |k: &str| text_of(payload.get(k));
    let input = |k: &str| text_of(payload.get("tool_input").and_then(|i| i.get(k)));
    let (sid, by) = (field("session_id"), field("agent_id"));
    let (aid, task) = match (
        field("tool_name").as_str(),
        field("hook_event_name").as_str(),
    ) {
        ("SendMessage", "PostToolUse") if by.is_empty() => {
            let to = input("to");
            if !dispatches::plain(&to) {
                return None;
            }
            let filed_as = current(events, payload, &sid, &to)?;
            let text = format!("{}\n{}", input("summary"), input("message"));
            let renamed = CORRECTION
                .captures_iter(&text)
                .map_while(Result::ok)
                .find(|c| c.get(2).is_some_and(|m| m.as_str() == filed_as))
                .and_then(|c| c.get(1).map(|m| m.as_str().to_owned()))?;
            (to, renamed)
        }
        ("Bash", "PreToolUse") if !by.is_empty() => {
            let task = own_step(&input("command"))?;
            // a task its brief names is the builder's own, no re-numbering: `451 T28+T29`'s `make decide T=T29` would have moved
            // the 64 lines after it to T29, 6 of them writes T28's closing checks would then set apart, measured 2026-11-21 (the
            // rule replayed over the night's 31,888 builder lines, its own steps read from their transcripts)
            let brief = meta_brief(payload, &by).unwrap_or_default();
            // and so is a bundle member its brief names only by its prompt's first line (451 T161: `449 sheet bundle (fresh 3)`)
            let briefed = TASK_NAMED
                .captures_iter(&brief)
                .map_while(Result::ok)
                .any(|c| c.get(1).is_some_and(|m| m.as_str() == task))
                || builder_named(payload, &by).is_some_and(|(_, tasks)| tasks.contains(&task));
            if briefed || current(events, payload, &sid, &by).as_deref() == Some(task.as_str()) {
                return None;
            }
            (by, task)
        }
        _ => return None,
    };
    Some((aid, task))
}

/// The one value every brief gives, None for none or a disagreement.
fn agreed(each: impl Iterator<Item = Option<String>>) -> Option<String> {
    let mut each = each.peekable();
    let first = each.peek()?.clone();
    each.all(|v| v == first).then_some(first).flatten()
}

/// An Agent call's prompt's first line, "" for any other call (a later line quotes other tasks).
fn prompt_head(payload: &Value) -> &str {
    if payload.get("tool_name").and_then(Value::as_str) != Some("Agent") {
        return "";
    }
    payload
        .get("tool_input")
        .and_then(|t| t.get("prompt"))
        .and_then(Value::as_str)
        .and_then(|p| p.lines().next())
        .unwrap_or_default()
}

/// One task start: its feature, its task, its epoch seconds where its `utc` parses.
pub type Start = (String, String, Option<f64>);

/// The task starts made in the tree at `root`, in file order: a row naming another tree is another worktree's builder's (451 T254,
/// the parallel trials of 2026-11-25: a line of one worktree was booked under the other's start), and a row naming none is from
/// before rows named their tree, read as before. A line that does not parse is skipped, a missing file is none. The one reader of
/// `task-starts.jsonl` the writer and `make events-refile` share (451 T56), with [`in_force`] and [`started`].
#[must_use]
pub fn starts(root: &Path) -> Vec<Start> {
    starts_where(root, &|e: &Value| {
        e.get("tree")
            .and_then(Value::as_str)
            .is_none_or(|t| crate::speckit::marks::same_tree(Path::new(t), root))
    })
}

/// Every task start of the clone, whichever tree made it: `make events-refile`'s reading, kept as it was before T254 (a re-file by
/// each line's own tree is not built here; the writer files a line by its tree as it is written).
#[must_use]
pub fn every_start(root: &Path) -> Vec<Start> {
    starts_where(root, &|_: &Value| true)
}

fn starts_where(root: &Path, keep: &dyn Fn(&Value) -> bool) -> Vec<Start> {
    // a start and its `make task-unstart` read as no start (451 T359)
    crate::speckit::marks::starts_text(&common_git_dir(root))
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l.trim()).ok())
        .filter(|e| keep(e))
        .map(|e| {
            let at = crate::iso::parse(&text_of(e.get("utc")));
            (text_of(e.get("feature")), text_of(e.get("task")), at)
        })
        .filter(|(f, t, _)| !f.is_empty() && !t.is_empty())
        .collect()
}

/// The task in force for `feature`: its last start.
#[must_use]
pub fn in_force(starts: &[Start], feature: &str) -> Option<String> {
    starts
        .iter()
        .rev()
        .find(|(f, _, _)| f == feature)
        .map(|(_, t, _)| t.clone())
}

/// The task the builder pool says holds the tree at `root` for `feature` (451 T332, T344): the first task of the registry's entry
/// for this tree (`builder_pool`, `<git common dir>/builder-pool.json`), where its feature - `make builder-tree`'s key, the
/// feature's number, or its directory's name - is the line's; None for a tree the pool does not list, a free one, and one held
/// for another feature or for none, which leave the start in force to answer as before. (Since 451 T529 a line no word files is
/// filed under the holder's feature, [`pool_feature`], so "another feature" is only a line whose own word named one.) A start the tree's builder made AFTER
/// the handout (`since`) is its own later word and names the task instead - a bundle's member, `make task-start T=<b>` in a tree
/// held for `a,b`; a start with no time is not one, and a handout whose time does not read is older than every timed start.
/// WHY the pool and not the start log alone: a handout moves no start, and a builder that never runs `make task-start` (a
/// measuring one; under two tiers, most) leaves the tree's last one in force - all 179 `Phase` lines of T315's check runs in
/// `diagram-backlog-t269` carried T285, five handouts old, observed 2026-11-26 (method: the 451 log's `Phase` lines of that tree
/// from 20:07 UTC counted by their task field, against `builder-pool.log`), so `make task-time` booked five tasks' build and
/// test seconds to one. WHY read here and not written by the handout as a start: the start log has other readers a start nobody
/// made would tell wrong - the landing's "was it started" (`land/ready.rs`), the stall check's (`set_down_hooks/stalls.rs`), the
/// time breakdown's first start of a task (`measure/task_time.rs`) - and its undo at release (`marks::live_starts`) would erase
/// the builder's own earlier starts of the task. One small file read a line that reaches this link.
fn pool_task(root: &Path, feature: &str, starts: &[Start]) -> Option<String> {
    let held = crate::builder_pool::read(&common_git_dir(root))
        .into_iter()
        .find(|t| crate::speckit::marks::same_tree(&t.tree, root))
        .filter(|t| feature == t.feature || feature.starts_with(&format!("{}-", t.feature)))?;
    let since = crate::iso::parse(&held.since);
    starts
        .iter()
        .rev()
        .find(|(f, _, _)| f == feature)
        .filter(|(_, _, at)| at.is_some() && *at >= since)
        .map(|(_, t, _)| t.clone())
        .or_else(|| held.tasks.first().cloned())
}

/// The feature directory the builder pool says holds the tree at `root` (451 T529): its registry entry's feature, read as a word of
/// the line's own ([`Specs::named`]); None for a tree the pool does not list, a free one, and a feature naming no one directory. Asked
/// after every word the line carries and before the fallback, so [`pool_task`] then names the holder's task. WHY: the pool tree
/// `diagram-backlog-b1` has no `.specify/feature.json`, so the fallback read no feature and the pool was never asked - 647 of its
/// `Phase` lines of 2026-11-27, T417's builder-checks and rust-test runs among them, went to `_unassigned.jsonl` with no task; and
/// `diagram-backlog-t269`, held for 461 T08, filed 6 lines in the 451 log under T285 by its stale `feature.json` (observed
/// 2026-11-27, method: every log's `Phase` lines counted by clone, log, task and fallback). The holder beats the session's
/// environment too: that is the whole session's, shared by every builder, where the registry names this tree's.
fn pool_feature(root: &Path, specs: &Specs) -> Option<String> {
    crate::builder_pool::read(&common_git_dir(root))
        .into_iter()
        .find(|t| crate::speckit::marks::same_tree(&t.tree, root))
        .filter(|t| !t.feature.trim().is_empty())
        .and_then(|t| specs.named(&t.feature))
}

/// The feature a task belongs to by the starts: the latest feature whose task in force it is, else the latest that started it at all -
/// a start more than [`STALE_START_S`] before `now` counting for neither (a start or a `now` with no time is never stale). The re-file
/// asks it with the starts made by a line's time and that time as `now`, so the two file a line alike (451 T56).
#[must_use]
pub fn started(starts: &[Start], task: &str, now: Option<f64>) -> Option<String> {
    let mut last: HashMap<&str, &str> = HashMap::new();
    for (f, t, _) in starts {
        last.insert(f, t);
    }
    let fresh = |at: &Option<f64>| match (at, now) {
        (Some(at), Some(now)) => now - at <= STALE_START_S,
        _ => true,
    };
    starts
        .iter()
        .rev()
        .find(|(f, t, at)| t == task && fresh(at) && last.get(f.as_str()) == Some(&task))
        .or_else(|| {
            starts
                .iter()
                .rev()
                .find(|(_, t, at)| t == task && fresh(at))
        })
        .map(|(f, _, _)| f.clone())
}

/// The page session a line is of (451 T167): its environment's `L7R_PAGE_SESSION`, else the line's own `session_id` where the clone's
/// `page-sessions/index.txt` lists it; None for any other session. WHY: 449 T330's page sessions' lines were booked to the mark's T312
/// and T328 (1,254 of 7e3b's lines, 141 of 2647's, 216 of f1d2's), observed 2026-11-23 (method: the 449 log's lines of the index's
/// four T330 ids, counted by task) - the hook that wrote them predated T161's environment read; the session id is in every payload.
fn page_session(
    payload: &Value,
    root: &Path,
    env: &dyn Fn(&str) -> Option<String>,
) -> Option<String> {
    env("L7R_PAGE_SESSION")
        .filter(|s| !s.trim().is_empty())
        .or_else(|| {
            let own = text_of(payload.get("session_id"));
            page_session_listed(root, &own).map(|_| own)
        })
}

/// Does the hook's environment name the session's feature (`feature_of`'s first two sources)?
fn declared(root: &Path, env: &dyn Fn(&str) -> Option<String>) -> bool {
    let own = env("L7R_FEATURE_DIRECTORY").unwrap_or_default();
    let named = env("SPECIFY_FEATURE").unwrap_or_default();
    let named = named.trim().trim_matches('/');
    !own.trim().trim_end_matches('/').is_empty()
        || (!named.is_empty() && root.join("specs").join(named).is_dir())
}

/// Where the payload's line is filed at `now` (the line's `t`); `carried` is the task its own command names (`T=`), `named` the feature
/// a gate tool names for its own line (451 T06: a landing's `F=`), read first, as a make command's `F=` is.
pub(super) fn filed(
    payload: &Value,
    carried: Option<&str>,
    named: Option<&str>,
    root: &Path,
    now: &str,
    env: &dyn Fn(&str) -> Option<String>,
) -> Filed {
    let specs = Specs {
        root,
        names: OnceCell::new(),
    };
    // a heredoc's body is text written to a file, never the command's own words: `F=` quoted in a test file filed a 451 builder's
    // `make rust-test` in 385's and 449's logs (451 T53; observed 2026-11-21, method: the dry run's moved lines' commands read from the
    // subagents' transcripts)
    let command = if text_of(payload.get("tool_name")) == "Bash" {
        strip_heredocs(&text_of(
            payload.get("tool_input").and_then(|t| t.get("command")),
        ))
    } else {
        String::new()
    };
    // a blank word names no feature (`specs/` itself is a directory)
    let said = named
        .filter(|w| !w.trim().is_empty())
        .and_then(|w| specs.named(w))
        .or_else(|| {
            if make_target(&command).is_empty() {
                None
            } else {
                first_group(&FEATURE_ARG, &command).and_then(|w| specs.named(&w))
            }
        });
    let events = log_path_in(root, "", env);
    let events = events.parent().unwrap_or(root);
    let briefs = briefs(payload, events, now);
    let starts = starts(root);
    let briefed = agreed(briefs.iter().map(|b| {
        brief_feature(b, &|n| specs.named(n), &|f| {
            starts.iter().any(|(s, _, _)| s == f)
        })
    }));
    // an Agent call whose description names no task: its prompt's first line's (451 T07, plan D6) - the task only, the feature
    // still the description's, since a prompt's line is free text a bare number in it could misfile
    // a closing step's own `T=` is its line's, as a tick's is (451 T106); an Agent call's own words - its description, its prompt's first
    // line - name the task it serves before the dispatching agent's correction does, and the correction comes before the agent's brief
    let carried = carried.map(str::to_owned).or_else(|| own_step(&command));
    let briefed_task = agreed(briefs.iter().map(|b| first_group(&TASK_NAMED, b)));
    let own_brief = text_of(payload.get("tool_name")) == "Agent"
        && !text_of(payload.get("tool_input").and_then(|t| t.get("description"))).is_empty();
    let head = || first_group(&TASK_NAMED, prompt_head(payload));
    let task = carried
        .clone()
        .or_else(|| {
            own_brief
                .then(|| briefed_task.clone().or_else(head))
                .flatten()
        })
        .or_else(|| {
            dispatches::corrected(
                events,
                &text_of(payload.get("session_id")),
                &text_of(payload.get("agent_id")),
            )
        })
        .or(briefed_task)
        .or_else(head);
    // A LINE IS ITS EDITOR'S (451 T161): an agent whose own description names no task is booked by its builder's reading - a bundle's
    // `449 sheet bundle (fresh 3): ...` by its prompt's first line, `449 bundle T312, T313, ...`; a review it launched by it - and a page
    // session's line by its brief; the clone's mark (below) only for the main session's own. WHY: the sheet bundle's four files were
    // booked to the mark's T317, the record bundle's, and refused that bundle's landing at land-alone's own-edits step (observed
    // 2026-11-22, method: the 449 log's edit lines of `reviews/owed.rs` and `gen_tests_seat.rs`, `by` a6ed2241ba6a59166, read against
    // its meta file and transcript).
    let aid = text_of(payload.get("agent_id"));
    // the page session, read once a line and only where no link before it asks (451 T167, [`page_session`])
    let listed = OnceCell::new();
    let page = || {
        listed
            .get_or_init(|| page_session(payload, root, env))
            .clone()
    };
    let mut theirs = None;
    let task = task.or_else(|| {
        let (feature, task) = Some(&aid)
            .filter(|a| !a.is_empty())
            .and_then(|a| builder_named(payload, a))
            .and_then(|(n, tasks)| Some((specs.named(&n), tasks.into_iter().next()?)))
            .or_else(|| {
                let (f, t) = page_session_brief(root, &page()?)?;
                Some((Some(f), t))
            })?;
        theirs = feature;
        Some(task)
    });
    // a builder's `make task-add F=449` is the builder's own time: its `F=` names where the call writes, not whose task it serves, and
    // filed by it the line took 449 from the `F=` and T36 from 451's brief (451 T53). The brief wins unless the command carries its own
    // `T=` - the re-file's rule (`make events-refile`, BY BRIEF), so the writer and the re-file agree
    let feature = if carried.is_some() {
        said.or(briefed)
    } else {
        briefed.or(said)
    }
    .or(theirs)
    .or_else(|| {
        task.as_deref()
            .and_then(|t| started(&starts, t, crate::iso::parse(now)))
    })
    .or_else(|| pool_feature(root, &specs));
    let (feature, fallback) = match feature {
        Some(f) => (f, false),
        // a session that declares its feature (a page session's `L7R_FEATURE_DIRECTORY`, a `SPECIFY_FEATURE` naming a feature) is
        // that feature's whole: not marked, the mark is for feature.json's guess
        None => (feature_of(root, env), !declared(root, env)),
    };
    let task = task.or_else(|| {
        if feature.is_empty() || !aid.is_empty() || page().is_some() {
            None
        } else {
            pool_task(root, &feature, &starts).or_else(|| in_force(&starts, &feature))
        }
    });
    Filed {
        feature,
        task,
        fallback,
    }
}
