//! Two counts recorded as inline Python one-liners, rewritten through the gate (feature 449 T248, FR-001: "to an equivalent command
//! through make, where it is inline or prose"): 374's `batch3-open-rows` and `batch4-open-rows`, and 449's `registered-guards`.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::super::events::read_text;
use super::Ran;

static HOOKS: LazyLock<Regex> = LazyLock::new(|| {
    l7r_shared::regex::build(r"([\w-]+-hooks)\.sh").unwrap_or_else(|e| unreachable!("{e}"))
});

fn load(path: &Path) -> Result<Value, String> {
    serde_json::from_str(&read_text(path)?).map_err(|e| format!("JSONDecodeError: {e}"))
}

fn is(v: &Value, key: &str, want: &str) -> bool {
    v.get(key).and_then(Value::as_str) == Some(want)
}

/// `l7r-gate measure spec 374 open-rows` (`m:batch3-open-rows`, `m:batch4-open-rows`): the rows of 328's ranking no wave took and
/// not deferred, and how many of them are E3 DRIFTED, printed as `<n> open, <m> E3 DRIFTED`.
pub(super) fn open_rows(root: &Path, out: &mut String) -> Ran {
    let ranking = load(&root.join("specs/328-match-the-research/ranking.json"))?;
    let Value::Array(rows) = ranking else {
        return Err("TypeError: the ranking holds no list".to_owned());
    };
    let open: Vec<&Value> = rows
        .iter()
        .filter(|x| l7r_shared::checks::falsy(x.get("wave")) && !is(x, "scope", "deferred"))
        .collect();
    let drifted = open
        .iter()
        .filter(|x| is(x, "tier", "E3") && is(x, "verdict", "DRIFTED"))
        .count();
    let _ = writeln!(out, "{} open, {drifted} E3 DRIFTED", open.len());
    Ok(0)
}

/// `l7r-gate measure spec 449 registered-guards` (`m:registered-guards`): the distinct `<name>-hooks.sh` guard files the hook commands
/// of `.claude/settings.json` name, over every event.
pub(super) fn registered_guards(root: &Path, out: &mut String) -> Ran {
    let settings = load(&root.join(".claude/settings.json"))?;
    let mut names = BTreeSet::new();
    let events = settings.get("hooks").and_then(Value::as_object);
    for groups in events.into_iter().flat_map(|e| e.values()) {
        for group in groups.as_array().into_iter().flatten() {
            for hook in group
                .get("hooks")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
            {
                let command = hook
                    .get("command")
                    .and_then(Value::as_str)
                    .unwrap_or_default();
                if let Ok(Some(m)) = HOOKS.captures(command) {
                    names.insert(m[1].to_owned());
                }
            }
        }
    }
    let _ = writeln!(out, "{}", names.len());
    Ok(0)
}

#[cfg(test)]
mod tests;
