//! `l7r-guard bench` (feature 449 T050, the port of `tests/hooks/hookbench.py`, feature 239 B): a frozen window of real commands replayed through a guard's decision, in
//! process, and the verdicts diffed against the guard as it stood at a ref. Two drafts of an exemption once passed their own cases while changing eleven real verdicts
//! for the worse: the verdict diff over the window is the check such a change owes. Every guard is in this binary now, so none is refused as having no decision.

use std::collections::{BTreeMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::time::{Instant, SystemTime};

use serde::Serialize;
use serde_json::{json, Value};

use crate::guards::house_style_hooks::WORDS;
use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::session::Session;
use crate::shared::tool::ask;
use crate::shared::tree::walk;
use crate::suite_tools::deps::tool_root;

/// silent | corrected | reported | blocked, from what a decision answered.
#[must_use]
pub fn classify(answers: &[Answer]) -> &'static str {
    if answers.iter().any(|a| matches!(a, Answer::Refuse(_))) {
        "blocked"
    } else if answers.iter().any(|a| matches!(a, Answer::Rewrite(_))) {
        "corrected"
    } else if answers.iter().any(|a| matches!(a, Answer::Notice(_))) {
        "reported"
    } else {
        "silent"
    }
}

/// The same four verdicts from what a spawned guard printed.
#[must_use]
pub fn classify_printed(report: &str, blocked: bool) -> &'static str {
    if blocked {
        "blocked"
    } else if report.trim().is_empty() {
        "silent"
    } else if !report.trim_start().starts_with('{') {
        "blocked"
    } else if report.contains("\"updatedInput\"") {
        "corrected"
    } else {
        "reported"
    }
}

fn payload(command: &str) -> Value {
    json!({"tool_name": "Bash", "tool_input": {"command": command}})
}

/// The guard named, with or without its `-hooks`.
#[must_use]
pub fn guard_named<'a>(name: &str, all: &'a [Guard]) -> Option<&'a Guard> {
    let full = format!("{name}-hooks");
    all.iter().find(|g| g.name == name || g.name == full)
}

/// Each command's verdict from the guard's own decision.
#[must_use]
pub fn verdicts(guard: &Guard, commands: &[String]) -> Vec<&'static str> {
    let verdict = |c: &String| {
        let event = Event {
            name: "PreToolUse".to_owned(),
            input: payload(c),
        };
        classify(&(guard.decide)(&event, &Session::from_input(&event.input)))
    };
    commands.iter().map(verdict).collect()
}

fn jsonl_under(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.is_dir() {
            jsonl_under(&path, out);
        } else if path.extension().is_some_and(|e| e == "jsonl") {
            out.push(path);
        }
    }
}

fn commands_in(line: &str) -> Vec<String> {
    let parsed: Value = serde_json::from_str(line).unwrap_or_default();
    let items = parsed["message"]["content"]
        .as_array()
        .cloned()
        .unwrap_or_default();
    let tool = items
        .iter()
        .filter(|c| c["type"] == "tool_use" && c["name"] == "Bash");
    tool.filter_map(|c| c["input"]["command"].as_str().map(str::to_owned))
        .collect()
}

/// Every unique Bash command in the last `days` of transcripts carrying a spelling or a dash.
#[must_use]
pub fn window_commands(days: f64, projects: &Path, now: SystemTime) -> Vec<String> {
    let mut files = Vec::new();
    for project in std::fs::read_dir(projects).into_iter().flatten().flatten() {
        jsonl_under(&project.path(), &mut files);
    }
    files.sort();
    let recent = |p: &PathBuf| {
        std::fs::metadata(p)
            .and_then(|m| m.modified())
            .is_ok_and(|m| {
                now.duration_since(m)
                    .is_ok_and(|age| age.as_secs_f64() < days * 86_400.0)
            })
    };
    let (mut seen, mut out) = (HashSet::new(), Vec::new());
    for path in files.iter().filter(|p| recent(p)) {
        let text = String::from_utf8_lossy(&std::fs::read(path).unwrap_or_default()).into_owned();
        for line in text.lines().filter(|l| l.contains("\"Bash\"")) {
            for command in commands_in(line) {
                if WORDS.is_match(&command).unwrap_or(false) && seen.insert(command.clone()) {
                    out.push(command);
                }
            }
        }
    }
    out
}

fn pretty(value: &Value) -> String {
    let mut buffer = Vec::new();
    let mut writer = serde_json::Serializer::with_formatter(
        &mut buffer,
        serde_json::ser::PrettyFormatter::with_indent(b" "),
    );
    let _ = value.serialize(&mut writer);
    String::from_utf8_lossy(&buffer).into_owned()
}

