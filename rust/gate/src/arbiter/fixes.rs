//! A tooling fix's record: what is open, the settling of one, and the nit an accepted round's words ask for (from `hm_arbiter.py`, split from `arbiter.rs` at the file-scale bar).

use std::path::{Path, PathBuf};

use l7r_guard::shared::checks;
use l7r_guard::shared::checks::arbiter as core;
use serde_json::{json, Map, Value};

use super::{
    accept_answers, append_jsonl, gm_question, py_repr, py_str, text, utc_now, Stop, HOUR_TRIGGER,
};

/// `(trigger, tooling_fix)` of every open arbiter tooling fix in feature `d` (`hm_arbiter.open_fixes`).
#[must_use]
pub fn open_fixes(d: &Path) -> Vec<(String, String)> {
    let mut fixes: Vec<(String, String)> = Vec::new();
    for line in std::fs::read_to_string(d.join("arbiter.jsonl"))
        .unwrap_or_default()
        .lines()
    {
        let Ok(r) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        if text(&r, "fix") == "open" && !checks::falsy(r.get("tooling_fix")) {
            let t = py_str(r.get("trigger"));
            let fix = py_str(r.get("tooling_fix"));
            match fixes.iter_mut().find(|(k, _)| *k == t) {
                Some(slot) => slot.1 = fix,
                None => fixes.push((t, fix)),
            }
        } else if matches!(text(&r, "status"), "done" | "declined") {
            let of = py_str(r.get("fix_of"));
            fixes.retain(|(k, _)| *k != of);
        }
    }
    fixes
}

/// Why feature `d` may not move on while an arbiter tooling fix is open, or "".
#[must_use]
pub fn fix_hold(d: &Path) -> String {
    let fixes = open_fixes(d);
    if fixes.is_empty() {
        return String::new();
    }
    let listed = fixes
        .iter()
        .map(|(t, fix)| format!("    {t}: {fix}"))
        .collect::<Vec<_>>()
        .join("\n");
    format!(
        "the round arbiter's tooling fix is open - make it, with its test, in this feature before going on (feature 379):\n{listed}\n  made:     make arbiter-fix-done ID=\"<trigger>\" NOTE=\"<what was built>\" TEST=<its test under tests/> LAND=\"<the fix's files>\" F=<feature> TICK=<the task> (lands them, settles the fix, ticks the task)\n  overhaul: make arbiter-fix-declined ID=\"<trigger>\" REASON=\"<why it overhauls a process>\" (a question for the GM, owed escalation-check)"
    )
}

pub(super) fn fix_home(root: &Path, trigger: &str) -> Option<PathBuf> {
    let active = core::feature_dir(root, "");
    let named = HOUR_TRIGGER
        .captures(trigger)
        .ok()
        .flatten()
        .map(|c| root.join("specs").join(&c[1]));
    let all = core::spec_dirs(root, "");
    [active, named]
        .into_iter()
        .flatten()
        .chain(all)
        .find(|d| d.is_dir() && open_fixes(d).iter().any(|(t, _)| t == trigger))
}

fn git_output(root: &Path, args: &[&str]) -> Option<String> {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .ok()?;
    done.status
        .success()
        .then(|| String::from_utf8_lossy(&done.stdout).trim().to_owned())
}

/// `hm_arbiter.committed_here`: committed at HEAD exactly as it stands in the tree.
fn committed_here(root: &Path, path: &str) -> bool {
    git_output(
        root,
        &["rev-parse", "-q", "--verify", &format!("HEAD:{path}")],
    )
    .is_some()
        && git_output(root, &["status", "--porcelain", "--", path])
            .is_some_and(|out| out.is_empty())
}

/// `hm_arbiter.on_main`: on main (after a fetch) with the same content as at the clone's HEAD.
fn on_main(root: &Path, path: &str) -> bool {
    let _ = git_output(root, &["fetch", "-q", "origin"]);
    let here = git_output(
        root,
        &["rev-parse", "-q", "--verify", &format!("HEAD:{path}")],
    );
    here.is_some_and(|h| {
        !h.is_empty()
            && git_output(
                root,
                &[
                    "rev-parse",
                    "-q",
                    "--verify",
                    &format!("origin/main:{path}"),
                ],
            )
            .is_some_and(|m| m == h)
    })
}

fn is_test_file(root: &Path, test: &str) -> bool {
    if test.is_empty() {
        return false;
    }
    let tests = checks::resolved(&root.join("tests"));
    let t = checks::resolved(&root.join(test));
    t.is_file() && t.ancestors().skip(1).any(|p| p == tests)
}

