//! A task's Approach is answered before it is ticked, and answered again after a trigger (feature 385 T02, plan D8 and D9; feature 449
//! T066, from `approach_gate.py`). The GM, 2026-10-17: sessions hyper-focused because nothing made them ask, in time, where a constraint
//! came from and whether it described the world there. The checklist asks; this makes the asking happen. The cohort's trigger stays in
//! `rust/gate/src/cohort/known.rs` (T068).

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::now_utc as rfc3339_now;
use super::sections::re;
use super::task::active_task;
use crate::codeid::common_git_dir;

/// Each run is recorded for `make tool-yield`, as `usage_log` records a Python tool's.
pub(super) const USAGE_LOG_TOOL: &str = "approach_gate";
const DEFAULT: &str = "docs/approach-checklist.md";
const OWED: &str = "approach-owed.json";
const RULED_PREFIXES: [&str; 2] = ["hour:", "red-gate@"];

static STAMP: LazyLock<Regex> =
    LazyLock::new(|| re(r"(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)(?::(\d\d))?Z"));
static ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(\d+)\.\s+\S"));
static STAMPED_HEAD: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?im)^#{3,4}\s+T\d+\w*\s+(?:part B|Approach)\b.*$"));
static NEXT_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4}\s"));

fn heads(part: &str) -> &str {
    if part == "A" {
        "Approach"
    } else if part == "B" {
        "part B"
    } else {
        part
    }
}

fn part_title(part: &str) -> &str {
    if part == "A" {
        "part A - at task start"
    } else if part == "B" {
        "part B - when the work resists"
    } else {
        part
    }
}

/// Days since 1970-01-01 of a proleptic Gregorian date.
fn days_from_civil(y: i64, m: i64, d: i64) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let doy = (153 * (m + if m > 2 { -3 } else { 9 }) + 2) / 5 + d - 1;
    era * 146_097 + (yoe * 365 + yoe / 4 - yoe / 100 + doy) - 719_468
}

/// The first `YYYY-MM-DDTHH:MM[:SS]Z` in the text, as epoch seconds.
pub(super) fn parse_utc(text: &str) -> Option<i64> {
    let c = STAMP.captures(text).ok().flatten()?;
    let at = |i: usize| c.get(i).map_or(0, |g| g.as_str().parse().unwrap_or(0));
    Some(days_from_civil(at(1), at(2), at(3)) * 86_400 + at(4) * 3600 + at(5) * 60 + at(6))
}

fn minute_of(utc: &str) -> String {
    format!("{}Z", utc.chars().take(16).collect::<String>())
}

/// The checklist every plan's tasks are worked under; None in a tree without it.
pub(super) fn checklist(root: &Path) -> Option<PathBuf> {
    Some(root.join(DEFAULT)).filter(|p| p.is_file())
}

fn numbers(text: &str) -> Vec<u32> {
    ITEM.captures_iter(text)
        .flatten()
        .map(|c| c[1].parse().unwrap_or(0))
        .collect()
}

fn part_items(list: &str, part: &str) -> Vec<u32> {
    re(&format!(r"(?ms)^## {part}\..*?(?=^## |\z)"))
        .find(list)
        .ok()
        .flatten()
        .map_or_else(Vec::new, |m| numbers(m.as_str()))
}

fn task_blocks(plan: &str, task: &str, part: &str) -> Vec<(String, String)> {
    let head = re(&format!(
        r"(?im)^#{{3,4}}\s+{}\s+{}\b.*$",
        fancy_regex::escape(task),
        fancy_regex::escape(heads(part))
    ));
    head.find_iter(plan)
        .flatten()
        .map(|m| {
            let rest = &plan[m.end()..];
            let body = NEXT_HEAD
                .find(rest)
                .ok()
                .flatten()
                .map_or(rest, |n| &rest[..n.start()]);
            (m.as_str().to_owned(), body.to_owned())
        })
        .collect()
}

