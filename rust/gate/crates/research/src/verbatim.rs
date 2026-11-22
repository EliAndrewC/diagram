//! Is every quoted passage on the page it cites, character for character? (`scripts/record/quote_verbatim.py`, feature 251 FR-003;
//! ported by feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`.) A question's notes are read as its page in the record's site
//! numbers them, each citation's passages found (a translated quotation's original is what is matched), each page fetched once - each
//! host at most once after it refuses - through the host's page cache, and each passage judged VERBATIM, DIFFERS or NOT-ON-PAGE against
//! the page's visible text, whitespace collapsed on both sides and nothing else forgiven. Its parts: [`html`] the visible text,
//! [`codecs`] the charsets, [`fetch`] the one seam to the network, [`judge`] the verdicts; `l7r-gate record quote-verbatim` is the
//! command (the `bundle` crate), and `owed::translation` reads [`passages`] in process.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::html_text::unescape;
use l7r_shared::py_text::{strip, SPACE_CLASS};
use serde_json::{json, Map, Value};
use unicode_normalization::UnicodeNormalization as _;

use crate::re;

pub mod codecs;
pub mod fetch;
pub mod html;
pub mod judge;

/// The quotation marks that delimit a passage, opening to closing.
const PAIRS: [(char, char); 4] = [('「', '」'), ('“', '”'), ('"', '"'), ('『', '』')];

/// `TRANSLATED`: the parenthetical between a translation and its original; group 1 the language when a translator is named.
static TRANSLATED: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"^[{SPACE_CLASS}]*\((?:title[{SPACE_CLASS}]+)?translated(?: from ([^;()]*(?:\([^()]*\))?[^;()]*?) by [^;()]+)?;[{SPACE_CLASS}]*original:[{SPACE_CLASS}]*\n?\z"
    ))
});
/// `JOINER`: what may stand between two quotations of one run, or two originals of one parenthetical.
static JOINER: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"^[{SPACE_CLASS}]*(?:and|/|,|;)?[{SPACE_CLASS}]*(?:original:)?[{SPACE_CLASS}]*\n?\z"
    ))
});
static SPACES: LazyLock<Regex> = LazyLock::new(|| re(&format!("[{SPACE_CLASS}]+")));
const CJK: &str = r"\x{3000}-\x{303f}\x{3040}-\x{30ff}\x{3400}-\x{4dbf}\x{4e00}-\x{9fff}\x{f900}-\x{faff}\x{ff00}-\x{ffef}";
/// A space between two CJK characters: a line break, never a word gap.
/// A space between two CJK characters, or between one and a digit (449 T197: a PDF line broken at 「割合は\n18.23」 kept its space).
static CJK_GAP: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        "(?<=[{CJK}]) (?=[{CJK}0-9])|(?<=[0-9]) (?=[{CJK}])"
    ))
});
/// The radicals a PDF's text layer may write for an ideograph, which NFKC folds back; and the superscript digits a
/// quotation writes where a page's `<sup>` leaves the bare digit (449 T257: shakkanho-jawiki's `m<sup>2</sup>`).
static RADICAL: LazyLock<Regex> = LazyLock::new(|| {
    re(r"[\x{2e80}-\x{2eff}\x{2f00}-\x{2fdf}\x{b2}\x{b3}\x{b9}\x{2070}\x{2074}-\x{2079}]")
});
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static NOTE: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<li id="(fn-\d+)">(.*?)</li>"#));
static FNBACK: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<a class="fnback".*?</a>"#));
static HREF: LazyLock<Regex> = LazyLock::new(|| re(r#"<a href="([^"]+)""#));
static CODE: LazyLock<Regex> = LazyLock::new(|| re(r"<code>([^<]+)</code>"));
static SUP: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<sup class="fn">.*?#(fn-\d+)".*?</sup>"#));
static BLOCKS: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"</?(?:p|li|h[1-6]|td|th|dd|dt|blockquote){}[^>]*>",
        crate::pyre::boundary()
    ))
});
static MARK: LazyLock<Regex> = LazyLock::new(|| re("\u{2063}(fn-\\d+)\u{2063}"));
static SENTENCE: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        "(?<=[.!?])[{SPACE_CLASS}]+(?=[A-Z(\"\u{201c}\u{300c}])"
    ))
});
static TRAILING_NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"-[0-9]+\n?\z"));

/// The first `n` characters of `text` (Python's `text[:n]`).
#[must_use]
pub fn head(text: &str, n: usize) -> &str {
    text.char_indices()
        .nth(n)
        .map_or(text, |(at, _)| &text[..at])
}

