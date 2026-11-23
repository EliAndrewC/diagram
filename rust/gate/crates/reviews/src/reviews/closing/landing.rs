//! A round-arbiter tooling fix that lands WITH its task (feature 451 T182).
//!
//! WHY: a fix built in Rust inside the very task being landed could not be settled (observed 2026-11-23, 451 T177 and
//! `ask:guard-wordings-sleep-and-slot`): `make arbiter-fix-done` wants its test on main; `LAND=` goes through `make land-tooling`, which
//! rightly refuses `rust/` (it skips the full gate); and the task's own `make land` was refused by [`super::fix_hold`] until the fix was
//! settled. So `make arbiter-fix-done ... LANDING=<task>` records the fix as PENDING here - its files and test committed in the clone,
//! no done row written - and the landing of that task ([`fix_hold_landing`] at its first pass, [`settle_landing`] before its ticks)
//! writes the done row into its own tick commit: fix and tick reach main in one push, or neither does ([`Settled::undo`], and a failed
//! push's revert). The rows go in BEFORE the ticks because the closing check at a feature's last tick reads the open fixes too.
//!
//! The pending entries live in the clone's git directory (`arbiter-fix-landing.json`), never in the tree: they are the clone's
//! landing's, and the done row that ends them is what main reads.

#[cfg(test)]
mod tests;

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::checks;
use serde_json::{Map, Value};

use super::super::gm_review::name;
use super::{hold_of, open_fixes};

/// The pending entries' file, under the clone's git directory.
pub const PENDING: &str = "arbiter-fix-landing.json";

#[expect(
    clippy::needless_pass_by_value,
    reason = "`map_err` hands the error by value"
)]
fn io(e: std::io::Error) -> String {
    format!("{PENDING}: {e}")
}

fn text(e: &Value, k: &str) -> String {
    e.get(k).and_then(Value::as_str).unwrap_or("").to_owned()
}

fn file(root: &Path) -> PathBuf {
    checks::common_dir(root).join(PENDING)
}

/// Every pending entry, oldest first; a file missing or not a JSON list reads as none.
#[must_use]
pub fn pending(root: &Path) -> Vec<Value> {
    std::fs::read_to_string(file(root))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| v.as_array().cloned())
        .unwrap_or_default()
}

fn save(root: &Path, entries: &[Value]) -> Result<(), String> {
    let path = file(root);
    if entries.is_empty() {
        return match std::fs::remove_file(&path) {
            Err(e) if e.kind() != std::io::ErrorKind::NotFound => Err(io(e)),
            _ => Ok(()),
        };
    }
    std::fs::write(&path, Value::Array(entries.to_vec()).to_string() + "\n").map_err(io)
}

/// `entry` kept pending, in place of any entry for its trigger.
///
/// # Errors
/// The file cannot be written.
pub fn add(root: &Path, entry: Value) -> Result<(), String> {
    let trigger = text(&entry, "trigger");
    let mut all = pending(root);
    all.retain(|e| text(e, "trigger") != trigger);
    all.push(entry);
    save(root, &all)
}

/// The pending entries that land with one of `tasks` of the feature named `feature`.
fn landing<'a>(all: &'a [Value], feature: &str, tasks: &[String]) -> Vec<&'a Value> {
    all.iter()
        .filter(|e| text(e, "feature") == feature && tasks.contains(&text(e, "task")))
        .collect()
}

/// [`super::fix_hold`] of `d`, the fixes pending on one of `tasks` (the landing's) left out: the landing carries them.
#[must_use]
pub fn fix_hold_landing(d: &Path, root: &Path, tasks: &[String]) -> String {
    let all = pending(root);
    let carried: Vec<String> = landing(&all, &name(d), tasks)
        .iter()
        .map(|e| text(e, "trigger"))
        .collect();
    let fixes: Vec<(String, String)> = open_fixes(d)
        .into_iter()
        .filter(|(t, _)| !carried.contains(t))
        .collect();
    hold_of(&fixes)
}

/// What [`settle_landing`] wrote: every trigger the landing carries (`triggers`, forgotten once it pushes), the (trigger, task) of each
/// done row written, and each log written with its content before.
pub struct Settled {
    pub triggers: Vec<String>,
    pub rows: Vec<(String, String)>,
    pub homes: Vec<(PathBuf, Vec<u8>)>,
}

impl Settled {
    /// Every log put back as it was: the landing did not push.
    ///
    /// # Errors
    /// A log cannot be written.
    pub fn undo(&self) -> Result<(), String> {
        for (path, before) in &self.homes {
            std::fs::write(path, before).map_err(io)?;
        }
        Ok(())
    }

    /// The landing's line for its rows, "" for none.
    #[must_use]
    pub fn said(&self) -> String {
        self.rows.iter().fold(String::new(), |mut out, (t, task)| {
            let _ = writeln!(out, "land: {t} settled in the tick commit (the round arbiter's tooling fix, landed with {task})");
            out
        })
    }
}

/// The done row of each fix pending on one of `tasks` of feature `d`, appended to its home's `arbiter.jsonl` where it is still open
/// there (one settled meanwhile by hand is only forgotten).
///
/// # Errors
/// A log cannot be written.
pub fn settle_landing(
    root: &Path,
    d: &Path,
    tasks: &[String],
    when: &str,
) -> Result<Settled, String> {
    let feature = name(d);
    let all = pending(root);
    let mut out = Settled {
        triggers: Vec::new(),
        rows: Vec::new(),
        homes: Vec::new(),
    };
    for e in landing(&all, &feature, tasks) {
        let (trigger, task) = (text(e, "trigger"), text(e, "task"));
        out.triggers.push(trigger.clone());
        let home = root.join("specs").join(text(e, "home"));
        if !open_fixes(&home).iter().any(|(t, _)| *t == trigger) {
            continue;
        }
        let log = home.join("arbiter.jsonl");
        let before = std::fs::read(&log).map_err(io)?;
        if !out.homes.iter().any(|(p, _)| *p == log) {
            out.homes.push((log.clone(), before.clone()));
        }
        let mut row = Map::new();
        row.insert("fix_of".to_owned(), Value::from(trigger.as_str()));
        row.insert("status".to_owned(), Value::from("done"));
        let note = format!("{} (landed with {feature} {task})", text(e, "note"));
        row.insert("note".to_owned(), Value::from(note));
        row.insert("test".to_owned(), Value::from(text(e, "test")));
        row.insert("utc".to_owned(), Value::from(when));
        let mut bytes = before;
        if bytes.last().is_some_and(|b| *b != b'\n') {
            bytes.push(b'\n');
        }
        bytes.extend(Value::Object(row).to_string().into_bytes());
        bytes.push(b'\n');
        std::fs::write(&log, bytes).map_err(io)?;
        out.rows.push((trigger, task));
    }
    Ok(out)
}

/// `triggers` no longer pending: their landing pushed.
///
/// # Errors
/// The file cannot be written.
pub fn forget(root: &Path, triggers: &[String]) -> Result<(), String> {
    let mut all = pending(root);
    all.retain(|e| !triggers.contains(&text(e, "trigger")));
    save(root, &all)
}
