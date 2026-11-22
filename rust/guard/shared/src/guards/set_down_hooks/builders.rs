//! THE BUILDERS AND THE GM'S QUESTIONS (449 T268): which running agents are builders and of which tasks - one, or a bundle's - and which
//! open tasks an open GM question holds; split out of `set_down_hooks.rs` past the file-scale bar.

use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

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
    let meta: Value = serde_json::from_str(
        &std::fs::read_to_string(dir.join(format!("agent-{id}.meta.json"))).ok()?,
    )
    .ok()?;
    if meta.get("spawnDepth").and_then(Value::as_u64) != Some(1) {
        return None;
    }
    let description = meta.get("description")?.as_str()?;
    let number = BRIEF.captures(description).ok().flatten()?[1].to_owned();
    let head = description.split(':').next().unwrap_or_default();
    let mut tasks = task_ids(head);
    if tasks.is_empty() {
        tasks = task_ids(&prompt_head(&dir.join(format!("agent-{id}.jsonl"))));
    }
    (!tasks.is_empty()).then_some((number, tasks))
}

/// Every task id in `text`, in order, each once.
fn task_ids(text: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for c in TASK_ID.captures_iter(text).map_while(Result::ok) {
        if !out.iter().any(|t| *t == c[1]) {
            out.push(c[1].to_owned());
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

/// A running builder: its feature number and the tasks it builds (one, or a bundle's).
pub(super) type Builder = (String, Vec<String>);

/// The builders still running, each by [`still_running`]'s rule over ONE reading of the transcript (a transcript reached 206 MB): its
/// (feature number, tasks), sorted - one a builder, a bundle's builder one however many tasks it holds. [`running`] alone would not do -
/// it leaves out an interim agent whenever another plainly runs.
pub(super) fn builders(path: &Path) -> std::io::Result<Vec<Builder>> {
    let read = read_in_order(path, "")?;
    let dir = subagents(path);
    let mut known = HashMap::new();
    let mut out = Vec::new();
    for id in read.ids.keys() {
        if let Some(built) = builder_brief(&dir, id) {
            if runs(&read, &dir, id, &mut known)? {
                out.push(built);
            }
        }
    }
    out.sort();
    out.dedup();
    Ok(out)
}
