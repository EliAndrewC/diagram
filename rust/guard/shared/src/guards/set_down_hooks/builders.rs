//! THE BUILDERS AND THE GM'S QUESTIONS (449 T268): which running agents are builders and of which tasks - one, or a bundle's - and which
//! open tasks an open GM question holds; split out of `set_down_hooks.rs` past the file-scale bar.

use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;

use serde_json::Value;

use super::{re, read_in_order, rows, runs, subagents, BRIEF, TASK_ID};
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
    builder_brief(dir, id).or_else(|| {
        let meta: Value = serde_json::from_str(
            &std::fs::read_to_string(dir.join(format!("agent-{id}.meta.json"))).ok()?,
        )
        .ok()?;
        let parent = meta.get("parentAgentId")?.as_str()?;
        builder_brief(dir, parent)
    })
}

/// The description of agent `id`, one the session dispatched (its meta's `spawnDepth` 1); None for any other.
fn dispatched(dir: &Path, id: &str) -> Option<String> {
    let meta: Value = serde_json::from_str(
        &std::fs::read_to_string(dir.join(format!("agent-{id}.meta.json"))).ok()?,
    )
    .ok()?;
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
fn task_ids(text: &str) -> Vec<String> {
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

/// A brief's head that names a landing (`449 batch landing: ...`), never `land-alone` or `land-tooling`.
static LANDS: LazyLock<Regex> = LazyLock::new(|| re(r"\b(?:land|landing|lands)\b(?!-)"));
/// A prompt's first line that runs `make land` (never `make land-tooling` or `make land-stop`).
static MAKE_LAND: LazyLock<Regex> = LazyLock::new(|| re(r"\bmake land(?![-\w])"));

/// Does agent `id` run a landing (451 T156): one the session dispatched whose description names a landing before its first colon, or
/// whose prompt's first line runs `make land`. WHY (2026-11-22): `449 batch landing: clear the six refusals and land` named no task, so
/// it read as no builder, and the Stop hook named a task-start through a 35-task landing - which the round arbiter's ruling
/// (ask:set-down-449-mid-landing) forbids. A builder whose brief only mentions landing past its colon is not one: it fails toward
/// naming the start, which the session sees.
fn lander(dir: &Path, id: &str) -> bool {
    dispatched(dir, id).is_some_and(|d| {
        LANDS
            .is_match(d.split(':').next().unwrap_or_default())
            .unwrap_or(false)
            || MAKE_LAND
                .is_match(&prompt_head(&dir.join(format!("agent-{id}.jsonl"))))
                .unwrap_or(false)
    })
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

/// A running builder: its feature number and the tasks it builds (one, or a bundle's).
pub(super) type Builder = (String, Vec<String>);

/// The builders still running, each by [`still_running`]'s rule over ONE reading of the transcript (a transcript reached 206 MB): its
/// (feature number, tasks), sorted - one a builder, a bundle's builder one however many tasks it holds - and whether a running agent
/// runs a landing ([`lander`], 451 T156). [`running`] alone would not do - it leaves out an interim agent whenever another plainly runs.
pub(super) fn builders(path: &Path) -> std::io::Result<(Vec<Builder>, bool)> {
    let read = read_in_order(path, "")?;
    let dir = subagents(path);
    let mut known = HashMap::new();
    let mut out = Vec::new();
    let mut landing = false;
    for id in read.ids.keys() {
        let built = builder_brief(&dir, id);
        let lands = lander(&dir, id);
        if (built.is_some() || lands) && runs(&read, &dir, id, &mut known)? {
            out.extend(built);
            landing |= lands;
        }
    }
    out.sort();
    out.dedup();
    Ok((out, landing))
}

/// Does a landing run in this clone (451 T156): a process under `proc` (`/proc`) whose working directory is the clone `root`, or its
/// landing worktree (`<root>-land`, land-alone's), running `l7r-gate land` (not `--stop`) or `land-alone.sh`. A landing a builder runs
/// in the background shows in neither the session's transcript nor any agent's brief. A process whose files cannot be read is not one.
pub(super) fn landing_process(root: &Path, proc: &Path) -> bool {
    let canon = |p: &Path| p.canonicalize().unwrap_or_else(|_| p.to_path_buf());
    let root = canon(root);
    let worktree = PathBuf::from(format!("{}-land", root.display()));
    let base = |a: &String| a.rsplit('/').next().unwrap_or_default().to_owned();
    std::fs::read_dir(proc)
        .into_iter()
        .flatten()
        .flatten()
        .any(|entry| {
            let Ok(cmdline) = std::fs::read(entry.path().join("cmdline")) else {
                return false;
            };
            let cwd = canon(&entry.path().join("cwd"));
            let args: Vec<String> = cmdline
                .split(|b| *b == 0)
                .map(|a| String::from_utf8_lossy(a).into_owned())
                .collect();
            let gate = base(&args[0]) == "l7r-gate"
                && args.get(1).is_some_and(|a| a == "land")
                && args.get(2).is_none_or(|a| a != "--stop");
            (cwd == root || cwd == worktree)
                && (gate || args.iter().any(|a| base(a) == "land-alone.sh"))
        })
}
