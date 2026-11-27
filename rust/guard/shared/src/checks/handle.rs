//! One hook event against the check state, the lock held (from `hm_checks.handle`, `_handle`, `close`, `main`).

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::arbiter;
use super::budget;
use super::pages::subject_blocks;
use super::passes;
use super::planhold;
use super::rounds::{self, Dispatch, PAGE_CHECKS};
use super::{clone_root, falsy, load, locked, map_mut, name_of, now, save, state_path, text};

fn parent_of(p: &Path) -> &Path {
    p.parent().map_or(Path::new("."), |d| d)
}
use crate::log;

/// Every check a dispatch is counted for: the page checks freeze their subject; `impl-drift` counts to FR-010 only.
fn is_check_kind(check: &str) -> bool {
    PAGE_CHECKS.contains(&check) || check == "impl-drift"
}

const MANIFEST_REASON_TOKENS: [&str; 2] = ["FREEZE_OK", "ARBITER_OK"];
/// The tool a restored plan section records in the usage log (`usage_log`'s registry, `check tool-signals`).
const USAGE_LOG_TOOL: &str = "planhold-restore";

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static MANIFEST_PATH: LazyLock<Regex> = LazyLock::new(|| re(r#"(/[^\s`"'<>)]*MANIFEST\.md)"#));
static TRIGGER_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^trigger: (.+)$"));
static UNIT_UID: LazyLock<Regex> = LazyLock::new(|| re(r"^unit: (\S+)"));

fn manifest_of(prompt: &str) -> (String, String) {
    let Some(path) = MANIFEST_PATH
        .captures(prompt)
        .ok()
        .flatten()
        .and_then(|c| c.get(1).map(|g| g.as_str().to_owned()))
    else {
        return (String::new(), String::new());
    };
    let body = std::fs::read_to_string(&path).unwrap_or_default();
    (path, body)
}

/// A reason that is two words and eight characters: the escape is taken and RECORDED in the guard census; a bare token is no escape.
#[must_use]
pub fn escaped(token: &str, body: &str) -> bool {
    let pattern = re(&format!(r#"\b{token}="([^"]*)""#));
    let Some(reason) = pattern
        .captures(body)
        .ok()
        .flatten()
        .and_then(|c| c.get(1).map(|g| g.as_str().to_owned()))
    else {
        return false;
    };
    if reason.split_whitespace().count() < 2 || reason.chars().count() < 8 {
        return false;
    }
    let shown: String = reason.chars().take(200).collect();
    let _ = log::write(&log::Entry {
        guard: "checks",
        event: "escaped",
        detail: &shown,
        rule: &token.to_lowercase().replace('_', "-"),
        context: None,
        input: &Value::Null,
        session_name: "",
    });
    true
}

/// The directory a call with no `cwd` ran in (Claude Code sends one with every hook; a test's call may not): the process's working
/// directory.
#[cfg(not(any(test, feature = "test-env")))]
fn here() -> String {
    std::env::current_dir()
        .map(|d| d.to_string_lossy().into_owned())
        .unwrap_or_default()
}

/// A test build's: the test thread's own `PWD` (`crate::env`), and where the test names none no tree, so no test's call reaches a
/// live clone's check state (451 T123: the guard's `PostToolUse` with no cwd, its tests run in the landing worktree while a review held
/// a section of the clone, found the hold through the common dir, wrote it back and failed the landing).
#[cfg(any(test, feature = "test-env"))]
fn here() -> String {
    crate::env::opt("PWD").unwrap_or_else(|| "/nonexistent-l7r-test-cwd".to_owned())
}

/// The tree a call's work is in, which the plan hold snapshots, judges and writes back (451 T306, T295's D3 limit): a Bash call's
/// is where its command lands as the walk reads its `cd`s and `-C`s - its first write's tree, else the tree it ends in - so a
/// builder's `cd <worktree> && sed -i ... plan.md`, run with the session's clone as its cwd, is judged in the worktree, where it was
/// neither refused nor written back. A command naming no `cd` or `-C` lands in its cwd and is not walked; any other tool's call is
/// its cwd's tree.
pub(crate) fn call_root(payload: &Value) -> Option<std::path::PathBuf> {
    let cwd = cwd_of(payload);
    let input = tool_input(payload);
    let command = text(&input, "command");
    if text(payload, "tool_name") == "Bash" && (command.contains("cd ") || command.contains("-C "))
    {
        let home = crate::env::var("HOME");
        let walk = crate::tree::walk_judged(command, Some(&cwd), "", &home);
        let landed = walk
            .targets
            .iter()
            .find_map(|t| t.path.as_deref())
            .or(walk.final_dir.as_deref());
        if let Some(root) = landed.and_then(clone_root) {
            return Some(root);
        }
    }
    clone_root(&cwd)
}

/// The directory of the call `payload` describes: its `cwd`, else [`here`].
#[must_use]
pub fn cwd_of(payload: &Value) -> String {
    let cwd = text(payload, "cwd");
    if cwd.is_empty() {
        here()
    } else {
        cwd.to_owned()
    }
}

/// One hook event; a refusal message (the hook exits 2 with it) or "". Held under the state's lock.
pub fn handle(mode: &str, payload: &Value, at: Option<f64>) -> String {
    let Some(path) = state_path(&cwd_of(payload)) else {
        return String::new();
    };
    let held = locked(&path);
    let out = handle_locked(mode, payload, &path, at.unwrap_or_else(now));
    drop(held);
    out
}

/// The feature a state counts under, its root read off where the state file sits.
fn current_feature(path: &Path, payload: &Value) -> String {
    let parent = parent_of(path);
    let owner = if name_of(parent) == ".git" {
        parent_of(parent).to_path_buf()
    } else {
        std::path::PathBuf::from(cwd_of(payload))
    };
    arbiter::feature_dir(&owner, "").map_or_else(String::new, |d| name_of(&d))
}

fn tool_input(payload: &Value) -> Value {
    payload
        .get("tool_input")
        .filter(|v| v.is_object())
        .cloned()
        .unwrap_or_else(|| json!({}))
}

fn str_values(ti: &Value) -> String {
    ti.as_object()
        .into_iter()
        .flatten()
        .map(|(_, v)| arbiter::py_text(v))
        .collect::<Vec<_>>()
        .join(" ")
}

/// A launch's or a return's bookkeeping, the state saved by the caller.
fn book_keep(mode: &str, tool: &str, state: &mut Value, payload: &Value, ti: &Value, path: &Path) {
    match (mode, tool) {
        ("launched", "Agent") => {
            let resp = payload
                .get("tool_response")
                .filter(|v| v.is_object())
                .cloned()
                .unwrap_or(json!({}));
            planhold::launched(state, text(payload, "tool_use_id"), text(&resp, "agentId"));
            rounds::launched(
                state,
                text(payload, "tool_use_id"),
                text(&resp, "agentId"),
                text(&resp, "status") == "async_launched",
                &super::reply::response_text(&resp),
                Some(&parent_of(path).join("check-replies")),
            );
        }
        ("launched", "TaskStop") => {
            let stopped = if text(ti, "task_id").is_empty() {
                text(ti, "shell_id")
            } else {
                text(ti, "task_id")
            };
            planhold::returned(state, stopped);
            for d in map_mut(state, "dispatches").values_mut() {
                if !stopped.is_empty()
                    && text(d, "aid") == stopped
                    && matches!(text(d, "state"), "running" | "pending")
                {
                    d["state"] = json!("answered");
                    d["closed"] = json!("stopped by the session (TaskStop)");
                }
            }
        }
        _ => {
            planhold::returned(state, text(payload, "agent_id"));
            rounds::pair_wave(
                state,
                text(payload, "agent_id"),
                text(payload, "agent_transcript_path"),
            );
            let reply_text = super::reply::reply_of(
                text(payload, "agent_transcript_path"),
                text(payload, "last_assistant_message"),
            );
            rounds::returned(
                state,
                text(payload, "agent_id"),
                &reply_text,
                Some(&parent_of(path).join("check-replies")),
            );
        }
    }
}

fn handle_locked(mode: &str, payload: &Value, path: &Path, t: f64) -> String {
    if mode == "returned" || mode == "launched" {
        passes::log_pass(parent_of(path), mode, payload, t);
    }
    let mut state = load(path);
    if mode == "edit" && !falsy(state.get("plan_holds")) {
        let was = hold_part(&state);
        planhold::snapshot(&mut state, call_root(payload).as_deref(), t);
        if hold_part(&state) != was {
            let _ = save(path, &state);
        }
    }
    let feature = current_feature(path, payload);
    let switched = state.get("feature").and_then(Value::as_str) != Some(feature.as_str());
    if switched {
        // A RECORD CHECK'S COUNT FOLLOWS ITS UNIT, whatever feature is active (451 T227): a change of feature wiped every count, so
        // record-format's rounds on 0097 in one feature were unseen in the next and no third round was held (2026-11-24). Nothing is
        // wiped now; a unit counted before keeps the feature it was counted in as its home, where its triggers are filed and ruled.
        let old = text(&state, "feature").to_owned();
        let units: Vec<String> = state
            .get("rounds")
            .and_then(Value::as_object)
            .map(|m| m.keys().cloned().collect())
            .unwrap_or_default();
        let homes = map_mut(&mut state, "round_home");
        for unit in units.into_iter().filter(|_| !old.is_empty()) {
            homes.entry(unit).or_insert_with(|| json!(old));
        }
        state["feature"] = json!(feature);
    }
    let ti = tool_input(payload);
    let tool = text(payload, "tool_name");
    let mut out = String::new();
    match (mode, tool) {
        ("dispatch", "Agent") => match dispatch_mode(&mut state, payload, &ti, path, t) {
            Flow::Return(msg) => return msg,
            Flow::Continue(said) => out = said,
        },
        ("launched", "Agent" | "TaskStop") | ("returned", _) => {
            // a launch or return no dispatch or hold names changes nothing: neither booked nor saved (451 T387: 98 ms on every Agent
            // call's end; a clone and compare of the 3.0 MB state to find that out cost 55 ms of it, measured 2026-11-27)
            if !switched && !concerns(mode, tool, &state, payload) {
                return out;
            }
            book_keep(mode, tool, &mut state, payload, &ti, path);
        }
        ("after", _) => {
            let root = call_root(payload);
            let was = hold_part(&state);
            let msg = planhold::restore(&mut state, root.as_deref(), text(payload, "tool_use_id"));
            if switched || hold_part(&state) != was {
                let _ = save(path, &state);
            }
            if !msg.is_empty() {
                if let Some(r) = root.as_deref() {
                    crate::usage::append(&super::common_dir(r), USAGE_LOG_TOOL, "step", "changed");
                }
            }
            return msg;
        }
        ("edit", _) => {
            return edit_mode(&state, payload, &ti, tool, t);
        }
        _ => return String::new(),
    }
    if out.is_empty() {
        let _ = save(path, &state);
    } else {
        keep_trips(path, &state);
    }
    out
}

/// What the plan hold reads and writes of the state - its holds and their kept text - compared around a call's snapshot and restore,
/// so the 3.0 MB state is saved only where one changed (451 T387).
fn hold_part(state: &Value) -> (Option<Value>, Option<Value>) {
    (
        state.get("plan_holds").cloned(),
        state.get("plan_snaps").cloned(),
    )
}

/// Whether a launch or a return books anything: an Agent launch whose call id is a dispatch's or a hold's; a return whose agent is
/// a dispatch's or a hold's, or that a wave dispatch still waiting for its agent could be paired with (`rounds::pair_wave`); a
/// `TaskStop`, always (451 T387).
fn concerns(mode: &str, tool: &str, state: &Value, payload: &Value) -> bool {
    let rows = |key: &str| {
        state
            .get(key)
            .and_then(Value::as_object)
            .into_iter()
            .flatten()
    };
    if mode == "launched" && tool == "Agent" {
        let tid = text(payload, "tool_use_id");
        return rows("dispatches")
            .chain(rows("plan_holds"))
            .any(|(k, _)| k == tid);
    }
    if mode == "launched" {
        return true;
    }
    let aid = text(payload, "agent_id");
    rows("dispatches").chain(rows("plan_holds")).any(|(_, d)| {
        text(d, "aid") == aid
            || (!falsy(d.get("wave"))
                && (text(d, "state") == "pending"
                    || (text(d, "state") == "returned" && falsy(d.get("reply")))))
    })
}

/// A REFUSED dispatch saves nothing of what it counted - but the footnote hold's own record must outlive its refusal: the trigger
/// it tripped (`flag_trips`) and the flags a ruling reset (`flags`), written onto the state as it stands on disk. WHY (feature 454's
/// check session, 2026-11-24, ruling `ask:454-c1b-fixloop-retrip`): the trip was written into a state never saved, so a ruled
/// trigger was never matched to its footnote and the same footnote tripped a new round number at every dispatch - three trips and
/// three arbiter dispatches with no round run. `GUARD_EDIT_OK`: fixing a guard that fires on correct work.
fn keep_trips(path: &Path, state: &Value) {
    // GUARD_EDIT_OK: the same fix, written with no branch a test cannot reach (the coverage floor)
    let trips = state.get("flag_trips").cloned().unwrap_or(Value::Null);
    let mut kept = load(path);
    let moved = kept.get("flag_trips") != Some(&trips) || kept.get("flags") != state.get("flags");
    if trips.is_object() && kept.is_object() && moved {
        kept["flag_trips"] = trips;
        kept["flags"] = state.get("flags").cloned().unwrap_or(Value::Null);
        let _ = save(path, &kept);
    }
}

/// What the `dispatch` branch decided.
enum Flow {
    /// `_handle` returns this now, nothing further saved.
    Return(String),
    /// The dispatch went through its counter; `out` is its refusal or "".
    Continue(String),
}

fn dispatch_mode(state: &mut Value, payload: &Value, ti: &Value, path: &Path, t: f64) -> Flow {
    let check = text(ti, "subagent_type").to_owned();
    let root = clone_root(&cwd_of(payload));
    let prompt = text(ti, "prompt").to_owned();
    if check == "round-arbiter" {
        let (_, body) = manifest_of(&prompt);
        let trigger = TRIGGER_LINE
            .captures(&body)
            .ok()
            .flatten()
            .map(|c| c[1].trim().to_owned());
        if let (Some(r), Some(trig)) = (root.as_deref(), trigger) {
            if arbiter::rulings(r, "").contains_key(&trig) {
                return Flow::Return(format!("{trig} is already ruled - one ruling per trigger, binding (feature 375 FR-011)"));
            }
        }
        return Flow::Return(String::new());
    }
    if check == "spec-fidelity" {
        let tid = text(payload, "tool_use_id");
        let id = if tid.is_empty() {
            crate::pyjson::py_float(t)
        } else {
            tid.to_owned()
        };
        planhold::hold(state, &id, &prompt, t, root.as_deref());
        let _ = save(path, state);
    }
    if check == "work-budget" && root.is_some() && !escaped("ARBITER_OK", &prompt) {
        let r = root.as_deref().map_or(Path::new("."), |d| d);
        let why = budget::refusal(
            arbiter::feature_dir(r, "").as_deref(),
            &arbiter::rulings(r, ""),
            &prompt,
        );
        if !why.is_empty() {
            return Flow::Return(why);
        }
    }
    if !is_check_kind(&check) {
        return Flow::Return(String::new());
    }
    let (manifest, body) = manifest_of(&prompt);
    let freeze_ok = escaped("FREEZE_OK", &prompt);
    let arbiter_ok = escaped("ARBITER_OK", &prompt);
    if let (Some(r), true) = (root.as_deref(), PAGE_CHECKS.contains(&check.as_str())) {
        versions(state, r, &body, t);
    }
    if !escaped("BATCH_OK", &prompt) {
        if let Some(held) = batch_refusal(root.as_deref(), &check, &body, t) {
            return Flow::Return(held);
        }
    }
    let tid_given = text(payload, "tool_use_id");
    let tid = if tid_given.is_empty() {
        crate::pyjson::py_float(t)
    } else {
        tid_given.to_owned()
    };
    let out = rounds::dispatch(
        state,
        &Dispatch {
            tid: &tid,
            check: &check,
            manifest: &manifest,
            text: &body,
            now: t,
            root: root.as_deref(),
            freeze_ok,
            arbiter_ok,
            who: arbiter::Who {
                sid: text(payload, "session_id"),
                by: text(payload, "agent_id"),
            },
        },
    );
    if out.is_empty() && tid.starts_with("wave:") {
        let row = &mut map_mut(state, "dispatches")[&tid];
        row["wave"] = json!(rounds::wave_key(&prompt));
        row["wave_len"] = json!(collapsed_len(&prompt));
    }
    if out.is_empty() {
        if let Some(r) = root.as_deref() {
            cascade_check(state, r, t);
        }
    }
    Flow::Continue(out)
}

fn collapsed_len(prompt: &str) -> usize {
    prompt
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
        .chars()
        .count()
}

fn versions(state: &mut Value, root: &Path, body: &str, t: f64) {
    for s in rounds::subjects_of_manifest(body) {
        let cur = subject_blocks(root, &s);
        let vs = map_mut(state, "versions")
            .entry(s.clone())
            .or_insert_with(|| json!([]))
            .as_array_mut()
            .unwrap_or_else(|| unreachable!("versions is a list"));
        let last_is_cur = vs.last().and_then(Value::as_array).is_some_and(|l| {
            l.iter().filter_map(Value::as_str).collect::<Vec<_>>()
                == cur.iter().map(String::as_str).collect::<Vec<_>>()
        });
        if !cur.is_empty() && !last_is_cur {
            vs.push(json!(cur));
            let overflow = vs.len().saturating_sub(12);
            vs.drain(..overflow);
            let history: Vec<Vec<String>> = vs
                .iter()
                .map(|v| {
                    v.as_array()
                        .into_iter()
                        .flatten()
                        .filter_map(|x| x.as_str().map(str::to_owned))
                        .collect()
                })
                .collect();
            let back = rounds::oscillation(&history);
            if !back.is_empty() {
                let trig = format!("reversal:{s}@{}", history.len());
                let detail = format!("{s}: a block dropped earlier is back - \"{back}...\"");
                let _ = arbiter::trip(root, &trig, "reversal", &s, &detail, &json!(t), "");
            }
        }
    }
}

fn cascade_check(state: &Value, root: &Path, t: f64) {
    let since = rounds::window_start(root);
    let n = rounds::dispatches_since(state, since);
    let (trigger, last) = arbiter::cascade_state(root, since);
    // the minimum first (451 T492): under it the trip cannot fire, so the work-tree diff (40 to 79 ms, 451 T388) is not run
    if !arbiter::cascade_can_trip(n, last) {
        return;
    }
    let lines = rounds::changed_lines(root);
    if arbiter::cascade(n, lines, last) {
        let _ = arbiter::trip(
            root,
            &trigger,
            "cascade",
            "",
            &format!("{n} check dispatches over {lines} changed lines"),
            &json!(t),
            "",
        );
    }
}

const POPUP_AGENTS: [&str; 3] = ["modal-form", "modal-depiction", "modal-research"];
const BATCHES: &str = "modal-batches.json";
const BATCHES_FRESH_S: f64 = 7200.0;

fn unit_uid(line: &str) -> Option<String> {
    let c = UNIT_UID.captures(line).ok().flatten()?;
    c[1].split_once(':').map(|(_, rest)| rest.to_owned())
}

/// A pop-up agent sent on ONE pop-up while `make record-owed` names it in a batch of two or more for the same agent; the refusal, or None.
fn batch_refusal(root: Option<&Path>, check: &str, body: &str, t: f64) -> Option<String> {
    let root = root?;
    if !POPUP_AGENTS.contains(&check) {
        return None;
    }
    let uids: std::collections::BTreeSet<String> = body.lines().filter_map(unit_uid).collect();
    if uids.len() != 1 {
        return None;
    }
    let uid = uids.into_iter().next().unwrap_or_default();
    let gd = super::git_stdout(
        root,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    );
    let rec: Value =
        serde_json::from_str(&std::fs::read_to_string(Path::new(&gd).join(BATCHES)).ok()?).ok()?;
    let kinds: Vec<String> = rec
        .get("batches")
        .and_then(|b| b.get(check))
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_owned))
        .collect();
    let utc = rec.get("utc").and_then(Value::as_f64).unwrap_or(0.0);
    if t - utc > BATCHES_FRESH_S
        || kinds.len() < 2
        || !kinds
            .iter()
            .any(|k| uid == *k || uid.ends_with(k.as_str()) || k.ends_with(uid.as_str()))
    {
        return None;
    }
    Some(batch_said(check, &kinds))
}

/// The batch refusal's words over its pop-ups (feature 385 T81: one agent on them all). Its list is its fix command's argument, so it
/// is never capped (`shared::listed`); 451 T177 holds it at its worst case in `suite_tools/messages/worst.rs` instead. `, batched`
/// ends it, since [`escape_for`] reads its escape, `BATCH_OK`, from that.
#[must_use]
pub fn batch_said(check: &str, kinds: &[String]) -> String {
    format!(
        "{} pop-ups owe {check} together - send ONE agent on them all: make modal-bundle KIND=\"{}\" FOR={check}, batched",
        kinds.len(),
        kinds.join(" ")
    )
}

fn edit_mode(state: &Value, payload: &Value, ti: &Value, tool: &str, t: f64) -> String {
    let root = clone_root(&cwd_of(payload));
    let held = planhold::refusal(state, call_root(payload).as_deref(), tool, ti, t);
    if !held.is_empty() {
        return held;
    }
    if tool == "Bash" {
        let command = text(ti, "command");
        if let Some(r) = root
            .as_deref()
            // the gate, read by the one make detector (feature 451 D1), as `record_edit_gate`'s prefilter reads it
            .filter(|_| crate::make::invoked(command).iter().any(|t| t == "done"))
        {
            let blocking = arbiter::blocking(r, "", true);
            if !blocking.is_empty() && !escaped("ARBITER_OK", command) {
                return arbiter::refusal_unbatched(&blocking, r);
            }
        }
        return if escaped("FREEZE_OK", command) {
            String::new()
        } else {
            rounds::apply_refusal(state, command, t)
        };
    }
    if matches!(tool, "Edit" | "Write" | "MultiEdit") {
        if escaped("FREEZE_OK", &str_values(ti)) {
            return String::new();
        }
        let old = if tool == "Edit" {
            text(ti, "old_string")
        } else {
            ""
        };
        let new_text = if text(ti, "new_string").is_empty() {
            text(ti, "content")
        } else {
            text(ti, "new_string")
        };
        return rounds::edit_refusal(state, text(ti, "file_path"), old, new_text, t);
    }
    String::new()
}

/// The escape that reaches the rule which refused (`hm_checks.escape_for`).
#[must_use]
pub fn escape_for(msg: &str) -> &'static str {
    if msg.ends_with(", batched") {
        "BATCH_OK"
    } else if msg.contains("arbiter") {
        MANIFEST_REASON_TOKENS[1]
    } else {
        MANIFEST_REASON_TOKENS[0]
    }
}

/// The refusal as the hook's stderr writes it: `BLOCKED: <msg>` and the escape line, which a message naming its escape already
/// goes without (451 T170, message-check: the tripwire refusal says `ARBITER_OK` in full; the line's source path,
/// `scripts/hooks/lib/hm_checks.py`, named a file deleted with the Python guards).
#[must_use]
pub fn blocked_text(msg: &str) -> String {
    let escape = escape_for(msg);
    if msg.contains(&format!("{escape}=")) {
        format!("BLOCKED: {msg}\n")
    } else {
        format!("BLOCKED: {msg}\n(escape {escape}=\"<reason>\" in the prompt or the edit)\n")
    }
}

/// `make check-closed`: `(exit code, stdout, stderr)`.
#[must_use]
pub fn close(
    root: &Path,
    subject: &str,
    reason: &str,
    at: f64,
    agent: &str,
) -> (i32, String, String) {
    let path = state_path(&root.to_string_lossy());
    let lock = path.as_deref().and_then(locked);
    let mut state = path.as_deref().map_or_else(super::empty, load);
    if !escaped("CHECK_CLOSED", &format!("CHECK_CLOSED=\"{reason}\"")) {
        drop(lock);
        return (2, String::new(), "check-closed: REASON needs two words and eight characters - it is what a later audit reads\n".to_owned());
    }
    let closed = rounds::close_dispatches(&mut state, subject, reason, at, agent);
    if let Some(p) = path.as_deref().filter(|_| closed.closed > 0) {
        let _ = save(p, &state);
    }
    drop(lock);
    let tail = if closed.still_running > 0 {
        format!(
            "; {} still running and not silent: wait for them",
            closed.still_running
        )
    } else {
        String::new()
    };
    (
        0,
        format!(
            "check-closed: {} silent dispatch(es) on {subject} closed - {reason}{tail}\n",
            closed.closed
        ),
        String::new(),
    )
}

#[cfg(test)]
mod hold_writes;
#[cfg(test)]
mod tests;
