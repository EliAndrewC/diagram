//! `DEFER_FORM_OK="<reason>"`, the deferral form's escape (feature 451 T17, D15): taken by `make decide` and `make plan-delta`, read
//! from the environment and recorded by the tool itself, as `PLAN_REVIEW_OK` is (T28's precedent: no `$(LOGESCAPE)` line, which would
//! record it twice). A section decided under it is not refused when its block later changes: `make plan-delta` reads the guard log's
//! escape records naming the feature and the task, and only for a block with a deferral finding, since the log is read whole.

use std::collections::BTreeSet;
use std::path::Path;

use l7r_shared::escape;
use serde_json::Value;

use super::{bypass_record, guard_log};

/// A variable of the environment the command reads (`std::env::var` in the binary, a closure in the tests).
pub(super) type Env<'a> = &'a dyn Fn(&str) -> Option<String>;

/// The guard log's rule for the escape, which [`decided_under`] reads back.
const RULE: &str = "defer-form-ok";

/// `DEFER_FORM_OK`'s reason when one is given, or the refusal of a value with no reason (two words and eight characters).
pub(super) fn taken(env: Env<'_>, verb: &str) -> Result<Option<String>, String> {
    let Some(why) = env("DEFER_FORM_OK").filter(|w| !w.trim().is_empty()) else {
        return Ok(None);
    };
    let why = why.trim().to_owned();
    if escape::enough(&why) {
        return Ok(Some(why));
    }
    guard_log("blocked", &why, "DEFER_FORM_OK-no-reason");
    Err(format!("{verb}: DEFER_FORM_OK needs a REASON, not just a value - two words and eight characters: why this section's found-and-left items keep their form (feature 451 T17)\n"))
}

/// The escape recorded in the guard log, naming the feature and `what` (a task, or `plan-delta`), and in `dev/bypass-log/`.
pub(super) fn record(root: &Path, dir: &Path, what: &str, why: &str) {
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    guard_log("escaped", &format!("{name} {what}: {why}"), RULE);
    bypass_record(root, &format!("decide-defer {name} {what}"), why);
}

/// The tasks of `dir`'s feature decided under the escape, from the guard log: each entry of the plan gate's rule whose detail names
/// the feature. A file is parsed only when its text holds the rule.
pub(super) fn decided_under(dir: &Path) -> BTreeSet<String> {
    let lead = format!("{} ", dir.file_name().unwrap_or_default().to_string_lossy());
    let mut out = BTreeSet::new();
    let entries = std::fs::read_dir(l7r_shared::log::dir())
        .into_iter()
        .flatten()
        .flatten();
    for entry in entries {
        let text = std::fs::read_to_string(entry.path()).unwrap_or_default();
        if !text.contains(RULE) {
            continue;
        }
        let v: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
        let field = |k: &str| v[k].as_str().unwrap_or("").to_owned();
        if field("guard") != "plan-gate" || field("event") != "escaped" || field("rule") != RULE {
            continue;
        }
        if let Some((task, _)) = field("detail")
            .strip_prefix(&lead)
            .and_then(|rest| rest.split_once(": "))
        {
            out.insert(task.to_owned());
        }
    }
    out
}

#[cfg(test)]
mod tests;
