//! `make tool-yield` - every tool of the project, how often it is used and how often it changes the outcome (feature 406 T04; feature
//! 449 T120, from `tool_yield.py`, under `ask:449-T83-scope`).
//!
//! WHY (the GM 2026-10-19): "Whether or not it's doing something for us should be a measurable question", for "basically ... every
//! tool" - "how often a tool is used ... Or how often it makes a difference" - and where a tool is "too new to have gathered
//! measurements, then that's fine".
//!
//! THE TOOLS are listed from the code (D163), never from what has fired, so a tool that never fired reads 0: the inventory
//! (`core`'s `measure::tool_inventory`, which `l7r-gate check tool-signals` reads too), the Makefile's targets, the `.claude/agents/`
//! types and the registry's steps. THE RECORDS (`tool_yield/records.rs`): the guard log, every clone's event logs and usage log, the
//! review ledger, the round arbiter's rulings and the bypass log. Wherever the Python raised (a broken settings file, Makefile or
//! registry, a bypass record that is no object) the command fails too, exit 1.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use l7r_gate_core::measure::tool_inventory::{
    check_paths, ending, hook_guards, read_lossy, read_text, recipe, registry, targets,
};
use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_guard::shared::log::civil;
use serde_json::Value;

use super::events::{py_str, re, Raised};
use super::reply;
use crate::Reply;

pub mod records;

/// The spec's "too new": first seen under 7 days ago (FR-001).
const TOO_NEW_DAYS: f64 = 7.0;
const DAY: f64 = 86_400.0;
const UNSEEN: [&str; 2] = [
    "the outcome of a target run no session made (a recipe, a script, the timer) - its run is counted, its outcome is not",
    "an automatic step written later that calls neither the helper nor guard_log - FR-004's check reads files, not steps",
];
const KINDS: [&str; 6] = ["", "guard", "check", "target", "review", "step"];

/// One tool's numbers.
#[derive(Clone, Debug, Default)]
pub struct Tally {
    pub kind: String,
    pub name: String,
    pub first: f64,
    pub uses: Vec<f64>,
    pub hits: usize,
    pub misses: usize,
    /// Target runs with no outcome record.
    pub unseen: usize,
    pub outcome_record: bool,
    hit_at: Vec<f64>,
    miss_at: Vec<f64>,
}

/// Every tool by (kind, name).
pub type Tools = BTreeMap<(String, String), Tally>;

impl Tally {
    #[must_use]
    pub fn new(kind: &str, name: &str) -> Self {
        Self {
            kind: kind.to_owned(),
            name: name.to_owned(),
            outcome_record: true,
            ..Self::default()
        }
    }

    /// A use at `t`: the first use the earliest, though a time of 0 (one `utc` could not read) starts it again, as the Python's
    /// `min(self.first, t) if self.first else t` did.
    pub fn use_at(&mut self, t: f64) {
        self.uses.push(t);
        self.first = if self.first == 0.0 {
            t
        } else {
            self.first.min(t)
        };
    }

    pub fn hit(&mut self, t: f64, yes: bool) {
        if yes {
            self.hits += 1;
            self.hit_at.push(t);
        }
    }

    pub fn miss(&mut self, t: f64, yes: bool) {
        if yes {
            self.misses += 1;
            self.miss_at.push(t);
        }
    }

    /// (uses, interventions, likely misfires) at or after `t`.
    #[must_use]
    pub fn since(&self, t: f64) -> (usize, usize, usize) {
        let n = |v: &[f64]| v.iter().filter(|u| **u >= t).count();
        (n(&self.uses), n(&self.hit_at), n(&self.miss_at))
    }
}

/// The tool `(kind, name)`, made where it is new (`t.setdefault`).
pub fn entry<'a>(t: &'a mut Tools, kind: &str, name: &str) -> &'a mut Tally {
    t.entry((kind.to_owned(), name.to_owned()))
        .or_insert_with(|| Tally::new(kind, name))
}

/// `{"hook": "guard"}.get(kind, kind)`.
fn guard_kind(kind: &str) -> &str {
    if kind == "hook" {
        "guard"
    } else {
        kind
    }
}

fn stem(p: &Path) -> String {
    p.file_stem()
        .map(|s| s.to_string_lossy().into_owned())
        .unwrap_or_default()
}

/// Every review's name: the `.claude/agents/*.md` stems.
fn reviews(root: &Path) -> BTreeSet<String> {
    ending(&root.join(".claude/agents"), ".md")
        .iter()
        .map(|p| stem(p))
        .collect()
}

/// The registry's `kind` of an entry, "step" where it names none: an entry that is no object is the Python's `AttributeError`.
fn registry_kind(entry: &Value) -> Result<String, Raised> {
    let Value::Object(m) = entry else {
        return Err("AttributeError: a registry entry is no object".to_owned());
    };
    Ok(m.get("kind").map_or_else(|| "step".to_owned(), py_str))
}

