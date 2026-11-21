//! THE ONE WRITER of the uncited filter's own lists (feature 449 T147; FR-003, one live writer per shared file): `research/not-kept.jsonl`,
//! feature 312's kept list and its import check - appended under the sources ledger's lock, so two agents of one session never interleave
//! half lines, each URL checked against the blocked list first; and the kept list's rewrites, [`unkeep`] and [`requeue`]. The attempts
//! log is the guard's `shared::attempts`, its own writer; the not-kept line of a pre-hold capture drops its manifest row through the
//! archive's manifest ([`not_kept`]).

use std::io::Write as _;
use std::path::Path;

use l7r_shared::consulted::{self, norm};
use l7r_shared::pyjson::{dumps, py_str, truthy, value_repr};
use serde_json::{json, Map, Value};

use crate::set::work;
use crate::{
    base, lines_keep, os_error, read_text, record_dir, today, Error, Result, ACCESS, KEPT,
    NOT_KEPT, REASONS,
};

/// `line`: one not-kept line, its reasons from [`REASONS`] (at least one) and its access state from [`ACCESS`].
///
/// # Errors
/// A reason or an access state the vocabulary lacks (`ValueError`).
pub fn line(url: &str, reasons: &[String], basis: &str, note: &str, access: &str) -> Result<Value> {
    if reasons.is_empty() || reasons.iter().any(|r| !REASONS.contains(&r.as_str())) {
        return Err(Error::new(
            "ValueError",
            format!(
                "{url}: reasons {} - each one of {}, at least one",
                value_repr(&json!(reasons)),
                REASONS.join(", ")
            ),
        ));
    }
    if !access.is_empty() && !ACCESS.contains(&access) {
        return Err(Error::new(
            "ValueError",
            format!(
                "{url}: access {} is not one of {}",
                value_repr(&json!(access)),
                ACCESS.join(", ")
            ),
        ));
    }
    let mut x = Map::new();
    x.insert("url".into(), json!(norm(url)));
    x.insert("raw".into(), json!(url));
    x.insert("reasons".into(), json!(reasons));
    x.insert("note".into(), json!(note));
    x.insert("basis".into(), json!(basis));
    x.insert("date".into(), json!(today()));
    x.insert("feature".into(), json!("312"));
    if !access.is_empty() {
        x.insert("access".into(), json!(access));
    }
    Ok(Value::Object(x))
}

/// `line.get("raw") or line["url"]`.
fn url_of(x: &Value) -> Result<String> {
    match x.get("raw").filter(|v| truthy(v)) {
        Some(v) => Ok(py_str(v)),
        None => x
            .get("url")
            .map(py_str)
            .ok_or_else(|| Error::new("KeyError", "'url'")),
    }
}

/// Append to one of the filter's lists (`rel`, under the record's base), under the ledger's kind of lock; a blocked URL refused first.
///
/// # Errors
/// A blocked URL, a line with no URL, the lock or the write.
pub fn write(root: &Path, lines: &[Value], rel: &str) -> Result<()> {
    if rel == l7r_shared::attempts::LOG {
        return Err(Error::new(
            "ValueError",
            "the attempts log is written by `add` (l7r-gate record attempts add), its one writer",
        ));
    }
    if lines.is_empty() {
        return Ok(());
    }
    for x in lines {
        consulted::check(&url_of(x)?, "the attempts log", &record_dir(root))?;
    }
    let path = base(root).join(rel);
    let up = path.parent().unwrap_or(&path);
    crate::mkdir(up)?;
    let _lock = consulted::locked(&consulted::home(root), 30.0)?;
    let text: String = lines.iter().map(|x| dumps(x, None, false) + "\n").collect();
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
        .and_then(|mut f| f.write_all(text.as_bytes()))
        .map_err(|e| os_error(&e, &path))
}

