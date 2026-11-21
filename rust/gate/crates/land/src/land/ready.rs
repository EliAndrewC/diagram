//! A READY TASK LANDS BESIDE THE MARK'S (feature 451 T101). WHY: with builders rolling (T88) the clone's one active-task mark names
//! whichever task started last, and the hold (`shared::speckit::holding`, 405 D4) refused any landing that did not tick it - T81, T88
//! and T93, each CLEAR and closing-checked, were refused "held by T97" at 18:32:27Z on 2026-11-21 (the 451 event log's `end` line, code
//! 2), T97 started 61 s before; the session moved the mark to T88 by hand (a task-start at 18:32:49Z), landed them at 18:40:27Z and
//! started T97 again at 18:41:08Z (the clone's `task-starts.jsonl`).
//!
//! WHAT THE MARK STILL HOLDS: the hold stopped a landing from pushing the worked task's half-done commits. So a landing is held by the
//! mark's task unless EACH task it lands is ready beside it: started in this clone (`task-starts.jsonl`, the record the event log files
//! by, never the mark), its plan section carrying a current CLEAR verdict (`l7r-gate plan decided <root> <feature> <task>`, the
//! builder-stop guard's question), and its files its own - no file of the delta (`origin/main...HEAD`) holds an edit another open task's
//! line names, made after the file last landed and before the delta's last commit of it. The feature's plan.md, tasks.md and
//! plan-review.json are judged by section instead (`scoped.rs` commits only the landing's own), and the review ledger by nobody: every
//! task writes them. A landing ruled ready names its tasks in `L7R_LAND_READY` to the push, where `sync-with-main.sh` and the CI merge
//! ask the same hold again; the ruling reads the delta and the tasks, never which task the mark names, so a task started while the gate
//! runs moves nothing.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use l7r_shared::py_text::strip;
use serde_json::Value;

use super::{head, name_of, py_read, rel_of, Land};

/// The feature's files a landing commits by section (`scoped.rs`): each holds every open task's section, line or verdict.
pub(super) const SECTIONED: [&str; 3] = ["plan.md", "tasks.md", "plan-review.json"];
/// The review ledger, which every task's passes write a row of.
const LEDGER: &str = "dev/review-ledger.md";
/// How far back a file's last landed change is read; an edit older than this, or than its file's last landed change, is landed.
const LANDED_SINCE: &str = "--since=7.days";

impl Land {
    /// What holds the landing of `tasks`: the mark's open task (`holding`), unless each of them is ready beside it.
    pub(super) fn hold(&self, d: &Path, tasks: &[String]) -> Result<String, String> {
        let held = self
            .inproc
            .holding(&d.to_string_lossy(), &tasks.join(" "), &self.root);
        let held = strip(&(held.stdout + &held.stderr)).to_owned();
        if held.is_empty() {
            return Ok(held);
        }
        let why = self.not_ready(d, tasks)?;
        if why.is_empty() {
            self.ready.set(true);
            self.say(&format!(
                "land: {} ready beside the active task - each started, its plan section CLEAR, its files its own (451 T101); it holds: {}",
                tasks.join(" "),
                head(&held, 200)
            ));
            return Ok(String::new());
        }
        Ok(format!(
            "{held} - and {} cannot land beside it (451 T101): {}",
            tasks.join(" "),
            why.join("; ")
        ))
    }

    /// The push's export of the ruling: `L7R_LAND_READY` naming the tasks, where the mark holds them now (a task started while the
    /// gate ran) and they are ready beside it - asked again here only where the first pass did not rule.
    pub(super) fn export_ready(&self, d: &Path, tasks: &[String]) -> Result<(), String> {
        if !self.ready.get() {
            let held = self
                .inproc
                .holding(&d.to_string_lossy(), &tasks.join(" "), &self.root);
            if strip(&held.stdout).is_empty() || !self.not_ready(d, tasks)?.is_empty() {
                return Ok(());
            }
        }
        self.export("L7R_LAND_READY", &tasks.join(" "));
        Ok(())
    }

    /// Why `tasks` cannot land beside another started task: each reason, none where they can.
    pub(super) fn not_ready(&self, d: &Path, tasks: &[String]) -> Result<Vec<String>, String> {
        let name = name_of(d);
        let number = name
            .split('-')
            .next()
            .unwrap_or_default()
            .trim_start_matches('0');
        let common = self.common_dir()?;
        let started = started_tasks(&common.join("task-starts.jsonl"), &name);
        let mut why = Vec::new();
        for t in tasks {
            if !started.contains(t.as_str()) {
                why.push(format!(
                    "{t} was never started in this clone (make task-start F={number} T={t})"
                ));
            }
        }
        let root = self.root.to_string_lossy().into_owned();
        for t in tasks {
            let (rc, out) = self.run(&[&self.gate(), "plan", "decided", &root, &name, t], &[])?;
            if rc != 0 {
                why.push(strip(&out).to_owned());
            }
        }
        for (file, (task, at)) in self.others_in_delta(d, tasks, &common)? {
            why.push(format!(
                "{file} in the delta holds {task}'s edit of {at}, not theirs - land them together (make land F={number} T=\"{} {task}\")",
                tasks.join(" ")
            ));
        }
        Ok(why)
    }

    /// The clone's git common directory: the landing worktree shares the clone's (`<clone>/.git`).
    fn common_dir(&self) -> Result<PathBuf, String> {
        let (_, out) = self.run(
            &[
                "git",
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            ],
            &[],
        )?;
        Ok(PathBuf::from(strip(&out)))
    }

