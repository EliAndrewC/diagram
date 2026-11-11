//! The occasions a feature DECLARES (feature 294; from `review_owed.py`, feature 449 T89): the `## Occasions` section of each active
//! feature's `tasks.md`, one `- <kind>: <argument>` line each, or a tweak's `Occasion:` commit line; a line on main at the base was
//! judged when it landed.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{found, re, Tree, Unit, DECLARED};
use crate::record::bundle::py_repr;
use crate::reviews::git;

static OCCASION: LazyLock<Regex> =
    LazyLock::new(|| re(r"^\s*-\s*(?P<kind>[a-z-]+)\s*:\s*(?P<arg>.+?)\s*$"));
static OPEN_BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[ \]"));
static SECTION: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?ms)^## Occasions\s*$(?P<body>.*?)(?=^## |\z)"));
static COMMIT_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"^Occasion:\s*(.*)$"));

/// A file at the base, stripped, as `_shown` read it (once a run: a lookup asks one feature's `tasks.md` up to six times).
struct Shown<'a> {
    root: &'a Path,
    base: &'a str,
    seen: BTreeMap<String, Option<String>>,
}

impl Shown<'_> {
    fn get(&mut self, path: &str) -> Option<String> {
        let (root, base) = (self.root, self.base);
        self.seen
            .entry(path.to_owned())
            .or_insert_with(|| git(root, &["show", &format!("{base}:{path}")]))
            .clone()
    }
}

fn read_strict(path: &Path) -> String {
    std::fs::read_to_string(path)
        .map(|t| crate::record::repo::universal(&t))
        .unwrap_or_default()
}

/// The feature directories this delta is the work of: the open feature the pointer names, and every `specs/NNN-*/` with a
/// `tasks.md` the delta touches that had not landed at the base.
fn active_features(root: &Path, base: &str, shown: &mut Shown) -> Vec<String> {
    let mut found: BTreeSet<String> = BTreeSet::new();
    let pointer = std::fs::read_to_string(root.join(".specify/feature.json"))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| {
            v.get("feature_directory")
                .map(crate::record::bundle::py_str)
        })
        .unwrap_or_default()
        .trim_end_matches('/')
        .to_owned();
    if !pointer.is_empty() {
        let tasks = root.join(&pointer).join("tasks.md");
        if tasks.is_file() && found_box(&read_strict(&tasks)) {
            found.insert(pointer);
        }
    }
    let touched = if base.is_empty() {
        String::new()
    } else {
        git(root, &["diff", "--name-only", base, "--", "specs"]).unwrap_or_default()
    };
    for path in touched.lines() {
        let parts: Vec<&str> = Path::new(path)
            .components()
            .map(|c| c.as_os_str().to_str().unwrap_or(""))
            .collect();
        if parts.len() < 2
            || parts[0] != "specs"
            || !root.join("specs").join(parts[1]).join("tasks.md").is_file()
        {
            continue;
        }
        let was = shown
            .get(&format!("specs/{}/tasks.md", parts[1]))
            .unwrap_or_default();
        let now = read_strict(&root.join("specs").join(parts[1]).join("tasks.md"));
        if !was.is_empty() && was.contains("- [x]") && !found_box(&was) && now.trim() == was.trim()
        {
            continue;
        }
        found.insert(format!("specs/{}", parts[1]));
    }
    found.into_iter().collect()
}

fn found_box(text: &str) -> bool {
    found(&OPEN_BOX, text)
}

/// Python's `str.splitlines`: every line boundary it knows.
fn splitlines(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut rest = text;
    while !rest.is_empty() {
        let Some((i, c)) = rest.char_indices().find(|(_, c)| {
            matches!(
                c,
                '\n' | '\r'
                    | '\u{0b}'
                    | '\u{0c}'
                    | '\u{1c}'
                    | '\u{1d}'
                    | '\u{1e}'
                    | '\u{85}'
                    | '\u{2028}'
                    | '\u{2029}'
            )
        }) else {
            out.push(rest);
            break;
        };
        out.push(&rest[..i]);
        let width = if c == '\r' && rest[i + 1..].starts_with('\n') {
            2
        } else {
            c.len_utf8()
        };
        rest = &rest[i + width..];
    }
    out
}

fn occasion(line: &str) -> Option<(String, String)> {
    let c = OCCASION.captures(line).ok().flatten()?;
    Some((c["kind"].to_owned(), c["arg"].to_owned()))
}

/// The `(kind, argument)` lines of a `tasks.md`'s `## Occasions` section, or None when it has no such section.
pub(crate) fn occasions_section(text: &str) -> Option<Vec<(String, String)>> {
    let c = SECTION.captures(text).ok().flatten()?;
    let body = c.name("body").map_or("", |m| m.as_str());
    Some(splitlines(body).into_iter().filter_map(occasion).collect())
}

