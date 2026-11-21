//! The record as a manual: a site with a navigation tree, and the whole record on one page (`record/site.py`, features 301, 303; ported
//! by feature 449 T148, phase 4's S5, `ask:449-phase4-slices` - the first production caller of this crate's record library). The GM,
//! 2026-10-01 (feature 301): *"a single page version which gets automatically assembled and that single page version has all of the
//! research and all of the sources and all of the citations with a linkable table of contents at the very top"*, and the sections
//! *"linked on the left"*; and (feature 303) the sections are `research/contents.json`, the questions homed and ordered by their tags.
//!
//! What `make record` writes under `research/site/` is listed in [`super::site_pages`]. Nothing is read back from what this writes: the
//! fragments are the record. A link that lands nowhere, an id used twice, a note nothing cites, a cited work with no write-up or a work
//! whose tags are missing or no section takes refuses the build, naming the fragment; every refusal is gathered, so one run names them all.
//!
//! No per-file memo (the Python's `store.MEMO`, which only `memo_check.py` filled): `ask:449-T81-slices` leaves a cache to the caller's
//! own measurement, and the push's check runs this build whole (feature 449 T148's plan entry records the measurement).

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::pyre::py;
use crate::record::contents::{self as ct, Section};
use crate::record::money::{self, Table};
use crate::record::notes::{Notes, Placed};
use crate::record::questions::{Page, Record, QUESTIONS};
use crate::record::site_links::{self as links, Index, QUESTION_DIR, REGISTRY_DIR};
use crate::record::site_notes as sn;
use crate::record::site_pages::{self as sp, Item, HALVES};
use crate::record::source_tags::{self as st, Catalog, Label};
use crate::record::split::split;
use crate::record::{archive, blocked, store};
use crate::sources::{page_text, Entry, Reader};
use crate::{Error, Result};
use l7r_shared::html_text::escape;

mod pages;
pub mod write;

pub const SITE: &str = "site";
/// The assets the site carries, copied from `research/assets/` - the hand-written ones. The glossary is derived.
pub const ASSETS: [&str; 5] = ["record.css", "record.js", "site.css", "site.js", "theme.js"];
/// Ids the site's own pages use, which no fragment may.
pub const RESERVED: [&str; 8] = [
    "contents",
    "citations",
    "record",
    "page-notes",
    "page-works",
    "tags",
    "research",
    "drawing",
];
/// The registry group of the pages read, judged worth keeping and never cited (feature 312 FR-013); its anchors carry the prefix.
pub const UNCITED_GROUP: &str = "uncited-works";
pub const UNCITED_PREFIX: &str = "uncited-";
pub const UNCITED_TITLE: &str = "Uncited sources";

