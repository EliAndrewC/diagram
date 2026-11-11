//! Which review checks are OWED by this delta, keyed on OCCASIONS (feature 294; ported from `scripts/reviews/review_owed.py`, feature
//! 449 T89). Each judgment check is owed only on the occasion its answer can change (`specs/294-settlement-review-rethink/research.md`
//! R1), and "a manifest moved" owes nothing: a map or sheet new to the pool, an element new to a map or sheet, or an occasion a
//! feature's `## Occasions` section (or a tweak's `Occasion:` commit line) declares. The reasons behind each rule stand in the
//! Python's comments, kept in git history; the words a person reads are the Python's.
//!
//! `l7r-gate reviews owed [--root DIR] [--why | --units | --check-declared | --glyph-gate SLUG | --glyph-dispatched SLUG |
//! --landing-mark on|off] [--landing] [--escaped]`.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{git, glyph, py_path, reply};
use crate::record::args::{parse, Spec};
use crate::record::bundle::py_repr;
use crate::record::repo::cat_blobs;
use crate::Reply;

/// Both pool trees, the live one first.
pub const TREES: [&str; 2] = ["pool", "legacy-hand-authored-pool"];
/// The checks an occasion can owe, in the order a session dispatches them.
const CHECKS: [&str; 5] = [
    "settlement-review",
    "building-review",
    "glyph-check",
    "size-audit",
    "fix-check",
];
/// The declarable occasions and the checks each owes (`new-program` owes two).
pub(super) const DECLARED: [(&str, &[&str]); 8] = [
    ("glyph-redrawn", &["glyph-check"]),
    ("placement-changed", &["glyph-check"]),
    ("new-form", &["settlement-review"]),
    ("new-tier", &["settlement-review"]),
    ("layout-revised", &["building-review"]),
    ("new-program", &["building-review", "size-audit"]),
    ("gm-fix", &["fix-check"]),
    ("none", &[]),
];
/// Ink-census keys that are not elements: unclassed ink and the place caption.
const NOT_ELEMENTS: [&str; 2] = ["-", "place"];

pub(super) fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static DATA_KIND: LazyLock<Regex> = LazyLock::new(|| re(r#"data-kind="([^"]+)""#));
/// Drawing or placement code - never the incremental gate in `l7r/diagram/ci/`, which draws and places nothing.
static CODE: LazyLock<Regex> = LazyLock::new(|| {
    re(r"^(l7r/(?!diagram/ci/).+\.py|(pool|legacy-hand-authored-pool)/.+\.(gen\.py|svg))$")
});

pub(super) fn found(re: &Regex, text: &str) -> bool {
    re.is_match(text).unwrap_or(false)
}

/// One owed review: a check of a subject, on the map or sheet it is judged on ("" when nothing draws it), for an occasion.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Unit {
    pub check: String,
    pub subject: String,
    pub on: String,
    pub occasion: String,
}

/// `_safe`: runs of anything but ASCII letters and digits as one `-`, trimmed, lowercased.
fn safe(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for c in text.chars() {
        if c.is_ascii_alphanumeric() {
            out.push(c.to_ascii_lowercase());
        } else if !out.ends_with('-') {
            out.push('-');
        }
    }
    out.trim_matches('-').to_owned()
}

impl Unit {
    fn new(check: &str, subject: &str, on: &str, occasion: String) -> Self {
        Self {
            check: check.to_owned(),
            subject: subject.to_owned(),
            on: on.to_owned(),
            occasion,
        }
    }

    /// The unit's file-safe name; a glyph check's carries its map too (feature 374 FR-007).
    #[must_use]
    pub fn slug(&self) -> String {
        let name = format!("{}--{}", self.check, safe(&self.subject));
        if self.check == "glyph-check" && !self.on.is_empty() {
            format!("{name}--{}", safe(&self.on))
        } else {
            name
        }
    }
}

/// `(ref, description)`: the merge base of HEAD with origin/main; HEAD without origin/main; "" with no commits.
#[must_use]
pub fn base_of(root: &Path) -> (String, String) {
    let head = git(root, &["rev-parse", "--verify", "-q", "HEAD"]).unwrap_or_default();
    if head.is_empty() {
        return (String::new(), "no commits yet".to_owned());
    }
    if git(root, &["rev-parse", "--verify", "-q", "origin/main"]).is_some_and(|o| !o.is_empty()) {
        if let Some(mb) =
            git(root, &["merge-base", "HEAD", "origin/main"]).filter(|m| !m.is_empty())
        {
            let desc = format!("origin/main (merge base {})", head8(&mb));
            return (mb, desc);
        }
    }
    let desc = format!("HEAD ({}; no origin/main)", head8(&head));
    (head, desc)
}

fn head8(text: &str) -> &str {
    crate::record::bundle::head(text, 8)
}

/// A map or sheet folder: `<tree>/<category>/<name>`.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Folder {
    pub path: PathBuf,
    pub name: String,
    tree: usize,
}

