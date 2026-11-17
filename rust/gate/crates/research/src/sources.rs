//! What a modal's references rest on, read from the research record itself (`interactive/sources.py`, features 134, 180, 194, 211, 301,
//! 303, 307; ported by feature 449 T144): the QUESTIONS a class's entry names, each linking its small page in the record's site, and the
//! registry's entries - each key's citation line, its write-ups, where a citation of it links.
//!
//! Not ported, because nothing calls them (`git grep` over every tracked file, 2026-11-16): `github_anchor`, `registry`, `parse_sections`,
//! `section_sources`, `footnote_sources`, `research_sources`, `citation_lines`, `registry_keys` and `urls_of`; they go with `sources.py`.
//! `clear_caches` and the `@cache`s have no counterpart: a [`Reader`] holds what it has read, and a new one reads again.

use std::cell::OnceCell;
use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::shared::cited_url::trimmed;
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::py_text::{collapse, strip};

use crate::record::archive::entry_bodies;
use crate::record::questions::Record;
use crate::record::{confusables, store, xref};
use crate::{drop_all, re, Error, Result, SPACE_CLASS};

/// Where a question links, relative to a map's own page (features 194, 301, 303).
pub const SITE_PAGES: &str = "../../../research/site/";
/// Where a question's small page is, under `SITE_PAGES`.
pub const QUESTION_PAGES: &str = "q/";
/// Where the questions are, in the record.
pub const QUESTIONS: &str = "questions";
/// The two write-ups and the uses a registry entry carries (feature 211).
pub const WHAT_LABEL: &str = "What it is:";
pub const WHY_LABEL: &str = "Why it applies, and its limits:";
pub const USED_LABEL: &str = "Used for:";

/// A research question an entry names: its FRAGMENT (feature 301), `research/questions/NNNN-<slug>[.drawing].html`.
pub static ENTRY_FRAGMENT: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r#"research/questions/(\d{{4}}-[^{SPACE_CLASS}/,;)"'`<>]+?(?:\.drawing)?\.html)"#
    ))
});
static HEADING_TAG: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r#"(?s)<h([1-6])(?:[{SPACE_CLASS}]+id="([^"]*)")?[^>]*>(.*?)</h\1>"#
    ))
});
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static DATED_TAIL: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"[{SPACE_CLASS}]*\([^()]*\b\d{{4}}-\d{{2}}-\d{{2}}\b[^()]*\)[{SPACE_CLASS}]*\z"
    ))
});
static MARKUP: LazyLock<Regex> = LazyLock::new(|| re(r"[*`]"));
static XREF: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<span class="xref">.*?</span>"#));
static ANY_COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static FIRST_P: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<p>(.*?)</p>"));
static CITE_URL: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r#"https?://[^{SPACE_CLASS}<>"]+"#)));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--(.*?)-->"));
static NOT_FETCHED: LazyLock<Regex> = LazyLock::new(|| re(r"unfetched|not fetched"));
static ENTRY_HEAD: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r#"(?s)<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>[{SPACE_CLASS}]*<p>(.*?)</p>"#
    ))
});
/// The GM's own campaign notes, named on a citation line: canon, not evidence (the GM's ruling of 2026-09-07).
static CANON_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"\bl7r\.md\b|\bbudgets\.md\b"));
/// The regex crate's `\w`, which the markup scan's `\b` reads (the pattern `markup_part` replaced was the regex crate's, not Python's).
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"^\w"));

fn word_at(text: &str, at: usize) -> bool {
    WORD.is_match(&text[at..]).unwrap_or(false)
}

/// Where a bare URL may stand: outside every tag and comment, and outside a link's text - the next markup part at or after `from`, as
/// `(?s)(<!--.*?-->|<a\b[^>]*>.*?</a>|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)` finds it: at the first `<` where a branch
/// matches, the first branch that does. Scanned by hand (feature 449 T148): the pattern ran on the backtracking engine and was seven
/// tenths of the record's whole site build, every page linked through it.
fn markup_part(text: &str, from: usize) -> Option<(usize, usize)> {
    let mut at = from;
    while let Some(found) = text[at..].find('<') {
        let i = at + found;
        let rest = &text[i..];
        let closed =
            |open: usize, close: &str| rest[open..].find(close).map(|e| i + open + e + close.len());
        let bounded = |name: &str| rest.starts_with(name) && !word_at(text, i + name.len());
        let hit = if rest.starts_with("<!--") {
            closed(4, "-->")
        } else {
            None
        }
        .or_else(|| {
            if !bounded("<a") {
                return None;
            }
            let tag = rest[2..].find('>')? + 3;
            closed(tag, "</a>")
        })
        .or_else(|| {
            if bounded("<script") {
                closed(7, "</script>")
            } else {
                None
            }
        })
        .or_else(|| {
            if bounded("<style") {
                closed(6, "</style>")
            } else {
                None
            }
        })
        .or_else(|| {
            let end = rest[1..].find('>')?;
            (end > 0).then_some(i + end + 2)
        });
        if let Some(end) = hit {
            return Some((i, end));
        }
        at = i + 1;
    }
    None
}

