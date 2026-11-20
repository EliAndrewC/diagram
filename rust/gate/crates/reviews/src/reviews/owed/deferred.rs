//! The hamlet reviews set aside at rust-only, recorded until the throw back (feature 444 FR-023; feature 449 T232). At rust-only the
//! review gate sets a pool hamlet's owed units aside, owed again "for every pool hamlet the port moved" once the port switch is thrown
//! back to integrated. What a delta owes is read against the landing's base, and a hamlet's base census is main's drawing of it (the
//! mirror's render-sync `.driver.json`): once the push landed and the mirror drew it, the delta no longer held the element, and at the
//! throw back the review it owed was owed by nothing (measured 2026-11-19 in a scratch mirror: an edited hamlet pushed at rust-only,
//! the mirror's render-sync, the switch thrown - `review-gate: clean`). So the gate records each unit it sets aside, and each hamlet
//! whose units it could not know (its redraw failed, which refuses nothing at rust-only) with its elements at the base, in the tracked
//! `dev/deferred-reviews.jsonl`, one row each, its time and commit, committed with the push; at integrated every unit the record holds
//! open, that still stands, is owed (`all_owed`) until the gate finds its review and records it reviewed - on main, so a review one
//! clone recorded clears it for every clone, where the verdict files are each clone's own.
//!
//! `l7r-gate reviews deferred set-aside --root DIR --utc T [--unknown FOLDER]... UNIT...` and
//! `l7r-gate reviews deferred reviewed --root DIR --utc T UNIT...`.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::{all_owed, base_legends, base_of, head8, rel, AtBase, Tree, Unit, DRIVER};
use crate::record::args::{parse_with, Spec};
use crate::record::bundle::py_repr;
use crate::reviews::{git, py_path, reply};
use crate::Reply;
use l7r_gate_pool::Kind;

/// The record: append-only, merged by union (`.gitattributes`), so two clones' rows both stand.
pub const RECORD: &str = "dev/deferred-reviews.jsonl";

/// The record's rows, in file order; a line that is no JSON object is skipped.
#[must_use]
pub fn rows(root: &Path) -> Vec<Value> {
    std::fs::read_to_string(root.join(RECORD))
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(Value::is_object)
        .collect()
}

fn field<'a>(row: &'a Value, key: &str) -> &'a str {
    row.get(key).and_then(Value::as_str).unwrap_or("")
}

/// Each unit's latest review time on the record (ISO UTC, compared as text).
fn reviewed(rows: &[Value]) -> BTreeMap<String, String> {
    let mut at: BTreeMap<String, String> = BTreeMap::new();
    for row in rows {
        let (unit, utc) = (field(row, "reviewed"), field(row, "utc"));
        if !unit.is_empty() && at.get(unit).is_none_or(|was| was.as_str() < utc) {
            at.insert(unit.to_owned(), utc.to_owned());
        }
    }
    at
}

/// Whether a unit set aside at `since` is still owed: no review recorded at or after it.
fn open(done: &BTreeMap<String, String>, slug: &str, since: &str) -> bool {
    done.get(slug).is_none_or(|at| at.as_str() < since)
}

/// A set-aside unit's occasion: when and where it was set aside, then why it was owed.
fn occasion(row: &Value, why: &str) -> String {
    format!(
        "set aside at rust-only {} ({}): {why}",
        field(row, "utc"),
        head8(field(row, "commit"))
    )
}

/// The units the record holds open that still stand in the tree: a unit row's unit, while its map is in the pool and, for an element's
/// check, the element still on it (a legend not known keeps it owed); a hamlet row's elements its drawing now holds that it did not
/// when it was set aside (a drawing not known names none - its problem line says how to draw it).
#[must_use]
pub fn standing(tree: &Tree, rows: &[Value]) -> Vec<Unit> {
    let done = reviewed(rows);
    let names: BTreeSet<&str> = tree.folders.iter().map(|d| d.name.as_str()).collect();
    let mut out: Vec<Unit> = Vec::new();
    let push = |u: Unit, out: &mut Vec<Unit>| {
        if !out.iter().any(|p| p.slug() == u.slug()) {
            out.push(u);
        }
    };
    for row in rows {
        let since = field(row, "utc");
        let unit = field(row, "unit");
        if !unit.is_empty() {
            let u = Unit::new(
                field(row, "check"),
                field(row, "subject"),
                field(row, "on"),
                occasion(row, field(row, "occasion")),
            );
            let element = matches!(u.check.as_str(), "glyph-check" | "size-audit");
            let on_map = tree
                .legends
                .get(&u.on)
                .is_none_or(|legend| legend.contains(&u.subject));
            if open(&done, unit, since) && names.contains(u.on.as_str()) && (!element || on_map) {
                push(u, &mut out);
            }
            continue;
        }
        let name = field(row, "name");
        let Some(now) = tree.legends.get(name) else {
            continue;
        };
        let was: BTreeSet<String> = row
            .get("was")
            .and_then(Value::as_array)
            .map(|a| {
                a.iter()
                    .filter_map(Value::as_str)
                    .map(str::to_owned)
                    .collect()
            })
            .unwrap_or_default();
        for element in now - &was {
            let why = format!(
                "{} is new to {name} since its units were not known",
                py_repr(&element)
            );
            let u = Unit::new("glyph-check", &element, name, occasion(row, &why));
            if open(&done, &u.slug(), since) {
                push(u, &mut out);
            }
        }
    }
    out
}

