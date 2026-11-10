//! The gate's first phase and its tree check (feature 375, FR-004, plan D14; feature 449 T071, from `preflight.py`, `ask:449-T071-scope`).
//!
//! Measured from 372's wave 106 (2026-10-10): its gate went red about six times, every cause one a cheap check finds - a file edited mid-gate,
//! `building-programs.md` stale twice, stub pointers in found rows, two untested lines. So `make done` begins here and stops here on a failure: the
//! derived files regenerated, the record built and its pointers resolved, the quick tier run. And THE TREE HELD STILL: the gate hashes every tracked file
//! that differs from HEAD when it starts and again before it reports green, and a difference fails it, naming the file.
//!
//! What reads Python or pytest stays behind one door until phase 4: `scripts/gates/preflight.py`, asked for the changed lines' coverage (only by
//! `make preflight`) and, in one batch, whether two versions of a `.py` file differ only where the gate does not look.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Instant;

use serde_json::{Map, Value};

use crate::cohort::git as git_said;
use crate::measure::text_err;
use crate::Reply;

const DERIVED: [&str; 3] = ["docs", "building-programs", "glossary"];
/// Tracked files the gate itself writes, measured on a gate run (feature 375 T23): the known-failing seeds `make seeds` rewrites at rust-only.
const GATE_WRITES: [&str; 1] = ["dev/known-seeds.txt"];
/// The records the claims round writes, which no phase of the gate reads (405 T41, D15), beside the active feature's own.
const RECORDS: [&str; 3] = [
    "dev/claims-index.json",
    "dev/claims-pages.json",
    "dev/review-ledger.md",
];
const FEATURE_RECORDS: [&str; 4] = [
    "found.jsonl",
    "arbiter.jsonl",
    "claims-carried.jsonl",
    "tasks.md",
];
/// The landing cohort's records: a NEW one is a run beside the gate committing its result (405 T48, D21).
const COHORT_LOG: &str = "dev/cohort-log/";
/// What a pool map's roll writes beside its generator (feature 385 T87, plan D108).
const MAP_OUTPUTS: [&str; 5] = [".json", ".png", ".svg", ".html", ".webp"];

/// Each run is recorded for `make tool-yield`, as `usage_log` records a Python tool's.
const USAGE_LOG_TOOL: &str = "preflight";

