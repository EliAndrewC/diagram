//! What a pattern can find on a research page, listed for `record-format` (`scripts/record/record_prepass.py`, features 251, 258, 260;
//! ported by feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`): per section of the page's visible text, the session-note
//! shapes and the vocabulary candidates a regular expression finds, and the rare words the model rules on - words of the entry the
//! glossary does not define and at most two of the record's question fragments use. It decides nothing and never edits.
//! `l7r-gate record record-prepass` is the command (the `bundle` crate); `apply-edits` reads [`prepass`] in process.
//!
//! The Python kept each fragment's words by its bytes in `record_cache.ParseCache` (`prepass-words`, feature 375 amendment 8); this port
//! keeps none (`ask:449-T81-slices`: each Rust caller keeps or drops caching on its own measurement - the T145 record), the counts the
//! same either way, and the Python's `functools.cache` of the derived inputs is a caller's (each run reads them once).

use std::collections::{BTreeMap, HashMap, HashSet};
use std::hash::BuildHasher;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::py_text::{repr, split, strip};
use l7r_guard::shared::pyjson::py_str;
use serde_json::{json, Map, Value};

use crate::pyre::{casefold, py};
use crate::sources::Reader;
use crate::{re, Error, Result};

pub const GLOSSARY: &str = "l7r/diagram/interactive/assets/glossary.json";
pub const RESEARCH: &str = "research";
/// HOW RARE A WORD HAS TO BE (feature 260 FR-002, measured in specs/260 R2): the cheapest cutoff that catches what this filter can.
pub const RARE_IN_AT_MOST: usize = 2;

