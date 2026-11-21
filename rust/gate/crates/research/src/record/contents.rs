//! The record's vocabulary and its table of contents (`record/contents.py`, feature 303; ported by feature 449 T144). A question carries
//! TAGS from `research/tags.json`; `research/contents.json` declares the sections, their nesting and a RULE over the tags; a question lives
//! in the first section, depth-first, whose rule takes it (the GM, 2026-10-01: regrouping is *"just a straightforward change"*). Nothing
//! about grouping is written anywhere else, and every refusal names the file.
//!
//! The Python's sections hold a parent pointer; here a section is owned by its parent, its ancestors found by [`path`], and a section is
//! named by its id (the ids are unique, refused otherwise), where the Python compared by identity.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::blocked::type_name;
use l7r_shared::py_text::strip;
use l7r_shared::pyjson::{dumps, py_str, sorted};
use serde_json::{Map, Value};

use crate::{caps, re, Error, Result};

pub const TAGS: &str = "tags.json";
pub const CONTENTS: &str = "contents.json";
pub const FACETS: [&str; 3] = ["subject", "setting", "level"];
/// What a clause of a section's rule may test: the primary subject, any subject, any setting, the level.
pub const CLAUSE_KEYS: [&str; 4] = ["primary", "subject", "setting", "level"];
/// The marker a page states its tags in, on the line after its heading.
pub static MARKER: LazyLock<Regex> = LazyLock::new(|| re(r"<!-- tags: (.*?) -->"));
static ID: LazyLock<Regex> = LazyLock::new(|| re(r"^[a-z0-9][a-z0-9-]*\n?\z"));

fn refused(message: String) -> Error {
    Error::new("ContentsError", message)
}

/// A question's tags: its subjects (the first is primary), its settings, its level.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Tags {
    pub subjects: Vec<String>,
    pub settings: Vec<String>,
    pub level: String,
}

impl Tags {
    #[must_use]
    pub fn primary(&self) -> &str {
        &self.subjects[0]
    }

    /// Every (facet, tag) the question carries - what its tag pages are.
    #[must_use]
    pub fn all(&self) -> Vec<(&'static str, String)> {
        let mut out: Vec<(&'static str, String)> = self
            .subjects
            .iter()
            .map(|s| ("subject", s.clone()))
            .collect();
        out.extend(self.settings.iter().map(|s| ("setting", s.clone())));
        out.push(("level", self.level.clone()));
        out
    }

    #[must_use]
    pub fn marker(&self) -> String {
        format!(
            "<!-- tags: subject={}; setting={}; level={} -->",
            self.subjects.join(","),
            self.settings.join(","),
            self.level
        )
    }
}

/// One tag of the vocabulary.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Tag {
    pub id: String,
    pub name: String,
    pub description: String,
}

/// The three facets: subjects and settings by id in file order, levels in presentation order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Vocabulary {
    pub subject: Vec<(String, Tag)>,
    pub setting: Vec<(String, Tag)>,
    pub level: Vec<Tag>,
}

impl Vocabulary {
    /// A facet's tags by id.
    #[must_use]
    pub fn facet(&self, name: &str) -> Vec<(String, Tag)> {
        match name {
            "level" => self
                .level
                .iter()
                .map(|t| (t.id.clone(), t.clone()))
                .collect(),
            "setting" => self.setting.clone(),
            _ => self.subject.clone(),
        }
    }

    fn knows(&self, facet: &str, id: &str) -> bool {
        match facet {
            "level" => self.level.iter().any(|t| t.id == id),
            "setting" => self.setting.iter().any(|(k, _)| k == id),
            _ => self.subject.iter().any(|(k, _)| k == id),
        }
    }

    /// A level's place in the presentation order.
    ///
    /// # Errors
    /// A level the vocabulary does not hold (Python's `list.index`).
    pub fn level_rank(&self, level: &str) -> Result<usize> {
        self.level
            .iter()
            .position(|t| t.id == level)
            .ok_or_else(|| Error::new("ValueError", "list.index(x): x not in list"))
    }
}

