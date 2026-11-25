//! The research backlog (feature 451 T236; the GM 2026-11-25, request.md "a research backlog": *"have some kind of research backlog.
//! Where we make a best guess about what to render, and then note it as being something that is unresearched"*): every decision
//! recorded UNRESEARCHED - not yet searched, a guess drawn meanwhile - as a claim of the code (`<label> - UNRESEARCHED[ <file>#<id>]`)
//! or an item tagged on a page (`data-label="UNRESEARCHED"`), listed by the code file it belongs to, so a port stage's end works the
//! items that stage touched. A page item belongs to the files of the claims that name it; one no claim names is listed under its page.
//! `make claims-report`'s UNRESEARCHED list is this list's claims, unscoped.

use std::collections::BTreeMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::flight;
use super::index;
use super::item_labels::every_tag;
use super::units::{rel, rglob, walked};
use crate::record::args::{parse, Spec};
use crate::Reply;

/// The work budget, whose stages a `STAGE=` names.
const BUDGET: &str = "dev/work-budget.json";
/// The label the backlog lists.
const LABEL: &str = "UNRESEARCHED";
/// A stage's function, which marks the crate holding the stages.
static STAGE_FN: LazyLock<Regex> =
    LazyLock::new(|| crate::record::units::re(r"\bfn stage_[a-z_]+\b"));

/// What `STAGE=` narrows the backlog to: a stage's own module and the stage crate's shared files (its driver), or a path glob over
/// the code files and pages.
pub enum Scope {
    All,
    Stage {
        name: String,
        own: Vec<String>,
        shared: Vec<String>,
    },
    Glob(String),
}

impl Scope {
    /// Whether a code file or a page is in scope.
    #[must_use]
    pub fn holds(&self, path: &str) -> bool {
        match self {
            Self::All => true,
            Self::Stage { own, shared, .. } => own.iter().chain(shared).any(|f| f == path),
            Self::Glob(g) => glob(g).is_match(path).unwrap_or(false),
        }
    }

    /// The heading a code file's entries stand under: a shared file says so.
    fn heading(&self, path: &str) -> String {
        match self {
            Self::Stage { shared, .. } if shared.iter().any(|f| f == path) => {
                format!("{path} (shared: no stage's own module - its stage's entries among them)")
            }
            _ => path.to_owned(),
        }
    }

    fn named(&self) -> String {
        match self {
            Self::All => String::new(),
            Self::Stage { name, .. } => format!(" in stage {name}"),
            Self::Glob(g) => format!(" in {g}"),
        }
    }
}

/// A path glob as a pattern: `**` any path, `*` and `?` within one component.
fn glob(g: &str) -> Regex {
    let mut out = String::from("^");
    let mut chars = g.chars().peekable();
    while let Some(c) = chars.next() {
        match c {
            '*' if chars.peek() == Some(&'*') => {
                chars.next();
                out.push_str(".*");
            }
            '*' => out.push_str("[^/]*"),
            '?' => out.push_str("[^/]"),
            c => out.push_str(&fancy_regex::escape(&c.to_string())),
        }
    }
    out.push('$');
    crate::record::units::re(&out)
}

/// The backlog's text: its head line, then each code file (or page no claim names) with its claims and items.
fn render(root: &Path, cur: &index::Cur, scope: &Scope) -> String {
    let mut groups: BTreeMap<String, Vec<String>> = BTreeMap::new();
    let mut claims = 0;
    // (page, id) -> the files of the claims naming it
    let mut named: BTreeMap<(String, String), Vec<String>> = BTreeMap::new();
    for r in cur.iter() {
        for item in &r.claim.items {
            named
                .entry(item.clone())
                .or_default()
                .push(r.unit.path.clone());
        }
        if r.claim.backing == LABEL && scope.holds(&r.unit.path) {
            claims += 1;
            groups
                .entry(scope.heading(&r.unit.path))
                .or_default()
                .push(format!("  claim  {} - {}", r.key, r.claim.account));
        }
    }
    let mut items = 0;
    for (page, it) in every_tag(root)
        .into_iter()
        .filter(|(_, i)| i.label == LABEL)
    {
        let shown = if it.guess.trim().is_empty() {
            &it.block
        } else {
            &it.guess
        };
        let line = format!("  item   {page}#{} - {shown}", it.id);
        let mut files = named
            .get(&(page.clone(), it.id.clone()))
            .cloned()
            .unwrap_or_default();
        files.sort();
        files.dedup();
        let mut homes: Vec<String> = files
            .iter()
            .filter(|f| scope.holds(f))
            .map(|f| scope.heading(f))
            .collect();
        // an item no claim names, or one whose page alone a glob holds, is listed under its page
        if homes.is_empty() && scope.holds(&page) {
            homes.push(if files.is_empty() {
                format!("{page} (no claim names the item)")
            } else {
                page.clone()
            });
        }
        if !homes.is_empty() {
            items += 1;
        }
        for h in homes {
            groups.entry(h).or_default().push(line.clone());
        }
    }
    let mut lines = vec![format!(
        "research-backlog: {claims} UNRESEARCHED claim(s), {items} UNRESEARCHED page item(s){} - not yet searched, a guess drawn meanwhile: work a stage's own at its end (feature 451 T236; make research-backlog STAGE=<stage or path glob>)",
        scope.named()
    )];
    for (home, entries) in groups {
        lines.push(home);
        lines.extend(entries);
    }
    lines.join("\n") + "\n"
}

