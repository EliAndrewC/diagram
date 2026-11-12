//! `l7r-gate speckit-todo` - every spec-kit feature not yet closed, by state (feature 330; ported from `scripts/speckit-todo.py` by
//! feature 449 T118, `ask:449-T83-scope`).
//!
//! The GM, 2026-10-08: *"we then need some way to mechanically easily see what spec kit features are open"* - once the old future-work
//! directory was retired, open work lives in `specs/` only, and this is how anyone finds it. The state rule, the tags and what holds a
//! landing are the guard's `shared::speckit`, the one copy the guards and the gate's crates call in process; this is the command line
//! over it, the report and the push's `--check`.
//!
//! ```text
//! speckit-todo [--root <repo>] [--all]            --all adds the closed features and why each is closed
//! speckit-todo [--root <repo>] --affects T,U      only the features carrying any of those tags, same layout
//! speckit-todo [--root <repo>] --by-affects       the open features grouped by tag (a feature under each of its tags)
//! speckit-todo [--root <repo>] --check            exit 1, with the line to add, when an open feature's tags are missing or unknown
//! speckit-todo --state <specs/NNN-slug>           one feature's state
//! speckit-todo --closed-by-status <dir>           `yes` when the spec's status line closes it, else `no`
//! speckit-todo --holding <dir>                    the open boxes that hold the landing, one a line (none: it may land)
//! speckit-todo [--root <repo>] --each-state <dir>...  each directory's state, one a line; one that cannot be read is an
//!                                                 `error: <why>` line and the exit is 1
//! ```
//!
//! `--each-state` is new with the port (feature 449 T118): the Python callers that imported the module by path
//! (`close_check.py`, `plan_hold.py`, `research_claims.py`, `tick-task.py`) ask it instead, one process for every directory where the
//! import read each in process. Each directory's state reads the vocabulary two levels above it, as `feature(d)` did, so a broken
//! `.specify/affects.json` fails that directory as the import raised there; with `--root`, the root's vocabulary is read once
//! instead, as `feature(d, vocab)` was handed one (`research_claims.py`), and a broken one fails the run with nothing printed. A run
//! with any failure exits 1, its reasons on stderr, so a caller that let the import's raise through fails, and one that caught
//! it per directory (`research_claims.py`) reads the other lines. It records no run in the usage log, as the import recorded none;
//! every other form records the run in the working directory's repository as `usage_log.exited` did (`passed`, or `refused` on a
//! non-zero exit). Argparse's own usage text is not kept (`ask:449-usage-text`); its exit 2 is.

mod report;
mod work_budget_view;

use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;

use l7r_gate_core::record::args::{parse, Spec};
use l7r_guard::shared::speckit::{
    affects, closed_by_status, features, holding, py_path, state, state_given_vocabulary,
    vocabulary, Feature, Vocabulary, STAGES,
};

use crate::Reply;

/// The name the usage log records a run under (feature 406 T01).
const USAGE_LOG_TOOL: &str = "speckit-todo";

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// The reply the Python's uncaught raise gave: exit 1, what it had printed, and its message after a `Traceback` line.
fn raised(why: &str) -> Reply {
    reply(
        String::new(),
        format!("Traceback (most recent call last):\n  l7r-gate speckit-todo\n{why}\n"),
        1,
    )
}

/// The run recorded in the working directory's repository (`usage_log.exited`, its `root` None).
fn record(cwd: &Path, code: i32) {
    let common = Command::new("git")
        .arg("-C")
        .arg(cwd)
        .args(["rev-parse", "--path-format=absolute", "--git-common-dir"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default();
    if !common.is_empty() {
        let outcome = if code == 0 { "passed" } else { "refused" };
        l7r_guard::shared::checks::passes::usage(
            Path::new(&common),
            USAGE_LOG_TOOL,
            "check",
            outcome,
        );
    }
}

/// The command line: what `speckit-todo.py`'s `main` answered, its run recorded in `cwd`'s repository where the Python recorded one.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let specs = [
        Spec::value("--root"),
        Spec::flag("--all"),
        Spec::flag("--check"),
        Spec::value("--affects"),
        Spec::flag("--by-affects"),
        Spec::value("--state"),
        Spec::value("--closed-by-status"),
        Spec::value("--holding"),
        Spec::list("--each-state"),
    ];
    let p = match parse(args, &specs) {
        Ok(p) => p,
        Err(why) => {
            return reply(
                String::new(),
                format!("usage: l7r-gate speckit-todo [--root ROOT] [--all] [--check] [--affects TAGS] [--by-affects] [--state DIR] [--closed-by-status DIR] [--holding DIR] [--each-state DIR ...]\nl7r-gate speckit-todo: error: {why}\n"),
                2,
            )
        }
    };
    let dirs = p.list("--each-state");
    if !dirs.is_empty() {
        return each_state(dirs, p.has("--root").then(|| p.text("--root", ".")));
    }
    let done = answer(
        p.text("--root", "."),
        &Flags {
            all: p.on("--all"),
            check: p.on("--check"),
            by_affects: p.on("--by-affects"),
            affects: p.text("--affects", ""),
            state: p.text("--state", ""),
            closed_by_status: p.text("--closed-by-status", ""),
            holding: p.text("--holding", ""),
        },
    );
    match done {
        Ok(r) => {
            record(cwd, r.code);
            r
        }
        Err(why) => raised(&why),
    }
}