/// The rendered text of a heading - what a reader sees.
#[must_use]
pub fn heading_text(heading: &str) -> String {
    strip(&drop_all(&MARKUP, &drop_all(&XREF, heading))).to_owned()
}

/// The text of an HTML fragment: tags dropped, entities decoded, whitespace collapsed.
#[must_use]
pub fn page_text(fragment: &str) -> String {
    collapse(&unescape(&drop_all(&TAG, &drop_all(&XREF, fragment))))
}

/// The heading as the references modal shows it: the rendered text, less a trailing dated parenthetical (spec 180 FR-005).
#[must_use]
pub fn question_text(heading: &str) -> String {
    strip(&drop_all(&DATED_TAIL, &heading_text(heading))).to_owned()
}

/// The file name of every question page an entry names, in its order (spec 180 D4: the primary question first), once each.
#[must_use]
pub fn entry_fragments(entry: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for c in ENTRY_FRAGMENT.captures_iter(entry).flatten() {
        if !out.iter().any(|f| f == &c[1]) {
            out.push(c[1].to_owned());
        }
    }
    out
}

/// One question behind a modal: its heading less the dated bookkeeping, and its small page in the record's site.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Question {
    pub text: String,
    pub url: String,
}

/// The QUESTIONS behind a modal (feature 180), in the order the entry names them; a path that names no fragment yields nothing (which
/// `check-entry-headings.py` refuses at the push).
#[must_use]
pub fn research_questions(entry: &str, research_dir: &Path) -> Vec<Question> {
    let mut out = Vec::new();
    for file in entry_fragments(entry) {
        let text = crate::read(&research_dir.join(QUESTIONS).join(&file)).unwrap_or_default();
        let plain = drop_all(&ANY_COMMENT, &text);
        let Some(m) = HEADING_TAG.captures(&plain).ok().flatten() else {
            continue;
        };
        let id = m.get(2).map_or("", |g| g.as_str());
        out.push(Question {
            text: question_text(&page_text(&m[3])),
            url: format!("{SITE_PAGES}{QUESTION_PAGES}{id}.html"),
        });
    }
    out
}

/// The record does NOT say the document was read: SUMMARY-ONLY, `URL: none`, or unfetched with no READ beside it.
#[must_use]
pub fn not_read(cite: &str) -> bool {
    if cite.contains("SUMMARY-ONLY") || cite.contains("URL: none") {
        return true;
    }
    NOT_FETCHED.is_match(cite).unwrap_or(false) && !cite.contains("READ")
}

/// Where a citation of `key` links: the first URL on its citation line when it was read, else the registry entry that says it was not
/// (spec 190 D2); `rel` the path from the citing page to the record.
#[must_use]
pub fn link_target(key: &str, cite: &str, rel: &str) -> String {
    let found = CITE_URL.find(cite).ok().flatten();
    let canon = CANON_FILE.is_match(cite).unwrap_or(false);
    let Some(m) = found.filter(|_| !not_read(cite) && !canon) else {
        return format!("{rel}SOURCES.html#{key}");
    };
    let mut u = m.as_str().trim_end_matches(['.', ',', ';', ':']);
    while u.ends_with(')') && u.matches(')').count() > u.matches('(').count() {
        u = &u[..u.len() - 1];
    }
    u.to_owned()
}

/// Every bare URL in `fragment` made a link to itself that opens in a new tab (feature 307); a URL already inside a link, a tag, a comment,
/// a script or a style is left as it is.
#[must_use]
pub fn linkify(fragment: &str) -> String {
    let mut out = String::new();
    let mut at = 0;
    while let Some((start, end)) = markup_part(fragment, at) {
        out.push_str(&link_text(&fragment[at..start]));
        out.push_str(&fragment[start..end]);
        at = end;
    }
    out.push_str(&link_text(&fragment[at..]));
    out
}

fn link_text(part: &str) -> String {
    let mut out = String::new();
    let mut at = 0;
    for m in CITE_URL.find_iter(part).flatten() {
        let u = trimmed(m.as_str());
        out.push_str(&part[at..m.start()]);
        let _ = write!(
            out,
            r#"<a href="{u}" target="_blank" rel="noopener">{u}</a>"#
        );
        at = m.start() + u.len();
    }
    out.push_str(&part[at..]);
    out
}

/// The parts of one registry entry (feature 211): `cite` the citation line's inner HTML, comments dropped; `line` the same as text WITH
/// its comments' text, the classifier's input; `what`, `why` and `used` the write-ups' inner HTML, "" where none is written.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Entry {
    pub cite: String,
    pub line: String,
    pub what: String,
    pub why: String,
    pub used: String,
}

