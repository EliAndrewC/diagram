//! A plan section or block is held while its review runs (feature 385 T85, from `hm_planhold.py`): a write that would change held text is refused, naming the running review; a `PLAN_EDIT_OK` passes only a dead hold.

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::{map_mut, resolved, text};
use crate::shared::plan_text::{blocks, task_sections};

/// A plan review returns in about 1-4 minutes (the evening's 42); past half an hour its hold is dead.
const HOLD_MAX_S: f64 = 1800.0;
const PENDING_S: f64 = 60.0;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static BUNDLE: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(\S*/plan-(\d{3}-[a-z0-9-]+?)-(?:(T\d+[a-z]?)|blocks-[\w-]+))/MANIFEST\.md")
});
static WRITE: LazyLock<Regex> = LazyLock::new(|| {
    re(r#"open\([^)]*['"][wa]['"]|write_text|\bsed\s+(?:-\S+\s+)*-i|>\s*['"]?\S*plan\.md|\btee\b"#)
});
static BLOCK_KEY: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?m)^<!-- block "((?:[^"\\]|\\.)*)" sha256"#));
static QUOTED: LazyLock<Regex> =
    LazyLock::new(|| re(r#""((?:[^"\\\n]|\\.){12,})"|'([^'\n]{12,})'"#));

/// `key.encode().decode("unicode_escape")`, as the Python decoded a held block's key: each backslash escape read, every other byte taken as one Latin-1 character (a non-ASCII key reads garbled, as it always did - and so matches no block, a bug the port keeps, FR-002).
fn unescape_key(key: &str) -> String {
    let bytes = key.as_bytes();
    let mut out = String::with_capacity(key.len());
    let mut i = 0;
    while i < bytes.len() {
        let escape = (bytes[i] == b'\\')
            .then(|| bytes.get(i + 1).copied())
            .flatten();
        let simple = escape.and_then(|n| match n {
            b'\\' => Some('\\'),
            b'"' => Some('"'),
            b'\'' => Some('\''),
            b'n' => Some('\n'),
            b't' => Some('\t'),
            b'r' => Some('\r'),
            b'a' => Some('\x07'),
            b'b' => Some('\x08'),
            b'f' => Some('\x0c'),
            b'v' => Some('\x0b'),
            _ => None,
        });
        if let Some(c) = simple {
            out.push(c);
            i += 2;
        } else {
            out.push(char::from(bytes[i]));
            i += 1;
        }
    }
    out
}

/// Record the hold a plan review's dispatch takes (at its `PreToolUse`).
pub fn hold(state: &mut Value, tid: &str, prompt: &str, now: f64) {
    let Ok(Some(m)) = BUNDLE.captures(prompt) else {
        return;
    };
    let bundle = m.get(1).map_or("", |g| g.as_str()).to_owned();
    let feature = m.get(2).map_or("", |g| g.as_str()).to_owned();
    let task = m.get(3).map(|g| g.as_str().to_owned());
    let keys: Vec<String> = if task.is_some() {
        Vec::new()
    } else {
        let text =
            std::fs::read_to_string(Path::new(&bundle).join("blocks.md")).unwrap_or_default();
        BLOCK_KEY
            .captures_iter(&text)
            .flatten()
            .map(|c| unescape_key(&c[1]))
            .collect()
    };
    map_mut(state, "plan_holds").insert(
        tid.to_owned(),
        json!({"feature": feature, "task": task.unwrap_or_default(), "blocks": keys, "t": now, "state": "pending"}),
    );
}

/// A hold's launch: its agent id.
pub fn launched(state: &mut Value, tid: &str, agent_id: &str) {
    if let Some(h) = state
        .get_mut("plan_holds")
        .and_then(Value::as_object_mut)
        .and_then(|holds| holds.get_mut(tid))
    {
        h["state"] = json!("running");
        h["aid"] = json!(agent_id);
    }
}

/// A review's return: its holds go.
pub fn returned(state: &mut Value, agent_id: &str) {
    if let Some(holds) = state.get_mut("plan_holds").and_then(Value::as_object_mut) {
        holds.retain(|_, h| h.get("aid").and_then(Value::as_str) != Some(agent_id));
    }
}

fn t_of(h: &Value) -> f64 {
    h.get("t").and_then(Value::as_f64).unwrap_or(0.0)
}

fn dead(h: &Value, now: f64) -> bool {
    (text(h, "state") == "pending" && now - t_of(h) > PENDING_S) || now - t_of(h) > HOLD_MAX_S
}

fn held(root: &Path, h: &Value) -> Vec<String> {
    let plan = root.join("specs").join(text(h, "feature")).join("plan.md");
    let Ok(body) = std::fs::read_to_string(plan) else {
        return Vec::new();
    };
    let task = text(h, "task");
    if !task.is_empty() {
        return task_sections(&body)
            .get(task)
            .filter(|s| !s.is_empty())
            .cloned()
            .into_iter()
            .collect();
    }
    let want: Vec<&str> = h
        .get("blocks")
        .and_then(Value::as_array)
        .map(|a| a.iter().filter_map(Value::as_str).collect())
        .unwrap_or_default();
    blocks(&body)
        .into_iter()
        .filter(|(k, ..)| want.contains(&k.as_str()))
        .map(|(_, b, _)| b)
        .collect()
}

/// A hold whose review was launched and has not died (`hm_planhold.live`).
#[must_use]
pub fn live(h: &Value, now: f64) -> bool {
    text(h, "state") == "running" && !dead(h, now)
}

/// A pending hold past `PENDING_S` never launched and never will: it goes, so an empty state starts nothing.
pub fn purge(state: &mut Value, now: f64) {
    if let Some(holds) = state.get_mut("plan_holds").and_then(Value::as_object_mut) {
        holds.retain(|_, h| !(text(h, "state") == "pending" && now - t_of(h) > PENDING_S));
    }
}

/// Before a write: the texts each live hold holds, kept under the call's id.
pub fn snapshot(state: &mut Value, root: Option<&Path>, tid: &str, now: f64) {
    purge(state, now);
    let Some(root) = root else {
        return;
    };
    let snaps: Map<String, Value> = state
        .get("plan_holds")
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
        .filter(|(_, h)| live(h, now))
        .map(|(id, h)| (id.clone(), json!(held(root, h))))
        .collect();
    if !snaps.is_empty() {
        map_mut(state, "plan_snaps").insert(tid.to_owned(), Value::Object(snaps));
    }
}

fn set_of(snaps: &Value) -> BTreeSet<String> {
    snaps
        .as_object()
        .into_iter()
        .flatten()
        .map(|(k, _)| k.clone())
        .collect()
}

fn describe(h: &Value) -> String {
    if text(h, "task").is_empty() {
        format!(
            "{} block(s)",
            h.get("blocks")
                .and_then(Value::as_array)
                .map_or(0, Vec::len)
        )
    } else {
        format!("{}'s section", text(h, "task"))
    }
}

/// `blocks` in the plan with the held ones of this hold, in document order (`hm_planhold.restore`'s `now_blocks`).
fn current_blocks(body: &str, want: &[&str]) -> Vec<(String, String)> {
    let mut seen = BTreeSet::new();
    blocks(body)
        .into_iter()
        .filter(|(k, ..)| want.contains(&k.as_str()) && seen.insert(k.clone()))
        .map(|(k, b, _)| (k, b))
        .collect()
}

fn write_back(root: &Path, h: &Value, before: &[String]) -> Option<String> {
    let plan = root.join("specs").join(text(h, "feature")).join("plan.md");
    let mut body = std::fs::read_to_string(&plan).ok()?;
    let task = text(h, "task");
    if task.is_empty() {
        let want: Vec<&str> = h
            .get("blocks")
            .and_then(Value::as_array)
            .map(|a| a.iter().filter_map(Value::as_str).collect())
            .unwrap_or_default();
        for ((_, now_body), old) in current_blocks(&body, &want).iter().zip(before) {
            if now_body != old {
                body = body.replacen(now_body, old, 1);
            }
        }
    } else if let (Some(sec), Some(first)) = (
        task_sections(&body).remove(task).filter(|s| !s.is_empty()),
        before.first(),
    ) {
        body = body.replacen(&sec, first, 1);
    }
    std::fs::write(&plan, body).ok()?;
    Some(format!(
        "that call changed {} of specs/{}/plan.md while its plan review runs (agent {}) - the held text is written back; wait for the review to return (feature 385 T85, hour 30's fix)",
        describe(h),
        text(h, "feature"),
        text(h, "aid")
    ))
}

/// After the write: any held text it changed is written back and the change refused, naming the review; or "".
pub fn restore(state: &mut Value, root: Option<&Path>, tid: &str) -> String {
    let snaps = state
        .get_mut("plan_snaps")
        .and_then(Value::as_object_mut)
        .and_then(|m| m.shift_remove(tid));
    let open: BTreeSet<String> = state.get("plan_holds").map_or_else(BTreeSet::new, set_of);
    if let Some(all) = state.get_mut("plan_snaps").and_then(Value::as_object_mut) {
        all.retain(|_, s| !set_of(s).is_disjoint(&open));
        if all.is_empty() {
            state
                .as_object_mut()
                .and_then(|m| m.shift_remove("plan_snaps"));
        }
    }
    let (Some(root), Some(snaps)) = (root, snaps) else {
        return String::new();
    };
    let holds = state.get("plan_holds").cloned().unwrap_or(Value::Null);
    for (hid, before) in snaps.as_object().into_iter().flatten() {
        let Some(h) = holds.get(hid).filter(|h| !h.is_null()) else {
            continue;
        };
        let before: Vec<String> = before
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|v| v.as_str().map(str::to_owned))
                    .collect()
            })
            .unwrap_or_default();
        if held(root, h) == before {
            continue;
        }
        if let Some(msg) = write_back(root, h, &before) {
            return msg;
        }
    }
    String::new()
}

