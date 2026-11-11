//! The record checks a delta owes, decided over plain text (from `record_units.py`, feature 449 T87): what counts as changed, what each change owes, and each unit's fingerprint. A pure function of the record's text, read by [`crate::record::owed`], which reads the repository.

use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::shared::checks::pages::{read_page, words, Page};
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::sha256;
use serde_json::{json, Value};

/// The record's directory, its questions, and every directory of registry write-ups a check can be owed on.
pub const QUESTIONS: &str = "research/questions";
pub const SOURCE_DIRS: [&str; 2] = [
    "research/sources/010-works-cited",
    "research/sources/040-uncited-works",
];
/// An absence note's own words: it cites no page, so no source-reader round is owed on it.
const ABSENCE: &str = "no publicly readable source";

/// Compiles a pattern the source spells out (`record_units`' own).
#[must_use]
pub fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
pub static NOTE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)<li data-note="([^"]+)">(.*?)</li>"#));
pub static ORIG_TOKEN: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<span class="orig" data-orig="([^"]+)"></span>"#));
pub static ORIG_STORED: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)<li data-orig="([^"]+)">(.*?)</li>"#));
pub static STEM: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(\d{4})-([^.]+)(\.drawing)?\.html$"));
static CODE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"<a href="[^"]*"(?: [^>]*)?>[\t-\r\x1c-\x1f \x85\xa0\x{1680}\x{2000}-\x{200a}\x{2028}\x{2029}\x{202f}\x{205f}\x{3000}]*<code>([a-z0-9][a-z0-9-]*)</code>[\t-\r\x1c-\x1f \x85\xa0\x{1680}\x{2000}-\x{200a}\x{2028}\x{2029}\x{202f}\x{205f}\x{3000}]*</a>"#,
    )
});
pub static HREF: LazyLock<Regex> = LazyLock::new(|| re(r#"<a href="([^"]+)""#));
pub static PASSAGE: LazyLock<Regex> =
    LazyLock::new(|| re("\"([^\"]+)\"|\u{201c}([^\u{201d}]+)\u{201d}"));
static SENTENCE_END: LazyLock<Regex> = LazyLock::new(|| {
    re("[.!?\u{3002}][\"\u{201d}\u{2019})]*((?: \\[\\^[\\w.-]+\\])*)(?= [A-Z\"\u{201c}(]|$)")
});
static QUOTED: LazyLock<Regex> = LazyLock::new(|| {
    re("\u{300c}([^\u{300c}\u{300d}]+)\u{300d}|\"([^\"]+)\"|\u{201c}([^\u{201d}]+)\u{201d}")
});

/// `re.findall` of a one- or two-group pattern, each match's group 1 (and 2).
#[must_use]
pub fn pairs_of(pattern: &Regex, text: &str) -> Vec<(String, String)> {
    pattern
        .captures_iter(text)
        .flatten()
        .map(|c| {
            (
                c.get(1).map_or_else(String::new, |g| g.as_str().to_owned()),
                c.get(2).map_or_else(String::new, |g| g.as_str().to_owned()),
            )
        })
        .collect()
}

/// A dict: insertion order kept, a key set again keeps its place.
#[derive(Debug, Clone)]
pub struct Keyed<V> {
    keys: Vec<String>,
    map: HashMap<String, V>,
}

impl<V> Default for Keyed<V> {
    fn default() -> Self {
        Self {
            keys: Vec::new(),
            map: HashMap::new(),
        }
    }
}

impl<V> Keyed<V> {
    #[must_use]
    pub fn get(&self, key: &str) -> Option<&V> {
        self.map.get(key)
    }

    pub fn insert(&mut self, key: String, value: V) {
        if !self.map.contains_key(&key) {
            self.keys.push(key.clone());
        }
        self.map.insert(key, value);
    }

    /// Inserts each `(key, value)` in turn.
    pub fn extend<I: IntoIterator<Item = (String, V)>>(&mut self, items: I) {
        for (k, v) in items {
            self.insert(k, v);
        }
    }

    #[must_use]
    pub fn contains(&self, key: &str) -> bool {
        self.map.contains_key(key)
    }

    pub fn iter(&self) -> impl Iterator<Item = (&String, &V)> {
        self.keys.iter().map(|k| (k, &self.map[k]))
    }
}

/// `hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]`.
#[must_use]
pub fn digest(parts: &[&str]) -> String {
    sha256::hex(parts.join("\x1f").as_bytes())
        .chars()
        .take(16)
        .collect()
}

fn digest_of<S: AsRef<str>>(parts: &[S]) -> String {
    digest(&parts.iter().map(AsRef::as_ref).collect::<Vec<_>>())
}

/// `dict(findall)` of a stored-originals file: the last of a key wins.
fn stored_table(originals: &str) -> HashMap<String, String> {
    pairs_of(&ORIG_STORED, originals).into_iter().collect()
}

/// The notes with their originals put back, token by token.
#[must_use]
pub fn restored<S: std::hash::BuildHasher>(notes: &str, table: &HashMap<String, String, S>) -> String {
    ORIG_TOKEN
        .replace_all(notes, |c: &Captures| {
            table.get(&c[1]).cloned().unwrap_or_default()
        })
        .into_owned()
}

/// key -> the note's words, with its originals put back (a changed original is a changed note).
#[must_use]
pub fn read_notes(notes: &str, originals: &str) -> Keyed<String> {
    let body = restored(notes, &stored_table(originals));
    let mut out = Keyed::default();
    for (key, text) in pairs_of(&NOTE, &body) {
        out.insert(key, words(&text));
    }
    out
}

/// What `source-reader` reads of a note: the pages it opens and the passages it looks for on them; "" where it quotes nothing it can find.
pub fn reading<S: std::hash::BuildHasher>(body: &str, originals: &HashMap<String, String, S>) -> String {
    let origs: Vec<String> = ORIG_TOKEN
        .captures_iter(body)
        .flatten()
        .map(|c| originals.get(&c[1]).cloned().unwrap_or_default())
        .collect();
    let passages: Vec<String> = if origs.is_empty() {
        let token_free = ORIG_TOKEN.replace_all(body, "");
        let bare = TAG.replace_all(&token_free, "");
        pairs_of(&PASSAGE, &unescape(&bare))
            .into_iter()
            .map(|(a, b)| if a.is_empty() { b } else { a })
            .collect()
    } else {
        origs
    };
    if passages.is_empty() {
        return String::new();
    }
    let mut parts: Vec<String> = pairs_of(&HREF, body).into_iter().map(|p| p.0).collect();
    parts.push("\x1e".to_owned());
    parts.extend(passages.iter().map(|p| words(p)));
    digest_of(&parts)
}

/// What one notes file holds: its notes' words, the keys each cites, what `source-reader` reads of each, the URLs each links.
#[derive(Clone)]
pub struct NotesParse {
    notes: Keyed<String>,
    cites: Keyed<Vec<String>>,
    readings: Keyed<String>,
    links: Keyed<Vec<String>>,
}

fn notes_parse(text: &str, originals: &str) -> NotesParse {
    let table = stored_table(originals);
    let (mut cites, mut readings, mut links) =
        (Keyed::default(), Keyed::default(), Keyed::default());
    for (key, body) in pairs_of(&NOTE, text) {
        let mut keys: Vec<String> = Vec::new();
        for c in CODE.captures_iter(&body).flatten() {
            if !keys.iter().any(|k| k == &c[1]) {
                keys.push(c[1].to_owned());
            }
        }
        cites.insert(key.clone(), keys);
        readings.insert(key.clone(), reading(&body, &table));
        links.insert(
            key,
            pairs_of(&HREF, &body).into_iter().map(|p| p.0).collect(),
        );
    }
    NotesParse {
        notes: read_notes(text, originals),
        cites,
        readings,
        links,
    }
}

/// The subject of a `STEM` match: its number, `.drawing` where it has it.
fn subject_of(c: &Captures) -> String {
    format!(
        "{}{}",
        &c[1],
        if c.get(3).is_some() { ".drawing" } else { "" }
    )
}

/// The subject a file name's stem names, and its slug, or None for no question page's name.
pub fn stem_of(name: &str) -> Option<(String, String)> {
    STEM.captures(name)
        .ok()
        .flatten()
        .map(|c| (subject_of(&c), c[2].to_owned()))
}

/// THE PARSES OF A RUN, KEPT BY THEIR TEXT (feature 449 T87, measured 2026-11-10 on this clone: `record-owed` read the record four times -
/// the merge base and the tree, for the listing and again for what is unanswered - 7.5 s against the Python's 2.5 s with its disk cache;
/// the base and the tree share nearly every file). In memory only, for the process: a text is its own key, so nothing kept is stale.
static PAGES: LazyLock<std::sync::Mutex<HashMap<String, Page>>> = LazyLock::new(Default::default);
/// A notes file and its originals, the key of its kept parse.
type NotesKey = (String, String);
static NOTES: LazyLock<std::sync::Mutex<HashMap<NotesKey, std::sync::Arc<NotesParse>>>> =
    LazyLock::new(Default::default);
/// Past this many texts a kept table starts again: the door lives a whole run, and a run reads two revisions.
const KEPT: usize = if cfg!(test) { 8 } else { 20_000 };

fn page_kept(text: &str) -> Page {
    let mut kept = PAGES
        .lock()
        .unwrap_or_else(std::sync::PoisonError::into_inner);
    if let Some(p) = kept.get(text) {
        return p.clone();
    }
    if kept.len() >= KEPT {
        kept.clear();
    }
    let page = read_page(text);
    kept.insert(text.to_owned(), page.clone());
    page
}

fn notes_kept(text: &str, originals: &str) -> std::sync::Arc<NotesParse> {
    let key = (text.to_owned(), originals.to_owned());
    let mut kept = NOTES
        .lock()
        .unwrap_or_else(std::sync::PoisonError::into_inner);
    if let Some(p) = kept.get(&key) {
        return p.clone();
    }
    if kept.len() >= KEPT {
        kept.clear();
    }
    let parsed = std::sync::Arc::new(notes_parse(text, originals));
    kept.insert(key, parsed.clone());
    parsed
}

/// The record as the checks read it (`record_units.Record`): pages by their stem, notes by stem, write-ups by key.
#[derive(Default)]
pub struct Record {
    pub pages: Keyed<Page>,
    pub notes: Keyed<Keyed<String>>,
    pub slugs: Keyed<String>,
    pub sources: Keyed<String>,
    pub cites: Keyed<Keyed<Vec<String>>>,
    pub readings: Keyed<Keyed<String>>,
    pub links: Keyed<Keyed<Vec<String>>>,
}

impl Record {
    /// From each question file's name and text, and each write-up's key and text (`record_units.Record.of`).
    pub fn of(files: &Keyed<String>, sources: &Keyed<String>) -> Self {
        let mut rec = Self::default();
        for (name, text) in files.iter() {
            if let Some(stem) = name.strip_suffix(".notes.html") {
                if let Some((subject, _)) = stem_of(&format!("{stem}.html")) {
                    let originals = files
                        .get(&format!("{stem}.originals.html"))
                        .map_or("", String::as_str);
                    let parsed = notes_kept(text, originals);
                    rec.notes.insert(subject.clone(), parsed.notes.clone());
                    rec.cites.insert(subject.clone(), parsed.cites.clone());
                    rec.readings
                        .insert(subject.clone(), parsed.readings.clone());
                    rec.links.insert(subject, parsed.links.clone());
                }
                continue;
            }
            if let Some((subject, slug)) = stem_of(name) {
                rec.pages.insert(subject.clone(), page_kept(text));
                rec.slugs.insert(subject, slug);
            }
        }
        for (key, text) in sources.iter() {
            rec.sources.insert(key.clone(), words(text));
        }
        rec
    }
}

/// Every heading, block and note's words in a record: what "stands nowhere at the base" is asked of.
#[derive(Default)]
struct Index {
    headings: HashSet<String>,
    blocks: HashSet<String>,
    notes: HashSet<String>,
}

fn index_of(rec: &Record) -> Index {
    let mut ix = Index::default();
    for (_, page) in rec.pages.iter() {
        ix.headings.insert(page.heading.clone());
        ix.blocks
            .extend(page.blocks.iter().map(|b| b.words.clone()));
    }
    for (_, notes) in rec.notes.iter() {
        ix.notes.extend(notes.iter().map(|(_, v)| v.clone()));
    }
    ix
}

/// The question a subject belongs to: `0094.drawing#k` -> `0094`.
#[must_use]
pub fn question(subject: &str) -> String {
    let head = subject.split('#').next().unwrap_or("");
    head.split('.').next().unwrap_or("").to_owned()
}

/// One owed check on one subject: `<check>:<subject>`, with what made it due and its fingerprint.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Unit {
    pub slug: String,
    pub occasion: String,
    pub fingerprint: String,
    pub reading: String,
}

impl Unit {
    #[must_use]
    pub fn check(&self) -> &str {
        self.slug
            .split_once(':')
            .map_or(self.slug.as_str(), |p| p.0)
    }

    #[must_use]
    pub fn subject(&self) -> &str {
        self.slug.split_once(':').map_or("", |p| p.1)
    }

    /// The unit for a Python caller; a slug with no colon has no `subject`, which the Python's raised on reading.
    #[must_use]
    pub fn json(&self) -> Value {
        let mut v = json!({
            "slug": self.slug,
            "occasion": self.occasion,
            "fingerprint": self.fingerprint,
            "reading": self.reading,
            "check": self.check(),
        });
        if let (Some(m), Some((_, subject))) = (v.as_object_mut(), self.slug.split_once(':')) {
            m.insert("subject".to_owned(), json!(subject));
        }
        v
    }
}

/// What the units owed so far say: the first occasion of each slug, and the slugs owed because a link moved.
#[derive(Default)]
struct Owing {
    out: Vec<(String, String)>,
    seen: HashSet<String>,
    moved: HashSet<String>,
}

impl Owing {
    fn owe(&mut self, slug: String, why: &str) {
        if self.seen.insert(slug.clone()) {
            self.out.push((slug, why.to_owned()));
        }
    }
}

fn notes_of<'a>(rec: &'a Record, stem: &str) -> Option<&'a Keyed<String>> {
    rec.notes.get(stem)
}

