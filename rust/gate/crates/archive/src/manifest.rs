//! The manifest and one URL archived (`archive.py`'s third part; ported by feature 449 T146): THE MANIFEST is one row per cited URL in
//! this repository (`research/archive/<id[:2]>/<id>.json`), which the record build reads (the `research` crate's `record::archive`, which
//! also says what is cited - asked here, so they agree). And IN ADDITION, every file of `/host-l7r-repo/academic-sources/` that
//! `research/archive/gm-copies.json` matches to a key is copied to `gm-copies/<file>` (FR-012), whatever the live fetch did.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_research::record::archive::{self as rec, Cited};
use l7r_guard::shared::pyjson::{dumps, py_str, sorted, truthy};
use serde_json::{json, Map, Value};

use crate::capture::{capture, split_large, PART};
use crate::fetch::{pdf_text, Client};
use crate::store::Archive;
use crate::{Error, Result};

/// The page cache's text is a fallback copy at any age - an old copy of a dead page beats none.
pub const CACHE_ANY_AGE_DAYS: f64 = 365.0 * 100.0;
/// Where the GM's copies go in the archive.
pub const GM_DEST: &str = "gm-copies";
/// How long a capture waits for the archive's lock.
pub const LOCK_WAIT: f64 = 600.0;

fn os_error(e: &std::io::Error, what: &Path) -> Error {
    Error::new("OSError", format!("{e}: '{}'", what.display()))
}

/// The record's directory under the repository.
#[must_use]
pub fn research(root: &Path) -> PathBuf {
    root.join("research")
}

/// `research/archive`.
#[must_use]
pub fn manifest_dir(root: &Path) -> PathBuf {
    research(root).join(rec::ARCHIVE_DIR)
}

/// A URL's manifest row, sharded as the archive is: `research/archive/<id[:2]>/<id>.json`.
#[must_use]
pub fn row_path(root: &Path, url: &str) -> PathBuf {
    let uid = rec::url_id(url);
    manifest_dir(root)
        .join(&uid[..2])
        .join(format!("{uid}.json"))
}

fn hex_name(name: &str, len: Option<usize>) -> bool {
    let hex = |b: u8| b.is_ascii_digit() || (b'a'..=b'f').contains(&b);
    match len {
        Some(n) => name.len() == n && name.bytes().all(hex),
        None => name.bytes().next().is_some_and(hex),
    }
}

/// Every row file, sorted (`sorted(glob("[0-9a-f][0-9a-f]/[0-9a-f]*.json"))`).
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the glob's `*.json` matched the name's case exactly, as this does"
)]
#[must_use]
pub fn row_files(root: &Path) -> Vec<PathBuf> {
    let names = |d: &Path| -> Vec<String> {
        std::fs::read_dir(d)
            .map(|r| {
                r.flatten()
                    .map(|e| e.file_name().to_string_lossy().into_owned())
                    .collect()
            })
            .unwrap_or_default()
    };
    let base = manifest_dir(root);
    let mut out = Vec::new();
    for shard in names(&base).into_iter().filter(|n| hex_name(n, Some(2))) {
        let dir = base.join(&shard);
        for f in names(&dir) {
            if hex_name(&f, None) && f.ends_with(".json") && dir.join(&f).is_file() {
                out.push(dir.join(f));
            }
        }
    }
    out.sort();
    out
}

/// Where a URL's captures go in the archive: `<id[:2]>/<id>`.
#[must_use]
pub fn capture_base(url: &str) -> String {
    let uid = rec::url_id(url);
    format!("{}/{uid}", &uid[..2])
}

/// A row file read as JSON.
///
/// # Errors
/// A file that is not UTF-8 or not JSON (the Python's `json.loads` raised), or unreadable.
pub fn load_row(path: &Path) -> Result<Value> {
    let text = std::fs::read(path).map_err(|e| os_error(&e, path))?;
    let text = String::from_utf8(text).map_err(|e| {
        Error::new(
            "UnicodeDecodeError",
            format!("'utf-8' codec can't decode: {e}"),
        )
    })?;
    l7r_guard::shared::pyjson::loads(&text)
        .map_err(|e| Error::new("JSONDecodeError", e.to_string()))
}