/// Whether held text `texts` would change under an Edit of the plan with `old`.
fn edit_hits(plan: &Path, texts: &[String], old: &str) -> bool {
    let current = std::fs::read_to_string(plan).unwrap_or_default();
    let at = if old.is_empty() {
        None
    } else {
        current.find(old)
    };
    texts.iter().any(|t| {
        current
            .find(t.as_str())
            .is_some_and(|start| at.is_some_and(|a| start <= a && a <= start + t.len()))
    }) || texts.iter().any(|t| !old.is_empty() && t.contains(old))
}

fn bash_hits(cmd: &str, feature: &str, texts: &[String]) -> bool {
    if !(cmd.contains("plan.md") && cmd.contains(feature) && WRITE.is_match(cmd).unwrap_or(false)) {
        return false;
    }
    let lines: BTreeSet<&str> = texts
        .iter()
        .flat_map(|t| t.lines())
        .map(str::trim)
        .filter(|l| l.len() >= 16)
        .collect();
    let heads: BTreeSet<&str> = texts
        .iter()
        .filter(|t| !t.trim().is_empty())
        .map(|t| t.lines().next().unwrap_or("").trim())
        .collect();
    let quoted: Vec<String> = QUOTED
        .captures_iter(cmd)
        .flatten()
        .flat_map(|c| [c.get(1), c.get(2)])
        .flatten()
        .map(|g| g.as_str().to_owned())
        .collect();
    heads.iter().any(|h| cmd.contains(h))
        || lines.iter().any(|l| cmd.contains(l))
        || quoted.iter().any(|q| texts.iter().any(|t| t.contains(q)))
}

