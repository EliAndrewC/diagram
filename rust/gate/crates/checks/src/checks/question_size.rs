//! A research question's prose stays under a size cap, on the questions a change touches (feature 250 D14; prose only since feature 292; feature 449 T065, from `check-question-size.py`). The cap is the record's 90th percentile of
//! question plus notes; each question over it is split along its topics by the session that works its page. A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use fancy_regex::Regex;

use super::moves::moved_only;
use super::{git_text, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-question-size";
const CAP: usize = 20_000;
const RECORD: &str = "research";
const COMPANIONS: [&str; 2] = [".notes.html", ".originals.html"];

fn with_commas(n: usize) -> String {
    let digits = n.to_string();
    digits
        .chars()
        .enumerate()
        .fold(String::new(), |mut out, (at, c)| {
            if at > 0 && (digits.len() - at) % 3 == 0 {
                out.push(',');
            }
            out.push(c);
            out
        })
}

fn is_question(rel: &str) -> bool {
    let (dirs, name) = rel.rsplit_once('/').unwrap_or(("", rel));
    let pattern = Regex::new(r"^[0-9]{4}-[^.]+(?:\.drawing)?\.html$").unwrap();
    pattern.is_match(name).unwrap_or(false) && dirs.split('/').any(|p| p == "questions")
}

/// A question's notes or originals file names the question it belongs to; a question is itself.
fn question_of(rel: &str) -> String {
    COMPANIONS
        .iter()
        .find_map(|s| rel.strip_suffix(s).map(|head| format!("{head}.html")))
        .unwrap_or_else(|| rel.to_owned())
}

/// The question's prose in bytes: a money mark is markup around words already counted (feature 413).
fn size(path: &Path) -> usize {
    let text = std::fs::read_to_string(path).unwrap_or_default();
    let money = Regex::new(r#"(?s)<span class="money"[^>]*>(.*?)</span>"#).unwrap();
    money.replace_all(&text, "$1").len()
}

fn changed(root: &Path) -> Vec<String> {
    let base = git_text(root, &["merge-base", "HEAD", "origin/main"])
        .trim()
        .to_owned();
    let against = if base.is_empty() { "HEAD" } else { &base };
    let mut names = git_text(root, &["diff", "--name-only", against, "--", RECORD]);
    names += &git_text(
        root,
        &["ls-files", "--others", "--exclude-standard", "--", RECORD],
    );
    let all: Vec<String> = names.split_whitespace().map(str::to_owned).collect();
    let moved = moved_only(root, &base, &all);
    let wanted: BTreeSet<String> = all
        .iter()
        .filter(|n| !moved.contains(*n))
        .map(|n| question_of(n))
        .filter(|q| is_question(q) && root.join(q).is_file())
        .collect();
    wanted.into_iter().collect()
}

fn every(root: &Path) -> Vec<String> {
    let mut found: Vec<PathBuf> = std::fs::read_dir(root.join(RECORD).join("questions"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    found.sort();
    found
        .iter()
        .map(|p| {
            format!(
                "{RECORD}/questions/{}",
                p.file_name().unwrap_or_default().to_string_lossy()
            )
        })
        .filter(|q| is_question(q))
        .collect()
}

fn report(root: &Path) -> Outcome {
    let mut over: Vec<(usize, String)> = every(root)
        .into_iter()
        .map(|q| (size(&root.join(&q)), q))
        .filter(|(n, _)| *n > CAP)
        .collect();
    over.sort_by(|a, b| b.cmp(a));
    let mut out = String::new();
    for (n, q) in &over {
        let _ = writeln!(out, "{:>7}  {q}", with_commas(*n));
    }
    let _ = writeln!(
        out,
        "{} question(s) over {} bytes of prose",
        over.len(),
        with_commas(CAP)
    );
    Outcome::out(out)
}

/// `l7r-gate check question-size [--report]`.
pub(super) fn cli(args: &[String], root: &Path) -> Outcome {
    if args.iter().any(|a| a == "--report") {
        return report(root);
    }
    let over: Vec<(usize, String)> = changed(root)
        .into_iter()
        .map(|q| (size(&root.join(&q)), q))
        .filter(|(n, _)| *n > CAP)
        .collect();
    if over.is_empty() {
        return Outcome::out(String::new());
    }
    let mut err = String::new();
    for (n, q) in &over {
        let _ = writeln!(err, "question-size: {q} is {} bytes of prose, over the {} cap - split it along its topics (a finding stays with its decision; each part its own question and heading; the joins point, they do not restate). Why and how: docs/research-record-rules.md, 'A question has a size'.", with_commas(*n), with_commas(CAP));
    }
    Outcome::refuse(err)
}

#[cfg(test)]
mod tests;