/// One clause of a rule: each key it tests and the values any of which matches.
pub type Clause = Vec<(String, Vec<String>)>;

/// A section of the table of contents: its words in each half, the rule it takes questions by, its subsections, and why its rule may
/// match nothing yet (`awaiting`, feature 389).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Section {
    pub id: String,
    pub title: String,
    pub description: String,
    pub drawing_description: String,
    pub takes: Vec<Clause>,
    pub sections: Vec<Section>,
    pub awaiting: String,
}

/// The section `id` and its ancestors, outermost first; empty where no section has the id.
#[must_use]
pub fn path<'a>(sections: &'a [Section], id: &str) -> Vec<&'a Section> {
    for s in sections {
        if s.id == id {
            return vec![s];
        }
        let below = path(&s.sections, id);
        if !below.is_empty() {
            let mut out = vec![s];
            out.extend(below);
            return out;
        }
    }
    Vec::new()
}

fn read_json(record_dir: &Path, name: &str) -> Result<Value> {
    let Some(text) = crate::read(&record_dir.join(name)) else {
        let what = if name == TAGS {
            "vocabulary"
        } else {
            "table of contents"
        };
        return Err(refused(format!(
            "{name}: missing - the record's {what} is a file, and the build will not invent it"
        )));
    };
    crate::json(&text).map_err(|e| refused(format!("{name}: not JSON ({e})")))
}

fn is_id(text: &str) -> bool {
    ID.is_match(text).unwrap_or(false)
}

fn tag(name: &str, facet: &str, tid: &str, body: &Value) -> Result<Tag> {
    let named = body.get("name").and_then(Value::as_str);
    match (is_id(tid), body.as_object(), named) {
        (true, Some(map), Some(n)) => Ok(Tag {
            id: tid.to_owned(),
            name: n.to_owned(),
            description: map.get("description").map_or_else(String::new, py_str),
        }),
        _ => Err(refused(format!(
            "{name}: {facet} `{tid}` - a tag is a lower-case id with a `name` and a `description`"
        ))),
    }
}

fn items_of(v: &Value) -> Result<&Map<String, Value>> {
    v.as_object().ok_or_else(|| {
        Error::new(
            "AttributeError",
            format!("'{}' object has no attribute 'items'", type_name(v)),
        )
    })
}

/// `tags.json`: every tag of the three facets; levels a list, their order the presentation order.
///
/// # Errors
/// A missing or broken file, a facet missing or extra, an empty level list, a malformed tag.
pub fn load_vocabulary(record_dir: &Path) -> Result<Vocabulary> {
    let data = read_json(record_dir, TAGS)?;
    let ok = data
        .as_object()
        .is_some_and(|m| m.len() == 3 && FACETS.iter().all(|f| m.contains_key(*f)));
    if !ok {
        return Err(refused(format!(
            "{TAGS}: holds exactly the facets {}",
            FACETS.join(", ")
        )));
    }
    let facet = |f: &str| -> Result<Vec<(String, Tag)>> {
        items_of(&data[f])?
            .iter()
            .map(|(k, v)| Ok((k.clone(), tag(TAGS, f, k, v)?)))
            .collect()
    };
    let (subject, setting) = (facet("subject")?, facet("setting")?);
    let levels = match &data["level"] {
        Value::Array(rows) if !rows.is_empty() => rows,
        _ => {
            return Err(refused(format!(
                "{TAGS}: `level` is a list, in presentation order"
            )))
        }
    };
    let level = levels
        .iter()
        .map(|x| {
            let id = if x.is_object() {
                x.get("id").map_or_else(String::new, py_str)
            } else {
                String::new()
            };
            tag(TAGS, "level", &id, x)
        })
        .collect::<Result<_>>()?;
    Ok(Vocabulary {
        subject,
        setting,
        level,
    })
}