fn owe_page(now: &Record, base: &Record, ix: &Index, stem: &str, page: &Page, owing: &mut Owing) {
    let q = question(stem);
    if !stem.ends_with(".drawing") && !ix.headings.contains(&page.heading) {
        owing.owe(format!("intro-check:{q}"), "the heading is new or changed");
    }
    for b in &page.blocks {
        if ix.blocks.contains(&b.words) {
            continue;
        }
        owing.owe(format!("record-format:{q}"), "visible words new or changed");
        if b.intro {
            owing.owe(format!("intro-check:{q}"), "the intro is new or changed");
        } else if b.marks.is_empty() {
            owing.owe(
                format!("quote-check:{stem}#unfootnoted"),
                "a block with no note mark changed (an uncited claim?)",
            );
        } else {
            for k in &b.marks {
                owing.owe(
                    format!("quote-check:{stem}#{k}"),
                    "a block carrying this note changed (SUPPORTS)",
                );
            }
        }
    }
    let Some(notes) = notes_of(now, stem) else {
        return;
    };
    let base_links = base.links.get(stem);
    for (k, w) in notes.iter() {
        let is_new = !ix.notes.contains(w);
        let was = base_links.and_then(|l| l.get(k));
        let is = now.links.get(stem).and_then(|l| l.get(k));
        let link_moved =
            !is_new && notes_of(base, stem).is_some_and(|n| n.contains(k)) && was != is;
        if is_new {
            if !w.contains(ABSENCE) {
                owing.owe(
                    format!("source-reader:{stem}#{k}"),
                    "the note is new or changed",
                );
            }
            owing.owe(
                format!("quote-check:{stem}#{k}"),
                "the note is new or changed",
            );
            owing.owe(format!("record-format:{q}"), "visible words new or changed");
        }
        if link_moved {
            let slug = format!("quote-check:{stem}#{k}");
            owing.owe(
                slug.clone(),
                "the note's link changed (READABLE on the page it now opens)",
            );
            owing.moved.insert(slug);
        }
    }
}

