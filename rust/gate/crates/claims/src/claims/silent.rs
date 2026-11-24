//! The record searched before a "the pages are silent" finding is filed (feature 451 T218).
//!
//! impl-drift judges from its bundle alone - the pages its claims cite - so "none of the cited pages says it" was filed where the
//! record does say it: feature 449's found row 210 (452 T22) said no page attests the kitchen door at the rear, and 0107, a page
//! the section did not cite, holds the sentence. A finding line that says the pages are silent is HELD - neither recorded nor
//! filed - until the record's nearest pages for its words are in the bundle; judged again with them there, a page that says it
//! makes the finding a citation fix or nothing, and a record that is truly silent files it after that one more reading. The
//! nearest pages are ranked by words alone and no score separates silent from said (measured 2026-11-24: the grave-marker size,
//! which no page gives, scores 0.60 on its nearest page; the kitchen row, which 0107 states, 0.31), so the rule is "read the
//! nearest three, then file", never a threshold.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::checks::pages::read_page;
use serde_json::{json, Map, Value};

use super::index::{load_map, save_store};
use super::reply::{bare, VERDICT};
use crate::record::repo::Fail;
use crate::record::units::re;

/// The searches the clone has asked for and not yet seen read: `{a claim's key, or an outside line's file: [pages]}`.
pub const SEARCHED: &str = ".git/claims-searched.json";
/// How many of the record's nearest pages a silent finding is read against.
pub const NEAREST: usize = 3;

/// A finding's own words for "the pages do not say it".
static SILENT: LazyLock<Regex> = LazyLock::new(|| {
    re(concat!(
        r"(?i)\bnone of the\b[^.;|]{0,40}\bpages?\b|\bno (?:cited )?page\b|\bsilent on\b|\bnot in the record\b",
        r"|\bpages?\b[^.;|]{0,60}\b(?:(?:do(?:es)? not|don't|doesn't|did not)\s+(?:say|give|attest|state|record|name|hold)",
        r"|gives? no\b|says? nothing|records? neither|(?:is|are) (?:only )?silent)",
        r"|\[§\]\s*\z",
    ))
});
static HEADING: LazyLock<Regex> =
    LazyLock::new(|| re(r"\A#*\s*\**OUTSIDE THE CHANGE\**\s*:?\s*\z"));
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[a-z]{4,}"));

/// Words too common in a finding's own voice to name its subject.
const STOP: &str = "page pages cited claim claims code says said does this that with from which where their there have been only \
    should would section block bundle finding effect none drifted mislabeled research needs verdict outside change label guess \
    drawing question questions html also than then them they into each such what when were will these those here about gives give \
    given names name named line lines note notes cite cites record recorded records silent sheet tool";

/// A text's subject words: lowercase runs of four letters or more, a plural's `s` dropped, the finding voice's own words out.
fn tokens(text: &str) -> BTreeSet<String> {
    let lower = text.to_lowercase();
    WORD.find_iter(&lower)
        .map_while(Result::ok)
        .map(|m| {
            let w = m.as_str();
            if w.len() > 4 {
                w.strip_suffix('s').unwrap_or(w)
            } else {
                w
            }
        })
        .filter(|w| !STOP.split_whitespace().any(|s| s == *w))
        .map(str::to_owned)
        .collect()
}

/// Every block of every question and drawing page under `qdir` as its subject words, by page: notes and originals are not pages.
fn corpus(qdir: &Path) -> Vec<(String, BTreeSet<String>)> {
    let mut names: Vec<String> = std::fs::read_dir(qdir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| {
            Path::new(n)
                .extension()
                .is_some_and(|e| e.eq_ignore_ascii_case("html"))
                && !n.contains(".notes.")
                && !n.contains(".originals.")
        })
        .collect();
    names.sort();
    let mut out = Vec::new();
    for n in names {
        let page = read_page(&std::fs::read_to_string(qdir.join(&n)).unwrap_or_default());
        out.push((n.clone(), tokens(&page.heading)));
        out.extend(page.blocks.iter().map(|b| (n.clone(), tokens(&b.words))));
    }
    out
}

/// The record's nearest pages for `words`, best first: each page scored by its best block, a block by the share of the words'
/// weight it holds, a word weighing more the fewer blocks hold it.
fn nearest(corpus: &[(String, BTreeSet<String>)], words: &str) -> Vec<String> {
    let mut df: HashMap<&str, f64> = HashMap::new();
    for (_, t) in corpus {
        for w in t {
            *df.entry(w).or_default() += 1.0;
        }
    }
    #[expect(
        clippy::cast_precision_loss,
        reason = "a count of blocks, far under 2^52"
    )]
    let n = corpus.len() as f64;
    let q = tokens(words);
    let mut best: BTreeMap<&str, f64> = BTreeMap::new();
    for (page, t) in corpus {
        let score: f64 = q
            .iter()
            .filter(|w| t.contains(*w))
            .map(|w| (n / df[w.as_str()]).ln())
            .sum();
        if score > best.get(page.as_str()).copied().unwrap_or(0.0) {
            best.insert(page, score);
        }
    }
    let mut ranked: Vec<(&str, f64)> = best.into_iter().collect();
    ranked.sort_by(|a, b| b.1.total_cmp(&a.1));
    ranked
        .into_iter()
        .take(NEAREST)
        .map(|(p, _)| p.to_owned())
        .collect()
}

