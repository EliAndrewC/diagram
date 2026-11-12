//! The push's checks (feature 383, 430; feature 449 T067, from `push_checks.py` and `push_gates.py`): what each push gate judges, so a push
//! whose delta holds none of it skips the gate (a push of records alone took 10.9 s, observed 2026-10-26, method: the push timed gate by
//! gate), and the push's own checks in order, the first refusal printing the shell's line and ending the run. The rows still in Python
//! run as their own processes until their tasks port them (`ask:449-T067-scope`); a passing self-test is kept per version of `scripts/`, and a
//! Rust one per gate binary too (T109).

use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use l7r_guard::shared::log::{write as log_write, Entry};
use l7r_guard::shared::sha256;
use serde_json::{json, Value};

use crate::plan::{git_line, pretty};
use crate::Reply;

/// Each run of a gate's skip is recorded for `make tool-yield`, as `usage_log` records a Python tool's.
const USAGE_LOG_TOOL: &str = "push_gates";

/// What each gate judges, read off the gate's own constants and pinned by `test_push_gates.py`.
#[must_use]
pub fn judges(gate: &str) -> Option<(&'static [&'static str], &'static str)> {
    match gate {
        "claims" => Some((
            &[
                "l7r/",
                "docs/buildings.md",
                "docs/buildings/",
                "research/questions/",
                "dev/claims-index.json",
                "dev/claims-deferred.json",
                "dev/claims-pages.json",
                "specs/",
            ],
            "engine code, Mode A procedure, cited page, claims record or task row",
        )),
        "entry" => Some((
            &["research/", "l7r/diagram/interactive/"],
            "research record or pop-up",
        )),
        "cohort" => Some((
            &[
                "l7r/",
                "pool/",
                "legacy-hand-authored-pool/",
                "dev/cohort-log/",
            ],
            "engine code",
        )),
        _ => None,
    }
}

fn split(text: &str) -> impl Iterator<Item = String> + '_ {
    text.split_whitespace().map(str::to_owned)
}

/// (the merge base, every path the delta holds, the uncommitted ones), or None with no merge base to read a delta from.
fn delta(root: &Path) -> Option<(String, Vec<String>, Vec<String>)> {
    let base = git_line(root, &["merge-base", "HEAD", "origin/main"]);
    if base.is_empty() {
        return None;
    }
    let mut dirty: Vec<String> = split(&git_line(root, &["diff", "--name-only", "HEAD"])).collect();
    dirty.extend(split(&git_line(
        root,
        &["ls-files", "--others", "--exclude-standard"],
    )));
    let mut paths: Vec<String> = split(&git_line(root, &["diff", "--name-only", &base, "HEAD"]))
        .chain(dirty.iter().cloned())
        .collect();
    paths.sort();
    paths.dedup();
    Some((base, paths, dirty))
}

/// The paths of `paths` under one of `prefixes`.
#[must_use]
pub fn judged(prefixes: &[&str], paths: &[String]) -> Vec<String> {
    paths
        .iter()
        .filter(|p| {
            prefixes.iter().any(|x| {
                if x.ends_with('/') {
                    p.starts_with(x)
                } else {
                    p == x
                }
            })
        })
        .cloned()
        .collect()
}

fn store_key(root: &Path, gate: &str, base: &str, paths: &[String]) -> String {
    let scripts = git_line(root, &["rev-parse", "HEAD:scripts"]);
    let mut args = vec!["ls-tree", "-r", "HEAD", "--"];
    args.extend(paths.iter().map(String::as_str));
    let tree = git_line(root, &args);
    // git's listing ends in a newline that `git_line` trims: the key stays the Python's, so a pass stored before the switch holds.
    let end = if tree.is_empty() { "" } else { "\n" };
    sha256::hex(format!("{gate}\n{base}\n{scripts}\n{tree}{end}").as_bytes())
}

fn store(root: &Path) -> PathBuf {
    let common = git_line(root, &["rev-parse", "--git-common-dir"]);
    root.join(common).join("push-gates")
}

