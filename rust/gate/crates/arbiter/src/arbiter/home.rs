//! A trigger's feature, resolved once for its ask, its bundle and its ruling, and the owed files its ruling clears (feature 451 T179).
//!
//! WHY: `make arbiter-bundle` and `make arbiter-ruled` took `round:spec-fidelity|plan:specs/449-rust-codebase#T377@3` - the feature's
//! path where its directory name is the form - whose feature then read as none named, so the ruling was filed in the active feature's
//! log (451's) and its plan accept cleared 18 of 451's owed blocks (observed 2026-11-23, 449 T377's builder); and a ruled trigger's
//! entry, filed with feature "" in the mirror's `arbiter-owed.json`, stayed there after its ruling cleared only the clone's file,
//! refusing every check dispatch that read it for days (observed 2026-11-23, T177's builder). So a trigger that names a feature
//! resolves to that feature's directory or is refused, naming the form; one naming none is filed where its owed row says it was owed,
//! else in the active feature, else refused; and its ruling takes it out of the clone's owed file and the mirror's.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::checks;
use l7r_shared::checks::arbiter as core;
use l7r_shared::env::Rooted;
use serde_json::{Map, Value};

use super::re;

static FEATURE_NAME: LazyLock<Regex> = LazyLock::new(|| re(r"^\d{3}-[a-z0-9][a-z0-9-]*$"));
static TASK_FORM: LazyLock<Regex> = LazyLock::new(|| re(r"^T\d+[a-z]?$"));
static ASK_NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"^ask:(\d{3})-"));

const PLAN_ROUND: &str = "round:spec-fidelity|plan:";
const SPEC_ROUND: &str = "round:spec-fidelity|";
const PLAN_FORM: &str = "a plan review's round is `round:spec-fidelity|plan:<NNN-slug>#<Tnn>@<n>` - the feature's directory name under specs/ (`449-rust-codebase`, never `specs/449-rust-codebase`) and one of its tasks, as the review-round guard's refusal names it whole";
const SPEC_FORM: &str = "a spec review's round is `round:spec-fidelity|<NNN-slug>#<pass>@<n>` - the feature's directory name under specs/, as the review-round guard's refusal names it whole";
const ASK_FORM: &str = "an ask about one feature opens with its number, `ask:<NNN>-<slug>` (`ask:449-T377-third-round`), or names none and is the active feature's";