    /// Each delta file, but the sectioned ones and the ledger, that holds another open task's edit: `{file: (task, its time)}`.
    fn others_in_delta(
        &self,
        d: &Path,
        tasks: &[String],
        common: &Path,
    ) -> Result<BTreeMap<String, (String, String)>, String> {
        let rel = rel_of(&self.root, d);
        let judged: BTreeSet<String> = self
            .delta_names()?
            .into_iter()
            .filter(|n| n != LEDGER && !SECTIONED.iter().any(|f| *n == format!("{rel}/{f}")))
            .collect();
        let mut found = BTreeMap::new();
        if judged.is_empty() {
            return Ok(found);
        }
        let open = open_tasks(&py_read(&d.join("tasks.md"))?);
        let base = strip(
            &self
                .run(&["git", "merge-base", "origin/main", "HEAD"], &[])?
                .1,
        )
        .to_owned();
        let landed = last_changes(
            &self
                .run(
                    &[
                        "git",
                        "log",
                        "--format=@%ct",
                        "--name-only",
                        LANDED_SINCE,
                        &base,
                    ],
                    &[],
                )?
                .1,
        );
        let committed = last_changes(
            &self
                .run(
                    &[
                        "git",
                        "log",
                        "--format=@%ct",
                        "--name-only",
                        &format!("{base}..HEAD"),
                    ],
                    &[],
                )?
                .1,
        );
        // the edit lines name the clone's paths, the common directory's parent - in the landing worktree too
        let clone = common.parent().unwrap_or(common);
        let prefix = format!("{}/", clone.to_string_lossy().trim_end_matches('/'));
        let events = self
            .root
            .opt("L7R_EVENTS_DIR")
            .map_or_else(|| common.join("l7r-events"), PathBuf::from);
        let name = name_of(d);
        for (task, at, path) in edit_lines(&events, &name) {
            let Some(file) = path.strip_prefix(&prefix) else {
                continue;
            };
            if tasks.contains(&task) || !open.contains(&task) || !judged.contains(file) {
                continue;
            }
            let after = landed
                .get(file)
                .copied()
                .map_or_else(landed_floor, f64::from);
            let before = committed
                .get(file)
                .copied()
                .map_or(f64::MIN, |c| f64::from(c) + 1.0);
            if after < at.0 && at.0 < before {
                found.entry(file.to_owned()).or_insert((task, at.1));
            }
        }
        Ok(found)
    }
}

/// The tasks `task-starts.jsonl` records started for `feature`.
fn started_tasks(path: &Path, feature: &str) -> BTreeSet<String> {
    std::fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(|v| v["feature"].as_str() == Some(feature))
        .filter_map(|v| v["task"].as_str().map(str::to_owned))
        .collect()
}

/// The tasks open in a tasks.md: each `- [ ] T<n>` line's id.
fn open_tasks(text: &str) -> BTreeSet<String> {
    text.lines()
        .filter_map(|l| l.trim_start().strip_prefix("- [ ] "))
        .filter_map(|rest| rest.split_whitespace().next())
        .filter(|id| id.starts_with('T') && id[1..].starts_with(|c: char| c.is_ascii_digit()))
        .map(str::to_owned)
        .collect()
}

/// `git log --format=@%ct --name-only`: each file's newest commit time (its first appearance, the log newest first).
fn last_changes(log: &str) -> BTreeMap<String, u32> {
    let mut at = 0;
    let mut out = BTreeMap::new();
    for line in log.lines() {
        if let Some(t) = line.strip_prefix('@') {
            at = t.trim().parse().unwrap_or(0);
        } else if !line.is_empty() {
            out.entry(line.to_owned()).or_insert(at);
        }
    }
    out
}

/// The oldest landed time read ([`LANDED_SINCE`]): an edit before it is taken as landed. A file changed in the window has its own.
fn landed_floor() -> f64 {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64());
    now - 7.0 * 86_400.0
}

/// Every task-tagged write the feature's event logs name: (task, (epoch seconds, its time as written), the path) - an Edit or Write's
/// `path`, a Bash call's `writes` (451 T93); a fallback line's task is a guess and is passed over, as the landing alone passes it.
fn edit_lines(events: &Path, feature: &str) -> Vec<(String, (f64, String), String)> {
    let mut logs: Vec<PathBuf> = std::fs::read_dir(events)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            let stem = p.file_stem().unwrap_or_default().to_string_lossy();
            p.extension().is_some_and(|x| x == "jsonl")
                && (stem == feature || stem.starts_with(&format!("{feature}-")))
        })
        .collect();
    logs.sort();
    let mut out = Vec::new();
    for log in logs {
        let text = String::from_utf8_lossy(&std::fs::read(&log).unwrap_or_default()).into_owned();
        for line in text.lines() {
            if !line.contains("\"PostToolUse\"")
                || !(line.contains("\"cat\":\"edit\"") || line.contains("\"writes\""))
            {
                continue;
            }
            let Ok(v) = serde_json::from_str::<Value>(line) else {
                continue;
            };
            let task = v["task"].as_str().unwrap_or_default().to_owned();
            let when = v["t"].as_str().unwrap_or_default().to_owned();
            let Some(secs) = l7r_shared::iso::parse(&when.replace('Z', "+00:00")) else {
                continue;
            };
            if task.is_empty() || v["fallback"].as_bool() == Some(true) {
                continue;
            }
            let mut paths: Vec<String> = v["writes"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(|w| w.as_str().map(str::to_owned))
                .collect();
            if v["cat"].as_str() == Some("edit") {
                paths.extend(v["path"].as_str().map(str::to_owned));
            }
            for path in paths {
                out.push((task.clone(), (secs, when.clone()), path));
            }
        }
    }
    out
}

#[cfg(test)]
mod tests;