/// Why the gate need not run, or "".
fn skip(root: &Path, gate: &str, prefixes: &[&str], what: &str) -> String {
    let Some((base, paths, dirty)) = delta(root) else {
        return String::new();
    };
    let mine = judged(prefixes, &paths);
    if mine.is_empty() {
        return format!(
            "{gate}-gate: nothing to judge - the delta holds no {what} (feature 430 T04)"
        );
    }
    if !mine.iter().any(|p| dirty.contains(p))
        && store(root)
            .join(gate)
            .join(store_key(root, gate, &base, &mine))
            .is_file()
    {
        return format!("{gate}-gate: passed already on this delta's content ({} path(s) it judges, unchanged) (feature 430 T04)", mine.len());
    }
    String::new()
}

fn record_pass(root: &Path, gate: &str, prefixes: &[&str]) {
    let Some((base, paths, dirty)) = delta(root) else {
        return;
    };
    let mine = judged(prefixes, &paths);
    if !mine.is_empty() && !mine.iter().any(|p| dirty.contains(p)) {
        let dir = store(root).join(gate);
        let _ = std::fs::create_dir_all(&dir);
        let _ = std::fs::write(dir.join(store_key(root, gate, &base, &mine)), "pass\n");
    }
}

/// `l7r-gate push-gate skip|pass <gate>`.
pub fn gate_cli(args: &[String], root: &Path) -> Reply {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    let usage = || {
        Reply { stdout: String::new(), stderr: "push-gate skip <gate>    exit 0, saying why, when the delta holds nothing the gate judges or a pass is stored for it\npush-gate pass <gate>    store the gate's pass for the delta as it stands\n".to_owned(), code: 2 }
    };
    let [verb, gate] = words.as_slice() else {
        return usage();
    };
    let Some((prefixes, what)) = judges(gate) else {
        return usage();
    };
    let reply = match *verb {
        "pass" => {
            record_pass(root, gate, prefixes);
            Reply {
                stdout: String::new(),
                stderr: String::new(),
                code: 0,
            }
        }
        "skip" => {
            let why = skip(root, gate, prefixes, what);
            if why.is_empty() {
                Reply {
                    stdout: String::new(),
                    stderr: String::new(),
                    code: 1,
                }
            } else {
                Reply {
                    stdout: why + "\n",
                    stderr: String::new(),
                    code: 0,
                }
            }
        }
        _ => return usage(),
    };
    crate::stamp::record_for(
        root,
        USAGE_LOG_TOOL,
        if reply.code == 0 { "passed" } else { "refused" },
    );
    reply
}

/// What runs a row.
#[derive(Clone, Copy)]
enum Tool {
    /// `l7r-gate <args>`.
    Gate,
    /// A Python script under `scripts/`, until its task ports it.
    Py(&'static str),
}

/// A row of the push: its name, what runs it, its arguments (`{root}` is the clone), the refusal, is it a self-test, what it needs.
struct Row(
    &'static str,
    Tool,
    &'static [&'static str],
    &'static str,
    bool,
    &'static str,
);