/// The tools a change's files belong to (feature 406 D165: a fix is read by its tools): a hook and the guards whose hook names a
/// changed helper, a refusing check, a review's agent file, a registered step by its file, a target whose recipe names a changed
/// script, and each Makefile target a hunk of `make_diff` (`git show -U0 -- Makefile`) changed.
///
/// # Errors
///
/// The inventory cannot be read: the Python's raise.
pub fn tools_of(
    root: &Path,
    files: &[String],
    make_diff: &str,
) -> Result<BTreeSet<(String, String)>, Raised> {
    let mut out: BTreeSet<(String, String)> = BTreeSet::new();
    let guards = hook_guards(root)?;
    let hook_text: Vec<(String, String)> = guards
        .iter()
        .filter_map(|g| {
            let p = root.join(format!("scripts/hooks/{g}-hooks.sh"));
            p.is_file().then(|| (g.clone(), read_lossy(&p)))
        })
        .collect();
    let check_rel: BTreeMap<String, String> = check_paths(root)?
        .iter()
        .map(|p| {
            (
                p.strip_prefix(root).unwrap_or(p).display().to_string(),
                stem(p),
            )
        })
        .collect();
    let make_path = root.join("Makefile");
    // the Python read "" for a missing Makefile and then raised in `targets`; reading it here raises the same
    let make = read_text(&make_path)?;
    let named: BTreeMap<String, String> = targets(root)?
        .into_iter()
        .map(|t| {
            let text = recipe(&make, &t);
            (t, text)
        })
        .collect();
    let reg = registry(root)?;
    let mut steps: Vec<(String, String, String)> = Vec::new();
    for (name, e) in &reg {
        let Value::Object(m) = e else {
            return Err("AttributeError: a registry entry is no object".to_owned());
        };
        let what = m.get("what").map_or_else(String::new, py_str);
        let path = what.split(' ').next().unwrap_or_default().to_owned();
        steps.push((name.clone(), path, registry_kind(e)?));
    }
    let hook_file = re(r"^scripts/hooks/([\w-]+)-hooks\.sh$");
    let agent_file = re(r"^\.claude/agents/([\w-]+)\.md$");
    for f in files {
        if let Some(c) = hook_file.captures(f).ok().flatten() {
            out.insert(("guard".to_owned(), c[1].to_owned()));
        } else if f.starts_with("scripts/") {
            // a helper a hook runs or imports: by its file name, or a lib module's stem
            let path = Path::new(f);
            let name = path
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default();
            let lib = f.starts_with("scripts/hooks/lib/");
            let word = re(&format!(r"\b{}\b", fancy_regex::escape(&stem(path))));
            for (g, text) in &hook_text {
                if text.contains(&name) || (lib && word.is_match(text).unwrap_or(false)) {
                    out.insert(("guard".to_owned(), g.clone()));
                }
            }
        }
        if let Some(c) = check_rel.get(f) {
            out.insert(("check".to_owned(), c.clone()));
        }
        if let Some(c) = agent_file.captures(f).ok().flatten() {
            out.insert(("review".to_owned(), c[1].to_owned()));
        }
        for (name, path, kind) in &steps {
            if path == f {
                out.insert((kind.clone(), name.clone()));
            }
        }
        if f.starts_with("scripts/") {
            for (t, text) in &named {
                if text.contains(f.as_str()) {
                    out.insert(("target".to_owned(), t.clone()));
                }
            }
        }
    }
    let hunk = re(r"^@@[^@]*@@\s*([a-z][\w-]*)\s*:(?!=)");
    let line_rule = re(r"^[+-]([a-z][\w-]*)\s*:(?!=)");
    for line in l7r_guard::shared::speckit::splitlines(make_diff) {
        let m = hunk
            .captures(line)
            .ok()
            .flatten()
            .or_else(|| line_rule.captures(line).ok().flatten());
        if let Some(m) = m {
            if named.contains_key(&m[1]) {
                out.insert(("target".to_owned(), m[1].to_owned()));
            }
        }
    }
    Ok(out
        .into_iter()
        .map(|(k, n)| (guard_kind(&k).to_owned(), n))
        .collect())
}

/// Every tool, listed from the code, with its numbers from the records; `guard_log` is the guard log's directory.
///
/// # Errors
///
/// The inventory or a record cannot be read where the Python raised.
pub fn collect(root: &Path, guard_log: &Path) -> Result<Tools, Raised> {
    let mut t = Tools::new();
    for name in hook_guards(root)? {
        t.insert(
            ("guard".to_owned(), name.clone()),
            Tally::new("guard", &name),
        );
    }
    for p in check_paths(root)? {
        let name = stem(&p);
        t.insert(
            ("check".to_owned(), name.clone()),
            Tally::new("check", &name),
        );
    }
    for name in targets(root)? {
        t.insert(
            ("target".to_owned(), name.clone()),
            Tally::new("target", &name),
        );
    }
    for name in reviews(root) {
        t.insert(
            ("review".to_owned(), name.clone()),
            Tally::new("review", &name),
        );
    }
    for (name, e) in registry(root)? {
        let kind = registry_kind(&e)?;
        entry(&mut t, guard_kind(&kind), &name);
    }
    records::tally_guards(&mut t, &records::guard_rows(guard_log));
    let dirs = records::git_dirs(root);
    let usage: Vec<_> = dirs
        .iter()
        .flat_map(|d| records::jsonl(&d.join("tool-usage.jsonl")))
        .collect();
    let began = records::tally_usage(&mut t, &usage);
    let mut events = Vec::new();
    for d in &dirs {
        let mut logs = ending(&d.join("l7r-events"), ".jsonl");
        logs.sort();
        events.extend(logs.iter().flat_map(|p| records::jsonl(p)));
    }
    records::tally_events(&mut t, &events, began);
    let mut held = records::tally_ledger(&mut t, &records::ledger_rows(root)?);
    if records::tally_arbiter(&mut t, root) {
        held.insert("round-arbiter".to_owned());
    }
    records::tally_bypass(&mut t, root)?;
    for ((kind, name), tool) in &mut t {
        if (kind == "check" || kind == "step") && tool.hits == 0 && tool.uses.is_empty() {
            tool.outcome_record = false;
        }
        if kind == "review" && !held.contains(name) {
            tool.outcome_record = false;
        }
    }
    Ok(t)
}