/// Why this write is refused while a plan review holds what it would change, or "".
pub fn refusal(
    state: &Value,
    root: Option<&Path>,
    tool: &str,
    ti: &Value,
    now: f64,
    escaped: bool,
) -> String {
    let Some(root) = root else {
        return String::new();
    };
    for h in state
        .get("plan_holds")
        .and_then(Value::as_object)
        .map(|m| m.values().cloned().collect::<Vec<_>>())
        .unwrap_or_default()
    {
        let plan = root.join("specs").join(text(&h, "feature")).join("plan.md");
        let texts = held(root, &h);
        let never = text(&h, "state") == "pending" && now - t_of(&h) > PENDING_S;
        if texts.is_empty() || never || (escaped && dead(&h, now)) {
            continue;
        }
        let hit = if matches!(tool, "Edit" | "Write" | "MultiEdit")
            && resolved(Path::new(text(ti, "file_path"))) == resolved(&plan)
        {
            if tool == "Write" {
                let content = text(ti, "content");
                texts.iter().any(|t| !content.contains(t.as_str()))
            } else {
                edit_hits(&plan, &texts, text(ti, "old_string"))
            }
        } else if tool == "Bash" {
            bash_hits(text(ti, "command"), text(&h, "feature"), &texts)
        } else {
            false
        };
        if hit {
            let who = if text(&h, "aid").is_empty() {
                "a dispatch not yet launched".to_owned()
            } else {
                format!("agent {}", text(&h, "aid"))
            };
            let tail = if dead(&h, now) {
                "; its dispatch looks dead: PLAN_EDIT_OK=\"<reason>\" passes it"
            } else {
                ""
            };
            return format!(
                "the plan review of {} in specs/{}/plan.md is running ({who}) - an edit now voids its verdict; wait for it to return (feature 385 T85){tail}",
                describe(&h),
                text(&h, "feature")
            );
        }
    }
    String::new()
}

#[cfg(test)]
mod tests;
