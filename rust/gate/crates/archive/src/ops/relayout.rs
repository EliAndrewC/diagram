//! The one-time relayout (`archive_ops.relayout`, feature 309; ported by feature 449 T147 with the rest of its file, the command kept
//! as the Python had it): the first ~1,700 captures were filed `<key>/<id>/`, `notes/<id>/` and `<key>/gm-copy/<name>`; the GM asked for
//! a layout that stays browsable past 5,000 (2026-10-02), so they move to `<id[:2]>/<id>/` and `gm-copies/<name>` (git renames), and the
//! manifest's rows to `research/archive/<id[:2]>/<id>.json`. On today's archive it finds nothing to move.

use std::path::{Path, PathBuf};

use l7r_guard::shared::pyjson::py_str;
use serde_json::{json, Value};

use super::{field, mkdir, rmdir, sorted_entries, unlink, write_table};
use crate::manifest::{
    capture_base, gm_table, load_row, manifest_dir, write_row, GM_DEST, LOCK_WAIT,
};
use crate::store::Archive;
use crate::{Error, Result};

/// `os.path.dirname` and `os.path.basename`.
pub(crate) fn split_last(p: &str) -> (&str, &str) {
    match p.rfind('/') {
        Some(i) => {
            let head = &p[..i];
            let trimmed = head.trim_end_matches('/');
            (
                if trimmed.is_empty() {
                    &head[..head.len().min(1)]
                } else {
                    trimmed
                },
                &p[i + 1..],
            )
        }
        None => ("", p),
    }
}

/// `renames[old] = new` (`replace`) or `renames.setdefault(old, new)`, in the dict's order.
fn rename(renames: &mut Vec<(String, String)>, old: String, new: String, replace: bool) {
    match renames.iter_mut().find(|(o, _)| *o == old) {
        Some((_, n)) if replace => *n = new,
        Some(_) => {}
        None => renames.push((old, new)),
    }
}

/// The flat rows: `research/archive/[0-9a-f]*.json`, sorted.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the glob's `*.json` matched the name's case exactly, as this does"
)]
fn flat_rows(root: &Path) -> Vec<PathBuf> {
    sorted_entries(&manifest_dir(root), false)
        .into_iter()
        .filter(|p| {
            let n = p
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default();
            n.ends_with(".json")
                && n.bytes()
                    .next()
                    .is_some_and(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
        })
        .collect()
}

/// Every directory under `dir`, deepest first.
fn dirs_deepest_first(dir: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    let mut todo = vec![dir.to_path_buf()];
    while let Some(d) = todo.pop() {
        for p in sorted_entries(&d, true) {
            if p.is_dir() && !p.is_symlink() {
                out.push(p.clone());
                todo.push(p);
            }
        }
    }
    out.sort_by_key(|p| std::cmp::Reverse(p.components().count()));
    out
}

fn empty(d: &Path) -> bool {
    std::fs::read_dir(d).is_ok_and(|mut r| r.next().is_none())
}

/// The renames made: a directory under its new name as one `git mv`, or its children moved into a new one.
fn apply_renames(store: &Archive, renames: &[(String, String)]) -> Result<()> {
    for (old, new) in renames {
        if !store.dir.join(old).exists() || old == new {
            continue;
        }
        let (_, last) = split_last(old);
        if new.ends_with(&format!("/{last}")) || new.starts_with(&format!("{GM_DEST}/")) {
            let up = store.dir.join(new);
            let up = up.parent().unwrap_or(&store.dir);
            mkdir(up)?;
            store.git(&["mv", "-k", old, new], true)?;
        } else {
            let to = store.dir.join(new);
            mkdir(&to)?;
            for child in sorted_entries(&store.dir.join(old), true) {
                let name = child
                    .file_name()
                    .map(|n| n.to_string_lossy().into_owned())
                    .unwrap_or_default();
                let rel = child
                    .strip_prefix(&store.dir)
                    .unwrap_or(&child)
                    .to_string_lossy()
                    .into_owned();
                store.git(&["mv", "-k", &rel, &format!("{new}/{name}")], true)?;
            }
        }
    }
    Ok(())
}

/// The old top-level folders the renames emptied, removed deepest first.
fn sweep(store: &Archive, renames: &[(String, String)]) -> Result<()> {
    let mut tops: Vec<&str> = renames
        .iter()
        .map(|(o, _)| o.split('/').next().unwrap_or_default())
        .collect();
    tops.sort_unstable();
    tops.dedup();
    for old in tops {
        let at = store.dir.join(old);
        if at.is_dir() {
            for d in dirs_deepest_first(&at) {
                if empty(&d) {
                    rmdir(&d)?;
                }
            }
        }
        if at.is_dir() && empty(&at) {
            rmdir(&at)?;
        }
    }
    Ok(())
}

/// Move the first captures to the sharded layout (git renames), and the manifest's rows with them. Returns the rows moved.
///
/// # Errors
/// The lock, the table, a row, a git step; a failed push (`RuntimeError`), after the table is written.
pub fn relayout(root: &Path, store: &Archive) -> Result<usize> {
    let mut moved = 0;
    let (table, failure) = {
        let _held = store.locked(LOCK_WAIT)?;
        store.ensure()?;
        let mut table = gm_table(root)?;
        let mut renames: Vec<(String, String)> = Vec::new();
        for (name, entry) in &mut table {
            for key in entry
                .get("keys")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default()
            {
                let old = format!("{}/gm-copy/{name}", py_str(&key));
                if store.dir.join(&old).exists() {
                    rename(&mut renames, old, format!("{GM_DEST}/{name}"), true);
                }
            }
            if let Value::Object(m) = entry {
                m.shift_remove("archived");
            }
        }
        for path in flat_rows(root) {
            let mut row = load_row(&path)?;
            let url = field(&row, "url")?;
            let base = capture_base(&url);
            for f in ["path", "first"] {
                let old = row.get(f).map(py_str).unwrap_or_default();
                if !old.is_empty() && !old.starts_with(&format!("{base}/")) {
                    let (dir, name) = split_last(&old);
                    rename(&mut renames, dir.to_owned(), base.clone(), false);
                    row[f] = json!(format!("{base}/{name}"));
                }
            }
            let mut gm: Vec<String> = row
                .get("gm_copies")
                .and_then(Value::as_array)
                .map(|a| {
                    a.iter()
                        .map(|g| {
                            let g = py_str(g);
                            renames
                                .iter()
                                .find(|(o, _)| *o == g)
                                .map_or(g, |(_, n)| n.clone())
                        })
                        .collect()
                })
                .unwrap_or_default();
            gm.sort();
            gm.dedup();
            row["gm_copies"] = json!(gm);
            write_row(root, &url, &row)?;
            unlink(&path)?;
            moved += 1;
        }
        renames.sort();
        apply_renames(store, &renames)?;
        sweep(store, &renames)?;
        for (name, entry) in &mut table {
            if store.dir.join(GM_DEST).join(name).exists() {
                if let Value::Object(m) = entry {
                    m.insert("archived".into(), json!(format!("{GM_DEST}/{name}")));
                }
            }
        }
        store.git(
            &["commit", "-q", "-m", "relayout: captures sharded by the URL id's first two hex digits, the GM's copies under gm-copies/"],
            false,
        )?;
        (table, store.push()?)
    };
    write_table(root, &table)?;
    if !failure.is_empty() {
        return Err(Error::new(
            "RuntimeError",
            format!("relayout committed but not pushed: {failure}"),
        ));
    }
    Ok(moved)
}
