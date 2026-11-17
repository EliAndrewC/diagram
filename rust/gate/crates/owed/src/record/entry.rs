//! Which feature classes' modal prose may have gone stale (`scripts/record/entry_owed.py`, feature 234; ported by feature 449 T149 under
//! `ask:449-phase4-slices` Q5, with the registry it reads): a class is named when a research question its `Entry:` names had its findings
//! changed in this delta AND the class's own explanation prose did not.
//!
//! WHY IT EXISTS (the GM, 2026-09-12, told to update the pigsty write-up): *"if I hadn't said that ... then would you have done it?"* It
//! would not have been: the prose and the record agreed with themselves, separately. The push refuses until each named pair is answered
//! (`scripts/gates/entry-gate.sh`, through `record record-owed`'s entry-drift family) - an unenforced doctrine is no doctrine (the GM).
//!
//! THE PROSE HALF IS DERIVED, NEVER RESTATED: the explanation prose is every tag the registry does not class as data
//! (`l7r_gate_registry::about::TAGS` less `DATA_TAGS`), so re-pointing an `Entry:` cannot silence the check while the words stand.
//! WHAT MOVED is a question page's findings - its heading and the words of every block but its intro (feature 311, spec FR-004), read by
//! the one reader of them (`pages::read_page`); a page renumbered by `make fragment-move` is compared with the one it was.
//!
//! Since feature 319 every kind is About-form and owes the modal checks instead (`modals.rs`), which `record-owed` applies by leaving out
//! every key this names that is an About-form modal - so in a tree whose registry loads, this names nothing that reaches the push. The
//! port keeps it whole, its command line (`record entry-owed`) and its words the Python's, for the differential and for a kind written in
//! the old form again.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_registry::about::{
    classes, compound_classes, get, modal_rel, parse_explanation, FeatureClass, DATA_TAGS, TAGS,
};
use l7r_gate_registry::kinds::{Registry, HAMLET_REGISTRY, SHEET_REGISTRY};
use l7r_guard::shared::checks::pages::read_page;

use super::leaves::fragments_for;
use super::modals::{read_at, MODAL_DIRS};
use super::repo::{cat_blobs, git, git_show, read_universal, Fail};
use super::units::re;
use crate::Reply;

const RESEARCH: &str = "research";

/// A question's page, relative to the record (feature 303): `questions/NNNN-<slug>[.drawing].html`.
static QUESTION: LazyLock<Regex> =
    LazyLock::new(|| re(r"^questions/(\d{4}-([^.]+)(\.drawing)?\.html)$"));
static NUMBERED: LazyLock<Regex> = LazyLock::new(|| re(r"^\d{4}-[^.]+(\.drawing)?\.html$"));

/// (ref, description): the merge base of HEAD with origin/main, else HEAD (`base_of`).
#[must_use]
pub fn base_of(root: &Path) -> (String, String) {
    let head = git(root, &["rev-parse", "--verify", "-q", "HEAD"])
        .trim()
        .to_owned();
    if head.is_empty() {
        return (String::new(), "no commits yet".to_owned());
    }
    if !git(root, &["rev-parse", "--verify", "-q", "origin/main"])
        .trim()
        .is_empty()
    {
        let mb = git(root, &["merge-base", "HEAD", "origin/main"])
            .trim()
            .to_owned();
        if !mb.is_empty() {
            let short: String = mb.chars().take(8).collect();
            return (mb, format!("origin/main (merge base {short})"));
        }
    }
    let short: String = head.chars().take(8).collect();
    (head.clone(), format!("HEAD ({short}; no origin/main)"))
}

/// What a modal is written FROM: the page's heading and the words of every block but its intro.
fn findings(page: &str) -> Vec<String> {
    let p = read_page(page);
    std::iter::once(p.heading)
        .chain(p.blocks.into_iter().filter(|b| !b.intro).map(|b| b.words))
        .collect()
}

/// The body a question's page had at `base` under another number in `questions/` (`make fragment-move`).
fn renamed_from(root: &Path, base: &str, rel: &str, slug: &str, drawing: &str) -> Option<String> {
    let dir = rel.rsplit_once('/').map_or("", |p| p.0);
    let listing = git(root, &["ls-tree", "--name-only", &format!("{base}:{dir}")]);
    let tail = format!("-{slug}{drawing}.html");
    let was: Vec<&str> = l7r_guard::shared::py_text::split(&listing)
        .into_iter()
        .filter(|n| n.ends_with(&tail) && NUMBERED.is_match(n).unwrap_or(false))
        .collect();
    match was.as_slice() {
        [one] => git_show(root, base, &format!("{dir}/{one}")),
        _ => None,
    }
}

