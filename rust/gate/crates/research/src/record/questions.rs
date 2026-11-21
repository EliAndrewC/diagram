//! The record's questions, one stem each, in one flat directory (`record/questions.py`, feature 303; ported by feature 449 T144): a
//! question's research page `NNNN-<slug>.html`, its drawing page `NNNN-<slug>.drawing.html`, and beside each its `.notes.html` and
//! `.originals.html`. A research page states its tags; a drawing page beside it inherits them; a lone drawing page says which question it is
//! about, or states its own. Nothing guesses: a file it does not recognize is a refusal naming it, and a load gathers every refusal.

use std::collections::{BTreeMap, HashMap};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::py_text::collapse;

pub use crate::record::contents::Section;
use crate::record::contents::{self as ct, Tags, Vocabulary};
use crate::{drop_all, re, Error, Result, SPACE_CLASS};

pub const QUESTIONS: &str = "questions";
pub const NOTES: &str = ".notes.html";
pub const ORIGINALS: &str = ".originals.html";
pub const DRAWING: &str = ".drawing";
static NAME: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"^(\d{{4}})-([^./{SPACE_CLASS}]+)(\.drawing)?(\.notes|\.originals)?\.html\n?\z"
    ))
});
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<h2 id="([^"]+)">(.*?)</h2>"#));
pub static ABOUT: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"<!-- about: (\d{{4}}-[^{SPACE_CLASS}]+) -->")));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static XREF: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<span class="xref">.*?</span>"#));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static TERMS: LazyLock<Regex> = LazyLock::new(|| re(&format!("[,{SPACE_CLASS}]+")));
static NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"^\d{1,4}\z"));

/// `int()` of a run of Unicode digits.
#[must_use]
pub fn digits_value(text: &str) -> u64 {
    text.chars()
        .filter_map(crate::digit_value)
        .fold(0, |n, d| n * 10 + u64::from(d))
}

/// One page of a question: its research page or its drawing page.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Page {
    pub stem: String,
    pub number: u64,
    pub drawing: bool,
    pub file: String,
    pub heading_id: String,
    pub title: String,
    pub text: String,
}

impl Page {
    fn base(&self) -> &str {
        self.file.strip_suffix(".html").unwrap_or(&self.file)
    }

    #[must_use]
    pub fn notes_file(&self) -> String {
        format!("{}{NOTES}", self.base())
    }

    #[must_use]
    pub fn originals_file(&self) -> String {
        format!("{}{ORIGINALS}", self.base())
    }

    #[must_use]
    pub fn half(&self) -> &'static str {
        if self.drawing {
            "drawing"
        } else {
            "research"
        }
    }
}

/// A question: its pages, the stem a lone drawing page is about, its tags and the id of the section it lives in.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Question {
    pub number: u64,
    pub stem: String,
    pub research: Option<Page>,
    pub drawing: Option<Page>,
    pub about: Option<String>,
    pub tags: Option<Tags>,
    pub home: Option<String>,
}

impl Question {
    fn new(number: u64, stem: &str) -> Self {
        Self {
            number,
            stem: stem.to_owned(),
            research: None,
            drawing: None,
            about: None,
            tags: None,
            home: None,
        }
    }

    #[must_use]
    pub fn pages(&self) -> Vec<&Page> {
        self.research.iter().chain(self.drawing.iter()).collect()
    }
}

/// Every question, the vocabulary and the contents, read and checked; a page found by its file or its heading id.
#[derive(Debug, Clone)]
pub struct Record {
    pub questions: Vec<Question>,
    pub vocab: Vocabulary,
    pub sections: Vec<Section>,
    stems: HashMap<String, usize>,
    files: BTreeMap<String, (usize, bool)>,
    ids: BTreeMap<String, (usize, bool)>,
}

impl Record {
    fn at(&self, (q, drawing): (usize, bool)) -> Option<&Page> {
        let q = &self.questions[q];
        if drawing {
            q.drawing.as_ref()
        } else {
            q.research.as_ref()
        }
    }

    /// The page of this file name (`by_file`).
    #[must_use]
    pub fn by_file(&self, file: &str) -> Option<&Page> {
        self.files.get(file).and_then(|r| self.at(*r))
    }

    /// The first page with this heading id (`by_id`).
    #[must_use]
    pub fn by_id(&self, id: &str) -> Option<&Page> {
        self.ids.get(id).and_then(|r| self.at(*r))
    }

