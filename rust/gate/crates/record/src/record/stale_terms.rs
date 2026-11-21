//! After a value changed in a feature directory, where does the OLD value still stand? (feature 253; feature 449 T79, from `stale_terms.py`.)
//!
//! Later `spec-fidelity` rounds were about 61% of what spec review cost, and in features 251 and 252 most of what they found was text the session had left stale.
//! For every line a change REPLACED, the SUBJECTS are the backticked terms the old and new line share, the OLD VALUES the words the old line carried and the new one
//! does not, of those the change touched: not a word the rewritten passage kept in place with both its neighbors, as a word re-wrapped onto the next line is
//! (`touched`, 451 T73); a CANDIDATE is any other line of the directory that names a subject, in the sense the changed line did (`names`, 451 T54), and still carries an old
//! value. A candidate is a line to look at, never a verdict.

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::{first_chars, py_lines, reply};
use crate::difflib::{opcodes, Tag};
use crate::Reply;

/// `research.md` keeps the value that was TESTED: with it included, 16 of 18 candidates were false (feature 251, specs/253 research R1, measured then).
const SKIP_NAMES: [&str; 5] = [
    "request.md",
    "gm-request.md",
    "research.md",
    "measurements.json",
    "plan-review.json",
];
const SKIP_DIR: &str = "measure";
const COMMON: &str = "the and for that this with from are was were has have had not but its their they them then than into onto over each when where which while will would should could may must can one two all any more most some such only also both here there what how why who does did done being been same other after before under between against about";

fn compiled(p: &str) -> Regex {
    l7r_shared::regex::build(p).unwrap_or_else(|e| unreachable!("{e}"))
}

static TOKEN: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"[A-Za-z][A-Za-z-]{2,}|\d+(?:[.,]\d+)*%?"));
static REQ: LazyLock<Regex> = LazyLock::new(|| compiled(r"^- \*\*(FR-\d{3}[a-z]?)\*\*"));
static CRIT: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"^- \*\*(SC-\d{3}[a-z]?)\*\*\s*\(([^)]*)\)"));
static FR: LazyLock<Regex> = LazyLock::new(|| compiled(r"FR-\d{3}[a-z]?"));
static COMMON_SET: LazyLock<HashSet<&'static str>> = LazyLock::new(|| COMMON.split(' ').collect());

/// The files of a feature directory, by path relative to it.
pub type Files = BTreeMap<String, String>;

/// One thing to look at.
#[derive(Debug, PartialEq, Eq)]
pub struct Candidate {
    file: String,
    line: usize,
    subject: String,
    old_values: Vec<String>,
    text: String,
    changed_in: String,
    changed_to: String,
    criterion: bool,
}

fn tokens(line: &str) -> BTreeSet<String> {
    TOKEN
        .find_iter(line)
        .map_while(Result::ok)
        .map(|m| m.as_str().to_lowercase())
        .filter(|t| !COMMON_SET.contains(t.as_str()))
        .collect()
}

/// The code spans of `line`, its backticks paired in order. A regex scan for 2 to 60 characters between backticks paired the closing
/// backtick of a span it could not keep (`t`) with the next span's opening one, making the prose between two spans a subject (451 T54).
fn spans(line: &str) -> Vec<&str> {
    let pieces: Vec<&str> = line.split('`').collect();
    let closed = pieces.len().saturating_sub(1);
    pieces.into_iter().take(closed).skip(1).step_by(2).collect()
}

fn subjects(line: &str) -> BTreeSet<String> {
    spans(line)
        .into_iter()
        .filter(|s| (2..=60).contains(&s.chars().count()))
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .map(str::to_owned)
        .collect()
}

/// A subject that is one ordinary word - letters alone, capitalized at most at its start (`end`, `well`, `street`, `Done`) - which
/// prose also writes in its ordinary sense. Any other term is a name: a phrase (`780 sq ft`, `make land`), a path, a number, an
/// identifier (`back_lane`, `FreeGround`) or a capitalized label (`GUESS`).
fn plain_word(subject: &str) -> bool {
    let mut chars = subject.chars();
    chars.next().is_some_and(char::is_alphabetic) && chars.all(char::is_lowercase)
}