/// `datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d")`: the microseconds rounded half to even first, as `CPython` rounds them.
#[must_use]
pub fn day_rounded(t: f64) -> String {
    let mut whole = t.trunc();
    let us = ((t - whole) * 1e6).round_ties_even();
    if us >= 1e6 {
        whole += 1.0;
    } else if us < 0.0 {
        whole -= 1.0;
    }
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let (y, m, d, ..) = civil(whole.max(0.0) as u64);
    format!("{y:04}-{m:02}-{d:02}")
}

fn row(tool: &Tally, now: f64) -> [String; 8] {
    let week = tool.uses.iter().filter(|u| **u >= now - 7.0 * DAY).count();
    let first = if tool.first == 0.0 {
        "-".to_owned()
    } else {
        day_rounded(tool.first)
    };
    let note = if tool.first != 0.0 && now - tool.first < TOO_NEW_DAYS * DAY {
        "too new".to_owned()
    } else if !tool.outcome_record {
        "no outcome record".to_owned()
    } else if tool.unseen > 0 {
        format!("{} run(s) with no outcome record", tool.unseen)
    } else {
        String::new()
    };
    let misses = if tool.kind == "check" || tool.kind == "step" {
        "no outcome record".to_owned()
    } else {
        tool.misses.to_string()
    };
    [
        tool.kind.clone(),
        tool.name.clone(),
        first,
        week.to_string(),
        tool.uses.len().to_string(),
        tool.hits.to_string(),
        misses,
        note,
    ]
}

/// The report: every tool of `kind` (all where it is empty), by kind, its uses most first, then its name.
#[must_use]
pub fn table(t: &Tools, kind: &str, now: f64) -> String {
    let mut lines = vec![
        "| kind | tool | first seen | uses (7 d) | uses (all) | interventions | likely misfires | note |".to_owned(),
        "|---|---|---|---|---|---|---|---|".to_owned(),
    ];
    let mut keys: Vec<&(String, String)> = t.keys().collect();
    keys.sort_by(|a, b| {
        (&a.0, std::cmp::Reverse(t[*a].uses.len()), &a.1).cmp(&(
            &b.0,
            std::cmp::Reverse(t[*b].uses.len()),
            &b.1,
        ))
    });
    for key in keys {
        if kind.is_empty() || key.0 == kind {
            lines.push(format!("| {} |", row(&t[key], now).join(" | ")));
        }
    }
    lines.push(String::new());
    lines.push("What this report still cannot see:".to_owned());
    lines.extend(UNSEEN.iter().map(|u| format!("- {u}")));
    lines.join("\n") + "\n"
}

/// The time now, in seconds since the epoch.
#[must_use]
pub fn now() -> f64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64())
}

/// `l7r-gate measure tool-yield [--kind KIND] [--root ROOT]`; `root` is the tree's top, the Python's own `ROOT`.
#[must_use]
pub fn cli(args: &[String], root: &Path, home: &Path) -> Reply {
    let specs = [Spec::value("--kind"), Spec::value("--root")];
    let usage = |why: &str| {
        reply(
            String::new(),
            format!("usage: l7r-gate measure tool-yield [--kind {{,guard,check,target,review,step}}] [--root ROOT]\nl7r-gate measure tool-yield: error: {why}\n"),
            2,
        )
    };
    let p = match parse_with(args, &specs, 0) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    let kind = p.text("--kind", "");
    if !KINDS.contains(&kind) {
        return usage(&format!(
            "argument --kind: invalid choice: {} (choose from '', 'guard', 'check', 'target', 'review', 'step')",
            l7r_guard::shared::py_text::repr(kind)
        ));
    }
    let root = PathBuf::from(p.text("--root", &root.display().to_string()));
    match collect(&root, &home.join(".claude/guard-log")) {
        Ok(t) => reply(table(&t, kind, now()), String::new(), 0),
        Err(why) => reply(
            String::new(),
            format!("Traceback (most recent call last):\n  l7r-gate measure tool-yield\n{why}\n"),
            1,
        ),
    }
}

#[cfg(test)]
pub mod tests;