/// Freeze the window into a dated fixture; its path.
#[must_use]
pub fn refresh(days: f64, out_dir: &Path, projects: &Path) -> PathBuf {
    let today = ask(out_dir, "date", &["+%F"], "").out.trim().to_owned();
    let commands = window_commands(days, projects, SystemTime::now());
    let out = out_dir.join(format!("command-window-{today}.json"));
    let frozen = json!({"taken": today, "days": days, "built_by": "make hookbench REFRESH=1", "what": "every unique Bash command in the window carrying a British spelling or a forbidden dash", "commands": commands});
    let _ = std::fs::write(&out, pretty(&frozen) + "\n");
    out
}

/// The newest frozen window.
fn latest_corpus(fixtures: &Path) -> Option<PathBuf> {
    let named = |p: &PathBuf| {
        p.file_name()
            .is_some_and(|n| n.to_string_lossy().starts_with("command-window-"))
            && p.extension().is_some_and(|e| e == "json")
    };
    let mut found: Vec<PathBuf> = std::fs::read_dir(fixtures)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(named)
        .collect();
    found.sort();
    found.pop()
}

/// Each verdict that moved: (before, after, command).
#[must_use]
pub fn diff<'a>(
    commands: &'a [String],
    before: &[&'static str],
    after: &[&'static str],
) -> Vec<(&'static str, &'static str, &'a str)> {
    let rows = commands.iter().zip(before).zip(after);
    rows.filter(|((_, b), a)| a != b)
        .map(|((c, b), a)| (*b, *a, c.as_str()))
        .collect()
}

/// Where to run the guard as it stood at a ref: the arguments after the program, the program.
fn baseline(
    tree: &Path,
    guard: &Guard,
    cargo: &str,
) -> Result<(String, Vec<String>, String), String> {
    let module = guard.name.replace('-', "_");
    if tree
        .join(format!("rust/guard/src/guards/{module}.rs"))
        .is_file()
    {
        let manifest = tree.join("rust/Cargo.toml").to_string_lossy().into_owned();
        let target = tree.join("target");
        // `--release`, not the tools' `--profile tool` (T95): this builds the guard as it stood at an older ref, whose manifest may
        // define no `tool` profile, into that worktree's own target, so nothing is shared to gain from it
        let script = format!("CARGO_TARGET_DIR='{}' '{cargo}' build --release --quiet --manifest-path '{manifest}' -p l7r_guard", target.display());
        let built = ask(tree, "bash", &["-c", &script], "");
        if built.code != 0 {
            return Err(format!(
                "hookbench: the guard at that ref would not build: {}",
                built.err
            ));
        }
        let binary = target
            .join("release/l7r-guard")
            .to_string_lossy()
            .into_owned();
        return Ok((
            binary,
            vec![
                "--only".to_owned(),
                guard.name.to_owned(),
                "PreToolUse".to_owned(),
            ],
            "its Rust guard built from that ref, one spawn a command".to_owned(),
        ));
    }
    let shells = [
        format!("scripts/hooks/{}.sh", guard.name),
        format!("scripts/{}.sh", guard.name),
    ];
    shells
        .iter()
        .map(|s| tree.join(s))
        .find(|p| p.is_file())
        .map_or_else(
            || {
                Err(format!(
                    "hookbench: {} did not exist at that ref",
                    guard.name
                ))
            },
            |shell| {
                Ok((
                    shell.to_string_lossy().into_owned(),
                    vec!["pretool".to_owned()],
                    "its shell guard at that ref, one spawn a command".to_owned(),
                ))
            },
        )
}

/// The verdicts from the guard as it stood at `reference`, and how they were obtained.
fn verdicts_at(
    root: &Path,
    reference: &str,
    guard: &Guard,
    commands: &[String],
    cargo: &str,
) -> Result<(Vec<&'static str>, String), String> {
    let tree = crate::shared::tempdir::TempDir::new("hookbench");
    let result = (|| {
        let tar = tree.join("a.tar").to_string_lossy().into_owned();
        let at = root.to_string_lossy().into_owned();
        let archive = |paths: &[&str]| {
            ask(
                root,
                "git",
                &[&["-C", &at, "archive", "-o", &tar, reference], paths].concat(),
                "",
            )
        };
        let first = archive(&["rust", "scripts"]);
        let made = if first.code == 0 {
            first
        } else {
            archive(&["scripts"])
        };
        if made.code != 0 {
            return Err(format!(
                "hookbench: cannot read scripts/ at {reference}: {}",
                made.err
            ));
        }
        let _ = ask(&tree, "tar", &["-xf", &tar], "");
        let (program, args, how) = baseline(&tree, guard, cargo)?;
        let began = Instant::now();
        let refs: Vec<&str> = args.iter().map(String::as_str).collect();
        let verdict = |c: &String| {
            let said = ask(&tree, &program, &refs, &payload(c).to_string());
            classify_printed(&said.out, said.code == 2)
        };
        let out: Vec<&'static str> = commands.iter().map(verdict).collect();
        Ok((
            out,
            format!("{how}, {:.1} s", began.elapsed().as_secs_f64()),
        ))
    })();
    drop(tree);
    result
}

fn report(
    guard: &Guard,
    corpus: &Path,
    commands: &[String],
    now: &[&'static str],
    took: f64,
) -> String {
    let count = |v: &str| now.iter().filter(|n| **n == v).count();
    let name = corpus
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    format!(
        "hookbench {}: {} commands from {name}, in process in {took:.1} s\n  corrected {}  reported {}  silent {}  blocked {}\n",
        guard.name, commands.len(), count("corrected"), count("reported"), count("silent"), count("blocked")
    )
}

fn diff_report(
    reference: &str,
    how: &str,
    changed: &[(&'static str, &'static str, &str)],
) -> String {
    let mut out = format!(
        "\nverdict diff against {reference} ({how}): {} changed\n",
        changed.len()
    );
    let mut moves: BTreeMap<String, usize> = BTreeMap::new();
    for (before, after, _) in changed {
        *moves.entry(format!("{before} -> {after}")).or_default() += 1;
    }
    let mut ranked: Vec<(String, usize)> = moves.into_iter().collect();
    ranked.sort_by_key(|(_, n)| std::cmp::Reverse(*n));
    for (movement, n) in ranked {
        let _ = writeln!(out, "  {n:4}  {movement}");
    }
    let home = std::env::var("HOME").unwrap_or_default();
    for (before, after, command) in changed.iter().take(25) {
        let targets: Vec<Option<String>> = walk(command, None, &home, &home)
            .targets
            .into_iter()
            .take(3)
            .map(|t| t.path)
            .collect();
        let head: String = command
            .trim()
            .lines()
            .next()
            .unwrap_or_default()
            .chars()
            .take(90)
            .collect();
        let _ = writeln!(out, "  [{before} -> {after}] targets={targets:?} :: {head}");
    }
    out
}

/// `l7r-guard bench`: `--refresh [DAYS]` freezes the window; `<guard> [--against <ref>]` replays it.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let projects =
        PathBuf::from(std::env::var("HOME").unwrap_or_default()).join(".claude/projects");
    answer(
        &tool_root(),
        args,
        &crate::guards(),
        &projects,
        &std::env::var("L7R_GUARD_CARGO").unwrap_or_else(|_| "cargo".to_owned()),
    )
}

pub(crate) fn answer(
    root: &Path,
    args: &[String],
    all: &[Guard],
    projects: &Path,
    cargo: &str,
) -> Reply {
    // the bench is not a guard firing: no case of it reaches the real log, and its own log goes when the bench returns (feature 449
    // T101)
    let own_log = crate::shared::tempdir::TempDir::new("hookbench-log");
    let fallback = own_log.as_os_str().to_owned();
    std::env::set_var(
        "GUARD_LOG_DIR",
        std::env::var_os("GUARD_LOG_DIR").unwrap_or(fallback),
    );
    let fail = |stderr: String| Reply {
        stdout: String::new(),
        stderr,
        code: 1,
    };
    let say = |stdout: String| Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    };
    let fixtures = root.join("tests/hooks/fixtures");
    let read_commands = |p: &Path| -> Vec<String> {
        let parsed: Value = serde_json::from_str(&std::fs::read_to_string(p).unwrap_or_default())
            .unwrap_or_default();
        parsed["commands"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
            .map(str::to_owned)
            .collect()
    };
    if args.iter().any(|a| a == "--refresh") {
        let days = args
            .iter()
            .find_map(|a| a.parse::<f64>().ok())
            .unwrap_or(14.0);
        let out = refresh(days, &fixtures, projects);
        let shown = out.strip_prefix(root).unwrap_or(&out).display();
        return say(format!(
            "hookbench: froze {} commands into {shown}\n",
            read_commands(&out).len()
        ));
    }
    let Some(name) = args.iter().find(|a| !a.starts_with('-')) else {
        return fail("hookbench: name a GUARD (e.g. house-style), or pass --refresh\n".to_owned());
    };
    let Some(guard) = guard_named(name, all) else {
        return fail(format!("hookbench: no guard named {name} in this binary - a guard still in shell (phase 3) is refused rather than spawned per command, which would hide the cost this bench exists to show\n"));
    };
    let Some(corpus) = latest_corpus(&fixtures) else {
        return fail("hookbench: no frozen corpus in tests/hooks/fixtures/ - run `make hookbench REFRESH=1` first\n".to_owned());
    };
    let commands = read_commands(&corpus);
    let began = Instant::now();
    let now = verdicts(guard, &commands);
    let mut out = report(
        guard,
        &corpus,
        &commands,
        &now,
        began.elapsed().as_secs_f64(),
    );
    if let Some(reference) = args
        .iter()
        .position(|a| a == "--against")
        .and_then(|i| args.get(i + 1))
    {
        match verdicts_at(root, reference, guard, &commands, cargo) {
            Ok((before, how)) => out.push_str(&diff_report(
                reference,
                &how,
                &diff(&commands, &before, &now),
            )),
            Err(why) => return fail(why + "\n"),
        }
    }
    say(out)
}

#[cfg(test)]
mod tests;