/// The citation line's text WITH its comments' text: the verification markers the classifier reads live in a comment (feature 209).
fn line_text(fragment: &str) -> String {
    let opened = COMMENT.replace_all(fragment, |c: &Captures| format!(" {} ", &c[1]));
    unescape(&drop_all(&TAG, &opened))
}

/// The three write-ups' patterns, `<p><em>label</em> ...</p>`, compiled once: compiled a call, they were a second of the site's build
/// over the registry's 2,900 entries (feature 449 T148).
static LABELED: LazyLock<[Regex; 3]> = LazyLock::new(|| {
    [WHAT_LABEL, WHY_LABEL, USED_LABEL].map(|label| {
        re(&format!(
            r"(?s)<p><em>{}</em>[{SPACE_CLASS}]*(.*?)</p>",
            fancy_regex::escape(label)
        ))
    })
});

/// The inner HTML of the entry's write-up `which` (0 what, 1 why, 2 used), "" where it has none.
fn labeled(body: &str, which: usize) -> String {
    LABELED[which]
        .captures(body)
        .ok()
        .flatten()
        .map_or_else(String::new, |c| strip(&c[1]).to_owned())
}

/// A record read for its readers: the questions loaded and the registry assembled once, each the first time it is asked for.
pub struct Reader {
    dir: PathBuf,
    record: OnceCell<Record>,
    tables: OnceCell<(Vec<xref::Pair>, Vec<confusables::Pair>)>,
}

impl Reader {
    #[must_use]
    pub fn new(research_dir: &Path) -> Self {
        Self {
            dir: research_dir.to_path_buf(),
            record: OnceCell::new(),
            tables: OnceCell::new(),
        }
    }

    fn record(&self) -> Result<&Record> {
        if let Some(r) = self.record.get() {
            return Ok(r);
        }
        let loaded = store::load(&self.dir)?;
        Ok(self.record.get_or_init(|| loaded))
    }

    /// A page of the record as a reader would open it, read from its fragments (features 301, 303): `SOURCES.html` the registry
    /// assembled, `questions/<file>` a question page with its cross-link and confusables written in; any other name read from its file,
    /// "" where it is not there.
    ///
    /// # Errors
    /// The registry's or the record's refusal, or a file under `questions/` that is no page of the record (Python's `KeyError`).
    pub fn record_text(&self, rel: &str) -> Result<String> {
        if rel == "SOURCES.html" && self.dir.join(store::REGISTRY_DIR).is_dir() {
            return store::registry_html(&self.dir);
        }
        if let Some(file) = rel
            .strip_prefix("questions/")
            .filter(|_| self.dir.join(rel).is_file())
        {
            let record = self.record()?;
            let page = record
                .by_file(file)
                .ok_or_else(|| Error::new("KeyError", format!("'{file}'")))?;
            let tables = if let Some(t) = self.tables.get() {
                t
            } else {
                let read = store::shared(record, &self.dir)?;
                self.tables.get_or_init(|| read)
            };
            return store::page_html(record, page, &self.dir, Some(tables));
        }
        Ok(crate::read(&self.dir.join(rel)).unwrap_or_default())
    }

    /// Key to the parts of its registry entry (feature 211), in the registry's order.
    ///
    /// # Errors
    /// The registry's refusal.
    pub fn registry_entries(&self) -> Result<Vec<(String, Entry)>> {
        let src = self.record_text("SOURCES.html")?;
        let mut out: Vec<(String, Entry)> = Vec::new();
        for (key, body) in entry_bodies(&src, false) {
            let cite = FIRST_P
                .captures(body)
                .ok()
                .flatten()
                .map_or_else(String::new, |c| c[1].to_owned());
            let entry = Entry {
                cite: collapse(&drop_all(&ANY_COMMENT, &cite)),
                line: line_text(&cite),
                what: labeled(body, 0),
                why: labeled(body, 1),
                used: labeled(body, 2),
            };
            match out.iter_mut().find(|(k, _)| *k == key) {
                Some(slot) => slot.1 = entry,
                None => out.push((key, entry)),
            }
        }
        Ok(out)
    }

    /// The keys whose source is the GM's own campaign notes.
    ///
    /// # Errors
    /// The registry's refusal.
    pub fn canon_keys(&self) -> Result<BTreeSet<String>> {
        let src = self.record_text("SOURCES.html")?;
        Ok(ENTRY_HEAD
            .captures_iter(&src)
            .flatten()
            .filter(|c| CANON_FILE.is_match(&c[2]).unwrap_or(false))
            .map(|c| c[1].to_owned())
            .collect())
    }
}

#[cfg(test)]
mod tests;