/// (what its search is kept under, the words searched for) where `line` is a finding that says the pages are silent: a VERDICT
/// other than IN-STEP on a claim of the bundle - NEEDS-RESEARCH always, another where its note says so - or, when `outside`, a
/// line under OUTSIDE THE CHANGE that names its effect (one that names none is dropped unfiled, feature 451 T219).
fn silent(line: &str, outside: bool, units: &Map<String, Value>) -> Option<(String, String)> {
    if let Some(m) = VERDICT.captures(line).ok().flatten() {
        let key = m[1].trim_matches('`');
        let says = &m[2] == "NEEDS-RESEARCH" || SILENT.is_match(&m[3]).unwrap_or(false);
        let unit = units.get(key)?;
        return (&m[2] != "IN-STEP" && says).then(|| {
            let claim = unit.get("claim").and_then(Value::as_str).unwrap_or("");
            (key.to_owned(), format!("{claim} {}", &m[3]))
        });
    }
    let row = line.strip_prefix("- ")?;
    let (file, rest) = row.split_once('|')?;
    (outside
        && crate::record::effect::named(rest).is_some()
        && SILENT.is_match(rest).unwrap_or(false))
    .then(|| (file.trim().trim_matches('`').to_owned(), rest.to_owned()))
}

/// The reply without the lines held, and what each held line is told: a finding that says the pages are silent is held while one
/// of the record's nearest pages for its words (those of its last search, where one is kept in `searched`) is not among the
/// bundle's `questions`. A line whose pages are all there is recorded as written, and a kept search whose pages the bundle holds is
/// forgotten - whether its finding came back or the second reading dropped it.
pub fn hold(
    reply: &str,
    units: &Map<String, Value>,
    qdir: &Path,
    bundle: &Path,
    searched: &Path,
) -> Result<(String, Vec<String>), Fail> {
    let mut kept = load_map(searched)?;
    let before = kept.clone();
    let (mut keep, mut held, mut outside) = (Vec::new(), Vec::new(), false);
    let names_of = |v: &Value| -> Vec<String> {
        let list = v.as_array().into_iter().flatten();
        list.filter_map(|n| n.as_str().map(str::to_owned)).collect()
    };
    let here = |names: &[String]| -> Vec<String> {
        let absent = |n: &&String| !bundle.join("questions").join(format!("{n}.txt")).is_file();
        names.iter().filter(absent).cloned().collect()
    };
    let mut pages: Option<Vec<(String, BTreeSet<String>)>> = None;
    let mut wanted: BTreeSet<String> = BTreeSet::new();
    for raw in reply.split('\n') {
        let line = bare(raw);
        if line.starts_with('#') || HEADING.is_match(line).unwrap_or(false) {
            outside = HEADING.is_match(line).unwrap_or(false);
        }
        let Some((key, words)) = silent(line, outside, units) else {
            keep.push(raw);
            continue;
        };
        // a search already asked for answers the line once its pages are in the bundle, whatever the reply's new words rank
        let asked: Option<Vec<String>> =
            kept.get(&key).map(names_of).filter(|n| here(n).is_empty());
        let names = match asked {
            Some(was) => was,
            None => nearest(pages.get_or_insert_with(|| corpus(qdir)), &words),
        };
        let missing = here(&names);
        if missing.is_empty() {
            keep.push(raw);
            continue;
        }
        let cut: String = line.chars().take(160).collect();
        held.push(format!(
            "HELD line - it says the pages are silent, and the record's nearest pages for its words are not in the bundle ({}): {cut}",
            missing.join(", ")
        ));
        wanted.extend(names.iter().cloned());
        kept.insert(key, json!(names));
    }
    // a search whose pages this bundle holds is read: forgotten, whether its finding came back or was dropped
    kept.retain(|_, v| !here(&names_of(v)).is_empty());
    if kept != before {
        save_store(searched, &kept)?;
    }
    if !held.is_empty() {
        let keys: Vec<&str> = units.keys().map(String::as_str).collect();
        held.push(format!(
            "a held line is neither recorded nor filed (451 T218): judge the bundle again with those pages in it - make claims-bundle UNITS=\"{}\" PAGES=\"{}\" REASON=\"the record searched before a silent finding is filed\" - where a page says it, the finding is a citation fix or nothing; where none does, the line is recorded as written",
            keys.join(","),
            wanted.into_iter().collect::<Vec<_>>().join(",")
        ));
    }
    Ok((keep.join("\n"), held))
}

#[cfg(test)]
mod tests;