fn matches(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// `squeeze`: whitespace collapsed, NFC (the radicals by NFKC), and a space between two CJK characters, or a CJK character and a digit, taken out.
#[must_use]
pub fn squeeze(text: &str) -> String {
    let folded = RADICAL.replace_all(text, |c: &fancy_regex::Captures| {
        c[0].nfkc().collect::<String>()
    });
    let collapsed = SPACES.replace_all(&folded, " ");
    let nfc: String = collapsed.nfc().collect();
    CJK_GAP.replace_all(strip(&nfc), "").into_owned()
}

/// `visible_text`: the text a reader sees of `markup`, squeezed.
#[must_use]
pub fn visible_text(markup: &str) -> String {
    squeeze(&html::visible(markup))
}

/// `decode`: `raw` as text by the declared charset, then the page's own `<meta>`, then the usual suspects - strict throughout (None).
#[must_use]
pub fn decode(raw: &[u8], declared: &str) -> Option<String> {
    static META: LazyLock<Regex> =
        LazyLock::new(|| re(r#"(?i)<meta[^>]+charset=["']?[ \t\n\r\x0b\x0c]*([A-Za-z0-9_-]+)"#));
    // the first 4,096 bytes as Latin-1, so a bytes pattern reads them byte for byte
    let front: String = raw.iter().take(4096).map(|&b| char::from(b)).collect();
    let meta = META
        .captures(&front)
        .ok()
        .flatten()
        .and_then(|c| c.get(1).map(|g| g.as_str().to_owned()))
        .unwrap_or_default();
    let mut tried: Vec<String> = Vec::new();
    for name in [
        declared,
        &meta,
        "utf-8",
        "shift_jis",
        "euc_jp",
        "gb18030",
        "big5",
    ] {
        let name = strip(name).to_lowercase();
        // a page labeled Shift_JIS is read as Windows-31J, as a browser reads it
        let name = if [
            "shift_jis",
            "shift-jis",
            "sjis",
            "x-sjis",
            "ms_kanji",
            "windows-31j",
        ]
        .contains(&name.as_str())
        {
            "cp932".to_owned()
        } else {
            name
        };
        if name.is_empty() || tried.contains(&name) {
            continue;
        }
        if let Some(text) = codecs::decode(raw, &name) {
            return Some(text);
        }
        tried.push(name);
    }
    None
}

/// `top_level_quotes`: (start, end) of each outermost quoted span in `chars`, delimiters included; `「」` nests.
#[must_use]
pub fn top_level_quotes(chars: &[char]) -> Vec<(usize, usize)> {
    let mut spans = Vec::new();
    let mut i = 0;
    while i < chars.len() {
        let Some(&(open, close)) = PAIRS.iter().find(|p| p.0 == chars[i]) else {
            i += 1;
            continue;
        };
        let (mut depth, mut j) = (1, i + 1);
        while j < chars.len() && depth > 0 {
            if chars[j] == close {
                depth -= 1;
            } else if chars[j] == open && close != open {
                depth += 1;
            }
            j += 1;
        }
        if depth > 0 {
            i += 1;
            continue;
        }
        spans.push((i, j));
        i = j;
    }
    spans
}

/// One quoted passage of a note.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Passage {
    pub quote: String,
    pub original: String,
    pub language: String,
    /// An original of several runs: the runs after the first.
    pub more: Option<Vec<String>>,
}

impl Passage {
    /// As the Python's dict: `quote`, `original`, `language`, then `more` where there is one.
    #[must_use]
    pub fn to_json(&self) -> Map<String, Value> {
        let mut m = Map::new();
        m.insert("quote".into(), json!(self.quote));
        m.insert("original".into(), json!(self.original));
        m.insert("language".into(), json!(self.language));
        if let Some(more) = &self.more {
            m.insert("more".into(), json!(more));
        }
        m
    }
}

fn text_of(chars: &[char], from: usize, to: usize) -> String {
    chars[from..to].iter().collect()
}

/// `translated_run`: two or more quotations from span `k` sharing one translation parenthetical holding as many originals.
#[expect(
    clippy::many_single_char_names,
    reason = "the Python's own names for the spans' indices, kept so the two read side by side"
)]
fn translated_run(chars: &[char], spans: &[(usize, usize)], k: usize) -> Vec<Passage> {
    let gap = |a: usize, b: usize| text_of(chars, spans[a].1, spans[b].0);
    let mut m = k;
    while m + 1 < spans.len() && !gap(m, m + 1).contains('(') && matches(&JOINER, &gap(m, m + 1)) {
        m += 1;
    }
    let n = m - k + 1;
    if n < 2 || m + n >= spans.len() {
        return Vec::new();
    }
    let between_text = gap(m, m + 1);
    let Some(between) = TRANSLATED.captures(&between_text).ok().flatten() else {
        return Vec::new();
    };
    if !(m + 1..m + n).all(|j| matches(&JOINER, &gap(j, j + 1))) {
        return Vec::new();
    }
    let language = squeeze(between.get(1).map_or("", |g| g.as_str()));
    (0..n)
        .map(|i| {
            let (q, o) = (spans[k + i], spans[m + 1 + i]);
            Passage {
                quote: text_of(chars, q.0 + 1, q.1 - 1),
                original: text_of(chars, o.0 + 1, o.1 - 1),
                language: language.clone(),
                more: None,
            }
        })
        .collect()
}