/// THE DECISION: every unit `now` owes against `base`, each with its occasion and fingerprint, sorted by slug (`record_units.owed`).
pub fn owed(now: &Record, base: &Record) -> Vec<Unit> {
    let ix = index_of(base);
    let mut owing = Owing::default();
    for (stem, page) in now.pages.iter() {
        owe_page(now, base, &ix, stem, page, &mut owing);
    }
    let mut held: HashMap<&str, &str> = HashMap::new();
    for (s, _) in now.pages.iter().filter(|(s, _)| !s.ends_with(".drawing")) {
        held.insert(now.slugs.get(s).map_or("", String::as_str), s);
    }
    for (stem, page) in base
        .pages
        .iter()
        .filter(|(s, p)| !s.ends_with(".drawing") && !p.intro().is_empty())
    {
        let slug = base.slugs.get(stem).map_or("", String::as_str);
        if let Some(h) = held.get(slug) {
            if now.pages.get(h).map_or("", Page::intro) != page.intro() {
                owing.owe(
                    format!("intro-check:{}", question(h)),
                    "the intro is removed or changed",
                );
            }
        }
    }
    for (key, w) in now.sources.iter() {
        if base.sources.get(key) != Some(w) {
            owing.owe(
                format!("source-applicability:{key}"),
                "the write-up is new or its visible words changed",
            );
        }
    }
    let mut out: Vec<Unit> = owing
        .out
        .iter()
        .map(|(slug, why)| {
            if owing.moved.contains(slug) && why.starts_with("the note's link changed") {
                let (stem, note) = slug
                    .split_once(':')
                    .map_or(("", ""), |p| p.1.split_once('#').unwrap_or((p.1, "")));
                let mut parts = vec![fingerprint(now, slug), "\x1e".to_owned()];
                if let Some(links) = now.links.get(stem).and_then(|l| l.get(note)) {
                    parts.extend(links.iter().cloned());
                }
                return Unit {
                    slug: slug.clone(),
                    occasion: why.clone(),
                    fingerprint: digest_of(&parts),
                    reading: String::new(),
                };
            }
            Unit {
                slug: slug.clone(),
                occasion: why.clone(),
                fingerprint: fingerprint(now, slug),
                reading: reading_of(now, slug),
            }
        })
        .collect();
    out.sort_by(|a, b| a.slug.cmp(&b.slug));
    out
}