/// Does `text` name `subject` in the sense the changed line did (451 T54)? A plain word only as that code span, since the word in
/// prose is the ordinary word (the log's refusals on `end`, `well`, `street`, `edge`, `drawn`: 451's 66 candidates, 56 of them
/// `end` read as "end" or inside Independent and `append_row`, measured 2026-11-21 from the commits at the snapshot and the refusal);
/// any other term written out, bare or in a span, but never inside a longer word: neither of its ends, where that end is a word's
/// character, runs on into one (`GUESS` not in GUESSES, `make land` not in `make landing`). The plain word's span is the literal
/// `` `word` ``, not a span paired in order, since a line that opens inside a span wrapped from the line before pairs every backtick
/// after it the wrong way (451's plan.md:107, which opens with the close of a span begun on line 106 and names "a last `end` line").
fn names(text: &str, subject: &str) -> bool {
    if plain_word(subject) {
        return text.contains(&format!("`{subject}`"));
    }
    let word = |c: char| c.is_alphanumeric() || c == '_' || c == '-';
    let (starts, ends) = (subject.starts_with(word), subject.ends_with(word));
    text.match_indices(subject).any(|(i, _)| {
        let prefixed = starts && text[..i].chars().next_back().is_some_and(word);
        let suffixed = ends && text[i + subject.len()..].chars().next().is_some_and(word);
        !prefixed && !suffixed
    })
}

/// `(old line, new line, the old line's words the change touched)` for each line the change REPLACED; pure insertions and deletions
/// pair with nothing.
fn changed_pairs(old: &str, new: &str) -> Vec<(String, String, String)> {
    let (a, b) = (py_lines(old), py_lines(new));
    let mut out = Vec::new();
    for (tag, i1, i2, j1, j2) in opcodes(&a, &b) {
        if tag == Tag::Replace {
            out.extend(
                a[i1..i2]
                    .iter()
                    .zip(&b[j1..j2])
                    .zip(touched(&a[i1..i2], &b[j1..j2]))
                    .map(|((x, y), t)| ((*x).to_owned(), (*y).to_owned(), t)),
            );
        }
    }
    out
}

/// For each line of a replaced passage, the words of it the change TOUCHED (451 T73): the passage read word by word, old against new,
/// every word but one kept in place with both its neighbors. A word re-wrapped onto the next line keeps them, so it is no old value
/// (451's `tasks`, `names` and `plan`: 12 of the 28 candidates T54 left, measured 2026-11-21 over the reconstructions at its
/// snapshot and refusal); a word the rewrite kept in a rewritten clause does not, so the contract's "D5's `end` line of code 0" and
/// plan.md:329's "`end` with code 1 ... count as rework", both since restated, are still caught by `code`, which the new passage writes
/// too ("code 0, or 3 ...", "whatever its code"), where the values read from the whole passage lost them. Which neighbors count is
/// a CONVENTION: a word is a run of non-space characters, its neighbors the next word either side, and the passage's two ends count as
/// kept, since the lines beyond them are unchanged.
///
/// ACCEPTED, with its cost: over the guard log's 82 reconstructed refusals this drops 54 of 299 candidates and 4 of 57 refusals, and
/// with them two lines a session revised that the line-by-line reading had caught by coincidence: 261's copse row (spec.md:273) and
/// 316's label list (plan.md:65, edited 15 s after its refusal, so maybe already in hand). Each was stale by an omission, the new
/// passage's words inserted before a sentence it kept whole, and carried no word the change touched. Priced: the values read from the
/// whole passage (451 at 6, losing the contract's catch) and a line carrying two or more re-wrapped words kept (16 of the 54 back, 15
/// of them wrong fires, 261's the one right one), measured 2026-11-21. Chosen by 451 T73's builder, for the launcher's ruling.
fn touched(old: &[&str], new: &[&str]) -> Vec<String> {
    let (a, b) = (passage_words(old), passage_words(new));
    let (at, bt): (Vec<&str>, Vec<&str>) = (
        a.iter().map(|w| w.1).collect(),
        b.iter().map(|w| w.1).collect(),
    );
    let mut kept = vec![false; a.len()];
    for (tag, i1, i2, _, _) in opcodes(&at, &bt) {
        if tag == Tag::Equal && i2 > i1 + 1 {
            kept[i1 + 1..i2 - 1].fill(true);
        }
    }
    let mut out = vec![String::new(); old.len()];
    for ((line, word), _) in a.iter().zip(&kept).filter(|(w, k)| !**k && w.0 < old.len()) {
        out[*line].push_str(word);
        out[*line].push(' ');
    }
    out
}