/// `passages`: the quoted passages of one note; `original` is what is matched.
#[must_use]
pub fn passages(note_text: &str) -> Vec<Passage> {
    let chars: Vec<char> = note_text.chars().collect();
    let spans = top_level_quotes(&chars);
    let mut found = Vec::new();
    let mut k = 0;
    while k < spans.len() {
        let (start, end) = spans[k];
        // a quoted phrase inside a parenthetical is the note's own gloss, never the source's
        let opened = chars[..start].iter().filter(|c| **c == '(').count();
        if opened > chars[..start].iter().filter(|c| **c == ')').count() {
            k += 1;
            continue;
        }
        let run = translated_run(&chars, &spans, k);
        if !run.is_empty() {
            k += 2 * run.len();
            found.extend(run);
            continue;
        }
        let mut entry = Passage {
            quote: text_of(&chars, start + 1, end - 1),
            original: String::new(),
            language: String::new(),
            more: None,
        };
        if k + 1 < spans.len() {
            let next = spans[k + 1];
            let between_text = text_of(&chars, end, next.0);
            if let Some(between) = TRANSLATED.captures(&between_text).ok().flatten() {
                entry.original = text_of(&chars, next.0 + 1, next.1 - 1);
                entry.language = squeeze(between.get(1).map_or("", |g| g.as_str()));
                // an original of several runs: the runs after the first sit inside the parentheses
                let mut j = k + 2;
                while j < spans.len()
                    && strip(&text_of(&chars, spans[j - 1].1, spans[j].0)).is_empty()
                {
                    entry.more.get_or_insert_with(Vec::new).push(text_of(
                        &chars,
                        spans[j].0 + 1,
                        spans[j].1 - 1,
                    ));
                    j += 1;
                }
                k += 1;
            }
        }
        found.push(entry);
        k += 1;
    }
    found
}

/// `classify`: an absence note, a grounds note, a citation (it has links) or an unlinked note.
#[must_use]
pub fn classify(note_text: &str, links: &[String]) -> &'static str {
    let lead = squeeze(note_text).to_lowercase();
    if lead.starts_with("no publicly readable source") {
        "absence"
    } else if lead.starts_with("no source is owed") {
        "grounds"
    } else if links.is_empty() {
        "unlinked"
    } else {
        "citation"
    }
}

/// `_strip`: a note's markup as squeezed visible text - comments and tags out, entities read.
#[must_use]
pub fn strip_markup(markup: &str) -> String {
    let bare = COMMENT.replace_all(markup, "");
    squeeze(&unescape(&TAG.replace_all(&bare, "")))
}

/// `footnotes`: one entry per `<li id="fn-N">` - id, key, links, class and passages, keyed in the Python's order.
#[must_use]
pub fn footnotes(citations_html: &str) -> Vec<Map<String, Value>> {
    let mut notes = Vec::new();
    for m in NOTE.captures_iter(citations_html).map_while(Result::ok) {
        let body = FNBACK.replace_all(&m[2], "").into_owned();
        let links: Vec<String> = HREF
            .captures_iter(&body)
            .map_while(Result::ok)
            .map(|c| unescape(&c[1]))
            .collect();
        let key = CODE
            .captures(&body)
            .ok()
            .flatten()
            .map(|c| c[1].to_owned())
            .unwrap_or_default();
        let text = strip_markup(&body);
        let kind = classify(&text, &links);
        let found: Vec<Value> = if kind == "citation" {
            passages(&text)
                .iter()
                .map(|p| Value::Object(p.to_json()))
                .collect()
        } else {
            Vec::new()
        };
        let mut note = Map::new();
        note.insert("id".into(), json!(&m[1]));
        note.insert("key".into(), json!(key));
        note.insert("links".into(), json!(links));
        note.insert("class".into(), json!(kind));
        note.insert("passages".into(), Value::Array(found));
        notes.push(note);
    }
    notes
}