/// The sentences of a block that carry `[^note]`: what a quote-check of that note judges the quotation against.
pub fn claims_of(block_words: &str, note: &str) -> Vec<String> {
    let (mut out, mut start) = (Vec::new(), 0);
    let mark = format!("[^{note}]");
    for m in SENTENCE_END.find_iter(block_words).flatten() {
        let sentence = strip(&block_words[start..m.end()]);
        if sentence.contains(&mark) {
            out.push(sentence.to_owned());
        }
        start = m.end();
    }
    let tail = strip(&block_words[start..]);
    if tail.contains(&mark) {
        out.push(tail.to_owned());
    }
    out
}

fn note_of<'a>(rec: &'a Record, stem: &str, note: &str) -> &'a str {
    rec.notes
        .get(stem)
        .and_then(|n| n.get(note))
        .map_or("", String::as_str)
}

fn blocks_carrying(rec: &Record, stem: &str, note: &str) -> Vec<String> {
    rec.pages.get(stem).map_or_else(Vec::new, |p| {
        p.blocks
            .iter()
            .filter(|b| b.marks.iter().any(|m| m == note))
            .map(|b| b.words.clone())
            .collect()
    })
}

fn stem_note(subject: &str) -> (&str, &str) {
    subject.split_once('#').unwrap_or((subject, ""))
}

