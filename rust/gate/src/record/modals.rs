//! Which About-form modals owe the modal checks (from `modal_owed.py`, feature 449 T87): a modal's text, its fingerprints and the units its words or its pages owe. Reads a revision through one listing and one batch.

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::shared::py_text::{collapse, split, strip, SPACE_CLASS};
use l7r_guard::suite_tools::pylex;
use serde_json::{json, Map, Value};

use super::repo::{cat_blobs, git, git_show, read_text, read_universal, Fail};
use super::units::{digest, re, Keyed};

pub(crate) const MODAL_DIRS: [&str; 2] = [
    "l7r/diagram/interactive/classes",
    "l7r/diagram/interactive/compound_kinds",
];
pub(crate) const MODALS: &str = "l7r/diagram/interactive/assets/modals";
pub(crate) const FORM_CHECK: &str = "modal-form";
pub(crate) const RESEARCH_CHECKS: [&str; 3] = ["modal-accuracy", "modal-references", "modal-gaps"];
pub(crate) const DEPICTION_CHECK: &str = "modal-depiction";
pub(crate) const RESEARCH_AGENT: &str = "modal-research";
/// A pop-up's checks in their order (feature 375 amendment 3, FR-019).
pub(crate) const ORDER: [&str; 3] = [FORM_CHECK, RESEARCH_AGENT, DEPICTION_CHECK];

/// The units each check of `ORDER` answers.
pub(crate) fn agent_units(agent: &str) -> &'static [&'static str] {
    match agent {
        "modal-form" => &["modal-form"],
        "modal-research" => &RESEARCH_CHECKS,
        _ => &["modal-depiction"],
    }
}

/// The check of `ORDER` that answers a unit's check, or "".
fn agent_of(unit_check: &str) -> &'static str {
    ORDER
        .iter()
        .find(|a| agent_units(a).contains(&unit_check))
        .copied()
        .unwrap_or("")
}

/// The unit checks of every check BEFORE the one answering `unit_checks`; none unless they are one check's.
pub(crate) fn earlier_units(unit_checks: &[String]) -> Vec<String> {
    let agents: HashSet<&str> = unit_checks.iter().map(|c| agent_of(c)).collect();
    let mut one = agents.iter();
    let (Some(agent), None) = (one.next(), one.next()) else {
        return Vec::new();
    };
    if agent.is_empty() {
        return Vec::new();
    }
    let at = ORDER.iter().position(|a| a == agent).unwrap_or(0);
    ORDER[..at]
        .iter()
        .flat_map(|a| agent_units(a).iter().map(|c| (*c).to_owned()))
        .collect()
}

const PARAGRAPHED: [&str; 2] = ["About", "Depiction"];
static TAG: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        "^(What|Why|Note|Caveat|About|Guesses|Depiction|Name|Covers|Label|Sources|Entry|Drawing|Form):[{SPACE_CLASS}]?(.*)$"
    ))
});
static PATH: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"research/questions/[^{SPACE_CLASS},;]+?\.html")));
static NON_SLUG: LazyLock<Regex> = LazyLock::new(|| re("[^a-z0-9-]"));
static NEWLINES: LazyLock<Regex> = LazyLock::new(|| re(r"\n{3,}"));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static MONEY_MARK: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)<span class="money"[^>]*>(.*?)</span>"#));

/// `re.sub(r"[^a-z0-9-]", "-", key.lower())`.
fn slug_of(key: &str) -> String {
    NON_SLUG.replace_all(&key.to_lowercase(), "-").into_owned()
}

/// One About-form modal class as its source states it: the parts the checks read.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub(crate) struct Modal {
    pub(crate) cls: String,
    pub(crate) key: String,
    pub(crate) origin: String,
    pub(crate) tags: Vec<(String, String)>,
    pub(crate) doc: String,
}

impl Modal {
    pub(crate) fn tag(&self, name: &str) -> &str {
        self.tags
            .iter()
            .find(|(k, _)| k == name)
            .map_or("", |(_, v)| v.as_str())
    }