/// `assertions`: fn id to the sentence its `<sup class="fn">` closes, from the page's visible text.
#[must_use]
pub fn assertions(research_html: &str) -> Map<String, Value> {
    let body = COMMENT.replace_all(research_html, "");
    let marked = SUP.replace_all(&body, "\u{2063}$1\u{2063}");
    let mut out = Map::new();
    for block in BLOCKS.split(&marked).map_while(Result::ok) {
        let text = strip_markup(block);
        for m in MARK.captures_iter(&text).map_while(Result::ok) {
            let whole = m.get(0).map_or(0, |g| g.start());
            let before = MARK.replace_all(&text[..whole], "");
            let sentence = SENTENCE
                .split(&before)
                .map_while(Result::ok)
                .last()
                .unwrap_or("");
            if !out.contains_key(&m[1]) {
                out.insert(m[1].to_owned(), json!(squeeze(sentence)));
            }
        }
    }
    out
}

/// `wanted`: `90-108,113` as the fn ids it names; a registry key or a note id names every note citing that key; nothing, None.
#[must_use]
pub fn wanted(spec: &str) -> Option<std::collections::BTreeSet<String>> {
    let mut ids = std::collections::BTreeSet::new();
    for part in spec.split(',').map(strip).filter(|p| !p.is_empty()) {
        let bare = part.strip_prefix("fn-").unwrap_or(part);
        let (lo, hi) = bare.split_once('-').unwrap_or((bare, ""));
        let digits = |s: &str| !s.is_empty() && s.chars().all(|c| crate::digit_value(c).is_some());
        let value = |s: &str| {
            s.chars().fold(0u64, |n, c| {
                n * 10 + u64::from(crate::digit_value(c).unwrap_or(0))
            })
        };
        if digits(lo) && (hi.is_empty() || digits(hi)) {
            let top = if hi.is_empty() { value(lo) } else { value(hi) };
            ids.extend((value(lo)..=top).map(|n| format!("fn-{n}")));
        } else {
            ids.insert(format!("key:{part}"));
            ids.insert(format!("key:{}", TRAILING_NUMBER.replace(part, "")));
        }
    }
    (!ids.is_empty()).then_some(ids)
}

/// `is_wanted`.
#[must_use]
pub fn is_wanted(
    note: &Map<String, Value>,
    only: Option<&std::collections::BTreeSet<String>>,
) -> bool {
    let field = |k: &str| note.get(k).and_then(Value::as_str).unwrap_or("");
    only.is_none_or(|ids| {
        ids.contains(field("id")) || ids.contains(&format!("key:{}", field("key")))
    })
}

/// `render`: a question's report as the session reads it.
#[must_use]
pub fn render(page: &str, entries: &[Map<String, Value>], refused: &[(String, String)]) -> String {
    let s = |v: &Value, k: &str| v.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
    let mut lines = vec![format!(
        "quote-verbatim: {page} - {} footnotes",
        entries.len()
    )];
    let mut tally: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    for e in entries {
        let e = Value::Object(e.clone());
        if s(&e, "class") != "citation" {
            *tally.entry(s(&e, "class")).or_default() += 1;
            continue;
        }
        let ps = e["passages"].as_array().cloned().unwrap_or_default();
        for p in &ps {
            let word = s(p, "quotation");
            *tally.entry(word.clone()).or_default() += 1;
            if word == "VERBATIM" {
                continue;
            }
            let target = if s(p, "original").is_empty() {
                s(p, "quote")
            } else {
                s(p, "original")
            };
            lines.push(format!(
                "  {} {} - {word} ({}): {}",
                s(&e, "id"),
                s(&e, "key"),
                s(p, "matched"),
                head(&target, 120)
            ));
            if word == "DIFFERS" {
                lines.push(format!("      page has: {}", head(&s(p, "page_text"), 200)));
                let diffs: Vec<String> = p["differences"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .take(6)
                    .filter_map(Value::as_str)
                    .map(str::to_owned)
                    .collect();
                let marks = if p["only_reference_markers"] == json!(true) {
                    "   [only the page's reference markers differ]"
                } else {
                    ""
                };
                lines.push(format!("      {}{marks}", diffs.join("; ")));
            } else if p.get("why").is_some() {
                lines.push(format!("      {}", s(p, "why")));
            }
        }
        if ps.is_empty() {
            *tally.entry("NO-QUOTE".to_owned()).or_default() += 1;
            lines.push(format!(
                "  {} {} - NO-QUOTE: a citation that quotes nothing",
                s(&e, "id"),
                s(&e, "key")
            ));
        }
    }
    lines.push(format!(
        "  {}",
        tally
            .iter()
            .map(|(k, v)| format!("{k} {v}"))
            .collect::<Vec<_>>()
            .join(", ")
    ));
    let mut hosts: Vec<&(String, String)> = refused.iter().collect();
    hosts.sort();
    for (host, why) in hosts {
        lines.push(format!("  refused: {host} - {why}"));
    }
    lines.join("\n")
}

#[cfg(test)]
mod tests;