/// A unit's `reading`, the narrower words an answer still holds for under another fingerprint; "" for every other check.
#[must_use]
pub fn reading_of(rec: &Record, slug: &str) -> String {
    let (check, subject) = slug.split_once(':').unwrap_or(("", ""));
    let (stem, note) = stem_note(subject);
    if check == "quote-check" && note != "unfootnoted" {
        let mut parts = vec![
            "quote-check".to_owned(),
            note_of(rec, stem, note).to_owned(),
        ];
        for w in blocks_carrying(rec, stem, note) {
            parts.extend(claims_of(&w, note));
        }
        return digest_of(&parts);
    }
    if check == "source-reader" {
        return rec
            .readings
            .get(stem)
            .and_then(|r| r.get(note))
            .cloned()
            .unwrap_or_default();
    }
    String::new()
}

/// A quote-check note's QUOTATION AND ITS CLAIM, and nothing else (feature 399).
pub fn quotation_key(rec: &Record, slug: &str) -> String {
    let (stem, note) = stem_note(slug.split_once(':').map_or("", |p| p.1));
    let w = note_of(rec, stem, note);
    let mut parts = vec!["quotation".to_owned()];
    if let Some(keys) = rec.cites.get(stem).and_then(|c| c.get(note)) {
        parts.extend(keys.iter().cloned());
    }
    parts.push("\x1e".to_owned());
    for c in QUOTED.captures_iter(w).flatten() {
        parts.push(
            (1..=3)
                .find_map(|i| c.get(i))
                .map_or_else(String::new, |g| g.as_str().to_owned()),
        );
    }
    parts.push("\x1e".to_owned());
    for b in blocks_carrying(rec, stem, note) {
        parts.extend(claims_of(&b, note));
    }
    digest_of(&parts)
}

