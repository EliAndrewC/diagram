//! The pairing's own state (plan T006 decision (c)): what `pair-hooks.sh` kept through inline Python, ported over the same files and
//! formats - the pairing state (`.git/pairing-state.json`), the review rounds (`.git/review-rounds.json`), the dispatch record, the
//! bypass log (`dev/bypass-log/<YYYY-MM>/`), the engine key's cache (`.git/pairing-key`) and the gate's freshness.

use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::{json, Map, Value};

use crate::shared::sha256;
use crate::shared::tool::ask;

/// A JSON object read from `p`, or an empty one (`except Exception: d = {}`).
fn object(p: &Path) -> Map<String, Value> {
    std::fs::read_to_string(p)
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| v.as_object().cloned())
        .unwrap_or_default()
}

/// `v` written as Python's `json.dumps(v, indent=n)` writes it (n spaces, `": "` and `","` at line ends).
fn dumps(v: &Value, indent: usize) -> String {
    let mut out = Vec::new();
    let pad = vec![b' '; indent];
    let mut writer = serde_json::Serializer::with_formatter(
        &mut out,
        serde_json::ser::PrettyFormatter::with_indent(&pad),
    );
    // a Value always serializes; an error would leave the buffer as far as it got
    let _ = serde::Serialize::serialize(v, &mut writer);
    String::from_utf8_lossy(&out).into_owned()
}

/// The pairing state file of `clone`.
#[must_use]
pub fn pairing_file(clone: &Path) -> PathBuf {
    clone.join(".git/pairing-state.json")
}

/// Set `field` to `value` in the pairing state (`write_pairing`).
pub fn write_pairing(clone: &Path, field: &str, value: &str) {
    let p = pairing_file(clone);
    let mut d = object(&p);
    d.insert(field.to_owned(), Value::String(value.to_owned()));
    let _ = std::fs::write(&p, dumps(&Value::Object(d), 2));
}

/// The clock, injectable only in a fixture (`pair_now`): `PAIR_NOW` where the clone is a temporary tree.
#[must_use]
pub fn now(clone: &Path) -> i64 {
    let c = clone.to_string_lossy();
    let fixture = c.contains("/test-") || c.contains("/tmp.") || c.starts_with("/tmp/");
    if fixture {
        if let Some(n) = std::env::var("PAIR_NOW")
            .ok()
            .and_then(|n| n.trim().parse().ok())
        {
            return n;
        }
    }
    wall()
}

/// A parallel span's bound (`PARALLEL_SPAN_S`): a definition, not a measurement - parallel calls land within seconds, a sequential one
/// is a model turn later.
const PARALLEL_SPAN_S: i64 = 60;

/// Record `map`'s dispatch at `key`; "parallel <span>" or "serialized <span>" when the last of the `owed` maps was just dispatched.
#[must_use]
pub fn record_dispatch(clone: &Path, map: &str, key: &str, at: i64, owed: &[String]) -> String {
    let p = pairing_file(clone);
    let mut d = object(&p);
    let mut disp = d
        .get("dispatched")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    let complete = |disp: &Map<String, Value>| {
        !owed.is_empty()
            && owed.iter().all(|m| {
                disp.get(m)
                    .and_then(|e| e.get("key"))
                    .and_then(Value::as_str)
                    == Some(key)
            })
    };
    let before = complete(&disp);
    disp.insert(map.to_owned(), json!({"key": key, "at": at}));
    let after = complete(&disp);
    d.insert("dispatched".to_owned(), Value::Object(disp.clone()));
    let _ = std::fs::write(&p, dumps(&Value::Object(d), 2));
    if !after || before {
        return String::new();
    }
    let ats: Vec<i64> = owed
        .iter()
        .filter_map(|m| {
            disp.get(m)
                .and_then(|e| e.get("at"))
                .and_then(Value::as_i64)
        })
        .collect();
    let span = ats.iter().max().unwrap_or(&0) - ats.iter().min().unwrap_or(&0);
    format!(
        "{} {span}",
        if span < PARALLEL_SPAN_S {
            "parallel"
        } else {
            "serialized"
        }
    )
}

/// The active feature's directory (`.specify/feature.json`), or "none".
fn feature(clone: &Path) -> String {
    object(&clone.join(".specify/feature.json"))
        .get("feature_directory")
        .and_then(Value::as_str)
        .filter(|f| !f.is_empty())
        .unwrap_or("none")
        .to_owned()
}

/// The round this dispatch of `unit` at `key` would be (`round_number`): the rounds recorded since the feature's tasks last landed,
/// plus this one when its key is new.
#[must_use]
pub fn round_number(clone: &Path, unit: &str, key: &str) -> usize {
    let f = feature(clone);
    let d = object(&clone.join(".git/review-rounds.json"));
    let landed = ask(
        clone,
        "git",
        &[
            "-C",
            &clone.to_string_lossy(),
            "log",
            "-1",
            "--format=%ct",
            "origin/main",
            "--",
            &format!("{f}/tasks.md"),
        ],
        "",
    )
    .out
    .trim()
    .parse::<i64>()
    .unwrap_or(0);
    let at = |k: &str| {
        k.rsplit_once('@')
            .map_or(0, |(_, t)| t.parse::<i64>().unwrap_or(0))
    };
    let keys: Vec<&str> = d
        .get(&f)
        .and_then(|u| u.get(unit))
        .and_then(Value::as_array)
        .map(|ks| {
            ks.iter()
                .filter_map(Value::as_str)
                .filter(|k| at(k) >= landed)
                .map(|k| k.split('@').next().unwrap_or(k))
                .collect()
        })
        .unwrap_or_default();
    keys.len() + usize::from(!keys.contains(&key))
}

