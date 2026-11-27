//! A TASK LANDS WITH THE FILES IT NAMES (feature 451 T294). WHY: on 2026-11-26 451 T270 landed WITHOUT ITS CODE (0526d8b7df,
//! repaired by 83f65718d7): the cherry-pick that would have carried it stood unfinished, and the landing pushed a HEAD that lacked
//! `rust/gate/crates/measure/src/measure/audit/held.rs`, the new module its plan section named. 451 T292 refuses an unfinished carry
//! ([`super::unfinished`]); this is the cheap true check under it - a carry never begun, or begun and backed out, lands nothing.
//!
//! So the first pass refuses a landing task whose own words name a file the landing tree's HEAD does not hold (one `git ls-tree` a
//! landing), naming each file and the carry to look for. The words read, and why only these:
//! - its OWN line of the `## Occasions` section (`- none: T<n> - ...`, a bundle's `- none: T<a>, T<b> - ...`, a declaration's tag
//!   after its subject, `- <kind>: <subject> - T<n>: ...`; a wrapped continuation joined on): every backquoted path under `rust/`,
//!   `scripts/` or `tests/`, and every backquoted `.rs`, `.sh`, `.py` or `.toml` name. A line lists the files a task touched, never
//!   one it read; a short name (`audit/held.rs`, `tests/idle.rs`) is held where any file under those three ends with it by whole
//!   components, so a line's relative names never refuse falsely.
//! - its plan sections (`### T<n> ...`, a bundle's `### T<a>, T<b> ...`) only where they name a path AS NEW: "`<path>`, new" or
//!   "(`<path>` (new", or "a new module|file|test|suite|crate|script|guard|binary `<path>`" (`::item` dropped). A section also names the
//!   files it read, deleted or moved and other tasks' files, so a path it names otherwise is not read: measured 2026-11-27 (a replay of
//!   every `make land` tick commit since 2026-11-20, each task's line and sections from the commit's parent, against the parent's
//!   tree - `dev/measurements/2026-11-27/landing-named-files/replay.py`): 486 task landings, 115 with a line naming 224 paths, 9 with
//!   a section naming 9 paths as new, and ONE refusal - T270's, its section's `audit/held.rs`; its Occasions line was in the unfinished
//!   pick, not in HEAD, so the line alone would not have refused it. Today's 451 plan-done.md, by the same reading over every path:
//!   53 of 862 paths no section marks new are absent from HEAD (deleted or moved since), which a whole-section rule would refuse.
//!
//! A false refusal - a line that misnames a file - is answered by restating the line; there is no escape, the check being true where
//! the line is (constitution XIV: a claim the code does not match is restated, not the code).

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::speckit::splitlines;

use super::Land;

/// The trees a full path names.
const TREES: [&str; 3] = ["rust/", "scripts/", "tests/"];
/// A path a line or section names: under one of `TREES`, an item after `::` left off.
const PATH: &str = r"`((?:rust|scripts|tests)/[^`\s*<>{}]+?)(?:::[^`]*)?`";

static SECTION: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?ms)^## Occasions\s*$(?P<body>.*?)(?=^## |\z)"));
static LINE: LazyLock<Regex> = LazyLock::new(|| re(r"^- [a-z-]+:\s*(?P<arg>.*)$"));
static TOKEN: LazyLock<Regex> = LazyLock::new(|| re(r"`([^`\s*<>{}$=]+)`"));
static SOURCE: LazyLock<Regex> = LazyLock::new(|| re(r"\.(?:rs|sh|py|toml)$"));
static NEW: LazyLock<[Regex; 2]> = LazyLock::new(|| {
    [
        re(&format!(r"{PATH},? \(?new\b")),
        re(&format!(
            r"\b[Nn]ew (?:module|file|test file|test|suite|crate|script|guard|binary)s?,? (?:\w+ )?{PATH}"
        )),
    ]
});

