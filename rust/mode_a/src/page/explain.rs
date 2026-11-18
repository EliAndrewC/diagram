//! The page's embedded data: one entry per present class and the glossary its words use (`page.explanations`, `rendered_text`,
//! `glossary_for`, features 134, 156, 180, 224, 319; ported by feature 449 T150).
//!
//! NO LABEL, NO LEAD, NO CAVEAT (feature 319): the classification is per statement in the modal's own text (`dev/modals.md` M11-M13) -
//! don't re-add a lead sentence, because a "This is a guess" opening on a modal that is mostly record read as the whole modal being a guess
//! (the GM, 2026-10-03: *"extremely misleading"*).
//!
//! Research:
//!     the modal's data - NONE: what each present class's modal carries, read from its registry entry, its conditions and the record

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use l7r_gate_registry::about::FeatureClass;
use l7r_gate_registry::conditions;
use l7r_gate_research::glossary::Term;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use serde_json::{json, Map, Value};

use super::{on_this_map, stub};
use crate::notes::MapNotes;
use crate::tags::PLACE;

/// The keys of an entry that are NOT reader-facing words: the cursor flag, the sibling KEYS and the questions - a DENY list, never an allow
/// list (feature 319: an allow list of five keys missed the About form's `about` and `guesses`).
///
/// Research: plumbing - NONE
pub const NOT_RENDERED: [&str; 3] = ["plain", "siblings", "questions"];

/// The questions behind an entry, as the page carries them: `{"text", "url"}` each.
fn questions(entry: &str, research: &Path) -> Value {
    for file in l7r_gate_research::sources::entry_fragments(entry) {
        crate::reads::note(
            &research
                .join(l7r_gate_research::sources::QUESTIONS)
                .join(file),
        );
    }
    Value::Array(
        l7r_gate_research::sources::research_questions(entry, research)
            .into_iter()
            .map(|q| json!({"text": q.text, "url": q.url}))
            .collect(),
    )
}

/// An entry line, its conditions applied where it carries any (`shown_entry(...) if entry_conditions(...) else ...`).
fn entry_shown(entry: &str, meta: &Map<String, Value>) -> Result<String, Error> {
    if conditions::entry_conditions(entry)?.is_empty() {
        Ok(entry.to_owned())
    } else {
        conditions::shown_entry(entry, meta)
    }
}

/// One present class's entry: its About, Guesses and Depiction items its conditions keep, the questions its entry names (feature 180,
/// read from the record), its siblings present, this map's own sentence (feature 156) and the cursor flag.
fn entry_of(
    tree: &Path,
    fc: &FeatureClass,
    present: &BTreeSet<String>,
    notes: &MapNotes,
    meta: &Map<String, Value>,
    plain: &[String],
) -> Result<Value, Error> {
    let mut conds = Vec::new();
    for item in fc.about.iter().chain(&fc.depiction).chain(&fc.guesses) {
        conds.push(conditions::split(item)?.0);
    }
    conds.extend(
        conditions::entry_conditions(&fc.entry)?
            .into_iter()
            .map(|(_, c)| Some(c)),
    );
    conds.extend(
        conditions::entry_conditions(&fc.drawing)?
            .into_iter()
            .map(|(_, c)| Some(c)),
    );
    // the knobs a condition is checked against: `knobs.json` (which the Python read by `pathlib`, past the cache's spy - noted here, the
    // safe direction) and the choices table
    crate::reads::note(&tree.join(conditions::KNOBS_FILE));
    crate::reads::note(&tree.join(l7r_gate_registry::choices::TABLE));
    conditions::check(tree, &fc.name, &conds)?;
    let entry = entry_shown(&fc.entry, meta)?;
    let research = tree.join("research");
    let drawing = if fc.drawing.is_empty() {
        json!([])
    } else {
        questions(&entry_shown(&fc.drawing, meta)?, &research)
    };
    Ok(json!({
        "name": fc.name,
        "about": conditions::shown(&fc.about, meta)?,
        "guesses": conditions::shown(&fc.guesses, meta)?,
        "depiction": conditions::shown(&fc.depiction, meta)?,
        "drawing": drawing,
        "questions": questions(&entry, &research),
        "siblings": fc.siblings.iter().map(|(k, _)| k).filter(|k| present.contains(*k)).collect::<Vec<_>>(),
        "on_this_map": on_this_map(notes, &fc.key),
        "plain": plain.contains(&fc.key),
    }))
}

/// The embedded data (`page.explanations`): one entry per present class in the registry's order, with only the siblings also present; a
/// present key the registry does not know gets a stub that says so. The knob-conditioned items (FR-015) are kept only where `meta`
/// records their value, and every condition is checked against the knob registry.
///
/// # Errors
/// A malformed or unknown condition, or the tables unreadable.
///
/// Research: what a modal carries - CONVENTION: only the classes present and only the siblings present (spec US4), an item kept only where the map records its knob's value (FR-015), the questions read from the record (feature 180), no lead or label (feature 319)
pub fn explanations(
    tree: &Path,
    present: &BTreeSet<String>,
    notes: &MapNotes,
    registry: &[FeatureClass],
    meta: &Map<String, Value>,
) -> Result<Map<String, Value>, Error> {
    let plain = super::plain_cursor(tree)?;
    let mut out = Map::new();
    for fc in registry {
        if present.contains(&fc.key) {
            out.insert(
                fc.key.clone(),
                entry_of(tree, fc, present, notes, meta, &plain)?,
            );
        }
    }
    for key in present {
        if key != PLACE && !registry.iter().any(|fc| fc.key == *key) {
            out.insert(key.clone(), stub(key));
        }
    }
    Ok(out)
}