    /// The question of this stem (`by_stem`).
    #[must_use]
    pub fn by_stem(&self, stem: &str) -> Option<&Question> {
        self.stems.get(stem).map(|i| &self.questions[*i])
    }

    /// Every file name a page has, in name order.
    #[must_use]
    pub fn files(&self) -> Vec<&String> {
        self.files.keys().collect()
    }

    /// Every heading id with its page's file, in id order.
    #[must_use]
    pub fn ids(&self) -> Vec<(&String, &str)> {
        self.ids
            .iter()
            .filter_map(|(k, r)| Some((k, self.at(*r)?.file.as_str())))
            .collect()
    }

    /// Every page, or every page of one half.
    #[must_use]
    pub fn pages(&self, half: Option<&str>) -> Vec<&Page> {
        self.questions
            .iter()
            .flat_map(Question::pages)
            .filter(|p| half.is_none_or(|h| p.half() == h))
            .collect()
    }

    /// The question a page belongs to.
    ///
    /// # Panics
    /// A page of another record (Python's `KeyError`).
    #[must_use]
    pub fn question_of(&self, page: &Page) -> &Question {
        &self.questions[self.stems[&page.stem]]
    }

    /// Pages in presentation order: level, then identity number, then research before drawing (spec FR-011).
    #[must_use]
    pub fn ordered<'a>(&self, pages: &[&'a Page]) -> Vec<&'a Page> {
        let rank = |p: &Page| {
            let level = self
                .question_of(p)
                .tags
                .as_ref()
                .map_or("", |t| t.level.as_str());
            (
                self.vocab.level_rank(level).unwrap_or(usize::MAX),
                p.number,
                p.drawing,
            )
        };
        let mut out = pages.to_vec();
        out.sort_by_key(|p| rank(p));
        out
    }

    /// The pages of one half whose question lives in exactly this section, in order.
    #[must_use]
    pub fn in_section(&self, section: &str, half: &str) -> Vec<&Page> {
        let mine: Vec<&Page> = self
            .pages(Some(half))
            .into_iter()
            .filter(|p| self.question_of(p).home.as_deref() == Some(section))
            .collect();
        self.ordered(&mine)
    }

    /// Does this section, or a subsection, home a page of this half? An empty section is omitted (FR-013).
    #[must_use]
    pub fn holds(&self, section: &Section, half: &str) -> bool {
        !self.in_section(&section.id, half).is_empty()
            || section.sections.iter().any(|s| self.holds(s, half))
    }

    /// The pages a tool's `Q=` or `IN=` names (spec 303 FR-019), in presentation order: a stem's number, a page's file name, a section's
    /// id (its subsections' questions too), or a tag's id in any facet; several terms joined.
    #[must_use]
    pub fn select(&self, term: &str) -> Vec<&Page> {
        let mut out: Vec<&Page> = Vec::new();
        let sections = ct::walk(&self.sections);
        for t in TERMS
            .split(term)
            .map_while(std::result::Result::ok)
            .filter(|t| !t.is_empty())
        {
            let found: Vec<&Page> = if let Some(p) = self.by_file(t) {
                vec![p]
            } else if NUMBER.is_match(t).unwrap_or(false) {
                let n = digits_value(t);
                self.pages(None)
                    .into_iter()
                    .filter(|p| p.number == n)
                    .collect()
            } else if let Some(s) = sections.iter().find(|s| s.id == t) {
                let inside: Vec<&str> = ct::walk(std::slice::from_ref(*s))
                    .iter()
                    .map(|x| x.id.as_str())
                    .collect();
                self.pages(None)
                    .into_iter()
                    .filter(|p| {
                        self.question_of(p)
                            .home
                            .as_deref()
                            .is_some_and(|h| inside.contains(&h))
                    })
                    .collect()
            } else {
                self.pages(None)
                    .into_iter()
                    .filter(|p| {
                        self.question_of(p)
                            .tags
                            .as_ref()
                            .is_some_and(|tags| tags.all().iter().any(|(_, tag)| tag == t))
                    })
                    .collect()
            };
            for p in found {
                if !out.iter().any(|o| o.file == p.file) {
                    out.push(p);
                }
            }
        }
        self.ordered(&out)
    }
}

/// A heading's text: the cross-link dropped, tags dropped, whitespace collapsed.
#[must_use]
pub fn text_of(markup: &str) -> String {
    collapse(&drop_all(&TAG, &drop_all(&XREF, markup)))
}

