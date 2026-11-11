//! A plan's decisions are reviewed before its tasks are ticked (feature 243; feature 449 T066, from `scripts/gates/plan_gate.py` and
//! what it imports). Constitution XVI puts an independent check in front of every exception, and a plan is written after the spec's
//! verdict: a plan decision that narrowed the spec reached ticked tasks and main unchecked (feature 239's P2). So `make tick` asks this
//! before it ticks, and the push asks it over the features its delta touches. Both take `PLAN_REVIEW_OK="<reason>"`.
//!
//! `make task-start` and the cohort's trigger stay in Python with what they read (`ask:449-T066-scope`); Python that still needs a verb
//! here reaches it through `scripts/plan_door.py`, one call each, a forwarder and never a fallback.

mod approach;
mod bundle;
mod engine_edit;
mod history;
mod lint;
mod record;
mod sections;
mod status;
mod task;

use std::io::Read;
use std::path::{Path, PathBuf};

use l7r_guard::shared::log::{civil, write as log_write, Entry};
use l7r_guard::shared::{escape, sha256};
use serde_json::{json, Value};

use history::History;
use record::Stop;
use sections::{blocks, digest, task_sections, wording_only};
use status::{block_status, owed, ruled_tasks, RECORD};
use task::{resolve, touched_features};

pub use l7r_gate_core::plan::*;

/// `l7r-gate claims <words>`, as the binary answers it.
pub type Claims = dyn Fn(&[String]) -> crate::Reply;

const BUNDLES: &str = "/tmp/l7r-check";

fn clock() -> (i64, u32, u32, u64, u64, u64) {
    civil(
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_or(0, |d| d.as_secs()),
    )
}

pub(super) fn today() -> String {
    let (y, m, d, ..) = clock();
    format!("{y:04}-{m:02}-{d:02}")
}

pub(super) fn now_utc() -> String {
    let (y, mo, d, h, mi, s) = clock();
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn reply(stdout: String, stderr: String, code: i32) -> crate::Reply {
    crate::Reply {
        stdout,
        stderr,
        code,
    }
}

fn said(text: impl Into<String>) -> crate::Reply {
    reply(text.into(), String::new(), 0)
}

fn fail(text: impl Into<String>, code: i32) -> crate::Reply {
    reply(String::new(), text.into(), code)
}

fn json_reply(value: &Value) -> crate::Reply {
    said(format!("{value}\n"))
}

/// One entry in the guard census.
fn guard_log(event: &str, detail: &str, rule: &str) {
    let detail: String = detail.chars().take(400).collect();
    let _ = log_write(&Entry {
        guard: "plan-gate",
        event,
        detail: &detail,
        rule,
        context: None,
        input: &Value::Null,
        session_name: "",
    });
}

/// The reason ships with the push: `dev/bypass-log/` is in the repository and `make audit` lists it.
fn bypass_record(root: &Path, place: &str, why: &str) {
    let dev = root.join("dev");
    if !dev.is_dir() {
        return;
    }
    let (y, mo, d, h, mi, s) = clock();
    let dir = dev.join(format!("bypass-log/{y:04}-{mo:02}"));
    let _ = std::fs::create_dir_all(&dir);
    let commit = git_line(root, &["rev-parse", "--short", "HEAD"]);
    let entry = json!({"utc": now_utc(), "target": format!("plan-gate {place}"), "commit": commit, "why": why});
    let mut out = Vec::new();
    let mut writer = serde_json::Serializer::with_formatter(
        &mut out,
        serde_json::ser::PrettyFormatter::with_indent(b"  "),
    );
    let _ = serde::Serialize::serialize(&entry, &mut writer);
    let name = format!(
        "{y:04}{mo:02}{d:02}T{h:02}{mi:02}{s:02}Z-{}.json",
        &sha256::hex(why.as_bytes())[..6]
    );
    let _ = std::fs::write(
        dir.join(name),
        String::from_utf8_lossy(&out).into_owned() + "\n",
    );
}

/// FR-001, FR-005 and FR-008 for `make tick`: (may tick, what to print).
fn tick_permitted(spec_dir: &Path, root: &Path, escaped: Option<&str>) -> (bool, String) {
    let Some((rule, reason)) = owed(spec_dir) else {
        return (true, String::new());
    };
    let name = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    let Some(why) = escaped.filter(|e| !e.is_empty()) else {
        guard_log("blocked", &format!("{name}: {reason}"), rule);
        return (false, format!("tick: refused - {name}'s plan decisions have no current CLEAR review (feature 243).\n  {reason}\n  A case that is genuinely exempt: PLAN_REVIEW_OK=\"<reason>\", which is recorded."));
    };
    if !escape::enough(why.trim()) {
        guard_log("blocked", why, "PLAN_REVIEW_OK-no-reason");
        return (false, "tick: PLAN_REVIEW_OK needs a REASON, not just a value - two words and eight characters.".to_owned());
    }
    guard_log("escaped", &format!("{name}: {why}"), "plan-review-ok");
    bypass_record(root, &format!("tick {name}"), why);
    (
        true,
        format!("tick: plan gate BYPASSED - {why} (recorded in dev/bypass-log/)"),
    )
}

fn stop_reply(prefix: &str, stop: Stop) -> crate::Reply {
    match stop {
        Stop::Declined(why) => fail(format!("{prefix}: {why}\n"), 2),
        Stop::Refused(why) => fail(format!("{prefix}: refused - {why}\n"), 1),
    }
}

/// The line `make decide` and `make plan-delta` end with when the clone owes claims a triage (feature 430 T07, D7).
fn triage_hint(root: &Path, claims: &Claims) -> String {
    let args = ["--root", &root.to_string_lossy(), "triage-owed"].map(str::to_owned);
    hint_of(&claims(&args).stdout)
}

/// The hint for `claims triage-owed`'s answer: the count it printed last, when above none.
fn hint_of(out: &str) -> String {
    match out.lines().last().and_then(|l| l.trim().parse::<u64>().ok()) {
        Some(n) if n > 0 => format!("claims owed a triage: {n} - `make claims-triage`, and dispatch it beside this review (impl-drift waits for the verdict)\n"),
        _ => String::new(),
    }
}

fn read_review(spec_dir: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(spec_dir.join(RECORD)).unwrap_or_default())
        .unwrap_or(json!({}))
}