/// `(line index, word)` of a passage between two empty ends, which stand for the unchanged lines around it (`usize::MAX` their index).
fn passage_words<'a>(block: &[&'a str]) -> Vec<(usize, &'a str)> {
    let mut out = vec![(usize::MAX, "")];
    for (i, line) in block.iter().enumerate() {
        out.extend(line.split_whitespace().map(|w| (i, w)));
    }
    out.push((usize::MAX, ""));
    out
}

/// For each line of `new` the change REPLACED (1-based), the whole old block it replaced (feature 442: a 3-line passage rewritten as 5).
fn rewritten_from(old: Option<&String>, new: &str) -> HashMap<usize, String> {
    let Some(old) = old else {
        return HashMap::new();
    };
    let (a, b) = (py_lines(old), py_lines(new));
    let mut out = HashMap::new();
    for (tag, i1, i2, j1, j2) in opcodes(&a, &b) {
        if tag == Tag::Replace {
            let block = a[i1..i2].join("\n");
            out.extend((j1..j2).map(|k| (k + 1, block.clone())));
        }
    }
    out
}

/// A file no candidate may come from: a skipped name or a skipped directory.
fn skipped(name: &str) -> bool {
    let path = Path::new(name);
    let last = path.file_name().unwrap_or_default().to_string_lossy();
    SKIP_NAMES.contains(&last.as_ref())
        || path
            .parent()
            .is_some_and(|p| p.iter().any(|c| c == SKIP_DIR))
}

/// `(line number, line)` of `text` that may be a candidate: none of a skipped file, none of the Review history, no task's dated `verify:` note.
fn watched_lines<'a>(name: &str, text: &'a str) -> Vec<(usize, &'a str)> {
    if skipped(name) {
        return Vec::new();
    }
    let (mut out, mut history) = (Vec::new(), false);
    for (i, line) in py_lines(text).into_iter().enumerate() {
        if line.starts_with("## ") {
            history = line.trim().to_lowercase().starts_with("## review history");
        }
        if !history && !line.trim_start().starts_with("verify:") {
            out.push((i + 1, line));
        }
    }
    out
}

/// Every line of `new` that names a changed line's subject and still carries its old value.
pub fn stale_candidates(old: &Files, new: &Files) -> Vec<Candidate> {
    let wrote: HashMap<&String, HashMap<usize, String>> = new
        .iter()
        .map(|(n, t)| (n, rewritten_from(old.get(n), t)))
        .collect();
    let mut seen: HashSet<(String, usize)> = HashSet::new();
    let mut found = Vec::new();
    for (name, new_text) in new {
        let Some(before) = old.get(name).filter(|_| !skipped(name)) else {
            continue;
        };
        for (old_line, new_line, changed) in changed_pairs(before, new_text) {
            let subj: BTreeSet<String> = subjects(&old_line)
                .intersection(&subjects(&new_line))
                .cloned()
                .collect();
            let mut gone: BTreeSet<String> = tokens(&changed)
                .difference(&tokens(&new_line))
                .cloned()
                .collect();
            for s in &subj {
                gone = gone.difference(&tokens_all(s)).cloned().collect();
            }
            if subj.is_empty() || gone.is_empty() {
                continue;
            }
            for (other, text) in new {
                for (n, line) in watched_lines(other, text) {
                    if line == new_line || seen.contains(&(other.clone(), n)) {
                        continue;
                    }
                    let hit = subj.iter().find(|s| names(line, s));
                    // A line this change rewrote from one that wrote the subject's word in ANY form was revisited on purpose: `names`
                    // here adds 274's "Only three named kinds ... the split" rewritten as "four ... `split`" and no real catch, measured
                    // 2026-11-21 over the 82 refusals of the guard log reconstructed from commits (451 T54).
                    if hit.is_some_and(|s| {
                        wrote[other].get(&n).is_some_and(|b| b.contains(s.as_str()))
                    }) {
                        continue;
                    }
                    let values: Vec<String> = gone.intersection(&tokens(line)).cloned().collect();
                    let Some(subject) = hit.filter(|_| !values.is_empty()) else {
                        continue;
                    };
                    seen.insert((other.clone(), n));
                    found.push(Candidate {
                        file: other.clone(),
                        line: n,
                        subject: subject.clone(),
                        old_values: values,
                        text: first_chars(line.trim(), 200),
                        changed_in: name.clone(),
                        changed_to: first_chars(new_line.trim(), 160),
                        criterion: false,
                    });
                }
            }
        }
    }
    found
}

