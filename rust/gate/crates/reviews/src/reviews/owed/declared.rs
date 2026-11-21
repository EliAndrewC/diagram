//! The occasions a feature DECLARES (feature 294; from `review_owed.py`, feature 449 T89): the `## Occasions` section of each active
//! feature's `tasks.md`, one `- <kind>: <argument>` line each, or a tweak's `Occasion:` commit line; a line on main at the base was
//! judged when it landed.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{found, pool_map_names, re, safe, Tree, Unit, DECLARED};
use crate::record::bundle::py_repr;
use crate::reviews::git;
use l7r_gate_core::difflib::ratio;

// a line with nothing after its colon is read too (449 T238), so `- placement-changed:` is refused with its form, never passed over
static OCCASION: LazyLock<Regex> =
    LazyLock::new(|| re(r"^\s*-\s*(?P<kind>[a-z-]+)\s*:\s*(?P<arg>.*?)\s*$"));
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
pub fn occasions_section(text: &str) -> Option<Vec<(String, String)>> {
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
        // a commit line with nothing after its colon declares nothing, as before 449 T238 read such lines (`Occasion: none:` is no
        // declaration): a commit message cannot be rewritten, so it is never refused with its form either (`misformed`)
        .filter(|(_, arg)| !arg.is_empty())
        .collect()
}

/// The source a tweak's `Occasion:` commit lines are read from.
const TWEAK: &str = "the delta's commit messages";

/// A section's `(kind, argument)` lines.
type Lines = Vec<(String, String)>;

/// What `declared` found: the units and the problems with the declarations (whether a declaration answers the delta is `forms`', 449
/// T238 round 2).
pub struct Declared {
    pub units: Vec<Unit>,
    pub problems: Vec<String>,
    /// The refusal's words for each `tasks.md` glyph line naming an element its current drawing does not hold (`undrawn`, 449 T238
    /// round 2), which `check_drawn` refuses after the gate's redraw.
    pub undrawn: Vec<String>,
}

/// What a declaration of `kind` with `arg` fails to name - `element`, `map`, `sheet` or `program` - where its units would have a subject
/// nobody can run (449 T238: `placement-changed: - on kuwabata` became `glyph-check--`, on no map), else None.
fn nothing_named(kind: &str, arg: &str) -> Option<&'static str> {
    let subject = arg.split(" - ").next().unwrap_or("").trim();
    let blank = |text: &str| safe(text).is_empty();
    match kind {
        "glyph-redrawn" | "placement-changed" => {
            blank(subject.split_once(" on ").map_or(subject, |(e, _)| e)).then_some("element")
        }
        "new-program" => {
            let (program, sheet) = subject.split_once(' ').unwrap_or((subject, ""));
            if blank(program) {
                Some("program")
            } else {
                blank(sheet).then_some("sheet")
            }
        }
        "layout-revised" => blank(subject).then_some("sheet"),
        "new-form" | "new-tier" | "gm-fix" => blank(subject).then_some("map"),
        // `none`, the one kind left (each caller has found the kind among `DECLARED`)
        _ => blank(arg).then_some("reason"),
    }
}

/// The form a declaration of `kind` takes.
fn form(kind: &str) -> String {
    match kind {
        "glyph-redrawn" | "placement-changed" => {
            format!("`- {kind}: <element>` or `- {kind}: <element> on <map>`, the element a class the map draws")
        }
        "new-program" => "`- new-program: <program> <sheet>`".to_owned(),
        "layout-revised" => "`- layout-revised: <sheet>`".to_owned(),
        "gm-fix" => "`- gm-fix: <map> - <the complaint>`".to_owned(),
        "none" => "`- none: <why>`".to_owned(),
        _ => format!("`- {kind}: <map>`"),
    }
}

/// The line as written, for a refusal to quote.
fn written(kind: &str, arg: &str) -> String {
    format!("- {kind}: {arg}").trim_end().to_owned()
}

