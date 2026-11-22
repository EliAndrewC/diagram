//! The research claims' tools (feature 316; `scripts/record/claims.py` and its satellites, `tunables.py`, `pager.py` and
//! `l7r/diagram/tools/claims_rust.py`, with the grammar, the section reader and `doc_units` of `l7r/diagram/tools/claims.py`, ported by
//! feature 449 T82 under `ask:449-T82-claims`): `l7r-gate claims <command>` behind `make claims-*`, `l7r-gate tunables` behind
//! `make tunables`, and `l7r-gate impl-check` behind `make impl-check` and the closing check (`impl_check.py`'s port, feature 449 T132, which
//! took `l7r-gate claims-door` with its last caller). The units are the Rust's and the procedure sections ([`scope`]): the `.py` half,
//! read through `scripts/bundle_door.py`, left with the engine's Python (feature 449 T158).

use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};

use crate::record::args::{parse, Spec};
use crate::Reply;

mod bundle;
mod carry;
mod commands;
mod context;
mod counters;
mod flight;
mod grammar;
pub mod impl_check;
mod index;
mod labels;
mod pager;
mod ports;
mod reads;
mod reply;
mod report;
pub mod scope;
mod seam;
mod stale;
mod triage;
mod tunables;
mod units;

/// Every path the claims tools read at a tree: the base read's (the engine, the procedures, the questions) and the records (the push
/// gate's test holds each judged).
#[must_use]
pub fn read_paths() -> Vec<&'static str> {
    let mut out = report::BASE_PATHS.to_vec();
    out.extend([
        index::INDEX,
        index::DEFERRED,
        index::STORE,
        index::QUESTIONS,
        ports::PORTS,
    ]);
    out
}

/// What the round arbiter's bundle reads of the claims at `root` (`arbiter_bundle.claims_section`): each claim's backing and line by key, and the index.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn rows_and_index(
    root: &Path,
) -> Result<(serde_json::Value, serde_json::Value), crate::record::repo::Fail> {
    let cur = index::current(root, &root.join(index::QUESTIONS))?;
    let rows: serde_json::Map<String, serde_json::Value> = cur
        .iter()
        .map(|r| {
            (
                r.key.clone(),
                serde_json::json!({"backing": r.claim.backing, "line": r.claim.line}),
            )
        })
        .collect();
    let index = index::load_map(&root.join(index::INDEX))?;
    Ok((
        serde_json::Value::Object(rows),
        serde_json::Value::Object(index),
    ))
}

/// The open findings a Rust stage's landing answers for, and the rest in the files it changes (feature 444 FR-021): `make land`'s
/// question, in process since feature 449 T121 (`ask:449-T83-scope`), where `land.py` asked the door.
///
/// `_root` and `_seam` (the Python modules the stage's seam imports) are read no more since feature 449 T158 deleted the engine's
/// Python, kept for the land's call.
///
/// # Errors
///
/// None since T158; the result is kept for the land's call, made while the seam's Python reads could fail.
pub fn scope_split(
    _root: &Path,
    report: &str,
    changed: &[String],
    _seam: &[String],
) -> Result<(Vec<String>, Vec<String>), crate::record::repo::Fail> {
    Ok(seam::split(report, changed))
}

/// The claims bundles in flight now (`claims_flight.live`).
///
/// # Errors
///
/// Where a flight mark cannot be read.
pub fn flight_live(root: &Path) -> Result<Vec<String>, crate::record::repo::Fail> {
    flight::live(root, flight::now())
}

/// A temporary directory no other run of this process or another takes, removed when it is dropped - on a `?` and a panic too
/// (feature 449 T101): `tempfile.TemporaryDirectory`'s.
pub fn temp_dir(tag: &str) -> l7r_shared::tempdir::TempDir {
    l7r_shared::tempdir::TempDir::new(&format!("claims-{tag}"))
}

/// `git -C dir args...` fed `input`; its stdout, or None where it failed.
#[must_use]
pub fn stdin_git(dir: &Path, args: &[&str], input: &str) -> Option<String> {
    let mut child = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::null())
        .spawn()
        .ok()?;
    if let Some(mut pipe) = child.stdin.take() {
        let _ = pipe.write_all(input.as_bytes());
    }
    let done = child.wait_with_output().ok()?;
    done.status
        .success()
        .then(|| String::from_utf8_lossy(&done.stdout).into_owned())
}

fn usage(what: &str, why: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{what}: {why}\n"),
        code: 2,
    }
}

/// The subcommands and the flags each takes, as `claims_cli._parser` declares them; the required ones.
fn specs(cmd: &str) -> Option<(Vec<Spec>, &'static [&'static str])> {
    let v = Spec::value;
    Some(match cmd {
        "owed" | "triage-owed" | "backfill" | "backfill-sections" | "rekey" | "refingerprint"
        | "gate" | "known" => (Vec::new(), &[]),
        "bundle" => (
            vec![
                Spec::flag("--owed"),
                v("--module"),
                v("--units"),
                v("--out"),
                v("--reason"),
                v("--with"),
                v("--pages"),
            ],
            &[],
        ),
        "record" | "triaged" => (vec![v("--bundle"), v("--reply")], &["--bundle", "--reply"]),
        "triage" => (vec![v("--out")], &[]),
        "report" => (vec![Spec::flag("--all")], &[]),
        "carry" => (
            vec![v("--feature"), v("--task"), v("--keys"), v("--ruling")],
            &["--feature"],
        ),
        "accept" => (vec![v("--keys"), v("--trigger")], &["--keys", "--trigger"]),
        "coverage" => (vec![v("--path"), Spec::flag("--rust")], &[]),
        _ => return None,
    })
}