    /// `<hamlet|sheet>/<slug>`, or `choice/<file stem>`.
    pub(crate) fn uid(&self) -> String {
        if self.origin.contains("/modals/choice/") {
            return format!("choice/{}", stem(&self.origin));
        }
        let registry =
            if self.origin.contains("/modals/sheet/") || self.origin.contains("compound_kinds") {
                "sheet"
            } else {
                "hamlet"
            };
        format!("{registry}/{}", slug_of(&self.key))
    }

    pub(crate) fn prose(&self) -> String {
        ["Name", "About", "Guesses", "Form"]
            .map(|t| self.tag(t))
            .join("\n")
    }

    pub(crate) fn entry(&self) -> &str {
        self.tag("Entry")
    }

    fn form(&self) -> &str {
        if self.tag("Form").is_empty() {
            "standard"
        } else {
            self.tag("Form")
        }
    }

    pub(crate) fn entry_files(&self) -> Vec<String> {
        unique_paths(self.entry())
    }

    pub(crate) fn depiction(&self) -> String {
        ["Depiction", "Drawing"].map(|t| self.tag(t)).join("\n")
    }

    pub(crate) fn drawing_files(&self) -> Vec<String> {
        unique_paths(self.tag("Drawing"))
    }

    /// The modal for a Python caller: its fields and every derived property, all computed here.
    pub(crate) fn json(&self) -> Value {
        let tags: Map<String, Value> = self
            .tags
            .iter()
            .map(|(k, v)| (k.clone(), json!(v)))
            .collect();
        json!({
            "cls": self.cls, "key": self.key, "origin": self.origin, "tags": tags, "doc": self.doc,
            "uid": self.uid(), "prose": self.prose(), "entry": self.entry(), "form": self.form(),
            "depiction": self.depiction(), "entry_files": self.entry_files(), "drawing_files": self.drawing_files(),
        })
    }

    /// A modal handed back by a Python caller.
    pub(crate) fn from_json(value: &Value) -> Self {
        let text = |k: &str| {
            value
                .get(k)
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_owned()
        };
        let tags = value
            .get("tags")
            .and_then(Value::as_object)
            .map_or_else(Vec::new, |m| {
                m.iter()
                    .map(|(k, v)| (k.clone(), v.as_str().unwrap_or("").to_owned()))
                    .collect()
            });
        Self {
            cls: text("cls"),
            key: text("key"),
            origin: text("origin"),
            tags,
            doc: text("doc"),
        }
    }
}

fn unique_paths(text: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for m in PATH.find_iter(text).flatten() {
        if !out.iter().any(|p| p == m.as_str()) {
            out.push(m.as_str().to_owned());
        }
    }
    out
}

/// The file stem of a repository-relative path.
pub(crate) fn stem(path: &str) -> String {
    Path::new(path)
        .file_stem()
        .map_or_else(String::new, |s| s.to_string_lossy().into_owned())
}

/// A class docstring's or modal file's tags, each value its lines (`modal_owed.parse_tags`); insertion order kept.
pub(crate) fn parse_tags(doc: &str) -> Vec<(String, String)> {
    let mut out: Vec<(String, Vec<String>)> = Vec::new();
    let mut cur: Option<usize> = None;
    for raw in crate::record::py_lines(doc) {
        let line = strip(raw);
        if let Ok(Some(c)) = TAG.captures(line) {
            let name = c[1].to_owned();
            let value: Vec<String> = if c[2].is_empty() {
                Vec::new()
            } else {
                vec![c[2].to_owned()]
            };
            let at = out.iter().position(|(k, _)| *k == name).unwrap_or_else(|| {
                out.push((name.clone(), Vec::new()));
                out.len() - 1
            });
            out[at].1 = value;
            cur = Some(at);
        } else if let Some(at) = cur {
            if !line.is_empty() || PARAGRAPHED.contains(&out[at].0.as_str()) {
                out[at].1.push(line.to_owned());
            }
        }
    }
    out.iter()
        .map(|(tag, lines)| (tag.clone(), join_tag(tag, lines)))
        .collect()
}

