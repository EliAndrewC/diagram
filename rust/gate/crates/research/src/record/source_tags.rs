//! The registry's source tags and the sections they group the works into (`record/source_tags.py`, feature 305; ported by feature 449
//! T144). Every keyed work states `<!-- tags: period=...; region=...; kind=... -->` on its entry's last line, the first value of a facet
//! primary; `research/source-tags.json` holds every value with its label and its standard explanation, `research/source-sections.json`
//! the sections in order, each with a rule over a work's primary tags. The GM's own campaign notes are canon: no tags, one fixed label.

use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::blocked::type_name;
use l7r_shared::html_text::escape;
use l7r_shared::py_text::strip;
use l7r_shared::pyjson::py_str;
use serde_json::Value;

use crate::{caps, re, Error, Result};

pub const VOCABULARY: &str = "source-tags.json";
pub const SECTIONS: &str = "source-sections.json";
pub const FACETS: [&str; 3] = ["period", "region", "kind"];
/// The marker an entry states its tags in, on its last line.
pub static MARKER: LazyLock<Regex> = LazyLock::new(|| re(r"\n?<!-- tags: (.*?) -->[ \t]*"));
/// A section id's prefix, so no section heading can collide with a registry key in the one-page record.
pub const SECTION_PREFIX: &str = "works-";
static ID: LazyLock<Regex> = LazyLock::new(|| re(r"^[a-z0-9][a-z0-9-]*\n?\z"));
/// The markers of the vocabulary block derived into the `source-applicability` contract (spec FR-012).
pub const CONTRACT_OPEN: &str = "<!-- source-tags: DERIVED by make source-tags-contract from research/source-tags.json - edit the vocabulary, never here -->";
pub const CONTRACT_CLOSE: &str = "<!-- /source-tags -->";

fn refused(message: String) -> Error {
    Error::new("SourceTagError", message)
}

fn is_id(text: &str) -> bool {
    ID.is_match(text).unwrap_or(false)
}

/// One value of a facet: its id, its label, its standard explanation.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Label {
    pub id: String,
    pub name: String,
    pub description: String,
}

/// A work's tags, each facet's values in order, the first primary.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SourceTags {
    pub period: Vec<String>,
    pub region: Vec<String>,
    pub kind: Vec<String>,
}

impl SourceTags {
    #[must_use]
    pub fn values(&self, facet: &str) -> &[String] {
        match facet {
            "period" => &self.period,
            "region" => &self.region,
            _ => &self.kind,
        }
    }

    #[must_use]
    pub fn primary(&self, facet: &str) -> &str {
        &self.values(facet)[0]
    }

    #[must_use]
    pub fn marker(&self) -> String {
        let parts: Vec<String> = FACETS
            .iter()
            .map(|f| format!("{f}={}", self.values(f).join(",")))
            .collect();
        format!("<!-- tags: {} -->", parts.join("; "))
    }
}

/// Each facet's values in the order their labels show, and the canon label.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Vocabulary {
    pub facets: Vec<(String, Vec<Label>)>,
    pub canon: Label,
}

impl Vocabulary {
    /// A facet's labels in order.
    #[must_use]
    pub fn labels(&self, facet: &str) -> &[Label] {
        self.facets
            .iter()
            .find(|(f, _)| f == facet)
            .map_or(&[], |(_, l)| l.as_slice())
    }

    /// A facet's values by id (`known`).
    #[must_use]
    pub fn known(&self, facet: &str) -> Vec<(String, Label)> {
        // the loader refused a value declared twice, so each id is here once
        self.labels(facet)
            .iter()
            .map(|l| (l.id.clone(), l.clone()))
            .collect()
    }

    fn label(&self, facet: &str, id: &str) -> Option<Label> {
        self.labels(facet)
            .iter()
            .rev()
            .find(|l| l.id == id)
            .cloned()
    }
}