/// A subject's own words, COMMON ones included: they are never an old value.
fn tokens_all(line: &str) -> BTreeSet<String> {
    TOKEN
        .find_iter(line)
        .map_while(Result::ok)
        .map(|m| m.as_str().to_lowercase())
        .collect()
}

/// `{id: (line number, the item's whole text, its cited list)}`.
fn items(text: &str, pattern: &Regex) -> BTreeMap<String, (usize, String, String)> {
    let lines = py_lines(text);
    let mut out = BTreeMap::new();
    for (i, line) in lines.iter().enumerate() {
        if let Ok(Some(c)) = pattern.captures(line) {
            let more = lines[i + 1..]
                .iter()
                .take_while(|m| m.starts_with("  ") && !m.trim_start().starts_with("- **"));
            let body: Vec<&str> = std::iter::once(*line).chain(more.copied()).collect();
            out.insert(
                c[1].to_owned(),
                (
                    i + 1,
                    body.join("\n"),
                    c.get(2).map_or("", |m| m.as_str()).to_owned(),
                ),
            );
        }
    }
    out
}

/// Each success criterion that cites a requirement the change REWROTE and was not itself touched (feature 442).
pub fn criteria_left_behind(old: &Files, new: &Files) -> Vec<Candidate> {
    let mut found = Vec::new();
    for (name, text) in new {
        let Some(before) = old
            .get(name)
            .filter(|_| Path::new(name).file_name().is_some_and(|n| n == "spec.md"))
        else {
            continue;
        };
        let (old_req, new_req) = (items(before, &REQ), items(text, &REQ));
        let rewritten: BTreeSet<&String> = new_req
            .iter()
            .filter(|(k, v)| old_req.get(*k).is_some_and(|o| o.1 != v.1))
            .map(|(k, _)| k)
            .collect();
        let old_crit = items(before, &CRIT);
        for (sc, (n, body, cites)) in items(text, &CRIT) {
            let cited: BTreeSet<String> = FR
                .find_iter(&cites)
                .map_while(Result::ok)
                .map(|m| m.as_str().to_owned())
                .filter(|f| rewritten.contains(f))
                .collect();
            let Some(first) = cited
                .iter()
                .next()
                .cloned()
                .filter(|_| old_crit.get(&sc).is_some_and(|o| o.1 == body))
            else {
                continue;
            };
            found.push(Candidate {
                file: name.clone(),
                line: n,
                subject: sc,
                old_values: cited.into_iter().collect(),
                text: first_chars(body.split('\n').next().unwrap_or("").trim(), 200),
                changed_in: name.clone(),
                changed_to: format!(
                    "{first} rewritten; this criterion untouched - does it still measure it?"
                ),
                criterion: true,
            });
        }
    }
    found
}

pub fn render(found: &[Candidate]) -> String {
    if found.is_empty() {
        return "stale-terms: no candidate - no line names a changed line's subject and still carries its old value".to_owned();
    }
    let mut out = format!("stale-terms: {} candidate(s) - each names a subject whose value CHANGED and still carries the old value:", found.len());
    for c in found.iter().take(25) {
        let values = c
            .old_values
            .iter()
            .take(4)
            .cloned()
            .collect::<Vec<_>>()
            .join(", ");
        if c.criterion {
            let _ = write!(out, "\n  {}:{}  `{}` cites {values}, which the change rewrote - the criterion was not touched\n      {}", c.file, c.line, c.subject, c.text);
        } else {
            let _ = write!(
                out,
                "\n  {}:{}  `{}` still with {values}\n      {}\n      (changed in {} to: {})",
                c.file, c.line, c.subject, c.text, c.changed_in, c.changed_to
            );
        }
    }
    if found.len() > 25 {
        let _ = write!(out, "\n  ... and {} more", found.len() - 25);
    }
    out
}