/// Where a verb's spec directory is, or the refusal saying it is not exactly one.
fn dir_of(feature: &str, root: &Path, prefix: &str) -> Result<PathBuf, crate::Reply> {
    resolve(feature, root).ok_or_else(|| {
        fail(
            format!("{prefix}: no single specs/{feature}* directory\n"),
            2,
        )
    })
}

fn parse_file(path: &str) -> Result<Value, Stop> {
    let text = std::fs::read_to_string(path).map_err(|e| Stop::Refused(e.to_string()))?;
    serde_json::from_str(&text).map_err(|e| Stop::Refused(e.to_string()))
}

fn decide(words: &[String], root: &Path, out_root: &Path, claims: &Claims) -> crate::Reply {
    let verb = words[0].as_str();
    let dir = resolve(&words[1], root);
    let plan = dir
        .as_ref()
        .and_then(|d| std::fs::read_to_string(d.join("plan.md")).ok())
        .unwrap_or_default();
    let section = task_sections(&plan).remove(&words[2]);
    let (Some(dir), Some(section)) = (dir, section) else {
        return fail(format!("{verb}: no plan section names {} in specs/{}* - put the task's decisions under a heading that names it\n", words[2], words[1]), 2);
    };
    if verb == "section-sha" {
        return said(digest(section.as_bytes()) + "\n");
    }
    let why = lint::refusal(&dir, &section);
    if !why.is_empty() {
        return fail(format!("decide: refused - {why}\n"), 2);
    }
    let top = dir
        .parent()
        .and_then(Path::parent)
        .unwrap_or(root)
        .to_owned();
    if let Some(why) = approach::refusal(&dir, &top, &words[2]) {
        return fail(format!("decide: refused - {why}\n"), 2);
    }
    let prompt = if wording_only(&section) {
        Ok(format!("decide: {}'s section is wording only - no plan review is owed and no bundle is built; `make tick` checks its commits against it", words[2]))
    } else {
        bundle::task_prompt(&dir, out_root, &words[2])
    };
    match prompt {
        Ok(text) => reply(text + "\n", triage_hint(&top, claims), 0),
        Err(why) => fail(why + "\n", 1),
    }
}

