//! An unresolved merge conflict committed (feature 241; feature 449 T067, from `hm_conflict.py`): the guard's one detector, over every
//! tracked file, for the gate and the push. The history here is never rewritten, so a conflict that lands is only fixed by a commit.

use std::fmt::Write as _;
use std::path::Path;

use l7r_guard::guards::conflict_marker_hooks::{
    conflicted, exemption_reason, has_conflict, staged_by, EXEMPT, HEAD_LINES,
};

use super::{git_z, scratch, Outcome};

/// The name its runs are recorded under in the `usage_log`.
pub(super) const USAGE_LOG_TOOL: &str = "conflict-markers";

fn tracked(root: &Path) -> Vec<String> {
    git_z(root, &["ls-files", "-z"]).unwrap_or_default()
}

/// Does this tracked file carry a conflict? Unreadable as text - binary, a directory, gone - is no.
fn carries(path: &Path) -> bool {
    std::fs::read_to_string(path).is_ok_and(|text| has_conflict(&text))
}

/// Every tracked file carrying a conflict, read on several threads: this runs at every push.
fn scan(root: &Path, files: &[String]) -> Vec<String> {
    let threads = std::thread::available_parallelism().map_or(1, std::num::NonZero::get);
    let check = |part: &[String]| -> Vec<String> {
        part.iter()
            .filter(|f| carries(&root.join(f)))
            .cloned()
            .collect()
    };
    let mut found: Vec<String> = std::thread::scope(|s| {
        let check = &check;
        let running: Vec<_> = files
            .chunks(files.len().div_ceil(threads).max(1))
            .map(|part| s.spawn(move || check(part)))
            .collect();
        running
            .into_iter()
            .flat_map(|t| t.join().unwrap_or_default())
            .collect()
    });
    found.sort();
    found
}

/// The file-level exemption's declarer among a file's first lines, if any.
fn declared(path: &Path) -> Option<String> {
    let text = std::fs::read_to_string(path).ok()?;
    text.lines().take(HEAD_LINES).find_map(exemption_reason)
}

fn list(root: &str) -> Outcome {
    let top = Path::new(root);
    let mut taken: Vec<(String, String)> = tracked(top)
        .into_iter()
        .filter_map(|f| declared(&top.join(&f)).map(|r| (f, r)))
        .collect();
    taken.sort();
    let mut out: String = taken
        .iter()
        .flat_map(|(p, r)| {
            [
                "  ".to_owned(),
                p.clone(),
                ": ".to_owned(),
                r.chars().take(96).collect(),
                "\n".to_owned(),
            ]
        })
        .collect();
    let none = if taken.is_empty() { " - none" } else { "" };
    let _ = writeln!(
        out,
        "  {} file(s) declare {}{none}",
        taken.len(),
        EXEMPT.trim_end_matches(':')
    );
    Outcome::out(out)
}

fn tracked_check(root: &str) -> Outcome {
    let top = Path::new(root);
    let files = tracked(top);
    let bad = scan(top, &files);
    if bad.is_empty() {
        return Outcome::out(format!(
            "conflict-markers: none in {} tracked file(s)\n",
            files.len()
        ));
    }
    // A path joined to "." reads as the bare name, as the Python's `Path` wrote it.
    let names: Vec<String> = bad
        .iter()
        .map(|p| format!("{root}/{p}").trim_start_matches("./").to_owned())
        .collect();
    let listed: String = names
        .iter()
        .flat_map(|p| ["  ", p.as_str(), "\n"])
        .collect();
    Outcome::refuse(format!("\nCONFLICT MARKERS IN TRACKED FILES - a merge was committed unresolved:\n{listed}\nResolve each and commit the resolution. The history here is never rewritten, so these cannot be\namended away - the fix is a commit on top. A file that must SHOW a triple says so with\n`{EXEMPT} <reason>` in its first {HEAD_LINES} lines (feature 241).\n\n"))
}