/// The URL's row, or none where it is missing or not JSON.
#[must_use]
pub fn read_row(root: &Path, url: &str) -> Option<Map<String, Value>> {
    let text = std::fs::read_to_string(row_path(root, url)).ok()?;
    match l7r_guard::shared::pyjson::loads(&text).ok()? {
        Value::Object(m) => Some(m),
        _ => None,
    }
}

/// The row written whole: keys sorted, indented by one, a newline, through a temporary file renamed over it.
///
/// # Errors
/// A write.
pub fn write_row(root: &Path, url: &str, row: &Value) -> Result<()> {
    let path = row_path(root, url);
    let up = path.parent().unwrap_or(&path);
    std::fs::create_dir_all(up).map_err(|e| os_error(&e, up))?;
    let name = path
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let tmp = path.with_file_name(format!(".{name}.{}.tmp", std::process::id()));
    std::fs::write(&tmp, dumps(&sorted(row), Some(1), false) + "\n")
        .map_err(|e| os_error(&e, &tmp))?;
    std::fs::rename(&tmp, &path).map_err(|e| os_error(&e, &path))
}

/// The GM's files, by name: each one's keys and, once copied, where it is in the archive (`archived`). No table, no files; a table that
/// will not parse is an error, never an empty table - the first backfill ran on a malformed one and copied none of the GM's files while
/// every row looked normal (2026-10-02).
///
/// # Errors
/// The table is not JSON or has no `files`.
pub fn gm_table(root: &Path) -> Result<Map<String, Value>> {
    let path = manifest_dir(root).join(rec::GM_COPIES);
    if !path.is_file() {
        return Ok(Map::new());
    }
    let table = load_row(&path)?;
    match table.get("files") {
        Some(Value::Object(m)) => Ok(m.clone()),
        Some(_) => Err(Error::new(
            "TypeError",
            "the table's files are not a mapping",
        )),
        None => Err(Error::new("KeyError", "'files'")),
    }
}

/// key -> the GM's files that copy it (FR-012), the files in name order.
///
/// # Errors
/// As [`gm_table`].
pub fn gm_copies(root: &Path) -> Result<Vec<(String, Vec<String>)>> {
    let table = gm_table(root)?;
    let mut names: Vec<&String> = table.keys().collect();
    names.sort();
    let mut out: Vec<(String, Vec<String>)> = Vec::new();
    for name in names {
        let keys = table[name]
            .get("keys")
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default();
        for key in keys.iter().map(py_str) {
            match out.iter_mut().find(|(k, _)| *k == key) {
                Some((_, v)) => v.push(name.clone()),
                None => out.push((key, vec![name.clone()])),
            }
        }
    }
    Ok(out)
}

/// The GM's downloads (`L7R_GM_SOURCES`, else `/host-l7r-repo/academic-sources`).
#[must_use]
pub fn gm_dir() -> PathBuf {
    std::env::var_os("L7R_GM_SOURCES").map_or_else(
        || PathBuf::from("/host-l7r-repo/academic-sources"),
        PathBuf::from,
    )
}

/// `PurePath.suffix` of a file name, lowercased.
fn suffix_lower(name: &Path) -> String {
    let n = name
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let n = n.trim_start_matches('.');
    n.rfind('.')
        .map_or_else(String::new, |i| n[i..].to_lowercase())
}