/// THE PATTERNS COMPILED SIDE BY SIDE (feature 449 T167): each `\b` is four look-arounds over Python's Unicode `\w` ([`py`]), and the
/// regex crate compiles each anew - these seven took 35-40 ms one after another and 12 ms side by side, the longest alone 6-10 ms
/// (observed 2026-11-17, method: each timed in the crate's test build), which put every test of a record-format round over FR-008's tenth
/// of a second; the patterns and their order are as they were.
static SESSION_NOTES: LazyLock<Vec<(&str, Regex)>> = LazyLock::new(|| {
    let patterns = [
        ("field", r"\b(?:Grounds|Evidence)\s*:"),
        ("feature number", r"\b[Ff]eature\s+\d{2,3}\b|\bF\d{3}\b"),
        ("task id", r"\bT\d{2,3}\b"),
        ("spec path", r"\bspecs/\d{3}-[\w-]+"),
        (
            "make target",
            r"\bmake\s+(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)+|quick|done|maps|map|audit|claim|tick|verify|soak)\b",
        ),
        (
            "file path",
            r"(?<![\w/.:-])(?:[\w.-]+/)+[\w.-]+\.(?:py|sh|json|md)\b|\b[\w-]+\.(?:py|sh)\b",
        ),
        (
            "fetch verdict",
            r"\b(?:SUMMARY-ONLY|UNFETCHABLE|NOT-FOUND|CONTRADICTED|NOT-READABLE|READ)\b|\bnot re-sourced\b|\bleftover\b",
        ),
    ];
    std::thread::scope(|scope| {
        let compiling: Vec<_> = patterns
            .into_iter()
            .map(|(label, p)| scope.spawn(move || (label, py(p))))
            .collect();
        compiling.into_iter().map(|c| c.join().unwrap()).collect()
    })
});
static IDENTIFIER: LazyLock<Regex> = LazyLock::new(|| py(r"^[A-Za-z_][\w.]*(?:\(\))?$"));
static CJK: LazyLock<Regex> = LazyLock::new(|| {
    re(r"[\x{3040}-\x{30ff}\x{3400}-\x{4dbf}\x{4e00}-\x{9fff}\x{ac00}-\x{d7af}]{2,}")
});
static BINOMIAL: LazyLock<Regex> = LazyLock::new(|| re(r"^[A-Z][a-z]{3,} [a-z]{4,}\z"));
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[A-Za-z][A-Za-z'-]+"));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static SPACES: LazyLock<Regex> = LazyLock::new(|| py(r"\s+"));
static SCRIPT: LazyLock<Regex> = LazyLock::new(|| py(r"(?si)<(script|style)\b.*?</\1>"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| py(r"(?si)<h[23]\b[^>]*>.*?</h[23]>"));
static HEADING_OPEN: LazyLock<Regex> = LazyLock::new(|| py(r"(?i)^<h[23]\b"));
static XREF: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<span class="xref">.*?</span>"#));
static CODE_SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"<code>([^<]+)</code>"));
static LINK_OPEN: LazyLock<Regex> = LazyLock::new(|| py(r"<a\b[^>]*>\s*$"));
static ITALIC: LazyLock<Regex> = LazyLock::new(|| py(r"(?si)<(em|i)\b[^>]*>(.*?)</\1>"));
static QUOTISH: LazyLock<Regex> = LazyLock::new(|| re("[\"\u{201c}\u{201d}.:!?]"));
static CODE_ANY: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<code\b[^>]*>.*?</code>"));
static REGISTRY_KEY: LazyLock<Regex> = LazyLock::new(|| re(r#"<h3 id="([a-z0-9][a-z0-9-]*)""#));
static PAGE_HEADING: LazyLock<Regex> = LazyLock::new(|| re(r#"<h[23] id="([^"]+)""#));
static NOT_BARE: LazyLock<Regex> = LazyLock::new(|| re(r"[^a-z0-9]+"));

/// `strip_comments`.
#[must_use]
pub fn strip_comments(markup: &str) -> String {
    COMMENT.replace_all(markup, "").into_owned()
}

/// `text_of`: the visible text, tags spaced out, entities read, whitespace collapsed.
#[must_use]
pub fn text_of(markup: &str) -> String {
    let spaced = TAG.replace_all(markup, " ");
    strip(&SPACES.replace_all(&unescape(&spaced), " ")).to_owned()
}

/// `sections`: (heading, body markup) per `<h2>`/`<h3>`; what precedes the first heading is `(top)`.
#[must_use]
pub fn sections(markup: &str) -> Vec<(String, String)> {
    let body = strip_comments(&SCRIPT.replace_all(markup, ""));
    let mut parts: Vec<&str> = Vec::new();
    let mut from = 0;
    for m in HEADING.find_iter(&body).flatten() {
        parts.push(&body[from..m.start()]);
        parts.push(m.as_str());
        from = m.end();
    }
    parts.push(&body[from..]);
    let (mut out, mut heading) = (Vec::new(), "(top)".to_owned());
    for part in parts {
        if HEADING_OPEN.is_match(part).unwrap_or(false) {
            heading = text_of(&XREF.replace_all(part, ""));
        } else if !strip(part).is_empty() {
            out.push((heading.clone(), part.to_owned()));
        }
    }
    out
}

/// `sentence_around`: the sentence holding characters `start..end` of `text`, at most 240 characters.
#[must_use]
pub fn sentence_around(text: &[char], start: usize, end: usize) -> String {
    let find_back = |stop: char| {
        (1..start.min(text.len()))
            .rev()
            .find(|&i| text[i - 1] == stop && text[i] == ' ')
            .map(|i| i - 1)
    };
    let left = find_back('.').max(find_back('?')).map_or(0, |i| i + 1);
    let right = (end..text.len().saturating_sub(1)).find(|&i| text[i] == '.' && text[i + 1] == ' ');
    let stop = right.map_or(text.len(), |r| r + 1);
    let piece: String = if left < stop {
        text[left..stop].iter().collect()
    } else {
        String::new()
    };
    strip(&piece).chars().take(240).collect()
}

fn char_index(text: &str, byte: usize) -> usize {
    text[..byte].chars().count()
}

/// `known_terms`: every glossary term and variant, case-folded.
///
/// # Errors
/// An entry that is not a mapping, or variants that are not a list.
pub fn known_terms(glossary: &Map<String, Value>) -> Result<HashSet<String>> {
    let mut known = HashSet::new();
    for (term, entry) in glossary {
        known.insert(casefold(term));
        let Value::Object(entry) = entry else {
            return Err(Error::new(
                "AttributeError",
                "object has no attribute 'get'",
            ));
        };
        match entry.get("variants") {
            Some(Value::Array(vs)) => known.extend(vs.iter().map(|v| casefold(&py_str(v)))),
            Some(Value::String(s)) if !s.is_empty() => {
                known.extend(s.chars().map(|c| casefold(&c.to_string())));
            }
            Some(Value::Object(m)) if !m.is_empty() => known.extend(m.keys().map(|k| casefold(k))),
            Some(v) if l7r_guard::shared::pyjson::truthy(v) => {
                return Err(Error::new("TypeError", "object is not iterable"));
            }
            _ => {}
        }
    }
    Ok(known)
}

/// One candidate line.
fn item(class: &str, label: &str, matched: &str, sentence: &str) -> Value {
    json!({"class": class, "label": label, "match": matched, "sentence": sentence})
}

/// `session_notes`: the session-note shapes in a section's visible text, then the engine identifiers in its `<code>`.
#[must_use]
pub fn session_notes(markup: &str) -> Vec<Value> {
    let text = text_of(markup);
    let chars: Vec<char> = text.chars().collect();
    let mut found = Vec::new();
    for (label, pattern) in SESSION_NOTES.iter() {
        for m in pattern.find_iter(&text).flatten() {
            let (s, e) = (char_index(&text, m.start()), char_index(&text, m.end()));
            found.push(item(
                "SESSION NOTE",
                label,
                m.as_str(),
                &sentence_around(&chars, s, e),
            ));
        }
    }
    for m in CODE_SPAN.captures_iter(markup).flatten() {
        let inner = strip(&unescape(&m[1])).to_owned();
        let at = m.get(0).map_or(0, |g| g.start());
        let linked = LINK_OPEN.is_match(&markup[..at]).unwrap_or(false);
        let shaped = inner.contains('_') || inner.contains('.') || inner.ends_with("()");
        if !linked && IDENTIFIER.is_match(&inner).unwrap_or(false) && shaped {
            let s = text.find(&inner).map_or(0, |b| char_index(&text, b));
            let e = s + inner.chars().count();
            found.push(item(
                "SESSION NOTE",
                "engine identifier",
                &inner,
                &sentence_around(&chars, s, e),
            ));
        }
    }
    found
}

/// `rare_words`: the words of one entry the glossary does not define and the record rarely uses, sorted - failing closed on a word the
/// corpus never saw.
#[must_use]
pub fn rare_words<A: BuildHasher, B: BuildHasher, C: BuildHasher>(
    text: &str,
    defined: &HashSet<String, A>,
    frequency: &HashMap<String, usize, B>,
    keys: &HashSet<String, C>,
) -> Vec<(String, usize)> {
    let mut out: BTreeMap<String, usize> = BTreeMap::new();
    for raw in WORD.find_iter(text).flatten() {
        let word = raw.as_str().to_lowercase();
        let seen = frequency.get(&word).copied().unwrap_or(0);
        if seen == 0 || defined.contains(&word) || keys.contains(&word) || seen > RARE_IN_AT_MOST {
            continue;
        }
        out.insert(word, seen);
    }
    out.into_iter().collect()
}

/// A file's text, `open(encoding="utf-8")`: None where it cannot be opened.
fn read_utf8(path: &Path) -> Result<Option<String>> {
    let Ok(raw) = std::fs::read(path) else {
        return Ok(None);
    };
    let text =
        String::from_utf8(raw).map_err(|e| Error::new("UnicodeDecodeError", e.to_string()))?;
    Ok(Some(text.replace("\r\n", "\n").replace('\r', "\n")))
}

/// `defined_words`: every variant the glossary defines, from the variant index (each line's text before its first tab).
///
/// # Errors
/// An index that is not UTF-8.
pub fn defined_words(record_dir: &Path) -> Result<HashSet<String>> {
    let Some(text) = read_utf8(&record_dir.join("assets/glossary-variants.txt"))? else {
        return Ok(HashSet::new());
    };
    Ok(text
        .split_inclusive('\n')
        .filter(|l| !strip(l).is_empty())
        .map(|l| l.split('\t').next().unwrap_or("").to_owned())
        .collect())
}

/// `registry_keys`: the source keys of `SOURCES.html`.
///
/// # Errors
/// The registry's refusal.
pub fn registry_keys(reader: &Reader) -> Result<HashSet<String>> {
    let page = reader.record_text("SOURCES.html")?;
    Ok(REGISTRY_KEY
        .captures_iter(&page)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect())
}

/// `os.walk(top)`: each directory (top first) with its files, in the order the directory lists them.
fn walk(top: &Path, out: &mut Vec<(std::path::PathBuf, Vec<String>)>) {
    let Ok(entries) = std::fs::read_dir(top) else {
        return;
    };
    let (mut dirs, mut files) = (Vec::new(), Vec::new());
    for e in entries.flatten() {
        let is_dir = std::fs::metadata(e.path()).is_ok_and(|m| m.is_dir());
        if is_dir {
            dirs.push(e.path());
        } else {
            files.push(e.file_name().to_string_lossy().into_owned());
        }
    }
    out.push((top.to_path_buf(), files));
    for d in dirs {
        if !std::fs::symlink_metadata(&d).is_ok_and(|m| m.file_type().is_symlink()) {
            walk(&d, out);
        }
    }
}

/// `corpus_frequency`: in how many of the record's question fragments each word appears (the built site and the assets left out).
///
/// # Errors
/// A fragment that is not UTF-8.
pub fn corpus_frequency(record_dir: &Path) -> Result<HashMap<String, usize>> {
    let mut freq: HashMap<String, usize> = HashMap::new();
    let mut dirs = Vec::new();
    walk(record_dir, &mut dirs);
    for (base, names) in dirs {
        let rel = base
            .strip_prefix(record_dir)
            .map(|r| r.to_string_lossy().into_owned())
            .unwrap_or_default();
        let shown = base.to_string_lossy();
        if shown.contains("citations")
            || shown.ends_with("assets")
            || base == record_dir
            || rel.split('/').next() == Some("site")
            || rel.starts_with(".site-")
        {
            continue;
        }
        for name in names {
            if !crate::has_ext(&name, "html") || name.starts_with('_') {
                continue;
            }
            let raw = std::fs::read(base.join(&name))
                .map_err(|e| Error::new("OSError", e.to_string()))?;
            let text = String::from_utf8(raw)
                .map_err(|e| Error::new("UnicodeDecodeError", e.to_string()))?;
            let words: HashSet<String> = WORD
                .find_iter(&text_of(&strip_comments(&text)))
                .flatten()
                .map(|m| m.as_str().to_lowercase())
                .collect();
            for word in words {
                *freq.entry(word).or_default() += 1;
            }
        }
    }
    Ok(freq)
}

/// `vocabulary`: the italic terms and the CJK runs of a section the glossary does not cover.
#[must_use]
pub fn vocabulary<S: BuildHasher>(markup: &str, known: &HashSet<String, S>) -> Vec<Value> {
    let text = text_of(markup);
    let chars: Vec<char> = text.chars().collect();
    let mut seen: HashSet<String> = HashSet::new();
    let mut found = Vec::new();
    let mut add = |label: &str, term: &str| {
        let key = casefold(term);
        if seen.contains(&key) || known.contains(&key) || term.is_empty() {
            return;
        }
        seen.insert(key);
        let s = text.find(term).map_or(0, |b| char_index(&text, b));
        found.push(item(
            "VOCABULARY",
            label,
            term,
            &sentence_around(&chars, s, s + term.chars().count()),
        ));
    };
    for m in ITALIC.captures_iter(markup).flatten() {
        let term = text_of(&m[2]);
        let n = split(&term).len();
        if (1..=3).contains(&n) && !QUOTISH.is_match(&term).unwrap_or(false) {
            add(
                if BINOMIAL.is_match(&term).unwrap_or(false) {
                    "binomial"
                } else {
                    "italic term"
                },
                &term,
            );
        }
    }
    for m in CJK.find_iter(&text).flatten() {
        add("CJK term", m.as_str());
    }
    found
}

/// `without_code`: visible text with `<code>` spans removed.
#[must_use]
pub fn without_code(markup: &str) -> String {
    text_of(&CODE_ANY.replace_all(markup, " "))
}

/// `_bare`: a heading reduced to its letters and digits, entities read.
#[must_use]
pub fn bare(heading: &str) -> String {
    let text = unescape(&TAG.replace_all(heading, ""));
    NOT_BARE.replace_all(&casefold(&text), "").into_owned()
}

/// `notes_index`: {question slug: the visible text of its notes}, keyed by the heading id of the page the notes belong to.
///
/// # Errors
/// A notes file or page that is not UTF-8.
pub fn notes_index(record_dir: &Path) -> Result<HashMap<String, String>> {
    let mut out = HashMap::new();
    let mut dirs = Vec::new();
    walk(record_dir, &mut dirs);
    for (base, names) in dirs {
        if base.to_string_lossy().contains("citations") || base == record_dir {
            continue;
        }
        for name in names {
            let Some(stem) = name.strip_suffix(".notes.html") else {
                continue;
            };
            let page = base.join(format!("{stem}.html"));
            let id = if page.is_file() {
                let text = read_utf8(&page)?.unwrap_or_default();
                PAGE_HEADING
                    .captures(&text)
                    .ok()
                    .flatten()
                    .map(|c| c[1].to_owned())
            } else {
                None
            };
            let key = id.unwrap_or_else(|| {
                let tail = name.split_once('-').map_or(name.as_str(), |p| p.1);
                tail[..tail.len() - ".notes.html".len()].to_owned()
            });
            let body =
                read_utf8(&base.join(&name))?.ok_or_else(|| Error::new("OSError", name.clone()))?;
            out.insert(bare(&key), without_code(&strip_comments(&body)));
        }
    }
    Ok(out)
}

/// What the rare-word pass reads of the record, each read once a run.
pub struct Corpus {
    pub defined: HashSet<String>,
    pub keys: HashSet<String>,
    pub freq: HashMap<String, usize>,
    pub notes: HashMap<String, String>,
}

impl Corpus {
    /// # Errors
    /// What any of the four readers refused.
    pub fn read(record_dir: &Path) -> Result<Self> {
        Ok(Self {
            defined: defined_words(record_dir)?,
            keys: registry_keys(&Reader::new(record_dir))?,
            freq: corpus_frequency(record_dir)?,
            notes: notes_index(record_dir)?,
        })
    }
}

/// Every pattern the pass reads, compiled side by side once a process before the pass reads the first (feature 449 T167, as
/// [`SESSION_NOTES`]: the look-around patterns 2-5 ms each one after another).
static WARM: LazyLock<()> = LazyLock::new(|| {
    std::thread::scope(|scope| {
        scope.spawn(|| LazyLock::force(&SESSION_NOTES));
        for pattern in [
            &IDENTIFIER,
            &CJK,
            &BINOMIAL,
            &WORD,
            &COMMENT,
            &TAG,
            &SPACES,
            &SCRIPT,
            &HEADING,
            &HEADING_OPEN,
            &XREF,
            &CODE_SPAN,
            &LINK_OPEN,
            &ITALIC,
            &QUOTISH,
            &CODE_ANY,
            &REGISTRY_KEY,
            &PAGE_HEADING,
            &NOT_BARE,
        ] {
            scope.spawn(move || LazyLock::force(pattern));
        }
    });
});

/// `prepass`: per section, its heading, the candidate lines, and the rare words the model must rule on (none without a record).
///
/// # Errors
/// The glossary's or the record's refusal.
pub fn prepass(
    markup: &str,
    glossary: &Map<String, Value>,
    record_dir: Option<&Path>,
) -> Result<Vec<Value>> {
    LazyLock::force(&WARM);
    let known = known_terms(glossary)?;
    let corpus = record_dir.map(Corpus::read).transpose()?;
    let mut out = Vec::new();
    for (heading, body) in sections(markup) {
        let rare: Vec<Value> = match &corpus {
            Some(c) => {
                let scanned = format!(
                    "{} {}",
                    without_code(&body),
                    c.notes.get(&bare(&heading)).map_or("", String::as_str)
                );
                rare_words(&scanned, &c.defined, &c.freq, &c.keys)
                    .into_iter()
                    .map(|(w, n)| json!([w, n]))
                    .collect()
            }
            None => Vec::new(),
        };
        let mut items = session_notes(&body);
        items.extend(vocabulary(&body, &known));
        out.push(json!({"section": heading, "items": items, "rare": rare}));
    }
    Ok(out)
}

/// `render`: the listing as `record-format` is handed it.
#[must_use]
pub fn render(page: &str, listing: &[Value]) -> String {
    let count = |s: &Value, k: &str| s[k].as_array().map_or(0, Vec::len);
    let total: usize = listing.iter().map(|s| count(s, "items")).sum();
    let rare: usize = listing.iter().map(|s| count(s, "rare")).sum();
    let text = |v: &Value| v.as_str().unwrap_or("").to_owned();
    let mut lines = vec![format!(
        "record-prepass: {page} - {} sections, {total} candidates (each is for record-format to confirm or dismiss)",
        listing.len()
    )];
    for sec in listing {
        let items = sec["items"].as_array().cloned().unwrap_or_default();
        if items.is_empty() {
            continue;
        }
        lines.push(format!("## {}", text(&sec["section"])));
        for it in items {
            lines.push(format!(
                "  {} [{}] {} - {}",
                text(&it["class"]),
                text(&it["label"]),
                repr(&text(&it["match"])),
                text(&it["sentence"])
            ));
        }
    }
    if rare > 0 {
        lines.push(String::new());
        lines.push(format!("## WORDS TO RULE ON ({rare}) - feature 260"));
        lines.push(String::new());
        lines.push("Every word below is in this entry, is defined by no glossary term, and appears in at most".to_owned());
        lines.push(format!("{RARE_IN_AT_MOST} of the record's question fragments (the count is beside each one). `record-format` rules"));
        lines.push("on EVERY one of them and says which verdict each got. The list is a floor, not the question:".to_owned());
        lines.push("it cannot see a MULTI-WORD term, and it does not raise a word the record uses often though".to_owned());
        lines.push(
            "the glossary does not define it - so anything else you notice is reported too."
                .to_owned(),
        );
        for sec in listing {
            let words = sec["rare"].as_array().cloned().unwrap_or_default();
            if words.is_empty() {
                continue;
            }
            lines.push(format!("### {}", text(&sec["section"])));
            let shown: Vec<String> = words
                .iter()
                .map(|w| format!("{} ({})", text(&w[0]), w[1]))
                .collect();
            lines.push(format!("  {}", shown.join(", ")));
        }
    }
    lines.join("\n")
}

/// The words `apply-edits` compares before and after a record-format round's blocks: every candidate's match and every rare word, over
/// the question's pages as they stand now.
///
/// # Errors
/// The glossary or the record unreadable.
pub fn prepass_words(root: &Path, q: &str) -> Result<HashSet<String>> {
    let qdir = root.join(RESEARCH).join("questions");
    let mut pages: Vec<String> = std::fs::read_dir(&qdir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n.starts_with(&format!("{q}-")) && crate::has_ext(n, "html"))
        .filter(|n| !n.ends_with(".notes.html") && !n.ends_with(".originals.html"))
        .collect();
    pages.sort();
    let mut markup = Vec::new();
    for p in &pages {
        let at = qdir.join(p);
        markup.push(
            read_utf8(&at)?.ok_or_else(|| {
                Error::new("OSError", format!("{}: cannot be read", at.display()))
            })?,
        );
    }
    let glossary = read_glossary(root)?;
    let listing = prepass(&markup.join("\n"), &glossary, Some(&root.join(RESEARCH)))?;
    let mut out = HashSet::new();
    for s in &listing {
        out.extend(
            s["items"]
                .as_array()
                .into_iter()
                .flatten()
                .map(|i| py_str(&i["match"])),
        );
        out.extend(
            s["rare"]
                .as_array()
                .into_iter()
                .flatten()
                .map(|w| py_str(&w[0])),
        );
    }
    Ok(out)
}

/// The glossary (`glossary.json`), empty where there is none.
///
/// # Errors
/// A glossary that is not UTF-8 or not JSON, or not a mapping.
pub fn read_glossary(root: &Path) -> Result<Map<String, Value>> {
    let path = root.join(GLOSSARY);
    if !path.is_file() {
        return Ok(Map::new());
    }
    let text = read_utf8(&path)?.unwrap_or_default();
    match crate::json(&text).map_err(|e| Error::new("JSONDecodeError", e))? {
        Value::Object(m) => Ok(m),
        _ => Err(Error::new(
            "AttributeError",
            "object has no attribute 'items'",
        )),
    }
}

#[cfg(test)]
mod tests;
