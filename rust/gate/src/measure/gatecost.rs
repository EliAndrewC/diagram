//! What a make target has actually been costing, from the recorded runs (feature 162; feature 449 T75, from `gatecost.py`).
//!
//! WHY (GM 2026-08-30): "I think those numbers for `make quick` are wrong and outdated." A number typed into a shell string in August is
//! wrong in September and nothing tells anybody, so no guard message states one: it asks here, and says nothing when the log cannot answer.
//! Green runs only: a failed gate's elapsed time measures where it stopped, not what it costs.

use std::collections::BTreeMap;
use std::path::Path;

use serde_json::Value;

use super::{json_files, median, reply};

const RECENT: usize = 25;

/// What this tree's log and the mirror's hold, a run named once. A checkout under `.clones/` also reads the mirror above it.
fn runs(root: &Path, target: &str, scope: Option<&str>, cache: Option<&str>) -> Vec<Value> {
    let top = root.display().to_string();
    let mirror = top.split("/.clones/").next().unwrap_or(&top).to_owned();
    let mut seen: BTreeMap<String, Value> = BTreeMap::new();
    let tops = if mirror == top {
        vec![top]
    } else {
        vec![top, mirror]
    };
    for tree in tops {
        for path in json_files(&Path::new(&tree).join("dev/run-log")) {
            let Ok(rec) =
                serde_json::from_str::<Value>(&std::fs::read_to_string(&path).unwrap_or_default())
            else {
                continue;
            };
            let wanted = rec["target"] == target
                && rec["result"] == "green"
                && rec["mode"] != "incremental"
                && scope.is_none_or(|s| rec["scope"] == s)
                && cache.is_none_or(|c| rec["cache"] == c);
            if wanted {
                seen.insert(
                    path.file_name()
                        .unwrap_or_default()
                        .to_string_lossy()
                        .into_owned(),
                    rec,
                );
            }
        }
    }
    let mut all: Vec<Value> = seen.into_values().collect();
    all.sort_by_key(|r| r["utc"].as_str().unwrap_or_default().to_owned());
    let start = all.len().saturating_sub(RECENT);
    all.split_off(start)
}

/// The median of recent green runs, of one roll-cache class when asked: "recent" means the last 25 of that class.
#[expect(
    clippy::cast_possible_truncation,
    reason = "Python's int() of a duration in seconds"
)]
pub(crate) fn median_seconds(
    root: &Path,
    target: &str,
    scope: Option<&str>,
    cache: Option<&str>,
) -> Option<i64> {
    let mut seconds: Vec<f64> = runs(root, target, scope, cache)
        .iter()
        .map(|r| r["seconds"].as_f64().unwrap_or(0.0))
        .collect();
    if seconds.is_empty() {
        return None;
    }
    Some(median(&mut seconds) as i64)
}

/// How many recent green runs the class holds: what the ratchet's below-sample rule reads.
pub(crate) fn class_count(
    root: &Path,
    target: &str,
    scope: Option<&str>,
    cache: Option<&str>,
) -> usize {
    runs(root, target, scope, cache).len()
}

/// `l7r-gate measure gatecost <target> [scope] [cache] | --count <target> [scope] [cache]`; nothing printed when the log cannot answer.
pub(crate) fn cli(args: &[String], root: &Path) -> crate::Reply {
    let (count, words) = match args.first().map(String::as_str) {
        Some("--count") => (true, &args[1..]),
        _ => (false, args),
    };
    let Some(target) = words.first() else {
        return reply(String::new(), String::new(), 0);
    };
    let scope = words.get(1).map(String::as_str);
    let cache = words.get(2).map(String::as_str).filter(|c| !c.is_empty());
    let text = if count {
        format!("{}\n", class_count(root, target, scope, cache))
    } else {
        median_seconds(root, target, scope, cache).map_or_else(String::new, |m| format!("{m}\n"))
    };
    reply(text, String::new(), 0)
}

#[cfg(test)]
mod tests;
