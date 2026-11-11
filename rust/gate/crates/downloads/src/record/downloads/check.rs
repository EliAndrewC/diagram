//! What the push refuses in the canonical list against main's (feature 313 plan D11), each naming its entry and the fix, and the self-test the push runs on it.

use std::collections::{BTreeMap, HashSet};
use std::path::Path;

use super::ingest::universal;
use super::parse::{entries, parse, render, Entry, Marks};
use super::read;
use super::CANON;
use crate::cohort::git;
use crate::Reply;

fn number(id: &str) -> u64 {
    id.parse().unwrap_or(0)
}

/// What the push refuses (plan D11).
pub(super) fn problems(old_text: Option<&str>, new_text: &str) -> Vec<String> {
    let new_blocks = parse(new_text);
    let new: Vec<&Entry> = entries(&new_blocks).collect();
    let ids: Vec<&str> = new.iter().map(|e| e.id.as_str()).collect();
    let mut seen: BTreeMap<&str, usize> = BTreeMap::new();
    for id in &ids {
        *seen.entry(id).or_insert(0) += 1;
    }
    let mut out: Vec<String> = seen
        .iter()
        .filter(|(_, n)| **n > 1)
        .map(|(id, _)| format!("entry {id} appears twice - an id is never reused; give the second its own with `make download-add`"))
        .collect();
    out.extend(new.iter().filter(|e| e.marks.is_none()).map(|e| format!("entry {} has no mark lines under its heading - the GM ticks them; `make download-add` writes them, or copy them from any entry", e.id)));
    let Some(old_text) = old_text else {
        return out;
    };
    let old_blocks = parse(old_text);
    let old_ids: Vec<&str> = entries(&old_blocks).map(|e| e.id.as_str()).collect();
    let old: HashSet<&str> = old_ids.iter().copied().collect();
    let current: HashSet<&str> = ids.iter().copied().collect();
    let lost: Vec<&str> = old_ids
        .iter()
        .copied()
        .filter(|i| !current.contains(i))
        .collect();
    if !lost.is_empty() {
        out.push(format!(
            "entries {} are gone - an entry is never removed; the GM's marks say when one is done",
            lost.join(", ")
        ));
    }
    let kept: Vec<&str> = ids.iter().copied().filter(|i| old.contains(i)).collect();
    let was: Vec<&str> = old_ids
        .iter()
        .copied()
        .filter(|i| current.contains(i))
        .collect();
    if kept != was {
        out.push(
            "entries are reordered against main - nothing is moved; new entries go at the end"
                .to_owned(),
        );
    }
    let tail_start = ids.iter().rposition(|i| old.contains(i));
    let top = old_ids
        .iter()
        .filter(|i| !i.starts_with('H'))
        .map(|i| number(i))
        .max()
        .unwrap_or(0);
    for id in ids.iter().filter(|i| !old.contains(*i)) {
        let first = ids.iter().position(|i| i == id);
        if id.starts_with('H') || first < tail_start || number(id) <= top {
            out.push(format!("entry {id} is not appended at the end under a new number - `make download-add FILE=<draft>` appends it"));
        }
    }
    out
}

pub(super) fn check(root: &Path, base: &str) -> Vec<String> {
    let path = root.join(CANON);
    if !path.is_file() {
        return Vec::new();
    }
    let done = git(root, &["show", &format!("{base}:{CANON}")]);
    let old = done.0.then(|| universal(&done.1));
    problems(old.as_deref(), &read(&path).unwrap_or_default())
}

/// Each named self-test that failed; empty when all pass.
pub(super) fn selftest_failures() -> Vec<&'static str> {
    let blank = Marks::default().lines().join("\n");
    let one = format!("# T\n\n### 1. A\n\n{blank}\n\n- body\n");
    let two = format!("{one}### 2. B\n\n{blank}\n\n- b\n");
    let swapped = format!("# T\n\n### 2. B\n\n{blank}\n\n- b\n\n### 1. A\n\n{blank}\n\n- body\n");
    let says = |found: Vec<String>, word: &str| found.iter().any(|p| p.contains(word));
    let elsewhere = Marks {
        elsewhere: true,
        ..Marks::default()
    };
    let contradiction = Marks {
        not_found: true,
        paywalled: true,
        ..Marks::default()
    };
    let fine = Marks {
        partial: true,
        paywalled: true,
        ..Marks::default()
    };
    failing(&[
        (
            render(&parse(&two)) == two,
            "parse and render are an identity",
        ),
        (
            problems(Some(&one), &two).is_empty(),
            "an entry appended at the end passes",
        ),
        (
            says(problems(Some(&two), &one), "gone"),
            "a removed entry is refused",
        ),
        (
            says(problems(Some(&two), &swapped), "reordered"),
            "a reorder is refused",
        ),
        (
            says(
                problems(Some(&one), &format!("{one}### 3. C\n\n- c\n")),
                "no mark lines",
            ),
            "an entry without marks is refused",
        ),
        (
            !elsewhere.problem().is_empty()
                && !contradiction.problem().is_empty()
                && fine.problem().is_empty(),
            "contradictory marks are named",
        ),
    ])
}

/// The names of the rows that did not hold.
pub(super) fn failing(rows: &[(bool, &'static str)]) -> Vec<&'static str> {
    rows.iter()
        .filter(|(ok, _)| !ok)
        .map(|(_, what)| *what)
        .collect()
}

/// The self-test's reply: silent on a pass, naming each failure otherwise.
pub(super) fn selftest(failed: &[&str]) -> Reply {
    let lines: Vec<String> = failed
        .iter()
        .map(|f| format!("downloads selftest: {f}\n"))
        .collect();
    let stderr = lines.concat();
    Reply {
        stdout: String::new(),
        code: i32::from(!failed.is_empty()),
        stderr,
    }
}
