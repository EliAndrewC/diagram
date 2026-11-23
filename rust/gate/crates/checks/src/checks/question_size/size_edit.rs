//! A size edit never changes a claim (feature 451 T184; the GM 2026-11-23, request.md "the convergence talk": *"no edit to
//! maintain entry size should ever be substantive"*). The 2026-11-23 cuts of 0009 and 0059 under the cap (cce80ca436)
//! dropped a quantifier, a body's restatement of its source and a source's term; a page over its limit is split, never cut.
//!
//! A SIZE EDIT is a change to a page that was over its limit before it, or that the words it removed would put back over
//! it - the add-then-trim of one session included, which a test of "the page shrank" would miss. Of such an edit the
//! CLAIM-BEARING tokens of every block it changed must still stand: a number, a label, a quoted passage and a proper name
//! anywhere on the page or on a page it now links to (a split's new page), a negation or qualifier in the block itself (a
//! "not" or an "every" stands somewhere on any page, so page-wide it would excuse every cut).

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;

/// What makes a token claim-bearing.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub(super) enum Kind {
    Number,
    Label,
    Quote,
    Name,
    Qualifier,
}

impl Kind {
    pub(super) const fn word(self) -> &'static str {
        match self {
            Self::Number => "number",
            Self::Label => "label",
            Self::Quote => "quoted passage",
            Self::Name => "name",
            Self::Qualifier => "qualifier",
        }
    }
}

/// A claim-bearing token a changed block held that the page no longer does.
#[derive(Debug)]
pub(super) struct Lost {
    pub(super) block: String,
    pub(super) kind: Kind,
    pub(super) token: String,
}

/// The negations, quantifiers, frequencies and hedges whose loss changes what a sentence claims.
const QUALIFIERS: [&str; 35] = [
    "not",
    "no",
    "never",
    "none",
    "nor",
    "neither",
    "without",
    "only",
    "some",
    "most",
    "mostly",
    "many",
    "few",
    "all",
    "every",
    "each",
    "always",
    "usually",
    "often",
    "seldom",
    "rarely",
    "sometimes",
    "probably",
    "perhaps",
    "may",
    "might",
    "about",
    "nearly",
    "almost",
    "roughly",
    "largely",
    "chiefly",
    "mainly",
    "partly",
    "already",
];

fn re(pattern: &str) -> Regex {
    l7r_shared::regex::build(pattern).expect("a size-edit pattern")
}