/// The map or sheet a declaration of `kind` names, where it names one: a glyph line's `on <map>`, a new form's, tier's or GM fix's map, a
/// revised layout's sheet, a new program's sheet.
fn named_map<'a>(kind: &str, arg: &'a str) -> Option<&'a str> {
    let subject = arg.split(" - ").next().unwrap_or("").trim();
    let map = match kind {
        "glyph-redrawn" | "placement-changed" => subject.split_once(" on ")?.1,
        "new-program" => subject.split_once(' ')?.1,
        "layout-revised" | "new-form" | "new-tier" | "gm-fix" => subject,
        _ => return None,
    };
    Some(map.trim())
}

/// The pool's map and sheet names, walked once and only when a declaration names a map (`forms`), or the tree's folders (`declared`).
struct Pool<'a> {
    root: &'a Path,
    names: Option<Vec<String>>,
}

impl Pool<'_> {
    fn names(&mut self) -> &[String] {
        let root = self.root;
        self.names.get_or_insert_with(|| pool_map_names(root))
    }

    /// Where the declaration names a map or sheet that is no pool map or sheet at all (449 T238 round 2: `well on nowhere` became a unit
    /// on no map), the refusal's words, naming the pool's three closest names. A name is read as its slug (`Kuwabata` is `kuwabata`).
    /// Whether the map draws the element is not asked: its drawing may be stale until the gate redraws it, and the element new to it.
    fn unknown(&mut self, kind: &str, arg: &str, source: &str) -> Option<String> {
        let map = named_map(kind, arg).filter(|m| !safe(m).is_empty())?;
        let names = self.names();
        if names.iter().any(|n| safe(n) == safe(map)) {
            return None;
        }
        let closest = closest(map, names.iter().collect());
        let closest = if closest.is_empty() {
            "the pool has none".to_owned()
        } else {
            format!("the closest: {}", closest.join(", "))
        };
        Some(format!(
            "`{}` ({source}) names `{map}`, no pool map or sheet - {closest}; write it {}, the map its folder's name",
            written(kind, arg),
            form(kind)
        ))
    }
}

/// The three of `names` closest to `wanted`, by `difflib`'s ratio over characters, ties by name.
fn closest<'n>(wanted: &str, names: Vec<&'n String>) -> Vec<&'n str> {
    let wanted: Vec<char> = wanted.chars().collect();
    let mut near: Vec<(f64, &String)> = names
        .into_iter()
        .map(|n| (ratio(&wanted, &n.chars().collect::<Vec<_>>()), n))
        .collect();
    near.sort_by(|a, b| b.0.total_cmp(&a.0).then_with(|| a.1.cmp(b.1)));
    near.into_iter().take(3).map(|(_, n)| n.as_str()).collect()
}

/// Where a glyph line names an element whose map's drawing is CURRENT and does not hold it (449 T238 round 2, the plan review's D9: a
/// unit on no map, which nobody can run), the refusal's words, naming the closest kinds drawn: on its named map when that map's legend is
/// known (`Tree::read` knows a legend only from a current drawing, so a map not current is left as it was - the element may be new to it),
/// or, with no map named, when every live map's legend is known (`tree.problems` empty) and none draws it.
fn undrawn(
    tree: &Tree,
    kind: &str,
    arg: &str,
    source: &str,
    element: &str,
    at: &str,
) -> Option<String> {
    let line = written(kind, arg);
    let (holds, near) = if at.is_empty() {
        if !tree.legends.first_drawing(element).is_empty() || !tree.problems.is_empty() {
            return None;
        }
        let all: BTreeSet<&String> = tree.legends.0.iter().flat_map(|(_, s)| s.iter()).collect();
        (
            "which no pool map or sheet draws - the closest drawn kinds",
            closest(element, all.into_iter().collect()),
        )
    } else {
        let set = tree.legends.get(at).filter(|s| !s.contains(element))?;
        ("", closest(element, set.iter().collect()))
    };
    let said = if at.is_empty() {
        holds.to_owned()
    } else {
        format!("which {at}'s drawing does not hold - its closest drawn kinds")
    };
    Some(format!(
        "`{line}` ({source}) names `{element}`, {said}: {}; write the element as the drawing names it, or `- none: <why>` where nothing \
         drawn is re-placed or redrawn",
        if near.is_empty() { "none".to_owned() } else { near.join(", ") }
    ))
}

