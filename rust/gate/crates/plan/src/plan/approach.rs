//! A task's Approach is answered before it is ticked, and answered again after a trigger (feature 385 T02, plan D8 and D9; feature 449
//! T066, from `approach_gate.py`). The GM, 2026-10-17: sessions hyper-focused because nothing made them ask, in time, where a constraint
//! came from and whether it described the world there. The checklist asks; this makes the asking happen. The cohort's trigger stays in
//! `rust/gate/crates/cohort/src/cohort/known.rs` (T068).

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
/// Why an owed block goes beside its task's other sections (451 T419): on 2026-11-27 three part B sections appended at the plan's
/// end stopped two carries, one on a commit's parent, which no later edit can fix; `make decide` refuses one standing apart.
const PLACE: &str =
    "a task's sections stand together, and `make decide` refuses a part B standing apart";

static STAMP: LazyLock<Regex> =
    LazyLock::new(|| re(r"(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)(?::(\d\d))?Z"));
static ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(\d+)\.\s+\S"));
static STAMPED_HEAD: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?im)^#{3,4}\s+T\d+\w*(?:,\s*T\d+\w*)*\s+(?:part B|Approach)\b.*$"));
static NEXT_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4}\s"));
/// A checklist item marked asked where written: owed only by a section that writes its line (feature 449 T196, item 12 - a new item
/// must not refuse the sections written before it, 58 open on 2026-11-19).
static ASKED: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(\d+)\.\s.*\(asked where written\)"));
static WRITTEN: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(\d+)\.(.*)$"));
static BOLD_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"\A\s*\*\*[^*]*\*\*"));

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
        .map_while(Result::ok)
        .map(|c| c[1].parse().unwrap_or(0))
        .collect()
}

fn part_text<'a>(list: &'a str, part: &str) -> &'a str {
    re(&format!(r"(?ms)^## {part}\..*?(?=^## |\z)"))
        .find(list)
        .ok()
        .flatten()
        .map_or("", |m| m.as_str())
}

fn part_items(list: &str, part: &str) -> Vec<u32> {
    numbers(part_text(list, part))
}

/// (the items every section of `part` owes, the items asked only where a section writes them).
fn split_items(list: &str, part: &str) -> (Vec<u32>, Vec<u32>) {
    let asked: Vec<u32> = ASKED
        .captures_iter(part_text(list, part))
        .map_while(Result::ok)
        .map(|c| c[1].parse().unwrap_or(0))
        .collect();
    let owed = part_items(list, part)
        .into_iter()
        .filter(|n| !asked.contains(n))
        .collect();
    (owed, asked)
}

/// The asked-where-written items a section writes but leaves empty: nothing after the number and its bold heading, or only a
/// `<...>` placeholder.
fn left_empty(body: &str, asked: &[u32]) -> Vec<u32> {
    WRITTEN
        .captures_iter(body)
        .map_while(Result::ok)
        .filter_map(|c| {
            let n: u32 = c[1].parse().unwrap_or(0);
            let rest = c[2].to_owned();
            let answer = BOLD_HEAD.replace(&rest, "");
            let answer = answer.trim();
            (asked.contains(&n)
                && (answer.is_empty() || (answer.starts_with('<') && answer.ends_with('>'))))
            .then_some(n)
        })
        .collect()
}