const CHECKS: [Row; 23] = [
    Row("file-scale selftest", Tool::Gate, &["check", "file-scale", "--selftest"], "check-file-scale selftest failed - the guard itself is broken; fix rust/gate/crates/checks/src/checks/ before pushing", true, ""),
    Row("file-scale", Tool::Gate, &["check", "file-scale", "{root}"], "a Rust file is past the ~1,000-line bar (above) - constitution Principle X clause 13, gated since feature 173", false, ""),
    Row("make-docs", Tool::Py("make-docs.py"), &["{root}", "--check"], "docs/make-targets.html is stale against the Makefile (above) - run `make docs` and commit the page; feature 385 FR-017", false, "docs/make-targets.html"),
    Row("ledger-owed", Tool::Py("reviews/ledger_owed.py"), &["--ledger", "{root}/dev/review-ledger.md", "--refuse"], "a check's pass has no row in dev/review-ledger.md (above) - write each from its reply: make ledger-owed WRITE=\"<where you recorded what you did>\" (or add the row printed, its ?s filled); features 371, 385 FR-019", false, ""),
    Row("entry-headings selftest", Tool::Py("gates/check-entry-headings.py"), &["--selftest"], "check-entry-headings selftest failed - the guard itself is broken; fix scripts/gates/check-entry-headings.py before pushing", true, "delta:entry-headings"),
    Row("entry-headings", Tool::Py("gates/check-entry-headings.py"), &["{root}"], "a class entry names a research heading that no longer resolves (above) - a rename owes its inbound links, feature 234", false, "delta:entry-headings"),
    Row("research-pointers selftest", Tool::Gate, &["check", "research-pointers", "--selftest"], "check-research-pointers selftest failed - the guard itself is broken; fix rust/gate/crates/checks/src/checks/ before pushing", true, ""),
    Row("research-pointers", Tool::Gate, &["check", "research-pointers", "{root}"], "a pointer to the research does not resolve, or names a built page (above) - feature 301; `make fragment-move` moves a fragment with its pointers", false, ""),
    Row("partial-citations", Tool::Gate, &["check", "partial-citations", "{root}"], "a footnote cites a source no one can wholly read with no confirmed passage (above) - feature 312 FR-020; confirm the passage (quote-check) and record it in research/partial-confirmations.jsonl, or make the note an absence note", false, "delta:partial-citations"),
    Row("downloads selftest", Tool::Gate, &["record", "downloads", "selftest"], "the download-list check's selftest failed - the guard itself is broken; fix rust/gate/crates/downloads/src/record/downloads/check.rs before pushing", true, ""),
    Row("downloads", Tool::Gate, &["record", "downloads", "check"], "the canonical download list is not append-only against main (above) - feature 313; `make download-add FILE=<draft.md>` appends an entry", false, ""),
    Row("spec-lint selftest", Tool::Gate, &["check", "spec-lint", "--selftest"], "spec-lint selftest failed - the guard itself is broken; fix rust/gate/crates/checks/src/checks/spec_lint.rs before pushing", true, ""),
    Row("spec-lint", Tool::Gate, &["check", "spec-lint", "--delta", "{root}"], "spec-lint found something a review round would otherwise spend itself on (above) - feature 236, the GM: mistakes caught early and cheaply", false, ""),
    Row("speckit-todo check", Tool::Py("speckit-todo.py"), &["--root", "{root}", "--check"], "an open feature does not say what it affects (above): add its **Affects** line - make speckit-todo CHECK=1 re-checks", false, ""),
    Row("conflict selftest", Tool::Gate, &["check", "conflict", "--selftest"], "conflict-marker selftest failed - the guard itself is broken; fix rust/guard/src/guards/conflict_marker_hooks.rs before pushing", true, ""),
    Row("conflict", Tool::Gate, &["check", "conflict", "--tracked", "{root}"], "a tracked file still carries an unresolved merge conflict (above) - the history here is never rewritten, so resolve it before it lands, feature 241", false, ""),
    Row("record", Tool::Py("gates/memo_check.py"), &["record"], "the record does not build cleanly (above; `make record CHECK=1` at the repository root names each refusal) - features 258 and 301", false, "research/sources"),
    Row("money-candidates", Tool::Gate, &["record", "money-candidates", "--check"], "an amount of money in the record is neither marked for the tooltip nor passed over (above) - mark it, or add `- <stem> | <amount> | <reason>` to specs/413-money-tooltip-on-the-record/backfill.md; feature 413", false, "research/sources"),
    Row("glossary", Tool::Py("gates/memo_check.py"), &["glossary"], "the committed glossary differs from its per-term files (run `make glossary` at the repository root, then commit) - feature 259, spec FR-006", false, "research/sources"),
    Row("gate-stamp selftest", Tool::Gate, &["stamp", "--selftest"], "gate-stamp selftest failed - the guard itself is broken; fix rust/gate/crates/tree/src/stamp.rs before pushing", true, ""),
    Row("gate-stamp", Tool::Gate, &["stamp", "--check", "origin/main"], "push refused by the green-gate guard (above)", false, ""),
    Row("gm-questions", Tool::Py("gm_review.py"), &["owed-check"], "a question for the GM in this push is still owed escalation-check (above) - the one door to him (feature 432, FR-002)", false, "specs"),
    Row("closing", Tool::Py("gates/close_check.py"), &["--push", "origin/main...HEAD"], "REFUSED: a feature this push closes owes what closing owes (feature 375) - the reasons above; a case that is genuinely exempt: CLOSE_OK=\"<reason>\" (recorded)", false, ""),
];

const STAMPS: &str = "l7r-cache/selftests.json";

/// A version of `scripts/`: what a kept self-test is kept against, so any change to the Python it could import runs it again.
fn scripts_version(tree: &Path) -> String {
    let listed = git_line(tree, &["ls-files", "-s", "--", "scripts"]);
    let changed = git_line(tree, &["diff", "--name-only", "--", "scripts"]);
    let mut text = listed;
    for path in changed.lines() {
        text += &sha256::hex(&std::fs::read(tree.join(path)).unwrap_or_default());
    }
    sha256::hex(text.as_bytes())
}