/// (a name, the text, is it a conflict): the markers are built here, so this file carries no triple of its own.
fn cases() -> Vec<(&'static str, String, bool)> {
    let (open, mid, close) = ("<".repeat(7), "=".repeat(7), ">".repeat(7));
    let triple = format!("{open} HEAD\nmine\n{mid}\ntheirs\n{close} other\n");
    let indented: String = triple.lines().flat_map(|l| ["    ", l, "\n"]).collect();
    vec![
        ("the triple at column 0", triple.clone(), true),
        (
            "a fence does not exempt it",
            format!("doc\n\n```\n{triple}```\n"),
            true,
        ),
        (
            "a lone underline is Markdown",
            format!("A heading\n{mid}\n\ntext\n"),
            false,
        ),
        (
            "a lone open marker is prose",
            format!("{open} is what git writes\n"),
            false,
        ),
        ("indented, the way prose shows it", indented, false),
        (
            "out of order is not a conflict",
            format!("{close} x\n{mid}\n{open} y\n"),
            false,
        ),
        (
            "the file-level exemption, with a reason",
            format!("{EXEMPT} this doc must show one\n{triple}"),
            false,
        ),
        (
            "as a comment, the way a script declares it",
            format!("# {EXEMPT} a fixture that must hold one\n{triple}"),
            false,
        ),
        (
            "not a one-word reason",
            format!("{EXEMPT} x\n{triple}"),
            true,
        ),
        (
            "not a mention mid-sentence",
            format!("a doc saying to put `{EXEMPT} <reason>` in the first 40 lines\n{triple}"),
            true,
        ),
        (
            "nor a placeholder reason",
            format!("{EXEMPT} <reason>\n{triple}"),
            true,
        ),
        (
            "not past the head",
            format!(
                "{}{EXEMPT} too far down to count\n{triple}",
                "\n".repeat(HEAD_LINES)
            ),
            true,
        ),
    ]
}

/// The rows whose verdict is not what they say.
fn wrong_cases<'a>(rows: &'a [(&'a str, String, bool)]) -> Vec<&'a str> {
    rows.iter()
        .filter(|(_, text, want)| has_conflict(text) != *want)
        .map(|(name, ..)| *name)
        .collect()
}

/// (the command, where it runs, does it stage a conflict, a name).
type Shape = (String, String, bool, &'static str);

/// The command half: the recorded incident's own shape, which the first implementation missed.
fn shapes(at: &str) -> Vec<Shape> {
    vec![
        (
            format!("CL={at}; git -C $CL add -A"),
            "/".to_owned(),
            true,
            "the incident shape `CL=...; git -C $CL add -A`",
        ),
        (
            "git add -A".to_owned(),
            at.to_owned(),
            true,
            "a bare `git add -A` in the tree",
        ),
        (
            "git add .".to_owned(),
            format!("{at}/sub"),
            false,
            "`git add .` in a clean subdirectory must pass",
        ),
        (
            "git commit -m \"a message naming f.md is not a pathspec\"".to_owned(),
            at.to_owned(),
            false,
            "a commit message must not be read as a pathspec",
        ),
    ]
}

fn wrong_shapes(rows: &[Shape]) -> Vec<&'static str> {
    rows.iter()
        .filter(|(cmd, base, want, _)| conflicted(&staged_by(cmd, base)).is_empty() == *want)
        .map(|(.., name)| *name)
        .collect()
}

fn command_shapes() -> Vec<&'static str> {
    let dir = scratch("conflict");
    let (open, mid, close) = ("<".repeat(7), "=".repeat(7), ">".repeat(7));
    let _ = std::process::Command::new("git")
        .arg("-C")
        .arg(&dir)
        .args(["init", "-q"])
        .output();
    let _ = std::fs::write(
        dir.join("f.md"),
        format!("{open} HEAD\nmine\n{mid}\ntheirs\n{close} other\n"),
    );
    let _ = std::fs::create_dir_all(dir.join("sub"));
    let _ = std::fs::write(dir.join("sub/ok.md"), "clean\n");
    let bad = wrong_shapes(&shapes(&dir.display().to_string()));
    let _ = std::fs::remove_dir_all(&dir);
    bad
}

fn selftest() -> Outcome {
    let all = cases();
    let mut bad = wrong_cases(&all);
    bad.extend(command_shapes());
    Outcome::selftest(
        bad.is_empty(),
        &format!(
            "_hm_conflict selftest: {} content cases + 4 command shapes\n",
            all.len()
        ),
        format!("_hm_conflict selftest FAILED: {}\n", bad.join("; ")),
    )
}

/// `l7r-gate check conflict --selftest | --tracked [ROOT] | --list [ROOT]`.
pub(super) fn cli(args: &[String]) -> Outcome {
    let root = args.get(1).map_or(".", String::as_str);
    match args.first().map(String::as_str) {
        Some("--selftest") => selftest(),
        Some("--list") => list(root),
        Some("--tracked") => tracked_check(root),
        _ => Outcome {
            stdout: String::new(),
            stderr: "usage: check conflict --selftest | --tracked <root> | --list <root>\n"
                .to_owned(),
            code: 2,
        },
    }
}

#[cfg(test)]
mod tests;