fn task_blocks(plan: &str, task: &str, part: &str) -> Vec<(String, String)> {
    let head = re(&format!(
        r"(?im)^#{{3,4}}\s+(?:T\d+[a-z]?,\s*)*{}(?:,\s*T\d+[a-z]?)*\s+{}\b.*$",
        fancy_regex::escape(task),
        fancy_regex::escape(heads(part))
    ));
    head.find_iter(plan)
        .map_while(Result::ok)
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
        .map_while(Result::ok)
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

/// (a block exists, the items the most complete block stamped at or after `since` leaves unanswered): every one of `items`, and
/// each of `asked` the block writes but leaves empty.
fn best(
    plan: &str,
    task: &str,
    part: &str,
    (items, asked): (&[u32], &[u32]),
    since: Option<i64>,
) -> (bool, Vec<u32>) {
    let found: Vec<Vec<u32>> = task_blocks(plan, task, part)
        .iter()
        .filter(|(h, _)| since.is_none_or(|s| parse_utc(h).is_some_and(|t| t >= s)))
        .map(|(_, b)| {
            let mut left = unanswered(b, items);
            left.extend(left_empty(b, asked));
            left
        })
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

/// Where `approach-owed.json` lives: the clone's COMMON git directory, so a block owed in a builder's pool tree is still owed where the
/// task lands (451 T442); `<root>/.git` outside a repository.
fn git_dir(root: &Path) -> PathBuf {
    common_git_dir(root).unwrap_or_else(|| root.join(".git"))
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
    owe_all(root, feature, &[task.to_owned()], trigger, part, now)
}

/// Record that each of `tasks` owes `part` after `trigger`; the message naming the ONE block that answers for them all - a bundle
/// heading, `### T1, T2 part B (<UTC>)`, which [`task_blocks`] reads as each task's (451 T472) - or "" where `tasks` is empty.
fn owe_all(
    root: &Path,
    feature: &str,
    tasks: &[String],
    trigger: &str,
    part: &str,
    now: Option<&str>,
) -> String {
    let Some(first) = tasks.first() else {
        return String::new();
    };
    let when = now.map_or_else(rfc3339_now, str::to_owned);
    let mut rows = owed_entries(root);
    let before = rows.len();
    for task in tasks {
        let same =
            |r: &Value| r["feature"] == feature && r["task"] == *task && r["trigger"] == trigger;
        if !rows.iter().any(same) {
            rows.push(json!({"feature": feature, "task": task, "trigger": trigger, "part": part, "utc": when}));
        }
    }
    if rows.len() > before {
        let _ = std::fs::write(git_dir(root).join(OWED), super::pretty(&Value::Array(rows)));
    }
    let minute = when.chars().take(16).collect::<String>();
    let named = tasks.join(", ");
    let head = if part == "B" {
        format!("### {named} part B ({minute}Z)")
    } else {
        format!("### {named} Approach (re-answered {minute}Z)")
    };
    let title = part_title(part);
    let place = format!("to specs/{feature}/plan.md directly after {first}'s other sections (never at the plan's end: {PLACE}), every item of part {part} numbered");
    if tasks.len() == 1 {
        return format!("approach owed: {trigger} - {first} owes the checklist's {title}, answered before the next attempt: add `{head}` {place}; `make tick` refuses {first} until it is there");
    }
    format!("approach owed: {trigger} - {named} owe the checklist's {title}, answered before the next attempt: add ONE section `{head}` {place} - it answers for all {}, since a red gate's record names its failing steps, never their files, so no task's share can be told (451 T472), and a task built inside another's section is left out of it (451 T307 part 2); `make tick` refuses each until it is there", tasks.len())
}

static TASK_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"^### (T\d+)"));
static PART_B_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"^### (T\d+)(?:,\s*T\d+)*\s+part B\b"));

/// Why `make decide` refuses `tasks` for a part B section of theirs standing apart from its task's other sections (451 T419), or
/// None: the `### T<n>` heading before it names another task (a bundle's part B is its first task's). WHY: [`PLACE`].
pub(super) fn apart(plan: &str, tasks: &[String]) -> Option<String> {
    let first = |r: &Regex, line: &str| {
        r.captures(line)
            .ok()
            .flatten()
            .and_then(|c| c.get(1))
            .map(|m| m.as_str().to_owned())
    };
    let mut before: Option<String> = None;
    let mut found = Vec::new();
    for line in plan.lines() {
        let Some(id) = first(&TASK_HEAD, line) else {
            continue;
        };
        if first(&PART_B_HEAD, line).is_some_and(|b| tasks.contains(&b))
            && before.as_ref() != Some(&id)
        {
            found.push(format!("`{line}`"));
        }
        before = Some(id);
    }
    (!found.is_empty()).then(|| {
        format!(
            "{} stand(s) apart from its task's other sections - move each to directly after them ({PLACE}; 451 T419)",
            found.join(", ")
        )
    })
}

