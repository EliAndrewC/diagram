//! The gate's first phase and its tree check (feature 375, FR-004, plan D14; feature 449 T071, from `preflight.py`, `ask:449-T071-scope`).
//!
//! Measured from 372's wave 106 (2026-10-10): its gate went red about six times, every cause one a cheap check finds - a file edited mid-gate,
//! `building-programs.md` stale twice, stub pointers in found rows, two untested lines. So `make done` begins here and stops here on a failure: the
//! derived files regenerated, the record built and its pointers resolved, the quick tier run. And THE TREE HELD STILL: the gate hashes every tracked file
//! that differs from HEAD when it starts and again before it reports green, and a difference fails it, naming the file.
//!
//! Whether two versions of a `.py` file differed only where the gate does not look was `codeid.py`'s, asked in one batch, until feature 449
//! T247 deleted it with the last `.py` file: a change is unseen now on its path and bytes alone.

use std::collections::{BTreeMap, BTreeSet};
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Instant;

use serde_json::Value;

use crate::cohort::git as git_said;
use crate::Reply;

const DERIVED: [&str; 3] = ["docs", "building-programs", "glossary"];
/// Tracked files the gate itself writes, measured on a gate run (feature 375 T23): the known-failing seeds `make seeds` rewrites at rust-only.
const GATE_WRITES: [&str; 1] = ["dev/known-seeds.txt"];
/// The records the claims round writes, which no phase of the gate reads (405 T41, D15), beside the active feature's own.
const RECORDS: [&str; 4] = [
    "dev/claims-index.json",
    "dev/claims-pages.json",
    // a procedure section's kept words, beside its snapshot (451 T215)
    "dev/claims-section-words.jsonl",
    "dev/review-ledger.md",
];
const FEATURE_RECORDS: [&str; 5] = [
    "found.jsonl",
    // the notes a check listed and did not file (451 T229)
    "noted.jsonl",
    "arbiter.jsonl",
    "claims-carried.jsonl",
    "tasks.md",
];
/// The landing cohort's records: a NEW one is a run beside the gate committing its result (405 T48, D21).
const COHORT_LOG: &str = "dev/cohort-log/";

/// Each run is recorded for `make tool-yield`, as `usage_log` records a Python tool's.
const USAGE_LOG_TOOL: &str = "preflight";

/// What the phase starts.
pub struct Tools {
    pub make: String,
}

fn git(root: &Path, args: &[&str]) -> String {
    let (fine, out) = git_said(root, args);
    if fine {
        out
    } else {
        String::new()
    }
}

fn hash_paths(root: &Path, paths: &[String]) -> Option<Vec<String>> {
    let mut child = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["hash-object", "-w", "--stdin-paths"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .ok()?;
    child
        .stdin
        .take()?
        .write_all(paths.join("\n").as_bytes())
        .ok()?;
    let done = child.wait_with_output().ok()?;
    done.status.success().then(|| {
        String::from_utf8_lossy(&done.stdout)
            .split_whitespace()
            .map(str::to_owned)
            .collect()
    })
}

/// HEAD and every tracked file that differs from it, by content hash; each blob is kept, so a later check can read what the file held (405 T41, D15).
pub fn tree(root: &Path) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    out.insert(
        "HEAD".to_owned(),
        git(root, &["rev-parse", "HEAD"]).trim().to_owned(),
    );
    let listed = git(root, &["diff", "--name-only", "HEAD"]);
    let paths: Vec<String> = listed
        .lines()
        .filter(|p| !p.is_empty() && !GATE_WRITES.contains(p))
        .map(str::to_owned)
        .collect();
    if !paths.is_empty() {
        let hashes = hash_paths(root, &paths).unwrap_or_else(|| vec!["?".to_owned(); paths.len()]);
        out.extend(paths.into_iter().zip(hashes));
    }
    out
}

#[must_use]
pub fn tree_moved(
    before: &BTreeMap<String, String>,
    after: &BTreeMap<String, String>,
) -> Vec<String> {
    let keys: BTreeSet<&String> = before.keys().chain(after.keys()).collect();
    keys.into_iter()
        .filter(|k| before.get(*k) != after.get(*k))
        .cloned()
        .collect()
}

