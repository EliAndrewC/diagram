//! A pop-up's Guesses bullets filled from the record's item tags (feature 451 T187; the GM 2026-11-23, request.md "the convergence
//! talk": *"Shouldn't attested versus guess be something that cascades mechanically rather than requiring a review, though?"*).
//!
//! A Guesses bullet may be a REFERENCE, `- {NNNN#<id>}` (a knob condition before it as on any bullet), naming an item tagged on question
//! NNNN's research or drawing page (`l7r_gate_research::record::items`). At build ([`resolve`], which every reader of a kind's modal
//! goes through: `about::feature` and `choices::modal`) it becomes the tag's own bullet while the tag says GUESS, and is dropped while it
//! says anything else. So a relabel is one edit on the page: the pop-up's file is unchanged and owes nothing, and its Guesses tab follows.
//!
//! A reference's NNNN is the item's HOME, not a bond (451 T200, the gap audit's item 12b): an item moved to another question's page is
//! found there while exactly one other question tags its id, so moving a tagged item breaks no pop-up; two such questions make it
//! ambiguous, refused naming both. Every page read for a reference is told to the Mode A generation cache ([`take_read`], drained by
//! `l7r_mode_a::reads::take`, 451 T200 item 12d), so a relabel regenerates a cached sheet whose Guesses it fills.
//!
//! [`restated`] is the check that keeps the About honest beside it: a GUESS-tagged item of a page the pop-up cites, its bullet's head
//! (the words before the first `: `) appearing in an About sentence that does not call it a guess, states a guess as a fact.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::{Path, PathBuf};
use std::sync::{LazyLock, Mutex, PoisonError};

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::record::items::{items, Item, GUESSED};
use l7r_gate_research::{Error, Result};

use crate::about::FeatureClass;

/// The record's questions, from the tree's root.
pub const QUESTIONS: &str = "research/questions";

static REFERENCE: LazyLock<Regex> =
    LazyLock::new(|| py(r"^((?:\[[a-z_]+=[^\]]*\]\s*)*)\{(\d{4})#([a-z0-9-]+)\}\s*$"));
static PAGE: LazyLock<Regex> =
    LazyLock::new(|| py(r"research/questions/(\d{4})-[a-z0-9-]+?(?:\.drawing)?\.html"));
static SENTENCE: LazyLock<Regex> = LazyLock::new(|| py(r"(?<=[.!?])\s+"));

/// The question pages a reference read, since the last [`take_read`]: the Mode A page writer's reads for the generation cache.
static READ: LazyLock<Mutex<BTreeSet<PathBuf>>> = LazyLock::new(|| Mutex::new(BTreeSet::new()));

/// Every question page a reference read since the last call, the log emptied (`l7r_mode_a::reads::take` drains it into its own).
#[must_use]
pub fn take_read() -> Vec<PathBuf> {
    std::mem::take(&mut *READ.lock().unwrap_or_else(PoisonError::into_inner))
        .into_iter()
        .collect()
}

/// A question's research and drawing pages, read once per question.
#[derive(Default)]
pub struct Pages {
    read: HashMap<String, Vec<Item>>,
    /// every other question's tags, by number, read once and only where a reference missed its home
    all: Option<BTreeMap<String, Vec<(PathBuf, Item)>>>,
}

/// A research or drawing page of the record (not its notes page), by its file name.
fn is_page(name: &str) -> bool {
    name.ends_with(".drawing.html")
        || (Path::new(name).extension().is_some_and(|e| e == "html")
            && !name.trim_end_matches(".html").contains('.'))
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
            (number.is_empty() || n.starts_with(&format!("{number}-"))) && is_page(&n)
        })
        .collect();
    out.sort();
    out
}

fn tags_of(path: &Path) -> Vec<Item> {
    items(&std::fs::read_to_string(path).unwrap_or_default())
}

fn note(path: &Path) {
    READ.lock()
        .unwrap_or_else(PoisonError::into_inner)
        .insert(path.to_path_buf());
}

