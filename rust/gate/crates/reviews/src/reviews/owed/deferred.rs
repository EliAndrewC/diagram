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
//! The settlement-review FR-019 owes every pool hamlet the port moved is recorded the same way (449 T233): no delta detects it for a hamlet
//! already in the pool, so `--moved` keeps a row open for each live hamlet (the review gate passes it on every push at rust-only).
//!
//! `l7r-gate reviews deferred set-aside --root DIR --utc T [--unknown FOLDER]... [--moved] UNIT...` and
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

/// Why a moved hamlet's settlement-review is owed (444 FR-019, 449 T233).
pub const MOVED: &str = "a pool hamlet the port moved (444 FR-019): drawn by the Rust stages alone since the Python hamlet engine was deleted (444 FR-024), its settlement-review owed at the throw back";

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
/// A row whose hamlet the delta renamed is carried to the new name (`carried`) and owed there.
#[must_use]
pub fn standing(tree: &Tree, rows: &[Value]) -> Vec<Unit> {
    let done = reviewed(rows);
    let names: BTreeSet<&str> = tree.folders.iter().map(|d| d.name.as_str()).collect();
    let extra = carried(tree.root, &tree.folders, rows);
    let mut out: Vec<Unit> = Vec::new();
    let push = |u: Unit, out: &mut Vec<Unit>| {
        if !out.iter().any(|p| p.slug() == u.slug()) {
            out.push(u);
        }
    };
    for row in rows.iter().chain(&extra) {
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

/// THE ROWS CARRIED ACROSS A RENAME (449 T233): a row names its hamlet (`on`, a map check's `subject`, a hamlet row's `name` and
/// folder), so a hamlet renamed at rust-only dropped every row it had and the throw back owed none (measured 2026-11-19 in a scratch
/// fixture). A rename is git's rename detection over the delta finding the folder's spec moved with it (`super::renamed`); each row
/// open under the old name is copied to the new one, its time and commit kept and its occasion saying where it came from. `standing`
/// owes the copies while the rename is in the delta; `set-aside` writes them, so they stand once it has landed. No row names a folder
/// the pool lacks: nothing is asked of git.
fn carried(root: &Path, folders: &[super::Folder], rows: &[Value]) -> Vec<Value> {
    let names: BTreeSet<&str> = folders.iter().map(|d| d.name.as_str()).collect();
    let gone = |n: &str| !n.is_empty() && !names.contains(n);
    if !rows
        .iter()
        .any(|r| gone(field(r, "on")) || gone(field(r, "name")))
    {
        return Vec::new();
    }
    let leaf = |p: &str| p.rsplit_once('/').map_or(p, |(_, n)| n).to_owned();
    let to: BTreeMap<String, (String, String, String)> =
        super::renamed(root, &base_of(root).0, folders)
            .into_iter()
            .map(|(old, new)| (leaf(&old), (leaf(&new), old, new)))
            .collect();
    let done = reviewed(rows);
    let mut out = Vec::new();
    for row in rows {
        let unit = field(row, "unit");
        if !unit.is_empty() {
            let Some((new, _, _)) = to.get(field(row, "on")) else {
                continue;
            };
            if !open(&done, unit, field(row, "utc")) {
                continue;
            }
            let old = field(row, "on");
            let subject = if field(row, "subject") == old {
                new.as_str()
            } else {
                field(row, "subject")
            };
            let check = field(row, "check");
            let mut copy = row.clone();
            copy["unit"] = json!(Unit::new(check, subject, new, String::new()).slug());
            copy["subject"] = json!(subject);
            copy["on"] = json!(new);
            copy["occasion"] = json!(format!(
                "{} (carried from {old} across its rename)",
                field(row, "occasion")
            ));
            copy["from"] = json!(old);
            out.push(copy);
        } else if let Some((new, old_rel, new_rel)) = to.get(field(row, "name")) {
            let mut copy = row.clone();
            copy["hamlet"] = json!(new_rel);
            copy["name"] = json!(new);
            copy["from"] = json!(old_rel);
            out.push(copy);
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
/// its elements at the base, unless the record's last row for it holds the same; with `moved`, a settlement-review row for each live
/// pool hamlet the record holds none open for (444 FR-019, 449 T233).
fn set_aside(root: &Path, utc: &str, unknown: &[&str], moved: bool, slugs: &[String]) -> Reply {
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
    let mut written: BTreeSet<String> = BTreeSet::new();
    let folders = super::folders(root);
    // the rows of a hamlet the delta renamed, written under its new name (449 T233), before anything else can claim that name's slugs
    for copy in carried(root, &folders, &had) {
        let unit = field(&copy, "unit").to_owned();
        let from = field(&copy, "from");
        if !unit.is_empty() {
            if !held.contains(unit.as_str()) && written.insert(unit.clone()) {
                let _ = writeln!(said, "deferred: {unit} carried from {from} across its rename, owed at the throw back");
                lines.push(copy);
            }
            continue;
        }
        let r = field(&copy, "hamlet");
        let same = |row: &Value| field(row, "hamlet") == r && row.get("was") == copy.get("was");
        if !had.iter().chain(&lines).any(same) {
            let _ = writeln!(said, "deferred: {r} carried from {from} across its rename, its units owed at the throw back");
            lines.push(copy);
        }
    }
    let mut record = |u: &Unit, lines: &mut Vec<Value>, said: &mut String| {
        let slug = u.slug();
        if !held.contains(slug.as_str()) && written.insert(slug.clone()) {
            let _ = writeln!(said, "deferred: {slug} recorded, owed at the throw back");
            lines.push(
                json!({"unit": slug, "check": u.check, "subject": u.subject, "on": u.on,
                "occasion": u.occasion, "utc": utc, "commit": commit}),
            );
        }
    };
    if !slugs.is_empty() {
        for u in all_owed(root).1 {
            if slug_named(slugs, &u.slug()) {
                record(&u, &mut lines, &mut said);
            }
        }
    }
    // THE HAMLETS THE PORT MOVED (444 FR-019: "its moved pool hamlets owing their settlement-reviews"; FR-023 defers each to the throw
    // back): a hamlet already in the pool owes no settlement-review the delta detects - only a map new to the pool does - so a Rust stage
    // that moved one set nothing aside, and the throw back owed nothing (measured 2026-11-19 in scratch, 449 T233). Every live hamlet is
    // drawn by the Rust stages alone since the Python engine was deleted (FR-024), so each is one the port moved; a row is kept open for
    // each until its review is recorded at integrated (a renamed hamlet's row is carried above).
    if moved {
        for d in &folders {
            if d.kind == Kind::Hamlet && !d.exempt() {
                let u = Unit::new("settlement-review", &d.name, &d.name, MOVED.to_owned());
                record(&u, &mut lines, &mut said);
            }
        }
    }
    let (base, _) = base_of(root);
    let mut at = AtBase::new(root, &base);
    for d in folders {
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

const USAGE: &str = "usage: l7r-gate reviews deferred set-aside|reviewed --root DIR --utc T [--unknown FOLDER]... [--moved] UNIT...\n";

/// `l7r-gate reviews deferred ...`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let verb = args.first().map_or("", String::as_str);
    let specs = [
        Spec::value("--root"),
        Spec::value("--utc"),
        Spec::value("--unknown"),
        Spec::flag("--moved"),
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
        set_aside(
            root,
            utc,
            &p.all("--unknown"),
            p.on("--moved"),
            &p.positional,
        )
    } else {
        mark_reviewed(root, utc, &p.positional)
    }
}

#[cfg(test)]
mod tests;