static H1: LazyLock<Regex> = LazyLock::new(|| py(r#"(?s)<h1 id="([^"]+)">(.*?)</h1>"#));
/// `<h([23]) id="([^"]+)">(.*?)</h\1>`, its back-reference written out as two branches (one heading level or the other, each closed by
/// its own tag), so the pattern runs on the regex engine rather than the backtracking one: the same matches, a third of the build's time
/// otherwise (feature 449 T148, measured on the real record). The level is group 1 or 4, the id 2 or 5, the text 3 or 6.
static HEAD: LazyLock<Regex> =
    LazyLock::new(|| py(r#"(?s)<h(2) id="([^"]+)">(.*?)</h2>|<h(3) id="([^"]+)">(.*?)</h3>"#));

/// A heading match's id and text, whichever branch matched.
fn head_parts<'t>(m: &fancy_regex::Captures<'t>) -> (&'t str, &'t str) {
    let pick = |a: usize, b: usize| m.get(a).or_else(|| m.get(b)).map_or("", |g| g.as_str());
    (pick(2, 5), pick(3, 6))
}
static XREF_SPAN: LazyLock<Regex> = LazyLock::new(|| py(r#"(?s)<span class="xref">.*?</span>"#));
static MAIN: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<main>\s*"));
static TRAILING_RULE: LazyLock<Regex> = LazyLock::new(|| py(r"\s*<hr>\s*$"));
static P: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<p>(.*?)</p>"));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<!--.*?-->"));
static SENTENCE: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)^(.+?[.!?])(?:\s|$)"));
/// What the assembly writes under a heading before the question's own opening: the "Not to be confused with:" list.
static CONFUSABLES: LazyLock<Regex> =
    LazyLock::new(|| py(r#"(?s)<div class="confusables">.*?</div>"#));
/// A citation line of the GM's campaign notes, its parenthesized URLs, and the joining words between two sections (`canon_list`).
static CANON_LINE: LazyLock<Regex> = LazyLock::new(|| {
    py(r"(?s)^<p>(The GM's campaign notes, <code>[^<]+</code>), (.*?)(<!--.*?-->)?</p>(?!.)")
});
static PAREN_URL: LazyLock<Regex> = LazyLock::new(|| py(r"\((https?://[^\s()]+)\)"));
static JOIN: LazyLock<Regex> = LazyLock::new(|| py(r"^\s*(?:,\s*)?(?:and\s+)?"));

fn drop(pattern: &Regex, text: &str) -> String {
    pattern.replace_all(text, "").into_owned()
}

fn refused(message: impl Into<String>) -> Error {
    Error::new("RecordError", message)
}

fn esc(text: &str) -> String {
    escape(text, true)
}

/// A fragment's visible text, its session notes dropped.
fn text_of(fragment: &str) -> String {
    page_text(&drop(&COMMENT, fragment))
}

/// The first sentence of a section's first paragraph - the line a listing shows under each question.
#[must_use]
pub fn lead_of(section: &str) -> String {
    let bare = drop(&CONFUSABLES, &drop(&COMMENT, section));
    let Some(m) = P.captures(&bare).ok().flatten() else {
        return String::new();
    };
    let text = text_of(&m[1]);
    SENTENCE
        .captures(&text)
        .ok()
        .flatten()
        .map_or_else(|| text.clone(), |s| s[1].to_owned())
}

/// A citation line naming two or more sections of the GM's campaign notes, as a bulleted list (the GM, 2026-10-02: *"when my campaign
/// notes include a list of different sections ... then it should be listed as a bulleted list, for legibility"*); any other line, or one
/// naming a single section, as it is.
#[must_use]
pub fn canon_list(line: &str) -> String {
    let stripped = l7r_shared::py_text::strip(line);
    let Some(m) = CANON_LINE.captures(stripped).ok().flatten() else {
        return line.to_owned();
    };
    let (lead, rest) = (&m[1], &m[2]);
    let comment = m.get(3).map_or("", |c| c.as_str());
    let mut items = Vec::new();
    let mut whole = String::new();
    let mut at = 0;
    for u in PAREN_URL
        .captures_iter(rest)
        .map_while(std::result::Result::ok)
    {
        let all = u.get(0).map_or(0..0, |g| g.range());
        let name = drop(&JOIN, &rest[at..all.start]);
        let name = l7r_shared::py_text::strip(&name);
        if name.is_empty() {
            u[1].clone_into(&mut whole);
        } else {
            items.push(format!("{name} ({})", &u[1]));
        }
        at = all.end;
    }
    if !l7r_shared::py_text::strip(&rest[at..]).is_empty() || items.len() < 2 {
        return line.to_owned();
    }
    let whole = if whole.is_empty() {
        String::new()
    } else {
        format!(" ({whole})")
    };
    let list: Vec<String> = items.iter().map(|i| format!("<li>{i}</li>\n")).collect();
    format!(
        "<p>{lead}{whole}:{comment}</p>\n<ul class=\"canon-sections\">\n{}</ul>",
        list.concat()
    )
}

fn item(text: &str, heading_id: &str) -> Item {
    let title = match HEAD.captures(text).ok().flatten() {
        Some(m) => text_of(&drop(&XREF_SPAN, head_parts(&m).1)),
        None => heading_id.to_owned(),
    };
    Item {
        id: heading_id.to_owned(),
        html: text.to_owned(),
        title,
        lead: lead_of(text),
    }
}

/// The anchor prefix of a registry group's sections and kinds: none for the works cited.
#[must_use]
pub fn group_prefix(gid: &str) -> &'static str {
    if gid == UNCITED_GROUP {
        UNCITED_PREFIX
    } else {
        ""
    }
}

/// The registry, taken apart into its groups and their entries.
pub struct Registry {
    pub title: String,
    pub title_id: String,
    pub intro: String,
    /// (group id, its own text, its entries)
    pub groups: Vec<(String, String, Vec<Item>)>,
}

impl Registry {
    /// # Errors
    /// The registry's fragments refused, or a front matter with no title.
    pub fn new(record_dir: &Path) -> Result<Self> {
        let page = split(
            &store::registry_html(record_dir)?,
            Some(store::ENTRY_LEVEL),
            2,
        )?;
        let front = match MAIN.find(&page.front).ok().flatten() {
            Some(m) => &page.front[m.end()..],
            None => page.front.as_str(),
        };
        let Some(h1) = H1.captures(front).ok().flatten() else {
            return Err(refused(format!(
                "{REGISTRY_DIR}/_front.html: no `<h1 id=...>` - the registry needs its title"
            )));
        };
        let end = h1.get(0).map_or(0, |g| g.end());
        let intro = drop(&TRAILING_RULE, &front[end..]);
        Ok(Self {
            title: text_of(&h1[2]),
            title_id: h1[1].to_owned(),
            intro: l7r_shared::py_text::strip(&intro).to_owned(),
            groups: page
                .sections
                .iter()
                .map(|s| {
                    let items = s.entries.iter().map(|e| item(&e.text, &e.id)).collect();
                    (s.id.clone(), s.text.clone(), items)
                })
                .collect(),
        })
    }

    pub fn items(&self) -> impl Iterator<Item = &Item> {
        self.groups.iter().flat_map(|(_, _, items)| items)
    }
}

/// Every id in the record, and the ids the build refuses: one used twice anywhere, because the single page holds them all (feature 301
/// FR-007), or one the site's own pages use.
///
/// # Errors
/// The collisions, every one named.
pub fn build_index(
    items: &[(String, Item)],
    registry: &Registry,
    section_ids: &[String],
) -> Result<Index> {
    let mut index = Index::new();
    let mut seen: HashMap<String, String> = HashMap::new();
    let mut errors: Vec<String> = Vec::new();
    let mut claim = |found: &str, place: &str| {
        match seen.get(found) {
        Some(first) if first != place => errors.push(format!("the id `{found}` is used in {first} and again in {place} - the single page holds both, and an id names one place")),
        Some(_) => {}
        None => {
            seen.insert(found.to_owned(), place.to_owned());
        }
    }
    };
    for (file, it) in items {
        index.add_page(file, &it.id, &it.html);
        let place = format!("{QUESTIONS}/{file}");
        claim(&it.id, &place);
        for found in links::ids_in(&it.html) {
            claim(&found, &place);
        }
    }
    index.add_registry(None, &registry.intro);
    claim(&registry.title_id, &format!("{REGISTRY_DIR}/_front.html"));
    for (gid, ghtml, gitems) in &registry.groups {
        index.add_registry(None, ghtml);
        for found in links::ids_in(ghtml) {
            claim(&found, &format!("{REGISTRY_DIR}/ group {gid}"));
        }
        for it in gitems {
            index.add_registry(Some(&it.id), &it.html);
            let place = format!("{REGISTRY_DIR}/ {}", it.id);
            claim(&it.id, &place);
            for found in links::ids_in(&it.html) {
                claim(&found, &place);
            }
        }
    }
    for sid in section_ids {
        claim(sid, st::SECTIONS);
    }
    for reserved in RESERVED {
        if let Some(at) = seen.get(reserved) {
            errors.push(format!(
                "the id `{reserved}` (in {at}) is one the site's own pages use"
            ));
        }
    }
    if !errors.is_empty() {
        let mut all = vec!["the record's ids collide:".to_owned()];
        all.extend(errors);
        return Err(refused(all.join("\n  ")));
    }
    Ok(index)
}

/// A question's own heading made the page's title: its first `<h2>`/`<h3>` becomes the `<h1>`.
#[must_use]
pub fn as_title(item_html: &str) -> String {
    let Some(m) = HEAD.captures(item_html).ok().flatten() else {
        return item_html.to_owned();
    };
    let all = m.get(0).map_or(0..0, |g| g.range());
    let (id, text) = head_parts(&m);
    format!(
        "{}<h1 id=\"{id}\">{text}</h1>{}",
        &item_html[..all.start],
        &item_html[all.end..]
    )
}

/// The built site: each path under `site/` and its bytes, in the order the build set them (a page set twice keeps its first place).
#[derive(Debug, Default, Clone, PartialEq, Eq)]
pub struct SiteFiles {
    pub files: Vec<(String, Vec<u8>)>,
    at: HashMap<String, usize>,
}

impl SiteFiles {
    pub fn set(&mut self, path: &str, data: impl Into<Vec<u8>>) {
        let data = data.into();
        if let Some(i) = self.at.get(path) {
            self.files[*i].1 = data;
        } else {
            self.at.insert(path.to_owned(), self.files.len());
            self.files.push((path.to_owned(), data));
        }
    }

    #[must_use]
    pub fn get(&self, path: &str) -> Option<&[u8]> {
        self.at.get(path).map(|i| self.files[*i].1.as_slice())
    }

    /// The pages: every `.html` the site holds.
    #[must_use]
    pub fn pages(&self) -> usize {
        self.files
            .iter()
            .filter(|(p, _)| crate::has_ext(p, "html"))
            .count()
    }
}

/// One build of the site: the files it writes, and every refusal it found.
pub struct Build {
    record_dir: PathBuf,
    record: Record,
    money: Table,
    money_errors: Vec<String>,
    items: Vec<(String, Item)>,
    item_at: HashMap<String, usize>,
    registry: Registry,
    catalog: Catalog,
    index: Index,
    group_of: HashMap<String, String>,
    entries: Vec<(String, Entry)>,
    archive: Map<String, Value>,
    notes: HashMap<String, Notes>,
    files: SiteFiles,
    errors: Vec<String>,
}

impl Build {
    /// The record read and indexed, and the refusals found while reading it.
    ///
    /// # Errors
    /// What the Python raised before its first page: the record's, the registry's or the catalog's refusal (`RecordError`), the ids
    /// colliding, a broken table or list (the library's own kind).
    pub fn new(record_dir: &Path) -> Result<Self> {
        let record = store::load(record_dir)?;
        let tables = store::shared(&record, record_dir)?;
        let money = money::load(record_dir)?;
        let mut money_errors = Vec::new();
        let mut items: Vec<(String, Item)> = Vec::new();
        for p in record.pages(None) {
            let html = store::page_html(&record, p, record_dir, Some(&tables))?;
            let html = annotated(&mut money_errors, &money, &html, &p.file)?;
            items.push((p.file.clone(), item(&html, &p.heading_id)));
        }
        let item_at = items
            .iter()
            .enumerate()
            .map(|(i, (f, _))| (f.clone(), i))
            .collect();
        let registry = Registry::new(record_dir)?;
        let mut entries_text: Vec<(String, String)> = Vec::new();
        for it in registry.items() {
            match entries_text.iter_mut().find(|(k, _)| k == &it.id) {
                Some(slot) => slot.1.clone_from(&it.html),
                None => entries_text.push((it.id.clone(), it.html.clone())),
            }
        }
        let reader = Reader::new(record_dir);
        let canon = reader.canon_keys()?;
        let catalog = Catalog::new(record_dir, &entries_text, &canon, store::REGISTRY_DIR)
            .map_err(|e| {
                if e.kind == "SourceTagError" {
                    refused(e.message)
                } else {
                    e
                }
            })?;
        let anchors = catalog.anchors();
        let uncited = registry
            .groups
            .iter()
            .any(|(gid, _, items)| gid == UNCITED_GROUP && !items.is_empty());
        let mut section_ids = anchors.clone();
        if uncited {
            section_ids.extend(anchors.iter().map(|a| format!("{UNCITED_PREFIX}{a}")));
        }
        let mut index = build_index(&items, &registry, &section_ids)?;
        let mut group_of: HashMap<String, String> = HashMap::new();
        let mut group_order: Vec<String> = Vec::new();
        for (gid, _, gitems) in &registry.groups {
            for it in gitems {
                if group_of.insert(it.id.clone(), gid.clone()).is_none() {
                    group_order.push(it.id.clone());
                }
            }
        }
        for (half, _) in HALVES {
            for section in ct::walk(&record.sections) {
                if record.holds(section, half) {
                    index.add_section(&section.id, half);
                }
            }
        }
        let entries = reader.registry_entries()?;
        let archive = archive::load(record_dir)?;
        let mut errors = catalog.errors.clone();
        errors.extend(
            group_order
                .iter()
                .filter(|k| group_of[*k] == UNCITED_GROUP && canon.contains(*k))
                .map(|k| format!("{REGISTRY_DIR}/ {k}: an uncited entry links the GM's own campaign notes - canon is never an uncited source (feature 312 FR-013)")),
        );
        Ok(Self {
            record_dir: record_dir.to_path_buf(),
            record,
            money,
            money_errors,
            items,
            item_at,
            registry,
            catalog,
            index,
            group_of,
            entries,
            archive,
            notes: HashMap::new(),
            files: SiteFiles::default(),
            errors,
        })
    }

    fn item_of(&self, file: &str) -> &Item {
        &self.items[self.item_at[file]].1
    }

    fn rewrite(
        &mut self,
        markup: &str,
        own: Option<&str>,
        here: &str,
        place: &str,
        single: bool,
    ) -> String {
        let (out, errs) = links::rewrite(
            markup,
            own,
            &self.index,
            here,
            single,
            place,
            &self.registry.title_id,
        );
        self.errors.extend(errs);
        out
    }

    fn notes_of(&mut self, page: &Page) -> Result<Notes> {
        if let Some(n) = self.notes.get(&page.file) {
            return Ok(n.clone());
        }
        // `page_notes` refuses only with a `RecordError` (its originals' and its notes' refusals are raised as one), which the build keeps
        let notes = match store::page_notes(&page.file, &self.record_dir) {
            Ok(read) => {
                let mut out = Notes::new();
                for (k, body) in read {
                    let place = format!("{} note {k}", page.file);
                    let body = annotated(&mut self.money_errors, &self.money, &body, &place)?;
                    out.push((k, body));
                }
                out
            }
            Err(e) => {
                self.errors.push(e.message);
                Notes::new()
            }
        };
        self.notes.insert(page.file.clone(), notes.clone());
        Ok(notes)
    }

    /// Every file of the site but the glossary and the assets, which [`build`] adds.
    ///
    /// # Errors
    /// Every refusal, as one `RecordError`; what the Python let through, as its kind.
    pub fn run(mut self) -> Result<SiteFiles> {
        let sections: Vec<Section> = self.record.sections.clone();
        for (half, _) in HALVES {
            for section in ct::walk(&sections) {
                if self.record.holds(section, half) {
                    self.section(half, section)?;
                }
            }
        }
        self.tags();
        self.registry_pages();
        self.home()?;
        self.single()?;
        let sources = self.source_nodes();
        let item_of = |file: &str| {
            let it = self.item_of(file);
            (it.title.clone(), it.id.clone())
        };
        let nav = sp::nav_js(&sp::nav_tree(&self.record, &item_of, &sources));
        self.files.set("nav.js", nav);
        self.errors
            .extend(archive::refusals(&self.record_dir, None)?);
        self.errors.extend(blocked::refusals(&self.record_dir)?);
        self.errors.append(&mut self.money_errors);
        if !self.errors.is_empty() {
            let mut all = vec![format!(
                "the site does not build ({} refusal(s)):",
                self.errors.len()
            )];
            all.append(&mut self.errors);
            return Err(refused(all.join("\n  ")));
        }
        Ok(self.files)
    }

    /// A section's pages in one half, each with its item.
    fn section_items(&self, section: &Section, half: &str) -> Vec<(Page, Item)> {
        self.record
            .in_section(&section.id, half)
            .into_iter()
            .map(|p| (p.clone(), self.item_of(&p.file).clone()))
            .collect()
    }

    fn path_of(&self, section: &Section) -> Vec<&Section> {
        ct::path(&self.record.sections, &section.id)
    }

    fn works(&mut self, placed: &[Placed], here: &str, place: &str) -> String {
        let keys = crate::citations::cited_keys(placed.iter().map(|p| p.body.as_str()));
        let (block, missing) =
            crate::citations::works_html(&keys, &self.entries, "", &self.catalog);
        self.errors.extend(missing.iter().map(|k| format!("{place}: cites `{k}`, whose registry entry has no write-up (`What it is:` and `Why it applies, and its limits:`)")));
        self.errors.extend(
            keys.iter()
                .filter(|k| self.group_of.get(*k).is_some_and(|g| g == UNCITED_GROUP))
                .map(|k| format!("{place}: cites `{k}`, an uncited source's entry - `make cite-uncited KEY={k}` moves it to the works cited, then give it its `Used for:` line (feature 312 FR-014)")),
        );
        self.rewrite(&block, None, here, place, false)
    }

    /// A COMPARATIVE source cited by a question that is not a comparative money question (feature 391, the GM 2026-10-18: such a source
    /// is "not because we will use it to establish the actual value of a koku").
    fn comparative_misuse(
        &self,
        placed: &[Placed],
        tags: Option<&ct::Tags>,
        place: &str,
    ) -> Vec<String> {
        if tags.is_some_and(|t| {
            t.all()
                .iter()
                .any(|(f, t)| *f == "subject" && t == "comparative")
        }) {
            return Vec::new();
        }
        crate::citations::cited_keys(placed.iter().map(|p| p.body.as_str()))
            .into_iter()
            .filter(|k| {
                self.catalog
                    .tags_of(k)
                    .is_some_and(|t| t.values("kind").iter().any(|v| v == "comparative"))
            })
            .map(|k| format!("{place}: cites `{k}`, a comparative source - only a comparative money question (subject `comparative`) may cite it (research/CLAUDE.md, Comparative money sources)"))
            .collect()
    }

    /// A question's small page: links resolved while every `href` is still the record's, then the references numbered, then the notes'
    /// keys turned to the works at the foot.
    fn question(
        &mut self,
        page: &Page,
        it: &Item,
        half: &str,
        section: &Section,
        run: &[&Item],
        at: usize,
    ) -> Result<()> {
        let file = page.file.clone();
        let here = format!("{QUESTION_DIR}/{}.html", it.id);
        let place = format!("{QUESTIONS}/{file}");
        let notes = self.notes_of(page)?;
        let rewritten = self.rewrite(&it.html, Some(&file), &here, &place, false);
        // `small_page` refuses only with a `NoteError` (a malformed key, a reference no note defines), which the build keeps
        let (body, placed) = match sn::small_page(&rewritten, &notes, &place) {
            Ok(done) => done,
            Err(e) => {
                self.errors.push(e.message);
                return Ok(());
            }
        };
        let used: HashSet<&str> = placed.iter().map(|p| p.key.as_str()).collect();
        let mut orphans: Vec<&str> = notes
            .iter()
            .map(|(k, _)| k.as_str())
            .filter(|k| !used.contains(k))
            .collect();
        orphans.sort_unstable();
        orphans.dedup();
        if !orphans.is_empty() {
            self.errors.push(format!(
                "{QUESTIONS}/{}: {} - defined as a note, referenced nowhere",
                page.notes_file(),
                orphans.join(", ")
            ));
        }
        let placed: Vec<Placed> = placed
            .into_iter()
            .map(|p| Placed {
                body: self.rewrite(&p.body, Some(&file), &here, &place, false),
                ..p
            })
            .collect();
        let works = if placed.is_empty() {
            String::new()
        } else {
            self.works(&placed, &here, &place)
        };
        let foot = sn::foot(&placed, &works);
        // every page's question has its tags (a research page states them, a drawing page alone takes its question's: `questions::load`)
        let tags = self.record.question_of(page).tags.clone();
        let misuse = self.comparative_misuse(&placed, tags.as_ref(), &place);
        self.errors.extend(misuse);
        let path = self.path_of(section);
        let mut trail = vec![(
            sp::half_title(half).to_owned(),
            format!("index.html#{half}"),
        )];
        trail.extend(sp::section_trail(half, &path));
        let tagged = tags
            .as_ref()
            .map(|t| sp::tags_line(t, &self.record.vocab, &here))
            .unwrap_or_default();
        let content = sp::crumbs(&here, &trail)
            + &as_title(&body)
            + &tagged
            + &foot
            + &sp::pager(run, at, &here, QUESTION_DIR);
        let page_text = sp::shell(
            &format!("{} - {}", it.title, section.title),
            &here,
            &sp::open_keys(half, &path),
            &content,
        );
        self.files.set(&here, page_text);
        Ok(())
    }

    /// A section's page in one half - its description, its subsections, its questions - and its questions' pages.
    fn section(&mut self, half: &str, section: &Section) -> Result<()> {
        let here = sp::section_file(half, section);
        let run = self.section_items(section, half);
        let items: Vec<&Item> = run.iter().map(|(_, i)| i).collect();
        for (at, (page, it)) in run.iter().enumerate() {
            self.question(page, it, half, section, &items, at)?;
        }
        let path = self.path_of(section);
        let mut trail = vec![(
            sp::half_title(half).to_owned(),
            format!("index.html#{half}"),
        )];
        let full = sp::section_trail(half, &path);
        trail.extend(full[..full.len().saturating_sub(1)].iter().cloned());
        let mut body = sp::crumbs(&here, &trail)
            + &format!(
                "<h1>{}</h1>\n{}\n",
                esc(&section.title),
                sp::description(section, half)
            );
        let subs: Vec<&Section> = section
            .sections
            .iter()
            .filter(|s| self.record.holds(s, half))
            .collect();
        if !subs.is_empty() {
            body += "<ul class=\"sections\">\n";
            for s in subs {
                let _ = writeln!(
                    body,
                    "<li><a href=\"../{}\">{}</a></li>",
                    sp::section_file(half, s),
                    esc(&s.title)
                );
            }
            body += "</ul>\n";
        }
        if !items.is_empty() {
            body += &sp::listing(&items, &here);
        }
        let text = sp::shell(
            &format!("{} - {}", section.title, sp::half_title(half)),
            &here,
            &sp::open_keys(half, &path),
            &body,
        );
        self.files.set(&here, text);
        Ok(())
    }

    /// Every tag's page: exactly the questions carrying it, in the order a section lists them (spec 303 FR-014).
    fn tags(&mut self) {
        for facet in ct::FACETS {
            for tag in sp::facet_tags(&self.record.vocab, facet) {
                let here = sp::tag_file(facet, &tag.id);
                let carrying: Vec<&Page> = self
                    .record
                    .questions
                    .iter()
                    .filter(|q| {
                        q.tags.as_ref().is_some_and(|t| {
                            t.all().iter().any(|(f, t)| *f == facet && *t == tag.id)
                        })
                    })
                    .flat_map(|q| q.pages())
                    .collect();
                let rows: Vec<String> = self
                    .record
                    .ordered(&carrying)
                    .iter()
                    .map(|p| {
                        let it = self.item_of(&p.file);
                        format!(
                            "<li><a href=\"../{QUESTION_DIR}/{}.html\">{}</a> <span class=\"lead\">({})</span></li>",
                            it.id,
                            esc(&it.title),
                            sp::half_title(p.half())
                        )
                    })
                    .collect();
                let mut body = sp::crumbs(
                    &here,
                    &[(sp::TAGS_GROUP.to_owned(), "index.html#tags".to_owned())],
                ) + &format!(
                    "<h1>{}: {}</h1>\n<p><em>{}</em></p>\n",
                    sp::facet_name(facet),
                    esc(&tag.name),
                    esc(&tag.description)
                );
                if rows.is_empty() {
                    body += "<p>No question carries this tag yet.</p>\n";
                } else {
                    let _ = writeln!(body, "<ul class=\"questions\">\n{}\n</ul>", rows.join("\n"));
                }
                let text = sp::shell(
                    &format!("{}: {}", sp::facet_name(facet), tag.name),
                    &here,
                    &format!("tags/{facet}"),
                    &body,
                );
                self.files.set(&here, text);
            }
        }
    }

    /// A registry group's entries under their works sections, in the sections' order and the registry's within each; an entry the
    /// catalog refused (already a build error) follows, under no section.
    fn grouped(&self, items: &[Item]) -> Vec<(Option<st::Section>, Vec<Item>)> {
        let by_key = by_key(items);
        let find = |k: &str| by_key.iter().find(|i| i.id == k).cloned();
        let keys: Vec<String> = by_key.iter().map(|i| i.id.clone()).collect();
        let mut out: Vec<(Option<st::Section>, Vec<Item>)> = self
            .catalog
            .grouped(&keys)
            .into_iter()
            .map(|(s, ks)| (Some(s), ks.iter().filter_map(|k| find(k)).collect()))
            .collect();
        let refused: Vec<Item> = items
            .iter()
            .filter(|i| self.catalog.section_of(&i.id).is_none())
            .cloned()
            .collect();
        if !refused.is_empty() {
            out.push((None, refused));
        }
        out
    }

    /// A registry group's entries by works section, then by primary kind (feature 307); the canon, untagged, under no kind.
    fn shelves(&self, items: &[Item]) -> Vec<Shelf> {
        self.grouped(items)
            .into_iter()
            .map(|(section, entries)| {
                let kinds = if section.is_none() {
                    vec![(None, entries)]
                } else {
                    let by_key = by_key(&entries);
                    let keys: Vec<String> = by_key.iter().map(|i| i.id.clone()).collect();
                    self.catalog
                        .by_kind(&keys)
                        .into_iter()
                        .map(|(lab, ks)| {
                            (
                                lab,
                                ks.iter()
                                    .filter_map(|k| by_key.iter().find(|i| &i.id == k).cloned())
                                    .collect(),
                            )
                        })
                        .collect()
                };
                (section, kinds)
            })
            .collect()
    }
}

/// Entries by their key as the Python's `{i.id: i for i in items}` holds them: a key's first place, its last entry (a group may hold one
/// key twice: two files of it naming one heading id, which the id check reads as one place).
fn by_key(items: &[Item]) -> Vec<Item> {
    let mut out: Vec<Item> = Vec::new();
    for it in items {
        match out.iter_mut().find(|i| i.id == it.id) {
            Some(slot) => slot.clone_from(it),
            None => out.push(it.clone()),
        }
    }
    out
}

/// A works section of a registry group, its kinds and their entries.
type Shelf = (Option<st::Section>, Vec<(Option<Label>, Vec<Item>)>);

/// `markup` with each marked amount's conversion written in (feature 413); its refusals kept once each, as the Python kept them (a
/// refusal already kept is dropped, two equal ones of one call both kept).
fn annotated(kept: &mut Vec<String>, table: &Table, markup: &str, place: &str) -> Result<String> {
    let (out, errs) = money::annotate(markup, place, table)?;
    let fresh: Vec<String> = errs.into_iter().filter(|e| !kept.contains(e)).collect();
    kept.extend(fresh);
    Ok(out)
}

/// Every file of the site, by its path under `site/`: the pages, the navigation, the glossary's script from the tree's glossary, and the
/// assets as the record holds them.
///
/// # Errors
/// [`Build::new`]'s and [`Build::run`]'s, the glossary's, or an asset that cannot be read.
pub fn build(record_dir: &Path, tree: &Path) -> Result<SiteFiles> {
    let mut files = Build::new(record_dir)?.run()?;
    files.set(
        "assets/glossary.js",
        crate::glossary::record_glossary_js(&crate::glossary::load(tree)?),
    );
    for name in ASSETS {
        let path = record_dir.join("assets").join(name);
        let text = crate::read(&path)
            .ok_or_else(|| Error::new("OSError", format!("cannot read '{}'", path.display())))?;
        files.set(&format!("assets/{name}"), text);
    }
    Ok(files)
}

#[cfg(test)]
mod tests;