fn join_tag(tag: &str, lines: &[String]) -> String {
    if PARAGRAPHED.contains(&tag) {
        let body = NEWLINES.replace_all(&lines.join("\n"), "\n\n").into_owned();
        let body = strip(&body).to_owned();
        return body
            .split("\n\n")
            .filter(|p| !strip(p).is_empty())
            .map(|p| split(p).join(" "))
            .collect::<Vec<_>>()
            .join("\n\n");
    }
    if tag == "Guesses" {
        let mut bullets: Vec<Vec<&str>> = Vec::new();
        for line in lines {
            if line.starts_with("- ") || bullets.is_empty() {
                bullets.push(vec![line]);
            } else if let Some(b) = bullets.last_mut() {
                b.push(line);
            }
        }
        return bullets
            .iter()
            .map(|b| b.join(" "))
            .collect::<Vec<_>>()
            .join("\n");
    }
    strip(&lines.join(" ")).to_owned()
}

/// The modal file (repository-relative) of the kind `key` defined in the module at `py_path`.
pub(crate) fn modal_file(py_path: &str, key: &str) -> String {
    let registry = if py_path.contains("compound_kinds") {
        "sheet"
    } else {
        "hamlet"
    };
    format!("{MODALS}/{registry}/{}.md", slug_of(key))
}

/// (class name, key, line, docstring) of every class in a module's source that sets a string `key`.
pub(crate) fn kinds_in(source: &str) -> Result<Vec<(String, String, usize, String)>, Fail> {
    pylex::kinds(source)
        .map(|found| {
            found
                .into_iter()
                .map(|k| (k.name, k.key, k.line, k.doc))
                .collect()
        })
        .ok_or_else(|| "a modal module does not parse".to_owned())
}

/// The file at `f`, or None; reads the tree now or a revision.
pub(crate) type Reader<'a> = &'a mut dyn FnMut(&str) -> Result<Option<String>, Fail>;

/// The modals of one module's source.
fn modals_in(source: &str, path: &str, read: Reader, about_only: bool) -> Result<Vec<Modal>, Fail> {
    let mut out = Vec::new();
    for (cls, key, line, doc) in kinds_in(source)? {
        let f = modal_file(path, &key);
        let found = read(&f)?;
        let origin = if found.is_some() {
            f
        } else {
            format!("{path}:{line}")
        };
        let text = found.unwrap_or(doc);
        let tags = parse_tags(&text);
        if (about_only && !tags.iter().any(|(k, _)| k == "About")) || tags.is_empty() {
            continue;
        }
        out.push(Modal {
            cls: format!("{}.{cls}", stem(path)),
            key,
            origin,
            tags,
            doc: text,
        });
    }
    Ok(out)
}

fn read_now(root: &Path) -> impl FnMut(&str) -> Result<Option<String>, Fail> + '_ {
    move |f| read_universal(&root.join(f))
}

/// A revision's files under some directories, read by one listing and one `git cat-file --batch`; any other path by its own `git show`.
pub(crate) struct RevReader {
    root: PathBuf,
    rev: String,
    dirs: Vec<String>,
    files: Option<HashMap<String, String>>,
}

impl RevReader {
    pub(crate) fn new(root: &Path, rev: &str, dirs: &[&str]) -> Self {
        Self {
            root: root.to_path_buf(),
            rev: rev.to_owned(),
            dirs: dirs
                .iter()
                .map(|d| d.trim_end_matches('/').to_owned())
                .collect(),
            files: None,
        }
    }

    fn load(&mut self) -> &HashMap<String, String> {
        if self.files.is_none() {
            let mut args = vec!["ls-tree", "-r", "--name-only", self.rev.as_str(), "--"];
            args.extend(self.dirs.iter().map(String::as_str));
            let listing = git(&self.root, &args);
            let names: Vec<String> = listing
                .split('\n')
                .filter(|n| !n.is_empty())
                .map(str::to_owned)
                .collect();
            let objects: Vec<String> = names.iter().map(|n| format!("{}:{n}", self.rev)).collect();
            let blobs = cat_blobs(&self.root, &objects);
            self.files = Some(names.into_iter().zip(blobs).collect());
        }
        self.files.get_or_insert_with(HashMap::new)
    }

