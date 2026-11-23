//! A GLYPH UNIT THE ROUND ARBITER DISCHARGED (feature 449 T377, the round arbiter's `ask:glyph-occasions-emit-449-T351`, its what (3): "If
//! the push has no route that reads an arbiter accept as a glyph unit's discharge, that route is built with the fix and its test"). An
//! `ask:` ruling names the units it discharges in its words alone, and the push read only a `round:` ruling bound to one unit (`arbiter
//! unit-ruled`, asked only once a unit has a verdict record), so a discharged glyph unit reached the review gate with no record and was
//! refused - `ask:449-land-final-glyphs`'s 50 units, then this ruling's 48, carried only by `REVIEW_GATE_OK`.
//!
//! `l7r-gate reviews discharge --root DIR --ruling TRIGGER UNIT...` records, for each glyph unit owed now, the accept that discharges it
//! and its kind's marks on its map as they read now (`marks::digest`: its tags and text, and the `<defs>` entries they use):
//! `<git dir>/review-verdicts/<unit>.discharge.json`, beside the verdicts, so `land-alone.sh` seeds a landing worktree with it as it does
//! them. The owed lookup passes over a glyph unit whose record's ruling reads `accept` in that feature's `arbiter.jsonl` and whose kind's
//! marks hash as recorded - so `make verify`, the glyph hour, the checkpoint and the push all read it discharged - and owes it again once
//! they move (the ruling: "If a sheet changes again before the push, any kind whose marks change is owed again under the rule"). The
//! session names the units, since only the ruling's words do; the tool refuses a ruling that is no accept, and a unit not owed, not a
//! glyph check, or drawn by no mark of its kind to bind it to (a hamlet's, whose drawing is no sheet read by kind) - all before it writes.
//!
//! Research: plumbing - NONE: records and reads a ruling's discharge of a review unit, deciding nothing about a map

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::{git, gitdir, py_path, reply, write_json};
use super::{marks, owed_discharged, read_replace, Discharged, Tree, Unit};
use crate::record::args::{parse_with, Spec};
use crate::record::repo::utc_now;
use crate::Reply;

const SUFFIX: &str = ".discharge.json";
const USAGE: &str = "usage: l7r-gate reviews discharge [--root DIR] --ruling TRIGGER UNIT...\n";

/// Where unit `slug`'s discharge is recorded: its git directory's, beside the verdicts.
fn record_of(root: &Path, slug: &str) -> PathBuf {
    gitdir(root)
        .unwrap_or(root.join(".git"))
        .join("review-verdicts")
        .join(format!("{slug}{SUFFIX}"))
}

fn text<'a>(v: &'a Value, k: &str) -> &'a str {
    v.get(k).and_then(Value::as_str).unwrap_or_default()
}

/// `trigger`'s ruling and the feature directory (from the root) whose `arbiter.jsonl` holds it: `only` that one where given, else the
/// first of every feature's (an ask is filed under the feature the session was on, not always the one it names).
fn ruling_of(root: &Path, trigger: &str, only: Option<&str>) -> Option<(String, String)> {
    let dirs: Vec<PathBuf> = only.map_or_else(
        || l7r_shared::checks::arbiter::spec_dirs(root, ""),
        |d| vec![root.join(d)],
    );
    for d in dirs {
        let log = std::fs::read_to_string(d.join("arbiter.jsonl")).unwrap_or_default();
        for row in log
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        {
            if text(&row, "trigger") == trigger {
                let feature = d.strip_prefix(root).unwrap_or(&d).display().to_string();
                return Some((feature, text(&row, "ruling").to_owned()));
            }
        }
    }
    None
}

/// The digest of each map's kinds' marks as drawn now, each sheet read once.
struct Sheets<'t> {
    tree: &'t Tree<'t>,
    read: BTreeMap<String, Option<marks::Marks>>,
}

impl<'t> Sheets<'t> {
    fn new(tree: &'t Tree<'t>) -> Self {
        Self {
            tree,
            read: BTreeMap::new(),
        }
    }

    /// `kind`'s marks on map `on` now, hashed; `None` where `on` has no drawn sheet or no mark of it.
    fn digest(&mut self, on: &str, kind: &str) -> Option<String> {
        let tree = self.tree;
        let sheet = self.read.entry(on.to_owned()).or_insert_with(|| {
            let d = tree
                .folders
                .iter()
                .find(|d| d.name == on && d.has(".svg"))?;
            Some(marks::read(&read_replace(&d.file(".svg"))))
        });
        marks::digest(sheet.as_ref()?, kind)
    }
}