/// What Python iterates of a value: a list's items, a dict's keys, a string's characters - or, where the Python first wrapped a string
/// in a list (`[value] if isinstance(value, str)`), the string whole.
fn listed(v: &Value, whole: bool) -> Result<Vec<Value>> {
    match v {
        Value::Array(rows) => Ok(rows.clone()),
        Value::Object(m) => Ok(m.keys().map(|k| Value::from(k.as_str())).collect()),
        Value::String(s) if whole => Ok(vec![Value::from(s.as_str())]),
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
            CLAUSE_KEYS.join(", ")
        )));
    };
    let mut out = Clause::new();
    for (key, value) in map {
        if !CLAUSE_KEYS.contains(&key.as_str()) {
            return Err(refused(format!(
                "{place}: `{key}` - a clause tests only {}",
                CLAUSE_KEYS.join(", ")
            )));
        }
        let facet = if key == "primary" || key == "subject" {
            "subject"
        } else {
            key.as_str()
        };
        let mut values = Vec::new();
        for v in listed(value, true)? {
            let text = py_str(&v);
            if !(v.is_string() && vocab.knows(facet, &text)) {
                return Err(refused(format!(
                    "{place}: `{key}: {text}` - no {facet} tag `{text}` in {TAGS}"
                )));
            }
            values.push(text);
        }
        out.push((key.clone(), values));
    }
    Ok(out)
}

fn section(raw: &Value, vocab: &Vocabulary, seen: &mut Vec<String>) -> Result<Section> {
    let sid = raw.get("id").map_or_else(String::new, py_str);
    if !raw.is_object() || !is_id(&sid) {
        return Err(refused(format!(
            "{CONTENTS}: a section is an object with a lower-case `id`"
        )));
    }
    let place = format!("{CONTENTS} section `{sid}`");
    if seen.contains(&sid) {
        return Err(refused(format!("{place}: the id is used twice")));
    }
    seen.push(sid.clone());
    let Some(title) = raw
        .get("title")
        .and_then(Value::as_str)
        .filter(|t| !t.is_empty())
    else {
        return Err(refused(format!("{place}: no `title`")));
    };
    let takes = match raw.get("takes") {
        Some(t) => listed(t, false)?
            .iter()
            .map(|c| clause(&place, c, vocab))
            .collect::<Result<_>>()?,
        None => Vec::new(),
    };
    let sections = match raw.get("sections") {
        Some(s) => listed(s, false)?
            .iter()
            .map(|c| section(c, vocab, seen))
            .collect::<Result<_>>()?,
        None => Vec::new(),
    };
    if takes.is_empty() && sections.is_empty() {
        return Err(refused(format!("{place}: takes nothing and holds nothing")));
    }
    let text = |k: &str| raw.get(k).map_or_else(String::new, py_str);
    Ok(Section {
        id: sid,
        title: title.to_owned(),
        description: text("description"),
        drawing_description: text("drawing_description"),
        takes,
        sections,
        awaiting: text("awaiting"),
    })
}

/// `contents.json`: the sections in order, each rule checked against the vocabulary.
///
/// # Errors
/// A missing or broken file, or any section or clause the contract refuses.
pub fn load_contents(record_dir: &Path, vocab: &Vocabulary) -> Result<Vec<Section>> {
    let data = read_json(record_dir, CONTENTS)?;
    let Some(rows) = data
        .get("sections")
        .and_then(Value::as_array)
        .filter(|_| data.is_object())
    else {
        return Err(refused(format!(
            "{CONTENTS}: an object with a `sections` list"
        )));
    };
    let mut seen = Vec::new();
    rows.iter().map(|s| section(s, vocab, &mut seen)).collect()
}

/// `contents.json`'s `opening`: the HTML the record's home page opens with (feature 424); absent, none.
///
/// # Errors
/// A missing or broken file, or an opening that is not text.
pub fn load_opening(record_dir: &Path) -> Result<String> {
    let data = read_json(record_dir, CONTENTS)?;
    match data.as_object().and_then(|m| m.get("opening")) {
        None => Ok(String::new()),
        Some(Value::String(s)) => Ok(s.clone()),
        Some(_) => Err(refused(format!(
            "{CONTENTS}: `opening` is the home page's opening, as HTML text"
        ))),
    }
}