/// The work budget's stages, read from `dev/work-budget.json`; none where it does not read.
fn stages(root: &Path) -> Vec<String> {
    std::fs::read_to_string(root.join(BUDGET))
        .ok()
        .and_then(|t| serde_json::from_str::<serde_json::Value>(&t).ok())
        .and_then(|v| {
            v.get("stages")?
                .as_object()
                .map(|m| m.keys().cloned().collect())
        })
        .unwrap_or_default()
}

/// The Rust files the claims walk reads, relative to `root`, with their text.
fn sources(root: &Path) -> Vec<(String, String)> {
    let base = root.join("rust");
    let mut out: Vec<(String, String)> = rglob(&base, ".rs")
        .iter()
        .filter(|p| walked(&rel(p, &base)))
        .map(|p| (rel(p, root), std::fs::read_to_string(p).unwrap_or_default()))
        .collect();
    out.sort();
    out
}

/// A file's crate: its path up to `/src/`.
fn crate_of(path: &str) -> &str {
    path.find("/src/").map_or(path, |i| &path[..i])
}

/// Whether a file is in a stage's own module: `<stage>.rs` or a file under `<stage>/`, a form's stage (`field.polder`) its stage's.
fn in_module(path: &str, stage: &str) -> bool {
    let stage = stage.split_once('.').map_or(stage, |(s, _)| s);
    let parts: Vec<&str> = path.split('/').collect();
    parts[..parts.len() - 1].contains(&stage)
        || parts.last() == Some(&format!("{stage}.rs").as_str())
}

/// A stage's scope: its own module in the crates that define a `stage_<name>` function (the stages' crates; never `rust/mode_a`'s
/// `labels/`, measured 2026-11-25: the stage `labels` matched eight Mode A files), and every file of those crates no stage's module
/// holds - the driver, which defines every `stage_<name>` and draws for several (`driver.rs::draw_field`), so a stage's end sees the
/// shared code it touched. Not the work budget's `stage_files`, which names the driver alone (`seat`'s was `rust/phases/src/driver.rs`,
/// its `seat/fords.rs` left out).
fn stage_scope(root: &Path, stage: &str, stages: &[String]) -> Scope {
    let files = sources(root);
    let crates: Vec<&str> = files
        .iter()
        .filter(|(_, text)| STAGE_FN.is_match(text).unwrap_or(false))
        .map(|(p, _)| crate_of(p))
        .collect();
    let ours: Vec<&String> = files
        .iter()
        .map(|(p, _)| p)
        .filter(|p| crates.contains(&crate_of(p)))
        .collect();
    let own = ours
        .iter()
        .filter(|p| in_module(p, stage))
        .map(|p| (*p).clone())
        .collect();
    let shared = ours
        .iter()
        .filter(|p| !stages.iter().any(|s| in_module(p, s)))
        .map(|p| (*p).clone())
        .collect();
    Scope::Stage {
        name: stage.to_owned(),
        own,
        shared,
    }
}

/// `l7r-gate research-backlog --root <root> [--stage <stage or path glob>]`.
#[must_use]
pub fn backlog_cli(args: &[String]) -> Reply {
    let reply = |stdout: String, stderr: String, code: i32| Reply {
        stdout,
        stderr,
        code,
    };
    let p = match parse(args, &[Spec::value("--root"), Spec::value("--stage")]) {
        Ok(p) => p,
        Err(why) => return super::usage("l7r-gate research-backlog", &why),
    };
    let root = flight::resolved(Path::new(p.text("--root", ".")));
    let scope = match p.text("--stage", "") {
        "" => Scope::All,
        s => {
            let known = stages(&root);
            if known.iter().any(|n| n == s) {
                stage_scope(&root, s, &known)
            } else if s.contains(['/', '*', '?']) {
                Scope::Glob(s.to_owned())
            } else {
                return reply(String::new(), format!("research-backlog: STAGE={s} names no stage of dev/work-budget.json's and is no path glob: give a stage (`STAGE=seat`) or a path glob (`STAGE='rust/phases/src/seat*'`)\n"), 2);
            }
        }
    };
    match index::current(&root, &root.join(index::QUESTIONS)) {
        Ok(cur) => reply(render(&root, &cur, &scope), String::new(), 0),
        Err(why) => reply(
            String::new(),
            format!("research-backlog: the claims could not be read\n{why}\n"),
            1,
        ),
    }
}

#[cfg(test)]
mod tests;
