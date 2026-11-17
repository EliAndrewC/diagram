//! A Rust unit's code fingerprint holds the value of every crate constant it reads (feature 449 T166), as a `.py` unit's has since
//! feature 316 (`tools/claims.module_units`' `values`: the dumped value of every in-scope module-level constant it names). Before T166 a
//! Rust unit's core was its own tokens alone, so a changed constant owed only the constant's own claim and none of the 111 claimed
//! functions reading one (measured by T165, 284 index rows): a figure could move under a claim judged against the old one.
//!
//! THE RULE, the Python's: each constant the unit reads - resolved as its bundle's context resolves a name (`context.rs`: the unit's own
//! file first, then a path or a `use` of the file naming the one item of its crate that defines it) - enters the core as
//! `<qualname>=<its value's fingerprint>`, sorted, keyed by the constant's name and not its file, so moving a constant between files
//! owes nothing; one level, as the Python's (a constant's own value is its own unit, and a constant reading another holds that one's
//! value). The value is the tokens after the item's `=`: a changed type or visibility owes no reader, as the Python dumps the value
//! alone. A unit reading no constant keeps the core it had, so the migration re-records only the readers' rows.

use std::path::Path;

use super::context::{constant, Tables};
use super::units::{rust_core, sha};

/// `<qualname>=<value fingerprint>` for each crate constant `body` (the item `qual` of `path`) reads, sorted, joined by `\x1e`; empty
/// where it reads none.
pub fn values(tables: &mut Tables, root: &Path, path: &str, qual: &str, body: &str) -> String {
    let mut hits: Vec<String> = tables
        .refs(root, path, body, qual)
        .into_iter()
        .filter(|r| constant(r))
        .map(|r| {
            // every reference resolved from a crate's items has its source there
            let src = tables.source(root, &r).unwrap_or_default();
            let name = r.split_once("::").map_or(r.as_str(), |p| p.1);
            format!("{name}={}", value_of(&src))
        })
        .collect();
    hits.sort();
    hits.dedup();
    hits.join("\x1e")
}

/// A constant's value fingerprinted: its tokens after the first `=` (a `const` or `static` always has one).
fn value_of(src: &str) -> String {
    let raw = crate::codeid::rust_tokens(src.as_bytes());
    let text = String::from_utf8_lossy(&raw);
    let toks: Vec<&str> = text.split('\0').collect();
    let at = toks.iter().position(|t| *t == "=").map_or(0, |i| i + 1);
    sha(&toks[at..].join("\0"))
}

/// A Rust item's core: its tokens (`rust_core`) where it reads no constant, else its tokens and the `values` it reads, hashed together
/// as the Python's `_sha(dump + "\x1d" + vals)`.
pub fn core(body: &str, values: &str) -> String {
    if values.is_empty() {
        return rust_core(body);
    }
    let raw = crate::codeid::rust_tokens(body.as_bytes());
    sha(&format!("{}\x1d{values}", String::from_utf8_lossy(&raw)))
}

/// A row's `reads` set to a unit's (`Some`, its code recorded with it), dropped where the unit reads none; left as it is where the code was
/// not (`None`).
pub fn stamp(row: &mut serde_json::Map<String, serde_json::Value>, reads: Option<&str>) {
    match reads {
        Some("") => {
            row.shift_remove("reads");
        }
        Some(r) => {
            row.insert("reads".into(), serde_json::json!(r));
        }
        None => {}
    }
}

/// Where `claims refingerprint` records each migration it makes, one row a run (feature 449 T166).
pub const MIGRATIONS: &str = "dev/claims-refingerprint.jsonl";

/// A row of [`MIGRATIONS`]: when, how many and which rows were carried to the current fingerprint. A carried row's code was the old
/// scheme's fingerprint of the code as it stands, so its check stands: the migration re-checks nothing and owes nothing.
///
/// # Errors
///
/// Where the record cannot be written.
pub fn record_migration(root: &Path, keys: &[String]) -> Result<(), crate::record::repo::Fail> {
    let row = serde_json::json!({
        "utc": crate::record::repo::utc_now(),
        "rows": keys.len(),
        "why": "each row's recorded code was its unit's fingerprint under the scheme before (no star re-exports, 417 T54; no Rust constant reads, 449 T166) of the code as it stands: carried to the current scheme, none re-checked, none owed",
        "keys": keys,
    });
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(root.join(MIGRATIONS))
        .map_err(crate::record::repo::fail)?;
    std::io::Write::write_all(&mut f, (crate::logs::one_line_utf8(&row) + "\n").as_bytes())
        .map_err(crate::record::repo::fail)
}

#[cfg(test)]
mod tests;