/// Count this dispatch's round of `unit` at `key` (`record_round`).
pub fn record_round(clone: &Path, unit: &str, key: &str, at: i64) {
    let p = clone.join(".git/review-rounds.json");
    let f = feature(clone);
    let mut d = object(&p);
    let mut units = d
        .get(&f)
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    let mut keys = units
        .get(unit)
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    if !keys
        .iter()
        .filter_map(Value::as_str)
        .any(|k| k.split('@').next() == Some(key))
    {
        keys.push(Value::String(format!("{key}@{at}")));
    }
    units.insert(unit.to_owned(), Value::Array(keys));
    d.insert(f, Value::Object(units));
    let _ = std::fs::write(&p, dumps(&Value::Object(d), 1));
}

/// The override's reason, where `make bypass-audit` reads it (`log_bypass`): only where the clone keeps a bypass log.
pub fn log_bypass(clone: &Path, why: &str, what: &str, at: SystemTime) {
    let dir = clone.join("dev/bypass-log");
    if !dir.is_dir() {
        return;
    }
    let secs = at.duration_since(UNIX_EPOCH).map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = crate::shared::log::civil(secs);
    let dir = dir.join(format!("{y:04}-{mo:02}"));
    if std::fs::create_dir_all(&dir).is_err() {
        return;
    }
    let stamp = format!("{y:04}{mo:02}{d:02}T{h:02}{mi:02}{s:02}Z");
    let name = format!(
        "{stamp}-{}.json",
        &sha256::hex(format!("{stamp}{what}").as_bytes())[..6]
    );
    let rec = json!({"utc": stamp, "guard": "pair-hooks", "what": what, "reason": why});
    let _ = std::fs::write(dir.join(name), dumps(&rec, 2));
}

/// The working tree's engine key, or "" (`engine_key`): the cached key while no `.py` under `l7r/` or `pool/` is newer than it, else
/// `make engine-key REF=worktree` asked and kept. Asked only on the branches that read it (plan T006 decision (b)).
#[must_use]
pub fn engine_key(clone: &Path) -> String {
    if !clone.is_dir() {
        return String::new();
    }
    let cache = clone.join(".git/pairing-key");
    let kept = std::fs::read_to_string(&cache).unwrap_or_default();
    let stamp = std::fs::metadata(&cache).and_then(|m| m.modified()).ok();
    if !kept.is_empty()
        && stamp
            .is_some_and(|t| !newer_py(&clone.join("l7r"), t) && !newer_py(&clone.join("pool"), t))
    {
        return kept.trim_end_matches('\n').to_owned();
    }
    let key: String = ask(clone, "make", &["-s", "engine-key", "REF=worktree"], "")
        .out
        .split_whitespace()
        .collect();
    if !key.is_empty() {
        let _ = std::fs::write(&cache, &key);
    }
    key
}

/// A `.py` under `dir` modified after `t` (`find <dir> -name '*.py' -newer <cache>`).
fn newer_py(dir: &Path, t: SystemTime) -> bool {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return false;
    };
    entries.filter_map(Result::ok).any(|e| {
        let p = e.path();
        if p.is_dir() {
            newer_py(&p, t)
        } else {
            p.extension().is_some_and(|x| x == "py")
                && e.metadata().and_then(|m| m.modified()).is_ok_and(|m| m > t)
        }
    })
}

/// The clock, unseamed: the seconds since the epoch.
#[must_use]
pub fn wall() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| i64::try_from(d.as_secs()).unwrap_or(0))
}

/// The clone's gate stamp says the gate is fresh (`l7r-gate stamp --fresh diagram`, run whether or not the wrapper is there).
#[must_use]
pub fn stamp_fresh(clone: &Path) -> bool {
    ask(
        clone,
        "bash",
        &[
            &clone.join("scripts/gates/l7r-gate.sh").to_string_lossy(),
            "stamp",
            "--fresh",
            "diagram",
        ],
        "",
    )
    .ok()
}

/// A green gate has seen exactly this content (`gate_green`): the clone's gate stamp, else its recorded verification key.
#[must_use]
pub fn gate_green(clone: &Path, key: &str) -> bool {
    if key.is_empty() {
        return false;
    }
    if clone.join("scripts/gates/l7r-gate.sh").is_file() {
        return stamp_fresh(clone);
    }
    object(&clone.join(".git/verification-state.json"))
        .get("engine_key")
        .and_then(Value::as_str)
        == Some(key)
}

#[cfg(test)]
mod tests;