/// (heading id, heading text) of a page, comments ignored; None where it has no `<h2 id=...>`.
#[must_use]
pub fn heading(text: &str) -> Option<(String, String)> {
    let plain = drop_all(&COMMENT, text);
    HEADING
        .captures(&plain)
        .ok()
        .flatten()
        .map(|m| (m[1].to_owned(), m[2].to_owned()))
}

fn read(path: &Path) -> Result<String> {
    l7r_gate_core::record::read_text(path)
        .map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))
}

/// Every stem in the directory, its pages read; a name that is not a question's file is a refusal.
fn gather(record_dir: &Path, errors: &mut Vec<String>) -> Result<Vec<Question>> {
    let root = record_dir.join(QUESTIONS);
    let mut names: Vec<String> = std::fs::read_dir(&root)
        .map(|d| {
            d.flatten()
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        })
        .unwrap_or_default();
    names.sort();
    let (mut questions, mut stems): (Vec<Question>, HashMap<String, usize>) =
        (Vec::new(), HashMap::new());
    let mut numbers: HashMap<u64, String> = HashMap::new();
    let mut companions: Vec<(String, String)> = Vec::new();
    for name in names {
        let Some(m) = NAME.captures(&name).ok().flatten() else {
            errors.push(format!(
                "{QUESTIONS}/{name}: not a question's file - NNNN-<slug>.html, .drawing.html, and their .notes.html and .originals.html"
            ));
            continue;
        };
        let (number, drawing, companion) =
            (digits_value(&m[1]), m.get(3).is_some(), m.get(4).is_some());
        let stem = format!("{}-{}", &m[1], &m[2]);
        let owner = numbers.entry(number).or_insert_with(|| stem.clone());
        if *owner != stem {
            errors.push(format!(
                "{QUESTIONS}/{name}: number {} is already {owner} - a number names one question",
                &m[1]
            ));
            continue;
        }
        let qi = *stems.entry(stem.clone()).or_insert_with(|| {
            questions.push(Question::new(number, &stem));
            questions.len() - 1
        });
        if companion {
            companions.push((stem, name.clone()));
            continue;
        }
        let text = read(&root.join(&name))?;
        let Some((heading_id, title)) = heading(&text) else {
            errors.push(format!("{QUESTIONS}/{name}: no `<h2 id=...>` heading"));
            continue;
        };
        let page = Page {
            stem,
            number,
            drawing,
            file: name.clone(),
            heading_id,
            title: text_of(&title),
            text,
        };
        if drawing {
            questions[qi].drawing = Some(page);
        } else {
            questions[qi].research = Some(page);
        }
    }
    for (stem, name) in companions {
        let base = name
            .strip_suffix(NOTES)
            .or_else(|| name.strip_suffix(ORIGINALS))
            .unwrap_or(&name);
        let page_file = format!("{base}.html");
        if !questions[stems[&stem]]
            .pages()
            .iter()
            .any(|p| p.file == page_file)
        {
            errors.push(format!(
                "{QUESTIONS}/{name}: beside no page - {page_file} does not exist"
            ));
        }
    }
    Ok(questions)
}

fn check_slug(q: &Question, errors: &mut Vec<String>) {
    let Some(owner) = q.research.as_ref().or(q.drawing.as_ref()) else {
        return;
    };
    let slug = q.stem.split_once('-').map_or("", |s| s.1);
    if slug != owner.heading_id {
        errors.push(format!(
            "{QUESTIONS}/{}: its name says `{slug}` and its heading is `{}` - the slug is the heading id",
            owner.file, owner.heading_id
        ));
    }
}