impl Folder {
    fn file(&self, ext: &str) -> PathBuf {
        self.path.join(format!("{}{ext}", self.name))
    }

    fn has(&self, ext: &str) -> bool {
        self.file(ext).is_file()
    }

    /// A Mode A sheet: an SVG (or its generator) and no manifest.
    #[must_use]
    pub fn is_sheet(&self) -> bool {
        !self.has(".json") && (self.has(".svg") || self.has(".gen.py"))
    }

    /// A hand-drawn Mode B map awaiting conversion owes no review: a legacy folder that is no Mode A sheet.
    fn exempt(&self) -> bool {
        self.tree == 1 && !self.is_sheet()
    }

    fn drawn(&self) -> bool {
        self.has(".json") || self.has(".svg") || self.has(".gen.py")
    }
}

fn names_in(dir: &Path) -> Vec<String> {
    std::fs::read_dir(dir)
        .map(|rd| {
            rd.filter_map(Result::ok)
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        })
        .unwrap_or_default()
}

/// `_folders`: every map or sheet folder (pathlib's `glob("*/*")`, hidden names included), the live pool first, then by path.
#[must_use]
pub fn folders(root: &Path) -> Vec<Folder> {
    let mut out = Vec::new();
    for (tree, name) in TREES.iter().enumerate() {
        let base = root.join(name);
        let mut here: Vec<(String, String)> = Vec::new();
        for category in names_in(&base) {
            for entry in names_in(&base.join(&category)) {
                if base.join(&category).join(&entry).is_dir() {
                    here.push((category.clone(), entry));
                }
            }
        }
        here.sort();
        out.extend(here.into_iter().map(|(c, n)| Folder {
            path: base.join(c).join(&n),
            name: n,
            tree,
        }));
    }
    out
}

/// Every map or sheet folder's name, of both pool trees (feature 248 FR-001).
pub fn pool_map_names(root: &Path) -> Vec<String> {
    let names: BTreeSet<String> = folders(root)
        .into_iter()
        .filter(Folder::drawn)
        .map(|f| f.name)
        .collect();
    names.into_iter().collect()
}

fn rel(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}

/// The pool trees at the base: one `ls-tree` listing, the files asked read by one `cat-file --batch` (feature 383 plan D5; Python's
/// `record_cache.RevReader`, not ported, `ask:449-T81-slices`).
struct AtBase<'a> {
    root: &'a Path,
    rev: &'a str,
    listing: Option<BTreeSet<String>>,
}

impl<'a> AtBase<'a> {
    fn new(root: &'a Path, rev: &'a str) -> Self {
        Self {
            root,
            rev,
            listing: None,
        }
    }

    fn listing(&mut self) -> &BTreeSet<String> {
        self.listing.get_or_insert_with(|| {
            let mut args = vec!["ls-tree", "-r", "--name-only", self.rev, "--"];
            args.extend(TREES);
            git(self.root, &args)
                .unwrap_or_default()
                .split('\n')
                .filter(|n| !n.is_empty())
                .map(str::to_owned)
                .collect()
        })
    }

    /// `_existed`: any file of the folder tracked at the base.
    fn existed(&mut self, folder: &str) -> bool {
        if self.rev.is_empty() {
            return false;
        }
        let prefix = format!("{folder}/");
        self.listing().iter().any(|n| n.starts_with(&prefix))
    }

    /// Each file's text at the base, or None where it has none (every path asked is under a pool tree, so in the listing or absent).
    fn read(&mut self, paths: &[String]) -> Vec<Option<String>> {
        let listed: Vec<bool> = {
            let all = self.listing();
            paths.iter().map(|p| all.contains(p)).collect()
        };
        let asked: Vec<String> = paths
            .iter()
            .zip(&listed)
            .filter(|(_, l)| **l)
            .map(|(p, _)| format!("{}:{p}", self.rev))
            .collect();
        let mut texts = cat_blobs(self.root, &asked).into_iter();
        listed
            .into_iter()
            .map(|l| if l { texts.next() } else { None })
            .collect()
    }
}

