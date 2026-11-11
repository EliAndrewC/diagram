//! The route and a gated push's conditions (FR-001a; what `ci/decision.py` and `ci/dispatch.py` did with the remote off). Engine code in
//! the delta is the GATED route, and it lands only on a green local `make done` of exactly the engine content the merge with main would
//! land, in a complete feature; every condition is evaluated and printed even after one fails, so a session sees the whole picture in
//! one turn.

use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;

use super::features::{self, FeatureStatus};
use super::via_make;
use crate::delta;
use crate::state::{self, State};

struct Condition {
    name: &'static str,
    passed: bool,
    why: String,
}

fn green_since_edit(st: Option<&State>, now: &str) -> Condition {
    let (passed, why) = match st {
        None => (false, "no local check recorded - run `make done` first".to_owned()),
        Some(s) if s.event != "green-local" => (false, format!("the last gate FAILED (`make {}` at {}) - run `make done` green before pushing", s.target, s.utc)),
        Some(s) if s.hash != now => (false, format!("`make {}` was green at {}, but the code changed since - that run vouched for different code; run `make done` again", s.target, s.utc)),
        Some(s) => (true, format!("`make {}` green at {} against exactly this code", s.target, s.utc)),
    };
    Condition {
        name: "green-local-since-edit",
        passed,
        why,
    }
}

/// A green local `make done` vouches for the engine content it tested, when main adds none (the GM, 2026-08-25).
fn merged_engine_green(st: Option<&State>, key: &str) -> Condition {
    let vouched = st.is_some_and(|s| {
        s.event == "green-local"
            && s.target == "done"
            && !s.engine_key.is_empty()
            && s.engine_key == key
    });
    Condition {
        name: "merged-engine-green",
        passed: vouched,
        why: if vouched {
            "a green local `make done` on exactly the engine content the merge lands".to_owned()
        } else {
            "no green local `make done` on the engine content the merge lands - merge main, then run `make done`".to_owned()
        },
    }
}

fn feature_complete(f: &FeatureStatus) -> Condition {
    Condition {
        name: "feature-complete",
        passed: f.complete(),
        why: f.why(),
    }
}

/// What the merge with main would write, or git's reason it conflicts.
fn would_be_tree(root: &Path) -> Result<String, String> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["merge-tree", "--write-tree", "origin/main", "HEAD"])
        .output();
    let (clean, out) = done.map_or((false, String::new()), |d| {
        (
            d.status.success(),
            String::from_utf8_lossy(&d.stdout).into_owned(),
        )
    });
    if clean {
        Ok(out.lines().next().unwrap_or_default().trim().to_owned())
    } else {
        Err(out.trim().to_owned())
    }
}

/// `PUSH`, or `REFUSE(<the first failing condition>)`.
fn verdict_of(conditions: &[Condition]) -> String {
    match conditions.iter().find(|c| !c.passed) {
        Some(c) => format!("REFUSE({})", c.name),
        None => "PUSH".to_owned(),
    }
}

/// The whole picture: the text, and the verdict (`PUSH`, or `REFUSE(<the first failing condition>)`).
fn picture(root: &Path, python: &str, specify: Option<&str>) -> Result<(String, String), String> {
    let delta_now = delta::compute_delta(root, "origin/main", python)?;
    let st = state::read(root)?;
    let now = state::current_hash(root, python)?;
    let active = features::active_feature(root, specify);
    let feature = features::feature_status(root, active.as_deref(), python);
    let mut text = format!(
        "delta: route {} - {}\n",
        delta_now.route(),
        delta_now.reason()
    );
    let tree = match would_be_tree(root) {
        Ok(tree) => tree,
        Err(why) => {
            let _ = writeln!(
                text,
                "the merge with origin/main CONFLICTS - merge main locally, resolve, commit:\n  {}",
                why.chars().take(400).collect::<String>()
            );
            return Ok((text, "REFUSE(merge-conflict)".to_owned()));
        }
    };
    let key = delta::engine_key(root, &tree, python)?;
    let conditions = [
        feature_complete(&feature),
        green_since_edit(st.as_ref(), &now),
        merged_engine_green(st.as_ref(), &key),
    ];
    for c in &conditions {
        let _ = writeln!(
            text,
            "  {} {}: {}",
            if c.passed { "ok " } else { "NO " },
            c.name,
            c.why
        );
    }
    let verdict = verdict_of(&conditions);
    Ok((text, verdict))
}

fn fetch(root: &Path) {
    let _ = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["fetch", "-q", "origin"])
        .output();
}

fn reply(stdout: String, stderr: String, code: i32) -> crate::Reply {
    crate::Reply {
        stdout,
        stderr,
        code,
    }
}

/// `l7r-gate ci status [--route] | gated-check`.
fn cli(args: &[String], root: &Path, python: &str, specify: Option<&str>) -> crate::Reply {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    let answer = match words.as_slice() {
        ["status", "--route"] => {
            fetch(root);
            delta::compute_delta(root, "origin/main", python)
                .map(|d| reply(format!("{}\n", d.route()), String::new(), 0))
        }
        ["status"] => {
            fetch(root);
            picture(root, python, specify).map(|(text, verdict)| {
                reply(format!("{text}verdict: {verdict}\n"), String::new(), 0)
            })
        }
        ["gated-check"] => {
            fetch(root);
            picture(root, python, specify).map(|(text, verdict)| {
                reply(
                    format!("{text}verdict: {verdict}\n"),
                    String::new(),
                    i32::from(verdict != "PUSH"),
                )
            })
        }
        _ => {
            return reply(
                String::new(),
                "usage: l7r-gate ci status [--route] | gated-check\n".to_owned(),
                2,
            )
        }
    };
    answer.unwrap_or_else(|why| reply(String::new(), format!("ci: {why}\n"), 2))
}

/// `l7r-gate ci ...`, refused outside this project's make.
fn guarded(
    args: &[String],
    root: &Path,
    procs: &dyn via_make::Procs,
    python: &str,
    specify: Option<&str>,
) -> crate::Reply {
    let tree = crate::codeid::script(root);
    let repo = tree.ancestors().nth(3).unwrap_or(root);
    if let Some(text) = via_make::refusal(procs, repo, "l7r.diagram.ci", "ci-status") {
        return reply(String::new(), text, 2);
    }
    cli(args, root, python, specify)
}

#[must_use]
pub fn entry(args: &[String], root: &Path) -> crate::Reply {
    let specify = std::env::var("SPECIFY_FEATURE").ok();
    guarded(args, root, &via_make::Live, "python3", specify.as_deref())
}

#[cfg(test)]
mod tests;
