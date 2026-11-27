//! A landed task's SIZE, COUNTS, TURNS and TOKENS beside its minutes (feature 451 T512; the GM 2026-11-27, request.md: "it is the
//! kind of thing that would make it much easier for me to eyeball how reasonable the times that I'm seeing look", with his caution
//! about Goodhart's Law). The figures are printed raw - no ratio of lines to minutes, no ranking - for the holistic process review
//! to read beside the minutes, never as a target.
//!
//! SIZE is read from git at report time, one `git log --numstat` over the clone's HEAD from the read-back's start (0.2 s over the
//! 2026-11-25T04:30Z to 2026-11-27T15:30Z read-back, measured 2026-11-27, so nothing is cached): every commit whose subject names
//! its tasks the way a builder's done commit is named (`451 T510: ...`, `451 T470 T363: ...`, `451 T363's coverage repair ...`)
//! and the session's coverage repair (`451: T492's and T495's coverage repair ...`). A cherry-picked carry keeps its subject, and
//! a carry finished by hand is that same commit, so it is read once. A BUNDLE's commit is not split: its whole diff is under each
//! task it names, marked shared, since no rule in the record says which of its lines are whose. A landing's tick commit
//! (`<feature>: T507 T508 ticked (make land)`) is the task and plan text moved to the done files, not the task's work, and is left
//! out. A file's lines are TEST under a `tests/` directory, in a `tests.rs` or a `*_tests.rs` sibling module; PROSE under
//! `specs/` or in any `.md`; else NON-TEST. A `#[cfg(test)] mod x { ... }` block inside a source file is not split out (93 of
//! the 1,552 `.rs` files held one on 2026-11-27): its lines are non-test, and the files of a task's diff holding one are counted.

use std::collections::HashMap;
use std::path::Path;

use super::super::events::git;
use super::book::Key;

/// Lines added and deleted.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct Lines {
    /// Added.
    pub add: u64,
    /// Deleted.
    pub del: u64,
}

/// Which of the three a file's lines are.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Class {
    /// Tests.
    Test,
    /// Everything that is neither tests nor prose.
    Code,
    /// Specs, plans and other Markdown.
    Prose,
}

/// A task's size from its commits.
#[derive(Debug, Default, Clone, PartialEq, Eq)]
pub struct Size {
    /// Test lines.
    pub test: Lines,
    /// Non-test lines.
    pub code: Lines,
    /// Spec, plan and other Markdown lines.
    pub prose: Lines,
    /// Its commits.
    pub commits: usize,
    /// The other tasks its commits name (a bundle's), each once.
    pub shared: Vec<String>,
    /// Its non-test `.rs` files that hold an inline `#[cfg(test)]` block, their lines counted non-test.
    pub inline: usize,
}

/// One commit: its subject and each file's (path, added, deleted).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Commit {
    /// Its subject.
    pub subject: String,
    /// (path, added, deleted) - a binary file's 0 and 0.
    pub files: Vec<(String, u64, u64)>,
}

/// A numstat path's new side: `a/{x => y}/b` is `a/y/b`, `x => y` is `y`.
#[must_use]
pub fn renamed_to(path: &str) -> String {
    if let (Some(open), Some(close)) = (path.find('{'), path.find('}')) {
        let inner = &path[open + 1..close];
        let new = inner.split(" => ").last().unwrap_or(inner);
        return format!("{}{new}{}", &path[..open], &path[close + 1..]).replace("//", "/");
    }
    path.split(" => ").last().unwrap_or(path).to_owned()
}

/// A path's extension, lower-cased, "" for none.
fn ext(path: &str) -> String {
    Path::new(path)
        .extension()
        .map(|e| e.to_string_lossy().to_ascii_lowercase())
        .unwrap_or_default()
}

/// The class of a file's lines (the module's doc).
#[must_use]
pub fn class_of(path: &str) -> Class {
    let p = renamed_to(path);
    let name = p.rsplit('/').next().unwrap_or(&p);
    if p.starts_with("specs/") || ext(name) == "md" {
        Class::Prose
    } else if p.starts_with("tests/")
        || p.contains("/tests/")
        || name == "tests.rs"
        || name.ends_with("_tests.rs")
    {
        Class::Test
    } else {
        Class::Code
    }
}

/// A task id, `T` and digits.
fn tid(w: &str) -> Option<String> {
    let digits = w.strip_prefix('T')?;
    (!digits.is_empty() && digits.bytes().all(|b| b.is_ascii_digit())).then(|| w.to_owned())
}

/// A feature number, digits.
fn number(w: &str) -> Option<String> {
    (!w.is_empty() && w.bytes().all(|b| b.is_ascii_digit())).then(|| w.to_owned())
}