/// `_at_base`'s fallback: an untracked render read from main's mirror copy beside `.clones/`.
fn mirror_copy(root: &Path, rel_path: &str) -> Option<String> {
    let parts: Vec<_> = root.components().collect();
    let at = parts.iter().position(|c| c.as_os_str() == ".clones")?;
    let mirror: PathBuf = parts[..at].iter().collect::<PathBuf>().join(rel_path);
    mirror.is_file().then(|| read_replace(&mirror))
}

/// `read_text(errors="replace")`.
fn read_replace(path: &Path) -> String {
    std::fs::read(path)
        .map(|b| crate::record::repo::universal(&String::from_utf8_lossy(&b)))
        .unwrap_or_default()
}

/// The element classes a manifest's ink census names (`ink_classes`), or none.
#[must_use]
pub fn ink_classes(text: Option<&str>) -> BTreeSet<String> {
    let Ok(Value::Object(top)) = serde_json::from_str::<Value>(text.unwrap_or("")) else {
        return BTreeSet::new();
    };
    match top.get("ink_classes") {
        Some(Value::Object(census)) => census
            .keys()
            .filter(|k| !NOT_ELEMENTS.contains(&k.as_str()))
            .cloned()
            .collect(),
        _ => BTreeSet::new(),
    }
}

/// The `data-kind`s a Mode A sheet's SVG tags.
pub fn sheet_kinds(text: Option<&str>) -> BTreeSet<String> {
    DATA_KIND
        .captures_iter(text.unwrap_or(""))
        .filter_map(Result::ok)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
        .collect()
}

/// One folder's elements now: its manifest's ink classes, or its sheet's kinds.
fn legend_of(d: &Folder) -> Option<BTreeSet<String>> {
    if d.has(".json") {
        Some(ink_classes(Some(&read_replace(&d.file(".json")))))
    } else if d.has(".svg") {
        Some(sheet_kinds(Some(&read_replace(&d.file(".svg")))))
    } else {
        None
    }
}

/// Each folder's elements now, by name, in the order Python's dict kept them (a later folder of one name updates it in place).
#[derive(Default)]
pub struct Legends(Vec<(String, BTreeSet<String>)>);

impl Legends {
    fn put(&mut self, name: &str, set: BTreeSet<String>) {
        if let Some(slot) = self.0.iter_mut().find(|(n, _)| n == name) {
            slot.1 = set;
        } else {
            self.0.push((name.to_owned(), set));
        }
    }

    #[must_use]
    pub fn get(&self, name: &str) -> Option<&BTreeSet<String>> {
        self.0.iter().find(|(n, _)| n == name).map(|(_, s)| s)
    }

    /// The first map or sheet (live pool first) whose legend has `element`, or "".
    fn first_drawing(&self, element: &str) -> String {
        self.0
            .iter()
            .find(|(_, s)| s.contains(element))
            .map(|(n, _)| n.clone())
            .unwrap_or_default()
    }
}

/// `legends`: each non-exempt folder's elements now.
#[must_use]
pub fn legends(all: &[Folder]) -> Legends {
    let mut out = Legends::default();
    for d in all.iter().filter(|d| !d.exempt()) {
        if let Some(set) = legend_of(d) {
            out.put(&d.name, set);
        }
    }
    out
}

/// What the owed lookup reads once a run: the folders and their legends now.
pub struct Tree<'a> {
    pub root: &'a Path,
    pub folders: Vec<Folder>,
    pub legends: Legends,
}

impl<'a> Tree<'a> {
    #[must_use]
    pub fn read(root: &'a Path) -> Self {
        let folders = folders(root);
        let legends = legends(&folders);
        Self {
            root,
            folders,
            legends,
        }
    }
}

/// The tracked files of each of these folders, by one `git ls-files`.
fn tracked(root: &Path, folders: &[String]) -> BTreeMap<String, Vec<String>> {
    let mut out: BTreeMap<String, Vec<String>> =
        folders.iter().map(|f| (f.clone(), Vec::new())).collect();
    if folders.is_empty() {
        return out;
    }
    let specs: Vec<String> = folders.iter().map(|f| format!("{f}/")).collect();
    let mut args = vec!["ls-files", "--"];
    args.extend(specs.iter().map(String::as_str));
    for line in git(root, &args).unwrap_or_default().lines() {
        if let Some(f) = folders.iter().find(|f| line.starts_with(&format!("{f}/"))) {
            out.entry(f.clone()).or_default().push(line.to_owned());
        }
    }
    out
}