/// Every word an entry shows its reader, whatever key it rides on: strings, and the strings inside lists.
///
/// Research: plumbing - NONE
#[must_use]
pub fn rendered_text(entry: &Map<String, Value>) -> String {
    let mut parts: Vec<&str> = Vec::new();
    for (key, value) in entry {
        if NOT_RENDERED.contains(&key.as_str()) {
            continue;
        }
        match value {
            Value::String(s) => parts.push(s),
            Value::Array(items) => parts.extend(items.iter().filter_map(Value::as_str)),
            _ => {}
        }
    }
    parts.join(" ")
}

/// Python's `\w`: a letter, a number or the underscore (`pyre::WORD`).
static WORD: LazyLock<fancy_regex::Regex> = LazyLock::new(|| py(r"\A\w\z"));

fn is_word(c: Option<char>) -> bool {
    c.is_some_and(|c| WORD.is_match(c.encode_utf8(&mut [0; 4])).unwrap_or(false))
}

/// Whether Python's `\b` holds at byte `at` of `hay`: a word character on one side and none on the other.
fn boundary(hay: &str, at: usize) -> bool {
    is_word(hay[..at].chars().next_back()) != is_word(hay[at..].chars().next())
}

/// Whether `needle` stands in `hay` as a whole word: `re.search(r"\b" + re.escape(needle) + r"\b", hay)` for the one form no automaton
/// takes, the empty needle - which stands at any boundary.
fn empty_word(hay: &str) -> bool {
    hay.char_indices()
        .map(|(i, _)| i)
        .chain([hay.len()])
        .any(|i| boundary(hay, i))
}

/// Which of `needles` stand in `hay` as whole words (`re.search(r"\b" + re.escape(v) + r"\b", hay)` for each): every place each stands
/// found in ONE pass, overlapping places among them as the search tries every start, and its boundaries tested there - a pattern compiled
/// per variant, then a substring search per variant, cost the page 6.9 and 0.35 s (feature 449 T150, observed 2026-11-18, method: the
/// page lockstep's cases timed, part A).
fn whole_words(hay: &str, needles: &[String]) -> Vec<bool> {
    let mut out: Vec<bool> = needles
        .iter()
        .map(|n| n.is_empty() && empty_word(hay))
        .collect();
    let mut unique: Vec<&str> = needles
        .iter()
        .map(String::as_str)
        .filter(|n| !n.is_empty())
        .collect();
    unique.sort_unstable();
    unique.dedup();
    // the automaton's only refusal is a size past its limits, which the glossary's few thousand words are far under
    let ac = aho_corasick::AhoCorasick::new(&unique).unwrap_or_else(|e| unreachable!("{e}"));
    let mut stands = vec![false; unique.len()];
    for m in ac.find_overlapping_iter(hay) {
        if boundary(hay, m.start()) && boundary(hay, m.end()) {
            stands[m.pattern().as_usize()] = true;
        }
    }
    for (n, o) in needles.iter().zip(&mut out) {
        if let Ok(k) = unique.binary_search(&n.as_str()) {
            *o = stands[k];
        }
    }
    out
}

/// The glossary entries whose terms occur in the present explanations (`page.glossary_for`), variants longest first so "head race" wins
/// over "head"; a cased term matched only as written. IT READS WHAT THE PAGE RENDERS ([`rendered_text`]) and nothing else.
///
/// Research: the page's glossary - CONVENTION: a term is defined only where the words the modals show use it as a whole word, a cased term only as written (feature 265)
#[must_use]
pub fn glossary_for(data: &Map<String, Value>, terms: &[Term]) -> Vec<Value> {
    let raw = data
        .values()
        .map(|d| d.as_object().map(rendered_text).unwrap_or_default())
        .collect::<Vec<_>>()
        .join(" ");
    let text = raw.to_lowercase();
    // a cased term's variants as written, over the text as written; every other's lower-cased, over the text lower-cased
    let (mut cased, mut folded) = (Vec::new(), Vec::new());
    for t in terms {
        for v in &t.variants {
            if t.cased {
                cased.push(v.clone());
            } else {
                folded.push(v.to_lowercase());
            }
        }
    }
    let (mut cased, mut folded) = (
        whole_words(&raw, &cased).into_iter(),
        whole_words(&text, &folded).into_iter(),
    );
    let mut out = Vec::new();
    for t in terms {
        let from = if t.cased { &mut cased } else { &mut folded };
        let found = from.by_ref().take(t.variants.len()).filter(|&b| b).count() > 0;
        if !found {
            continue;
        }
        let mut variants = t.variants.clone();
        variants.sort_by_key(|v| std::cmp::Reverse(v.chars().count()));
        let mut entry = json!({"term": t.term, "variants": variants, "def": t.definition});
        if t.cased {
            entry["cased"] = json!(true);
        }
        out.push(entry);
    }
    out
}

#[cfg(test)]
mod tests {
    #[test]
    fn a_word_stands_where_its_boundaries_do() {
        let words = |hay: &str, n: &[&str]| {
            super::whole_words(hay, &n.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>())
        };
        assert_eq!(
            words("a bund here", &["bund", "bun", "", "here"]),
            [true, false, true, true]
        );
        assert_eq!(words("", &[""]), [false]);
        assert_eq!(words("-", &["", "-"]), [false, false]);
        assert_eq!(words("x-y", &["-"]), [true]);
        assert_eq!(words("x-", &["-"]), [false]);
        let entry = serde_json::json!({"a": 1, "b": "w"});
        assert_eq!(super::rendered_text(entry.as_object().unwrap()), "w");
    }
}