fn is(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// The feature directory `name` under `root/specs`, where `name` is one's directory name and it is there.
fn feature(root: &Path, name: &str) -> Option<PathBuf> {
    let d = root.join("specs").join(name);
    (is(&FEATURE_NAME, name) && d.is_dir()).then_some(d)
}

pub(super) fn name_of(d: &Path) -> String {
    d.file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
}

/// The feature directory a trigger's own words name, checked: `Ok(None)` where they name none, `Err` naming the form where they name
/// one that is not there, or a task that is not that feature's. An ask with REVIEW=plan names only tasks of its feature: its accept
/// clears their blocks.
///
/// # Errors
///
/// The trigger names a feature or a task that does not resolve.
pub(super) fn named(root: &Rooted, trigger: &str, review: &str) -> Result<Option<PathBuf>, String> {
    if let Some(rest) = trigger.strip_prefix(PLAN_ROUND) {
        let unit = rest.rsplit_once('@').map_or(rest, |(u, _)| u);
        let (name, task) = unit.split_once('#').unwrap_or((unit, ""));
        let d = feature(root, name)
            .ok_or_else(|| format!("{trigger} names no feature: {PLAN_FORM}"))?;
        if !is(&TASK_FORM, task) || !crate::plan::feature_task(&d, task) {
            return Err(format!("{trigger} names no task of {name}: {PLAN_FORM}"));
        }
        return Ok(Some(d));
    }
    if let Some(rest) = trigger.strip_prefix(SPEC_ROUND) {
        let name = rest.split(['#', '@']).next().unwrap_or("");
        return feature(root, name)
            .map(Some)
            .ok_or_else(|| format!("{trigger} names no feature: {SPEC_FORM}"));
    }
    let Some(subject) = trigger.strip_prefix("ask:") else {
        return Ok(None);
    };
    let number = ASK_NUMBER
        .captures(trigger)
        .ok()
        .flatten()
        .map(|c| c[1].to_owned());
    let d = match number {
        Some(n) => {
            let dirs = core::spec_dirs(root, &format!("{n}-"));
            if dirs.len() != 1 {
                return Err(format!(
                    "{trigger} names feature {n}, which {} directories under specs/ hold: {ASK_FORM}",
                    dirs.len()
                ));
            }
            Some(dirs[0].clone())
        }
        None => None,
    };
    if review == "plan" {
        let home = d
            .clone()
            .or_else(|| core::feature_dir_in(root, "", root.reader()));
        // read as the accept reads them, in either case ("t377" is T377)
        let stray: Vec<String> = crate::plan::task_ids(subject)
            .into_iter()
            .filter(|t| {
                !home
                    .as_deref()
                    .is_some_and(|h| crate::plan::feature_task(h, t))
            })
            .collect();
        if !stray.is_empty() {
            let of = home
                .as_deref()
                .map_or_else(|| "no feature".to_owned(), name_of);
            return Err(format!("{trigger} names {}, no task of {of}: an ask with REVIEW=plan names only its feature's tasks, whose plan blocks its accept clears - {ASK_FORM}", stray.join(", ")));
        }
    }
    Ok(d)
}

/// The feature a ruling on `trigger` is filed in, resolved once: the one its words name ([`named`]), else the one its owed row names
/// (its `feature`, else a red gate's `home`, the landing that tripped it, 461 T84), else the active one; `Err` where none resolves or its words name one that does not.
///
/// # Errors
///
/// No feature resolves, or the trigger names one that is not there.
pub(super) fn resolve(root: &Rooted, trigger: &str) -> Result<PathBuf, String> {
    let row = core::owed(root)
        .get(trigger)
        .cloned()
        .unwrap_or(Value::Null);
    let field = |k: &str| row.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
    if let Some(d) = named(root, trigger, &field("review"))? {
        return Ok(d);
    }
    // the feature its owed row says it was owed in, else the landing a red gate's row names (`home`, 461 T84: `feature` there would
    // scope which feature's gates it holds)
    for owed_in in [field("feature"), field("home")] {
        let d = root.join("specs").join(&owed_in);
        if !owed_in.is_empty() && !owed_in.contains('/') && d.is_dir() {
            return Ok(d);
        }
    }
    core::feature_dir_in(root, trigger, root.reader()).ok_or_else(|| {
        format!("no active feature (.specify/feature.json), and neither {trigger} nor its owed row names one, to record the ruling in")
    })
}

/// `{trigger: its ruling}` of feature `d`'s `arbiter.jsonl`, read as `core::rulings_in` reads the active feature's.
pub(super) fn ruled_in(d: &Path) -> Map<String, Value> {
    let text = std::fs::read_to_string(d.join("arbiter.jsonl")).unwrap_or_default();
    let mut out = Map::new();
    for line in checks::reply::py_lines(&text) {
        if let Ok(row) = serde_json::from_str::<Value>(line) {
            if let Some(t) = row.get("trigger").map(core::py_text) {
                out.insert(t, row);
            }
        }
    }
    out
}

/// The mirror a clone at `root` stands in: its path cut at `/.clones/`, as the session's mirror is derived; None outside one.
fn mirror_of(root: &Path) -> Option<PathBuf> {
    let text = root.to_string_lossy();
    text.split_once("/.clones/")
        .map(|(top, _)| PathBuf::from(top))
}

/// The trigger taken out of every owed file that holds it: the clone's, and the mirror's where its entry there is this feature's or no
/// feature's (an id such as `cascade@1` repeats across features, so another feature's entry stays). The mirror's is touched only where
/// it exists.
///
/// # Errors
///
/// A lock or an owed file that cannot be had.
pub(super) fn pop_everywhere(root: &Path, trigger: &str, feature: &str) -> Result<(), String> {
    let own = checks::common_dir(root);
    core::pop_owed(&own, trigger)?;
    let Some(theirs) = mirror_of(root).map(|m| checks::common_dir(&m)) else {
        return Ok(());
    };
    if checks::resolved(&theirs) == checks::resolved(&own) || !theirs.join(checks::OWED).is_file() {
        return Ok(());
    }
    checks::with_owed(&theirs, &mut |state| {
        let ours = state.get(trigger).is_some_and(|v| {
            let f = v.get("feature").and_then(Value::as_str).unwrap_or("");
            f.is_empty() || f == feature
        });
        ours && state
            .as_object_mut()
            .and_then(|m| m.shift_remove(trigger))
            .is_some()
    })
}