/// Why `make tick` may not tick `task` (D8 and D9), or None.
pub(super) fn refusal(spec_dir: &Path, root: &Path, task: &str) -> Option<String> {
    let text = std::fs::read_to_string(spec_dir.join("plan.md")).unwrap_or_default();
    let path = checklist(root)?;
    if let Some(ahead) = future_refusal(&text, None) {
        return Some(ahead);
    }
    let lines = std::fs::read_to_string(path).unwrap_or_default();
    let (items, asked) = split_items(&lines, "A");
    let name = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    let (exists, missing) = best(&text, task, "A", (&items, &asked), None);
    if !exists {
        return Some(format!("{task} has no `### {task} Approach` block in {name}/plan.md - answer every item of the checklist's part A ({}) before it is ticked (feature 385 D8)", joined(&items)));
    }
    if !missing.is_empty() {
        return Some(format!(
            "{task}'s Approach block leaves part A item(s) {} unanswered (feature 385 D8)",
            joined(&missing)
        ));
    }
    // a bundle's part B stands with its first task's sections, which that task's tick may archive before the others' (451 T472)
    let done = l7r_shared::speckit::archive::plan_done(spec_dir);
    let both = format!("{text}\n{done}");
    for row in owed_entries(root) {
        if row["feature"] != *name || row["task"] != task {
            continue;
        }
        let part = row["part"]
            .as_str()
            .filter(|p| !p.is_empty())
            .unwrap_or("B");
        let utc = row["utc"].as_str().unwrap_or("None");
        let (owed, asked) = split_items(&lines, part);
        let (exists, missing) = best(
            &both,
            task,
            part,
            (&owed, &asked),
            parse_utc(&minute_of(utc)),
        );
        if !exists || !missing.is_empty() {
            let what = if exists {
                format!("item(s) {} unanswered", joined(&missing))
            } else {
                "no block stamped after it".to_owned()
            };
            return Some(format!("{} at {utc} owes {task} the checklist's {}: {what} - add `### {task} {} (<UTC>)` stamped at or after it, directly after {task}'s other sections (feature 385 D9; {PLACE})", row["trigger"].as_str().unwrap_or("None"), part_title(part), heads(part)));
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
    let path = git_dir(root).join("task-starts.jsonl");
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    let mut out = vec![active.to_owned()];
    // a start and its `make task-unstart` read as no start (451 T359)
    let starts =
        l7r_shared::speckit::marks::live_starts(&std::fs::read_to_string(path).unwrap_or_default());
    for raw in starts.lines() {
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

/// The active feature's directory, its name and the in-flight tasks, or None when no task is active.
fn flight(root: &Path) -> Option<(PathBuf, String, Vec<String>)> {
    let (dir, task) = active_task(root);
    let dir = dir
        .filter(|d| !task.is_empty() && d.join("plan.md").is_file() && checklist(root).is_some())?;
    let name = dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let tasks = in_flight(root, &dir, &task);
    Some((dir, name, tasks))
}

/// Charge the trigger to every in-flight task of the active feature; the messages, or None when no task is active.
pub(super) fn owe_in_flight(
    root: &Path,
    trigger: &str,
    part: &str,
    now: Option<&str>,
) -> Option<String> {
    let (_, name, tasks) = flight(root)?;
    Some(
        tasks
            .iter()
            .map(|t| owe(root, &name, t, trigger, part, now))
            .collect::<Vec<_>>()
            .join("\n"),
    )
}

/// The round arbiter ruled: an `hour:` or `red-gate@` ruling owes part B. A red gate's owes ONE section for the batch (451 T472):
/// the run log keeps a red's failing steps alone (`result: failed: static`, no test or file), so its failures cannot be tied to a
/// task's files, and tonight's 23, 20 and 20 sections each said the same nine answers but its id. A task a `Built here:` line names
/// is left out, judged by its host (451 T307 part 2: a heading naming it fills its stub, as T395's, T416's and T421's did).
pub(super) fn ruled(root: &Path, trigger: &str, now: Option<&str>) -> Option<String> {
    if !RULED_PREFIXES.iter().any(|p| trigger.starts_with(p)) {
        return None;
    }
    if !trigger.starts_with("red-gate@") {
        return owe_in_flight(root, trigger, "B", now);
    }
    let (dir, name, tasks) = flight(root)?;
    let own: Vec<String> = tasks
        .into_iter()
        .filter(|t| super::inside::built_inside(&dir, t).is_none())
        .collect();
    Some(owe_all(root, &name, &own, trigger, "B", now))
}

#[cfg(test)]
mod tests;