    /// The files directly in `directory` at the revision, sorted.
    fn names(&mut self, directory: &str) -> Vec<String> {
        let d = format!("{}/", directory.trim_end_matches('/'));
        let mut out: Vec<String> = self
            .load()
            .keys()
            .filter(|n| n.starts_with(&d) && !n[d.len()..].contains('/'))
            .cloned()
            .collect();
        out.sort();
        out
    }

    fn inside(&self, path: &str) -> bool {
        self.dirs
            .iter()
            .any(|d| path == d || path.starts_with(&format!("{d}/")))
    }

    /// The file at `path` at the revision, or None where it has none.
    pub(crate) fn read(&mut self, path: &str) -> Option<String> {
        if self.inside(path) {
            return self.load().get(path).cloned();
        }
        git_show(&self.root, &self.rev, path)
    }
}

/// `read_at` on a revision's modal directories and any path else.
pub(crate) fn read_at(root: &Path, rev: &str) -> RevReader {
    let mut dirs: Vec<&str> = MODAL_DIRS.to_vec();
    dirs.push(MODALS);
    RevReader::new(root, rev, &dirs)
}

/// A title-card choice's modal, from its file; None for no tags (or, `about_only`, no About).
pub(crate) fn choice_modal(path: &str, text: &str, about_only: bool) -> Option<Modal> {
    let tags = parse_tags(text);
    if tags.is_empty() || (about_only && !tags.iter().any(|(k, _)| k == "About")) {
        return None;
    }
    let s = stem(path);
    Some(Modal {
        cls: format!("choice.{s}"),
        key: s,
        origin: path.to_owned(),
        tags,
        doc: text.to_owned(),
    })
}

fn ends(name: &str, suffix: &str) -> bool {
    name.as_bytes().ends_with(suffix.as_bytes())
}

fn glob_sorted(dir: &Path, suffix: &str) -> Vec<String> {
    let mut names: Vec<String> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| ends(n, suffix))
        .collect();
    names.sort();
    names
}

/// Every modal in the tree now.
pub(crate) fn modals_now(root: &Path, about_only: bool) -> Result<Vec<Modal>, Fail> {
    let mut out = Vec::new();
    for d in MODAL_DIRS {
        for name in glob_sorted(&root.join(d), ".py") {
            let rel = format!("{d}/{name}");
            let text = read_text(&root.join(&rel))?;
            let mut read = read_now(root);
            out.extend(modals_in(&text, &rel, &mut read, about_only)?);
        }
    }
    let choice = format!("{MODALS}/choice");
    for name in glob_sorted(&root.join(&choice), ".md") {
        let rel = format!("{choice}/{name}");
        if let Some(m) = choice_modal(&rel, &read_text(&root.join(&rel))?, about_only) {
            out.push(m);
        }
    }
    Ok(out)
}

/// The modals at a revision, keyed by uid.
pub(crate) fn modals_at(root: &Path, rev: &str, about_only: bool) -> Result<Keyed<Modal>, Fail> {
    let mut out = Keyed::default();
    let mut read = read_at(root, rev);
    for d in MODAL_DIRS {
        for name in read.names(d).into_iter().filter(|n| ends(n, ".py")) {
            let source = read.read(&name).unwrap_or_default();
            let mut reader = |f: &str| Ok(read.read(f));
            for m in modals_in(&source, &name, &mut reader, about_only)? {
                out.insert(m.uid(), m);
            }
        }
    }
    for name in read
        .names(&format!("{MODALS}/choice"))
        .into_iter()
        .filter(|n| ends(n, ".md"))
    {
        let text = read.read(&name).unwrap_or_default();
        out.extend(choice_modal(&name, &text, about_only).map(|m| (m.uid(), m)));
    }
    Ok(out)
}

/// An About-form modal by class name, key or uid, among `modals`.
pub(crate) fn find<'a>(modals: &'a [Modal], kind: &str) -> Option<&'a Modal> {
    modals.iter().find(|m| {
        kind == m.uid()
            || kind == m.key
            || kind == m.cls
            || m.cls.split_once('.').is_some_and(|p| kind == p.1)
    })
}

/// A research page's words for a fingerprint: comments out, whitespace folded.
fn page_words(text: &str) -> String {
    collapse(&COMMENT.replace_all(text, ""))
}