/// One clause of a section's rule: each facet it tests and the values any of which matches.
pub type Clause = Vec<(String, Vec<String>)>;

/// A works section: its heading, its description, and the clauses it takes works by (none for the canon one).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Section {
    pub id: String,
    pub title: String,
    pub description: String,
    pub canon: bool,
    pub takes: Vec<Clause>,
}

fn read_json(record_dir: &Path, name: &str) -> Result<Value> {
    // a file that is there but not UTF-8 is the Python's `UnicodeDecodeError`, which its `except OSError` lets through - never
    // "missing" (feature 449 T145: the differential's broken-vocabulary case under `make reserve TAGS=`)
    if let Ok(bytes) = std::fs::read(record_dir.join(name)) {
        if let Err(e) = String::from_utf8(bytes) {
            return Err(Error::new("UnicodeDecodeError", e.to_string()));
        }
    }
    let Some(text) = crate::read(&record_dir.join(name)) else {
        let what = if name == VOCABULARY {
            "vocabulary"
        } else {
            "sections"
        };
        return Err(refused(format!(
            "{name}: missing - the record's source {what} is a file, and the build will not invent it"
        )));
    };
    crate::json(&text).map_err(|e| refused(format!("{name}: not JSON ({e})")))
}

fn label(place: &str, raw: &Value) -> Result<Label> {
    let id = raw.get("id").map_or_else(String::new, py_str);
    let (name, description) = (
        raw.get("name").and_then(Value::as_str),
        raw.get("description").and_then(Value::as_str),
    );
    match (raw.is_object() && is_id(&id), name, description) {
        (true, Some(n), Some(d)) => Ok(Label {
            id,
            name: n.to_owned(),
            description: d.to_owned(),
        }),
        _ => Err(refused(format!(
            "{place}: a value is an object with a lower-case `id`, a `name` and a `description`"
        ))),
    }
}

/// `source-tags.json`: each facet a non-empty list of values in label order, and the canon label.
///
/// # Errors
/// A missing or broken file, the wrong keys, an empty facet, a malformed or repeated value.
pub fn load_vocabulary(record_dir: &Path) -> Result<Vocabulary> {
    let data = read_json(record_dir, VOCABULARY)?;
    let ok = data.as_object().is_some_and(|m| {
        m.len() == 4 && m.contains_key("canon") && FACETS.iter().all(|f| m.contains_key(*f))
    });
    if !ok {
        return Err(refused(format!(
            "{VOCABULARY}: holds exactly {} and canon",
            FACETS.join(", ")
        )));
    }
    let mut facets = Vec::new();
    for facet in FACETS {
        let Some(rows) = data[facet].as_array().filter(|r| !r.is_empty()) else {
            return Err(refused(format!(
                "{VOCABULARY}: `{facet}` is a non-empty list, in the order its labels show"
            )));
        };
        let labels: Vec<Label> = rows
            .iter()
            .map(|v| label(&format!("{VOCABULARY} {facet}"), v))
            .collect::<Result<_>>()?;
        let ids: HashSet<&str> = labels.iter().map(|l| l.id.as_str()).collect();
        if ids.len() != labels.len() {
            return Err(refused(format!(
                "{VOCABULARY}: a {facet} value is declared twice"
            )));
        }
        facets.push((facet.to_owned(), labels));
    }
    let canon = label(&format!("{VOCABULARY} canon"), &data["canon"])?;
    Ok(Vocabulary { facets, canon })
}

/// What Python iterates of a value: a list's items, a dict's keys, a string's characters.
fn listed(v: &Value) -> Result<Vec<Value>> {
    match v {
        Value::Array(rows) => Ok(rows.clone()),
        Value::Object(m) => Ok(m.keys().map(|k| Value::from(k.as_str())).collect()),
        Value::String(s) => Ok(s.chars().map(|c| Value::from(c.to_string())).collect()),
        other => Err(Error::new(
            "TypeError",
            format!("'{}' object is not iterable", type_name(other)),
        )),
    }
}