/// What the phase starts.
pub(crate) struct Tools {
    pub make: String,
    pub python: String,
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
pub(crate) fn tree(root: &Path) -> BTreeMap<String, String> {
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

pub(crate) fn tree_moved(
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

/// Which of `changes` are in a byte-hashed area, asked of the stamp as one batch (FR-006).
fn raw_areas(root: &Path, changes: &[&Change]) -> BTreeSet<String> {
    let listed: String = changes.iter().flat_map(|c| [c.0.as_str(), "\n"]).collect();
    crate::stamp::raw_matches(root, &mut listed.as_bytes())
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

/// The door's batch answer: for each change, are its two versions the same but for what the gate does not see?
fn same_python(root: &Path, tools: &Tools, changes: &[&Change]) -> BTreeSet<String> {
    let dir = std::env::temp_dir().join(format!("l7r-preflight-{}", std::process::id()));
    let _ = std::fs::create_dir_all(&dir);
    let mut lines = String::new();
    for (i, (path, old, new)) in changes.iter().enumerate() {
        let (a, b) = (dir.join(format!("{i}.old")), dir.join(format!("{i}.new")));
        let _ = std::fs::write(&a, old.as_deref().unwrap_or_default());
        let _ = std::fs::write(&b, new.as_deref().unwrap_or_default());
        let _ = writeln!(lines, "{path}\t{}\t{}", a.display(), b.display());
    }
    let asked = door(root, tools, &["--same-py"], &lines);
    let _ = std::fs::remove_dir_all(&dir);
    let same = asked.map_or_else(
        |_| Vec::new(),
        |out| out.lines().map(|l| l == "1").collect::<Vec<bool>>(),
    );
    changes
        .iter()
        .zip(same)
        .filter(|(_, s)| *s)
        .map(|(c, _)| c.0.clone())
        .collect()
}

/// The Python door, its stdout; an error when it failed.
fn door(root: &Path, tools: &Tools, args: &[&str], input: &str) -> Result<String, String> {
    let mut child = Command::new(&tools.python)
        .arg(root.join("scripts/gates/preflight.py"))
        .args(args)
        .arg("--root")
        .arg(root)
        .env("PYTHONDONTWRITEBYTECODE", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(text_err)?;
    if let Some(mut pipe) = child.stdin.take() {
        let _ = pipe.write_all(input.as_bytes());
    }
    let done = child.wait_with_output().map_err(text_err)?;
    if done.status.success() {
        Ok(String::from_utf8_lossy(&done.stdout).into_owned())
    } else {
        Err(String::from_utf8_lossy(&done.stderr).into_owned())
    }
}

/// Is a change one the gate does not see, on its path and bytes alone? `None` when only its `.py` source can say.
fn plainly_unseen(change: &Change, active: &BTreeSet<String>) -> Option<bool> {
    let (path, old, new) = change;
    if old == new || RECORDS.contains(&path.as_str()) || active.contains(path) {
        return Some(true);
    }
    if old.is_none() && path.starts_with(COHORT_LOG) && crate::checks::has_ext(path, "json") {
        return Some(true);
    }
    if !crate::checks::has_ext(path, "py") || old.is_none() || new.is_none() {
        return Some(false);
    }
    None
}

/// The paths of `changes` the gate does not see (405 T41, D15): the same bytes; one of the claims round's records; or a `.py` file outside the byte-hashed
/// areas whose semantic id and statement lines are unchanged. The Python is started at most once, and only when such a file changed.
pub(crate) fn unseen(root: &Path, tools: &Tools, changes: &[Change]) -> BTreeSet<String> {
    let active = active_records(root);
    let mut out = BTreeSet::new();
    let mut undecided = Vec::new();
    for change in changes {
        match plainly_unseen(change, &active) {
            Some(true) => {
                out.insert(change.0.clone());
            }
            Some(false) => {}
            None => undecided.push(change),
        }
    }
    if undecided.is_empty() {
        return out;
    }
    let raw = raw_areas(root, &undecided);
    undecided.retain(|c| !raw.contains(&c.0));
    if !undecided.is_empty() {
        out.extend(same_python(root, tools, &undecided));
    }
    out
}

/// `tree_moved`, less every change the gate does not see, across a HEAD move too. "HEAD" stays when its move cannot be read.
pub(crate) fn seen_moves(
    root: &Path,
    tools: &Tools,
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
    let invisible = unseen(root, tools, &changes);
    paths
        .into_iter()
        .filter(|p| !invisible.contains(p))
        .collect()
}

/// The map outputs of every pool map the gate's own run rolled, by its roll census (feature 385 T87, plan D108).
pub(crate) fn rolled_outputs(root: &Path, census: &Path) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    let top = root;
    for line in std::fs::read_to_string(census).unwrap_or_default().lines() {
        let Ok(record) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        let generator = PathBuf::from(record["gen"].as_str().unwrap_or(""));
        let name = generator
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        let Some(stem) = name
            .strip_suffix(".gen.py")
            .filter(|_| record["kind"] == "roll")
        else {
            continue;
        };
        let parent = generator.parent().unwrap_or(&generator);
        let dir = std::fs::canonicalize(parent).unwrap_or_else(|_| parent.to_owned());
        let Ok(rel) = dir.strip_prefix(top) else {
            continue;
        };
        out.extend(
            MAP_OUTPUTS
                .iter()
                .map(|ext| format!("{}/{stem}{ext}", rel.display())),
        );
    }
    out
}

/// Probe test files a diagnosis left in the tree (`tests/**/test_zz_probe*.py`): each runs in the full suite and can turn it red on its own.
pub(crate) fn stray_probes(root: &Path) -> Vec<String> {
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
pub(crate) struct Asked {
    pub root: String,
    pub skip_quick: bool,
    pub workers: String,
    pub tree_snap: String,
    pub tree_check: String,
    pub census: String,
    pub would_write: String,
    pub content: String,
    pub quiet: bool,
    pub no_coverage: bool,
}

pub(crate) fn parse(args: &[String]) -> Asked {
    let mut a = Asked {
        root: ".".to_owned(),
        workers: std::env::var("XDIST_WORKERS").unwrap_or_else(|_| "4".to_owned()),
        ..Asked::default()
    };
    let mut words = args.iter();
    while let Some(word) = words.next() {
        let mut value = || words.next().cloned().unwrap_or_default();
        match word.as_str() {
            "--root" => a.root = value(),
            "--workers" => a.workers = value(),
            "--tree-snap" => a.tree_snap = value(),
            "--tree-check" => a.tree_check = value(),
            "--census" => a.census = value(),
            "--would-write" => a.would_write = value(),
            "--content" => a.content = value(),
            "--skip-quick" => a.skip_quick = true,
            "--quiet" => a.quiet = true,
            "--no-coverage" => a.no_coverage = true,
            _ => {}
        }
    }
    a
}

fn snapshot(path: &str) -> Option<BTreeMap<String, String>> {
    serde_json::from_str(&std::fs::read_to_string(path).ok()?).ok()
}

/// The gate-write guard's question for an Edit or a Write (405 T41, D15): 0 when writing the path to those bytes is unseen by the gate.
fn would_write(root: &Path, tools: &Tools, a: &Asked) -> i32 {
    let Some(snap) = snapshot(&a.tree_check) else {
        return 1;
    };
    let rel = a.would_write.clone();
    let head = snap.get("HEAD").cloned().unwrap_or_default();
    let old = blob(root, snap.get(&rel).map_or(&format!("{head}:{rel}"), |s| s));
    let new = (!a.content.is_empty())
        .then(|| std::fs::read(&a.content).ok())
        .flatten();
    i32::from(!unseen(root, tools, &[(rel.clone(), old, new)]).contains(&rel))
}

/// `--tree-check`: did the tree move while the gate ran?
fn tree_check(root: &Path, tools: &Tools, a: &Asked, say: &mut dyn std::io::Write) -> i32 {
    let Some(before) = snapshot(&a.tree_check) else {
        return 0;
    };
    let moved = seen_moves(root, tools, &before, &tree(root));
    let census = if a.census.is_empty() {
        root.join(".git/roll-census.jsonl")
    } else {
        PathBuf::from(&a.census)
    };
    let rolled = rolled_outputs(root, &census);
    let (rerolled, moved): (Vec<String>, Vec<String>) =
        moved.into_iter().partition(|m| rolled.contains(m));
    if !rerolled.is_empty() {
        let _ = writeln!(
            say,
            "preflight: re-rolled by the gate - commit them (feature 385 T87):\n  {}",
            rerolled.join("\n  ")
        );
    }
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

/// The door's two lists of uncovered lines, `{file: [lines]}`.
type Gaps = BTreeMap<String, Vec<i64>>;

fn twelve(lines: &[i64]) -> String {
    let shown: Vec<String> = lines.iter().take(12).map(i64::to_string).collect();
    format!("[{}]", shown.join(", "))
}

fn gaps_of(v: &Value) -> Gaps {
    v.as_object().map_or_else(Gaps::new, Map::iter_gaps)
}

/// A JSON object of integer lists, read.
trait IterGaps {
    fn iter_gaps(&self) -> Gaps;
}

impl IterGaps for Map<String, Value> {
    fn iter_gaps(&self) -> Gaps {
        self.iter()
            .map(|(k, v)| {
                (
                    k.clone(),
                    v.as_array()
                        .map_or_else(Vec::new, |a| a.iter().filter_map(Value::as_i64).collect()),
                )
            })
            .collect()
    }
}

/// The verdict on the door's coverage answer: its report and the exit.
pub(crate) fn judge_coverage(
    mut off: Gaps,
    on: &Gaps,
    exempt: &BTreeSet<String>,
    say: &mut dyn std::io::Write,
) -> i32 {
    let slated: Gaps = exempt.iter().filter_map(|f| off.remove_entry(f)).collect();
    for (file, lines) in &slated {
        let _ = writeln!(say, "preflight: {file} lines {} - unrun, and slated for the Rust port (dev/coverage-exempt.json): information, not refused", twelve(lines));
    }
    for (file, lines) in on {
        let _ = writeln!(say, "preflight: {file} lines {} - no quick test runs them; a rolled map or a test the quick tier skips may (the gate's floor judges)", twelve(lines));
    }
    if off.is_empty() {
        return 0;
    }
    for (file, lines) in &off {
        let _ = writeln!(say, "preflight: {file} lines {} - in a changed function, run by no quick test, and reached by no roll (off the hamlet path, or only unit tests reached it at the last green gate): only a unit test covers them", twelve(lines));
    }
    let _ = writeln!(say, "preflight: the gate stops here - the 100% floor would refuse these minutes from now (feature 375 FR-004)");
    1
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
    // THE COVERAGE STEP IS make preflight's, NOT THE GATE'S (405 T47, D25): 98-107 s of every gate, and it refused about twice, once wrongly
    let (mut off, mut on) = (Gaps::new(), Gaps::new());
    if !a.no_coverage {
        match door(root, tools, &["--cover", "--workers", &a.workers], "") {
            Ok(text) => {
                let got: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
                (off, on) = (gaps_of(&got["off"]), gaps_of(&got["on"]));
            }
            Err(why) => {
                let _ = writeln!(say, "preflight: the coverage step failed:\n{why}");
                return 1;
            }
        }
    }
    let mut steps = format!(
        "derived {derived:.0} s, record and pointers {:.0} s, quick {:.0} s",
        pointers_done - derived,
        quick_done - pointers_done
    );
    if !a.no_coverage {
        let _ = write!(
            steps,
            ", coverage of the changed lines {:.0} s",
            start.elapsed().as_secs_f64() - quick_done
        );
    }
    let _ = writeln!(say, "preflight: {steps}");
    let exempt: BTreeSet<String> = crate::exempt::paths(root)
        .unwrap_or_default()
        .into_iter()
        .collect();
    if judge_coverage(off, &on, &exempt, say) != 0 {
        return 1;
    }
    let _ = writeln!(
        say,
        "preflight: clean in {:.0} s",
        start.elapsed().as_secs_f64()
    );
    0
}

/// One run; its exit.
pub(crate) fn run(a: &Asked, tools: &Tools, say: &mut dyn std::io::Write) -> i32 {
    let root = std::fs::canonicalize(&a.root).unwrap_or_else(|_| PathBuf::from(&a.root));
    let code = if !a.would_write.is_empty() && !a.tree_check.is_empty() {
        would_write(&root, tools, a)
    } else if !a.tree_snap.is_empty() {
        let text = serde_json::to_string(&tree(&root)).unwrap_or_default();
        i32::from(std::fs::write(&a.tree_snap, text).is_err())
    } else if !a.tree_check.is_empty() {
        tree_check(&root, tools, a, say)
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
pub(crate) fn cli(args: &[String]) -> Reply {
    let tools = Tools {
        make: "make".to_owned(),
        python: "python3".to_owned(),
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