fn page_words_unmarked(text: &str) -> String {
    page_words(&MONEY_MARK.replace_all(text, |c: &Captures| c[1].to_owned()))
}

fn pages(root: &Path, files: &[String]) -> Result<Vec<String>, Fail> {
    files
        .iter()
        .map(|f| {
            read_universal(&root.join(f)).map(|t| t.map_or_else(String::new, |t| page_words(&t)))
        })
        .collect()
}

fn digest_owned(parts: &[String]) -> String {
    digest(&parts.iter().map(String::as_str).collect::<Vec<_>>())
}

/// (the form units' fingerprint, the research units' fingerprint).
pub(crate) fn fingerprints(root: &Path, m: &Modal) -> Result<(String, String), Fail> {
    let mut research = vec![m.uid(), m.prose(), m.entry().to_owned()];
    let form = digest_owned(&research);
    research.extend(pages(root, &m.entry_files())?);
    Ok((form, digest_owned(&research)))
}

/// What `modal-depiction` judges: the `Entry:` list, the Depiction tab, the `Drawing:` list and those pages.
pub(crate) fn depiction_fingerprint(root: &Path, m: &Modal) -> Result<String, Fail> {
    let mut parts = vec![m.uid(), m.entry().to_owned(), m.depiction()];
    parts.extend(pages(root, &m.drawing_files())?);
    Ok(digest_owned(&parts))
}

/// The depiction fingerprint as amendment 1 computed it, About in it.
pub(crate) fn amendment1_depiction_fingerprint(root: &Path, m: &Modal) -> Result<String, Fail> {
    let mut parts = vec![
        m.uid(),
        m.tag("About").to_owned(),
        m.entry().to_owned(),
        m.depiction(),
    ];
    parts.extend(pages(root, &m.drawing_files())?);
    Ok(digest_owned(&parts))
}

/// The depiction fingerprint as it was computed before amendment 1.
pub(crate) fn legacy_depiction_fingerprint(root: &Path, m: &Modal) -> Result<String, Fail> {
    let mut parts = vec![m.uid(), m.prose(), m.depiction()];
    parts.extend(pages(root, &m.drawing_files())?);
    Ok(digest_owned(&parts))
}

/// Whether an edit from `was` to `m` owes `modal-depiction`.
pub(crate) fn depiction_owed_by(was: Option<&Modal>, m: &Modal) -> bool {
    was.is_none_or(|w| w.depiction() != m.depiction() || w.entry() != m.entry())
}

fn changed_pages(root: &Path, base: &str) -> Result<HashSet<String>, Fail> {
    let mut changed: HashSet<String> = HashSet::new();
    if !base.is_empty() {
        changed.extend(
            split(&git(
                root,
                &["diff", "--name-only", base, "--", "research/questions"],
            ))
            .into_iter()
            .map(str::to_owned),
        );
    }
    changed.extend(
        split(&git(
            root,
            &[
                "ls-files",
                "--others",
                "--exclude-standard",
                "--",
                "research/questions",
            ],
        ))
        .into_iter()
        .map(str::to_owned),
    );
    if base.is_empty() {
        return Ok(changed);
    }
    let names: Vec<String> = {
        let mut v: Vec<String> = changed.iter().cloned().collect();
        v.sort();
        v
    };
    let moved: HashSet<String> = crate::checks::moves::moved_only(root, base, &names)
        .into_iter()
        .collect();
    changed.retain(|n| !moved.contains(n));
    let mut listed: Vec<String> = changed.iter().cloned().collect();
    listed.sort();
    let objects: Vec<String> = listed.iter().map(|f| format!("{base}:{f}")).collect();
    let old: HashMap<String, String> = listed
        .iter()
        .cloned()
        .zip(cat_blobs(root, &objects))
        .collect();
    let mut kept = HashSet::new();
    for f in changed {
        let was = page_words_unmarked(old.get(&f).map_or("", String::as_str));
        let now = page_words_unmarked(&read_universal(&root.join(&f))?.unwrap_or_default());
        if was != now {
            kept.insert(f);
        }
    }
    Ok(kept)
}