/// Whether unit `u`'s recorded discharge stands: its ruling an accept in its feature's log, its kind's marks as they were recorded.
fn stands(root: &Path, sheets: &mut Sheets, u: &Unit) -> Option<String> {
    let rec: Value =
        serde_json::from_str(&std::fs::read_to_string(record_of(root, &u.slug())).ok()?).ok()?;
    let trigger = text(&rec, "ruling");
    let (_, ruling) = ruling_of(root, trigger, Some(text(&rec, "feature")))?;
    (ruling == "accept" && sheets.digest(&u.on, &u.subject).as_deref() == Some(text(&rec, "marks")))
        .then(|| trigger.to_owned())
}

/// The glyph units a standing discharge answers, taken out of `units`: each `(slug, ruling)`.
pub(super) fn take(tree: &Tree, units: &mut Vec<Unit>) -> Vec<Discharged> {
    let mut sheets = Sheets::new(tree);
    let mut taken = Vec::new();
    units.retain(|u| {
        let by = (u.check == "glyph-check")
            .then(|| stands(tree.root, &mut sheets, u))
            .flatten();
        if let Some(by) = &by {
            taken.push((u.slug(), by.clone()));
        }
        by.is_none()
    });
    taken
}

/// `l7r-gate reviews discharge`'s command line: every unit judged first, then each recorded - or none, and every refusal listed.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let specs = [Spec::value("--root"), Spec::value("--ruling")];
    let Ok(p) = parse_with(args, &specs, usize::MAX) else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let trigger = p.text("--ruling", "");
    if trigger.is_empty() || p.positional.is_empty() {
        return reply(String::new(), USAGE.to_owned(), 2);
    }
    let asked = p.text("--root", ".");
    let Some(top) =
        git(&py_path(asked), &["rev-parse", "--show-toplevel"]).filter(|t| !t.is_empty())
    else {
        return reply(
            String::new(),
            format!("l7r-gate reviews discharge: {asked} is not a git repository\n"),
            1,
        );
    };
    let root = Path::new(&top);
    let refuse = |why: String| {
        reply(
            String::new(),
            format!("l7r-gate reviews discharge: refused - {why}\n"),
            1,
        )
    };
    let Some((feature, ruling)) = ruling_of(root, trigger, None) else {
        return refuse(format!(
            "no feature's arbiter.jsonl holds {trigger}: name the round arbiter's ruling by its trigger"
        ));
    };
    if ruling != "accept" {
        return refuse(format!(
            "{trigger} ruled {ruling}: only an accept discharges a review unit"
        ));
    }
    let (_, owed, _, taken) = owed_discharged(root);
    let tree = Tree::read(root);
    let mut sheets = Sheets::new(&tree);
    let (mut out, mut refused, mut records) = (String::new(), Vec::new(), Vec::new());
    for slug in &p.positional {
        if let Some((_, by)) = taken.iter().find(|(s, _)| s == slug) {
            let _ = writeln!(out, "{slug}: already discharged by {by}");
            continue;
        }
        let Some(u) = owed.iter().find(|u| &u.slug() == slug) else {
            refused.push(format!(
                "{slug} is not owed now (`l7r-gate reviews owed --landing` lists what is)"
            ));
            continue;
        };
        if u.check != "glyph-check" {
            refused.push(format!(
                "{slug} is a {}: only a glyph check is discharged here",
                u.check
            ));
            continue;
        }
        let Some(marks) = sheets.digest(&u.on, &u.subject) else {
            refused.push(format!(
                "{slug}: {} draws no mark of {} read by kind, so nothing binds the discharge",
                u.on, u.subject
            ));
            continue;
        };
        let rec = json!({"unit": slug, "check": u.check, "subject": u.subject, "on": u.on, "ruling": trigger,
            "feature": feature, "marks": marks, "utc": utc_now()});
        let _ = writeln!(
            out,
            "{slug}: discharged by {trigger} (its marks on {} as they read now, {marks})",
            u.on
        );
        records.push((record_of(root, slug), rec));
    }
    if !refused.is_empty() {
        return refuse(format!("nothing recorded:\n  {}", refused.join("\n  ")));
    }
    for (path, rec) in records {
        let _ = path.parent().map(std::fs::create_dir_all);
        let _ = write_json(&path, &rec);
    }
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