fn clause(place: &str, raw: &Value, vocab: &Vocabulary) -> Result<Clause> {
    let Some(map) = raw.as_object().filter(|m| !m.is_empty()) else {
        return Err(refused(format!(
            "{place}: a clause is an object of {}",
            FACETS.join(", ")
        )));
    };
    let mut out = Clause::new();
    for (facet, value) in map {
        if !FACETS.contains(&facet.as_str()) {
            return Err(refused(format!(
                "{place}: `{facet}` - a clause tests only {}",
                FACETS.join(", ")
            )));
        }
        let values = if value.is_string() {
            vec![value.clone()]
        } else {
            listed(value)?
        };
        let mut kept = Vec::new();
        for v in values {
            let text = py_str(&v);
            if !(v.is_string() && vocab.label(facet, &text).is_some()) {
                return Err(refused(format!(
                    "{place}: `{facet}: {text}` - no {facet} value `{text}` in {VOCABULARY}"
                )));
            }
            kept.push(text);
        }
        out.push((facet.clone(), kept));
    }
    Ok(out)
}

/// `source-sections.json`: the sections in order, each rule checked against the vocabulary; exactly one canon.
///
/// # Errors
/// A missing or broken file, a malformed or repeated section, a section both canon and taking or neither, not exactly one canon.
pub fn load_sections(record_dir: &Path, vocab: &Vocabulary) -> Result<Vec<Section>> {
    let data = read_json(record_dir, SECTIONS)?;
    let Some(rows) = data
        .get("sections")
        .and_then(Value::as_array)
        .filter(|_| data.is_object())
    else {
        return Err(refused(format!(
            "{SECTIONS}: an object with a `sections` list"
        )));
    };
    let mut out: Vec<Section> = Vec::new();
    for raw in rows {
        let sid = if raw.is_object() {
            raw.get("id").map_or_else(String::new, py_str)
        } else {
            String::new()
        };
        if !raw.is_object() || !is_id(&sid) || !sid.starts_with(SECTION_PREFIX) {
            return Err(refused(format!(
                "{SECTIONS}: a section is an object with a lower-case `id` starting `{SECTION_PREFIX}`"
            )));
        }
        let place = format!("{SECTIONS} section `{sid}`");
        if out.iter().any(|s| s.id == sid) {
            return Err(refused(format!("{place}: the id is used twice")));
        }
        let Some(title) = raw
            .get("title")
            .and_then(Value::as_str)
            .filter(|t| !t.is_empty())
        else {
            return Err(refused(format!("{place}: no `title`")));
        };
        let canon = raw.get("canon") == Some(&Value::Bool(true));
        let takes: Vec<Clause> = match raw.get("takes") {
            Some(t) => listed(t)?
                .iter()
                .map(|c| clause(&place, c, vocab))
                .collect::<Result<_>>()?,
            None => Vec::new(),
        };
        if canon != takes.is_empty() {
            return Err(refused(format!(
                "{place}: a section takes works by clauses, or is the canon section with none - not both, not neither"
            )));
        }
        out.push(Section {
            id: sid,
            title: title.to_owned(),
            description: raw.get("description").map_or_else(String::new, py_str),
            canon,
            takes,
        });
    }
    if out.iter().filter(|s| s.canon).count() != 1 {
        return Err(refused(format!(
            "{SECTIONS}: exactly one section is the canon section"
        )));
    }
    Ok(out)
}