static SUP: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<sup[^>]*>.*?</sup>|<!--.*?-->"));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<br>|<[^>]+>"));
static NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"\d[\d,.]*(?:-\d+)?"));
static LABEL: LazyLock<Regex> = LazyLock::new(|| {
    re(r"\b(?:GUESS|ATTESTED|attested|CONVENTION|UNRESEARCHED|inference|deliberate deviation)\b")
});
static QUOTE: LazyLock<Regex> = LazyLock::new(|| re(r#""[^"]{8,}"|“[^”]{8,}”|「[^」]{4,}」"#));
static EM: LazyLock<Regex> = LazyLock::new(|| re(r"<em>([^<]+)</em>"));
static NAME: LazyLock<Regex> = LazyLock::new(|| re(r"(?<=[a-z,;(] )[A-Z][A-Za-z-]+"));
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[a-z]+"));

fn all<'r, 't>(pattern: &'r Regex, text: &'t str) -> impl Iterator<Item = &'t str> + use<'r, 't> {
    pattern
        .find_iter(text)
        .map_while(Result::ok)
        .map(|m| m.as_str())
}

/// A block's words as a reader meets them: no footnote marks, comments or tags.
pub(super) fn text(block: &str) -> String {
    let bare = SUP.replace_all(block, "");
    TAG.replace_all(&bare, " ").into_owned()
}

/// A page's blocks: the record writes one `<p>`, `<li>` or heading per line.
pub(super) fn blocks(page: &str) -> Vec<&str> {
    page.lines()
        .map(str::trim)
        .filter(|l| ["<li", "<p", "<h2", "<h3"].iter().any(|t| l.starts_with(t)))
        .collect()
}

fn page_wide(block: &str) -> Vec<(Kind, String)> {
    let t = text(block);
    let mut out: Vec<(Kind, String)> = all(&NUMBER, &t)
        .map(|n| (Kind::Number, n.trim_end_matches(['.', ',']).to_owned()))
        .collect();
    out.extend(all(&LABEL, &t).map(|l| (Kind::Label, l.to_owned())));
    out.extend(all(&QUOTE, &t).map(|q| (Kind::Quote, q.to_owned())));
    out.extend(
        EM.captures_iter(block)
            .map_while(Result::ok)
            .filter_map(|c| c.get(1))
            .map(|m| (Kind::Name, m.as_str().to_owned())),
    );
    out.extend(all(&NAME, &t).map(|n| (Kind::Name, n.to_owned())));
    out.sort();
    out.dedup();
    out
}

fn qualifiers(block: &str) -> BTreeMap<String, usize> {
    let mut counts = BTreeMap::new();
    for w in all(&WORD, &text(block).to_lowercase()) {
        if QUALIFIERS.contains(&w) {
            *counts.entry(w.to_owned()).or_insert(0) += 1;
        }
    }
    counts
}

fn words(block: &str) -> BTreeMap<String, usize> {
    let mut counts = BTreeMap::new();
    for w in text(block).split_whitespace() {
        *counts.entry(w.to_lowercase()).or_insert(0) += 1;
    }
    counts
}

/// The block of `pool` most like `old` by shared words: where a changed block's words went.
fn nearest<'p>(old: &str, pool: &[&'p str]) -> &'p str {
    let mine = words(old);
    let score = |b: &str| {
        let theirs = words(b);
        let shared: usize = mine
            .iter()
            .map(|(w, n)| (*n).min(*theirs.get(w).unwrap_or(&0)))
            .sum();
        let total: usize = mine.values().sum::<usize>() + theirs.values().sum::<usize>() - shared;
        shared * 10_000 / total.max(1)
    };
    pool.iter().copied().max_by_key(|b| score(b)).unwrap_or("")
}

fn changed<'o>(old: &'o str, pool: &[&str]) -> Vec<&'o str> {
    blocks(old)
        .into_iter()
        .filter(|b| !pool.contains(b))
        .collect()
}

fn heading(block: &str) -> String {
    let t = text(block);
    let t = t.split_whitespace().collect::<Vec<_>>().join(" ");
    t.chars().take(70).collect()
}

/// The claim-bearing tokens the change from `old` to `new` dropped, `linked` the pages `new` now points to.
pub(super) fn lost(old: &str, new: &str, linked: &[String]) -> Vec<Lost> {
    let mut pool: Vec<&str> = blocks(new);
    for page in linked {
        pool.extend(blocks(page));
    }
    let mut standing = text(new);
    for page in linked {
        standing.push('\n');
        standing.push_str(&text(page));
    }
    let mut out = Vec::new();
    for block in changed(old, &pool) {
        let to = nearest(block, &pool);
        for (kind, token) in page_wide(block) {
            if !standing.contains(&token) {
                out.push(Lost {
                    block: heading(block),
                    kind,
                    token,
                });
            }
        }
        let kept = qualifiers(to);
        for (word, n) in qualifiers(block) {
            if *kept.get(&word).unwrap_or(&0) < n {
                out.push(Lost {
                    block: heading(block),
                    kind: Kind::Qualifier,
                    token: word,
                });
            }
        }
    }
    out
}

/// The bytes of the words the change removed: each changed block's words its nearest new block no longer holds.
pub(super) fn removed_bytes(old: &str, new: &str) -> usize {
    let pool = blocks(new);
    changed(old, &pool)
        .into_iter()
        .map(|block| {
            let kept = words(nearest(block, &pool));
            words(block)
                .iter()
                .map(|(w, n)| n.saturating_sub(*kept.get(w).unwrap_or(&0)) * (w.len() + 1))
                .sum::<usize>()
        })
        .sum()
}

/// Was the change made to fit the limit: the page over it before, or the removed words putting it back over?
pub(super) const fn is_size_edit(
    old_len: usize,
    new_len: usize,
    removed: usize,
    limit: usize,
) -> bool {
    old_len > limit || new_len + removed > limit
}

#[cfg(test)]
mod tests;