/// Each declaration in a feature's `tasks.md` whose form owes nothing anyone can run (449 T238), the refusal's words for it: one naming
/// no element, map, sheet or reason, an unknown occasion, and one naming a map or sheet the pool does not hold - each a line that read
/// as declared and owed no review anyone can run. A tweak's commit line is never refused here: a commit message cannot be rewritten, so
/// the refusal could not be met; its line owes no unit and is a problem line (`declared`).
fn misformed(sources: &[(String, Option<Lines>)], pool: &mut Pool) -> Vec<String> {
    let known: Vec<&str> = DECLARED.iter().map(|(k, _)| *k).collect();
    let mut out = Vec::new();
    for (source, lines) in sources.iter().filter(|(s, _)| s != TWEAK) {
        for (kind, arg) in lines.iter().flatten() {
            let line = written(kind, arg);
            if !known.contains(&kind.as_str()) {
                out.push(format!(
                    "`{line}` ({source}) is no occasion (one of {})",
                    known.join(", ")
                ));
            } else if kind == "none" && nothing_named(kind, arg).is_some() {
                out.push(format!(
                    "`{line}` ({source}) names no reason - write it {}",
                    form(kind)
                ));
            } else if let Some(what) = nothing_named(kind, arg) {
                out.push(format!(
                    "`{line}` ({source}) names no {what} - write it {} (a ` - <why>` after it), or `- none: <why>` where nothing \
                     is re-placed or redrawn",
                    form(kind)
                ));
            } else if let Some(why) = pool.unknown(kind, arg, source) {
                out.push(why);
            }
        }
    }
    out
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
            if let Some(why) = undrawn(tree, kind, arg, source, element, at) {
                if source != TWEAK {
                    out.undrawn.push(why.clone());
                }
                out.problems.push(why);
                continue;
            }
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

/// Each active feature's (and the delta's commit messages') declarations not yet on main: `(source, its lines)`, None for a feature
/// with no `## Occasions` section.
fn sources(
    root: &Path,
    base: &str,
    features: &[String],
    shown: &mut Shown,
) -> Vec<(String, Option<Lines>)> {
    let mut sources: Vec<(String, Option<Lines>)> = Vec::new();
    for feature in features.iter().cloned() {
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
        sources.push((TWEAK.to_owned(), Some(tweak)));
    }
    sources
}

/// Whether `text` holds `task` as a word, never as the start of another (`T23` in `T238`).
fn names_task(text: &str, task: &str) -> bool {
    text.split(|c: char| !c.is_alphanumeric() && c != '_')
        .any(|w| w == task)
}

/// Whether a declaration of `kind` with `arg` is `task`'s OWN (449 T238 round 2: a line that only mentions the task, "found by T236"
/// inside another task's line, answered): a `none:` line's first word (`- none: T239 - <why>`); a declaration's tag, the first word
/// after its subject's ` - ` (`- placement-changed: marsh on kuwabata - T236: <why>`, the form the refusal prints and 449's and 444's
/// lines take, observed 2026-11-20); or its trailing parenthetical holding the task (`... (449 T236)`).
fn owns_task(kind: &str, arg: &str, task: &str) -> bool {
    let first = |text: &str| {
        text.split_whitespace()
            .next()
            .is_some_and(|w| w.trim_end_matches([':', ',', ';', '.']) == task)
    };
    let tagged = if kind == "none" {
        first(arg)
    } else {
        arg.split_once(" - ").is_some_and(|(_, why)| first(why))
    };
    let trailing = arg
        .trim_end()
        .strip_suffix(')')
        .and_then(|a| a.rfind('(').map(|i| &a[i + 1..]))
        .is_some_and(|inside| names_task(inside, task));
    tagged || trailing
}

/// A section's `(kind, argument)` lines with each one's wrapped continuation joined on (an indented line that opens no `- ` entry), as
/// 444 wraps its lines: a trailing parenthetical may sit on the continuation.
fn joined_entries(text: &str) -> Lines {
    let Some(c) = SECTION.captures(text).ok().flatten() else {
        return Vec::new();
    };
    let mut out: Lines = Vec::new();
    let mut open = false;
    for line in splitlines(c.name("body").map_or("", |m| m.as_str())) {
        if let Some(o) = occasion(line) {
            out.push(o);
            open = true;
        } else if open
            && line.starts_with([' ', '\t'])
            && !line.trim().is_empty()
            && !line.trim_start().starts_with('-')
        {
            if let Some((_, arg)) = out.last_mut() {
                arg.push(' ');
                arg.push_str(line.trim());
            }
        } else {
            open = false;
        }
    }
    out
}

/// Whether the task the landing holds is declared (449 T238 round 2): the clone's started task (`make task-start`'s mark, the one the
/// landing's holding box reads, `speckit::active_task`) of an active feature, not ticked at the base, named by a line of that feature's
/// `## Occasions` - the section as it stands, a line already on main included (a declaration pushed with the spec, before the code,
/// names the task all the same). Else why not, and the started task's id where there is one. Before, ANY section answered: one whose
/// every line had landed, another feature's (T236's commit, replayed with its own line taken out, was refused nothing).
fn started_answers(root: &Path, features: &[String], shown: &mut Shown) -> (bool, String, String) {
    for f in features {
        let task = l7r_shared::speckit::active_task(&root.join(f)).unwrap_or_default();
        if task.is_empty() {
            continue;
        }
        let ticked = re(&format!(
            r"(?m)^- \[[xX]\] {}\b",
            fancy_regex::escape(&task)
        ));
        if ["tasks.md", "tasks-done.md"]
            .iter()
            .any(|n| found(&ticked, &shown.get(&format!("{f}/{n}")).unwrap_or_default()))
        {
            return (
                false,
                format!(
                    "the started task, {f} {task}, was ticked on main already - start the task this delta is (`make task-start \
                     F=<feature> T=<task>`)"
                ),
                String::new(),
            );
        }
        let lines = joined_entries(&read_strict(&root.join(f).join("tasks.md")));
        let named = lines.iter().any(|(kind, arg)| owns_task(kind, arg, &task));
        let why = if named {
            String::new()
        } else {
            format!("the started task, {f} {task} (`make task-start`), is named by no line of its `## Occasions` as the line's own task")
        };
        return (named, why, task);
    }
    (
        false,
        "no task of an active feature is started (`make task-start F=<feature> T=<task>`)"
            .to_owned(),
        String::new(),
    )
}

/// What `check_declared` asks, with no legend read (the pool walked only when a declaration names a map): whether a declaration answers
/// this delta, why not, and the started task; the refusal's words for each declaration whose form owes nothing anyone can run (449
/// T238).
pub(super) struct Forms {
    /// A line naming the started task as its own (`started_answers`).
    pub answered: bool,
    /// The delta's commit `Occasion:` lines owing a review someone can run, each of which answers the delta at `--check-declared`; at
    /// `--check-drawn` one naming an element its map's current drawing does not hold answers nothing (`answers_drawn`, D9c).
    pub tweak: Lines,
    /// Why no line answers it, for the refusal.
    pub why: String,
    /// The started task's id, or "" where none answers.
    pub task: String,
    pub misformed: Vec<String>,
}

pub(super) fn forms(root: &Path, base: &str) -> Forms {
    let mut shown = Shown {
        root,
        base,
        seen: BTreeMap::new(),
    };
    let features = active_features(root, base, &mut shown);
    let sources = sources(root, base, &features, &mut shown);
    let mut pool = Pool { root, names: None };
    let misformed = misformed(&sources, &mut pool);
    let (answered, why, task) = started_answers(root, &features, &mut shown);
    // a commit line answers only as one owing a review someone can run (449 T238 round 2: `Occasion: bogus: x` answered, as a section
    // did); its form is never refused, but a later commit can carry a line that answers
    let tweak = sources
        .iter()
        .filter(|(s, _)| s == TWEAK)
        .flat_map(|(_, l)| l.iter().flatten())
        .filter(|(kind, arg)| {
            DECLARED.iter().any(|(k, _)| k == kind)
                && nothing_named(kind, arg).is_none()
                && pool.unknown(kind, arg, TWEAK).is_none()
        })
        .cloned()
        .collect();
    Forms {
        answered,
        tweak,
        why,
        task,
        misformed,
    }
}

/// Whether a well-formed commit line still answers once the drawings are current (449 T238 round 2, the plan review's D9c): a glyph line
/// naming an element its map's CURRENT drawing does not hold answers nothing (it owes no unit, so the code it answered for would ship
/// unreviewed); any other line - and one whose map is not current (D9r) - answers as at `--check-declared`.
fn answers_drawn(tree: &Tree, kind: &str, arg: &str) -> bool {
    if !matches!(kind, "glyph-redrawn" | "placement-changed") {
        return true;
    }
    let subject = arg.split(" - ").next().unwrap_or("").trim();
    let (element, at) = subject.split_once(" on ").unwrap_or((subject, ""));
    undrawn(tree, kind, arg, TWEAK, element.trim(), at.trim()).is_none()
}

/// The units the active features (and the delta's commit messages) declare, and the problems.
#[must_use]
pub fn declared(tree: &Tree, base: &str) -> Declared {
    let mut shown = Shown {
        root: tree.root,
        base,
        seen: BTreeMap::new(),
    };
    let features = active_features(tree.root, base, &mut shown);
    let sources = sources(tree.root, base, &features, &mut shown);
    let mut pool = Pool {
        root: tree.root,
        names: Some(
            tree.folders
                .iter()
                .filter(|f| f.drawn())
                .map(|f| f.name.clone())
                .collect::<BTreeSet<String>>()
                .into_iter()
                .collect(),
        ),
    };
    let mut out = Declared {
        units: Vec::new(),
        problems: Vec::new(),
        undrawn: Vec::new(),
    };
    for (source, lines) in sources {
        let Some(lines) = lines else { continue };
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
            if let Some(what) = nothing_named(&kind, &arg) {
                out.problems.push(format!(
                    "`{}` ({source}) names no {what} - write it {}",
                    written(&kind, &arg),
                    form(&kind)
                ));
                continue;
            }
            if let Some(why) = pool.unknown(&kind, &arg, &source) {
                out.problems.push(why);
                continue;
            }
            declared_units(tree, &source, &kind, &arg, checks, &mut out);
        }
    }
    out
}