/// The tags an entry states, checked against the vocabulary; None if it states none.
///
/// # Errors
/// Two markers, a facet missing, repeated or unknown, a value stated twice, or a value not in the vocabulary (naming the allowed ones).
pub fn parse(text: &str, place: &str, vocab: &Vocabulary) -> Result<Option<SourceTags>> {
    let found = caps(&MARKER, text);
    let Some(first) = found.first() else {
        return Ok(None);
    };
    if found.len() > 1 {
        return Err(refused(format!("{place}: two tags markers")));
    }
    let mut parts: Vec<(String, Vec<String>)> = Vec::new();
    for chunk in first[1].split(';') {
        let chunk = strip(chunk);
        let (key, value) = chunk.split_once('=').unwrap_or((chunk, ""));
        if !chunk.contains('=') || !FACETS.contains(&key) || parts.iter().any(|(k, _)| k == key) {
            return Err(refused(format!(
                "{place}: `{chunk}` - the marker is `period=a; region=x,y; kind=k`, each facet once"
            )));
        }
        parts.push((
            key.to_owned(),
            value
                .split(',')
                .map(strip)
                .filter(|v| !v.is_empty())
                .map(str::to_owned)
                .collect(),
        ));
    }
    let get = |f: &str| {
        parts
            .iter()
            .find(|(k, _)| k == f)
            .map(|p| p.1.clone())
            .unwrap_or_default()
    };
    for facet in FACETS {
        let values = get(facet);
        if values.is_empty() {
            return Err(refused(format!("{place}: no {facet} in its tags")));
        }
        let known: Vec<String> = vocab.known(facet).into_iter().map(|(k, _)| k).collect();
        for v in &values {
            if !known.contains(v) {
                return Err(refused(format!(
                    "{place}: `{facet}={v}` - not a {facet} value; the values are {} ({VOCABULARY})",
                    known.join(", ")
                )));
            }
        }
        if values.iter().collect::<HashSet<_>>().len() != values.len() {
            return Err(refused(format!("{place}: a {facet} value is stated twice")));
        }
    }
    Ok(Some(SourceTags {
        period: get("period"),
        region: get("region"),
        kind: get("kind"),
    }))
}

/// Does any clause of the section take these tags: every facet a clause names matches the primary value.
#[must_use]
pub fn takes(section: &Section, tags: &SourceTags) -> bool {
    section.takes.iter().any(|c| {
        c.iter()
            .all(|(f, values)| values.iter().any(|v| v == tags.primary(f)))
    })
}

/// The section a work lives in: the canon section for a canon work (`tags` None), else the first that takes it.
#[must_use]
pub fn home<'a>(sections: &'a [Section], tags: Option<&SourceTags>) -> Option<&'a Section> {
    match tags {
        None => sections.iter().find(|s| s.canon),
        Some(t) => sections.iter().find(|s| !s.canon && takes(s, t)),
    }
}

/// An entry as the reader sees it: without its tags marker.
#[must_use]
pub fn strip_marker(entry_html: &str) -> String {
    MARKER.replace_all(entry_html, "").into_owned()
}

fn chip(facet: &str, label: &Label) -> String {
    let text = escape(&label.description, true);
    format!(
        r#"<span class="srctag srctag-{facet}" data-def="{text}" title="{text}">{}</span>"#,
        escape(&label.name, true)
    )
}