/// The file name of every question page whose findings changed against `base` (feature 303); a page with no older file is new.
fn moved_anchors(root: &Path, base: &str) -> Result<BTreeSet<String>, Fail> {
    let listed = git(
        root,
        &["diff", "--name-only", base, "--", &format!("{RESEARCH}/")],
    );
    let names: Vec<&str> = l7r_guard::shared::py_text::split(&listed);
    let olds = cat_blobs(
        root,
        &names
            .iter()
            .map(|n| format!("{base}:{n}"))
            .collect::<Vec<_>>(),
    );
    let mut moved = BTreeSet::new();
    for (rel, old) in names.iter().zip(olds) {
        let inside = rel.strip_prefix(&format!("{RESEARCH}/")).unwrap_or(rel);
        let Ok(Some(m)) = QUESTION.captures(inside) else {
            continue;
        };
        let Some(new) = read_universal(&root.join(rel))? else {
            continue;
        };
        let old = if old.is_empty() {
            let drawing = m.get(3).map_or("", |g| g.as_str());
            let Some(text) = renamed_from(root, base, rel, &m[2], drawing) else {
                continue;
            };
            text
        } else {
            old
        };
        if findings(&old) != findings(&new) {
            moved.insert(m[1].to_owned());
        }
    }
    Ok(moved)
}

/// A modal's explanation prose: every tag the registry does not class as data, joined; None where the text does not parse.
fn prose_of(text: &str, class: &str) -> Option<String> {
    let parts = parse_explanation(Some(text), class).ok()?;
    let prose: Vec<&str> = TAGS
        .iter()
        .filter(|t| !DATA_TAGS.contains(t))
        .map(|t| get(&parts, t))
        .collect();
    Some(prose.join("\u{241f}"))
}

/// key -> explanation prose of every kind of `registry` whose file `read` gives; `at` collects key -> that file.
fn prose_by_key(
    registry: &Registry,
    read: &mut dyn FnMut(&str) -> Result<Option<String>, Fail>,
    mut at: Option<&mut HashMap<String, String>>,
) -> Result<HashMap<String, String>, Fail> {
    let mut out = HashMap::new();
    for (_, kind) in registry.kinds() {
        let file = modal_rel(registry, kind.key);
        let Some(text) = read(&file)? else {
            continue;
        };
        if let Some(prose) = prose_of(&text, kind.class) {
            out.insert(kind.key.to_owned(), prose);
            if let Some(at) = at.as_deref_mut() {
                at.insert(kind.key.to_owned(), file);
            }
        }
    }
    Ok(out)
}

/// The fragments an `entry-drift` dispatch should read for the moved pages `hit`, named in the line that dispatches it (feature 258).
/// Each page's listing is asked once a run (`known`), as the Python's `fragments_batch` asked every hit of a run once: a page many kinds
/// name would otherwise be listed again for each.
fn fragments_line(hit: &[&String], cwd: &Path, known: &mut HashMap<String, Vec<String>>) -> String {
    let mut out: Vec<String> = Vec::new();
    for file in hit {
        let listed = known
            .entry((*file).clone())
            .or_insert_with(|| fragments_for(file, cwd));
        for f in listed.iter() {
            if !f.ends_with(".notes.html") && !f.ends_with(".originals.html") && !out.contains(f) {
                out.push(f.clone());
            }
        }
    }
    if out.is_empty() {
        String::new()
    } else {
        format!("\n      read: {}", out.join(", "))
    }
}

/// THE DECISION: a class is named when a page its entry names moved and its own prose did not; a class new in this delta is never named.
fn named_pairs(
    moved: &BTreeSet<String>,
    anchors: &BTreeMap<String, BTreeSet<String>>,
    now: &HashMap<String, String>,
    was: &HashMap<String, String>,
    at: &HashMap<String, String>,
    cwd: &Path,
    known: &mut HashMap<String, Vec<String>>,
) -> Vec<String> {
    let mut out = Vec::new();
    for (key, named) in anchors {
        let hit: Vec<&String> = named.intersection(moved).collect();
        if !hit.is_empty() && was.get(key).is_some_and(|w| Some(w) == now.get(key)) {
            let names: Vec<&str> = hit.iter().map(|h| h.as_str()).collect();
            out.push(format!(
                "{key} - {} - prose at {}{}",
                names.join(" "),
                at.get(key).map_or(MODAL_DIRS[0], String::as_str),
                fragments_line(&hit, cwd, known)
            ));
        }
    }
    out
}

