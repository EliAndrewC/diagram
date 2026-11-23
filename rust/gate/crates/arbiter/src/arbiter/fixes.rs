//! A tooling fix's record: what is open, the settling of one, and the nit an accepted round's words ask for (from `hm_arbiter.py`, split from `arbiter.rs` at the file-scale bar).

use std::path::{Path, PathBuf};

use l7r_shared::checks;
use l7r_shared::checks::arbiter as core;
use l7r_shared::env::Rooted;
use serde_json::{json, Map, Value};

use super::{
    accept_answers, append_jsonl, gm_question, py_repr, py_str, text, utc_now, Stop, HOUR_TRIGGER,
};

// `open_fixes` and `fix_hold` moved to `reviews::closing` (feature 449 T127): the closing check reads them in process, and `reviews`
// cannot build on this crate; `arbiter.rs` re-exports them.
use l7r_gate_reviews::reviews::closing::{landing, open_fixes};

/// `make arbiter-fix-done ... LANDING=<task> FILES="<the fix's files>" [F=<feature>]` (feature 451 T182): the fix lands with that task.
pub(super) struct Landing {
    pub task: String,
    pub feature: String,
    pub files: Vec<String>,
}

pub(super) fn fix_home(root: &Rooted, trigger: &str) -> Option<PathBuf> {
    let active = core::feature_dir_in(root, "", root.reader());
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

/// A test that proves a fix: a file under `tests/`, or a Rust crate's own tests under `rust/` - a `tests.rs` or a file in a `tests/`
/// directory. WHY the second: feature 449 moved the tooling into Rust crates, each tested from its own `src/`, and deleted the Python
/// tests (FR-001b), so the round arbiter's fix to `rust/gate/crates/claims/src/claims/ports.rs` had no `tests/` file to name
/// (ask:449-T184-elongated-retired-2, observed 2026-11-18).
fn is_test_file(root: &Path, test: &str) -> bool {
    if test.is_empty() {
        return false;
    }
    let t = checks::resolved(&root.join(test));
    if !t.is_file() {
        return false;
    }
    let tests = checks::resolved(&root.join("tests"));
    let rust = checks::resolved(&root.join("rust"));
    let rust_test = t.ancestors().skip(1).any(|p| p == rust)
        && (t.file_name().is_some_and(|n| n == "tests.rs")
            || t.ancestors()
                .skip(1)
                .any(|p| p.file_name().is_some_and(|n| n == "tests")));
    t.ancestors().skip(1).any(|p| p == tests) || rust_test
}

/// `hm_arbiter.settle_fix`: close an open tooling fix in the feature that holds it; a declined one becomes a question for the GM; one
/// that lands with its task ([`Landing`]) is left pending for that landing ([`pend_fix`]).
pub(super) fn settle_fix(
    root: &Rooted,
    trigger: &str,
    status: &str,
    note: &str,
    test: &str,
    landing: Option<&Landing>,
) -> Result<Value, Stop> {
    let home = fix_home(root, trigger).or_else(|| core::feature_dir_in(root, "", root.reader()));
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
    if status == "done" && !is_test_file(root, test) {
        return Err(Stop::Refused(format!(
            "TEST={} is not a file under tests/ or a Rust crate's tests - a fix is done with the test that proves it",
            if test.is_empty() { "<none>" } else { test }
        )));
    }
    if let Some(l) = landing {
        return pend_fix(root, &d, trigger, (status, note, test), l);
    }
    if status == "done" {
        // ENGINE=1, which settled a fix committed here before it landed, gave way to LANDING= (451 T182): its done row was on main
        // before its code, and the task's landing was still refused until then
        if !on_main(root, test) {
            return Err(Stop::Refused(format!("{test} is not on main as it is here - land and settle it in one command: the same make arbiter-fix-done with LAND=\"<the fix's files>\" (it runs make land-tooling on them first); a fix in rust/, which land-tooling refuses, lands with its task: commit it and its test, then the same command with LANDING=<the task> FILES=\"<the fix's files>\" in place of LAND=")));
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
        gm_question(&d, &format!("Build this tooling fix the round arbiter asked for, which the session declined? The fix: {fix} Declined because: {note}"), trigger, &when)?;
    }
    Ok(value)
}

/// The open task `task` of the feature `named` (its directory name or number; the fix's `home` when empty), or why not.
fn landing_feature(root: &Path, named: &str, home: &Path, task: &str) -> Result<PathBuf, Stop> {
    let d = if named.is_empty() {
        home.to_path_buf()
    } else if root.join("specs").join(named).is_dir() {
        root.join("specs").join(named)
    } else {
        let dirs = core::spec_dirs(root, &format!("{named}-"));
        match dirs.as_slice() {
            [one] => one.clone(),
            _ => {
                return Err(Stop::Refused(format!(
                "no feature {named} under specs/ - F= names the feature whose task lands the fix"
            )))
            }
        }
    };
    let open = std::fs::read_to_string(d.join("tasks.md"))
        .unwrap_or_default()
        .lines()
        .any(|l| {
            l.trim_start()
                .strip_prefix("- [ ] ")
                .is_some_and(|r| r.split_whitespace().next() == Some(task))
        });
    if !open {
        return Err(Stop::Refused(format!(
            "{task} is no open task of {} - LANDING= names the task whose make land carries the fix",
            d.file_name().unwrap_or_default().to_string_lossy()
        )));
    }
    Ok(d)
}

/// A fix that lands with its task (feature 451 T182): its files and test committed here as they stand, its task open, it is kept
/// pending in the clone ([`landing::add`]) - no done row yet: `make land` of that task writes it into its own tick commit.
fn pend_fix(
    root: &Rooted,
    home: &Path,
    trigger: &str,
    (status, note, test): (&str, &str, &str),
    l: &Landing,
) -> Result<Value, Stop> {
    if status != "done" {
        return Err(Stop::Refused(
            "LANDING= settles a fix that is done - a declined fix is a question for the GM, never a landing".to_owned(),
        ));
    }
    if l.files.is_empty() {
        return Err(Stop::Refused("FILES= names the fix's files - LANDING= settles a fix whose files and test its task's landing carries".to_owned()));
    }
    if let Some(p) = l
        .files
        .iter()
        .map(String::as_str)
        .chain([test])
        .find(|p| !committed_here(root, p))
    {
        return Err(Stop::Refused(format!("{p} is not committed as it stands - commit the fix and its test first, then the same make arbiter-fix-done")));
    }
    let d = landing_feature(root, &l.feature, home, &l.task)?;
    let entry = json!({
        "trigger": trigger,
        "feature": super::home::name_of(&d),
        "task": l.task,
        "home": super::home::name_of(home),
        "note": note,
        "test": test,
        "files": l.files,
        "utc": utc_now(),
    });
    landing::add(root, entry.clone()).map_err(Stop::Refused)?;
    Ok(entry)
}

/// `hm_arbiter.nit_answers`: the wording an `accept` ruling asked to fix in passing, made, answers the accepted unit again.
pub(super) fn nit_answers(
    root: &Rooted,
    trigger: &str,
    old: &str,
    new: &str,
) -> Result<Vec<String>, Stop> {
    let ruled = core::rulings_in(root, "", root.reader());
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
    accept_answers(
        root,
        &format!("{check}|{subject}"),
        &format!(
            "the wording the round arbiter's accept asked for ({trigger}): {} -> {}",
            py_repr(old),
            py_repr(new)
        ),
    )
}