impl Pages {
    /// Every tagged item of question `number`'s two pages.
    pub fn of(&mut self, tree: &Path, number: &str) -> &[Item] {
        self.read.entry(number.to_owned()).or_insert_with(|| {
            question_files(tree, number)
                .iter()
                .inspect(|p| note(p))
                .flat_map(|p| tags_of(p))
                .collect()
        })
    }

    /// The item `{number#id}` names: on its home question's pages, else on the one other question whose pages tag `id` (451 T200).
    ///
    /// # Errors
    /// No question tags `id`, or several besides its home do: the message's tail, after the reference.
    pub fn locate(
        &mut self,
        tree: &Path,
        number: &str,
        id: &str,
    ) -> std::result::Result<Item, String> {
        if let Some(it) = self.of(tree, number).iter().find(|i| i.id == id) {
            return Ok(it.clone());
        }
        let all = self.all.get_or_insert_with(|| {
            let mut by: BTreeMap<String, Vec<(PathBuf, Item)>> = BTreeMap::new();
            for p in question_files(tree, "") {
                let n: String = p.file_name().map_or_else(String::new, |n| {
                    n.to_string_lossy().chars().take(4).collect()
                });
                by.entry(n)
                    .or_default()
                    .extend(tags_of(&p).into_iter().map(|i| (p.clone(), i)));
            }
            by
        });
        let found: Vec<(&String, &(PathBuf, Item))> = all
            .iter()
            .filter(|(n, _)| n.as_str() != number)
            .filter_map(|(n, tags)| tags.iter().find(|(_, i)| i.id == id).map(|t| (n, t)))
            .collect();
        match found.as_slice() {
            [(_, (path, it))] => {
                note(path);
                Ok(it.clone())
            }
            [] => Err(format!("names no item: tag it on question {number}'s page (`<span class=\"item\" data-item=\"{id}\" data-label=\"...\" data-guess=\"...\"></span>`, research/questions/NNNN-*.drawing.html) or fix the reference")),
            many => Err(format!(
                "names no item on question {number}'s pages, and questions {} each tag `{id}` - write the one meant, `{{{}#{id}}}`",
                many.iter().map(|(n, _)| n.as_str()).collect::<Vec<_>>().join(", "),
                many[0].0
            )),
        }
    }
}

/// The kind's class with each reference bullet filled from its tag, or dropped while the tag is no GUESS or UNRESEARCHED.
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
        let item = pages.locate(tree, number, id).map_err(|why| {
            Error::new(
                "ValueError",
                format!("{key}: the Guesses bullet {{{number}#{id}}} {why}"),
            )
        })?;
        if GUESSED.contains(&item.label.as_str()) {
            // the bullet is owed from the first reference (451 T192): an unreferenced GUESS tag may carry none; an UNRESEARCHED tag is
            // a guess to the reader as well (451 T236)
            if item.guess.trim().is_empty() {
                return Err(Error::new(
                    "ValueError",
                    format!("{key}: the Guesses bullet {{{number}#{id}}} names {} tag with no data-guess: add data-guess=\"<what is guessed>: <why no page says>\" to its tag, from its block's own words", a(&item.label)),
                ));
            }
            out.push(format!("{cond}{}", item.guess));
        }
    }
    Ok(out)
}

/// The label with its article, as a message names it: `a GUESS`, `an UNRESEARCHED`.
fn a(label: &str) -> String {
    let an = label.starts_with(['A', 'E', 'I', 'O', 'U']);
    format!("{} {label}", if an { "an" } else { "a" })
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
        for it in pages
            .of(tree, &n)
            .iter()
            .filter(|i| GUESSED.contains(&i.label.as_str()))
        {
            let phrase = head(&it.guess);
            if phrase.split_whitespace().count() < 3 {
                continue;
            }
            for s in &sentences {
                let low = s.to_lowercase();
                if low.contains(&phrase) && !low.contains("guess") {
                    out.push(format!(
                        "{}: its About states {n}#{} (\"{phrase}\"), tagged {}, as a fact - in \"{s}\": move it to Guesses as `- {{{n}#{}}}`, or say in the sentence that it is a guess",
                        fc.key, it.id, a(&it.label), it.id
                    ));
                }
            }
        }
    }
    out
}

#[cfg(test)]
mod tests;