/// A work's labels, one per value in facet order (the canon label alone for a canon work), each carrying its standard explanation.
#[must_use]
pub fn labels_html(tags: Option<&SourceTags>, vocab: &Vocabulary) -> String {
    let chips: Vec<String> = match tags {
        None => vec![chip("canon", &vocab.canon)],
        Some(t) => FACETS
            .iter()
            .flat_map(|f| {
                t.values(f)
                    .iter()
                    .filter_map(move |v| Some(chip(f, &vocab.label(f, v)?)))
            })
            .collect(),
    };
    format!(r#"<p class="srctags">{}</p>"#, chips.join(" "))
}

/// A section's heading in a list of works, with its description beneath.
#[must_use]
pub fn section_heading(section: &Section, level: usize, anchor: &str) -> String {
    let desc = if section.description.is_empty() {
        String::new()
    } else {
        format!(
            "\n<p class=\"works-section-desc\"><em>{}</em></p>",
            section.description
        )
    };
    format!(
        r#"<h{level} class="works-section" id="{anchor}">{}</h{level}>{desc}"#,
        escape(&section.title, true)
    )
}

/// Every value and its explanation, as the contract lists them, between the markers.
#[must_use]
pub fn contract_block(vocab: &Vocabulary) -> String {
    let mut rows: Vec<String> = FACETS
        .iter()
        .flat_map(|f| {
            vocab
                .labels(f)
                .iter()
                .map(move |l| format!("- `{f}={}` - **{}**: {}", l.id, l.name, l.description))
        })
        .collect();
    rows.push(format!(
        "- (no marker) - **{}**: {}",
        vocab.canon.name, vocab.canon.description
    ));
    format!("{CONTRACT_OPEN}\n{}\n{CONTRACT_CLOSE}", rows.join("\n"))
}

/// `text` with its derived block rewritten from the vocabulary.
///
/// # Errors
/// The markers missing, or the closing one before the opening.
pub fn synced_contract(text: &str, vocab: &Vocabulary) -> Result<String> {
    match (text.find(CONTRACT_OPEN), text.find(CONTRACT_CLOSE)) {
        (Some(start), Some(end)) if end >= start => Ok(format!(
            "{}{}{}",
            &text[..start],
            contract_block(vocab),
            &text[end + CONTRACT_CLOSE.len()..]
        )),
        _ => Err(refused(
            "the contract has no derived source-tags block - its two markers are missing"
                .to_owned(),
        )),
    }
}

/// The id of one kind's run inside a section (feature 307).
#[must_use]
pub fn kind_anchor(section: &Section, kind: &Label) -> String {
    format!("{}-{}", section.id, kind.id)
}

/// A kind's heading inside a section's run of works, its explanation the heading's tooltip; `prefix` scopes its id (feature 312).
#[must_use]
pub fn kind_heading(section: &Section, kind: &Label, level: usize, prefix: &str) -> String {
    format!(
        r#"<h{level} class="works-kind" id="{prefix}{}" title="{}">{}</h{level}>"#,
        kind_anchor(section, kind),
        escape(&kind.description, true),
        escape(&kind.name, true)
    )
}

/// Every registry entry's tags and section, read once a build; `errors` holds every refusal, each naming its entry, and a refused entry has
/// no section and is left out of every list.
#[derive(Debug, Clone)]
pub struct Catalog {
    pub vocab: Vocabulary,
    pub sections: Vec<Section>,
    /// key to its tags (None for a canon work), in the order the entries came.
    pub tags: Vec<(String, Option<SourceTags>)>,
    /// key to its section's id.
    pub section: Vec<(String, String)>,
    pub errors: Vec<String>,
    /// Where each key's tags and section stand in the two lists: the site asks them once a work a page, and a scan of 2,900 entries a
    /// question made the build's registry pages quadratic (feature 449 T148, the site's port measured against the Python's dicts).
    at: HashMap<String, usize>,
}

impl Catalog {
    /// Every entry of `entries` (key, text) read against the vocabulary and the sections; `canon` the GM's own notes' keys.
    ///
    /// # Errors
    /// The vocabulary's or the sections' refusal; an entry's own is kept in `errors`.
    pub fn new(
        record_dir: &Path,
        entries: &[(String, String)],
        canon: &BTreeSet<String>,
        place: &str,
    ) -> Result<Self> {
        let vocab = load_vocabulary(record_dir)?;
        let sections = load_sections(record_dir, &vocab)?;
        let mut cat = Self {
            vocab,
            sections,
            tags: Vec::new(),
            section: Vec::new(),
            errors: Vec::new(),
            at: HashMap::new(),
        };
        for (key, text) in entries {
            let at = format!("{place}/ {key}");
            let tags = match parse(text, &at, &cat.vocab) {
                Ok(t) => t,
                Err(e) => {
                    cat.errors.push(e.message);
                    continue;
                }
            };
            if canon.contains(key) {
                if tags.is_some() {
                    cat.errors.push(format!("{at}: a canon entry (the GM's own notes) carries no tags - remove its marker"));
                    continue;
                }
            } else if tags.is_none() {
                cat.errors.push(format!(
                    "{at}: no tags - every keyed work states `<!-- tags: period=...; region=...; kind=... -->` on its last line ({VOCABULARY})"
                ));
                continue;
            }
            let Some(sec) = home(&cat.sections, tags.as_ref()).map(|s| s.id.clone()) else {
                let t = tags.as_ref().map_or_else(Vec::new, |t| {
                    FACETS
                        .iter()
                        .map(|f| format!("{f}={}", t.primary(f)))
                        .collect()
                });
                cat.errors.push(format!(
                    "{at}: no section of {SECTIONS} takes the primary tags {}",
                    t.join(", ")
                ));
                continue;
            };
            if let Some(&i) = cat.at.get(key) {
                cat.tags[i].1 = tags;
                cat.section[i].1 = sec;
            } else {
                cat.at.insert(key.clone(), cat.tags.len());
                cat.tags.push((key.clone(), tags));
                cat.section.push((key.clone(), sec));
            }
        }
        Ok(cat)
    }

    /// A key's tags; none for a canon work or a key the catalog does not hold.
    #[must_use]
    pub fn tags_of(&self, key: &str) -> Option<&SourceTags> {
        self.at.get(key).and_then(|i| self.tags[*i].1.as_ref())
    }

    /// The id of a key's section; none for a key the catalog refused or does not hold.
    #[must_use]
    pub fn section_of(&self, key: &str) -> Option<&str> {
        self.at.get(key).map(|i| self.section[*i].1.as_str())
    }

    /// A work's labels; "" for a key with no section.
    #[must_use]
    pub fn labels(&self, key: &str) -> String {
        if self.section_of(key).is_some() {
            labels_html(self.tags_of(key), &self.vocab)
        } else {
            String::new()
        }
    }

    /// `keys` under their primary KIND in the vocabulary's order, each keeping the order given; untagged keys - the canon - under none.
    #[must_use]
    pub fn by_kind(&self, keys: &[String]) -> Vec<(Option<Label>, Vec<String>)> {
        let untagged: Vec<String> = keys
            .iter()
            .filter(|k| self.tags_of(k).is_none())
            .cloned()
            .collect();
        let mut out = Vec::new();
        if !untagged.is_empty() {
            out.push((None, untagged));
        }
        for lab in self.vocab.labels("kind") {
            let run: Vec<String> = keys
                .iter()
                .filter(|k| self.tags_of(k).is_some_and(|t| t.primary("kind") == lab.id))
                .cloned()
                .collect();
            if !run.is_empty() {
                out.push((Some(lab.clone()), run));
            }
        }
        out
    }

    /// Every id the nested sources may use: each section's, and each section-and-kind's.
    #[must_use]
    pub fn anchors(&self) -> Vec<String> {
        let mut out = Vec::new();
        for s in &self.sections {
            out.push(s.id.clone());
            out.extend(self.vocab.labels("kind").iter().map(|l| kind_anchor(s, l)));
        }
        out
    }

    /// `keys` under their sections in the sections' order, each keeping the order given; an empty section and a refused key left out.
    #[must_use]
    pub fn grouped(&self, keys: &[String]) -> Vec<(Section, Vec<String>)> {
        self.sections
            .iter()
            .filter_map(|s| {
                let run: Vec<String> = keys
                    .iter()
                    .filter(|k| self.section_of(k) == Some(s.id.as_str()))
                    .cloned()
                    .collect();
                (!run.is_empty()).then(|| (s.clone(), run))
            })
            .collect()
    }
}

#[cfg(test)]
mod tests;