fn element_units(
    owed: &BTreeMap<String, (String, String)>,
    sheets: &BTreeSet<String>,
) -> Vec<Unit> {
    let mut units = Vec::new();
    for (element, (on, why)) in owed {
        units.push(Unit::new("glyph-check", element, on, why.clone()));
        if sheets.contains(on) {
            units.push(Unit::new("size-audit", element, on, why.clone()));
        }
    }
    units
}

/// A folder's legend at the base: known now (`Ok`, a moved folder) or to be read there (`Err((path, a manifest))`).
type AtBaseOrNow = Result<BTreeSet<String>, (String, bool)>;

/// The occasions the delta itself shows: maps and sheets new to the pool, and elements new to a map or sheet.
#[must_use]
pub fn detected(tree: &Tree, base: &str) -> Vec<Unit> {
    let root = tree.root;
    let mut at = AtBase::new(root, base);
    let live: Vec<&Folder> = tree
        .folders
        .iter()
        .filter(|d| !d.exempt() && d.drawn())
        .collect();
    let unborn_rel: Vec<String> = live
        .iter()
        .map(|d| rel(root, &d.path))
        .filter(|r| !at.existed(r))
        .collect();
    let unborn = tracked(root, &unborn_rel);
    let names: Vec<String> = unborn.values().flatten().cloned().collect();
    let moved = moved_only(root, base, &names);
    let mut new_folders: Vec<&Folder> = Vec::new();
    // each folder's legend at the base, in folder order: known now (a moved folder), or read at the base in one batch below
    let mut order: Vec<(String, AtBaseOrNow)> = Vec::new();
    for d in &live {
        let r = rel(root, &d.path);
        if let Some(files) = unborn.get(&r) {
            if files.iter().any(|f| moved.contains(f)) {
                order.push((d.name.clone(), Ok(legend_of(d).unwrap_or_default())));
            } else {
                new_folders.push(d);
            }
            continue;
        }
        if d.has(".json") {
            order.push((d.name.clone(), Err((rel(root, &d.file(".json")), true))));
        } else if d.has(".svg") {
            order.push((d.name.clone(), Err((rel(root, &d.file(".svg")), false))));
        }
    }
    let paths: Vec<String> = order
        .iter()
        .filter_map(|(_, w)| w.as_ref().err().map(|(p, _)| p.clone()))
        .collect();
    let mut texts = at.read(&paths).into_iter();
    let mut before = Legends::default();
    for (name, was) in order {
        let set = match was {
            Ok(set) => set,
            Err((path, manifest)) => {
                let text = texts.next().flatten().or_else(|| mirror_copy(root, &path));
                if manifest {
                    ink_classes(text.as_deref())
                } else {
                    sheet_kinds(text.as_deref())
                }
            }
        };
        before.put(&name, set);
    }
    let empty = BTreeSet::new();
    let pool_legend: BTreeSet<String> = before.0.iter().flat_map(|(_, s)| s.clone()).collect();
    let mut units = Vec::new();
    let mut owed: BTreeMap<String, (String, String)> = BTreeMap::new();
    for d in new_folders {
        let kind = if d.is_sheet() { "sheet" } else { "map" };
        let check = if d.is_sheet() {
            "building-review"
        } else {
            "settlement-review"
        };
        units.push(Unit::new(
            check,
            &d.name,
            &d.name,
            format!("a {kind} new to the pool"),
        ));
        for element in tree.legends.get(&d.name).unwrap_or(&empty) - &pool_legend {
            let why = format!(
                "{} is new to the pool's legend (on the new {kind} {})",
                py_repr(&element),
                d.name
            );
            owed.entry(element).or_insert((d.name.clone(), why));
        }
    }
    for (name, was) in &before.0 {
        for element in tree.legends.get(name).unwrap_or(&empty) - was {
            let why = format!("{} is new to {name}", py_repr(&element));
            owed.entry(element).or_insert((name.clone(), why));
        }
    }
    let sheets: BTreeSet<String> = tree
        .folders
        .iter()
        .filter(|d| d.is_sheet())
        .map(|d| d.name.clone())
        .collect();
    units.extend(element_units(&owed, &sheets));
    units
}

/// `moves.moved_only`, in-process: the names whose working-tree content is a blob the base already held.
fn moved_only(root: &Path, base: &str, names: &[String]) -> BTreeSet<String> {
    if base.is_empty() || names.is_empty() {
        return BTreeSet::new();
    }
    crate::checks::moves::moved_only(root, base, names)
}