/// The top level's `--root`, and the subcommand with its own arguments.
fn split_top(args: &[String]) -> Result<(String, &str, &[String]), String> {
    let mut root = ".".to_owned();
    let mut i = 0;
    while i < args.len() {
        let a = &args[i];
        if let Some(value) = a.strip_prefix("--root=") {
            value.clone_into(&mut root);
            i += 1;
        } else if a.len() > 2 && "--root".starts_with(a.as_str()) {
            match args.get(i + 1) {
                Some(value) if !value.starts_with('-') => root.clone_from(value),
                _ => return Err("argument --root: expected one argument".to_owned()),
            }
            i += 2;
        } else if a.starts_with('-') {
            return Err(format!("unrecognized arguments: {a}"));
        } else {
            return Ok((root, a, &args[i + 1..]));
        }
    }
    Err("the following arguments are required: cmd".to_owned())
}

/// The repository `--root` names: its top level, or `--root` as given outside one.
fn toplevel(root: &str) -> PathBuf {
    let top = crate::record::repo::git(Path::new(root), &["rev-parse", "--show-toplevel"]);
    let top = if top.is_empty() { root.to_owned() } else { top };
    PathBuf::from(l7r_shared::py_text::strip(&top))
}

/// THE PATTERNS COMPILED SIDE BY SIDE, ONCE A PROCESS (feature 449 T167): the crate's 48 patterns and core's took 25 ms to compile one
/// after another, the longest 3-5 ms (observed 2026-11-17, method: each compiled in the crate's test build), and a command compiled the ones it
/// read as it reached them, 15 ms of its first run; here each is compiled on a thread of its own while the command asks git for the
/// tree, a pattern the command reaches first waiting on its thread as it would on its own compiling. A test of a command took over
/// FR-008's tenth of a second with it.
static WARM: std::sync::LazyLock<()> = std::sync::LazyLock::new(|| {
    for set in [
        &bundle::WARM[..],
        &carry::WARM[..],
        &context::WARM[..],
        &counters::WARM[..],
        &grammar::WARM[..],
        &impl_check::WARM[..],
        &index::WARM[..],
        &labels::WARM[..],
        &reply::WARM[..],
        &report::WARM[..],
        &seam::WARM[..],
        &stale::WARM[..],
        &triage::WARM[..],
        &tunables::WARM[..],
        &units::WARM[..],
    ] {
        for pattern in set {
            let pattern: &'static std::sync::LazyLock<fancy_regex::Regex> = pattern;
            std::thread::spawn(move || std::sync::LazyLock::force(pattern));
        }
    }
});

/// `l7r-gate claims [--root DIR] <command> [...]`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    std::sync::LazyLock::force(&WARM);
    let (root, cmd, rest) = match split_top(args) {
        Ok(t) => t,
        Err(why) => return usage("l7r-gate claims", &why),
    };
    let Some((specs, required)) = specs(cmd) else {
        return usage(
            "l7r-gate claims",
            &format!("argument cmd: invalid choice: '{cmd}'"),
        );
    };
    let parsed = match parse(rest, &specs) {
        Ok(p) => p,
        Err(why) => return usage(&format!("l7r-gate claims {cmd}"), &why),
    };
    let missing: Vec<&str> = required
        .iter()
        .copied()
        .filter(|r| !parsed.has(r))
        .collect();
    if !missing.is_empty() {
        return usage(
            &format!("l7r-gate claims {cmd}"),
            &format!(
                "the following arguments are required: {}",
                missing.join(", ")
            ),
        );
    }
    let root = toplevel(&root);
    let mut out = commands::Out::default();
    let code = match commands::run(cmd, &parsed, &root, &mut out) {
        Ok(code) => code,
        Err(why) => {
            let _ = write!(
                out.err,
                "Traceback (most recent call last):\n  l7r-gate claims {cmd}\n{why}\n"
            );
            1
        }
    };
    Reply {
        stdout: out.out,
        stderr: out.err,
        code,
    }
}

/// `l7r-gate tunables [--root DIR] [--path P] [--all] [--count] [--inline]`.
#[must_use]
pub fn tunables_cli(args: &[String]) -> Reply {
    let specs = [
        Spec::value("--root"),
        Spec::value("--path"),
        Spec::flag("--all"),
        Spec::flag("--count"),
        Spec::flag("--inline"),
    ];
    let p = match parse(args, &specs) {
        Ok(p) => p,
        Err(why) => return usage("l7r-gate tunables", &why),
    };
    let root = flight::resolved(Path::new(p.text("--root", ".")));
    let path = p.text("--path", "");
    let said = index::current(&root, &root.join(index::QUESTIONS)).and_then(|cur| {
        if p.on("--inline") {
            tunables::inline(&root, &cur, path)
                .map(|found| tunables::render_inline(&found, p.on("--count")))
        } else {
            Ok(tunables::render(
                &tunables::tunables(&cur, path, !p.on("--all")),
                p.on("--count"),
            ))
        }
    });
    match said {
        Ok(text) => Reply {
            stdout: text + "\n",
            stderr: String::new(),
            code: 0,
        },
        Err(why) => Reply {
            stdout: String::new(),
            stderr: format!("Traceback (most recent call last):\n  l7r-gate tunables\n{why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