fn blob(root: &Path, spec: &str) -> Option<Vec<u8>> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["cat-file", "-p", spec])
        .output()
        .ok()?;
    done.status.success().then_some(done.stdout)
}

/// The claims round's record files of the active feature (`.specify/feature.json`).
fn active_records(root: &Path) -> BTreeSet<String> {
    let parsed: Option<Value> = std::fs::read_to_string(root.join(".specify/feature.json"))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok());
    let dir = parsed
        .as_ref()
        .and_then(|v| v["feature_directory"].as_str())
        .unwrap_or("")
        .trim_end_matches('/')
        .to_owned();
    if dir.is_empty() {
        return BTreeSet::new();
    }
    FEATURE_RECORDS
        .iter()
        .map(|n| format!("{dir}/{n}"))
        .collect()
}

/// One changed file: its path and the bytes before and after (none: absent).
type Change = (String, Option<Vec<u8>>, Option<Vec<u8>>);

/// Is a change one the gate does not see, on its path and bytes alone? (A `.py` file outside the byte-hashed areas whose semantic id and
/// statement lines were unchanged was one too, asked of `codeid.py`, until feature 449 T247 deleted it with the last `.py` file.)
fn plainly_unseen(change: &Change, active: &BTreeSet<String>) -> bool {
    let (path, old, new) = change;
    if old == new || RECORDS.contains(&path.as_str()) || active.contains(path) {
        return true;
    }
    old.is_none() && path.starts_with(COHORT_LOG) && crate::checks::has_ext(path, "json")
}

/// The paths of `changes` the gate does not see (405 T41, D15): the same bytes; one of the claims round's records.
#[must_use]
pub fn unseen(root: &Path, changes: &[Change]) -> BTreeSet<String> {
    let active = active_records(root);
    changes
        .iter()
        .filter(|c| plainly_unseen(c, &active))
        .map(|c| c.0.clone())
        .collect()
}

/// `tree_moved`, less every change the gate does not see, across a HEAD move too. "HEAD" stays when its move cannot be read.
pub fn seen_moves(
    root: &Path,
    before: &BTreeMap<String, String>,
    after: &BTreeMap<String, String>,
) -> Vec<String> {
    let moved = tree_moved(before, after);
    if moved.is_empty() {
        return moved;
    }
    let side = |m: &BTreeMap<String, String>| m.get("HEAD").cloned().unwrap_or_default();
    let (bh, ah) = (side(before), side(after));
    let mut paths: BTreeSet<String> = moved.into_iter().filter(|m| m != "HEAD").collect();
    if bh != ah {
        let (fine, diff) = git_said(root, &["diff", "--name-only", &bh, &ah]);
        if !fine {
            paths.insert("HEAD".to_owned());
            return paths.into_iter().collect();
        }
        paths.extend(diff.lines().filter(|l| !l.is_empty()).map(str::to_owned));
    }
    let version = |m: &BTreeMap<String, String>, head: &str, p: &str| {
        blob(root, m.get(p).map_or(&format!("{head}:{p}"), |s| s))
    };
    let changes: Vec<Change> = paths
        .iter()
        .map(|p| (p.clone(), version(before, &bh, p), version(after, &ah, p)))
        .collect();
    let invisible = unseen(root, &changes);
    paths
        .into_iter()
        .filter(|p| !invisible.contains(p))
        .collect()
}

/// Probe test files a diagnosis left in the tree (`tests/**/test_zz_probe*.py`): each runs in the full suite and can turn it red on its own.
#[must_use]
pub fn stray_probes(root: &Path) -> Vec<String> {
    let mut out = Vec::new();
    let mut todo = vec![root.join("tests")];
    while let Some(dir) = todo.pop() {
        for path in std::fs::read_dir(&dir)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
        {
            if path.is_dir() {
                todo.push(path);
            } else if path
                .file_name()
                .is_some_and(|n| n.to_string_lossy().starts_with("test_zz_probe"))
                && path.extension().is_some_and(|x| x == "py")
            {
                out.push(
                    path.strip_prefix(root)
                        .unwrap_or(&path)
                        .display()
                        .to_string(),
                );
            }
        }
    }
    out.sort();
    out
}