/// Every owed unit, detected and declared, deduplicated, in dispatch order: `(the base's description, units, problems)`.
#[must_use]
pub fn all_owed(root: &Path) -> (String, Vec<Unit>, Vec<String>) {
    let (base, desc) = base_of(root);
    let tree = Tree::read(root);
    let declared = declared(&tree, &base);
    let mut seen: Vec<Unit> = Vec::new();
    for u in detected(&tree, &base).into_iter().chain(declared.units) {
        let slug = u.slug();
        let Some(i) = seen.iter().position(|p| p.slug() == slug) else {
            seen.push(u);
            continue;
        };
        let more = u.occasion.split_once("): ").map_or("", |(_, m)| m);
        let prev = &seen[i];
        if !more.is_empty() && !prev.occasion.contains(more) {
            let occasion = if prev.occasion.contains("): ") {
                format!("{}; {more}", prev.occasion)
            } else {
                format!("{}: {more}", prev.occasion)
            };
            seen[i] = Unit::new(&prev.check, &prev.subject, &prev.on, occasion);
        }
    }
    let rank = |u: &Unit| {
        CHECKS
            .iter()
            .position(|c| *c == u.check)
            .unwrap_or(usize::MAX)
    };
    seen.sort_by(|a, b| (rank(a), &a.subject).cmp(&(rank(b), &b.subject)));
    (desc, seen, declared.problems)
}

/// The units DUE: every non-glyph unit, and the glyph units the feature's hour makes due; at `landing`, every owed unit.
#[must_use]
pub fn owed(root: &Path, landing: bool) -> (String, Vec<Unit>, Vec<String>) {
    let (desc, units, problems) = all_owed(root);
    if landing {
        return (desc, units, problems);
    }
    let due = glyph::glyph_due(root, &units, None).0;
    let kept = units
        .into_iter()
        .filter(|u| u.check != "glyph-check" || due.contains(u))
        .collect();
    (desc, kept, problems)
}

/// Drawing or placement code the delta touches (committed, staged, unstaged or untracked), less what it only moved.
fn touched_code(root: &Path, base: &str) -> Vec<String> {
    let diff = if base.is_empty() {
        String::new()
    } else {
        git(root, &["diff", "--name-only", base]).unwrap_or_default()
    };
    let untracked = git(root, &["ls-files", "--others", "--exclude-standard"]).unwrap_or_default();
    let names: BTreeSet<String> = diff
        .lines()
        .chain(untracked.lines())
        .filter(|p| !p.is_empty() && found(&CODE, p) && !p.contains("/tests/"))
        .map(str::to_owned)
        .collect();
    let listed: Vec<String> = names.iter().cloned().collect();
    let moved = moved_only(root, base, &listed);
    names.into_iter().filter(|n| !moved.contains(n)).collect()
}

/// The refusal when drawing or placement code moved and no active feature declares its occasions, else None.
#[must_use]
pub fn check_declared(root: &Path) -> Option<String> {
    let (base, _) = base_of(root);
    let code = touched_code(root, &base);
    if code.is_empty() || declared(&Tree::read(root), &base).any_section {
        return None;
    }
    let mut shown = code.iter().take(5).cloned().collect::<Vec<_>>().join(", ");
    if code.len() > 5 {
        let _ = write!(shown, " and {} more", code.len() - 5);
    }
    Some(format!(
        "drawing or placement code moved ({shown}) and no active feature's tasks.md has an `## Occasions` section, nor any commit \
         of the delta an `Occasion:` line. Declare what the change re-places or redraws - `- placement-changed: <class>` (or `<class> on <map>` for the map it moved), \
         `- glyph-redrawn: <class>`, ... or `- none: <why>` in the feature's tasks.md; a tweak with no feature puts \
         `Occasion: glyph-redrawn: <class> - <why>` in its commit message \
         (feature 294: whether a change is substantial is the feature's to declare, never silent)"
    ))
}

/// The one-line answer a person or a guard message quotes.
#[must_use]
pub fn ruling(desc: &str, units: &[Unit], problems: &[String]) -> String {
    let head = if units.is_empty() {
        format!("no review owed against {desc}: no occasion in the delta")
    } else {
        let each: Vec<String> = units
            .iter()
            .map(|u| {
                let on = if u.on.is_empty() { "?" } else { &u.on };
                format!("{}:{} on {on} ({})", u.check, u.subject, u.occasion)
            })
            .collect();
        format!("owed against {desc}: {}", each.join("; "))
    };
    if problems.is_empty() {
        head
    } else {
        format!("{head} | PROBLEMS: {}", problems.join("; "))
    }
}