/// (slug, occasion, fingerprint) for every unit an About-form modal owes against `base`; `uid` scopes it to one pop-up.
pub(crate) fn owed(
    root: &Path,
    base: &str,
    uid: &str,
) -> Result<Vec<(String, String, String)>, Fail> {
    let before = if base.is_empty() {
        Keyed::default()
    } else {
        modals_at(root, base, true)?
    };
    let changed = changed_pages(root, base)?;
    let mut rows = Vec::new();
    for m in modals_now(root, true)? {
        if !uid.is_empty() && m.uid() != uid {
            continue;
        }
        rows.extend(owed_row(root, &m, before.get(&m.uid()), &changed)?);
    }
    Ok(rows)
}

fn name_list(files: &[String]) -> String {
    files
        .iter()
        .map(|f| {
            Path::new(f)
                .file_name()
                .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
        })
        .collect::<Vec<_>>()
        .join(" ")
}

fn owed_row(
    root: &Path,
    m: &Modal,
    was: Option<&Modal>,
    changed: &HashSet<String>,
) -> Result<Vec<(String, String, String)>, Fail> {
    let mut rows = Vec::new();
    let uid = m.uid();
    let (fp_form, fp_research) = fingerprints(root, m)?;
    let moved_text = was.is_none_or(|w| w.prose() != m.prose() || w.entry() != m.entry());
    let moved_pages: Vec<String> = m
        .entry_files()
        .into_iter()
        .filter(|f| changed.contains(f))
        .collect();
    if moved_text {
        let why = if was.is_none() {
            "new to the About form"
        } else {
            "its About, Guesses or Entry changed"
        };
        rows.push((format!("{FORM_CHECK}:{uid}"), why.to_owned(), fp_form));
        rows.extend(
            RESEARCH_CHECKS
                .iter()
                .map(|c| (format!("{c}:{uid}"), why.to_owned(), fp_research.clone())),
        );
    } else if !moved_pages.is_empty() {
        let why = format!("a page its Entry names moved ({})", name_list(&moved_pages));
        rows.extend(
            RESEARCH_CHECKS
                .iter()
                .map(|c| (format!("{c}:{uid}"), why.clone(), fp_research.clone())),
        );
    }
    let moved_drawing: Vec<String> = m
        .drawing_files()
        .into_iter()
        .filter(|f| changed.contains(f))
        .collect();
    if depiction_owed_by(was, m) {
        let why = if was.is_none() {
            "new to the About form"
        } else {
            "its Depiction, Drawing: or Entry: changed"
        };
        rows.push((
            format!("{DEPICTION_CHECK}:{uid}"),
            why.to_owned(),
            depiction_fingerprint(root, m)?,
        ));
    } else if !moved_drawing.is_empty() {
        let why = format!(
            "a page its Drawing: names moved ({})",
            name_list(&moved_drawing)
        );
        rows.push((
            format!("{DEPICTION_CHECK}:{uid}"),
            why,
            depiction_fingerprint(root, m)?,
        ));
    }
    Ok(rows)
}

/// The keys of every About-form modal.
pub(crate) fn about_keys(root: &Path) -> Result<HashSet<String>, Fail> {
    Ok(modals_now(root, true)?.into_iter().map(|m| m.key).collect())
}

/// `record modal-owed [--root DIR]`: the owed units, one a line (`modal_owed.py`'s own command line).
pub(crate) fn cli(args: &[String]) -> crate::Reply {
    let flags = [super::args::Spec::value("--root")];
    let parsed = match super::args::parse(args, &flags) {
        Ok(p) => p,
        Err(complaint) => {
            return crate::Reply {
                stdout: String::new(),
                stderr: format!("usage: l7r-gate record modal-owed: {complaint}\n"),
                code: 2,
            }
        }
    };
    let given = parsed.text("--root", ".");
    let root = std::fs::canonicalize(given).unwrap_or_else(|_| given.into());
    match owed(&root, &super::owed::merge_base(&root), "") {
        Ok(rows) => crate::Reply {
            stdout: rows.iter().fold(String::new(), |mut out, (slug, why, _)| {
                let _ = writeln!(out, "{slug}  - {why}");
                out
            }),
            stderr: String::new(),
            code: 0,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: why + "\n",
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