/// The flags of a run.
#[derive(Default)]
pub struct Asked {
    pub root: String,
    pub skip_quick: bool,
    pub tree_snap: String,
    pub tree_check: String,
    pub would_write: String,
    pub content: String,
    pub quiet: bool,
}

#[must_use]
pub fn parse(args: &[String]) -> Asked {
    let mut a = Asked {
        root: ".".to_owned(),
        ..Asked::default()
    };
    let mut words = args.iter();
    while let Some(word) = words.next() {
        let mut value = || words.next().cloned().unwrap_or_default();
        match word.as_str() {
            "--root" => a.root = value(),
            "--tree-snap" => a.tree_snap = value(),
            "--tree-check" => a.tree_check = value(),
            "--would-write" => a.would_write = value(),
            "--content" => a.content = value(),
            "--skip-quick" => a.skip_quick = true,
            "--quiet" => a.quiet = true,
            _ => {}
        }
    }
    a
}

fn snapshot(path: &str) -> Option<BTreeMap<String, String>> {
    serde_json::from_str(&std::fs::read_to_string(path).ok()?).ok()
}

/// The gate-write guard's question for an Edit or a Write (405 T41, D15): 0 when writing the path to those bytes is unseen by the gate.
fn would_write(root: &Path, a: &Asked) -> i32 {
    let Some(snap) = snapshot(&a.tree_check) else {
        return 1;
    };
    let rel = a.would_write.clone();
    let head = snap.get("HEAD").cloned().unwrap_or_default();
    let old = blob(root, snap.get(&rel).map_or(&format!("{head}:{rel}"), |s| s));
    let new = (!a.content.is_empty())
        .then(|| std::fs::read(&a.content).ok())
        .flatten();
    i32::from(!unseen(root, &[(rel.clone(), old, new)]).contains(&rel))
}

/// `--tree-check`: did the tree move while the gate ran?
fn tree_check(root: &Path, a: &Asked, say: &mut dyn std::io::Write) -> i32 {
    let Some(before) = snapshot(&a.tree_check) else {
        return 0;
    };
    let moved = seen_moves(root, &before, &tree(root));
    // NO ROLL CENSUS (feature 449 T222): a move the gate's own roll made was excused by the census `_census.py` wrote, read here. The
    // Python roll that wrote it is gone, and the Rust driver writes only gitignored renders (a hamlet's `.driver.svg` and `.driver.json`,
    // a sheet's picture and page), which this snapshot never holds; so every tracked move is the tree moving, with nothing to excuse.
    if moved.is_empty() {
        return 0;
    }
    if !a.quiet {
        let named: Vec<&str> = moved
            .iter()
            .map(|m| {
                if m == "HEAD" {
                    "HEAD (a commit or a checkout)"
                } else {
                    m.as_str()
                }
            })
            .collect();
        let _ = writeln!(say, "GATE NOT GREEN: the tree moved while the gate ran - it vouches for none of it (feature 375 FR-004):\n  {}", named.join("\n  "));
    }
    1
}

/// Run a step, its output shown only on a failure (the last 3,000 characters of each stream).
fn step(cmd: &mut Command, say: &mut dyn std::io::Write) -> bool {
    let Ok(done) = cmd.output() else { return false };
    if !done.status.success() {
        for stream in [&done.stdout, &done.stderr] {
            let text = String::from_utf8_lossy(stream);
            let tail = text.char_indices().rev().nth(2999).map_or(0, |(i, _)| i);
            let _ = say.write_all(text[tail..].as_bytes());
        }
    }
    done.status.success()
}

fn make(tools: &Tools, root: &Path, words: &[&str]) -> Command {
    let mut c = Command::new(&tools.make);
    c.arg("--no-print-directory").args(words).current_dir(root);
    c
}

fn status_lines(root: &Path) -> BTreeSet<String> {
    git(root, &["status", "--porcelain"])
        .lines()
        .map(str::to_owned)
        .collect()
}