/// The GM's file `name` in the archive (call under the lock): copied from the inbox to `gm-copies/<name>` once, its text beside a PDF
/// as `<name>.txt` so `make archive-find` reads it; returns its archive path, or empty where it is neither in the archive nor in the
/// inbox. A file the table already places (`archived`) is looked for there.
///
/// # Errors
/// A copy or a commit.
pub fn place_gm(store: &Archive, name: &str, entry: &Value) -> Result<String> {
    let dest = entry
        .get("archived")
        .filter(|v| truthy(v))
        .map_or_else(|| format!("{GM_DEST}/{name}"), py_str);
    let source = store.gm.join(name);
    // NEVER A FILE OVER GITHUB'S LIMIT (feature 449 T160, found measuring the inbox's test): the inbox leaves such an entry waiting
    // (`process_inbox`), but the GM's copies told to their rows (`sync_gm_copies`) placed it anyway - a 100 MB commit that GitHub
    // refuses, after which every push of the archive fails - and `archive.py` did the same; it waits here too, for LFS or a split
    if !store.dir.join(&dest).exists() && source.exists() && crate::ops::too_big(&source).is_empty()
    {
        store.copy_in(&dest, &source)?;
        if source.is_file() && suffix_lower(&source) == ".pdf" {
            // read after it was copied, so it reads: a file that vanished between is a PDF with no text, as `pdftotext` finds one
            let text = pdf_text(&std::fs::read(&source).unwrap_or_default());
            if !text.is_empty() {
                store.put_file(
                    &format!("{dest}.txt"),
                    text.as_bytes(),
                    &format!("the text of {dest}"),
                )?;
            }
        }
    }
    Ok(if store.dir.join(&dest).exists() {
        dest
    } else {
        String::new()
    })
}

/// The UTC time as `%Y%m%dT%H%M%SZ`, a capture's directory name.
#[must_use]
pub fn stamp() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}{mo:02}{d:02}T{h:02}{mi:02}{s:02}Z")
}

/// `datetime.now(timezone.utc).isoformat(timespec="seconds")`.
#[must_use]
pub fn now_iso() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}+00:00")
}

/// Where the working copy and its lock live: beside the page cache (`L7R_SOURCES_HOME` moves both).
#[must_use]
pub fn home_of(root: &Path) -> PathBuf {
    l7r_guard::shared::consulted::home(root)
}

fn strings(v: &[String]) -> Value {
    json!(v)
}

/// Where a capture landed: its directory (none where it had no files), the GM's copies placed, and the push's failure.
struct Landed<'a> {
    rel: Option<&'a str>,
    gm_paths: Vec<String>,
    failure: &'a str,
}

/// The URL's manifest row after a capture: what it was before (`old`) kept where the capture brought nothing new.
fn row_of(
    url: &str,
    who: &Cited,
    got: &crate::capture::Capture,
    landed: &Landed<'_>,
    old: &Map<String, Value>,
) -> Map<String, Value> {
    let text_of = |m: &Map<String, Value>, k: &str| m.get(k).map_or_else(String::new, py_str);
    let mut gm: Vec<String> = landed.gm_paths.clone();
    if let Some(Value::Array(had)) = old.get("gm_copies") {
        gm.extend(had.iter().map(py_str));
    }
    gm.sort();
    gm.dedup();
    let first = old
        .get("first")
        .filter(|v| truthy(v))
        .cloned()
        .unwrap_or_else(|| json!(landed.rel.unwrap_or_default()));
    let mut row = Map::new();
    row.insert("url".into(), json!(url));
    row.insert("keys".into(), strings(&who.keys));
    row.insert("notes".into(), strings(&who.notes));
    row.insert("outcome".into(), json!(got.outcome));
    let path = landed.rel.map_or_else(
        || old.get("path").cloned().unwrap_or(json!("")),
        |r| json!(r),
    );
    row.insert("path".into(), path);
    row.insert("first".into(), first);
    row.insert("captured".into(), json!(now_iso()));
    row.insert("sha256".into(), json!(text_of(&got.record, "sha256")));
    row.insert("revision".into(), json!(text_of(&got.record, "revision")));
    row.insert("final_url".into(), json!(text_of(&got.record, "final_url")));
    row.insert("reason".into(), json!(got.reason));
    row.insert("gm_copies".into(), json!(gm));
    if !landed.failure.is_empty() {
        row.insert("held".into(), json!(got.outcome));
        row.insert("outcome".into(), json!("pending-upload"));
        row.insert(
            "reason".into(),
            json!(format!("push failed: {}", landed.failure)),
        );
    }
    row
}