/// Append the rows; none written, nothing touched (an empty record left behind would be a change for the gate to commit).
fn append(root: &Path, lines: &[Value]) -> Result<(), String> {
    if lines.is_empty() {
        return Ok(());
    }
    let path = root.join(RECORD);
    let write = || -> std::io::Result<()> {
        std::fs::create_dir_all(root.join("dev"))?;
        let mut f = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path)?;
        for line in lines {
            writeln!(f, "{line}")?;
        }
        Ok(())
    };
    write().map_err(|e| format!("{RECORD}: {e}"))
}

/// `set-aside`: a row for each named unit owed now that the record does not hold open already, and a row for each named hamlet holding
/// its elements at the base, unless the record's last row for it holds the same.
fn set_aside(root: &Path, utc: &str, unknown: &[&str], slugs: &[String]) -> Reply {
    let commit = git(root, &["rev-parse", "HEAD"]).unwrap_or_default();
    let had = rows(root);
    let done = reviewed(&had);
    let held: BTreeSet<&str> = had
        .iter()
        .filter(|r| open(&done, field(r, "unit"), field(r, "utc")))
        .map(|r| field(r, "unit"))
        .collect();
    let mut lines: Vec<Value> = Vec::new();
    let mut said = String::new();
    for u in all_owed(root).1 {
        let slug = u.slug();
        if slug_named(slugs, &slug) && !held.contains(slug.as_str()) {
            let _ = writeln!(said, "deferred: {slug} recorded, owed at the throw back");
            lines.push(
                json!({"unit": slug, "check": u.check, "subject": u.subject, "on": u.on,
                "occasion": u.occasion, "utc": utc, "commit": commit}),
            );
        }
    }
    let (base, _) = base_of(root);
    let mut at = AtBase::new(root, &base);
    for d in super::folders(root) {
        let r = rel(root, &d.path);
        if d.kind != Kind::Hamlet || !unknown.contains(&r.as_str()) {
            continue;
        }
        let order = vec![(d.name.clone(), Err((rel(root, &d.file(DRIVER)), true)))];
        let was: Vec<String> = base_legends(root, &mut at, order)
            .get(&d.name)
            .map(|s| s.iter().cloned().collect())
            .unwrap_or_default();
        let last = had.iter().rev().find(|row| field(row, "hamlet") == r);
        if last.is_some_and(|row| row.get("was") == Some(&json!(was))) {
            continue;
        }
        let _ = writeln!(said, "deferred: {r} recorded with its elements at the base, its units owed at the throw back");
        lines.push(json!({"hamlet": r, "name": d.name, "was": was, "utc": utc, "commit": commit}));
    }
    match append(root, &lines) {
        Ok(()) => reply(said, String::new(), 0),
        Err(why) => reply(
            String::new(),
            format!("l7r-gate reviews deferred: {why}\n"),
            1,
        ),
    }
}

fn slug_named(slugs: &[String], slug: &str) -> bool {
    slugs.iter().any(|s| s == slug)
}

/// `reviewed`: a row for each named unit the record holds open, its review found by the gate.
fn mark_reviewed(root: &Path, utc: &str, slugs: &[String]) -> Reply {
    let commit = git(root, &["rev-parse", "HEAD"]).unwrap_or_default();
    let tree = Tree::read(root);
    let mut lines: Vec<Value> = Vec::new();
    let mut said = String::new();
    for u in standing(&tree, &rows(root)) {
        let slug = u.slug();
        if slug_named(slugs, &slug) {
            let _ = writeln!(said, "deferred: {slug} reviewed, recorded");
            lines.push(json!({"reviewed": slug, "utc": utc, "commit": commit}));
        }
    }
    match append(root, &lines) {
        Ok(()) => reply(said, String::new(), 0),
        Err(why) => reply(
            String::new(),
            format!("l7r-gate reviews deferred: {why}\n"),
            1,
        ),
    }
}

const USAGE: &str = "usage: l7r-gate reviews deferred set-aside|reviewed --root DIR --utc T [--unknown FOLDER]... UNIT...\n";

/// `l7r-gate reviews deferred ...`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let verb = args.first().map_or("", String::as_str);
    let specs = [
        Spec::value("--root"),
        Spec::value("--utc"),
        Spec::value("--unknown"),
    ];
    let Ok(p) = parse_with(args.get(1..).unwrap_or_default(), &specs, usize::MAX) else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let utc = p.text("--utc", "");
    if utc.is_empty() || !matches!(verb, "set-aside" | "reviewed") {
        return reply(String::new(), USAGE.to_owned(), 2);
    }
    let asked = p.text("--root", ".");
    let Some(top) =
        git(&py_path(asked), &["rev-parse", "--show-toplevel"]).filter(|t| !t.is_empty())
    else {
        return reply(
            String::new(),
            format!("l7r-gate reviews deferred: {asked} is not a git repository\n"),
            1,
        );
    };
    let root = Path::new(&top);
    if verb == "set-aside" {
        set_aside(root, utc, &p.all("--unknown"), &p.positional)
    } else {
        mark_reviewed(root, utc, &p.positional)
    }
}

#[cfg(test)]
mod tests;