/// The refusal when a declared glyph line names an element its map's CURRENT drawing does not hold (449 T238 round 2, the plan review's
/// D9: it became a unit on no map, which nobody can run), else None. The review gate asks it after it redraws the maps not current,
/// where it asks what is owed: `--check-declared` runs before the redraw and so cannot tell a stale drawing from a wrong name.
#[must_use]
///
/// And (D9c) a delta whose placement code only commit `Occasion:` lines answered, each naming an element its map's current drawing does
/// not hold, is refused as undeclared: such a line owes no unit, so the code would ship unreviewed (before D9 the unit on no map held the
/// landing). The line itself is never refused, a commit message not being rewritable.
pub fn check_drawn(root: &Path) -> Option<String> {
    let (base, _) = super::base_of(root);
    let tree = Tree::read(root);
    let d = declared(&tree, &base);
    let mut out: Vec<String> = Vec::new();
    if !d.undrawn.is_empty() {
        out.push(format!(
            "a declaration names an element its map's drawing does not hold, owing a review nobody can run: {}",
            d.undrawn.join("; ")
        ));
    }
    let forms = forms(root, &base);
    if !forms.answered
        && !forms.tweak.is_empty()
        && !forms
            .tweak
            .iter()
            .any(|(kind, arg)| answers_drawn(&tree, kind, arg))
    {
        let code = super::touched_code(root, &base);
        if !code.is_empty() {
            out.push(super::undeclared(
                &code,
                &format!(
                    "the delta's `Occasion:` commit lines name only elements their maps' current drawings do not hold, so none \
                     answers it; {}",
                    forms.why
                ),
                &forms.task,
            ));
        }
    }
    (!out.is_empty()).then(|| out.join("\n"))
}
