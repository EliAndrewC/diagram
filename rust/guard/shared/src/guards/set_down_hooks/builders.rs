//! THE BUILDERS AND THE GM'S QUESTIONS (449 T268): which running agents are builders and of which tasks - one, or a bundle's - and which
//! open tasks an open GM question holds; split out of `set_down_hooks.rs` past the file-scale bar.

use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;

use serde_json::Value;

use super::{re, rows, BRIEF, TASK_ID};
use crate::state::field;

/// Does a task wait on the GM's answer (449 T268, the session's note 2026-11-22: "a task whose line waits on the GM (T252, filed for his
/// answer) shouldn't be named as the next to start")? An open question of the feature's GM-review queue (`gm-review.jsonl`, a
/// `question` row `owed` or `kept`, `make gm-review`'s two open states) names it in its text - T252's kept question ends "(T252)".
/// Its end is recorded: the GM's answer moves the row out of those states, and the task can start. The question's text alone is read,
/// not its `source`, which names the task that asked it (T252's names T228).
pub(super) fn asks_the_gm(root: &Path, feature: &str, id: &str) -> Result<bool, String> {
    let named = re(&format!(r"\b{}\b", fancy_regex::escape(id)));
    Ok(
        rows(&root.join("specs").join(feature).join("gm-review.jsonl"))?
            .iter()
            .any(|r| {
                field(r, "kind") == "question"
                    && matches!(field(r, "status"), "owed" | "kept")
                    && named.is_match(field(r, "question")).unwrap_or(false)
            }),
    )
}

/// The (feature number, tasks) a builder builds, read from agent `id`'s meta file in the session's `subagents` directory `dir`; None
/// for any agent but a builder - one the session dispatched (`spawnDepth` 1) whose description opens with a feature number. Its tasks
/// are the ids its description names before its first colon (`449 T271: ...`, `449 bundle T258, T268, T269: ...`); a bundle brief
/// naming none (`449 record bundle: nine ...`) is read for the ids of its prompt's first line, the first record of the agent's own
/// transcript (`Feature 449, a bundle of nine ...: T254, T255, ...`). WHY (449 T268, the session's note 2026-11-22: "A builder started
/// under a bundle mark ... must count as running for its bundle's tasks"): the old `<feature> T<n>` brief matched neither live bundle
/// description, so the Stop hook counted 1 of 3 builders running while three ran. `builder_stop_hooks` (451 T84) reads it too.
#[must_use]
pub fn builder_brief(dir: &Path, id: &str) -> Option<(String, Vec<String>)> {
    let description = dispatched(dir, id)?;
    let number = BRIEF.captures(&description).ok().flatten()?[1].to_owned();
    let head = description.split(':').next().unwrap_or_default();
    let mut tasks = task_ids(head);
    if tasks.is_empty() {
        tasks = task_ids(&prompt_head(&dir.join(format!("agent-{id}.jsonl"))));
    }
    (!tasks.is_empty()).then_some((number, tasks))
}

/// A task id, and the feature number before it where one stands there (`check_bundle_hooks/own.rs`'s and `left/whose.rs`'s reading).
static NAMED: LazyLock<Regex> = LazyLock::new(|| re(r"(?:\b(\d{3})\s+)?\b(T\d+[a-z]?)\b"));
/// A page-session brief's file name: `t197-g2-checks.md`.
static BRIEF_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"^t(\d+[a-z]?)-"));

/// The brief the clone at `root`'s `page-sessions/index.txt` lists for session `sid` (its last line for `sid`), None where it lists
/// none: whether a line's session is a page session at all (451 T167, `event_log_hooks/filed.rs`), apart from whether its brief names a
/// task.
#[must_use]
pub fn page_session_listed(root: &Path, sid: &str) -> Option<PathBuf> {
    let index = std::fs::read_to_string(
        crate::guards::event_log_hooks::common_git_dir(root).join("page-sessions/index.txt"),
    )
    .ok()?;
    index.lines().rev().find_map(|l| {
        l.split_once(' ')
            .filter(|(id, _)| *id == sid)
            .map(|(_, path)| PathBuf::from(path.trim()))
    })
}

/// The (feature directory, task) page session `sid`'s brief names, the clone at `root` holding its `page-sessions/index.txt` (`<sid>
/// <brief path>`, the runner's `L7R_PAGE_SESSION` its first column, its last line for `sid` read): the feature its `specs/<feature>/`
/// path names, the task its first line names (`# Brief - feature 449 task T197, ...`), else its file name's (`t197-g2-checks.md`). None
/// where any of those is missing. The one reader, which a check's own task (449 T258, `check_bundle_hooks/own.rs`) and the event log's
/// booking of a page session's lines (451 T161, `event_log_hooks/filed.rs`) share.
#[must_use]
pub fn page_session_brief(root: &Path, sid: &str) -> Option<(String, String)> {
    let brief = page_session_listed(root, sid)?;
    let parts: Vec<String> = brief
        .components()
        .map(|c| c.as_os_str().to_string_lossy().into_owned())
        .collect();
    let at = parts.iter().rposition(|p| p == "specs")?;
    let feature = parts.get(at + 1)?.clone();
    let first = std::fs::read_to_string(&brief).unwrap_or_default();
    let line = first.lines().next().unwrap_or_default();
    let task = NAMED
        .captures(line)
        .ok()
        .flatten()
        .map(|c| c[2].to_owned())
        .or_else(|| {
            let name = brief.file_name()?.to_string_lossy().into_owned();
            BRIEF_FILE
                .captures(&name)
                .ok()
                .flatten()
                .map(|c| format!("T{}", &c[1]))
        })?;
    Some((feature, task))
}