/// A question's stated tags and `about:`, with the refusals of spec FR-007.
fn tags(q: &mut Question, vocab: &Vocabulary, errors: &mut Vec<String>) {
    let has_research = q.research.is_some();
    let pages: Vec<Page> = q.pages().into_iter().cloned().collect();
    for page in pages {
        let place = format!("{QUESTIONS}/{}", page.file);
        let stated = match ct::parse_tags(&page.text, &place, vocab) {
            Ok(s) => s,
            Err(e) => {
                errors.push(e.message);
                continue;
            }
        };
        let about = ABOUT
            .captures(&page.text)
            .ok()
            .flatten()
            .map(|m| m[1].to_owned());
        if !page.drawing {
            if about.is_some() {
                errors.push(format!(
                    "{place}: an `about:` on a research page - only a lone drawing page names the question it is about"
                ));
            }
            if stated.is_none() {
                let blank = Tags {
                    subjects: vec!["<subject>".to_owned()],
                    settings: vec!["<setting>".to_owned()],
                    level: "<level>".to_owned(),
                };
                errors.push(format!(
                    "{place}: no tags - a research page states `{}` on the line after its heading",
                    blank.marker()
                ));
            }
            q.tags = stated;
        } else if has_research {
            if stated.is_some() || about.is_some() {
                let what = if stated.is_some() {
                    "tags"
                } else {
                    "an about:"
                };
                errors.push(format!("{place}: states {what} - a drawing page beside its research page inherits its tags"));
            }
        } else if about.is_some() && stated.is_some() {
            errors.push(format!(
                "{place}: states both tags and an `about:` - it inherits from the question it is about, or is a question of its own"
            ));
        } else if about.is_some() {
            q.about = about;
        } else if stated.is_none() {
            errors.push(format!(
                "{place}: no tags and no `about:` - a drawing page alone in its stem says which question it draws, or states its own tags"
            ));
        } else {
            q.tags = stated;
        }
    }
}

/// Every question, tagged and homed, or a `QuestionError` naming every refusal (spec FR-007, FR-010).
///
/// # Errors
/// The vocabulary's or the contents' refusal (`ContentsError`), an unreadable page, or every refusal of the questions gathered.
pub fn load(record_dir: &Path) -> Result<Record> {
    let vocab = ct::load_vocabulary(record_dir)?;
    let sections = ct::load_contents(record_dir, &vocab)?;
    let mut errors = Vec::new();
    let mut questions = gather(record_dir, &mut errors)?;
    questions.sort_by_key(|q| q.number);
    let stems: HashMap<String, usize> = questions
        .iter()
        .enumerate()
        .map(|(i, q)| (q.stem.clone(), i))
        .collect();
    let (mut files, mut ids) = (BTreeMap::new(), BTreeMap::new());
    for i in 0..questions.len() {
        check_slug(&questions[i], &mut errors);
        tags(&mut questions[i], &vocab, &mut errors);
        let pages: Vec<(String, String, bool)> = questions[i]
            .pages()
            .iter()
            .map(|p| (p.file.clone(), p.heading_id.clone(), p.drawing))
            .collect();
        for (file, id, drawing) in pages {
            if let Some(&(fq, fd)) = ids.get(&id) {
                let q: &Question = &questions[fq];
                let first = if fd {
                    q.drawing.as_ref()
                } else {
                    q.research.as_ref()
                }
                .map_or(String::new(), |p| p.file.clone());
                errors.push(format!(
                    "{QUESTIONS}/{file}: heading id `{id}` is also {first}'s"
                ));
            } else {
                ids.insert(id, (i, drawing));
            }
            files.insert(file, (i, drawing));
        }
    }
    let about: Vec<(usize, String)> = questions
        .iter()
        .enumerate()
        .filter_map(|(i, q)| Some((i, q.about.clone()?)))
        .collect();
    for (i, target) in about {
        if let Some(t) = stems
            .get(&target)
            .filter(|t| questions[**t].research.is_some())
        {
            let tags = questions[*t].tags.clone();
            questions[i].tags = tags;
        } else {
            let q = &questions[i];
            let named = q
                .drawing
                .as_ref()
                .map_or(q.stem.clone(), |d| d.file.clone());
            errors.push(format!(
                "{QUESTIONS}/{named}: `about: {target}` names no research question"
            ));
        }
    }
    for q in &mut questions {
        let Some(t) = &q.tags else { continue };
        q.home = ct::home(&sections, t).map(|s| s.id.clone());
        if q.home.is_none() {
            errors.push(format!(
                "{QUESTIONS}/{}: tags {} - no section of {} takes them",
                q.stem,
                t.marker(),
                ct::CONTENTS
            ));
        }
    }
    if errors.is_empty() {
        let every: Vec<Tags> = questions.iter().filter_map(|q| q.tags.clone()).collect();
        errors.extend(ct::idle_rules(&sections, &every));
    }
    if !errors.is_empty() {
        let mut lines = vec![format!(
            "the questions do not load ({} refusal(s)):",
            errors.len()
        )];
        lines.extend(errors);
        return Err(Error::new("QuestionError", lines.join("\n  ")));
    }
    Ok(Record {
        questions,
        vocab,
        sections,
        stems,
        files,
        ids,
    })
}

#[cfg(test)]
mod tests;