/// `--each-state`: each directory's state, or an `error:` line where its reading failed, exit 1 when one did; with `root`, that
/// root's vocabulary read once (a broken one fails the run, nothing printed) and none above each directory.
fn each_state(dirs: &[String], root: Option<&str>) -> Reply {
    if let Some(root) = root {
        if let Err(why) = vocabulary(&py_path(root)) {
            return raised(&why);
        }
    }
    let (mut out, mut err) = (String::new(), String::new());
    for d in dirs {
        let d = py_path(d);
        let said = if root.is_some() {
            state_given_vocabulary(&d)
        } else {
            state(&d)
        };
        match said {
            Ok(s) => out += &(s + "\n"),
            Err(why) => {
                let _ = writeln!(out, "error: {why}");
                let _ = writeln!(err, "speckit-todo: {}: {why}", d.display());
            }
        }
    }
    let code = i32::from(!err.is_empty());
    reply(out, err, code)
}

/// The flags `main` reads; an empty value is an unset one, as the Python's `if args.holding:` read it.
struct Flags<'a> {
    all: bool,
    check: bool,
    by_affects: bool,
    affects: &'a str,
    state: &'a str,
    closed_by_status: &'a str,
    holding: &'a str,
}

/// `main`, in its order: the holding boxes, the status line, the check, one state, the tag filter, the report.
fn answer(root: &str, f: &Flags) -> Result<Reply, String> {
    if !f.holding.is_empty() {
        let out: String = holding(&py_path(f.holding))?
            .into_iter()
            .map(|l| l + "\n")
            .collect();
        return Ok(reply(out, String::new(), 0));
    }
    if !f.closed_by_status.is_empty() {
        let yes = closed_by_status(&py_path(f.closed_by_status))?;
        return Ok(reply(
            format!("{}\n", if yes { "yes" } else { "no" }),
            String::new(),
            0,
        ));
    }
    let root = py_path(root);
    if f.check {
        let vocab = vocabulary(&root)?;
        let specs = root.join("specs");
        let listed = features(&specs)?;
        let msg = check_message(&untagged(&root, &listed), &vocab)
            + &placeholder_message(&off_placeholder(&vocab, &listed), &vocab)?;
        let code = i32::from(!msg.is_empty());
        return Ok(reply(String::new(), msg, code));
    }
    if !f.state.is_empty() {
        // `state` reads the vocabulary above the directory first, as the Python's `feature(d)` did, and fails where it raised
        return Ok(reply(
            format!("{}\n", state(&py_path(f.state))?),
            String::new(),
            0,
        ));
    }
    let mut only = Vec::new();
    if !f.affects.is_empty() {
        let vocab = vocabulary(&root)?;
        let (known, unknown) = affects(&format!("**Affects**: {}", f.affects), &vocab);
        if !unknown.is_empty() || known.is_empty() {
            let named = if unknown.is_empty() {
                f.affects.to_owned()
            } else {
                unknown.join(", ")
            };
            return Ok(reply(
                String::new(),
                format!(
                    "speckit-todo: AFFECTS names no tag it knows: {named}\nTags: {}.\n",
                    known_tags(&vocab)
                ),
                2,
            ));
        }
        only = known;
    }
    let out = report::report(&root, f.all, f.by_affects, &only)?;
    Ok(reply(out, String::new(), 0))
}