fn re(pattern: &str) -> Regex {
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// The files of a tree, and every directory above them.
pub(super) struct Held {
    files: BTreeSet<String>,
    dirs: BTreeSet<String>,
}

impl Held {
    /// From `git ls-tree -r --name-only -z`'s output.
    pub(super) fn of(listing: &str) -> Self {
        let files: BTreeSet<String> = listing
            .split('\0')
            .filter(|f| !f.is_empty())
            .map(str::to_owned)
            .collect();
        let dirs = files
            .iter()
            .flat_map(|f| f.match_indices('/').map(|(i, _)| f[..i].to_owned()))
            .collect();
        Self { files, dirs }
    }

    /// Whether `named` is a file or directory of the tree, or the end, by whole components, of a file under one of `TREES`.
    fn holds(&self, named: &str) -> bool {
        let named = named.trim_end_matches('/');
        let tail = format!("/{named}");
        self.files.contains(named)
            || self.dirs.contains(named)
            || self
                .files
                .iter()
                .any(|f| TREES.iter().any(|t| f.starts_with(t)) && f.ends_with(&tail))
    }
}

/// Whether `text` opens with a list of task ids holding `task` (`T299, T282 - ...`).
fn leads_with(text: &str, task: &str) -> bool {
    text.split_whitespace()
        .map(|w| w.trim_end_matches([',', ':', ';', '.']))
        .take_while(|w| {
            w.len() > 1 && w.starts_with('T') && w[1..].chars().all(|c| c.is_ascii_digit())
        })
        .any(|w| w == task)
}

/// `task`'s own lines of a tasks.md's `## Occasions`, each with its wrapped continuation joined on.
fn own_lines(tasks_md: &str, task: &str) -> Vec<String> {
    let Some(c) = SECTION.captures(tasks_md).ok().flatten() else {
        return Vec::new();
    };
    let mut lines: Vec<String> = Vec::new();
    let mut open = false;
    for line in splitlines(c.name("body").map_or("", |m| m.as_str())) {
        if line.starts_with("- ") {
            lines.push(line.to_owned());
            open = true;
        } else if open && line.starts_with([' ', '\t']) && !line.trim().is_empty() {
            if let Some(last) = lines.last_mut() {
                last.push(' ');
                last.push_str(line.trim());
            }
        } else {
            open = false;
        }
    }
    lines
        .into_iter()
        .filter(|l| {
            let arg = LINE
                .captures(l)
                .ok()
                .flatten()
                .map_or(String::new(), |c| c["arg"].to_owned());
            leads_with(&arg, task)
                || arg
                    .split_once(" - ")
                    .is_some_and(|(_, tag)| leads_with(tag, task))
        })
        .collect()
}

/// `task`'s own sections of a plan.md: each `### ` heading whose ids hold it, to the next `### ` heading.
fn own_sections(plan_md: &str, task: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    let mut ours = false;
    for line in splitlines(plan_md) {
        if let Some(heading) = line.strip_prefix("### ") {
            ours = leads_with(heading, task);
            if ours {
                out.push(String::new());
            }
        }
        if let Some(section) = out.last_mut().filter(|_| ours) {
            section.push_str(line);
            section.push('\n');
        }
    }
    out
}

/// The files `task`'s own words name that `held` does not hold, in order, each once: its Occasions line's, then its sections' new ones.
pub(super) fn missing(tasks_md: &str, plan_md: &str, task: &str, held: &Held) -> Vec<String> {
    let lined = own_lines(tasks_md, task).into_iter().flat_map(|l| {
        TOKEN
            .captures_iter(&l)
            .map_while(Result::ok)
            .map(|c| c[1].trim_end_matches([':', ',', ';', '.']).to_owned())
            .filter(|t| {
                TREES.iter().any(|p| t.starts_with(p)) || SOURCE.is_match(t).unwrap_or(false)
            })
            .collect::<Vec<_>>()
    });
    let sections = own_sections(plan_md, task);
    let new = NEW.iter().flat_map(|r| {
        sections.iter().flat_map(|s| {
            r.captures_iter(s)
                .map_while(Result::ok)
                .map(|c| c[1].to_owned())
                .collect::<Vec<_>>()
        })
    });
    let mut out: Vec<String> = Vec::new();
    for named in lined.chain(new) {
        if !held.holds(&named) && !out.contains(&named) {
            out.push(named);
        }
    }
    out
}

/// The refusal's words for `files` missing, '' where none.
pub(super) fn refusal(files: &[String]) -> String {
    if files.is_empty() {
        return String::new();
    }
    let shown: Vec<String> = files.iter().map(|f| format!("`{f}`")).collect();
    format!(
        "its Occasions line or plan section names {} that the landing tree's HEAD does not hold - its code is not carried \
         (451 T270 landed so): `make builder-trees` lists each done commit not carried with its `make carry`; a line that \
         misnames a file is restated",
        shown.join(", ")
    )
}

impl Land {
    /// The landing tree's HEAD, read once a landing.
    pub(super) fn held(&self) -> Result<Held, String> {
        let (rc, out) =
            super::unfinished::git(&self.root, &["ls-tree", "-r", "--name-only", "-z", "HEAD"])?;
        if rc != 0 {
            return Err(format!("git ls-tree HEAD: {out}"));
        }
        Ok(Held::of(&out))
    }
}

/// Why `task` of the feature `d` may not land for a file it names that HEAD lacks; '' where it may.
pub(super) fn refused(d: &Path, tasks_md: &str, task: &str, held: &Held) -> String {
    let plan = std::fs::read_to_string(d.join("plan.md")).unwrap_or_default();
    refusal(&missing(tasks_md, &plan, task, held))
}

#[cfg(test)]
mod tests;