const MODES: [&str; 6] = [
    "--why",
    "--units",
    "--check-declared",
    "--glyph-gate",
    "--glyph-dispatched",
    "--landing-mark",
];

fn usage(why: &str) -> Reply {
    reply(String::new(), format!("l7r-gate reviews owed: {why}\n"), 2)
}

/// `review_owed.py`'s command line.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let specs = [
        Spec::value("--root"),
        Spec::flag("--why"),
        Spec::flag("--units"),
        Spec::flag("--check-declared"),
        Spec::value("--glyph-gate"),
        Spec::value("--glyph-dispatched"),
        Spec::value("--landing-mark"),
        Spec::flag("--landing"),
        Spec::flag("--escaped"),
        Spec::flag("--help"),
    ];
    let p = match parse(args, &specs) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    if p.on("--help") {
        return reply(
            "usage: l7r-gate reviews owed [--root DIR] [--why | --units | --check-declared | --glyph-gate SLUG | --glyph-dispatched SLUG | --landing-mark {on,off}] [--landing] [--escaped]\n".to_owned(),
            String::new(),
            0,
        );
    }
    let given: Vec<&str> = MODES
        .iter()
        .copied()
        .filter(|m| p.on(m) || p.has(m))
        .collect();
    if given.len() > 1 {
        return usage(&format!(
            "argument {}: not allowed with argument {}",
            given[1], given[0]
        ));
    }
    let mark = p.text("--landing-mark", "");
    if p.has("--landing-mark") && !matches!(mark, "on" | "off") {
        return usage(&format!(
            "argument --landing-mark: invalid choice: {}",
            py_repr(mark)
        ));
    }
    let asked = p.text("--root", ".");
    let Some(top) =
        git(&py_path(asked), &["rev-parse", "--show-toplevel"]).filter(|t| !t.is_empty())
    else {
        return reply(
            String::new(),
            format!("_review_owed: {asked} is not a git repository\n"),
            1,
        );
    };
    let root = PathBuf::from(top);
    run(&root, &p, mark)
}

fn run(root: &Path, p: &crate::record::args::Parsed, mark: &str) -> Reply {
    if p.on("--check-declared") {
        return check_declared(root).map_or_else(
            || reply(String::new(), String::new(), 0),
            |r| reply(r + "\n", String::new(), 1),
        );
    }
    if !mark.is_empty() {
        glyph::mark_landing(root, mark == "on");
        return reply(String::new(), String::new(), 0);
    }
    let (gate, dispatched) = (p.text("--glyph-gate", ""), p.text("--glyph-dispatched", ""));
    if !gate.is_empty() || !dispatched.is_empty() {
        let slug = if gate.is_empty() { dispatched } else { gate };
        let (code, out) = glyph::glyph_cli(root, slug, !gate.is_empty(), p.on("--escaped"));
        return reply(out, String::new(), code);
    }
    let landing = p.on("--landing");
    let (desc, all, problems) = all_owed(root);
    let (due, waiting) = if landing {
        (all.clone(), Vec::new())
    } else {
        glyph::glyph_due(root, &all, None)
    };
    let units: Vec<Unit> = all
        .into_iter()
        .filter(|u| landing || u.check != "glyph-check" || due.contains(u))
        .collect();
    let mut out = String::new();
    if p.on("--why") {
        out += &ruling(&desc, &units, &problems);
        out.push('\n');
        if !waiting.is_empty() {
            let each: Vec<String> = waiting
                .iter()
                .map(|(u, when)| format!("{} ({when})", u.slug()))
                .collect();
            let _ = writeln!(
                out,
                "glyph checks owed and not yet due (feature 375 amendment 9 - on the feature's hour, or at landing): {}",
                each.join(", ")
            );
        }
    } else if p.on("--units") {
        for u in &units {
            let _ = writeln!(
                out,
                "{}\t{}\t{}\t{}\t{}",
                u.slug(),
                u.check,
                u.subject,
                u.on,
                u.occasion
            );
        }
    } else {
        for u in &units {
            let _ = writeln!(out, "{}", u.slug());
        }
    }
    reply(out, String::new(), 0)
}

mod declared;
pub use declared::declared;
#[cfg(test)]
pub use declared::occasions_section;

#[cfg(test)]
mod tests;