/// Written to the not-kept list; FR-010: a pre-hold capture not kept loses its manifest row, its copy staying in the archive's history.
///
/// # Errors
/// As [`write`]; a row that will not read or go.
pub fn not_kept(root: &Path, lines: &[Value]) -> Result<()> {
    write(root, lines, NOT_KEPT)?;
    for x in lines {
        let row = l7r_gate_archive::manifest::row_path(root, &crate::lists::field(x, "raw")?);
        if row.is_file()
            && !l7r_gate_archive::manifest::load_row(&row)?
                .get("keys")
                .is_some_and(truthy)
        {
            crate::remove_file(&row)?;
        }
    }
    Ok(())
}

/// The pages kept, on the kept list.
///
/// # Errors
/// As [`write`].
pub fn kept(root: &Path, urls: &[String], basis: &str) -> Result<()> {
    let lines: Vec<Value> = urls
        .iter()
        .map(|u| json!({"url": norm(u), "raw": u, "basis": basis, "date": today(), "feature": "312"}))
        .collect();
    write(root, &lines, KEPT)
}

/// `x[k]` of a list's line.
///
/// # Errors
/// As the Python's subscript raised.
pub fn field(x: &Value, k: &str) -> Result<String> {
    l7r_gate_archive::ops::field(x, k)
}

/// A list's lines (`at.read`: each line that parses, of any type).
///
/// # Errors
/// A file that is not UTF-8.
pub fn read(root: &Path, rel: &str) -> Result<Vec<Value>> {
    Ok(l7r_shared::attempts::read(root, rel)?)
}

/// A kept page judged again NOT-KEPT (a duplicate found later, a page the filter kept in error): its line leaves the kept list and a
/// not-kept line records why. An entry written for it is retired by `merge`, not here. The kept list is rewritten before the not-kept
/// line is checked, as the Python did.
///
/// # Errors
/// A page not on the kept list (`ValueError`), the lock, the write, the line.
pub fn unkeep(root: &Path, raw: &str, reasons: &[String], basis: &str, note: &str) -> Result<()> {
    let path = base(root).join(KEPT);
    let q = dumps(&json!(raw), None, false);
    {
        let _lock = consulted::locked(&consulted::home(root), 30.0)?;
        let text = read_text(&path)?;
        let all = lines_keep(&text);
        if !all.iter().any(|s| s.contains(&q)) {
            return Err(Error::new(
                "ValueError",
                format!("{raw} is not on the kept list"),
            ));
        }
        let kept: String = all.into_iter().filter(|s| !s.contains(&q)).collect();
        crate::write_text(&path, &kept)?;
    }
    write(root, &[line(raw, reasons, basis, note, "")?], NOT_KEPT)
}

/// The kept and not-kept lines of a work dropped (`requeue`'s rewrite), whether any went.
///
/// # Errors
/// The lock, a line that is not JSON or has no URL, the write.
pub fn drop_verdicts(root: &Path, raw: &str) -> Result<bool> {
    let n = work(&norm(raw));
    let mut hit = false;
    let _lock = consulted::locked(&consulted::home(root), 30.0)?;
    for rel in [KEPT, NOT_KEPT] {
        let path = base(root).join(rel);
        let text = if path.is_file() {
            read_text(&path)?
        } else {
            String::new()
        };
        let all = lines_keep(&text);
        let mut keep = String::new();
        for s in &all {
            if crate::strip(s).is_empty() || work(&field(&crate::loads(s)?, "url")?) != n {
                keep.push_str(s);
            } else {
                hit = true;
            }
        }
        crate::write_text(&path, &keep)?;
    }
    Ok(hit)
}

/// `{x["url"] for x in lines}`.
///
/// # Errors
/// A line with no URL.
pub fn urls_of(lines: &[Value]) -> Result<std::collections::HashSet<String>> {
    lines.iter().map(|x| field(x, "url")).collect()
}

/// `x.get(k)` of a line that may not be a mapping (`AttributeError` as the Python's `.get` raised).
///
/// # Errors
/// The line is no mapping.
pub fn get<'v>(x: &'v Value, k: &str) -> Result<Option<&'v Value>> {
    match x {
        Value::Object(m) => Ok(m.get(k)),
        other => Err(Error::new(
            "AttributeError",
            format!(
                "'{}' object has no attribute 'get'",
                l7r_shared::blocked::type_name(other)
            ),
        )),
    }
}

#[cfg(test)]
mod tests;