fn plan_delta(dir: &Path, out_root: &Path, claims: &Claims) -> crate::Reply {
    let plan = dir.join("plan.md");
    let review = read_review(dir);
    let text = std::fs::read_to_string(&plan).unwrap_or_default();
    if let Some(ahead) = approach::future_refusal(&text, None) {
        return fail(format!("plan-delta: {ahead}\n"), 1);
    }
    let history = History::new(&plan, "HEAD");
    let ruled = ruled_tasks(&review, &text, Some(&history));
    let done = std::fs::read_to_string(dir.join("plan-done.md")).unwrap_or_default();
    let (mut keys, blocked) = block_status(&review, &text, &ruled, Some(&history), &done);
    for key in blocked {
        if !keys.contains(&key) {
            keys.push(key);
        }
    }
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    if keys.is_empty() {
        return said(format!(
            "plan-delta: no block of {name}'s plan is owed a review\n"
        ));
    }
    let bodies: Vec<String> = blocks(&text)
        .into_iter()
        .filter(|(k, ..)| keys.contains(k))
        .map(|(_, b, _)| b)
        .collect();
    let why = lint::plan_refusal(dir, &text, &bodies);
    if !why.is_empty() {
        return fail(
            format!("plan-delta: refused, no bundle written - {why}\n"),
            1,
        );
    }
    match bundle::delta_prompt(dir, out_root, &keys) {
        Ok(prompt) => reply(
            prompt + "\n",
            triage_hint(
                dir.parent()
                    .and_then(Path::parent)
                    .unwrap_or(Path::new(".")),
                claims,
            ),
            0,
        ),
        Err(why) => fail(why + "\n", 1),
    }
}

fn slim(dir: &Path) -> crate::Reply {
    let path = dir.join(RECORD);
    let Ok(before) = std::fs::read_to_string(&path) else {
        return said("");
    };
    let slimmed = pretty(&record::slim_record(
        &serde_json::from_str(&before).unwrap_or(json!({})),
    ));
    let _ = std::fs::write(&path, &slimmed);
    said(format!(
        "slim: {}/{RECORD} {} KB -> {} KB, its verdicts kept\n",
        dir.file_name().unwrap_or_default().to_string_lossy(),
        before.len() / 1024,
        slimmed.len() / 1024
    ))
}