/// A hash of exactly the words the unit's check reads.
pub fn fingerprint(rec: &Record, slug: &str) -> String {
    let (check, subject) = slug.split_once(':').unwrap_or(("", ""));
    let (stem, note) = stem_note(subject);
    let q = question(subject);
    let empty = Page::default();
    if check == "intro-check" {
        let page = rec.pages.get(&q).unwrap_or(&empty);
        return digest(&[&page.heading, page.intro()]);
    }
    if check == "record-format" {
        let mut parts: Vec<String> = Vec::new();
        for s in [q.clone(), format!("{q}.drawing")] {
            let page = rec.pages.get(&s).unwrap_or(&empty);
            parts.push(page.heading.clone());
            parts.extend(page.blocks.iter().map(|b| b.words.clone()));
            if let Some(notes) = rec.notes.get(&s) {
                let mut kv: Vec<_> = notes.iter().collect();
                kv.sort_by(|a, b| a.0.cmp(b.0));
                parts.extend(kv.iter().map(|(k, v)| format!("{k}={v}")));
            }
        }
        return digest_of(&parts);
    }
    if check == "source-applicability" {
        return digest(&[rec.sources.get(subject).map_or("", String::as_str)]);
    }
    let page = rec.pages.get(stem).unwrap_or(&empty);
    let note_text = note_of(rec, stem, note);
    if check == "source-reader" {
        return digest(&[note_text]);
    }
    if note == "unfootnoted" {
        return digest_of(
            &page
                .blocks
                .iter()
                .filter(|b| b.marks.is_empty() && !b.intro)
                .map(|b| b.words.clone())
                .collect::<Vec<_>>(),
        );
    }
    let mut parts = vec![note_text.to_owned()];
    parts.extend(
        page.blocks
            .iter()
            .filter(|b| b.marks.iter().any(|m| m == note))
            .map(|b| b.words.clone()),
    );
    digest_of(&parts)
}

#[cfg(test)]
mod tests;