/// (the base's description, one `key - what moved - where the prose lives` line per named class).
///
/// # Errors
/// A registry that does not load (the Python's import error), or a file that cannot be read.
pub fn owed(root: &Path) -> Result<(String, Vec<String>), Fail> {
    owed_from(
        root,
        &std::env::current_dir().unwrap_or_default(),
        &registries,
    )
}

/// The two registries, each with its kinds (`CLASSES` and `COMPOUND_CLASSES`): a kind refused or with no file fails the report, as the
/// Python's import failed it.
type Loaded = Vec<(Registry, Vec<FeatureClass>)>;

fn registries(root: &Path) -> Result<Loaded, Fail> {
    let loaded = |r: l7r_gate_research::Result<Vec<FeatureClass>>| {
        r.map_err(|e| format!("{}: {}", e.kind, e.message))
    };
    Ok(vec![
        (HAMLET_REGISTRY, loaded(classes(root))?),
        (SHEET_REGISTRY, loaded(compound_classes(root))?),
    ])
}

/// [`owed`], the fragments a named line lists found under `cwd`, as the Python found them under its working directory, and the
/// registries `load` gives (a test gives a few kinds where the whole registry would cost its fixture every file, FR-008).
fn owed_from(
    root: &Path,
    cwd: &Path,
    load: &dyn Fn(&Path) -> Result<Loaded, Fail>,
) -> Result<(String, Vec<String>), Fail> {
    let (base, desc) = base_of(root);
    if base.is_empty() {
        return Ok((desc, Vec::new()));
    }
    let moved = moved_anchors(root, &base)?;
    if moved.is_empty() {
        return Ok((desc, Vec::new()));
    }
    let registries = load(root)?;
    let mut then = read_at(root, &base);
    let mut known = HashMap::new();
    let mut pairs = Vec::new();
    // each registry against its own files: a compound's `well` and a hamlet's `well` are two modals under one key (feature 268)
    for (registry, defs) in &registries {
        let mut at = HashMap::new();
        let now = prose_by_key(
            registry,
            &mut |f| read_universal(&root.join(f)),
            Some(&mut at),
        )?;
        let was = prose_by_key(registry, &mut |f| Ok(then.read(f)), None)?;
        let anchors: BTreeMap<String, BTreeSet<String>> = defs
            .iter()
            .map(|fc| {
                (
                    fc.key.clone(),
                    l7r_gate_research::sources::entry_fragments(&fc.entry)
                        .into_iter()
                        .collect(),
                )
            })
            .collect();
        pairs.extend(named_pairs(
            &moved, &anchors, &now, &was, &at, cwd, &mut known,
        ));
    }
    Ok((desc, pairs))
}

/// The one-line ruling `--why` prints.
fn ruling(desc: &str, lines: &[String]) -> String {
    if lines.is_empty() {
        return format!("no modal's research section moved against {desc}");
    }
    format!("research moved under {} unchanged modal(s) against {desc} - dispatch `entry-drift` at each, then rewrite the prose or record why not in dev/bypass-log/", lines.len())
}

/// `record entry-owed [--root DIR] [--why]` (`entry_owed.py`'s own command line): one line per named class, or with `--why` the ruling;
/// exit 0 either way, 1 where DIR is not a git repository.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let reply = |stdout: String, stderr: String, code: i32| Reply {
        stdout,
        stderr,
        code,
    };
    let (mut root, mut why) = (".".to_owned(), false);
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--why" => why = true,
            "--root" => match it.next() {
                Some(r) => r.clone_into(&mut root),
                None => return reply(
                    String::new(),
                    "usage: l7r-gate record entry-owed: argument --root: expected one argument\n"
                        .to_owned(),
                    2,
                ),
            },
            other => match other.strip_prefix("--root=") {
                Some(r) => r.clone_into(&mut root),
                None => {
                    return reply(
                        String::new(),
                        format!(
                            "usage: l7r-gate record entry-owed: unrecognized arguments: {other}\n"
                        ),
                        2,
                    )
                }
            },
        }
    }
    let top = git(Path::new(&root), &["rev-parse", "--show-toplevel"])
        .trim()
        .to_owned();
    if top.is_empty() {
        return reply(
            String::new(),
            format!("_entry_owed: {root} is not a git repository\n"),
            1,
        );
    }
    match owed(Path::new(&top)) {
        Ok((desc, lines)) => {
            let body = if why {
                ruling(&desc, &lines)
            } else {
                lines.join("\n")
            };
            let end = if why || !lines.is_empty() { "\n" } else { "" };
            reply(body + end, String::new(), 0)
        }
        Err(e) => reply(String::new(), e + "\n", 1),
    }
}

#[cfg(test)]
mod tests;