/// THE RUST SELF-TESTS KEPT PER BINARY (feature 449 T109; the GM 2026-11-11): the six ran on every push whether or not the binary had
/// changed, 0.28 s of a 3.7 s push at load 0.5 and about 0.4 s under the sync-with-main suite's load (2026-11-11). Each tests the binary
/// on fixtures of its own, but gate-stamp's, which hashes `.py` files through the tree's `codeid.py`: so a Rust self-test is kept
/// against the version of `scripts/` and the binary as a file - its path, inode, size and time, which a rebuild writes anew. Hashing
/// its 15.6 MB took 33 ms, a ninth of what keeping it saves; a binary whose file cannot be read keeps nothing.
fn binary_id(path: &Path) -> Option<String> {
    let meta = std::fs::metadata(path).ok()?;
    let at = meta
        .modified()
        .ok()?
        .duration_since(std::time::UNIX_EPOCH)
        .ok()?
        .as_nanos();
    Some(format!(
        "{}:{}:{}:{at}",
        path.display(),
        std::os::unix::fs::MetadataExt::ino(&meta),
        meta.len()
    ))
}

fn stamps_file(root: &Path, off: bool) -> Option<PathBuf> {
    if off {
        None
    } else {
        crate::codeid::common_git_dir(root).map(|c| c.join(STAMPS))
    }
}

fn holds(root: &Path, needs: &str) -> bool {
    match needs.strip_prefix("delta:") {
        Some(check) => crate::checks::needs_run(check, root),
        None => needs.is_empty() || root.join(needs).exists(),
    }
}

/// Where the tools are, for this run.
struct Tools {
    tree: PathBuf,
    python: String,
    off: bool,
    /// The gate binary the Rust self-tests run, this process's own: what a passed one is kept against (T109).
    binary: Option<PathBuf>,
}

/// A row's command, in the clone.
fn row_command(tools: &Tools, row: &Row, root: &Path) -> Command {
    let root_text = root.display().to_string();
    let args: Vec<String> = row
        .2
        .iter()
        .map(|a| a.replace("{root}", &root_text))
        .collect();
    let mut command = match row.1 {
        Tool::Gate => Command::new(tools.tree.join("scripts/gates/l7r-gate.sh")),
        Tool::Py(rel) => {
            let mut c = Command::new(&tools.python);
            c.arg(tools.tree.join("scripts").join(rel))
                .env("PYTHONDONTWRITEBYTECODE", "1");
            c
        }
    };
    command.args(&args).current_dir(root);
    command
}

/// The push's rows as `make`'s timing reads them: the one-process run, then each row its own process, a row the clone cannot run named with no command; a row the push would skip on this delta is timed all the same, the measure being what the checks cost.
#[must_use]
pub fn timing_rows(tree: &Path, root: &Path) -> Vec<(String, Option<Command>)> {
    let tools = Tools {
        tree: tree.to_owned(),
        python: "python3".to_owned(),
        off: false,
        binary: None,
    };
    let mut whole = Command::new(tree.join("scripts/gates/l7r-gate.sh"));
    whole.arg("push-checks").arg(root).current_dir(root);
    let mut rows = vec![("push checks (one process)".to_owned(), Some(whole))];
    rows.extend(CHECKS.iter().map(|row| {
        (
            row.0.to_owned(),
            (row.5.starts_with("delta:") || holds(root, row.5))
                .then(|| row_command(&tools, row, root)),
        )
    }));
    rows
}

/// Run one row in the clone: its output passes through, but for a self-test's stdout.
/// Run one row in the clone, its output kept to be shown in the table's order (a self-test's stdout dropped); none where it cannot start.
fn run_row(tools: &Tools, row: &Row, root: &Path) -> Option<std::process::Output> {
    let mut command = row_command(tools, row, root);
    if row.4 {
        command.stdout(Stdio::null());
    }
    command.output().ok()
}