/// The tags and aliases a line may name, comma-separated.
fn known_tags(vocab: &Vocabulary) -> String {
    vocab
        .stage
        .iter()
        .map(|(t, _)| t.as_str())
        .chain(vocab.aliases.iter().map(|(a, _)| a.as_str()))
        .collect::<Vec<_>>()
        .join(", ")
}

/// The open features that name no known tag, or an unknown one - none in a repository with no vocabulary.
fn untagged<'a>(root: &Path, listed: &'a [Feature]) -> Vec<&'a Feature> {
    if !root.join(l7r_guard::shared::speckit::AFFECTS).is_file() {
        return Vec::new();
    }
    listed
        .iter()
        .filter(|f| f.state != "closed" && (f.affects.is_empty() || !f.unknown.is_empty()))
        .collect()
}

fn problem(f: &Feature) -> String {
    if f.no_spec {
        "no spec.md - write one first".to_owned()
    } else if !f.unknown.is_empty() {
        format!("unknown: {}", f.unknown.join(", "))
    } else {
        "no **Affects** line".to_owned()
    }
}

/// The refusal, with the line to add and the tags it may name - empty when nothing is missing.
fn check_message(missing: &[&Feature], vocab: &Vocabulary) -> String {
    if missing.is_empty() {
        return String::new();
    }
    let names: Vec<String> = missing
        .iter()
        .map(|f| format!("  specs/{}/spec.md  ({})", f.name, problem(f)))
        .collect();
    format!(
        "speckit-todo: {} open feature(s) do not say what they affect:\n{}\n\
         Add this line under the **Status** line, naming every tag it touches, comma-separated:\n  **Affects**: hamlet, magistracy\n\
         Tags: {}.\n\
         A new tag is one entry in .specify/affects.json. The stage is derived - the earliest among the tags, a tier not\n\
         yet scripted counting its code too; a thing two tiers need is owed at the earlier one (the GM, 2026-10-10).\n",
        missing.len(),
        names.join("\n"),
        known_tags(vocab)
    )
}

/// The open features owed at a tier not yet scripted that are not that tier's placeholder (the GM, 2026-10-10: *"all of the things
/// that are owed when we implement villages should be consolidated into a single spec kit feature"*, and the same for each later tier).
fn off_placeholder<'a>(vocab: &Vocabulary, listed: &'a [Feature]) -> Vec<&'a Feature> {
    listed
        .iter()
        .filter(|f| {
            f.state != "closed"
                && STAGES[1..].contains(&f.owed.as_str())
                && vocab.placeholder(&f.owed).and_then(|v| v.as_str()) != Some(f.name.as_str())
        })
        .collect()
}

/// The refusal, naming each feature's placeholder - empty when every later-tier item is in its placeholder.
fn placeholder_message(off: &[&Feature], vocab: &Vocabulary) -> Result<String, String> {
    if off.is_empty() {
        return Ok(String::new());
    }
    let mut lines = Vec::new();
    for f in off {
        let home = vocab.placeholder(&f.owed).filter(|v| truthy(v));
        lines.push(match home {
            Some(home) => {
                let home = home
                    .as_str()
                    .ok_or_else(|| format!("AttributeError: the placeholder of {} is not a name", f.owed))?;
                format!(
                    "  specs/{}/  (owed at {}): carry its text into specs/{home}/spec.md under '## Carried items' and close it '**Status**: Superseded by {} (<date>): carried word for word ...'",
                    f.name,
                    f.owed,
                    home.split('-').next().unwrap_or_default()
                )
            }
            None => format!(
                "  specs/{}/  (owed at {}, which has no placeholder yet): make it the {} tier's placeholder - add \"{}\": \"{}\" under \"placeholders\" in .specify/affects.json",
                f.name, f.owed, f.owed, f.owed, f.name
            ),
        });
    }
    Ok(format!(
        "speckit-todo: {} feature(s) owed at a tier not yet scripted sit outside that tier's placeholder:\n{}\n\
         (the GM, 2026-10-10: everything owed when a tier is scripted is one feature, not exhaustive; tag it with a\n\
         scripted kind too - hamlet, magistracy - if it is owed now.)\n",
        off.len(),
        lines.join("\n")
    ))
}

/// Python's truth of a JSON value.
fn truthy(v: &serde_json::Value) -> bool {
    use serde_json::Value;
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64().is_some_and(|f| f != 0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}

#[cfg(test)]
mod tests;