/// Every section, depth-first in contents order.
#[must_use]
pub fn walk(sections: &[Section]) -> Vec<&Section> {
    let mut out = Vec::new();
    for s in sections {
        out.push(s);
        out.extend(walk(&s.sections));
    }
    out
}

/// Does one clause match: every key it tests.
#[must_use]
pub fn matches(clause: &Clause, tags: &Tags) -> bool {
    clause.iter().all(|(key, values)| {
        let have: Vec<&str> = match key.as_str() {
            "primary" => vec![tags.primary()],
            "subject" => tags.subjects.iter().map(String::as_str).collect(),
            "setting" => tags.settings.iter().map(String::as_str).collect(),
            _ => vec![tags.level.as_str()],
        };
        values.iter().any(|v| have.contains(&v.as_str()))
    })
}

#[must_use]
pub fn takes(section: &Section, tags: &Tags) -> bool {
    section.takes.iter().any(|c| matches(c, tags))
}

/// The first section, depth-first, whose rule takes these tags (spec FR-010).
#[must_use]
pub fn home<'a>(sections: &'a [Section], tags: &Tags) -> Option<&'a Section> {
    walk(sections).into_iter().find(|s| takes(s, tags))
}

/// The tags a page states in its marker, checked against the vocabulary; None if it states none (spec FR-007).
///
/// # Errors
/// Two markers, a facet missing, repeated or unknown, two levels, a tag stated twice or not in the vocabulary.
pub fn parse_tags(text: &str, place: &str, vocab: &Vocabulary) -> Result<Option<Tags>> {
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
                "{place}: `{chunk}` - the marker is `subject=a,b; setting=x; level=y`, each facet once"
            )));
        }
        let values = value
            .split(',')
            .map(strip)
            .filter(|v| !v.is_empty())
            .map(str::to_owned)
            .collect();
        parts.push((key.to_owned(), values));
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
        for v in &values {
            if !vocab.knows(facet, v) {
                return Err(refused(format!(
                    "{place}: `{facet}={v}` - no such tag in {TAGS}"
                )));
            }
        }
        let mut unique = values.clone();
        unique.sort();
        unique.dedup();
        if unique.len() != values.len() {
            return Err(refused(format!("{place}: a {facet} tag is stated twice")));
        }
    }
    let level = get("level");
    if level.len() != 1 {
        return Err(refused(format!(
            "{place}: {} levels - a question has exactly one",
            level.len()
        )));
    }
    Ok(Some(Tags {
        subjects: get("subject"),
        settings: get("setting"),
        level: level[0].clone(),
    }))
}

/// A clause as `json.dumps(c, sort_keys=True)` writes it.
fn clause_json(c: &Clause) -> String {
    let map: Map<String, Value> = c
        .iter()
        .map(|(k, v)| (k.clone(), Value::from(v.clone())))
        .collect();
    dumps(&sorted(&Value::Object(map)), None, true)
}

/// A message for each clause that matches no question at all - a typo, not a regrouping; a section `awaiting` its first question is
/// exempt until a clause matches, and then its `awaiting` is stale (feature 389).
#[must_use]
pub fn idle_rules(sections: &[Section], every: &[Tags]) -> Vec<String> {
    let mut bad = Vec::new();
    for s in walk(sections) {
        let idle: Vec<&Clause> = s
            .takes
            .iter()
            .filter(|c| !every.iter().any(|t| matches(c, t)))
            .collect();
        if !s.awaiting.is_empty() {
            if idle.len() < s.takes.len() {
                bad.push(format!(
                    "{CONTENTS} section `{}`: it holds a question now - delete its `awaiting`",
                    s.id
                ));
            }
            continue;
        }
        for c in idle {
            bad.push(format!(
                "{CONTENTS} section `{}`: the clause {} matches no question",
                s.id,
                clause_json(c)
            ));
        }
    }
    bad
}

#[cfg(test)]
mod tests;