/// Every text file under `root`, under a million bytes, `__pycache__` aside.
fn read_dir(root: &Path) -> Files {
    let (mut out, mut todo) = (Files::new(), vec![root.to_path_buf()]);
    while let Some(dir) = todo.pop() {
        for path in std::fs::read_dir(&dir)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
        {
            if path.is_dir() {
                if path.file_name().is_some_and(|n| n != "__pycache__") {
                    todo.push(path);
                }
            } else if std::fs::metadata(&path).is_ok_and(|m| m.len() < 1_000_000) {
                if let Some(text) = std::fs::read(&path)
                    .ok()
                    .and_then(|b| String::from_utf8(b).ok())
                {
                    out.insert(
                        path.strip_prefix(root)
                            .unwrap_or(&path)
                            .display()
                            .to_string(),
                        text,
                    );
                }
            }
        }
    }
    out
}

/// The feature directory's text files as they stood at a git ref.
fn read_ref(clone: &Path, reference: &str, feature: &str) -> Files {
    let base = format!("specs/{feature}/");
    let names = crate::cohort::git(
        clone,
        &["ls-tree", "-r", "--name-only", reference, "--", &base],
    )
    .1;
    let mut out = Files::new();
    for full in names.split_whitespace() {
        let shown = Command::new("git")
            .arg("-C")
            .arg(clone)
            .args(["show", &format!("{reference}:{full}")])
            .output();
        if let Some(text) = shown.ok().and_then(|o| String::from_utf8(o.stdout).ok()) {
            out.insert(full[base.len()..].to_owned(), text);
        }
    }
    out
}

fn all_found(old: &Files, new: &Files) -> Vec<Candidate> {
    let mut found = stale_candidates(old, new);
    found.extend(criteria_left_behind(old, new));
    found
}

fn feature_dir(clone: &Path, feature: &str) -> Option<PathBuf> {
    let exact = clone.join("specs").join(feature);
    if exact.is_dir() {
        return Some(exact);
    }
    let mut all: Vec<PathBuf> = std::fs::read_dir(clone.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    all.retain(|p| {
        p.file_name()
            .is_some_and(|n| n.to_string_lossy().starts_with(feature))
    });
    all.sort();
    all.into_iter().next()
}

fn refused(words: &str) -> Reply {
    reply(String::new(), format!("stale-terms: {words}\n"), 2)
}

/// `record stale-terms <feature> [--clone DIR] [--against REF]`: exit 1 with candidates, as a search that found something.
pub fn cli(args: &[String]) -> Reply {
    let flag = |name: &str| {
        args.windows(2)
            .find(|w| w[0] == name)
            .map(|w| w[1].as_str())
    };
    let (clone_given, against) = (
        flag("--clone").unwrap_or("."),
        flag("--against").unwrap_or(""),
    );
    let Some(feature) = args.first().filter(|a| !a.starts_with("--")) else {
        return refused("name the feature directory under specs/");
    };
    let clone = std::fs::canonicalize(clone_given).unwrap_or_else(|_| PathBuf::from(clone_given));
    let Some(dir) = feature_dir(&clone, feature) else {
        return refused(&format!("no feature directory matches specs/{feature}*"));
    };
    let name = dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let snap = clone.join(".git/review-round").join(&name).join("snapshot");
    let old = if !against.is_empty() {
        read_ref(&clone, against, &name)
    } else if snap.is_dir() {
        read_dir(&snap)
    } else {
        return refused(&format!("no snapshot of {name} (no review round was dispatched yet) - name a ref with --against"));
    };
    let found = all_found(&old, &read_dir(&dir));
    reply(
        render(&found) + "\n",
        String::new(),
        i32::from(!found.is_empty()),
    )
}

/// `record stale-dirs <old dir> <new dir>`: the review-round guard's question: the count and the rendered candidates, or nothing.
pub fn dirs_cli(args: &[String]) -> Reply {
    let [old, new] = args else {
        return refused("usage: l7r-gate record stale-dirs <old dir> <new dir>");
    };
    let found = all_found(&read_dir(Path::new(old)), &read_dir(Path::new(new)));
    let out = if found.is_empty() {
        String::new()
    } else {
        format!("{}\n{}\n", found.len(), render(&found))
    };
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