/// The regenerated derived files, the record and its pointers. False when one failed.
fn cheap_steps(root: &Path, tools: &Tools, say: &mut dyn std::io::Write) -> (bool, Option<f64>) {
    let start = Instant::now();
    let before = status_lines(root);
    for target in DERIVED {
        if !step(&mut make(tools, root, &[target]), say) {
            let _ = writeln!(
                say,
                "preflight: `make {target}` failed - the gate stops here (feature 375 FR-004)"
            );
            return (false, None);
        }
    }
    let derived = start.elapsed().as_secs_f64();
    let moved: Vec<String> = status_lines(root)
        .difference(&before)
        .filter_map(|m| m.get(3..).map(|p| p.trim_end().to_owned()))
        .filter(|p| !p.trim().is_empty())
        .collect();
    if !moved.is_empty() {
        let _ = writeln!(
            say,
            "preflight: regenerated, commit them with the change:\n  {}",
            moved.join("\n  ")
        );
    }
    let mut pointers = Command::new(root.join("scripts/gates/l7r-gate.sh"));
    pointers
        .args(["check", "research-pointers"])
        .arg(root)
        .current_dir(root);
    let mut record = make(tools, root, &["record", "CHECK=1"]);
    for (cmd, what) in [
        (&mut record, "the record does not build"),
        (&mut pointers, "a research pointer does not resolve"),
    ] {
        if !step(cmd, say) {
            let _ = writeln!(
                say,
                "preflight: {what} - the gate stops here (feature 375 FR-004)"
            );
            return (false, None);
        }
    }
    (true, Some(derived))
}

/// The phase itself.
fn phase(root: &Path, tools: &Tools, a: &Asked, say: &mut dyn std::io::Write) -> i32 {
    let probes = stray_probes(root);
    if !probes.is_empty() {
        let _ = writeln!(say, "preflight: probe test files are left in the tree - delete them; the gate stops here (feature 385):\n  {}", probes.join("\n  "));
        return 1;
    }
    let start = Instant::now();
    let (fine, derived) = cheap_steps(root, tools, say);
    let Some(derived) = derived.filter(|_| fine) else {
        return 1;
    };
    let pointers_done = start.elapsed().as_secs_f64();
    if !a.skip_quick {
        let quick = make(tools, root, &["quick", "FROM_PREFLIGHT=1"]).status();
        if !quick.is_ok_and(|s| s.success()) {
            let _ = writeln!(
                say,
                "preflight: `make quick` failed - the gate stops here (feature 375 FR-004)"
            );
            return 1;
        }
    }
    let quick_done = start.elapsed().as_secs_f64();
    let steps = format!(
        "derived {derived:.0} s, record and pointers {:.0} s, quick {:.0} s",
        pointers_done - derived,
        quick_done - pointers_done
    );
    let _ = writeln!(say, "preflight: {steps}");
    let _ = writeln!(
        say,
        "preflight: clean in {:.0} s",
        start.elapsed().as_secs_f64()
    );
    0
}

/// One run; its exit.
pub fn run(a: &Asked, tools: &Tools, say: &mut dyn std::io::Write) -> i32 {
    let root = std::fs::canonicalize(&a.root).unwrap_or_else(|_| PathBuf::from(&a.root));
    let code = if !a.would_write.is_empty() && !a.tree_check.is_empty() {
        would_write(&root, a)
    } else if !a.tree_snap.is_empty() {
        let text = serde_json::to_string(&tree(&root)).unwrap_or_default();
        i32::from(std::fs::write(&a.tree_snap, text).is_err())
    } else if !a.tree_check.is_empty() {
        tree_check(&root, a, say)
    } else {
        phase(&root, tools, a, say)
    };
    crate::stamp::record_for(
        &root,
        USAGE_LOG_TOOL,
        if code == 0 { "passed" } else { "refused" },
    );
    code
}

/// `l7r-gate preflight ...`; the output is live, a phase taking minutes.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let tools = Tools {
        make: "make".to_owned(),
    };
    let code = run(&parse(args), &tools, &mut std::io::stdout());
    Reply {
        stdout: String::new(),
        stderr: String::new(),
        code,
    }
}

#[cfg(test)]
mod tests;