fn record_verb(words: &[String], root: &Path) -> crate::Reply {
    let dir = match dir_of(&words[1], root, "plan-verdict") {
        Ok(d) => d,
        Err(r) => return r,
    };
    let name = dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let count = |v: &Value| v["decisions"].as_array().map_or(0, Vec::len);
    let done = match words[0].as_str() {
        "record" => parse_file(&words[2])
            .and_then(|r| record::record(&dir, &r, &words[4], None))
            .map(|out| {
                format!(
                    "plan-verdict: {} recorded in {name}/{RECORD} ({} decision(s))\n",
                    out["verdict"].as_str().unwrap_or(""),
                    count(&out)
                )
            }),
        "record-task" => parse_file(&words[3])
            .and_then(|r| record::record_task(&dir, &words[2], &r, &words[5], None))
            .map(|out| {
                format!(
                    "plan-verdict: {} recorded for {name} {} ({} decision(s))\n",
                    out["verdict"].as_str().unwrap_or(""),
                    words[2],
                    count(&out)
                )
            }),
        _ => parse_file(&words[2])
            .and_then(|r| record::record_blocks(&dir, &r, &words[4], None))
            .map(|got| {
                let mut text = format!(
                    "plan-verdict: {} recorded for {} block(s) of {name}'s plan ({} decision(s))\n",
                    got["verdict"].as_str().unwrap_or(""),
                    got["blocks"].as_array().map_or(0, Vec::len),
                    count(&got)
                );
                for line in got["approach_owed"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .filter_map(Value::as_str)
                {
                    text += line;
                    text.push('\n');
                }
                text
            }),
    };
    done.map_or_else(|stop| stop_reply("plan-verdict", stop), said)
}

fn approach_verb(words: &[String], root: &Path) -> crate::Reply {
    let answer = match (words.first().map(String::as_str), words.len()) {
        (Some("owed"), 3) => {
            let why = resolve(&words[1], root).and_then(|d| approach::refusal(&d, root, &words[2]));
            let code = i32::from(why.is_some());
            crate::stamp::record_for(root, approach::USAGE_LOG_TOOL, if code == 0 { "passed" } else { "refused" });
            return reply(why.map_or(String::new(), |w| w + "\n"), String::new(), code);
        }
        (Some("ruled"), 2) => approach::ruled(root, &words[1], None),
        (Some("owe-in-flight"), 3) => approach::owe_in_flight(root, &words[1], &words[2], None),
        _ => return fail("usage: l7r-gate plan approach owed <feature> <task> | ruled <trigger> | owe-in-flight <trigger> <part>\n", 2),
    };
    crate::stamp::record_for(root, approach::USAGE_LOG_TOOL, "passed");
    said(answer.map_or(String::new(), |m| m + "\n"))
}

/// The cohort's trigger for part B of the active task (`approach::owe_in_flight`).
#[must_use]
pub fn owe_in_flight(root: &Path, trigger: &str, part: &str) -> Option<String> {
    approach::owe_in_flight(root, trigger, part, None)
}

/// What Python that still needs a verb calls, through `scripts/plan_door.py`.
fn door(words: &[String], stdin: &mut dyn Read, escaped: Option<&str>) -> crate::Reply {
    let mut text = String::new();
    let word = |i: usize| words.get(i).map_or("", String::as_str);
    match word(0) {
        "task-sections" => {
            let _ = stdin.read_to_string(&mut text);
            let found: serde_json::Map<String, Value> = task_sections(&text)
                .into_iter()
                .map(|(k, v)| (k, Value::from(v)))
                .collect();
            json_reply(&Value::Object(found))
        }
        "blocks" => {
            let _ = stdin.read_to_string(&mut text);
            let found: Vec<Value> = blocks(&text)
                .into_iter()
                .map(|(k, b, at)| json!([k, b, at]))
                .collect();
            json_reply(&Value::Array(found))
        }
        "wording-only" => {
            let _ = stdin.read_to_string(&mut text);
            json_reply(&json!(wording_only(&text)))
        }
        "active-task" => {
            let (dir, task) = task::active_task(Path::new(word(1)));
            json_reply(&json!([dir.map(|d| d.display().to_string()), task]))
        }
        "touched-features" => json_reply(&json!(touched_features(Path::new(word(1)), word(2)))),
        "tick-permitted" => {
            let (ok, message) = tick_permitted(Path::new(word(1)), Path::new(word(2)), escaped);
            json_reply(&json!([ok, message]))
        }
        "archive" => json_reply(&json!(task::archive(Path::new(word(1)), None))),
        "resolve" => json_reply(&json!(
            resolve(word(1), Path::new(word(2))).map(|d| d.display().to_string())
        )),
        "approach-refusal" => json_reply(&json!(approach::refusal(
            Path::new(word(1)),
            Path::new(word(2)),
            word(3)
        ))),
        "approach-ruled" => json_reply(&json!(approach::ruled(Path::new(word(1)), word(2), None))),
        "accept" => match record::arbiter_accept(Path::new(word(1)), word(2), None) {
            Ok(named) => json_reply(&json!(named)),
            Err(stop) => stop_reply("arbiter-accept", stop),
        },
        "bypass-record" => {
            bypass_record(Path::new(word(1)), word(2), word(3));
            said("")
        }
        _ => fail("usage: l7r-gate plan door <verb>\n", 2),
    }
}

fn answer(
    words: &[String],
    root: &Path,
    out_root: &Path,
    python: &str,
    stdin: &mut dyn Read,
    escaped: Option<&str>,
    claims: &Claims,
) -> crate::Reply {
    let verb = words.first().map_or("", String::as_str);
    let n = words.len();
    match (verb, n) {
        ("door", _) => door(&words[1..], stdin, escaped),
        ("approach", _) => approach_verb(&words[1..], root),
        ("engine-edit", 1) => engine_edit::cli(stdin, python),
        ("arbiter-accept", 3) => match dir_of(&words[1], root, "arbiter-accept") {
            Err(r) => r,
            Ok(dir) => match record::arbiter_accept(&dir, &words[2], None) {
                Ok(named) => said(format!("arbiter-accept: {} block(s) of {}'s plan recorded CLEAR on {}\n", named.len(), dir.file_name().unwrap_or_default().to_string_lossy(), words[2])),
                Err(stop) => stop_reply("arbiter-accept", stop),
            },
        },
        ("decided", 1 | 2) => {
            let why = task::decision_refusal(Path::new(words.get(1).map_or(".", String::as_str)));
            reply(if why.is_empty() { why.clone() } else { format!("{why}\n") }, String::new(), i32::from(!why.is_empty()))
        }
        ("decide" | "section-sha", 3) => decide(words, root, out_root, claims),
        ("record" | "record-blocks", 5) if words[3] == "--as" => record_verb(words, root),
        ("record-task", 6) if words[4] == "--as" => record_verb(words, root),
        ("slim" | "archive" | "delta", 2) => {
            let Some(dir) = resolve(&words[1], root).filter(|d| d.join("plan.md").is_file()) else {
                return fail(format!("{verb}: no single specs/{}* directory with a plan.md\n", words[1]), 2);
            };
            match verb {
                "slim" => slim(&dir),
                "archive" => {
                    let ids = task::archive(&dir, None);
                    let list = if ids.is_empty() { "none finished".to_owned() } else { ids.join(", ") };
                    said(format!("plan-archive: {} task section(s) moved to {}/plan-done.md: {list}\n", ids.len(), dir.file_name().unwrap_or_default().to_string_lossy()))
                }
                _ => plan_delta(&dir, out_root, claims),
            }
        }
        ("owed", 2) => match owed(Path::new(&words[1])) {
            Some((rule, reason)) => reply(format!("{rule}\t{reason}\n"), String::new(), 1),
            None => said(""),
        },
        ("push", 1 | 2) => {
            let range = words.get(1).map_or("origin/main...HEAD", String::as_str);
            let found = task::push_owed(root, range, "HEAD");
            let lines: Vec<String> = found.iter().map(|(f, rule, reason)| format!("{f}\t{rule}\t{reason}\n")).collect();
            let lines = lines.concat();
            reply(lines, String::new(), i32::from(!found.is_empty()))
        }
        _ => fail("usage: l7r-gate plan owed <dir> | push [range] | record | record-task | record-blocks | delta | archive | slim | decide | decided | section-sha | arbiter-accept | approach | door | engine-edit\n", 2),
    }
}

/// `l7r-gate plan <verb> ...`.
/// What an hour or red-gate ruling owes the active task's part B (`plan_door.approach_ruled`), for `l7r-gate arbiter`.
/// The active task's feature directory, as `plan_door.active_task` answered it (the claims carry's, 449 T82).
#[must_use]
pub fn active_feature(root: &Path) -> Option<PathBuf> {
    task::active_task(root).0
}

/// A spec directory from a number or a name, as `plan_door.resolve` answered it (the claims carry's, 449 T82).
#[must_use]
pub fn resolve_feature(feature: &str, root: &Path) -> Option<PathBuf> {
    resolve(feature, root)
}

#[must_use]
pub fn approach_ruled(root: &Path, trigger: &str) -> Option<String> {
    approach::ruled(root, trigger, None)
}

/// The accept as the plan's verdict: the blocks recorded CLEAR (`plan_door.arbiter_accept`), for `l7r-gate arbiter`, which has just written the ruling it reads.
#[must_use]
pub fn arbiter_accept_listed(dir: &Path, trigger: &str) -> Vec<String> {
    record::arbiter_accept(dir, trigger, None).unwrap_or_default()
}

/// `l7r-gate plan <verb> ...`; `claims` is `l7r-gate claims`, which the binary hands in (the claims crate reads the plan's, so the
/// plan cannot name it - feature 449 T92), asked for the triage hint `decide` and `delta` end with.
pub fn cli(words: &[String], root: &Path, claims: &Claims) -> crate::Reply {
    let escaped = std::env::var("PLAN_REVIEW_OK").ok();
    answer(
        words,
        root,
        Path::new(BUNDLES),
        "python3",
        &mut std::io::stdin(),
        escaped.as_deref(),
        claims,
    )
}

#[cfg(test)]
mod tests;
