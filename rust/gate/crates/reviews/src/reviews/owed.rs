//! Which review checks are OWED by this delta, keyed on OCCASIONS (feature 294; ported from `scripts/reviews/review_owed.py`, feature
//! 449 T89). Each judgment check is owed only on the occasion its answer can change (`specs/294-settlement-review-rethink/research.md`
//! R1), and "a manifest moved" owes nothing: a map or sheet new to the pool, an element new to a map or sheet, or an occasion a
//! feature's `## Occasions` section (or a tweak's `Occasion:` commit line) declares. The reasons behind each rule stand in the
//! Python's comments, kept in git history; the words a person reads are the Python's.
//!
//! `l7r-gate reviews owed [--root DIR] [--why | --units | --undrawn | --check-declared | --check-drawn | --glyph-gate SLUG | --glyph-dispatched SLUG |
//! --landing-mark on|off] [--landing] [--escaped]`.

use l7r_shared::env::Rooted;
use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{git, glyph};
use crate::record::bundle::py_repr;
use crate::record::repo::cat_blobs;

pub use l7r_gate_pool::TREES;
use l7r_gate_pool::{walk, Kind, Map, LEGACY};

/// The checks an occasion can owe, in the order a session dispatches them.
const CHECKS: [&str; 5] = [
    "settlement-review",
    "building-review",
    "glyph-check",
    "size-audit",
    "fix-check",
];
/// Whether a name has a review unit's slug form, `<check>--<subject>` (449 T312): no map's name, since none starts with a check's.
#[must_use]
pub fn is_unit_slug(name: &str) -> bool {
    CHECKS.iter().any(|c| {
        name.strip_prefix(c)
            .is_some_and(|rest| rest.starts_with("--"))
    })
}
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
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static DATA_KIND: LazyLock<Regex> = LazyLock::new(|| re(r#"data-kind="([^"]+)""#));
/// Drawing or placement code - never the incremental gate in `l7r/diagram/ci/`, which draws and places nothing. The Rust engines' code
/// is not here: a change that redraws an element owes its glyph-check, read from the change (`redrawn`, 449 T237), and is refused
/// nothing for it; a change that redraws no element - a Rust stage, the compound's layout, the driver's own placement - is refused
/// undeclared as these paths are (`redrawn::placed`, 449 T238).
// a pool map's drawing is its spec - a hamlet's `.spec.json`, a compound's `.compound.json`, a hand sheet's `.svg` - since feature 449 T221
// deleted the `.gen.py` files that wrapped them
static CODE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"^(l7r/(?!diagram/ci/).+\.py|(pool|legacy-hand-authored-pool)/.+\.(spec\.json|compound\.json|svg))$",
    )
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

/// `(ref, description)`: the merge base of HEAD with origin/main; HEAD without origin/main; "" with no commits. At a hand-in, the base
/// it names (`l7r_gate_core::delta_base`, 461 T42): the work applied on it is judged, not every staged batch below it.
#[must_use]
pub fn base_of(root: &Path) -> (String, String) {
    if let Some(base) = l7r_gate_core::delta_base::named(root) {
        let desc = format!("the hand-in base ({})", head8(&base));
        return (base, desc);
    }
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

/// A map or sheet folder: `<tree>/<category>/<name>`, as the pool walk found and classified it (feature 449 T220: its files asked of the
/// walk's listing, never stat-ed again).
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Folder {
    pub path: PathBuf,
    pub name: String,
    tree: &'static str,
    kind: Kind,
    files: Vec<String>,
}

impl From<Map> for Folder {
    fn from(m: Map) -> Self {
        Self {
            path: m.dir,
            name: m.name,
            tree: m.tree,
            kind: m.kind,
            files: m.files,
        }
    }
}

impl Folder {
    fn file(&self, ext: &str) -> PathBuf {
        self.path.join(format!("{}{ext}", self.name))
    }

    fn has(&self, ext: &str) -> bool {
        self.files.contains(&format!("{}{ext}", self.name))
    }

    /// A Mode A sheet: a generated compound or a hand sheet, by the walk's precedence.
    #[must_use]
    pub fn is_sheet(&self) -> bool {
        self.kind.is_sheet()
    }

    /// A hand-drawn Mode B map awaiting conversion owes no review: a legacy folder that is no Mode A sheet.
    fn exempt(&self) -> bool {
        self.tree == LEGACY && !self.is_sheet()
    }

    /// A folder the walk could classify: a hamlet, a sheet or a frozen exhibit (one it reported is no map).
    fn drawn(&self) -> bool {
        self.kind != Kind::Report
    }
}

/// Every map or sheet folder, from the one pool walk (feature 449 T220): the live pool first, then by tier and name, hidden names
/// included.
#[must_use]
pub fn folders(root: &Path) -> Vec<Folder> {
    walk(root).maps.into_iter().map(Folder::from).collect()
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

/// The `data-kind`s a Mode A sheet's SVG tags, less what is no element (its placeholder marks `-`, the compound's title among them: read
/// as an element, a sheet whose base could not be read owed `glyph-check----<sheet>` and `size-audit--`, units nobody can run, 449 T238).
pub fn sheet_kinds(text: Option<&str>) -> BTreeSet<String> {
    DATA_KIND
        .captures_iter(text.unwrap_or(""))
        .map_while(Result::ok)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
        .filter(|k| !NOT_ELEMENTS.contains(&k.as_str()))
        .collect()
}

/// The Rust driver's record of a live hamlet's drawing (449 T230): its ink census is the hamlet's legend, where the tracked
/// `<name>.json` is the deleted Python's, never rewritten.
const DRIVER: &str = ".driver.json";

/// Whether a record holds an ink census at all, as distinct from one naming no element: a record with none was drawn by no driver
/// that keeps one.
fn has_census(text: Option<&str>) -> bool {
    serde_json::from_str::<Value>(text.unwrap_or("")).is_ok_and(|v| v.get("ink_classes").is_some())
}

/// One folder's elements now: a live hamlet's the Rust driver's ink census, read only where the generation cache serves that drawing
/// as current (else the elements it draws are not known, and the problem says how to draw it); a sheet's its kinds, a generated
/// compound's only where its drawing is current too (449 T231). (A folder read by
/// its `<name>.json` alone is a frozen exhibit, which only the legacy tree holds and which owes no review: `Folder::exempt`.)
fn legend_of(
    d: &Folder,
    current: &mut dyn FnMut(&Folder) -> bool,
) -> Result<Option<BTreeSet<String>>, String> {
    if d.kind == Kind::Hamlet {
        let text = std::fs::read(d.file(DRIVER))
            .ok()
            .map(|b| String::from_utf8_lossy(&b).into_owned());
        return if !current(d) {
            Err(
                "its Rust drawing is not current, so the elements it draws are not known"
                    .to_owned(),
            )
        } else if has_census(text.as_deref()) {
            Ok(Some(ink_classes(text.as_deref())))
        } else {
            Err("its Rust drawing records no ink census (drawn before 449 T230)".to_owned())
        };
    }
    // A GENERATED COMPOUND'S `.svg` IS ITS DRAWING (449 T231): read as last drawn whatever its program says now, so an edit not redrawn
    // owed none of the reviews its new elements owe, and no caller was told; a hand sheet's `.svg` is its spec, current by being it
    if d.kind == Kind::Compound && d.tree != LEGACY && !current(d) {
        return Err(
            "its drawing is not current, so the elements it draws are not known".to_owned(),
        );
    }
    Ok(if d.has(".svg") {
        Some(sheet_kinds(Some(&read_replace(&d.file(".svg")))))
    } else {
        None
    })
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

/// `legends`: each non-exempt folder's elements now, and a problem for each live hamlet or compound whose elements are not known (with
/// the folder's name, `hidden.rs` adding the units it hides); a folder the pool walk could not classify is no map and draws nothing
/// (feature 449 T220). `stale` names an engine whose binary is older than its sources (451 T164): every map it draws is not current, and
/// the problem says so, where it read as one map's drawing.
pub fn legends(
    root: &Path,
    all: &[Folder],
    current: &mut dyn FnMut(&Folder) -> bool,
    stale: &mut dyn FnMut(&Folder) -> Option<String>,
) -> (Legends, Vec<String>, Vec<(usize, String)>) {
    let mut out = Legends::default();
    let mut problems = Vec::new();
    let mut unknown = Vec::new();
    for d in all.iter().filter(|d| !d.exempt() && d.drawn()) {
        match legend_of(d, current) {
            Ok(Some(set)) => out.put(&d.name, set),
            Ok(None) => {}
            Err(why) => {
                let at = rel(root, &d.path);
                let why = match stale(d) {
                    Some(engine) => format!("{why}: {engine}"),
                    None => why,
                };
                unknown.push((problems.len(), d.name.clone()));
                problems.push(format!(
                    "{at}: {why} - `make map MAP={at}` draws it, and the reviews it owes are read from that"
                ));
            }
        }
    }
    (out, problems, unknown)
}

/// The live maps whose drawing is a render the generation cache keeps and does not serve as current (449 T231), `(kind, folder)`: a
/// hamlet, whose elements are its Rust drawing's census and so unknown (a problem line, never a unit), and a generated compound, whose
/// `.svg` would be read as it was last drawn - so an edit not redrawn owed none of the reviews its new elements owe. The review gate
/// redraws each before it asks what is owed. A hand sheet is never listed: its `.svg` is its spec, the legend read from it is the
/// sheet as it is now (`spec_of`), and a redraw changes only its page. A legacy folder is frozen and is never drawn.
pub fn undrawn(
    root: &Path,
    all: &[Folder],
    current: &mut dyn FnMut(&Folder) -> bool,
) -> Vec<(&'static str, String)> {
    all.iter()
        .filter(|d| d.tree != LEGACY && matches!(d.kind, Kind::Hamlet | Kind::Compound))
        .filter(|d| !current(d))
        .map(|d| (d.kind.tag(), rel(root, &d.path)))
        .collect()
}

/// What the owed lookup reads once a run: the folders, their legends now, and the hamlets and compounds whose legends are not known.
pub struct Tree<'a> {
    pub root: &'a Path,
    pub folders: Vec<Folder>,
    pub legends: Legends,
    pub problems: Vec<String>,
    /// Each folder whose legend is not known: its problem line's index and its name (451 T164, `hidden.rs`).
    pub unknown: Vec<(usize, String)>,
}

impl<'a> Tree<'a> {
    /// The tree, a live hamlet's or compound's drawing asked of the generation cache read-only (`l7r_gate_pool::Currency`, no engine
    /// built; one walk and one launcher start an engine, 449 T231).
    #[must_use]
    pub fn read(root: &'a Path) -> Self {
        let folders = folders(root);
        let mut currency = l7r_gate_pool::Currency::new(root);
        let mut engines = hidden::Engines::new(root);
        let (legends, problems, unknown) = legends(
            root,
            &folders,
            &mut |d| currency.of(&d.path.display().to_string()),
            &mut |d| engines.stale(d.kind),
        );
        Self {
            root,
            folders,
            legends,
            problems,
            unknown,
        }
    }
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

/// Each folder's legend at the base, in folder order: known now (a moved folder), or read at the base in one batch.
fn base_legends(root: &Path, at: &mut AtBase, order: Vec<(String, AtBaseOrNow)>) -> Legends {
    let paths: Vec<String> = order
        .iter()
        .filter_map(|(_, w)| w.as_ref().err().map(|(p, _)| p.clone()))
        .collect();
    // A HAMLET'S BASE CENSUS (449 T230): its `.driver.json` is gitignored, so main's mirror copy - and where no driver's census stands
    // there either (drawn before T230's driver, or no mirror), the tracked `<name>.json` the deleted Python wrote, the base's only
    // record of what the hamlet drew. Without it every element the driver draws would read as new to the map.
    let olds: Vec<String> = paths
        .iter()
        .filter_map(|p| p.strip_suffix(DRIVER).map(|stem| format!("{stem}.json")))
        .collect();
    let mut texts = at.read(&paths).into_iter();
    let mut old_texts = at.read(&olds).into_iter();
    let mut before = Legends::default();
    for (name, was) in order {
        let set = match was {
            Ok(set) => set,
            Err((path, manifest)) => {
                let mut text = texts.next().flatten().or_else(|| mirror_copy(root, &path));
                if let Some(stem) = path.strip_suffix(DRIVER) {
                    let old = old_texts.next().flatten();
                    if !has_census(text.as_deref()) {
                        text = old.or_else(|| mirror_copy(root, &format!("{stem}.json")));
                    }
                }
                if manifest {
                    ink_classes(text.as_deref())
                } else {
                    sheet_kinds(text.as_deref())
                }
            }
        };
        before.put(&name, set);
    }
    before
}

/// The occasions the delta itself shows - maps and sheets new to the pool, and elements new to a map or sheet - with each standing
/// folder's legend at the base, which `hidden.rs` reads the units a stale map hides against.
fn detected_at(tree: &Tree, base: &str) -> (Vec<Unit>, Legends) {
    let root = tree.root;
    let mut at = AtBase::new(root, base);
    let live: Vec<&Folder> = tree
        .folders
        .iter()
        .filter(|d| !d.exempt() && d.drawn())
        .collect();
    let unborn: BTreeSet<String> = live
        .iter()
        .map(|d| rel(root, &d.path))
        .filter(|r| !at.existed(r))
        .collect();
    // A FOLDER NOT AT THE BASE IS NEW TO THE POOL unless the delta RENAMED it (449 T233): its spec moved with it, by git's rename
    // detection. Before, it read as moved when any one of its files was a blob the base held, so a new hamlet whose spec or notes matched
    // another's text owed no settlement-review, even at integrated (measured 2026-11-19 in a scratch fixture).
    let moved_to: BTreeSet<String> = if unborn.is_empty() {
        BTreeSet::new()
    } else {
        renamed(root, base, &tree.folders).into_values().collect()
    };
    let mut new_folders: Vec<&Folder> = Vec::new();
    // each folder's legend at the base, in folder order: known now (a moved folder), or read at the base in one batch below
    let mut order: Vec<(String, AtBaseOrNow)> = Vec::new();
    for d in &live {
        let r = rel(root, &d.path);
        if unborn.contains(&r) {
            if moved_to.contains(&r) {
                order.push((
                    d.name.clone(),
                    Ok(tree.legends.get(&d.name).cloned().unwrap_or_default()),
                ));
            } else {
                new_folders.push(d);
            }
            continue;
        }
        if d.kind == Kind::Hamlet {
            order.push((d.name.clone(), Err((rel(root, &d.file(DRIVER)), true))));
        } else if d.has(".svg") {
            order.push((d.name.clone(), Err((rel(root, &d.file(".svg")), false))));
        }
    }
    let before = base_legends(root, &mut at, order);
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
    units.extend(redrawn::units(tree, base, &before));
    (units, before)
}

/// The spec a folder of this kind is drawn from, the file that names it: a hamlet's `.spec.json`, a compound's `.compound.json`, a hand
/// sheet's `.svg`, a frozen exhibit's `.json`.
fn spec_suffix(kind: Kind) -> Option<&'static str> {
    match kind {
        Kind::Hamlet => Some(".spec.json"),
        Kind::Compound => Some(".compound.json"),
        Kind::HandSheet => Some(".svg"),
        Kind::Frozen => Some(".json"),
        Kind::Report => None,
    }
}

/// The folders the delta RENAMED, `old folder -> new folder` (each from the root): a folder whose spec git's rename detection over the
/// delta (`git diff -M --diff-filter=R <base>`, the working tree against the base) finds moved from another folder, one no longer in the
/// pool. A copy beside its source is no rename (git pairs only a path the delta removed), nor is a file moved within its own folder
/// (449 T233).
pub(crate) fn renamed(root: &Path, base: &str, folders: &[Folder]) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    if base.is_empty() {
        return out;
    }
    let diff = git(
        root,
        &["diff", "-M", "--name-status", "--diff-filter=R", base, "--"],
    )
    .unwrap_or_default();
    let standing: BTreeSet<String> = folders.iter().map(|d| rel(root, &d.path)).collect();
    let pairs = diff.lines().filter_map(|line| {
        let mut parts = line.split('\t').skip(1);
        Some((parts.next()?, parts.next()?))
    });
    for (from, to) in pairs {
        let Some(d) = folders
            .iter()
            .find(|d| spec_suffix(d.kind).is_some_and(|suffix| rel(root, &d.file(suffix)) == to))
        else {
            continue;
        };
        let old = from.rsplit_once('/').map_or("", |(dir, _)| dir).to_owned();
        let new = rel(root, &d.path);
        if !old.is_empty() && old != new && !standing.contains(&old) {
            out.insert(old, new);
        }
    }
    out
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
    let (desc, units, problems, _) = owed_discharged(root);
    (desc, units, problems)
}

/// A unit the round arbiter's accept discharged (449 T377): its slug and the ruling's trigger.
pub type Discharged = (String, String);

/// [`all_owed`], with the glyph units a round arbiter's accept discharged taken out of its units and named (`discharged.rs`).
#[must_use]
pub fn owed_discharged(root: &Path) -> (String, Vec<Unit>, Vec<String>, Vec<Discharged>) {
    let (base, desc) = base_of(root);
    let tree = Tree::read(root);
    let declared = declared(&tree, &base);
    let (found, before) = detected_at(&tree, &base);
    let mut seen: Vec<Unit> = Vec::new();
    for u in found.into_iter().chain(declared.units) {
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
    // THE REVIEWS SET ASIDE AT RUST-ONLY (444 FR-023, 449 T232): owed once the port switch is thrown back, from the record the review
    // gate kept when it set them aside - the delta no longer holds them once the push has landed (`deferred.rs`)
    if crate::cohort::port_mode(root) != "rust-only" {
        for u in deferred::standing(&tree, &deferred::rows(root)) {
            if !seen.iter().any(|p| p.slug() == u.slug()) {
                seen.push(u);
            }
        }
    }
    seen.sort_by(|a, b| (rank(a), &a.subject).cmp(&(rank(b), &b.subject)));
    let taken = discharged::take(&tree, &mut seen);
    let mut problems = hidden::named(&tree, &before);
    problems.extend(declared.problems);
    (desc, seen, problems, taken)
}

/// The units DUE: every non-glyph unit, and the glyph units the feature's hour makes due; at `landing`, every owed unit.
#[must_use]
pub fn owed(root: &Path, landing: bool) -> (String, Vec<Unit>, Vec<String>) {
    owed_in(&Rooted::process(root), landing)
}

/// [`owed`] with the root's environment carried (feature 451 T38).
#[must_use]
pub fn owed_in(root: &Rooted, landing: bool) -> (String, Vec<Unit>, Vec<String>) {
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

/// Drawing or placement code the delta touches (committed, staged, unstaged or untracked), less what it only moved: `CODE`'s paths,
/// and the Rust engines' placement code whose code changed (`redrawn::placed`, 449 T238).
pub(super) fn touched_code(root: &Path, base: &str) -> Vec<String> {
    let delta = redrawn::delta_paths(root, base);
    let mut names: BTreeSet<String> = delta
        .iter()
        .filter(|p| found(&CODE, p) && !p.contains("/tests/"))
        .cloned()
        .collect();
    names.extend(redrawn::placed(root, base, &delta));
    let listed: Vec<String> = names.iter().cloned().collect();
    let moved = moved_only(root, base, &listed);
    names.into_iter().filter(|n| !moved.contains(n)).collect()
}

/// The refusal when drawing or placement code moved and no declaration answers this delta - a line of an active feature's `## Occasions`
/// naming the task the landing holds, or a commit's `Occasion:` line (449 T238 round 2: before, any section answered, one whose lines
/// had all landed or another feature's) - or when a declaration's form owes nothing anyone can run (449 T238: it read as declared, so
/// nothing was refused, and its unit, on no map, could not be dispatched), else None. Neither reads a legend: what a declaration names
/// is read from its words and the pool's folder names.
#[must_use]
pub fn check_declared(root: &Path) -> Option<String> {
    check_declared_as(root, None)
}

/// [`check_declared`] with the bundle `make verify` carries in read in place of the clone's started-task mark (451 T166).
#[must_use]
pub fn check_declared_as(root: &Path, started: Option<&Started>) -> Option<String> {
    let (base, _) = base_of(root);
    let forms = declared::forms(root, &base, started);
    let mut out: Vec<String> = Vec::new();
    if !forms.misformed.is_empty() {
        out.push(format!(
            "an `## Occasions` declaration owes a review nobody can run: {}",
            forms.misformed.join("; ")
        ));
    }
    let code = if forms.answered || !forms.tweak.is_empty() {
        Vec::new()
    } else {
        touched_code(root, &base)
    };
    if !code.is_empty() {
        out.push(undeclared(&code, &forms.why, &forms.task));
    }
    (!out.is_empty()).then(|| out.join("\n"))
}

/// The refusal's words for drawing or placement code moved with nothing declared for it: why no line answers, and the line to write,
/// naming the started task (`task`, or `<task>`).
pub(super) fn undeclared(code: &[String], why: &str, task: &str) -> String {
    let mut shown = code.iter().take(5).cloned().collect::<Vec<_>>().join(", ");
    if code.len() > 5 {
        let _ = write!(shown, " and {} more", code.len() - 5);
    }
    let t = if task.is_empty() { "<task>" } else { task };
    format!(
        "drawing or placement code moved ({shown}) and no declaration answers this delta: {why}. Declare what the change re-places \
         or redraws on a line of the started task's feature's `## Occasions`, naming the task - `- placement-changed: <element> on \
         <map> - {t}: <why>`, `- glyph-redrawn: <element> on <map> - {t}: <why>`, ... or `- none: {t} - <why>`; a tweak with no \
         feature puts `Occasion: none: <why>` (or `Occasion: glyph-redrawn: <element> - <why>`) in its commit message (feature 294: \
         whether a change is substantial is the feature's to declare, never silent; 449 T238: a section naming only other tasks, or \
         whose lines have all landed, answers nothing)"
    )
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

mod cli;
pub use cli::{cli, cli_in};
mod declared;
pub mod deferred;
pub mod discharged;
mod hidden;
mod marks;
mod redrawn;
#[cfg(test)]
pub use declared::occasions_section;
pub use declared::{check_drawn, declared, Started};

#[cfg(test)]
mod tests;