/// `hm_arbiter.settle_fix`: close an open tooling fix in the feature that holds it; a declined one becomes a question for the GM.
pub(super) fn settle_fix(
    root: &Path,
    trigger: &str,
    status: &str,
    note: &str,
    test: &str,
) -> Result<Value, Stop> {
    let home = fix_home(root, trigger).or_else(|| core::feature_dir(root, ""));
    let d =
        home.ok_or_else(|| Stop::Refused("no active feature (.specify/feature.json)".to_owned()))?;
    let name = d
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    let fix = open_fixes(&d)
        .into_iter()
        .find(|(t, _)| t == trigger)
        .map(|(_, f)| f)
        .ok_or_else(|| {
            Stop::Refused(format!(
                "{trigger} has no open tooling fix in {name} - `make tick` names the open ones"
            ))
        })?;
    if note.split_whitespace().count() < 2 || note.chars().count() < 8 {
        return Err(Stop::Refused(
            "the NOTE (or REASON) needs two words and eight characters - it is what the GM reads"
                .to_owned(),
        ));
    }
    let mut note = note.to_owned();
    if status == "done" {
        if !is_test_file(root, test) {
            return Err(Stop::Refused(format!(
                "TEST={} is not a file under tests/ - a fix is done with the test that proves it",
                if test.is_empty() { "<none>" } else { test }
            )));
        }
        if !on_main(root, test) {
            let engine = std::env::var("ARBITER_FIX_ENGINE").is_ok_and(|v| !v.is_empty());
            if !(engine && committed_here(root, test)) {
                return Err(Stop::Refused(format!("{test} is not on main as it is here - land and settle it in one command: the same make arbiter-fix-done with LAND=\"<the fix's files>\" (it runs make land-tooling on them first) (an ENGINE fix, which land-tooling refuses, lands with its feature: commit it and its test, then the same command with ENGINE=1)")));
            }
            note.push_str(" (an engine fix: it lands with the feature)");
        }
    } else if status != "declined" {
        return Err(Stop::Refused("status is done or declined".to_owned()));
    }
    let when = utc_now();
    let mut row = Map::new();
    row.insert("fix_of".to_owned(), json!(trigger));
    row.insert("status".to_owned(), json!(status));
    row.insert("note".to_owned(), json!(note));
    if status == "done" {
        row.insert("test".to_owned(), json!(test));
    }
    row.insert("utc".to_owned(), json!(when));
    let value = Value::Object(row);
    append_jsonl(&d.join("arbiter.jsonl"), &value)?;
    if status == "declined" {
        gm_question(root, &d, &format!("Build this tooling fix the round arbiter asked for, which the session declined? The fix: {fix} Declined because: {note}"), trigger, &when);
    }
    Ok(value)
}

/// `hm_arbiter.nit_answers`: the wording an `accept` ruling asked to fix in passing, made, answers the accepted unit again.
pub(super) fn nit_answers(
    root: &Path,
    trigger: &str,
    old: &str,
    new: &str,
) -> Result<Vec<String>, Stop> {
    let ruled = core::rulings(root, "");
    let r = ruled
        .get(trigger)
        .filter(|r| text(r, "ruling") == "accept" && text(r, "kind") == "round");
    let Some(r) = r else {
        return Err(Stop::Refused(format!(
            "{trigger} has no `accept` ruling on a round - a nit is made only under one"
        )));
    };
    let what = py_str(r.get("what"));
    if old.trim().is_empty() || new.trim().is_empty() || !what.contains(old) || !what.contains(new)
    {
        let shown: String = what.chars().take(300).collect();
        return Err(Stop::Refused(format!(
            "the ruling's `what` must quote both OLD and NEW - it reads: {shown}"
        )));
    }
    let unit = text(r, "unit");
    let (check, subject) = unit.split_once('|').unwrap_or((unit, ""));
    let own = subject
        .strip_prefix("modal:")
        .map(|name| root.join(format!("l7r/diagram/interactive/assets/modals/{name}.md")));
    let body = own
        .as_deref()
        .and_then(|p| std::fs::read_to_string(p).ok())
        .unwrap_or_default();
    if !body.contains(new) || body.contains(old) {
        let named = own
            .as_deref()
            .map_or_else(|| subject.to_owned(), |p| p.to_string_lossy().into_owned());
        return Err(Stop::Refused(format!("{named} must hold NEW and no longer OLD - make the edit first (a page's nit is not this target's)")));
    }
    Ok(accept_answers(
        root,
        &format!("{check}|{subject}"),
        &format!(
            "the wording the round arbiter's accept asked for ({trigger}): {} -> {}",
            py_repr(old),
            py_repr(new)
        ),
    ))
}