/// Archive one cited URL, copy its keys' GM files, write its manifest row, and push when asked. Returns the row.
///
/// # Errors
/// A blocked URL, the GM's table, the lock, a write or a commit - each as the Python raised it.
pub fn archive_url(
    root: &Path,
    url: &str,
    who: &Cited,
    client: &mut dyn Client,
    store: &Archive,
    push: bool,
) -> Result<Map<String, Value>> {
    let url = rec::clean(url);
    let record_dir = research(root);
    l7r_gate_research::record::blocked::check(&url, "the archive", &record_dir)?;
    let copies = gm_copies(root)?;
    let table = gm_table(root)?;
    let mut mine: Vec<String> = Vec::new();
    for k in &who.keys {
        for (key, names) in &copies {
            if key == k {
                mine.extend(names.iter().cloned());
            }
        }
    }
    mine.sort();
    mine.dedup();
    // the page cache beside the working copy: `src.home(root)`, which is the store's home wherever the Python made one
    let cache = l7r_gate_research::pages::cached(&store.home, &url, CACHE_ANY_AGE_DAYS, false)?;
    let mut got = capture(
        client,
        &url,
        !mine.is_empty(),
        cache.as_ref().map_or("", |c| c.text.as_str()),
        &record_dir,
    )?;
    let (files, parts) = split_large(std::mem::take(&mut got.files), PART);
    let when = stamp();
    let mut rel = format!("{}/{when}", capture_base(&url));
    let mut record = got.record.clone();
    record.insert("captured".into(), json!(when));
    record.insert("keys".into(), strings(&who.keys));
    record.insert("notes".into(), strings(&who.notes));
    record.insert("outcome".into(), json!(got.outcome));
    record.insert("parts".into(), Value::Object(parts));
    let mut gm_paths: Vec<String> = Vec::new();
    let failure = {
        let _held = store.locked(LOCK_WAIT)?;
        store.ensure()?;
        if !files.is_empty() {
            let mut all = files.clone();
            all.push((
                "capture.json".to_owned(),
                (dumps(&Value::Object(record), Some(1), false) + "\n").into_bytes(),
            ));
            rel = store.put(&rel, &all, &format!("{}: {url}", got.outcome))?;
        }
        for name in &mine {
            let p = place_gm(store, name, table.get(name).unwrap_or(&Value::Null))?;
            if !p.is_empty() {
                gm_paths.push(p);
            }
        }
        if push {
            store.push()?
        } else {
            String::new()
        }
    };
    let old = read_row(root, &url).unwrap_or_default();
    let landed = Landed {
        rel: (!files.is_empty()).then_some(rel.as_str()),
        gm_paths,
        failure: &failure,
    };
    let row = row_of(&url, who, &got, &landed, &old);
    write_row(root, &url, &Value::Object(row.clone()))?;
    Ok(row)
}

/// Every GM file `gm-copies.json` matches copied into the archive, and every row of its key told so - without fetching anything
/// (FR-012). A row the live fetch left `partial` or `unreachable` becomes `archived-gm-copy` (plan D2: the GM's copy stands in where the
/// live page failed). Returns the rows changed (a row changed for two keys counts twice, as the Python counted it).
///
/// # Errors
/// A row or the table that will not read, the lock, a copy; a failed push (`RuntimeError`).
pub fn sync_gm_copies(root: &Path, store: &Archive) -> Result<usize> {
    let copies = gm_copies(root)?;
    let table = gm_table(root)?;
    let mut rows: Vec<Value> = row_files(root)
        .iter()
        .map(|p| load_row(p))
        .collect::<Result<_>>()?;
    let mut changed = 0;
    let failure = {
        let _held = store.locked(LOCK_WAIT)?;
        store.ensure()?;
        for (key, names) in &copies {
            let mut paths = Vec::new();
            for name in names {
                let p = place_gm(store, name, table.get(name).unwrap_or(&Value::Null))?;
                if !p.is_empty() {
                    paths.push(p);
                }
            }
            for row in &mut rows {
                let keyed = row
                    .get("keys")
                    .and_then(Value::as_array)
                    .is_some_and(|ks| ks.iter().any(|k| py_str(k) == *key));
                if !keyed || paths.is_empty() {
                    continue;
                }
                let before = row.clone();
                let mut gm: Vec<String> = row
                    .get("gm_copies")
                    .and_then(Value::as_array)
                    .map(|a| a.iter().map(py_str).collect())
                    .unwrap_or_default();
                gm.extend(paths.iter().cloned());
                gm.sort();
                gm.dedup();
                row["gm_copies"] = json!(gm);
                let outcome = row
                    .get("outcome")
                    .ok_or_else(|| Error::new("KeyError", "'outcome'"))?;
                if matches!(outcome.as_str(), Some("partial" | "unreachable")) {
                    row["outcome"] = json!("archived-gm-copy");
                }
                if *row != before {
                    write_row(root, &py_str(&row["url"]), row)?;
                    changed += 1;
                }
            }
        }
        store.push()?
    };
    if !failure.is_empty() {
        return Err(Error::new(
            "RuntimeError",
            format!("the GM's copies are committed but the push failed: {failure}"),
        ));
    }
    Ok(changed)
}