fn unanswered(body: &str, items: &[u32]) -> Vec<u32> {
    let got = numbers(body);
    items.iter().copied().filter(|n| !got.contains(n)).collect()
}

fn future_stamps(plan: &str, now: &str) -> Vec<String> {
    let clock = parse_utc(&minute_of(now)).unwrap_or(0);
    STAMPED_HEAD
        .find_iter(plan)
        .flatten()
        .filter(|m| parse_utc(m.as_str()).is_some_and(|t| t > clock))
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// The refusal for a plan with a heading stamped in the future (feature 385 T50: a stamp typed ahead of the clock let "written after
/// its trigger" pass without being so), or None.
pub(super) fn future_refusal(plan: &str, now: Option<&str>) -> Option<String> {
    let clock = now.map_or_else(rfc3339_now, str::to_owned);
    let ahead = future_stamps(plan, &clock);
    if ahead.is_empty() {
        return None;
    }
    Some(format!("stamped after the clock ({}Z): {} - stamp a part B with the time it is written (feature 385 T50)", clock.chars().take(16).collect::<String>(), ahead.join("; ")))
}

/// (a block exists, the items the most complete block stamped at or after `since` leaves unanswered).
fn best(plan: &str, task: &str, part: &str, items: &[u32], since: Option<i64>) -> (bool, Vec<u32>) {
    let found: Vec<Vec<u32>> = task_blocks(plan, task, part)
        .iter()
        .filter(|(h, _)| since.is_none_or(|s| parse_utc(h).is_some_and(|t| t >= s)))
        .map(|(_, b)| unanswered(b, items))
        .collect();
    let exists = !found.is_empty();
    (
        exists,
        found
            .into_iter()
            .min_by_key(Vec::len)
            .unwrap_or_else(|| items.to_vec()),
    )
}

fn git_dir(root: &Path) -> PathBuf {
    let out = super::git_line(root, &["rev-parse", "--absolute-git-dir"]);
    if out.is_empty() {
        root.join(".git")
    } else {
        PathBuf::from(out)
    }
}

fn owed_entries(root: &Path) -> Vec<Value> {
    let text = std::fs::read_to_string(git_dir(root).join(OWED)).unwrap_or_default();
    serde_json::from_str(&text).unwrap_or_default()
}

fn joined(items: &[u32]) -> String {
    items
        .iter()
        .map(u32::to_string)
        .collect::<Vec<_>>()
        .join(", ")
}

/// Record that `task` owes `part` after `trigger`; the message naming the part and the block to write.
pub(super) fn owe(
    root: &Path,
    feature: &str,
    task: &str,
    trigger: &str,
    part: &str,
    now: Option<&str>,
) -> String {
    let when = now.map_or_else(rfc3339_now, str::to_owned);
    let mut rows = owed_entries(root);
    let same = |r: &Value| r["feature"] == feature && r["task"] == task && r["trigger"] == trigger;
    if !rows.iter().any(same) {
        rows.push(json!({"feature": feature, "task": task, "trigger": trigger, "part": part, "utc": when}));
        let _ = std::fs::write(git_dir(root).join(OWED), super::pretty(&Value::Array(rows)));
    }
    let minute = when.chars().take(16).collect::<String>();
    let head = if part == "B" {
        format!("### {task} part B ({minute}Z)")
    } else {
        format!("### {task} Approach (re-answered {minute}Z)")
    };
    format!("approach owed: {trigger} - {task} owes the checklist's {}, answered before the next attempt: add `{head}` to specs/{feature}/plan.md, every item of part {part} numbered; `make tick` refuses {task} until it is there", part_title(part))
}

/// Why `make tick` may not tick `task` (D8 and D9), or None.
pub(super) fn refusal(spec_dir: &Path, root: &Path, task: &str) -> Option<String> {
    let text = std::fs::read_to_string(spec_dir.join("plan.md")).unwrap_or_default();
    let path = checklist(root)?;
    if let Some(ahead) = future_refusal(&text, None) {
        return Some(ahead);
    }
    let lines = std::fs::read_to_string(path).unwrap_or_default();
    let items = part_items(&lines, "A");
    let name = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    let (exists, missing) = best(&text, task, "A", &items, None);
    if !exists {
        return Some(format!("{task} has no `### {task} Approach` block in {name}/plan.md - answer every item of the checklist's part A ({}) before it is ticked (feature 385 D8)", joined(&items)));
    }
    if !missing.is_empty() {
        return Some(format!(
            "{task}'s Approach block leaves part A item(s) {} unanswered (feature 385 D8)",
            joined(&missing)
        ));
    }
    for row in owed_entries(root) {
        if row["feature"] != *name || row["task"] != task {
            continue;
        }
        let part = row["part"]
            .as_str()
            .filter(|p| !p.is_empty())
            .unwrap_or("B");
        let utc = row["utc"].as_str().unwrap_or("None");
        let (exists, missing) = best(
            &text,
            task,
            part,
            &part_items(&lines, part),
            parse_utc(&minute_of(utc)),
        );
        if !exists || !missing.is_empty() {
            let what = if exists {
                format!("item(s) {} unanswered", joined(&missing))
            } else {
                "no block stamped after it".to_owned()
            };
            return Some(format!("{} at {utc} owes {task} the checklist's {}: {what} - add `### {task} {} (<UTC>)` stamped at or after it (feature 385 D9)", row["trigger"].as_str().unwrap_or("None"), part_title(part), heads(part)));
        }
    }
    None
}

fn last_tick(root: &Path, dir: &Path) -> i64 {
    super::git_line(
        root,
        &[
            "log",
            "-1",
            "--format=%ct",
            "--grep=ticked",
            "--",
            &dir.join("tasks.md").to_string_lossy(),
        ],
    )
    .parse()
    .unwrap_or(0)
}

/// Every task a trigger charges: the active task, and each open task of the feature started since its last tick (405, the GM
/// 2026-10-21: the work that resisted may be any of them).
fn in_flight(root: &Path, dir: &Path, active: &str) -> Vec<String> {
    let tasks = std::fs::read_to_string(dir.join("tasks.md")).unwrap_or_default();
    let since = last_tick(root, dir);
    let path = common_git_dir(root)
        .unwrap_or_else(|| git_dir(root))
        .join("task-starts.jsonl");
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    let mut out = vec![active.to_owned()];
    for raw in std::fs::read_to_string(path).unwrap_or_default().lines() {
        let row: Value = serde_json::from_str(raw).unwrap_or(Value::Null);
        let task = row["task"].as_str().unwrap_or("");
        let open = re(&format!(r"(?m)^- \[ \] {}\b", fancy_regex::escape(task)));
        if row["feature"] == *name
            && !task.is_empty()
            && !out.iter().any(|t| t == task)
            && parse_utc(row["utc"].as_str().unwrap_or("")).unwrap_or(0) >= since
            && open.is_match(&tasks).unwrap_or(false)
        {
            out.push(task.to_owned());
        }
    }
    out
}

/// Charge the trigger to every in-flight task of the active feature; the messages, or None when no task is active.
pub(super) fn owe_in_flight(
    root: &Path,
    trigger: &str,
    part: &str,
    now: Option<&str>,
) -> Option<String> {
    let (dir, task) = active_task(root);
    let dir = dir
        .filter(|d| !task.is_empty() && d.join("plan.md").is_file() && checklist(root).is_some())?;
    let name = dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    Some(
        in_flight(root, &dir, &task)
            .iter()
            .map(|t| owe(root, &name, t, trigger, part, now))
            .collect::<Vec<_>>()
            .join("\n"),
    )
}

/// The round arbiter ruled: an `hour:` or `red-gate@` ruling owes part B.
pub(super) fn ruled(root: &Path, trigger: &str, now: Option<&str>) -> Option<String> {
    if !RULED_PREFIXES.iter().any(|p| trigger.starts_with(p)) {
        return None;
    }
    owe_in_flight(root, trigger, "B", now)
}

#[cfg(test)]
mod tests;
