//! A pop-up's Guesses bullets filled from the record's item tags (feature 451 T187; the GM 2026-11-23, request.md "the convergence
//! talk": *"Shouldn't attested versus guess be something that cascades mechanically rather than requiring a review, though?"*).
//!
//! A Guesses bullet may be a REFERENCE, `- {NNNN#<id>}` (a knob condition before it as on any bullet), naming an item tagged on question
//! NNNN's research or drawing page (`l7r_gate_research::record::items`). At build ([`resolve`], which every reader of a kind's modal
//! goes through: `about::feature` and `choices::modal`) it becomes the tag's own bullet while the tag says GUESS, and is dropped while it
//! says anything else. So a relabel is one edit on the page: the pop-up's file is unchanged and owes nothing, and its Guesses tab follows.
//!
//! [`restated`] is the check that keeps the About honest beside it: a GUESS-tagged item of a page the pop-up cites, its bullet's head
//! (the words before the first `: `) appearing in an About sentence that does not call it a guess, states a guess as a fact.

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::record::items::{items, Item};
use l7r_gate_research::{Error, Result};

use crate::about::FeatureClass;

/// The record's questions, from the tree's root.
pub const QUESTIONS: &str = "research/questions";

static REFERENCE: LazyLock<Regex> =
    LazyLock::new(|| py(r"^((?:\[[a-z_]+=[^\]]*\]\s*)*)\{(\d{4})#([a-z0-9-]+)\}\s*$"));
static PAGE: LazyLock<Regex> =
    LazyLock::new(|| py(r"research/questions/(\d{4})-[a-z0-9-]+?(?:\.drawing)?\.html"));
static SENTENCE: LazyLock<Regex> = LazyLock::new(|| py(r"(?<=[.!?])\s+"));

/// A question's research and drawing pages, read once per question.
#[derive(Default)]
pub struct Pages {
    read: HashMap<String, Vec<Item>>,
}

fn question_files(tree: &Path, number: &str) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(tree.join(QUESTIONS))
        .into_iter()
        .flatten()
        .map_while(std::io::Result::ok)
        .map(|e| e.path())
        .filter(|p| {
            let n = p
                .file_name()
                .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
            n.starts_with(&format!("{number}-"))
                && (n.ends_with(".drawing.html") || !n.trim_end_matches(".html").contains('.'))
        })
        .collect();
    out.sort();
    out
}

impl Pages {
    /// Every tagged item of question `number`'s two pages.
    pub fn of(&mut self, tree: &Path, number: &str) -> &[Item] {
        self.read.entry(number.to_owned()).or_insert_with(|| {
            question_files(tree, number)
                .iter()
                .filter_map(|p| std::fs::read_to_string(p).ok())
                .flat_map(|t| items(&t))
                .collect()
        })
    }
}

/// The kind's class with each reference bullet filled from its tag, or dropped while the tag is no GUESS.
///
/// # Errors
/// A reference naming an item no page of its question tags.
pub fn resolve(tree: &Path, mut fc: FeatureClass) -> Result<FeatureClass> {
    fc.guesses = bullets(tree, &fc.key, std::mem::take(&mut fc.guesses))?;
    Ok(fc)
}

/// Guesses bullets (each without its `- `) with each reference filled from its tag, or dropped while the tag is no GUESS: what
/// [`resolve`] does to a kind's, and what a modal check's bundle shows its agent (`l7r_gate_bundle`'s modal bundle).
///
/// # Errors
/// A reference naming an item no page of its question tags.
pub fn bullets(tree: &Path, key: &str, guesses: Vec<String>) -> Result<Vec<String>> {
    let mut pages = Pages::default();
    let mut out = Vec::new();
    for bullet in guesses {
        let Ok(Some(c)) = REFERENCE.captures(&bullet) else {
            out.push(bullet);
            continue;
        };
        let (cond, number, id) = (&c[1], &c[2], &c[3]);
        let Some(item) = pages.of(tree, number).iter().find(|i| i.id == id) else {
            return Err(Error::new(
                "ValueError",
                format!("{key}: the Guesses bullet {{{number}#{id}}} names no item: tag it on question {number}'s page (`<span class=\"item\" data-item=\"{id}\" data-label=\"...\" data-guess=\"...\"></span>`, research/questions/NNNN-*.drawing.html) or fix the reference"),
            ));
        };
        if item.label == "GUESS" {
            out.push(format!("{cond}{}", item.guess));
        }
    }
    Ok(out)
}

/// The head of a bullet: its words before the first `: `, lowercased, a leading "that " dropped.
fn head(guess: &str) -> String {
    let h = guess
        .split(": ")
        .next()
        .unwrap_or_default()
        .trim()
        .to_lowercase();
    h.strip_prefix("that ").unwrap_or(&h).to_owned()
}

/// Every About sentence of the kind that states a GUESS-tagged item of a page it cites without calling it a guess.
#[must_use]
pub fn restated(tree: &Path, fc: &FeatureClass, pages: &mut Pages) -> Vec<String> {
    let mut numbers: Vec<String> = PAGE
        .captures_iter(&format!("{} {}", fc.entry, fc.drawing))
        .map_while(std::result::Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    numbers.sort();
    numbers.dedup();
    let sentences: Vec<String> = fc
        .about
        .iter()
        .flat_map(|p| {
            SENTENCE
                .split(p)
                .map_while(std::result::Result::ok)
                .map(str::to_owned)
                .collect::<Vec<_>>()
        })
        .collect();
    let mut out = Vec::new();
    for n in numbers {
        for it in pages.of(tree, &n).iter().filter(|i| i.label == "GUESS") {
            let phrase = head(&it.guess);
            if phrase.split_whitespace().count() < 3 {
                continue;
            }
            for s in &sentences {
                let low = s.to_lowercase();
                if low.contains(&phrase) && !low.contains("guess") {
                    out.push(format!(
                        "{}: its About states {n}#{} (\"{phrase}\"), tagged a GUESS, as a fact - in \"{s}\": move it to Guesses as `- {{{n}#{}}}`, or say in the sentence that it is a guess",
                        fc.key, it.id, it.id
                    ));
                }
            }
        }
    }
    out
}

#[cfg(test)]
mod tests;