/// Every cited URL with no row, or a row still waiting on its upload.
///
/// # Errors
/// The record's or the manifest's refusal.
pub fn owed(root: &Path) -> Result<Vec<(String, Cited)>> {
    let dir = research(root);
    let rows = rec::load(&dir)?;
    Ok(rec::cited(&dir)?
        .into_iter()
        .filter(
            |(u, _)| match rows.get(&rec::url_id(u)).and_then(|r| r.get("outcome")) {
                None | Some(Value::Null) => true,
                Some(o) => o.as_str() == Some("pending-upload"),
            },
        )
        .collect())
}

/// Rows waiting on an upload, once a push has gone through, get their real outcome back.
///
/// # Errors
/// A row that will not read or write.
pub fn settle(root: &Path) -> Result<usize> {
    let mut n = 0;
    for path in row_files(root) {
        let mut row = load_row(&path)?;
        let held = row.get("held").filter(|v| truthy(v)).is_some();
        if row.get("outcome").and_then(Value::as_str) == Some("pending-upload") && held {
            if let Value::Object(m) = &mut row {
                let held = m.shift_remove("held").unwrap_or(Value::Null);
                m.insert("outcome".into(), held);
                m.insert("reason".into(), json!(""));
            }
            write_row(root, &py_str(&row["url"]), &row)?;
            n += 1;
        }
    }
    Ok(n)
}

/// The coverage table (spec FR-004): counts per outcome, every URL with none, and every unreachable one's reason; exit 1 where a cited
/// URL has no row.
///
/// # Errors
/// The record's or the manifest's refusal; a row with no outcome.
pub fn report(root: &Path, out: &mut String) -> Result<i32> {
    let dir = research(root);
    let rows = rec::load(&dir)?;
    let mut counts: Vec<(String, usize)> = Vec::new();
    let (mut missing, mut failed) = (Vec::new(), Vec::new());
    for (url, _) in rec::cited(&dir)? {
        let row = rows.get(&rec::url_id(&url));
        let outcome = match row {
            Some(r) => py_str(
                r.get("outcome")
                    .ok_or_else(|| Error::new("KeyError", "'outcome'"))?,
            ),
            None => "(none)".to_owned(),
        };
        match counts.iter_mut().find(|(o, _)| *o == outcome) {
            Some((_, n)) => *n += 1,
            None => counts.push((outcome.clone(), 1)),
        }
        match row {
            None => missing.push(url),
            Some(r) if outcome == "unreachable" || outcome == "partial" => {
                let reason = r.get("reason").map_or_else(String::new, py_str);
                failed.push(format!("{outcome:11} {url} - {reason}"));
            }
            Some(_) => {}
        }
    }
    let total: usize = counts.iter().map(|(_, n)| n).sum();
    let _ = writeln!(out, "archive coverage: {total} cited URL(s)");
    for outcome in rec::OUTCOMES.iter().copied().chain(["(none)"]) {
        if let Some((_, n)) = counts.iter().find(|(o, _)| o == outcome) {
            let _ = writeln!(out, "  {outcome:26} {n:5}");
        }
    }
    for line in &failed {
        let _ = writeln!(out, "  {line}");
    }
    for url in missing.iter().take(50) {
        let _ = writeln!(out, "  no row: {url}");
    }
    Ok(i32::from(!missing.is_empty()))
}

#[cfg(test)]
mod tests;