/// The feature number and tasks a commit's subject names (the module's doc), none for any other subject.
#[must_use]
pub fn named(subject: &str) -> Option<(String, Vec<String>)> {
    let words: Vec<&str> = subject.split(' ').collect();
    let first = words.first().copied().unwrap_or_default();
    let mut tasks = Vec::new();
    if let Some(num) = first.strip_suffix(':') {
        // the session's repair: `451: T492's and T495's coverage repair`
        let num = number(num)?;
        let mut i = 1;
        loop {
            tasks.push(tid(words.get(i)?.strip_suffix("'s")?)?);
            i += 1;
            if words.get(i) != Some(&"and") {
                break;
            }
            i += 1;
        }
        return (words.get(i..i + 2) == Some(&["coverage", "repair"][..])).then_some((num, tasks));
    }
    let num = number(first)?;
    // the leading task words, `and` between them: `451 T143 and T342's close`, `451 T313 (with ...)`, `451 T397 part (c):`
    for w in words.iter().skip(1) {
        if *w == "and" && !tasks.is_empty() {
            continue;
        }
        let end = w.strip_suffix(':').or_else(|| w.strip_suffix("'s"));
        let Some(id) = tid(end.unwrap_or(w).trim_end_matches(',')) else {
            break;
        };
        tasks.push(id);
        if end.is_some() {
            break;
        }
    }
    (!tasks.is_empty()).then_some((num, tasks))
}

/// `git log --numstat --format=%x1e%s`'s output read: each commit's subject and files.
#[must_use]
pub fn parse(text: &str) -> Vec<Commit> {
    text.split('\u{1e}')
        .filter(|c| !c.trim().is_empty())
        .map(|c| {
            let mut lines = c.lines();
            let subject = lines.next().unwrap_or_default().to_owned();
            let files = lines
                .filter_map(|l| {
                    let mut f = l.splitn(3, '\t');
                    let (a, d, p) = (f.next()?, f.next()?, f.next()?);
                    Some((p.to_owned(), a.parse().unwrap_or(0), d.parse().unwrap_or(0)))
                })
                .collect();
            Commit { subject, files }
        })
        .collect()
}

/// Whether a source file's text holds an inline test block: a `#[cfg(test)]` line before a `mod <name> {` line.
#[must_use]
pub fn inline_tests(text: &str) -> bool {
    let lines: Vec<&str> = text
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty())
        .collect();
    lines.windows(2).any(|w| {
        w[0] == "#[cfg(test)]"
            && w[1].ends_with('{')
            && (w[1].starts_with("mod ")
                || w[1].starts_with("pub mod ")
                || w[1].starts_with("pub(crate) mod "))
    })
}

/// Each landed task's size from `commits` (newest first, as git lists them), `root` the tree whose files are read for inline tests.
#[must_use]
pub fn of_commits(commits: &[Commit], landed: &[Key], root: &Path) -> HashMap<Key, Size> {
    let mut out: HashMap<Key, Size> = HashMap::new();
    let mut inline_seen: HashMap<Key, Vec<String>> = HashMap::new();
    for c in commits {
        let Some((num, tasks)) = named(&c.subject) else {
            continue;
        };
        for t in &tasks {
            let Some(key) = landed
                .iter()
                .find(|k| k.1 == *t && k.0.split('-').next() == Some(num.as_str()))
            else {
                continue;
            };
            let s = out.entry(key.clone()).or_default();
            s.commits += 1;
            for o in tasks.iter().filter(|o| *o != t) {
                if !s.shared.contains(o) {
                    s.shared.push(o.clone());
                }
            }
            for (path, a, d) in &c.files {
                let into = match class_of(path) {
                    Class::Test => &mut s.test,
                    Class::Code => &mut s.code,
                    Class::Prose => &mut s.prose,
                };
                into.add += a;
                into.del += d;
                let p = renamed_to(path);
                let seen = inline_seen.entry(key.clone()).or_default();
                if class_of(path) == Class::Code && ext(&p) == "rs" && !seen.contains(&p) {
                    let text = std::fs::read_to_string(root.join(&p)).unwrap_or_default();
                    if inline_tests(&text) {
                        s.inline += 1;
                    }
                    seen.push(p);
                }
            }
        }
    }
    out
}

/// Each landed task's size from the commits of `root`'s HEAD since `since` (an ISO time): none where git cannot be read.
#[must_use]
pub fn sizes(root: &Path, since: &str, landed: &[Key]) -> HashMap<Key, Size> {
    let text = git(
        root,
        &[
            "log",
            "--numstat",
            "--format=%x1e%s",
            &format!("--since={since}"),
            "HEAD",
        ],
    )
    .unwrap_or_default();
    of_commits(&parse(&text), landed, root)
}
