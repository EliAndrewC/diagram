//! `make events-refile RETASK=<session id>` (feature 451 T168): the lines of a named page session re-booked, within their own log, to
//! the task its brief names. WHY: the hook before 451 T167 booked a page session's lines to the clone's mark, so 449 T330's sessions
//! (7e3b, 2647, f1d2) sat under T312 and T328 and `make where-time` credited their minutes there; the refile's two rules move lines
//! across features and never re-task one within a feature (observed 2026-11-23, method: the 449 log's lines of those ids counted by
//! task). The task and feature are the shared reader's (`set_down_hooks::page_session_brief`, 451 T161), the clone's `page-sessions/index.txt`;
//! the log rewritten is the brief's feature's, in `from`. Idempotent: a line already on the brief's task is not changed, so a second run
//! changes nothing. A session the index does not list, or whose brief names no task, is reported and left.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::Path;

use serde_json::Value;

use super::{reply, write_back};
use crate::Reply;

/// One session re-booked: its lines by task before, and the task they go to.
fn session(root: &Path, from: &Path, sid: &str, dry: bool, out: &mut String) -> Result<(), String> {
    let Some((feature, task)) = l7r_shared::guards::set_down_hooks::page_session_brief(root, sid)
    else {
        let _ = writeln!(
            out,
            "retask: {sid}: no page-session brief naming a task in the index, left"
        );
        return Ok(());
    };
    let path = from.join(format!("{feature}.jsonl"));
    let bytes = std::fs::read(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    let body = String::from_utf8_lossy(&bytes);
    let mut before: BTreeMap<String, usize> = BTreeMap::new();
    let mut kept = String::new();
    let mut changed = 0;
    for raw in body.split_inclusive('\n') {
        let parsed = serde_json::from_str::<Value>(raw.trim_end_matches('\n'));
        let Ok(Value::Object(mut e)) = parsed else {
            kept.push_str(raw);
            continue;
        };
        if e.get("sid").and_then(Value::as_str) != Some(sid) {
            kept.push_str(raw);
            continue;
        }
        let was = e
            .get("task")
            .and_then(Value::as_str)
            .unwrap_or("-")
            .to_owned();
        *before.entry(was.clone()).or_default() += 1;
        if was == task {
            kept.push_str(raw);
        } else {
            changed += 1;
            e.insert("task".into(), Value::from(task.clone()));
            kept.push_str(&Value::Object(e).to_string());
            kept.push('\n');
        }
    }
    let counts: Vec<String> = before.iter().map(|(t, n)| format!("{t} {n}")).collect();
    let _ = writeln!(
        out,
        "retask: {sid} in {feature}: before [{}], after [{task} {}], {changed} re-booked{}",
        counts.join(", "),
        before.values().sum::<usize>(),
        if dry {
            " (dry run: nothing written)"
        } else {
            ""
        }
    );
    if dry || changed == 0 {
        return Ok(());
    }
    write_back(&path, kept.into_bytes(), bytes.len())
}

/// The command's `--retask` mode: each named session re-booked, the counts printed.
pub fn cli(root: &Path, from: &Path, sids: &[String], dry: bool) -> Reply {
    let mut out = String::new();
    for sid in sids {
        if let Err(why) = session(root, from, sid, dry, &mut out) {
            return reply(out, format!("retask: {why}\n"), 1);
        }
    }
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