/// The `Occasion: <kind>: <argument>` lines of the delta's own commit messages - where a tweak declares.
fn commit_occasions(root: &Path, base: &str) -> Vec<(String, String)> {
    if base.is_empty() {
        return Vec::new();
    }
    let log = git(root, &["log", "--format=%B", &format!("{base}..HEAD")]).unwrap_or_default();
    splitlines(&log)
        .into_iter()
        .filter_map(|line| {
            let c = COMMIT_LINE.captures(line.trim()).ok().flatten()?;
            occasion(&format!("- {}", c.get(1).map_or("", |m| m.as_str())))
        })
        .collect()
}

/// A section's `(kind, argument)` lines.
type Lines = Vec<(String, String)>;

/// What `declared` found: the units, the problems with the declarations, and whether any feature declares at all.
pub(crate) struct Declared {
    pub units: Vec<Unit>,
    pub problems: Vec<String>,
    pub any_section: bool,
}

fn declared_units(
    tree: &Tree,
    source: &str,
    kind: &str,
    arg: &str,
    checks: &[&str],
    out: &mut Declared,
) {
    let subject = arg.split(" - ").next().unwrap_or("").trim();
    let what = arg.split_once(" - ").map_or("", |(_, w)| w).trim();
    let said = if what.is_empty() {
        String::new()
    } else {
        format!(": {what}")
    };
    for check in checks {
        if *check == "glyph-check" {
            let (element, at) = subject.split_once(" on ").unwrap_or((subject, ""));
            let (element, at) = (element.trim(), at.trim());
            let on = if at.is_empty() {
                let on = tree.legends.first_drawing(element);
                if on.is_empty() {
                    out.problems.push(format!(
                        "{source}: {kind}: {} is drawn on no pool map or sheet",
                        py_repr(element)
                    ));
                }
                on
            } else {
                let on = if tree.legends.get(at).is_some_and(|s| s.contains(element)) {
                    at.to_owned()
                } else {
                    String::new()
                };
                if on.is_empty() {
                    out.problems.push(format!(
                        "{source}: {kind}: {} is not drawn on {}",
                        py_repr(element),
                        py_repr(at)
                    ));
                }
                on
            };
            out.units.push(Unit::new(
                check,
                element,
                &on,
                format!("declared {kind} ({source}){said}"),
            ));
        } else if kind == "new-program" {
            let (program, sheet) = subject.split_once(' ').unwrap_or((subject, ""));
            let sheet = sheet.trim();
            let named = if *check == "building-review" {
                sheet
            } else {
                program
            };
            out.units.push(Unit::new(
                check,
                named,
                sheet,
                format!("declared {kind} {program} ({source}){said}"),
            ));
        } else {
            out.units.push(Unit::new(
                check,
                subject,
                subject,
                format!("declared {kind} ({source}){said}"),
            ));
        }
    }
}

/// The units the active features (and the delta's commit messages) declare, the problems, whether any declares at all.
pub(crate) fn declared(tree: &Tree, base: &str) -> Declared {
    let root = tree.root;
    let mut shown = Shown {
        root,
        base,
        seen: BTreeMap::new(),
    };
    let mut sources: Vec<(String, Option<Lines>)> = Vec::new();
    for feature in active_features(root, base, &mut shown) {
        let tasks = root.join(&feature).join("tasks.md");
        let lines = occasions_section(&read_strict(&tasks));
        let landed: BTreeSet<(String, String)> = if base.is_empty() {
            BTreeSet::new()
        } else {
            occasions_section(
                &shown
                    .get(&format!("{feature}/tasks.md"))
                    .unwrap_or_default(),
            )
            .unwrap_or_default()
            .into_iter()
            .collect()
        };
        sources.push((
            feature,
            lines.map(|l| l.into_iter().filter(|o| !landed.contains(o)).collect()),
        ));
    }
    let tweak = commit_occasions(root, base);
    if !tweak.is_empty() {
        sources.push(("the delta's commit messages".to_owned(), Some(tweak)));
    }
    let mut out = Declared {
        units: Vec::new(),
        problems: Vec::new(),
        any_section: false,
    };
    for (source, lines) in sources {
        let Some(lines) = lines else { continue };
        out.any_section = true;
        for (kind, arg) in lines {
            let Some((_, checks)) = DECLARED.iter().find(|(k, _)| *k == kind) else {
                let known: Vec<&str> = DECLARED.iter().map(|(k, _)| *k).collect();
                out.problems.push(format!(
                    "{source}: unknown occasion {} (one of {})",
                    py_repr(&kind),
                    known.join(", ")
                ));
                continue;
            };
            declared_units(tree, &source, &kind, &arg, checks, &mut out);
        }
    }
    out
}