fn run_checks(tools: &Tools, rows: &[Row], root: &Path, skips: &[String]) -> Reply {
    let at = stamps_file(root, tools.off);
    let mut stamps: Value = at
        .as_ref()
        .and_then(|p| std::fs::read_to_string(p).ok())
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or(json!({}));
    let mut changed = false;
    let version = scripts_version(&tools.tree);
    let gate = tools
        .binary
        .as_deref()
        .and_then(binary_id)
        .map(|b| sha256::hex(format!("{version}\n{b}").as_bytes()));
    let mut failed = String::new();
    let owed: Vec<(&Row, Option<&String>)> = rows
        .iter()
        .filter(|r| !skips.iter().any(|s| s == r.0) && holds(root, r.5))
        .map(|row| {
            let key = match row.1 {
                Tool::Py(_) => Some(&version),
                Tool::Gate => gate.as_ref(),
            };
            (row, key.filter(|_| row.4))
        })
        .filter(|(row, key)| !key.is_some_and(|k| stamps[row.0] == k.as_str()))
        .collect();
    // THE ROWS SIDE BY SIDE (feature 449 T115; the GM 2026-11-11): one after another they were 0.82 s of a fixture push's 1.33 s and
    // 2.28 s of a real one (2026-11-12), each its own read-only process. All start at once; then, in the table's order, each row's output
    // is shown and the first refusal ends the run as before - a row after it shows nothing and keeps nothing.
    let ran: Vec<Option<std::process::Output>> = std::thread::scope(|s| {
        let runs: Vec<_> = owed
            .iter()
            .map(|(row, _)| s.spawn(move || run_row(tools, row, root)))
            .collect();
        runs.into_iter().map(|r| r.join().ok().flatten()).collect()
    });
    for ((row, key), out) in owed.into_iter().zip(ran) {
        let passed = out.is_some_and(|o| {
            let _ = std::io::Write::write_all(&mut std::io::stdout(), &o.stdout);
            let _ = std::io::Write::write_all(&mut std::io::stderr(), &o.stderr);
            o.status.success()
        });
        if !passed {
            failed = format!("sync-with-main: {}\n", row.3);
            if row.0 == "closing" {
                let _ = log_write(&Entry {
                    guard: "sync-with-main",
                    event: "blocked",
                    detail: "closing",
                    rule: "closing-owes",
                    context: None,
                    input: &Value::Null,
                    session_name: "",
                });
            }
            break;
        }
        if let Some(k) = key {
            stamps[row.0] = Value::from(k.as_str());
            changed = true;
        }
    }
    if let Some(path) = at.filter(|_| changed) {
        let _ = std::fs::create_dir_all(path.parent().unwrap_or(root));
        let _ = std::fs::write(path, pretty(&stamps));
    }
    Reply {
        stdout: String::new(),
        code: i32::from(!failed.is_empty()),
        stderr: failed,
    }
}

fn parse_skips(rest: &[String]) -> Result<Vec<String>, String> {
    let mut skips = Vec::new();
    let mut words = rest.iter();
    while let Some(word) = words.next() {
        match (word.as_str(), words.next()) {
            ("--skip", Some(name)) => skips.push(name.clone()),
            _ => return Err(format!("push_checks: unknown argument '{word}'\n")),
        }
    }
    let unknown: Vec<&str> = skips
        .iter()
        .map(String::as_str)
        .filter(|s| !CHECKS.iter().any(|r| r.0 == *s))
        .collect();
    if unknown.is_empty() {
        Ok(skips)
    } else {
        Err(format!(
            "push_checks: no check named {} (--list names them)\n",
            unknown.join(", ")
        ))
    }
}

/// `l7r-gate push-checks <root> [--skip <name> ...] [--list]`.
pub fn checks_cli(args: &[String], tree: &Path, off: bool) -> Reply {
    let usage = |text: String| Reply {
        stdout: String::new(),
        stderr: text,
        code: 2,
    };
    match args.first().map(String::as_str) {
        Some("--list") => Reply {
            stdout: CHECKS.iter().flat_map(|r| [r.0, "\n"]).collect(),
            stderr: String::new(),
            code: 0,
        },
        None => usage("usage: push-checks <root> [--skip <name> ...] [--list]\n".to_owned()),
        Some(root) => match parse_skips(&args[1..]) {
            Err(why) => usage(why),
            Ok(skips) => {
                let top = std::fs::canonicalize(root).unwrap_or_default();
                run_checks(
                    &Tools {
                        tree: tree.to_owned(),
                        python: "python3".to_owned(),
                        off,
                        binary: std::env::current_exe().ok(),
                    },
                    &CHECKS,
                    &top,
                    &skips,
                )
            }
        },
    }
}

#[cfg(test)]
mod tests;