/// The tasks agent `id` builds by its builder's reading ([`builder_brief`]), else by the builder that dispatched it (its meta's
/// `parentAgentId`, a review a builder launched), in the session's `subagents` directory `dir`: the feature number and tasks (451 T161,
/// the event log's booking of a line whose agent's own description names no task).
#[must_use]
pub fn agent_builder(dir: &Path, id: &str) -> Option<(String, Vec<String>)> {
    builder_brief(dir, id).or_else(|| builder_brief(dir, &parent_of(dir, id)?))
}

/// Agent `id`'s meta file in the session's `subagents` directory `dir`, read.
fn meta(dir: &Path, id: &str) -> Option<Value> {
    serde_json::from_str(&std::fs::read_to_string(dir.join(format!("agent-{id}.meta.json"))).ok()?)
        .ok()
}

/// The agent that dispatched agent `id` (its meta's `parentAgentId`): None for one the session dispatched, or one with no meta.
pub(super) fn parent_of(dir: &Path, id: &str) -> Option<String> {
    Some(meta(dir, id)?.get("parentAgentId")?.as_str()?.to_owned())
}

/// Whether agent `id` is one the session itself dispatched (its meta's `spawnDepth` 1), never a sub-agent's own (451 T183: the
/// findings guard waits on the session's reviews alone).
#[must_use]
pub fn session_dispatched(dir: &Path, id: &str) -> bool {
    meta(dir, id).is_some_and(|m| m.get("spawnDepth").and_then(Value::as_u64) == Some(1))
}

/// The description of agent `id`, one the session dispatched (its meta's `spawnDepth` 1); None for any other.
fn dispatched(dir: &Path, id: &str) -> Option<String> {
    let meta = meta(dir, id)?;
    if meta.get("spawnDepth").and_then(Value::as_u64) != Some(1) {
        return None;
    }
    Some(meta.get("description")?.as_str()?.to_owned())
}

/// A range's widest span read member by member (451 T156): a CONVENTION past every bundle seen (T289-T300, twelve); a longer one, or
/// one written backwards or with a letter, is read as its two ends, as before.
const SPAN: u64 = 200;

/// Every task id in `text`, in order, each once; a range (`T278-T281`) is each of its members, its first id's width kept (`T02-T04`).
/// WHY (451 T156, 2026-11-22): `449 T289-T300 bundle (fresh): ...` read as T289 and T300 alone, so the ten between were named free to
/// start while their builder ran.
pub(super) fn task_ids(text: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for c in TASK_ID.captures_iter(text).map_while(Result::ok) {
        let (from, a) = (&c[1], &c[2]);
        let mut each = vec![format!("T{from}{a}")];
        if let Some(to) = c.get(3).map(|m| m.as_str()) {
            let b = c.get(4).map_or("", |m| m.as_str());
            let (lo, hi) = (from.parse().unwrap_or(0_u64), to.parse().unwrap_or(0_u64));
            if a.is_empty() && b.is_empty() && hi > lo && hi - lo <= SPAN {
                each = (lo..=hi)
                    .map(|n| format!("T{n:0w$}", w = from.len()))
                    .collect();
            } else {
                each.push(format!("T{to}{b}"));
            }
        }
        for t in each {
            if !out.contains(&t) {
                out.push(t);
            }
        }
    }
    out
}

/// The first line of an agent's prompt: its own transcript's first record's text, "" where it has none.
fn prompt_head(transcript: &Path) -> String {
    let Ok(file) = File::open(transcript) else {
        return String::new();
    };
    // A line that cannot be read leaves `first` unparsable (empty, or a valid prefix cut short), so it reads as no prompt below.
    let mut first = String::new();
    let _ = BufReader::new(file).read_line(&mut first);
    let record: Value = serde_json::from_str(&first).unwrap_or(Value::Null);
    let content = &record["message"]["content"];
    let text = content.as_str().map_or_else(
        || {
            content
                .as_array()
                .and_then(|blocks| blocks.iter().find_map(|b| b["text"].as_str()))
                .unwrap_or_default()
        },
        |t| t,
    );
    text.lines().next().unwrap_or_default().to_owned()
}
